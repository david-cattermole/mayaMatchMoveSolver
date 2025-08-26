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

//! Goldstein-Price function benchmarks
//!
//! This function has many local minima and is challenging because
//! different starting points can lead to different local optima.
//! Tests the solver's ability to handle complex landscapes.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::SolverConfig;
use std::time::Duration;

mod common;
use common::*;

fn bench_goldstein_price_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("goldstein_price_configs");
    group.measurement_time(Duration::from_secs(12));

    let problem = GoldsteinPriceFunction;
    let configs = BenchmarkConfig::default_configs();
    let starting_points = GoldsteinPriceFunction::starting_points();

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

fn bench_goldstein_price_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("goldstein_price_starting_points");
    group.measurement_time(Duration::from_secs(10));

    let problem = GoldsteinPriceFunction;
    let default_config = &BenchmarkConfig::default_configs()[0];

    // Extended set of starting points to test local minima convergence
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
            parameters: vec![1.0, 1.0],
        },
        StartingPoint {
            name: "Quadrant2",
            parameters: vec![-1.0, 1.0],
        },
        StartingPoint {
            name: "Quadrant3",
            parameters: vec![-1.0, -1.0],
        },
        StartingPoint {
            name: "Quadrant4",
            parameters: vec![1.0, -1.0],
        },
        StartingPoint {
            name: "VeryFar",
            parameters: vec![5.0, -5.0],
        },
        StartingPoint {
            name: "Asymmetric",
            parameters: vec![0.5, -1.5],
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

fn bench_goldstein_price_local_minima(c: &mut Criterion) {
    let mut group = c.benchmark_group("goldstein_price_local_minima");
    group.measurement_time(Duration::from_secs(15));

    let problem = GoldsteinPriceFunction;

    // Test how different configs handle the multiple local minima
    let minima_configs = vec![
        BenchmarkConfig::default_configs()[0].clone(), // Default
        BenchmarkConfig::default_configs()[1].clone(), // HighPrecision
        BenchmarkConfig::default_configs()[2].clone(), // FastConvergence
        BenchmarkConfig::default_configs()[5].clone(), // SmallTrustRegion
    ];

    // Starting point that's equidistant from multiple local minima
    let central_start = StartingPoint {
        name: "Central",
        parameters: vec![0.5, -0.5],
    };

    for config in &minima_configs {
        let bench_id = BenchmarkId::from_parameter(config.name);
        group.bench_with_input(bench_id, &central_start, |b, start_point| {
            b.iter(|| {
                black_box(run_benchmark(&problem, config, start_point).unwrap())
            });
        });
    }
    group.finish();
}

fn bench_goldstein_price_convergence_study(c: &mut Criterion) {
    let mut group = c.benchmark_group("goldstein_price_convergence");
    group.measurement_time(Duration::from_secs(10));

    let problem = GoldsteinPriceFunction;
    let challenging_start = StartingPoint {
        name: "FarPoint",
        parameters: vec![2.0, 2.0],
    };

    // Test different iteration limits to study convergence behavior
    let convergence_configs = vec![
        BenchmarkConfig {
            name: "QuickStop",
            config: SolverConfig {
                max_iterations: 50,
                ..Default::default()
            },
        },
        BenchmarkConfig {
            name: "MediumStop",
            config: SolverConfig {
                max_iterations: 200,
                ..Default::default()
            },
        },
        BenchmarkConfig {
            name: "ExtendedStop",
            config: SolverConfig {
                max_iterations: 500,
                ..Default::default()
            },
        },
        BenchmarkConfig {
            name: "UnlimitedStop",
            config: SolverConfig {
                max_iterations: 1000,
                max_function_evaluations: 10000,
                ..Default::default()
            },
        },
    ];

    for config in &convergence_configs {
        let bench_id = BenchmarkId::from_parameter(config.name);
        group.bench_with_input(
            bench_id,
            &challenging_start,
            |b, start_point| {
                b.iter(|| {
                    black_box(
                        run_benchmark(&problem, config, start_point).unwrap(),
                    )
                });
            },
        );
    }
    group.finish();
}

criterion_group!(
    benches,
    bench_goldstein_price_configs,
    bench_goldstein_price_starting_points,
    bench_goldstein_price_local_minima,
    bench_goldstein_price_convergence_study
);
criterion_main!(benches);
