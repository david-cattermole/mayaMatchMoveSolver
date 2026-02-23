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

//! Integration test for complete camera solve using Blasterwalk dataset.

#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use anyhow::Result;
use mmsfm_rust::datatype::{
    CameraFilmBack, ImageSize, MillimeterUnit, UnitValue,
};

use mmsfm_rust::sfm_camera::{
    BundleAdjustmentSolverType, CameraSolveConfig, GlobalAdjustmentConfig,
};

use crate::common::bundle_adjustment_solver_type_to_naming;
use crate::common::data_utils::load_marker_data;
use crate::common::marker_noise::add_noise_to_markers;
use crate::common::visualization::scene::ViewConfigurationBuilder;
use crate::common::NamingSolverType;
use crate::common::{
    test_output_file_naming, DataCondition, OutputFileNaming, TestType,
    VisualizationType,
};

fn run_camera_solve_blasterwalk(
    is_noisy: bool,
    solver_type: BundleAdjustmentSolverType,
) -> Result<()> {
    let (mut markers, mut frame_range) =
        load_marker_data("blasterwalk_camera_2dtracks_v1_format.uv")?;

    let naming_solver_type =
        bundle_adjustment_solver_type_to_naming(&solver_type);
    let solver_suffix = naming_solver_type.as_str();

    let (dataset_name, condition) = if is_noisy {
        add_noise_to_markers(&mut markers, 0.005);
        (
            format!("Blasterwalk (noisy, {})", solver_suffix),
            DataCondition::Noisy,
        )
    } else {
        (
            format!("Blasterwalk (clean, {})", solver_suffix),
            DataCondition::Clean,
        )
    };

    // Create output naming for visualizations.
    let naming = test_output_file_naming(
        TestType::CameraSolve,
        "blasterwalk",
        VisualizationType::Scene3d,
    )
    .with_condition(condition)
    .with_solver(naming_solver_type);

    // Setup camera parameters.
    let initial_focal_length = MillimeterUnit::new(56.4);
    let film_back = CameraFilmBack::new(
        MillimeterUnit::new(36.0),
        MillimeterUnit::new(20.25), // 16:9 aspect ratio.
    );
    let image_size = ImageSize::from_pixels(3600.0, 2025.0);

    // Random seed for reproducibility.
    let seed = 42;

    // Configure global focal length optimization using DE.
    let generation_count = 10;
    let global_config = GlobalAdjustmentConfig::small_refinement(
        (51.4, 61.4),
        generation_count,
        seed,
    );

    // // Configure global focal length optimization using Uniform Grid
    // // Search.
    // let global_config = GlobalAdjustmentConfig::uniform_grid_search(
    //     (51.4, 61.4), // +/- 5mm around the initial 56.4mm estimate
    //     11,           // 11 samples = every 1mm
    // );

    // Configure solver.
    let config = CameraSolveConfig {
        origin_frame: 1,
        bundle_solver_type: solver_type,
        ..Default::default()
    };

    // Define visualization views.
    let views = vec![
        ViewConfigurationBuilder::new()
            .view_name("top")
            .rotation_ortho_top()
            .resolution_hd()
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("right")
            .rotation_ortho_right()
            .resolution_hd()
            .build(),
    ];

    let step_by = 1;
    common::run_camera_solve_dataset_test(
        &markers,
        frame_range,
        &dataset_name,
        &naming,
        views,
        initial_focal_length,
        film_back,
        image_size,
        config,
        None,
        // Some(&global_config), // Use UGS to optimize focal length.
        step_by,
    )
}

#[test]
#[ignore] // TODO: Make this run faster so we can test faster.
fn test_camera_solve_clean_blasterwalk_dense_lm() -> Result<()> {
    run_camera_solve_blasterwalk(false, BundleAdjustmentSolverType::DenseLM)
}

#[test]
fn test_camera_solve_clean_blasterwalk_sparse_lm() -> Result<()> {
    run_camera_solve_blasterwalk(
        false,
        BundleAdjustmentSolverType::SparseLevenbergMarquardt,
    )
}

#[test]
#[ignore] // TODO: Make this run faster so we can test faster.
fn test_camera_solve_noisy_blasterwalk_dense_lm() -> Result<()> {
    run_camera_solve_blasterwalk(true, BundleAdjustmentSolverType::DenseLM)
}

#[test]
#[ignore]
fn test_camera_solve_noisy_blasterwalk_sparse_lm() -> Result<()> {
    run_camera_solve_blasterwalk(
        true,
        BundleAdjustmentSolverType::SparseLevenbergMarquardt,
    )
}
