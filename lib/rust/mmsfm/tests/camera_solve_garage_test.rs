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

//! Integration test for complete camera solve using Garage dataset.

#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use crate::common::bundle_adjustment_solver_type_to_naming;
use crate::common::data_utils::load_marker_data;
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
use mmsfm_rust::sfm_camera::GlobalAdjustmentConfig;
use mmsfm_rust::sfm_camera::{BundleAdjustmentSolverType, CameraSolveConfig};

fn run_camera_solve_garage(
    is_noisy: bool,
    solver_type: BundleAdjustmentSolverType,
) -> Result<()> {
    let (mut markers, mut frame_range) =
        load_marker_data("garage_2dtracks_v1_format.uv")?;

    let naming_solver_type =
        bundle_adjustment_solver_type_to_naming(&solver_type);
    let solver_suffix = naming_solver_type.as_str();

    let (dataset_name, condition) = if is_noisy {
        add_noise_to_markers(&mut markers, 0.005);
        (
            format!("Garage (noisy, {})", solver_suffix),
            DataCondition::Noisy,
        )
    } else {
        (
            format!("Garage (clean, {})", solver_suffix),
            DataCondition::Clean,
        )
    };

    // Create output naming for visualizations.
    let naming = test_output_file_naming(
        TestType::CameraSolve,
        "garage",
        VisualizationType::Scene3d,
    )
    .with_condition(condition)
    .with_solver(naming_solver_type);

    // Setup camera parameters.
    //
    // TODO: These values are unknown and are probably wrong.  We
    // should use a differential evolution (DE) global solver to
    // refine the 35mm focal length estimate.
    let focal_length = MillimeterUnit::new(25.0);
    let film_back = CameraFilmBack::from_millimeters(36.0, 20.25);
    let image_size = ImageSize::from_pixels(960.0, 540.0);

    // Random seed for reproducibility.
    let seed = 42;

    // Configure global focal length optimization using DE.
    let generation_count = 10;
    let global_config = GlobalAdjustmentConfig::small_refinement(
        (20.0, 30.0),
        generation_count,
        seed,
    );

    // Configure solver.
    let config = CameraSolveConfig {
        origin_frame: 0,
        bundle_solver_type: solver_type,
        ..Default::default()
    };

    // Define visualization views.
    let views = vec![scene::ViewConfigurationBuilder::new()
        .view_name("top")
        .rotation_ortho_top()
        .resolution_hd()
        .build()];

    let step_by = 1;
    common::run_camera_solve_dataset_test(
        &markers,
        frame_range,
        &dataset_name,
        &naming,
        views,
        focal_length,
        film_back,
        image_size,
        config,
        None,
        // Some(&global_config), // Use DE to optimize focal length.
        step_by,
    )
}

#[test]
#[ignore] // Slow - large dataset with 250 markers and 2707 frames
fn test_camera_solve_clean_garage_dense_lm() -> Result<()> {
    run_camera_solve_garage(false, BundleAdjustmentSolverType::DenseLM)
}

#[test]
fn test_camera_solve_clean_garage_sparse_lm() -> Result<()> {
    run_camera_solve_garage(
        false,
        BundleAdjustmentSolverType::SparseLevenbergMarquardt,
    )
}

#[test]
#[ignore] // Slow - large dataset with 250 markers and 2707 frames
fn test_camera_solve_noisy_garage_dense_lm() -> Result<()> {
    run_camera_solve_garage(true, BundleAdjustmentSolverType::DenseLM)
}

#[test]
#[ignore]
fn test_camera_solve_noisy_garage_sparse_lm() -> Result<()> {
    run_camera_solve_garage(
        true,
        BundleAdjustmentSolverType::SparseLevenbergMarquardt,
    )
}
