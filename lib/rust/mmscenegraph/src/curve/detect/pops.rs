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
use crate::curve::derivatives::allocate_derivatives_order_1;
use crate::curve::derivatives::calculate_derivatives_order_1;
use crate::math::distributions::standard_deviation_of_values;
use crate::math::distributions::Statistics;

// Calculates how many standard deviations a value is from the mean.
fn calculate_z_score(stats: &Statistics, value: f64) -> f64 {
    (value - stats.mean).abs() / stats.std_dev.max(1e-10)
}

// Normalize the deviations relative to the global statistics.
//
// Adjusts a local deviation score relative to global statistics.
fn normalize_local_deviation(
    global_stats: &Statistics,
    local_stats: &Statistics,
    deviation: f64,
) -> f64 {
    deviation * (local_stats.std_dev / global_stats.std_dev.max(1e-10))
}

// Computes a smoothness score for a window of the animation curve using velocity statistics.
fn calculate_window_smoothness_score(
    i: usize,
    window_start: usize,
    window_end: usize,
    times: &[f64],
    values: &[f64],
    velocity: &[f64],
    global_velocity_stats: &Statistics,
) -> f64 {
    let window_size = if window_end > window_start {
        window_end - window_start
    } else {
        window_start - window_end
    };
    if window_size < 2 {
        return 0.0;
    }

    let local_velocity = &velocity[window_start..window_end];
    let local_velocity_stats = standard_deviation_of_values(&local_velocity);
    let local_velocity_stats = match local_velocity_stats {
        Some(value) => value,
        None => return 0.0,
    };

    // Check for discontinuity.
    let velocity_deviation =
        calculate_z_score(&local_velocity_stats, velocity[i]);

    // Normalize the deviations relative to the global statistics.
    let smoothness_score = normalize_local_deviation(
        &global_velocity_stats,
        &local_velocity_stats,
        velocity_deviation,
    );

    smoothness_score
}

/// Represents a point that was classified as a pop
#[derive(Debug)]
pub struct PopPoint {
    pub time: f64,
    pub value: f64,
    pub score: f64,
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
    times: &[f64],
    values: &[f64],
    senstivity: f64,
    out_velocity: &mut [f64],
    out_scores: &mut [f64],
) -> Result<()> {
    if (times.len() != values.len()) && (times.len() != out_scores.len()) {
        bail!("Times, values and output arrays must have the same length.");
    }

    calculate_derivatives_order_1(times, values, out_velocity)?;

    // Calculate statistics for each derivative
    let global_velocity_stats =
        standard_deviation_of_values(&out_velocity).unwrap();

    let n = times.len();
    let window_size = 2;

    // Forward pass
    let mut i = window_size;
    while i < n {
        let window_start = i - window_size;
        let window_end = i;

        let score = calculate_window_smoothness_score(
            i,
            window_start,
            window_end,
            times,
            values,
            &out_velocity,
            &global_velocity_stats,
        );
        out_scores[i] = score;

        i += 1;
        if score > senstivity {
            let next = i + 1;
            if next <= (n - 1) {
                i = next;
            }
        }
    }

    // Backward pass
    let mut i = n - window_size;
    while i > 0 {
        let window_start = i;
        let window_end = i + window_size;

        let score = calculate_window_smoothness_score(
            i,
            window_start,
            window_end,
            times,
            values,
            &out_velocity,
            &global_velocity_stats,
        );
        out_scores[i] = score.min(out_scores[i]);

        i -= 1;
        if score > senstivity {
            let next = i.saturating_sub(1);
            if next <= (n - 1) {
                i = next;
            }
        }
    }

    Ok(())
}

/// Find pops in the data.
pub fn detect_curve_pops(
    times: &[f64],
    values: &[f64],
    threshold: f64,
) -> Result<Vec<PopPoint>> {
    if times.len() != values.len() {
        bail!("Times and values must have the same length.");
    }

    let n = times.len();
    let mut velocity = allocate_derivatives_order_1(times.len())?;
    let mut scores = vec![0.0; n];

    let sensitivity = threshold;
    calculate_per_frame_pop_score(
        &times,
        &values,
        sensitivity,
        &mut velocity,
        &mut scores,
    )?;

    let mut out_values = Vec::new();
    out_values.reserve(n);

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

    Ok(out_values)
}

pub fn filter_curve_pops(
    times: &[f64],
    values: &[f64],
    threshold: f64,
) -> Result<Vec<(f64, f64)>> {
    if times.len() != values.len() {
        bail!("Times and values must have the same length.");
    }

    let n = times.len();
    let mut velocity = allocate_derivatives_order_1(times.len())?;
    let mut scores = vec![0.0; n];

    let sensitivity = threshold;
    calculate_per_frame_pop_score(
        &times,
        &values,
        sensitivity,
        &mut velocity,
        &mut scores,
    )?;

    let mut out_values_xy = Vec::new();
    out_values_xy.reserve(n);

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

    // Ok((out_values_x, out_values_y))
    Ok(out_values_xy)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_detect_acceleration_changes() -> Result<()> {
        let times = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0];
        let values = vec![
            // Smooth acceleration
            1.0, 1.2, 1.5, 2.0, 2.7, 3.6,
            // Sudden pop (discontinuous acceleration)
            5.0, // Return to smooth motion
            5.5, 5.8, 6.0,
        ];

        let threshold = 3.0;
        let pops = detect_curve_pops(&times, &values, threshold)?;

        assert!(pops[4].score < threshold); // Smooth acceleration should not be detected
        assert!(pops[6].score > threshold); // Sudden pop should be detected

        Ok(())
    }

    #[test]
    fn test_smooth_acceleration() -> Result<()> {
        let times = vec![1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0];
        // Gradually increasing acceleration
        let values = vec![0.0, 0.1, 0.4, 0.9, 1.6, 2.5, 3.6, 4.9];

        let threshold = 3.0;
        let pops = detect_curve_pops(&times, &values, threshold)?;

        // Should not detect any pops in smoothly accelerating curve
        assert!(pops.iter().all(|x| x.score < threshold));

        Ok(())
    }
}
