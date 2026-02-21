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

//! Common utilities for sparse optimization solvers.
//!
//! This module contains shared functions used across multiple sparse
//! optimization algorithms (Levenberg-Marquardt, Powell Dog-Leg, and
//! Bundle Adjustment). These utilities are designed to be zero-allocation
//! where possible, accepting pre-allocated buffers for output.

use mmcholmod::sparse_matrix::{SparseMatrixCOO, SparseMatrixCSC};
use nalgebra::DVector;

/// Clear a SparseMatrixCOO for reuse.
///
/// This resets the matrix to empty state while keeping the allocated storage.
pub fn clear_sparse_coo(matrix: &mut SparseMatrixCOO) {
    matrix.row_indices.clear();
    matrix.col_indices.clear();
    matrix.values.clear();
}

/// Compute least squares cost: 0.5 * ||residuals||²
///
/// This is the standard cost function for non-linear least squares problems.
///
/// # Arguments
///
/// * `residuals` - The residual vector
///
/// # Returns
///
/// The cost value (0.5 * sum of squared residuals)
pub fn compute_least_squares_cost(residuals: &DVector<f64>) -> f64 {
    0.5 * residuals.norm_squared()
}

/// Compute J^T × x for sparse CSC matrix.
///
/// Computes the product of the transpose of a sparse Jacobian matrix
/// with a dense vector. This is commonly used for gradient computation:
/// gradient = J^T × residuals.
///
/// # Arguments
///
/// * `jacobian` - The Jacobian matrix in CSC (Compressed Sparse Column) format
/// * `x` - The input vector (typically residuals)
/// * `out` - Pre-allocated output vector to store J^T × x
///
/// # Performance
///
/// This function reuses the `out` buffer to avoid allocations. It should
/// be called with a workspace buffer to maximize performance.
pub fn sparse_jt_multiply(
    jacobian: &SparseMatrixCSC,
    x: &DVector<f64>,
    out: &mut DVector<f64>,
) {
    out.fill(0.0);

    // J^T * x for CSC matrix: iterate over columns
    for col in 0..jacobian.ncol {
        let start = jacobian.col_pointers[col] as usize;
        let end = jacobian.col_pointers[col + 1] as usize;

        for idx in start..end {
            let row = jacobian.row_indices[idx] as usize;
            let value = jacobian.values[idx];
            out[col] += value * x[row];
        }
    }
}

/// Assemble J^T J + damping term in sparse COO format (upper triangular).
///
/// Computes the normal equations matrix J^T J and adds diagonal damping
/// (regularization). This is used in both Levenberg-Marquardt and
/// Powell Dog-Leg trust region methods.
///
/// # Arguments
///
/// * `jacobian` - The Jacobian matrix in CSC format
/// * `jtj_coo_buffer` - Pre-allocated COO buffer for output (will be cleared)
/// * `scaling` - Parameter scaling factors (for damping)
/// * `damping_factor` - Damping parameter (lambda or mu)
/// * `extra_regularization` - Additional regularization term (default 0.0)
/// * `epsilon` - Threshold for dropping near-zero entries
///
/// # Output
///
/// The function fills `jtj_coo_buffer` with the upper triangular part of
/// (J^T J + damping_factor * diag(scaling)^2 + extra_regularization * I).
///
/// # Performance
///
/// This function reuses the COO buffer to avoid allocations. The buffer
/// is cleared at the start of the function.
pub fn assemble_jtj_with_damping(
    jacobian: &SparseMatrixCSC,
    jtj_coo_buffer: &mut SparseMatrixCOO,
    scaling: &[f64],
    damping_factor: f64,
    extra_regularization: f64,
    epsilon: f64,
) -> Result<(), mmcholmod::CholmodError> {
    clear_sparse_coo(jtj_coo_buffer);

    // Compute J^T * J (upper triangular only)
    for col_j in 0..jacobian.ncol {
        let start_j = jacobian.col_pointers[col_j] as usize;
        let end_j = jacobian.col_pointers[col_j + 1] as usize;

        for col_i in col_j..jacobian.ncol {
            let start_i = jacobian.col_pointers[col_i] as usize;
            let end_i = jacobian.col_pointers[col_i + 1] as usize;

            let mut sum = 0.0;

            // Compute dot product of columns i and j
            let mut idx_i = start_i;
            let mut idx_j = start_j;

            while idx_i < end_i && idx_j < end_j {
                let row_i = jacobian.row_indices[idx_i] as usize;
                let row_j = jacobian.row_indices[idx_j] as usize;

                if row_i == row_j {
                    sum += jacobian.values[idx_i] * jacobian.values[idx_j];
                    idx_i += 1;
                    idx_j += 1;
                } else if row_i < row_j {
                    idx_i += 1;
                } else {
                    idx_j += 1;
                }
            }

            // Add damping to diagonal: damping_factor * scale^2 + extra_regularization
            if col_i == col_j {
                let scale = scaling[col_i];
                sum += damping_factor * scale * scale + extra_regularization;
            }

            if sum.abs() > epsilon {
                jtj_coo_buffer.push(col_j, col_i, sum)?;
            }
        }
    }

    Ok(())
}

