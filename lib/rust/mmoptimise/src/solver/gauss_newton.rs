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

use crate::solver::common::*;
use anyhow::Result;
use log::{debug, info, warn};
use mmcore::dual::Dual;
use nalgebra::{DMatrix, DVector};
use num_traits::Float;

/// Workspace for the Gauss-Newton solver.
///
/// Contains only the necessary pre-allocated memory for Gauss-Newton
/// optimization, avoiding the trust region management structures needed
/// by Levenberg-Marquardt.
#[derive(Debug)]
pub struct GaussNewtonWorkspace {
    // Problem dimensions.
    n: usize, // number of parameters.
    m: usize, // number of residuals.

    // Pre-allocated nalgebra matrices and vectors.
    pub parameters: DVector<f64>,
    pub trial_parameters: DVector<f64>,
    pub best_parameters: DVector<f64>,
    residuals: DVector<f64>,
    trial_residuals: DVector<f64>,
    best_residuals: DVector<f64>,
    jacobian: DMatrix<f64>,

    // Normal equations workspace.
    normal_matrix: DMatrix<f64>, // J^T * J (n x n)
    gradient: DVector<f64>,      // J^T * residuals (n x 1)

    // Step computation workspace.
    step: DVector<f64>,
    scaling: DVector<f64>, // Parameter scaling factors
}

impl GaussNewtonWorkspace {
    /// Create a new workspace for Gauss-Newton optimization.
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

        if m < n {
            return Err(OptimisationError::InvalidInput(
                "Number of residuals must be >= number of parameters"
                    .to_string(),
            )
            .into());
        }

        Ok(Self {
            n,
            m,
            parameters: DVector::from_row_slice(initial_parameters),
            trial_parameters: DVector::from_row_slice(initial_parameters),
            best_parameters: DVector::from_row_slice(initial_parameters),
            residuals: DVector::zeros(m),
            trial_residuals: DVector::zeros(m),
            best_residuals: DVector::zeros(m),
            jacobian: DMatrix::zeros(m, n),
            normal_matrix: DMatrix::zeros(n, n),
            gradient: DVector::zeros(n),
            step: DVector::zeros(n),
            scaling: DVector::from_element(n, 1.0),
        })
    }

    /// Reuse an existing workspace with new initial parameters.
    ///
    /// Allows reusing the allocated memory as long as the problem
    /// dimensions match. All workspace data is properly reset.
    pub fn reuse_with<P: OptimisationProblem>(
        &mut self,
        problem: &P,
        initial_parameters: &[f64],
    ) -> Result<()> {
        let n = problem.parameter_count();
        let m = problem.residual_count();

        if n != self.n {
            return Err(OptimisationError::InvalidInput(format!(
                "Parameter count mismatch: workspace has {}, problem has {}",
                self.n, n
            ))
            .into());
        }

        if m != self.m {
            return Err(OptimisationError::InvalidInput(format!(
                "Residual count mismatch: workspace has {}, problem has {}",
                self.m, m
            ))
            .into());
        }

        if initial_parameters.len() != n {
            return Err(OptimisationError::InvalidInput(format!(
                "Expected {} parameters, got {}",
                n,
                initial_parameters.len()
            ))
            .into());
        }

        // Update parameter vectors with new initial values.
        self.parameters.copy_from_slice(initial_parameters);
        self.trial_parameters.copy_from_slice(initial_parameters);
        self.best_parameters.copy_from_slice(initial_parameters);

        // Reset all workspace data without reallocating memory.
        self.residuals.fill(0.0);
        self.trial_residuals.fill(0.0);
        self.best_residuals.fill(0.0);
        self.jacobian.fill(0.0);
        self.normal_matrix.fill(0.0);
        self.gradient.fill(0.0);
        self.step.fill(0.0);
        self.scaling.fill(1.0);

        Ok(())
    }

    /// Get the number of parameters.
    pub fn parameter_count(&self) -> usize {
        self.n
    }

    /// Get the number of residuals.
    pub fn residual_count(&self) -> usize {
        self.m
    }
}

/// Configuration parameters for the Gauss-Newton solver.
///
/// Gauss-Newton is simpler than Levenberg-Marquardt, requiring fewer
/// configuration parameters since there's no trust region management.
///
/// ## When to Use Gauss-Newton vs Levenberg-Marquardt
///
/// | Use Gauss-Newton When             | Use Levenberg-Marquardt When |
/// |-----------------------------------+------------------------------|
/// | Problem is well-conditioned       | Problem is ill-conditioned   |
/// | Good initial guess available      | Far from optimum             |
/// | Near-quadratic objective function | Highly nonlinear objective   |
/// | Speed is critical                 | Robustness is critical       |
/// | Residuals are small at solution   | Large residuals expected     |
/// |-----------------------------------+------------------------------|
///
/// ## Configuration Guidelines
///
/// ```rust
/// # use mmoptimise_rust::solver::gauss_newton::GaussNewtonConfig;
/// # use mmoptimise_rust::solver::common::ParameterScalingMode;
/// // Standard configuration for well-conditioned problems
/// let config = GaussNewtonConfig::default();
///
/// // High-precision configuration
/// let precise_config = GaussNewtonConfig {
///     function_tolerance: 1e-12,
///     parameter_tolerance: 1e-12,
///     gradient_tolerance: 1e-12,
///     max_iterations: 100,
///     scaling_mode: ParameterScalingMode::Auto,
///     ..Default::default()
/// };
///
/// // Fast approximation
/// let fast_config = GaussNewtonConfig {
///     function_tolerance: 1e-4,
///     parameter_tolerance: 1e-4,
///     gradient_tolerance: 1e-4,
///     max_iterations: 20,
///     ..Default::default()
/// };
///
/// // Custom line search configuration
/// let custom_line_search_config = GaussNewtonConfig {
///     armijo_constant: 1e-3,           // Less strict sufficient decrease.
///     max_line_search_iterations: 25,  // More line search attempts.
///     min_step_size: 1e-12,            // Allow smaller steps.
///     ..Default::default()
/// };
///
/// // Robust configuration for difficult problems
/// let robust_config = GaussNewtonConfig {
///     regularization_threshold: 1e-12,        // Apply regularization more readily.
///     min_adaptive_regularization: 1e-8,      // Higher minimum regularization.
///     adaptive_recovery_step_fraction: 0.05,  // More conservative recovery steps.
///     ..Default::default()
/// };
///
/// // Verify configurations work
/// assert_eq!(config.function_tolerance, 1e-6);
/// assert_eq!(precise_config.max_iterations, 100);
/// assert_eq!(fast_config.max_iterations, 20);
/// ```
#[derive(Debug, Clone, Copy)]
pub struct GaussNewtonConfig {
    /// Function tolerance. Convergence when relative reduction in
    /// cost is below this.
    pub function_tolerance: f64,
    /// Parameter tolerance. Convergence when relative change in
    /// parameters is below this.
    pub parameter_tolerance: f64,
    /// Gradient tolerance. Convergence when gradient norm is below
    /// this.
    pub gradient_tolerance: f64,
    /// Maximum number of iterations.
    pub max_iterations: usize,
    /// Maximum number of function evaluations.
    pub max_function_evaluations: usize,
    /// Scaling mode for parameters.
    pub scaling_mode: ParameterScalingMode,
    /// Enable verbose output.
    pub verbose: bool,
    /// Machine epsilon multiplier for numerical tolerances.
    pub epsilon_factor: f64,
    /// Regularization parameter for numerical stability (small
    /// positive value).
    pub regularization: f64,
    /// Threshold above which regularization is applied to normal
    /// matrix.
    pub regularization_threshold: f64,
    /// Armijo condition parameter for sufficient decrease in line
    /// search (typically 1e-4).
    pub armijo_constant: f64,
    /// Minimum acceptable step size in line search before
    /// termination.
    pub min_step_size: f64,
    /// Minimum regularization value used in adaptive regularization
    /// recovery.
    pub min_adaptive_regularization: f64,
    /// Step size fraction used in adaptive regularization recovery
    /// attempts.
    pub adaptive_recovery_step_fraction: f64,
    /// Maximum number of line search iterations before giving up.
    pub max_line_search_iterations: usize,
}

