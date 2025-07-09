//
// Copyright (C) 2024, 2025 David Cattermole.
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
/// Mathematical interpolation functions.
use crate::constant::Real;
use enum_dispatch::enum_dispatch;
use std::cell::{Cell, RefCell};

/// Return 'min_value' to 'max_value' linearly, for a 'mix' value
/// between 0.0 and 1.0.
///
/// Usage:
/// - Smoothly transition between two values
/// - Generate points along a line
/// - Create gradients or animations
pub fn lerp_f64(min_value: Real, max_value: Real, mix: Real) -> Real {
    ((1.0 - mix) * min_value) + (mix * max_value)
}

/// Return a value between 0.0 and 1.0 for a value in an input range
/// 'from' to 'to'.
///
/// Usage:
/// - Find normalized position in a range
/// - Convert absolute values to percentages
/// - Inverse of lerp operation
pub fn inverse_lerp_f64(from: Real, to: Real, value: Real) -> Real {
    (value - from) / (to - from)
}

/// Remap from an 'original' value range to a 'target' value range.
pub fn remap_f64(
    original_from: Real,
    original_to: Real,
    target_from: Real,
    target_to: Real,
    value: Real,
) -> Real {
    let map_to_original_range =
        inverse_lerp_f64(original_from, original_to, value);
    lerp_f64(target_from, target_to, map_to_original_range)
}

fn linear_interpolate_point_y_value_at_value_x(
    value_x: f64,
    point_a_x: f64,
    point_a_y: f64,
    point_b_x: f64,
    point_b_y: f64,
) -> f64 {
    let mix_x = inverse_lerp_f64(point_a_x, point_b_x, value_x);
    let mix_y = lerp_f64(point_a_y, point_b_y, mix_x);
    mix_y
}

pub fn linear_interpolate_y_value_at_value_x(
    value_x: f64,
    point_a_x: f64,
    point_a_y: f64,
    point_b_x: f64,
    point_b_y: f64,
    point_c_x: f64,
    point_c_y: f64,
) -> f64 {
    if value_x < point_b_x {
        linear_interpolate_point_y_value_at_value_x(
            value_x, point_a_x, point_a_y, point_b_x, point_b_y,
        )
    } else if value_x > point_b_x {
        linear_interpolate_point_y_value_at_value_x(
            value_x, point_b_x, point_b_y, point_c_x, point_c_y,
        )
    } else {
        point_b_y
    }
}

#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Interpolation {
    // Nearest,
    Linear,
    QuadraticNUBS,
    CubicNUBS,
    CubicSpline,
}

#[enum_dispatch]
pub trait CurveInterpolator {
    /// Update control points.
    fn set_control_points(
        &self,
        control_points_x: &[f64],
        control_points_y: &[f64],
    );

    /// Update control points X coordinates.
    fn set_control_points_x(&self, control_points_x: &[f64]);

    /// Update control points X coordinates.
    fn set_control_points_y(&self, control_points_y: &[f64]);

    /// Interpolate X coordinate value.
    fn interpolate(&self, value_x: f64) -> f64;
}

#[derive(Debug, Clone)]
pub struct LinearInterpolator {
    control_points_x: RefCell<Vec<f64>>,
    control_points_y: RefCell<Vec<f64>>,
}

impl LinearInterpolator {
    fn new() -> Self {
        Self {
            control_points_x: RefCell::new(Vec::new()),
            control_points_y: RefCell::new(Vec::new()),
        }
    }
}

impl CurveInterpolator for LinearInterpolator {
    fn set_control_points(
        &self,
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) {
        assert_eq!(control_points_x.len(), control_points_y.len());

        let mut x_points = self.control_points_x.borrow_mut();
        let mut y_points = self.control_points_y.borrow_mut();

        x_points.clear();
        y_points.clear();
        x_points.extend_from_slice(control_points_x);
        y_points.extend_from_slice(control_points_y);
    }

    fn set_control_points_x(&self, control_points_x: &[f64]) {
        let mut x_points = self.control_points_x.borrow_mut();
        x_points.clear();
        x_points.extend_from_slice(control_points_x);
    }

    fn set_control_points_y(&self, control_points_y: &[f64]) {
        let mut y_points = self.control_points_y.borrow_mut();
        y_points.clear();
        y_points.extend_from_slice(control_points_y);
    }

