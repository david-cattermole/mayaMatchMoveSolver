//
// Copyright (C) 2024 David Cattermole.
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
pub enum InterpolationMethod {
    // Nearest,
    Linear,
    CubicNUBS,
    CubicSpline,
}

#[enum_dispatch]
pub trait CurveInterpolator {
    fn interpolate(
        &self,
        value_x: f64,
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) -> f64;
}

#[derive(Debug, Clone, Copy)]
pub struct LinearInterpolator;

impl LinearInterpolator {
    pub fn new() -> Self {
        Self
    }
}

impl CurveInterpolator for LinearInterpolator {
    fn interpolate(
        &self,
        value_x: f64,
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) -> f64 {
        debug_assert_eq!(control_points_x.len(), control_points_y.len());

        for i in 0..control_points_x.len() - 1 {
            if value_x <= control_points_x[i + 1] {
                if value_x == control_points_x[i + 1] {
                    return control_points_y[i + 1];
                }
                return linear_interpolate_point_y_value_at_value_x(
                    value_x,
                    control_points_x[i],
                    control_points_y[i],
                    control_points_x[i + 1],
                    control_points_y[i + 1],
                );
            }
        }

        *control_points_y.last().unwrap()
    }
}

#[derive(Debug, Clone, Copy)]
pub struct CubicNUBSInterpolator;

impl CubicNUBSInterpolator {
    pub fn new() -> Self {
        Self
    }

    fn cubic_basis_function(t: f64, i: usize) -> f64 {
        let t = t.clamp(0.0, 1.0);
        match i {
            0 => (1.0 - t).powi(3) / 6.0,
            1 => (3.0 * t.powi(3) - 6.0 * t.powi(2) + 4.0) / 6.0,
            2 => (-3.0 * t.powi(3) + 3.0 * t.powi(2) + 3.0 * t + 1.0) / 6.0,
            3 => t.powi(3) / 6.0,
            _ => 0.0,
        }
    }

    fn extrapolate_control_point_y_value(
        p1_x: f64,
        p1_y: f64,
        p2_x: f64,
        p2_y: f64,
        target_x: f64,
    ) -> f64 {
        let dx = p2_x - p1_x;
        if dx.abs() < f64::EPSILON {
            return p1_y;
        }
        let slope = (p2_y - p1_y) / dx;
        p1_y + slope * (target_x - p1_x)
    }

    // Get 4 control points for a segment, handling boundaries with
    // extrapolation.
    fn get_control_points(
        segment_idx: usize,
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) -> [(f64, f64); 4] {
        let n = control_points_x.len();
        let mut points = [(0.0, 0.0); 4];

        for i in 0..4 {
            let idx = segment_idx as isize + (i as isize - 1);

            if idx < 0 {
                // Extrapolate before the start.
                let x = control_points_x[0]
                    + idx as f64 * (control_points_x[1] - control_points_x[0]);
                let y = Self::extrapolate_control_point_y_value(
                    control_points_x[0],
                    control_points_y[0],
                    control_points_x[1],
                    control_points_y[1],
                    x,
                );
                points[i] = (x, y);
            } else if idx >= n as isize {
                // Extrapolate after the end.
                let last_idx = n - 1;
                let x = control_points_x[last_idx]
                    + (idx as f64 - last_idx as f64)
                        * (control_points_x[last_idx]
                            - control_points_x[last_idx - 1]);
                let y = Self::extrapolate_control_point_y_value(
                    control_points_x[last_idx - 1],
                    control_points_y[last_idx - 1],
                    control_points_x[last_idx],
                    control_points_y[last_idx],
                    x,
                );
                points[i] = (x, y);
            } else {
                // Within bounds.
                points[i] = (
                    control_points_x[idx as usize],
                    control_points_y[idx as usize],
                );
            }
        }

        points
    }
}

impl CurveInterpolator for CubicNUBSInterpolator {
    fn interpolate(
        &self,
        value_x: f64,
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) -> f64 {
        debug_assert_eq!(control_points_x.len(), control_points_y.len());
        debug_assert!(
            control_points_x.len() >= 2,
            "Need at least 2 control points"
        );

        // Find the appropriate segment.
        let mut segment_idx = 0;
        for i in 0..control_points_x.len() - 1 {
            if value_x <= control_points_x[i + 1] {
                segment_idx = i;
                break;
            }
        }

        // Get the 4 control points needed for this segment.
        let control_points = Self::get_control_points(
            segment_idx,
            control_points_x,
            control_points_y,
        );

        // Calculate local parameter t.
        let t = if segment_idx + 1 < control_points_x.len() {
            (value_x - control_points_x[segment_idx])
                / (control_points_x[segment_idx + 1]
                    - control_points_x[segment_idx])
        } else {
            1.0
        };

        // Calculate the interpolated value using the basis functions.
        let mut result = 0.0;
        for i in 0..4 {
            result += Self::cubic_basis_function(t, i) * control_points[i].1;
        }

        result
    }
}

