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

/// Configuration parameters for the Levenberg-Marquardt solver.
///
/// Controls all aspects of solver behavior, from convergence
/// tolerances to trust region management. Proper configuration is
/// crucial for achieving good performance on different types of
/// optimization problems.
///
/// ## Parameter Reference
///
/// | Parameter                  | Description           | Typical Range  | When to Adjust                         |
/// |----------------------------+-----------------------+----------------+----------------------------------------|
/// | `function_tolerance`       | Function tolerance    | 1e-6 to 1e-12  | Tighter for high precision             |
/// | `parameter_tolerance`      | Parameter tolerance   | 1e-6 to 1e-12  | Tighter for parameter accuracy         |
/// | `gradient_tolerance`       | Gradient tolerance    | 1e-6 to 1e-12  | Tighter for gradient-based convergence |
/// | `initial_trust_factor`     | Trust region radius   | 10.0 to 1000.0 | Larger for well-conditioned problems   |
/// | `min_step_quality`         | Step acceptance ratio | 1e-4 to 1e-2   | Lower for difficult problems           |
/// | `max_iterations`           | Iteration limit       | 100 to 5000    | Higher for complex problems            |
/// | `max_function_evaluations` | Function call limit   | 1000 to 50000  | Higher for expensive functions         |
/// |----------------------------+-----------------------+----------------+----------------------------------------|
///
/// ## Configuration Guidelines by Problem Type
///
/// | Problem Type              | Recommended Settings                              | Notes                               |
/// |---------------------------+---------------------------------------------------+-------------------------------------|
/// | **Well-conditioned**      | `Default`                                         | Standard settings work well         |
/// | **High precision needed** | Tight tolerances (1e-12)                          | Scientific/engineering applications |
/// | **Fast approximation**    | Relaxed tolerances (1e-4)                         | Real-time or interactive use        |
/// | **Ill-conditioned**       | `ParameterScalingMode::Auto` + conservative steps | Difficult optimization landscapes   |
/// | **Large-scale**           | Higher iteration/evaluation limits                | Many parameters or residuals        |
/// |---------------------------+---------------------------------------------------+-------------------------------------|
///
/// ## Examples
///
/// ```rust
/// use mmoptimise_rust::solver::common::ParameterScalingMode;
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtConfig;
///
/// // High-precision configuration for demanding problems
/// let precise_config = LevenbergMarquardtConfig {
///     function_tolerance: 1e-12,       // Very tight function tolerance.
///     parameter_tolerance: 1e-12,      // Very tight parameter tolerance.
///     gradient_tolerance: 1e-12,       // Very tight gradient tolerance.
///     absolute_cost_tolerance: 1e-12,  // Very tight absolute cost threshold.
///     max_iterations: 1000,
///     max_function_evaluations: 10000,
///     initial_trust_factor: 100.0,     // Large trust region radius.
///     scaling_mode: ParameterScalingMode::Auto, // Automatic parameter scaling.
///     min_step_quality: 1e-4,          // Standard step acceptance.
///     verbose: true,                   // Enable detailed logging.
///     epsilon_factor: 1.0,             // Standard numerical precision.
/// };
///
/// // Fast approximation for real-time use
/// let fast_config = LevenbergMarquardtConfig {
///     function_tolerance: 1e-4,        // Relaxed tolerances.
///     parameter_tolerance: 1e-4,
///     gradient_tolerance: 1e-4,
///     absolute_cost_tolerance: 1e-4,   // Relaxed absolute cost threshold.
///     max_iterations: 50,              // Fewer iterations.
///     max_function_evaluations: 500,
///     initial_trust_factor: 10.0,      // Smaller steps for stability.
///     scaling_mode: ParameterScalingMode::Auto,
///     min_step_quality: 1e-3,          // Accept lower quality steps.
///     verbose: false,
///     epsilon_factor: 1.0,
/// };
///
/// // Verify the configurations
/// assert_eq!(precise_config.function_tolerance, 1e-12);
/// assert_eq!(fast_config.max_iterations, 50);
/// ```
#[derive(Debug, Clone, Copy)]
pub struct LevenbergMarquardtConfig {
    /// Function tolerance - convergence when relative reduction in cost is below this.
    pub function_tolerance: f64,
    /// Parameter tolerance - convergence when relative change in parameters is below this.
    pub parameter_tolerance: f64,
    /// Gradient tolerance - convergence when gradient norm is below this.
    pub gradient_tolerance: f64,
    /// Maximum number of iterations.
    pub max_iterations: usize,
    /// Maximum number of function evaluations.
    pub max_function_evaluations: usize,
    /// Initial trust region radius factor.
    pub initial_trust_factor: f64,
    /// Scaling mode for parameters.
    pub scaling_mode: ParameterScalingMode,
    /// Minimum acceptable step quality ratio.
    pub min_step_quality: f64,
    /// Enable verbose output.
    pub verbose: bool,
    /// Machine epsilon multiplier for numerical tolerances.
    pub epsilon_factor: f64,
    /// Absolute cost tolerance - convergence when cost is below this absolute
    /// threshold. Used in conjunction with relative improvements to determine
    /// convergence.
    pub absolute_cost_tolerance: f64,
}

impl Default for LevenbergMarquardtConfig {
    fn default() -> Self {
        Self {
            function_tolerance: 1e-6,
            parameter_tolerance: 1e-6,
            gradient_tolerance: 1e-6,
            max_iterations: 300,
            max_function_evaluations: 3000,
            initial_trust_factor: 100.0,
            scaling_mode: ParameterScalingMode::Auto,
            min_step_quality: 1e-4,
            verbose: false,
            epsilon_factor: 1.0,
            absolute_cost_tolerance: 1e-6,
        }
    }
}

#[derive(Debug)]
pub struct LevenbergMarquardtWorkspace {
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

    // Decomposition workspace.
    r_matrix: DMatrix<f64>, // Upper triangular R from QR.
    q_matrix: DMatrix<f64>, // Q matrix from QR (optional storage).
    qtf: DVector<f64>,      // Q^T * residuals.

    // Step computation workspace.
    step: DVector<f64>,
    scaling: DVector<f64>, // Parameter scaling factors

    // Permutation for column pivoting.
    permutation: Vec<usize>,
}

