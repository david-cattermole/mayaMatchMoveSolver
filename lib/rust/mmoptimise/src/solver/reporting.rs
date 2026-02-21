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

//! Solver iteration reporting and timing utilities.
//!
//! Provides Ceres-style progress output for optimization solvers.
//! All functionality is compile-time conditional via `DEBUG` flags in each solver.
//!
//! # Zero-Overhead Design
//!
//! When `DEBUG = false`, the Rust optimizer eliminates all this code,
//! resulting in zero runtime overhead.
//!
//! # Example Usage
//!
//! ```rust,ignore
//! const DEBUG: bool = true;  // Set to false for production
//!
//! let mut timings = if DEBUG { Some(SolverTimings::new()) } else { None };
//!
//! if DEBUG {
//!     print_problem_summary(&ProblemSummary {
//!         parameter_blocks: 1,
//!         parameters: n,
//!         residuals: m,
//!         solver_type: "TRUST_REGION (Levenberg-Marquardt)",
//!         linear_solver: "QR_DECOMPOSITION",
//!         threads: 1,
//!     });
//!     print_iteration_header();
//! }
//!
//! for iteration in 0..max_iterations {
//!     if DEBUG {
//!         if let Some(ref mut t) = timings {
//!             t.start_iteration();
//!         }
//!     }
//!
//!     // ... solver iteration logic ...
//!
//!     if DEBUG {
//!         if let Some(ref mut t) = timings {
//!             t.finish_iteration();
//!             print_iteration(&IterationMetrics { ... }, true);
//!         }
//!     }
//! }
//! ```

use std::time::Instant;

/// Timing data accumulator for solver iterations.
///
/// Tracks cumulative time spent in different solver operations across iterations.
/// Provides methods to record timing for each operation type.
#[derive(Debug, Clone)]
pub struct SolverTimings {
    /// When solver started (epoch for all timing)
    pub total_start: Instant,
    /// When current iteration started
    pub iteration_start: Instant,

    // Cumulative times (seconds)
    /// Total time in residual evaluation
    pub residual_time_seconds: f64,
    /// Total time in Jacobian evaluation
    pub jacobian_time_seconds: f64,
    /// Total time in linear solver
    pub linear_solver_time_seconds: f64,
    /// Total time in minimizer overhead (computed as difference)
    pub minimizer_time_seconds: f64,
    /// Total elapsed time
    pub total_time_seconds: f64,

    // Per-iteration tracking
    /// Last iteration's residual time
    pub last_residual_time_seconds: f64,
    /// Last iteration's Jacobian time
    pub last_jacobian_time_seconds: f64,
    /// Last iteration's linear solver time
    pub last_linear_solver_time_seconds: f64,
}

impl SolverTimings {
    /// Create new timing tracker starting now.
    pub fn new() -> Self {
        let now = Instant::now();
        Self {
            total_start: now,
            iteration_start: now,
            residual_time_seconds: 0.0,
            jacobian_time_seconds: 0.0,
            linear_solver_time_seconds: 0.0,
            minimizer_time_seconds: 0.0,
            total_time_seconds: 0.0,
            last_residual_time_seconds: 0.0,
            last_jacobian_time_seconds: 0.0,
            last_linear_solver_time_seconds: 0.0,
        }
    }

    /// Mark the start of a new iteration.
    pub fn start_iteration(&mut self) {
        self.iteration_start = Instant::now();
        // Reset per-iteration counters
        self.last_residual_time_seconds = 0.0;
        self.last_jacobian_time_seconds = 0.0;
        self.last_linear_solver_time_seconds = 0.0;
    }

    /// Record time spent in residual evaluation.
    pub fn record_residual_time(&mut self, start: Instant) {
        let elapsed_seconds = start.elapsed().as_secs_f64();
        self.last_residual_time_seconds += elapsed_seconds;
        self.residual_time_seconds += elapsed_seconds;
    }

    /// Record time spent in Jacobian evaluation.
    pub fn record_jacobian_time(&mut self, start: Instant) {
        let elapsed_seconds = start.elapsed().as_secs_f64();
        self.last_jacobian_time_seconds += elapsed_seconds;
        self.jacobian_time_seconds += elapsed_seconds;
    }

    /// Record time spent in linear solver.
    pub fn record_linear_solver_time(&mut self, start: Instant) {
        let elapsed_seconds = start.elapsed().as_secs_f64();
        self.last_linear_solver_time_seconds += elapsed_seconds;
        self.linear_solver_time_seconds += elapsed_seconds;
    }

    /// Finish current iteration and update cumulative times.
    ///
    /// Computes minimizer overhead as: total - (residual + jacobian + linear_solver)
    pub fn finish_iteration(&mut self) {
        self.total_time_seconds = self.total_start.elapsed().as_secs_f64();
        self.minimizer_time_seconds = self.total_time_seconds
            - (self.residual_time_seconds
                + self.jacobian_time_seconds
                + self.linear_solver_time_seconds);
    }

    /// Get iteration time (time since start_iteration was called).
    pub fn iteration_elapsed(&self) -> f64 {
        self.iteration_start.elapsed().as_secs_f64()
    }
}

impl Default for SolverTimings {
    fn default() -> Self {
        Self::new()
    }
}

/// Per-iteration metrics for progress table display.
///
/// Contains all the metrics shown in each row of the Ceres-style iteration table.
#[derive(Debug)]
pub struct IterationMetrics {
    /// Iteration number (0-indexed)
    pub iteration: usize,
    /// Current cost (objective function value)
    pub cost: f64,
    /// Cost reduction from previous iteration
    pub cost_change: f64,
    /// Gradient norm (normalized by cost)
    pub gradient_norm: f64,
    /// Step size (L2 norm of parameter change)
    pub step_norm: f64,
    /// Trust region ratio (actual/predicted reduction) - LM/Powell only
    pub tr_ratio: f64,
    /// Trust region radius - LM/Powell only
    pub tr_radius: f64,
    /// Line search iterations - Gauss-Newton only
    pub ls_iter: usize,
    /// Time for this iteration (seconds)
    pub iter_time_seconds: f64,
    /// Total elapsed time (seconds)
    pub total_time_seconds: f64,
}

