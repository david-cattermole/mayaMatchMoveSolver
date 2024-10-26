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

mod common;

use anyhow::Result;
use approx::assert_relative_eq;

use crate::common::chan_data_filter_only_x;
use crate::common::chan_data_filter_only_y;
use crate::common::construct_input_file_path;
use crate::common::construct_output_file_path;
use crate::common::find_data_dir;
#[allow(unused_imports)]
use crate::common::print_chan_data;
use crate::common::read_chan_file;
use crate::common::save_chart_linear_n3_regression;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::math::curve_fit::nonlinear_line_n3;

#[test]
fn linear_3_point_raw() -> Result<()> {
    let chart_title = "linear_3_point_raw";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "linear_3_point_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "linear_3_point_raw.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "linear_3_point_raw.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point_a, point_b, point_c) = nonlinear_line_n3(&x_values, &y_values)?;
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");

    save_chart_linear_n3_regression(
        &data_raw,
        &data,
        point_a,
        point_b,
        point_c,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_a.y(), -1.21533949192, epsilon = 1.0e-2);

    assert_relative_eq!(point_b.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), 4.5, epsilon = 1.0e-2);

    assert_relative_eq!(point_c.x(), 1101.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 1.855, epsilon = 1.0e-2);

    Ok(())
}

#[test]
fn linear_3_point_variance1() -> Result<()> {
    let chart_title = "linear_3_point_variance1";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "linear_3_point_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "linear_3_point_variance1.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "linear_3_point_variance1.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point_a, point_b, point_c) = nonlinear_line_n3(&x_values, &y_values)?;
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");

    save_chart_linear_n3_regression(
        &data_raw,
        &data,
        point_a,
        point_b,
        point_c,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_a.y(), -1.21533949192, epsilon = 1.0e-2);

    assert_relative_eq!(point_b.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), 4.5, epsilon = 1.0e-2);

    assert_relative_eq!(point_c.x(), 1101.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 1.855, epsilon = 1.0e-2);

    Ok(())
}

#[test]
fn linear_3_point_variance2() -> Result<()> {
    let chart_title = "linear_3_point_variance2";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "linear_3_point_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "linear_3_point_variance2.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "linear_3_point_variance2.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point_a, point_b, point_c) = nonlinear_line_n3(&x_values, &y_values)?;
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");

    save_chart_linear_n3_regression(
        &data_raw,
        &data,
        point_a,
        point_b,
        point_c,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_a.y(), -1.21533949192, epsilon = 1.0e-1);

    assert_relative_eq!(point_b.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), 4.5, epsilon = 1.0e-1);

    assert_relative_eq!(point_c.x(), 1101.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 1.855, epsilon = 1.0e-1);

    Ok(())
}

#[test]
fn linear_3_point_variance3() -> Result<()> {
    let chart_title = "linear_3_point_variance3";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "linear_3_point_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "linear_3_point_variance3.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "linear_3_point_variance3.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point_a, point_b, point_c) = nonlinear_line_n3(&x_values, &y_values)?;
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");

    save_chart_linear_n3_regression(
        &data_raw,
        &data,
        point_a,
        point_b,
        point_c,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_a.y(), -1.21533949192, epsilon = 0.3);

    assert_relative_eq!(point_b.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), 4.5, epsilon = 0.2);

    assert_relative_eq!(point_c.x(), 1101.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 1.855, epsilon = 0.3);

    Ok(())
}

#[test]
fn linear_3_point_variance4() -> Result<()> {
    let chart_title = "linear_3_point_variance4";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "linear_3_point_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "linear_3_point_variance4.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "linear_3_point_variance4.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point_a, point_b, point_c) = nonlinear_line_n3(&x_values, &y_values)?;
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");

    save_chart_linear_n3_regression(
        &data_raw,
        &data,
        point_a,
        point_b,
        point_c,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_a.y(), -1.21533949192, epsilon = 0.75);

    assert_relative_eq!(point_b.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), 4.5, epsilon = 2.0);

    assert_relative_eq!(point_c.x(), 1101.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 1.855, epsilon = 2.5);

    Ok(())
}
