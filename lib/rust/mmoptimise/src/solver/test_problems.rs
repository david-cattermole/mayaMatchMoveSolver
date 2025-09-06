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

use crate::solver::common::{OptimisationError, OptimisationProblem};

/// The Rosenbrock function.
///
/// A classic optimization test problem.
///
/// **Mathematical Form**: f(x, y) = (a - x)^2 + b*(y - x^2)^2
///
/// **Global Minimum**: (x, y) = (a, a^2) with f = 0
/// **Default Parameters**: a = 1, b = 100, so minimum at (1, 1)
///
/// **Test Purpose**: This problem tests solver robustness with:
/// - A narrow, curved valley that's difficult to navigate
/// - Poor conditioning when b >> 1 (default b = 100)
/// - Requires both coarse and fine optimization phases
/// - Classic benchmark for gradient-based methods
///
/// **Least-Squares Formulation**:
/// - r1 = a - x
/// - r2 = √b * (y - x^2)
/// - Minimizes ||r||^2 = r1^2 + r2^2 = original Rosenbrock function
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
        if parameters.len() != 2 {
            return Err(OptimisationError::InvalidInput(
                "Rosenbrock problem requires exactly 2 parameters".to_string(),
            )
            .into());
        }

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

/// Curve fitting problem.
///
/// Fitting exponential model to noisy data.
///
/// **Mathematical Form**: y = exp(m*x + c)
/// **Parameters**: m (slope), c (intercept)
/// **Data**: Noisy data points.
///
/// **Test Purpose**: This problem tests solver performance with:
/// - Real-world noisy data (representative of practical applications)
/// - Non-linear exponential model requiring robust optimization
/// - Over-determined system (65 residuals, 2 parameters)
/// - Realistic tolerances due to noise in observations
/// - Tests parameter scaling between slope and intercept terms
///
/// **Residual Structure**: For each data point (xi, yi):
/// - ri = yi - exp(m*xi + c)
/// - Minimizes sum of squared residuals
pub struct CurveFittingProblem {
    pub x_data: Vec<f64>,
    pub y_data: Vec<f64>,
}

