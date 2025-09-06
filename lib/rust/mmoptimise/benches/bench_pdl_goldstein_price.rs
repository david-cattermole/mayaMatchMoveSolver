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

//! Goldstein-Price function benchmarks using Powell Dog-Leg solver.
//!
//! The Goldstein-Price function is a challenging optimization test
//! problem with multiple local minima and complex topology. It provides
//! a good test of the solver's robustness.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::powell_dogleg::PowellDogLegWorkspace;
use mmoptimise_rust::solver::test_problems::GoldsteinPriceFunction;
use std::time::Duration;

mod common;
use common::*;

fn bench_goldstein_price_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_goldstein_price_configs");
    // Longer timeout for complex function.
    group.measurement_time(Duration::from_secs(15));

    let problem = GoldsteinPriceFunction;
    // Filter for Powell Dog-Leg configs only
    let configs = powell_dogleg_configs();
    let starting_points = goldstein_price_starting_points();

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

fn bench_goldstein_price_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_goldstein_price_starting_points");
    group.measurement_time(Duration::from_secs(12));

    let problem = GoldsteinPriceFunction;
    let (_, default_config) = powell_dogleg_configs()[0];

    // Extended set of challenging starting points for Goldstein-Price
    let challenging_points = vec![
        StartingPoint {
            name: "NearMinimum",
            parameters: vec![0.1, -0.9],
        },
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0],
        },
        StartingPoint {
            name: "FarPoint",
            parameters: vec![2.0, 2.0],
        },
        StartingPoint {
            name: "Quadrant1",
            parameters: vec![1.5, 1.5],
        },
        StartingPoint {
            name: "Quadrant2",
            parameters: vec![-1.5, 1.5],
        },
        StartingPoint {
            name: "Quadrant3",
            parameters: vec![-1.5, -1.5],
        },
        StartingPoint {
            name: "Quadrant4",
            parameters: vec![1.5, -1.5],
        },
        StartingPoint {
            name: "VeryFar",
            parameters: vec![5.0, -5.0],
        },
        StartingPoint {
            name: "EdgeCase",
            parameters: vec![0.01, -1.01],
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

fn bench_goldstein_price_trust_region_comparison(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_goldstein_price_trust_region");
    group.measurement_time(Duration::from_secs(20));

    let problem = GoldsteinPriceFunction;
    let challenging_start = StartingPoint {
        name: "FarPoint",
        parameters: vec![2.0, 2.0],
    };

    // Test different trust region configurations specific to Powell Dog-Leg
    let trust_region_configs = powell_dogleg_configs();

    let mut workspace =
        PowellDogLegWorkspace::new(&problem, &challenging_start.parameters)
            .expect("Failed to create workspace");

    for (config_name, config) in &trust_region_configs {
        let bench_id = BenchmarkId::from_parameter(config_name);
        group.bench_with_input(
            bench_id,
            &challenging_start,
            |b, start_point| {
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
            },
        );
    }
    group.finish();
}

fn bench_goldstein_price_convergence_analysis(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_goldstein_price_convergence");
    group.measurement_time(Duration::from_secs(10));

    let problem = GoldsteinPriceFunction;
    let (_, default_config) = powell_dogleg_configs()[0];

    // Test convergence from various distances to minimum
    let distance_points = vec![
        StartingPoint {
            name: "VeryClose",
            parameters: vec![0.05, -0.95],
        },
        StartingPoint {
            name: "Close",
            parameters: vec![0.2, -0.8],
        },
        StartingPoint {
            name: "Medium",
            parameters: vec![0.5, -0.5],
        },
        StartingPoint {
            name: "Far",
            parameters: vec![1.0, 0.0],
        },
        StartingPoint {
            name: "VeryFar",
            parameters: vec![2.0, 1.0],
        },
    ];

    let mut workspace =
        PowellDogLegWorkspace::new(&problem, &distance_points[0].parameters)
            .expect("Failed to create workspace");

    for start_point in &distance_points {
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
    bench_goldstein_price_configs,
    bench_goldstein_price_starting_points,
    bench_goldstein_price_trust_region_comparison,
    bench_goldstein_price_convergence_analysis
);
criterion_main!(benches);
