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
use crate::common::find_output_dir;
#[allow(unused_imports)]
use crate::common::print_chan_data;
use crate::common::read_chan_file;
use crate::common::save_chart_linear_n_points_regression;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::math::curve_fit::nonlinear_line_n_points;
use mmscenegraph_rust::math::curve_fit::Point2;
use mmscenegraph_rust::math::interpolate::Interpolation;

fn curvefit_common(
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
    let in_file_path_raw =
        construct_input_file_path(&data_dir, in_reference_file_name)?;
    let in_file_path = construct_input_file_path(&data_dir, in_file_name)?;
    let out_file_path = construct_output_file_path(&output_dir, out_file_name)?;

    let data_raw = read_chan_file(&in_file_path_raw.as_os_str())?;
    let data = read_chan_file(&in_file_path.as_os_str())?;
    // print_chan_data(&data);
    let x_values = chan_data_filter_only_x(&data);
    let y_values = chan_data_filter_only_y(&data);

    let n_points = 4;
    let interpolation_method = Interpolation::Linear;
    let points = nonlinear_line_n_points(
        &x_values,
        &y_values,
        n_points,
        interpolation_method,
    )?;
    println!("points={points:?}");

    save_chart_linear_n_points_regression(
        &data_raw,
        &data,
        &points,
        chart_title,
        &out_file_path.as_os_str(),
        chart_resolution,
    )?;

    Ok(points)
}

#[test]
fn curvefit_linear_4_point_raw() -> Result<()> {
    let chart_title = "curvefit_linear_4_point_raw";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_raw.chan";
    let out_file_name = "curvefit_linear_4_point_raw.png";
    let n_points = 4;
    let interpolation_method = Interpolation::Linear;

    let points = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
        n_points,
        interpolation_method,
    )?;

    let point_a = points[0];
    let point_b = points[1];
    let point_c = points[2];
    let point_d = points[3];
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");
    println!("point_d={point_d:?}");

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_a.y(), -1.215, epsilon = 1.0e-3);

    assert_relative_eq!(point_b.x(), 1034.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), -2.6193617, epsilon = 1.0e-3);

    assert_relative_eq!(point_c.x(), 1067.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 3.61752396, epsilon = 1.0e-3);

    assert_relative_eq!(point_d.x(), 1101.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_d.y(), 1.855, epsilon = 1.0e-3);

    Ok(())
}

#[test]
fn curvefit_linear_4_point_variance1() -> Result<()> {
    let chart_title = "curvefit_linear_4_point_variance1";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_variance1.chan";
    let out_file_name = "curvefit_linear_4_point_variance1.png";
    let n_points = 4;
    let interpolation_method = Interpolation::Linear;

    let points = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
        n_points,
        interpolation_method,
    )?;

    let point_a = points[0];
    let point_b = points[1];
    let point_c = points[2];
    let point_d = points[3];
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");
    println!("point_d={point_d:?}");

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_a.y(), -1.215, epsilon = 1.0e-2);

    assert_relative_eq!(point_b.x(), 1034.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), -2.6193617, epsilon = 1.0e-2);

    assert_relative_eq!(point_c.x(), 1067.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 3.61752396, epsilon = 1.0e-2);

    assert_relative_eq!(point_d.x(), 1101.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_d.y(), 1.855, epsilon = 1.0e-2);

    Ok(())
}

#[test]
fn curvefit_linear_4_point_variance2() -> Result<()> {
    let chart_title = "curvefit_linear_4_point_variance2";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_variance2.chan";
    let out_file_name = "curvefit_linear_4_point_variance2.png";
    let n_points = 4;
    let interpolation_method = Interpolation::Linear;

    let points = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
        n_points,
        interpolation_method,
    )?;

    let point_a = points[0];
    let point_b = points[1];
    let point_c = points[2];
    let point_d = points[3];
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");
    println!("point_d={point_d:?}");

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_a.y(), -1.215, epsilon = 1.0e-1);

    assert_relative_eq!(point_b.x(), 1034.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), -2.6193617, epsilon = 1.0e-1);

    assert_relative_eq!(point_c.x(), 1067.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 3.61752396, epsilon = 1.0e-1);

    assert_relative_eq!(point_d.x(), 1101.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_d.y(), 1.855, epsilon = 1.0e-1);

    Ok(())
}

#[test]
fn curvefit_linear_4_point_variance3() -> Result<()> {
    let chart_title = "curvefit_linear_4_point_variance3";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_variance3.chan";
    let out_file_name = "curvefit_linear_4_point_variance3.png";
    let n_points = 4;
    let interpolation_method = Interpolation::Linear;

    let points = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
        n_points,
        interpolation_method,
    )?;

    let point_a = points[0];
    let point_b = points[1];
    let point_c = points[2];
    let point_d = points[3];
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");
    println!("point_d={point_d:?}");

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_a.y(), -1.215, epsilon = 0.3);

    assert_relative_eq!(point_b.x(), 1034.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), -2.6193617, epsilon = 0.3);

    assert_relative_eq!(point_c.x(), 1067.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 3.61752396, epsilon = 0.3);

    assert_relative_eq!(point_d.x(), 1101.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_d.y(), 1.855, epsilon = 1.0e-1);

    Ok(())
}

#[test]
fn curvefit_linear_4_point_variance4() -> Result<()> {
    let chart_title = "curvefit_linear_4_point_variance4";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_variance4.chan";
    let out_file_name = "curvefit_linear_4_point_variance4.png";
    let n_points = 4;
    let interpolation_method = Interpolation::Linear;

    let points = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
        n_points,
        interpolation_method,
    )?;

    let point_a = points[0];
    let point_b = points[1];
    let point_c = points[2];
    let point_d = points[3];
    println!("point_a={point_a:?}");
    println!("point_b={point_b:?}");
    println!("point_c={point_c:?}");
    println!("point_d={point_d:?}");

    assert_relative_eq!(point_a.x(), 1001.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_a.y(), -1.215, epsilon = 0.4);

    assert_relative_eq!(point_b.x(), 1034.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_b.y(), -2.6193617, epsilon = 3.0);

    assert_relative_eq!(point_c.x(), 1067.0, epsilon = 1.0e-1);
    assert_relative_eq!(point_c.y(), 3.61752396, epsilon = 5.5);

    assert_relative_eq!(point_d.x(), 1101.0, epsilon = 1.0e-9);
    assert_relative_eq!(point_d.y(), 1.855, epsilon = 3.5);

    Ok(())
}
