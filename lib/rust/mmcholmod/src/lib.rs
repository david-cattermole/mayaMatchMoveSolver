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

//! CHOLMOD sparse Cholesky solver bindings for Rust.
//!
//! This crate provides safe Rust bindings to the CHOLMOD library,
//! which implements sparse Cholesky factorization for solving
//! symmetric positive definite linear systems.
//!
//! # Example
//!
//! ```no_run
//! use mmcholmod_rust::solver::CholmodSolver;
//! use mmcholmod_rust::sparse_matrix::{SparseMatrixCOO, SymmetryType};
//!
//! // Create a 2x2 symmetric positive definite matrix
//! let mut coo = SparseMatrixCOO::new(2, 2, SymmetryType::UpperTriangular).unwrap();
//! coo.push(0, 0, 2.0).unwrap();
//! coo.push(0, 1, 1.0).unwrap();
//! coo.push(1, 1, 2.0).unwrap();
//! let csc = coo.to_csc().unwrap();
//!
//! // Solve Ax=b
//! let mut solver = CholmodSolver::new().unwrap();
//! solver.analyze(&csc, false).unwrap();
//! solver.factorize(&csc, false).unwrap();
//! let x = solver.solve(&vec![3.0, 3.0], false).unwrap();
//! ```

mod ffi;
pub mod solver;
pub mod sparse_matrix;

// Re-export main types for convenience.
pub use solver::{CholmodError, CholmodSolver};
pub use sparse_matrix::{
    SparseMatrixCOO, SparseMatrixCSC, SparseMatrixError, SymmetryType,
};