impl Default for GaussNewtonConfig {
    fn default() -> Self {
        let machine_epsilon = f64::EPSILON;

        Self {
            function_tolerance: 1e-6,
            parameter_tolerance: 1e-6,
            gradient_tolerance: 1e-6,
            max_iterations: 100, // Fewer iterations than LM since no trust region.
            max_function_evaluations: 1000,
            scaling_mode: ParameterScalingMode::Auto,
            verbose: false,
            epsilon_factor: 1.0,
            regularization: 1e-10, // Small regularization for numerical stability.
            // Threshold for applying regularization.
            regularization_threshold: machine_epsilon.sqrt(),
            // Standard Armijo condition parameter for sufficient decrease.
            armijo_constant: 1e-4,
            // Minimum step size.
            min_step_size: machine_epsilon.powf(0.25),
            // Minimum adaptive regularization.
            min_adaptive_regularization: machine_epsilon.sqrt(),
            // Conservative step fraction for adaptive recovery.
            adaptive_recovery_step_fraction: 0.1,
            // Reasonable number of line search iterations.
            max_line_search_iterations: 15,
        }
    }
}

/// Gauss-Newton solver for non-linear least squares optimization.
///
/// A simplified version of the Levenberg-Marquardt algorithm without
/// trust region management. It's faster and simpler but less robust
/// for ill-conditioned or highly nonlinear problems.
///
/// ## Algorithm Overview
///
/// The Gauss-Newton method iteratively solves:
/// ```text
/// (J^T J) Δp = -J^T r
/// p_{k+1} = p_k + Δp
/// ```
/// where J is the Jacobian and r is the residual vector.
///
/// ## Usage Example
///
/// ```rust
/// # use mmoptimise_rust::solver::gauss_newton::GaussNewtonConfig;
/// # use mmoptimise_rust::solver::gauss_newton::GaussNewtonSolver;
/// # use mmoptimise_rust::solver::gauss_newton::GaussNewtonWorkspace;
/// # use mmoptimise_rust::solver::test_problems::RosenbrockProblem;
/// # use anyhow::Result;
/// # fn main() -> Result<()> {
/// // For well-conditioned problems near the solution.
/// let solver = GaussNewtonSolver::with_defaults();
/// let problem = RosenbrockProblem::new();
/// let initial_params = vec![0.8, 0.8];
/// let mut workspace = GaussNewtonWorkspace::new(&problem, &initial_params)?;
/// let result = solver.solve_problem(&problem, &mut workspace)?;
///
/// if result.status.is_success() {
///     println!("Converged to: {:?}", result.parameters);
/// }
/// # Ok(())
/// # }
/// ```
///
/// ## When Gauss-Newton Fails
///
/// The solver may fail or converge slowly when:
/// - The Jacobian is rank-deficient (use regularization or switch to LM).
/// - Far from the optimum (use better initial guess or switch to LM).
/// - Highly nonlinear problem (switch to LM).
/// - Large residuals at solution (switch to LM).
///
/// ## Performance Tips
///
/// - **Initial Guess**: Gauss-Newton is very sensitive to initial parameters.
/// - **Scaling**: Use `ParameterScalingMode::Auto` for problems with different parameter scales.
/// - **Regularization**: Increase if encountering numerical instabilities.
/// - **Workspace Reuse**: Reuse workspace for multiple similar problems.
pub struct GaussNewtonSolver {
    config: GaussNewtonConfig,
}

impl GaussNewtonSolver {
    pub fn new(config: GaussNewtonConfig) -> Self {
        Self { config }
    }

    pub fn with_defaults() -> Self {
        Self {
            config: GaussNewtonConfig::default(),
        }
    }

    /// Compute the cost from residuals (0.5 * sum of squares).
    fn compute_cost(&self, residuals: &DVector<f64>) -> f64 {
        0.5 * residuals.norm_squared()
    }

    /// Check if parameters contain NaN or infinite values.
    fn validate_parameters(&self, parameters: &DVector<f64>) -> Result<()> {
        for (i, &param) in parameters.iter().enumerate() {
            if !param.is_finite() {
                return Err(OptimisationError::SolverError(format!(
                    "Parameter {} is not finite: {}",
                    i, param
                ))
                .into());
            }
        }
        Ok(())
    }

    /// Compute the Jacobian using automatic differentiation.
    fn compute_jacobian<P: OptimisationProblem>(
        &self,
        problem: &P,
        workspace: &mut GaussNewtonWorkspace,
    ) -> Result<usize> {
        let n = workspace.n;
        let m = workspace.m;
        let mut nfev = 0;

        // Create dual number parameters.
        let mut dual_parameters = DVector::<Dual<f64>>::zeros(n);
        for i in 0..n {
            dual_parameters[i] = Dual::new(workspace.parameters[i], 0.0);
        }

        // Compute Jacobian column by column.
        for j in 0..n {
            dual_parameters[j].dual = 1.0;

            let mut dual_residuals = DVector::<Dual<f64>>::zeros(m);
            problem.residuals(
                dual_parameters.as_slice(),
                dual_residuals.as_mut_slice(),
            )?;
            nfev += 1;

            for i in 0..m {
                let jacobian_entry = dual_residuals[i].dual;
                if !jacobian_entry.is_finite() {
                    warn!(
                        "Non-finite Jacobian entry at ({}, {}): {}",
                        i, j, jacobian_entry
                    );
                    workspace.jacobian[(i, j)] = 0.0;
                } else {
                    workspace.jacobian[(i, j)] = jacobian_entry;
                }
            }

            dual_parameters[j].dual = 0.0;
        }

        Ok(nfev)
    }

