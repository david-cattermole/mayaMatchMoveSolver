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

use crate::common::chan_data_filter_only_x;
use crate::common::chan_data_filter_only_y;
use crate::common::construct_input_file_path;
use crate::common::construct_output_file_path;
use crate::common::find_data_dir;
use crate::common::print_actual_pops;
use crate::common::print_chan_data;
use crate::common::read_chan_file;
use crate::common::save_chart_linear_n3_regression_pop;
use crate::common::save_chart_linear_n_points_regression_pop;
use crate::common::save_chart_linear_regression_pop;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::curve::detect::pops::detect_curve_pops;
use mmscenegraph_rust::curve::detect::pops::filter_curve_pops;
use mmscenegraph_rust::curve::detect::pops::PopPoint;
use mmscenegraph_rust::curve::resample::resample_uniform_xy;
use mmscenegraph_rust::curve::resample::Interpolation;
use mmscenegraph_rust::math::curve_fit::linear_regression;
use mmscenegraph_rust::math::curve_fit::nonlinear_line_n3;
use mmscenegraph_rust::math::curve_fit::nonlinear_line_n_points;

fn compare_detected_vs_actual_pops(
    actual_pop_times: &[f64],
    pops: &[PopPoint],
    allowed_not_found: usize,
) {
    let pop_times: Vec<f64> = pops.iter().map(|x| x.time).collect();

    let mut not_found_count = 0;
    for actual_pop_time in actual_pop_times {
        let found =
            pop_times.iter().find(|&&x| x == *actual_pop_time).is_some();
        if !found {
            println!("actual_pop_time={actual_pop_time} not found");
            not_found_count += 1;
        }
    }

    // Should find all pops.
    assert_eq!(not_found_count, allowed_not_found);
}

#[test]
fn identity_pop1() -> Result<()> {
    let chart_title = "identity_pop1";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_pop =
        construct_input_file_path(&data_dir, "identity_pop1.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_raw.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "identity_pop1.png")?;

    let data_pop = read_chan_file(&in_file_path_pop.as_os_str())?;
    let data_raw = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data_pop);
    let y_values = chan_data_filter_only_y(&data_pop);
    let y_values_raw = chan_data_filter_only_y(&data_raw);

    let actual_pops =
        print_actual_pops(&x_values, &y_values, &y_values_raw, 1.0e-9);

    let threshold = 0.1;
    let pops = detect_curve_pops(&x_values, &y_values, threshold)?;
    for pop in &pops {
        println!("pop: {pop:?}");
    }

    let resample_start = 1001.0;
    let resample_end = 1101.0;
    let resample_by = 1.0;
    let interpolation = Interpolation::Linear;
    let data_filtered = filter_curve_pops(&x_values, &y_values, threshold)?;
    let data_filtered = resample_uniform_xy(
        &data_filtered,
        resample_start,
        resample_end,
        resample_by,
        interpolation,
    )?;
    let x_values_filtered = chan_data_filter_only_x(&data_filtered);
    let y_values_filtered = chan_data_filter_only_y(&data_filtered);

    let (point, slope) =
        linear_regression(&x_values_filtered, &y_values_filtered)?;
    println!("point={point:?} slope={slope:?}");

    save_chart_linear_regression_pop(
        &data_raw,
        &data_pop,
        &data_filtered,
        point,
        slope,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(pops.len() >= actual_pops.len());
    compare_detected_vs_actual_pops(&actual_pops, &pops, 1);

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 0.0, epsilon = 1.0e-5);
    assert_relative_eq!(slope.as_degrees(), 0.0, epsilon = 1.0e-3);

    Ok(())
}

