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
//! This benchmark suite tests the performance and accuracy of the
//! curve fitting implementations in mmscenegraph, focusing on
//! real-world scenarios like animation curve processing and noisy
//! data fitting.

use criterion::{
    black_box, criterion_group, criterion_main, BenchmarkId, Criterion,
};
use mmscenegraph_rust::math::curve_fit::{
    linear_regression, nonlinear_line_n3, nonlinear_line_n3_with_initial,
    nonlinear_line_n_points, nonlinear_line_n_points_with_initial, Point2,
};
use mmscenegraph_rust::math::interpolate::Interpolation;
use std::time::Duration;

mod common;

// Test data generators for reproducible benchmarks.
struct DataGenerator {
    random_index: usize,
}

impl DataGenerator {
    fn new() -> Self {
        Self { random_index: 0 }
    }

    fn get_next_random(&mut self) -> f64 {
        if self.random_index >= common::RANDOM_VALUES.len() {
            // Wrap around if we exceed the array.
            self.random_index = 0;
        }
        let value = common::RANDOM_VALUES[self.random_index];
        self.random_index += 1;
        value
    }

    // Generate linear data with optional noise.
    fn linear_data(
        &mut self,
        count: usize,
        noise_level: f64,
    ) -> (Vec<f64>, Vec<f64>) {
        let mut x_values = Vec::with_capacity(count);
        let mut y_values = Vec::with_capacity(count);

        let slope = 2.5;
        let intercept = 1.0;

        for i in 0..count {
            let x = (i as f64) * 0.1;
            let y_ideal = slope * x + intercept;
            let noise = if noise_level > 0.0 {
                (self.get_next_random() - 0.5) * noise_level
            } else {
                0.0
            };
            let y = y_ideal + noise;

            x_values.push(x);
            y_values.push(y);
        }

        (x_values, y_values)
    }

    // Generate sinusoidal data with optional noise.
    fn sine_wave_data(
        &mut self,
        count: usize,
        noise_level: f64,
    ) -> (Vec<f64>, Vec<f64>) {
        let mut x_values = Vec::with_capacity(count);
        let mut y_values = Vec::with_capacity(count);

        let frequency = 1.0;
        let amplitude = 3.0;
        let offset = 2.0;

        for i in 0..count {
            let x = (i as f64) * 0.2;
            let y_ideal = amplitude * (frequency * x).sin() + offset;
            let noise = if noise_level > 0.0 {
                (self.get_next_random() - 0.5) * noise_level
            } else {
                0.0
            };
            let y = y_ideal + noise;

            x_values.push(x);
            y_values.push(y);
        }

        (x_values, y_values)
    }

    // Generate polynomial data with optional noise.
    fn polynomial_data(
        &mut self,
        count: usize,
        noise_level: f64,
    ) -> (Vec<f64>, Vec<f64>) {
        let mut x_values = Vec::with_capacity(count);
        let mut y_values = Vec::with_capacity(count);

        // Cubic polynomial:
        // y = 0.5x³ - 2x² + 3x + 1
        for i in 0..count {
            let x = (i as f64) * 0.1 - 2.0; // Center around 0.
            let y_ideal = 0.5 * x.powi(3) - 2.0 * x.powi(2) + 3.0 * x + 1.0;
            let noise = if noise_level > 0.0 {
                (self.get_next_random() - 0.5) * noise_level
            } else {
                0.0
            };
            let y = y_ideal + noise;

            x_values.push(x);
            y_values.push(y);
        }

        (x_values, y_values)
    }

    // Generate exponential decay data.
    fn exponential_decay_data(
        &mut self,
        count: usize,
        noise_level: f64,
    ) -> (Vec<f64>, Vec<f64>) {
        let mut x_values = Vec::with_capacity(count);
        let mut y_values = Vec::with_capacity(count);

        let decay_rate = 0.5;
        let initial_value = 10.0;

        for i in 0..count {
            let x = (i as f64) * 0.1;
            let y_ideal = initial_value * (-decay_rate * x).exp();
            let noise = if noise_level > 0.0 {
                (self.get_next_random() - 0.5) * noise_level
            } else {
                0.0
            };
            let y = y_ideal + noise;

            x_values.push(x);
            y_values.push(y);
        }

        (x_values, y_values)
    }