    /// Solve the Gauss-Newton normal equations:
    /// (J^T J) step = -J^T r
    fn solve_normal_equations(
        &self,
        workspace: &mut GaussNewtonWorkspace,
    ) -> Result<bool> {
        let n = workspace.n;
        let machine_epsilon = f64::EPSILON * self.config.epsilon_factor;

        // Compute J^T J (normal matrix) - store in workspace.
        workspace.normal_matrix =
            workspace.jacobian.transpose() * &workspace.jacobian;

        // Use the gradient that was already computed in solve_problem.
        let neg_gradient = -&workspace.gradient;

        // Add regularization to diagonal for numerical stability (only if significant).
        if self.config.regularization > self.config.regularization_threshold {
            for i in 0..n {
                let scale = workspace.scaling[i];
                workspace.normal_matrix[(i, i)] +=
                    self.config.regularization * scale * scale;
            }
        }

        // Try Cholesky decomposition first (faster if matrix is positive definite).
        if let Some(chol) = workspace.normal_matrix.clone().cholesky() {
            workspace.step = chol.solve(&neg_gradient);
            return Ok(true);
        }

        // Fall back to QR decomposition if Cholesky fails.
        let qr = workspace.normal_matrix.clone().qr();

        // Check condition number using R diagonal elements.
        let r = qr.r();
        let r_diag = r.diagonal();
        let max_diag = r_diag.iter().fold(0.0, |a, &b| a.max(b.abs()));
        let min_diag =
            r_diag.iter().fold(f64::INFINITY, |a, &b| a.min(b.abs()));

        if min_diag < machine_epsilon * max_diag {
            warn!(
                "Near-singular normal matrix, condition number > {:.2e}",
                max_diag / min_diag
            );
            return Ok(false);
        }

        // Use QR solver for better numerical stability.
        match qr.solve(&neg_gradient) {
            Some(solution) => {
                workspace.step = solution;
            }
            None => {
                warn!("QR decomposition failed to solve system");
                return Ok(false);
            }
        }

        Ok(true)
    }

    /// Update parameter scaling based on Jacobian column norms.
    fn update_scaling(&self, workspace: &mut GaussNewtonWorkspace) {
        let n = workspace.n;

        match self.config.scaling_mode {
            ParameterScalingMode::None => {
                workspace.scaling.fill(1.0);
            }
            ParameterScalingMode::Auto => {
                // Scale by column norms of Jacobian.
                for j in 0..n {
                    let col_norm = workspace.jacobian.column(j).norm();
                    if col_norm > f64::EPSILON {
                        workspace.scaling[j] =
                            workspace.scaling[j].max(col_norm);
                    }
                }
            }
            ParameterScalingMode::Manual => {
                // User has provided scaling, keep it unchanged.
            }
        }
    }

