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

//! Main camera solver API with optional global optimization.

use std::sync::Arc;

use anyhow::Result;
use mmlogger::Logger;

use mmio::uvtrack_reader::{FrameRange, MarkersData};

use super::config::{
    CameraSolveConfig, GlobalAdjustmentConfig, SolveQuality,
    SolveQualityMetrics,
};
use super::intermediate_writer::IntermediateResultWriter;
use super::solve_core::camera_solve_inner;
use super::solve_global_adjustment::run_camera_solve_with_global_adjustment;
use crate::datatype::{
    BundlePositions, CameraFilmBack, CameraIntrinsics, CameraPoses, ImageSize,
};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Solve camera poses and 3D bundle positions from 2D marker tracks.
///
/// When `global_adjustment_config` is `Some`, first optimizes focal
/// length using Differential Evolution or Uniform Grid search, then
/// runs the final solve with the best focal length found.
pub fn camera_solve<L: Logger>(
    logger: &mut L,
    scene_frame_range: FrameRange,
    markers: &MarkersData,
    camera_intrinsics: &CameraIntrinsics,
    film_back: &CameraFilmBack<f64>,
    image_size: &ImageSize<f64>,
    config: &CameraSolveConfig,
    global_adjustment_config: Option<&GlobalAdjustmentConfig>,
    intermediate_writer: Option<Arc<dyn IntermediateResultWriter>>,
    camera_poses: &mut CameraPoses,
    bundle_positions: &mut BundlePositions,
    quality_metrics: &mut SolveQualityMetrics,
) -> Result<()> {
    match global_adjustment_config {
        None => {
            // Standard solve with final solve quality.
            let final_solve_start = std::time::Instant::now();
            let solve_quality = SolveQuality::Final;
            let print_summary = true;
            let result = camera_solve_inner(
                logger,
                scene_frame_range,
                markers,
                camera_intrinsics,
                image_size,
                config,
                solve_quality,
                print_summary,
                intermediate_writer,
                camera_poses,
                bundle_positions,
                quality_metrics,
            );
            quality_metrics.final_solve_time_secs =
                Some(final_solve_start.elapsed().as_secs_f64());
            result
        }
        Some(global_config) => {
            // Global adjustment solver.
            run_camera_solve_with_global_adjustment(
                logger,
                scene_frame_range,
                markers,
                camera_intrinsics,
                film_back,
                image_size,
                config,
                global_config,
                intermediate_writer,
                camera_poses,
                bundle_positions,
                quality_metrics,
            )
        }
    }
}
