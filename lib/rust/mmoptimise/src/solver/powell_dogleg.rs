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

#[derive(Debug)]
pub struct PowellDogLegWorkspace {
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

    // Dog-leg algorithm workspace.
    gradient: DVector<f64>,          // J^T * residuals.
    gauss_newton_step: DVector<f64>, // Full Gauss-Newton step.
    cauchy_step: DVector<f64>,       // Steepest descent (Cauchy point) step.
    dogleg_step: DVector<f64>,       // Final dog-leg step.
    normal_matrix: DMatrix<f64>,     // J^T * J.

    // Step computation workspace.
    scaling: DVector<f64>, // Parameter scaling factors.
}

impl PowellDogLegWorkspace {
    /// Reuse an existing PowellDogLegWorkspace with new initial
    /// parameters.
    ///
    /// Allows reusing the allocated memory of an existing workspace
    /// as long as the parameter count and residual count match the
    /// new problem. All workspace data is properly reset, but no new
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

        // Update parameter vectors with new initial values.
        self.parameters.copy_from_slice(initial_parameters);
        self.trial_parameters.copy_from_slice(initial_parameters);
        self.best_parameters.copy_from_slice(initial_parameters);

        // Reset all workspace data without reallocating memory.
        self.residuals.fill(0.0);
        self.trial_residuals.fill(0.0);
        self.best_residuals.fill(0.0);
        self.jacobian.fill(0.0);
        self.gradient.fill(0.0);
        self.gauss_newton_step.fill(0.0);
        self.cauchy_step.fill(0.0);
        self.dogleg_step.fill(0.0);
        self.normal_matrix.fill(0.0);
        self.scaling.fill(1.0);

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
            gradient: DVector::zeros(n),
            gauss_newton_step: DVector::zeros(n),
            cauchy_step: DVector::zeros(n),
            dogleg_step: DVector::zeros(n),
            normal_matrix: DMatrix::zeros(n, n),
            scaling: DVector::from_element(n, 1.0),
        })
    }
}

/// Powell Dog-Leg solver with trust region management.
///
/// An implementation of the Powell Dog-Leg algorithm for non-linear
/// least squares optimization. The algorithm combines the robustness
/// of steepest descent with the fast convergence properties of
/// Gauss-Newton near the optimum.
///
/// ## Algorithm Overview
///
/// The Dog-Leg method works by:
/// 1. Computing the Cauchy point (steepest descent step).
/// 2. Computing the Gauss-Newton step.
/// 3. Choosing between these steps or interpolating along the "dog-leg" path.
/// 4. Adapting the trust region based on step quality.
///
/// ## When to Use Dog-Leg vs Other Solvers
///
/// | Use Dog-Leg When                      | Use Levenberg-Marquardt When     | Use Gauss-Newton When            |
/// |---------------------------------------|----------------------------------|----------------------------------|
/// | Moderate to highly nonlinear problems | Highly ill-conditioned problems  | Well-conditioned, near-quadratic |
/// | Good balance of speed and robustness  | Maximum robustness needed        | Maximum speed needed             |
/// | Unknown problem conditioning          | Far from optimum with poor guess | Close to optimum with good guess |
/// | General-purpose optimization          | Difficult convergence cases      | Simple, well-behaved problems    |
///
/// ## Usage Examples
///
/// ### Basic Usage
/// ```rust
/// use mmoptimise_rust::solver::powell_dogleg::{PowellDogLegSolver, PowellDogLegWorkspace};
/// use mmoptimise_rust::solver::test_problems::RosenbrockProblem;
///
/// let solver = PowellDogLegSolver::with_defaults();
/// let problem = RosenbrockProblem::new();
/// let initial_params = vec![0.0, 0.0];
/// let mut workspace = PowellDogLegWorkspace::new(&problem, &initial_params).unwrap();
/// let result = solver.solve_problem(&problem, &mut workspace).unwrap();
///
/// // Verify convergence.
/// assert!(result.iterations > 0);
/// assert!(result.cost < 1e-6);  // Default absolute_cost_tolerance
/// ```
///
/// ### Custom Configuration
/// ```rust
/// use mmoptimise_rust::solver::powell_dogleg::{PowellDogLegSolver, PowellDogLegConfig};
/// use mmoptimise_rust::solver::common::ParameterScalingMode;
///
/// let config = PowellDogLegConfig {
///     function_tolerance: 1e-8,
///     max_iterations: 200,
///     scaling_mode: ParameterScalingMode::Auto,
///     initial_trust_radius: 10.0,
///     verbose: false,
///     ..Default::default()
/// };
/// let solver = PowellDogLegSolver::new(config);
///
/// // Configuration is ready for use.
/// assert_eq!(config.function_tolerance, 1e-8);
/// assert_eq!(config.max_iterations, 200);
/// ```
///
/// ## Algorithm Details
///
/// ### Trust Region Management
/// The algorithm maintains a trust region radius Δ and adapts it based on
/// the quality of each step:
/// - **Good steps** (ρ > 0.75): Expand trust region
/// - **Acceptable steps** (ρ > 0.25): Keep trust region
/// - **Poor steps** (ρ < 0.25): Shrink trust region and retry
///
/// ### Step Selection Strategy
/// ```text
/// 1. If ||p_GN|| ≤ Δ: Use full Gauss-Newton step
/// 2. If ||p_C|| ≥ Δ: Use scaled Cauchy step
/// 3. Otherwise: Interpolate along dog-leg path
/// ```
///
/// Where:
/// - `p_GN` is the Gauss-Newton step: `(J^T J)^(-1) J^T r`
/// - `p_C` is the Cauchy step: `α g` where `g = J^T r` and `α` minimizes along gradient
///
/// ## Performance Tips
///
/// - **Initial Parameters**: Good initial guess improves convergence speed
/// - **Trust Region Size**: Start with `initial_trust_radius` ≈ ||x₀||
/// - **Scaling**: Use `ParameterScalingMode::Auto` for mixed parameter scales
/// - **Workspace Reuse**: Reuse workspace for similar problems to avoid allocation
///
/// ## Troubleshooting Guide
///
/// ### Slow Convergence
/// ```rust
/// use mmoptimise_rust::solver::powell_dogleg::PowellDogLegConfig;
/// use mmoptimise_rust::solver::common::ParameterScalingMode;
///
/// let config = PowellDogLegConfig {
///     initial_trust_radius: 1.0,  // Smaller for conservative steps
///     max_iterations: 500,        // More iterations allowed
///     scaling_mode: ParameterScalingMode::Auto,
///     ..Default::default()
/// };
/// ```
///
/// ### Poor Convergence from Bad Initial Guess
/// ```rust
/// use mmoptimise_rust::solver::powell_dogleg::{PowellDogLegSolver, PowellDogLegWorkspace};
/// use mmoptimise_rust::solver::test_problems::RosenbrockProblem;
///
/// // Try multiple starting points
/// let starting_points = vec![
///     vec![0.0, 0.0],
///     vec![0.5, 0.5],
///     vec![-0.5, -0.5],
/// ];
///
/// let problem = RosenbrockProblem::new();
/// let solver = PowellDogLegSolver::with_defaults();
/// for start in starting_points {
///     let mut workspace = PowellDogLegWorkspace::new(&problem, &start).unwrap();
///     let result = solver.solve_problem(&problem, &mut workspace).unwrap();
///     if result.status.is_success() {
///         println!("Converged from {:?}", start);
///         break;
///     }
/// }
/// ```
///
/// ### Numerical Issues
/// ```rust
/// use mmoptimise_rust::solver::powell_dogleg::PowellDogLegConfig;
///
/// let config = PowellDogLegConfig {
///     cauchy_regularization: 1e-8,  // Increase if Cauchy step computation fails.
///     gn_regularization: 1e-8,      // Increase if Gauss-Newton step fails.
///     epsilon_factor: 10.0,         // More conservative numerical tolerances.
///     ..Default::default()
/// };
/// ```
pub struct PowellDogLegSolver {
    config: PowellDogLegConfig,
}