    fn interpolate(&self, value_x: f64) -> f64 {
        let x_points = self.control_points_x.borrow();
        let y_points = self.control_points_y.borrow();

        assert_eq!(x_points.len(), y_points.len());

        for i in 0..x_points.len() - 1 {
            if value_x <= x_points[i + 1] {
                if value_x == x_points[i + 1] {
                    return y_points[i + 1];
                }
                return linear_interpolate_point_y_value_at_value_x(
                    value_x,
                    x_points[i],
                    y_points[i],
                    x_points[i + 1],
                    y_points[i + 1],
                );
            }
        }

        *y_points.last().unwrap()
    }
}

/// Generic Non-Uniform B-Spline interpolator with compile-time degree.
///
/// This implementation uses const generics to provide degree-specific
/// B-spline interpolation while maintaining zero runtime overhead.
/// The degree is known at compile time, allowing the compiler to
/// optimize and inline degree-specific code paths.
///
/// Supports:
/// - Degree 2 (Quadratic): C1 continuity, requires at least 3 control points
/// - Degree 3 (Cubic): C2 continuity, requires at least 4 control points
///
/// NUBS solve the fundamental interpolation problem by providing:
/// - **Local control**: Moving one control point affects only nearby
///   curve segments.
/// - **Numerical stability**: Avoids oscillations that plague
///   high-degree polynomial interpolation.
/// - **Smooth curves**: Generates visually seamless curves without
///   angular artifacts.
/// - **Predictable behavior**: Curves remain within the convex hull
///   of control points.
///
/// The implementation uses the Cox-de Boor algorithm for basis
/// function evaluation, which provides O(degree^2) complexity per
/// point and maintains numerical stability through recursive
/// computation that avoids division by zero.
///
/// # Academic References
///
/// - Cox, M.G. (1972): "The Numerical Evaluation of B-Splines", IMA Journal of Applied Mathematics
/// - de Boor, C. (1978): "A Practical Guide to Splines", Springer-Verlag
/// - Piegl, L. & Tiller, W. (1997): "The NURBS Book", Springer-Verlag
///
#[derive(Debug, Clone)]
pub struct NUBSInterpolator<const DEGREE: usize> {
    control_points_x: RefCell<Vec<f64>>,
    control_points_y: RefCell<Vec<f64>>,
    knots: RefCell<Vec<f64>>,
    cache_dirty: Cell<bool>,
}

impl<const DEGREE: usize> NUBSInterpolator<DEGREE> {
    /// Creates a new Non-Uniform B-Spline interpolator with the specified degree.
    pub fn new() -> Self {
        // Compile-time assertion to ensure valid degree.
        assert!(
            DEGREE >= 1 && DEGREE <= 3,
            "NUBS degree must be between 1 and 3"
        );

        Self {
            control_points_x: RefCell::new(Vec::new()),
            control_points_y: RefCell::new(Vec::new()),
            knots: RefCell::new(Vec::new()),
            cache_dirty: Cell::new(true),
        }
    }

    /// Returns the minimum number of control points required for this degree.
    #[inline]
    const fn min_control_points() -> usize {
        DEGREE + 1
    }

