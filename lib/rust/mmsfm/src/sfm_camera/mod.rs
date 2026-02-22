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

//! Incremental Structure-from-Motion (SfM) camera solver
//!
//! This module implements a complete incremental SfM pipeline that:
//! 1. Analyzes frames to find optimal initialization pair
//! 2. Solves initial camera relative pose
//! 3. Incrementally adds camera poses using relative pose or PnP
//! 4. Triangulates 3D bundle positions
//! 5. Refines solution with bundle adjustment
//! 6. Transforms result to desired coordinate system
//!
//! Based on the Python implementation in `solvercamerautils.py`.

// Module declarations.
mod bundle_adjustment;
mod bundle_adjustment_utils;
mod camera_pnp;
mod camera_pnp_methods;
mod config;
mod constants;
mod focal_length_evaluator;
mod frame_graph;
mod frame_score;
mod intermediate_writer;
mod reprojection;
mod solve;
mod solve_core;
mod solve_frame_selection;
mod solve_global_adjustment;
mod solve_retriangulate;
mod solve_timing;
mod solve_utils;
mod transforms;
mod triangulation_fixed_depth;
mod validation;

// Re-export public API.
pub use config::{
    BundleAdjustmentSolverType, CameraSolveConfig, GlobalAdjustmentConfig,
    GlobalAdjustmentMode, SolveQualityMetrics,
};
pub use frame_score::analyze_frame_scoring_and_marker_selection;
pub use intermediate_writer::IntermediateResultWriter;
pub use reprojection::ReprojectionErrorStats;
pub use solve::camera_solve;
pub use validation::{
    detect_camera_position_collapse, validate_and_filter_bundles,
    BundleValidationConfig, BundleValidationResult,
};
