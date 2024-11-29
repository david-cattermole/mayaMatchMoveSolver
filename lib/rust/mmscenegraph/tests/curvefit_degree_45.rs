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
use crate::common::print_chan_data;
use crate::common::read_chan_file;
use crate::common::save_chart_linear_regression;
use crate::common::CHART_RESOLUTION;

use mmscenegraph_rust::math::curve_fit::linear_regression;
use mmscenegraph_rust::math::curve_fit::AngleRadian;
use mmscenegraph_rust::math::curve_fit::Point2;

fn curvefit_common(
    chart_title: &str,
    in_reference_file_name: &str,
    in_file_name: &str,
    out_file_name: &str,
) -> Result<(Point2, AngleRadian)> {
    let chart_resolution = CHART_RESOLUTION;

    let data_dir = find_data_dir()?;
    let in_reference_file_path =
        construct_input_file_path(&data_dir, in_reference_file_name)?;
    let in_file_path = construct_input_file_path(&data_dir, in_file_name)?;
    let out_file_path = construct_output_file_path(&data_dir, out_file_name)?;

    let data_raw = read_chan_file(&in_reference_file_path.as_os_str())?;
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

    Ok((point, slope))
}

#[test]
fn degree_45_up_raw() -> Result<()> {
    let chart_title = "curvefit_degree_45_up_raw";
    let in_reference_file_name = "degree_45_up_raw.chan";
    let in_file_name = "degree_45_up_raw.chan";
    let out_file_name = "curvefit_degree_45_up_raw.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 50.0, epsilon = 1.0e-9);
    assert_relative_eq!(slope.as_degrees(), 45.0, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn degree_45_up_variance1() -> Result<()> {
    let chart_title = "curvefit_degree_45_up_variance1";
    let in_reference_file_name = "degree_45_up_raw.chan";
    let in_file_name = "degree_45_up_variance1.chan";
    let out_file_name = "curvefit_degree_45_up_variance1.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-3);
    assert_relative_eq!(point.y(), 50.0, epsilon = 1.0e-3);
    assert_relative_eq!(slope.as_degrees(), 45.0, epsilon = 1.0e-3);

    Ok(())
}

#[test]
fn degree_45_up_variance2() -> Result<()> {
    let chart_title = "curvefit_degree_45_up_variance2";
    let in_reference_file_name = "degree_45_up_raw.chan";
    let in_file_name = "degree_45_up_variance2.chan";
    let out_file_name = "curvefit_degree_45_up_variance2.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 50.0, epsilon = 1.0e-2);
    assert_relative_eq!(slope.as_degrees(), 45.0, epsilon = 1.0e-2);

    Ok(())
}

#[test]
fn degree_45_up_variance3() -> Result<()> {
    let chart_title = "curvefit_degree_45_up_variance3";
    let in_reference_file_name = "degree_45_up_raw.chan";
    let in_file_name = "degree_45_up_variance3.chan";
    let out_file_name = "curvefit_degree_45_up_variance3.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 50.0, epsilon = 1.14);
    assert_relative_eq!(slope.as_degrees(), 45.0, epsilon = 1.0e-1);

    Ok(())
}

#[test]
fn degree_45_up_variance4() -> Result<()> {
    let chart_title = "curvefit_degree_45_up_variance4";
    let in_reference_file_name = "degree_45_up_raw.chan";
    let in_file_name = "degree_45_up_variance4.chan";
    let out_file_name = "curvefit_degree_45_up_variance4.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), 50.0, epsilon = 1.14);
    assert_relative_eq!(slope.as_degrees(), 45.0, epsilon = 0.75);

    Ok(())
}

#[test]
fn degree_45_down_raw() -> Result<()> {
    let chart_title = "curvefit_degree_45_down_raw";
    let in_reference_file_name = "degree_45_down_raw.chan";
    let in_file_name = "degree_45_down_raw.chan";
    let out_file_name = "curvefit_degree_45_down_raw.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), -50.0, epsilon = 1.0e-9);
    assert_relative_eq!(slope.as_degrees(), -45.0, epsilon = 1.0e-9);

    Ok(())
}

#[test]
fn degree_45_down_variance1() -> Result<()> {
    let chart_title = "curvefit_degree_45_down_variance1";
    let in_reference_file_name = "degree_45_down_raw.chan";
    let in_file_name = "degree_45_down_variance1.chan";
    let out_file_name = "curvefit_degree_45_down_variance1.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-3);
    assert_relative_eq!(point.y(), -50.0, epsilon = 1.0e-3);
    assert_relative_eq!(slope.as_degrees(), -45.0, epsilon = 1.0e-3);

    Ok(())
}

#[test]
fn degree_45_down_variance2() -> Result<()> {
    let chart_title = "curvefit_degree_45_down_variance2";
    let in_reference_file_name = "degree_45_down_raw.chan";
    let in_file_name = "degree_45_down_variance2.chan";
    let out_file_name = "curvefit_degree_45_down_variance2.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), -50.0, epsilon = 1.0e-2);
    assert_relative_eq!(slope.as_degrees(), -45.0, epsilon = 1.0e-2);

    Ok(())
}

#[test]
fn degree_45_down_variance3() -> Result<()> {
    let chart_title = "curvefit_degree_45_down_variance3";
    let in_reference_file_name = "degree_45_down_raw.chan";
    let in_file_name = "degree_45_down_variance3.chan";
    let out_file_name = "curvefit_degree_45_down_variance3.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), -50.0, epsilon = 1.14);
    assert_relative_eq!(slope.as_degrees(), -45.0, epsilon = 1.0e-1);

    Ok(())
}

#[test]
fn degree_45_down_variance4() -> Result<()> {
    let chart_title = "curvefit_degree_45_down_variance4";
    let in_reference_file_name = "degree_45_down_raw.chan";
    let in_file_name = "degree_45_down_variance4.chan";
    let out_file_name = "curvefit_degree_45_down_variance4.png";

    let (point, slope) = curvefit_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
    )?;

    assert_relative_eq!(point.x(), 1051.0, epsilon = 1.0e-9);
    assert_relative_eq!(point.y(), -50.0, epsilon = 1.14);
    assert_relative_eq!(slope.as_degrees(), -45.0, epsilon = 0.75);

    Ok(())
}
