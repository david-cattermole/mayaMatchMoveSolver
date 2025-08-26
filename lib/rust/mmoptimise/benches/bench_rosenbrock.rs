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

//! Rosenbrock function benchmarks.
//!
//! The Rosenbrock function is a classic optimization test problem
//! that creates a narrow, curved valley. It's challenging for
//! optimizers because the valley is easy to find but the minimum is
//! difficult to reach.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use std::time::Duration;

mod common;
use common::*;

fn bench_rosenbrock_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("rosenbrock_configs");
    group.measurement_time(Duration::from_secs(10));

    let problem = RosenbrockProblem::new();
    let configs = BenchmarkConfig::default_configs();
    let starting_points = RosenbrockProblem::starting_points();

    for config in &configs {
        for start_point in &starting_points {
            let bench_id = BenchmarkId::new(config.name, start_point.name);
            group.bench_with_input(bench_id, start_point, |b, start_point| {
                b.iter(|| {
                    black_box(
                        run_benchmark(&problem, config, start_point).unwrap(),
                    )
                });
            });
        }
    }
    group.finish();
}

fn bench_rosenbrock_variants(c: &mut Criterion) {
    let mut group = c.benchmark_group("rosenbrock_variants");
    group.measurement_time(Duration::from_secs(8));

    let default_config = &BenchmarkConfig::default_configs()[0];
    let starting_points = RosenbrockProblem::starting_points();

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

    for (variant_name, problem) in &variants {
        for start_point in &starting_points {
            let bench_id = BenchmarkId::new(*variant_name, start_point.name);
            group.bench_with_input(bench_id, start_point, |b, start_point| {
                b.iter(|| {
                    black_box(
                        run_benchmark(problem, default_config, start_point)
                            .unwrap(),
                    )
                });
            });
        }
    }
    group.finish();
}

fn bench_rosenbrock_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("rosenbrock_starting_points");
    group.measurement_time(Duration::from_secs(8));

    let problem = RosenbrockProblem::new();
    let default_config = &BenchmarkConfig::default_configs()[0];

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

    for start_point in &challenging_points {
        let bench_id = BenchmarkId::from_parameter(start_point.name);
        group.bench_with_input(bench_id, start_point, |b, start_point| {
            b.iter(|| {
                black_box(
                    run_benchmark(&problem, default_config, start_point)
                        .unwrap(),
                )
            });
        });
    }
    group.finish();
}

criterion_group!(
    benches,
    bench_rosenbrock_configs,
    bench_rosenbrock_variants,
    bench_rosenbrock_starting_points
);
criterion_main!(benches);