/// Configuration parameters for the Powell Dog-Leg solver.
///
/// The Dog-Leg method requires fewer parameters than
/// Levenberg-Marquardt since it doesn't need damping parameter
/// tuning, but it adds trust region specific controls.
///
/// ## Default Configuration
/// The default settings are suitable for most optimization problems:
/// ```rust
/// use mmoptimise_rust::solver::powell_dogleg::PowellDogLegConfig;
///
/// let config = PowellDogLegConfig::default();
/// assert_eq!(config.function_tolerance, 1e-6);
/// assert_eq!(config.absolute_cost_tolerance, 1e-6);
/// assert_eq!(config.initial_trust_radius, 1.0);
/// assert_eq!(config.max_iterations, 100);
/// ```
///
/// ## Configuration Examples
///
/// ### High Precision
/// ```rust
/// use mmoptimise_rust::solver::powell_dogleg::PowellDogLegConfig;
/// use mmoptimise_rust::solver::common::ParameterScalingMode;
///
/// let precise = PowellDogLegConfig {
///     function_tolerance: 1e-12,
///     parameter_tolerance: 1e-12,
///     gradient_tolerance: 1e-12,
///     absolute_cost_tolerance: 1e-12,
///     max_iterations: 500,
///     scaling_mode: ParameterScalingMode::Auto,
///     ..Default::default()
/// };
/// ```
///
/// ### Fast Approximation
/// ```rust
/// use mmoptimise_rust::solver::powell_dogleg::PowellDogLegConfig;
///
/// let fast = PowellDogLegConfig {
///     function_tolerance: 1e-4,
///     parameter_tolerance: 1e-4,
///     gradient_tolerance: 1e-4,
///     absolute_cost_tolerance: 1e-4,
///     max_iterations: 50,
///     initial_trust_radius: 10.0,  // Larger for faster convergence.
///     ..Default::default()
/// };
/// ```
///
/// ### Conservative (Robust)
/// ```rust
/// use mmoptimise_rust::solver::powell_dogleg::PowellDogLegConfig;
///
/// let robust = PowellDogLegConfig {
///     initial_trust_radius: 0.1,      // Small initial steps
///     min_trust_radius: 1e-12,        // Allow very small steps
///     max_trust_radius: 100.0,        // Limit maximum step size
///     trust_expand_factor: 1.5,       // Conservative expansion
///     trust_shrink_factor: 0.25,      // Aggressive shrinkage
///     ..Default::default()
/// };
/// ```
#[derive(Debug, Clone, Copy)]
pub struct PowellDogLegConfig {
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
    /// Scaling mode for parameters.
    pub scaling_mode: ParameterScalingMode,
    /// Enable verbose output.
    pub verbose: bool,
    /// Machine epsilon multiplier for numerical tolerances.
    pub epsilon_factor: f64,
    /// Initial trust region radius.
    pub initial_trust_radius: f64,
    /// Minimum trust region radius (algorithm stops if smaller).
    pub min_trust_radius: f64,
    /// Maximum trust region radius.
    pub max_trust_radius: f64,
    /// Factor to expand trust region on good steps.
    pub trust_expand_factor: f64,
    /// Factor to shrink trust region on poor steps.
    pub trust_shrink_factor: f64,
    /// Minimum step quality ratio to accept step.
    pub min_step_quality: f64,
    /// Regularization for Cauchy step computation.
    pub cauchy_regularization: f64,
    /// Regularization for Gauss-Newton step computation.
    pub gn_regularization: f64,
    /// Absolute cost tolerance - convergence when cost is below this absolute threshold.
    /// Used in conjunction with relative improvements to determine convergence.
    pub absolute_cost_tolerance: f64,
}

