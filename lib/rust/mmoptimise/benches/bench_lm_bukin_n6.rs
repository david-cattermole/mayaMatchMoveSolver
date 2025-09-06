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

//! Bukin N.6 function benchmarks
//!
//! This is an extremely difficult optimization problem with a very
//! narrow valley. It's one of the most challenging test functions
//! and often causes solvers to fail.  Success on this function
//! indicates a very robust solver.

use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};
use mmoptimise_rust::solver::common::ParameterScalingMode;
use mmoptimise_rust::solver::levenberg_marquardt::{
    LevenbergMarquardtConfig, LevenbergMarquardtWorkspace,
};
use mmoptimise_rust::solver::test_problems::BukinN6Problem;
use std::hint::black_box;
use std::time::Duration;

mod common;
use common::*;

fn bench_bukin_n6_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("bukin_n6_configs");
    group.measurement_time(Duration::from_secs(20)); // Much longer for this difficult problem.

    let problem = BukinN6Problem;

    // Only test most relevant configs for this extremely difficult problem.
    let configs = vec![
        levenberg_marquardt_configs()[0], // Default.
        levenberg_marquardt_configs()[1], // HighPrecision.
        levenberg_marquardt_configs()[3], // SmallTrustRegion.
    ];
    let starting_points = bukin_n6_starting_points();

    let mut workspace = LevenbergMarquardtWorkspace::new(
        &problem,
        &starting_points[0].parameters,
    )
    .expect("Failed to create workspace");

    for (config_name, config) in &configs {
        for start_point in &starting_points {
            let bench_id = BenchmarkId::new(*config_name, start_point.name);
            group.bench_with_input(bench_id, start_point, |b, start_point| {
                b.iter(|| {
                    // Use unwrap_or to handle potential solver failures gracefully.
                    black_box(
                        run_lm_benchmark_with_workspace(
                            &problem,
                            *config,
                            start_point,
                            &mut workspace,
                        )
                        .unwrap_or((
                            Duration::from_millis(0),
                            false,
                            0,
                            0,
                            f64::INFINITY,
                        )),
                    )
                });
            });
        }
    }
    group.finish();
}

fn bench_bukin_n6_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("bukin_n6_starting_points");
    group.measurement_time(Duration::from_secs(15));

    let problem = BukinN6Problem;
    // Use high precision for this difficult problem.
    let high_precision_config = &levenberg_marquardt_configs()[1].1;

    // Extended set of starting points within the valid domain.
    let challenging_points = vec![
        StartingPoint {
            name: "ValidDomain1",
            parameters: vec![-8.0, 0.5],
        },
        StartingPoint {
            name: "ValidDomain2",
            parameters: vec![-12.0, 2.0],
        },
        StartingPoint {
            name: "EdgeCase",
            parameters: vec![-5.0, 0.0],
        },
        StartingPoint {
            name: "NearGlobal",
            parameters: vec![-9.5, 0.9],
        },
        StartingPoint {
            name: "FarFromGlobal",
            parameters: vec![-6.0, 2.5],
        },
        StartingPoint {
            name: "Boundary",
            parameters: vec![-15.0, -3.0],
        },
        StartingPoint {
            name: "Center",
            parameters: vec![-10.0, 0.0],
        },
    ];

    let mut workspace = LevenbergMarquardtWorkspace::new(
        &problem,
        &challenging_points[0].parameters,
    )
    .expect("Failed to create workspace");

    for start_point in &challenging_points {
        let bench_id = BenchmarkId::from_parameter(start_point.name);
        group.bench_with_input(bench_id, start_point, |b, start_point| {
            b.iter(|| {
                black_box(
                    run_lm_benchmark_with_workspace(
                        &problem,
                        *high_precision_config,
                        start_point,
                        &mut workspace,
                    )
                    .unwrap_or((
                        Duration::from_millis(0),
                        false,
                        0,
                        0,
                        f64::INFINITY,
                    )),
                )
            });
        });
    }
    group.finish();
}

fn bench_bukin_n6_robustness(c: &mut Criterion) {
    let mut group = c.benchmark_group("bukin_n6_robustness");
    // Longest time for robustness testing.
    group.measurement_time(Duration::from_secs(25));

    let problem = BukinN6Problem;
    let standard_start = StartingPoint {
        name: "ValidDomain1",
        parameters: vec![-8.0, 0.5],
    };

    // Test different solver strategies for this extremely difficult
    // problem.
    let configs = levenberg_marquardt_configs();

    let mut workspace =
        LevenbergMarquardtWorkspace::new(&problem, &standard_start.parameters)
            .expect("Failed to create workspace");

    for (config_name, config) in &configs {
        let bench_id = BenchmarkId::from_parameter(config_name);
        group.bench_with_input(bench_id, &standard_start, |b, start_point| {
            b.iter(|| {
                black_box(
                    run_lm_benchmark_with_workspace(
                        &problem,
                        *config,
                        start_point,
                        &mut workspace,
                    )
                    .unwrap_or((
                        Duration::from_millis(0),
                        false,
                        0,
                        0,
                        f64::INFINITY,
                    )),
                )
            });
        });
    }
    group.finish();
}

criterion_group!(
    benches,
    bench_bukin_n6_configs,
    bench_bukin_n6_starting_points,
    bench_bukin_n6_robustness
);
criterion_main!(benches);