impl CurveFittingProblem {
    pub fn from_example_data() -> Self {
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
        if parameters.len() != 2 {
            return Err(OptimisationError::InvalidInput(
                "Curve fitting requires 2 parameters (m, c)".to_string(),
            )
            .into());
        }

        let m = parameters[0];
        let c = parameters[1];

        for (i, (x, y)) in self.x_data.iter().zip(&self.y_data).enumerate() {
            let x_val = <T as From<f64>>::from(*x);
            let y_val = <T as From<f64>>::from(*y);
            // Residual: y - exp(m*x + c)
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

/// Bukin function N.6.
///
/// An extremely challenging optimization landscape.
///
/// **Mathematical Form**: f(x, y) = 100 * sqrt(|y - 0.01*x^2|) + 0.01 * |x + 10|
/// **Global Minimum**: f(-10, 1) = 0
/// **Domain**: -15 <= x <= -5, -3 <= y <= 3
///
/// **Test Purpose**: This problem tests solver resilience with:
/// - Extremely narrow curved valley (much worse than Rosenbrock)
/// - Non-smooth objective (absolute values, square roots)
/// - Multiple local minima and saddle points
/// - Restricted domain requiring careful step size control
/// - Tests solver behavior near function non-differentiabilities
///
/// **Numerical Challenges**:
/// - Gradient discontinuities at |·| = 0 points
/// - Very steep valley walls (factor of 100)
/// - Requires precise navigation of narrow feasible region
pub struct BukinN6Problem;

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
        if parameters.len() != 2 {
            return Err(OptimisationError::InvalidInput(
                "Bukin N6 requires 2 parameters".to_string(),
            )
            .into());
        }

        let x = parameters[0];
        let y = parameters[1];

        let point_zero_one = <T as From<f64>>::from(0.01);
        let ten = <T as From<f64>>::from(10.0);

        // Split into two residuals to form a least squares problem:
        // f(x,y) = r1^2 + r2^2 where:
        // r1 = 10 * (|y - 0.01*x^2|)^(1/4)  (fourth root to get sqrt when squared)
        // r2 = 0.1 * sqrt(|x + 10|)

        let term1 = (y - point_zero_one * x * x).abs();
        let term2 = (x + ten).abs();

        // Use fourth root for first term so squaring gives sqrt
        out_residuals[0] = <T as From<f64>>::from(10.0)
            * term1.powf(<T as From<f64>>::from(0.25));
        // Use sqrt for second term
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

/// Goldstein-Price function.
///
/// A complex multi-modal optimization landscape.
///
/// **Mathematical Form**: Product of two quadratic polynomials
/// **Global Minimum**: f(0, -1) = 3
/// **Characteristics**: Highly multi-modal with many local minima
///
/// **Test Purpose**: This problem tests solver capability with:
/// - Multiple local minima requiring global search capability
/// - Complex polynomial structure with high-order terms
/// - Tests convergence to different local minima from different starts
/// - Requires robust line search and step size control
/// - Benchmark for testing solver consistency across runs
///
/// **Optimization Challenges**:
/// - Easy to get trapped in local minima
/// - Steep gradients and poor conditioning in some regions
/// - Requires good initial guess for consistent global convergence
pub struct GoldsteinPriceFunction;

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
        if parameters.len() != 2 {
            return Err(OptimisationError::InvalidInput(
                "Goldstein-Price requires 2 parameters".to_string(),
            )
            .into());
        }

        let x = parameters[0];
        let y = parameters[1];

        // The Goldstein-Price function is:
        // f(x,y) = [1 + (x + y + 1)^2 * (19 - 14x + 3x^2 - 14y + 6xy + 3y^2)]
        //        * [30 + (2x - 3y)^2 * (18 - 32x + 12x^2 + 48y - 36xy + 27y^2)]

        // To convert to least squares, split into two residuals:
        // r1 = sqrt(term1) - sqrt(1 + (1+1+1)^2 * 19) at minimum
        // r2 = sqrt(term2) - sqrt(30) at minimum
        // This ensures m >= n constraint while maintaining the same optimization

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

        // Split into two residuals to satisfy m >= n
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

/// Near-singular Jacobian problem.
///
/// Tests numerical stability with rank-deficient systems.
///
/// **Mathematical Form**:
/// - r1 = x1 + 1e-10 * x2 - 1
/// - r2 = x1 + 1e-10 * x2 - 1  (nearly identical to r1)
///
/// **Test Purpose**: This problem tests solver robustness with:
/// - **Nearly rank-deficient Jacobian matrix** - The two residuals are almost linearly dependent
/// - **Numerical conditioning issues** - Small coefficient (1e-10) creates near-singularity
/// - **Linear system stability** - Tests solver's ability to detect and handle ill-conditioning
/// - **Regularization behavior** - Tests automatic regularization mechanisms
/// - **Error detection** - Validates proper handling of near-singular normal equations
///
/// **Condition Number**: Extremely high (~1e10), approaching machine precision limits
///
/// **Expected Solver Behavior**:
/// - **Robust solvers**: Should detect singularity and handle gracefully (e.g., via regularization)
/// - **Naive solvers**: May fail with numerical errors or produce unreliable results
/// - **Gauss-Newton**: Should trigger small step size or regularization recovery
/// - **LM solvers**: Should increase damping parameter to improve conditioning
pub struct NearSingularProblem;

impl OptimisationProblem for NearSingularProblem {
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
        // Create residuals where Jacobian is nearly singular:
        // r1 = x1 + 1e-10 * x2 - 1
        // r2 = x1 + 1e-10 * x2 - 1  (nearly identical to r1)
        let x1 = parameters[0];
        let x2 = parameters[1];
        let tiny = <T as From<f64>>::from(1e-10);
        let one = <T as From<f64>>::from(1.0);

        out_residuals[0] = x1 + tiny * x2 - one;
        out_residuals[1] = x1 + tiny * x2 - one;
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }
    fn residual_count(&self) -> usize {
        2
    }
}

/// Zero Jacobian column problem.
///
/// Tests handling of parameters that don't affect the objective.
///
/// **Mathematical Form**:
/// - r1 = x1 - 1
/// - r2 = x1 - 1
/// - **Note**: x2 parameter appears in function signature but doesn't affect residuals
///
/// **Test Purpose**: This problem tests solver capability with:
/// - **Rank-deficient Jacobian** - Second column is entirely zero
/// - **Unidentifiable parameters** - x2 cannot be determined from residuals
/// - **Linear system singularity** - J^T*J matrix is singular
/// - **Parameter subset optimization** - Only x1 affects the objective
/// - **Robustness testing** - Validates graceful handling of degenerate cases
///
/// **Expected Solver Behavior**:
/// - **Robust solvers**: Should detect rank deficiency immediately (iteration 0 or 1)
/// - **Error handling**: Should terminate with `SmallStepSize` or similar status
/// - **Parameter values**: x1 should converge to 1.0, x2 remains at initial value
/// - **Regularization**: May help but won't resolve fundamental rank deficiency
/// - **Practical insight**: Demonstrates need for identifiable parameter sets
pub struct ZeroJacobianProblem;

impl OptimisationProblem for ZeroJacobianProblem {
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
        // Only first parameter affects residuals, second parameter has zero
        // partial derivatives.
        let x1 = parameters[0];
        let _x2 = parameters[1]; // Unused, creates zero Jacobian column.
        let one = <T as From<f64>>::from(1.0);

        out_residuals[0] = x1 - one;
        out_residuals[1] = x1 - one;
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }
    fn residual_count(&self) -> usize {
        2
    }
}

/// Cost stagnation problem.
///
/// Tests convergence detection in extremely flat regions.
///
/// **Mathematical Form**:
/// - r1 = 1e-6 * (x - 1)^4
/// - r2 = 1e-6 * (y - 1)^4
/// - **Optimum**: (x, y) = (1, 1) with f = 0
///
/// **Test Purpose**: This problem tests solver convergence detection with:
/// - **Extremely flat cost landscape** - Fourth-power terms create very small gradients near optimum
/// - **Gradient tolerance testing** - Tests gradient-based convergence criteria
/// - **Cost stagnation detection** - Tests function value improvement thresholds
/// - **Numerical precision limits** - Small scale factor (1e-6) tests tolerance handling
/// - **Step size sensitivity** - Small gradients may produce very small steps
///
/// **Mathematical Properties**:
/// - **Gradient**: ∇f = [4 * 1e-6 * (x-1)^3, 4 * 1e-6 * (y-1)^3]
/// - **Hessian**: H = diag[12 * 1e-6 * (x-1)^2, 12 * 1e-6 * (y-1)^2]
/// - **Near (1,1)**: Gradients and Hessian values become extremely small
///
/// **Expected Solver Behavior**:
/// - **Convergence criteria**: Should trigger `SmallGradient` or `SmallCostReduction`
/// - **Iteration count**: May require many iterations due to small steps
/// - **Tolerance sensitivity**: Success depends heavily on gradient/function tolerance settings
/// - **Numerical stability**: Tests solver behavior at limits of floating-point precision
/// - **Practical insight**: Represents optimization near already-good parameter values
pub struct StagnationProblem;

impl OptimisationProblem for StagnationProblem {
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
        // Function with a very flat region near the optimum.
        let x = parameters[0];
        let y = parameters[1];
        let one = <T as From<f64>>::from(1.0);
        let small = <T as From<f64>>::from(1e-6);

