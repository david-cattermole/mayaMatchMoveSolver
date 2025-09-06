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
use num_traits::{Float, Zero};
use std::ops::{Add, Div, Mul, Sub};
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
    #[error("Numerical instability detected")]
    NumericalInstability,
}

/// Status codes indicating how the solver terminated.
///
/// These status codes help interpret the quality and reliability of
/// the optimization result.  Understanding what each status means is
/// crucial for debugging and validating solutions.
///
/// ## Convergence Status Meanings
///
/// ### Successful Convergence
/// - **`Success`**: Converged to optimal solution within all tolerances. This is the ideal outcome.
/// - **`ToleranceReached`**: Met one or more tolerance criteria (function_tolerance, parameter_tolerance, or gradient_tolerance). Usually indicates good convergence.
/// - **`SmallCostReduction`**: Cost reduction below threshold, indicating we're near an optimum.
/// - **`SmallStepSize`**: Step size below threshold, suggesting we're at a local minimum.
/// - **`SmallGradient`**: Gradient norm below threshold, indicating a stationary point.
///
/// ### Termination Conditions
/// - **`MaxIterationsReached`**: Hit iteration limit. May need more iterations or better initial guess.
/// - **`FunctionCallsExceeded`**: Hit function evaluation limit. Consider increasing limit or improving problem conditioning.
///
/// ## Interpreting Results
///
/// ```rust
/// use mmoptimise_rust::solver::common::SolverStatus;
///
/// // Example showing how to interpret different solver statuses
/// fn interpret_status(status: SolverStatus) {
///     match status {
///         SolverStatus::Success => {
///             println!("Optimal solution found!");
///             // result.parameters contains the optimal values
///         },
///         SolverStatus::ToleranceReached => {
///             println!("Good convergence achieved");
///             // Check result.cost to verify solution quality
///         },
///         SolverStatus::MaxIterationsReached => {
///             println!("Need more iterations or better initial guess");
///             // Consider increasing max_iterations or improving starting point
///         },
///         _ => {
///             if status.is_success() {
///                 println!("Converged successfully: {:?}", status);
///             } else {
///                 println!("Solver had difficulties: {:?}", status);
///             }
///         }
///     }
/// }
/// ```
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum SolverStatus {
    /// Converged to optimal solution within all tolerances.
    Success,
    /// Met one or more tolerance criteria.
    ToleranceReached,
    /// Hit iteration limit (may need more iterations).
    MaxIterationsReached,
    /// Hit function evaluation limit.
    FunctionCallsExceeded,
    /// Cost reduction below threshold (near optimum).
    SmallCostReduction,
    /// Step size below threshold (near optimum).
    SmallStepSize,
    /// Gradient norm below threshold (near optimum).
    SmallGradient,
}

#[derive(Debug, Clone)]
pub struct OptimisationResult {
    pub status: SolverStatus,
    pub parameters: Vec<f64>,
    pub residuals: Vec<f64>,
    pub cost: f64,
    pub iterations: usize,
    pub function_evaluations: usize,
    pub jacobian_evaluations: usize,
    pub message: &'static str,
}

/// Parameter scaling modes for improving solver convergence.
///
/// Scaling helps normalize parameters with different units or magnitudes,
/// which is crucial for solver stability and convergence speed.
///
/// ## When to Use Each Mode
///
/// | Mode       | Description                                         | Best For                                                    |
/// |------------+-----------------------------------------------------+-------------------------------------------------------------|
/// | **Auto**   | Automatically scales based on Jacobian column norms | Most problems (recommended default)                         |
/// | **Manual** | User-provided scaling factors for each parameter    | When you know parameter ranges and units                    |
/// | **None**   | No scaling applied                                  | Well-conditioned problems with similar parameter magnitudes |
/// +------------+-----------------------------------------------------+-------------------------------------------------------------+
///
/// ## Examples
///
/// ```rust
/// use mmoptimise_rust::solver::common::ParameterScalingMode;
/// use mmoptimise_rust::solver::levenberg_marquardt::LevenbergMarquardtConfig;
///
/// // Recommended for most problems
/// let auto_config = LevenbergMarquardtConfig {
///     scaling_mode: ParameterScalingMode::Auto,
///     ..Default::default()
/// };
///
/// // Manual scaling when parameters have very different ranges
/// let manual_config = LevenbergMarquardtConfig {
///     scaling_mode: ParameterScalingMode::Manual,
///     ..Default::default()
/// };
///
/// // Example showing different scaling modes
/// assert_eq!(auto_config.scaling_mode, ParameterScalingMode::Auto);
/// assert_eq!(manual_config.scaling_mode, ParameterScalingMode::Manual);
/// ```
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ParameterScalingMode {
    /// No scaling applied - use when parameters are already well-scaled.
    None,
    /// Automatically scale based on initial Jacobian column norms (recommended).
    Auto,
    /// User-provided scaling factors for fine-tuned control.
    Manual,
}

impl SolverStatus {
    /// Returns `true` if the solver status indicates successful
    /// convergence.
    ///
    /// Considers all the "success" status codes that indicate the
    /// solver has found a satisfactory solution, even if it didn't
    /// reach the absolute optimal point.
    ///
    /// # Example
    /// ```rust
    /// use mmoptimise_rust::solver::common::SolverStatus;
    ///
    /// let status = SolverStatus::Success;
    /// assert!(status.is_success());
    ///
    /// let status = SolverStatus::MaxIterationsReached;
    /// assert!(!status.is_success());
    /// ```
    pub fn is_success(self) -> bool {
        matches!(
            self,
            SolverStatus::Success
                | SolverStatus::ToleranceReached
                | SolverStatus::SmallCostReduction
                | SolverStatus::SmallStepSize
                | SolverStatus::SmallGradient
        )
    }
}

