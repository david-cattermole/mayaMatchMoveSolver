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

//! Powell's function benchmarks
//!
//! Powell's function is a classic test problem that's challenging
//! because it has very different scaling in different directions and
//! includes both quadratic and quartic terms.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use std::time::Duration;

mod common;
use common::*;

fn bench_powell_configs(c: &mut Criterion) {
    let mut group = c.benchmark_group("powell_configs");
    group.measurement_time(Duration::from_secs(10));

    let problem = PowellProblem;
    let configs = BenchmarkConfig::default_configs();
    let starting_points = PowellProblem::starting_points();

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

fn bench_powell_starting_points(c: &mut Criterion) {
    let mut group = c.benchmark_group("powell_starting_points");
    group.measurement_time(Duration::from_secs(8));

    let problem = PowellProblem;
    let default_config = &BenchmarkConfig::default_configs()[0];

    // Extended set of challenging starting points for Powell's
    // function.
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
            name: "Symmetric",
            parameters: vec![1.0, 1.0, 1.0, 1.0],
        },
        StartingPoint {
            name: "Antisymmetric",
            parameters: vec![1.0, -1.0, 1.0, -1.0],
        },
        StartingPoint {
            name: "Large",
            parameters: vec![10.0, -10.0, 5.0, -5.0],
        },
        StartingPoint {
            name: "Mixed",
            parameters: vec![2.5, -0.5, 1.5, 0.5],
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

fn bench_powell_scaling_modes(c: &mut Criterion) {
    let mut group = c.benchmark_group("powell_scaling_modes");
    group.measurement_time(Duration::from_secs(8));

    let problem = PowellProblem;
    let challenging_start = StartingPoint {
        name: "FarPoint",
        parameters: vec![5.0, -5.0, 3.0, -3.0],
    };

    // Test different scaling modes - Powell's function benefits from
    // scaling.
    let scaling_configs = vec![
        BenchmarkConfig::default_configs()[0].clone(), // Default (Auto).
        BenchmarkConfig::default_configs()[3].clone(), // NoScaling.
        BenchmarkConfig::default_configs()[4].clone(), // ManualScaling.
    ];

    for config in &scaling_configs {
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
    bench_powell_configs,
    bench_powell_starting_points,
    bench_powell_scaling_modes
);
criterion_main!(benches);
