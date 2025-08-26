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

//! Curve fitting benchmarks
//!
//! Tests the solver on real noisy data. This represents practical
//! curve fitting scenarios that users would encounter in real
//! applications.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use std::time::Duration;

mod common;
use common::*;

fn bench_curve_fitting_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("curve_fitting_configs");
    // Longer for noisy data.
    group.measurement_time(Duration::from_secs(12));

    let problem = CurveFittingProblem::example_data1();
    let configs = BenchmarkConfig::default_configs();
    let starting_points = CurveFittingProblem::starting_points();

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

fn bench_curve_fitting_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("curve_fitting_starting_points");
    group.measurement_time(Duration::from_secs(10));

    let problem = CurveFittingProblem::example_data1();
    let default_config = &BenchmarkConfig::default_configs()[0];

    // Extended set of starting points for curve fitting
    let challenging_points = vec![
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0],
        },
        StartingPoint {
            name: "NearTrue",
            parameters: vec![0.25, 0.08],
        },
        StartingPoint {
            name: "FarFromTrue",
            parameters: vec![1.0, -0.5],
        },
        StartingPoint {
            name: "Negative",
            parameters: vec![-0.5, -0.2],
        },
        StartingPoint {
            name: "Large",
            parameters: vec![2.0, 1.0],
        },
        StartingPoint {
            name: "VeryFar",
            parameters: vec![5.0, -2.0],
        },
        StartingPoint {
            name: "SmallSlope",
            parameters: vec![0.01, 0.1],
        },
        StartingPoint {
            name: "SteepSlope",
            parameters: vec![1.5, 0.05],
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

fn bench_curve_fitting_precision_comparison(c: &mut Criterion) {
    let mut group = c.benchmark_group("curve_fitting_precision");
    group.measurement_time(Duration::from_secs(15));

    let problem = CurveFittingProblem::example_data1();
    let challenging_start = StartingPoint {
        name: "FarFromTrue",
        parameters: vec![1.0, -0.5],
    };

    // Compare different precision settings for noisy data.
    let precision_configs = vec![
        BenchmarkConfig::default_configs()[2].clone(), // FastConvergence.
        BenchmarkConfig::default_configs()[0].clone(), // Default.
        BenchmarkConfig::default_configs()[1].clone(), // HighPrecision.
    ];

    for config in &precision_configs {
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
    bench_curve_fitting_configs,
    bench_curve_fitting_starting_points,
    bench_curve_fitting_precision_comparison
);
criterion_main!(benches);
