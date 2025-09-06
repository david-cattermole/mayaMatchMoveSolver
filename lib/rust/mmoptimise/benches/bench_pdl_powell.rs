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

//! Powell function benchmarks using Powell Dog-Leg solver.
//!
//! Powell's function is a classic optimization test problem that is
//! particularly challenging due to its ill-conditioning and near-singular
//! behavior. It's a good test of solver robustness.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::powell_dogleg::PowellDogLegWorkspace;
use mmoptimise_rust::solver::test_problems::PowellProblem;
use std::time::Duration;

mod common;
use common::*;

fn bench_powell_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_powell_configs");
    // Longer timeout for ill-conditioned problem.
    group.measurement_time(Duration::from_secs(15));

    let problem = PowellProblem;
    // Filter for Powell Dog-Leg configs only
    let configs = powell_dogleg_configs();
    let starting_points = powell_starting_points();

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

fn bench_powell_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_powell_starting_points");
    group.measurement_time(Duration::from_secs(12));

    let problem = PowellProblem;
    let (_, default_config) = powell_dogleg_configs()[0];

    // Extended set of challenging starting points for Powell function
    let challenging_points = vec![
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0, 0.0, 0.0],
        },
        StartingPoint {
            name: "StandardStart",
            parameters: vec![3.0, -1.0, 0.0, 1.0],
        },
        StartingPoint {
            name: "FarPoint",
            parameters: vec![5.0, -5.0, 3.0, -3.0],
        },
        StartingPoint {
            name: "AllPositive",
            parameters: vec![2.0, 2.0, 2.0, 2.0],
        },
        StartingPoint {
            name: "AllNegative",
            parameters: vec![-2.0, -2.0, -2.0, -2.0],
        },
        StartingPoint {
            name: "Alternating",
            parameters: vec![1.0, -1.0, 1.0, -1.0],
        },
        StartingPoint {
            name: "LargeValues",
            parameters: vec![10.0, -10.0, 5.0, -5.0],
        },
        StartingPoint {
            name: "SmallNonzero",
            parameters: vec![0.1, -0.1, 0.05, 0.05],
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

fn bench_powell_trust_region_analysis(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_powell_trust_region_analysis");
    group.measurement_time(Duration::from_secs(20));

    let problem = PowellProblem;
    let challenging_start = StartingPoint {
        name: "StandardStart",
        parameters: vec![3.0, -1.0, 0.0, 1.0],
    };

    // Test different trust region configurations for Powell function
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

fn bench_powell_convergence_robustness(c: &mut Criterion) {
    let mut group = c.benchmark_group("pdl_powell_convergence_robustness");
    group.measurement_time(Duration::from_secs(15));

    let problem = PowellProblem;
    let (_, default_config) = powell_dogleg_configs()[0];

    // Test robustness with various levels of ill-conditioning
    let robustness_points = vec![
        StartingPoint {
            name: "WellConditioned",
            parameters: vec![0.1, -0.1, 0.1, -0.1],
        },
        StartingPoint {
            name: "ModeratelyIllConditioned",
            parameters: vec![1.0, -1.0, 0.5, -0.5],
        },
        StartingPoint {
            name: "IllConditioned",
            parameters: vec![3.0, -1.0, 0.0, 1.0],
        },
        StartingPoint {
            name: "VeryIllConditioned",
            parameters: vec![5.0, -5.0, 3.0, -3.0],
        },
        StartingPoint {
            name: "ExtremelyIllConditioned",
            parameters: vec![10.0, -10.0, 8.0, -8.0],
        },
    ];

    let mut workspace =
        PowellDogLegWorkspace::new(&problem, &robustness_points[0].parameters)
            .expect("Failed to create workspace");

    for start_point in &robustness_points {
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
    bench_powell_configs,
    bench_powell_starting_points,
    bench_powell_trust_region_analysis,
    bench_powell_convergence_robustness
);
criterion_main!(benches);