    /// Main solver routine
    pub fn solve_problem<P: OptimisationProblem>(
        &self,
        problem: &P,
        workspace: &mut GaussNewtonWorkspace,
    ) -> Result<OptimisationResult> {
        let n = workspace.n;
        let machine_epsilon = f64::EPSILON * self.config.epsilon_factor;

        // Initialize counters.
        let mut nfev = 0;
        let mut njev = 0;

        // Initial function evaluation.
        problem.residuals(
            workspace.parameters.as_slice(),
            workspace.residuals.as_mut_slice(),
        )?;
        nfev += 1;
        let mut current_cost = self.compute_cost(&workspace.residuals);
        let mut previous_cost = current_cost;

        if !current_cost.is_finite() {
            return Err(OptimisationError::SolverError(
                "Initial cost is not finite".to_string(),
            )
            .into());
        }

        // Store best solution.
        let mut best_cost = current_cost;
        workspace.best_parameters.copy_from(&workspace.parameters);
        workspace.best_residuals.copy_from(&workspace.residuals);

        // Main iteration loop.
        for iteration in 0..self.config.max_iterations {
            if self.config.verbose {
                info!(
                    "Gauss-Newton Iteration {}: cost = {:.6e}",
                    iteration, current_cost
                );
            }

            // Check for absolute cost convergence.
            if current_cost < machine_epsilon.sqrt() {
                debug!("Converged: cost near zero");
                return Ok(OptimisationResult {
                    status: SolverStatus::Success,
                    parameters: workspace.parameters.as_slice().to_vec(),
                    residuals: workspace.residuals.as_slice().to_vec(),
                    cost: current_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    jacobian_evaluations: njev,
                    message: "Converged: cost near machine precision",
                });
            }

            // Check for relative cost improvement.
            if iteration > 0 && previous_cost > current_cost {
                let relative_improvement =
                    (previous_cost - current_cost) / previous_cost.max(1.0);
                if relative_improvement < self.config.function_tolerance {
                    debug!(
                        "Converged: relative cost improvement below tolerance"
                    );
                    return Ok(OptimisationResult {
                        status: SolverStatus::ToleranceReached,
                        parameters: workspace.parameters.as_slice().to_vec(),
                        residuals: workspace.residuals.as_slice().to_vec(),
                        cost: current_cost,
                        iterations: iteration,
                        function_evaluations: nfev,
                        jacobian_evaluations: njev,
                        message: "Converged: relative cost improvement below tolerance",
                    });
                }
            }

            // Compute Jacobian.
            let jac_evals = self.compute_jacobian(problem, workspace)?;
            nfev += jac_evals;
            njev += 1;

            // Compute gradient for convergence check.
            workspace.gradient =
                workspace.jacobian.transpose() * &workspace.residuals;

            // Update scaling on first iteration or if requested.
            if iteration == 0
                || self.config.scaling_mode == ParameterScalingMode::Auto
            {
                self.update_scaling(workspace);
            }

            // Compute gradient norm for convergence check.
            let gradient_norm =
                workspace.gradient.norm() / current_cost.max(1.0);
            if gradient_norm < self.config.gradient_tolerance {
                debug!("Converged: gradient norm below tolerance");
                return Ok(OptimisationResult {
                    status: SolverStatus::SmallGradient,
                    parameters: workspace.parameters.as_slice().to_vec(),
                    residuals: workspace.residuals.as_slice().to_vec(),
                    cost: current_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    jacobian_evaluations: njev,
                    message: "Converged: gradient norm below tolerance",
                });
            }

            // Solve for step using Gauss-Newton normal equations.
            let step_computed = self.solve_normal_equations(workspace)?;

            if !step_computed {
                warn!("Failed to compute step at iteration {}", iteration);
                // Return best solution found so far.
                return Ok(OptimisationResult {
                    status: SolverStatus::SmallStepSize,
                    parameters: workspace.best_parameters.as_slice().to_vec(),
                    residuals: workspace.best_residuals.as_slice().to_vec(),
                    cost: best_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    jacobian_evaluations: njev,
                    message: "Failed: singular normal matrix detected",
                });
            }

            // Validate computed step for NaN/Inf values.
            if let Err(e) = self.validate_parameters(&workspace.step) {
                warn!(
                    "Invalid step computed at iteration {}: {}",
                    iteration, e
                );
                return Ok(OptimisationResult {
                    status: SolverStatus::SmallStepSize,
                    parameters: workspace.best_parameters.as_slice().to_vec(),
                    residuals: workspace.best_residuals.as_slice().to_vec(),
                    cost: best_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    jacobian_evaluations: njev,
                    message:
                        "Failed: invalid step computed (NaN or Inf values)",
                });
            }

            // Enhanced line search with Armijo condition.
            let mut alpha = 1.0;
            let max_line_search = self.config.max_line_search_iterations;
            let mut line_search_success = false;
            let c1 = self.config.armijo_constant;

            // Compute directional derivative for Armijo condition.
            let directional_derivative =
                workspace.gradient.dot(&workspace.step);

            for _ls_iter in 0..max_line_search {
                // Compute trial point.
                for i in 0..n {
                    workspace.trial_parameters[i] =
                        workspace.parameters[i] + alpha * workspace.step[i];
                }

                // Evaluate at trial point.
                problem.residuals(
                    workspace.trial_parameters.as_slice(),
                    workspace.trial_residuals.as_mut_slice(),
                )?;
                nfev += 1;

                let trial_cost = self.compute_cost(&workspace.trial_residuals);

                // Armijo condition: sufficient decrease.
                let armijo_threshold =
                    current_cost + c1 * alpha * directional_derivative;
                if trial_cost <= armijo_threshold && trial_cost < current_cost {
                    // Validate trial parameters before accepting.
                    if let Err(e) =
                        self.validate_parameters(&workspace.trial_parameters)
                    {
                        warn!("Trial parameters are invalid: {}", e);
                        alpha *= 0.5;
                        if alpha < self.config.min_step_size {
                            break;
                        }
                        continue;
                    }

                    // Accept step.
                    workspace.parameters.copy_from(&workspace.trial_parameters);
                    workspace.residuals.copy_from(&workspace.trial_residuals);
                    previous_cost = current_cost;
                    current_cost = trial_cost;
                    line_search_success = true;

                    // Update best solution.
                    if current_cost < best_cost {
                        best_cost = current_cost;
                        workspace
                            .best_parameters
                            .copy_from(&workspace.parameters);
                        workspace
                            .best_residuals
                            .copy_from(&workspace.residuals);
                    }
                    break;
                }

                // Adaptive step size reduction.
                if trial_cost >= current_cost * 2.0 {
                    // Large increase in cost, reduce step size aggressively.
                    alpha *= 0.1;
                } else {
                    // Moderate reduction.
                    alpha *= 0.5;
                }

                if alpha < self.config.min_step_size {
                    break;
                }

                // Check function evaluation limit.
                if nfev >= self.config.max_function_evaluations {
                    return Ok(OptimisationResult {
                        status: SolverStatus::FunctionCallsExceeded,
                        parameters: workspace
                            .best_parameters
                            .as_slice()
                            .to_vec(),
                        residuals: workspace.best_residuals.as_slice().to_vec(),
                        cost: best_cost,
                        iterations: iteration,
                        function_evaluations: nfev,
                        jacobian_evaluations: njev,
                        message:
                            "Terminated: function evaluation limit exceeded",
                    });
                }
            }

            if !line_search_success {
                // Line search failed - try adaptive regularization.
                debug!("Line search failed at iteration {}", iteration);

                // Try increasing regularization and recomputing step.
                let original_regularization = self.config.regularization;
                let adaptive_regularization = (original_regularization * 10.0)
                    .max(self.config.min_adaptive_regularization);

                // Create a temporary config with increased regularization.
                let mut adaptive_config = self.config;
                adaptive_config.regularization = adaptive_regularization;
                let adaptive_solver = GaussNewtonSolver::new(adaptive_config);

                // Try computing step with adaptive regularization.
                let adaptive_step_computed =
                    adaptive_solver.solve_normal_equations(workspace)?;

                if adaptive_step_computed {
                    // Try a small step with the adaptive regularization.
                    let small_alpha =
                        self.config.adaptive_recovery_step_fraction;
                    for i in 0..workspace.parameters.len() {
                        workspace.trial_parameters[i] = workspace.parameters[i]
                            + small_alpha * workspace.step[i];
                    }

                    // Evaluate the trial point.
                    problem.residuals(
                        workspace.trial_parameters.as_slice(),
                        workspace.trial_residuals.as_mut_slice(),
                    )?;
                    nfev += 1;

                    let trial_cost =
                        self.compute_cost(&workspace.trial_residuals);

                    if trial_cost < current_cost
                        && self
                            .validate_parameters(&workspace.trial_parameters)
                            .is_ok()
                    {
                        // Accept the adaptive step.
                        workspace
                            .parameters
                            .copy_from(&workspace.trial_parameters);
                        workspace
                            .residuals
                            .copy_from(&workspace.trial_residuals);
                        previous_cost = current_cost;
                        current_cost = trial_cost;

                        if current_cost < best_cost {
                            best_cost = current_cost;
                            workspace
                                .best_parameters
                                .copy_from(&workspace.parameters);
                            workspace
                                .best_residuals
                                .copy_from(&workspace.residuals);
                        }

                        debug!("Adaptive regularization recovery successful at iteration {}", iteration);
                        continue; // Continue with the main loop.
                    }
                }

                // Adaptive regularization failed too - return best
                // solution.
                return Ok(OptimisationResult {
                    status: SolverStatus::SmallStepSize,
                    parameters: workspace.best_parameters.as_slice().to_vec(),
                    residuals: workspace.best_residuals.as_slice().to_vec(),
                    cost: best_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    jacobian_evaluations: njev,
                    message: "Failed: line search could not find improvement",
                });
            }

            // Check for convergence based on step size..
            let step_norm = workspace.step.norm();
            let param_norm = workspace.parameters.norm().max(1.0);

            if step_norm < self.config.parameter_tolerance * param_norm {
                debug!("Converged: step size below tolerance");
                return Ok(OptimisationResult {
                    status: SolverStatus::SmallStepSize,
                    parameters: workspace.parameters.as_slice().to_vec(),
                    residuals: workspace.residuals.as_slice().to_vec(),
                    cost: current_cost,
                    iterations: iteration + 1,
                    function_evaluations: nfev,
                    jacobian_evaluations: njev,
                    message: "Converged: step size below tolerance",
                });
            }

            // Check for cost reduction convergence.
            if iteration > 0 {
                let actual_reduction = previous_cost - current_cost;
                if actual_reduction
                    < self.config.function_tolerance * current_cost
                {
                    debug!("Converged: small cost reduction");
                    return Ok(OptimisationResult {
                        status: SolverStatus::SmallCostReduction,
                        parameters: workspace.parameters.as_slice().to_vec(),
                        residuals: workspace.residuals.as_slice().to_vec(),
                        cost: current_cost,
                        iterations: iteration + 1,
                        function_evaluations: nfev,
                        jacobian_evaluations: njev,
                        message: "Converged: small cost reduction",
                    });
                }
            }
        }

        // Maximum iterations reached.
        Ok(OptimisationResult {
            status: SolverStatus::MaxIterationsReached,
            parameters: workspace.best_parameters.as_slice().to_vec(),
            residuals: workspace.best_residuals.as_slice().to_vec(),
            cost: best_cost,
            iterations: self.config.max_iterations,
            function_evaluations: nfev,
            jacobian_evaluations: njev,
            message: "Terminated: maximum iterations reached",
        })
    }

