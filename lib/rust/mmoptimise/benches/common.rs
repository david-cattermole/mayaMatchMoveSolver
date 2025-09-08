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

use anyhow::anyhow;
use anyhow::Result;
use mmoptimise_rust::solver::common::{
    OptimisationProblem, ParameterScalingMode,
};
use mmoptimise_rust::solver::gauss_newton::{
    GaussNewtonConfig, GaussNewtonSolver, GaussNewtonWorkspace,
};
use mmoptimise_rust::solver::levenberg_marquardt::{
    LevenbergMarquardtConfig, LevenbergMarquardtSolver,
    LevenbergMarquardtWorkspace,
};
use mmoptimise_rust::solver::powell_dogleg::{
    PowellDogLegConfig, PowellDogLegSolver, PowellDogLegWorkspace,
};
use mmoptimise_rust::solver::test_problems::{
    BukinN6Problem, CurveFittingProblem, ExtendedRosenbrockProblem,
    GoldsteinPriceFunction, PowellProblem, RosenbrockProblem,
};

/// Configuration factory functions for each solver type.
/// These configs are designed to be comparable across all solvers.
pub fn levenberg_marquardt_configs(
) -> Vec<(&'static str, LevenbergMarquardtConfig)> {
    vec![
        ("Default", LevenbergMarquardtConfig::default()),
        (
            "HighPrecision",
            LevenbergMarquardtConfig {
                function_tolerance: 1e-12,
                parameter_tolerance: 1e-12,
                gradient_tolerance: 1e-12,
                max_iterations: 500,
                ..Default::default()
            },
        ),
    ]
}

pub fn gauss_newton_configs() -> Vec<(&'static str, GaussNewtonConfig)> {
    vec![
        ("Default", GaussNewtonConfig::default()),
        (
            "HighPrecision",
            GaussNewtonConfig {
                function_tolerance: 1e-12,
                parameter_tolerance: 1e-12,
                gradient_tolerance: 1e-12,
                max_iterations: 500,
                ..Default::default()
            },
        ),
    ]
}

pub fn powell_dogleg_configs() -> Vec<(&'static str, PowellDogLegConfig)> {
    vec![
        ("Default", PowellDogLegConfig::default()),
        (
            "HighPrecision",
            PowellDogLegConfig {
                function_tolerance: 1e-12,
                parameter_tolerance: 1e-12,
                gradient_tolerance: 1e-12,
                max_iterations: 500,
                ..Default::default()
            },
        ),
    ]
}

/// Standard problem variants for consistent benchmarking across all solvers.
pub fn rosenbrock_problem_variants() -> Vec<(&'static str, RosenbrockProblem)> {
    vec![
        ("Standard", RosenbrockProblem::new()),
        ("Easy", RosenbrockProblem::with_parameters(1.0, 10.0)),
    ]
}

/// Benchmark starting points for different difficulty levels.
#[derive(Clone, Debug)]
pub struct StartingPoint {
    pub name: &'static str,
    pub parameters: Vec<f64>,
}

/// Expected solution for validation in benchmarks.
#[derive(Clone, Debug)]
pub struct ExpectedSolution {
    pub parameters: Vec<f64>,
    pub parameter_tolerance: f64, // Epsilon for parameter comparison
    pub maximum_cost_threshold: f64, // Max acceptable final cost.
}

/// Expected solution factory functions for each problem type.
/// These define the known optimal solutions that benchmarks must validate against.
pub fn rosenbrock_expected_solution() -> ExpectedSolution {
    ExpectedSolution {
        parameters: vec![1.0, 1.0], // Global minimum at (1, 1)
        parameter_tolerance: 1e-6,
        maximum_cost_threshold: 1e-10,
    }
}

pub fn powell_expected_solution() -> ExpectedSolution {
    ExpectedSolution {
        parameters: vec![0.0, 0.0, 0.0, 0.0], // Global minimum at origin.
        parameter_tolerance: 1e-1,
        maximum_cost_threshold: 1e-7,
    }
}

