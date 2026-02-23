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

//! Relative pose tests for the Cube D dataset.

#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use crate::common::bundle_adjustment_solver_type_to_naming;
use crate::common::{
    add_noise_to_markers, load_marker_data, run_relative_pose_dataset_test,
    visualization::{
        scene::ViewConfigurationBuilder, test_output_file_naming,
        DataCondition, OutputFileNaming, TestType, VisualizationType,
    },
    FramePair,
};
use anyhow::Result;
use mmsfm_rust::datatype::{
    CameraFilmBack, ImageSize, MillimeterUnit, UnitValue,
};

fn run_relative_pose_cube_d(is_noisy: bool) -> Result<()> {
    let (mut markers, _frame_range) =
        load_marker_data("test_cube_d_markers_v1_fmt.uv")?;

    let (dataset_name, condition) = if is_noisy {
        add_noise_to_markers(&mut markers, 0.005);
        ("Cube D (noisy)", DataCondition::Noisy)
    } else {
        ("Cube D (clean)", DataCondition::Clean)
    };

    let naming = test_output_file_naming(
        TestType::RelativePose,
        "cube_d",
        VisualizationType::Scene3d,
    )
    .with_condition(condition);

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

    run_relative_pose_dataset_test(
        &markers,
        &frame_pair,
        8, // Expect at least 8 markers.
        dataset_name,
        &naming,
        views,
        focal_length,
        film_back,
        image_size_a,
        image_size_b,
    )
}

#[test]
fn test_relative_pose_clean_cube_d() -> Result<()> {
    run_relative_pose_cube_d(false)
}

#[test]
fn test_relative_pose_noisy_cube_d() -> Result<()> {
    run_relative_pose_cube_d(true)
}
