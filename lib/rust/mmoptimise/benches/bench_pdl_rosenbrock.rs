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

//! Rosenbrock function benchmarks using Powell Dog-Leg solver.
//!
//! The Rosenbrock function is a classic optimization test problem
//! that creates a narrow, curved valley. It's challenging for
//! optimizers because the valley is easy to find but the minimum is
//! difficult to reach.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::powell_dogleg::PowellDogLegWorkspace;
use mmoptimise_rust::solver::test_problems::RosenbrockProblem;
use std::time::Duration;

mod common;
use common::*;

fn bench_rosenbrock_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_rosenbrock_configs");
    group.measurement_time(Duration::from_secs(10));

    let problem = RosenbrockProblem::new();
    let configs = powell_dogleg_configs();
    let starting_points = rosenbrock_starting_points();

    let mut workspace =
        PowellDogLegWorkspace::new(&problem, &starting_points[0].parameters)
            .expect("Failed to create workspace");

    for (config_name, config) in &configs {
        for start_point in &starting_points {
            let bench_id = BenchmarkId::new(*config_name, start_point.name);
            group.bench_with_input(bench_id, start_point, |b, start_point| {
                b.iter(|| {
                    black_box(
                        run_pdl_benchmark_with_workspace(
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
    let mut group = c.benchmark_group("pdl_rosenbrock_variants");
    group.measurement_time(Duration::from_secs(8));

    // Use default Powell Dog-Leg config
    let (_, default_config) = powell_dogleg_configs()[0];
    let starting_points = rosenbrock_starting_points();

    // Test different Rosenbrock parameter values.
    let variants = vec![
        ("Standard_1_100", RosenbrockProblem::new()),
        (
            "Modified_2_50",
            RosenbrockProblem::with_parameters(2.0, 50.0),
        ),
        ("Easy_1_10", RosenbrockProblem::with_parameters(1.0, 10.0)),
        (
            "Hard_0.5_200",
            RosenbrockProblem::with_parameters(0.5, 200.0),
        ),
    ];

    let mut workspace = PowellDogLegWorkspace::new(
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
                        run_pdl_benchmark_with_workspace(
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

fn bench_rosenbrock_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_rosenbrock_starting_points");
    group.measurement_time(Duration::from_secs(8));

    let problem = RosenbrockProblem::new();
    let (_, default_config) = powell_dogleg_configs()[0];

    // Extended set of challenging starting points.
    let challenging_points = vec![
        StartingPoint {
            name: "VeryFar",
            parameters: vec![-5.0, 5.0],
        },
        StartingPoint {
            name: "Saddle",
            parameters: vec![0.0, 1.0],
        },
        StartingPoint {
            name: "Ridge",
            parameters: vec![1.0, 0.0],
        },
        StartingPoint {
            name: "Opposite",
            parameters: vec![-1.0, -1.0],
        },
        StartingPoint {
            name: "Extreme",
            parameters: vec![-10.0, 10.0],
        },
    ];

    let mut workspace =
        PowellDogLegWorkspace::new(&problem, &challenging_points[0].parameters)
            .expect("Failed to create workspace");

    for start_point in &challenging_points {
        let bench_id = BenchmarkId::from_parameter(start_point.name);
        group.bench_with_input(bench_id, start_point, |b, start_point| {
            b.iter(|| {
                black_box(
                    run_pdl_benchmark_with_workspace(
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

/// Benchmark using PowellDogLegWorkspace::new() for each iteration (baseline)
fn bench_rosenbrock_memory_comparison_new(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_rosenbrock_memory_comparison");
    group.measurement_time(Duration::from_secs(10));

    let problem = RosenbrockProblem::new();
    let (_, default_config) = powell_dogleg_configs()[0];
    let starting_points = vec![
        StartingPoint {
            name: "Point1",
            parameters: vec![0.0, 0.0],
        },
        StartingPoint {
            name: "Point2",
            parameters: vec![-1.2, 1.0],
        },
        StartingPoint {
            name: "Point3",
            parameters: vec![2.0, -1.0],
        },
        StartingPoint {
            name: "Point4",
            parameters: vec![-0.5, 2.5],
        },
    ];

    group.bench_function("using_new", |b| {
        b.iter(|| {
            for start_point in &starting_points {
                black_box(
                    run_pdl_benchmark(&problem, default_config, start_point)
                        .unwrap(),
                );
            }
        })
    });

    group.finish();
}

/// Benchmark using PowellDogLegWorkspace::reuse_with() (optimized)
fn bench_rosenbrock_memory_comparison_reuse(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_rosenbrock_memory_comparison");
    group.measurement_time(Duration::from_secs(10));

    let problem = RosenbrockProblem::new();
    let (_, default_config) = powell_dogleg_configs()[0];
    let starting_points = vec![
        StartingPoint {
            name: "Point1",
            parameters: vec![0.0, 0.0],
        },
        StartingPoint {
            name: "Point2",
            parameters: vec![-1.2, 1.0],
        },
        StartingPoint {
            name: "Point3",
            parameters: vec![2.0, -1.0],
        },
        StartingPoint {
            name: "Point4",
            parameters: vec![-0.5, 2.5],
        },
    ];

    group.bench_function("using_reuse_with", |b| {
        let mut workspace = PowellDogLegWorkspace::new(
            &problem,
            &starting_points[0].parameters,
        )
        .expect("Failed to create workspace");

        b.iter(|| {
            for start_point in &starting_points {
                black_box(
                    run_pdl_benchmark_with_workspace(
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
    bench_rosenbrock_starting_points,
    bench_rosenbrock_memory_comparison_new,
    bench_rosenbrock_memory_comparison_reuse
);
criterion_main!(benches);
