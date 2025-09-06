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

//! Rosenbrock function benchmarks using Gauss-Newton solver.
//!
//! The Rosenbrock function is a classic optimization test problem
//! that creates a narrow, curved valley. Gauss-Newton is expected
//! to perform well when starting near the optimum but may struggle
//! from far starting points.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::gauss_newton::GaussNewtonWorkspace;
use mmoptimise_rust::solver::test_problems::RosenbrockProblem;
use std::time::Duration;

mod common;
use common::*;

fn bench_rosenbrock_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_rosenbrock_configs");
    group.measurement_time(Duration::from_secs(10));

    let problem = RosenbrockProblem::new();
    let configs = gauss_newton_configs();
    // Use starting points closer to optimum for GN (it's less robust than LM/PDL)
    let starting_points = vec![
        StartingPoint {
            name: "NearMinimum",
            parameters: vec![0.8, 0.8],
        },
        StartingPoint {
            name: "ModeratelyClose",
            parameters: vec![0.5, 0.5],
        },
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0],
        },
    ];

    let mut workspace =
        GaussNewtonWorkspace::new(&problem, &starting_points[0].parameters)
            .expect("Failed to create workspace");

    for (config_name, config) in &configs {
        for start_point in &starting_points {
            let bench_id = BenchmarkId::new(*config_name, start_point.name);
            group.bench_with_input(bench_id, start_point, |b, start_point| {
                b.iter(|| {
                    black_box(
                        run_gn_benchmark_with_workspace(
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

fn bench_rosenbrock_variants(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_rosenbrock_variants");
    group.measurement_time(Duration::from_secs(8));

    // Use default Gauss-Newton config
    let (_, default_config) = gauss_newton_configs()[0];
    let starting_points = vec![
        StartingPoint {
            name: "NearMinimum",
            parameters: vec![0.8, 0.8],
        },
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0],
        },
    ];

    // Test different Rosenbrock parameter values with easier settings for GN
    let variants = vec![
        ("Easy_1_10", RosenbrockProblem::with_parameters(1.0, 10.0)),
        ("Standard_1_100", RosenbrockProblem::new()),
        (
            "Modified_2_50",
            RosenbrockProblem::with_parameters(2.0, 50.0),
        ),
    ];

    let mut workspace = GaussNewtonWorkspace::new(
        &variants[0].1,
        &starting_points[0].parameters,
    )
    .expect("Failed to create workspace");

    for (variant_name, problem) in &variants {
        for start_point in &starting_points {
            let bench_id = BenchmarkId::new(*variant_name, start_point.name);
            group.bench_with_input(bench_id, start_point, |b, start_point| {
                b.iter(|| {
                    black_box(
                        run_gn_benchmark_with_workspace(
                            problem,
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

fn bench_rosenbrock_convergence_basin(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_rosenbrock_convergence_basin");
    group.measurement_time(Duration::from_secs(8));

    let problem = RosenbrockProblem::new();
    let (_, default_config) = gauss_newton_configs()[0];

    // Test convergence basin - points at increasing distances from optimum
    let basin_points = vec![
        StartingPoint {
            name: "VeryClose",
            parameters: vec![0.95, 0.95],
        },
        StartingPoint {
            name: "Close",
            parameters: vec![0.8, 0.8],
        },
        StartingPoint {
            name: "Moderate",
            parameters: vec![0.6, 0.6],
        },
        StartingPoint {
            name: "Challenging",
            parameters: vec![0.3, 0.3],
        },
        StartingPoint {
            name: "Difficult",
            parameters: vec![0.0, 0.0],
        },
        StartingPoint {
            name: "VeryDifficult",
            parameters: vec![-0.5, 0.5],
        },
    ];

    let mut workspace =
        GaussNewtonWorkspace::new(&problem, &basin_points[0].parameters)
            .expect("Failed to create workspace");

    for start_point in &basin_points {
        let bench_id = BenchmarkId::from_parameter(start_point.name);
        group.bench_with_input(bench_id, start_point, |b, start_point| {
            b.iter(|| {
                black_box(
                    run_gn_benchmark_with_workspace(
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
    group.finish();
}

/// Benchmark using GaussNewtonWorkspace::new() for each iteration (baseline)
fn bench_rosenbrock_memory_comparison_new(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_rosenbrock_memory_comparison");
    group.measurement_time(Duration::from_secs(10));

    let problem = RosenbrockProblem::new();
    let (_, default_config) = gauss_newton_configs()[0];
    let starting_points = vec![
        StartingPoint {
            name: "Point1",
            parameters: vec![0.8, 0.8],
        },
        StartingPoint {
            name: "Point2",
            parameters: vec![0.6, 0.6],
        },
        StartingPoint {
            name: "Point3",
            parameters: vec![0.4, 0.4],
        },
        StartingPoint {
            name: "Point4",
            parameters: vec![0.2, 0.2],
        },
    ];

    group.bench_function("using_new", |b| {
        b.iter(|| {
            for start_point in &starting_points {
                black_box(
                    run_gn_benchmark(&problem, default_config, start_point)
                        .unwrap(),
                );
            }
        })
    });

    group.finish();
}

/// Benchmark using GaussNewtonWorkspace::reuse_with() (optimized)
fn bench_rosenbrock_memory_comparison_reuse(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_rosenbrock_memory_comparison");
    group.measurement_time(Duration::from_secs(10));

    let problem = RosenbrockProblem::new();
    let (_, default_config) = gauss_newton_configs()[0];
    let starting_points = vec![
        StartingPoint {
            name: "Point1",
            parameters: vec![0.8, 0.8],
        },
        StartingPoint {
            name: "Point2",
            parameters: vec![0.6, 0.6],
        },
        StartingPoint {
            name: "Point3",
            parameters: vec![0.4, 0.4],
        },
        StartingPoint {
            name: "Point4",
            parameters: vec![0.2, 0.2],
        },
    ];

    group.bench_function("using_reuse_with", |b| {
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &starting_points[0].parameters)
                .expect("Failed to create workspace");

        b.iter(|| {
            for start_point in &starting_points {
                black_box(
                    run_gn_benchmark_with_workspace(
                        &problem,
                        default_config,
                        start_point,
                        &mut workspace,
                    )
                    .unwrap(),
                );
            }
        })
    });

    group.finish();
}

criterion_group!(
    benches,
    bench_rosenbrock_configs,
    bench_rosenbrock_variants,
    bench_rosenbrock_convergence_basin,
    bench_rosenbrock_memory_comparison_new,
    bench_rosenbrock_memory_comparison_reuse
);
criterion_main!(benches);
