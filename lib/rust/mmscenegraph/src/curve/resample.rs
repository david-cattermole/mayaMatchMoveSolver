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

#[derive(Debug, Copy, Clone)]
pub enum Interpolation {
    Nearest,
    Linear,
}

fn resample_uniform_xy_nearest(
    values_xy: &[(Real, Real)],
    start: Real,
    end: Real,
    increment: Real,
    out_values_xy: &mut Vec<(Real, Real)>,
) {
    let mut current_time = start;
    while current_time <= end {
        // Binary search for the closest point.
        let closest_index = values_xy
            .binary_search_by(|&(x, _)| {
                let diff = x - current_time;
                if diff.abs() < f64::EPSILON {
                    std::cmp::Ordering::Equal
                } else if diff < 0.0 {
                    std::cmp::Ordering::Less
                } else {
                    std::cmp::Ordering::Greater
                }
            })
            .unwrap_or_else(|i| {
                if i == 0 {
                    0
                } else if i >= values_xy.len() {
                    values_xy.len() - 1
                } else {
                    // Compare distances to find nearest.
                    let prev_dist = (values_xy[i - 1].0 - current_time).abs();
                    let next_dist = (values_xy[i].0 - current_time).abs();
                    if prev_dist < next_dist {
                        i - 1
                    } else {
                        i
                    }
                }
            });

        out_values_xy.push((current_time, values_xy[closest_index].1));
        current_time += increment;
    }
}

fn resample_uniform_xy_linear(
    values_xy: &[(Real, Real)],
    start: Real,
    end: Real,
    increment: Real,
    out_values_xy: &mut Vec<(Real, Real)>,
) {
    let mut current_time = start;
    while current_time <= end {
        // Find surrounding points for interpolation.
        let search_result = values_xy.binary_search_by(|&(x, _)| {
            let diff = x - current_time;
            if diff.abs() < f64::EPSILON {
                std::cmp::Ordering::Equal
            } else if diff < 0.0 {
                std::cmp::Ordering::Less
            } else {
                std::cmp::Ordering::Greater
            }
        });

        let interpolated_value = match search_result {
            Ok(exact_index) => {
                // Exact match found.
                values_xy[exact_index].1
            }
            Err(insert_index) => {
                if insert_index == 0 {
                    // Before first point.
                    values_xy[0].1
                } else if insert_index >= values_xy.len() {
                    // After last point.
                    values_xy[values_xy.len() - 1].1
                } else {
                    // Interpolate between points.
                    let (x1, y1) = values_xy[insert_index - 1];
                    let (x2, y2) = values_xy[insert_index];

                    // Linear interpolation formula:
                    // y = y1 + (y2-y1)*(x-x1)/(x2-x1)
                    let t = (current_time - x1) / (x2 - x1);
                    y1 + (y2 - y1) * t
                }
            }
        };

        out_values_xy.push((current_time, interpolated_value));
        current_time += increment;
    }
}

pub fn resample_uniform_xy(
    values_xy: &[(Real, Real)],
    start: Real,
    end: Real,
    increment: Real,
    interpolation: Interpolation,
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
    if expected_count == 0 {
        bail!("Expected count must be greater than 0.");
    }

    let mut out_values_xy = Vec::with_capacity(expected_count);

    match interpolation {
        Interpolation::Nearest => resample_uniform_xy_nearest(
            values_xy,
            start,
            end,
            increment,
            &mut out_values_xy,
        ),
        Interpolation::Linear => resample_uniform_xy_linear(
            values_xy,
            start,
            end,
            increment,
            &mut out_values_xy,
        ),
    }

    Ok(out_values_xy)
}
