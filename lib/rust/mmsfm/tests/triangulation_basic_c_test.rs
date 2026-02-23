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

//! Triangulation test with camera B above, tilted down 10 degrees.

#![allow(unused)]
#![allow(unused_imports)]
#![allow(dead_code)]
#![allow(non_snake_case)]

mod common;

use crate::common::triangulation_utils::{
    create_synthetic_3d_points_grid, forward_project_points_to_nview,
};
use crate::common::{
    create_synthetic_camera_setup_with_config, run_triangulate_all_methods,
    CameraConfiguration,
};
use crate::common::{
    test_output_file_naming, OutputFileNaming, TestType, VisualizationType,
};
use anyhow::Result;
use mmsfm_rust::datatype::conversions::convert_ndc_to_uv_points;
use mmsfm_rust::datatype::{ImageSize, NdcValue};
use nalgebra::Point3;

#[test]
fn triangulation_c_test() -> Result<()> {
    let config = CameraConfiguration::new_tilt(
        Point3::new(0.0, 5.0, 0.0), // 5 units up.
        -10.0,                      // 10 degrees down tilt.
    );
    let (pose_a, pose_b, intrinsics_a, intrinsics_b) =
        create_synthetic_camera_setup_with_config(&config)?;

    // Grid of 3D points at Z=-20 (in front of both cameras).
    let points_3d = create_synthetic_3d_points_grid(3, 2.0, -20.0, 0.0);

    let ndc_points_all_cameras = forward_project_points_to_nview(
        &points_3d,
        &[pose_a.clone(), pose_b.clone()],
        &[intrinsics_a.clone(), intrinsics_b.clone()],
    )?;

    let ndc_points_a = &ndc_points_all_cameras[0];
    let ndc_points_b = &ndc_points_all_cameras[1];

    let uv_coords_a = convert_ndc_to_uv_points(ndc_points_a);
    let uv_coords_b = convert_ndc_to_uv_points(ndc_points_b);

    let naming = test_output_file_naming(
        TestType::Triangulation,
        "basic_c",
        VisualizationType::Scene3d,
    );

    run_triangulate_all_methods(
        &uv_coords_a,
        &uv_coords_b,
        ndc_points_a,
        ndc_points_b,
        &pose_a,
        &pose_b,
        &intrinsics_a,
        &intrinsics_b,
        "Triangulation Basic - C",
        &naming,
        ImageSize::full_hd(),
        true, // All points should be in front of cameras.
        1.0,  // Max reprojection error (pixels).
    )?;

    Ok(())
}
