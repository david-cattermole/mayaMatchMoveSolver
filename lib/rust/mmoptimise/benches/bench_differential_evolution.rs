//
// Copyright (C) 2025, 2026 David Cattermole.
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

//! Differential Evolution benchmarks across multiple challenging
//! test problems.
//!
//! This benchmark suite tests DE performance on globally difficult
//! optimization landscapes that are poorly suited for gradient-based
//! methods.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmoptimise_rust::global::{
    DifferentialEvolution, DifferentialEvolutionConfig,
    DifferentialEvolutionStrategy, LeastSquaresEvaluator,
};
use mmoptimise_rust::solver::test_problems::{
    BukinN6Problem, GoldsteinPriceFunction, PowellProblem, RosenbrockProblem,
};
use std::time::Duration;

/// Benchmark configuration presets
struct DEBenchConfig {
    name: &'static str,
    strategy: DifferentialEvolutionStrategy,
    scaling_factor: f64,
    crossover_rate: f64,
    population_multiplier: usize,
    generations: usize,
}

fn de_bench_configs() -> Vec<DEBenchConfig> {
    vec![
        DEBenchConfig {
            name: "LargeRefinement",
            strategy: DifferentialEvolutionStrategy::Rand1Bin,
            scaling_factor: 0.8,
            crossover_rate: 0.9,
            population_multiplier: 20,
            generations: 500,
        },
        DEBenchConfig {
            name: "SmallRefinement",
            strategy: DifferentialEvolutionStrategy::Best1Bin,
            scaling_factor: 0.3,
            crossover_rate: 0.2,
            population_multiplier: 10,
            generations: 300,
        },
    ]
}

fn bench_de_rosenbrock(c: &mut Criterion) {
    let mut group = c.benchmark_group("de_rosenbrock");
    group.measurement_time(Duration::from_secs(15));

    let problem = RosenbrockProblem::new();
    let evaluator = LeastSquaresEvaluator::new(problem);

    for preset in de_bench_configs() {
        let cfg = DifferentialEvolutionConfig {
            num_dimensions: 2,
            population_size: preset.population_multiplier * 2,
            scaling_factor: preset.scaling_factor,
            crossover_rate: preset.crossover_rate,
            generations: preset.generations,
            strategy: preset.strategy,
            bounds: vec![(-5.0, 5.0), (-5.0, 5.0)],
            seed: 42,
            cost_tolerance: None,
            param_tolerance: None,
            diversity_tolerance: None,
        };

        let bench_id = BenchmarkId::new(preset.name, "default");
        group.bench_with_input(bench_id, &cfg, |b, cfg| {
            b.iter(|| {
                let mut solver =
                    DifferentialEvolution::new(cfg.clone()).unwrap();
                let mut best = vec![0.0; cfg.num_dimensions];
                black_box(
                    solver
                        .run(&evaluator, &mut best, &mmlogger::NoOpLogger)
                        .unwrap(),
                )
            });
        });
    }
    group.finish();
}

fn bench_de_goldstein_price(c: &mut Criterion) {
    let mut group = c.benchmark_group("de_goldstein_price");
    group.measurement_time(Duration::from_secs(20));

    let problem = GoldsteinPriceFunction;
    let evaluator = LeastSquaresEvaluator::new(problem);

    for preset in de_bench_configs() {
        let cfg = DifferentialEvolutionConfig {
            num_dimensions: 2,
            population_size: preset.population_multiplier * 2,
            scaling_factor: preset.scaling_factor,
            crossover_rate: preset.crossover_rate,
            generations: preset.generations,
            strategy: preset.strategy,
            bounds: vec![(-2.0, 2.0), (-2.0, 2.0)],
            seed: 43,
            cost_tolerance: None,
            param_tolerance: None,
            diversity_tolerance: None,
        };

        let bench_id = BenchmarkId::new(preset.name, "default");
        group.bench_with_input(bench_id, &cfg, |b, cfg| {
            b.iter(|| {
                let mut solver =
                    DifferentialEvolution::new(cfg.clone()).unwrap();
                let mut best = vec![0.0; cfg.num_dimensions];
                black_box(
                    solver
                        .run(&evaluator, &mut best, &mmlogger::NoOpLogger)
                        .unwrap(),
                )
            });
        });
    }
    group.finish();
}

