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

//! Extended Rosenbrock function benchmarks using Powell Dog-Leg solver.
//!
//! Tests the Powell Dog-Leg solver on higher-dimensional versions of the
//! classic Rosenbrock function. This stresses the solver's ability to
//! handle larger parameter spaces.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::powell_dogleg::PowellDogLegWorkspace;
use mmoptimise_rust::solver::test_problems::ExtendedRosenbrockProblem;
use std::time::Duration;

mod common;
use common::*;

fn bench_extended_rosenbrock_data_sizes(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_extended_rosenbrock_data_sizes");
    // Longer timeout for higher-dimensional problems.
    group.measurement_time(Duration::from_secs(15));

    let (_, default_config) = powell_dogleg_configs()[0];

    let dimensions = vec![4, 6, 8, 10, 12];

    for n in dimensions {
        let problem = ExtendedRosenbrockProblem::new(n);
        let starting_points = extended_rosenbrock_starting_points(n);

        let mut workspace = PowellDogLegWorkspace::new(
            &problem,
            &starting_points[0].parameters,
        )
        .expect("Failed to create workspace");

        for start_point in &starting_points {
            let bench_id =
                BenchmarkId::new(format!("N{}", n), start_point.name);
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
    }
    group.finish();
}

fn bench_extended_rosenbrock_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_extended_rosenbrock_configs");
    group.measurement_time(Duration::from_secs(12));

    // Use a moderate dimension for config comparison
    let problem = ExtendedRosenbrockProblem::new(6);
    let starting_points = extended_rosenbrock_starting_points(6);

    // Filter for Powell Dog-Leg configs only
    let configs = powell_dogleg_configs();

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

fn bench_extended_rosenbrock_challenging_starts(c: &mut Criterion) {
    let mut group =
        c.benchmark_group("pdl_extended_rosenbrock_challenging_starts");
    group.measurement_time(Duration::from_secs(10));

    let n = 8; // Fixed dimension for starting point comparison
    let problem = ExtendedRosenbrockProblem::new(n);
    let (_, default_config) = powell_dogleg_configs()[0];

    // Additional challenging starting points
    let challenging_points = vec![
        StartingPoint {
            name: "AllZeros",
            parameters: vec![0.0; n],
        },
        StartingPoint {
            name: "AllOnes",
            parameters: vec![1.0; n],
        },
        StartingPoint {
            name: "LargeValues",
            parameters: vec![5.0; n],
        },
        StartingPoint {
            name: "NegativeValues",
            parameters: vec![-2.0; n],
        },
        StartingPoint {
            name: "Mixed",
            parameters: (0..n)
                .map(|i| if i % 2 == 0 { -1.0 } else { 2.0 })
                .collect(),
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

criterion_group!(
    benches,
    bench_extended_rosenbrock_data_sizes,
    bench_extended_rosenbrock_configs,
    bench_extended_rosenbrock_challenging_starts
);
criterion_main!(benches);
