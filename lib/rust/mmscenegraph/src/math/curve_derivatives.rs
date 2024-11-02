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

use anyhow::bail;
use anyhow::Result;
use log::debug;

use crate::constant::Real;

/// Given arrays of time and value points, calculate the derivative using
/// previous and next values (except for the first and last points).
/// Writes results into the provided output slice.
///
/// # Arguments
/// * `times` - Slice of time points
/// * `values` - Slice of corresponding values
/// * `out` - Slice where derivatives will be written, must be same length as inputs
///
/// # Returns
/// `Ok(())` if successful, `Err` if slice lengths don't match
///
/// This function avoids allocations and is designed to be easy for
/// compilers to auto-vectorize.
fn calc_derivative(
    times: &[Real],
    values: &[Real],
    out: &mut [Real],
) -> Result<()> {
    // Verify slice lengths match
    if times.len() != values.len() || times.len() != out.len() {
        bail!("Input and output slices must have equal length");
    }

    let n = times.len();
    if n < 2 {
        // Zero out the output for small inputs, because only a single
        // time/value cannot change, so there is no derivative.
        out.fill(0.0);

        return Ok(());
    }

    // First point, using forward difference: (f(x + h) - f(x)) / h
    out[0] = (values[1] - values[0]) / (times[1] - times[0]);

    // Middle points, using central difference: (f(x + h) - f(x - h)) / (2h)
    for i in 1..n - 1 {
        // Forward and backward time differences
        let dt_forward = times[i + 1] - times[i];
        let dt_backward = times[i] - times[i - 1];
        let total_dt = dt_forward + dt_backward;

        // Weights for weighted average
        let w_backward = dt_forward / total_dt;
        let w_forward = dt_backward / total_dt;

        // Forward and backward value differences
        let dv_forward = values[i + 1] - values[i];
        let dv_backward = values[i] - values[i - 1];

        // Weighted average of forward and backward derivatives
        out[i] = w_backward * (dv_backward / dt_backward)
            + w_forward * (dv_forward / dt_forward);
    }

    // Last point, using backward difference: (f(x) - f(x - h)) / h
    let last = n - 1;
    out[last] =
        (values[last] - values[last - 1]) / (times[last] - times[last - 1]);

    Ok(())
}

/// Allocate vectors for 1st order derivatives.
pub fn allocate_derivatives_order_1(num: usize) -> Result<Vec<Real>> {
    let velocity = vec![0.0; num];
    Ok(velocity)
}

/// Allocate vectors for 2nd order derivatives.
pub fn allocate_derivatives_order_2(
    num: usize,
) -> Result<(Vec<Real>, Vec<Real>)> {
    let velocity = vec![0.0; num];
    let acceleration = vec![0.0; num];
    Ok((velocity, acceleration))
}

/// Allocate vectors for 3rd order derivatives.
pub fn allocate_derivatives_order_3(
    num: usize,
) -> Result<(Vec<Real>, Vec<Real>, Vec<Real>)> {
    let velocity = vec![0.0; num];
    let acceleration = vec![0.0; num];
    let jerk = vec![0.0; num];
    Ok((velocity, acceleration, jerk))
}

/// Calculate 1st order derivatives (velocity) from time and value
/// data.
///
/// Returns vectors of the same length as input by using finite
/// differences.
pub fn calculate_derivatives_order_1(
    times: &[Real],
    values: &[Real],
    out_velocity: &mut [Real],
) -> Result<()> {
    // Verify slice lengths match
    if times.len() != values.len() || times.len() != out_velocity.len() {
        bail!("Input and output slices must have equal length; times.len()={} values.len()={} out_velocity.len()={}",
              times.len(),
              values.len(),
              out_velocity.len())
    }

    let n = values.len();
    if n < 4 {
        bail!("Need at least 4 points for derivative analysis");
    }

    calc_derivative(times, values, out_velocity)?;

    Ok(())
}

/// Calculate 2nd order derivatives (velocity and acceleration) from
/// time and value data.
///
/// Returns vectors of the same length as input by using finite
/// differences.
pub fn calculate_derivatives_order_2(
    times: &[Real],
    values: &[Real],
    out_velocity: &mut [Real],
    out_acceleration: &mut [Real],
) -> Result<()> {
    // Verify slice lengths match
    if times.len() != values.len()
        || times.len() != out_velocity.len()
        || times.len() != out_acceleration.len()
    {
        bail!("Input and output slices must have equal length; times.len()={} values.len()={} out_velocity.len()={} out_acceleration.len()={}",
        times.len(),
        values.len(),
        out_velocity.len(),
        out_acceleration.len(),
        )
    }

    let n = values.len();
    if n < 4 {
        bail!("Need at least 4 points for derivative analysis");
    }

    calc_derivative(times, values, out_velocity)?;
    calc_derivative(times, &out_velocity, out_acceleration)?;

    Ok(())
}

/// Calculate 3rd order derivatives (velocity, acceleration, and jerk)
/// from time and value data.
///
/// Returns vectors of the same length as input by using finite
/// differences.
pub fn calculate_derivatives_order_3(
    times: &[Real],
    values: &[Real],
    out_velocity: &mut [Real],
    out_acceleration: &mut [Real],
    out_jerk: &mut [Real],
) -> Result<()> {
    // Verify slice lengths match
    if times.len() != values.len()
        || times.len() != out_velocity.len()
        || times.len() != out_acceleration.len()
        || times.len() != out_jerk.len()
    {
        bail!("Input and output slices must have equal length; times.len()={} values.len()={} out_velocity.len()={} out_acceleration.len()={} out_jerk.len()={}",
              times.len(),
              values.len(),
              out_velocity.len(),
              out_acceleration.len(),
              out_jerk.len());
    }

    let n = values.len();
    if n < 4 {
        bail!("Need at least 4 points for derivative analysis");
    }

    calc_derivative(times, values, out_velocity)?;
    calc_derivative(times, out_velocity, out_acceleration)?;
    calc_derivative(times, out_acceleration, out_jerk)?;

    Ok(())
}
