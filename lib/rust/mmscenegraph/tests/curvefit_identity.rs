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
use crate::common::print_chan_data;
use crate::common::read_chan_file;
use crate::common::save_chart_linear_regression;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::math::curve_fit::linear_regression;

#[test]
fn identity_raw() -> Result<()> {
    let chart_title = "identity_raw";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "identity_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_raw.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "identity_raw.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point, slope) = linear_regression(&x_values, &y_values)?;
    println!("point={point:?} slope={slope:?}");

    save_chart_linear_regression(
        &data_raw,
        &data,
        point,
        slope,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 0.0, epsilon = 1.0e-9);
    assert_relative_eq!(slope.as_degrees(), 0.0, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn identity_variance1() -> Result<()> {
    let chart_title = "identity_variance1";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "identity_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_variance1.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "identity_variance1.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point, slope) = linear_regression(&x_values, &y_values)?;
    println!("point={point:?} slope={slope:?}");

    save_chart_linear_regression(
        &data_raw,
        &data,
        point,
        slope,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 0.0, epsilon = 1.0e-3);
    assert_relative_eq!(slope.as_degrees(), 0.0, epsilon = 1.0e-1);

    Ok(())
}

#[test]
fn identity_variance2() -> Result<()> {
    let chart_title = "identity_variance2";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "identity_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_variance2.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "identity_variance2.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point, slope) = linear_regression(&x_values, &y_values)?;
    println!("point={point:?} slope={slope:?}");

    save_chart_linear_regression(
        &data_raw,
        &data,
        point,
        slope,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 0.0, epsilon = 1.0e-2);
    assert_relative_eq!(slope.as_degrees(), 0.0, epsilon = 1.0);

    Ok(())
}

#[test]
fn identity_variance3() -> Result<()> {
    let chart_title = "identity_variance3";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "identity_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_variance3.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "identity_variance3.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point, slope) = linear_regression(&x_values, &y_values)?;
    println!("point={point:?} slope={slope:?}");

    save_chart_linear_regression(
        &data_raw,
        &data,
        point,
        slope,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 0.0, epsilon = 1.0e-1);
    assert_relative_eq!(slope.as_degrees(), 0.0, epsilon = 1.3);

    Ok(())
}

#[test]
fn identity_variance4() -> Result<()> {
    let chart_title = "identity_variance4";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_raw =
        construct_input_file_path(&data_dir, "identity_raw.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_variance4.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "identity_variance4.png")?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let (point, slope) = linear_regression(&x_values, &y_values)?;
    println!("point={point:?} slope={slope:?}");

    save_chart_linear_regression(
        &data_raw,
        &data,
        point,
        slope,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 0.0, epsilon = 1.0e-1);
    assert_relative_eq!(slope.as_degrees(), 0.0, epsilon = 1.3);

    Ok(())
}