#[test]
fn identity_pop2() -> Result<()> {
    let chart_title = "identity_pop2";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_pop =
        construct_input_file_path(&data_dir, "identity_pop2.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "identity_raw.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "identity_pop2.png")?;

    let data_pop = read_chan_file(&in_file_path_pop.as_os_str())?;
    let data_raw = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data_pop);
    let y_values = chan_data_filter_only_y(&data_pop);
    let y_values_raw = chan_data_filter_only_y(&data_raw);

    let actual_pops =
        print_actual_pops(&x_values, &y_values, &y_values_raw, 1.0e-9);

    let threshold = 0.1;
    let pops = detect_curve_pops(&x_values, &y_values, threshold)?;
    for pop in &pops {
        println!("pop: {pop:?}");
    }

    let resample_start = 1001.0;
    let resample_end = 1101.0;
    let resample_by = 1.0;
    let interpolation = Interpolation::Linear;
    let data_filtered = filter_curve_pops(&x_values, &y_values, threshold)?;
    let data_filtered = resample_uniform_xy(
        &data_filtered,
        resample_start,
        resample_end,
        resample_by,
        interpolation,
    )?;
    let x_values_filtered = chan_data_filter_only_x(&data_filtered);
    let y_values_filtered = chan_data_filter_only_y(&data_filtered);

    let (point, slope) =
        linear_regression(&x_values_filtered, &y_values_filtered)?;
    println!("point={point:?} slope={slope:?}");

    save_chart_linear_regression_pop(
        &data_raw,
        &data_pop,
        &data_filtered,
        point,
        slope,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert_eq!(data_filtered.len(), data_raw.len());
    assert!(pops.len() >= actual_pops.len());
    compare_detected_vs_actual_pops(&actual_pops, &pops, 0);

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 0.0, epsilon = 1.0e-2);
    assert_relative_eq!(slope.as_degrees(), 0.0, epsilon = 1.0e-2);

    Ok(())
}

#[test]
fn linear_3_point_pop3() -> Result<()> {
    let chart_title = "linear_3_point_pop3";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_pop =
        construct_input_file_path(&data_dir, "linear_3_point_pop3.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "linear_3_point_raw.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "linear_3_point_pop3.png")?;

    let data_pop = read_chan_file(&in_file_path_pop.as_os_str())?;
    let data_raw = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data_pop);
    let y_values = chan_data_filter_only_y(&data_pop);
    let y_values_raw = chan_data_filter_only_y(&data_raw);

    let actual_pops =
        print_actual_pops(&x_values, &y_values, &y_values_raw, 1.0e-9);

    let threshold = 0.1;
    let pops = detect_curve_pops(&x_values, &y_values, threshold)?;
    for pop in &pops {
        println!("pop: {pop:?}");
    }

    let resample_start = 1001.0;
    let resample_end = 1101.0;
    let resample_by = 1.0;
    let interpolation = Interpolation::Linear;
    let data_filtered = filter_curve_pops(&x_values, &y_values, threshold)?;
    let data_filtered = resample_uniform_xy(
        &data_filtered,
        resample_start,
        resample_end,
        resample_by,
        interpolation,
    )?;
    let x_values_filtered = chan_data_filter_only_x(&data_filtered);
    let y_values_filtered = chan_data_filter_only_y(&data_filtered);

    let (point_a, point_b, point_c) =
        nonlinear_line_n3(&x_values_filtered, &y_values_filtered)?;
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");

    save_chart_linear_n3_regression_pop(
        &data_raw,
        &data_pop,
        &data_filtered,
        point_a,
        point_b,
        point_c,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(pops.len() >= actual_pops.len());
    compare_detected_vs_actual_pops(&actual_pops, &pops, 0);

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_a.y(), -1.21533949192, epsilon = 0.3);

    assert_relative_eq!(point_b.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), 4.5, epsilon = 0.2);

    assert_relative_eq!(point_c.x(), 1101.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 1.855, epsilon = 0.3);

    Ok(())
}

