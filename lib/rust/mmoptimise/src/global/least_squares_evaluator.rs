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

use crate::global::Evaluator;

/// Wrapper that converts any `OptimisationProblem` into an `Evaluator`.
///
/// This allows reusing existing least-squares test problems from
/// `solver::test_problems` with Differential Evolution by computing
/// the sum of squared residuals plus a weighted variance penalty.
///
/// # Cost Function
///
/// The evaluator computes:
/// ```text
/// cost = SSR + VARIANCE_WEIGHT * variance
/// ```
///
/// where:
/// - SSR = sum of squared residuals
/// - variance = population variance of residuals
/// - VARIANCE_WEIGHT = 0.1 (default tuning parameter)
///
/// This formulation is dimensionally consistent (both terms are [residual²])
/// and penalizes solutions with high variance in residuals, favoring
/// more uniform error distributions.
///
/// # Tuning
///
/// - **VARIANCE_WEIGHT = 0.1**: Standard setting (10% variance contribution)
/// - Increase for problems where uniform residuals are critical
/// - Decrease if only total error matters
///
/// # Example
///
/// ```ignore
/// use mmoptimise::differential_evolution::{LeastSquaresEvaluator, DifferentialEvolution};
/// use mmoptimise::solver::test_problems::RosenbrockProblem;
///
/// let problem = RosenbrockProblem::new();
/// let evaluator = LeastSquaresEvaluator::new(problem);
///
/// // Use with DE solver
/// let mut de = DifferentialEvolution::new(config)?;
/// let result = de.run(&evaluator, &mut workspace)?;
/// ```
pub struct LeastSquaresEvaluator<P> {
    problem: P,
    residual_buffer: Vec<f64>,
}

/// Weight for variance penalty in cost function.
///
/// Adjust this to control the trade-off between total error (SSR)
/// and uniformity of residuals (variance).
const VARIANCE_WEIGHT: f64 = 1.0;

impl<P> LeastSquaresEvaluator<P>
where
    P: crate::solver::common::OptimisationProblem,
{
    pub fn new(problem: P) -> Self {
        let residual_count = problem.residual_count();
        Self {
            problem,
            residual_buffer: vec![0.0; residual_count],
        }
    }
}

impl<P> Evaluator for LeastSquaresEvaluator<P>
where
    P: crate::solver::common::OptimisationProblem + Sync,
{
    fn evaluate(&self, x: &[f64]) -> f64 {
        let mut residuals = vec![0.0; self.residual_buffer.len()];

        // Compute residuals
        if let Err(_) = self.problem.residuals(x, &mut residuals) {
            return f64::INFINITY;
        }

        let n = residuals.len() as f64;
        if n == 0.0 {
            return f64::INFINITY;
        }

        // Compute sum of squared residuals.
        let ssr: f64 = residuals.iter().map(|r| r * r).sum();

        // Compute population variance:
        // variance = sum((x - mean)^2) / n
        let mean: f64 = residuals.iter().sum::<f64>() / n;
        let variance: f64 = residuals
            .iter()
            .map(|r| {
                let diff = r - mean;
                diff * diff
            })
            .sum::<f64>()
            / n;

        // Return weighted combination:
        // SSR + variance penalty
        //
        // Both terms are dimensionally consistent ([residual^2]).
        ssr + VARIANCE_WEIGHT * variance
    }
}
