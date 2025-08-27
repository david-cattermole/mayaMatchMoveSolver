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

//! Common utilities and problem definitions for mmoptimise
//! benchmarks.

use anyhow::Result;
use mmoptimise_rust::{
    LevenbergMarquardt, OptimisationProblem, ScalingMode, SolverConfig,
    SolverWorkspace,
};
use num_traits::{Float, Zero};
use std::ops::{Add, Div, Mul, Sub};

/// Benchmark configuration for different solver setups.
#[derive(Clone, Debug)]
pub struct BenchmarkConfig {
    pub name: &'static str,
    pub config: SolverConfig,
}

impl BenchmarkConfig {
    pub fn default_configs() -> Vec<Self> {
        vec![
            BenchmarkConfig {
                name: "Default",
                config: SolverConfig::default(),
            },
            BenchmarkConfig {
                name: "HighPrecision",
                config: SolverConfig {
                    ftol: 1e-12,
                    xtol: 1e-12,
                    gtol: 1e-12,
                    max_iterations: 1000,
                    ..Default::default()
                },
            },
            BenchmarkConfig {
                name: "FastConvergence",
                config: SolverConfig {
                    ftol: 1e-4,
                    xtol: 1e-4,
                    gtol: 1e-4,
                    max_iterations: 100,
                    ..Default::default()
                },
            },
            BenchmarkConfig {
                name: "NoScaling",
                config: SolverConfig {
                    scaling_mode: ScalingMode::None,
                    ..Default::default()
                },
            },
            BenchmarkConfig {
                name: "ManualScaling",
                config: SolverConfig {
                    scaling_mode: ScalingMode::Manual,
                    ..Default::default()
                },
            },
            BenchmarkConfig {
                name: "SmallTrustRegion",
                config: SolverConfig {
                    initial_trust_factor: 0.1,
                    ..Default::default()
                },
            },
        ]
    }
}

/// Benchmark starting points for different difficulty levels.
#[derive(Clone, Debug)]
pub struct StartingPoint {
    pub name: &'static str,
    pub parameters: Vec<f64>,
}

/// Rosenbrock function - classic optimization test problem:
/// f(x, y) = (a - x)^2 + b*(y - x^2)^2
///
/// Global minimum at (x, y) = (a, a^2) with f = 0
pub struct RosenbrockProblem {
    pub a: f64,
    pub b: f64,
}

#[allow(dead_code)]
impl RosenbrockProblem {
    pub fn new() -> Self {
        Self { a: 1.0, b: 100.0 }
    }

    pub fn with_parameters(a: f64, b: f64) -> Self {
        Self { a, b }
    }

    pub fn starting_points() -> Vec<StartingPoint> {
        vec![
            StartingPoint {
                name: "NearMinimum",
                parameters: vec![0.9, 0.9],
            },
            StartingPoint {
                name: "Origin",
                parameters: vec![0.0, 0.0],
            },
            StartingPoint {
                name: "FarPoint",
                parameters: vec![-1.2, 1.0],
            },
            StartingPoint {
                name: "ChallengingPoint",
                parameters: vec![-2.0, 2.0],
            },
        ]
    }
}

impl OptimisationProblem for RosenbrockProblem {
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> Result<()>
    where
        T: Copy
            + Add<Output = T>
            + Sub<Output = T>
            + Mul<Output = T>
            + Div<Output = T>
            + From<f64>
            + Sized
            + Zero
            + Float,
    {
        let x = parameters[0];
        let y = parameters[1];
        let a = <T as From<f64>>::from(self.a);
        let b = <T as From<f64>>::from(self.b);

        out_residuals[0] = a - x;
        out_residuals[1] = b.sqrt() * (y - x * x);
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }

    fn residual_count(&self) -> usize {
        2
    }
}

/// Extended Rosenbrock function for N dimensions:
/// f(x) = sum_{i=1}^{N/2} [100*(x_{2i} - x_{2i-1}^2)^2 + (1 - x_{2i-1})^2]
pub struct ExtendedRosenbrockProblem {
    pub n: usize,
}

#[allow(dead_code)]
impl ExtendedRosenbrockProblem {
    pub fn new(n: usize) -> Self {
        assert!(n >= 2 && n % 2 == 0, "N must be even and >= 2");
        Self { n }
    }

