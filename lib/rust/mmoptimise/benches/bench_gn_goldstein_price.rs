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

//! Goldstein-Price function benchmarks using Gauss-Newton solver.
//!
//! The Goldstein-Price function is challenging for Gauss-Newton due to
//! its multiple local minima and complex topology. GN needs good starting
//! points to succeed.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::gauss_newton::GaussNewtonWorkspace;
use mmoptimise_rust::solver::test_problems::GoldsteinPriceFunction;
use std::time::Duration;

mod common;
use common::*;

fn bench_goldstein_price_near_minimum(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_goldstein_price_near_minimum");
    group.measurement_time(Duration::from_secs(8));

    let problem = GoldsteinPriceFunction;
    let (_, default_config) = gauss_newton_configs()[0];

    // Start very close to the global minimum for GN to succeed
    let near_minimum_points = vec![
        StartingPoint {
            name: "VeryClose",
            parameters: vec![0.05, -0.95],
        },
        StartingPoint {
            name: "Close",
            parameters: vec![0.1, -0.9],
        },
        StartingPoint {
            name: "Moderate",
            parameters: vec![0.2, -0.8],
        },
    ];

    let mut workspace =
        GaussNewtonWorkspace::new(&problem, &near_minimum_points[0].parameters)
            .expect("Failed to create workspace");

    for start_point in &near_minimum_points {
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

fn bench_goldstein_price_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_goldstein_price_configs");
    group.measurement_time(Duration::from_secs(10));

    let problem = GoldsteinPriceFunction;
    let good_start = StartingPoint {
        name: "Close",
        parameters: vec![0.1, -0.9],
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
    bench_goldstein_price_near_minimum,
    bench_goldstein_price_configs
);
criterion_main!(benches);
