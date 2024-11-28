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
use thiserror::Error;

use crate::constant::Real; // f64

#[derive(Error, Debug)]
enum InfillError {
    #[error("Times and Values slice length does not match.")]
    TimeValueSliceLengthNotMatch,

    #[error("Insufficient points in curve (minimum 2 required).")]
    DataSliceIsEmpty,

    #[error("Non-finite values in data slices.")]
    DataSliceNonFiniteValues,

    #[error("Time values must be strictly increasing.")]
    NonSequentialTime,

    #[error("Data slice must be larger than 1.")]
    DataSliceLengthTooSmall,
}

/// Represents a gap in the curve data that needs to be filled
#[derive(Debug)]
struct Gap {
    start_time: Real,
    end_time: Real,
    start_value: Real,
    end_value: Real,
}

/// Finds gaps in the data that need to be filled.
fn find_gaps(times: &[Real], values: &[Real]) -> Vec<(Gap, usize)> {
    times
        .windows(2)
        .enumerate()
        .filter_map(|(i, window)| {
            let gap_size = window[1] - window[0];
            if gap_size > 1.0 && gap_size.is_finite() {
                Some((
                    Gap {
                        start_time: window[0],
                        end_time: window[1],
                        start_value: values[i],
                        end_value: values[i + 1],
                    },
                    i,
                ))
            } else {
                None
            }
        })
        .collect()
}

/// Calculates coefficients for cubic interpolation.
fn calculate_cubic_coefficients(
    start_time: Real,
    end_time: Real,
    start_value: Real,
    end_value: Real,
    start_slope: Real,
    end_slope: Real,
) -> Option<(Real, Real, Real, Real)> {
    let dt = end_time - start_time;
    if dt.abs() < Real::EPSILON {
        return None;
    }

    let a =
        2.0 * start_value - 2.0 * end_value + dt * start_slope + dt * end_slope;
    let b = -3.0 * start_value + 3.0 * end_value
        - 2.0 * dt * start_slope
        - dt * end_slope;
    let c = dt * start_slope;
    let d = start_value;

    if ![a, b, c, d].iter().all(|x| x.is_finite()) {
        return None;
    }

    Some((a, b, c, d))
}

/// Evaluates cubic polynomial at given t
#[inline]
fn evaluate_cubic(t: Real, a: Real, b: Real, c: Real, d: Real) -> Real {
    ((a * t + b) * t + c) * t + d
}

fn calculate_slope(
    time1: Real,
    value1: Real,
    time2: Real,
    value2: Real,
) -> Real {
    (value2 - value1) / (time2 - time1)
}

fn infill_curve_cubic(
    times: &[Real],
    values: &[Real],
) -> Result<(Vec<Real>, Vec<Real>)> {
    let gaps_with_indices = find_gaps(times, values);
    if gaps_with_indices.is_empty() {
        return Ok((times.to_vec(), values.to_vec()));
    }

    let mut all_points: Vec<(Real, Real)> = times
        .iter()
        .zip(values.iter())
        .map(|(&t, &v)| (t, v))
        .collect();

    // Process gaps sequentially to use previously interpolated
    // points.
    for (gap, i) in gaps_with_indices {
        // For start slope, look at actual points in all_points.
        let start_points: Vec<(Real, Real)> = all_points
            .iter()
            .filter(|xy| xy.0 <= gap.start_time)
            .map(|(t, v)| (*t, *v))
            .rev()
            .take(2)
            .collect();

        let start_slope = if start_points.len() >= 2 {
            calculate_slope(
                start_points[0].0,
                start_points[0].1,
                start_points[1].0,
                start_points[1].1,
            )
        } else {
            calculate_slope(times[i], values[i], times[i + 1], values[i + 1])
        };

        // For end slope, use next actual point and any interpolated
        // points before it.
        let end_points: Vec<(Real, Real)> = all_points
            .iter()
            .filter(|xy| xy.0 >= gap.end_time)
            .map(|(t, v)| (*t, *v))
            .take(2)
            .collect();

        let end_slope = if end_points.len() >= 2 {
            calculate_slope(
                end_points[0].0,
                end_points[0].1,
                end_points[1].0,
                end_points[1].1,
            )
        } else {
            calculate_slope(times[i], values[i], times[i + 1], values[i + 1])
        };

        if let Some((a, b, c, d)) = calculate_cubic_coefficients(
            gap.start_time,
            gap.end_time,
            gap.start_value,
            gap.end_value,
            start_slope,
            end_slope,
        ) {
            let mut t = gap.start_time + 1.0;
            let insert_pos =
                all_points.partition_point(|&(time, _)| time <= gap.start_time);
            let mut interpolated = Vec::new();

            while t < gap.end_time {
                let normalized_t =
                    (t - gap.start_time) / (gap.end_time - gap.start_time);
                let value = evaluate_cubic(normalized_t, a, b, c, d);
                if value.is_finite() {
                    interpolated.push((t, value));
                }
                t += 1.0;
            }

            all_points.splice(insert_pos..insert_pos, interpolated);
        }
    }

    all_points.sort_by(|a, b| a.0.partial_cmp(&b.0).unwrap_or(Ordering::Equal));
    let (times_filled, values_filled): (Vec<Real>, Vec<Real>) =
        all_points.into_iter().unzip();

    Ok((times_filled, values_filled))
}

