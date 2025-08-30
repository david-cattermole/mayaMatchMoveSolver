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
use crate::curve::curvature::allocate_curvature;
use crate::curve::curvature::calculate_curvature;
use crate::curve::derivatives::allocate_derivatives_order_2;
use crate::curve::derivatives::calculate_derivatives_order_2;
use crate::curve::detect::keypoints::detect_level_keypoints;
use crate::curve::detect::keypoints::filter_keypoints_by_type_and_level;
use crate::curve::detect::keypoints::KeypointType;
use crate::curve::smooth::gaussian::gaussian_smooth_2d;
use crate::math::interpolate::evaluate_curve_points;
use crate::math::interpolate::Interpolation;

/// Represents a level in the animation curve pyramid.
#[derive(Debug)]
pub struct PyramidLevel {
    /// X-value (time)
    pub times: Vec<Real>,

    /// Y-value (animated property)
    pub values: Vec<Real>,

    /// First derivative
    pub velocity: Vec<Real>,

    /// Second derivative.
    pub acceleration: Vec<Real>,

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
    pub curvature: Vec<Real>,

    /// Level 0 is the unchanged input points. Higher levels are
    /// smoothed and reduced number of samples.
    pub level: usize,
}

/// As the `level` argument increases, the calculated number gets
/// larger; '2^level'.
fn pyramid_level_scale(level: usize) -> Real {
    (2.0 as Real).powi(level as i32)
}

/// As the `level` argument increases, the calculated number gets
/// smaller; '2^(-level)'.
fn pyramid_level_inverse_scale(level: usize) -> Real {
    (2.0 as Real).powi(-(level as i32))
}

impl PyramidLevel {
    /// Level 0 scale is 1.0. Higher levels are larger.
    pub fn scale(&self) -> Real {
        pyramid_level_scale(self.level)
    }

    /// Level 0 scale is 1.0. Higher levels are larger.
    pub fn inverse_scale(&self) -> Real {
        pyramid_level_inverse_scale(self.level)
    }
}