#[test]
fn degree_45_up_pop3() -> Result<()> {
    let chart_title = "degree_45_up_pop3";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_pop =
        construct_input_file_path(&data_dir, "degree_45_up_pop3.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "degree_45_up_raw.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "degree_45_up_pop3.png")?;

    let data_pop = read_chan_file(&in_file_path_pop.as_os_str())?;
    let data_raw = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data_pop);
    let y_values = chan_data_filter_only_y(&data_pop);
    let y_values_raw = chan_data_filter_only_y(&data_raw);

    let actual_pops =
        print_actual_pops(&x_values, &y_values, &y_values_raw, 1.0e-9);

    let threshold = 0.1;
    let pops = detect_curve_pops(&x_values, &y_values, threshold)?;
    for pop in &pops {
        println!("pop: {pop:?}");
    }

    let resample_start = 1001.0;
    let resample_end = 1101.0;
    let resample_by = 1.0;
    let interpolation = Interpolation::Linear;
    let data_filtered = filter_curve_pops(&x_values, &y_values, threshold)?;
    let data_filtered = resample_uniform_xy(
        &data_filtered,
        resample_start,
        resample_end,
        resample_by,
        interpolation,
    )?;
    let x_values_filtered = chan_data_filter_only_x(&data_filtered);
    let y_values_filtered = chan_data_filter_only_y(&data_filtered);

    let (point, slope) =
        linear_regression(&x_values_filtered, &y_values_filtered)?;
    println!("point={point:?} slope={slope:?}");

    save_chart_linear_regression_pop(
        &data_raw,
        &data_pop,
        &data_filtered,
        point,
        slope,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    assert!(pops.len() >= actual_pops.len());
    compare_detected_vs_actual_pops(&actual_pops, &pops, 1);

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 50.0, epsilon = 1.14);
    assert_relative_eq!(slope.as_degrees(), 45.0, epsilon = 1.0e-1);

    Ok(())
}

#[test]
fn bounce_5_up_down_pop3() -> Result<()> {
    let chart_title = "bounce_5_up_down_pop3";
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path_pop =
        construct_input_file_path(&data_dir, "bounce_5_up_down_pop3.chan")?;
    let in_file_path =
        construct_input_file_path(&data_dir, "bounce_5_up_down_raw.chan")?;
    let out_file_path =
        construct_output_file_path(&data_dir, "bounce_5_up_down_pop3.png")?;

    let data_pop = read_chan_file(&in_file_path_pop.as_os_str())?;
    let data_raw = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data_pop);
    let y_values = chan_data_filter_only_y(&data_pop);
    let y_values_raw = chan_data_filter_only_y(&data_raw);

    let actual_pops =
        print_actual_pops(&x_values, &y_values, &y_values_raw, 1.0e-9);

    let threshold = 0.1;
    let pops = detect_curve_pops(&x_values, &y_values, threshold)?;
    for pop in &pops {
        println!("pop: {pop:?}");
    }

    let resample_start = 1001.0;
    let resample_end = 1101.0;
    let resample_by = 1.0;
    let interpolation = Interpolation::Linear;
    let data_filtered = filter_curve_pops(&x_values, &y_values, threshold)?;
    let data_filtered = resample_uniform_xy(
        &data_filtered,
        resample_start,
        resample_end,
        resample_by,
        interpolation,
    )?;
    let x_values_filtered = chan_data_filter_only_x(&data_filtered);
    let y_values_filtered = chan_data_filter_only_y(&data_filtered);

    let points =
        nonlinear_line_n_points(&x_values_filtered, &y_values_filtered, 5)?;
    println!("points={points:?}");

    save_chart_linear_n_points_regression_pop(
        &data_raw,
        &data_pop,
        &data_filtered,
        &points,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    let point_a = points[0];
    let point_b = points[1];
    let point_c = points[2];
    let point_d = points[3];
    let point_e = points[4];
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");
    println!("point_d={point_d:?}");
    println!("point_e={point_e:?}");

    assert!(pops.len() >= actual_pops.len());
    compare_detected_vs_actual_pops(&actual_pops, &pops, 1);

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_a.y(), -0.9371984654725308, epsilon = 1.0e-9);

    assert_relative_eq!(point_b.x(), 1026.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), 3.0081663616798155, epsilon = 1.0e-9);

    assert_relative_eq!(point_c.x(), 1051.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), -1.5667686469713358, epsilon = 1.0e-9);

    assert_relative_eq!(point_d.x(), 1076.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_d.y(), 3.168206647014793, epsilon = 1.0e-9);

    assert_relative_eq!(point_e.x(), 1101.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_e.y(), -2.9104705224487954, epsilon = 1.0e-9);

    Ok(())
}
