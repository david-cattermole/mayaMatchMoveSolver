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

use anyhow::Result;

use mmscenegraph_rust::math::curve_fit::nonlinear_line_n_points;
use mmscenegraph_rust::math::curve_fit::Point2;
use mmscenegraph_rust::math::interpolate::Interpolation;

use crate::common::chart_saving::{
    save_chart_n3_regression, save_chart_n_points_regression,
};
use crate::common::chart_utils::CHART_RESOLUTION;
use crate::common::data_utils::{
    chan_data_filter_only_x, chan_data_filter_only_y,
};
use crate::common::directory::{
    construct_input_file_path, construct_output_file_path, find_data_dir,
    find_output_dir,
};
use crate::common::file_io::read_chan_file;

#[allow(dead_code)]
pub fn curvefit_n_points_common(
    chart_title: &str,
    in_reference_file_name: &str,
    in_file_name: &str,
    out_file_name: &str,
    n_points: usize,
    interpolation_method: Interpolation,
) -> Result<Vec<Point2>> {
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let output_dir = find_output_dir()?;
    let in_reference_file_path =
        construct_input_file_path(&data_dir, in_reference_file_name)?;
    let in_file_path = construct_input_file_path(&data_dir, in_file_name)?;
    let out_file_path = construct_output_file_path(&output_dir, out_file_name)?;

    let data_raw = read_chan_file(&in_reference_file_path.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let points = nonlinear_line_n_points(
        &x_values,
        &y_values,
        n_points,
        interpolation_method,
    )?;

    println!("points={points:?}");

    match n_points {
        3 => {
            let point_a = points[0];
            let point_b = points[1];
            let point_c = points[2];
            save_chart_n3_regression(
                &data_raw,
                &data,
                point_a,
                point_b,
                point_c,
                interpolation_method,
                chart_title,
                &out_file_path.as_os_str(),
                chart_resolution,
            )?;
        }
        _ => {
            save_chart_n_points_regression(
                &data_raw,
                &data,
                &points,
                interpolation_method,
                chart_title,
                &out_file_path.as_os_str(),
                chart_resolution,
            )?;
        }
    }

    Ok(points)
}
