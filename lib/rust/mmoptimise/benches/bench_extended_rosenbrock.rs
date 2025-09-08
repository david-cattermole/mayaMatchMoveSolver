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

//! Extended Rosenbrock function benchmarks across all three solvers.
//!
//! The Extended Rosenbrock function generalizes the classic 2D
//! Rosenbrock to higher dimensions. This tests solver scalability and
//! performance on higher-dimensional optimization problems.

use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};
use mmoptimise_rust::solver::gauss_newton::GaussNewtonWorkspace;
use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtWorkspace;
use mmoptimise_rust::solver::powell_dogleg::PowellDogLegWorkspace;
use mmoptimise_rust::solver::test_problems::ExtendedRosenbrockProblem;
use std::hint::black_box;
use std::time::Duration;

mod common;
use common::*;

fn bench_extended_rosenbrock_solver_comparison(c: &mut Criterion) {
    let mut group = c.benchmark_group("extended_rosenbrock_solver_comparison");
    group.measurement_time(Duration::from_secs(15));

    // Test with 10-dimensional problem.
    let problem = ExtendedRosenbrockProblem::new(10);
    let expected = extended_rosenbrock_expected_solution(10);
    let starting_points = extended_rosenbrock_starting_points(10);

    // Use default configurations for fair comparison.
    let lm_config = levenberg_marquardt_configs()[0].1;
    let gn_config = gauss_newton_configs()[0].1;
    let pdl_config = powell_dogleg_configs()[0].1;

    // Create workspaces for each solver.
    let mut lm_workspace = LevenbergMarquardtWorkspace::new(
        &problem,
        &starting_points[0].parameters,
    )
    .expect("Failed to create LM workspace.");

    let mut gn_workspace =
        GaussNewtonWorkspace::new(&problem, &starting_points[0].parameters)
            .expect("Failed to create GN workspace.");

    let mut pdl_workspace =
        PowellDogLegWorkspace::new(&problem, &starting_points[0].parameters)
            .expect("Failed to create PDL workspace.");

    for start_point in &starting_points {
        let bench_id = BenchmarkId::new("LevenbergMarquardt", start_point.name);
        group.bench_with_input(bench_id, start_point, |b, start_point| {
            b.iter(|| {
                black_box(
                    run_lm_benchmark(
                        &problem,
                        &expected,
                        lm_config,
                        start_point,
                        &mut lm_workspace,
                    )
                    .unwrap(),
                )
            });
        });

        let bench_id = BenchmarkId::new("GaussNewton", start_point.name);
        group.bench_with_input(bench_id, start_point, |b, start_point| {
            b.iter(|| {
                black_box(
                    run_gn_benchmark(
                        &problem,
                        &expected,
                        gn_config,
                        start_point,
                        &mut gn_workspace,
                    )
                    .unwrap(),
                )
            });
        });

        let bench_id = BenchmarkId::new("PowellDogLeg", start_point.name);
        group.bench_with_input(bench_id, start_point, |b, start_point| {
            b.iter(|| {
                black_box(
                    run_pdl_benchmark(
                        &problem,
                        &expected,
                        pdl_config,
                        start_point,
                        &mut pdl_workspace,
                    )
                    .unwrap(),
                )
            });
        });
    }
    group.finish();
}

criterion_group!(benches, bench_extended_rosenbrock_solver_comparison);
criterion_main!(benches);
