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

//! Integration test for complete camera solve using Soccer Cones datasets.

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

/// Camera parameters shared by both v1 and v2 soccer cones datasets.
///
/// The UV files embed camera metadata (24mm focal, 35x19.6875mm film back)
/// but the solver is run with approximate 35mm / 36x20.25mm values for
/// investigation purposes.
fn soccer_cones_camera_params(
) -> (MillimeterUnit<f64>, CameraFilmBack<f64>, ImageSize<f64>) {
    let focal_length = MillimeterUnit::new(35.0);
    let film_back = CameraFilmBack::new(
        MillimeterUnit::new(36.0),
        MillimeterUnit::new(20.25), // 16:9 aspect ratio.
    );
    let image_size = ImageSize::from_pixels(3840.0, 2160.0);
    (focal_length, film_back, image_size)
}

fn run_camera_solve_soccer_cones(
    uv_filename: &str,
    dataset_label: &str,
    test_prefix: &str,
    is_noisy: bool,
) -> Result<()> {
    let (mut markers, frame_range) = load_marker_data(uv_filename)?;

    let solver_type = BundleAdjustmentSolverType::SparseLevenbergMarquardt;
    let naming_solver_type =
        bundle_adjustment_solver_type_to_naming(&solver_type);
    let solver_suffix = naming_solver_type.as_str();

    let (dataset_name, condition) = if is_noisy {
        add_noise_to_markers(&mut markers, 0.005);
        (
            format!("{} (noisy, {})", dataset_label, solver_suffix),
            DataCondition::Noisy,
        )
    } else {
        (
            format!("{} (clean, {})", dataset_label, solver_suffix),
            DataCondition::Clean,
        )
    };

    // Create output naming for visualizations.
    let naming = test_output_file_naming(
        TestType::CameraSolve,
        test_prefix,
        VisualizationType::Scene3d,
    )
    .with_condition(condition)
    .with_solver(naming_solver_type);

    let (focal_length, film_back, image_size) = soccer_cones_camera_params();

    // Random seed for reproducibility.
    let seed = 42;

    // Configure global focal length optimization using DE.
    // The embedded focal length is 24mm; we search around 35mm ± 5mm.
    let generation_count = 10;
    let global_config = GlobalAdjustmentConfig::small_refinement(
        (30.0, 40.0),
        generation_count,
        seed,
    );

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
        focal_length,
        film_back,
        image_size,
        config,
        None,
        // Some(&global_config), // Uncomment to optimize focal length.
        step_by,
    )
}

// ---------------------------------------------------------------------------
// Soccer Cones v1 (71 markers, 231 frames)
// ---------------------------------------------------------------------------

#[test]
fn test_camera_solve_clean_soccer_cones_v1_sparse_lm() -> Result<()> {
    run_camera_solve_soccer_cones(
        "tracking_soccer_cones_v1.uv",
        "Soccer Cones v1",
        "soccer_cones_v1",
        false,
    )
}

#[test]
#[ignore]
fn test_camera_solve_noisy_soccer_cones_v1_sparse_lm() -> Result<()> {
    run_camera_solve_soccer_cones(
        "tracking_soccer_cones_v1.uv",
        "Soccer Cones v1",
        "soccer_cones_v1",
        true,
    )
}

// ---------------------------------------------------------------------------
// Soccer Cones v2 (62 markers, 231 frames)
// ---------------------------------------------------------------------------

#[test]
fn test_camera_solve_clean_soccer_cones_v2_sparse_lm() -> Result<()> {
    run_camera_solve_soccer_cones(
        "tracking_soccer_cones_v2.uv",
        "Soccer Cones v2",
        "soccer_cones_v2",
        false,
    )
}

#[test]
#[ignore]
fn test_camera_solve_noisy_soccer_cones_v2_sparse_lm() -> Result<()> {
    run_camera_solve_soccer_cones(
        "tracking_soccer_cones_v2.uv",
        "Soccer Cones v2",
        "soccer_cones_v2",
        true,
    )
}
