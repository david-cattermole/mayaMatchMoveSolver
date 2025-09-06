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

//! Extended Rosenbrock function benchmarks
//!
//! Tests scalability of the solver with higher dimensional versions
//! of the Rosenbrock function. These tests are important for
//! understanding how the solver performance degrades with problem
//! size.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtWorkspace;
use mmoptimise_rust::solver::test_problems::ExtendedRosenbrockProblem;
use std::time::Duration;

mod common;
use common::*;

fn bench_extended_rosenbrock_dimensions(c: &mut Criterion) {
    let mut group = c.benchmark_group("extended_rosenbrock_dimensions");
    // Longer for higher dimensions.
    group.measurement_time(Duration::from_secs(15));

    let (_, default_config) = levenberg_marquardt_configs()[0];
    let dimensions = vec![4, 8, 16, 32];

    for n in dimensions {
        let problem = ExtendedRosenbrockProblem::new(n);
        let starting_points = extended_rosenbrock_starting_points(n);

        let mut workspace = LevenbergMarquardtWorkspace::new(
            &problem,
            &starting_points[0].parameters,
        )
        .expect("Failed to create workspace");

        for start_point in &starting_points {
            let bench_id =
                BenchmarkId::new(format!("dim_{}", n), start_point.name);
            group.bench_with_input(bench_id, start_point, |b, start_point| {
                b.iter(|| {
                    black_box(
                        run_lm_benchmark_with_workspace(
                            &problem,
                            default_config,
                            start_point,
                            &mut workspace,
                        )
                        .unwrap(),
                    )
                });
            });
        }
    }
    group.finish();
}

fn bench_extended_rosenbrock_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("extended_rosenbrock_configs");
    group.measurement_time(Duration::from_secs(12));

    let problem = ExtendedRosenbrockProblem::new(8); // 8D problem.
    let configs = levenberg_marquardt_configs();
    let starting_points = extended_rosenbrock_starting_points(8);

    let mut workspace = LevenbergMarquardtWorkspace::new(
        &problem,
        &starting_points[0].parameters,
    )
    .expect("Failed to create workspace");

    for (config_name, config) in &configs {
        for start_point in &starting_points {
            let bench_id = BenchmarkId::new(*config_name, start_point.name);
            group.bench_with_input(bench_id, start_point, |b, start_point| {
                b.iter(|| {
                    black_box(
                        run_lm_benchmark_with_workspace(
                            &problem,
                            *config,
                            start_point,
                            &mut workspace,
                        )
                        .unwrap(),
                    )
                });
            });
        }
    }
    group.finish();
}

fn bench_extended_rosenbrock_scalability(c: &mut Criterion) {
    let mut group = c.benchmark_group("extended_rosenbrock_scalability");
    // Even longer for scalability tests.
    group.measurement_time(Duration::from_secs(20));

    // FastConvergence for scalability.
    let (_, fast_config) = levenberg_marquardt_configs()[2];

    // Test how execution time scales with problem size.
    let dimensions = vec![4, 8, 16, 32, 64];
    let standard_start = StartingPoint {
        name: "Alternating",
        parameters: vec![], // Will be filled for each dimension.
    };

    for n in dimensions {
        let problem = ExtendedRosenbrockProblem::new(n);
        let start_point = StartingPoint {
            name: standard_start.name,
            parameters: (0..n)
                .map(|i| if i % 2 == 0 { -1.2 } else { 1.0 })
                .collect(),
        };

        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &start_point.parameters)
                .expect("Failed to create workspace");

        let bench_id = BenchmarkId::from_parameter(format!("{}D", n));
        group.bench_with_input(bench_id, &start_point, |b, start_point| {
            b.iter(|| {
                black_box(
                    run_lm_benchmark_with_workspace(
                        &problem,
                        fast_config,
                        start_point,
                        &mut workspace,
                    )
                    .unwrap(),
                )
            });
        });
    }
    group.finish();
}

criterion_group!(
    benches,
    bench_extended_rosenbrock_dimensions,
    bench_extended_rosenbrock_configs,
    bench_extended_rosenbrock_scalability
);
criterion_main!(benches);
