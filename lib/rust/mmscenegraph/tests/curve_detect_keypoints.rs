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

#![allow(unused_imports)]
#![allow(unused_variables)]
#![allow(dead_code)]

mod common;

use anyhow::Result;

use crate::common::chan_data_filter_only_x;
use crate::common::chan_data_filter_only_y;
use crate::common::construct_input_file_path;
use crate::common::construct_output_file_path;
use crate::common::find_data_dir;
use crate::common::print_actual_pops;
use crate::common::print_chan_data;
use crate::common::read_chan_file;
use crate::common::save_chart_linear_n3_regression_pop;
use crate::common::save_chart_linear_n_points_regression;
use crate::common::save_chart_linear_n_points_regression_pop;
use crate::common::save_chart_linear_regression_pop;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::curve::detect::keypoints::analyze_curve;
use mmscenegraph_rust::curve::detect::keypoints::RankedKeypoint;
use mmscenegraph_rust::curve::detect::pops::detect_curve_pop_scores;
use mmscenegraph_rust::curve::detect::pops::detect_curve_pops;
use mmscenegraph_rust::curve::detect::pops::filter_curve_pops;
use mmscenegraph_rust::math::curve_fit::linear_regression;
use mmscenegraph_rust::math::curve_fit::nonlinear_line_n3;
use mmscenegraph_rust::math::curve_fit::nonlinear_line_n_points;
use mmscenegraph_rust::math::curve_fit::nonlinear_line_n_points_with_initial;
use mmscenegraph_rust::math::curve_fit::Point2;
use mmscenegraph_rust::math::interpolate::evaluate_curve_points;
use mmscenegraph_rust::math::interpolate::InterpolationMethod;

fn print_keypoints(keypoints: &[RankedKeypoint]) {
    println!("keypoints.len()={:?}", keypoints.len());
    for (i, keypoint) in keypoints.iter().enumerate() {
        println!("keypoints[{i}]={keypoint:?}");
    }
}

fn print_points(points: &[Point2]) {
    println!("points.len()={:?}", points.len());
    for (i, point) in points.iter().enumerate() {
        println!("points[{i}]={point:?}");
    }
}

fn keypoints_common(
    chart_title: &str,
    in_file_name: &str,
    out_file_name: &str,
    target_keypoints: usize,
) -> Result<()> {
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path = construct_input_file_path(&data_dir, in_file_name)?;
    let out_file_path = construct_output_file_path(&data_dir, out_file_name)?;

    let data_raw = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data_raw);
    let x_values = chan_data_filter_only_x(&data_raw);
    let y_values = chan_data_filter_only_y(&data_raw);

    let keypoints = analyze_curve(&x_values, &y_values, target_keypoints)?;
    print_keypoints(&keypoints);

    let x_values_keypoint: Vec<Real> =
        keypoints.iter().map(|x| x.time as Real).collect();
    let y_values_keypoint: Vec<Real> =
        keypoints.iter().map(|x| x.value as Real).collect();
    let xy_values_keypoint: Vec<(Real, Real)> = keypoints
        .iter()
        .map(|x| (x.time as Real, x.value as Real))
        .collect();

    let mut weights = vec![0.0; x_values.len()];
    detect_curve_pop_scores(&x_values, &y_values, &mut weights)?;
    // println!("weights: {weights:?}");
    assert_eq!(x_values.len(), weights.len());
    for i in 0..weights.len() {
        weights[i] = 1.0 / weights[i];
    }
    // println!("weights: {weights:?}");
    // assert!(false);

    let interpolation_method = InterpolationMethod::CubicNUBS;
    let points = nonlinear_line_n_points_with_initial(
        &x_values,
        &y_values,
        &x_values_keypoint,
        &y_values_keypoint,
        &weights,
        interpolation_method,
    )?;
    print_points(&points);

    let control_points_x: Vec<Real> =
        points.iter().map(|p| p.x() as Real).collect();
    let control_points_y: Vec<Real> =
        points.iter().map(|p| p.y() as Real).collect();
    let xy_values_eval = evaluate_curve_points(
        &x_values,
        &control_points_x,
        &control_points_y,
        interpolation_method,
    );

    save_chart_linear_n_points_regression(
        &data_raw,
        &xy_values_eval,
        &points,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_eq!(points.len(), x_values_keypoint.len());

    Ok(())
}

#[test]
fn keypoints_bounce_5_up_down_raw() -> Result<()> {
    let chart_title = "keypoints_bounce_5_up_down_raw";
    let in_file_name = "bounce_5_up_down_raw.chan";
    let out_file_name = "keypoints_bounce_5_up_down_raw.png";
    let target_keypoints = 10;
    keypoints_common(chart_title, in_file_name, out_file_name, target_keypoints)
}

#[test]
fn keypoints_bounce_5_up_down_variance2() -> Result<()> {
    let chart_title = "keypoints_bounce_5_up_down_variance2";
    let in_file_name = "bounce_5_up_down_variance2.chan";
    let out_file_name = "keypoints_bounce_5_up_down_variance2.png";
    let target_keypoints = 10;
    keypoints_common(chart_title, in_file_name, out_file_name, target_keypoints)
}

#[test]
fn keypoints_bounce_5_up_down_pop2() -> Result<()> {
    let chart_title = "keypoints_bounce_5_up_down_pop2";
    let in_file_name = "bounce_5_up_down_pop2.chan";
    let out_file_name = "keypoints_bounce_5_up_down_pop2.png";
    let target_keypoints = 10;
    keypoints_common(chart_title, in_file_name, out_file_name, target_keypoints)
}
