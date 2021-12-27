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

use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::math::rotate::euler::RotateOrder;
use mmscenegraph_rust::math::transform::multiply;
use mmscenegraph_rust::math::transform::Transform;

const EPSILON: Real = 1.0e-6;

#[test]
fn translate_y_only() {
    let tfm_a = Transform::from_txyz(0.0, 1.0, 0.0);
    let tfm_b = Transform::from_txyz(0.0, 41.0, 0.0);

    // Compute
    let matrix = multiply(&tfm_a, &tfm_b);

    println!("Matrix: {0}", matrix);
    //
    assert_relative_eq!(matrix[(0, 0)], 1.0);
    assert_relative_eq!(matrix[(0, 1)], 0.0);
    assert_relative_eq!(matrix[(0, 2)], 0.0);
    assert_relative_eq!(matrix[(0, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(1, 0)], 0.0);
    assert_relative_eq!(matrix[(1, 1)], 1.0);
    assert_relative_eq!(matrix[(1, 2)], 0.0);
    assert_relative_eq!(matrix[(1, 3)], 42.0);
    //
    assert_relative_eq!(matrix[(2, 0)], 0.0);
    assert_relative_eq!(matrix[(2, 1)], 0.0);
    assert_relative_eq!(matrix[(2, 2)], 1.0);
    assert_relative_eq!(matrix[(2, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(3, 0)], 0.0);
    assert_relative_eq!(matrix[(3, 1)], 0.0);
    assert_relative_eq!(matrix[(3, 2)], 0.0);
    assert_relative_eq!(matrix[(3, 3)], 1.0);
}

#[test]
fn translate_xyz() {
    let tfm_a = Transform::from_txyz(-1.1, 1.0, 2.5);
    let tfm_b = Transform::from_txyz(-42.0, 1.2, -20.0);

    // Compute
    let matrix = multiply(&tfm_a, &tfm_b);

    println!("Matrix: {0}", matrix);
    let tx = -1.1 + -42.0;
    let ty = 1.0 + 1.2;
    let tz = 2.5 + -20.0;
    //
    assert_relative_eq!(matrix[(0, 0)], 1.0);
    assert_relative_eq!(matrix[(0, 1)], 0.0);
    assert_relative_eq!(matrix[(0, 2)], 0.0);
    assert_relative_eq!(matrix[(0, 3)], tx);
    //
    assert_relative_eq!(matrix[(1, 0)], 0.0);
    assert_relative_eq!(matrix[(1, 1)], 1.0);
    assert_relative_eq!(matrix[(1, 2)], 0.0);
    assert_relative_eq!(matrix[(1, 3)], ty);
    //
    assert_relative_eq!(matrix[(2, 0)], 0.0);
    assert_relative_eq!(matrix[(2, 1)], 0.0);
    assert_relative_eq!(matrix[(2, 2)], 1.0);
    assert_relative_eq!(matrix[(2, 3)], tz);
    //
    assert_relative_eq!(matrix[(3, 0)], 0.0);
    assert_relative_eq!(matrix[(3, 1)], 0.0);
    assert_relative_eq!(matrix[(3, 2)], 0.0);
    assert_relative_eq!(matrix[(3, 3)], 1.0);
}

#[test]
fn rotate_y_only() {
    let tfm_a = Transform::from_rxyz(0.0, 90.0, 0.0, RotateOrder::XYZ);
    let tfm_b = Transform::from_rxyz(0.0, 90.0, 0.0, RotateOrder::XYZ);

    // Compute
    let matrix = multiply(&tfm_a, &tfm_b);

    println!("Matrix: {0}", matrix);
    //
    assert_relative_eq!(matrix[(0, 0)], -1.0);
    assert_relative_eq!(matrix[(0, 1)], 0.0);
    assert_relative_eq!(matrix[(0, 2)], 0.0);
    assert_relative_eq!(matrix[(0, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(1, 0)], 0.0);
    assert_relative_eq!(matrix[(1, 1)], 1.0);
    assert_relative_eq!(matrix[(1, 2)], 0.0);
    assert_relative_eq!(matrix[(1, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(2, 0)], 0.0);
    assert_relative_eq!(matrix[(2, 1)], 0.0);
    assert_relative_eq!(matrix[(2, 2)], -1.0);
    assert_relative_eq!(matrix[(2, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(3, 0)], 0.0);
    assert_relative_eq!(matrix[(3, 1)], 0.0);
    assert_relative_eq!(matrix[(3, 2)], 0.0);
    assert_relative_eq!(matrix[(3, 3)], 1.0);
}

#[test]
fn rotate_xyz_with_xyz_rotate_order() {
    let tfm_a = Transform::from_rxyz(45.0, 90.0, 45.0, RotateOrder::XYZ);
    let tfm_b = Transform::from_rxyz(-45.0, 90.0, 90.0, RotateOrder::XYZ);

    // Compute
    let matrix = multiply(&tfm_a, &tfm_b);

    println!("Matrix: {0}", matrix);
    //
    assert_relative_eq!(matrix[(0, 0)], -1.0);
    assert_relative_eq!(matrix[(0, 1)], 0.0);
    assert_relative_eq!(matrix[(0, 2)], 0.0);
    assert_relative_eq!(matrix[(0, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(1, 0)], 0.0);
    assert_relative_eq!(matrix[(1, 1)], -0.707107, epsilon = EPSILON);
    assert_relative_eq!(matrix[(1, 2)], 0.707107, epsilon = EPSILON);
    assert_relative_eq!(matrix[(1, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(2, 0)], 0.0);
    assert_relative_eq!(matrix[(2, 1)], 0.707107, epsilon = EPSILON);
    assert_relative_eq!(matrix[(2, 2)], 0.707107, epsilon = EPSILON);
    assert_relative_eq!(matrix[(2, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(3, 0)], 0.0);
    assert_relative_eq!(matrix[(3, 1)], 0.0);
    assert_relative_eq!(matrix[(3, 2)], 0.0);
    assert_relative_eq!(matrix[(3, 3)], 1.0);
}

#[test]
fn rotate_xyz_with_mixed_rotate_order() {
    let tfm_a = Transform::from_rxyz(45.0, 90.0, 45.0, RotateOrder::ZXY);
    let tfm_b = Transform::from_rxyz(-45.0, 90.0, 90.0, RotateOrder::ZYX);

    // Compute
    let matrix = multiply(&tfm_a, &tfm_b);

    println!("Matrix: {0}", matrix);
    //
    assert_relative_eq!(matrix[(0, 0)], -0.146447, epsilon = EPSILON);
    assert_relative_eq!(matrix[(0, 1)], 0.853553, epsilon = EPSILON);
    assert_relative_eq!(matrix[(0, 2)], 0.5);
    assert_relative_eq!(matrix[(0, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(1, 0)], 0.853553, epsilon = EPSILON);
    assert_relative_eq!(matrix[(1, 1)], -0.146447, epsilon = EPSILON);
    assert_relative_eq!(matrix[(1, 2)], 0.5);
    assert_relative_eq!(matrix[(1, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(2, 0)], 0.5);
    assert_relative_eq!(matrix[(2, 1)], 0.5);
    assert_relative_eq!(matrix[(2, 2)], -0.707107, epsilon = EPSILON);
    assert_relative_eq!(matrix[(2, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(3, 0)], 0.0);
    assert_relative_eq!(matrix[(3, 1)], 0.0);
    assert_relative_eq!(matrix[(3, 2)], 0.0);
    assert_relative_eq!(matrix[(3, 3)], 1.0);
}

#[test]
fn scale_y_only() {
    let tfm_a = Transform::from_sxyz(1.0, 100.0, 1.0);
    let tfm_b = Transform::from_sxyz(1.0, 0.1, 1.0);

    // Compute
    let matrix = multiply(&tfm_a, &tfm_b);

    println!("Matrix: {0}", matrix);
    //
    assert_relative_eq!(matrix[(0, 0)], 1.0);
    assert_relative_eq!(matrix[(0, 1)], 0.0);
    assert_relative_eq!(matrix[(0, 2)], 0.0);
    assert_relative_eq!(matrix[(0, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(1, 0)], 0.0);
    assert_relative_eq!(matrix[(1, 1)], 10.0);
    assert_relative_eq!(matrix[(1, 2)], 0.0);
    assert_relative_eq!(matrix[(1, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(2, 0)], 0.0);
    assert_relative_eq!(matrix[(2, 1)], 0.0);
    assert_relative_eq!(matrix[(2, 2)], 1.0);
    assert_relative_eq!(matrix[(2, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(3, 0)], 0.0);
    assert_relative_eq!(matrix[(3, 1)], 0.0);
    assert_relative_eq!(matrix[(3, 2)], 0.0);
    assert_relative_eq!(matrix[(3, 3)], 1.0);
}

#[test]
fn scale_xyz() {
    let tfm_a = Transform::from_sxyz(10.0, 100.0, -1.0);
    let tfm_b = Transform::from_sxyz(23.0, 0.1, 252.0);

    // Compute
    let matrix = multiply(&tfm_a, &tfm_b);

    println!("Matrix: {0}", matrix);
    //
    assert_relative_eq!(matrix[(0, 0)], 230.0);
    assert_relative_eq!(matrix[(0, 1)], 0.0);
    assert_relative_eq!(matrix[(0, 2)], 0.0);
    assert_relative_eq!(matrix[(0, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(1, 0)], 0.0);
    assert_relative_eq!(matrix[(1, 1)], 10.0);
    assert_relative_eq!(matrix[(1, 2)], 0.0);
    assert_relative_eq!(matrix[(1, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(2, 0)], 0.0);
    assert_relative_eq!(matrix[(2, 1)], 0.0);
    assert_relative_eq!(matrix[(2, 2)], -252.0);
    assert_relative_eq!(matrix[(2, 3)], 0.0);
    //
    assert_relative_eq!(matrix[(3, 0)], 0.0);
    assert_relative_eq!(matrix[(3, 1)], 0.0);
    assert_relative_eq!(matrix[(3, 2)], 0.0);
    assert_relative_eq!(matrix[(3, 3)], 1.0);
}