    /// Set user-provided scaling factors.
    pub fn set_scaling(
        &self,
        workspace: &mut GaussNewtonWorkspace,
        scaling: &[f64],
    ) -> Result<()> {
        if scaling.len() != workspace.n {
            return Err(OptimisationError::InvalidInput(format!(
                "Expected {} scaling factors, got {}",
                workspace.n,
                scaling.len()
            ))
            .into());
        }

        for (i, &s) in scaling.iter().enumerate() {
            if s <= 0.0 {
                return Err(OptimisationError::InvalidInput(format!(
                    "Scaling factor {i} must be positive, got {s}",
                ))
                .into());
            }
            workspace.scaling[i] = s;
        }

        Ok(())
    }
}

#[cfg(test)]
mod gauss_newton_tests {
    use super::*;
    use crate::solver::test_problems::{
        CurveFittingProblem, DifficultLandscapeProblem, GoldsteinPriceFunction,
        Mock3DProblem, NearSingularProblem, OscillatingProblem,
        RosenbrockProblem, StagnationProblem, UnderdeterminedProblem,
        ZeroJacobianProblem,
    };
    use approx::assert_relative_eq;
    use num_traits::{Float, Zero};
    use std::ops::{Add, Div, Mul, Sub};

    #[test]
    fn test_gauss_newton_rosenbrock() {
        let problem = RosenbrockProblem::new();
        let solver = GaussNewtonSolver::with_defaults();

        // Start closer to minimum since Gauss-Newton is less robust.
        let initial_parameters = vec![0.8, 0.8];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton on Rosenbrock from (0.8, 0.8):");
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Status: {:?}", result.status);

        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
        assert!(result.cost < 1e-10);
    }

    #[test]
    fn test_gauss_newton_curve_fitting() {
        let problem = CurveFittingProblem::from_example_data();

        let config = GaussNewtonConfig {
            max_iterations: 100,
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        // Start from (0, 0).
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton curve fitting (exponential):");
        println!("  Initial: m = 0.0, c = 0.0");
        println!(
            "  Final: m = {:.6}, c = {:.6}",
            result.parameters[0], result.parameters[1]
        );
        println!("  Cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should converge to approximately m=0.3, c=0.1.
        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 0.3, epsilon = 1e-2);
        assert_relative_eq!(result.parameters[1], 0.1, epsilon = 5e-2);
    }

    #[test]
    fn test_gauss_newton_far_from_minimum() {
        let problem = RosenbrockProblem::new();

        // Start far from minimum - Gauss-Newton may struggle.
        let initial_parameters = vec![-1.2, 1.0];

        let config = GaussNewtonConfig {
            max_iterations: 200,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton from far point (-1.2, 1.0):");
        println!(
            "  Final: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Status: {:?}", result.status);

        // Gauss-Newton might not converge from far away, but should at least improve.
        let initial_cost = {
            let mut initial_residuals = vec![0.0; 2];
            problem
                .residuals(&initial_parameters, &mut initial_residuals)
                .unwrap();
            initial_residuals.iter().map(|r| r * r).sum::<f64>() * 0.5
        };
        assert!(
            result.cost < initial_cost,
            "Should at least improve from initial"
        );
    }

    #[test]
    fn test_gauss_newton_with_regularization() {
        let problem = RosenbrockProblem::new();

        // Test with different regularization values.
        let regularizations = vec![0.0, 1e-10, 1e-6, 1e-3];

        for reg in regularizations {
            let config = GaussNewtonConfig {
                regularization: reg,
                ..Default::default()
            };
            let solver = GaussNewtonSolver::new(config);

            let initial_parameters = vec![0.7, 0.7];
            let mut workspace =
                GaussNewtonWorkspace::new(&problem, &initial_parameters)
                    .unwrap();
            let result =
                solver.solve_problem(&problem, &mut workspace).unwrap();

            println!(
                "\nGN with regularization={:.0e}: {} iters, cost: {:.6e}",
                reg, result.iterations, result.cost
            );

            // All should converge successfully.
            assert!(result.status.is_success());
        }
    }

    #[test]
    fn test_gauss_newton_workspace_reuse() {
        let problem = RosenbrockProblem::new();

        let initial_parameters1 = vec![0.8, 0.8];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters1).unwrap();

        // Verify initial state.
        assert_eq!(workspace.parameters[0], 0.8);
        assert_eq!(workspace.parameters[1], 0.8);

        let initial_parameters2 = vec![0.9, 0.9];
        workspace
            .reuse_with(&problem, &initial_parameters2)
            .unwrap();

        // Verify workspace was properly reset.
        assert_eq!(workspace.parameters[0], 0.9);
        assert_eq!(workspace.parameters[1], 0.9);

        // Test that reused workspace works with Gauss-Newton solver.
        let solver = GaussNewtonSolver::with_defaults();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);

        println!("\nGN workspace reuse test:");
        println!("  Reused workspace from [0.9, 0.9] and converged to [{:.6}, {:.6}]",
                 result.parameters[0], result.parameters[1]);
        println!("  Cost: {:.6e}", result.cost);
    }