/// Fills gaps in animation curve data using smooth interpolation.
pub fn infill_curve(
    times: &[Real],
    values: &[Real],
) -> Result<(Vec<Real>, Vec<Real>)> {
    // Input validation
    if times.len() != values.len() {
        bail!(InfillError::TimeValueSliceLengthNotMatch);
    }
    if times.is_empty() {
        bail!(InfillError::DataSliceIsEmpty);
    }
    if times.len() == 1 {
        bail!(InfillError::DataSliceLengthTooSmall);
    }
    if !times.windows(2).all(|w| w[0] < w[1]) {
        bail!(InfillError::NonSequentialTime);
    }
    if !times.iter().chain(values.iter()).all(|x| x.is_finite()) {
        bail!(InfillError::DataSliceNonFiniteValues);
    }

    infill_curve_cubic(times, values)
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    const EPSILON: Real = 1e-10;

    #[test]
    fn test_basic_interpolation() -> Result<()> {
        let times = vec![0.0, 1.0, 5.0, 6.0];
        let values = vec![0.0, 1.0, 5.0, 6.0];

        let result = infill_curve(&times, &values).unwrap();
        let (filled_times, filled_values) = result;

        // Should have more points than original due to gap between 1.0 and 5.0.
        assert!(filled_times.len() > times.len());
        assert_eq!(filled_times.len(), filled_values.len());

        // Original points should be preserved.
        for (t, v) in times.iter().zip(values.iter()) {
            let idx = filled_times
                .iter()
                .position(|x| (x - t).abs() < EPSILON)
                .unwrap();
            assert_relative_eq!(filled_values[idx], *v, epsilon = EPSILON);
        }

        // Interpolated values should be monotonic in gap.
        let gap_points: Vec<(Real, Real)> = filled_times
            .iter()
            .zip(filled_values.iter())
            .filter(|(&t, _)| t > 1.0 && t < 5.0)
            .map(|(&t, &v)| (t, v))
            .collect();

        assert!(!gap_points.is_empty());

        // Values should increase monotonically.
        for i in 1..gap_points.len() {
            assert!(gap_points[i].1 >= gap_points[i - 1].1);
        }

        Ok(())
    }

    #[test]
    fn test_invalid_inputs() -> Result<()> {
        // Mismatched lengths.
        assert!(infill_curve(&[1.0, 2.0], &[1.0]).is_err());

        // Empty input.
        assert!(infill_curve(&[], &[]).is_err());

        // Non-monotonic times.
        assert!(infill_curve(&[0.0, 2.0, 1.0], &[0.0, 2.0, 1.0]).is_err());

        // Infinite values.
        assert!(infill_curve(&[0.0, 1.0, Real::INFINITY], &[0.0, 1.0, 2.0])
            .is_err());
        assert!(infill_curve(&[0.0, 1.0, 2.0], &[0.0, Real::NAN, 2.0]).is_err());

        Ok(())
    }

    #[test]
    fn test_no_gaps() -> Result<()> {
        let times = vec![0.0, 1.0, 2.0, 3.0];
        let values = vec![0.0, 1.0, 2.0, 3.0];

        let result = infill_curve(&times, &values).unwrap();
        let (filled_times, filled_values) = result;

        // Should return original data unchanged.
        assert_eq!(filled_times.len(), times.len());
        for i in 0..times.len() {
            assert_relative_eq!(filled_times[i], times[i], epsilon = EPSILON);
            assert_relative_eq!(filled_values[i], values[i], epsilon = EPSILON);
        }

        Ok(())
    }

    #[test]
    fn test_edge_gaps() -> Result<()> {
        let times = vec![0.0, 1.0, 6.0, 7.0, 8.0, 15.0];
        let values = vec![0.0, 1.0, 6.0, 7.0, 8.0, 15.0];

        let result = infill_curve(&times, &values).unwrap();
        let (filled_times, filled_values) = result;

        // Should handle gaps at both edges of data.
        assert!(filled_times.len() > times.len());

        // Check monotonicity in first gap (1.0 to 6.0).
        let first_gap: Vec<(Real, Real)> = filled_times
            .iter()
            .zip(filled_values.iter())
            .filter(|(&t, _)| t > 1.0 && t < 6.0)
            .map(|(&t, &v)| (t, v))
            .collect();

        for i in 1..first_gap.len() {
            assert!(first_gap[i].1 >= first_gap[i - 1].1);
        }

        // Check monotonicity in second gap (8.0 to 15.0).
        let second_gap: Vec<(Real, Real)> = filled_times
            .iter()
            .zip(filled_values.iter())
            .filter(|(&t, _)| t > 8.0 && t < 15.0)
            .map(|(&t, &v)| (t, v))
            .collect();

        for i in 1..second_gap.len() {
            assert!(second_gap[i].1 >= second_gap[i - 1].1);
        }

        Ok(())
    }

    #[test]
    fn test_single_point() -> Result<()> {
        let times = vec![1.0];
        let values = vec![2.0];
        assert!(infill_curve(&times, &values).is_err());

        Ok(())
    }
}
