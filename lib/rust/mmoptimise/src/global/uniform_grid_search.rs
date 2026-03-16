//
// Copyright (C) 2025 David Cattermole.
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

//! Uniform Grid Search global optimization algorithm.
//!
//! A simple brute-force optimization method that exhaustively
//! evaluates uniformly-spaced samples across parameter bounds.
//! Unlike gradient-based methods or Differential Evolution:
//!
//! - Deterministic: always evaluates the same grid points
//! - Simple: no population, no mutation/crossover
//! - Exhaustive: guarantees finding grid-aligned optima
//! - Parallelizable: all evaluations are independent
//!
//! # When to Use Uniform Grid Search
//!
//! **Use Uniform Grid Search when:**
//! - Parameter space is low-dimensional (1-3 dimensions)
//! - Evaluation budget is known and fixed
//! - Need deterministic, reproducible results
//! - Want to ensure coverage of parameter space
//! - Objective function is cheap enough for exhaustive search
//!
//! **Avoid when:**
//! - High-dimensional (>3 dimensions) - combinatorial explosion!
//! - Need adaptive search based on landscape
//! - Evaluation is very expensive
//!
//! # Quick Start
//!
//! ```ignore
//! use mmoptimise::global::{UniformGridSearch, UniformGridSearchConfig, Evaluator};
//!
//! // Define cost function
//! struct MyEvaluator;
//! impl Evaluator for MyEvaluator {
//!     fn evaluate(&self, params: &[f64]) -> f64 {
//!         params[0].powi(2)  // Simple quadratic
//!     }
//! }
//!
//! // Configure grid search
//! let config = UniformGridSearchConfig {
//!     num_dimensions: 1,
//!     num_samples_per_dimension: vec![11],
//!     bounds: vec![(-5.0, 5.0)],
//! };
//!
//! // Run optimization
//! let solver = UniformGridSearch::new(config)?;
//! let mut best_params = vec![0.0];
//! let best_cost = solver.run(&MyEvaluator, &mut best_params, &mmlogger::NoOpLogger)?;
//! ```
//!
//! # 1D Example: Focal Length Optimization
//!
//! ```ignore
//! // Search focal length from 10mm to 20mm with 11 samples
//! let config = UniformGridSearchConfig {
//!     num_dimensions: 1,
//!     num_samples_per_dimension: vec![11],
//!     bounds: vec![(10.0, 20.0)],
//! };
//!
//! let solver = UniformGridSearch::new(config)?;
//! let mut best_focal_length = vec![0.0];
//! let best_cost = solver.run(&evaluator, &mut best_focal_length, &mmlogger::NoOpLogger)?;
//!
//! // Samples: [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
//! // Total evaluations: 11
//! ```
//!
//! # 2D Example: Multi-parameter Search
//!
//! ```ignore
//! // Search focal length × aperture with asymmetric sampling
//! let config = UniformGridSearchConfig {
//!     num_dimensions: 2,
//!     num_samples_per_dimension: vec![11, 5],  // 55 total evaluations
//!     bounds: vec![(10.0, 20.0), (0.0, 1.0)],
//! };
//!
//! let solver = UniformGridSearch::new(config)?;
//! let mut best_params = vec![0.0, 0.0];
//! let best_cost = solver.run(&evaluator, &mut best_params, &mmlogger::NoOpLogger)?;
//! ```
//!
//! # Combinatorial Explosion Warning
//!
//! Grid search suffers from the curse of dimensionality:
//! - 1D with 10 samples = 10 evaluations
//! - 2D with 10 samples each = 100 evaluations
//! - 3D with 10 samples each = 1,000 evaluations
//! - 4D with 10 samples each = 10,000 evaluations
//!
//! For high-dimensional problems, use Differential Evolution instead.

use anyhow::Result;
use mmlogger::mm_log_progress;
use rayon::prelude::*;
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Mutex;
use thiserror::Error;

use crate::global::Evaluator;

/// How many seconds must pass between periodic progress log lines during
/// a grid search. Change this value in source to adjust the interval.
const PROGRESS_LOG_INTERVAL_SECS: f64 = 10.0;

// ----------------------------------------------------------
// Config / Errors
// ----------------------------------------------------------

