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

//! Curve fitting benchmarks using Gauss-Newton solver
//!
//! Tests the solver on real noisy data. Gauss-Newton should perform
//! well for curve fitting problems since they're typically well-conditioned
//! and have good structure.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::gauss_newton::GaussNewtonWorkspace;
use mmoptimise_rust::solver::test_problems::CurveFittingProblem;
use std::time::Duration;

mod common;
use common::*;

fn bench_curve_fitting_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_curve_fitting_configs");
    // Moderate timeout for curve fitting.
    group.measurement_time(Duration::from_secs(10));

    let problem = CurveFittingProblem::from_example_data();
    // Filter for Gauss-Newton configs only
    let configs = gauss_newton_configs();
    let starting_points = curve_fitting_starting_points();

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

fn bench_curve_fitting_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_curve_fitting_starting_points");
    group.measurement_time(Duration::from_secs(8));

    let problem = CurveFittingProblem::from_example_data();
    let (_, default_config) = gauss_newton_configs()[0];

    // Starting points suitable for Gauss-Newton (not too far from solution)
    let suitable_points = vec![
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0],
        },
        StartingPoint {
            name: "NearTrue",
            parameters: vec![0.25, 0.08],
        },
        StartingPoint {
            name: "Moderate",
            parameters: vec![0.5, -0.1],
        },
        StartingPoint {
            name: "SmallSlope",
            parameters: vec![0.1, 0.1],
        },
        StartingPoint {
            name: "ReasonableGuess",
            parameters: vec![0.3, 0.05],
        },
    ];

    let mut workspace =
        GaussNewtonWorkspace::new(&problem, &suitable_points[0].parameters)
            .expect("Failed to create workspace");

    for start_point in &suitable_points {
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

fn bench_curve_fitting_precision_comparison(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_curve_fitting_precision");
    group.measurement_time(Duration::from_secs(12));

    let problem = CurveFittingProblem::from_example_data();
    let good_start = StartingPoint {
        name: "NearTrue",
        parameters: vec![0.25, 0.08],
    };

    // Compare different precision settings for curve fitting with GN
    let precision_configs = gauss_newton_configs();

    let mut workspace =
        GaussNewtonWorkspace::new(&problem, &good_start.parameters)
            .expect("Failed to create workspace");

    for (config_name, config) in &precision_configs {
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

fn bench_curve_fitting_regularization_study(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_curve_fitting_regularization");
    group.measurement_time(Duration::from_secs(10));

    let problem = CurveFittingProblem::from_example_data();
    let challenging_start = StartingPoint {
        name: "Origin",
        parameters: vec![0.0, 0.0],
    };

    // Test different regularization levels for numerical stability
    let regularization_configs = gauss_newton_configs();

    let mut workspace =
        GaussNewtonWorkspace::new(&problem, &challenging_start.parameters)
            .expect("Failed to create workspace");

    for (config_name, config) in &regularization_configs {
        let bench_id = BenchmarkId::from_parameter(config_name);
        group.bench_with_input(
            bench_id,
            &challenging_start,
            |b, start_point| {
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
            },
        );
    }
    group.finish();
}

criterion_group!(
    benches,
    bench_curve_fitting_configs,
    bench_curve_fitting_starting_points,
    bench_curve_fitting_precision_comparison,
    bench_curve_fitting_regularization_study
);
criterion_main!(benches);
