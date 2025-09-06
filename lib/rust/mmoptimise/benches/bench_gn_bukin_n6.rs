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

//! Bukin function N.6 benchmarks using Gauss-Newton solver.
//!
//! The Bukin function N.6 is extremely difficult for Gauss-Newton
//! due to its narrow ridge and discontinuous derivatives. This benchmark
//! primarily tests the limits of GN's applicability.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::gauss_newton::GaussNewtonWorkspace;
use mmoptimise_rust::solver::test_problems::BukinN6Problem;
use std::time::Duration;

mod common;
use common::*;

fn bench_bukin_n6_very_close_to_minimum(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_bukin_n6_very_close_minimum");
    // Short timeout since GN likely won't succeed on this problem
    group.measurement_time(Duration::from_secs(5));

    let problem = BukinN6Problem;
    let (_, default_config) = gauss_newton_configs()[0];

    // Start extremely close to the global minimum (only hope for GN)
    let very_close_points = vec![
        StartingPoint {
            name: "ExtremelClose",
            parameters: vec![-9.99, 0.99],
        },
        StartingPoint {
            name: "VeryClose1",
            parameters: vec![-10.01, 1.01],
        },
        StartingPoint {
            name: "VeryClose2",
            parameters: vec![-9.98, 0.98],
        },
    ];

    let mut workspace =
        GaussNewtonWorkspace::new(&problem, &very_close_points[0].parameters)
            .expect("Failed to create workspace");

    for start_point in &very_close_points {
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

fn bench_bukin_n6_failure_analysis(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_bukin_n6_failure_analysis");
    // Very short timeout to analyze failure modes
    group.measurement_time(Duration::from_secs(3));

    let problem = BukinN6Problem;
    let (_, default_config) = gauss_newton_configs()[0];

    // Test various failure modes for educational purposes
    let failure_points = vec![
        StartingPoint {
            name: "ModerateDistance",
            parameters: vec![-9.5, 0.5],
        },
        StartingPoint {
            name: "ValidDomain",
            parameters: vec![-8.0, 0.5],
        },
        StartingPoint {
            name: "EdgeCase",
            parameters: vec![-5.0, 0.0],
        },
    ];

    let mut workspace =
        GaussNewtonWorkspace::new(&problem, &failure_points[0].parameters)
            .expect("Failed to create workspace");

    for start_point in &failure_points {
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

criterion_group!(
    benches,
    bench_bukin_n6_very_close_to_minimum,
    bench_bukin_n6_failure_analysis
);
criterion_main!(benches);