fn bench_de_powell(c: &mut Criterion) {
    let mut group = c.benchmark_group("de_powell");
    group.measurement_time(Duration::from_secs(25));

    let problem = PowellProblem;
    let evaluator = LeastSquaresEvaluator::new(problem);

    for preset in de_bench_configs() {
        let cfg = DifferentialEvolutionConfig {
            num_dimensions: 4,
            population_size: preset.population_multiplier * 4,
            scaling_factor: preset.scaling_factor,
            crossover_rate: preset.crossover_rate,
            generations: preset.generations,
            strategy: preset.strategy,
            bounds: vec![(-5.0, 5.0), (-5.0, 5.0), (-5.0, 5.0), (-5.0, 5.0)],
            seed: 44,
            cost_tolerance: None,
            param_tolerance: None,
            diversity_tolerance: None,
        };

        let bench_id = BenchmarkId::new(preset.name, "default");
        group.bench_with_input(bench_id, &cfg, |b, cfg| {
            b.iter(|| {
                let mut solver =
                    DifferentialEvolution::new(cfg.clone()).unwrap();
                let mut best = vec![0.0; cfg.num_dimensions];
                black_box(
                    solver
                        .run(&evaluator, &mut best, &mmlogger::NoOpLogger)
                        .unwrap(),
                )
            });
        });
    }
    group.finish();
}

fn bench_de_bukin_n6(c: &mut Criterion) {
    let mut group = c.benchmark_group("de_bukin_n6");
    group.measurement_time(Duration::from_secs(30));

    let problem = BukinN6Problem;
    let evaluator = LeastSquaresEvaluator::new(problem);

    for preset in de_bench_configs() {
        let cfg = DifferentialEvolutionConfig {
            num_dimensions: 2,
            population_size: preset.population_multiplier * 2,
            scaling_factor: preset.scaling_factor,
            crossover_rate: preset.crossover_rate,
            generations: preset.generations * 2, // Extra difficult
            strategy: preset.strategy,
            bounds: vec![(-15.0, -5.0), (-3.0, 3.0)],
            seed: 45,
            cost_tolerance: None,
            param_tolerance: None,
            diversity_tolerance: None,
        };

        let bench_id = BenchmarkId::new(preset.name, "default");
        group.bench_with_input(bench_id, &cfg, |b, cfg| {
            b.iter(|| {
                let mut solver =
                    DifferentialEvolution::new(cfg.clone()).unwrap();
                let mut best = vec![0.0; cfg.num_dimensions];
                black_box(
                    solver
                        .run(&evaluator, &mut best, &mmlogger::NoOpLogger)
                        .unwrap(),
                )
            });
        });
    }
    group.finish();
}

fn bench_de_strategy_comparison(c: &mut Criterion) {
    let mut group = c.benchmark_group("de_strategy_comparison");
    group.measurement_time(Duration::from_secs(15));

    let problem = RosenbrockProblem::new();
    let evaluator = LeastSquaresEvaluator::new(problem);

    let strategies = vec![
        ("Rand1Bin", DifferentialEvolutionStrategy::Rand1Bin),
        ("Best1Bin", DifferentialEvolutionStrategy::Best1Bin),
    ];

    for (name, strategy) in strategies {
        let cfg = DifferentialEvolutionConfig {
            num_dimensions: 2,
            population_size: 40,
            scaling_factor: 0.8,
            crossover_rate: 0.9,
            generations: 300,
            strategy,
            bounds: vec![(-5.0, 5.0), (-5.0, 5.0)],
            seed: 46,
            cost_tolerance: None,
            param_tolerance: None,
            diversity_tolerance: None,
        };

        let bench_id = BenchmarkId::new("Rosenbrock", name);
        group.bench_with_input(bench_id, &cfg, |b, cfg| {
            b.iter(|| {
                let mut solver =
                    DifferentialEvolution::new(cfg.clone()).unwrap();
                let mut best = vec![0.0; cfg.num_dimensions];
                black_box(
                    solver
                        .run(&evaluator, &mut best, &mmlogger::NoOpLogger)
                        .unwrap(),
                )
            });
        });
    }
    group.finish();
}

criterion_group!(
    benches,
    bench_de_rosenbrock,
    bench_de_goldstein_price,
    bench_de_powell,
    bench_de_bukin_n6,
    bench_de_strategy_comparison
);
criterion_main!(benches);
