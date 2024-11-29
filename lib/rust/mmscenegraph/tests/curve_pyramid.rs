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
// use crate::common::print_chan_data;
use crate::common::print_curvature_arrays;
use crate::common::read_chan_file;
use crate::common::save_chart_curvature_curves;
use crate::common::save_chart_curves_compare_many;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::curve::pyramid::build_pyramid_levels;
use mmscenegraph_rust::curve::pyramid::compute_pyramid_depth;

fn curve_pyramid_common(
    chart_title: &str,
    in_file_name: &str,
    out_file_name: &str,
) -> Result<()> {
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path = construct_input_file_path(&data_dir, in_file_name)?;
    let out_file_path = construct_output_file_path(&data_dir, out_file_name)?;

    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let pyramid_depth = compute_pyramid_depth(x_values.len());
    let pyramid_levels =
        build_pyramid_levels(&x_values, &y_values, pyramid_depth)?;

    let mut xy_levels_values = Vec::new();
    for pyramid_level in pyramid_levels {
        let times = pyramid_level.times;
        let values = pyramid_level.values;
        let xy_level_values: Vec<(f64, f64)> =
            times.iter().zip(values).map(|(x, y)| (*x, y)).collect();

        xy_levels_values.push(xy_level_values);
    }

    let mut data_curves = Vec::new();
    for xy_level_values in xy_levels_values {
        data_curves.push(xy_level_values);
    }

    save_chart_curves_compare_many(
        &data_curves,
        chart_title,
        out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn curve_pyramid_bounce_5_up_down_raw() -> Result<()> {
    let chart_title = "pyramid_bounce_5_up_down_raw";
    let in_file_name = "bounce_5_up_down_raw.chan";
    let out_file_name = "pyramid_bounce_5_up_down_raw.png";
    curve_pyramid_common(chart_title, in_file_name, out_file_name)
}

#[test]
fn curve_pyramid_bounce_5_up_down_variance1() -> Result<()> {
    let chart_title = "pyramid_bounce_5_up_down_variance1";
    let in_file_name = "bounce_5_up_down_variance1.chan";
    let out_file_name = "pyramid_bounce_5_up_down_variance1.png";
    curve_pyramid_common(chart_title, in_file_name, out_file_name)
}

#[test]
fn curve_pyramid_bounce_5_up_down_variance2() -> Result<()> {
    let chart_title = "pyramid_bounce_5_up_down_variance2";
    let in_file_name = "bounce_5_up_down_variance2.chan";
    let out_file_name = "pyramid_bounce_5_up_down_variance2.png";
    curve_pyramid_common(chart_title, in_file_name, out_file_name)
}

#[test]
fn curve_pyramid_bounce_5_up_down_variance3() -> Result<()> {
    let chart_title = "pyramid_bounce_5_up_down_variance3";
    let in_file_name = "bounce_5_up_down_variance3.chan";
    let out_file_name = "pyramid_bounce_5_up_down_variance3.png";
    curve_pyramid_common(chart_title, in_file_name, out_file_name)
}

#[test]
fn curve_pyramid_bounce_5_up_down_variance4() -> Result<()> {
    let chart_title = "pyramid_bounce_5_up_down_variance4";
    let in_file_name = "bounce_5_up_down_variance4.chan";
    let out_file_name = "pyramid_bounce_5_up_down_variance4.png";
    curve_pyramid_common(chart_title, in_file_name, out_file_name)
}

#[test]
fn curve_pyramid_bounce_5_up_down_pop1() -> Result<()> {
    let chart_title = "pyramid_bounce_5_up_down_pop1";
    let in_file_name = "bounce_5_up_down_pop1.chan";
    let out_file_name = "pyramid_bounce_5_up_down_pop1.png";
    curve_pyramid_common(chart_title, in_file_name, out_file_name)
}

#[test]
fn curve_pyramid_bounce_5_up_down_pop2() -> Result<()> {
    let chart_title = "pyramid_bounce_5_up_down_pop2";
    let in_file_name = "bounce_5_up_down_pop2.chan";
    let out_file_name = "pyramid_bounce_5_up_down_pop2.png";
    curve_pyramid_common(chart_title, in_file_name, out_file_name)
}

#[test]
fn curve_pyramid_bounce_5_up_down_pop3() -> Result<()> {
    let chart_title = "pyramid_bounce_5_up_down_pop3";
    let in_file_name = "bounce_5_up_down_pop3.chan";
    let out_file_name = "pyramid_bounce_5_up_down_pop3.png";
    curve_pyramid_common(chart_title, in_file_name, out_file_name)
}

#[test]
fn curve_pyramid_bounce_5_up_down_pop4() -> Result<()> {
    let chart_title = "pyramid_bounce_5_up_down_pop4";
    let in_file_name = "bounce_5_up_down_pop4.chan";
    let out_file_name = "pyramid_bounce_5_up_down_pop4.png";
    curve_pyramid_common(chart_title, in_file_name, out_file_name)
}
