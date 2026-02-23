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

//! Bundle adjustment tests using the Opera House dataset.

#![allow(unused)]
#![allow(dead_code)]
#![allow(unused_imports)]
#![allow(non_snake_case)]

mod common;

use crate::common::bundle_adjustment_solver_type_to_naming;
use crate::common::bundle_adjustment_utils::run_bundle_adjustment_dataset_test;
use crate::common::data_utils::{load_marker_data, select_optimal_frame_pair};
use crate::common::marker_noise::add_noise_to_markers;
use crate::common::visualization::scene;
use crate::common::NamingSolverType;
use crate::common::{
    test_output_file_naming, DataCondition, OutputFileNaming, TestType,
    VisualizationType,
};

use anyhow::Result;

use mmsfm_rust::datatype::{
    CameraFilmBack, ImageSize, MillimeterUnit, UnitValue,
};
use mmsfm_rust::sfm_camera::BundleAdjustmentSolverType;

fn run_bundle_adjustment_operahouse(
    is_noisy: bool,
    solver_type: BundleAdjustmentSolverType,
) -> Result<()> {
    let (mut markers, frame_range) =
        load_marker_data("operahouse_v1_format.uv")?;

    let naming_solver_type =
        bundle_adjustment_solver_type_to_naming(&solver_type);
    let solver_suffix = naming_solver_type.as_str();

    let (dataset_name, condition) = if is_noisy {
        add_noise_to_markers(&mut markers, 0.005);
        (
            format!("Opera House (noisy, {})", solver_suffix),
            DataCondition::Noisy,
        )
    } else {
        (
            format!("Opera House (clean, {})", solver_suffix),
            DataCondition::Clean,
        )
    };

    let frame_pair = select_optimal_frame_pair(&markers, &frame_range)?;

    let naming = test_output_file_naming(
        TestType::BundleAdjust,
        "operahouse",
        VisualizationType::Scene3d,
    )
    .with_condition(condition)
    .with_solver(naming_solver_type);

    let film_back = CameraFilmBack::from_millimeters(36.0, 27.0);
    let focal_length = MillimeterUnit::new(91.0); // ~22.4 degrees horizontal FoV
    let image_size_a = ImageSize::from_pixels(3072.0, 2304.0);
    let image_size_b = ImageSize::from_pixels(3072.0, 2304.0);

    let views = vec![
        scene::ViewConfigurationBuilder::new()
            .view_name("front")
            .rotation_ortho_front()
            .resolution_hd()
            .build(),
        scene::ViewConfigurationBuilder::new()
            .view_name("right")
            .rotation_ortho_right()
            .resolution_hd()
            .build(),
        scene::ViewConfigurationBuilder::new()
            .view_name("top")
            .rotation_ortho_top()
            .resolution_hd()
            .build(),
    ];

    run_bundle_adjustment_dataset_test(
        &markers,
        &frame_pair,
        25, // Expect at least 25 markers
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
fn test_bundle_adjustment_clean_operahouse_dense_lm() -> Result<()> {
    run_bundle_adjustment_operahouse(false, BundleAdjustmentSolverType::DenseLM)
}

#[test]
#[ignore]
fn test_bundle_adjustment_noisy_operahouse_dense_lm() -> Result<()> {
    run_bundle_adjustment_operahouse(true, BundleAdjustmentSolverType::DenseLM)
}