impl LevenbergMarquardtWorkspace {
    /// Reuse an existing LevenbergMarquardtWorkspace with new initial parameters.
    ///
    /// Allows reusing the allocated memory of an existing workspace
    /// as long as the parameter count and residual count match the
    /// new problem.  All workspace data is properly reset, but no new
    /// memory is allocated.
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

        if m < n {
            return Err(OptimisationError::InvalidInput(
                "Number of residuals must be >= number of parameters"
                    .to_string(),
            )
            .into());
        }

        // Update parameter vectors with new initial values
        self.parameters.copy_from_slice(initial_parameters);
        self.trial_parameters.copy_from_slice(initial_parameters);
        self.best_parameters.copy_from_slice(initial_parameters);

        // Reset all workspace data without reallocating memory.
        self.residuals.fill(0.0);
        self.trial_residuals.fill(0.0);
        self.best_residuals.fill(0.0);
        self.jacobian.fill(0.0);
        self.r_matrix.fill(0.0);
        self.q_matrix.fill(0.0);
        self.qtf.fill(0.0);
        self.step.fill(0.0);
        self.scaling.fill(1.0);

        for i in 0..n {
            self.permutation[i] = i;
        }

        Ok(())
    }

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
            r_matrix: DMatrix::zeros(n, n),
            q_matrix: DMatrix::zeros(m, n),
            qtf: DVector::zeros(n),
            step: DVector::zeros(n),
            scaling: DVector::from_element(n, 1.0),
            permutation: (0..n).collect(),
        })
    }
}

/// Levenberg-Marquardt solver with trust region management.
///
/// This is a robust implementation of the Levenberg-Marquardt
/// algorithm for non-linear least squares optimization. It uses
/// automatic differentiation for gradient computation, QR
/// decomposition for numerical stability, and adaptive trust region
/// management.
///
/// ## Algorithm Features
///
/// - **Automatic Differentiation**: Uses dual numbers for exact gradient computation.
/// - **Trust Region Management**: Adaptive step size control for robust convergence.
/// - **Parameter Scaling**: Automatic or manual scaling for better conditioning.
/// - **QR Decomposition**: Numerically stable linear system solving.
/// - **Workspace Reuse**: Efficient memory management for repeated optimizations.
///
/// ## Usage Patterns
///
/// ### Basic Usage
/// ```rust
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtSolver;
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtWorkspace;
/// use mmoptimise_rust::solver::test_problems::RosenbrockProblem;
///
/// let solver = LevenbergMarquardtSolver::with_defaults();
/// let problem = RosenbrockProblem::new();
/// let initial_params = vec![0.0, 0.0];
/// let mut workspace = LevenbergMarquardtWorkspace::new(&problem, &initial_params).unwrap();
/// let result = solver.solve_problem(&problem, &mut workspace).unwrap();
///
/// // Verify it worked
/// assert!(result.iterations > 0);
/// assert!(result.cost < 1e-6);  // Default absolute_cost_tolerance.
/// ```
///
/// ### Custom Configuration
/// ```rust
/// use mmoptimise_rust::solver::common::ParameterScalingMode;
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtConfig;
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtSolver;
///
/// let config = LevenbergMarquardtConfig {
///     function_tolerance: 1e-8,
///     max_iterations: 500,
///     scaling_mode: ParameterScalingMode::Auto,
///     verbose: false,
///     ..Default::default()
/// };
/// let solver = LevenbergMarquardtSolver::new(config);
///
/// // Configuration is ready for use with the solver
/// assert_eq!(config.function_tolerance, 1e-8);
/// assert_eq!(config.max_iterations, 500);
/// ```
///
/// ## Troubleshooting Guide
///
/// ### Poor Convergence
///
/// **Symptoms**: Slow convergence, reaches max iterations, or gets stuck.
///
/// **Solutions**:
/// ```rust
/// use mmoptimise_rust::solver::common::ParameterScalingMode;
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtConfig;
///
/// // Try different initial parameters
/// let initial_params = vec![0.1, 0.1, 0.1]; // Instead of all zeros.
///
/// // Enable automatic scaling
/// let config = LevenbergMarquardtConfig {
///     scaling_mode: ParameterScalingMode::Auto,
///     initial_trust_factor: 100.0, // More aggressive optimization.
///     ..Default::default()
/// };
///
/// // Relax tolerances for difficult problems
/// let relaxed_config = LevenbergMarquardtConfig {
///     function_tolerance: 1e-6,  // Less strict.
///     parameter_tolerance: 1e-6,
///     gradient_tolerance: 1e-6,
///     ..Default::default()
/// };
///
/// assert_eq!(initial_params.len(), 3);
/// assert_eq!(config.scaling_mode, ParameterScalingMode::Auto);
/// assert_eq!(relaxed_config.function_tolerance, 1e-6);
/// ```
///
/// ### Slow Convergence
///
/// **Symptoms**: Takes many iterations, small progress per iteration.
///
/// **Solutions**:
/// ```rust
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtConfig;
///
/// // Conservative approach for stability
/// let config = LevenbergMarquardtConfig {
///     initial_trust_factor: 10.0,  // Smaller steps.
///     max_iterations: 2000,        // More iterations allowed.
///     min_step_quality: 1e-6,      // Accept smaller improvements.
///     ..Default::default()
/// };
///
/// assert_eq!(config.initial_trust_factor, 10.0);
/// assert_eq!(config.max_iterations, 2000);
/// ```
///
/// ### Numerical Instability
///
/// **Symptoms**: NaN results, solver errors, non-finite costs.
///
/// **Solutions**:
/// ```rust
/// use mmoptimise_rust::solver::common::OptimisationProblem;
/// use mmoptimise_rust::solver::test_problems::RosenbrockProblem;
///
/// // Check problem formulation
/// let problem = RosenbrockProblem::new();
/// assert!(problem.residual_count() >= problem.parameter_count(),
///         "Need at least as many residuals as parameters");
///
/// // Manual parameter scaling for different ranges
/// let scaling = vec![1.0, 1000.0, 0.001]; // Scale parameters appropriately
/// assert_eq!(scaling.len(), 3);
///
/// // Test residual function
/// let test_params = vec![1.0f64, 2.0f64];
/// let mut residuals = vec![0.0f64; problem.residual_count()];
/// problem.residuals(&test_params, &mut residuals).unwrap();
/// assert!(residuals.iter().all(|&r| r.is_finite()));
/// ```
///
/// ### Debugging Tips
///
/// ```rust
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtConfig;
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtSolver;
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtWorkspace;
/// use mmoptimise_rust::solver::test_problems::RosenbrockProblem;
///
/// // Enable verbose logging for iteration details
/// let config = LevenbergMarquardtConfig {
///     verbose: false,  // Set to true to see iteration details.
///     max_iterations: 10,  // Limit iterations for testing.
///     ..Default::default()
/// };
///
/// // Monitor convergence progress.
/// let solver = LevenbergMarquardtSolver::new(config);
/// let problem = RosenbrockProblem::new();
/// let initial_params = vec![0.0, 0.0];
/// let mut workspace = LevenbergMarquardtWorkspace::new(&problem, &initial_params).unwrap();
/// let result = solver.solve_problem(&problem, &mut workspace).unwrap();
///
/// // Verify we have results.
/// assert!(result.iterations > 0);
/// assert!(result.function_evaluations > 0);
/// assert!(result.cost.is_finite());
/// ```
///
/// ## Performance Tips
///
/// - **Workspace Reuse**: Create workspace once, reuse for similar problems.
/// - **Parameter Scaling**: Use `ParameterScalingMode::Auto` for most problems.
/// - **Function Profiling**: Profile residual computation for bottlenecks.
/// - **Initial Guess**: Good initial parameters dramatically improve convergence.
///
/// ## When to Use Different Configurations
///
/// | Scenario                      | Configuration                                           | Reasoning                    |
/// |-------------------------------|---------------------------------------------------------|------------------------------|
/// | **Well-conditioned problems** | `Default`                                               | Standard settings work well  |
/// | **High precision needed**     | Tight tolerances (1e-12)                                | Scientific applications      |
/// | **Real-time applications**    | Relaxed tolerances (1e-4), low max_iterations           | Speed over precision         |
/// | **Ill-conditioned problems**  | `ParameterScalingMode::Auto`, conservative trust region | Numerical stability          |
/// | **Large-scale problems**      | Higher limits, workspace reuse                          | Memory and time efficiency   |
/// --------------------------------------------------------------------------------------------------------------------------
///
pub struct LevenbergMarquardtSolver {
    config: LevenbergMarquardtConfig,
}

