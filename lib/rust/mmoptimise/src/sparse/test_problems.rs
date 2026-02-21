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

use anyhow::Result;

use crate::solver::test_problems::{
    CurveFittingProblem, ExtendedRosenbrockProblem, PowellProblem,
    RosenbrockProblem,
};
use crate::sparse::SparseOptimisationProblem;

// ============================================================================
// Sparse Optimisation Problem Implementations
// ============================================================================

// Sparse implementation for RosenbrockProblem
impl SparseOptimisationProblem for RosenbrockProblem {
    fn compute_sparse_jacobian(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> Result<(Vec<usize>, Vec<usize>, Vec<f64>)> {
        let x = parameters[0];
        let y = parameters[1];
        let sqrt_b = self.b.sqrt();

        out_residuals[0] = self.a - x;
        out_residuals[1] = sqrt_b * (y - x * x);

        let mut row_indices = Vec::new();
        let mut col_indices = Vec::new();
        let mut values = Vec::new();

        // r0 derivatives
        row_indices.push(0);
        col_indices.push(0);
        values.push(-1.0);

        // r1 derivatives
        row_indices.push(1);
        col_indices.push(0);
        values.push(-2.0 * sqrt_b * x);

        row_indices.push(1);
        col_indices.push(1);
        values.push(sqrt_b);

        Ok((row_indices, col_indices, values))
    }

    fn parameter_count(&self) -> usize {
        2
    }

    fn residual_count(&self) -> usize {
        2
    }
}

// Sparse implementation for ExtendedRosenbrockProblem
impl SparseOptimisationProblem for ExtendedRosenbrockProblem {
    fn compute_sparse_jacobian(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> Result<(Vec<usize>, Vec<usize>, Vec<f64>)> {
        let mut row_indices = Vec::new();
        let mut col_indices = Vec::new();
        let mut values = Vec::new();

        for i in 0..(self.n / 2) {
            let x_i = parameters[2 * i];
            let x_i1 = parameters[2 * i + 1];

            out_residuals[2 * i] = 1.0 - x_i;
            out_residuals[2 * i + 1] = 10.0 * (x_i1 - x_i * x_i);

            // r_{2i} = 1 - x_i
            row_indices.push(2 * i);
            col_indices.push(2 * i);
            values.push(-1.0);

            // r_{2i+1} = 10 * (x_{i+1} - x_i^2)
            row_indices.push(2 * i + 1);
            col_indices.push(2 * i);
            values.push(-20.0 * x_i);

            row_indices.push(2 * i + 1);
            col_indices.push(2 * i + 1);
            values.push(10.0);
        }

        Ok((row_indices, col_indices, values))
    }

    fn parameter_count(&self) -> usize {
        self.n
    }

    fn residual_count(&self) -> usize {
        self.n
    }
}

// Sparse implementation for PowellProblem
impl SparseOptimisationProblem for PowellProblem {
    fn compute_sparse_jacobian(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> Result<(Vec<usize>, Vec<usize>, Vec<f64>)> {
        let x0 = parameters[0];
        let x1 = parameters[1];
        let x2 = parameters[2];
        let x3 = parameters[3];

        out_residuals[0] = x0 + 10.0 * x1;
        out_residuals[1] = 5.0_f64.sqrt() * (x2 - x3);
        out_residuals[2] = (x1 - 2.0 * x2).powi(2);
        out_residuals[3] = 10.0_f64.sqrt() * (x0 - x3).powi(2);

        let mut row_indices = Vec::new();
        let mut col_indices = Vec::new();
        let mut values = Vec::new();

        // r0 derivatives
        row_indices.push(0);
        col_indices.push(0);
        values.push(1.0);

        row_indices.push(0);
        col_indices.push(1);
        values.push(10.0);

        // r1 derivatives
        row_indices.push(1);
        col_indices.push(2);
        values.push(5.0_f64.sqrt());

        row_indices.push(1);
        col_indices.push(3);
        values.push(-5.0_f64.sqrt());

        // r2 derivatives
        let diff = x1 - 2.0 * x2;
        row_indices.push(2);
        col_indices.push(1);
        values.push(2.0 * diff);

        row_indices.push(2);
        col_indices.push(2);
        values.push(-4.0 * diff);

        // r3 derivatives
        let diff2 = x0 - x3;
        row_indices.push(3);
        col_indices.push(0);
        values.push(2.0 * 10.0_f64.sqrt() * diff2);

        row_indices.push(3);
        col_indices.push(3);
        values.push(-2.0 * 10.0_f64.sqrt() * diff2);

        Ok((row_indices, col_indices, values))
    }

    fn parameter_count(&self) -> usize {
        4
    }

    fn residual_count(&self) -> usize {
        4
    }
}

// Sparse implementation for CurveFittingProblem
impl SparseOptimisationProblem for CurveFittingProblem {
    fn compute_sparse_jacobian(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> Result<(Vec<usize>, Vec<usize>, Vec<f64>)> {
        let m = parameters[0];
        let c = parameters[1];

        let mut row_indices = Vec::new();
        let mut col_indices = Vec::new();
        let mut values = Vec::new();

        for i in 0..self.x_data.len() {
            let x_i = self.x_data[i];
            let y_i = self.y_data[i];
            let exp_val = (m * x_i + c).exp();

            out_residuals[i] = exp_val - y_i;

            // dr_i/dm = x_i * exp(m*x_i + c)
            row_indices.push(i);
            col_indices.push(0);
            values.push(x_i * exp_val);

            // dr_i/dc = exp(m*x_i + c)
            row_indices.push(i);
            col_indices.push(1);
            values.push(exp_val);
        }

        Ok((row_indices, col_indices, values))
    }

    fn parameter_count(&self) -> usize {
        2
    }

    fn residual_count(&self) -> usize {
        self.x_data.len()
    }
}
