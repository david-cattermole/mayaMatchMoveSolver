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

//! Bundle adjustment tests using the cube2 C dataset.

#![allow(unused)]
#![allow(dead_code)]
#![allow(unused_imports)]
#![allow(non_snake_case)]

mod common;

use anyhow::Result;
use common::{
    add_noise_to_markers, load_marker_data, run_bundle_adjustment_dataset_test,
    visualization::{
        bundle_adjustment_solver_type_to_naming, test_output_file_naming,
        DataCondition, NamingSolverType, OutputFileNaming, TestType,
        ViewConfigurationBuilder, VisualizationType,
    },
    FramePair,
};
use mmsfm_rust::datatype::{
    CameraFilmBack, ImageSize, MillimeterUnit, UnitValue,
};
use mmsfm_rust::sfm_camera::BundleAdjustmentSolverType;

fn run_bundle_adjustment_cube2_c(
    is_noisy: bool,
    solver_type: BundleAdjustmentSolverType,
) -> Result<()> {
    let (mut markers, _frame_range) =
        load_marker_data("test_cube2_c_markers_v1_fmt.uv")?;

    let naming_solver_type =
        bundle_adjustment_solver_type_to_naming(&solver_type);
    let solver_suffix = naming_solver_type.as_str();

    let (dataset_name, condition) = if is_noisy {
        add_noise_to_markers(&mut markers, 0.005);
        (
            format!("Cube2 C (noisy, {})", solver_suffix),
            DataCondition::Noisy,
        )
    } else {
        (
            format!("Cube2 C (clean, {})", solver_suffix),
            DataCondition::Clean,
        )
    };

    let naming = test_output_file_naming(
        TestType::BundleAdjust,
        "cube2_c",
        VisualizationType::Scene3d,
    )
    .with_condition(condition)
    .with_solver(naming_solver_type);

    let frame_pair = FramePair {
        frame_a: 1,
        frame_b: 101,
    };

    let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
    let focal_length = MillimeterUnit::new(35.0);
    let image_size_a = ImageSize::from_pixels(3600.0, 2400.0);
    let image_size_b = ImageSize::from_pixels(3600.0, 2400.0);

    let views = vec![
        ViewConfigurationBuilder::new()
            .view_name("front")
            .rotation_ortho_front()
            .resolution_hd()
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("right")
            .rotation_ortho_right()
            .resolution_hd()
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("top")
            .rotation_ortho_top()
            .resolution_hd()
            .build(),
    ];

    run_bundle_adjustment_dataset_test(
        &markers,
        &frame_pair,
        16, // Expect at least 16 markers.
        &dataset_name,
        &naming,
        views,
        focal_length,
        film_back,
        image_size_a,
        image_size_b,
        solver_type,
        None, // Use all points.
    )
}

#[test]
fn test_bundle_adjustment_clean_cube2_c_dense_lm() -> Result<()> {
    run_bundle_adjustment_cube2_c(false, BundleAdjustmentSolverType::DenseLM)
}

#[test]
fn test_bundle_adjustment_noisy_cube2_c_dense_lm() -> Result<()> {
    run_bundle_adjustment_cube2_c(true, BundleAdjustmentSolverType::DenseLM)
}