impl Default for PowellDogLegConfig {
    fn default() -> Self {
        Self {
            function_tolerance: 1e-6,
            parameter_tolerance: 1e-6,
            gradient_tolerance: 1e-6,
            max_iterations: 100,
            max_function_evaluations: 1000,
            scaling_mode: ParameterScalingMode::Auto,
            verbose: false,
            epsilon_factor: 1.0,
            initial_trust_radius: 1.0,
            min_trust_radius: 1e-10,
            max_trust_radius: 1e3,
            trust_expand_factor: 2.0,
            trust_shrink_factor: 0.5,
            min_step_quality: 1e-4,
            cauchy_regularization: 1e-10,
            gn_regularization: 1e-10,
            absolute_cost_tolerance: 1e-6,
        }
    }
}

impl PowellDogLegSolver {
    pub fn new(config: PowellDogLegConfig) -> Self {
        Self { config }
    }

    pub fn with_defaults() -> Self {
        Self {
            config: PowellDogLegConfig::default(),
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
        workspace: &mut PowellDogLegWorkspace,
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

    /// Compute the Cauchy point (steepest descent step with trust
    /// region constraint).
    ///
    /// The Cauchy point is the minimizer of the quadratic model along
    /// the steepest descent direction, subject to the trust region
    /// constraint.
    fn compute_cauchy_step(
        &self,
        workspace: &mut PowellDogLegWorkspace,
        trust_radius: f64,
    ) -> Result<()> {
        let n = workspace.n;

        // Compute gradient: g = J^T * r
        workspace.gradient =
            workspace.jacobian.transpose() * &workspace.residuals;

        // Check for zero gradient.
        let gradient_norm = workspace.gradient.norm();
        if gradient_norm < f64::EPSILON * self.config.epsilon_factor {
            workspace.cauchy_step.fill(0.0);
            return Ok(());
        }

        // Compute J * g for quadratic term.
        let jg = &workspace.jacobian * &workspace.gradient;
        let alpha_denom = jg.norm_squared() + self.config.cauchy_regularization;

        // Compute optimal step length along gradient direction.
        let alpha_unconstrained = gradient_norm * gradient_norm / alpha_denom;

        // Apply trust region constraint.
        let gradient_step_norm = alpha_unconstrained * gradient_norm;
        let alpha = if gradient_step_norm <= trust_radius {
            alpha_unconstrained
        } else {
            trust_radius / gradient_norm
        };

        // Compute Cauchy step:
        // p_C = -α * g
        for i in 0..n {
            workspace.cauchy_step[i] = -alpha * workspace.gradient[i];
        }

        Ok(())
    }

    /// Compute the Gauss-Newton step.
    ///
    /// Solves (J^T J + regularization * I) p = -J^T r
    fn compute_gauss_newton_step(
        &self,
        workspace: &mut PowellDogLegWorkspace,
    ) -> Result<bool> {
        let n = workspace.n;

        // Compute normal matrix: J^T J.
        workspace.normal_matrix =
            workspace.jacobian.transpose() * &workspace.jacobian;

        // Add regularization to diagonal.
        for i in 0..n {
            let scale = workspace.scaling[i];
            workspace.normal_matrix[(i, i)] +=
                self.config.gn_regularization * scale * scale;
        }

        // Compute right-hand side: -J^T r
        let neg_gradient = -&workspace.gradient;

        // Try Cholesky decomposition first.
        if let Some(chol) = workspace.normal_matrix.clone().cholesky() {
            workspace.gauss_newton_step = chol.solve(&neg_gradient);
            return Ok(true);
        }

        // Fall back to QR decomposition.
        let qr = workspace.normal_matrix.clone().qr();
        let q = qr.q();
        let r = qr.r();

        // Check for rank deficiency and handle near-zero diagonal elements.
        let machine_epsilon = f64::EPSILON * self.config.epsilon_factor;
        let r_diag = r.diagonal();
        let max_diag = r_diag.iter().fold(0.0, |a, &b| a.max(b.abs()));
        let min_diag =
            r_diag.iter().fold(f64::INFINITY, |a, &b| a.min(b.abs()));

        // Create a mutable copy of R to handle singular diagonal
        // elements.
        let mut r_regularized = r.clone();

        // Handle near-zero diagonal elements.
        for i in 0..n {
            if r_regularized[(i, i)].abs() < machine_epsilon * max_diag {
                let regularization_value = if max_diag > 0.0 {
                    machine_epsilon * max_diag
                } else {
                    machine_epsilon
                };
                r_regularized[(i, i)] =
                    regularization_value.copysign(r_regularized[(i, i)]);
            }
        }

        if min_diag < machine_epsilon * max_diag {
            warn!(
                "Near-singular normal matrix detected, applying diagonal regularization"
            );
        }

        // Solve R * step = Q^T * (-gradient)
        let qt_b = q.transpose() * neg_gradient;
        workspace.gauss_newton_step = DVector::zeros(n);

        for i in (0..n).rev() {
            let mut sum = qt_b[i];
            for j in (i + 1)..n {
                sum -= r_regularized[(i, j)] * workspace.gauss_newton_step[j];
            }
            workspace.gauss_newton_step[i] = sum / r_regularized[(i, i)];
        }

        Ok(true)
    }

    /// Compute the dog-leg step by choosing between Cauchy,
    /// Gauss-Newton, or interpolated step.
    ///
    /// The dog-leg path consists of:
    ///
    /// 1. Cauchy point to Gauss-Newton step interpolation if both fit
    ///    in trust region.
    ///
    /// 2. Scaled Cauchy step if Gauss-Newton step is too large.
    ///
    /// 3. Full Gauss-Newton step if it fits in trust region.
    ///
    fn compute_dogleg_step(
        &self,
        workspace: &mut PowellDogLegWorkspace,
        trust_radius: f64,
    ) -> Result<()> {
        let n = workspace.n;

        // Compute step norms with scaling.
        let cauchy_norm = (0..n)
            .map(|i| {
                let s = workspace.cauchy_step[i] * workspace.scaling[i];
                s * s
            })
            .sum::<f64>()
            .sqrt();

        let gn_norm = (0..n)
            .map(|i| {
                let s = workspace.gauss_newton_step[i] * workspace.scaling[i];
                s * s
            })
            .sum::<f64>()
            .sqrt();

        if gn_norm <= trust_radius {
            // Use full Gauss-Newton step if it's within trust region.
            workspace
                .dogleg_step
                .copy_from(&workspace.gauss_newton_step);
        } else if cauchy_norm >= trust_radius {
            // Scale Cauchy step to trust region boundary.
            let scale_factor = trust_radius / cauchy_norm;
            for i in 0..n {
                workspace.dogleg_step[i] =
                    scale_factor * workspace.cauchy_step[i];
            }
        } else {
            // Interpolate along dog-leg path from Cauchy to Gauss-Newton.
            //
            // Find intersection of dog-leg path with trust region boundary.

            // Dog-leg path: p(τ) = p_C + τ(p_GN - p_C) for τ ∈ [0,1]
            // We need to find τ such that ||p(τ)|| = trust_radius

            let mut diff_step = DVector::zeros(n);
            for i in 0..n {
                diff_step[i] =
                    workspace.gauss_newton_step[i] - workspace.cauchy_step[i];
            }

            // Quadratic equation coefficients for ||p_C + τ(p_GN - p_C)||² = Δ²
            let a = (0..n)
                .map(|i| {
                    let s = diff_step[i] * workspace.scaling[i];
                    s * s
                })
                .sum::<f64>();

            let b = 2.0
                * (0..n)
                    .map(|i| {
                        let cs =
                            workspace.cauchy_step[i] * workspace.scaling[i];
                        let ds = diff_step[i] * workspace.scaling[i];
                        cs * ds
                    })
                    .sum::<f64>();

            let c = cauchy_norm * cauchy_norm - trust_radius * trust_radius;

            // Solve quadratic:
            // aτ² + bτ + c = 0
            let discriminant = b * b - 4.0 * a * c;
            if discriminant < 0.0 || a.abs() < f64::EPSILON {
                // Use scaled Cauchy step directly as a fallback.
                // This ensures we stay within the trust region
                // without invalid tau > 1.
                let scale_factor = trust_radius / cauchy_norm;
                for i in 0..n {
                    workspace.dogleg_step[i] =
                        scale_factor * workspace.cauchy_step[i];
                }
            } else {
                // Take the positive root.
                let sqrt_disc = discriminant.sqrt();
                let tau1 = (-b + sqrt_disc) / (2.0 * a);
                let tau2 = (-b - sqrt_disc) / (2.0 * a);

                let tau = if tau1 >= 0.0 && tau1 <= 1.0 {
                    tau1
                } else if tau2 >= 0.0 && tau2 <= 1.0 {
                    tau2
                } else {
                    // Clamp to [0, 1].
                    tau1.clamp(0.0, 1.0)
                };

                // Compute interpolated step:
                // p = p_C + τ(p_GN - p_C)
                for i in 0..n {
                    workspace.dogleg_step[i] =
                        workspace.cauchy_step[i] + tau * diff_step[i];
                }
            }
        }

        Ok(())
    }

    /// Update parameter scaling based on Jacobian column norms.
    fn update_scaling(&self, workspace: &mut PowellDogLegWorkspace) {
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

    /// Main solver routine.
    pub fn solve_problem<P: OptimisationProblem>(
        &self,
        problem: &P,
        workspace: &mut PowellDogLegWorkspace,
    ) -> Result<OptimisationResult> {
        let n = workspace.n;
        let machine_epsilon = f64::EPSILON * self.config.epsilon_factor;

        // Initialize counters.
        let mut nfev = 0;
        let mut njev = 0;

        // Initialize trust region parameters.
        let mut trust_radius = self.config.initial_trust_radius;
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
        for iteration in 0..self.config.max_iterations {
            if self.config.verbose {
                info!(
                    "Powell Dog-Leg Iteration {}: cost = {:.6e}, trust_radius = {:.6e}",
                    iteration, current_cost, trust_radius
                );
            }

            // Check for absolute cost convergence.
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

            // Check for relative cost improvement.
            if iteration > 0 && previous_cost > current_cost {
                let relative_improvement =
                    (previous_cost - current_cost) / previous_cost.max(1.0);
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

            // Compute gradient:
            // g = J^T * r
            workspace.gradient =
                workspace.jacobian.transpose() * &workspace.residuals;

            // Update scaling on first iteration or if requested.
            if iteration == 0
                || self.config.scaling_mode == ParameterScalingMode::Auto
            {
                self.update_scaling(workspace);
            }

            // Check gradient norm for convergence.
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

            // Trust region sub-problem loop.
            let mut step_accepted = false;
            let max_trust_iterations = 20;

            for _trust_iter in 0..max_trust_iterations {
                // Check trust region bounds.
                if trust_radius < self.config.min_trust_radius {
                    debug!("Trust region became too small");
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

                // Compute Gauss-Newton step first.
                let gn_success = self.compute_gauss_newton_step(workspace)?;

                if !gn_success {
                    // If Gauss-Newton fails, compute and use Cauchy
                    // step only.
                    self.compute_cauchy_step(workspace, trust_radius)?;
                    workspace.dogleg_step.copy_from(&workspace.cauchy_step);
                } else {
                    // Check if Gauss-Newton step fits within trust
                    // region.
                    let gn_norm = (0..n)
                        .map(|i| {
                            let s = workspace.gauss_newton_step[i]
                                * workspace.scaling[i];
                            s * s
                        })
                        .sum::<f64>()
                        .sqrt();

                    if gn_norm <= trust_radius {
                        // Use full Gauss-Newton step (most efficient path).
                        workspace
                            .dogleg_step
                            .copy_from(&workspace.gauss_newton_step);
                    } else {
                        // Only now compute Cauchy step for dog-leg
                        // interpolation.
                        self.compute_cauchy_step(workspace, trust_radius)?;
                        self.compute_dogleg_step(workspace, trust_radius)?;
                    }
                }

                // Compute trial point.
                for i in 0..n {
                    workspace.trial_parameters[i] =
                        workspace.parameters[i] + workspace.dogleg_step[i];
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

                // Compute predicted reduction using quadratic model.
                // pred_red = -g^T p - 0.5 p^T J^T J p
                let grad_term = workspace.gradient.dot(&workspace.dogleg_step);
                let jp = &workspace.jacobian * &workspace.dogleg_step;
                let hessian_term = 0.5 * jp.norm_squared();
                let predicted_reduction = -(grad_term + hessian_term);

                // Compute step quality ratio.
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
                    // Poor step: shrink trust region.
                    trust_radius *= self.config.trust_shrink_factor;
                } else if ratio > 0.75 {
                    // Good step: expand trust region.
                    //
                    // Standard algorithm: expand whenever ratio > 0.75
                    trust_radius = (trust_radius
                        * self.config.trust_expand_factor)
                        .min(self.config.max_trust_radius);
                }

                // Accept or reject step.
                if ratio > self.config.min_step_quality {
                    // Accept step.
                    workspace.parameters.copy_from(&workspace.trial_parameters);
                    workspace.residuals.copy_from(&workspace.trial_residuals);
                    previous_cost = current_cost;
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
                        message: "Function evaluation limit exceeded",
                    });
                }
            }

            if !step_accepted {
                warn!(
                    "Failed to find acceptable step at iteration {}",
                    iteration
                );
                return Ok(OptimisationResult {
                    status: SolverStatus::SmallStepSize,
                    parameters: workspace.best_parameters.as_slice().to_vec(),
                    residuals: workspace.best_residuals.as_slice().to_vec(),
                    cost: best_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    jacobian_evaluations: njev,
                    message: "Failed to find acceptable step",
                });
            }

            // Check for convergence based on step size.
            let step_norm = workspace.dogleg_step.norm();
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
            if current_cost < self.config.absolute_cost_tolerance {
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
            message: "Maximum iterations reached",
        })
    }

    /// Set user-provided scaling factors.
    pub fn set_scaling(
        &self,
        workspace: &mut PowellDogLegWorkspace,
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
    fn test_powell_dogleg_rosenbrock_from_origin() {
        let problem = RosenbrockProblem::new();
        let solver = PowellDogLegSolver::with_defaults();

        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nPowell Dog-Leg on Rosenbrock from origin:");
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
        assert!(result.cost < 1e-9);
    }

    #[test]
    fn test_powell_dogleg_rosenbrock_from_far_point() {
        let problem = RosenbrockProblem::new();

        let config = PowellDogLegConfig {
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            max_iterations: 500,
            ..Default::default()
        };
        let solver = PowellDogLegSolver::new(config);

        let initial_parameters = vec![-1.2, 1.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nPowell Dog-Leg on Rosenbrock from (-1.2, 1.0):");
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
        assert!(result.cost < 1e-11);
    }

    #[test]
    fn test_powell_dogleg_different_trust_radius() {
        let problem = RosenbrockProblem::new();
        let initial_parameters = vec![0.0, 0.0];

        let trust_radii = vec![0.1, 1.0, 10.0];

        for trust_radius in trust_radii {
            let config = PowellDogLegConfig {
                initial_trust_radius: trust_radius,
                ..Default::default()
            };
            let solver = PowellDogLegSolver::new(config);

            let mut workspace =
                PowellDogLegWorkspace::new(&problem, &initial_parameters)
                    .unwrap();
            let result =
                solver.solve_problem(&problem, &mut workspace).unwrap();

            println!(
                "\nTrust radius {}: {} iters, cost: {:.6e}",
                trust_radius, result.iterations, result.cost
            );

            // All should converge
            assert!(result.status.is_success());
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
        }
    }

    #[test]
    fn test_powell_dogleg_scaling_modes() {
        let problem = RosenbrockProblem::new();
        let initial_parameters = vec![0.5, 0.5];

        // Test with no scaling.
        let config_none = PowellDogLegConfig {
            scaling_mode: ParameterScalingMode::None,
            ..Default::default()
        };
        let solver_none = PowellDogLegSolver::new(config_none);
        let mut workspace_none =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_none = solver_none
            .solve_problem(&problem, &mut workspace_none)
            .unwrap();

        // Test with auto scaling.
        let config_auto = PowellDogLegConfig {
            scaling_mode: ParameterScalingMode::Auto,
            ..Default::default()
        };
        let solver_auto = PowellDogLegSolver::new(config_auto);
        let mut workspace_auto =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_auto = solver_auto
            .solve_problem(&problem, &mut workspace_auto)
            .unwrap();

        // Test with manual scaling.
        let config_manual = PowellDogLegConfig {
            scaling_mode: ParameterScalingMode::Manual,
            ..Default::default()
        };
        let solver_manual = PowellDogLegSolver::new(config_manual);
        let mut workspace_manual =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        solver_manual
            .set_scaling(&mut workspace_manual, &[2.0, 1.0])
            .unwrap();
        let result_manual = solver_manual
            .solve_problem(&problem, &mut workspace_manual)
            .unwrap();

        println!("\nPowell Dog-Leg scaling mode comparison:");
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
    fn test_powell_dogleg_curve_fitting() {
        let problem = CurveFittingProblem::from_example_data();

        let config = PowellDogLegConfig {
            max_iterations: 200,
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            ..Default::default()
        };
        let solver = PowellDogLegSolver::new(config);

        // Start from (0, 0).
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nPowell Dog-Leg curve fitting (exponential):");
        println!("  Initial: m = 0.0, c = 0.0");
        println!(
            "  Final: m = {:.6}, c = {:.6}",
            result.parameters[0], result.parameters[1]
        );
        println!("  Cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // The true parameters used to generate the data were m=0.3, c=0.1
        //
        // Due to noise, we won't recover exactly these values.
        assert!(
            result.status.is_success()
                || result.status == SolverStatus::MaxIterationsReached
        );
        assert_relative_eq!(result.parameters[0], 0.3, epsilon = 0.2);
        assert_relative_eq!(result.parameters[1], 0.1, epsilon = 0.3);
    }

    #[test]
    fn test_powell_dogleg_workspace_reuse() {
        let problem = RosenbrockProblem::new();

        let initial_parameters1 = vec![0.0, 0.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters1).unwrap();

        // Verify initial state.
        assert_eq!(workspace.parameters[0], 0.0);
        assert_eq!(workspace.parameters[1], 0.0);

        let initial_parameters2 = vec![0.5, -0.5];
        workspace
            .reuse_with(&problem, &initial_parameters2)
            .unwrap();

        // Verify workspace was properly reset.
        assert_eq!(workspace.parameters[0], 0.5);
        assert_eq!(workspace.parameters[1], -0.5);
        assert_eq!(workspace.trial_parameters[0], 0.5);
        assert_eq!(workspace.trial_parameters[1], -0.5);

        // Test that reused workspace works with solver.
        let solver = PowellDogLegSolver::with_defaults();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);

        println!("\nPowell Dog-Leg workspace reuse test:");
        println!("  Reused workspace from [0.5, -0.5] and converged to [{:.6}, {:.6}]",
                 result.parameters[0], result.parameters[1]);
        println!("  Cost: {:.6e}", result.cost);
    }

    #[test]
    fn test_powell_dogleg_multiple_starting_points() {
        let config = PowellDogLegConfig {
            function_tolerance: 1e-6,
            parameter_tolerance: 1e-6,
            gradient_tolerance: 1e-6,
            max_iterations: 200,
            verbose: false,
            ..Default::default()
        };

        let problem = RosenbrockProblem::new();
        let solver = PowellDogLegSolver::new(config);

        // Test from multiple starting points.
        let starting_points = vec![
            vec![0.5, 0.5],
            vec![2.0, 2.0],
            vec![-0.5, 0.5],
            vec![1.5, 2.0],
        ];

        for (i, initial_parameters) in starting_points.iter().enumerate() {
            let mut workspace =
                PowellDogLegWorkspace::new(&problem, initial_parameters)
                    .unwrap();
            let result =
                solver.solve_problem(&problem, &mut workspace).unwrap();

            println!(
                "\nPowell Dog-Leg test {} from [{:.1}, {:.1}]:",
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
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
            assert!(result.cost < 1e-10);
        }
    }

    #[test]
    fn test_powell_dogleg_rosenbrock_problem_at_minimum() {
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
    fn test_powell_dogleg_rosenbrock_problem_away_from_minimum() {
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
    fn test_powell_dogleg_goldstein_price() {
        let problem = GoldsteinPriceFunction;

        let config = PowellDogLegConfig {
            function_tolerance: 1e-8,
            parameter_tolerance: 1e-8,
            gradient_tolerance: 1e-8,
            max_iterations: 100,
            initial_trust_radius: 0.5, // Smaller trust region for this complex function.
            ..Default::default()
        };
        let solver = PowellDogLegSolver::new(config);

        // Start reasonably close to the global minimum.
        let initial_parameters = vec![0.2, -0.8];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nPowell Dog-Leg on Goldstein-Price function:");
        println!("  Initial: [0.2, -0.8]");
        println!(
            "  Final: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Status: {:?}", result.status);

        // Should converge to a reasonable local minimum
        assert!(
            result.status.is_success()
                || result.status == SolverStatus::MaxIterationsReached
        );

        // Global minimum is at (0, -1), but we might find a local minimum.
        let near_global = (result.parameters[0] - 0.0).abs() < 0.5
            && (result.parameters[1] - (-1.0)).abs() < 0.5;

        if near_global {
            println!("  Found region near global minimum!");
        } else {
            println!("  Found local minimum (acceptable for complex function)");
            // Accept any reasonable local minimum with low cost.
            assert!(
                result.cost < 10.0,
                "Should find a reasonable local minimum"
            );
        }
    }

    #[test]
    fn test_powell_dogleg_modified_rosenbrock() {
        // Test with different a and b values.
        let problem = RosenbrockProblem::with_parameters(2.0, 50.0);
        let solver = PowellDogLegSolver::with_defaults();

        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nPowell Dog-Leg Modified Rosenbrock (a=2, b=50):");
        println!(
            "  Final parameters: [{:.6}, {:.6}]",
            result.parameters[0], result.parameters[1]
        );
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);

        // Should converge to (2, 4) for a=2.
        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 2.0, epsilon = 5e-5);
        assert_relative_eq!(result.parameters[1], 4.0, epsilon = 1e-4);
        assert!(result.cost < 5e-10);
    }

    #[test]
    fn test_powell_dogleg_near_minimum_start() {
        let problem = RosenbrockProblem::new();
        let solver = PowellDogLegSolver::with_defaults();

        // Start very close to minimum.
        let initial_parameters = vec![0.999, 0.999];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nPowell Dog-Leg from near minimum:");
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
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-6);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-6);
        assert!(result.cost < 1e-11);
    }

    #[test]
    fn test_powell_dogleg_tau_interpolation_bug_fix() {
        // This test creates a scenario that would trigger the tau > 1 bug
        // in the original implementation.
        let problem = RosenbrockProblem::new();

        let config = PowellDogLegConfig {
            initial_trust_radius: 0.01, // Very small trust region
            max_iterations: 50,
            function_tolerance: 1e-6,
            parameter_tolerance: 1e-6,
            gradient_tolerance: 1e-6,
            verbose: false,
            ..Default::default()
        };
        let solver = PowellDogLegSolver::new(config);

        // Start from a point that creates a case where Cauchy norm < trust_radius
        // but the quadratic equation for tau would fail or give tau > 1
        let initial_parameters = vec![0.1, 0.1];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\\nPowell Dog-Leg tau interpolation bug fix test:");
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

        // Should still converge successfully without the tau > 1 bug
        assert!(
            result.status.is_success()
                || result.status == SolverStatus::MaxIterationsReached
                || result.status == SolverStatus::ToleranceReached
        );

        // Should make reasonable progress toward the optimum
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
    fn test_powell_dogleg_convergence_criteria() {
        let problem = RosenbrockProblem::new();

        // Test with very tight tolerances to trigger max iterations.
        let config = PowellDogLegConfig {
            function_tolerance: 1e-15,
            parameter_tolerance: 1e-15,
            gradient_tolerance: 1e-15,
            max_iterations: 10, // Very few iterations.
            verbose: false,
            ..Default::default()
        };
        let solver = PowellDogLegSolver::new(config);

        let initial_parameters = vec![-0.5, 1.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nPowell Dog-Leg with max_iterations=10:");
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

        // Should hit max iterations or converge early.
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
    fn test_powell_dogleg_trust_region_radius_limiting() {
        let problem = RosenbrockProblem::new();

        // Test with very small trust region radius to force step limiting.
        let config = PowellDogLegConfig {
            function_tolerance: 1e-9,
            parameter_tolerance: 1e-9,
            gradient_tolerance: 1e-9,
            max_iterations: 300, // More iterations since steps are limited.
            initial_trust_radius: 0.1, // Very small trust region radius.
            verbose: false,
            ..Default::default()
        };
        let solver = PowellDogLegSolver::new(config);

        // Start from a challenging point that would normally take large steps.
        let initial_parameters = vec![-2.0, 2.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!(
            "\nPowell Dog-Leg with initial_trust_radius=0.1 from (-2.0, 2.0):"
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

        // Should eventually converge to minimum (1, 1), but may take more iterations.
        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
        assert!(result.cost < 1e-9);

        // The solver should converge successfully even with step limiting.
        println!(
            "Trust region limiting test: converged in {} iterations",
            result.iterations
        );
    }

    #[test]
    fn test_powell_dogleg_trust_region_radius_comparison() {
        let problem = RosenbrockProblem::new();
        let initial_parameters = vec![-1.0, 1.0];

        // Test with default trust region radius (large).
        let config_large = PowellDogLegConfig {
            function_tolerance: 1e-9,
            parameter_tolerance: 1e-9,
            gradient_tolerance: 1e-9,
            initial_trust_radius: 100.0, // Large trust region radius.
            max_iterations: 100,
            verbose: false,
            ..Default::default()
        };
        let solver_large = PowellDogLegSolver::new(config_large);
        let mut workspace_large =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_large = solver_large
            .solve_problem(&problem, &mut workspace_large)
            .unwrap();

        // Test with small trust region radius.
        let config_small = PowellDogLegConfig {
            function_tolerance: 1e-9,
            parameter_tolerance: 1e-9,
            gradient_tolerance: 1e-9,
            initial_trust_radius: 0.3, // Small trust region radius.
            max_iterations: 200,
            verbose: false,
            ..Default::default()
        };
        let solver_small = PowellDogLegSolver::new(config_small);
        let mut workspace_small =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_small = solver_small
            .solve_problem(&problem, &mut workspace_small)
            .unwrap();

        println!("\nPowell Dog-Leg trust region radius comparison:");
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
        assert_relative_eq!(result_large.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result_large.parameters[1], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result_small.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result_small.parameters[1], 1.0, epsilon = 1e-5);

        // Both should converge successfully regardless of iteration count.
        println!(
            "  Iteration difference: {} (small) vs {} (large)",
            result_small.iterations, result_large.iterations
        );
    }

    #[test]
    fn test_powell_dogleg_trust_region_radius_edge_cases() {
        let problem = RosenbrockProblem::new();

        // Test with very large trust region radius (should behave like unlimited).
        let config_huge = PowellDogLegConfig {
            function_tolerance: 1e-9,
            parameter_tolerance: 1e-9,
            gradient_tolerance: 1e-9,
            initial_trust_radius: 1000.0, // Very large trust region radius.
            max_iterations: 100,
            verbose: false,
            ..Default::default()
        };
        let solver_huge = PowellDogLegSolver::new(config_huge);
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result =
            solver_huge.solve_problem(&problem, &mut workspace).unwrap();

        // Should converge normally.
        assert!(result.status.is_success());
        assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
        assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);

        println!("\nPowell Dog-Leg trust region radius edge case test:");
        println!(
            "  Large trust region radius result: {:.6e} cost in {} iterations",
            result.cost, result.iterations
        );
    }

    #[test]
    fn test_powell_dogleg_bukin_n6() {
        let problem = BukinN6Problem;

        // Use tighter tolerances for this difficult problem
        let config = PowellDogLegConfig {
            function_tolerance: 1e-12,
            parameter_tolerance: 1e-12,
            gradient_tolerance: 1e-12,
            max_iterations: 500,
            verbose: false,
            ..Default::default()
        };
        let solver = PowellDogLegSolver::new(config);

        // Start from a point in the valid domain but away from minimum
        let initial_parameters = vec![-5.0, 0.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nPowell Dog-Leg Bukin N6 function:");
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
    fn test_powell_dogleg_workspace_reuse_dimension_mismatch() {
        let problem2d = RosenbrockProblem::new(); // 2 parameters, 2 residuals

        // Create workspace for 2D problem
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem2d, &initial_parameters)
                .unwrap();

        // Try to reuse with incompatible problem dimensions.
        let problem3d = Mock3DProblem;
        let parameters3d = vec![0.0, 0.0, 0.0];

        // This should fail with dimension mismatch
        let result = workspace.reuse_with(&problem3d, &parameters3d);
        assert!(result.is_err());

        // Test parameter count mismatch
        let wrong_params = vec![0.0, 0.0, 0.0]; // 3 params for 2D problem
        let result = workspace.reuse_with(&problem2d, &wrong_params);
        assert!(result.is_err());
    }

    #[test]
    fn test_powell_dogleg_configurable_absolute_cost_tolerance() {
        let problem = RosenbrockProblem::new();

        // Test with very strict absolute cost tolerance
        let config_strict = PowellDogLegConfig {
            function_tolerance: 1e-6,
            absolute_cost_tolerance: 1e-12, // Very strict
            max_iterations: 500,
            ..Default::default()
        };
        let solver_strict = PowellDogLegSolver::new(config_strict);

        let initial_parameters = vec![0.1, 0.1]; // Close to optimum
        let mut workspace_strict =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_strict = solver_strict
            .solve_problem(&problem, &mut workspace_strict)
            .unwrap();

        // Test with relaxed absolute cost tolerance
        let config_relaxed = PowellDogLegConfig {
            function_tolerance: 1e-6,
            absolute_cost_tolerance: 1e-3, // Very relaxed
            max_iterations: 500,
            ..Default::default()
        };
        let solver_relaxed = PowellDogLegSolver::new(config_relaxed);

        let mut workspace_relaxed =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();
        let result_relaxed = solver_relaxed
            .solve_problem(&problem, &mut workspace_relaxed)
            .unwrap();

        println!("\nPowell Dog-Leg configurable absolute cost tolerance test:");
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
    fn test_powell_dogleg_workspace_reuse_performance() {
        let problem = RosenbrockProblem::new();

        // Create workspace once
        let initial_parameters = vec![0.0, 0.0];
        let mut workspace =
            PowellDogLegWorkspace::new(&problem, &initial_parameters).unwrap();

        // Test multiple reuses with different starting points
        let starting_points = vec![
            vec![0.5, 0.5],
            vec![-1.2, 1.0],
            vec![2.0, -1.0],
            vec![-0.5, 2.5],
        ];

        let solver = PowellDogLegSolver::with_defaults();

        for (i, start_point) in starting_points.iter().enumerate() {
            // Reuse workspace
            workspace.reuse_with(&problem, start_point).unwrap();

            // Solve
            let result =
                solver.solve_problem(&problem, &mut workspace).unwrap();

            println!(
                "\nPowell Dog-Leg reuse test {} from [{:.1}, {:.1}]:",
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

            // All should converge to (1, 1)
            assert!(result.status.is_success());
            assert_relative_eq!(result.parameters[0], 1.0, epsilon = 1e-5);
            assert_relative_eq!(result.parameters[1], 1.0, epsilon = 1e-5);
            assert!(result.cost < 1e-9);
        }
    }
}