/// Configuration for Uniform Grid Search optimization.
///
/// # Examples
///
/// ```ignore
/// // 1D search with 11 samples
/// let config = UniformGridSearchConfig {
///     num_dimensions: 1,
///     num_samples_per_dimension: vec![11],
///     bounds: vec![(10.0, 20.0)],
/// };
///
/// // 2D search with asymmetric sampling
/// let config = UniformGridSearchConfig {
///     num_dimensions: 2,
///     num_samples_per_dimension: vec![11, 5],  // 55 evaluations
///     bounds: vec![(10.0, 20.0), (0.0, 1.0)],
/// };
/// ```
#[derive(Debug, Clone)]
pub struct UniformGridSearchConfig {
    /// Number of dimensions (parameters being optimized).
    pub num_dimensions: usize,

    /// Number of samples for each dimension.
    ///
    /// Length must equal `num_dimensions`. Each value must be >= 1.
    /// Total evaluations = product of all sample counts.
    ///
    /// Example: `[11, 5, 3]` → 165 total evaluations
    pub num_samples_per_dimension: Vec<usize>,

    /// Parameter bounds as (min, max) pairs for each dimension.
    ///
    /// Length must equal `num_dimensions`. Each pair must satisfy min < max.
    pub bounds: Vec<(f64, f64)>,
}

#[derive(Error, Debug)]
pub enum UniformGridSearchError {
    #[error(
        "bounds dimension mismatch: bounds.len()={0} != num_dimensions={1}"
    )]
    BoundsDimMismatch(usize, usize),

    #[error("num_samples_per_dimension dimension mismatch: len={0} != num_dimensions={1}")]
    NumSamplesDimMismatch(usize, usize),

    #[error("invalid bounds for dimension {0}: min >= max")]
    InvalidBounds(usize),

    #[error("invalid num_samples for dimension {0}: must be >= 1, got {1}")]
    InvalidNumSamples(usize, usize),
}

// ----------------------------------------------------------
// Helper Functions
// ----------------------------------------------------------

/// Generate Cartesian product of samples from each dimension.
///
/// Uses index arithmetic to avoid recursion and minimize allocations.
/// Each grid point has a unique linear index from 0 to (total_points - 1).
///
/// # Algorithm
///
/// Convert linear index to multi-dimensional coordinates using modulo:
/// - Similar to converting a number to different base representation
/// - Dimension 0 varies fastest (innermost loop)
/// - Dimension N-1 varies slowest (outermost loop)
///
/// # Example
///
/// ```ignore
/// let samples = vec![
///     vec![10.0, 15.0, 20.0],  // dimension 0: 3 samples
///     vec![0.0, 1.0],           // dimension 1: 2 samples
/// ];
/// let grid = generate_grid_points(&samples);
///
/// // Result: 6 points
/// // [10, 0], [15, 0], [20, 0], [10, 1], [15, 1], [20, 1]
/// ```
fn generate_grid_points(samples_per_dim: &[Vec<f64>]) -> Vec<Vec<f64>> {
    let num_dims = samples_per_dim.len();
    if num_dims == 0 {
        return vec![];
    }

    // Calculate total number of grid points
    let total_points: usize = samples_per_dim.iter().map(|v| v.len()).product();

    if total_points == 0 {
        return vec![];
    }

    let mut grid_points = Vec::with_capacity(total_points);

    // Generate all combinations using index arithmetic
    // Dimension 0 varies fastest (innermost loop)
    for i in 0..total_points {
        let mut point = Vec::with_capacity(num_dims);
        let mut idx = i;

        // Convert linear index to multi-dimensional coordinates
        for dim in 0..num_dims {
            let dim_size = samples_per_dim[dim].len();
            point.push(samples_per_dim[dim][idx % dim_size]);
            idx /= dim_size;
        }

        grid_points.push(point);
    }

    grid_points
}

// ----------------------------------------------------------
// Uniform Grid Search
// ----------------------------------------------------------

/// Uniform Grid Search optimizer.
///
/// Exhaustively evaluates all points on a uniform grid across
/// parameter bounds, returning the best solution found.
pub struct UniformGridSearch {
    cfg: UniformGridSearchConfig,
}

