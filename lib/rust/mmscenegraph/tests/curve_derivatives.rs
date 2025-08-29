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
use approx::assert_relative_eq;

use crate::common::chan_data_combine_xy;
use crate::common::chan_data_filter_only_x;
use crate::common::chan_data_filter_only_y;
use crate::common::construct_input_file_path;
use crate::common::construct_output_file_path;
use crate::common::find_data_dir;
use crate::common::find_output_dir;
use crate::common::print_chan_data;
use crate::common::print_derivative_arrays;
use crate::common::read_chan_file;
use crate::common::save_chart_derivative_curves;
use crate::common::save_chart_linear_regression;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::curve::derivatives::allocate_derivatives_order_3;
use mmscenegraph_rust::curve::derivatives::calculate_derivatives_order_3;

#[test]
fn calculate_derivatives1() -> Result<()> {
    let chart_title = "calculate_derivatives1";
    let chart_resolution = CHART_RESOLUTION;

    let output_dir = find_output_dir()?;
    let out_file_path =
        construct_output_file_path(&output_dir, "calculate_derivatives1.png")?;

    // Constant speed, upwards.
    let x_values = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0];
    let y_values = vec![1.0, 1.1, 1.2, 1.3, 1.4, 1.5];

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data = chan_data_combine_xy(&x_values, &y_values);
    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_eq!(velocity.len(), 6);
    assert_eq!(acceleration.len(), 6);
    assert_eq!(jerk.len(), 6);

    assert_relative_eq!(velocity[0], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[1], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[2], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[3], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[4], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[5], 0.1, epsilon = 1.0e-9);

    assert_relative_eq!(acceleration[0], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[1], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[2], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[4], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[5], 0.0, epsilon = 1.0e-9);

    assert_relative_eq!(jerk[0], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[1], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[2], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[4], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[5], 0.0, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn calculate_derivatives2() -> Result<()> {
    let chart_title = "calculate_derivatives2";
    let chart_resolution = CHART_RESOLUTION;

    let output_dir = find_output_dir()?;
    let out_file_path =
        construct_output_file_path(&output_dir, "calculate_derivatives2.png")?;

    // Constant velocity, downwards.
    let x_values = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0];
    let y_values = vec![-1.0, -1.1, -1.2, -1.3, -1.4, -1.5];

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data = chan_data_combine_xy(&x_values, &y_values);
    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_eq!(velocity.len(), 6);
    assert_eq!(acceleration.len(), 6);
    assert_eq!(jerk.len(), 6);

    assert_relative_eq!(velocity[0], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[1], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[2], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[3], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[4], -0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[5], -0.1, epsilon = 1.0e-9);

    assert_relative_eq!(acceleration[0], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[1], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[2], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[4], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[5], 0.0, epsilon = 1.0e-9);

    assert_relative_eq!(jerk[0], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[1], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[2], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[4], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[5], 0.0, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn calculate_derivatives3() -> Result<()> {
    let chart_title = "calculate_derivatives3";
    let chart_resolution = CHART_RESOLUTION;

    let output_dir = find_output_dir()?;
    let out_file_path =
        construct_output_file_path(&output_dir, "calculate_derivatives3.png")?;

    // Variable velocity.
    let x_values = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0];
    let y_values = vec![1.0, 1.1, 1.25, 1.5, 2.0, 4.0];

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data = chan_data_combine_xy(&x_values, &y_values);
    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_eq!(velocity.len(), 6);
    assert_eq!(acceleration.len(), 6);
    assert_eq!(jerk.len(), 6);

    assert_relative_eq!(velocity[0], 0.1, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[1], 0.125, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[2], 0.2, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[3], 0.375, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[4], 1.25, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[5], 2.0, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn calculate_derivatives4() -> Result<()> {
    let chart_title = "calculate_derivatives4";
    let chart_resolution = CHART_RESOLUTION;

    let output_dir = find_output_dir()?;
    let out_file_path =
        construct_output_file_path(&output_dir, "calculate_derivatives4.png")?;

    let x_values = vec![0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0];
    let y_values = vec![0.0, 1.0, 4.0, 9.0, 16.0, 25.0, 36.0]; // f(x) = x^2

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data = chan_data_combine_xy(&x_values, &y_values);
    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_eq!(velocity.len(), 7);
    assert_eq!(acceleration.len(), 7);
    assert_eq!(jerk.len(), 7);

    // Expected derivatives of x^2;
    assert_relative_eq!(velocity[0], 1.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[1], 2.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[2], 4.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[3], 6.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[4], 8.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[5], 10.0, epsilon = 1.0e-9);
    assert_relative_eq!(velocity[6], 11.0, epsilon = 1.0e-9);

    assert_relative_eq!(acceleration[0], 1.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[1], 1.5, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[2], 2.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[3], 2.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[4], 2.0, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[5], 1.5, epsilon = 1.0e-9);
    assert_relative_eq!(acceleration[6], 1.0, epsilon = 1.0e-9);

    assert_relative_eq!(jerk[0], 0.5, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[1], 0.5, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[2], 0.25, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[3], 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[4], -0.25, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[5], -0.5, epsilon = 1.0e-9);
    assert_relative_eq!(jerk[6], -0.5, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn calculate_derivatives_identity_pop1() -> Result<()> {
    let chart_title = "derivatives_identity_pop1";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_pop1.chan")?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "derivatives_identity_pop1.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn calculate_derivatives_identity_pop2() -> Result<()> {
    let chart_title = "derivatives_identity_pop2";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_pop2.chan")?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "derivatives_identity_pop2.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn calculate_derivatives_identity_pop3() -> Result<()> {
    let chart_title = "derivatives_identity_pop3";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_pop3.chan")?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "derivatives_identity_pop3.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn calculate_derivatives_identity_pop4() -> Result<()> {
    let chart_title = "derivatives_identity_pop4";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_pop4.chan")?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "derivatives_identity_pop4.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn calculate_derivatives_bounce_5_up_down_raw() -> Result<()> {
    let chart_title = "derivatives_bounce_5_up_down_raw";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path =
        construct_input_file_path(&data_dir, "bounce_5_up_down_raw.chan")?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "derivatives_bounce_5_up_down_raw.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn calculate_derivatives_bounce_5_up_down_variance1() -> Result<()> {
    let chart_title = "derivatives_bounce_5_up_down_variance1";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance1.chan",
    )?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "derivatives_bounce_5_up_down_variance1.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn calculate_derivatives_bounce_5_up_down_variance2() -> Result<()> {
    let chart_title = "derivatives_bounce_5_up_down_variance2";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance2.chan",
    )?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "derivatives_bounce_5_up_down_variance2.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn calculate_derivatives_bounce_5_up_down_variance3() -> Result<()> {
    let chart_title = "derivatives_bounce_5_up_down_variance3";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance3.chan",
    )?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "derivatives_bounce_5_up_down_variance3.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn calculate_derivatives_bounce_5_up_down_variance4() -> Result<()> {
    let chart_title = "derivatives_bounce_5_up_down_variance4";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance4.chan",
    )?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "derivatives_bounce_5_up_down_variance4.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (mut velocity, mut acceleration, mut jerk) =
        allocate_derivatives_order_3(x_values.len())?;
    calculate_derivatives_order_3(
        &x_values,
        &y_values,
        &mut velocity,
        &mut acceleration,
        &mut jerk,
    )?;

    print_derivative_arrays(&velocity, &acceleration, &jerk);

    let data_velocity = chan_data_combine_xy(&x_values, &velocity);
    let data_acceleration = chan_data_combine_xy(&x_values, &acceleration);
    let data_jerk = chan_data_combine_xy(&x_values, &jerk);

    save_chart_derivative_curves(
        &data,
        &data_velocity,
        &data_acceleration,
        &data_jerk,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}