/// Computes appropriate pyramid depth based on input size.
pub fn compute_pyramid_depth(input_size: usize) -> usize {
    debug!("compute_pyramid_depth: input_size={:?}", input_size);

    const MIN_LEVEL_SIZE: usize = 8;
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

/// Down-sample the curve points by a scale factor.
fn downsample_curve_points(
    times: &[Real],
    values: &[Real],
    scale: Real,
) -> Result<(Vec<Real>, Vec<Real>)> {
    debug!("downsample_curve_points: times.len()={:?}", times.len());
    debug!("downsample_curve_points: values.len()={:?}", values.len());

    if times.len() != values.len() {
        bail!("Times and values slice lengths must match.");
    }
    if times.len() < 2 {
        bail!("Times and values are less than 2.");
    }

    let first_time = times[0];
    let last_index = times.len() - 1;
    let last_time = times[last_index];

    let time_range = last_time - first_time;
    let increment = (time_range / times.len() as Real) * scale;
    let count = ((time_range / increment) as usize) + 1;
    debug!("downsample_curve_points: time_range={time_range}");
    debug!("downsample_curve_points: increment={increment}");
    debug!("downsample_curve_points: count={count}");

    let mut out_times = Vec::with_capacity(count);
    let mut current_time = first_time;
    while current_time <= last_time {
        debug!("downsample_curve_points: current_time={current_time}");
        out_times.push(current_time);
        current_time += increment;
    }

    // Must ensure that the full time range is maintained - we don't
    // want to have the curve shrunk each time a down-sampling occurs.
    let out_times_last_index = out_times.len() - 1;
    let out_times_last_time = out_times[out_times_last_index];
    let diff = out_times_last_time - last_time;
    if diff.abs() < increment {
        out_times[out_times_last_index] = last_time;
    } else {
        out_times.push(last_time);
    }

    // Because quadratic NUBS interpolation allows a smooth
    // re-sampling between points, and does not have tangent issues on
    // the boundaries.
    let interpolation_method = Interpolation::QuadraticNUBS;

    let downsampled_xy =
        evaluate_curve_points(&out_times, times, values, interpolation_method);
    assert_eq!(out_times.len(), downsampled_xy.len());

    let mut out_values = Vec::with_capacity(count);
    for xy in downsampled_xy {
        out_values.push(xy.1);
    }
    assert_eq!(out_times.len(), out_values.len());

    debug!(
        "downsample_curve_points: out_times.len()={:?}",
        out_times.len()
    );
    debug!(
        "downsample_curve_points: out_values.len()={:?}",
        out_values.len()
    );

    Ok((out_times, out_values))
}

/// Compute derivatives handling variable time intervals and edge cases
fn compute_metadata(
    times: &[Real],
    values: &[Real],
    out_velocity: &mut [Real],
    out_acceleration: &mut [Real],
    out_curvature: &mut [Real],
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
    times: Vec<Real>,
    values: Vec<Real>,
    level_num: usize,
) -> Result<PyramidLevel> {
    debug!("create_pyramid_level: level_num={level_num}");
    for (t, v) in times.iter().zip(values.iter()) {
        debug!("create_pyramid_level: t={t} v={v}");
    }

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

fn merge_curves(
    samples_a: &[(Real, Real)],
    samples_b: &[(Real, Real)],
    time_width: Real,
) -> Result<Vec<(Real, Real)>> {
    let mut samples = Vec::with_capacity(samples_a.len() + samples_b.len());

    let mut overlapping_with_a = vec![false; samples_a.len()];
    for xy_b in samples_b.iter() {
        let time_b = xy_b.0;
        let _value_b = xy_b.1;
        for (i, (time_a, _value_a)) in samples_a.iter().enumerate() {
            let time_diff = (time_a - time_b).abs();
            if time_diff < time_width {
                overlapping_with_a[i] = true;
            }
        }
    }

    for (xy, overlapping) in samples_a.iter().zip(overlapping_with_a) {
        if overlapping == false {
            samples.push(*xy);
        }
    }

    for xy in samples_b.iter() {
        samples.push(*xy);
    }

    // Sort by time
    samples.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());

    Ok(samples)
}

/// Builds pyramid with careful handling of boundaries and intervals.
pub fn build_pyramid_levels(
    times: &[Real],
    values: &[Real],
    num_levels: usize,
) -> Result<Vec<PyramidLevel>> {
    debug!("build_pyramid_levels: values.len()={:?}", values.len());
    debug!("build_pyramid_levels: times.len()={:?}", times.len());
    debug!("build_pyramid_levels: num_levels={:?}", num_levels);

    let use_keypoint_detection = true;
    let smooth_factor = 1.0;

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
        let smooth_width = scale * smooth_factor;
        debug!("build_pyramid_levels: smooth_width={smooth_width}");

        let mut smoothed_values = vec![0.0; values.len()];
        gaussian_smooth_2d(times, values, smooth_width, &mut smoothed_values)?;
        debug!(
            "build_pyramid_levels: smoothed_values.len()={}",
            smoothed_values.len()
        );

        let (downsampled_times, downsampled_values) =
            downsample_curve_points(times, &smoothed_values, scale)?;
        debug!(
            "build_pyramid_levels: downsampled_times.len()={}",
            downsampled_times.len()
        );

        let (out_times, out_values) = if use_keypoint_detection == false {
            // Uniform sampling.
            (downsampled_times, downsampled_values)
        } else {
            // A mixture of uniform sampling with key-point feature
            // preservation.
            let first_time = times[0];
            let last_index = times.len() - 1;
            let last_time = times[last_index];

            let reduction_scale = scale;
            let time_range = last_time - first_time;
            let increment =
                (time_range / times.len() as Real) * reduction_scale;
            let count = ((time_range / increment) as usize) + 1;
            debug!("build_pyamid_levels: time_range={time_range}");
            debug!("build_pyamid_levels: increment={increment}");
            debug!("build_pyamid_levels: count={count}");

            let target_keypoints = count / 2;

            // Detect keypoints.
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
            let all_keypoints = detect_level_keypoints(
                &times,
                &smoothed_values,
                &velocity,
                &acceleration,
                &curvature,
                level_num,
            );
            debug!(
                "build_pyamid_levels: all_keypoints.len()={}",
                all_keypoints.len()
            );

            let mut selected_keypoints = Vec::with_capacity(target_keypoints);

            // Always include endpoints.
            for keypoint in all_keypoints
                .iter()
                .filter(|k| k.keypoint_type == KeypointType::Endpoint)
            {
                selected_keypoints.push(keypoint.clone());
            }

            // Minimum spacing between keypoints (adaptive based on target
            // count).
            let min_spacing = time_range / (target_keypoints as Real * 2.0);

            filter_keypoints_by_type_and_level(
                KeypointType::ExtremeValue,
                level_num,
                min_spacing,
                target_keypoints,
                &all_keypoints,
                &mut selected_keypoints,
            );

            let mut downsampled_xy: Vec<_> = downsampled_times
                .iter()
                .zip(downsampled_values)
                .map(|(&t, v)| (t, v))
                .collect();
            downsampled_xy.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());

            let mut keypoints = Vec::with_capacity(selected_keypoints.len());
            for keypoint in selected_keypoints.iter() {
                keypoints.push((keypoint.time, keypoint.value));
            }
            keypoints.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap());

            let mut samples = merge_curves(&downsampled_xy, &keypoints, scale)?;

            // Ensure first frame is maintained.
            const EPSILON: Real = 0.0001;
            let first_sample_xy = samples[0];
            let first_time_diff = (times[0] - first_sample_xy.0).abs();
            if first_time_diff > EPSILON {
                samples.insert(0, (times[0], smoothed_values[0]));
            }

            // Ensure last frame is maintained.
            let times_last_index = times.len() - 1;
            let samples_last_index = samples.len() - 1;
            let last_sample_xy = samples[samples_last_index];
            let last_time_diff =
                (times[times_last_index] - last_sample_xy.0).abs();
            if last_time_diff > EPSILON {
                samples.push((
                    times[times_last_index],
                    smoothed_values[times_last_index],
                ));
            }

            let out_times = samples.iter().map(|xy| xy.0 as Real).collect();
            let out_values = samples.iter().map(|xy| xy.1 as Real).collect();
            (out_times, out_values)
        };

        let pyramid_level =
            create_pyramid_level(out_times, out_values, level_num)?;
        pyramid.push(pyramid_level);
    }

    Ok(pyramid)
}
