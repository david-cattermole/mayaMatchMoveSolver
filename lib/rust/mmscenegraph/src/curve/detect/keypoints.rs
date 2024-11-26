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
use std::cmp::Ordering;
use thiserror::Error;

use crate::curve::pyramid::build_pyramid_levels;
use crate::curve::pyramid::compute_pyramid_depth;
use crate::curve::pyramid::PyramidLevel;

#[derive(Error, Debug)]
enum KeypointsError {
    #[error("Target keypoints must be greater than 0.")]
    TargetKeypointsTooLow,

    #[error("Insufficient points in curve (minimum 2 required).")]
    NonSequentialTime,

    #[error("Time values must be strictly increasing.")]
    InsufficientPoints,
}

#[derive(Debug, Clone, PartialEq)]
pub enum KeypointType {
    ExtremeValue, // Local min/max in value
    Inflection,   // Curvature sign change
    VelocityPeak, // Local max in velocity
    Endpoint,     // Start/end points
}

/// Keypoint with importance score used for sorting.
#[derive(Debug, Clone)]
pub struct RankedKeypoint {
    pub time: f64,
    pub value: f64,
    pub importance: f64,
    pub level_detected: usize,
    pub keypoint_type: KeypointType,
}

impl Ord for RankedKeypoint {
    fn cmp(&self, other: &Self) -> Ordering {
        // First compare level_detected.
        match self.level_detected.cmp(&other.level_detected) {
            Ordering::Equal => {
                // If level_detected is equal, compare importance.
                self.importance
                    .partial_cmp(&other.importance)
                    .unwrap_or(Ordering::Equal)
            }
            ordering => ordering,
        }
    }
}

impl PartialOrd for RankedKeypoint {
    fn partial_cmp(&self, other: &Self) -> Option<Ordering> {
        Some(self.cmp(other))
    }
}

impl PartialEq for RankedKeypoint {
    fn eq(&self, other: &Self) -> bool {
        // self.importance == other.importance
        self.importance == other.importance
            && self.level_detected == other.level_detected
    }
}

impl Eq for RankedKeypoint {}

/// Compute importance for different keypoint types.
fn compute_extreme_value_importance(
    curr_value: f64,
    prev_value: f64,
    next_value: f64,
    curr_curvature: f64,
) -> f64 {
    let value_diff = ((curr_value - prev_value).abs()
        + (curr_value - next_value).abs())
        / 2.0;
    let curvature_weight = curr_curvature.abs();
    value_diff * curvature_weight
}

fn compute_inflection_importance(velocity: f64, curvature: f64) -> f64 {
    curvature.abs() * (1.0 + velocity.abs())
}

fn compute_velocity_importance(velocity: f64, acceleration: f64) -> f64 {
    velocity.abs() * (1.0 + acceleration.abs())
}

