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
use crate::math::interpolate::evaluate_curve_points;
use crate::math::interpolate::Interpolation;

pub fn resample_uniform_xy(
    values_xy: &[(Real, Real)],
    start: Real,
    end: Real,
    increment: Real,
    interpolation_method: Interpolation,
) -> Result<Vec<(Real, Real)>> {
    if values_xy.is_empty() {
        bail!("Input value slices must have values.");
    }
    if start == end {
        bail!("Start and end times must be different.");
    }
    if increment <= 0.0 {
        bail!("Increment must be positive.");
    }

    let expected_count = ((end - start) / increment).ceil() as usize + 1;
    debug!("expected_count: {expected_count:?}");
    assert!(expected_count > 0, "Expected count must be greater than 0.");

    // Split input into separate x and y vectors.
    let (control_points_x, control_points_y): (Vec<Real>, Vec<Real>) =
        values_xy.iter().copied().unzip();

    // Generate uniform x values for resampling.
    let mut x_values = Vec::with_capacity(expected_count);
    let mut current_time = start;
    while current_time <= end {
        x_values.push(current_time);
        debug!("resample: current_time={current_time}");
        current_time += increment;
    }

    Ok(evaluate_curve_points(
        &x_values,
        &control_points_x,
        &control_points_y,
        interpolation_method,
    ))
}