    /// Generates a clamped uniform knot vector for B-spline evaluation.
    ///
    /// Clamped knot vectors solve the "endpoint problem" by forcing
    /// B-spline curves to pass through their first and last control
    /// points. This is achieved by repeating boundary knots (degree + 1)
    /// times, which ensures the interpolation matrix remains
    /// well-conditioned and the curve becomes tangent to the control
    /// polygon at endpoints.
    ///
    /// Uniform spacing provides computational simplicity while
    /// maintaining adequate flexibility. Unlike non-uniform
    /// distributions that require complex parameterization
    /// calculations, uniform knots enable efficient evaluation
    /// algorithms and predictable memory access patterns.
    ///
    /// The structure is the same for all degrees:
    /// - First (degree + 1) knots = 0.0.
    /// - Interior knots uniformly spaced.
    /// - Last (degree + 1) knots = 1.0.
    ///
    /// **Example**: For degree 3 NUBS with 6 control points, this outputs:
    /// [0.0, 0.0, 0.0, 0.0, 0.25, 0.5, 0.75, 1.0, 1.0, 1.0, 1.0]
    ///
    /// # Arguments
    ///
    /// * `n_control_points` - Number of control points.
    ///
    /// # Returns
    ///
    /// Vector of knot values normalized to [0, 1] interval for
    /// numerical stability
    fn generate_knot_vector(n_control_points: usize) -> Vec<f64> {
        let n = n_control_points;

        // Mathematical requirement: For n control points and degree
        // p, we need exactly n + p + 1 knots.
        let n_knots = n + DEGREE + 1;
        let mut knots = vec![0.0; n_knots];

        assert!(
            n >= Self::min_control_points(),
            "Need at least {} control points for degree {} Non-Uniform B-Spline, got {}.",
            Self::min_control_points(),
            DEGREE,
            n
        );

        // Clamp the first and last (degree+1) knots to ensure
        // endpoint interpolation.
        //
        // This mathematical trick forces the curve to pass through
        // the first and last control points by making the basis
        // functions equal 1.0 at the boundaries.
        for i in 0..=DEGREE {
            knots[i] = 0.0;
            knots[n_knots - 1 - i] = 1.0;
        }

        // Interior knots uniformly spaced to provide computational
        // efficiency while maintaining curve quality. This creates
        // the parameter intervals that define where each basis
        // function has support.
        let n_interior = n.saturating_sub(DEGREE + 1);
        if n_interior > 0 {
            for i in 1..=n_interior {
                knots[DEGREE + i] = i as f64 / (n_interior + 1) as f64;
            }
        }

        knots
    }

    /// Finds the knot span index containing the given parameter
    /// value.
    ///
    /// Returns the index i such that u is in [knots[i], knots[i+1]).
    /// For clamped B-splines, this will be in the range [DEGREE,
    /// n-1].
    ///
    /// # Arguments
    ///
    /// * `u_coord` - Parameter value in [0, 1]
    /// * `knots` - Knot vector
    /// * `n_control_points` - Number of control points
    ///
    /// # Returns
    ///
    /// Knot span index
    fn find_knot_span(
        u_coord: f64,
        control_point_count: usize,
        knots: &[f64],
    ) -> usize {
        let n = control_point_count;

        // Special case: if u_coord is at the end, return the last
        // valid span.
        if u_coord >= 1.0 - f64::EPSILON {
            return n - 1;
        }

        // Binary search for the knot span.
        //
        // We search in the range [degree, n-1] for the valid spans.
        let mut low = DEGREE;
        let mut high = n - 1;
        while low < high {
            let mid = (low + high) / 2;

            if u_coord < knots[mid + 1] {
                high = mid;
            } else {
                low = mid + 1;
            }
        }

        // At this point, low == high, and u_coord is in [knots[low],
        // knots[low+1]).
        low
    }

