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
use std::cmp::Ordering;

use crate::curve::curvature::allocate_curvature;
use crate::curve::curvature::calculate_curvature;
use crate::curve::derivatives::allocate_derivatives_order_2;
use crate::curve::derivatives::calculate_derivatives_order_2;
use crate::curve::smooth::gaussian::gaussian_smooth_2d;
use crate::math::interpolate::inverse_lerp_f64;
use crate::math::interpolate::lerp_f64;

/// Represents a level in the animation curve pyramid.
#[derive(Debug)]
pub struct PyramidLevel {
    /// X-value (time)
    pub times: Vec<f64>,

    /// Y-value (animated property)
    pub values: Vec<f64>,

    /// First derivative
    pub velocity: Vec<f64>,

    /// Second derivative.
    pub acceleration: Vec<f64>,

    /// Key properties of curvature:
    ///
    /// - It's highest where the curve changes direction rapidly
    ///   (sharp turns).
    ///
    /// - It's zero for straight lines (constant velocity, no
    ///   acceleration).
    ///
    /// - The sign of curvature tells you whether the curve is bending
    ///   up (+) or down (-).
    ///
    /// - Units are 1/radius - smaller radius = sharper curve = higher
    ///   curvature.
    pub curvature: Vec<f64>,

    /// Level 0 is the unchanged input points. Higher levels are
    /// smoothed and reduced number of samples.
    pub level: usize,
}

/// As the `level` argument increases, the calculated number gets
/// larger; '2^level'.
fn pyramid_level_scale(level: usize) -> f64 {
    2.0f64.powi(level as i32)
}

/// As the `level` argument increases, the calculated number gets
/// smaller; '2^(-level)'.
fn pyramid_level_inverse_scale(level: usize) -> f64 {
    2.0f64.powi(-(level as i32))
}

impl PyramidLevel {
    /// Level 0 scale is 1.0. Higher levels are larger.
    pub fn scale(&self) -> f64 {
        pyramid_level_scale(self.level)
    }

    /// Level 0 scale is 1.0. Higher levels are larger.
    pub fn inverse_scale(&self) -> f64 {
        pyramid_level_inverse_scale(self.level)
    }
}

/// Computes appropriate pyramid depth based on input size.
pub fn compute_pyramid_depth(input_size: usize) -> usize {
    debug!("compute_pyramid_depth: input_size={:?}", input_size);

    const MIN_LEVEL_SIZE: usize = 4;
    const MAX_DEPTH: usize = 10; // Prevent excessive depth.
    const MIN_DEPTH: usize = 1;

    let mut depth = 0;
    let mut size = input_size;

    // Ensure at least one level
    while size >= MIN_LEVEL_SIZE && depth < MAX_DEPTH {
        size /= 2;
        depth += 1;
    }

    let depth = depth.clamp(MIN_DEPTH, MAX_DEPTH);
    debug!("compute_pyramid_depth: depth={:?}", depth);

    depth
}

/// Down-sample handling variable intervals and odd/even counts, using
/// a sliding window that considers previous, current, and next points
/// for better curve preservation.
fn downsample_curve_points(
    times: &[f64],
    values: &[f64],
    increment: usize,
) -> Result<(Vec<f64>, Vec<f64>)> {
    debug!("downsample_curve_points: times.len()={:?}", times.len());
    debug!("downsample_curve_points: values.len()={:?}", values.len());
    debug!("downsample_curve_points: increment={:?}", increment);
    if times.len() != values.len() {
        bail!("Times and values slice lengths must match.");
    }
    if times.len() < 2 {
        bail!("Times and values are less than 2.");
    }
    if increment < 1 {
        bail!("Invalid time intervals in curve points");
    }

    let half_increment = increment / 2;
    debug!(
        "downsample_curve_points: half_increment={:?}",
        half_increment
    );

    // TODO: Improve this guessed value.
    let approx_count = (times.len() / 2) + 1;
    let mut out_times = Vec::with_capacity(approx_count);
    let mut out_values = Vec::with_capacity(approx_count);

    // Always keep first point.
    out_times.push(times[0]);
    out_values.push(values[0]);

    // Handle interior points using a sliding 3-point window.
    let mut i = half_increment;
    while i < times.len() - half_increment {
        let curr_time = times[i];
        let prev_time = times[i - half_increment];
        let next_time = times[i + half_increment];

        let curr_value = values[i];
        let prev_value = values[i - half_increment];
        let next_value = values[i + half_increment];

        // Time intervals between points.
        let dt_prev = curr_time - prev_time;
        let dt_next = next_time - curr_time;

        if dt_prev <= 0.0 || dt_next <= 0.0 {
            bail!("Invalid time intervals in curve points");
        }

        // Calculate weights based on time intervals.
        let total_dt = dt_prev + dt_next;
        let w_prev = dt_prev / total_dt;
        let w_next = dt_next / total_dt;
        let w_total = w_prev + w_next;

        // Compute weighted average considering 2 points.
        //
        // TODO: Make sure the current values are used too.
        let weighted_value =
            (prev_value * w_prev + next_value * w_next) / w_total;
        let weighted_time = (prev_time * w_prev + next_time * w_next) / w_total;

        out_times.push(weighted_time);
        out_values.push(weighted_value);

        i += increment;
    }

    // Handle remaining points.
    match times.len().saturating_sub(i) {
        // One point remaining.
        1 => {
            let last_index = times.len() - 1;
            let last_time = times[last_index];
            let last_value = values[last_index];
            out_times.push(last_time);
            out_values.push(last_value);
        }
        // Two points remaining.
        2 => {
            let last_index = times.len() - 1;
            let prev_index = times.len() - 2;
            let last_time = times[last_index];
            let prev_time = times[last_index];
            let last_value = values[last_index];
            let prev_value = values[last_index];

            // Weighted average of final two points
            let dt = last_time - prev_time;
            if dt <= 0.0 {
                bail!("Invalid time interval in final points");
            }

            // Second to last point.
            let time = (prev_time + last_time) * 0.5;
            let value = (prev_value + last_value) * 0.5;
            out_times.push(last_time);
            out_values.push(last_value);

            // Last point.
            out_times.push(last_time);
            out_values.push(last_value);
        }
        _ => {}
    }

    Ok((out_times, out_values))
}

