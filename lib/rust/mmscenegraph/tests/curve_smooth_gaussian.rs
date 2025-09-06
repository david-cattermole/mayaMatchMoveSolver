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

// #![allow(unused_imports)]
// #![allow(unused_variables)]
// #![allow(dead_code)]

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
use crate::common::read_chan_file;
use crate::common::save_chart_curves_compare_two;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::curve::smooth::gaussian::gaussian_smooth_2d;

#[test]
fn curve_smooth_gaussian1() -> Result<()> {
    let chart_title = "curve_smooth_gaussian1";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance4.chan",
    )?;
    let out_file_path =
        construct_output_file_path(&output_dir, "curve_smooth_gaussian1.png")?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let smoothing_width = 1.0;
    let mut y_values_smoothed: Vec<Real> = vec![0.0; y_values.len()];
    gaussian_smooth_2d(
        &x_values,
        &y_values,
        smoothing_width,
        &mut y_values_smoothed,
    )?;

    let data_smoothed = chan_data_combine_xy(&x_values, &y_values_smoothed);

    save_chart_curves_compare_two(
        &data,
        &data_smoothed,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(y_values.len() >= y_values_smoothed.len());
    for (y1, y2) in y_values.iter().zip(y_values_smoothed) {
        assert_relative_eq!(*y1, y2, epsilon = 1.0e-9);
    }

    Ok(())
}

#[test]
fn curve_smooth_gaussian2() -> Result<()> {
    let chart_title = "curve_smooth_gaussian2";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance4.chan",
    )?;
    let out_file_path =
        construct_output_file_path(&output_dir, "curve_smooth_gaussian2.png")?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let smoothing_width = 2.0;
    let mut y_values_smoothed: Vec<Real> = vec![0.0; y_values.len()];
    gaussian_smooth_2d(
        &x_values,
        &y_values,
        smoothing_width,
        &mut y_values_smoothed,
    )?;

    let data_smoothed = chan_data_combine_xy(&x_values, &y_values_smoothed);

    save_chart_curves_compare_two(
        &data,
        &data_smoothed,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(y_values.len() >= y_values_smoothed.len());

    Ok(())
}

#[test]
fn curve_smooth_gaussian5() -> Result<()> {
    let chart_title = "curve_smooth_gaussian5";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance4.chan",
    )?;
    let out_file_path =
        construct_output_file_path(&output_dir, "curve_smooth_gaussian5.png")?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let smoothing_width = 5.0;
    let mut y_values_smoothed: Vec<Real> = vec![0.0; y_values.len()];
    gaussian_smooth_2d(
        &x_values,
        &y_values,
        smoothing_width,
        &mut y_values_smoothed,
    )?;

    let data_smoothed = chan_data_combine_xy(&x_values, &y_values_smoothed);

    save_chart_curves_compare_two(
        &data,
        &data_smoothed,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(y_values.len() >= y_values_smoothed.len());

    Ok(())
}

#[test]
fn curve_smooth_gaussian10() -> Result<()> {
    let chart_title = "curve_smooth_gaussian10";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance4.chan",
    )?;
    let out_file_path =
        construct_output_file_path(&output_dir, "curve_smooth_gaussian10.png")?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let smoothing_width = 10.0;
    let mut y_values_smoothed: Vec<Real> = vec![0.0; y_values.len()];
    gaussian_smooth_2d(
        &x_values,
        &y_values,
        smoothing_width,
        &mut y_values_smoothed,
    )?;

    let data_smoothed = chan_data_combine_xy(&x_values, &y_values_smoothed);

    save_chart_curves_compare_two(
        &data,
        &data_smoothed,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(y_values.len() >= y_values_smoothed.len());

    Ok(())
}

#[test]
fn curve_smooth_gaussian25() -> Result<()> {
    let chart_title = "curve_smooth_gaussian25";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance4.chan",
    )?;
    let out_file_path =
        construct_output_file_path(&output_dir, "curve_smooth_gaussian25.png")?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let smoothing_width = 25.0;
    let mut y_values_smoothed: Vec<Real> = vec![0.0; y_values.len()];
    gaussian_smooth_2d(
        &x_values,
        &y_values,
        smoothing_width,
        &mut y_values_smoothed,
    )?;

    let data_smoothed = chan_data_combine_xy(&x_values, &y_values_smoothed);

    save_chart_curves_compare_two(
        &data,
        &data_smoothed,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(y_values.len() >= y_values_smoothed.len());

    Ok(())
}

#[test]
fn curve_smooth_gaussian50() -> Result<()> {
    let chart_title = "curve_smooth_gaussian50";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance4.chan",
    )?;
    let out_file_path =
        construct_output_file_path(&output_dir, "curve_smooth_gaussian50.png")?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let smoothing_width = 50.0;
    let mut y_values_smoothed: Vec<Real> = vec![0.0; y_values.len()];
    gaussian_smooth_2d(
        &x_values,
        &y_values,
        smoothing_width,
        &mut y_values_smoothed,
    )?;

    let data_smoothed = chan_data_combine_xy(&x_values, &y_values_smoothed);

    save_chart_curves_compare_two(
        &data,
        &data_smoothed,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(y_values.len() >= y_values_smoothed.len());

    Ok(())
}

#[test]
fn curve_smooth_gaussian100() -> Result<()> {
    let chart_title = "curve_smooth_gaussian100";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_file_path = construct_input_file_path(
        &data_dir,
        "bounce_5_up_down_variance4.chan",
    )?;
    let out_file_path = construct_output_file_path(
        &output_dir,
        "curve_smooth_gaussian100.png",
    )?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let smoothing_width = 100.0;
    let mut y_values_smoothed: Vec<Real> = vec![0.0; y_values.len()];
    gaussian_smooth_2d(
        &x_values,
        &y_values,
        smoothing_width,
        &mut y_values_smoothed,
    )?;

    let data_smoothed = chan_data_combine_xy(&x_values, &y_values_smoothed);

    save_chart_curves_compare_two(
        &data,
        &data_smoothed,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(y_values.len() >= y_values_smoothed.len());

    Ok(())
}
