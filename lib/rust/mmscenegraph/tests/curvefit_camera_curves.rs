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
// Curve-fitting tests with camera data.
//
// Tests curve fitting functions using realistic camera animation curves:
// - 2-point linear regression tests (linear_regression function)
// - 3-point curve fitting tests (nonlinear_line_n_points function with Linear and QuadraticNUBS)
// - 4-point curve fitting tests (nonlinear_line_n_points function with Linear, QuadraticNUBS, and CubicNUBS)
// - 5-point curve fitting tests (nonlinear_line_n_points function with Linear, QuadraticNUBS, and CubicNUBS)
// - 16-point curve fitting tests (nonlinear_line_n_points function with Linear, QuadraticNUBS, and CubicNUBS)
//
// Features tested:
// - Quality of fit metrics using NRMSE
// - Bounds validation (with noted algorithmic finding)
// - Multiple interpolation methods: Linear, QuadraticNUBS, CubicNUBS
//

#![allow(unused_imports)]
#![allow(unused_variables)]
#![allow(dead_code)]

mod common;

use anyhow::Result;
use approx::assert_relative_eq;

use crate::common::calculate_quality_of_fit;
use crate::common::chan_data_filter_only_x;
use crate::common::chan_data_filter_only_y;
use crate::common::construct_input_file_path;
use crate::common::construct_output_file_path;
use crate::common::find_data_dir;
use crate::common::find_output_dir;
use crate::common::print_chan_data;
use crate::common::read_chan_file;
use crate::common::save_chart_linear_regression;
use crate::common::save_chart_n_points_regression;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::math::curve_fit::linear_regression;
use mmscenegraph_rust::math::curve_fit::nonlinear_line_n_points;
use mmscenegraph_rust::math::curve_fit::AngleRadian;
use mmscenegraph_rust::math::curve_fit::Point2;
use mmscenegraph_rust::math::interpolate::Interpolation;
use mmscenegraph_rust::math::statistics::calc_normalized_root_mean_square_error;

/// Generate predicted values from 2-point linear regression.
fn generate_predicted_values_linear_regression(
    x_values: &[f64],
    point: Point2,
    angle: AngleRadian,
) -> Vec<f64> {
    let slope = angle.value().tan();
    x_values
        .iter()
        .map(|&x| point.y() + slope * (x - point.x()))
        .collect()
}

/// Generate predicted values from N control points using linear interpolation.
fn generate_predicted_values_n_points(
    x_values: &[f64],
    control_points: &[Point2],
) -> Vec<f64> {
    x_values
        .iter()
        .map(|&x| {
            // Find the two control points to interpolate between.
            let mut y = control_points[0].y(); // Default to first point.

            for i in 0..(control_points.len() - 1) {
                let x0 = control_points[i].x();
                let x1 = control_points[i + 1].x();

                if x >= x0 && x <= x1 {
                    let y0 = control_points[i].y();
                    let y1 = control_points[i + 1].y();
                    let t = (x - x0) / (x1 - x0);
                    y = y0 + t * (y1 - y0);
                    break;
                }
            }

            y
        })
        .collect()
}

/// Assert that curve bounds match data bounds.
fn assert_bounds_correctness(
    x_values: &[f64],
    y_values: &[f64],
    control_points: &[Point2],
) {
    let data_x_min = x_values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
    let data_x_max = x_values.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
    let data_y_min = y_values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
    let data_y_max = y_values.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));

    let control_x_min = control_points
        .iter()
        .map(|p| p.x())
        .fold(f64::INFINITY, |a, b| a.min(b));
    let control_x_max = control_points
        .iter()
        .map(|p| p.x())
        .fold(f64::NEG_INFINITY, |a, b| a.max(b));

    // NOTE: Ideally, control points should span at least the full range of sample data
    // (control_x_min <= data_x_min and control_x_max >= data_x_max)

    let x_range = data_x_max - data_x_min;
    let bounds_tolerance = x_range * 0.05; // Allow 5% deviation from ideal bounds.

    // Check that control points approximately span the data range
    assert!(
        control_x_min <= data_x_min + bounds_tolerance,
        "Control X minimum {} is too far from data minimum {} (tolerance: {})",
        control_x_min,
        data_x_min,
        bounds_tolerance
    );
    assert!(
        control_x_max >= data_x_max - bounds_tolerance,
        "Control X maximum {} is too far from data maximum {} (tolerance: {})",
        control_x_max,
        data_x_max,
        bounds_tolerance
    );
}