impl UniformGridSearch {
    /// Create a new Uniform Grid Search solver.
    ///
    /// # Validation
    ///
    /// Returns error if:
    /// - `bounds.len()` != `num_dimensions`
    /// - `num_samples_per_dimension.len()` != `num_dimensions`
    /// - Any dimension has `num_samples < 1`
    /// - Any bounds pair has `min >= max`
    ///
    /// # Examples
    ///
    /// ```ignore
    /// let config = UniformGridSearchConfig {
    ///     num_dimensions: 1,
    ///     num_samples_per_dimension: vec![11],
    ///     bounds: vec![(10.0, 20.0)],
    /// };
    ///
    /// let solver = UniformGridSearch::new(config)?;
    /// ```
    pub fn new(
        cfg: UniformGridSearchConfig,
    ) -> Result<Self, UniformGridSearchError> {
        // Validate bounds length
        if cfg.bounds.len() != cfg.num_dimensions {
            return Err(UniformGridSearchError::BoundsDimMismatch(
                cfg.bounds.len(),
                cfg.num_dimensions,
            ));
        }

        // Validate num_samples_per_dimension length
        if cfg.num_samples_per_dimension.len() != cfg.num_dimensions {
            return Err(UniformGridSearchError::NumSamplesDimMismatch(
                cfg.num_samples_per_dimension.len(),
                cfg.num_dimensions,
            ));
        }

        // Validate bounds (min < max)
        for (i, &(min, max)) in cfg.bounds.iter().enumerate() {
            if !(min < max) {
                return Err(UniformGridSearchError::InvalidBounds(i));
            }
        }

        // Validate num_samples (must be >= 1)
        for (i, &num_samples) in
            cfg.num_samples_per_dimension.iter().enumerate()
        {
            if num_samples < 1 {
                return Err(UniformGridSearchError::InvalidNumSamples(
                    i,
                    num_samples,
                ));
            }
        }

        Ok(Self { cfg })
    }

    /// Run the Uniform Grid Search optimization.
    ///
    /// Generates a uniform grid of sample points across parameter bounds,
    /// evaluates all points in parallel, and returns the best solution.
    ///
    /// # Algorithm
    ///
    /// 1. For each dimension, generate uniformly-spaced samples
    /// 2. Generate Cartesian product of all dimension samples
    /// 3. Evaluate all grid points in parallel using rayon
    /// 4. Return grid point with minimum cost
    ///
    /// # Arguments
    ///
    /// * `evaluator` - Cost function evaluator (must be thread-safe)
    /// * `best_out` - Output buffer for best parameters (length must equal `num_dimensions`)
    ///
    /// # Returns
    ///
    /// The cost of the best solution found.
    ///
    /// # Panics
    ///
    /// Panics if `best_out.len()` != `num_dimensions`.
    pub fn run<E: Evaluator + Sync, L: mmlogger::Logger + Sync>(
        &self,
        evaluator: &E,
        best_out: &mut [f64],
        logger: &L,
    ) -> Result<f64, UniformGridSearchError> {
        assert_eq!(
            best_out.len(),
            self.cfg.num_dimensions,
            "Output slice length mismatch (expected {})",
            self.cfg.num_dimensions
        );

        let start_time = std::time::Instant::now();

        // Step 1: Generate uniformly-spaced samples for each dimension
        let mut samples_per_dim: Vec<Vec<f64>> = Vec::new();
        for (i, &(min, max)) in self.cfg.bounds.iter().enumerate() {
            let n = self.cfg.num_samples_per_dimension[i];
            let mut dim_samples = Vec::with_capacity(n);

            if n == 1 {
                // Single sample: use midpoint
                dim_samples.push((min + max) / 2.0);
            } else {
                // Multiple samples: uniform spacing including endpoints
                for k in 0..n {
                    let t = k as f64 / (n - 1) as f64;
                    dim_samples.push(min + t * (max - min));
                }
            }
            samples_per_dim.push(dim_samples);
        }

        // Step 2: Generate Cartesian product of all dimension samples
        let grid_points = generate_grid_points(&samples_per_dim);
        let total_points = grid_points.len();

        mm_log_progress!(
            logger,
            "[UGS] Evaluating {} grid points across {} dimension(s)...",
            total_points,
            self.cfg.num_dimensions
        );

        // Progress tracking shared across rayon threads.
        let completed = AtomicUsize::new(0);
        let last_log_time = Mutex::new(std::time::Instant::now());
        // Tracks (best_cost, best_params) seen so far across all threads.
        let best_so_far: Mutex<(f64, Vec<f64>)> =
            Mutex::new((f64::MAX, vec![f64::NAN; self.cfg.num_dimensions]));

        // Step 3: Evaluate all grid points in parallel.
        //
        // After each evaluation, update the shared best and emit a
        // progress line at most once per PROGRESS_LOG_INTERVAL_SECS.
        let results: Vec<(usize, f64)> = grid_points
            .par_iter()
            .enumerate()
            .map(|(idx, params)| {
                let cost = evaluator.evaluate(params);

                // Update shared best if this result is an improvement.
                {
                    let mut best = best_so_far.lock().unwrap();
                    if cost < best.0 {
                        best.0 = cost;
                        best.1.copy_from_slice(params);
                    }
                }

                let done =
                    completed.fetch_add(1, Ordering::Relaxed) + 1;

                // Decide whether to emit a progress line.
                let now = std::time::Instant::now();
                let should_log = {
                    let mut last_time = last_log_time.lock().unwrap();
                    if now
                        .duration_since(*last_time)
                        .as_secs_f64()
                        >= PROGRESS_LOG_INTERVAL_SECS
                    {
                        *last_time = now;
                        true
                    } else {
                        false
                    }
                };

                if should_log {
                    let elapsed_secs =
                        start_time.elapsed().as_secs_f64();
                    let remaining = total_points.saturating_sub(done);
                    let eta_secs = if done > 0 && remaining > 0 {
                        elapsed_secs * remaining as f64 / done as f64
                    } else {
                        0.0
                    };
                    let (current_best_cost, current_best_params) = {
                        let g = best_so_far.lock().unwrap();
                        (g.0, g.1.clone())
                    };

                    let num_dimensions = current_best_params.len();
                    let params_str = if num_dimensions <= 10 {
                        format!("{:?}", current_best_params)
                    } else {
                        format!(
                            "[{:.6}, {:.6}, ... {} more]",
                            current_best_params[0],
                            current_best_params[1],
                            num_dimensions - 2
                        )
                    };

                    mm_log_progress!(
                        logger,
                        "[UGS] {}/{} | best cost: {:.9}, params: {} | elapsed: {:.1}s (ETA: ~{:.0}s)",
                        done,
                        total_points,
                        current_best_cost,
                        params_str,
                        elapsed_secs,
                        eta_secs,
                    );
                }

                (idx, cost)
            })
            .collect();

        // Step 4: Find minimum cost
        let (best_idx, best_cost) = results
            .iter()
            .min_by(|(_, c1), (_, c2)| {
                c1.partial_cmp(c2).unwrap_or(std::cmp::Ordering::Equal)
            })
            .expect("Grid search found no valid solutions");

        let elapsed = start_time.elapsed();

        // Copy best solution to output buffer
        best_out.copy_from_slice(&grid_points[*best_idx]);

        mm_log_progress!(
            logger,
            "[UGS] Best cost: {:.6}, params: {:?}, time: {:.2}s",
            best_cost,
            best_out,
            elapsed.as_secs_f64()
        );

        Ok(*best_cost)
    }
}

