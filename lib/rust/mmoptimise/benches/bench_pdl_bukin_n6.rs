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

//! Bukin function N.6 benchmarks using Powell Dog-Leg solver.
//!
//! The Bukin function N.6 is an extremely difficult optimization
//! problem with a narrow ridge and multiple local minima. It's
//! one of the most challenging test functions for optimization algorithms.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::powell_dogleg::PowellDogLegWorkspace;
use mmoptimise_rust::solver::test_problems::BukinN6Problem;
use std::time::Duration;

mod common;
use common::*;

fn bench_bukin_n6_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_bukin_n6_configs");
    // Very long timeout for extremely difficult problem.
    group.measurement_time(Duration::from_secs(20));

    let problem = BukinN6Problem;
    // Filter for Powell Dog-Leg configs only.
    let configs = powell_dogleg_configs();
    let starting_points = bukin_n6_starting_points();

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

fn bench_bukin_n6_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_bukin_n6_starting_points");
    group.measurement_time(Duration::from_secs(18));

    let problem = BukinN6Problem;
    let (_, default_config) = powell_dogleg_configs()[0];

    // Extended set of starting points within the valid domain [-15, -5] x [-3, 3]
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
            name: "NearOptimum",
            parameters: vec![-9.8, 0.8],
        },
        StartingPoint {
            name: "FarFromOptimum",
            parameters: vec![-6.0, -2.5],
        },
        StartingPoint {
            name: "OnRidge1",
            parameters: vec![-7.0, 0.49],
        },
        StartingPoint {
            name: "OnRidge2",
            parameters: vec![-11.0, 1.21],
        },
        StartingPoint {
            name: "Valley1",
            parameters: vec![-13.0, 1.69],
        },
        StartingPoint {
            name: "Valley2",
            parameters: vec![-9.0, 0.81],
        },
        StartingPoint {
            name: "Boundary1",
            parameters: vec![-14.9, 2.9],
        },
        StartingPoint {
            name: "Boundary2",
            parameters: vec![-5.1, -2.9],
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

fn bench_bukin_n6_trust_region_stress_test(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_bukin_n6_trust_region_stress");
    group.measurement_time(Duration::from_secs(25));

    let problem = BukinN6Problem;
    // Use a particularly challenging starting point.
    let stress_start = StartingPoint {
        name: "StressTest",
        parameters: vec![-6.0, -2.0],
    };

    // Test all Powell Dog-Leg configurations on this difficult
    // problem.
    let stress_configs = powell_dogleg_configs();

    let mut workspace =
        PowellDogLegWorkspace::new(&problem, &stress_start.parameters)
            .expect("Failed to create workspace");

    for (config_name, config) in &stress_configs {
        let bench_id = BenchmarkId::from_parameter(config_name);
        group.bench_with_input(bench_id, &stress_start, |b, start_point| {
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
    group.finish();
}

fn bench_bukin_n6_convergence_analysis(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_bukin_n6_convergence_analysis");
    group.measurement_time(Duration::from_secs(15));

    let problem = BukinN6Problem;
    let (_, default_config) = powell_dogleg_configs()[0];

    // Test convergence behavior from different regions
    let region_points = vec![
        StartingPoint {
            name: "LeftRegion",
            parameters: vec![-14.0, 1.0],
        },
        StartingPoint {
            name: "CenterRegion",
            parameters: vec![-10.0, 1.0],
        },
        StartingPoint {
            name: "RightRegion",
            parameters: vec![-6.0, 1.0],
        },
        StartingPoint {
            name: "TopRegion",
            parameters: vec![-10.0, 2.5],
        },
        StartingPoint {
            name: "BottomRegion",
            parameters: vec![-10.0, -2.5],
        },
        StartingPoint {
            name: "NearGlobalMin",
            parameters: vec![-10.1, 0.9],
        },
    ];

    let mut workspace =
        PowellDogLegWorkspace::new(&problem, &region_points[0].parameters)
            .expect("Failed to create workspace");

    for start_point in &region_points {
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
    bench_bukin_n6_configs,
    bench_bukin_n6_starting_points,
    bench_bukin_n6_trust_region_stress_test,
    bench_bukin_n6_convergence_analysis
);
criterion_main!(benches);