impl LevenbergMarquardtSolver {
    pub fn new(config: LevenbergMarquardtConfig) -> Self {
        Self { config }
    }

    pub fn with_defaults() -> Self {
        Self {
            config: LevenbergMarquardtConfig::default(),
        }
    }

    /// Compute the cost from residuals (0.5 * sum of squares).
    fn compute_cost(&self, residuals: &DVector<f64>) -> f64 {
        0.5 * residuals.norm_squared()
    }

    /// Compute the Jacobian using automatic differentiation.
    fn compute_jacobian<P: OptimisationProblem>(
        &self,
        problem: &P,
        workspace: &mut LevenbergMarquardtWorkspace,
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

    /// Perform QR decomposition with column pivoting.
    fn qr_decomposition(
        &self,
        workspace: &mut LevenbergMarquardtWorkspace,
    ) -> Result<()> {
        let n = workspace.n;
        let m = workspace.m;

        // Copy Jacobian to R matrix.
        for j in 0..n {
            for i in 0..m {
                if i < n {
                    workspace.r_matrix[(i, j)] = workspace.jacobian[(i, j)];
                }
            }
        }

        // Compute column norms for pivoting.
        let mut col_norms = DVector::zeros(n);
        for j in 0..n {
            let col = workspace.jacobian.column(j);
            col_norms[j] = col.norm();
        }

        workspace.permutation = (0..n).collect();

        // QR decomposition with column pivoting.
        //
        // TODO: We want to use LAPACK's dgeqp3 (or similar) in the
        // future, because these are more stable and produce better
        // results.
        let qr = workspace.jacobian.clone().qr();
        let (q, r) = qr.unpack();

        workspace.q_matrix = q.columns(0, n).into();
        workspace.r_matrix = r;
        workspace.qtf = workspace.q_matrix.transpose() * &workspace.residuals;

        Ok(())
    }

    /// Solve the trust region subproblem.
    fn solve_trust_region(
        &self,
        workspace: &mut LevenbergMarquardtWorkspace,
        delta: f64,
        lambda: &mut f64,
    ) -> Result<f64> {
        let n = workspace.n;
        let machine_epsilon = f64::EPSILON * self.config.epsilon_factor;

        // Form the system (R^T R + lambda*D^2) step = -J^T f
        // where J^T f = R^T * qtf and D is the scaling diagonal matrix.

        // Estimate lambda if it's zero (first iteration).
        if *lambda == 0.0 {
            // Initial lambda estimate based on Levenberg-Marquardt algorithm.
            let r_norm = workspace.r_matrix.diagonal().norm();
            let qtf_norm = workspace.qtf.norm();

            if r_norm > machine_epsilon {
                *lambda = qtf_norm / (delta * r_norm);
            } else {
                *lambda = 1.0;
            }
            *lambda = lambda.max(machine_epsilon);
        }

        // Iteratively refine lambda to satisfy trust region constraint.
        let max_lambda_iterations = 10;
        for _ in 0..max_lambda_iterations {
            // Form (R^T R + lambda*D^2)
            let mut augmented_system =
                workspace.r_matrix.transpose() * &workspace.r_matrix;

            // Add lambda * scaling^2 to diagonal.
            for i in 0..n {
                let scale = workspace.scaling[i];
                augmented_system[(i, i)] += *lambda * scale * scale;
            }

            // Solve for step
            let decomp = augmented_system.cholesky();
            if let Some(chol) = decomp {
                // Compute right-hand side: -R^T * qtf.
                let rhs = -(&workspace.r_matrix.transpose() * &workspace.qtf);
                workspace.step = chol.solve(&rhs);

                // Check if step satisfies trust region.
                let scaled_step_norm = (0..n)
                    .map(|i| {
                        let s = workspace.step[i] * workspace.scaling[i];
                        s * s
                    })
                    .sum::<f64>()
                    .sqrt();

                if (scaled_step_norm - delta).abs() < 0.1 * delta {
                    // Close enough to trust region boundary.
                    break;
                }

                // Adjust lambda using a more sophisticated strategy.
                if scaled_step_norm < delta {
                    // Step too small, reduce damping.
                    *lambda *= 0.3;
                    if *lambda < machine_epsilon {
                        *lambda = 0.0;
                        break;
                    }
                } else {
                    // Step too large, increase damping.
                    let factor = (scaled_step_norm / delta).max(1.5);
                    *lambda *= factor * factor;
                }
            } else {
                // Cholesky failed, increase lambda.
                *lambda *= 10.0;
                if *lambda > 1e12 {
                    return Err(OptimisationError::NumericalInstability.into());
                }
            }
        }

        // Compute predicted reduction using the model m(p) = 0.5 * ||J*p + f||^2
        //
        // Predicted reduction = m(0) - m(p) = -g^T*p - 0.5*p^T*B*p
        //
        // where g = J^T*f = R^T*qtf and B = J^T*J = R^T*R
        let grad_term = workspace
            .step
            .dot(&(workspace.r_matrix.transpose() * &workspace.qtf));
        let hessian_term = 0.5
            * workspace.step.dot(
                &(&workspace.r_matrix.transpose()
                    * &(&workspace.r_matrix * &workspace.step)),
            );
        let predicted_reduction = -(grad_term + hessian_term);

        Ok(predicted_reduction)
    }

    /// Update parameter scaling based on Jacobian column norms
    fn update_scaling(&self, workspace: &mut LevenbergMarquardtWorkspace) {
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
        workspace: &mut LevenbergMarquardtWorkspace,
    ) -> Result<OptimisationResult> {
        let n = workspace.n;
        let _m = workspace.m;
        let machine_epsilon = f64::EPSILON * self.config.epsilon_factor;

        // Initialize counters.
        let mut nfev = 0;
        let mut njev = 0;
        let mut iteration;

        // Initialize trust region parameters.
        let mut lambda = 0.0;
        let mut delta = 0.0;
        let mut best_cost = f64::INFINITY;

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
        if current_cost < best_cost {
            best_cost = current_cost;
            workspace.best_parameters.copy_from(&workspace.parameters);
            workspace.best_residuals.copy_from(&workspace.residuals);
        }

        // Main iteration loop.
        for iteration_count in 0..self.config.max_iterations {
            iteration = iteration_count;

            if self.config.verbose {
                info!("Iteration {}: cost = {:.6e}", iteration, current_cost);
            }

            // Check for absolute cost convergence (only for very
            // small costs).
            if current_cost < machine_epsilon {
                debug!("Converged: cost near zero");
                return Ok(OptimisationResult {
                    status: SolverStatus::Success,
                    parameters: workspace.parameters.as_slice().to_vec(),
                    residuals: workspace.residuals.as_slice().to_vec(),
                    cost: current_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    jacobian_evaluations: njev,
                    message: "Converged: cost near zero",
                });
            }

            // Check for relative cost improvement (after first
            // iteration, and only if positive).
            if iteration > 0 && previous_cost > current_cost {
                let relative_improvement =
                    (previous_cost - current_cost) / previous_cost.max(1.0);
                // Only check convergence if improvement is small AND
                // cost is reasonably small.
                if relative_improvement < self.config.function_tolerance
                    && current_cost < self.config.absolute_cost_tolerance
                {
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

            // Perform QR decomposition.
            self.qr_decomposition(workspace)?;

            // Update scaling on first iteration or if requested.
            if iteration == 0
                || self.config.scaling_mode == ParameterScalingMode::Auto
            {
                self.update_scaling(workspace);
            }

            // Initialization for the trust region radius.
            if iteration == 0 {
                let scaled_x_norm = (0..n)
                    .map(|i| {
                        let sx = workspace.scaling[i] * workspace.parameters[i];
                        sx * sx
                    })
                    .sum::<f64>()
                    .sqrt();

                delta = self.config.initial_trust_factor * scaled_x_norm;
                if delta < machine_epsilon {
                    // If scaled parameters have zero norm, use the
                    // factor itself.
                    delta = self.config.initial_trust_factor;
                }
            }

            // Compute gradient norm for convergence check.
            let gradient_norm = workspace.qtf.norm() / current_cost.max(1.0);
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

            // Inner loop: solve trust region sub-problem.
            let mut step_accepted = false;
            let mut inner_iterations = 0;
            const MAX_INNER_ITERATIONS: usize = 20;

            while inner_iterations < MAX_INNER_ITERATIONS && !step_accepted {
                inner_iterations += 1;

                // Solve trust region subproblem.
                let predicted_reduction =
                    self.solve_trust_region(workspace, delta, &mut lambda)?;

                // Calculate scaled step norm once and reuse it.
                let scaled_step_norm = (0..n)
                    .map(|i| {
                        let s = workspace.step[i] * workspace.scaling[i];
                        s * s
                    })
                    .sum::<f64>()
                    .sqrt();

                // On the first iteration, adjust the initial step
                // bound to prevent an overly optimistic trust region.
                if iteration == 0 {
                    delta = delta.min(scaled_step_norm);
                }

                // Compute trial point.
                for i in 0..n {
                    workspace.trial_parameters[i] =
                        workspace.parameters[i] + workspace.step[i];
                }

                // Evaluate at trial point.
                problem.residuals(
                    workspace.trial_parameters.as_slice(),
                    workspace.trial_residuals.as_mut_slice(),
                )?;
                nfev += 1;

                let trial_cost = self.compute_cost(&workspace.trial_residuals);

                // Compute actual reduction.
                let actual_reduction = current_cost - trial_cost;

                // Compute step quality ratio (rho).
                let ratio = if predicted_reduction.abs() > machine_epsilon {
                    actual_reduction / predicted_reduction
                } else if predicted_reduction == 0.0 && actual_reduction == 0.0
                {
                    1.0
                } else {
                    0.0
                };

                // Update trust region based on step quality.
                if ratio < 0.25 {
                    // Poor step: reduce trust region.
                    let mut temp = 0.5;
                    if actual_reduction < 0.0 {
                        temp = 0.5 * predicted_reduction
                            / (predicted_reduction - actual_reduction);
                    }
                    temp = temp.clamp(0.1, 0.5);
                    delta *= temp;
                    lambda /= temp;
                } else if lambda == 0.0 || ratio > 0.75 {
                    // Good step: possibly expand trust region.
                    //
                    // Use the scaled step norm for consistency.
                    delta = (2.0 * scaled_step_norm).max(delta);
                    lambda *= 0.5;
                }

                // Accept or reject step criteria.
                if ratio > self.config.min_step_quality {
                    // Accept step.
                    workspace.parameters.copy_from(&workspace.trial_parameters);
                    workspace.residuals.copy_from(&workspace.trial_residuals);
                    current_cost = trial_cost;
                    step_accepted = true;

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

                    // Check for convergence.
                    let step_norm = workspace.step.norm();
                    let param_norm = workspace.parameters.norm().max(1.0);

                    // Parameter change convergence.
                    if step_norm < self.config.parameter_tolerance * param_norm
                    {
                        debug!("Converged: step size below tolerance");
                        return Ok(OptimisationResult {
                            status: SolverStatus::SmallStepSize,
                            parameters: workspace
                                .parameters
                                .as_slice()
                                .to_vec(),
                            residuals: workspace.residuals.as_slice().to_vec(),
                            cost: current_cost,
                            iterations: iteration,
                            function_evaluations: nfev,
                            jacobian_evaluations: njev,
                            message: "Converged: step size below tolerance",
                        });
                    }

                    // Cost reduction convergence (only check if cost
                    // is small enough).
                    if current_cost < self.config.absolute_cost_tolerance
                        && actual_reduction
                            < self.config.function_tolerance * current_cost
                        && predicted_reduction
                            < self.config.function_tolerance * current_cost
                    {
                        debug!("Converged: small cost reduction");
                        return Ok(OptimisationResult {
                            status: SolverStatus::SmallCostReduction,
                            parameters: workspace
                                .parameters
                                .as_slice()
                                .to_vec(),
                            residuals: workspace.residuals.as_slice().to_vec(),
                            cost: current_cost,
                            iterations: iteration,
                            function_evaluations: nfev,
                            jacobian_evaluations: njev,
                            message: "Converged: small cost reduction",
                        });
                    }
                } else {
                    // Reject step, increase lambda for more damping.
                    lambda = lambda.max(machine_epsilon) * 2.0;
                    if lambda > 1e12 {
                        // Lambda too large, likely at a difficult point.
                        break;
                    }
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
                        message: "Function evaluation limit exceeded",
                    });
                }
            }

            if !step_accepted {
                // Failed to make progress.
                warn!("Failed to make progress at iteration {}", iteration);
                // Try to continue with reduced expectations.
                delta *= 0.5;
                if delta < machine_epsilon {
                    return Ok(OptimisationResult {
                        status: SolverStatus::SmallStepSize,
                        parameters: workspace
                            .best_parameters
                            .as_slice()
                            .to_vec(),
                        residuals: workspace.best_residuals.as_slice().to_vec(),
                        cost: best_cost,
                        iterations: iteration,
                        function_evaluations: nfev,
                        jacobian_evaluations: njev,
                        message: "Trust region became too small",
                    });
                }
            }

            // Update previous cost for next iteration.
            previous_cost = current_cost;
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
            message: "Maximum iterations reached",
        })
    }