pub fn bukin_n6_expected_solution() -> ExpectedSolution {
    ExpectedSolution {
        parameters: vec![-10.0, 1.0], // Global minimum.
        parameter_tolerance: 1e-4,
        maximum_cost_threshold: 1e-8,
    }
}

pub fn goldstein_price_expected_solution() -> ExpectedSolution {
    ExpectedSolution {
        parameters: vec![0.0, -1.0], // Global minimum.
        parameter_tolerance: 1e-4,
        maximum_cost_threshold: 3.01, // Function value is 3 at minimum.
    }
}

pub fn extended_rosenbrock_expected_solution(n: usize) -> ExpectedSolution {
    ExpectedSolution {
        parameters: vec![1.0; n], // All parameters should be 1.0.
        parameter_tolerance: 1e-6,
        maximum_cost_threshold: 1e-10,
    }
}

pub fn curve_fitting_expected_solution() -> ExpectedSolution {
    // Based on CurveFittingProblem, the true parameters for the exponential model are:
    // y = exp(m*x + c), where the synthetic data was generated with m=0.3, c=0.1.
    ExpectedSolution {
        parameters: vec![0.3, 0.1], // True parameters used to generate the data.
        parameter_tolerance: 1e-2,
        maximum_cost_threshold: 1.9, // Allow some error due to noise in data.
    }
}

/// Starting point factory functions for different problem types.
/// These are standardized across all solvers for fair comparison.
pub fn rosenbrock_starting_points() -> Vec<StartingPoint> {
    vec![
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0],
        },
        StartingPoint {
            name: "Standard",
            parameters: vec![-1.2, 1.0],
        },
        StartingPoint {
            name: "Challenging",
            parameters: vec![-2.0, 2.0],
        },
    ]
}

pub fn curve_fitting_starting_points() -> Vec<StartingPoint> {
    vec![
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0],
        },
        StartingPoint {
            name: "Near",
            parameters: vec![0.25, 0.08],
        },
        StartingPoint {
            name: "Far",
            parameters: vec![1.0, -0.5],
        },
    ]
}

pub fn powell_starting_points() -> Vec<StartingPoint> {
    vec![
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0, 0.0, 0.0],
        },
        StartingPoint {
            name: "Standard",
            parameters: vec![3.0, -1.0, 0.0, 1.0],
        },
        StartingPoint {
            name: "Far",
            parameters: vec![5.0, -5.0, 3.0, -3.0],
        },
    ]
}

pub fn bukin_n6_starting_points() -> Vec<StartingPoint> {
    vec![
        StartingPoint {
            name: "Point1",
            parameters: vec![-8.0, 0.5],
        },
        StartingPoint {
            name: "Point2",
            parameters: vec![-12.0, 2.0],
        },
        StartingPoint {
            name: "Edge",
            parameters: vec![-5.0, 0.0],
        },
    ]
}

pub fn goldstein_price_starting_points() -> Vec<StartingPoint> {
    vec![
        StartingPoint {
            name: "Near",
            parameters: vec![0.1, -0.9],
        },
        StartingPoint {
            name: "Origin",
            parameters: vec![0.0, 0.0],
        },
        StartingPoint {
            name: "Far",
            parameters: vec![2.0, 2.0],
        },
    ]
}

pub fn extended_rosenbrock_starting_points(n: usize) -> Vec<StartingPoint> {
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
            name: "Pattern",
            parameters: (0..n).map(|i| (i as f64 * 0.3) % 2.0 - 1.0).collect(),
        },
    ]
}

