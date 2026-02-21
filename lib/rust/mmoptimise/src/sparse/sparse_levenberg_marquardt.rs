//
// Copyright (C) 2025, 2026 David Cattermole.
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

//! Sparse Levenberg-Marquardt solver implementation.
//!
//! This module provides a sparse matrix variant of the Levenberg-Marquardt
//! algorithm for large-scale non-linear least squares problems. It uses
//! CHOLMOD for efficient sparse linear algebra operations.

use anyhow::Result;
use mmcholmod::solver::CholmodSolver;
use mmcholmod::sparse_matrix::{
    SparseMatrixCOO, SparseMatrixCSC, SymmetryType,
};
use nalgebra::DVector;

use std::time::Instant;

use crate::solver::common::*;
use crate::solver::reporting::{
    print_final_summary, print_iteration, print_iteration_header,
    print_problem_summary, print_timing_breakdown, IterationMetrics,
    ProblemSummary, SolverTimings,
};
use crate::sparse::SparseOptimisationProblem;

const ENABLE_REPORTING: bool = false;
const DEBUG: bool = false;

/// Configuration parameters for the Sparse Levenberg-Marquardt solver.
///
/// Controls all aspects of solver behavior, from convergence
/// tolerances to trust region management.
#[derive(Debug, Clone, Copy)]
pub struct SparseLevenbergMarquardtConfig {
    /// Function tolerance
    ///
    /// Convergence when relative reduction in cost is below this.
    pub function_tolerance: f64,

    /// Parameter tolerance.
    ///
    /// Convergence when relative change in parameters is below this.
    pub parameter_tolerance: f64,

    /// Gradient tolerance.
    ///
    /// Convergence when gradient norm is below this.
    pub gradient_tolerance: f64,

    /// Absolute cost tolerance threshold.
    pub absolute_cost_tolerance: f64,

    /// Maximum number of iterations.
    pub max_iterations: usize,

    /// Maximum number of function evaluations.
    pub max_function_evaluations: usize,

    /// Initial trust region factor.
    pub initial_trust_factor: f64,

    /// Parameter scaling mode.
    pub scaling_mode: ParameterScalingMode,

    /// Minimum step quality for acceptance.
    pub min_step_quality: f64,

    /// Factor for adjusting machine epsilon in numerical comparisons.
    pub epsilon_factor: f64,

    /// Regularization factor for numerical stability.
    pub lambda_regularization: f64,

    /// Minimum allowed trust region radius.
    pub min_trust_radius: f64,

    /// Maximum allowed trust region radius.
    pub max_trust_radius: f64,

    /// Reporting mode - controls diagnostic output level.
    pub reporting_mode: ReportingMode,
}

impl Default for SparseLevenbergMarquardtConfig {
    fn default() -> Self {
        Self {
            function_tolerance: 1e-6,
            parameter_tolerance: 1e-6,
            gradient_tolerance: 1e-6,
            absolute_cost_tolerance: 1e-6,
            max_iterations: 500,
            max_function_evaluations: 50000,
            initial_trust_factor: 100.0,
            scaling_mode: ParameterScalingMode::Auto,
            min_step_quality: 1e-4,
            epsilon_factor: 1.0,
            lambda_regularization: 1e-10,
            min_trust_radius: 1e-15,
            max_trust_radius: 1e10,
            reporting_mode: ReportingMode::Full,
        }
    }
}

/// Workspace for Sparse Levenberg-Marquardt solver.
///
/// Contains pre-allocated storage for sparse matrices and vectors
/// used during optimization, avoiding repeated allocations.
pub struct SparseLevenbergMarquardtWorkspace {
    // Problem dimensions.
    n: usize, // number of parameters.
    m: usize, // number of residuals.

    // Parameter and residual vectors (dense)
    pub parameters: DVector<f64>,
    pub trial_parameters: DVector<f64>,
    pub best_parameters: DVector<f64>,
    residuals: DVector<f64>,
    trial_residuals: DVector<f64>,
    best_residuals: DVector<f64>,

    // Sparse Jacobian storage (CSC format)
    jacobian_csc: Option<SparseMatrixCSC>,

    // Levenberg-Marquardt workspace.
    gradient: DVector<f64>, // J^T * residuals
    step: DVector<f64>,     // Step to take
    scaling: DVector<f64>,  // Parameter scaling

    // CHOLMOD solver for (JtJ + λI) factorization
    cholmod_solver: CholmodSolver,
    cholmod_initialized: bool,

    // Trust region management.
    lambda: f64, // Damping parameter

    // Reusable buffers to eliminate per-iteration allocations
    jac_coo_buffer: SparseMatrixCOO,
    jtj_coo_buffer: SparseMatrixCOO,
    j_step_buffer: DVector<f64>,
    neg_gradient_buffer: Vec<f64>,
}

