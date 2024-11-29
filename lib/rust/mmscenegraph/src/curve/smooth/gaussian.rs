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
//! Gaussian smoothing.
//!
//! This has been ported from the Maya Python code;
//! <project root>/python/mmSolver/utils/smooth.py
//!
//! Additionally, this algorithm has been improved to work with both
//! 1d and 2d data, where time values are not uniform.

use anyhow::bail;
use anyhow::Result;

use crate::constant::Real;
use crate::constant::REAL_E;

/// Compute array of Gaussian weights for a given sigma value.
#[inline]
fn compute_gaussian_weights_1d(
    sigma: Real,
    center: usize,
    out_weights: &mut [Real],
    out_weights_sum: &mut Real,
) {
    // Calculate center position for Gaussian
    let center_pos = center as Real;

    // Precompute constant factors
    let sigma_squared_2 = 2.0 * sigma.powi(2);

    // Zero out input weights;
    for weight in &mut *out_weights {
        *weight = 0.0;
    }

    // Compute all weights in a single vectorizable loop
    for i in 0..out_weights.len() {
        let x = i as Real;
        let diff = x - center_pos;
        out_weights[i] = REAL_E.powf(-diff.powi(2) / sigma_squared_2);
    }

    *out_weights_sum = 0.0;
    for weight in out_weights {
        *out_weights_sum += *weight;
    }
}

/// Compute array of Gaussian weights for a given sigma value,
/// adjusting for non-uniform time sampling.
#[inline]
fn compute_gaussian_weights_2d(
    times: &[Real],
    sigma: Real,
    center_index: usize,
    out_weights: &mut [Real],
    out_weights_sum: &mut Real,
) {
    // Get center time value
    let center_time = times[center_index];

    // Precompute constant factors
    let sigma_squared_2 = 2.0 * sigma.powi(2);

    // Zero out input weights
    for weight in &mut *out_weights {
        *weight = 0.0;
    }

    // Compute weights based on time differences rather than indices
    for i in 0..out_weights.len() {
        let time_diff = times[i] - center_time;
        out_weights[i] = REAL_E.powf(-time_diff.powi(2) / sigma_squared_2);
    }

    // Calculate sum of weights
    *out_weights_sum = 0.0;
    for weight in out_weights {
        *out_weights_sum += *weight;
    }
}

/// Gaussian smoothing.
///
/// # Arguments
/// * `values` - Slice of values to smooth
/// * `width` - Smoothing width (>1.0 for smoothing effect)
/// * `out_values` - Pre-allocated buffer for output values, must be same length as input
pub fn gaussian_smooth_1d(
    values: &[Real],
    width: Real,
    out_values: &mut [Real],
) -> Result<()> {
    if values.len() != out_values.len() {
        bail!("Output buffer must be same length as input values");
    }

    if width == 1.0 {
        out_values.copy_from_slice(values);
        return Ok(());
    } else if width < 1.0 {
        bail!("Width must be 1.0 or greater.");
    }

    let sigma = (width - 1.0) * 0.5;
    assert!(sigma > 0.0);

    let len = values.len();
    let mut weights = vec![0.0; len];

    for i in 0..len {
        let mut weights_sum = 0.0;
        compute_gaussian_weights_1d(sigma, i, &mut weights, &mut weights_sum);
        let inv_sum = 1.0 / weights_sum;

        let mut weighted_sum = 0.0;
        for j in 0..len {
            weighted_sum += values[j] * weights[j] * inv_sum;
        }

        out_values[i] = weighted_sum;
    }

    Ok(())
}

