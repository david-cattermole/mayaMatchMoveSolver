//
// Copyright (C) 2020, 2021 David Cattermole.
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

#[macro_use]
extern crate approx;

use nalgebra as na;

use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::math::camera::get_projection_matrix;
use mmscenegraph_rust::math::camera::FilmFit;
use mmscenegraph_rust::math::reprojection::reproject_as_normalised_coord;
use mmscenegraph_rust::math::rotate::euler::RotateOrder;
use mmscenegraph_rust::math::transform::calculate_matrix;
use mmscenegraph_rust::math::transform::multiply;
use mmscenegraph_rust::math::transform::Transform;

const EPSILON: Real = 1.0e-5;

#[test]
fn single_point() {
    // Test with both translation and rotation of the camera matrix.

    // 3D Point to be reprojected
    let px = -0.5;
    let py = 2.7;
    let pz = 0.0;

    // Camera Transform Values
    let tx = -2.0;
    let ty = 2.0;
    let tz = 5.0;
    let rx = 10.0;
    let ry = -10.0;
    let rz = -10.0;

    // Camera Projection Values
    let focal_length = 35.0;
    let film_back_width = 36.0 / 25.4;
    let film_back_height = 24.0 / 25.4;
    let film_offset_x = 0.0;
    let film_offset_y = 0.0;
    let image_width = 2048.0; // 3600.0; // 960.0;
    let image_height = 1556.0; // 2400.0; // 540.0;
    let film_fit = FilmFit::Horizontal;
    let near_clip_plane = 0.1;
    let far_clip_plane = 10000.0;
    let camera_scale = 1.0;

    // Compute
    let roo_xyz = RotateOrder::XYZ;
    let camera_transform =
        Transform::from_txyz_rxyz(tx, ty, tz, rx, ry, rz, roo_xyz);
    let camera_transform_matrix = calculate_matrix(&camera_transform);
    let camera_projection_matrix = get_projection_matrix(
        focal_length,
        film_back_width,
        film_back_height,
        film_offset_x,
        film_offset_y,
        image_width,
        image_height,
        film_fit,
        near_clip_plane,
        far_clip_plane,
        camera_scale,
    );
    let point = na::Matrix4::<Real>::new(
        1.0, 0.0, 0.0, px, //
        0.0, 1.0, 0.0, py, //
        0.0, 0.0, 1.0, pz, //
        0.0, 0.0, 0.0, 1.0, //
    );
    let screen_point = reproject_as_normalised_coord(
        camera_transform_matrix,
        camera_projection_matrix,
        point,
    );

    assert_relative_eq!(screen_point.x, 0.0865145148481126, epsilon = EPSILON);
    assert_relative_eq!(screen_point.y, 0.0096299819122515, epsilon = EPSILON);
}

#[test]
fn two_bundles_under_group() {
    let roo_xyz = RotateOrder::XYZ;
    let group_tfm =
        Transform::from_txyz_rxyz(0.0, 0.0, -10.0, 0.0, 15.0, 0.0, roo_xyz);

    let bundle_a_tfm = Transform::from_txyz(-5.0, 0.0, 0.0);
    let bundle_b_tfm = Transform::from_txyz(5.0, 0.0, 0.0);

    let roo_zxy = RotateOrder::ZXY;
    let camera_transform =
        Transform::from_txyz_rxyz(0.0, 5.0, 10.0, -10.0, 0.0, 0.0, roo_zxy);

    let focal_length = 35.0;
    let film_back_width = 36.0 / 25.4;
    let film_back_height = 24.0 / 25.4;
    let film_offset_x = 0.0;
    let film_offset_y = 0.0;
    let image_width = 2048.0; // 3600.0; // 960.0;
    let image_height = 1556.0; // 2400.0; // 540.0;
    let film_fit = FilmFit::Horizontal;
    let near_clip_plane = 0.1;
    let far_clip_plane = 10000.0;
    let camera_scale = 1.0;
    let camera_projection_matrix = get_projection_matrix(
        focal_length,
        film_back_width,
        film_back_height,
        film_offset_x,
        film_offset_y,
        image_width,
        image_height,
        film_fit,
        near_clip_plane,
        far_clip_plane,
        camera_scale,
    );
    // println!("Camera Projection Matrix: {}", camera_projection_matrix);

    let camera_transform_matrix = calculate_matrix(&camera_transform);
    println!("Camera Transform Matrix: {}", camera_transform_matrix);
    let expected_result = na::Matrix4::<Real>::new(
        1.0, 0.0, 0.0, 0.0, //
        0.0, 0.984808, -0.173648, 0.0, //
        0.0, 0.173648, 0.984808, 0.0, //
        0.0, 5.0, 10.0, 1.0, //
    )
    .transpose();
    let eq =
        camera_transform_matrix.relative_eq(&expected_result, EPSILON, EPSILON);
    assert_eq!(eq, true,);

    let bundle_a_matrix = multiply(&group_tfm, &bundle_a_tfm);
    println!("Bundle A: {}", bundle_a_matrix);
    let expected_result = na::Matrix4::<Real>::new(
        0.965926, 0.0, -0.258819, 0.0, //
        0.0, 1.0, 0.0, 0.0, //
        0.258819, 0.0, 0.965926, 0.0, //
        -4.829629, 0.0, -8.705905, 1.0, //
    )
    .transpose();
    let eq = bundle_a_matrix.relative_eq(&expected_result, EPSILON, EPSILON);
    assert_eq!(eq, true);

    let bundle_b_matrix = multiply(&group_tfm, &bundle_b_tfm);
    println!("Bundle B: {}", bundle_b_matrix);
    let expected_result = na::Matrix4::<Real>::new(
        0.965926, 0.0, -0.258819, 0.0, //
        0.0, 1.0, 0.0, 0.0, //
        0.258819, 0.0, 0.965926, 0.0, //
        4.829629, 0.0, -11.294095, 1.0, //
    )
    .transpose();
    let eq = bundle_b_matrix.relative_eq(&expected_result, EPSILON, EPSILON);
    assert_eq!(eq, true);

    let screen_point_a = reproject_as_normalised_coord(
        camera_transform_matrix,
        camera_projection_matrix,
        bundle_a_matrix,
    );
    println!("Screen-Point A: {}", screen_point_a);

    let screen_point_b = reproject_as_normalised_coord(
        camera_transform_matrix,
        camera_projection_matrix,
        bundle_b_matrix,
    );
    println!("Screen-Point B: {}", screen_point_b);

    assert_relative_eq!(screen_point_a.x, -0.243416, epsilon = EPSILON);
    assert_relative_eq!(screen_point_a.y, -0.111167, epsilon = EPSILON);

    assert_relative_eq!(screen_point_b.x, 0.2150060, epsilon = EPSILON);
    assert_relative_eq!(screen_point_b.y, -0.071858, epsilon = EPSILON);
}
