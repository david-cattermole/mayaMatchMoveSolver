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

// Submodules.
pub mod utils;
pub mod visualization;

// Test runner utilities.
pub mod bundle_adjustment_utils;
pub mod camera_pose_from_bundles_utils;
pub mod camera_relative_pose_utils;
pub mod camera_solve_utils;
pub mod triangulation_utils;

// Data utilities.
pub mod data_utils;
pub mod marker_noise;
pub mod marker_utils;
pub mod synthetic_data;

// Re-export test runners.
pub use bundle_adjustment_utils::run_bundle_adjustment_dataset_test;
pub use camera_pose_from_bundles_utils::run_camera_pose_from_bundles_dataset_test;
pub use camera_relative_pose_utils::run_relative_pose_dataset_test;
pub use camera_solve_utils::run_camera_solve_dataset_test;

// Re-export data utilities.
pub use data_utils::{load_marker_data, select_optimal_frame_pair, FramePair};
pub use marker_noise::add_noise_to_markers;
pub use marker_utils::extract_point_correspondences;

// Re-export utils.
pub use utils::find_output_dir;

// Re-export visualization utilities.
pub use visualization::{
    bundle_adjustment_solver_type_to_naming, test_output_file_naming,
    visualize_marker_reprojections_2d_scatter,
    visualize_marker_reprojections_sequential, CameraPoseWithFrame,
    DataCondition, NamingSolverType, OutputFileNaming, Stage, TestType,
    ViewConfiguration, ViewConfigurationBuilder, ViewName, VisualizationType,
};

// Re-export triangulation utilities.
pub use triangulation_utils::{
    create_synthetic_camera_setup_with_config, run_triangulate_all_methods,
    run_triangulation_method, run_triangulation_test_from_file,
    CameraConfiguration, TriangulationMethod,
};
