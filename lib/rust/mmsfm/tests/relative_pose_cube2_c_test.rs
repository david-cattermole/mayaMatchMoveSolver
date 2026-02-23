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

//! Relative pose tests for the Cube2 C dataset.

#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use crate::common::camera_relative_pose_utils::run_relative_pose_dataset_test;
use crate::common::data_utils::{load_marker_data, FramePair};
use crate::common::marker_noise::add_noise_to_markers;
use crate::common::visualization::scene::ViewConfigurationBuilder;
use crate::common::{
    test_output_file_naming, DataCondition, OutputFileNaming, TestType,
    VisualizationType,
};
use anyhow::Result;
use mmsfm_rust::datatype::{
    CameraFilmBack, ImageSize, MillimeterUnit, UnitValue,
};

fn run_relative_pose_cube2_c(is_noisy: bool) -> Result<()> {
    let (mut markers, _frame_range) =
        load_marker_data("test_cube2_c_markers_v1_fmt.uv")?;

    let (dataset_name, condition) = if is_noisy {
        add_noise_to_markers(&mut markers, 0.005);
        ("Cube2 C (noisy)", DataCondition::Noisy)
    } else {
        ("Cube2 C (clean)", DataCondition::Clean)
    };

    let naming = test_output_file_naming(
        TestType::RelativePose,
        "cube2_c",
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
        16, // Expect at least 16 markers.
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
fn test_relative_pose_clean_cube2_c() -> Result<()> {
    run_relative_pose_cube2_c(false)
}

#[test]
fn test_relative_pose_noisy_cube2_c() -> Result<()> {
    run_relative_pose_cube2_c(true)
}