    /// Evaluates B-spline basis functions using the Cox-de Boor
    /// recursion algorithm.
    ///
    /// This is the core computational engine that makes B-splines
    /// numerically stable.  The Cox-de Boor algorithm revolutionized
    /// B-spline computation by providing the first numerically stable
    /// evaluation method, replacing unstable divided difference
    /// approaches that accumulated floating-point errors.
    ///
    /// **Local support property**: Each basis function N_{i,p}(u) is
    /// non-zero only on the interval [t_i, t_{i+p+1}]. This means
    /// only (degree + 1) basis functions contribute to any point on
    /// the curve, enabling efficient evaluation.
    ///
    /// The recursive formulation automatically handles edge cases:
    /// - Division by zero is avoided through careful denominator checking.
    /// - Only non-zero basis functions should be computed (local support property).
    /// - Numerical stability is maintained through the recursive structure.
    ///
    /// # Mathematical Foundation
    ///
    /// The Cox-de Boor recursion formula:
    /// ```text
    /// N[i,0](u) = 1 if t[i] <= u < t[i+1], 0 otherwise
    /// N[i,p](u) = ((u - t[i]) / (t[i+p] - t[i])) * N[i,p-1](u)
    ///           + ((t[i+p+1] - u) / (t[i+p+1] - t[i+1])) * N[i+1,p-1](u)
    /// ```
    ///
    /// # Arguments
    ///
    /// * `control_point_index` - Index of the control point for this basis function.
    /// * `degree` - Degree of the basis function (2 for quadratic, 3 for cubic).
    /// * `u_coord` - Parameter value in [0, 1] to evaluate.
    /// * `knots` - Knot vector defining the parameter space.
    ///
    /// # Returns
    ///
    /// Basis function value at the given parameter, guaranteed to be in [0, 1].
    fn basis_function(
        control_point_index: usize,
        degree: usize,
        u_coord: f64,
        knots: &[f64],
    ) -> f64 {
        let cp_index = control_point_index;
        let current_knot = knots[cp_index];
        let next_knot = knots[cp_index + 1];

        // Base case: degree 0 basis functions are indicator
        // functions.
        if degree == 0 {
            // For the last valid basis function when u_coord is at
            // the end, we need to include the right endpoint to
            // handle u_coord = 1.0.
            let in_range = u_coord >= current_knot && u_coord < next_knot;

            // Handle the special case where u_coord = 1.0 at the last
            // knot.
            let u_coord_at_one = next_knot >= 1.0 - f64::EPSILON
                && u_coord >= 1.0 - f64::EPSILON;

            if in_range || u_coord_at_one {
                1.0
            } else {
                0.0
            }
        } else {
            let mut left = 0.0;
            let mut right = 0.0;

            // Left side of the recursion:
            // (u - t[i]) / (t[i+p] - t[i]) * N[i,p-1](u)
            let degree_current_knot = knots[cp_index + degree];
            let denominator1 = degree_current_knot - current_knot;
            if denominator1 > f64::EPSILON {
                left = (u_coord - current_knot) / denominator1
                    * Self::basis_function(
                        cp_index,
                        degree - 1,
                        u_coord,
                        knots,
                    );
            }

            // Right side of the recursion:
            // (t[i+p+1] - u) / (t[i+p+1] - t[i+1]) * N[i+1,p-1](u)
            let degree_next_knot = knots[cp_index + degree + 1];
            let denominator2 = degree_next_knot - next_knot;
            if denominator2 > f64::EPSILON {
                right = (degree_next_knot - u_coord) / denominator2
                    * Self::basis_function(
                        cp_index + 1,
                        degree - 1,
                        u_coord,
                        knots,
                    );
            }

            left + right
        }
    }

    /// Maps x-coordinate values to normalized parameter space using
    /// chord length approximation.
    ///
    /// This function addresses the fundamental challenge of
    /// parameterizing curves: how to map the irregular spacing of
    /// control points in physical space to the uniform parameter
    /// space [0, 1] required by B-spline evaluation.
    ///
    /// **Current implementation**: Uses simple linear mapping
    /// (inverse lerp) as a rough approximation to chord length
    /// parameterization. While not true chord length, this preserves
    /// relative spacing better than uniform parameterization.
    ///
    /// # Arguments
    ///
    /// * `value_x` - X-coordinate to map to parameter space.
    /// * `control_points_x` - Array of control point x-coordinates (must be sorted).
    ///
    /// # Returns
    ///
    /// Parameter value in [0, 1] corresponding to the input x-coordinate.
    fn value_to_u_coordinate(value_x: f64, control_points_x: &[f64]) -> f64 {
        if control_points_x.is_empty() {
            return 0.0;
        }

        let first_x = control_points_x[0];
        let last_x = control_points_x[control_points_x.len() - 1];

        // Clamp to parameter bounds.
        if value_x <= first_x {
            0.0
        } else if value_x >= last_x {
            1.0
        } else {
            // Linear approximation to chord length parameterization.
            //
            // This provides a simple but effective mapping that
            // preserves the relative spacing of control points in
            // parameter space.
            inverse_lerp_f64(first_x, last_x, value_x)
        }
    }

    fn update_cache(&self) {
        let x_points = self.control_points_x.borrow();

        // Generate clamped uniform knot vector to ensure endpoint
        // interpolation and provide computational stability.
        let new_knots = Self::generate_knot_vector(x_points.len());
        drop(x_points);

        *self.knots.borrow_mut() = new_knots;
        self.cache_dirty.set(false);
    }
}

