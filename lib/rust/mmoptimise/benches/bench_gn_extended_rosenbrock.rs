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

//! Extended Rosenbrock function benchmarks using Gauss-Newton solver.
//!
//! Tests the Gauss-Newton solver on higher-dimensional versions of the
//! classic Rosenbrock function. GN may struggle with larger dimensions
//! due to its lack of regularization.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::gauss_newton::GaussNewtonWorkspace;
use mmoptimise_rust::solver::test_problems::ExtendedRosenbrockProblem;
use std::time::Duration;

mod common;
use common::*;

fn bench_extended_rosenbrock_small_dimensions(c: &mut Criterion) {
    let mut group =
        c.benchmark_group("gn_extended_rosenbrock_small_dimensions");
    // Conservative timeout for GN on higher dimensions
    group.measurement_time(Duration::from_secs(10));

    let (_, default_config) = gauss_newton_configs()[0];

    // Use smaller dimensions for GN since it's less robust
    let dimensions = vec![4, 6, 8];

    for n in dimensions {
        let problem = ExtendedRosenbrockProblem::new(n);
        // Use good starting points for GN
        let good_starts = vec![
            StartingPoint {
                name: "NearOptimal",
                parameters: (0..n)
                    .map(|i| if i % 2 == 0 { 0.8 } else { 0.6 })
                    .collect(),
            },
            StartingPoint {
                name: "Origin",
                parameters: vec![0.0; n],
            },
        ];

        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &good_starts[0].parameters)
                .expect("Failed to create workspace");

        for start_point in &good_starts {
            let bench_id =
                BenchmarkId::new(format!("N{}", n), start_point.name);
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
    }
    group.finish();
}

fn bench_extended_rosenbrock_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_extended_rosenbrock_configs");
    group.measurement_time(Duration::from_secs(8));

    // Use a small dimension for config comparison
    let problem = ExtendedRosenbrockProblem::new(4);
    let good_start = StartingPoint {
        name: "NearOptimal",
        parameters: vec![0.8, 0.6, 0.8, 0.6],
    };

    // Filter for Gauss-Newton configs only
    let configs = gauss_newton_configs();

    let mut workspace =
        GaussNewtonWorkspace::new(&problem, &good_start.parameters)
            .expect("Failed to create workspace");

    for (config_name, config) in &configs {
        let bench_id = BenchmarkId::from_parameter(config_name);
        group.bench_with_input(bench_id, &good_start, |b, start_point| {
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
    group.finish();
}

criterion_group!(
    benches,
    bench_extended_rosenbrock_small_dimensions,
    bench_extended_rosenbrock_configs
);
criterion_main!(benches);
