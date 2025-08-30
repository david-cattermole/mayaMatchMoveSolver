//
// Copyright (C) 2024 David Cattermole.
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

use mmscenegraph_rust::constant::FrameTime;
use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::math::curve_fit::AngleRadian;
use mmscenegraph_rust::math::curve_fit::Point2;
use mmscenegraph_rust::math::interpolate::evaluate_curve_points;
use mmscenegraph_rust::math::interpolate::Interpolation;

// Generate fitted line Y values for given X coordinates using point and angle.
pub fn generate_fitted_line_values(
    x_coordinates: &[FrameTime],
    point: Point2,
    angle: AngleRadian,
) -> Vec<Real> {
    let (dir_x, dir_y) = angle.as_direction();
    let slope = if dir_x.abs() < 1e-10 {
        // Vertical line case - use a very large slope.
        if dir_y > 0.0 {
            1e10
        } else {
            -1e10
        }
    } else {
        dir_y / dir_x
    };

    // Line equation: y = point.y + slope * (x - point.x)
    x_coordinates
        .iter()
        .map(|&x| point.y() + slope * (x as Real - point.x()))
        .collect()
}

// Create a control points line with proper type conversion.
pub fn create_control_points_line(points: &[Point2]) -> Vec<(f64, Real)> {
    points.iter().map(|p| (p.x() as f64, p.y())).collect()
}

pub fn create_control_points_from_points(
    point_a: Point2,
    point_b: Point2,
    point_c: Point2,
) -> Vec<(f64, Real)> {
    let mut line = Vec::<(FrameTime, Real)>::new();
    line.push((point_a.x(), point_a.y()));
    line.push((point_b.x(), point_b.y()));
    line.push((point_c.x(), point_c.y()));
    line
}

// Create interpolated curve using proper interpolation method instead
// of just connecting control points.
pub fn create_interpolated_curve_from_control_points(
    x_sample_values: &[f64],
    control_points: &[Point2],
    interpolation_method: Interpolation,
) -> Vec<(FrameTime, Real)> {
    let control_points_x: Vec<f64> =
        control_points.iter().map(|p| p.x()).collect();
    let control_points_y: Vec<f64> =
        control_points.iter().map(|p| p.y()).collect();

    evaluate_curve_points(
        x_sample_values,
        &control_points_x,
        &control_points_y,
        interpolation_method,
    )
}

pub fn create_interpolated_curve_from_3_points(
    x_sample_values: &[f64],
    point_a: Point2,
    point_b: Point2,
    point_c: Point2,
    interpolation_method: Interpolation,
) -> Vec<(f64, Real)> {
    let control_points = vec![point_a, point_b, point_c];
    create_interpolated_curve_from_control_points(
        x_sample_values,
        &control_points,
        interpolation_method,
    )
}

pub fn create_control_points_from_point_and_dir(
    point: Point2,
    dir_x: Real,
    dir_y: Real,
) -> Vec<(f64, Real)> {
    let mut line = Vec::<(FrameTime, Real)>::new();
    line.push(((point.x() as Real - dir_x) as FrameTime, point.y() - dir_y));
    line.push((point.x() as FrameTime, point.y()));
    line.push(((point.x() as Real + dir_x) as FrameTime, point.y() + dir_y));
    line
}