impl<const DEGREE: usize> CurveInterpolator for NUBSInterpolator<DEGREE> {
    fn set_control_points(
        &self,
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) {
        assert_eq!(control_points_x.len(), control_points_y.len());
        assert!(
            control_points_x.len() >= Self::min_control_points(),
            "Need at least {} control points for degree {} Non-Uniform B-Spline.",
            Self::min_control_points(),
            DEGREE
        );

        let mut x_points = self.control_points_x.borrow_mut();
        let mut y_points = self.control_points_y.borrow_mut();

        x_points.clear();
        y_points.clear();
        x_points.extend_from_slice(control_points_x);
        y_points.extend_from_slice(control_points_y);

        self.cache_dirty.set(true);
    }

    fn set_control_points_x(&self, control_points_x: &[f64]) {
        let mut x_points = self.control_points_x.borrow_mut();
        x_points.clear();
        x_points.extend_from_slice(control_points_x);
        self.cache_dirty.set(true);
    }

    fn set_control_points_y(&self, control_points_y: &[f64]) {
        let mut y_points = self.control_points_y.borrow_mut();
        y_points.clear();
        y_points.extend_from_slice(control_points_y);
        self.cache_dirty.set(true);
    }

    /// Interpolates a y-value for the given x-coordinate using NUBS
    /// curves.
    ///
    /// # Arguments
    ///
    /// * `value_x` - X-coordinate to interpolate
    /// * `control_points_x` - X-coordinates of control points (must be sorted ascending)
    /// * `control_points_y` - Y-coordinates of control points (same length as x array)
    ///
    /// # Returns
    ///
    /// Interpolated y-value at the specified x-coordinate
    fn interpolate(&self, value_x: f64) -> f64 {
        let x_points = self.control_points_x.borrow();
        if x_points.is_empty() {
            return 0.0;
        }
        drop(x_points); // Release borrow early.

        if self.cache_dirty.get() {
            self.update_cache();
        }

        let x_points = self.control_points_x.borrow();
        let y_points = self.control_points_y.borrow();
        let knots = self.knots.borrow();

        // Find the knot span containing u_coord This allows us to
        // evaluate only the (degree + 1) non-zero basis functions.
        let n = x_points.len();
        let u_coord = Self::value_to_u_coordinate(value_x, &x_points);
        let span = Self::find_knot_span(u_coord, x_points.len(), &knots);

        // Evaluate B-spline using only the non-zero basis functions.
        //
        // Due to local support, only basis functions [span-degree,
        // span] are non-zero.
        let mut result = 0.0;
        let start_idx = span.saturating_sub(DEGREE);
        let end_idx = span.min(n - 1);

        for i in start_idx..=end_idx {
            let basis = Self::basis_function(i, DEGREE, u_coord, &knots);
            result += basis * y_points[i];
        }

        result
    }
}

// Type aliases for specific degrees.
pub type QuadraticNUBSInterpolator = NUBSInterpolator<2>;
pub type CubicNUBSInterpolator = NUBSInterpolator<3>;

/// Cubic coefficients for a single spline segment.
#[derive(Debug, Clone, Copy)]
struct CubicCoefficients {
    a: f64, // coefficient of (x-xi)^3
    b: f64, // coefficient of (x-xi)^2
    c: f64, // coefficient of (x-xi)
    d: f64, // constant term
}

/// Natural cubic spline interpolator that provides smooth,
/// shape-preserving interpolation for data points with excellent
/// computational performance.
///
/// Cubic splines minimize "bending energy" by setting second
/// derivatives to zero at endpoints, creating natural-looking curves
/// that behave like elastic beams with free ends. This approach
/// provides predictable extrapolation and prevents artificial
/// oscillations beyond data ranges.
///
/// **Performance characteristics:**
/// - O(n) setup cost to solve tridiagonal system for second derivatives.
/// - O(1) evaluation per point after binary search to locate segment.
/// - 2-3x faster evaluation than B-spline methods for most applications.
///
/// **Best suited for:** Scientific visualization, time series data,
/// real-time applications requiring smooth animation curves, and any
/// scenario prioritizing evaluation speed.
///
/// **References:**
/// - Spline interpolation theory: https://en.wikipedia.org/wiki/Spline_interpolation
/// - Numerical implementation: "Numerical Recipes" by Press et al.
#[derive(Debug, Clone)]
pub struct CubicSplineInterpolator {
    control_points_x: RefCell<Vec<f64>>,
    control_points_y: RefCell<Vec<f64>>,
    coefficients: RefCell<Vec<CubicCoefficients>>,
    cache_dirty: Cell<bool>,
}