        // Near (1,1), the function becomes very flat.
        let dx = x - one;
        let dy = y - one;

        // Fourth power makes it very flat.
        out_residuals[0] = small * dx * dx * dx * dx;
        out_residuals[1] = small * dy * dy * dy * dy;
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }
    fn residual_count(&self) -> usize {
        2
    }
}

/// Oscillating behavior problem.
///
/// Tests solver robustness with sinusoidal perturbations.
///
/// **Mathematical Form**:
/// - r1 = (x - 1) * (1 + 0.1 * sin(2x))
/// - r2 = (y - 1) * (1 + 0.1 * cos(2y))
/// - **Optimum**: (x, y) = (1, 1) with f = 0
///
/// **Purpose**:
/// This problem introduces oscillatory behavior near the optimum through
/// sinusoidal perturbations. The derivatives contain additional cosine and sine
/// terms that can create small-scale oscillations in the gradient, potentially
/// causing:
///
/// - Step size oscillations if line search is not robust
/// - Convergence instability near the solution
/// - Testing of solver's ability to handle non-monotonic progress
///
/// The problem is designed to have a clear global minimum at (1,1) but with
/// local perturbations that test the solver's stability when dealing with
/// oscillatory gradient information.
pub struct OscillatingProblem;

impl OptimisationProblem for OscillatingProblem {
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
        // A function with some local complexity that might cause oscillation.
        let x = parameters[0];
        let y = parameters[1];
        let one = <T as From<f64>>::from(1.0);
        let two = <T as From<f64>>::from(2.0);
        let scale = <T as From<f64>>::from(0.1);

