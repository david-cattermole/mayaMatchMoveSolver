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

//! Foreign Function Interface (FFI) bindings to CHOLMOD C library.
//!
//! This module provides unsafe extern "C" declarations for calling
//! the C wrapper functions defined in interface_cholmod.c.

/// Type alias for C boolean values
pub type CcBool = i32;

/// Exit codes from C interface
pub const SUCCESSFUL_EXIT: i32 = 0;
pub const ERROR_NULL_POINTER: i32 = 100000;
pub const ERROR_MALLOC: i32 = 200000;
pub const ERROR_NOT_POSITIVE_DEFINITE: i32 = 300000;
pub const ERROR_NOT_INITIALIZED: i32 = 400000;
pub const ERROR_NOT_FACTORIZED: i32 = 500000;
pub const ERROR_ALREADY_INITIALIZED: i32 = 600000;
pub const ERROR_INVALID_INPUT: i32 = 700000;

/// Opaque struct holding a C-pointer to InterfaceCHOLMOD.
///
/// This is an opaque type that wraps the C struct. Rust code cannot
/// inspect its contents directly.
///
/// Reference: <https://doc.rust-lang.org/nomicon/ffi.html#representing-opaque-structs>
#[repr(C)]
pub struct InterfaceCHOLMOD {
    _data: [u8; 0],
    _marker: core::marker::PhantomData<(*mut u8, core::marker::PhantomPinned)>,
}

/// Enforce Send on the C structure.
///
/// This is safe because the C structure does not share state between
/// threads, and all access is controlled through Rust's ownership
/// system.
///
/// <https://stackoverflow.com/questions/50258359/can-a-struct-containing-a-raw-pointer-implement-send-and-be-ffi-safe>
unsafe impl Send for InterfaceCHOLMOD {}

extern "C" {
    /// Allocates a new CHOLMOD solver.
    pub fn solver_cholmod_new() -> *mut InterfaceCHOLMOD;

    /// Deallocates the CHOLMOD solver.
    pub fn solver_cholmod_drop(solver: *mut InterfaceCHOLMOD);

    /// Performs symbolic factorization (analyze phase).
    ///
    /// # Arguments
    /// * `solver` - Pointer to solver structure.
    /// * `nrow` - Number of rows.
    /// * `ncol` - Number of columns.
    /// * `nzmax` - Maximum number of nonzeros.
    /// * `col_pointers` - Column pointers array (CSC format).
    /// * `row_indices` - Row indices array (CSC format).
    /// * `values` - Values array (can be NULL for pattern).
    /// * `stype` - Symmetry type: -1 (lower), 0 (unsym), 1 (upper).
    /// * `verbose` - Enable verbose output.
    pub fn solver_cholmod_analyze(
        solver: *mut InterfaceCHOLMOD,
        nrow: i32,
        ncol: i32,
        nzmax: i32,
        col_pointers: *const i32,
        row_indices: *const i32,
        values: *const f64,
        stype: i32,
        verbose: CcBool,
    ) -> i32;

    /// Performs numeric factorization.
    ///
    /// # Arguments
    /// * `solver` - Pointer to solver structure.
    /// * `nrow` - Number of rows.
    /// * `ncol` - Number of columns.
    /// * `nzmax` - Maximum number of nonzeros.
    /// * `col_pointers` - Column pointers array (CSC format).
    /// * `row_indices` - Row indices array (CSC format).
    /// * `values` - Values array.
    /// * `stype` - Symmetry type: -1 (lower), 0 (unsym), 1 (upper)
    /// * `verbose` - Enable verbose output.
    pub fn solver_cholmod_factorize(
        solver: *mut InterfaceCHOLMOD,
        nrow: i32,
        ncol: i32,
        nzmax: i32,
        col_pointers: *const i32,
        row_indices: *const i32,
        values: *const f64,
        stype: i32,
        verbose: CcBool,
    ) -> i32;

    /// Solves the linear system Ax=b.
    ///
    /// # Arguments
    /// * `solver` - Pointer to solver structure.
    /// * `x` - Output solution vector (must be pre-allocated).
    /// * `rhs` - Right-hand side vector.
    /// * `n` - Dimension of the system.
    /// * `verbose` - Enable verbose output.
    pub fn solver_cholmod_solve(
        solver: *mut InterfaceCHOLMOD,
        x: *mut f64,
        rhs: *const f64,
        n: i32,
        verbose: CcBool,
    ) -> i32;

    /// Gets the reciprocal condition number estimate.
    ///
    /// # Arguments
    /// * `solver` - Pointer to solver structure.
    /// * `rcond_estimate` - Output reciprocal condition number.
    pub fn solver_cholmod_rcond(
        solver: *mut InterfaceCHOLMOD,
        rcond_estimate: *mut f64,
    ) -> i32;

    /// Resets the solver to uninitialized state, allowing reuse.
    ///
    /// # Arguments
    /// * `solver` - Pointer to solver structure.
    pub fn solver_cholmod_reset(solver: *mut InterfaceCHOLMOD);
}