impl CubicSplineInterpolator {
    fn new() -> Self {
        Self {
            control_points_x: RefCell::new(Vec::new()),
            control_points_y: RefCell::new(Vec::new()),
            coefficients: RefCell::new(Vec::new()),
            cache_dirty: Cell::new(true),
        }
    }

    /// Solves tridiagonal linear systems using the Thomas algorithm
    /// in O(n) time.
    ///
    /// The tridiagonal structure emerges naturally from cubic spline
    /// continuity requirements: each interior point needs C0, C1, and
    /// C2 continuity, creating equations involving only three
    /// adjacent second derivatives. This mathematical structure
    /// enables dramatic performance improvements over general matrix
    /// methods (O(n) vs O(n^3)).
    ///
    /// **Algorithm details:** Forward sweep eliminates sub-diagonal,
    /// back substitution solves for unknowns. This is numerically
    /// stable for diagonally dominant matrices (typical in spline
    /// problems).
    ///
    /// **Why this matters:** The tridiagonal system isn't just
    /// computationally efficient - it's numerically well-conditioned
    /// for most practical problems, ensuring stable solutions even
    /// with challenging data distributions.
    fn solve_tridiagonal(
        a: &[f64], // Sub-diagonal (length n-1)
        b: &[f64], // Main diagonal (length n)
        c: &[f64], // Super-diagonal (length n-1)
        d: &[f64], // Right-hand side (length n)
    ) -> Vec<f64> {
        let n = b.len();
        let mut c_prime = vec![0.0; n];
        let mut d_prime = vec![0.0; n];
        let mut x = vec![0.0; n];

        // Forward sweep: eliminate sub-diagonal elements.
        c_prime[0] = c[0] / b[0];
        d_prime[0] = d[0] / b[0];

        for i in 1..n {
            let denom = b[i] - a[i - 1] * c_prime[i - 1];
            c_prime[i] = if i < n - 1 { c[i] / denom } else { 0.0 };
            d_prime[i] = (d[i] - a[i - 1] * d_prime[i - 1]) / denom;
        }

        // Back substitution: solve for unknowns from bottom up.
        x[n - 1] = d_prime[n - 1];
        for i in (0..n - 1).rev() {
            x[i] = d_prime[i] - c_prime[i] * x[i + 1];
        }

        x
    }

    /// Validates input data to prevent mathematical instabilities and
    /// undefined behavior.
    ///
    /// Cubic splines require strictly increasing x-values because the
    /// mathematical formulation depends on well-defined intervals
    /// between points. Duplicate or reversed x-values would create
    /// division by zero or negative intervals, breaking the
    /// algorithm's foundation.
    fn validate_input(
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) -> Result<(), &'static str> {
        if control_points_x.len() != control_points_y.len() {
            return Err("X and Y arrays must have the same length");
        }

        if control_points_x.len() < 2 {
            return Err("Need at least 2 control points");
        }

        // Check for duplicate x values.
        for i in 0..control_points_x.len() - 1 {
            if (control_points_x[i + 1] - control_points_x[i]).abs() < 1e-10 {
                return Err("Duplicate or near-duplicate x values detected");
            }
        }

        // Check that x values are sorted.
        for i in 0..control_points_x.len() - 1 {
            if control_points_x[i] > control_points_x[i + 1] {
                return Err("X values must be sorted in ascending order");
            }
        }