    // Generate challenging data with sudden changes (step function).
    fn step_function_data(
        &mut self,
        count: usize,
        noise_level: f64,
    ) -> (Vec<f64>, Vec<f64>) {
        let mut x_values = Vec::with_capacity(count);
        let mut y_values = Vec::with_capacity(count);

        let step_position = count as f64 * 0.5;

        for i in 0..count {
            let x = i as f64;
            let y_ideal = if x < step_position { 1.0 } else { 5.0 };
            let noise = if noise_level > 0.0 {
                (self.get_next_random() - 0.5) * noise_level
            } else {
                0.0
            };
            let y = y_ideal + noise;

            x_values.push(x);
            y_values.push(y);
        }

        (x_values, y_values)
    }

    // Generate animation keyframe-like data.
    fn animation_keyframe_data(
        &mut self,
        count: usize,
        noise_level: f64,
    ) -> (Vec<f64>, Vec<f64>) {
        let mut x_values = Vec::with_capacity(count);
        let mut y_values = Vec::with_capacity(count);

        // Simulate typical animation curve: ease in, linear, ease
        // out.
        for i in 0..count {
            let x = i as f64;
            let t = x / (count - 1) as f64; // Normalize to [0, 1].

            // Smoothstep function for easing.
            let y_ideal = t * t * (3.0 - 2.0 * t) * 10.0;
            let noise = if noise_level > 0.0 {
                (self.get_next_random() - 0.5) * noise_level
            } else {
                0.0
            };
            let y = y_ideal + noise;

            x_values.push(x);
            y_values.push(y);
        }

        (x_values, y_values)
    }
}

// Benchmark linear regression with different data sizes and noise
// levels.
fn bench_linear_regression_data_sizes(c: &mut Criterion) {
    let mut group = c.benchmark_group("linear_regression_data_sizes");
    group.measurement_time(Duration::from_secs(5));

    let mut data_gen = DataGenerator::new();
    let data_sizes = [10, 50, 100, 500, 1000];
    let noise_levels = [0.0, 0.1, 0.5];

    for &size in &data_sizes {
        for &noise in &noise_levels {
            let (x_values, y_values) = data_gen.linear_data(size, noise);
            let bench_id = BenchmarkId::new(
                format!("size_{}_noise_{}", size, (noise * 100.0) as u32),
                "",
            );

            group.bench_with_input(
                bench_id,
                &(&x_values, &y_values),
                |b, (x, y)| {
                    b.iter(|| black_box(linear_regression(x, y).unwrap()));
                },
            );
        }
    }
    group.finish();
}

// Benchmark N3 curve fitting with different initialization methods.
fn bench_n3_initialization_methods(c: &mut Criterion) {
    let mut group = c.benchmark_group("n3_initialization_methods");
    group.measurement_time(Duration::from_secs(8));

    let mut data_gen = DataGenerator::new();
    let data_types = [
        ("linear", data_gen.linear_data(100, 0.1)),
        ("sine", data_gen.sine_wave_data(100, 0.1)),
        ("polynomial", data_gen.polynomial_data(100, 0.1)),
        ("exponential", data_gen.exponential_decay_data(100, 0.1)),
    ];

    for (data_name, (x_values, y_values)) in &data_types {
        let bench_id = BenchmarkId::new("default", *data_name);
        group.bench_with_input(bench_id, &(x_values, y_values), |b, (x, y)| {
            b.iter(|| black_box(nonlinear_line_n3(x, y).unwrap()));
        });
    }
    group.finish();
}

// Benchmark N3 with custom initial positions.
fn bench_n3_with_custom_initial(c: &mut Criterion) {
    let mut group = c.benchmark_group("n3_custom_initial");
    group.measurement_time(Duration::from_secs(6));

    let mut data_gen = DataGenerator::new();
    let (x_values, y_values) = data_gen.polynomial_data(100, 0.2);

    // Different initial control point strategies.
    let initial_strategies = [
        ("evenly_spaced", {
            let x_min = x_values.iter().copied().fold(f64::INFINITY, f64::min);
            let x_max =
                x_values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            let x_range = x_max - x_min;
            (
                vec![x_min, x_min + x_range / 2.0, x_max],
                vec![
                    y_values[0],
                    y_values[y_values.len() / 2],
                    y_values[y_values.len() - 1],
                ],
            )
        }),
        ("edge_weighted", {
            let x_min = x_values.iter().copied().fold(f64::INFINITY, f64::min);
            let x_max =
                x_values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
            let x_range = x_max - x_min;
            (
                vec![
                    x_min + x_range * 0.1,
                    x_min + x_range * 0.5,
                    x_min + x_range * 0.9,
                ],
                vec![
                    y_values[0],
                    y_values[y_values.len() / 2],
                    y_values[y_values.len() - 1],
                ],
            )
        }),
    ];

    for (strategy_name, (init_x, init_y)) in &initial_strategies {
        let bench_id = BenchmarkId::from_parameter(strategy_name);
        group.bench_with_input(
            bench_id,
            &(init_x, init_y),
            |b, (init_x, init_y)| {
                b.iter(|| {
                    black_box(
                        nonlinear_line_n3_with_initial(
                            &x_values, &y_values, init_x, init_y,
                        )
                        .unwrap(),
                    )
                });
            },
        );
    }
    group.finish();
}