// 2-Point Linear Regression Tests.
fn curvefit_camera_curves_2_point_linear_common(
    chart_title: &str,
    in_file_name: &str,
    out_file_name: &str,
    min_quality: f64,
) -> Result<()> {
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(&data_dir, in_file_name)?;
    let out_file_path = construct_output_file_path(&output_dir, out_file_name)?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point, angle) = linear_regression(&x_values, &y_values)?;
    println!("2-point: point={point:?} angle={angle:?}");

    // Generate predicted values and calculate quality.
    let predicted_values =
        generate_predicted_values_linear_regression(&x_values, point, angle);
    let quality = calculate_quality_of_fit(&y_values, &predicted_values)?;
    println!("2-point quality: {:.2}%", quality);

    // Assert quality.
    assert!(
        quality >= min_quality,
        "Quality {:.2}% is below minimum {:.2}%",
        quality,
        min_quality
    );

    // Assert bounds.
    let data_x_min = x_values.iter().fold(f64::INFINITY, |a, &b| a.min(b));
    let data_x_max = x_values.iter().fold(f64::NEG_INFINITY, |a, &b| a.max(b));
    assert!(
        point.x() >= data_x_min && point.x() <= data_x_max,
        "Point x-coordinate {} is outside data range [{}, {}]",
        point.x(),
        data_x_min,
        data_x_max
    );

    save_chart_linear_regression(
        &data,
        &data,
        point,
        angle,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

// N-Point Curve Fitting Tests.
fn curvefit_camera_curves_npoint_common(
    chart_title: &str,
    in_file_name: &str,
    out_file_name: &str,
    n_points: usize,
    min_quality: f64,
    interpolation_method: Interpolation,
) -> Result<()> {
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(&data_dir, in_file_name)?;
    let out_file_path = construct_output_file_path(&output_dir, out_file_name)?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let control_points = nonlinear_line_n_points(
        &x_values,
        &y_values,
        n_points,
        interpolation_method,
    )?;
    println!("{}-point: control_points={control_points:?}", n_points);

    // Generate predicted values and calculate quality.
    let predicted_values =
        generate_predicted_values_n_points(&x_values, &control_points);
    let quality = calculate_quality_of_fit(&y_values, &predicted_values)?;
    println!("{}-point quality: {:.2}%", n_points, quality);

    // Assert quality.
    assert!(
        quality >= min_quality,
        "Quality {:.2}% is below minimum {:.2}%",
        quality,
        min_quality
    );

    // Assert bounds correctness.
    assert_bounds_correctness(&x_values, &y_values, &control_points);

    save_chart_n_points_regression(
        &data,
        &data,
        &control_points,
        interpolation_method,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

// 2-Point Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_2_point_linear() -> Result<()> {
    curvefit_camera_curves_2_point_linear_common(
        "FocalLength 2-Point Linear",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_2_point_linear.png",
        50.0,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_2_point_linear() -> Result<()> {
    curvefit_camera_curves_2_point_linear_common(
        "RotateX 2-Point Linear",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_2_point_linear.png",
        70.0,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_2_point_linear() -> Result<()> {
    curvefit_camera_curves_2_point_linear_common(
        "RotateY 2-Point Linear",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_2_point_linear.png",
        50.0,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_2_point_linear() -> Result<()> {
    curvefit_camera_curves_2_point_linear_common(
        "RotateZ 2-Point Linear",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_2_point_linear.png",
        50.0,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_2_point_linear() -> Result<()> {
    curvefit_camera_curves_2_point_linear_common(
        "TranslateX 2-Point Linear",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_2_point_linear.png",
        50.0,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_2_point_linear() -> Result<()> {
    curvefit_camera_curves_2_point_linear_common(
        "TranslateY 2-Point Linear",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_2_point_linear.png",
        50.0,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_2_point_linear() -> Result<()> {
    curvefit_camera_curves_2_point_linear_common(
        "TranslateZ 2-Point Linear",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_2_point_linear.png",
        50.0,
    )
}

// 3-Point Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_3_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 3-Point Linear",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_3_point_linear.png",
        3,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_3_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 3-Point Linear",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_3_point_linear.png",
        3,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_3_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 3-Point Linear",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_3_point_linear.png",
        3,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_3_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 3-Point Linear",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_3_point_linear.png",
        3,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_3_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 3-Point Linear",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_3_point_linear.png",
        3,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_3_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 3-Point Linear",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_3_point_linear.png",
        3,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_3_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 3-Point Linear",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_3_point_linear.png",
        3,
        50.0,
        Interpolation::Linear,
    )
}

// 3-Point QuadraticNUBS Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_3_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 3-Point QuadraticNUBS",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_3_point_quadratic_nubs.png",
        3,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_3_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 3-Point QuadraticNUBS",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_3_point_quadratic_nubs.png",
        3,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_3_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 3-Point QuadraticNUBS",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_3_point_quadratic_nubs.png",
        3,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_3_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 3-Point QuadraticNUBS",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_3_point_quadratic_nubs.png",
        3,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_3_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 3-Point QuadraticNUBS",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_3_point_quadratic_nubs.png",
        3,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_3_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 3-Point QuadraticNUBS",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_3_point_quadratic_nubs.png",
        3,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_3_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 3-Point QuadraticNUBS",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_3_point_quadratic_nubs.png",
        3,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

// 4-Point Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_4_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 4-Point CubicNUBS",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_4_point_cubic_nubs.png",
        4,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_4_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 4-Point CubicNUBS",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_4_point_cubic_nubs.png",
        4,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_4_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 4-Point CubicNUBS",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_4_point_cubic_nubs.png",
        4,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_4_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 4-Point CubicNUBS",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_4_point_cubic_nubs.png",
        4,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_4_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 4-Point CubicNUBS",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_4_point_cubic_nubs.png",
        4,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_4_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 4-Point CubicNUBS",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_4_point_cubic_nubs.png",
        4,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_4_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 4-Point CubicNUBS",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_4_point_cubic_nubs.png",
        4,
        50.0,
        Interpolation::CubicNUBS,
    )
}

// 4-Point Linear Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_4_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 4-Point Linear",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_4_point_linear.png",
        4,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_4_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 4-Point Linear",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_4_point_linear.png",
        4,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_4_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 4-Point Linear",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_4_point_linear.png",
        4,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_4_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 4-Point Linear",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_4_point_linear.png",
        4,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_4_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 4-Point Linear",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_4_point_linear.png",
        4,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_4_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 4-Point Linear",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_4_point_linear.png",
        4,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_4_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 4-Point Linear",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_4_point_linear.png",
        4,
        50.0,
        Interpolation::Linear,
    )
}

// 4-Point QuadraticNUBS Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_4_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 4-Point QuadraticNUBS",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_4_point_quadratic_nubs.png",
        4,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_4_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 4-Point QuadraticNUBS",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_4_point_quadratic_nubs.png",
        4,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_4_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 4-Point QuadraticNUBS",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_4_point_quadratic_nubs.png",
        4,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_4_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 4-Point QuadraticNUBS",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_4_point_quadratic_nubs.png",
        4,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_4_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 4-Point QuadraticNUBS",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_4_point_quadratic_nubs.png",
        4,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_4_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 4-Point QuadraticNUBS",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_4_point_quadratic_nubs.png",
        4,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_4_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 4-Point QuadraticNUBS",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_4_point_quadratic_nubs.png",
        4,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

// 5-Point Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_5_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 5-Point CubicNUBS",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_5_point_cubic_nubs.png",
        5,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_5_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 5-Point CubicNUBS",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_5_point_cubic_nubs.png",
        5,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_5_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 5-Point CubicNUBS",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_5_point_cubic_nubs.png",
        5,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_5_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 5-Point CubicNUBS",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_5_point_cubic_nubs.png",
        5,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_5_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 5-Point CubicNUBS",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_5_point_cubic_nubs.png",
        5,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_5_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 5-Point CubicNUBS",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_5_point_cubic_nubs.png",
        5,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_5_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 5-Point CubicNUBS",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_5_point_cubic_nubs.png",
        5,
        50.0,
        Interpolation::CubicNUBS,
    )
}

// 5-Point Linear Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_5_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 5-Point Linear",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_5_point_linear.png",
        5,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_5_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 5-Point Linear",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_5_point_linear.png",
        5,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_5_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 5-Point Linear",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_5_point_linear.png",
        5,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_5_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 5-Point Linear",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_5_point_linear.png",
        5,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_5_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 5-Point Linear",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_5_point_linear.png",
        5,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_5_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 5-Point Linear",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_5_point_linear.png",
        5,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_5_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 5-Point Linear",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_5_point_linear.png",
        5,
        50.0,
        Interpolation::Linear,
    )
}

// 5-Point QuadraticNUBS Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_5_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 5-Point QuadraticNUBS",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_5_point_quadratic_nubs.png",
        5,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_5_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 5-Point QuadraticNUBS",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_5_point_quadratic_nubs.png",
        5,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_5_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 5-Point QuadraticNUBS",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_5_point_quadratic_nubs.png",
        5,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_5_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 5-Point QuadraticNUBS",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_5_point_quadratic_nubs.png",
        5,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_5_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 5-Point QuadraticNUBS",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_5_point_quadratic_nubs.png",
        5,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_5_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 5-Point QuadraticNUBS",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_5_point_quadratic_nubs.png",
        5,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_5_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 5-Point QuadraticNUBS",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_5_point_quadratic_nubs.png",
        5,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

// 16-Point Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_16_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 16-Point CubicNUBS",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_16_point_cubic_nubs.png",
        16,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_16_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 16-Point CubicNUBS",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_16_point_cubic_nubs.png",
        16,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_16_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 16-Point CubicNUBS",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_16_point_cubic_nubs.png",
        16,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_16_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "16-Point RotateZ",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_16_point_cubic_nubs.png",
        16,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_16_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 16-Point CubicNUBS",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_16_point_cubic_nubs.png",
        16,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_16_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 16-Point CubicNUBS",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_16_point_cubic_nubs.png",
        16,
        50.0,
        Interpolation::CubicNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_16_point_cubic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 16-Point CubicNUBS",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_16_point_cubic_nubs.png",
        16,
        50.0,
        Interpolation::CubicNUBS,
    )
}

// 16-Point Linear Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_16_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 16-Point Linear",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_16_point_linear.png",
        16,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_16_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 16-Point Linear",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_16_point_linear.png",
        16,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_16_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 16-Point Linear",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_16_point_linear.png",
        16,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_16_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 16-Point Linear",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_16_point_linear.png",
        16,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_16_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 16-Point Linear",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_16_point_linear.png",
        16,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_16_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 16-Point Linear",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_16_point_linear.png",
        16,
        50.0,
        Interpolation::Linear,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_16_point_linear() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 16-Point Linear",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_16_point_linear.png",
        16,
        50.0,
        Interpolation::Linear,
    )
}

