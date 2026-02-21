//
// Copyright (C) 2025 David Cattermole.
//
// This file is part of mmSolver.
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

//! Benchmark comparing Sparse Levenberg-Marquardt vs Dense Levenberg-Marquardt.
//!
//! This benchmark demonstrates the performance benefits of the sparse
//! solver for problems with sparse Jacobians.

use anyhow::Result;
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};
use mmoptimise_rust::solver::common::OptimisationProblem;
use mmoptimise_rust::solver::levenberg_marquardt::{
    LevenbergMarquardtConfig, LevenbergMarquardtSolver,
    LevenbergMarquardtWorkspace,
};
use mmoptimise_rust::sparse::sparse_levenberg_marquardt::{
    SparseLevenbergMarquardtConfig, SparseLevenbergMarquardtSolver,
    SparseLevenbergMarquardtWorkspace,
};
use mmoptimise_rust::sparse::sparse_powell_dogleg::SparseOptimisationProblem;
use num_traits::Float;
use std::hint::black_box;
use std::ops::{Add, Div, Mul, Sub};
use std::time::Duration;

/// Tridiagonal linear system problem.
///
/// This is a sparse problem where each residual depends on only
/// 3 parameters (the tridiagonal structure).
struct TridiagonalProblem {
    n: usize,
    b: Vec<f64>,
}

impl TridiagonalProblem {
    fn new(n: usize) -> Self {
        let b = vec![1.0; n];
        Self { n, b }
    }
}

// Dense implementation for dense LM solver
impl OptimisationProblem for TridiagonalProblem {
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> Result<()>
    where
        T: Copy
            + Add<Output = T>
            + Sub<Output = T>
            + Mul<Output = T>
            + Div<Output = T>
            + From<f64>
            + Sized
            + num_traits::Zero
            + Float,
    {
        for i in 0..self.n {
            let mut ax_i = <T as From<f64>>::from(2.0) * parameters[i];
            if i > 0 {
                ax_i = ax_i - parameters[i - 1];
            }
            if i < self.n - 1 {
                ax_i = ax_i - parameters[i + 1];
            }
            out_residuals[i] = ax_i - <T as From<f64>>::from(self.b[i]);
        }
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        self.n
    }

    fn residual_count(&self) -> usize {
        self.n
    }
}

// Sparse implementation for sparse LM solver
impl SparseOptimisationProblem for TridiagonalProblem {
    fn compute_sparse_jacobian(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> Result<(Vec<usize>, Vec<usize>, Vec<f64>)> {
        let mut row_indices = Vec::new();
        let mut col_indices = Vec::new();
        let mut values = Vec::new();

        for i in 0..self.n {
            let mut ax_i = 2.0 * parameters[i];
            if i > 0 {
                ax_i -= parameters[i - 1];
            }
            if i < self.n - 1 {
                ax_i -= parameters[i + 1];
            }
            out_residuals[i] = ax_i - self.b[i];

            // Build sparse Jacobian
            row_indices.push(i);
            col_indices.push(i);
            values.push(2.0);

            if i > 0 {
                row_indices.push(i);
                col_indices.push(i - 1);
                values.push(-1.0);
            }

            if i < self.n - 1 {
                row_indices.push(i);
                col_indices.push(i + 1);
                values.push(-1.0);
            }
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

fn bench_sparse_vs_dense_small(c: &mut Criterion) {
    let mut group = c.benchmark_group("sparse_vs_dense_lm_small");
    group.measurement_time(Duration::from_secs(10));

    let sizes = vec![10, 20, 50];

    for n in sizes {
        let problem = TridiagonalProblem::new(n);
        let config = LevenbergMarquardtConfig::default();
        let initial = vec![0.0; n];

        // Dense solver
        let dense_solver = LevenbergMarquardtSolver::new(config);
        let mut dense_workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial).unwrap();

        group.bench_with_input(BenchmarkId::new("Dense", n), &n, |b, _| {
            b.iter(|| {
                dense_workspace.reuse_with(&problem, &initial).unwrap();
                black_box(
                    dense_solver
                        .solve_problem(&problem, &mut dense_workspace)
                        .unwrap(),
                )
            });
        });

        // Sparse solver
        let sparse_config = SparseLevenbergMarquardtConfig::default();
        let sparse_solver = SparseLevenbergMarquardtSolver::new(sparse_config);
        let mut sparse_workspace =
            SparseLevenbergMarquardtWorkspace::new(&problem, &initial).unwrap();

        group.bench_with_input(BenchmarkId::new("Sparse", n), &n, |b, _| {
            b.iter(|| {
                sparse_workspace.reuse_with(&problem, &initial).unwrap();
                black_box(
                    sparse_solver
                        .solve_problem(&problem, &mut sparse_workspace)
                        .unwrap(),
                )
            });
        });
    }

    group.finish();
}

fn bench_sparse_vs_dense_large(c: &mut Criterion) {
    let mut group = c.benchmark_group("sparse_vs_dense_lm_large");
    group.measurement_time(Duration::from_secs(15));
    group.sample_size(10); // Fewer samples for large problems

    let sizes = vec![100, 200, 500];

    for n in sizes {
        let problem = TridiagonalProblem::new(n);
        let config = LevenbergMarquardtConfig {
            max_iterations: 100,
            ..Default::default()
        };
        let initial = vec![0.0; n];

        // Dense solver
        let dense_solver = LevenbergMarquardtSolver::new(config);
        let mut dense_workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial).unwrap();

        group.bench_with_input(BenchmarkId::new("Dense", n), &n, |b, _| {
            b.iter(|| {
                dense_workspace.reuse_with(&problem, &initial).unwrap();
                black_box(
                    dense_solver
                        .solve_problem(&problem, &mut dense_workspace)
                        .unwrap(),
                )
            });
        });

        // Sparse solver
        let sparse_config = SparseLevenbergMarquardtConfig {
            max_iterations: 100,
            ..Default::default()
        };
        let sparse_solver = SparseLevenbergMarquardtSolver::new(sparse_config);
        let mut sparse_workspace =
            SparseLevenbergMarquardtWorkspace::new(&problem, &initial).unwrap();

        group.bench_with_input(BenchmarkId::new("Sparse", n), &n, |b, _| {
            b.iter(|| {
                sparse_workspace.reuse_with(&problem, &initial).unwrap();
                black_box(
                    sparse_solver
                        .solve_problem(&problem, &mut sparse_workspace)
                        .unwrap(),
                )
            });
        });
    }

    group.finish();
}

criterion_group!(
    benches,
    bench_sparse_vs_dense_small,
    bench_sparse_vs_dense_large
);
criterion_main!(benches);
