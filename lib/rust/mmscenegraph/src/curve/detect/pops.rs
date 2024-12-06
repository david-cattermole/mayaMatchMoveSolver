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
use crate::curve::derivatives::allocate_derivatives_order_2;
use crate::curve::derivatives::calculate_derivatives_order_2;
use crate::curve::smooth::gaussian::gaussian_smooth_2d;
use crate::math::statistics::calc_median_absolute_deviation_sigma;
use crate::math::statistics::calc_population_standard_deviation;
use crate::math::statistics::calc_z_score;
use crate::math::statistics::SortedDataSlice;
use crate::math::statistics::SortedDataSliceOps;

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

fn create_pop_values(times: &[Real], values: &[Real]) -> Result<Vec<f64>> {
    // Because a value of 3.0 seems to work best with the test data.
    let width = 3.0;

    let mut diff_values_a = values.to_vec();
    gaussian_smooth_2d(times, values, width, &mut diff_values_a)?;

    let n = values.len();
    for i in 0..n {
        let value = values[i];
        let smoothed_value = diff_values_a[i];
        diff_values_a[i] = smoothed_value - value;
    }

    Ok(diff_values_a)
}

/// Find pops in the data.
pub fn detect_curve_pops(
    times: &[Real],
    values: &[Real],
    threshold: Real,
) -> Result<Vec<(Real, Real)>> {
    if times.len() != values.len() {
        bail!("Times and values must have the same length.");
    }

    let diff_values = create_pop_values(times, values)?;

    let n = times.len();
    let (mut velocity, mut acceleration) = allocate_derivatives_order_2(n)?;
    let mut scores = vec![0.0; n];

    calculate_per_frame_pop_score(
        &times,
        &diff_values,
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
                out_values.push((t, v));
            }
        }
    } else {
        for i in 0..n {
            let score = scores[i];
            let t = times[i];
            let v = values[i];
            debug!("t={t} v={v} score={score}");
            if score > threshold {
                out_values.push((t, v));
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

    let diff_values = create_pop_values(times, values)?;

    let n = times.len();
    let (mut velocity, mut acceleration) =
        allocate_derivatives_order_2(values.len())?;
    let mut scores = vec![0.0; n];

    calculate_per_frame_pop_score(
        &times,
        &diff_values,
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

/// Return the pop-scores, for each frame in the curve.
pub fn detect_curve_pop_scores(
    times: &[Real],
    values: &[Real],
    out_scores: &mut [Real],
) -> Result<()> {
    if times.len() != values.len() {
        bail!("Times and values must have the same length.");
    }
    if times.len() != out_scores.len() {
        bail!("Times and out_scores must have the same length.");
    }

    let diff_values = create_pop_values(times, values)?;

    let n = times.len();
    let (mut velocity, mut acceleration) = allocate_derivatives_order_2(n)?;

    calculate_per_frame_pop_score(
        &times,
        &diff_values,
        &mut velocity,
        &mut acceleration,
        out_scores,
    )?;

    Ok(())
}