        // Add some oscillatory terms that might cause issues.
        out_residuals[0] = (x - one) * (one + scale * (x * two).sin());
        out_residuals[1] = (y - one) * (one + scale * (y * two).cos());
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }
    fn residual_count(&self) -> usize {
        2
    }
}

/// Difficult optimization landscape.
///
/// Tests solver performance with extreme conditioning.
///
/// **Mathematical Form**:
/// - r1 = 1000 * x² + y² - 1
/// - r2 = 0
/// - **Optimum**: Approximately (0, 0) with f ≈ 1
///
/// **Purpose**:
/// This problem creates an extremely ill-conditioned optimization landscape
/// with:
///
/// - **High condition number**: The x-direction is scaled by 1000x compared to y
/// - **Steep gradients**: Rapid change in the x-direction creates numerical challenges
/// - **Line search difficulties**: Large steps in x can cause overshooting
/// - **Poor convergence**: Standard algorithms may struggle with the scaling mismatch
///
/// The elliptical contours are extremely elongated, testing:
///
/// - Solver's ability to handle badly scaled problems
/// - Numerical stability with large gradient differences
/// - Convergence behavior when Hessian eigenvalues differ by orders of magnitude
/// - Step size selection in the presence of dramatic scaling differences
pub struct DifficultLandscapeProblem;

impl OptimisationProblem for DifficultLandscapeProblem {
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
        // Create a function with a very steep gradient that can cause line
        // search issues:
        // f(x,y) = 1000 * x^2 + y^2 - 1 (highly scaled problem)
        let x = parameters[0];
        let y = parameters[1];
        let scale = <T as From<f64>>::from(1000.0);
        let one = <T as From<f64>>::from(1.0);

        let f = scale * x * x + y * y - one;
        out_residuals[0] = f;
        out_residuals[1] = T::zero(); // Second residual is always zero
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }
    fn residual_count(&self) -> usize {
        2
    }
}

/// Mock 3D problem.
///
/// Tests basic solver functionality with higher dimensional parameter space.
///
/// **Mathematical Form**:
/// - r1 = 0
/// - r2 = 0
/// - r3 = 0
/// - **Parameters**: 3 (x, y, z)
/// - **Residuals**: 3 (all zero)
///
/// **Purpose**:
/// This is a trivial test problem that serves as a basic functionality check for:
/// - **Higher dimensionality**: Tests solver with 3 parameters instead of typical 2
/// - **Memory allocation**: Verifies correct array sizing for parameters and residuals
/// - **Interface validation**: Ensures solver can handle 3D parameter vectors
/// - **Trivial convergence**: Should converge immediately (cost is always 0)
///
/// Since all residuals are zero, any parameter values result in perfect convergence.
/// This problem is primarily used for:
/// - Basic functionality testing
/// - Memory layout verification
/// - Dimensional compatibility checks
/// - Baseline performance measurement
pub struct Mock3DProblem;

impl OptimisationProblem for Mock3DProblem {
    fn residuals<T>(
        &self,
        _parameters: &[T],
        _out_residuals: &mut [T],
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
        Ok(())
    }
    fn parameter_count(&self) -> usize {
        3
    }
    fn residual_count(&self) -> usize {
        3
    }
}

