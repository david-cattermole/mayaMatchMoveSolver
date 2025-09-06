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

//! Powell function benchmarks using Gauss-Newton solver.
//!
//! Powell's function is challenging for Gauss-Newton due to its
//! ill-conditioning. GN needs good starting points and may benefit
//! from regularization to handle numerical issues.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::solver::gauss_newton::GaussNewtonWorkspace;
use mmoptimise_rust::solver::test_problems::PowellProblem;
use std::time::Duration;

mod common;
use common::*;

fn bench_powell_well_conditioned_starts(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_powell_well_conditioned_starts");
    group.measurement_time(Duration::from_secs(10));

    let problem = PowellProblem;
    let (_, default_config) = gauss_newton_configs()[0];

    // Use starting points that are better conditioned for GN
    let well_conditioned_points = vec![
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0, 0.0, 0.0],
        },
        StartingPoint {
            name: "SmallNonzero",
            parameters: vec![0.1, -0.1, 0.05, 0.05],
        },
        StartingPoint {
            name: "Moderate",
            parameters: vec![0.5, -0.5, 0.2, -0.2],
        },
        StartingPoint {
            name: "Conservative",
            parameters: vec![1.0, -1.0, 0.5, -0.5],
        },
    ];

    let mut workspace = GaussNewtonWorkspace::new(
        &problem,
        &well_conditioned_points[0].parameters,
    )
    .expect("Failed to create workspace");

    for start_point in &well_conditioned_points {
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

fn bench_powell_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("gn_powell_configs");
    group.measurement_time(Duration::from_secs(10));

    let problem = PowellProblem;
    let good_start = StartingPoint {
        name: "SmallNonzero",
        parameters: vec![0.1, -0.1, 0.05, 0.05],
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
    bench_powell_well_conditioned_starts,
    bench_powell_configs
);
criterion_main!(benches);
