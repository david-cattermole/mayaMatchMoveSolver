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

//! Safe Rust wrapper for CHOLMOD sparse Cholesky solver.
//!
//! This module provides a safe, idiomatic Rust interface to the
//! CHOLMOD library for solving sparse symmetric positive definite
//! linear systems using Cholesky factorization.

use crate::ffi;
use crate::sparse_matrix::{SparseMatrixCSC, SparseMatrixError};
use thiserror::Error;

/// Error types for CHOLMOD solver operations.
#[derive(Error, Debug)]
pub enum CholmodError {
    #[error("Solver allocation failed")]
    AllocationFailed,

    #[error("Null pointer error")]
    NullPointer,

    #[error("Memory allocation error")]
    MemoryError,

    #[error("Matrix is not positive definite")]
    NotPositiveDefinite,

    #[error("Solver not initialized")]
    NotInitialized,

    #[error("Solver not factorized")]
    NotFactorized,

    #[error("Solver already initialized")]
    AlreadyInitialized,

    #[error("Invalid input")]
    InvalidInput,

    #[error("Unknown error: code {0}")]
    Unknown(i32),

    #[error("Sparse matrix error: {0}")]
    SparseMatrix(#[from] SparseMatrixError),

    #[error("Dimension mismatch: expected {expected}, got {actual}")]
    DimensionMismatch { expected: usize, actual: usize },
}

/// Convert C error codes to Rust error types.
fn handle_error_code(code: i32) -> Result<(), CholmodError> {
    match code {
        ffi::SUCCESSFUL_EXIT => Ok(()),
        ffi::ERROR_NULL_POINTER => Err(CholmodError::NullPointer),
        ffi::ERROR_MALLOC => Err(CholmodError::MemoryError),
        ffi::ERROR_NOT_POSITIVE_DEFINITE => {
            Err(CholmodError::NotPositiveDefinite)
        }
        ffi::ERROR_NOT_INITIALIZED => Err(CholmodError::NotInitialized),
        ffi::ERROR_NOT_FACTORIZED => Err(CholmodError::NotFactorized),
        ffi::ERROR_ALREADY_INITIALIZED => Err(CholmodError::AlreadyInitialized),
        ffi::ERROR_INVALID_INPUT => Err(CholmodError::InvalidInput),
        code => Err(CholmodError::Unknown(code)),
    }
}

/// CHOLMOD sparse Cholesky solver.
///
/// This solver performs Cholesky factorization (A = LL' or A = LDL')
/// of symmetric positive definite matrices and solves linear systems
/// using the factorization.
///
/// # Example
///
/// ```no_run
/// use mmcholmod_rust::solver::CholmodSolver;
/// use mmcholmod_rust::sparse_matrix::{SparseMatrixCOO, SymmetryType};
///
/// // Create a simple 2x2 symmetric positive definite matrix.
/// // A = [2.0  1.0]
/// //     [1.0  2.0]
/// let mut coo = SparseMatrixCOO::new(2, 2, SymmetryType::UpperTriangular).unwrap();
/// coo.push(0, 0, 2.0).unwrap();
/// coo.push(0, 1, 1.0).unwrap();
/// coo.push(1, 1, 2.0).unwrap();
/// let csc = coo.to_csc().unwrap();
///
/// // Create solver and factorize.
/// let mut solver = CholmodSolver::new().unwrap();
/// solver.analyze(&csc, false).unwrap();
/// solver.factorize(&csc, false).unwrap();
///
/// // Solve Ax=b with b=[1.0, 1.0]
/// let b = vec![1.0, 1.0];
/// let x = solver.solve(&b, false).unwrap();
/// ```
pub struct CholmodSolver {
    /// Pointer to C solver structure.
    solver: *mut ffi::InterfaceCHOLMOD,
    /// Track initialization state.
    initialized: bool,
    /// Track factorization state.
    factorized: bool,
    /// Matrix dimension (rows = cols for square matrices).
    ndim: usize,
}

/// Ensure the solver can be sent between threads.
unsafe impl Send for CholmodSolver {}

impl CholmodSolver {
    /// Create a new CHOLMOD solver instance.
    pub fn new() -> Result<Self, CholmodError> {
        let solver = unsafe { ffi::solver_cholmod_new() };

        if solver.is_null() {
            return Err(CholmodError::AllocationFailed);
        }

        Ok(CholmodSolver {
            solver,
            initialized: false,
            factorized: false,
            ndim: 0,
        })
    }

