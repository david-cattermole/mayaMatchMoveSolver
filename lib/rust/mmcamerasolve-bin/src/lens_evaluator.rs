//
// Copyright (C) 2026 David Cattermole.
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

//! Evaluators for global parameter optimization (focal length and lens).

use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;

use mmio::nuke_lens_common::NukeLensData;
use mmio::uvtrack_reader::{FrameRange, MarkersData};
use mmlogger::{mm_log_debug, Logger};
use mmoptimise::global::Evaluator;

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;
use mmsfm::datatype::common::UnitValue;
use mmsfm::datatype::{
    BundlePositions, CameraFilmBack, CameraIntrinsics, CameraPoses, ImageSize,
    MillimeterUnit,
};
use mmsfm::sfm_camera::{
    camera_solve_inner, AdjustmentParameterLayout, CameraSolveConfig,
    SolveQuality, SolveQualityMetrics,
};

use crate::undistort::{apply_lens_overrides, undistort_markers_with_lens};

/// Minimum number of bundles required for a solve to be considered valid.
pub const MINIMUM_ACCEPTED_BUNDLE_COUNT: usize = 6;

/// Evaluates a candidate parameter vector (focal length + lens params)
/// by applying undistortion with the candidate lens params and running
/// a full camera solve.
///
/// Takes distorted markers and applies undistortion per-evaluation
/// with candidate lens parameter values, deferring the undistortion
/// until optimization time.
pub struct LensAwareEvaluator<L: Logger> {
    frame_range: FrameRange,
    /// Raw distorted markers — NOT pre-undistorted.
    distorted_markers: Arc<MarkersData>,
    /// Whether the marker data has explicit distorted UV fields.
    has_explicit_distorted: bool,
    /// Baseline lens data loaded from Nuke .nk file.
    nuke_lens: Arc<NukeLensData>,
    film_back: CameraFilmBack<f64>,
    image_size: ImageSize<f64>,
    config: Arc<CameraSolveConfig>,
    solve_quality: SolveQuality,
    /// Maps x[i] to what it controls (focal length, lens params, etc).
    parameter_layout: AdjustmentParameterLayout,
    eval_counter: Arc<AtomicUsize>,
    current_generation: Arc<AtomicUsize>,
    logger: L,
}

impl<L: Logger> LensAwareEvaluator<L> {
    pub fn new(
        frame_range: FrameRange,
        distorted_markers: Arc<MarkersData>,
        has_explicit_distorted: bool,
        nuke_lens: Arc<NukeLensData>,
        film_back: CameraFilmBack<f64>,
        image_size: ImageSize<f64>,
        config: Arc<CameraSolveConfig>,
        solve_quality: SolveQuality,
        parameter_layout: AdjustmentParameterLayout,
        current_generation: Arc<AtomicUsize>,
        logger: L,
    ) -> Self {
        Self {
            frame_range,
            distorted_markers,
            has_explicit_distorted,
            nuke_lens,
            film_back,
            image_size,
            config,
            solve_quality,
            parameter_layout,
            eval_counter: Arc::new(AtomicUsize::new(0)),
            current_generation,
            logger,
        }
    }
}

impl<L: Logger> Evaluator for LensAwareEvaluator<L> {
    fn evaluate(&self, x: &[f64]) -> f64 {
        let eval_num = self.eval_counter.fetch_add(1, Ordering::SeqCst) + 1;
        let gen = self.current_generation.load(Ordering::SeqCst);

        mm_log_debug!(
            self.logger,
            "[LensEval {} Gen {}] Running...",
            eval_num,
            gen
        );

        // 1. Determine focal length.
        let focal_length_mm = match self.parameter_layout.focal_length_index() {
            Some(idx) => x[idx],
            None => self.nuke_lens.camera_parameters.focal_length_cm * 10.0,
        };

        // 2. Build lens parameter overrides from x and apply.
        let overrides = self.parameter_layout.lens_overrides_from_params(x);
        let mut modified_lens = (*self.nuke_lens).clone();
        apply_lens_overrides(&mut modified_lens, &overrides);

        // 3. Clone markers and apply undistortion with modified lens.
        let mut markers_clone = (*self.distorted_markers).clone();
        if undistort_markers_with_lens(
            &mut markers_clone,
            &modified_lens,
            self.has_explicit_distorted,
        )
        .is_err()
        {
            return f64::MAX;
        }

        // 4. Create intrinsics with candidate focal length.
        let intrinsics = CameraIntrinsics::from_centered_lens(
            MillimeterUnit::new(focal_length_mm),
            self.film_back,
        );

        // 5. Run camera solve.
        let mut camera_poses = CameraPoses::new();
        let mut bundle_positions = BundlePositions::new();
        let mut quality_metrics = SolveQualityMetrics::default();
        let noop_logger = mmlogger::NoOpLogger;
        let print_summary = false;

        match camera_solve_inner(
            &noop_logger,
            self.frame_range,
            &markers_clone,
            &intrinsics,
            &self.image_size,
            &self.config,
            self.solve_quality,
            print_summary,
            None,
            &mut camera_poses,
            &mut bundle_positions,
            &mut quality_metrics,
        ) {
            Ok(_) => {
                if bundle_positions.len() >= MINIMUM_ACCEPTED_BUNDLE_COUNT {
                    quality_metrics.mean_reprojection_error
                } else {
                    f64::MAX
                }
            }
            Err(_) => f64::MAX,
        }
    }
}