    pub fn starting_points(n: usize) -> Vec<StartingPoint> {
        vec![
            StartingPoint {
                name: "Origin",
                parameters: vec![0.0; n],
            },
            StartingPoint {
                name: "Alternating",
                parameters: (0..n)
                    .map(|i| if i % 2 == 0 { -1.2 } else { 1.0 })
                    .collect(),
            },
            StartingPoint {
                name: "Random",
                parameters: (0..n)
                    .map(|i| (i as f64 * 0.3) % 2.0 - 1.0)
                    .collect(),
            },
        ]
    }
}

impl OptimisationProblem for ExtendedRosenbrockProblem {
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> Result<()>
    where
        T: Copy
            + Add<Output = T>
            + Sub<Output = T>
            + Mul<Output = T>
            + Div<Output = T>
            + From<f64>
            + Sized
            + Zero
            + Float,
    {
        let one = <T as From<f64>>::from(1.0);
        let hundred = <T as From<f64>>::from(100.0);

        for i in 0..(self.n / 2) {
            let x1 = parameters[2 * i];
            let x2 = parameters[2 * i + 1];

            out_residuals[2 * i] = hundred.sqrt() * (x2 - x1 * x1);
            out_residuals[2 * i + 1] = one - x1;
        }
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        self.n
    }

    fn residual_count(&self) -> usize {
        self.n
    }
}

/// Powell's function - another classic difficult optimization problem:
/// f(x) = (x1 + 10*x2)^2 + 5*(x3 - x4)^2 + (x2 - 2*x3)^4 + 10*(x1 - x4)^4
pub struct PowellProblem;

#[allow(dead_code)]
impl PowellProblem {
    pub fn starting_points() -> Vec<StartingPoint> {
        vec![
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
        ]
    }
}

impl OptimisationProblem for PowellProblem {
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> Result<()>
    where
        T: Copy
            + Add<Output = T>
            + Sub<Output = T>
            + Mul<Output = T>
            + Div<Output = T>
            + From<f64>
            + Sized
            + Zero
            + Float,
    {
        let x1 = parameters[0];
        let x2 = parameters[1];
        let x3 = parameters[2];
        let x4 = parameters[3];

        let ten = <T as From<f64>>::from(10.0);
        let five = <T as From<f64>>::from(5.0);
        let two = <T as From<f64>>::from(2.0);

        out_residuals[0] = x1 + ten * x2;
        out_residuals[1] = five.sqrt() * (x3 - x4);
        out_residuals[2] = (x2 - two * x3) * (x2 - two * x3);
        out_residuals[3] = ten.sqrt() * (x1 - x4) * (x1 - x4);

        Ok(())
    }

    fn parameter_count(&self) -> usize {
        4
    }

    fn residual_count(&self) -> usize {
        4
    }
}

/// Curve fitting problem - fitting y = exp(m*x + c) to noisy data.
pub struct CurveFittingProblem {
    pub x_data: Vec<f64>,
    pub y_data: Vec<f64>,
}

