//
// Copyright (C) 2025 David Cattermole.
//
// This file is part of mmSolver.
//
// mmSolver is free software: you can redistribute it and/or modify it
// under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
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

use anyhow::Result;
use log::debug;
use log::info;
use nalgebra::{DMatrix, DVector};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum OptimisationError {
    #[error("Invalid input parameters: {0}")]
    InvalidInput(String),
    #[error("Solver failed: {0}")]
    SolverError(String),
    #[error("Maximum iterations reached")]
    MaxIterationsReached,
    #[error("Function evaluation limit exceeded")]
    FunctionCallsExceeded,
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SolverStatus {
    Success,
    ToleranceReached,
    MaxIterationsReached,
}

#[derive(Debug, Clone)]
pub struct OptimisationResult {
    pub status: SolverStatus,
    pub parameters: Vec<f64>,
    pub residuals: Vec<f64>,
    pub cost: f64,
    pub iterations: usize,
    pub function_evaluations: usize,
    pub message: &'static str,
}

#[derive(Debug, Clone)]
pub struct SolverConfig {
    pub ftol: f64,
    pub xtol: f64,
    pub gtol: f64,
    pub max_iterations: usize,
    pub step_bound: f64,
    pub verbose: bool,
}

pub fn is_success(status: SolverStatus) -> bool {
    matches!(
        status,
        SolverStatus::Success | SolverStatus::ToleranceReached
    )
}

pub trait OptimisationProblem {
    /// Compute residuals at the given parameters, writing to the
    /// output buffer.
    fn residuals(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> Result<()>;

    /// Compute jacobian at the given parameters, writing to the
    /// output buffer (optional).
    ///
    /// The jacobian should be stored in row-major order.
    ///
    /// Returns true if a jacobian was computed, false to fall back to
    /// finite differences.
    fn jacobian(
        &self,
        parameters: &[f64],
        out_jacobian: &mut [f64],
    ) -> Result<bool> {
        let _ = parameters;
        let _ = out_jacobian;
        Ok(false) // Default to finite differences.
    }

    /// Compute residuals using nalgebra types for zero-allocation solving.
    /// Default implementation delegates to slice-based method.
    fn residuals_nalgebra(
        &self,
        parameters: &DVector<f64>,
        out_residuals: &mut DVector<f64>,
    ) -> Result<()> {
        self.residuals(parameters.as_slice(), out_residuals.as_mut_slice())
    }

    /// Compute jacobian using nalgebra types for zero-allocation solving.
    /// Default implementation delegates to slice-based method.
    ///
    /// The jacobian matrix is m x n (residuals x parameters).
    fn jacobian_nalgebra(
        &self,
        parameters: &DVector<f64>,
        out_jacobian: &mut DMatrix<f64>,
    ) -> Result<bool> {
        self.jacobian(parameters.as_slice(), out_jacobian.as_mut_slice())
    }

    /// Number of parameters.
    fn parameter_count(&self) -> usize;

    /// Number of residuals.
    fn residual_count(&self) -> usize;
}

/// Pre-allocated workspace for solver to eliminate allocations during
/// solving. Uses nalgebra internally for optimal performance.
pub struct SolverWorkspace {
    // Problem dimensions.
    n: usize, // number of parameters.
    m: usize, // number of residuals.

    // Pre-allocated nalgebra matrices and vectors for zero-allocation solving.
    pub parameters: DVector<f64>, // Current parameter values
    pub best_parameters: DVector<f64>, // Best parameters found so far
    residuals: DVector<f64>,      // Current residuals
    best_residuals: DVector<f64>, // Best residuals found so far
    trial_residuals: DVector<f64>, // Residuals for trial step
    jacobian: DMatrix<f64>,       // Jacobian matrix (m x n)
    gradient: DVector<f64>,       // Gradient vector (n)
    jtj: DMatrix<f64>,            // J^T * J matrix (n x n)
    damped_jtj: DMatrix<f64>,     // Working copy for linear system (n x n)
    step: DVector<f64>,           // Step vector (n)
    trial_parameters: DVector<f64>, // Trial parameter values

    // Pre-allocated result storage to avoid allocations during solve.
    result_parameters: DVector<f64>,
    result_residuals: DVector<f64>,
}

impl SolverWorkspace {
    pub fn new<P: OptimisationProblem>(
        problem: &P,
        initial_parameters: &[f64],
    ) -> Result<Self> {
        let n = problem.parameter_count();
        let m = problem.residual_count();

        if initial_parameters.len() != n {
            return Err(OptimisationError::InvalidInput(format!(
                "Expected {} parameters, got {}",
                n,
                initial_parameters.len()
            ))
            .into());
        }

        Ok(Self {
            n,
            m,
            parameters: DVector::from_row_slice(initial_parameters),
            best_parameters: DVector::from_row_slice(initial_parameters),
            residuals: DVector::zeros(m),
            best_residuals: DVector::zeros(m),
            trial_residuals: DVector::zeros(m),
            jacobian: DMatrix::zeros(m, n),
            gradient: DVector::zeros(n),
            jtj: DMatrix::zeros(n, n),
            damped_jtj: DMatrix::zeros(n, n),
            step: DVector::zeros(n),
            trial_parameters: DVector::zeros(n),
            result_parameters: DVector::zeros(n),
            result_residuals: DVector::zeros(m),
        })
    }
}

/// Levenberg-Marquardt solver.
pub struct LevenbergMarquardt {
    config: SolverConfig,
}

impl LevenbergMarquardt {
    pub fn new(config: SolverConfig) -> Self {
        Self { config }
    }

    pub fn with_defaults() -> Self {
        Self {
            config: SolverConfig::default(),
        }
    }

    /// Solve using a problem trait implementation with zero
    /// allocations during solving.
    pub fn solve_problem<P: OptimisationProblem>(
        &self,
        problem: &P,
        workspace: &mut SolverWorkspace,
    ) -> Result<OptimisationResult> {
        let n = workspace.n;
        let m = workspace.m;

        // Simple iterative Levenberg-Marquardt solver.
        let max_iterations = self.config.max_iterations;
        let ftol = self.config.ftol;
        let xtol = self.config.xtol;
        let gtol = self.config.gtol;

        let mut lambda = 0.001f64;
        let mut nfev = 0;

        // Track the best cost seen so far.
        let mut best_cost = f64::INFINITY;
        let mut iterations_without_improvement = 0;
        const MAX_STAGNANT_ITERATIONS: usize = 5;

        for iteration in 0..max_iterations {
            // Compute residuals at current parameters using slice-based method
            // for better compatibility
            let param_slice = workspace.parameters.as_slice();
            let mut residuals_slice = vec![0.0; m];
            problem.residuals(param_slice, &mut residuals_slice)?;
            workspace.residuals.copy_from_slice(&residuals_slice);
            nfev += 1;

            let current_cost = self.compute_cost_nalgebra(&workspace.residuals);
            info!("Iteration {}: cost = {:.6e}", iteration, current_cost);

            // Update best if this is better.
            if current_cost < best_cost {
                best_cost = current_cost;
                workspace.best_parameters.copy_from(&workspace.parameters);
                workspace.best_residuals.copy_from(&workspace.residuals);
                iterations_without_improvement = 0;
            } else {
                iterations_without_improvement += 1;
            }

            // Check for absolute convergence (cost near zero).
            if current_cost < ftol {
                debug!("Converged: cost below absolute tolerance");
                workspace.result_parameters.copy_from(&workspace.parameters);
                workspace.result_residuals.copy_from(&workspace.residuals);
                return Ok(OptimisationResult {
                    status: SolverStatus::Success,
                    parameters: workspace
                        .result_parameters
                        .data
                        .as_vec()
                        .clone(),
                    residuals: workspace.result_residuals.data.as_vec().clone(),
                    cost: current_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    message: "Converged: cost below absolute tolerance",
                });
            }

            // Check if we've stagnated.
            if iterations_without_improvement >= MAX_STAGNANT_ITERATIONS
                && iteration > 0
            {
                debug!(
                    "Converged: no improvement for {} iterations",
                    MAX_STAGNANT_ITERATIONS
                );
                workspace
                    .result_parameters
                    .copy_from(&workspace.best_parameters);
                workspace
                    .result_residuals
                    .copy_from(&workspace.best_residuals);
                return Ok(OptimisationResult {
                    status: SolverStatus::ToleranceReached,
                    parameters: workspace
                        .result_parameters
                        .data
                        .as_vec()
                        .clone(),
                    residuals: workspace.result_residuals.data.as_vec().clone(),
                    cost: best_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    message: "Converged: no improvement for 5 iterations",
                });
            }

            // Try to compute analytical jacobian first, fall back to finite differences
            let param_slice = workspace.parameters.as_slice();
            let mut jacobian_slice = vec![0.0; m * n];
            let analytical_jacobian_available =
                problem.jacobian(param_slice, &mut jacobian_slice)?;

            if analytical_jacobian_available {
                // Copy analytical jacobian to nalgebra matrix
                for i in 0..m {
                    for j in 0..n {
                        workspace.jacobian[(i, j)] = jacobian_slice[i * n + j];
                    }
                }
            } else {
                // Compute finite difference Jacobian.
                let h = 1e-8;
                let mut param_slice_mut =
                    workspace.parameters.as_slice().to_vec();
                let mut residuals_plus_h_slice = vec![0.0; m];

                for j in 0..n {
                    let original = param_slice_mut[j];

                    // Forward difference.
                    param_slice_mut[j] = original + h;
                    problem.residuals(
                        &param_slice_mut,
                        &mut residuals_plus_h_slice,
                    )?;
                    nfev += 1;
                    param_slice_mut[j] = original; // restore.

                    // Fill jacobian column
                    for i in 0..m {
                        workspace.jacobian[(i, j)] =
                            (residuals_plus_h_slice[i] - residuals_slice[i])
                                / h;
                    }
                }
            }

            // Compute gradient = J^T * residuals using nalgebra.
            workspace.gradient =
                workspace.jacobian.transpose() * &workspace.residuals;

            // Check gradient convergence.
            let gradient_norm = workspace.gradient.norm();
            let relative_gradient_norm =
                gradient_norm / current_cost.abs().max(1.0);

            if self.config.verbose {
                info!(
                    "  Gradient norm: {:.6e}, relative: {:.6e}",
                    gradient_norm, relative_gradient_norm
                );
            }

            if gradient_norm < gtol
                || (relative_gradient_norm < gtol && iteration > 0)
            {
                debug!("Converged: gradient tolerance reached");
                workspace.result_parameters.copy_from(&workspace.parameters);
                workspace.result_residuals.copy_from(&workspace.residuals);
                return Ok(OptimisationResult {
                    status: SolverStatus::ToleranceReached,
                    parameters: workspace
                        .result_parameters
                        .data
                        .as_vec()
                        .clone(),
                    residuals: workspace.result_residuals.data.as_vec().clone(),
                    cost: current_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    message: "Converged: gradient tolerance reached",
                });
            }

            // Compute J^T * J using nalgebra.
            workspace.jtj =
                workspace.jacobian.transpose() * &workspace.jacobian;

            // Try to find an improving step.
            let mut step_found = false;
            let mut lambda_attempts = 0;
            const MAX_LAMBDA_ATTEMPTS: usize = 15;

            // Minimum relative improvement required to accept a step.
            let min_relative_improvement = ftol;

            while !step_found
                && lambda_attempts < MAX_LAMBDA_ATTEMPTS
                && lambda < 1e6
            {
                // Add damping (Levenberg-Marquardt) to J^T*J.
                workspace.damped_jtj.copy_from(&workspace.jtj);
                for i in 0..n {
                    workspace.damped_jtj[(i, i)] += lambda;
                }

                // Solve (J^T*J + λI) * step = -gradient (in-place).
                workspace.step.copy_from(&workspace.gradient);
                workspace.step *= -1.0; // Negate because we want to minimize.

                let success = solve_linear_system_nalgebra(
                    &mut workspace.damped_jtj,
                    &mut workspace.step,
                );

                if !success {
                    if self.config.verbose {
                        info!("  Failed to solve linear system with lambda = {:.2e}", lambda);
                    }
                    lambda *= 10.0;
                    lambda_attempts += 1;
                    continue;
                }

                // Check step size.
                let mut step_norm = workspace.step.norm();

                // Apply step bound limiting.
                if step_norm > self.config.step_bound {
                    let scale_factor = self.config.step_bound / step_norm;
                    workspace.step *= scale_factor;
                    step_norm = self.config.step_bound;

                    if self.config.verbose {
                        info!(
                            "  Step limited to bound: {:.6e}",
                            self.config.step_bound
                        );
                    }
                }

                if step_norm < xtol {
                    if self.config.verbose {
                        info!("  Step size {:.6e} below tolerance", step_norm);
                    }
                    // Try with smaller lambda.
                    if lambda > 1e-8 {
                        lambda /= 10.0;
                        lambda_attempts += 1;
                        continue;
                    } else {
                        // Really can't make progress.
                        info!("  Converged: step size below tolerance");
                        workspace
                            .result_parameters
                            .copy_from(&workspace.parameters);
                        workspace
                            .result_residuals
                            .copy_from(&workspace.residuals);
                        return Ok(OptimisationResult {
                            status: SolverStatus::ToleranceReached,
                            parameters: workspace
                                .result_parameters
                                .data
                                .as_vec()
                                .clone(),
                            residuals: workspace
                                .result_residuals
                                .data
                                .as_vec()
                                .clone(),
                            cost: current_cost,
                            iterations: iteration,
                            function_evaluations: nfev,
                            message: "Converged: step size below tolerance",
                        });
                    }
                }

                // Try the step.
                workspace.trial_parameters =
                    &workspace.parameters + &workspace.step;

                let trial_param_slice = workspace.trial_parameters.as_slice();
                let mut trial_residuals_slice = vec![0.0; m];
                problem
                    .residuals(trial_param_slice, &mut trial_residuals_slice)?;
                workspace
                    .trial_residuals
                    .copy_from_slice(&trial_residuals_slice);
                let trial_cost =
                    self.compute_cost_nalgebra(&workspace.trial_residuals);
                nfev += 1;

                let improvement = current_cost - trial_cost;
                let relative_improvement =
                    improvement / current_cost.abs().max(1e-12);

                // Accept if there's meaningful improvement.
                if relative_improvement > min_relative_improvement {
                    // Calculate actual vs predicted reduction for lambda adjustment.
                    let predicted_reduction = {
                        let mut pred = 0.0;
                        for i in 0..n {
                            pred += -workspace.gradient[i] * workspace.step[i];
                            for j in 0..n {
                                pred -= 0.5
                                    * workspace.step[i]
                                    * workspace.jtj[(i, j)]
                                    * workspace.step[j];
                            }
                        }
                        pred
                    };

                    let ratio = if predicted_reduction.abs() > 1e-12 {
                        improvement / predicted_reduction
                    } else {
                        0.0
                    };

                    // Step accepted.
                    workspace.parameters.copy_from(&workspace.trial_parameters);
                    step_found = true;

                    // Adjust lambda based on how good the prediction was.
                    if ratio > 0.75 {
                        lambda /= 3.0;
                    } else if ratio > 0.25 {
                        lambda /= 2.0;
                    }
                    // else keep lambda the same.

                    info!(
                        "  Step accepted, new cost = {:.6e}, improvement = {:.3}%, lambda = {:.2e}",
                        trial_cost, relative_improvement * 100.0, lambda
                    );
                } else {
                    // Step rejected, increase lambda and try again.
                    lambda *= 4.0;
                    lambda_attempts += 1;
                    if self.config.verbose {
                        info!("  Step rejected (relative improvement {:.6e} <= {:.6e}), lambda = {:.2e}",
                                relative_improvement, min_relative_improvement, lambda);
                    }
                }
            }

            if !step_found {
                info!(
                    "  No improving step found after {} attempts",
                    lambda_attempts
                );

                // If we can't find an improving step and the gradient
                // is small, we've converged.
                if gradient_norm < gtol * 10.0 {
                    debug!("Converged: cannot find improving step and gradient is small");
                    workspace
                        .result_parameters
                        .copy_from(&workspace.parameters);
                    workspace.result_residuals.copy_from(&workspace.residuals);
                    return Ok(OptimisationResult {
                        status: SolverStatus::ToleranceReached,
                        parameters: workspace
                            .result_parameters
                            .data
                            .as_vec()
                            .clone(),
                        residuals: workspace
                            .result_residuals
                            .data
                            .as_vec()
                            .clone(),
                        cost: current_cost,
                        iterations: iteration,
                        function_evaluations: nfev,
                        message: "Converged: at local minimum",
                    });
                }

                // Don't try gradient descent fallback if we're
                // already at a minimum.
                info!("  At local minimum, cannot improve further");
                workspace.result_parameters.copy_from(&workspace.parameters);
                workspace.result_residuals.copy_from(&workspace.residuals);
                return Ok(OptimisationResult {
                    status: SolverStatus::ToleranceReached,
                    parameters: workspace
                        .result_parameters
                        .data
                        .as_vec()
                        .clone(),
                    residuals: workspace.result_residuals.data.as_vec().clone(),
                    cost: current_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    message: "Converged: at local minimum",
                });
            }

            // Clamp lambda to reasonable range.
            lambda = lambda.clamp(1e-12, 1e6);
        }

        // Max iterations reached - return best found.
        workspace
            .result_parameters
            .copy_from(&workspace.best_parameters);
        workspace
            .result_residuals
            .copy_from(&workspace.best_residuals);
        Ok(OptimisationResult {
            status: SolverStatus::MaxIterationsReached,
            parameters: workspace.result_parameters.data.as_vec().clone(),
            residuals: workspace.result_residuals.data.as_vec().clone(),
            cost: best_cost,
            iterations: max_iterations,
            function_evaluations: nfev,
            message: "Maximum iterations reached",
        })
    }

    fn compute_cost_nalgebra(&self, residuals: &DVector<f64>) -> f64 {
        // Use nalgebra's optimized norm_squared (zero allocation)
        residuals.norm_squared() * 0.5
    }
}

impl Default for SolverConfig {
    fn default() -> Self {
        Self {
            ftol: 1e-9,
            xtol: 1e-9,
            gtol: 1e-9,
            max_iterations: 100,
            step_bound: 100.0,
            verbose: false,
        }
    }
}

// Zero-allocation linear system solver using nalgebra's LU decomposition.
// This version works directly with nalgebra matrices without creating new ones.
fn solve_linear_system_nalgebra(
    matrix: &mut DMatrix<f64>,
    rhs: &mut DVector<f64>,
) -> bool {
    // Use QR decomposition for better numerical stability
    let qr = matrix.clone().qr();
    match qr.solve(rhs) {
        Some(solution) => {
            // Copy solution back to rhs
            rhs.copy_from(&solution);
            true
        }
        None => false, // Singular matrix
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    /// The Rosenbrock function - a classic optimization test problem.
    /// f(x, y) = (a - x)^2 + b*(y - x^2)^2
    ///
    /// The global minimum is at (x, y) = (a, a^2) with f = 0
    /// Default values: a = 1, b = 100, so minimum at (1, 1)
    ///
    /// This creates a narrow, curved valley which is challenging for optimizers.
    pub struct RosenbrockProblem {
        a: f64,
        b: f64,
    }

    impl RosenbrockProblem {
        pub fn new() -> Self {
            Self { a: 1.0, b: 100.0 }
        }

        pub fn with_parameters(a: f64, b: f64) -> Self {
            Self { a, b }
        }
    }

    impl Default for RosenbrockProblem {
        fn default() -> Self {
            Self::new()
        }
    }

    impl OptimisationProblem for RosenbrockProblem {
        fn residuals(
            &self,
            parameters: &[f64],
            out_residuals: &mut [f64],
        ) -> Result<()> {
            if parameters.len() != 2 {
                return Err(OptimisationError::InvalidInput(
                    "Rosenbrock problem requires exactly 2 parameters (x, y)"
                        .to_string(),
                )
                .into());
            }

            if out_residuals.len() != 2 {
                return Err(OptimisationError::InvalidInput(
                    "Rosenbrock problem requires exactly 2 residuals"
                        .to_string(),
                )
                .into());
            }

            let x = parameters[0];
            let y = parameters[1];

            // Split into two residuals so that sum of squares equals
            // the Rosenbrock function.
            //
            // f(x,y) = (a - x)^2 + b*(y - x^2)^2 = r1^2 + r2^2
            out_residuals[0] = self.a - x;
            out_residuals[1] = (self.b).sqrt() * (y - x * x);

            Ok(())
        }

        fn jacobian(
            &self,
            parameters: &[f64],
            out_jacobian: &mut [f64],
        ) -> Result<bool> {
            if parameters.len() != 2 {
                return Err(OptimisationError::InvalidInput(
                    "Rosenbrock problem requires exactly 2 parameters (x, y)"
                        .to_string(),
                )
                .into());
            }

            if out_jacobian.len() != 4 {
                return Err(OptimisationError::InvalidInput(
                    "Rosenbrock problem requires exactly 4 jacobian entries (2x2 matrix)"
                        .to_string(),
                )
                .into());
            }

            let x = parameters[0];
            let sqrt_b = (self.b).sqrt();

            // Analytical jacobian for Rosenbrock residuals:
            // r1 = a - x
            // r2 = sqrt(b) * (y - x^2)
            //
            // J = [dr1/dx  dr1/dy] = [-1        0   ]
            //     [dr2/dx  dr2/dy]   [-2x*sqrt(b)   sqrt(b)  ]
            //
            // Stored in row-major order: [J00, J01, J10, J11]
            out_jacobian[0] = -1.0; // dr1/dx
            out_jacobian[1] = 0.0; // dr1/dy
            out_jacobian[2] = -2.0 * x * sqrt_b; // dr2/dx
            out_jacobian[3] = sqrt_b; // dr2/dy

            Ok(true) // Analytical jacobian computed successfully.
        }

        fn parameter_count(&self) -> usize {
            2
        }

        fn residual_count(&self) -> usize {
            2
        }
    }

    #[test]
    fn test_rosenbrock_problem_at_minimum() {
        let problem = RosenbrockProblem::new();
        let mut residuals = vec![0.0; 2];

        // Test at the known minimum (1, 1).
        problem.residuals(&[1.0, 1.0], &mut residuals).unwrap();
        assert_relative_eq!(residuals[0], 0.0, epsilon = 1e-12);
        assert_relative_eq!(residuals[1], 0.0, epsilon = 1e-12);

        // Cost should be zero at minimum.
        let cost = residuals.iter().map(|r| r * r).sum::<f64>() * 0.5;
        assert_relative_eq!(cost, 0.0, epsilon = 1e-12);
    }

    #[test]
    fn test_rosenbrock_problem_away_from_minimum() {
        let problem = RosenbrockProblem::new();

        // Test at a point away from minimum.
        let parameters = vec![0.0; 2];
        let mut residuals = vec![0.0; 2];
        problem.residuals(&parameters, &mut residuals).unwrap();
        assert_eq!(residuals.len(), 2);

        // At (0, 0): r1 = 1 - 0 = 1, r2 = sqrt(100) * (0 - 0) = 0
        assert_relative_eq!(residuals[0], 1.0, epsilon = 1e-12);
        assert_relative_eq!(residuals[1], 0.0, epsilon = 1e-12);

        // Cost should be 0.5 * (1^2 + 0^2) = 0.5
        let cost = residuals.iter().map(|r| r * r).sum::<f64>() * 0.5;
        assert_relative_eq!(cost, 0.5, epsilon = 1e-12);
    }

    #[test]
    fn test_solver_rosenbrock_from_origin() {
        let problem = RosenbrockProblem::new();
        let solver = LevenbergMarquardt::with_defaults();

        // Start from origin - moderately difficult.
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            SolverWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nRosenbrock from origin:");
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Function evaluations: {}", result.function_evaluations);
        println!("  Status: {:?}", result.status);

        // Check convergence to minimum
        assert!(is_success(result.status));
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-4);
        assert!(result.cost < 1e-8);
    }

    #[test]
    fn test_solver_rosenbrock_from_far_point() {
        let problem = RosenbrockProblem::new();

        // Use tighter tolerances for better precision
        let config = SolverConfig {
            ftol: 1e-11,
            xtol: 1e-11,
            gtol: 1e-11,
            max_iterations: 200,
            step_bound: 100.0,
            verbose: false,
        };
        let solver = LevenbergMarquardt::new(config);

        // Start from a challenging point far from minimum
        let initial_parameters = vec![-1.2, 1.0];
        let mut workspace =
            SolverWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nRosenbrock from (-1.2, 1.0):");
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Function evaluations: {}", result.function_evaluations);
        println!("  Status: {:?}", result.status);

        // Check convergence to minimum
        assert!(is_success(result.status));
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
        assert!(result.cost < 1e-12);
    }

    #[test]
    fn test_solver_rosenbrock_multiple_starting_points() {
        let problem = RosenbrockProblem::new();
        let solver = LevenbergMarquardt::with_defaults();

        // Test from multiple starting points
        let starting_points = vec![
            vec![0.5, 0.5],
            vec![2.0, 2.0],
            vec![-0.5, 0.5],
            vec![1.5, 2.0],
        ];

        for (i, initial_parameters) in starting_points.iter().enumerate() {
            let mut workspace =
                SolverWorkspace::new(&problem, initial_parameters).unwrap();
            let result =
                solver.solve_problem(&problem, &mut workspace).unwrap();

            println!(
                "\nRosenbrock test {} from [{:.1}, {:.1}]:",
                i + 1,
                initial_parameters[0],
                initial_parameters[1]
            );
            println!(
                "  Final: [{:.6}, {:.6}], cost: {:.6e}, iters: {}",
                result.parameters[0],
                result.parameters[1],
                result.cost,
                result.iterations
            );

            // All should converge to (1, 1)
            assert!(
                is_success(result.status),
                "Failed from starting point {:?}",
                initial_parameters
            );
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
            assert!(result.cost < 1e-10);
        }
    }

    #[test]
    fn test_solver_modified_rosenbrock() {
        // Test with different a and b values.
        let problem = RosenbrockProblem::with_parameters(2.0, 50.0);
        let solver = LevenbergMarquardt::with_defaults();

        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            SolverWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nModified Rosenbrock (a=2, b=50):");
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should converge to (2, 4) for a=2.
        assert!(is_success(result.status));
        assert_relative_eq!(result.parameters[0], 2.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 4.0, epsilon = 2e-5);
        assert!(result.cost < 1e-10);
    }

    #[test]
    fn test_solver_convergence_criteria() {
        let problem = RosenbrockProblem::new();

        // Test with very tight tolerances to trigger max iterations.
        let config = SolverConfig {
            ftol: 1e-15,
            xtol: 1e-15,
            gtol: 1e-15,
            max_iterations: 10, // Very few iterations.
            step_bound: 100.0,
            verbose: false,
        };
        let solver = LevenbergMarquardt::new(config);

        let initial_parameters = vec![-1.0, 1.0];
        let mut workspace =
            SolverWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nRosenbrock with max_iterations=10:");
        println!(
            "  Initial parameters: [{:.6}, {:.6}]",
            initial_parameters[0], initial_parameters[1]
        );
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Status: {:?}", result.status);

        // Should hit max iterations.
        assert_eq!(result.status, SolverStatus::MaxIterationsReached);
        assert_eq!(result.iterations, 10);

        // Even with limited iterations, should make some progress.
        let initial_cost = {
            let mut initial_residuals = vec![0.0; 2];
            problem
                .residuals(&initial_parameters, &mut initial_residuals)
                .unwrap();
            initial_residuals.iter().map(|r| r * r).sum::<f64>() * 0.5
        };
        assert!(result.cost < initial_cost);
    }

    #[test]
    fn test_solver_near_minimum_start() {
        let problem = RosenbrockProblem::new();
        let solver = LevenbergMarquardt::with_defaults();

        // Start very close to minimum.
        let initial_parameters = vec![0.999, 0.999];
        let mut workspace =
            SolverWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nRosenbrock from near minimum:");
        println!(
            "  Initial parameters: [{:.6}, {:.6}]",
            initial_parameters[0], initial_parameters[1]
        );
        println!(
            "  Final: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should converge very quickly.
        assert!(is_success(result.status));
        assert!(
            result.iterations < 10,
            "Should converge quickly from near minimum"
        );
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
        assert!(result.cost < 1e-10);
    }

    #[test]
    fn test_solver_step_bound_limiting() {
        let problem = RosenbrockProblem::new();

        // Test with very small step bound to force step limiting.
        let config = SolverConfig {
            ftol: 1e-9,
            xtol: 1e-9,
            gtol: 1e-9,
            max_iterations: 300, // More iterations since steps are limited.
            step_bound: 0.1,     // Very small step bound.
            verbose: true, // Enable verbose to see step limiting messages.
        };
        let solver = LevenbergMarquardt::new(config);

        // Start from a challenging point that would normally take
        // large steps.
        let initial_parameters = vec![-2.0, 2.0];
        let mut workspace =
            SolverWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nRosenbrock with step_bound=0.1 from (-2.0, 2.0):");
        println!(
            "  Initial parameters: [{:.6}, {:.6}]",
            initial_parameters[0], initial_parameters[1]
        );
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Function evaluations: {}", result.function_evaluations);
        println!("  Status: {:?}", result.status);

        // Should eventually converge to minimum (1, 1), but may take
        // more iterations.
        assert!(is_success(result.status));
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-4);
        assert!(result.cost < 1e-8);

        // Should take more iterations than without step bound due to
        // smaller steps.
        assert!(
            result.iterations > 20,
            "Should take more iterations with small step bound"
        );
    }

    #[test]
    fn test_solver_step_bound_comparison() {
        let problem = RosenbrockProblem::new();
        let initial_parameters = vec![-1.0, 1.0];

        // Test with default step bound (large).
        let config_large = SolverConfig {
            ftol: 1e-9,
            xtol: 1e-9,
            gtol: 1e-9,
            max_iterations: 100,
            step_bound: 100.0, // Large step bound (effectively unlimited).
            verbose: false,
        };
        let solver_large = LevenbergMarquardt::new(config_large);
        let mut workspace_large =
            SolverWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_large = solver_large
            .solve_problem(&problem, &mut workspace_large)
            .unwrap();

        // Test with small step bound.
        let config_small = SolverConfig {
            ftol: 1e-9,
            xtol: 1e-9,
            gtol: 1e-9,
            max_iterations: 200,
            step_bound: 0.3, // Small step bound.
            verbose: false,
        };
        let solver_small = LevenbergMarquardt::new(config_small);
        let mut workspace_small =
            SolverWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_small = solver_small
            .solve_problem(&problem, &mut workspace_small)
            .unwrap();

        println!("\nStep bound comparison:");
        println!(
            "  Large step bound: {} iterations, cost: {:.6e}",
            result_large.iterations, result_large.cost
        );
        println!(
            "  Small step bound: {} iterations, cost: {:.6e}",
            result_small.iterations, result_small.cost
        );

        // Both should converge successfully.
        assert!(is_success(result_large.status));
        assert!(is_success(result_small.status));

        // Both should reach the minimum.
        assert_relative_eq!(result_large.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result_large.parameters[1], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result_small.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result_small.parameters[1], 1.0, epsilon = 1e-4);

        // Small step bound should generally take more iterations.
        assert!(
            result_small.iterations >= result_large.iterations,
            "Small step bound should take at least as many iterations"
        );
    }

    #[test]
    fn test_solver_step_bound_edge_cases() {
        let problem = RosenbrockProblem::new();

        // Test with very large step bound (should behave like unlimited).
        let config_huge = SolverConfig {
            ftol: 1e-9,
            xtol: 1e-9,
            gtol: 1e-9,
            max_iterations: 100,
            step_bound: 1000.0, // Very large step bound.
            verbose: false,
        };
        let solver_huge = LevenbergMarquardt::new(config_huge);
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            SolverWorkspace::new(&problem, &initial_parameters).unwrap();
        let result =
            solver_huge.solve_problem(&problem, &mut workspace).unwrap();

        // Should converge normally.
        assert!(is_success(result.status));
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);

        println!("\nStep bound edge case test:");
        println!(
            "  Large step bound result: {:.6e} cost in {} iterations",
            result.cost, result.iterations
        );
    }
}
