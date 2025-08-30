//
// Copyright (C) 2024, 2025 David Cattermole.
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

use crate::common::curvefit_n_points_common;
use mmscenegraph_rust::math::interpolate::Interpolation;

#[test]
fn curvefit_4_point_quadratic_nubs_raw() -> Result<()> {
    let chart_title = "curvefit_4_point_quadratic_nubs_raw";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_raw.chan";
    let out_file_name = "curvefit_4_point_quadratic_nubs_raw.png";
    let n_points = 4;
    let interpolation_method = Interpolation::QuadraticNUBS;

    let points = curvefit_n_points_common(
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

    // TODO: Control point expectations will be updated after running
    // tests to see actual values.
    //
    // QuadraticNUBS will produce different control points than linear
    // interpolation.
    println!("Expected values need to be determined from test run");

    Ok(())
}

#[test]
fn curvefit_4_point_quadratic_nubs_variance1() -> Result<()> {
    let chart_title = "curvefit_4_point_quadratic_nubs_variance1";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_variance1.chan";
    let out_file_name = "curvefit_4_point_quadratic_nubs_variance1.png";
    let n_points = 4;
    let interpolation_method = Interpolation::QuadraticNUBS;

    let _points = curvefit_n_points_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
        n_points,
        interpolation_method,
    )?;

    // TODO: Control point expectations will be updated after running
    // tests to see actual values.
    println!("Expected values need to be determined from test run");

    Ok(())
}

#[test]
fn curvefit_4_point_quadratic_nubs_variance2() -> Result<()> {
    let chart_title = "curvefit_4_point_quadratic_nubs_variance2";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_variance2.chan";
    let out_file_name = "curvefit_4_point_quadratic_nubs_variance2.png";
    let n_points = 4;
    let interpolation_method = Interpolation::QuadraticNUBS;

    let _points = curvefit_n_points_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
        n_points,
        interpolation_method,
    )?;

    // TODO: Control point expectations will be updated after running
    // tests to see actual values.
    println!("Expected values need to be determined from test run");

    Ok(())
}

#[test]
fn curvefit_4_point_quadratic_nubs_variance3() -> Result<()> {
    let chart_title = "curvefit_4_point_quadratic_nubs_variance3";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_variance3.chan";
    let out_file_name = "curvefit_4_point_quadratic_nubs_variance3.png";
    let n_points = 4;
    let interpolation_method = Interpolation::QuadraticNUBS;

    let _points = curvefit_n_points_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
        n_points,
        interpolation_method,
    )?;

    // TODO: Control point expectations will be updated after running
    // tests to see actual values.
    println!("Expected values need to be determined from test run");

    Ok(())
}

#[test]
fn curvefit_4_point_quadratic_nubs_variance4() -> Result<()> {
    let chart_title = "curvefit_4_point_quadratic_nubs_variance4";
    let in_reference_file_name = "linear_4_point_raw.chan";
    let in_file_name = "linear_4_point_variance4.chan";
    let out_file_name = "curvefit_4_point_quadratic_nubs_variance4.png";
    let n_points = 4;
    let interpolation_method = Interpolation::QuadraticNUBS;

    let _points = curvefit_n_points_common(
        chart_title,
        in_reference_file_name,
        in_file_name,
        out_file_name,
        n_points,
        interpolation_method,
    )?;

    // TODO: Control point expectations will be updated after running
    // tests to see actual values.
    println!("Expected values need to be determined from test run");

    Ok(())
}