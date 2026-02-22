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

//! Visualization utilities for Structure from Motion data.
//!
//! Provides functions for creating 3D scene views, 2D marker reprojections,
//! and residual error plots.

pub mod output_naming;
pub mod reprojection;
pub mod residuals;
pub mod scene;

pub use output_naming::{
    bundle_adjustment_solver_type_to_naming, DataCondition, NamingSolverType,
    OutputFileNaming, Stage, TestType, ViewName, VisualizationType,
};
pub use reprojection::{
    visualize_marker_reprojections_2d_scatter,
    visualize_marker_reprojections_sequential, FramePair,
};
pub use residuals::{
    visualize_multi_frame_residuals_per_marker,
    visualize_residual_errors_line_plot,
};
pub use scene::{
    calculate_scene_bounds_for_all_frames, calculate_scene_center,
    calculate_uniform_scene_bounds, visualize_sfm_scene_views,
    visualize_sfm_trajectory_views, BundleVisibilityMap, CameraPoseWithFrame,
    EpipolarLineOptions, SceneBounds, ViewConfiguration,
    ViewConfigurationBuilder,
};