/// Detect keypoints specific to animation curves
fn detect_level_keypoints(
    level: &PyramidLevel,
    existing_keypoints: &[RankedKeypoint],
    current_level: usize,
) -> Vec<RankedKeypoint> {
    // println!("detect_level_keypoints: level.level={:?}", level.level);
    // println!("detect_level_keypoints: level.scale={:?}", level.scale());
    // println!(
    //     "detect_level_keypoints: existing_keypoints.len()={:?}",
    //     existing_keypoints.len()
    // );
    // println!(
    //     "detect_level_keypoints: existing_keypoints={:?}",
    //     existing_keypoints
    // );
    // println!("detect_level_keypoints: current_level={:?}", current_level);

    let mut keypoints = Vec::new();
    let times = &level.times;
    let values = &level.values;
    let velocity = &level.velocity;
    let acceleration = &level.acceleration;
    let curvature = &level.curvature;

    for i in 1..times.len() - 1 {
        let curr_time = times[i];
        let prev_time = times[i - 1];
        let next_time = times[i + 1];

        let curr_value = values[i];
        let prev_value = values[i - 1];
        let next_value = values[i + 1];

        let curr_velocity = velocity[i];
        let prev_velocity = velocity[i - 1];
        let next_velocity = velocity[i + 1];

        let curr_acceleration = acceleration[i];
        let prev_acceleration = acceleration[i - 1];
        let next_acceleration = acceleration[i + 1];

        let curr_curvature = curvature[i];
        let prev_curvature = curvature[i - 1];
        let next_curvature = curvature[i + 1];

        let extreme_value_max =
            curr_value > prev_value && curr_value > next_value;
        let extreme_value_min =
            curr_value < prev_value && curr_value < next_value;

        let is_inflection = (curr_curvature * prev_curvature) < 0.0;

        let velocity_peak = (curr_velocity.abs() > prev_velocity.abs())
            && (curr_velocity.abs() > next_velocity.abs());

        let acceleration_change = (curr_acceleration - prev_acceleration).abs();

        let mut importance = 0.0;
        let mut keypoint_type = None;
        if extreme_value_max || extreme_value_min {
            importance = compute_extreme_value_importance(
                curr_value,
                prev_value,
                next_value,
                curr_curvature,
            );
            keypoint_type = Some(KeypointType::ExtremeValue);
        } else if is_inflection {
            importance =
                compute_inflection_importance(curr_velocity, curr_curvature);
            keypoint_type = Some(KeypointType::Inflection);
        } else if velocity_peak {
            importance =
                compute_velocity_importance(curr_velocity, curr_acceleration);
            keypoint_type = Some(KeypointType::VelocityPeak);
        }

        // If point is important and not near existing keypoints
        if let Some(kp_type) = keypoint_type {
            let level_scale = level.scale();
            // let level_scale = level.inverse_scale();

            if !is_near_existing_keypoint(
                curr_time,
                level_scale,
                existing_keypoints,
            ) {
                keypoints.push(RankedKeypoint {
                    time: curr_time,
                    value: curr_value,
                    importance,
                    level_detected: current_level,
                    keypoint_type: kp_type,
                });
            }
        }
    }

    // println!(
    //     "detect_level_keypoints: keypoints.len()={:?}",
    //     keypoints.len()
    // );
    // for keypoint in &keypoints {
    //     println!("detect_level_keypoints: keypoint={:?}", keypoint);
    // }

    keypoints
}

/// Check if point is near any existing keypoint.
fn is_near_existing_keypoint(
    time: f64,
    scale: f64,
    existing_keypoints: &[RankedKeypoint],
) -> bool {
    // println!("is_near_existing_keypoint: time={:?}", time);
    // println!("is_near_existing_keypoint: scale={:?}", scale);
    // println!(
    //     "is_near_existing_keypoint: existing_keypoints.len()={:?}",
    //     existing_keypoints.len()
    // );

    // Larger scale values are lower-resolution levels - each sample
    // represents a larger number of the original samples.
    let threshold = scale;

    for existing_point in existing_keypoints.iter() {
        let time_diff = (time - existing_point.time).abs();
        if time_diff < threshold {
            // println!(
            //     "is_near_existing_keypoint: found close! time_diff={:?} | {:?}",
            //     time_diff, existing_point
            // );

            return true;
        }
    }

    false
}

/// Validates input curve data.
fn validate_curve_data(times: &[f64], values: &[f64]) -> Result<()> {
    // println!("validate_curve_data: values.len()={:?}", values.len());
    // println!("validate_curve_data: times.len()={:?}", times.len());

    // Check minimum size.
    if values.len() < 2 || times.len() < 2 {
        bail!(KeypointsError::InsufficientPoints);
    }

    // Check equal lengths.
    if values.len() != times.len() {
        bail!(KeypointsError::InsufficientPoints);
    }

    // Check strictly increasing time values.
    for i in 1..times.len() {
        // println!("times[{}]={}", i, times[i]);
        if times[i - 1] >= times[i] {
            bail!(KeypointsError::NonSequentialTime);
        }
    }

    Ok(())
}