    #[test]
    fn test_gauss_newton_scaling_modes() {
        let problem = RosenbrockProblem::new();
        let initial_parameters = vec![0.8, 0.8];

        // Test with no scaling.
        let config_none = GaussNewtonConfig {
            scaling_mode: ParameterScalingMode::None,
            ..Default::default()
        };
        let solver_none = GaussNewtonSolver::new(config_none);
        let mut workspace_none =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_none = solver_none
            .solve_problem(&problem, &mut workspace_none)
            .unwrap();

        // Test with auto scaling.
        let config_auto = GaussNewtonConfig {
            scaling_mode: ParameterScalingMode::Auto,
            ..Default::default()
        };
        let solver_auto = GaussNewtonSolver::new(config_auto);
        let mut workspace_auto =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_auto = solver_auto
            .solve_problem(&problem, &mut workspace_auto)
            .unwrap();

        // Test with manual scaling.
        let config_manual = GaussNewtonConfig {
            scaling_mode: ParameterScalingMode::Manual,
            ..Default::default()
        };
        let solver_manual = GaussNewtonSolver::new(config_manual);
        let mut workspace_manual =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        solver_manual
            .set_scaling(&mut workspace_manual, &[2.0, 1.0])
            .unwrap();
        let result_manual = solver_manual
            .solve_problem(&problem, &mut workspace_manual)
            .unwrap();

        println!("\nGN scaling mode comparison:");
        println!(
            "  None: {} iterations, cost: {:.6e}",
            result_none.iterations, result_none.cost
        );
        println!(
            "  Auto: {} iterations, cost: {:.6e}",
            result_auto.iterations, result_auto.cost
        );
        println!(
            "  Manual: {} iterations, cost: {:.6e}",
            result_manual.iterations, result_manual.cost
        );

        // All should converge successfully.
        assert!(result_none.status.is_success());
        assert!(result_auto.status.is_success());
        assert!(result_manual.status.is_success());
    }