// 16-Point QuadraticNUBS Tests for All Camera Curves.
#[test]
fn curvefit_camera_curves_focal_length_16_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "FocalLength 16-Point QuadraticNUBS",
        "camera_curve_focalLength_raw.chan",
        "curvefit_camera_curves_focal_length_16_point_quadratic_nubs.png",
        16,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_x_16_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateX 16-Point QuadraticNUBS",
        "camera_curve_rotateX_raw.chan",
        "curvefit_camera_curves_rotate_x_16_point_quadratic_nubs.png",
        16,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_y_16_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateY 16-Point QuadraticNUBS",
        "camera_curve_rotateY_raw.chan",
        "curvefit_camera_curves_rotate_y_16_point_quadratic_nubs.png",
        16,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_rotate_z_16_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "RotateZ 16-Point QuadraticNUBS",
        "camera_curve_rotateZ_raw.chan",
        "curvefit_camera_curves_rotate_z_16_point_quadratic_nubs.png",
        16,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_x_16_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateX 16-Point QuadraticNUBS",
        "camera_curve_translateX_raw.chan",
        "curvefit_camera_curves_translate_x_16_point_quadratic_nubs.png",
        16,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_y_16_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateY 16-Point QuadraticNUBS",
        "camera_curve_translateY_raw.chan",
        "curvefit_camera_curves_translate_y_16_point_quadratic_nubs.png",
        16,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}

#[test]
fn curvefit_camera_curves_translate_z_16_point_quadratic_nubs() -> Result<()> {
    curvefit_camera_curves_npoint_common(
        "TranslateZ 16-Point QuadraticNUBS",
        "camera_curve_translateZ_raw.chan",
        "curvefit_camera_curves_translate_z_16_point_quadratic_nubs.png",
        16,
        50.0,
        Interpolation::QuadraticNUBS,
    )
}