    /// Perform symbolic factorization (analyze phase).
    ///
    /// This analyzes the sparsity pattern of the matrix and
    /// determines the optimal ordering for factorization. This only
    /// needs to be called once for matrices with the same sparsity
    /// pattern.
    ///
    /// # Arguments
    ///
    /// * `matrix` - Sparse matrix in CSC format.
    /// * `verbose` - Enable verbose output.
    pub fn analyze(
        &mut self,
        matrix: &SparseMatrixCSC,
        verbose: bool,
    ) -> Result<(), CholmodError> {
        // Verify matrix is square
        matrix.verify_square()?;

        let nrow = matrix.nrow as i32;
        let ncol = matrix.ncol as i32;
        let nzmax = matrix.nnz() as i32;
        let stype = matrix.symmetry.to_stype();
        let verbose_flag = if verbose { 1 } else { 0 };

        let status = unsafe {
            ffi::solver_cholmod_analyze(
                self.solver,
                nrow,
                ncol,
                nzmax,
                matrix.col_pointers.as_ptr(),
                matrix.row_indices.as_ptr(),
                matrix.values.as_ptr(),
                stype,
                verbose_flag,
            )
        };

        handle_error_code(status)?;

        self.initialized = true;
        self.ndim = matrix.nrow;
        Ok(())
    }

    /// Perform numeric factorization.
    ///
    /// This computes the actual Cholesky factors using the ordering
    /// determined by the analyze phase. Can be called multiple times
    /// with different matrix values (but same sparsity pattern).
    ///
    /// # Arguments
    ///
    /// * `matrix` - Sparse matrix in CSC format.
    /// * `verbose` - Enable verbose output.
    pub fn factorize(
        &mut self,
        matrix: &SparseMatrixCSC,
        verbose: bool,
    ) -> Result<(), CholmodError> {
        // Verify matrix is square
        matrix.verify_square()?;

        let nrow = matrix.nrow as i32;
        let ncol = matrix.ncol as i32;
        let nzmax = matrix.nnz() as i32;
        let stype = matrix.symmetry.to_stype();
        let verbose_flag = if verbose { 1 } else { 0 };

        let status = unsafe {
            ffi::solver_cholmod_factorize(
                self.solver,
                nrow,
                ncol,
                nzmax,
                matrix.col_pointers.as_ptr(),
                matrix.row_indices.as_ptr(),
                matrix.values.as_ptr(),
                stype,
                verbose_flag,
            )
        };

        handle_error_code(status)?;

        self.factorized = true;
        Ok(())
    }

    /// Solve the linear system Ax=b.
    ///
    /// Uses the previously computed Cholesky factorization to solve
    /// the linear system.
    ///
    /// # Arguments
    ///
    /// * `rhs` - Right-hand side vector b.
    /// * `verbose` - Enable verbose output.
    ///
    /// # Returns
    ///
    /// Solution vector x.
    pub fn solve(
        &mut self,
        rhs: &[f64],
        verbose: bool,
    ) -> Result<Vec<f64>, CholmodError> {
        if rhs.len() != self.ndim {
            return Err(CholmodError::DimensionMismatch {
                expected: self.ndim,
                actual: rhs.len(),
            });
        }

        let mut x = vec![0.0; self.ndim];
        let n = self.ndim as i32;
        let verbose_flag = if verbose { 1 } else { 0 };

        let status = unsafe {
            ffi::solver_cholmod_solve(
                self.solver,
                x.as_mut_ptr(),
                rhs.as_ptr(),
                n,
                verbose_flag,
            )
        };

        handle_error_code(status)?;

        Ok(x)
    }

    /// Get the reciprocal condition number estimate.
    ///
    /// Returns an estimate of the reciprocal of the condition number.
    ///
    /// Values close to 0 indicate an ill-conditioned matrix.
    pub fn rcond(&self) -> Result<f64, CholmodError> {
        let mut rcond = 0.0;

        let status =
            unsafe { ffi::solver_cholmod_rcond(self.solver, &mut rcond) };

        handle_error_code(status)?;

        Ok(rcond)
    }

    /// Check if solver has been initialized.
    pub fn is_initialized(&self) -> bool {
        self.initialized
    }

    /// Check if matrix has been factorized.
    pub fn is_factorized(&self) -> bool {
        self.factorized
    }

    /// Get matrix dimension.
    pub fn ndim(&self) -> usize {
        self.ndim
    }