    #[test]
    fn test_gauss_newton_convergence_criteria() {
        let problem = RosenbrockProblem::new();

        // Test with very tight tolerances to trigger max iterations.
        let config = GaussNewtonConfig {
            function_tolerance: 1e-15,
            parameter_tolerance: 1e-15,
            gradient_tolerance: 1e-15,
            max_iterations: 10, // Very few iterations.
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        let initial_parameters = vec![0.5, 0.5];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGN with max_iterations=10:");
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

        // Should hit max iterations or converge.
        assert!(
            result.status == SolverStatus::MaxIterationsReached
                || result.status.is_success()
        );
        assert!(result.iterations <= 10);

        // Even with limited iterations, should make some progress.
        let initial_cost = {
            let mut initial_residuals = vec![0.0; 2];
            problem
                .residuals(&initial_parameters, &mut initial_residuals)
                .unwrap();
            initial_residuals.iter().map(|r| r * r).sum::<f64>() * 0.5
        };
        assert!(result.cost <= initial_cost);
    }

    #[test]
    fn test_gauss_newton_multiple_starting_points() {
        let config = GaussNewtonConfig {
            function_tolerance: 1e-6,
            parameter_tolerance: 1e-6,
            gradient_tolerance: 1e-6,
            max_iterations: 200,
            verbose: false,
            ..Default::default()
        };

        let problem = RosenbrockProblem::new();
        let solver = GaussNewtonSolver::new(config);

        // Test from multiple starting points (close to minimum since Gauss-Newton is less robust)
        let starting_points = vec![
            vec![0.8, 0.8],
            vec![1.2, 1.2],
            vec![0.9, 1.1],
            vec![1.1, 0.9],
        ];

        for (i, initial_parameters) in starting_points.iter().enumerate() {
            let mut workspace =
                GaussNewtonWorkspace::new(&problem, initial_parameters)
                    .unwrap();
            let result =
                solver.solve_problem(&problem, &mut workspace).unwrap();

            println!(
                "\nGN test {} from [{:.1}, {:.1}]:",
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

            // All should converge to (1, 1) from near the minimum.
            assert!(
                result.status.is_success(),
                "Failed from starting point {:?}",
                initial_parameters
            );
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
            assert!(result.cost < 1e-10);
        }
    }

    #[test]
    fn test_gauss_newton_goldstein_price_near_minimum() {
        let problem = GoldsteinPriceFunction;

        let config = GaussNewtonConfig {
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            max_iterations: 100,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        // Start very close to the global minimum for Gauss-Newton
        let initial_parameters = vec![0.05, -0.95];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGN on Goldstein-Price from near global minimum:");
        println!("  Initial: [0.05, -0.95]");
        println!(
            "  Final: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Status: {:?}", result.status);

        // Should converge successfully from near minimum.
        assert!(result.status.is_success());

        // Check if we're near the global minimum (0, -1).
        let near_global = (result.parameters[0] - 0.0).abs() < 0.1
            && (result.parameters[1] - (-1.0)).abs() < 0.1;

        if near_global {
            println!("  Found global minimum region!");
            assert_relative_eq!(result.parameters[0], 0.0, epsilon = 0.01);
            assert_relative_eq!(result.parameters[1], -1.0, epsilon = 0.01);
        }

        // At minimum, should have low cost.
        assert!(result.cost < 1e-6);
    }

    #[test]
    fn test_gauss_newton_nan_parameters() {
        let problem = RosenbrockProblem::new();
        let solver = GaussNewtonSolver::with_defaults();

        // Test with NaN initial parameters
        let initial_parameters = vec![f64::NAN, 0.0];
        let workspace_result =
            GaussNewtonWorkspace::new(&problem, &initial_parameters);

        // Should create workspace successfully (NaN validation happens during solve)
        assert!(workspace_result.is_ok());

        let mut workspace = workspace_result.unwrap();
        let result = solver.solve_problem(&problem, &mut workspace);

        println!("\nGauss-Newton with NaN initial parameters:");

        // Solver should return an error when encountering NaN
        match result {
            Ok(opt_result) => {
                println!("  Status: {:?}", opt_result.status);
                println!("  Final cost: {:.6e}", opt_result.cost);
                // If it somehow succeeds, it should not claim success
                assert!(
                    !opt_result.status.is_success(),
                    "Solver should not succeed with NaN parameters"
                );
            }
            Err(error) => {
                println!("  Error (expected): {:?}", error);
                // This is the expected behavior - solver should error out
                assert!(
                    error.to_string().contains("not finite")
                        || error.to_string().contains("NaN")
                        || error.to_string().contains("infinite")
                );
            }
        }
    }

    #[test]
    fn test_gauss_newton_infinite_parameters() {
        let problem = RosenbrockProblem::new();
        let solver = GaussNewtonSolver::with_defaults();

        // Test with infinite initial parameters
        let initial_parameters = vec![f64::INFINITY, 0.0];
        let workspace_result =
            GaussNewtonWorkspace::new(&problem, &initial_parameters);

        assert!(workspace_result.is_ok());

        let mut workspace = workspace_result.unwrap();
        let result = solver.solve_problem(&problem, &mut workspace);

        println!("\nGauss-Newton with infinite initial parameters:");

        // Solver should return an error when encountering infinity
        match result {
            Ok(opt_result) => {
                println!("  Status: {:?}", opt_result.status);
                println!("  Final cost: {:.6e}", opt_result.cost);
                // If it somehow succeeds, it should not claim success
                assert!(
                    !opt_result.status.is_success(),
                    "Solver should not succeed with infinite parameters"
                );
            }
            Err(error) => {
                println!("  Error (expected): {:?}", error);
                // This is the expected behavior - solver should error out
                assert!(
                    error.to_string().contains("not finite")
                        || error.to_string().contains("infinite")
                        || error.to_string().contains("NaN")
                );
            }
        }
    }

    #[test]
    fn test_gauss_newton_near_singular_jacobian() {
        // NearSingularProblem is a problem with a nearly singular
        // Jacobian.
        let problem = NearSingularProblem;
        let solver = GaussNewtonSolver::with_defaults();

        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton with near-singular Jacobian:");
        println!("  Status: {:?}", result.status);
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Solver should either converge or detect the singular condition
        assert!(
            result.status == SolverStatus::SmallStepSize
                || result.status == SolverStatus::SmallGradient
                || result.status.is_success(),
            "Should handle near-singular Jacobian gracefully"
        );
    }

    #[test]
    fn test_gauss_newton_zero_jacobian_column() {
        // ZeroJacobianProblem is a problem where one parameter
        // doesn't affect the residuals.
        let problem = ZeroJacobianProblem;
        let solver = GaussNewtonSolver::with_defaults();

        let initial_parameters = vec![0.0, 5.0]; // Second parameter is irrelevant
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton with zero Jacobian column:");
        println!("  Status: {:?}", result.status);
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should handle zero Jacobian column gracefully
        assert!(
            result.status == SolverStatus::SmallStepSize
                || result.status == SolverStatus::SmallGradient
                || result.status.is_success(),
            "Should handle zero Jacobian column gracefully"
        );

        // The solver correctly detects the issue immediately
        // This demonstrates proper handling of singular/rank-deficient systems
        if result.status == SolverStatus::SmallStepSize {
            // Expected behavior - solver detects it cannot make progress
            assert!(result.iterations <= 1, "Should detect issue quickly");
            println!("  Successfully detected zero Jacobian column");
        } else if result.status.is_success() {
            // If somehow it converges, the first parameter should be correct
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
            assert!(result.cost < 1e-10);
        }
    }

    #[test]
    fn test_gauss_newton_workspace_dimension_mismatch() {
        let problem2d = RosenbrockProblem::new(); // 2 parameters, 2 residuals.

        // Create workspace for 2D problem.
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem2d, &initial_parameters).unwrap();

        // Try to reuse with incompatible problem dimensions.
        let problem3d = Mock3DProblem;
        let parameters3d = vec![0.0, 0.0, 0.0];

        // This should fail with dimension mismatch.
        let result = workspace.reuse_with(&problem3d, &parameters3d);
        assert!(result.is_err());

        // Test parameter count mismatch with same problem.
        let wrong_params = vec![0.0, 0.0, 0.0]; // 3 params for 2D problem.
        let result = workspace.reuse_with(&problem2d, &wrong_params);
        assert!(result.is_err());

        println!("\nWorkspace dimension mismatch test passed - errors caught as expected");
    }

    #[test]
    fn test_gauss_newton_invalid_scaling_factors() {
        let problem = RosenbrockProblem::new();
        let solver = GaussNewtonSolver::with_defaults();
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();

        // Test negative scaling factor
        let negative_scaling = vec![-1.0, 1.0];
        let result = solver.set_scaling(&mut workspace, &negative_scaling);
        assert!(result.is_err());

        // Test zero scaling factor
        let zero_scaling = vec![0.0, 1.0];
        let result = solver.set_scaling(&mut workspace, &zero_scaling);
        assert!(result.is_err());

        // Test wrong number of scaling factors
        let wrong_count_scaling = vec![1.0, 1.0, 1.0]; // 3 factors for 2 parameters
        let result = solver.set_scaling(&mut workspace, &wrong_count_scaling);
        assert!(result.is_err());

        // Test valid scaling factors
        let valid_scaling = vec![1.0, 2.0];
        let result = solver.set_scaling(&mut workspace, &valid_scaling);
        assert!(result.is_ok());

        println!(
            "\nInvalid scaling factors test passed - errors caught as expected"
        );
    }

    #[test]
    fn test_gauss_newton_empty_parameters() {
        let problem = RosenbrockProblem::new();

        // Test with empty parameter vector.
        let empty_parameters = vec![];
        let workspace_result =
            GaussNewtonWorkspace::new(&problem, &empty_parameters);

        // Should fail during workspace creation
        assert!(workspace_result.is_err());

        println!("\nEmpty parameters test passed - error caught as expected");
    }

    #[test]
    fn test_gauss_newton_insufficient_residuals() {
        // UnderdeterminedProblem is a problem with fewer residuals
        // than parameters (underdetermined).
        let problem = UnderdeterminedProblem;
        let initial_parameters = vec![0.0, 0.0];

        // Should fail during workspace creation due to insufficient
        // residuals.
        let workspace_result =
            GaussNewtonWorkspace::new(&problem, &initial_parameters);
        assert!(workspace_result.is_err());

        println!(
            "\nInsufficient residuals test passed - error caught as expected"
        );
    }

    #[test]
    fn test_gauss_newton_parameter_count_validation() {
        let problem = RosenbrockProblem::new();

        // Test various invalid parameter counts.
        let test_cases = vec![
            (vec![], "empty parameters"),
            (vec![1.0], "too few parameters"),
            (vec![1.0, 2.0, 3.0], "too many parameters"),
        ];

        for (params, description) in test_cases {
            let workspace_result = GaussNewtonWorkspace::new(&problem, &params);
            assert!(
                workspace_result.is_err(),
                "Should fail for {}: {:?}",
                description,
                params
            );
        }

        // Test valid parameter count.
        let valid_params = vec![1.0, 2.0];
        let workspace_result =
            GaussNewtonWorkspace::new(&problem, &valid_params);
        assert!(workspace_result.is_ok());

        println!("\nParameter count validation test passed");
    }

    #[test]
    fn test_gauss_newton_line_search_failure() {
        // DifficultLandscapeProblem is a problem where line search
        // might struggle.
        let problem = DifficultLandscapeProblem;
        let config = GaussNewtonConfig {
            max_iterations: 50,
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        // Start from a challenging point
        let initial_parameters = vec![10.0, 10.0];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton line search challenge:");
        println!("  Status: {:?}", result.status);
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should either succeed or hit a reasonable stopping condition
        assert!(
            result.status.is_success()
                || result.status == SolverStatus::SmallStepSize
                || result.status == SolverStatus::MaxIterationsReached
                || result.status == SolverStatus::SmallGradient,
            "Should handle line search challenges gracefully"
        );
    }

    #[test]
    fn test_gauss_newton_max_function_evaluations() {
        let problem = RosenbrockProblem::new();

        // Set a very low function evaluation limit
        let config = GaussNewtonConfig {
            max_function_evaluations: 10, // Very few function evaluations allowed
            max_iterations: 100,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        let initial_parameters = vec![-1.2, 1.0]; // Challenging starting point
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton with function evaluation limit:");
        println!("  Status: {:?}", result.status);
        println!("  Function evaluations: {}", result.function_evaluations);
        println!("  Final cost: {:.6e}", result.cost);

        // Should hit function evaluation limit - allow some flexibility for Jacobian computation
        assert!(
            result.status == SolverStatus::FunctionCallsExceeded,
            "Should hit function evaluation limit"
        );
        assert!(
            result.function_evaluations <= 15,
            "Function evaluations should be reasonably close to limit"
        );
    }

    #[test]
    fn test_gauss_newton_step_size_limiting() {
        let problem = RosenbrockProblem::new();

        // Use high regularization to force small steps
        let config = GaussNewtonConfig {
            regularization: 1e-3, // High regularization
            max_iterations: 200,
            function_tolerance: 1e-10,
            parameter_tolerance: 1e-10,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        let initial_parameters = vec![-2.0, 2.0]; // Far from minimum
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton with high regularization (small steps):");
        println!("  Status: {:?}", result.status);
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should either converge slowly or hit small step condition
        assert!(
            result.status.is_success()
                || result.status == SolverStatus::SmallStepSize
                || result.status == SolverStatus::MaxIterationsReached,
            "Should handle step size limiting gracefully"
        );

        // Even with small steps, should make some progress
        let initial_cost = {
            let mut initial_residuals = vec![0.0; 2];
            problem
                .residuals(&initial_parameters, &mut initial_residuals)
                .unwrap();
            initial_residuals.iter().map(|r| r * r).sum::<f64>() * 0.5
        };
        assert!(result.cost < initial_cost, "Should make some progress");
    }

    #[test]
    fn test_gauss_newton_adaptive_regularization_recovery() {
        // Test the adaptive regularization recovery mechanism
        let problem = RosenbrockProblem::new();

        let config = GaussNewtonConfig {
            regularization: 0.0, // Start with no regularization
            max_iterations: 100,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        // Start from a very challenging point
        let initial_parameters = vec![-5.0, 5.0];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton adaptive regularization test:");
        println!("  Status: {:?}", result.status);
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // The solver should handle challenging starting points
        // Even if it doesn't fully converge, it should make progress
        let initial_cost = {
            let mut initial_residuals = vec![0.0; 2];
            problem
                .residuals(&initial_parameters, &mut initial_residuals)
                .unwrap();
            initial_residuals.iter().map(|r| r * r).sum::<f64>() * 0.5
        };

        assert!(
            result.cost < initial_cost,
            "Should make progress from challenging start"
        );

        // Should not fail catastrophically
        assert!(result.cost.is_finite(), "Final cost should be finite");
    }

    #[test]
    fn test_gauss_newton_very_tight_tolerances() {
        let problem = RosenbrockProblem::new();

        // Set tolerances at machine precision level
        let config = GaussNewtonConfig {
            function_tolerance: f64::EPSILON,
            parameter_tolerance: f64::EPSILON,
            gradient_tolerance: f64::EPSILON,
            max_iterations: 500,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        let initial_parameters = vec![0.8, 0.8]; // Close to minimum
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton with machine precision tolerances:");
        println!("  Status: {:?}", result.status);
        println!(
            "  Final parameters: [{:.12}, {:.12}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should either achieve very high precision or hit iteration limit
        assert!(
            result.status.is_success()
                || result.status == SolverStatus::MaxIterationsReached,
            "Should handle machine precision tolerances"
        );

        if result.status.is_success() {
            // If it converged, it should be very precise
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-8);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-8);
            assert!(result.cost < 1e-12);
        }
    }

    #[test]
    fn test_gauss_newton_gradient_convergence() {
        let problem = RosenbrockProblem::new();

        // Focus on gradient-based convergence
        let config = GaussNewtonConfig {
            gradient_tolerance: 1e-12, // Very tight gradient tolerance
            function_tolerance: 1e-15, // Looser function tolerance
            parameter_tolerance: 1e-15, // Looser parameter tolerance
            max_iterations: 200,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        let initial_parameters = vec![0.9, 0.9];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton gradient convergence test:");
        println!("  Status: {:?}", result.status);
        println!(
            "  Final parameters: [{:.8}, {:.8}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should converge via gradient criterion
        assert!(
            result.status == SolverStatus::SmallGradient
                || result.status.is_success(),
            "Should achieve gradient convergence or general success"
        );

        if result.status.is_success() {
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-6);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-6);
        }
    }

    #[test]
    fn test_gauss_newton_cost_stagnation() {
        // StagnationProblem is a problem where cost improvements
        // become very small.
        let problem = StagnationProblem;
        let config = GaussNewtonConfig {
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            max_iterations: 100,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        let initial_parameters = vec![1.1, 1.1]; // Close to the flat region.
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton cost stagnation test:");
        println!("  Status: {:?}", result.status);
        println!(
            "  Final parameters: [{:.8}, {:.8}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should handle flat cost landscapes gracefully.
        assert!(
            result.status == SolverStatus::SmallCostReduction
                || result.status == SolverStatus::SmallGradient
                || result.status == SolverStatus::SmallStepSize
                || result.status.is_success(),
            "Should handle cost stagnation gracefully"
        );
    }

    #[test]
    fn test_gauss_newton_oscillating_behavior() {
        // The OscillatingProblem is a problem that might cause
        // oscillating behavior.
        let problem = OscillatingProblem;
        let config = GaussNewtonConfig {
            max_iterations: 150,
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            verbose: false,
            ..Default::default()
        };
        let solver = GaussNewtonSolver::new(config);

        let initial_parameters = vec![0.5, 0.5];
        let mut workspace =
            GaussNewtonWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGauss-Newton oscillating behavior test:");
        println!("  Status: {:?}", result.status);
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should handle oscillatory problems reasonably.
        assert!(
            result.status.is_success()
                || result.status == SolverStatus::MaxIterationsReached
                || result.status == SolverStatus::SmallStepSize,
            "Should handle oscillatory behavior gracefully"
        );

        // Should at least be closer to the optimum (1, 1).
        let distance_to_optimum = ((result.parameters[0] - 1.0).powi(2)
            + (result.parameters[1] - 1.0).powi(2))
        .sqrt();
        assert!(
            distance_to_optimum < 0.5,
            "Should get reasonably close to optimum"
        );
    }
}