// Benchmark N-points curve fitting with different interpolation
// methods.
fn bench_n_points_interpolation_methods(c: &mut Criterion) {
    let mut group = c.benchmark_group("n_points_interpolation_methods");
    group.measurement_time(Duration::from_secs(10));

    let mut data_gen = DataGenerator::new();
    let (x_values, y_values) = data_gen.sine_wave_data(200, 0.1);

    let control_point_counts = [4, 8, 16];
    let interpolation_methods = [
        Interpolation::Linear,
        Interpolation::QuadraticNUBS,
        Interpolation::CubicNUBS,
    ];

    for &control_count in &control_point_counts {
        for &method in &interpolation_methods {
            let bench_id = BenchmarkId::new(
                format!("{:?}", method),
                format!("controls_{}", control_count),
            );

            group.bench_with_input(
                bench_id,
                &(control_count, method),
                |b, (count, method)| {
                    b.iter(|| {
                        black_box(
                            nonlinear_line_n_points(
                                &x_values, &y_values, *count, *method,
                            )
                            .unwrap(),
                        )
                    });
                },
            );
        }
    }
    group.finish();
}

// Benchmark scalability with increasing data sizes.
fn bench_n_points_scalability(c: &mut Criterion) {
    let mut group = c.benchmark_group("n_points_scalability");
    group.measurement_time(Duration::from_secs(10));

    let mut data_gen = DataGenerator::new();
    let data_sizes = [50, 100, 500, 1000, 2000];
    let control_points = 8;
    let interpolation = Interpolation::CubicNUBS;

    for &size in &data_sizes {
        let (x_values, y_values) = data_gen.polynomial_data(size, 0.1);
        let bench_id = BenchmarkId::from_parameter(size);

        group.bench_with_input(bench_id, &(x_values, y_values), |b, (x, y)| {
            b.iter(|| {
                black_box(
                    nonlinear_line_n_points(
                        x,
                        y,
                        control_points,
                        interpolation,
                    )
                    .unwrap(),
                )
            });
        });
    }
    group.finish();
}

// Benchmark different data complexity scenarios.
fn bench_data_complexity_scenarios(c: &mut Criterion) {
    let mut group = c.benchmark_group("data_complexity_scenarios");
    group.measurement_time(Duration::from_secs(8));

    let mut data_gen = DataGenerator::new();
    let scenarios = [
        ("smooth_linear", data_gen.linear_data(100, 0.0)),
        ("noisy_linear", data_gen.linear_data(100, 0.3)),
        ("smooth_sine", data_gen.sine_wave_data(100, 0.0)),
        ("noisy_sine", data_gen.sine_wave_data(100, 0.2)),
        ("smooth_polynomial", data_gen.polynomial_data(100, 0.0)),
        ("noisy_polynomial", data_gen.polynomial_data(100, 0.3)),
        (
            "exponential_decay",
            data_gen.exponential_decay_data(100, 0.1),
        ),
        ("step_function", data_gen.step_function_data(100, 0.1)),
        (
            "animation_curve",
            data_gen.animation_keyframe_data(100, 0.05),
        ),
    ];

    let control_points = 6;
    let interpolation = Interpolation::QuadraticNUBS;

    for (scenario_name, (x_values, y_values)) in &scenarios {
        let bench_id = BenchmarkId::from_parameter(scenario_name);
        group.bench_with_input(bench_id, &(x_values, y_values), |b, (x, y)| {
            b.iter(|| {
                black_box(
                    nonlinear_line_n_points(
                        x,
                        y,
                        control_points,
                        interpolation,
                    )
                    .unwrap(),
                )
            });
        });
    }
    group.finish();
}

