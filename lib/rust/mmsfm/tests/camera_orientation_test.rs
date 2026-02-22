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

//! Camera orientation validation SfM visualization tests.

#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use crate::common::visualization::scene::{
    visualize_sfm_scene_views, ViewConfigurationBuilder,
};
use crate::common::{
    test_output_file_naming, OutputFileNaming, TestType, VisualizationType,
};
use anyhow::Result;
use mmsfm_rust::datatype::camera_pose::CameraPose;
use mmsfm_rust::datatype::CameraFilmBack;
use mmsfm_rust::datatype::CameraIntrinsics;
use mmsfm_rust::datatype::MillimeterUnit;
use mmsfm_rust::datatype::UnitValue;
use nalgebra::{Matrix3, Point3, Vector3};

#[test]
fn camera_orientation_validation_sfm_test() -> Result<()> {
    // Test to validate that camera frustums properly orient according
    // to camera pose rotation
    let intrinsics_a = CameraIntrinsics::from_centered_lens(
        MillimeterUnit::new(35.0),
        CameraFilmBack::from_millimeters(36.0, 24.0),
    );
    let intrinsics_b = intrinsics_a.clone();

    // Create two cameras with different rotations to test frustum
    // orientation
    let pose_a = CameraPose::default(); // Identity camera at origin

    // Create camera B with 90 degrees rotation around Y-axis (should
    // point sideways)
    let rotation_b = Matrix3::new(
        0.0, 0.0, 1.0, // X' = Z
        0.0, 1.0, 0.0, // Y' = Y
        -1.0, 0.0, 0.0, // Z' = -X (90 degrees rotation around Y)
    );
    let center_b = Vector3::new(5.0, 0.0, 0.0);
    let pose_b = CameraPose::new(rotation_b, center_b.into());

    // Create a simple scene
    let points_3d = vec![
        Point3::new(0.0, 0.0, -2.0), // In front of camera A (default)
        Point3::new(2.0, 0.0, 0.0),  // To the right of camera A
        Point3::new(3.0, 1.0, 2.0),  // Between cameras
        Point3::new(8.0, 0.0, 0.0),  // In front of camera B (rotated)
    ];

    // Test with multiple view configurations showing different angles.
    let views = vec![
        ViewConfigurationBuilder::new()
            .view_name("top")
            .rotation_ortho_top()
            .resolution_hd()
            .build(),
        ViewConfigurationBuilder::new()
            .view_name("viewA")
            .rotation_ortho_three_quarter_a()
            .resolution_hd()
            .build(),
    ];

    // Create output naming for visualizations
    let naming = test_output_file_naming(
        TestType::CameraOrientation,
        "validation",
        VisualizationType::Scene3d,
    );

    visualize_sfm_scene_views(
        &pose_a,
        &pose_b,
        &points_3d,
        "Camera Orientation Validation",
        &naming,
        views,
        &intrinsics_a,
        &intrinsics_b,
    )
}