/// Problem summary information displayed before iterations.
///
/// Provides overview of problem size and solver configuration.
#[derive(Debug)]
pub struct ProblemSummary {
    /// Number of parameter blocks (for structured problems like BA)
    pub parameter_blocks: usize,
    /// Total number of parameters
    pub parameters: usize,
    /// Total number of residuals
    pub residuals: usize,
    /// Solver type description (e.g., "TRUST_REGION (Levenberg-Marquardt)")
    pub solver_type: &'static str,
    /// Linear solver type (e.g., "QR_DECOMPOSITION", "CHOLMOD_CHOLESKY")
    pub linear_solver: &'static str,
    /// Number of threads (currently always 1)
    pub threads: usize,
}

/// Print iteration table header matching Ceres format.
pub fn print_iteration_header() {
    eprintln!();
    eprintln!("iter      cost      cost_change  |gradient|   |step|    tr_ratio    tr_radius   ls_iter  iter_time  total_time");
    eprintln!("----  ------------  ------------  ----------  --------  ----------  ----------  -------  ---------  ----------");
}

/// Print single iteration row in Ceres format.
///
/// # Arguments
/// * `metrics` - Iteration metrics to display
/// * `has_trust_region` - true for LM/Powell (show tr_ratio/tr_radius), false for GN (show ls_iter)
pub fn print_iteration(metrics: &IterationMetrics, has_trust_region: bool) {
    if has_trust_region {
        // Trust region solvers (LM, Powell Dog-Leg)
        eprintln!(
            "{:4}  {:12.6e}  {:12.2e}  {:10.2e}  {:8.2e}  {:10.2e}  {:10.2e}   -       {:9.6}  {:10.6}",
            metrics.iteration,
            metrics.cost,
            metrics.cost_change,
            metrics.gradient_norm,
            metrics.step_norm,
            metrics.tr_ratio,
            metrics.tr_radius,
            metrics.iter_time_seconds,
            metrics.total_time_seconds
        );
    } else {
        // Line search solvers (Gauss-Newton)
        eprintln!(
            "{:4}  {:12.6e}  {:12.2e}  {:10.2e}  {:8.2e}        -           -     {:3}      {:9.6}  {:10.6}",
            metrics.iteration,
            metrics.cost,
            metrics.cost_change,
            metrics.gradient_norm,
            metrics.step_norm,
            metrics.ls_iter,
            metrics.iter_time_seconds,
            metrics.total_time_seconds
        );
    }
}

/// Print problem summary header matching Ceres format.
pub fn print_problem_summary(summary: &ProblemSummary) {
    eprintln!();
    eprintln!("Solver Summary (Given)");
    eprintln!();

    // Only show parameter blocks if there's structure (BA problems)
    if summary.parameter_blocks > 1 {
        eprintln!(
            "                               Original                  Reduced"
        );
        eprintln!(
            "Parameter blocks            {:10}                {:10}",
            summary.parameter_blocks, summary.parameter_blocks
        );
    }

    eprintln!(
        "Parameters                  {:10}                {:10}",
        summary.parameters, summary.parameters
    );
    eprintln!(
        "Residuals                   {:10}                {:10}",
        summary.residuals, summary.residuals
    );
    eprintln!();
    eprintln!("Minimizer                   {}", summary.solver_type);
    eprintln!("Linear solver               {}", summary.linear_solver);
    eprintln!("Threads                     {:10}", summary.threads);
}

/// Print timing breakdown by operation type.
pub fn print_timing_breakdown(timings: &SolverTimings) {
    eprintln!();
    eprintln!("Time (in seconds):");
    eprintln!(
        "  Residual evaluation       {:10.6}",
        timings.residual_time_seconds
    );
    eprintln!(
        "  Jacobian evaluation       {:10.6}",
        timings.jacobian_time_seconds
    );
    eprintln!(
        "  Linear solver             {:10.6}",
        timings.linear_solver_time_seconds
    );
    eprintln!(
        "  Minimizer                 {:10.6}",
        timings.minimizer_time_seconds
    );
    eprintln!(
        "  Total                     {:10.6}",
        timings.total_time_seconds
    );
}

/// Print final summary with cost change and termination reason.
///
/// # Arguments
/// * `initial_cost` - Cost at start of optimization
/// * `final_cost` - Cost at end of optimization
/// * `iterations` - Number of iterations performed
/// * `termination_reason` - Human-readable termination message
pub fn print_final_summary(
    initial_cost: f64,
    final_cost: f64,
    iterations: usize,
    termination_reason: &str,
) {
    let cost_change = initial_cost - final_cost;
    let relative_change = if initial_cost.abs() > 1e-10 {
        cost_change / initial_cost
    } else {
        0.0
    };

    eprintln!();
    eprintln!("Solver Summary (Iterative)");
    eprintln!();
    eprintln!(
        "                                     Initial                      Final"
    );
    eprintln!(
        "Cost                             {:12.6e}              {:12.6e}",
        initial_cost, final_cost
    );
    eprintln!(
        "Change                           {:12.6e}              {:12.6e}",
        cost_change, relative_change
    );
    eprintln!();
    eprintln!("Minimizer iterations         {:10}", iterations);
    eprintln!();
    eprintln!("Termination:                 {}", termination_reason);
    eprintln!();
}