/// Process pyramid levels with careful handling of boundaries.
fn process_pyramid_levels(
    pyramids: &[PyramidLevel],
    target_keypoints: usize,
) -> Result<Vec<RankedKeypoint>> {
    // println!("process_pyramid_levels: pyramids={:?}", pyramids);
    // println!(
    //     "process_pyramid_levels: target_keypoints={:?}",
    //     target_keypoints
    // );

    let mut all_keypoints = Vec::new();

    // Always include endpoints from finest level.
    if let Some(base_level) = pyramids.first() {
        if !base_level.times.is_empty() {
            // Add first point.
            all_keypoints.push(RankedKeypoint {
                time: base_level.times[0],
                value: base_level.values[0],
                importance: f64::INFINITY, // Ensure endpoints are kept.
                level_detected: 0,
                keypoint_type: KeypointType::Endpoint,
            });

            // Add last point.
            let last = base_level.times.len() - 1;
            all_keypoints.push(RankedKeypoint {
                time: base_level.times[last],
                value: base_level.values[last],
                importance: f64::INFINITY,
                level_detected: 0,
                keypoint_type: KeypointType::Endpoint,
            });
        }
    }

    // Process levels from coarse to fine.
    let mut max_level = 0;
    for pyramid in pyramids.iter().rev() {
        let pyramid_keypoints =
            detect_level_keypoints(pyramid, &all_keypoints, pyramid.level);

        for keypoint in pyramid_keypoints {
            all_keypoints.push(keypoint);
        }

        max_level = max_level.max(pyramid.level);
    }

    // Select well-distributed keypoints.
    let mut selected =
        pick_keypoints(all_keypoints, max_level, target_keypoints);

    // Ensure endpoints are included and ordered by time.
    selected.sort_by(|a, b| a.time.partial_cmp(&b.time).unwrap());

    Ok(selected)
}

fn filter_keypoints_by_type_and_level(
    only_keypoint_type: KeypointType,
    only_level_detected: usize,
    min_spacing: f64,
    target_keypoints: usize,
    keypoints: &[RankedKeypoint],
    out_keypoints: &mut Vec<RankedKeypoint>,
) {
    // Add remaining keypoints considering both importance and spacing.
    for keypoint in keypoints.iter() {
        // Skip endpoints as they're already included.
        if keypoint.keypoint_type != only_keypoint_type {
            continue;
        }

        if keypoint.level_detected != only_level_detected {
            continue;
        }

        // Check spacing against all selected keypoints.
        //
        // TODO: Make the code universally check this type of thing.
        for out_keypoint in &mut *out_keypoints {
            let spacing = (keypoint.time - out_keypoint.time).abs();
            if spacing < min_spacing {
                continue; // Too close to an existing keypoint
            }
        }

        // Check if we've reached our target.
        if out_keypoints.len() >= target_keypoints {
            break;
        }

        // If the keypoint is well-spaced and important enough, add it.
        if keypoint.importance > 0.0 {
            out_keypoints.push(keypoint.clone());
        }
    }
}

