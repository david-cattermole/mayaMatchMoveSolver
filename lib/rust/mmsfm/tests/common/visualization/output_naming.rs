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

//! Test output file naming, using find_output_dir() to resolve the output directory.

pub use mmsfm_rust::visualization::output_naming::{
    bundle_adjustment_solver_type_to_naming, DataCondition, NamingSolverType,
    OutputFileNaming, Stage, TestType, ViewName, VisualizationType,
};

use crate::common::find_output_dir;

/// Creates an OutputFileNaming using the test output directory.
pub fn test_output_file_naming(
    test_type: TestType,
    dataset_name: impl Into<String>,
    visualization_type: VisualizationType,
) -> OutputFileNaming {
    let output_dir =
        find_output_dir().expect("Failed to find test output directory");
    OutputFileNaming::new(
        output_dir,
        test_type,
        dataset_name,
        visualization_type,
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_simple_filename() {
        let naming = test_output_file_naming(
            TestType::BundleAdjust,
            "cube_a",
            VisualizationType::Scene3d,
        );

        assert_eq!(naming.filename(), "cube_a_scene_3d.png");
    }

    #[test]
    fn test_full_filename() {
        let naming = test_output_file_naming(
            TestType::BundleAdjust,
            "cube_a",
            VisualizationType::Scene3d,
        )
        .with_condition(DataCondition::Clean)
        .with_solver(NamingSolverType::DenseLM)
        .with_stage(Stage::Initial)
        .with_view(ViewName::Front);

        assert_eq!(
            naming.filename(),
            "cube_a_clean_dense_lm_scene_3d_00_initial_front.png"
        );
    }

    #[test]
    fn test_marker_reprojection_filename() {
        let naming = test_output_file_naming(
            TestType::BundleAdjust,
            "blasterwalk",
            VisualizationType::MarkerReprojection2d,
        )
        .with_condition(DataCondition::Clean)
        .with_solver(NamingSolverType::DenseLM)
        .with_stage(Stage::Optimised);

        assert_eq!(
            naming.filename(),
            "blasterwalk_clean_dense_lm_marker_reprojections_2d_01_optimised.png"
        );
    }

    #[test]
    fn test_residuals_line_plot_filename() {
        let naming = test_output_file_naming(
            TestType::BundleAdjust,
            "operahouse",
            VisualizationType::ResidualsLinePlot,
        )
        .with_condition(DataCondition::Noisy)
        .with_stage(Stage::Final);

        assert_eq!(
            naming.filename(),
            "operahouse_noisy_residuals_line_plot_02_final.png"
        );
    }

    #[test]
    fn test_trajectory_frame_filename() {
        let naming = test_output_file_naming(
            TestType::CameraSolve,
            "cube_a",
            VisualizationType::Scene3d,
        )
        .with_view(ViewName::Top)
        .with_frame(42);

        assert_eq!(naming.filename(), "cube_a_scene_3d_top.0042.png");
    }

    #[test]
    fn test_clone_with_stage() {
        let base = test_output_file_naming(
            TestType::BundleAdjust,
            "cube_a",
            VisualizationType::Scene3d,
        )
        .with_condition(DataCondition::Clean)
        .with_view(ViewName::Front);

        let initial = base.clone_with_stage(Stage::Initial);
        let optimised = base.clone_with_stage(Stage::Optimised);

        assert_eq!(
            initial.filename(),
            "cube_a_clean_scene_3d_00_initial_front.png"
        );
        assert_eq!(
            optimised.filename(),
            "cube_a_clean_scene_3d_01_optimised_front.png"
        );
    }

    #[test]
    fn test_clone_with_view() {
        let base = test_output_file_naming(
            TestType::BundleAdjust,
            "cube_a",
            VisualizationType::Scene3d,
        )
        .with_stage(Stage::Initial);

        let front = base.clone_with_view(ViewName::Front);
        let top = base.clone_with_view(ViewName::Top);
        let right = base.clone_with_view(ViewName::Right);

        assert_eq!(front.filename(), "cube_a_scene_3d_00_initial_front.png");
        assert_eq!(top.filename(), "cube_a_scene_3d_00_initial_top.png");
        assert_eq!(right.filename(), "cube_a_scene_3d_00_initial_right.png");
    }

    #[test]
    fn test_clone_with_visualization() {
        let base = test_output_file_naming(
            TestType::BundleAdjust,
            "cube_a",
            VisualizationType::Scene3d,
        )
        .with_stage(Stage::Initial);

        let scene = base.clone();
        let markers = base
            .clone_with_visualization(VisualizationType::MarkerReprojection2d);
        let residuals =
            base.clone_with_visualization(VisualizationType::ResidualsLinePlot);

        assert_eq!(scene.filename(), "cube_a_scene_3d_00_initial.png");
        assert_eq!(
            markers.filename(),
            "cube_a_marker_reprojections_2d_00_initial.png"
        );
        assert_eq!(
            residuals.filename(),
            "cube_a_residuals_line_plot_00_initial.png"
        );
    }
}
