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

//! Sparse matrix data structures for interfacing with CHOLMOD.
//!
//! CHOLMOD uses CSC (Compressed Sparse Column) format as its native
//! representation. This module provides structures to build and
//! manipulate sparse matrices in formats compatible with CHOLMOD.

use thiserror::Error;

/// Error types for sparse matrix operations.
#[derive(Error, Debug)]
pub enum SparseMatrixError {
    #[error("Invalid matrix dimensions: rows={rows}, cols={cols}")]
    InvalidDimensions { rows: usize, cols: usize },

    #[error("Invalid entry: row={row}, col={col}, nrow={nrow}, ncol={ncol}")]
    InvalidEntry {
        row: usize,
        col: usize,
        nrow: usize,
        ncol: usize,
    },

    #[error("Matrix is not square: {rows}x{cols}")]
    NotSquare { rows: usize, cols: usize },

    #[error("Matrix must be symmetric for Cholesky factorization")]
    NotSymmetric,

    #[error("Conversion error: {0}")]
    ConversionError(String),
}

/// Symmetry type for sparse matrices.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum SymmetryType {
    /// Lower triangular part only (stype = -1).
    LowerTriangular,
    /// Unsymmetric (stype = 0).
    Unsymmetric,
    /// Upper triangular part only (stype = 1).
    UpperTriangular,
}

impl SymmetryType {
    /// Convert to CHOLMOD stype integer.
    pub fn to_stype(&self) -> i32 {
        match self {
            SymmetryType::LowerTriangular => -1,
            SymmetryType::Unsymmetric => 0,
            SymmetryType::UpperTriangular => 1,
        }
    }
}

/// Sparse matrix in COO (Coordinate) format.
///
/// This format is convenient for building matrices incrementally by
/// adding individual entries. It can be converted to CSC format for
/// use with CHOLMOD.
#[derive(Debug, Clone)]
pub struct SparseMatrixCOO {
    /// Number of rows.
    pub nrow: usize,
    /// Number of columns.
    pub ncol: usize,
    /// Row indices.
    pub row_indices: Vec<usize>,
    /// Column indices.
    pub col_indices: Vec<usize>,
    /// Values.
    pub values: Vec<f64>,
    /// Symmetry type.
    pub symmetry: SymmetryType,
}

impl SparseMatrixCOO {
    /// Create a new sparse matrix in COO format.
    pub fn new(
        nrow: usize,
        ncol: usize,
        symmetry: SymmetryType,
    ) -> Result<Self, SparseMatrixError> {
        if nrow == 0 || ncol == 0 {
            return Err(SparseMatrixError::InvalidDimensions {
                rows: nrow,
                cols: ncol,
            });
        }

        Ok(SparseMatrixCOO {
            nrow,
            ncol,
            row_indices: Vec::new(),
            col_indices: Vec::new(),
            values: Vec::new(),
            symmetry,
        })
    }

    /// Add an entry to the matrix.
    ///
    /// For symmetric matrices, only entries in the specified triangle
    /// should be added.
    pub fn push(
        &mut self,
        row: usize,
        col: usize,
        value: f64,
    ) -> Result<(), SparseMatrixError> {
        if row >= self.nrow || col >= self.ncol {
            return Err(SparseMatrixError::InvalidEntry {
                row,
                col,
                nrow: self.nrow,
                ncol: self.ncol,
            });
        }

        self.row_indices.push(row);
        self.col_indices.push(col);
        self.values.push(value);

        Ok(())
    }

    /// Get the number of nonzero entries.
    pub fn nnz(&self) -> usize {
        self.values.len()
    }

    /// Convert to CSC format.
    pub fn to_csc(&self) -> Result<SparseMatrixCSC, SparseMatrixError> {
        SparseMatrixCSC::from_coo(self)
    }
}

/// Sparse matrix in CSC (Compressed Sparse Column) format.
///
/// This is CHOLMOD's native format. Matrices must be in this format
/// before being passed to the CHOLMOD solver.
#[derive(Debug, Clone)]
pub struct SparseMatrixCSC {
    /// Number of rows.
    pub nrow: usize,
    /// Number of columns.
    pub ncol: usize,
    /// Column pointers (size: ncol + 1).
    pub col_pointers: Vec<i32>,
    /// Row indices (size: nnz).
    pub row_indices: Vec<i32>,
    /// Values (size: nnz).
    pub values: Vec<f64>,
    /// Symmetry type.
    pub symmetry: SymmetryType,
}