/// Compute derivatives handling variable time intervals and edge cases
fn compute_metadata(
    times: &[f64],
    values: &[f64],
    out_velocity: &mut [f64],
    out_acceleration: &mut [f64],
    out_curvature: &mut [f64],
) -> Result<()> {
    debug!("compute_metadata: times.len()={:?}", times.len());

    if times.len() < 2 {
        bail!("Insufficient points to compute derivatives. Minimum 2 points required.");
    }

    calculate_derivatives_order_2(
        times,
        values,
        out_velocity,
        out_acceleration,
    )?;
    calculate_curvature(out_velocity, out_acceleration, out_curvature)?;

    Ok(())
}

fn create_pyramid_level(
    times: Vec<f64>,
    values: Vec<f64>,
    level_num: usize,
) -> Result<PyramidLevel> {
    let (mut velocity, mut acceleration) =
        allocate_derivatives_order_2(times.len())?;
    let mut curvature = allocate_curvature(times.len())?;
    compute_metadata(
        &times,
        &values,
        &mut velocity,
        &mut acceleration,
        &mut curvature,
    )?;
    Ok(PyramidLevel {
        times: times.to_vec(),
        values: values.to_vec(),
        velocity,
        acceleration,
        curvature,
        level: level_num,
    })
}

/// Builds pyramid with careful handling of boundaries and intervals.
pub fn build_pyramid_levels(
    times: &[f64],
    values: &[f64],
    num_levels: usize,
) -> Result<Vec<PyramidLevel>> {
    debug!("build_pyramid_levels: values.len()={:?}", values.len());
    debug!("build_pyramid_levels: times.len()={:?}", times.len());
    debug!("build_pyramid_levels: num_levels={:?}", num_levels);

    let mut pyramid = Vec::with_capacity(num_levels);

    // Initialize base level (level zero).
    let level_num = 0;
    let pyramid_level =
        create_pyramid_level(times.to_vec(), values.to_vec(), level_num)?;
    pyramid.push(pyramid_level);

    const MIN_PYRAMID_CURVE_SAMPLES: usize = 8;

    // Build subsequent levels with validation
    for level_num in 1..num_levels {
        debug!("build_pyramid_levels: level_num={level_num}");
        let prev_level = &pyramid[level_num - 1];

        if prev_level.times.len() < MIN_PYRAMID_CURVE_SAMPLES {
            break;
        }

        let scale = pyramid_level_scale(level_num);
        debug!("build_pyramid_levels: scale={scale}");

        // Using a smaller smooth width than the down-sampling seems
        // to provide more robust and uniform results.
        let smooth_width = scale * 0.5;
        debug!("build_pyramid_levels: smooth_width={smooth_width}");

        let mut smoothed_values = vec![0.0; values.len()];
        gaussian_smooth_2d(times, values, smooth_width, &mut smoothed_values)?;
        debug!(
            "build_pyramid_levels: smoothed_values.len()={}",
            smoothed_values.len()
        );

        // Reduce point count.
        let (downsampled_times, downsampled_values) =
            downsample_curve_points(times, &smoothed_values, scale as usize)?;
        debug!(
            "build_pyramid_levels: downsampled_times.len()={}",
            downsampled_times.len()
        );

        let pyramid_level = create_pyramid_level(
            downsampled_times,
            downsampled_values,
            level_num,
        )?;
        pyramid.push(pyramid_level);
    }

    Ok(pyramid)
}
