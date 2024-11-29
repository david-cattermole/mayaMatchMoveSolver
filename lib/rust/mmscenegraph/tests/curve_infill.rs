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
use approx::assert_relative_ne;

use crate::common::chan_data_combine_xy;
use crate::common::chan_data_filter_only_x;
use crate::common::chan_data_filter_only_y;
use crate::common::construct_input_file_path;
use crate::common::construct_output_file_path;
use crate::common::find_data_dir;
use crate::common::print_actual_pops;
use crate::common::print_chan_data;
use crate::common::print_derivative_arrays;
use crate::common::read_chan_file;
use crate::common::save_chart_curves_compare_two;
use crate::common::save_chart_derivative_curves;
use crate::common::save_chart_linear_n3_regression_pop;
use crate::common::save_chart_linear_n_points_regression_pop;
use crate::common::save_chart_linear_regression_pop;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::curve::infill::infill_curve;
use mmscenegraph_rust::curve::resample::resample_uniform_xy;
use mmscenegraph_rust::math::interpolate::InterpolationMethod;

fn infill_resample_common(
    chart_title: &str,
    in_file_name: &str,
    out_file_name: &str,
    resample_by: Real,
) -> Result<()> {
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path = construct_input_file_path(&data_dir, in_file_name)?;
    let out_file_path = construct_output_file_path(&data_dir, out_file_name)?;

    let data_raw = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data_raw);
    let y_values = chan_data_filter_only_y(&data_raw);

    let resample_start = 1001.0;
    let resample_end = 1101.0;
    let data_filtered = resample_uniform_xy(
        &data_raw,
        resample_start,
        resample_end,
        resample_by,
        InterpolationMethod::Linear,
    )?;
    assert!(data_filtered.len() < data_raw.len());
    let x_values_filtered = chan_data_filter_only_x(&data_filtered);
    let y_values_filtered = chan_data_filter_only_y(&data_filtered);

    let (x_values_filled, y_values_filled) =
        infill_curve(&x_values_filtered, &y_values_filtered)?;
    let data_filled = chan_data_combine_xy(&x_values_filled, &y_values_filled);

    save_chart_curves_compare_two(
        &data_raw,
        &data_filled,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn bounce_5_up_down_infill_2() -> Result<()> {
    let chart_title = "infill_resample2_bounce_5_up_down";
    let in_file_name = "bounce_5_up_down_raw.chan";
    let out_file_name = "infill_resample2_bounce_5_up_down.png";
    let resample_by = 2.0;

    infill_resample_common(
        chart_title,
        in_file_name,
        out_file_name,
        resample_by,
    )
}

#[test]
fn bounce_5_up_down_infill_5() -> Result<()> {
    let chart_title = "infill_resample5_bounce_5_up_down";
    let in_file_name = "bounce_5_up_down_raw.chan";
    let out_file_name = "infill_resample5_bounce_5_up_down.png";
    let resample_by = 5.0;

    infill_resample_common(
        chart_title,
        in_file_name,
        out_file_name,
        resample_by,
    )
}

#[test]
fn bounce_5_up_down_infill_10() -> Result<()> {
    let chart_title = "infill_resample10_bounce_5_up_down";
    let in_file_name = "bounce_5_up_down_raw.chan";
    let out_file_name = "infill_resample10_bounce_5_up_down.png";
    let resample_by = 10.0;

    infill_resample_common(
        chart_title,
        in_file_name,
        out_file_name,
        resample_by,
    )
}

#[test]
fn bounce_5_up_down_infill_20() -> Result<()> {
    let chart_title = "infill_resample20_bounce_5_up_down";
    let in_file_name = "bounce_5_up_down_raw.chan";
    let out_file_name = "infill_resample20_bounce_5_up_down.png";
    let resample_by = 20.0;

    infill_resample_common(
        chart_title,
        in_file_name,
        out_file_name,
        resample_by,
    )
}

fn infill_gap_common(
    chart_title: &str,
    in_file_name: &str,
    out_file_name: &str,
    gaps: &[(Real, Real)],
) -> Result<()> {
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_file_path = construct_input_file_path(&data_dir, in_file_name)?;
    let out_file_path = construct_output_file_path(&data_dir, out_file_name)?;

    let data_raw = read_chan_file(&in_file_path.as_os_str())?;
    let x_values = chan_data_filter_only_x(&data_raw);
    let y_values = chan_data_filter_only_y(&data_raw);

    // Cut out gaps.
    let mut data_filtered = data_raw.clone();
    for gap in gaps {
        let gap_time_start = gap.0;
        let gap_time_end = gap.1;
        assert!(gap_time_start < gap_time_end);
        assert_relative_ne!(gap_time_start, gap_time_end, epsilon = 1.0e-9);

        for xy in &data_filtered.clone() {
            let x = xy.0;
            let y = xy.1;
            if x >= gap_time_start && x <= gap_time_end {
                let index =
                    data_filtered.iter().position(|xy| xy.0 == x).unwrap();
                data_filtered.remove(index);
            }
        }
    }
    assert!(data_filtered.len() < data_raw.len());
    let x_values_filtered = chan_data_filter_only_x(&data_filtered);
    let y_values_filtered = chan_data_filter_only_y(&data_filtered);

    let (x_values_filled, y_values_filled) =
        infill_curve(&x_values_filtered, &y_values_filtered)?;
    let data_filled = chan_data_combine_xy(&x_values_filled, &y_values_filled);

    save_chart_curves_compare_two(
        &data_raw,
        &data_filled,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(())
}

#[test]
fn bounce_5_up_down_infill_gap1() -> Result<()> {
    let chart_title = "infill_gap1_bounce_5_up_down";
    let in_file_name = "bounce_5_up_down_raw.chan";
    let out_file_name = "infill_gap1_bounce_5_up_down.png";
    let gaps: &[(Real, Real)] = &[
        (1003.0, 1011.0),
        (1012.0, 1024.0),
        (1026.0, 1049.0),
        (1051.0, 1074.0),
        (1076.0, 1100.0),
    ];

    infill_gap_common(chart_title, in_file_name, out_file_name, gaps)
}

#[test]
fn bounce_5_up_down_infill_gap2() -> Result<()> {
    let chart_title = "infill_gap2_bounce_5_up_down";
    let in_file_name = "bounce_5_up_down_raw.chan";
    let out_file_name = "infill_gap2_bounce_5_up_down.png";
    let gaps: &[(Real, Real)] = &[
        (1003.0, 1023.0),
        (1027.0, 1048.0),
        (1052.0, 1073.0),
        (1077.0, 1099.0),
    ];

    infill_gap_common(chart_title, in_file_name, out_file_name, gaps)
}