impl SparseLevenbergMarquardtWorkspace {
    /// Create a new workspace for the sparse Levenberg-Marquardt solver.
    pub fn new<P: SparseOptimisationProblem>(
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
            jacobian_csc: None,
            gradient: DVector::zeros(n),
            step: DVector::zeros(n),
            scaling: DVector::from_element(n, 1.0),
            cholmod_solver: CholmodSolver::new()?,
            cholmod_initialized: false,
            lambda: 0.0,
            jac_coo_buffer: SparseMatrixCOO::new(
                m,
                n,
                SymmetryType::Unsymmetric,
            )?,
            jtj_coo_buffer: SparseMatrixCOO::new(
                n,
                n,
                SymmetryType::UpperTriangular,
            )?,
            j_step_buffer: DVector::zeros(m),
            neg_gradient_buffer: vec![0.0; n],
        })
    }

    /// Reuse workspace with new initial parameters.
    pub fn reuse_with<P: SparseOptimisationProblem>(
        &mut self,
        problem: &P,
        initial_parameters: &[f64],
    ) -> Result<()> {
        let n = problem.parameter_count();
        let m = problem.residual_count();

        if n != self.n || m != self.m {
            return Err(OptimisationError::InvalidInput(format!(
                "Dimension mismatch: workspace has {}x{}, problem has {}x{}",
                self.n, self.m, n, m
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

        self.parameters.copy_from_slice(initial_parameters);
        self.trial_parameters.copy_from_slice(initial_parameters);
        self.best_parameters.copy_from_slice(initial_parameters);
        self.residuals.fill(0.0);
        self.trial_residuals.fill(0.0);
        self.best_residuals.fill(0.0);
        self.gradient.fill(0.0);
        self.step.fill(0.0);
        self.scaling.fill(1.0);
        self.lambda = 0.0;

        // Reset CHOLMOD solver
        self.cholmod_solver.reset();
        self.cholmod_initialized = false;

        // Reset reusable buffers
        crate::sparse::common::clear_sparse_coo(&mut self.jac_coo_buffer);
        crate::sparse::common::clear_sparse_coo(&mut self.jtj_coo_buffer);
        self.j_step_buffer.fill(0.0);
        self.neg_gradient_buffer.fill(0.0);

        Ok(())
    }
}

/// Sparse Levenberg-Marquardt solver with trust region management.
///
/// This is a sparse implementation of the Levenberg-Marquardt
/// algorithm for non-linear least squares optimization. It uses
/// automatic differentiation for gradient computation, CHOLMOD
/// for sparse linear system solving, and adaptive trust region
/// management.
pub struct SparseLevenbergMarquardtSolver {
    config: SparseLevenbergMarquardtConfig,
}

impl SparseLevenbergMarquardtSolver {
    /// Create a new solver with given configuration.
    pub fn new(config: SparseLevenbergMarquardtConfig) -> Self {
        Self { config }
    }

    /// Create a new solver with default configuration.
    pub fn with_defaults() -> Self {
        Self {
            config: SparseLevenbergMarquardtConfig::default(),
        }
    }

    /// Set manual parameter scaling.
    pub fn set_scaling(
        &self,
        workspace: &mut SparseLevenbergMarquardtWorkspace,
        scaling: &[f64],
    ) -> Result<()> {
        if scaling.len() != workspace.n {
            return Err(OptimisationError::InvalidInput(format!(
                "Expected {} scaling values, got {}",
                workspace.n,
                scaling.len()
            ))
            .into());
        }

        for (i, &s) in scaling.iter().enumerate() {
            if s <= 0.0 || !s.is_finite() {
                return Err(OptimisationError::InvalidInput(format!(
                    "Invalid scaling value at index {}: {}",
                    i, s
                ))
                .into());
            }
        }

        workspace.scaling.copy_from_slice(scaling);
        Ok(())
    }

    /// Update parameter scaling based on Jacobian diagonal.
    fn update_scaling(
        &self,
        workspace: &mut SparseLevenbergMarquardtWorkspace,
    ) {
        if self.config.scaling_mode == ParameterScalingMode::None {
            return;
        }

        if let Some(ref jacobian) = workspace.jacobian_csc {
            // Compute diagonal of J^T * J for scaling
            for col in 0..jacobian.ncol {
                let start = jacobian.col_pointers[col] as usize;
                let end = jacobian.col_pointers[col + 1] as usize;

                let mut col_norm_sq = 0.0;
                for idx in start..end {
                    let value = jacobian.values[idx];
                    col_norm_sq += value * value;
                }

                if col_norm_sq > 0.0 {
                    workspace.scaling[col] = col_norm_sq.sqrt().max(1.0);
                } else {
                    workspace.scaling[col] = 1.0;
                }
            }
        }
    }

    /// Solve the trust region subproblem using CHOLMOD.
    fn solve_trust_region(
        &self,
        workspace: &mut SparseLevenbergMarquardtWorkspace,
        delta: f64,
    ) -> Result<f64> {
        if DEBUG {
            eprintln!("[Sparse LM] === Solve Trust Region ===");
        }

        let n = workspace.n;
        let machine_epsilon = f64::EPSILON * self.config.epsilon_factor;

        let jacobian = workspace.jacobian_csc.as_ref().ok_or_else(|| {
            OptimisationError::SolverError("Jacobian not available".to_string())
        })?;

        // Estimate lambda if it's zero (first iteration)
        if workspace.lambda == 0.0 {
            // Initial lambda estimate
            let gradient_norm = workspace.gradient.norm();
            if delta > machine_epsilon && gradient_norm > machine_epsilon {
                workspace.lambda = gradient_norm / delta;
            } else {
                workspace.lambda = 1.0;
            }
            workspace.lambda = workspace.lambda.max(machine_epsilon);
        }

        // Iteratively refine lambda to satisfy trust region constraint
        let max_lambda_iterations = 10;
        let mut predicted_reduction = 0.0;

        for iter in 0..max_lambda_iterations {
            // Build (J^T * J + lambda * D^2) in sparse format using reusable buffer
            crate::sparse::common::assemble_jtj_with_damping(
                jacobian,
                &mut workspace.jtj_coo_buffer,
                workspace.scaling.as_slice(),
                workspace.lambda,
                self.config.lambda_regularization,
                machine_epsilon,
            )?;

            let jtj_lambda_csc = workspace.jtj_coo_buffer.to_csc()?;

            // Initialize or re-analyze CHOLMOD solver if needed
            if !workspace.cholmod_initialized {
                workspace.cholmod_solver.analyze(&jtj_lambda_csc, false)?;
                workspace.cholmod_initialized = true;
            }

            // Factorize the system
            match workspace.cholmod_solver.factorize(&jtj_lambda_csc, false) {
                Ok(_) => {
                    // Solve (J^T * J + lambda * D^2) * step = -J^T * residuals
                    // Reuse neg_gradient_buffer
                    for i in 0..n {
                        workspace.neg_gradient_buffer[i] =
                            -workspace.gradient[i];
                    }
                    let solution = workspace
                        .cholmod_solver
                        .solve(&workspace.neg_gradient_buffer, false)?;

                    for i in 0..n {
                        workspace.step[i] = solution[i];
                    }

                    // Check if step satisfies trust region
                    let scaled_step_norm = (0..n)
                        .map(|i| {
                            let s = workspace.step[i] * workspace.scaling[i];
                            s * s
                        })
                        .sum::<f64>()
                        .sqrt();

                    if DEBUG {
                        eprintln!(
                            "[Sparse LM]   Lambda iteration {}: λ={:.3e}, ||D*step||={:.3e}, delta={:.3e}",
                            iter, workspace.lambda, scaled_step_norm, delta
                        );
                    }

                    // Compute predicted reduction for quality ratio calculation.
                    // pred_red = 0.5 * ||f||^2 - 0.5 * ||f + J*step||^2
                    // ≈ -step^T * J^T * f - 0.5 * step^T * J^T * J * step
                    // = -step^T * gradient - 0.5 * ||J*step||^2

                    // Compute J * step using reusable buffer
                    crate::sparse::common::sparse_j_multiply(
                        jacobian,
                        &workspace.step,
                        &mut workspace.j_step_buffer,
                    );

                    let linear_term = workspace.step.dot(&workspace.gradient);
                    let quadratic_term: f64 =
                        0.5 * workspace.j_step_buffer.norm_squared();
                    predicted_reduction = -linear_term - quadratic_term;

                    // Adjust lambda based on trust region constraint.
                    if scaled_step_norm <= delta * 1.1 {
                        // Step is within trust region (with small tolerance).
                        break;
                    } else {
                        // Step is too large, increase lambda.
                        workspace.lambda *= 2.0;
                        workspace.lambda = workspace.lambda.min(1e10);
                    }
                }
                Err(_) => {
                    // Matrix not positive definite, increase lambda.
                    if DEBUG {
                        eprintln!(
                            "[Sparse LM]   Matrix not positive definite at λ={:.3e}, increasing",
                            workspace.lambda
                        );
                    }
                    workspace.lambda *= 10.0;
                    workspace.lambda = workspace.lambda.min(1e10);
                }
            }
        }

        Ok(predicted_reduction)
    }

    /// Main solver routine.
    pub fn solve_problem<P: SparseOptimisationProblem>(
        &self,
        problem: &P,
        workspace: &mut SparseLevenbergMarquardtWorkspace,
    ) -> Result<OptimisationResult> {
        let n = workspace.n;
        let _m = workspace.m;
        let machine_epsilon = f64::EPSILON * self.config.epsilon_factor;

        let mut nfev = 0;
        let mut njev = 0;
        let mut delta = self.config.initial_trust_factor;
        let mut best_cost = f64::INFINITY;
        let mut previous_cost;

        // Initialize timing infrastructure.
        let mut timings = if ENABLE_REPORTING
            && self.config.reporting_mode != ReportingMode::Silent
        {
            Some(SolverTimings::new())
        } else {
            None
        };

        // Initial evaluation.
        let residual_start = if ENABLE_REPORTING
            && self.config.reporting_mode != ReportingMode::Silent
        {
            Some(Instant::now())
        } else {
            None
        };
        let (row_indices, col_indices, values) = problem
            .compute_sparse_jacobian(
                workspace.parameters.as_slice(),
                workspace.residuals.as_mut_slice(),
            )?;
        nfev += 1;
        njev += 1;

        if ENABLE_REPORTING
            && self.config.reporting_mode != ReportingMode::Silent
        {
            if let (Some(ref mut t), Some(start)) =
                (&mut timings, residual_start)
            {
                t.record_jacobian_time(start);
            }
        }

        let mut current_cost =
            crate::sparse::common::compute_least_squares_cost(
                &workspace.residuals,
            );

        let initial_cost_for_summary = current_cost;
        if !current_cost.is_finite() {
            // Provide detailed diagnostic information about
            // non-finite residuals.
            let non_finite_residuals: Vec<(usize, f64)> = workspace
                .residuals
                .iter()
                .enumerate()
                .filter(|(_, &r)| !r.is_finite())
                .map(|(i, &r)| (i, r))
                .take(10) // Limit to first 10 for readability.
                .collect();

            let non_finite_count = workspace
                .residuals
                .iter()
                .filter(|&&r| !r.is_finite())
                .count();

            return Err(OptimisationError::SolverError(format!(
                "Initial cost is not finite (cost={:.3e}). Found {} non-finite residuals. Values: {:?}",
                current_cost, non_finite_count, non_finite_residuals
            ))
            .into());
        }
        if current_cost < best_cost {
            best_cost = current_cost;
            workspace.best_parameters.copy_from(&workspace.parameters);
            workspace.best_residuals.copy_from(&workspace.residuals);
        }

        // Build sparse Jacobian using reusable buffer.
        crate::sparse::common::clear_sparse_coo(&mut workspace.jac_coo_buffer);
        for i in 0..values.len() {
            workspace.jac_coo_buffer.push(
                row_indices[i],
                col_indices[i],
                values[i],
            )?;
        }
        workspace.jacobian_csc = Some(workspace.jac_coo_buffer.to_csc()?);

        // Print problem summary and iteration header.
        if ENABLE_REPORTING {
            match self.config.reporting_mode {
                ReportingMode::Silent => {}
                ReportingMode::Iterations => {
                    print_iteration_header();
                }
                ReportingMode::Summary | ReportingMode::Full => {
                    print_problem_summary(&ProblemSummary {
                        parameter_blocks: 1,
                        parameters: n,
                        residuals: workspace.m,
                        solver_type:
                            "SPARSE_TRUST_REGION (Levenberg-Marquardt)",
                        linear_solver: "CHOLMOD_CHOLESKY",
                        threads: 1,
                    });
                    print_iteration_header();
                }
            }
        }

        // Main iteration loop.
        for iteration in 0..self.config.max_iterations {
            // Start timing this iteration.
            if ENABLE_REPORTING
                && self.config.reporting_mode != ReportingMode::Silent
            {
                if let Some(ref mut t) = timings {
                    t.start_iteration();
                }
            }

            // Track cost from previous iteration for cost_change calculation.
            previous_cost = current_cost;

            // Check for absolute cost convergence.
            if current_cost < machine_epsilon {
                if ENABLE_REPORTING
                    && self.config.reporting_mode != ReportingMode::Silent
                {
                    if let Some(ref mut t) = timings {
                        t.finish_iteration();
                    }
                }
                if ENABLE_REPORTING {
                    if let Some(ref timings) = timings {
                        match self.config.reporting_mode {
                            ReportingMode::Silent
                            | ReportingMode::Iterations => {}
                            ReportingMode::Summary => {
                                print_final_summary(
                                    initial_cost_for_summary,
                                    current_cost,
                                    iteration,
                                    "Converged: cost near zero",
                                );
                            }
                            ReportingMode::Full => {
                                print_timing_breakdown(timings);
                                print_final_summary(
                                    initial_cost_for_summary,
                                    current_cost,
                                    iteration,
                                    "Converged: cost near zero",
                                );
                            }
                        }
                    }
                }
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
                    if ENABLE_REPORTING
                        && self.config.reporting_mode != ReportingMode::Silent
                    {
                        if let Some(ref mut t) = timings {
                            t.finish_iteration();
                        }
                    }
                    if ENABLE_REPORTING {
                        if let Some(ref mut t) = timings {
                            match self.config.reporting_mode {
                                ReportingMode::Silent
                                | ReportingMode::Iterations => {}
                                ReportingMode::Summary => {
                                    print_final_summary(
                                        initial_cost_for_summary,
                                        current_cost,
                                        iteration,
                                        "Converged: relative cost improvement below tolerance",
                                    );
                                }
                                ReportingMode::Full => {
                                    print_timing_breakdown(t);
                                    print_final_summary(
                                        initial_cost_for_summary,
                                        current_cost,
                                        iteration,
                                        "Converged: relative cost improvement below tolerance",
                                    );
                                }
                            }
                        }
                    }
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

            // Compute gradient: J^T * residuals
            if let Some(ref jacobian) = workspace.jacobian_csc {
                crate::sparse::common::sparse_jt_multiply(
                    jacobian,
                    &workspace.residuals,
                    &mut workspace.gradient,
                );
            }

            // Update scaling on first iteration or if requested.
            if iteration == 0
                || self.config.scaling_mode == ParameterScalingMode::Auto
            {
                self.update_scaling(workspace);
            }

            // Initialize trust region on first iteration.
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
                    delta = self.config.initial_trust_factor;
                }
                if DEBUG {
                    eprintln!(
                        "[Sparse LM] Initial trust region: delta={:.3e}",
                        delta
                    );
                }
            }

            // Check gradient convergence.
            let gradient_norm =
                workspace.gradient.norm() / current_cost.max(1.0);
            if gradient_norm < self.config.gradient_tolerance {
                if ENABLE_REPORTING
                    && self.config.reporting_mode != ReportingMode::Silent
                {
                    if let Some(ref mut t) = timings {
                        t.finish_iteration();
                    }
                }
                if ENABLE_REPORTING {
                    if let Some(ref mut t) = timings {
                        match self.config.reporting_mode {
                            ReportingMode::Silent
                            | ReportingMode::Iterations => {}
                            ReportingMode::Summary => {
                                print_final_summary(
                                    initial_cost_for_summary,
                                    current_cost,
                                    iteration,
                                    "Converged: gradient norm below tolerance",
                                );
                            }
                            ReportingMode::Full => {
                                print_timing_breakdown(t);
                                print_final_summary(
                                    initial_cost_for_summary,
                                    current_cost,
                                    iteration,
                                    "Converged: gradient norm below tolerance",
                                );
                            }
                        }
                    }
                }
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

            // Check if we've exceeded function evaluation limit.
            if nfev >= self.config.max_function_evaluations {
                if ENABLE_REPORTING
                    && self.config.reporting_mode != ReportingMode::Silent
                {
                    if let Some(ref mut t) = timings {
                        t.finish_iteration();
                    }
                }
                if ENABLE_REPORTING {
                    if let Some(ref mut t) = timings {
                        match self.config.reporting_mode {
                            ReportingMode::Silent
                            | ReportingMode::Iterations => {}
                            ReportingMode::Summary => {
                                print_final_summary(
                                    initial_cost_for_summary,
                                    best_cost,
                                    iteration,
                                    "Maximum function evaluations reached",
                                );
                            }
                            ReportingMode::Full => {
                                print_timing_breakdown(t);
                                print_final_summary(
                                    initial_cost_for_summary,
                                    best_cost,
                                    iteration,
                                    "Maximum function evaluations reached",
                                );
                            }
                        }
                    }
                }
                return Ok(OptimisationResult {
                    status: SolverStatus::MaxIterationsReached,
                    parameters: workspace.best_parameters.as_slice().to_vec(),
                    residuals: workspace.best_residuals.as_slice().to_vec(),
                    cost: best_cost,
                    iterations: iteration,
                    function_evaluations: nfev,
                    jacobian_evaluations: njev,
                    message: "Maximum function evaluations reached",
                });
            }

            // Inner loop: solve trust region sub-problem.
            let mut step_accepted = false;
            let mut inner_iterations = 0;
            const MAX_INNER_ITERATIONS: usize = 20;

            if DEBUG {
                eprintln!(
                    "[Sparse LM] Entering trust region loop (max {} attempts)",
                    MAX_INNER_ITERATIONS
                );
            }

            // TODO: Can we avoid re-calculations of specific
            // components of this loop similar to the
            // `sparse_lm_bundle_adjustment` solver?
            while inner_iterations < MAX_INNER_ITERATIONS && !step_accepted {
                inner_iterations += 1;

                if DEBUG {
                    eprintln!(
                        "[Sparse LM]   Trust region attempt {}/{}: λ={:.3e}, delta={:.3e}",
                        inner_iterations, MAX_INNER_ITERATIONS, workspace.lambda, delta
                    );
                }

                // Check if trust region is too small
                if delta < self.config.min_trust_radius {
                    if ENABLE_REPORTING
                        && self.config.reporting_mode != ReportingMode::Silent
                    {
                        if let Some(ref mut t) = timings {
                            t.finish_iteration();
                        }
                    }
                    if ENABLE_REPORTING {
                        if let Some(ref mut t) = timings {
                            match self.config.reporting_mode {
                                ReportingMode::Silent
                                | ReportingMode::Iterations => {}
                                ReportingMode::Summary => {
                                    print_final_summary(
                                        initial_cost_for_summary,
                                        best_cost,
                                        iteration,
                                        "Trust region became too small",
                                    );
                                }
                                ReportingMode::Full => {
                                    print_timing_breakdown(t);
                                    print_final_summary(
                                        initial_cost_for_summary,
                                        best_cost,
                                        iteration,
                                        "Trust region became too small",
                                    );
                                }
                            }
                        }
                    }
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

                // Solve trust region subproblem
                let linear_solver_start = if ENABLE_REPORTING
                    && self.config.reporting_mode != ReportingMode::Silent
                {
                    Some(Instant::now())
                } else {
                    None
                };

                let predicted_reduction =
                    self.solve_trust_region(workspace, delta)?;

                if ENABLE_REPORTING
                    && self.config.reporting_mode != ReportingMode::Silent
                {
                    if let (Some(ref mut t), Some(start)) =
                        (&mut timings, linear_solver_start)
                    {
                        t.record_linear_solver_time(start);
                    }
                }

                // Calculate scaled step norm
                let scaled_step_norm = (0..n)
                    .map(|i| {
                        let s = workspace.step[i] * workspace.scaling[i];
                        s * s
                    })
                    .sum::<f64>()
                    .sqrt();

                if iteration == 0 {
                    delta = delta.min(scaled_step_norm);
                }

                // Compute trial point.
                workspace.trial_parameters.copy_from(&workspace.parameters);
                workspace.trial_parameters += &workspace.step;

                // Evaluate at trial point (compute residuals only, ignore Jacobian)
                let residual_start = if ENABLE_REPORTING
                    && self.config.reporting_mode != ReportingMode::Silent
                {
                    Some(Instant::now())
                } else {
                    None
                };

                let _ = problem.compute_sparse_jacobian(
                    workspace.trial_parameters.as_slice(),
                    workspace.trial_residuals.as_mut_slice(),
                )?;
                nfev += 1;

                if ENABLE_REPORTING
                    && self.config.reporting_mode != ReportingMode::Silent
                {
                    if let (Some(ref mut t), Some(start)) =
                        (&mut timings, residual_start)
                    {
                        t.record_residual_time(start);
                    }
                }

                let trial_cost =
                    crate::sparse::common::compute_least_squares_cost(
                        &workspace.trial_residuals,
                    );
                let actual_reduction = current_cost - trial_cost;

                let ratio = if predicted_reduction.abs() > machine_epsilon {
                    actual_reduction / predicted_reduction
                } else if predicted_reduction == 0.0 && actual_reduction == 0.0
                {
                    1.0
                } else {
                    0.0
                };

                if DEBUG {
                    eprintln!("[Sparse LM]   Step quality analysis:");
                    eprintln!(
                        "[Sparse LM]     predicted_reduction = {:.3e}",
                        predicted_reduction
                    );
                    eprintln!(
                        "[Sparse LM]     actual_reduction    = {:.3e}",
                        actual_reduction
                    );
                    eprintln!(
                        "[Sparse LM]     ρ (quality ratio)   = {:.3e}",
                        ratio
                    );
                }

                // Accept or reject step based on quality ratio
                if ratio > self.config.min_step_quality
                    && trial_cost.is_finite()
                {
                    // Accept the step
                    step_accepted = true;
                    workspace.parameters.copy_from(&workspace.trial_parameters);
                    workspace.residuals.copy_from(&workspace.trial_residuals);
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

                    // Re-evaluate Jacobian for next iteration.
                    let jacobian_start = if ENABLE_REPORTING
                        && self.config.reporting_mode != ReportingMode::Silent
                    {
                        Some(Instant::now())
                    } else {
                        None
                    };

                    let (row_indices, col_indices, values) = problem
                        .compute_sparse_jacobian(
                            workspace.parameters.as_slice(),
                            workspace.residuals.as_mut_slice(),
                        )?;
                    nfev += 1;
                    njev += 1;

                    if ENABLE_REPORTING
                        && self.config.reporting_mode != ReportingMode::Silent
                    {
                        if let (Some(ref mut t), Some(start)) =
                            (&mut timings, jacobian_start)
                        {
                            t.record_jacobian_time(start);
                        }
                    }

                    // Build new sparse Jacobian using reusable buffer.
                    crate::sparse::common::clear_sparse_coo(
                        &mut workspace.jac_coo_buffer,
                    );
                    for i in 0..values.len() {
                        workspace.jac_coo_buffer.push(
                            row_indices[i],
                            col_indices[i],
                            values[i],
                        )?;
                    }
                    workspace.jacobian_csc =
                        Some(workspace.jac_coo_buffer.to_csc()?);

                    // Adjust trust region based on quality.
                    if ratio > 0.75 {
                        // Very good step, increase trust region.
                        delta = (2.0 * delta).min(self.config.max_trust_radius);
                        workspace.lambda *= 0.5;
                    } else if ratio > 0.25 {
                        // Good step, keep trust region.
                        // lambda stays the same.
                    } else {
                        // Marginal step, decrease trust region slightly.
                        delta *= 0.75;
                        workspace.lambda *= 1.5;
                    }

                    // Print iteration output.
                    if ENABLE_REPORTING
                        && self.config.reporting_mode != ReportingMode::Silent
                    {
                        if let Some(ref mut t) = timings {
                            t.finish_iteration();
                            let step_norm = workspace.step.norm();
                            let cost_change = previous_cost - current_cost;
                            print_iteration(
                                &IterationMetrics {
                                    iteration,
                                    cost: current_cost,
                                    cost_change,
                                    gradient_norm,
                                    step_norm,
                                    tr_ratio: ratio,
                                    tr_radius: delta,
                                    ls_iter: 0,
                                    iter_time_seconds: t.iteration_elapsed(),
                                    total_time_seconds: t.total_time_seconds,
                                },
                                true,
                            );
                        }
                    }

                    // Check parameter convergence.
                    let param_change_norm = workspace.step.norm();
                    let param_norm = workspace.parameters.norm();
                    let relative_param_change =
                        param_change_norm / param_norm.max(1.0);

                    if relative_param_change < self.config.parameter_tolerance {
                        if ENABLE_REPORTING {
                            if let Some(ref t) = timings {
                                match self.config.reporting_mode {
                                    ReportingMode::Silent
                                    | ReportingMode::Iterations => {}
                                    ReportingMode::Summary => {
                                        print_final_summary(
                                            initial_cost_for_summary,
                                            current_cost,
                                            iteration + 1,
                                            "Converged: parameter change below tolerance",
                                        );
                                    }
                                    ReportingMode::Full => {
                                        print_timing_breakdown(t);
                                        print_final_summary(
                                            initial_cost_for_summary,
                                            current_cost,
                                            iteration + 1,
                                            "Converged: parameter change below tolerance",
                                        );
                                    }
                                }
                            }
                        }
                        return Ok(OptimisationResult {
                            status: SolverStatus::SmallStepSize,
                            parameters: workspace
                                .parameters
                                .as_slice()
                                .to_vec(),
                            residuals: workspace.residuals.as_slice().to_vec(),
                            cost: current_cost,
                            iterations: iteration + 1,
                            function_evaluations: nfev,
                            jacobian_evaluations: njev,
                            message:
                                "Converged: parameter change below tolerance",
                        });
                    }
                } else {
                    // Reject the step, decrease trust region.
                    delta *= 0.25;
                    workspace.lambda *= 4.0;

                    if DEBUG {
                        eprintln!(
                            "[Sparse LM]   Step REJECTED: ratio = {:.3e}, reducing delta to {:.3e}",
                            ratio, delta
                        );
                    }
                }
            }

            if !step_accepted {
                if ENABLE_REPORTING
                    && self.config.reporting_mode != ReportingMode::Silent
                {
                    if let Some(ref mut t) = timings {
                        t.finish_iteration();
                    }
                }
                if ENABLE_REPORTING {
                    if let Some(ref mut t) = timings {
                        match self.config.reporting_mode {
                            ReportingMode::Silent
                            | ReportingMode::Iterations => {}
                            ReportingMode::Summary => {
                                print_final_summary(
                                    initial_cost_for_summary,
                                    best_cost,
                                    iteration,
                                    "Failed to find acceptable step",
                                );
                            }
                            ReportingMode::Full => {
                                print_timing_breakdown(t);
                                print_final_summary(
                                    initial_cost_for_summary,
                                    best_cost,
                                    iteration,
                                    "Failed to find acceptable step",
                                );
                            }
                        }
                    }
                }
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
        }

        // Max iterations reached
        if ENABLE_REPORTING {
            if let Some(ref t) = timings {
                match self.config.reporting_mode {
                    ReportingMode::Silent | ReportingMode::Iterations => {}
                    ReportingMode::Summary => {
                        print_final_summary(
                            initial_cost_for_summary,
                            best_cost,
                            self.config.max_iterations,
                            "Maximum iterations reached",
                        );
                    }
                    ReportingMode::Full => {
                        print_timing_breakdown(t);
                        print_final_summary(
                            initial_cost_for_summary,
                            best_cost,
                            self.config.max_iterations,
                            "Maximum iterations reached",
                        );
                    }
                }
            }
        }

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
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Simple sparse test problem: identity problem similar to sparse Powell DogLeg tests
    /// residual[i] = parameter[i] - (i + 1)
    /// This has a simple zero-residual solution at parameter[i] = i + 1
    struct SparseProblem {
        n: usize,
    }

    impl SparseProblem {
        fn new(n: usize) -> Self {
            Self { n }
        }
    }

    impl SparseOptimisationProblem for SparseProblem {
        fn parameter_count(&self) -> usize {
            self.n
        }

        fn residual_count(&self) -> usize {
            self.n
        }

        fn compute_sparse_jacobian(
            &self,
            parameters: &[f64],
            residuals: &mut [f64],
        ) -> Result<(Vec<usize>, Vec<usize>, Vec<f64>)> {
            let mut row_indices = Vec::new();
            let mut col_indices = Vec::new();
            let mut values = Vec::new();

            // Simple identity-like problem
            for i in 0..self.n {
                // residual[i] = parameter[i] - (i + 1)
                residuals[i] = parameters[i] - (i + 1) as f64;

                // Jacobian: dr_i/dp_i = 1 (diagonal)
                row_indices.push(i);
                col_indices.push(i);
                values.push(1.0);
            }

            Ok((row_indices, col_indices, values))
        }
    }

    #[test]
    fn test_solver_creation() {
        let solver = SparseLevenbergMarquardtSolver::with_defaults();
        assert_eq!(solver.config.max_iterations, 500);
    }

    #[test]
    fn test_simple_sparse_problem() {
        let problem = SparseProblem::new(3);
        let initial_parameters = vec![0.0, 0.0, 0.0];

        let config = SparseLevenbergMarquardtConfig {
            ..Default::default()
        };
        let solver = SparseLevenbergMarquardtSolver::new(config);

        let mut workspace = SparseLevenbergMarquardtWorkspace::new(
            &problem,
            &initial_parameters,
        )
        .unwrap();

        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        println!("\nSparse problem result:");
        println!("  Final parameters: {:?}", result.parameters);
        println!("  Final cost: {:.6e}", result.cost);
        println!("  Iterations: {}", result.iterations);
        println!("  Status: {:?}", result.status);

        assert!(result.status.is_success());
        assert!(result.cost < 1e-8);
    }

    #[test]
    fn test_workspace_reuse() {
        let problem = SparseProblem::new(4);
        let initial_parameters1 = vec![1.0, 2.0, 3.0, 4.0];
        let initial_parameters2 = vec![0.5, 1.5, 2.5, 3.5];

        let mut workspace = SparseLevenbergMarquardtWorkspace::new(
            &problem,
            &initial_parameters1,
        )
        .unwrap();

        // Reuse workspace with new parameters
        workspace
            .reuse_with(&problem, &initial_parameters2)
            .unwrap();

        assert_eq!(workspace.parameters[0], 0.5);
        assert_eq!(workspace.parameters[1], 1.5);
        assert_eq!(workspace.parameters[2], 2.5);
        assert_eq!(workspace.parameters[3], 3.5);
    }

    #[test]
    fn test_scaling_modes() {
        let problem = SparseProblem::new(2);
        let initial_parameters = vec![0.0, 0.0];

        // Test with no scaling
        let config_none = SparseLevenbergMarquardtConfig {
            scaling_mode: ParameterScalingMode::None,
            ..Default::default()
        };
        let solver_none = SparseLevenbergMarquardtSolver::new(config_none);
        let mut workspace_none = SparseLevenbergMarquardtWorkspace::new(
            &problem,
            &initial_parameters,
        )
        .unwrap();
        let result_none = solver_none
            .solve_problem(&problem, &mut workspace_none)
            .unwrap();

        // Test with auto scaling
        let config_auto = SparseLevenbergMarquardtConfig {
            scaling_mode: ParameterScalingMode::Auto,
            ..Default::default()
        };
        let solver_auto = SparseLevenbergMarquardtSolver::new(config_auto);
        let mut workspace_auto = SparseLevenbergMarquardtWorkspace::new(
            &problem,
            &initial_parameters,
        )
        .unwrap();
        let result_auto = solver_auto
            .solve_problem(&problem, &mut workspace_auto)
            .unwrap();

        // Both should converge
        assert!(result_none.status.is_success());
        assert!(result_auto.status.is_success());
        assert!(result_none.cost < 1e-8);
        assert!(result_auto.cost < 1e-8);
    }

    #[test]
    fn test_convergence_criteria() {
        let problem = SparseProblem::new(2);
        let initial_parameters = vec![10.0, 20.0]; // Far from solution

        let config = SparseLevenbergMarquardtConfig {
            function_tolerance: 1e-10,
            parameter_tolerance: 1e-10,
            gradient_tolerance: 1e-10,
            max_iterations: 100,
            ..Default::default()
        };

        let solver = SparseLevenbergMarquardtSolver::new(config);
        let mut workspace = SparseLevenbergMarquardtWorkspace::new(
            &problem,
            &initial_parameters,
        )
        .unwrap();

        let result = solver.solve_problem(&problem, &mut workspace).unwrap();

        // Should converge to a good solution
        assert!(result.status.is_success());
        assert!(result.cost < 1e-8);

        // Check approximate solution (depends on problem structure)
        println!("Final parameters: {:?}", result.parameters);
    }
}