// ----------------------------------------------------------
// Tests
// ----------------------------------------------------------
#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    /// Simple quadratic evaluator for testing
    struct Quadratic {
        target: Vec<f64>,
    }

    impl Evaluator for Quadratic {
        fn evaluate(&self, x: &[f64]) -> f64 {
            x.iter()
                .zip(self.target.iter())
                .map(|(a, b)| (a - b).powi(2))
                .sum()
        }
    }

    #[test]
    fn test_grid_point_generation_1d() {
        let samples = vec![vec![10.0, 15.0, 20.0]];
        let grid = generate_grid_points(&samples);

        assert_eq!(grid.len(), 3);
        assert_eq!(grid[0], vec![10.0]);
        assert_eq!(grid[1], vec![15.0]);
        assert_eq!(grid[2], vec![20.0]);
    }

    #[test]
    fn test_grid_point_generation_2d() {
        let samples = vec![vec![10.0, 20.0], vec![0.0, 1.0]];
        let grid = generate_grid_points(&samples);

        assert_eq!(grid.len(), 4);
        assert_eq!(grid[0], vec![10.0, 0.0]);
        assert_eq!(grid[1], vec![20.0, 0.0]);
        assert_eq!(grid[2], vec![10.0, 1.0]);
        assert_eq!(grid[3], vec![20.0, 1.0]);
    }

    #[test]
    fn test_grid_point_generation_asymmetric() {
        let samples = vec![vec![1.0, 2.0, 3.0], vec![10.0, 20.0]];
        let grid = generate_grid_points(&samples);

        assert_eq!(grid.len(), 6);
        assert_eq!(grid[0], vec![1.0, 10.0]);
        assert_eq!(grid[1], vec![2.0, 10.0]);
        assert_eq!(grid[2], vec![3.0, 10.0]);
        assert_eq!(grid[3], vec![1.0, 20.0]);
        assert_eq!(grid[4], vec![2.0, 20.0]);
        assert_eq!(grid[5], vec![3.0, 20.0]);
    }

    #[test]
    fn test_grid_search_1d_quadratic() {
        let config = UniformGridSearchConfig {
            num_dimensions: 1,
            num_samples_per_dimension: vec![21],
            bounds: vec![(-10.0, 10.0)],
        };

        let solver = UniformGridSearch::new(config).unwrap();
        let eval = Quadratic { target: vec![0.0] };
        let mut best = vec![0.0];

        let cost = solver.run(&eval, &mut best, &mmlogger::NoOpLogger).unwrap();

        assert_eq!(cost, 0.0);
        assert_eq!(best[0], 0.0);
    }

    #[test]
    fn test_grid_search_1d_offset_target() {
        let config = UniformGridSearchConfig {
            num_dimensions: 1,
            num_samples_per_dimension: vec![21],
            bounds: vec![(-5.0, 5.0)],
        };

        let solver = UniformGridSearch::new(config).unwrap();
        let eval = Quadratic { target: vec![2.0] };
        let mut best = vec![0.0];

        let cost = solver.run(&eval, &mut best, &mmlogger::NoOpLogger).unwrap();

        assert_eq!(cost, 0.0);
        assert_eq!(best[0], 2.0);
    }

    #[test]
    fn test_grid_search_2d_quadratic() {
        let config = UniformGridSearchConfig {
            num_dimensions: 2,
            num_samples_per_dimension: vec![21, 21],
            bounds: vec![(-5.0, 5.0), (-5.0, 5.0)],
        };

        let solver = UniformGridSearch::new(config).unwrap();
        let eval = Quadratic {
            target: vec![1.0, -1.0],
        };
        let mut best = vec![0.0, 0.0];

        let cost = solver.run(&eval, &mut best, &mmlogger::NoOpLogger).unwrap();

        assert_eq!(cost, 0.0);
        assert_eq!(best[0], 1.0);
        assert_eq!(best[1], -1.0);
    }

    #[test]
    fn test_grid_search_single_sample_uses_midpoint() {
        let config = UniformGridSearchConfig {
            num_dimensions: 1,
            num_samples_per_dimension: vec![1],
            bounds: vec![(10.0, 20.0)],
        };

        let solver = UniformGridSearch::new(config).unwrap();
        let eval = Quadratic { target: vec![15.0] };
        let mut best = vec![0.0];

        let cost = solver.run(&eval, &mut best, &mmlogger::NoOpLogger).unwrap();

        assert_eq!(best[0], 15.0); // midpoint of [10, 20]
        assert_eq!(cost, 0.0);
    }

    #[test]
    fn test_uniform_spacing_inclusive_endpoints() {
        let config = UniformGridSearchConfig {
            num_dimensions: 1,
            num_samples_per_dimension: vec![11],
            bounds: vec![(10.0, 20.0)],
        };

        let _solver = UniformGridSearch::new(config).unwrap();

        // Generate samples manually to test spacing
        let min = 10.0;
        let max = 20.0;
        let n = 11;
        let mut expected = Vec::new();
        for k in 0..n {
            let t = k as f64 / (n - 1) as f64;
            expected.push(min + t * (max - min));
        }

        assert_eq!(expected[0], 10.0); // min
        assert_eq!(expected[10], 20.0); // max
        assert_eq!(expected[5], 15.0); // midpoint

        // Verify uniform spacing
        for k in 0..n - 1 {
            let diff = expected[k + 1] - expected[k];
            assert_relative_eq!(diff, 1.0, epsilon = 1e-10);
        }
    }

    #[test]
    fn test_validation_bounds_mismatch() {
        let config = UniformGridSearchConfig {
            num_dimensions: 2,
            num_samples_per_dimension: vec![10, 10],
            bounds: vec![(0.0, 1.0)], // Wrong: only 1 bound for 2 dimensions
        };

        let result = UniformGridSearch::new(config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validation_num_samples_mismatch() {
        let config = UniformGridSearchConfig {
            num_dimensions: 2,
            num_samples_per_dimension: vec![10], // Wrong: only 1 for 2 dimensions
            bounds: vec![(0.0, 1.0), (0.0, 1.0)],
        };

        let result = UniformGridSearch::new(config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validation_invalid_bounds() {
        let config = UniformGridSearchConfig {
            num_dimensions: 1,
            num_samples_per_dimension: vec![10],
            bounds: vec![(5.0, 1.0)], // Wrong: min > max
        };

        let result = UniformGridSearch::new(config);
        assert!(result.is_err());
    }

    #[test]
    fn test_validation_zero_samples() {
        let config = UniformGridSearchConfig {
            num_dimensions: 1,
            num_samples_per_dimension: vec![0], // Wrong: must be >= 1
            bounds: vec![(0.0, 1.0)],
        };

        let result = UniformGridSearch::new(config);
        assert!(result.is_err());
    }
}