/// Underdetermined problem.
///
/// Tests solver behavior with fewer residuals than parameters.
///
/// **Mathematical Form**:
/// - r1 = x1 - 1
/// - **Parameters**: 2 (x1, x2)
/// - **Residuals**: 1 (underdetermined system)
///
/// **Purpose**:
/// This problem creates an underdetermined system where there are more
/// parameters than residuals, resulting in:
///
/// - **Non-unique solution**: Infinite solutions exist (x1 = 1, x2 = anything)
/// - **Rank-deficient Jacobian**: The Jacobian matrix is not full rank
/// - **Solver robustness**: Tests how solvers handle singular or near-singular systems
/// - **Convergence behavior**: May converge to different solutions depending on starting point
///
/// The problem tests:
/// - **Matrix factorization stability**: Handling of rank-deficient systems
/// - **Convergence criteria**: When to stop with non-unique solutions
/// - **Numerical stability**: Behavior when normal equations are singular
/// - **Regularization needs**: Whether additional constraints are required
///
/// Expected behavior varies by solver:
/// - Some solvers may find one of the infinite solutions
/// - Others may struggle with the singular system
/// - Regularized methods should handle this more gracefully
pub struct UnderdeterminedProblem;

impl OptimisationProblem for UnderdeterminedProblem {
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
        // Only one residual for two parameters.
        let x1 = parameters[0];
        let one = <T as From<f64>>::from(1.0);
        out_residuals[0] = x1 - one;
        Ok(())
    }

    fn parameter_count(&self) -> usize {
        2
    }
    fn residual_count(&self) -> usize {
        // NOTE: Fewer residuals than parameters.
        1
    }
}

/// Powell's function.
///
/// A classic difficult optimization problem.
///
/// **Mathematical Form**: f(x) = (x1 + 10*x2)^2 + 5*(x3 - x4)^2 + (x2 - 2*x3)^4 + 10*(x1 - x4)^4
///
/// **Global Minimum**: Approximately (0, 0, 0, 0) with f = 0
///
/// **Test Purpose**: This problem tests solver robustness with:
/// - Mixed quadratic and quartic terms creating complex curvature
/// - Different scaling between terms causing conditioning issues  
/// - Multiple local minima in higher dimensional space
/// - Tests solver behavior with rank-deficient Jacobian regions
///
/// **Least-Squares Formulation**:
/// - r1 = x1 + 10*x2
/// - r2 = √5 * (x3 - x4)
/// - r3 = (x2 - 2*x3)^2
/// - r4 = √10 * (x1 - x4)^2
/// - Minimizes ||r||^2 = r1^2 + r2^2 + r3^2 + r4^2 = original Powell function
pub struct PowellProblem;

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
        if parameters.len() != 4 {
            return Err(OptimisationError::InvalidInput(
                "Powell problem requires exactly 4 parameters".to_string(),
            )
            .into());
        }

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

/// Extended Rosenbrock function.
///
/// Generalization of Rosenbrock function to N dimensions.
///
/// **Mathematical Form**: f(x) = sum_{i=1}^{N/2} [100*(x_{2i} - x_{2i-1}^2)^2 + (1 - x_{2i-1})^2]
/// **Global Minimum**: (1, 1, ..., 1) with f = 0
/// **Constraint**: N must be even and >= 2
///
/// **Test Purpose**: This problem tests solver performance with:
/// - Higher dimensional parameter spaces (common sizes: 4, 10, 100, 1000)
/// - Scalability of algorithms as problem size increases
/// - Memory allocation efficiency for large Jacobian matrices
/// - Convergence behavior in higher dimensions
/// - Tests for algorithmic complexity scaling
///
/// **Least-Squares Formulation**: For each pair (x_{2i-1}, x_{2i}):
/// - r_{2i-1} = 10 * (x_{2i} - x_{2i-1}^2)  (valley constraint)
/// - r_{2i} = 1 - x_{2i-1}                  (bias towards x=1)
/// - Minimizes sum over all pairs: ||r||^2
pub struct ExtendedRosenbrockProblem {
    pub n: usize,
}

impl ExtendedRosenbrockProblem {
    pub fn new(n: usize) -> Self {
        assert!(n >= 2 && n % 2 == 0, "N must be even and >= 2");
        Self { n }
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
        if parameters.len() != self.n {
            return Err(OptimisationError::InvalidInput(format!(
                "Extended Rosenbrock requires {} parameters",
                self.n
            ))
            .into());
        }

        let one = <T as From<f64>>::from(1.0);
        let ten = <T as From<f64>>::from(10.0);

        for i in 0..(self.n / 2) {
            let x1 = parameters[2 * i];
            let x2 = parameters[2 * i + 1];

            out_residuals[2 * i] = ten * (x2 - x1 * x1);
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