// Benchmark N-points with custom initial control points.
fn bench_n_points_custom_initial(c: &mut Criterion) {
    let mut group = c.benchmark_group("n_points_custom_initial");
    group.measurement_time(Duration::from_secs(6));

    let mut data_gen = DataGenerator::new();
    let (x_values, y_values) = data_gen.animation_keyframe_data(150, 0.1);

    let control_count = 8;
    let interpolation = Interpolation::CubicNUBS;

    // Generate initial control points.
    let x_min = x_values.iter().copied().fold(f64::INFINITY, f64::min);
    let x_max = x_values.iter().copied().fold(f64::NEG_INFINITY, f64::max);
    let x_range = x_max - x_min;

    let x_initial: Vec<f64> = (0..control_count)
        .map(|i| x_min + (i as f64 / (control_count - 1) as f64) * x_range)
        .collect();

    // Simple linear interpolation for initial Y values.
    let y_initial: Vec<f64> = x_initial
        .iter()
        .map(|&x| {
            // Find closest data point for initial estimate.
            let mut closest_idx = 0;
            let mut closest_dist = (x_values[0] - x).abs();
            for (i, &data_x) in x_values.iter().enumerate() {
                let dist = (data_x - x).abs();
                if dist < closest_dist {
                    closest_dist = dist;
                    closest_idx = i;
                }
            }
            y_values[closest_idx]
        })
        .collect();

    group.bench_function("custom_initial_positions", |b| {
        b.iter(|| {
            black_box(
                nonlinear_line_n_points_with_initial(
                    &x_values,
                    &y_values,
                    &x_initial,
                    &y_initial,
                    interpolation,
                )
                .unwrap(),
            )
        });
    });

    group.finish();
}

// Benchmark memory allocation patterns with different control point
// counts.
fn bench_memory_allocation_patterns(c: &mut Criterion) {
    let mut group = c.benchmark_group("memory_allocation_patterns");
    group.measurement_time(Duration::from_secs(8));

    let mut data_gen = DataGenerator::new();
    let (x_values, y_values) = data_gen.polynomial_data(500, 0.1);

    let control_counts = [4, 8, 16, 32, 64];
    let interpolation = Interpolation::Linear; // Use simple method to focus on allocation.

    for &control_count in &control_counts {
        let bench_id = BenchmarkId::from_parameter(control_count);
        group.bench_with_input(bench_id, &control_count, |b, &count| {
            b.iter(|| {
                black_box(
                    nonlinear_line_n_points(
                        &x_values,
                        &y_values,
                        count,
                        interpolation,
                    )
                    .unwrap(),
                )
            });
        });
    }
    group.finish();
}

// Benchmark convergence characteristics with challenging data.
fn bench_convergence_characteristics(c: &mut Criterion) {
    let mut group = c.benchmark_group("convergence_characteristics");
    group.measurement_time(Duration::from_secs(12));

    let mut data_gen = DataGenerator::new();

    // Generate challenging datasets that test solver robustness.
    let challenging_datasets = [
        ("high_noise", data_gen.sine_wave_data(100, 1.0)), // Very noisy.
        ("sparse_data", data_gen.polynomial_data(20, 0.1)), // Few data points.
        ("steep_gradients", {
            let mut x = Vec::new();
            let mut y = Vec::new();
            for i in 0..100 {
                let x_val = i as f64 * 0.1;
                let y_val = if x_val < 5.0 {
                    x_val * 10.0
                } else {
                    50.0 - (x_val - 5.0) * 20.0
                };
                x.push(x_val);
                y.push(y_val);
            }
            (x, y)
        }),
        ("oscillatory", {
            let mut x = Vec::new();
            let mut y = Vec::new();
            for i in 0..150 {
                let x_val = i as f64 * 0.1;
                let y_val = (x_val * 5.0).sin() * (x_val * 0.5).exp();
                x.push(x_val);
                y.push(y_val);
            }
            (x, y)
        }),
    ];

    let control_points = 8;
    let interpolation = Interpolation::CubicNUBS;

    for (dataset_name, (x_values, y_values)) in &challenging_datasets {
        let bench_id = BenchmarkId::from_parameter(dataset_name);
        group.bench_with_input(bench_id, &(x_values, y_values), |b, (x, y)| {
            b.iter(|| {
                // Use unwrap_or to handle potential convergence
                // failures gracefully.
                black_box(
                    nonlinear_line_n_points(
                        x,
                        y,
                        control_points,
                        interpolation,
                    )
                    .unwrap_or_else(|_| {
                        vec![Point2::new(0.0, 0.0); control_points]
                    }),
                )
            });
        });
    }
    group.finish();
}

criterion_group!(
    benches,
    bench_linear_regression_data_sizes,
    bench_n3_initialization_methods,
    bench_n3_with_custom_initial,
    bench_n_points_interpolation_methods,
    bench_n_points_scalability,
    bench_data_complexity_scenarios,
    bench_n_points_custom_initial,
    bench_memory_allocation_patterns,
    bench_convergence_characteristics
);
criterion_main!(benches);