/// Validates that a solver found the expected solution within
/// tolerance.
///
/// This ensures benchmarks verify correctness, not just performance.
pub fn validate_solution(
    actual_params: &[f64],
    actual_cost: f64,
    expected: &ExpectedSolution,
) -> Result<()> {
    // Check that we have the correct number of parameters.
    if actual_params.len() != expected.parameters.len() {
        return Err(anyhow!(
            "Parameter count mismatch: got {}, expected {}.",
            actual_params.len(),
            expected.parameters.len()
        ));
    }

    // Check parameter accuracy.
    for (i, (&actual, &expected_param)) in actual_params
        .iter()
        .zip(expected.parameters.iter())
        .enumerate()
    {
        let error = (actual - expected_param).abs();
        if error > expected.parameter_tolerance {
            return Err(anyhow!(
                "Parameter {} out of tolerance: got {:.6}, expected {:.6}, error {:.2e}, tolerance {:.2e}.",
                i, actual, expected_param, error, expected.parameter_tolerance
            ));
        }
    }

    // Check cost threshold.
    if actual_cost > expected.maximum_cost_threshold {
        return Err(anyhow!(
            "Cost too high: got {:.2e}, maximum cost threshold {:.2e}.",
            actual_cost,
            expected.maximum_cost_threshold
        ));
    }

    Ok(())
}

/// Run a Levenberg-Marquardt benchmark.
pub fn run_lm_benchmark<P: OptimisationProblem>(
    problem: &P,
    expected: &ExpectedSolution,
    config: LevenbergMarquardtConfig,
    starting_point: &StartingPoint,
    workspace: &mut LevenbergMarquardtWorkspace,
) -> Result<(std::time::Duration, bool, usize, usize, f64)> {
    workspace.reuse_with(problem, &starting_point.parameters)?;
    let start = std::time::Instant::now();
    let solver = LevenbergMarquardtSolver::new(config);
    let result = solver.solve_problem(problem, workspace)?;
    let duration = start.elapsed();
    let success = result.status.is_success();

    if success {
        validate_solution(&result.parameters, result.cost, expected)?;

        Ok((
            duration,
            success,
            result.iterations,
            result.function_evaluations,
            result.cost,
        ))
    } else {
        Err(anyhow!("Solve failed!"))
    }
}

/// Run a Gauss-Newton benchmark.
pub fn run_gn_benchmark<P: OptimisationProblem>(
    problem: &P,
    expected: &ExpectedSolution,
    config: GaussNewtonConfig,
    starting_point: &StartingPoint,
    workspace: &mut GaussNewtonWorkspace,
) -> Result<(std::time::Duration, bool, usize, usize, f64)> {
    workspace.reuse_with(problem, &starting_point.parameters)?;
    let start = std::time::Instant::now();
    let solver = GaussNewtonSolver::new(config);
    let result = solver.solve_problem(problem, workspace)?;
    let duration = start.elapsed();
    let success = result.status.is_success();

    if success {
        validate_solution(&result.parameters, result.cost, expected)?;

        Ok((
            duration,
            success,
            result.iterations,
            result.function_evaluations,
            result.cost,
        ))
    } else {
        Err(anyhow!("Solve failed!"))
    }
}

/// Run a Powell Dog-Leg benchmark.
pub fn run_pdl_benchmark<P: OptimisationProblem>(
    problem: &P,
    expected: &ExpectedSolution,
    config: PowellDogLegConfig,
    starting_point: &StartingPoint,
    workspace: &mut PowellDogLegWorkspace,
) -> Result<(std::time::Duration, bool, usize, usize, f64)> {
    workspace.reuse_with(problem, &starting_point.parameters)?;
    let start = std::time::Instant::now();
    let solver = PowellDogLegSolver::new(config);
    let result = solver.solve_problem(problem, workspace)?;
    let duration = start.elapsed();
    let success = result.status.is_success();

    if success {
        validate_solution(&result.parameters, result.cost, expected)?;

        Ok((
            duration,
            success,
            result.iterations,
            result.function_evaluations,
            result.cost,
        ))
    } else {
        Err(anyhow!("Solve failed!"))
    }
}
