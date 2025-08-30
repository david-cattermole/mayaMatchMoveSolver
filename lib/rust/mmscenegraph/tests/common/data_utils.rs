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

use mmscenegraph_rust::constant::FrameTime;
use mmscenegraph_rust::constant::Real;
use mmscenegraph_rust::math::statistics::calc_normalized_root_mean_square_error;

#[allow(dead_code)]
pub fn print_actual_pops(
    x_values: &[f64],
    y_values_pop: &[f64],
    y_values_raw: &[f64],
    threshold: f64,
) -> Vec<f64> {
    println!("print_actual_pops: start");
    let mut out = Vec::new();
    for (x, (y_pop, y_raw)) in
        x_values.iter().zip(y_values_pop.iter().zip(y_values_raw))
    {
        let diff = (y_raw - y_pop).abs();
        if diff > threshold {
            println!("print_actual_pop: x={x} diff={diff}");
            out.push(*x)
        }
    }
    println!("print_actual_pops: end; count={}", out.len());

    out
}

#[allow(dead_code)]
pub fn print_derivative_arrays(
    velocity: &[f64],
    acceleration: &[f64],
    jerk: &[f64],
) {
    println!("Velocity (1st order derivative) count {} :", velocity.len());
    for (i, v) in velocity.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!(
        "Acceleration (2nd order derivative) count {} :",
        acceleration.len()
    );
    for (i, v) in acceleration.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!("Jerk (3rd order derivative) count {} :", jerk.len());
    for (i, v) in jerk.iter().enumerate() {
        println!("i={i} v={v}");
    }
}

#[allow(dead_code)]
pub fn print_curvature_arrays(
    velocity: &[f64],
    acceleration: &[f64],
    curvature: &[f64],
) {
    println!("Velocity (1st order derivative) count {} :", velocity.len());
    for (i, v) in velocity.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!(
        "Acceleration (2nd order derivative) count {} :",
        acceleration.len()
    );
    for (i, v) in acceleration.iter().enumerate() {
        println!("i={i} v={v}");
    }

    println!("Curvature count {} :", curvature.len());
    for (i, v) in curvature.iter().enumerate() {
        println!("i={i} v={v}");
    }
}

/// Calculate quality of fit metric:
/// quality = max(0.0, min(100.0, (1.0 - nrmse) * 100.0))
#[allow(dead_code)]
pub fn calculate_quality_of_fit(
    actual: &[f64],
    predicted: &[f64],
) -> Result<f64> {
    let nrmse = calc_normalized_root_mean_square_error(actual, predicted)?;
    let quality = (1.0 - nrmse).clamp(0.0, 1.0) * 100.0;
    Ok(quality)
}

#[allow(dead_code)]
pub fn chan_data_filter_only_x(data: &[(FrameTime, Real)]) -> Vec<Real> {
    data.iter().map(|x| x.0 as Real).collect()
}

#[allow(dead_code)]
pub fn chan_data_filter_only_y(data: &[(FrameTime, Real)]) -> Vec<Real> {
    data.iter().map(|x| x.1 as Real).collect()
}

#[allow(dead_code)]
pub fn chan_data_combine_xy(
    x_values: &[FrameTime],
    y_values: &[Real],
) -> Vec<(FrameTime, Real)> {
    assert_eq!(x_values.len(), y_values.len());
    x_values
        .iter()
        .zip(y_values.iter())
        .map(|x| (*x.0, *x.1))
        .collect()
}
