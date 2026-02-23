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


#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use anyhow::Result;
use common::{
    add_noise_to_markers, load_marker_data,
    run_camera_pose_from_bundles_dataset_test,
    visualization::{
        scene::{self, EpipolarLineOptions, ViewConfigurationBuilder},
        test_output_file_naming, DataCondition, OutputFileNaming, TestType,
        VisualizationType,
    },
};
use mmsfm_rust::datatype::{
    CameraFilmBack, ImageSize, MillimeterUnit, UnitValue,
};
use nalgebra::Point3;
use std::collections::HashMap;

fn run_camera_pose_from_bundles_cube_c(is_noisy: bool) -> Result<()> {
    let (mut markers, _frame_range) =
        load_marker_data("test_cube_c_markers_v1_fmt.uv")?;

    let (
        dataset_name,
        condition,
        min_success_rate_percent,
        max_mean_error_pixels,
        max_max_error_pixels,
    ) = if is_noisy {
        add_noise_to_markers(&mut markers, 0.005);
        (
            "Cube C (noisy)",
            DataCondition::Noisy,
            Some(30),
            Some(15.0),
            Some(1500.0),
        )
    } else {
        ("Cube C (clean)", DataCondition::Clean, None, None, None)
    };

    let naming = test_output_file_naming(
        TestType::CameraPoseFromBundles,
        "cube_c",
        VisualizationType::Scene3d,
    )
    .with_condition(condition);

    let mut ground_truth_3d: HashMap<&str, Point3<f64>> = HashMap::new();
    ground_truth_3d.insert("locator1_MKR", Point3::new(-3.75, 3.75, -16.25));
    ground_truth_3d.insert("locator2_MKR", Point3::new(3.75, 3.75, -16.25));
    ground_truth_3d.insert("locator3_MKR", Point3::new(-3.75, -3.75, -16.25));
    ground_truth_3d.insert("locator4_MKR", Point3::new(3.75, -3.75, -16.25));
    ground_truth_3d.insert("locator5_MKR", Point3::new(-3.75, 3.75, -23.75));
    ground_truth_3d.insert("locator6_MKR", Point3::new(3.75, 3.75, -23.75));
    ground_truth_3d.insert("locator7_MKR", Point3::new(-3.75, -3.75, -23.75));
    ground_truth_3d.insert("locator8_MKR", Point3::new(3.75, -3.75, -23.75));

    let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
    let focal_length = MillimeterUnit::new(35.0);
    let image_size = ImageSize::from_pixels(3600.0, 2400.0);

    let epipolar_opts = EpipolarLineOptions {
        enabled: true,
        opacity: 0.2,
        max_points: None,
        ..Default::default()
    };

    let views = vec![
        ViewConfigurationBuilder::new()
            .view_name("top")
            .rotation_ortho_top()
            .resolution_hd()
            .epipolar_options(epipolar_opts.clone())
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("front")
            .rotation_ortho_front()
            .resolution_hd()
            .epipolar_options(epipolar_opts.clone())
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("right")
            .rotation_ortho_right()
            .resolution_hd()
            .epipolar_options(epipolar_opts.clone())
            .build(),
    ];

    run_camera_pose_from_bundles_dataset_test(
        &markers,
        ground_truth_3d,
        8, // Expect at least 8 markers.
        dataset_name,
        &naming,
        views,
        focal_length,
        film_back,
        image_size,
        min_success_rate_percent,
        max_mean_error_pixels,
        max_max_error_pixels,
    )
}

#[test]
fn test_camera_pose_from_bundles_clean_cube_c() -> Result<()> {
    run_camera_pose_from_bundles_cube_c(false)
}

#[test]
fn test_camera_pose_from_bundles_noisy_cube_c() -> Result<()> {
    run_camera_pose_from_bundles_cube_c(true)
}