/// Gaussian smoothing for animation curves with non-uniform time
/// sampling.
///
/// # Arguments
/// * `times` - Slice of time values (x-axis).
/// * `values` - Slice of corresponding values to smooth (y-axis).
/// * `width` - Smoothing width (>1.0 for smoothing effect).
/// * `out_values` - Pre-allocated buffer for output values, must be
///    same length as input.
pub fn gaussian_smooth_2d(
    times: &[Real],
    values: &[Real],
    width: Real,
    out_values: &mut [Real],
) -> Result<()> {
    // Input validation
    if times.len() != values.len() {
        bail!("Times and values arrays must have the same length");
    }
    if values.len() != out_values.len() {
        bail!("Output buffer must be same length as input values");
    }
    if times.len() < 2 {
        out_values.copy_from_slice(values);
        return Ok(());
    }

    // Check times are monotonically increasing
    for i in 1..times.len() {
        if times[i] <= times[i - 1] {
            bail!("Time values must be strictly monotonically increasing");
        }
    }

    if width == 1.0 {
        out_values.copy_from_slice(values);
        return Ok(());
    } else if width < 1.0 {
        bail!("Width must be 1.0 or greater.");
    }

    let sigma = (width - 1.0) * 0.5;
    assert!(sigma > 0.0);

    let len = values.len();
    let mut weights = vec![0.0; len];

    for i in 0..len {
        let mut weights_sum = 0.0;
        compute_gaussian_weights_2d(
            times,
            sigma,
            i,
            &mut weights,
            &mut weights_sum,
        );
        let inv_sum = 1.0 / weights_sum;

        let mut weighted_sum = 0.0;
        for j in 0..len {
            weighted_sum += values[j] * weights[j] * inv_sum;
        }

        out_values[i] = weighted_sum;
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    #[test]
    fn test_1d_large_array() -> Result<()> {
        let values: Vec<Real> = (0..1000).map(|x| x as Real).collect();
        let mut result = vec![0.0; values.len()];
        gaussian_smooth_1d(&values, 5.0, &mut result)?;

        assert_eq!(result.len(), values.len());
        Ok(())
    }

    #[test]
    fn test_1d_alignment() -> Result<()> {
        let sizes = [1, 8, 16, 32, 64, 128];
        for size in sizes.iter() {
            let values: Vec<Real> = (0..*size).map(|x| x as Real).collect();
            let mut result = vec![0.0; values.len()];
            gaussian_smooth_1d(&values, 3.0, &mut result)?;
            assert_eq!(result.len(), values.len());
        }
        Ok(())
    }

    #[test]
    fn test_1d_edge_cases() -> Result<()> {
        // Empty array
        let empty: Vec<Real> = vec![];
        let mut result = vec![];
        gaussian_smooth_1d(&empty, 2.0, &mut result)?;
        assert_eq!(result, empty);

        // Single value
        let single = vec![1.0];
        let mut result = vec![0.0];
        gaussian_smooth_1d(&single, 2.0, &mut result)?;
        assert_eq!(result, single);

        // No smoothing
        let values = vec![1.0, 2.0, 3.0];
        let mut result = vec![0.0; values.len()];
        gaussian_smooth_1d(&values, 1.0, &mut result)?;
        assert_eq!(result, values);

        Ok(())
    }

    #[test]
    fn test_2d_uniform_sampling() -> Result<()> {
        let times: Vec<Real> = (0..5).map(|x| x as Real).collect();
        let values = vec![1.0, 2.0, 3.0, 2.0, 1.0];
        let mut result = vec![0.0; values.len()];
        gaussian_smooth_2d(&times, &values, 2.0, &mut result)?;

        assert_eq!(result.len(), values.len());
        assert!(result[2] < values[2]); // Peak should be reduced
        Ok(())
    }

    /// Helper function to generate an array of time values matching array indices
    fn generate_uniform_times(len: usize) -> Vec<Real> {
        (0..len).map(|x| x as Real).collect()
    }

    #[test]
    fn test_2d_matches_1d_uniform() -> Result<()> {
        // Test arrays of different sizes with matching functions
        let test_sizes = [5, 100, 1000];
        let test_widths = [1.5, 2.0, 3.0, 5.0, 10.0];

        for &size in &test_sizes {
            let values: Vec<Real> =
                (0..size).map(|x| (x as Real * 0.1).sin()).collect();
            let times = generate_uniform_times(values.len());

            for &width in &test_widths {
                let mut result_1d = vec![0.0; values.len()];
                let mut result_2d = vec![0.0; values.len()];

                gaussian_smooth_1d(&values, width, &mut result_1d)?;
                gaussian_smooth_2d(&times, &values, width, &mut result_2d)?;

                for (r1, r2) in result_1d.iter().zip(result_2d.iter()) {
                    assert_relative_eq!(r1, r2, epsilon = 1e-10);
                }
            }
        }
        Ok(())
    }

    #[test]
    fn test_invalid_output_buffer() {
        let values = vec![1.0, 2.0, 3.0];
        let mut small_buffer = vec![0.0; 2];
        assert!(gaussian_smooth_1d(&values, 2.0, &mut small_buffer).is_err());

        let times = vec![1.0, 2.0, 3.0];
        assert!(gaussian_smooth_2d(&times, &values, 2.0, &mut small_buffer)
            .is_err());
    }

    #[test]
    fn test_2d_matches_1d_extreme_values() -> Result<()> {
        let values = vec![1e6, 1e-6, 1e6, 1e-6, 1e6];
        let times = generate_uniform_times(values.len());

        let mut result_1d = vec![0.0; values.len()];
        let mut result_2d = vec![0.0; values.len()];

        gaussian_smooth_1d(&values, 2.0, &mut result_1d)?;
        gaussian_smooth_2d(&times, &values, 2.0, &mut result_2d)?;

        for (r1, r2) in result_1d.iter().zip(result_2d.iter()) {
            assert_relative_eq!(r1, r2, epsilon = 1e-10);
        }
        Ok(())
    }
}