/// Compute J × v for sparse CSC matrix.
///
/// Computes the product of a sparse Jacobian matrix with a dense vector.
/// This is used for computing J * step in trust region methods.
///
/// # Arguments
///
/// * `jacobian` - The Jacobian matrix in CSC format
/// * `v` - The input vector (typically a step)
/// * `out` - Pre-allocated output vector to store J × v
///
/// # Performance
///
/// This function reuses the `out` buffer to avoid allocations.
pub fn sparse_j_multiply(
    jacobian: &SparseMatrixCSC,
    v: &DVector<f64>,
    out: &mut DVector<f64>,
) {
    out.fill(0.0);

    for col in 0..jacobian.ncol {
        let start = jacobian.col_pointers[col] as usize;
        let end = jacobian.col_pointers[col + 1] as usize;

        for idx in start..end {
            let row = jacobian.row_indices[idx] as usize;
            out[row] += jacobian.values[idx] * v[col];
        }
    }
}

/// Compute ||J × v||^2 for sparse CSC matrix without allocating.
///
/// Computes the squared norm of J * v directly, without allocating
/// an intermediate buffer. More efficient than computing J*v and
/// then taking the norm when only the norm is needed.
///
/// # Arguments
///
/// * `jacobian` - The Jacobian matrix in CSC format
/// * `v` - The input vector
///
/// # Returns
///
/// The squared L2 norm of J × v
pub fn sparse_j_multiply_norm_squared(
    jacobian: &SparseMatrixCSC,
    v: &DVector<f64>,
) -> f64 {
    let mut result = 0.0;

    // For each row of J
    for row in 0..jacobian.nrow {
        let mut dot = 0.0;

        // Accumulate dot product for this row
        for col in 0..jacobian.ncol {
            let start = jacobian.col_pointers[col] as usize;
            let end = jacobian.col_pointers[col + 1] as usize;

            for idx in start..end {
                if jacobian.row_indices[idx] as usize == row {
                    dot += jacobian.values[idx] * v[col];
                    break;
                }
            }
        }

        result += dot * dot;
    }

    result
}

/// Compute normalized gradient norm for convergence checking.
///
/// Computes ||gradient|| / max(cost, 1.0) which is a scale-invariant
/// measure of gradient size commonly used for convergence checks.
///
/// # Arguments
///
/// * `gradient` - The gradient vector
/// * `cost` - The current cost value
///
/// # Returns
///
/// The normalized gradient norm
pub fn compute_normalized_gradient_norm(
    gradient: &DVector<f64>,
    cost: f64,
) -> f64 {
    gradient.norm() / cost.max(1.0)
}

/// Compute Jacobian column norms for parameter scaling.
///
/// Computes the L2 norm of each column of the Jacobian matrix.
/// This is equivalent to the square root of the diagonal of J^T J.
///
/// # Arguments
///
/// * `jacobian` - The Jacobian matrix in CSC format
/// * `out` - Pre-allocated output vector for column norms
///
/// # Performance
///
/// This function reuses the `out` buffer to avoid allocations.
pub fn compute_jacobian_column_norms(
    jacobian: &SparseMatrixCSC,
    out: &mut DVector<f64>,
) {
    for col in 0..jacobian.ncol {
        let start = jacobian.col_pointers[col] as usize;
        let end = jacobian.col_pointers[col + 1] as usize;

        let mut col_norm_sq = 0.0;
        for idx in start..end {
            let value = jacobian.values[idx];
            col_norm_sq += value * value;
        }

        out[col] = if col_norm_sq > 0.0 {
            col_norm_sq.sqrt().max(1.0)
        } else {
            1.0
        };
    }
}