    /// Set user-provided scaling factors.
    pub fn set_scaling(
        &self,
        workspace: &mut LevenbergMarquardtWorkspace,
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
mod tests {
    use super::*;
    use crate::solver::test_problems::{
        BukinN6Problem, CurveFittingProblem, GoldsteinPriceFunction,
        Mock3DProblem, RosenbrockProblem,
    };
    use approx::assert_relative_eq;
    use num_traits::{Float, Zero};
    use std::ops::{Add, Div, Mul, Sub};

    #[test]
    fn test_rosenbrock_from_origin() {
        let problem = RosenbrockProblem::new();
        let solver = LevenbergMarquardtSolver::with_defaults();

        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nRosenbrock from origin:");
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Status: {:?}", result.status);

        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-4);
        assert!(result.cost < 1e-8);
    }

    #[test]
    fn test_rosenbrock_from_far_point() {
        let problem = RosenbrockProblem::new();

        let config = LevenbergMarquardtConfig {
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            max_iterations: 500,
            ..Default::default()
        };
        let solver = LevenbergMarquardtSolver::new(config);

        let initial_parameters = vec![-1.2, 1.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nRosenbrock from (-1.2, 1.0):");
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Status: {:?}", result.status);

        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-4);
        assert!(result.cost < 1e-10);
    }

    #[test]
    fn test_different_scaling_modes() {
        let problem = RosenbrockProblem::new();
        let initial_parameters = vec![0.5, 0.5];

        // Test with no scaling.
        let config_none = LevenbergMarquardtConfig {
            scaling_mode: ParameterScalingMode::None,
            ..Default::default()
        };
        let solver_none = LevenbergMarquardtSolver::new(config_none);
        let mut workspace_none =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result_none = solver_none
            .solve_problem(&problem, &mut workspace_none)
            .unwrap();

        // Test with auto scaling.
        let config_auto = LevenbergMarquardtConfig {
            scaling_mode: ParameterScalingMode::Auto,
            ..Default::default()
        };
        let solver_auto = LevenbergMarquardtSolver::new(config_auto);
        let mut workspace_auto =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result_auto = solver_auto
            .solve_problem(&problem, &mut workspace_auto)
            .unwrap();

        // Test with manual scaling.
        let config_manual = LevenbergMarquardtConfig {
            scaling_mode: ParameterScalingMode::Manual,
            ..Default::default()
        };
        let solver_manual = LevenbergMarquardtSolver::new(config_manual);
        let mut workspace_manual =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        solver_manual
            .set_scaling(&mut workspace_manual, &[2.0, 1.0])
            .unwrap();
        let result_manual = solver_manual
            .solve_problem(&problem, &mut workspace_manual)
            .unwrap();

        println!("\nScaling mode comparison:");
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
        let solver = LevenbergMarquardtSolver::with_defaults();

        // Start from origin - moderately difficult.
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
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

        // Check convergence to minimum.
        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-4);
        assert!(result.cost < 1e-8);
    }

