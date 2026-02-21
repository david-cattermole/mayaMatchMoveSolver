//
// Copyright (C) 2025, 2026 David Cattermole.
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

//! Sparse optimization solvers for large-scale problems.
//!
//! This module provides efficient sparse matrix implementations of
//! non-linear least squares solvers using CHOLMOD for sparse linear algebra.

use anyhow::Result;

mod common;
mod sparse_levenberg_marquardt;
mod test_problems;

// Re-export Sparse LM solver types
pub use sparse_levenberg_marquardt::{
    SparseLevenbergMarquardtConfig, SparseLevenbergMarquardtSolver,
    SparseLevenbergMarquardtWorkspace,
};

// Re-export common utility functions
pub use common::{
    assemble_jtj_with_damping, clear_sparse_coo, compute_jacobian_column_norms,
    compute_least_squares_cost, compute_normalized_gradient_norm,
    sparse_j_multiply, sparse_j_multiply_norm_squared, sparse_jt_multiply,
};

/// Trait for optimization problems that provide sparse Jacobians.
///
/// This trait defines the interface for problems that can be solved
/// using sparse matrix optimization algorithms. Problems must provide
/// their Jacobian matrix in sparse COO (coordinate) format.
pub trait SparseOptimisationProblem {
    /// Compute residuals and sparse Jacobian.
    ///
    /// The Jacobian should be provided in COO (coordinate) format,
    /// which will be converted to CSC format internally.
    ///
    /// Returns (row_indices, col_indices, values) for the Jacobian
    /// where J[row_indices[k], col_indices[k]] = values[k]
    fn compute_sparse_jacobian(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> Result<(Vec<usize>, Vec<usize>, Vec<f64>)>;

    /// Number of optimization parameters.
    fn parameter_count(&self) -> usize;

    /// Number of residual equations.
    fn residual_count(&self) -> usize;

    /// Normalize parameters in-place after step acceptance (optional).
    ///
    /// This method is called by solvers after a step is accepted but before
    /// the next iteration begins. It allows problems to apply gauge-fixing
    /// transforms (e.g., similarity normalization for bundle adjustment).
    ///
    /// # Arguments
    ///
    /// * `parameters` - Mutable parameter vector to normalize in-place.
    ///
    /// # Returns
    ///
    /// `true` if normalization was applied, `false` if skipped or not implemented.
    ///
    /// # Default Implementation
    ///
    /// Returns `false` (no normalization).
    fn normalize_parameters(&self, _parameters: &mut [f64]) -> bool {
        false
    }
}