/// Select a well-distributed subset of keypoints based on importance
/// and spacing.
fn pick_keypoints(
    mut all_keypoints: Vec<RankedKeypoint>,
    max_level: usize,
    target_keypoints: usize,
) -> Vec<RankedKeypoint> {
    // println!("pick_keypoints: max_level={:?}", max_level);
    // println!("pick_keypoints: target_keypoints={:?}", target_keypoints);

    // println!(
    //     "pick_keypoints: all_keypoints.len()={:?}",
    //     all_keypoints.len()
    // );
    // for (i, keypoint) in all_keypoints.iter().enumerate() {
    //     println!("pick_keypoints: all_keypoints[{}]={:?}", i, keypoint);
    // }

    if target_keypoints == 0 {
        return Vec::new();
    }

    // Convert heap to sorted vector
    if all_keypoints.is_empty() {
        return Vec::new();
    }

    // Sort with stable handling of NaN (highest importance first)
    all_keypoints.sort_by(|a, b| match b.partial_cmp(&a) {
        Some(ordering) => ordering,
        None => Ordering::Equal, // Handle NaN case
    });

    // for (i, keypoint) in all_keypoints.iter().enumerate() {
    //     println!(
    //         "pick_keypoints: sorted keypoint[{}]={:?}",
    //         i, keypoint
    //     );
    // }

    let mut selected = Vec::with_capacity(target_keypoints);

    // Always include endpoints (they should be the most important due
    // to f64::INFINITY).
    for keypoint in all_keypoints
        .iter()
        .filter(|k| k.keypoint_type == KeypointType::Endpoint)
    {
        selected.push(keypoint.clone());
    }
    assert_eq!(selected.len(), 2);

    // If we only have endpoints, we're done.
    if selected.len() >= target_keypoints {
        // Sort by time before returning.
        selected.sort_by(|a, b| a.time.partial_cmp(&b.time).unwrap());
        return selected;
    }

    // Calculate the time range for spacing calculations.
    let min_time = all_keypoints
        .iter()
        .map(|k| k.time)
        .fold(f64::INFINITY, f64::min);
    let max_time = all_keypoints
        .iter()
        .map(|k| k.time)
        .fold(f64::NEG_INFINITY, f64::max);
    let time_range = max_time - min_time;

    // Minimum spacing between keypoints (adaptive based on target
    // count).
    let min_spacing = time_range / (target_keypoints as f64 * 2.0);

    for level_num in (0..=max_level).rev() {
        filter_keypoints_by_type_and_level(
            KeypointType::ExtremeValue,
            level_num,
            min_spacing,
            target_keypoints,
            &all_keypoints,
            &mut selected,
        );

        filter_keypoints_by_type_and_level(
            KeypointType::VelocityPeak,
            level_num,
            min_spacing,
            target_keypoints,
            &all_keypoints,
            &mut selected,
        );

        filter_keypoints_by_type_and_level(
            KeypointType::Inflection,
            level_num,
            min_spacing,
            target_keypoints,
            &all_keypoints,
            &mut selected,
        );
    }

    // If we still need more points, relax the spacing constraint.
    if selected.len() < target_keypoints {
        let relaxed_spacing = min_spacing * 0.5;

        'relaxed: for keypoint in all_keypoints.iter() {
            if keypoint.keypoint_type == KeypointType::Endpoint {
                continue;
            }

            for selected_keypoint in &selected {
                let spacing = (keypoint.time - selected_keypoint.time).abs();
                if spacing < relaxed_spacing {
                    continue 'relaxed;
                }
            }

            if !selected.iter().any(|k| k.time == keypoint.time) {
                selected.push(keypoint.clone());
            }

            if selected.len() >= target_keypoints {
                break;
            }
        }
    }

    // Ensure keypoints are sorted by time
    selected.sort_by(|a, b| a.time.partial_cmp(&b.time).unwrap());
    selected
}

/// Main analysis function with robust error handling.
pub fn analyze_curve(
    times: &[f64],
    values: &[f64],
    target_keypoints: usize,
) -> Result<Vec<RankedKeypoint>> {
    // println!("analyze_curve: times.len()={:?}", times.len());
    // println!("analyze_curve: values.len()={:?}", values.len());
    // println!("analyze_curve: target_keypoints={:?}", target_keypoints);

    // Add validation for target_keypoints
    if target_keypoints == 0 {
        bail!(KeypointsError::TargetKeypointsTooLow);
    }

    validate_curve_data(times, values)?;

    let num_levels = compute_pyramid_depth(values.len());
    let pyramid_levels = build_pyramid_levels(times, values, num_levels)?;
    let keypoints = process_pyramid_levels(&pyramid_levels, target_keypoints)?;

    Ok(keypoints)
}