        Ok(())
    }

    /// Calculates cubic polynomial coefficients by first computing
    /// second derivatives.
    ///
    /// This approach exploits a fundamental mathematical insight: for
    /// cubic polynomials, the second derivative is linear between
    /// endpoints. By solving for second derivatives first using
    /// natural boundary conditions (S''(x_0) = S''(x_n) = 0), we
    /// transform a complex interpolation problem into a simple linear
    /// system.
    ///
    /// **Mathematical elegance:** Natural boundary conditions
    /// minimize bending energy, ensuring the smoothest possible curve
    /// through the data points while providing predictable linear
    /// extrapolation beyond the data range.
    ///
    /// **Returns:** Tuple of cubic coefficients (a, b, c, d) for each
    /// segment where:
    /// S(x) = a*(x-x_i)^3 + b*(x-x_i)^2 + c*(x-x_i) + d
    fn calculate_coefficients(
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) -> Result<Vec<CubicCoefficients>, &'static str> {
        Self::validate_input(control_points_x, control_points_y)?;

        let n = control_points_x.len() - 1;
        if n < 1 {
            return Ok(vec![]);
        }

        let mut coefficients = Vec::with_capacity(n);

        // Calculate h (differences in x) and slopes.
        let mut h = vec![0.0; n];
        let mut slopes = vec![0.0; n];
        for i in 0..n {
            h[i] = control_points_x[i + 1] - control_points_x[i];
            // Ensure we have positive intervals between points.
            assert!(h[i].abs() > f64::EPSILON);
            slopes[i] = (control_points_y[i + 1] - control_points_y[i]) / h[i];
        }

        if n == 1 {
            // Only two points - use linear interpolation (degenerate cubic).
            coefficients.push(CubicCoefficients {
                a: 0.0,
                b: 0.0,
                c: slopes[0],
                d: control_points_y[0],
            });
            return Ok(coefficients);
        }

        // Initialize the second derivatives array.
        let mut m = vec![0.0; n + 1];

        // Natural spline boundary conditions: zero second derivative
        // at endpoints. This creates the "natural" behavior of a
        // physical beam.
        m[0] = 0.0;
        m[n] = 0.0;

        if n > 1 {
            // Set up the tridiagonal system for INTERIOR second
            // derivatives.
            //
            // We only solve for interior points since boundary values
            // are fixed.
            let system_size = n - 1;

            if system_size == 1 {
                // Special case: only one interior point (3 control
                // points total).
                //
                // Direct solution for a single equation.
                m[1] = 3.0 * (slopes[1] - slopes[0]) / (2.0 * (h[0] + h[1]));
            } else {
                // General case: multiple interior points require
                // tridiagonal solve.
                let mut a = vec![0.0; system_size - 1]; // sub-diagonal.
                let mut b = vec![0.0; system_size]; // main diagonal.
                let mut c = vec![0.0; system_size - 1]; // super-diagonal.
                let mut d = vec![0.0; system_size]; // right-hand side.

                // Build tridiagonal system from continuity equations:
                // h[i-1]*m[i-1] + 2*(h[i-1]+h[i])*m[i] + h[i]*m[i+1] = 6*(slopes[i]-slopes[i-1])

                // First row (for m[1]).
                b[0] = 2.0 * (h[0] + h[1]);
                c[0] = h[1];
                d[0] = 6.0 * (slopes[1] - slopes[0]);

                // Middle rows.
                for i in 1..system_size - 1 {
                    a[i - 1] = h[i];
                    b[i] = 2.0 * (h[i] + h[i + 1]);
                    c[i] = h[i + 1];
                    d[i] = 6.0 * (slopes[i + 1] - slopes[i]);
                }

                // Last row (for m[n-1]).
                a[system_size - 2] = h[system_size - 1];
                b[system_size - 1] =
                    2.0 * (h[system_size - 1] + h[system_size]);
                d[system_size - 1] =
                    6.0 * (slopes[system_size] - slopes[system_size - 1]);

                // Solve the tridiagonal system.
                let interior_m = Self::solve_tridiagonal(&a, &b, &c, &d);

                // Copy the interior values to the full m array.
                for i in 0..system_size {
                    m[i + 1] = interior_m[i];
                }
            }
        }

        // Calculate the coefficients for each segment using the
        // standard cubic spline formulas.
        //
        // These formulas ensure C0, C1, and C2 continuity at all
        // interior points.
        for i in 0..n {
            let hi = h[i];
            let yi = control_points_y[i];
            let yi1 = control_points_y[i + 1];
            let mi = m[i];
            let mi1 = m[i + 1];

            coefficients.push(CubicCoefficients {
                a: (mi1 - mi) / (6.0 * hi),
                b: mi / 2.0,
                c: (yi1 - yi) / hi - hi * (mi1 + 2.0 * mi) / 6.0,
                d: yi,
            });
        }

        Ok(coefficients)
    }

    fn update_cache(&self) {
        let x_points = self.control_points_x.borrow();
        let y_points = self.control_points_y.borrow();

        Self::validate_input(&x_points, &y_points).unwrap();

        // Calculate coefficients for all segments.
        let new_coefficients = Self::calculate_coefficients(
            &x_points, &y_points,
        )
        .expect(
            "Coefficients must compute; validation should prevent failures.",
        );

        drop(x_points);
        drop(y_points);

        *self.coefficients.borrow_mut() = new_coefficients;
        self.cache_dirty.set(false);
    }
}

