//
// Copyright (C) 2025, 2026 David Cattermole.
//
// This file is part of mmSolver.
//
// mmSolver is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// mmSolver is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
// ====================================================================
//

//! Focal length evaluator for global focal length optimization.

use super::config::{CameraSolveConfig, SolveQuality, SolveQualityMetrics};
use super::solve_core::camera_solve_inner;
use crate::datatype::common::UnitValue;
use crate::datatype::{
    BundlePositions, CameraFilmBack, CameraIntrinsics, CameraPoses, ImageSize,
    MillimeterUnit,
};

use mmio::uvtrack_reader::{FrameRange, MarkersData};
use mmlogger::Logger;
use mmoptimise::global::Evaluator;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = true;

pub const MINIMUM_ACCEPTED_BUNDLE_COUNT: usize = 6;

/// Evaluates a candidate focal length by running a full camera solve.
///
/// Implements `Evaluator` so it can be used with Differential Evolution
/// or Uniform Grid Search. Each call runs an independent solve with fresh
/// output buffers, making it safe to call from multiple threads.
pub struct CameraSolveFocalLengthEvaluator<L: Logger> {
    frame_range: FrameRange,
    markers: Arc<MarkersData>,
    film_back: CameraFilmBack<f64>,
    image_size: ImageSize<f64>,
    config: Arc<CameraSolveConfig>,
    solve_quality: SolveQuality,
    /// Counts total evaluations for progress logging.
    eval_counter: Arc<AtomicUsize>,
    /// Shared with the optimizer so log messages can show the current generation.
    current_generation: Arc<AtomicUsize>,
    /// Logger for debug output during evaluations.
    logger: L,
}

impl<L: Logger> CameraSolveFocalLengthEvaluator<L> {
    /// Create a new focal length evaluator.
    pub fn new(
        frame_range: FrameRange,
        markers: Arc<MarkersData>,
        film_back: CameraFilmBack<f64>,
        image_size: ImageSize<f64>,
        config: Arc<CameraSolveConfig>,
        solve_quality: SolveQuality,
        current_generation: Arc<AtomicUsize>,
        logger: L,
    ) -> Self {
        Self {
            frame_range,
            markers,
            film_back,
            image_size,
            config,
            solve_quality,
            eval_counter: Arc::new(AtomicUsize::new(0)),
            current_generation,
            logger,
        }
    }
}

impl<L: Logger> Evaluator for CameraSolveFocalLengthEvaluator<L> {
    /// Run the camera solve for the given focal length and return the
    /// mean reprojection error, or `f64::MAX` if the solve failed.
    fn evaluate(&self, x: &[f64]) -> f64 {
        use std::time::Instant;

        let focal_length_mm = x[0];
        let thread_id = mmcore::threadutils::thread_id_u64();
        let eval_num = self.eval_counter.fetch_add(1, Ordering::SeqCst) + 1;
        let gen = self.current_generation.load(Ordering::SeqCst);

        mm_debug_log!(
            self.logger,
            "[DE Eval {} Gen {}] [#{}] focal_length={:.8}mm - Running...",
            eval_num,
            gen,
            thread_id,
            focal_length_mm
        );

        let start_time = Instant::now();

        // Create intrinsics with candidate focal length.
        let intrinsics = CameraIntrinsics::from_centered_lens(
            MillimeterUnit::new(focal_length_mm),
            self.film_back,
        );

        // Create temporary output buffers (per-thread, avoid
        // synchronization).
        let mut camera_poses = CameraPoses::new();
        let mut bundle_positions = BundlePositions::new();
        let mut quality_metrics = SolveQualityMetrics::default();

        // Run camera solve with this focal length.
        // Use NoOpLogger since evaluations run in parallel threads
        // and we only care about the final solve result.
        let noop_logger = mmlogger::NoOpLogger;
        let print_summary = false;
        let result = match camera_solve_inner(
            &noop_logger,
            self.frame_range,
            &self.markers,
            &intrinsics,
            &self.image_size,
            &self.config,
            self.solve_quality,
            print_summary,
            None, // No intermediate writer during DE/UGS evaluation.
            &mut camera_poses,
            &mut bundle_positions,
            &mut quality_metrics,
        ) {
            Ok(_) => {
                let elapsed = start_time.elapsed();
                let _num_cameras = camera_poses.len();
                let num_bundles = bundle_positions.len();
                let num_frames = self.frame_range.frame_count();

                if num_bundles >= MINIMUM_ACCEPTED_BUNDLE_COUNT {
                    mm_debug_log!(
                        self.logger,
                        "[DE Eval {} Gen {}] [#{}] focal_length={:.8}mm ACCEPTED mean={:.6}px, median={:.6}px, bundles={}, frames_solved={}/{}, time={:.3}s",
                        eval_num, gen, thread_id, focal_length_mm,
                        quality_metrics.mean_reprojection_error,
                        quality_metrics.median_reprojection_error,
                        num_bundles,
                        quality_metrics.frames_solved,
                        num_frames,
                        elapsed.as_secs_f64()
                    );

                    quality_metrics.mean_reprojection_error
                } else {
                    mm_debug_log!(
                        self.logger,
                        "[DE Eval {} Gen {}] [#{}] focal_length={:.8}mm REJECTED mean={:.6}px, median={:.6}px, bundles={}, frames_solved={}/{}, time={:.3}s",
                        eval_num, gen, thread_id, focal_length_mm,
                        quality_metrics.mean_reprojection_error,
                        quality_metrics.median_reprojection_error,
                        num_bundles,
                        quality_metrics.frames_solved,
                        num_frames,
                        elapsed.as_secs_f64()
                    );
                    f64::MAX // Invalid focal length - guide DE away.
                }
            }
            Err(e) => {
                let elapsed = start_time.elapsed();
                mm_debug_log!(
                    self.logger,
                    "[DE Eval {} Gen {}] [#{}] focal_length={:.8}mm FAILED (time={:.3}s) error: {}",
                    eval_num, gen, thread_id, focal_length_mm, elapsed.as_secs_f64(), e
                );
                f64::MAX // Invalid focal length - guide DE away.
            }
        };

        result
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_evaluator_creation() {
        // Simple smoke test to verify evaluator can be created
        let frame_range = FrameRange::new(1, 10);
        let markers = Arc::new(MarkersData::new());
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let image_size = ImageSize::from_pixels(3600.0, 2400.0);
        let config = Arc::new(CameraSolveConfig::default());

        let current_generation = Arc::new(AtomicUsize::new(0));
        let evaluator = CameraSolveFocalLengthEvaluator::new(
            frame_range,
            markers,
            film_back,
            image_size,
            config,
            SolveQuality::Draft,
            current_generation,
            mmlogger::NoOpLogger,
        );

        // If we get here without panic, creation succeeded
        // Verify eval_counter starts at 0
        assert_eq!(evaluator.eval_counter.load(Ordering::SeqCst), 0);
    }
}
