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
use std::fmt;

use crate::constant::Real;
use crate::curve::derivatives::allocate_derivatives_order_2;
use crate::curve::derivatives::calculate_derivatives_order_2;
use crate::math::statistics::calc_median_absolute_deviation_sigma;
use crate::math::statistics::calc_population_standard_deviation;
use crate::math::statistics::calc_z_score;
use crate::math::statistics::SortedDataSlice;
use crate::math::statistics::SortedDataSliceOps;

/// Represents a point that was classified as a pop
#[derive(Debug)]
pub struct PopPoint {
    pub time: Real,
    pub value: Real,
    pub score: Real,
}

impl fmt::Display for PopPoint {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            f,
            "PopPoint [ t={:.2}, v={:.2} (score={:.2}) ]",
            self.time, self.value, self.score
        )
    }
}

fn calculate_per_frame_pop_score(
    times: &[Real],
    values: &[Real],
    out_velocity: &mut [Real],
    out_acceleration: &mut [Real],
    out_scores: &mut [Real],
) -> Result<()> {
    if (times.len() != values.len()) && (times.len() != out_scores.len()) {
        bail!("Times, values and output arrays must have the same length.");
    }

    calculate_derivatives_order_2(
        times,
        values,
        out_velocity,
        out_acceleration,
    )?;

    let mut sorted_acceleration = out_acceleration.to_vec();
    sorted_acceleration.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let acceleration_slice =
        SortedDataSlice::new(&sorted_acceleration, None, None)?;

    // Reuse this allocation many times.
    let mut sorted_deviations = vec![0.0; values.len()];

    for i in 0..times.len() {
        let acceleration = out_acceleration[i];
        let acceleration_mad_sigma = calc_median_absolute_deviation_sigma(
            acceleration,
            &acceleration_slice,
            &mut sorted_deviations,
        )?;
        out_scores[i] = acceleration_mad_sigma;
    }

    let mut sorted_scores = out_scores.to_vec();
    sorted_scores.sort_by(|a, b| a.partial_cmp(b).unwrap());
    let scores_slice = SortedDataSlice::new(&sorted_scores, None, None)?;

    let std_dev = calc_population_standard_deviation(&scores_slice)?;
    debug!("calculate_per_frame_pop_score: scores std_dev={std_dev}");

    let median = scores_slice.median();
    debug!("calculate_per_frame_pop_score: scores median={median}");

    for i in 0..out_scores.len() {
        let score = calc_z_score(median, std_dev, out_scores[i]).abs();
        out_scores[i] = score;
    }

    Ok(())
}

/// Find pops in the data.
pub fn detect_curve_pops(
    times: &[Real],
    values: &[Real],
    threshold: Real,
) -> Result<Vec<PopPoint>> {
    if times.len() != values.len() {
        bail!("Times and values must have the same length.");
    }

    let n = times.len();
    let (mut velocity, mut acceleration) =
        allocate_derivatives_order_2(times.len())?;
    let mut scores = vec![0.0; n];

    calculate_per_frame_pop_score(
        &times,
        &values,
        &mut velocity,
        &mut acceleration,
        &mut scores,
    )?;

    let mut out_values = Vec::new();
    out_values.reserve(n);

    let include_neighbours = false;
    if include_neighbours {
        for i in 0..n {
            let prev = i.saturating_sub(1);
            let next = (i + 1).min(n - 1);

            let score_prev = scores[prev];
            let score_current = scores[i];
            let score_next = scores[next];

            let pop_prev = score_prev > threshold;
            let pop_current = score_current > threshold;
            let pop_next = score_next > threshold;

            if pop_prev || pop_current || pop_next {
                let t = times[i];
                let v = values[i];

                let point = PopPoint {
                    time: t,
                    value: v,
                    score: score_current,
                };
                out_values.push(point);
            }
        }
    } else {
        for i in 0..n {
            let score = scores[i];
            if score > threshold {
                let t = times[i];
                let v = values[i];

                let point = PopPoint {
                    time: t,
                    value: v,
                    score: score,
                };
                out_values.push(point);
            }
        }
    }

    Ok(out_values)
}

pub fn filter_curve_pops(
    times: &[Real],
    values: &[Real],
    threshold: Real,
) -> Result<Vec<(Real, Real)>> {
    if times.len() != values.len() {
        bail!("Times and values must have the same length.");
    }

    let n = times.len();
    let (mut velocity, mut acceleration) =
        allocate_derivatives_order_2(times.len())?;
    let mut scores = vec![0.0; n];

    calculate_per_frame_pop_score(
        &times,
        &values,
        &mut velocity,
        &mut acceleration,
        &mut scores,
    )?;

    let mut out_values_xy = Vec::new();
    out_values_xy.reserve(n);

    let include_neighbours = false;
    if include_neighbours {
        for i in 0..n {
            let prev = i.saturating_sub(1);
            let next = (i + 1).min(n - 1);

            let score_prev = scores[prev];
            let score_current = scores[i];
            let score_next = scores[next];

            let pop_prev = score_prev <= threshold;
            let pop_current = score_current <= threshold;
            let pop_next = score_next <= threshold;

            if pop_prev || pop_current || pop_next {
                let t = times[i];
                let v = values[i];
                out_values_xy.push((t, v));
            }
        }
    } else {
        for i in 0..n {
            let score = scores[i];
            if score <= threshold {
                let t = times[i];
                let v = values[i];
                out_values_xy.push((t, v));
            }
        }
    }

    Ok(out_values_xy)
}