impl CurveInterpolator for CubicSplineInterpolator {
    fn set_control_points(
        &self,
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) {
        assert_eq!(control_points_x.len(), control_points_y.len());
        assert!(
            control_points_x.len() >= 2,
            "Need at least 2 control points for Cubic Spline."
        );

        let mut x_points = self.control_points_x.borrow_mut();
        let mut y_points = self.control_points_y.borrow_mut();

        x_points.clear();
        y_points.clear();
        x_points.extend_from_slice(control_points_x);
        y_points.extend_from_slice(control_points_y);

        self.cache_dirty.set(true);
    }

    fn set_control_points_x(&self, control_points_x: &[f64]) {
        let mut x_points = self.control_points_x.borrow_mut();
        x_points.clear();
        x_points.extend_from_slice(control_points_x);
        self.cache_dirty.set(true);
    }

    fn set_control_points_y(&self, control_points_y: &[f64]) {
        let mut y_points = self.control_points_y.borrow_mut();
        y_points.clear();
        y_points.extend_from_slice(control_points_y);
        self.cache_dirty.set(true);
    }

    /// Interpolates a y-value for the given x-coordinate using cubic
    /// B-spline curves.
    fn interpolate(&self, value_x: f64) -> f64 {
        let x_points = self.control_points_x.borrow();
        let n = x_points.len();

        // Handle edge cases.
        if n == 0 {
            return 0.0;
        }
        if n == 1 {
            let y_points = self.control_points_y.borrow();
            return y_points[0];
        }

        if value_x <= x_points[0] {
            let y_points = self.control_points_y.borrow();
            return y_points[0];
        }
        if value_x >= x_points[n - 1] {
            let y_points = self.control_points_y.borrow();
            return y_points[n - 1];
        }
        drop(x_points); // Release early.

        if self.cache_dirty.get() {
            self.update_cache();
        }

        let x_points = self.control_points_x.borrow();
        let coefficients = self.coefficients.borrow();

        // Binary search to find the correct segment.
        //
        // Invariant:
        // control_points_x[left] <= value_x < control_points_x[right]
        let mut left = 0;
        let mut right = n - 1;
        while left < right - 1 {
            let mid = (left + right) / 2;
            if value_x < x_points[mid] {
                right = mid;
            } else {
                left = mid;
            }
        }
        let segment_idx = left;

        // Evaluate the cubic polynomial for this segment.
        let dx = value_x - x_points[segment_idx];
        let coef = &coefficients[segment_idx];
        ((coef.a * dx + coef.b) * dx + coef.c) * dx + coef.d
    }
}

#[enum_dispatch(CurveInterpolator)]
#[derive(Debug, Clone)]
pub enum Interpolator {
    Linear(LinearInterpolator),
    QuadraticNUBS(QuadraticNUBSInterpolator),
    CubicNUBS(CubicNUBSInterpolator),
    CubicSpline(CubicSplineInterpolator),
}

impl Interpolator {
    /// Creates an interpolator (without control points).
    pub fn from_method(method: Interpolation) -> Self {
        match method {
            Interpolation::Linear => Self::Linear(LinearInterpolator::new()),
            Interpolation::QuadraticNUBS => {
                Self::QuadraticNUBS(QuadraticNUBSInterpolator::new())
            }
            Interpolation::CubicNUBS => {
                Self::CubicNUBS(CubicNUBSInterpolator::new())
            }
            Interpolation::CubicSpline => {
                Self::CubicSpline(CubicSplineInterpolator::new())
            }
        }
    }
}

pub fn evaluate_curve_points(
    x_values: &[f64],
    control_points_x: &[f64],
    control_points_y: &[f64],
    interpolation_method: Interpolation,
) -> Vec<(f64, f64)> {
    let interpolator = Interpolator::from_method(interpolation_method);
    interpolator.set_control_points(control_points_x, control_points_y);

    x_values
        .iter()
        .map(|&x| {
            let y = interpolator.interpolate(x);
            (x, y)
        })
        .collect()
}