#[allow(dead_code)]
impl CurveFittingProblem {
    pub fn example_data1() -> Self {
        let data = vec![
            (0.000000e+00, 1.133898e+00),
            (7.500000e-02, 1.334902e+00),
            (1.500000e-01, 1.213546e+00),
            (2.250000e-01, 1.252016e+00),
            (3.000000e-01, 1.392265e+00),
            (3.750000e-01, 1.314458e+00),
            (4.500000e-01, 1.472541e+00),
            (5.250000e-01, 1.536218e+00),
            (6.000000e-01, 1.355679e+00),
            (6.750000e-01, 1.463566e+00),
            (7.500000e-01, 1.490201e+00),
            (8.250000e-01, 1.658699e+00),
            (9.000000e-01, 1.067574e+00),
            (9.750000e-01, 1.464629e+00),
            (1.050000e+00, 1.402653e+00),
            (1.125000e+00, 1.713141e+00),
            (1.200000e+00, 1.527021e+00),
            (1.275000e+00, 1.702632e+00),
            (1.350000e+00, 1.423899e+00),
            (1.425000e+00, 1.543078e+00),
            (1.500000e+00, 1.664015e+00),
            (1.575000e+00, 1.732484e+00),
            (1.650000e+00, 1.543296e+00),
            (1.725000e+00, 1.959523e+00),
            (1.800000e+00, 1.685132e+00),
            (1.875000e+00, 1.951791e+00),
            (1.950000e+00, 2.095346e+00),
            (2.025000e+00, 2.361460e+00),
            (2.100000e+00, 2.169119e+00),
            (2.175000e+00, 2.061745e+00),
            (2.250000e+00, 2.178641e+00),
            (2.325000e+00, 2.104346e+00),
            (2.400000e+00, 2.584470e+00),
            (2.475000e+00, 1.914158e+00),
            (2.550000e+00, 2.368375e+00),
            (2.625000e+00, 2.686125e+00),
            (2.700000e+00, 2.712395e+00),
            (2.775000e+00, 2.499511e+00),
            (2.850000e+00, 2.558897e+00),
            (2.925000e+00, 2.309154e+00),
            (3.000000e+00, 2.869503e+00),
            (3.075000e+00, 3.116645e+00),
            (3.150000e+00, 3.094907e+00),
            (3.225000e+00, 2.471759e+00),
            (3.300000e+00, 3.017131e+00),
            (3.375000e+00, 3.232381e+00),
            (3.450000e+00, 2.944596e+00),
            (3.525000e+00, 3.385343e+00),
            (3.600000e+00, 3.199826e+00),
            (3.675000e+00, 3.423039e+00),
            (3.750000e+00, 3.621552e+00),
            (3.825000e+00, 3.559255e+00),
            (3.900000e+00, 3.530713e+00),
            (3.975000e+00, 3.561766e+00),
            (4.050000e+00, 3.544574e+00),
            (4.125000e+00, 3.867945e+00),
            (4.200000e+00, 4.049776e+00),
            (4.275000e+00, 3.885601e+00),
            (4.350000e+00, 4.110505e+00),
            (4.425000e+00, 4.345320e+00),
            (4.500000e+00, 4.161241e+00),
            (4.575000e+00, 4.363407e+00),
            (4.650000e+00, 4.161576e+00),
            (4.725000e+00, 4.619728e+00),
            (4.800000e+00, 4.737410e+00),
            (4.875000e+00, 4.727863e+00),
            (4.950000e+00, 4.669206e+00),
        ];

        let (x_data, y_data): (Vec<_>, Vec<_>) = data.into_iter().unzip();
        Self { x_data, y_data }
    }

    pub fn starting_points() -> Vec<StartingPoint> {
        vec![
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
        ]
    }
}

impl OptimisationProblem for CurveFittingProblem {
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> Result<()>
    where
        T: Copy
            + Add<Output = T>
            + Sub<Output = T>
            + Mul<Output = T>
            + Div<Output = T>
            + From<f64>
            + Sized
            + Zero
            + Float,
    {
        let m = parameters[0];
        let c = parameters[1];

        for (i, (x, y)) in self.x_data.iter().zip(&self.y_data).enumerate() {
            let x_val = <T as From<f64>>::from(*x);
            let y_val = <T as From<f64>>::from(*y);
            out_residuals[i] = y_val - (m * x_val + c).exp();
        }
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }

    fn residual_count(&self) -> usize {
        self.x_data.len()
    }
}

/// Bukin function N.6 - extremely difficult optimization problem:
///
/// f(x, y) = 100 * sqrt(|y - 0.01*x^2|) + 0.01 * |x + 10|
///
/// Global minimum: f(-10, 1) = 0
pub struct BukinN6Problem;

#[allow(dead_code)]
impl BukinN6Problem {
    pub fn starting_points() -> Vec<StartingPoint> {
        vec![
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
        ]
    }
}

impl OptimisationProblem for BukinN6Problem {
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> Result<()>
    where
        T: Copy
            + Add<Output = T>
            + Sub<Output = T>
            + Mul<Output = T>
            + Div<Output = T>
            + From<f64>
            + Sized
            + Zero
            + Float,
    {
        let x = parameters[0];
        let y = parameters[1];

        let point_zero_one = <T as From<f64>>::from(0.01);
        let ten = <T as From<f64>>::from(10.0);

        let term1 = (y - point_zero_one * x * x).abs();
        let term2 = (x + ten).abs();

        out_residuals[0] = <T as From<f64>>::from(10.0)
            * term1.powf(<T as From<f64>>::from(0.25));
        out_residuals[1] = <T as From<f64>>::from(0.1) * term2.sqrt();

        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }

    fn residual_count(&self) -> usize {
        2
    }
}

/// Goldstein-Price function - complex function with multiple local
/// minima.
///
/// Global minimum: f(0, -1) = 3
pub struct GoldsteinPriceFunction;

#[allow(dead_code)]
impl GoldsteinPriceFunction {
    pub fn starting_points() -> Vec<StartingPoint> {
        vec![
            StartingPoint {
                name: "NearMinimum",
                parameters: vec![0.1, -0.9],
            },
            StartingPoint {
                name: "Origin",
                parameters: vec![0.0, 0.0],
            },
            StartingPoint {
                name: "FarPoint",
                parameters: vec![2.0, 2.0],
            },
        ]
    }
}

impl OptimisationProblem for GoldsteinPriceFunction {
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> Result<()>
    where
        T: Copy
            + Add<Output = T>
            + Sub<Output = T>
            + Mul<Output = T>
            + Div<Output = T>
            + From<f64>
            + Sized
            + Zero
            + Float,
    {
        let x = parameters[0];
        let y = parameters[1];

        let one = <T as From<f64>>::from(1.0);
        let term1_base = x + y + one;
        let term1_mult = <T as From<f64>>::from(19.0)
            - <T as From<f64>>::from(14.0) * x
            + <T as From<f64>>::from(3.0) * x * x
            - <T as From<f64>>::from(14.0) * y
            + <T as From<f64>>::from(6.0) * x * y
            + <T as From<f64>>::from(3.0) * y * y;
        let term1 = one + term1_base * term1_base * term1_mult;

        let term2_base =
            <T as From<f64>>::from(2.0) * x - <T as From<f64>>::from(3.0) * y;
        let term2_mult = <T as From<f64>>::from(18.0)
            - <T as From<f64>>::from(32.0) * x
            + <T as From<f64>>::from(12.0) * x * x
            + <T as From<f64>>::from(48.0) * y
            - <T as From<f64>>::from(36.0) * x * y
            + <T as From<f64>>::from(27.0) * y * y;
        let term2 =
            <T as From<f64>>::from(30.0) + term2_base * term2_base * term2_mult;

        out_residuals[0] = term1.sqrt() - <T as From<f64>>::from(1.0);
        out_residuals[1] =
            term2.sqrt() - <T as From<f64>>::from(30.0f64.sqrt());

        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }

    fn residual_count(&self) -> usize {
        2
    }
}

/// Run a single benchmark for any optimization problem.
pub fn run_benchmark<P: OptimisationProblem>(
    problem: &P,
    config: &BenchmarkConfig,
    starting_point: &StartingPoint,
) -> Result<(std::time::Duration, bool, usize, usize, f64)> {
    let solver = LevenbergMarquardt::new(config.config);
    let mut workspace =
        SolverWorkspace::new(problem, &starting_point.parameters)?;

    let start = std::time::Instant::now();
    let result = solver.solve_problem(problem, &mut workspace)?;
    let duration = start.elapsed();

    let success = mmoptimise_rust::is_success(result.status);
    Ok((
        duration,
        success,
        result.iterations,
        result.function_evaluations,
        result.cost,
    ))
}

/// Run a benchmark with a reused workspace for improved performance.
///
/// This function allows reusing an existing workspace to avoid memory
/// allocations when running multiple benchmarks with the same problem
/// structure.
pub fn run_benchmark_with_workspace<P: OptimisationProblem>(
    problem: &P,
    config: &BenchmarkConfig,
    starting_point: &StartingPoint,
    workspace: &mut SolverWorkspace,
) -> Result<(std::time::Duration, bool, usize, usize, f64)> {
    let solver = LevenbergMarquardt::new(config.config);

    workspace.reuse_with(problem, &starting_point.parameters)?;

    let start = std::time::Instant::now();
    let result = solver.solve_problem(problem, workspace)?;
    let duration = start.elapsed();

    let success = mmoptimise_rust::is_success(result.status);
    Ok((
        duration,
        success,
        result.iterations,
        result.function_evaluations,
        result.cost,
    ))
}