/// Trait for defining optimization problems compatible with
/// optimization solvers.
///
/// Allows you to define custom optimization problems by implementing
/// residual computation. Solvers use automatic differentiation (dual
/// numbers) to compute gradients, so your residual function must work
/// with generic numeric types.
///
/// ## Requirements
///
/// - **Overdetermined system**: `residual_count() >= parameter_count()`.
/// - **Differentiable**: Residual function must be smooth and differentiable.
/// - **Generic numerics**: Must work with both `f64` and `Dual<f64>` types.
///
/// ## Implementation Guidelines
///
/// 1. **Residual Definition**: Define residuals as `predicted - actual` or similar.
/// 2. **Numerical Stability**: Avoid operations that can cause NaN or infinite values.
/// 3. **Parameter Scaling**: Consider parameter magnitudes when designing the problem.
/// 4. **Testing**: Always test your residual function before optimization.
///
/// ## Basic Example: Exponential Curve Fitting
///
/// ```rust
/// use mmoptimise_rust::solver::common::OptimisationProblem;
/// use anyhow::Result;
/// use std::ops::{Add, Sub, Mul, Div};
/// use num_traits::{Float, Zero};
///
/// // Simple quadratic fitting problem: y = a*x^2 + b*x + c
/// struct QuadraticFitting {
///     x_data: Vec<f64>,
///     y_data: Vec<f64>,
/// }
///
/// impl OptimisationProblem for QuadraticFitting {
///     fn residuals<T>(
///         &self,
///         parameters: &[T],
///         out_residuals: &mut [T],
///     ) -> Result<()>
///     where
///         T: Copy + Add<Output = T> + Sub<Output = T> + Mul<Output = T> + Div<Output = T>
///             + From<f64> + Sized + Zero + Float,
///     {
///         // Parameters: [a, b, c] for y = a*x^2 + b*x + c
///         let a = parameters[0];
///         let b = parameters[1];
///         let c = parameters[2];
///
///         for (i, (&x, &y)) in self.x_data.iter().zip(&self.y_data).enumerate() {
///             let x_val = <T as From<f64>>::from(x);
///             let y_val = <T as From<f64>>::from(y);
///             let predicted = a * x_val * x_val + b * x_val + c;
///
///             // Residual = predicted - actual
///             out_residuals[i] = predicted - y_val;
///         }
///         Ok(())
///     }
///
///     fn parameter_count(&self) -> usize { 3 }  // [a, b, c]
///     fn residual_count(&self) -> usize { self.x_data.len() }
/// }
///
/// // Example usage
/// let problem = QuadraticFitting {
///     x_data: vec![0.0, 1.0, 2.0],
///     y_data: vec![1.0, 4.0, 9.0], // y = x^2 + 3x + 1
/// };
/// assert_eq!(problem.parameter_count(), 3);
/// assert_eq!(problem.residual_count(), 3);
/// ```
///
/// ## Advanced Example: Parameter Constraints
///
/// ```rust
/// use mmoptimise_rust::solver::common::OptimisationProblem;
/// use anyhow::Result;
/// use std::ops::{Add, Sub, Mul, Div};
/// use num_traits::{Float, Zero};
///
/// // Linear problem with positive constraint: y = exp(raw_param) * x
/// struct ConstrainedProblem {
///     data: Vec<(f64, f64)>,
/// }
///
/// impl OptimisationProblem for ConstrainedProblem {
///     fn residuals<T>(&self, parameters: &[T], out_residuals: &mut [T]) -> Result<()>
///     where T: Copy + Add<Output = T> + Sub<Output = T> + Mul<Output = T> + Div<Output = T>
///             + From<f64> + Sized + Zero + Float,
///     {
///         // Transform parameter to ensure positivity: param = exp(raw_param)
///         let positive_param = parameters[0].exp();
///
///         for (i, &(x, y)) in self.data.iter().enumerate() {
///             let x_val = <T as From<f64>>::from(x);
///             let y_val = <T as From<f64>>::from(y);
///             let predicted = positive_param * x_val;
///             out_residuals[i] = predicted - y_val;
///         }
///         Ok(())
///     }
///
///     fn parameter_count(&self) -> usize { 1 }
///     fn residual_count(&self) -> usize { self.data.len() }
/// }
///
/// // Example usage
/// let problem = ConstrainedProblem {
///     data: vec![(1.0, 2.0), (2.0, 4.0), (3.0, 6.0)],
/// };
/// assert_eq!(problem.parameter_count(), 1);
/// assert_eq!(problem.residual_count(), 3);
/// ```
pub trait OptimisationProblem {
    /// Compute residuals for both `f64` and `Dual<f64>` types.
    ///
    /// Must compute the residual vector for the given parameters.
    /// The solver uses automatic differentiation, so this function
    /// must work with generic numeric types (both f64 and
    /// `Dual<f64>`).
    ///
    /// # Parameters
    ///
    /// - `parameters`: Input parameters (length = `parameter_count()`).
    /// - `out_residuals`: Output residuals (length = `residual_count()`).
    ///
    /// # Returns
    ///
    /// `Ok(())` on success, or an error if computation fails.
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
            + Float;

    /// Number of optimization parameters.
    fn parameter_count(&self) -> usize;

    /// Number of residual equations (must be >= parameter_count).
    fn residual_count(&self) -> usize;
}