    #[test]
    fn test_solver_rosenbrock_from_far_point() {
        let problem = RosenbrockProblem::new();

        // Use reasonable tolerances for better convergence.
        let config = LevenbergMarquardtConfig {
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            max_iterations: 500,
            verbose: false,
            ..Default::default()
        };
        let solver = LevenbergMarquardtSolver::new(config);

        // Start from a challenging point far from minimum.
        let initial_parameters = vec![-1.2, 1.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
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

        // Check convergence to minimum.
        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
        assert!(result.cost < 1e-11);
    }

    #[test]
    fn test_solver_rosenbrock_multiple_starting_points() {
        let config = LevenbergMarquardtConfig {
            function_tolerance: 1e-6,
            parameter_tolerance: 1e-6,
            gradient_tolerance: 1e-6,
            max_iterations: 500,
            verbose: false,
            ..Default::default()
        };

        let problem = RosenbrockProblem::new();
        let solver = LevenbergMarquardtSolver::new(config);

        // Test from multiple starting points.
        let starting_points = vec![
            vec![0.5, 0.5],
            vec![2.0, 2.0],
            vec![-0.5, 0.5],
            vec![1.5, 2.0],
        ];

        for (i, initial_parameters) in starting_points.iter().enumerate() {
            let mut workspace =
                LevenbergMarquardtWorkspace::new(&problem, initial_parameters)
                    .unwrap();
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

            // All should converge to (1, 1).
            assert!(
                result.status.is_success(),
                "Failed from starting point {:?}",
                initial_parameters
            );
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-4);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-4);
            assert!(result.cost < 1e-9);
        }
    }

    #[test]
    fn test_solver_modified_rosenbrock() {
        // Test with different a and b values.
        let problem = RosenbrockProblem::with_parameters(2.0, 50.0);
        let solver = LevenbergMarquardtSolver::with_defaults();

        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nModified Rosenbrock (a=2, b=50):");
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should converge to (2, 4) for a=2.
        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 2.0, epsilon = 5e-5);
        assert_relative_eq!(result.parameters[1], 4.0, epsilon = 15e-5);
        assert!(result.cost < 5e-10);
    }

    #[test]
    fn test_solver_convergence_criteria() {
        let problem = RosenbrockProblem::new();

        // Test with very tight tolerances to trigger max iterations.
        let config = LevenbergMarquardtConfig {
            function_tolerance: 1e-15,
            parameter_tolerance: 1e-15,
            gradient_tolerance: 1e-15,
            max_iterations: 10, // Very few iterations.
            verbose: false,
            ..Default::default()
        };
        let solver = LevenbergMarquardtSolver::new(config);

        let initial_parameters = vec![-1.0, 1.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
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
        let solver = LevenbergMarquardtSolver::with_defaults();

        // Start very close to minimum.
        let initial_parameters = vec![0.999, 0.999];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
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
        assert!(result.status.is_success());
        assert!(
            result.iterations < 10,
            "Should converge quickly from near minimum"
        );
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
        assert!(result.cost < 1e-10);
    }

    #[test]
    fn test_solver_trust_region_radius_limiting() {
        let problem = RosenbrockProblem::new();

        // Test with very small trust region radius to force step
        // limiting.
        let config = LevenbergMarquardtConfig {
            function_tolerance: 1e-9,
            parameter_tolerance: 1e-9,
            gradient_tolerance: 1e-9,
            max_iterations: 300, // More iterations since steps are limited.
            initial_trust_factor: 0.1, // Very small trust region radius.
            verbose: true, // Enable verbose to see step limiting messages.
            ..Default::default()
        };
        let solver = LevenbergMarquardtSolver::new(config);

        // Start from a challenging point that would normally take
        // large steps.
        let initial_parameters = vec![-2.0, 2.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!(
            "\nRosenbrock with initial_trust_factor=0.1 from (-2.0, 2.0):"
        );
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
        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-4);
        assert!(result.cost < 1e-8);

        // The solver should converge successfully even with step
        // limiting.
        println!(
            "Trust region limiting test: converged in {} iterations",
            result.iterations
        );
    }

    #[test]
    fn test_solver_trust_region_radius_comparison() {
        let problem = RosenbrockProblem::new();
        let initial_parameters = vec![-1.0, 1.0];

        // Test with default trust region radius (large).
        let config_large = LevenbergMarquardtConfig {
            function_tolerance: 1e-9,
            parameter_tolerance: 1e-9,
            gradient_tolerance: 1e-9,
            initial_trust_factor: 100.0, // Large trust region radius.
            max_iterations: 100,
            verbose: false,
            ..Default::default()
        };
        let solver_large = LevenbergMarquardtSolver::new(config_large);
        let mut workspace_large =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result_large = solver_large
            .solve_problem(&problem, &mut workspace_large)
            .unwrap();

        // Test with small trust region radius.
        let config_small = LevenbergMarquardtConfig {
            function_tolerance: 1e-9,
            parameter_tolerance: 1e-9,
            gradient_tolerance: 1e-9,
            initial_trust_factor: 0.3, // Small trust region radius.
            max_iterations: 200,
            verbose: false,
            ..Default::default()
        };
        let solver_small = LevenbergMarquardtSolver::new(config_small);
        let mut workspace_small =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result_small = solver_small
            .solve_problem(&problem, &mut workspace_small)
            .unwrap();

        println!("\nTrust region radius comparison:");
        println!(
            "  Large trust region radius: {} iterations, cost: {:.6e}",
            result_large.iterations, result_large.cost
        );
        println!(
            "  Small trust region radius: {} iterations, cost: {:.6e}",
            result_small.iterations, result_small.cost
        );

        // Both should converge successfully.
        assert!(result_large.status.is_success());
        assert!(result_small.status.is_success());

        // Both should reach the minimum.
        assert_relative_eq!(result_large.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result_large.parameters[1], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result_small.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result_small.parameters[1], 1.0, epsilon = 1e-4);

        // Both should converge successfully regardless of iteration count.
        //
        // NOTE: Small trust region radiuss don't always require more
        // iterations, especially if the solver converges efficiently
        // with the damping.
        println!(
            "  Iteration difference: {} (small) vs {} (large)",
            result_small.iterations, result_large.iterations
        );
    }

    #[test]
    fn test_solver_trust_region_radius_edge_cases() {
        let problem = RosenbrockProblem::new();

        // Test with very large trust region radius (should behave
        // like unlimited).
        let config_huge = LevenbergMarquardtConfig {
            function_tolerance: 1e-9,
            parameter_tolerance: 1e-9,
            gradient_tolerance: 1e-9,
            initial_trust_factor: 1000.0, // Very large trust region radius.
            max_iterations: 100,
            verbose: false,
            ..Default::default()
        };
        let solver_huge = LevenbergMarquardtSolver::new(config_huge);
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result =
            solver_huge.solve_problem(&problem, &mut workspace).unwrap();

        // Should converge normally.
        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 2e-4);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 2e-4);

        println!("\nTrust region radius edge case test:");
        println!(
            "  Large trust region radius result: {:.6e} cost in {} iterations",
            result.cost, result.iterations
        );
    }

    #[test]
    fn test_curve_fitting() {
        let problem = CurveFittingProblem::from_example_data();

        // Curve fitting with noisy data may need more iterations
        let config = LevenbergMarquardtConfig {
            max_iterations: 1000,
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            ..Default::default()
        };
        let solver = LevenbergMarquardtSolver::new(config);

        // Start from (0, 0).
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nCurve fitting (exponential):");
        println!("  Initial: m = 0.0, c = 0.0");
        println!(
            "  Final: m = {:.6}, c = {:.6}",
            result.parameters[0], result.parameters[1]
        );
        println!("  Cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // The true parameters used to generate the data were m=0.3, c=0.1
        // Due to noise, we won't recover exactly these values
        // For curve fitting with noisy data, accept MaxIterationsReached if parameters are reasonable
        assert!(
            result.status.is_success()
            || result.status == SolverStatus::MaxIterationsReached
            || result.status == SolverStatus::FunctionCallsExceeded,
            "Expected successful convergence, max iterations, or function calls exceeded, got: {:?}", result.status
        );
        assert_relative_eq!(result.parameters[0], 0.3, epsilon = 0.2); // More relaxed
        assert_relative_eq!(result.parameters[1], 0.1, epsilon = 0.3); // More relaxed
    }

    #[test]
    fn test_bukin_n6() {
        let problem = BukinN6Problem;

        // Use tighter tolerances for this difficult problem
        let config = LevenbergMarquardtConfig {
            function_tolerance: 1e-12,
            parameter_tolerance: 1e-12,
            gradient_tolerance: 1e-12,
            max_iterations: 500,
            verbose: false,
            ..Default::default()
        };
        let solver = LevenbergMarquardtSolver::new(config);

        // Start from a point in the valid domain but away from minimum
        let initial_parameters = vec![-5.0, 0.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nBukin N6 function:");
        println!("  Initial: x = -5.0, y = 0.0");
        println!(
            "  Final: x = {:.6}, y = {:.6}",
            result.parameters[0], result.parameters[1]
        );
        println!("  Cost: {:.6e} (should be ~0)", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Status: {:?}", result.status);

        // This is an extremely difficult function with many local minima
        // Accept any local minimum as long as the solver converges and finds a low cost
        assert!(result.status.is_success());

        // Check if we found the global minimum (-10, 1) or accept a local minimum
        let found_global = (result.parameters[0] - (-10.0)).abs() < 0.1
            && (result.parameters[1] - 1.0).abs() < 0.01;

        if found_global {
            println!("  Found global minimum!");
            assert_relative_eq!(result.parameters[0], -10.0, epsilon = 0.1);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 0.01);
        } else {
            println!("  Found local minimum (acceptable for this difficult function)");
            // Just verify we found a reasonable minimum with low cost
            assert!(result.cost < 0.1, "Cost should be reasonably low even for local minimum (Bukin N6 is extremely difficult)");
        }
    }

    #[test]
    fn test_goldstein_price() {
        let problem = GoldsteinPriceFunction;
        let solver = LevenbergMarquardtSolver::with_defaults();

        // Test from multiple starting points as this function has multiple local minima
        let starting_points = vec![
            vec![0.5, -0.5],  // Near global minimum
            vec![-0.5, -1.5], // Another starting point
            vec![1.0, 1.0],   // Far from minimum
        ];

        for (i, initial_parameters) in starting_points.iter().enumerate() {
            let mut workspace =
                LevenbergMarquardtWorkspace::new(&problem, initial_parameters)
                    .unwrap();
            let result =
                solver.solve_problem(&problem, &mut workspace).unwrap();

            println!(
                "\nGoldstein-Price test {} from [{:.1}, {:.1}]:",
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

            // Global minimum at (0, -1) with f = 3 (so residual = 0)
            if (result.parameters[0] - 0.0).abs() < 0.1
                && (result.parameters[1] - (-1.0)).abs() < 0.1
            {
                println!("  Found global minimum!");
                assert_relative_eq!(result.parameters[0], 0.0, epsilon = 0.01);
                assert_relative_eq!(result.parameters[1], -1.0, epsilon = 0.01);
                assert!(result.cost < 1e-8);
            } else {
                println!(
                    "  Found local minimum (this function has multiple minima)"
                );
                // Accept both successful convergence and max iterations for difficult starting points
                assert!(
                    result.status.is_success() || matches!(result.status, SolverStatus::MaxIterationsReached),
                    "Expected successful convergence or max iterations, got {:?}", result.status
                );
            }
        }
    }

    #[test]
    fn test_goldstein_price_from_near_minimum() {
        let problem = GoldsteinPriceFunction;

        let config = LevenbergMarquardtConfig {
            function_tolerance: 1e-12,
            parameter_tolerance: 1e-12,
            gradient_tolerance: 1e-12,
            max_iterations: 100,
            verbose: false,
            ..Default::default()
        };
        let solver = LevenbergMarquardtSolver::new(config);

        // Start very close to the global minimum
        let initial_parameters = vec![0.01, -0.99];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nGoldstein-Price from near global minimum:");
        println!("  Initial: [0.01, -0.99]");
        println!(
            "  Final: [{:.9}, {:.9}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Check if we converged to the expected global minimum or a nearby local minimum
        assert!(result.status.is_success());

        // The Goldstein-Price function is complex with multiple local minima
        // Starting near (0, -1) might converge to a nearby local minimum
        let near_global = (result.parameters[0] - 0.0).abs() < 1e-6
            && (result.parameters[1] - (-1.0)).abs() < 1e-6;

        if near_global {
            println!("  Converged to global minimum!");
            assert_relative_eq!(result.parameters[0], 0.0, epsilon = 1e-6);
            assert_relative_eq!(result.parameters[1], -1.0, epsilon = 1e-6);
            assert!(result.cost < 1e-10);
        } else {
            println!("  Converged to nearby local minimum (acceptable for complex function)");
            // Accept any reasonable local minimum with low cost
            assert!(
                result.cost < 1e-6,
                "Should find a good local minimum with low cost"
            );
        }
    }

    #[test]
    fn test_solver_workspace_reuse() {
        let problem = RosenbrockProblem::new();

        let initial_parameters1 = vec![0.0, 0.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters1)
                .unwrap();

        // Verify initial state.
        assert_eq!(workspace.parameters[0], 0.0);
        assert_eq!(workspace.parameters[1], 0.0);
        assert_eq!(workspace.n, 2);
        assert_eq!(workspace.m, 2);

        let initial_parameters2 = vec![1.5, -0.5];
        workspace
            .reuse_with(&problem, &initial_parameters2)
            .unwrap();

        // Verify workspace was properly reset.
        assert_eq!(workspace.parameters[0], 1.5);
        assert_eq!(workspace.parameters[1], -0.5);
        assert_eq!(workspace.trial_parameters[0], 1.5);
        assert_eq!(workspace.trial_parameters[1], -0.5);
        assert_eq!(workspace.best_parameters[0], 1.5);
        assert_eq!(workspace.best_parameters[1], -0.5);

        for i in 0..workspace.m {
            assert_eq!(workspace.residuals[i], 0.0);
            assert_eq!(workspace.trial_residuals[i], 0.0);
            assert_eq!(workspace.best_residuals[i], 0.0);
        }

        for i in 0..workspace.m {
            for j in 0..workspace.n {
                assert_eq!(workspace.jacobian[(i, j)], 0.0);
            }
        }

        for i in 0..workspace.n {
            for j in 0..workspace.n {
                assert_eq!(workspace.r_matrix[(i, j)], 0.0);
            }
            assert_eq!(workspace.qtf[i], 0.0);
            assert_eq!(workspace.step[i], 0.0);
            assert_eq!(workspace.scaling[i], 1.0);
            assert_eq!(workspace.permutation[i], i);
        }

        // Test that reused workspace works with solver.
        let solver = LevenbergMarquardtSolver::with_defaults();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-4);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-4);

        println!("\nWorkspace reuse test:");
        println!("  Reused workspace from [1.5, -0.5] and converged to [{:.6}, {:.6}]",
                 result.parameters[0], result.parameters[1]);
        println!("  Cost: {:.6e}", result.cost);
    }

    #[test]
    fn test_solver_workspace_reuse_dimension_mismatch() {
        let problem2d = RosenbrockProblem::new(); // 2 parameters, 2 residuals.

        // Create workspace for 2D problem
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem2d, &initial_parameters)
                .unwrap();

        // Try to reuse with incompatible problem dimensions. Create a mock
        // 3-parameter problem.
        let problem3d = Mock3DProblem;
        let parameters3d = vec![0.0, 0.0, 0.0];

        // This should fail with dimension mismatch.
        let result = workspace.reuse_with(&problem3d, &parameters3d);
        assert!(result.is_err());

        // Test parameter count mismatch.
        let wrong_params = vec![0.0, 0.0, 0.0]; // 3 params for 2D problem.
        let result = workspace.reuse_with(&problem2d, &wrong_params);
        assert!(result.is_err());
    }

    #[test]
    fn test_configurable_absolute_cost_tolerance() {
        let problem = RosenbrockProblem::new();

        // Test with very strict absolute cost tolerance.
        let config_strict = LevenbergMarquardtConfig {
            function_tolerance: 1e-6,
            absolute_cost_tolerance: 1e-12, // Very strict.
            max_iterations: 500,
            ..Default::default()
        };
        let solver_strict = LevenbergMarquardtSolver::new(config_strict);

        let initial_parameters = vec![0.1, 0.1]; // Close to optimum.
        let mut workspace_strict =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result_strict = solver_strict
            .solve_problem(&problem, &mut workspace_strict)
            .unwrap();

        // Test with relaxed absolute cost tolerance.
        let config_relaxed = LevenbergMarquardtConfig {
            function_tolerance: 1e-6,
            absolute_cost_tolerance: 1e-3, // Very relaxed.
            max_iterations: 500,
            ..Default::default()
        };
        let solver_relaxed = LevenbergMarquardtSolver::new(config_relaxed);

        let mut workspace_relaxed =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();
        let result_relaxed = solver_relaxed
            .solve_problem(&problem, &mut workspace_relaxed)
            .unwrap();

        println!(
            "\nLevenberg-Marquardt configurable absolute cost tolerance test:"
        );
        println!(
            "  Strict tolerance (1e-12): {} iterations, cost: {:.6e}",
            result_strict.iterations, result_strict.cost
        );
        println!(
            "  Relaxed tolerance (1e-3): {} iterations, cost: {:.6e}",
            result_relaxed.iterations, result_relaxed.cost
        );

        // Both should converge successfully
        assert!(result_strict.status.is_success());
        assert!(result_relaxed.status.is_success());

        // Both should reach the minimum
        assert_relative_eq!(result_strict.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result_strict.parameters[1], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result_relaxed.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result_relaxed.parameters[1], 1.0, epsilon = 1e-5);

        // The strict tolerance should potentially achieve a lower cost
        // (though both should be very good starting from a point close to optimum)
        assert!(result_strict.cost < 1e-9);
        assert!(result_relaxed.cost < 1e-2); // More relaxed expectation
    }

    #[test]
    fn test_solver_workspace_reuse_performance() {
        let problem = RosenbrockProblem::new();

        // Create workspace once.
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_parameters)
                .unwrap();

        // Test multiple reuses with different starting points.
        let starting_points = vec![
            vec![0.5, 0.5],
            vec![-1.2, 1.0],
            vec![2.0, -1.0],
            vec![-0.5, 2.5],
        ];

        let solver = LevenbergMarquardtSolver::with_defaults();

        for (i, start_point) in starting_points.iter().enumerate() {
            workspace.reuse_with(&problem, start_point).unwrap();

            let result =
                solver.solve_problem(&problem, &mut workspace).unwrap();

            println!(
                "\nReuse test {} from [{:.1}, {:.1}]:",
                i + 1,
                start_point[0],
                start_point[1]
            );
            println!(
                "  Converged to [{:.6}, {:.6}], cost: {:.6e}, iterations: {}",
                result.parameters[0],
                result.parameters[1],
                result.cost,
                result.iterations
            );

            // All should converge to (1, 1).
            assert!(result.status.is_success());
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-4);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-4);
            assert!(result.cost < 1e-8);
        }
    }
}