#[derive(Debug, Clone, Copy)]
pub struct CubicSplineInterpolator;

impl CubicSplineInterpolator {
    pub fn new() -> Self {
        Self
    }

    // Calculate the coefficients for cubic spline interpolation.
    fn calculate_coefficients(
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) -> Vec<(f64, f64, f64, f64)> {
        let n = control_points_x.len() - 1;
        let mut coefficients = vec![(0.0, 0.0, 0.0, 0.0); n];

        if n < 1 {
            return coefficients;
        }

        // Calculate h (differences in x) and slopes.
        let mut h = vec![0.0; n];
        let mut slopes = vec![0.0; n];
        for i in 0..n {
            h[i] = control_points_x[i + 1] - control_points_x[i];
            slopes[i] = (control_points_y[i + 1] - control_points_y[i]) / h[i];
        }

        // Set up the tridiagonal system for second derivatives.
        let mut a = vec![0.0; n - 1];
        let mut b = vec![0.0; n - 1];
        let mut c = vec![0.0; n - 1];
        let mut r = vec![0.0; n - 1];

        for i in 0..n - 1 {
            a[i] = h[i];
            b[i] = 2.0 * (h[i] + h[i + 1]);
            c[i] = h[i + 1];
            r[i] = 3.0 * (slopes[i + 1] - slopes[i]);
        }

        // Solve the tridiagonal system using Thomas algorithm.
        let mut m = vec![0.0; n + 1];
        let mut l = vec![0.0; n - 1];
        let mut u = vec![0.0; n - 1];
        let mut z = vec![0.0; n - 1];

        l[0] = b[0];
        u[0] = c[0] / l[0];
        z[0] = r[0] / l[0];

        for i in 1..n - 1 {
            l[i] = b[i] - a[i] * u[i - 1];
            u[i] = c[i] / l[i];
            z[i] = (r[i] - a[i] * z[i - 1]) / l[i];
        }

        m[n] = 0.0;
        m[0] = 0.0;

        for i in (1..n).rev() {
            m[i] = z[i - 1] - u[i - 1] * m[i + 1];
        }

        // Calculate the coefficients for each segment.
        for i in 0..n {
            let hi = h[i];
            let yi = control_points_y[i];
            let yi1 = control_points_y[i + 1];
            let mi = m[i];
            let mi1 = m[i + 1];

            coefficients[i] = (
                (mi1 - mi) / (6.0 * hi),
                mi / 2.0,
                (yi1 - yi) / hi - hi * (mi1 + 2.0 * mi) / 6.0,
                yi,
            );
        }

        coefficients
    }
}

impl CurveInterpolator for CubicSplineInterpolator {
    fn interpolate(
        &self,
        value_x: f64,
        control_points_x: &[f64],
        control_points_y: &[f64],
    ) -> f64 {
        debug_assert_eq!(control_points_x.len(), control_points_y.len());
        debug_assert!(
            control_points_x.len() >= 2,
            "Need at least 2 control points"
        );

        // Handle edge cases.
        if value_x <= control_points_x[0] {
            return control_points_y[0];
        }
        if value_x >= *control_points_x.last().unwrap() {
            return *control_points_y.last().unwrap();
        }

        // Find the appropriate segment.
        let mut segment_idx = 0;
        for i in 0..control_points_x.len() - 1 {
            if value_x <= control_points_x[i + 1] {
                segment_idx = i;
                break;
            }
        }

        // Calculate coefficients for all segments.
        let coefficients =
            Self::calculate_coefficients(control_points_x, control_points_y);

        // Calculate the local x value.
        let dx = value_x - control_points_x[segment_idx];
        let (a, b, c, d) = coefficients[segment_idx];

        // Evaluate the cubic polynomial.
        ((a * dx + b) * dx + c) * dx + d
    }
}

#[enum_dispatch(CurveInterpolator)]
#[derive(Debug, Clone)]
pub enum Interpolator {
    Linear(LinearInterpolator),
    CubicNUBS(CubicNUBSInterpolator),
    CubicSpline(CubicSplineInterpolator),
}

impl Interpolator {
    pub fn from_method(method: InterpolationMethod) -> Self {
        match method {
            InterpolationMethod::Linear => {
                Self::Linear(LinearInterpolator::new())
            }
            InterpolationMethod::CubicNUBS => {
                Self::CubicNUBS(CubicNUBSInterpolator::new())
            }
            InterpolationMethod::CubicSpline => {
                Self::CubicSpline(CubicSplineInterpolator::new())
            }
        }
    }
}

pub fn evaluate_curve_points(
    x_values: &[f64],
    control_points_x: &[f64],
    control_points_y: &[f64],
    interpolation_method: InterpolationMethod,
) -> Vec<(f64, f64)> {
    let interpolator = Interpolator::from_method(interpolation_method);
    x_values
        .iter()
        .map(|&x| {
            let y =
                interpolator.interpolate(x, control_points_x, control_points_y);
            (x, y)
        })
        .collect()
}