    /// Reset the solver to uninitialized state, allowing reuse with
    /// different problems.
    ///
    /// This frees the internal factorization and resets state flags,
    /// allowing the solver to be reused for a different matrix
    /// structure. This is more efficient than creating a new solver
    /// instance when you need to solve multiple different problems
    /// sequentially.
    ///
    /// After calling reset(), you must call analyze() and factorize()
    /// again before calling solve().
    pub fn reset(&mut self) {
        unsafe {
            ffi::solver_cholmod_reset(self.solver);
        }
        self.initialized = false;
        self.factorized = false;
        self.ndim = 0;
    }
}

impl Drop for CholmodSolver {
    /// Cleanup solver resources.
    fn drop(&mut self) {
        unsafe {
            ffi::solver_cholmod_drop(self.solver);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::sparse_matrix::{SparseMatrixCOO, SymmetryType};

    #[test]
    fn test_solver_creation() {
        let solver = CholmodSolver::new();
        assert!(solver.is_ok());
    }

    #[test]
    fn test_simple_2x2_system() {
        // Create a simple 2x2 symmetric positive definite matrix.
        // A = [2.0  1.0]
        //     [1.0  2.0]
        // Store upper triangle only.
        let mut coo =
            SparseMatrixCOO::new(2, 2, SymmetryType::UpperTriangular).unwrap();
        coo.push(0, 0, 2.0).unwrap();
        coo.push(0, 1, 1.0).unwrap();
        coo.push(1, 1, 2.0).unwrap();

        let csc = coo.to_csc().unwrap();

        let mut solver = CholmodSolver::new().unwrap();

        solver.analyze(&csc, false).unwrap();
        assert!(solver.is_initialized());

        solver.factorize(&csc, false).unwrap();
        assert!(solver.is_factorized());

        // Solve Ax=b with b=[3.0, 3.0]
        // Expected solution: x=[1.0, 1.0]
        let b = vec![3.0, 3.0];
        let x = solver.solve(&b, false).unwrap();

        // Verify solution.
        assert_eq!(x.len(), 2);
        assert!((x[0] - 1.0).abs() < 1e-10);
        assert!((x[1] - 1.0).abs() < 1e-10);
    }

    #[test]
    fn test_cholmod_simple_example() {
        // This test is based on cholmod_di_simple.c
        //
        // Create a simple symmetric positive definite matrix.
        //
        // We'll use a 5x5 tridiagonal matrix:
        //
        // A = [ 2 -1  0  0  0]
        //     [-1  2 -1  0  0]
        //     [ 0 -1  2 -1  0]
        //     [ 0  0 -1  2 -1]
        //     [ 0  0  0 -1  2]
        //
        // This matrix is symmetric positive definite.
        //
        // Store only upper triangle.

        let n = 5;
        let mut coo =
            SparseMatrixCOO::new(n, n, SymmetryType::UpperTriangular).unwrap();

        // Diagonal entries.
        for i in 0..n {
            coo.push(i, i, 2.0).unwrap();
        }

        // Upper diagonal entries.
        for i in 0..n - 1 {
            coo.push(i, i + 1, -1.0).unwrap();
        }

        let csc = coo.to_csc().unwrap();

        let mut solver = CholmodSolver::new().unwrap();
        solver.analyze(&csc, false).unwrap();
        solver.factorize(&csc, false).unwrap();

        // Solve Ax=b where b = ones(n,1)
        let b = vec![1.0; n];
        let x = solver.solve(&b, false).unwrap();

        // Verify solution by computing residual r = Ax - b
        // For the tridiagonal matrix:
        // (Ax)_i = 2*x_i - x_{i-1} - x_{i+1}
        let mut ax = vec![0.0; n];
        for i in 0..n {
            ax[i] = 2.0 * x[i];
            if i > 0 {
                ax[i] -= x[i - 1];
            }
            if i < n - 1 {
                ax[i] -= x[i + 1];
            }
        }

        // Compute residual norm.
        let mut residual_norm = 0.0;
        for i in 0..n {
            let diff = ax[i] - b[i];
            residual_norm += diff * diff;
        }
        residual_norm = residual_norm.sqrt();

        // Compute norm of A (approximately 4.0 for this matrix).
        let anorm = 4.0;

        // Compute norm of x.
        let mut xnorm = 0.0;
        for i in 0..n {
            xnorm += x[i] * x[i];
        }
        xnorm = xnorm.sqrt();

        // Relative residual.
        let relative_residual = residual_norm / (anorm * xnorm + 1.0);

        println!("Residual norm: {}", residual_norm);
        println!("Relative residual: {}", relative_residual);

        // Check that residual is small (should be near machine precision).
        assert!(
            relative_residual < 1e-10,
            "Residual too large: {}",
            relative_residual
        );

        // Get condition number estimate.
        let rcond = solver.rcond().unwrap();
        println!("Reciprocal condition number: {}", rcond);
        assert!(rcond > 0.0);
    }

    #[test]
    fn test_identity_matrix() {
        // Test with identity matrix (trivial case).
        let n = 3;
        let mut coo =
            SparseMatrixCOO::new(n, n, SymmetryType::UpperTriangular).unwrap();

        // Identity matrix.
        for i in 0..n {
            coo.push(i, i, 1.0).unwrap();
        }

        let csc = coo.to_csc().unwrap();

        let mut solver = CholmodSolver::new().unwrap();
        solver.analyze(&csc, false).unwrap();
        solver.factorize(&csc, false).unwrap();

        // Solve Ix=b, should get x=b.
        let b = vec![1.0, 2.0, 3.0];
        let x = solver.solve(&b, false).unwrap();

        for i in 0..n {
            assert!((x[i] - b[i]).abs() < 1e-10);
        }
    }
}