impl SparseMatrixCSC {
    /// Create CSC matrix from COO matrix.
    pub fn from_coo(coo: &SparseMatrixCOO) -> Result<Self, SparseMatrixError> {
        let nrow = coo.nrow;
        let ncol = coo.ncol;
        let nnz = coo.nnz();

        // Count entries per column.
        let mut col_counts = vec![0i32; ncol];
        for &col in &coo.col_indices {
            col_counts[col] += 1;
        }

        // Build column pointers (cumulative sum).
        let mut col_pointers = vec![0i32; ncol + 1];
        for i in 0..ncol {
            col_pointers[i + 1] = col_pointers[i] + col_counts[i];
        }

        // Allocate arrays for row indices and values.
        let mut row_indices = vec![0i32; nnz];
        let mut values = vec![0.0; nnz];

        // Fill in row indices and values, sorted by column
        let mut col_positions = col_pointers.clone();
        for i in 0..nnz {
            let col = coo.col_indices[i];
            let pos = col_positions[col] as usize;
            row_indices[pos] = coo.row_indices[i] as i32;
            values[pos] = coo.values[i];
            col_positions[col] += 1;
        }

        // Sort each column by row index (CHOLMOD expects sorted columns).
        for col in 0..ncol {
            let start = col_pointers[col] as usize;
            let end = col_pointers[col + 1] as usize;
            if end > start {
                // Create indices for sorting.
                let mut indices: Vec<usize> = (start..end).collect();
                indices.sort_by_key(|&i| row_indices[i]);

                // Reorder row_indices and values.
                let row_temp: Vec<i32> =
                    indices.iter().map(|&i| row_indices[i]).collect();
                let val_temp: Vec<f64> =
                    indices.iter().map(|&i| values[i]).collect();

                for i in 0..indices.len() {
                    row_indices[start + i] = row_temp[i];
                    values[start + i] = val_temp[i];
                }
            }
        }

        Ok(SparseMatrixCSC {
            nrow,
            ncol,
            col_pointers,
            row_indices,
            values,
            symmetry: coo.symmetry,
        })
    }

    /// Get the number of nonzero entries.
    pub fn nnz(&self) -> usize {
        self.values.len()
    }

    /// Verify that the matrix is square.
    pub fn verify_square(&self) -> Result<(), SparseMatrixError> {
        if self.nrow != self.ncol {
            return Err(SparseMatrixError::NotSquare {
                rows: self.nrow,
                cols: self.ncol,
            });
        }
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_coo_creation() {
        let matrix =
            SparseMatrixCOO::new(3, 3, SymmetryType::Unsymmetric).unwrap();
        assert_eq!(matrix.nrow, 3);
        assert_eq!(matrix.ncol, 3);
        assert_eq!(matrix.nnz(), 0);
    }

    #[test]
    fn test_coo_push() {
        let mut matrix =
            SparseMatrixCOO::new(3, 3, SymmetryType::Unsymmetric).unwrap();
        matrix.push(0, 0, 1.0).unwrap();
        matrix.push(1, 1, 2.0).unwrap();
        matrix.push(2, 2, 3.0).unwrap();
        assert_eq!(matrix.nnz(), 3);
    }

    #[test]
    fn test_coo_to_csc() {
        let mut coo =
            SparseMatrixCOO::new(3, 3, SymmetryType::Unsymmetric).unwrap();
        coo.push(0, 0, 1.0).unwrap();
        coo.push(1, 1, 2.0).unwrap();
        coo.push(2, 2, 3.0).unwrap();

        let csc = coo.to_csc().unwrap();
        assert_eq!(csc.nrow, 3);
        assert_eq!(csc.ncol, 3);
        assert_eq!(csc.nnz(), 3);
        assert_eq!(csc.col_pointers, vec![0, 1, 2, 3]);
        assert_eq!(csc.row_indices, vec![0, 1, 2]);
        assert_eq!(csc.values, vec![1.0, 2.0, 3.0]);
    }

    #[test]
    fn test_symmetry_type() {
        assert_eq!(SymmetryType::LowerTriangular.to_stype(), -1);
        assert_eq!(SymmetryType::Unsymmetric.to_stype(), 0);
        assert_eq!(SymmetryType::UpperTriangular.to_stype(), 1);
    }
}
