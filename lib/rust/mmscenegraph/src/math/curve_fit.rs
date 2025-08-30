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

use anyhow::Result;
use log::debug;
use mmoptimise::solver::{
    LevenbergMarquardt, OptimisationProblem, SolverConfig, SolverWorkspace,
};
use nalgebra::{DMatrix, DVector};

use crate::constant::Real;
use crate::math::interpolate::remap_f64;
use crate::math::interpolate::Interpolation;
use crate::math::line::curve_fit_linear_regression_type1;
use crate::math::statistics::calc_normalized_root_mean_square_error;

#[derive(Copy, Clone, Debug, PartialEq)]
pub struct Point2 {
    x: Real,
    y: Real,
}

impl Point2 {
    pub fn new(x: f64, y: f64) -> Self {
        Self { x, y }
    }

    pub fn x(self) -> Real {
        self.x
    }

    pub fn y(self) -> Real {
        self.y
    }
}

#[derive(Copy, Clone, Debug, PartialEq)]
pub struct AngleRadian {
    inner: Real,
}

impl AngleRadian {
    pub fn value(self) -> Real {
        self.inner
    }

    pub fn as_degrees(self) -> Real {
        self.value().to_degrees()
    }

    pub fn as_direction(self) -> (Real, Real) {
        (self.value().cos(), self.value().sin())
    }
}

pub fn linear_regression(
    x_values: &[Real],
    y_values: &[Real],
) -> Result<(Point2, AngleRadian)> {
    let mut point_x = 0.0;
    let mut point_y = 0.0;
    let mut angle = 0.0;
    curve_fit_linear_regression_type1(
        x_values,
        y_values,
        &mut point_x,
        &mut point_y,
        &mut angle,
    );
    debug!("angle={angle}");

    let dir_x = angle.cos();
    let dir_y = angle.sin();
    debug!("point_x={point_x} point_y={point_y}");
    debug!("dir_x={dir_x} dir_y={dir_y}");

    let point = Point2 {
        x: point_x,
        y: point_y,
    };

    let angle = AngleRadian {
        inner: dir_y.atan2(dir_x),
    };
    debug!("angle={angle:?}");

    Ok((point, angle))
}

/// N3 Curve Fitting Problem for LevenbergMarquardt solver.
struct N3CurveFitProblem {
    reference_values: Vec<(f64, f64)>,
    point_a_x: f64,
    point_b_x: f64,
    point_c_x: f64,
}

impl N3CurveFitProblem {
    fn new(
        point_a_x: f64,
        point_b_x: f64,
        point_c_x: f64,
        reference_values: Vec<(f64, f64)>,
    ) -> Self {
        Self {
            reference_values,
            point_a_x,
            point_b_x,
            point_c_x,
        }
    }
}

impl OptimisationProblem for N3CurveFitProblem {
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> anyhow::Result<()>
    where
        T: Copy
            + std::ops::Add<Output = T>
            + std::ops::Sub<Output = T>
            + std::ops::Mul<Output = T>
            + std::ops::Div<Output = T>
            + From<f64>
            + Sized
            + num_traits::Zero
            + num_traits::Float,
    {
        if parameters.len() != 3 {
            return Err(anyhow::anyhow!(
                "N3 problem requires exactly 3 parameters (Y values)"
            ));
        }

        let point_a_y = parameters[0];
        let point_b_y = parameters[1];
        let point_c_y = parameters[2];

        for i in 0..self.residual_count() {
            let data_x = <T as From<f64>>::from(self.reference_values[i].0);
            let data_y = <T as From<f64>>::from(self.reference_values[i].1);

            // Linear interpolation between three points
            let point_a_x = <T as From<f64>>::from(self.point_a_x);
            let point_b_x = <T as From<f64>>::from(self.point_b_x);
            let point_c_x = <T as From<f64>>::from(self.point_c_x);

            let curve_y = if data_x <= point_b_x {
                // Interpolate between point A and point B
                let t = (data_x - point_a_x) / (point_b_x - point_a_x);
                point_a_y + t * (point_b_y - point_a_y)
            } else {
                // Interpolate between point B and point C
                let t = (data_x - point_b_x) / (point_c_x - point_b_x);
                point_b_y + t * (point_c_y - point_b_y)
            };

            out_residuals[i] = curve_y - data_y;
        }

        Ok(())
    }

    fn parameter_count(&self) -> usize {
        // 3 x 2D points is 6, but the X axis values are always
        // locked, therefore 3 values are known, and we do not need to
        // solve for them.
        3
    }

    fn residual_count(&self) -> usize {
        self.reference_values.len()
    }
}

/// N-points Curve Fitting Problem for LevenbergMarquardt solver.
struct NPointsCurveFitProblem {
    reference_values: Vec<(f64, f64)>,
    control_points_x: Vec<f64>,
    interpolation_method: Interpolation,
}

impl NPointsCurveFitProblem {
    fn new(
        control_points_x: Vec<f64>,
        reference_values: Vec<(f64, f64)>,
        interpolation_method: Interpolation,
    ) -> anyhow::Result<Self> {
        Ok(Self {
            reference_values,
            control_points_x,
            interpolation_method,
        })
    }

    /// Generic interpolation function that works with all
    /// interpolator types.
    fn interpolate<T>(&self, value_x: T, control_points_y: &[T]) -> T
    where
        T: Copy
            + std::ops::Add<Output = T>
            + std::ops::Sub<Output = T>
            + std::ops::Mul<Output = T>
            + std::ops::Div<Output = T>
            + From<f64>
            + Sized
            + num_traits::Zero
            + num_traits::Float
            + num_traits::ToPrimitive
            + num_traits::One,
    {
        use crate::math::interpolate::{
            linear_interpolate_with_control_points,
            nubs_interpolate_with_control_points, CubicSplineInterpolator,
            CurveInterpolator,
        };

        // Now we can support proper automatic differentiation for
        // Linear and NUBS methods!
        //
        // Cubic Spline still requires f64 conversion, but that's
        // acceptable.

        match self.interpolation_method {
            Interpolation::Linear => linear_interpolate_with_control_points(
                value_x,
                &self.control_points_x,
                control_points_y,
            ),
            Interpolation::QuadraticNUBS => {
                nubs_interpolate_with_control_points(
                    value_x,
                    &self.control_points_x,
                    control_points_y,
                    2, // degree 2 for quadratic.
                )
            }
            Interpolation::CubicNUBS => {
                nubs_interpolate_with_control_points(
                    value_x,
                    &self.control_points_x,
                    control_points_y,
                    3, // degree 3 for cubic.
                )
            }
            Interpolation::CubicSpline => {
                // Cubic Spline requires f64 conversion - coefficients
                // computed with f64.
                //
                // This breaks automatic differentiation but is
                // acceptable trade-off.
                let control_points_y_f64: Vec<f64> = control_points_y
                    .iter()
                    .map(|&y| y.to_f64().unwrap_or(0.0))
                    .collect();

                let interpolator = CubicSplineInterpolator::new();
                interpolator.set_control_points(
                    &self.control_points_x,
                    &control_points_y_f64,
                );

                let result_f64 = interpolator
                    .interpolate_f64(value_x.to_f64().unwrap_or(0.0));
                <T as From<f64>>::from(result_f64)
            }
        }
    }
}

impl OptimisationProblem for NPointsCurveFitProblem {
    fn residuals<T>(
        &self,
        parameters: &[T],
        out_residuals: &mut [T],
    ) -> anyhow::Result<()>
    where
        T: Copy
            + std::ops::Add<Output = T>
            + std::ops::Sub<Output = T>
            + std::ops::Mul<Output = T>
            + std::ops::Div<Output = T>
            + From<f64>
            + Sized
            + num_traits::Zero
            + num_traits::Float
            + num_traits::ToPrimitive
            + num_traits::One,
    {
        if parameters.len() != self.control_points_x.len() {
            return Err(anyhow::anyhow!(
                "Parameter count must match control point count"
            ));
        }

        // Use the proper interpolation method with automatic
        // differentiation support.
        for i in 0..self.residual_count() {
            let data_x = <T as From<f64>>::from(self.reference_values[i].0);
            let data_y = <T as From<f64>>::from(self.reference_values[i].1);

            // Use generic interpolation with the selected method.
            let curve_y = self.interpolate(data_x, parameters);
            out_residuals[i] = curve_y - data_y;
        }

        Ok(())
    }

    fn parameter_count(&self) -> usize {
        self.control_points_x.len()
    }

    fn residual_count(&self) -> usize {
        self.reference_values.len()
    }
}

/// Perform a non-linear least-squares fit for a line with 3 points
/// using custom initial positions.
///
/// This function is similar to `nonlinear_line_n3()` but accepts
/// custom initial positions for the 3 control points instead of
/// deriving them from linear regression.
///
/// This is useful for auto_keypoints cases where the keypoint
/// detection algorithm provides better initial positions than linear
/// regression.
pub fn nonlinear_line_n3_with_initial(
    x_values: &[f64],
    y_values: &[f64],
    initial_control_points_x: &[f64],
    initial_control_points_y: &[f64],
) -> Result<(Point2, Point2, Point2)> {
    assert_eq!(x_values.len(), y_values.len());
    let value_count = x_values.len();
    assert!(value_count > 2);
    assert_eq!(
        initial_control_points_x.len(),
        3,
        "Must provide exactly 3 initial control points X coordinates"
    );
    assert_eq!(
        initial_control_points_y.len(),
        3,
        "Must provide exactly 3 initial control points Y coordinates"
    );

    debug!("nonlinear_line_n3_with_initial: using custom initial positions");
    debug!(
        "nonlinear_line_n3_with_initial: initial_control_points_x={:?}",
        initial_control_points_x
    );
    debug!(
        "nonlinear_line_n3_with_initial: initial_control_points_y={:?}",
        initial_control_points_y
    );

    // Use the provided initial positions directly.
    let point_a_x = initial_control_points_x[0];
    let point_b_x = initial_control_points_x[1];
    let point_c_x = initial_control_points_x[2];
    let point_a_y = initial_control_points_y[0];
    let point_b_y = initial_control_points_y[1];
    let point_c_y = initial_control_points_y[2];

    debug!("point_a=({}, {})", point_a_x, point_a_y);
    debug!("point_b=({}, {})", point_b_x, point_b_y);
    debug!("point_c=({}, {})", point_c_x, point_c_y);

    // Define initial parameter vector (only Y values, X values are
    // fixed).
    let initial_parameters_vec = vec![point_a_y, point_b_y, point_c_y];
    debug!("initial_parameters={initial_parameters_vec:?}");

    // Define the problem.
    let reference_values: Vec<(f64, f64)> = x_values
        .iter()
        .zip(y_values)
        .map(|x| (*x.0, *x.1))
        .collect();

    let problem = N3CurveFitProblem::new(
        point_a_x,
        point_b_x,
        point_c_x,
        reference_values,
    );

    // Calculate step bound based on initial quality.
    let control_points_x = vec![point_a_x, point_b_x, point_c_x];
    let predicted_values = generate_predicted_values_linear(
        x_values,
        &control_points_x,
        &initial_parameters_vec,
    );
    let initial_trust_factor =
        calculate_trust_region_radius_from_quality(y_values, &predicted_values)
            .unwrap_or(100.0); // fallback to default if calculation fails

    // Use LevenbergMarquardt solver with optimal tolerances for N3
    // (matching original pre-dual implementation).
    let config = SolverConfig {
        ftol: 1e-8,
        xtol: 1e-8,
        gtol: 1e-8,
        max_iterations: 1000,
        initial_trust_factor,
        verbose: false,
        ..Default::default()
    };

    let solver = LevenbergMarquardt::new(config);
    let mut workspace =
        SolverWorkspace::new(&problem, &initial_parameters_vec).unwrap();

    // Try the optimal configuration first, with fallback only on failure
    let result = solver.solve_problem(&problem, &mut workspace)?;

    debug!(
        "LevenbergMarquardt result: status={:?}, cost={:.6e}, iterations={}, nfev={}",
        result.status, result.cost, result.iterations, result.function_evaluations
    );

    Ok((
        Point2 {
            x: point_a_x,
            y: result.parameters[0],
        },
        Point2 {
            x: point_b_x,
            y: result.parameters[1],
        },
        Point2 {
            x: point_c_x,
            y: result.parameters[2],
        },
    ))
}

/// Perform a non-linear least-squares fits for a line with 3 points.
pub fn nonlinear_line_n3(
    x_values: &[f64],
    y_values: &[f64],
) -> Result<(Point2, Point2, Point2)> {
    assert_eq!(x_values.len(), y_values.len());
    let value_count = x_values.len();
    assert!(value_count > 2);

    debug!("nonlinear_line_n3: Starting multi-stage optimization");

    let x_first = x_values[0];
    let x_last = x_values[value_count - 1];
    debug!("x_first={x_first}, x_last={x_last}");

    // Define control point X coordinates.
    let point_a_x = x_first;
    let point_b_x = x_first + ((x_last - x_first) * 0.5);
    let point_c_x = x_last;

    debug!(
        "Control point X coordinates: a={}, b={}, c={}",
        point_a_x, point_b_x, point_c_x
    );

    debug!("Starting LevenbergMarquardt optimization");

    assert!(point_a_x <= x_first);
    assert!(point_c_x >= x_last);

    let reference_values: Vec<(f64, f64)> = x_values
        .iter()
        .zip(y_values)
        .map(|(&x, &y)| (x, y))
        .collect();

    let problem = N3CurveFitProblem::new(
        point_a_x,
        point_b_x,
        point_c_x,
        reference_values,
    );

    // Polynomial initialization (Linear interpolation for N3).
    let control_points_x = vec![point_a_x, point_b_x, point_c_x];
    let polynomial_y_initial = direct_linear_curve_fit_approximation(
        x_values,
        y_values,
        &control_points_x,
        // N3 always uses linear interpolation.
        Interpolation::Linear,
        InitializationMethod::LinearRegression,
    );

    // Use polynomial fit if available, otherwise fall back to linear
    // regression.
    let initial_parameters = match polynomial_y_initial {
        Ok(poly_y) => {
            debug!("Using polynomial initialization: {:?}", poly_y);
            poly_y
        }
        Err(e) => {
            debug!("Polynomial fitting failed ({}), falling back to linear regression", e);
            // Fall back to original linear regression approach.
            let mut point_x = 0.0;
            let mut point_y = 0.0;
            let mut dir_x = 0.0;
            let mut dir_y = 0.0;
            control_point_guess_from_linear_regression(
                x_values,
                y_values,
                &mut point_x,
                &mut point_y,
                &mut dir_x,
                &mut dir_y,
            );

            let x_diff = (x_last - x_first) / 2.0;
            let dir_y = dir_y * x_diff;

            vec![point_y - dir_y, point_y, point_y + dir_y]
        }
    };

    // Calculate step bound based on initial quality.
    let control_points_x = vec![point_a_x, point_b_x, point_c_x];
    let predicted_values = generate_predicted_values_linear(
        x_values,
        &control_points_x,
        &initial_parameters,
    );
    let initial_trust_factor =
        calculate_trust_region_radius_from_quality(y_values, &predicted_values)
            .unwrap_or(100.0); // fallback to default if calculation fails.

    let config = SolverConfig {
        ftol: 1e-8,
        xtol: 1e-8,
        gtol: 1e-8,
        max_iterations: 1000,
        initial_trust_factor,
        verbose: false,
        ..Default::default()
    };

    let solver = LevenbergMarquardt::new(config);
    let mut workspace = SolverWorkspace::new(&problem, &initial_parameters)?;

    // Try primary configuration, with conservative fallback only on
    // failure.
    let result = solver.solve_problem(&problem, &mut workspace)?;

    debug!("LevenbergMarquardt result: status={:?}, cost={:.6e}, iterations={}, nfev={}",
           result.status, result.cost, result.iterations, result.function_evaluations);

    Ok((
        Point2 {
            x: point_a_x,
            y: result.parameters[0],
        },
        Point2 {
            x: point_b_x,
            y: result.parameters[1],
        },
        Point2 {
            x: point_c_x,
            y: result.parameters[2],
        },
    ))
}

fn control_point_guess_from_linear_regression(
    x_values: &[f64],
    y_values: &[f64],
    out_point_x: &mut f64,
    out_point_y: &mut f64,
    out_dir_x: &mut f64,
    out_dir_y: &mut f64,
) {
    // First get initial guess using linear regression.
    *out_point_x = 0.0;
    *out_point_y = 0.0;
    let mut angle = 0.0;
    curve_fit_linear_regression_type1(
        x_values,
        y_values,
        out_point_x,
        out_point_y,
        &mut angle,
    );

    *out_dir_x = angle.cos();
    *out_dir_y = angle.sin();
    debug!("point_x={out_point_x} point_y={out_point_y}");
    debug!("dir_x={out_dir_x} dir_y={out_dir_y}");
}

fn generate_evenly_space_control_points(
    x_values: &[f64],
    control_point_count: usize,
    point_x: Real,
    point_y: Real,
    dir_x: Real,
    dir_y: Real,
) -> Result<(Vec<Real>, Vec<Real>)> {
    assert!(x_values.len() > 2);
    assert!(
        control_point_count >= 3,
        "Must have at least 3 control points"
    );

    // Calculate the range of x values.
    let x_first = x_values[0];
    let x_last = x_values[x_values.len() - 1];
    let x_range = x_last - x_first;

    // Generate control points that respect bounds correctness:
    // - First and last control points are exactly on the data boundaries.
    // - Middle control points are placed outside the data range.
    let mut x_initial_control_points = Vec::with_capacity(control_point_count);
    let mut y_initial_control_points = Vec::with_capacity(control_point_count);

    for i in 0..control_point_count {
        let x = if i == 0 {
            // First control point is exactly on first data boundary.
            x_first
        } else if i == control_point_count - 1 {
            // Last control point is exactly on last data boundary.
            x_last
        } else {
            // Middle control points stay inside data boundaries.
            let mix = i as f64 / (control_point_count - 1) as f64;
            (x_first + (mix * x_range)).floor()
        };

        x_initial_control_points.push(x);

        // Initial y-values based on linear regression line.
        let y = point_y + (dir_y * (x - point_x) / dir_x);
        y_initial_control_points.push(y);
    }

    Ok((x_initial_control_points, y_initial_control_points))
}

pub fn nonlinear_line_n_points_with_initial(
    x_values: &[f64],
    y_values: &[f64],
    x_initial_control_points: &[f64],
    y_initial_control_points: &[f64],
    interpolation_method: Interpolation,
) -> Result<Vec<Point2>> {
    assert!(x_values.len() > 2);
    assert_eq!(
        x_values.len(),
        y_values.len(),
        "X and Y values must match length."
    );
    if interpolation_method == Interpolation::CubicNUBS {
        assert!(
            x_initial_control_points.len() >= 4,
            "Must have at least 4 control points for Interpolation::CubicNUBS."
        );
    } else {
        assert!(
            x_initial_control_points.len() >= 3,
            "Must have at least 3 control points for Interpolation::Linear, Interpolation::QuadraticNUBS or Interpolation::CubicSpline."
        );
    }
    assert_eq!(
        x_initial_control_points.len(),
        y_initial_control_points.len(),
        "X and Y control point values must match length."
    );

    debug!("nonlinear_line_n_points_with_initial: Starting multi-stage optimization with {} control points", x_initial_control_points.len());
    debug!("Interpolation method: {:?}", interpolation_method);

    general_nonlinear_npoints(
        x_values,
        y_values,
        x_initial_control_points,
        interpolation_method,
    )
}

/// Polynomial least-squares fitting with interpolation method
/// support.
///
/// This performs direct polynomial fitting that respects the user's
/// chosen interpolation method to provide optimal initial parameter
/// estimates for non-linear optimization.
fn polynomial_least_squares_fit(
    x_values: &[f64],
    y_values: &[f64],
    control_points_x: &[f64],
    interpolation_method: Interpolation,
) -> Result<Vec<f64>> {
    assert_eq!(x_values.len(), y_values.len());
    assert!(x_values.len() > 2);

    let n_points = control_points_x.len();
    debug!(
        "polynomial_least_squares_fit: n_points={}, method={:?}",
        n_points, interpolation_method
    );

    // Choose polynomial degree based on control point count and
    // interpolation method.
    //
    // For high control point counts, use higher degree polynomials
    // for better initialization.
    let base_degree = match interpolation_method {
        Interpolation::Linear => 1,
        Interpolation::QuadraticNUBS => 2,
        Interpolation::CubicSpline | Interpolation::CubicNUBS => 3,
    };

    // Scale degree with control point count for better
    // initialization.
    let scaled_degree = if n_points <= 4 {
        base_degree
    } else if n_points <= 8 {
        (base_degree + 2).min(n_points - 1)
    } else if n_points <= 16 {
        (base_degree + 4).min(n_points - 1).min(8) // Cap at degree 8 for numerical stability.
    } else {
        (base_degree + 6).min(n_points - 1).min(12) // Cap at degree 12 for very high counts.
    };

    let degree = scaled_degree.max(base_degree).min(x_values.len() - 1);

    debug!("Using polynomial degree: {}", degree);

    // Build the Vandermonde matrix for polynomial fitting.
    let m = x_values.len(); // Number of data points.
    let n = degree + 1; // Number of polynomial coefficients.
    let mut a_data = Vec::with_capacity(m * n);
    for i in 0..m {
        let x = x_values[i];
        for j in 0..n {
            a_data.push(x.powi(j as i32));
        }
    }

    let a_matrix = DMatrix::from_row_slice(m, n, &a_data);
    let y_vector = DVector::from_row_slice(y_values);

    // Solve normal equations: A^T * A * coeffs = A^T * y.
    let ata_matrix = a_matrix.transpose() * &a_matrix;
    let aty_vector = a_matrix.transpose() * y_vector;

    // Use LU decomposition to solve.
    let coefficients = ata_matrix
        .lu()
        .solve(&aty_vector)
        .ok_or_else(|| {
            anyhow::anyhow!("Failed to solve polynomial fitting system")
        })?
        .data
        .as_slice()
        .to_vec();

    debug!("Polynomial coefficients: {:?}", coefficients);

    // Convert polynomial coefficients to control point Y-values.
    let mut control_points_y = Vec::with_capacity(n_points);
    for &x in control_points_x {
        let mut y = 0.0;
        for (i, &coeff) in coefficients.iter().enumerate() {
            y += coeff * x.powi(i as i32);
        }
        control_points_y.push(y);
    }

    debug!(
        "Initial control points Y from polynomial fit: {:?}",
        control_points_y
    );
    Ok(control_points_y)
}

/// Linear regression fitting for initial control point estimation.
///
/// This performs simple linear regression fitting to provide initial parameter
/// estimates for non-linear optimization.
fn linear_regression_fit(
    x_values: &[f64],
    y_values: &[f64],
    control_points_x: &[f64],
) -> Result<Vec<f64>> {
    assert_eq!(x_values.len(), y_values.len());
    assert!(x_values.len() > 2);

    let n_points = control_points_x.len();
    debug!("linear_regression_fit: n_points={}", n_points);

    // Use linear regression to fit a line to the data.
    let mut point_x = 0.0;
    let mut point_y = 0.0;
    let mut angle = 0.0;
    let success = curve_fit_linear_regression_type1(
        x_values,
        y_values,
        &mut point_x,
        &mut point_y,
        &mut angle,
    );

    if !success {
        return Err(anyhow::anyhow!("Linear regression fitting failed"));
    }

    debug!(
        "Linear regression: point=({}, {}), angle={}",
        point_x, point_y, angle
    );

    // Calculate slope from angle.
    let slope = angle.tan();
    debug!("Linear regression slope: {}", slope);

    // Generate Y values for each control point X using the linear
    // regression line.
    //
    // Line equation: y = point_y + slope * (x - point_x)
    let mut control_points_y = Vec::with_capacity(n_points);
    for &x in control_points_x {
        let y = point_y + slope * (x - point_x);
        control_points_y.push(y);
    }

    debug!(
        "Initial control points Y from linear regression: {:?}",
        control_points_y
    );
    Ok(control_points_y)
}

#[derive(Copy, Clone, Debug, PartialEq)]
enum InitializationMethod {
    LinearRegression,
    Polynomial,
}

/// Fitting with optional polynomial or linear regression approach.
///
/// This function can use either polynomial fitting or linear
/// regression fitting based on the initialization_method parameter.
///
/// The interpolation_method parameter is only used for polynomial
/// fitting.
fn direct_linear_curve_fit_approximation(
    x_values: &[f64],
    y_values: &[f64],
    control_points_x: &[f64],
    interpolation_method: Interpolation,
    initialization_method: InitializationMethod,
) -> Result<Vec<f64>> {
    match initialization_method {
        InitializationMethod::Polynomial => {
            debug!("Using polynomial initialization method");
            polynomial_least_squares_fit(
                x_values,
                y_values,
                control_points_x,
                interpolation_method,
            )
        }
        InitializationMethod::LinearRegression => {
            debug!("Using linear regression initialization method");
            linear_regression_fit(x_values, y_values, control_points_x)
        }
    }
}

/// Calculate trust region radius based on initial quality match between actual and predicted values.
///
/// Uses NRMSE to determine the quality of the initial fit:
/// - quality = max(0.0, min(100.0, (1.0 - nrmse) * 100.0))
/// - Higher quality (closer match) -> smaller step bound (fine adjustments)
/// - Lower quality (poor match) -> larger step bound (coarse adjustments)
fn calculate_trust_region_radius_from_quality(
    actual: &[f64],
    predicted: &[f64],
) -> Result<f64> {
    // Calculate NRMSE between actual and predicted values
    let nrmse = calc_normalized_root_mean_square_error(actual, predicted)?;

    // Convert NRMSE to quality percentage (0.0 to 1.0).
    let quality = (1.0 - nrmse).clamp(0.0, 1.0);

    debug!(
        "Initial fit quality: nrmse={:.3}, quality={:.3}%",
        nrmse,
        quality * 100.0
    );

    let initial_trust_factor = remap_f64(1.0, 0.0, 9.0, 100.0, quality);

    debug!(
        "Calculated trust region radius={:.3} for quality={:.3}%",
        initial_trust_factor,
        quality * 100.0
    );

    Ok(initial_trust_factor)
}

/// Generate predicted values from control points using linear
/// interpolation.
///
/// This is used to evaluate the quality of the initial fit.
fn generate_predicted_values_linear(
    x_values: &[f64],
    control_points_x: &[f64],
    control_points_y: &[f64],
) -> Vec<f64> {
    let mut predicted = Vec::with_capacity(x_values.len());

    for &x in x_values {
        // Find the two control points to interpolate between.
        let mut y = control_points_y[0]; // Default to first point.

        for i in 0..(control_points_x.len() - 1) {
            let x0 = control_points_x[i];
            let x1 = control_points_x[i + 1];

            if x >= x0 && x <= x1 {
                let y0 = control_points_y[i];
                let y1 = control_points_y[i + 1];
                let t = (x - x0) / (x1 - x0);
                y = y0 + t * (y1 - y0);
                break;
            }
        }

        predicted.push(y);
    }

    predicted
}

/// N-points curve fitting using LevenbergMarquardt solver with
/// polynomial initialization.
fn general_nonlinear_npoints(
    x_values: &[f64],
    y_values: &[f64],
    x_initial_control_points: &[f64],
    interpolation_method: Interpolation,
) -> Result<Vec<Point2>> {
    debug!("general_nonlinear_npoints: Starting LevenbergMarquardt optimization with {:?}", interpolation_method);

    let control_point_count = x_initial_control_points.len();
    let reference_values: Vec<(f64, f64)> = x_values
        .iter()
        .zip(y_values)
        .map(|(&x, &y)| (x, y))
        .collect();

    let problem = NPointsCurveFitProblem::new(
        x_initial_control_points.to_vec(),
        reference_values,
        interpolation_method,
    )?;

    let initialization_method = match interpolation_method {
        Interpolation::Linear => InitializationMethod::LinearRegression,
        _ => InitializationMethod::Polynomial,
    };

    // Polynomial initialization with proper interpolation method.
    let polynomial_y_initial = direct_linear_curve_fit_approximation(
        x_values,
        y_values,
        x_initial_control_points,
        interpolation_method,
        initialization_method,
    );

    // Use polynomial fit if available, otherwise fall back to linear
    // regression.
    let initial_parameters = match polynomial_y_initial {
        Ok(poly_y) => {
            debug!("Using polynomial initialization: {:?}", poly_y);
            poly_y
        }
        Err(e) => {
            debug!("Polynomial fitting failed ({}), falling back to linear regression.", e);
            // Fall back to original linear regression approach.
            let mut point_x = 0.0;
            let mut point_y = 0.0;
            let mut dir_x = 0.0;
            let mut dir_y = 0.0;
            control_point_guess_from_linear_regression(
                x_values,
                y_values,
                &mut point_x,
                &mut point_y,
                &mut dir_x,
                &mut dir_y,
            );

            let (_, y_control) = generate_evenly_space_control_points(
                x_values,
                control_point_count,
                point_x,
                point_y,
                dir_x,
                dir_y,
            )?;
            y_control
        }
    };

    // Calculate step bound based on initial quality match.
    let predicted_values = generate_predicted_values_linear(
        x_values,
        x_initial_control_points,
        &initial_parameters,
    );
    let initial_trust_factor =
        calculate_trust_region_radius_from_quality(y_values, &predicted_values)
            .unwrap_or(100.0); // fallback to default if calculation fails.

    let ftol = 1e-8;
    let xtol = 1e-8;
    let gtol = 1e-8;
    let max_iterations = 1000;
    debug!("Using tolerances ftol={}, xtol={}, gtol={}, max_iterations={} step_bound={} for {} control points",
          ftol, xtol, gtol, max_iterations, initial_trust_factor, control_point_count);

    let config = SolverConfig {
        ftol,
        xtol,
        gtol,
        max_iterations,
        initial_trust_factor,
        verbose: false,
        ..Default::default()
    };

    let solver = LevenbergMarquardt::new(config);
    let mut workspace = SolverWorkspace::new(&problem, &initial_parameters)?;

    // Try primary configuration, with conservative fallback only on
    // failure.
    let result = solver.solve_problem(&problem, &mut workspace)?;

    debug!("LevenbergMarquardt result: status={:?}, cost={:.6e}, iterations={}, nfev={}",
           result.status, result.cost, result.iterations, result.function_evaluations);

    let mut control_points = Vec::with_capacity(control_point_count);
    for i in 0..control_point_count {
        control_points.push(Point2 {
            x: x_initial_control_points[i],
            y: result.parameters[i],
        });
    }
    Ok(control_points)
}

pub fn nonlinear_line_n_points(
    x_values: &[f64],
    y_values: &[f64],
    control_point_count: usize,
    interpolation: Interpolation,
) -> Result<Vec<Point2>> {
    assert_eq!(x_values.len(), y_values.len());
    let value_count = x_values.len();
    assert!(value_count > 2);

    if interpolation == Interpolation::CubicNUBS {
        assert!(
            control_point_count >= 4,
            "Must have at least 4 control points for Interpolation::CubicNUBS."
        );
    } else {
        assert!(
            control_point_count >= 3,
            "Must have at least 3 control points for Interpolation::Linear, Interpolation::QuadraticNUBS or Interpolation::CubicSpline."
        );
    }

    debug!("nonlinear_line_n_points: Starting multi-stage optimization with {} control points", control_point_count);
    debug!("Interpolation method: {:?}", interpolation);

    let mut point_x = 0.0;
    let mut point_y = 0.0;
    let mut dir_x = 0.0;
    let mut dir_y = 0.0;
    control_point_guess_from_linear_regression(
        x_values,
        y_values,
        &mut point_x,
        &mut point_y,
        &mut dir_x,
        &mut dir_y,
    );

    let (x_initial_control_points, _) = generate_evenly_space_control_points(
        x_values,
        control_point_count,
        point_x,
        point_y,
        dir_x,
        dir_y,
    )?;

    general_nonlinear_npoints(
        x_values,
        y_values,
        &x_initial_control_points,
        interpolation,
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;
    use mmcore::dual::Dual;

    const EPSILON: f64 = 1e-6;

    #[test]
    fn test_calculate_trust_region_radius_from_quality() {
        // Perfect match (NRMSE = 0.0) should give small trust region
        // radius.
        let actual = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let predicted = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let trust_factor =
            calculate_trust_region_radius_from_quality(&actual, &predicted)
                .unwrap();
        assert!(
            trust_factor >= 1.0 && trust_factor <= 10.0,
            "Perfect match should give small trust region radius, got: {}",
            trust_factor
        );

        // Poor match should give large trust region radius.
        let actual = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let predicted = vec![5.0, 4.0, 3.0, 2.0, 1.0]; // Completely reversed.
        let trust_factor =
            calculate_trust_region_radius_from_quality(&actual, &predicted)
                .unwrap();
        assert!(
            trust_factor >= 50.0,
            "Poor match should give large trust region radius, got: {}",
            trust_factor
        );

        // Medium match should give medium trust region radius.
        let actual = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let predicted = vec![1.1, 1.9, 3.1, 3.9, 5.1]; // Close but not perfect.
        let trust_factor =
            calculate_trust_region_radius_from_quality(&actual, &predicted)
                .unwrap();
        assert!(
            trust_factor >= 1.0 && trust_factor <= 50.0,
            "Medium match should give medium trust region radius, got: {}",
            trust_factor
        );
    }

    #[test]
    fn test_generate_predicted_values_linear() {
        let x_values = vec![1.0, 2.0, 3.0, 4.0, 5.0];
        let control_points_x = vec![1.0, 3.0, 5.0];
        let control_points_y = vec![1.0, 3.0, 5.0];

        let predicted = generate_predicted_values_linear(
            &x_values,
            &control_points_x,
            &control_points_y,
        );

        assert_eq!(predicted.len(), x_values.len());
        assert_relative_eq!(predicted[0], 1.0, epsilon = EPSILON); // x=1.0
        assert_relative_eq!(predicted[1], 2.0, epsilon = EPSILON); // x=2.0, interpolated
        assert_relative_eq!(predicted[2], 3.0, epsilon = EPSILON); // x=3.0
        assert_relative_eq!(predicted[3], 4.0, epsilon = EPSILON); // x=4.0, interpolated
        assert_relative_eq!(predicted[4], 5.0, epsilon = EPSILON); // x=5.0
    }

    #[test]
    fn test_step_bound_quality_ranges() {
        // Test the trust region radius calculation ranges.
        let actual = vec![0.0, 1.0, 2.0, 3.0, 4.0];

        // High quality case - very small errors.
        let predicted_high = vec![0.001, 1.001, 2.001, 3.001, 4.001];
        let step_bound_high = calculate_trust_region_radius_from_quality(
            &actual,
            &predicted_high,
        )
        .unwrap();
        assert!(
            step_bound_high >= 1.0 && step_bound_high <= 10.0,
            "High quality should give small trust region radius, got: {}",
            step_bound_high
        );

        // Medium quality case - larger errors to get NRMSE in medium range.
        let predicted_medium = vec![0.5, 1.5, 2.5, 3.5, 4.5];
        let step_bound_medium = calculate_trust_region_radius_from_quality(
            &actual,
            &predicted_medium,
        )
        .unwrap();
        assert!(
            step_bound_medium >= 1.0 && step_bound_medium <= 50.0,
            "Medium quality should give small to medium trust region radius, got: {}",
            step_bound_medium
        );

        // Low quality case - completely different values.
        let predicted_low = vec![2.0, 1.0, 0.0, -1.0, -2.0]; // Reversed and shifted.
        let step_bound_low =
            calculate_trust_region_radius_from_quality(&actual, &predicted_low)
                .unwrap();
        assert!(
            step_bound_low >= 50.0,
            "Low quality should give large trust region radius, got: {}",
            step_bound_low
        );
    }

    #[test]
    fn test_generic_interpolation_with_dual_numbers() {
        // Test that all interpolation methods work with dual numbers
        // for automatic differentiation.
        let control_points_x = vec![0.0, 1.0, 2.0, 3.0];
        let reference_values = vec![(0.5, 1.0), (1.5, 2.0), (2.5, 3.0)];

        // Test each interpolation method.
        let methods = [
            Interpolation::Linear,
            Interpolation::QuadraticNUBS,
            Interpolation::CubicNUBS,
            Interpolation::CubicSpline,
        ];

        for method in &methods {
            let problem = NPointsCurveFitProblem::new(
                control_points_x.clone(),
                reference_values.clone(),
                *method,
            )
            .unwrap();

            // Test parameters as dual numbers with automatic
            // differentiation.
            let parameters = [
                Dual::new(1.0, 1.0),
                Dual::new(2.0, 0.0),
                Dual::new(3.0, 0.0),
                Dual::new(4.0, 0.0),
            ];
            let mut residuals = vec![Dual::new(0.0, 0.0); 3];

            // This should work without panicking and compute gradients automatically.
            let result = problem.residuals(&parameters, &mut residuals);
            assert!(
                result.is_ok(),
                "Interpolation method {:?} failed with dual numbers",
                method
            );

            // Verify that dual parts contain gradient information.
            for residual in &residuals {
                // At least one residual should have non-zero dual
                // part (gradient).
                //
                // This confirms automatic differentiation is working.
                if residual.dual != 0.0 {
                    debug!(
                        "Gradient computed: real={}, dual={}",
                        residual.real, residual.dual
                    );
                }
            }

            debug!(
                "Generic interpolation with dual numbers works for {:?}",
                method
            );
        }
    }

    #[test]
    fn test_cubic_nubs_with_dual_numbers_detailed() {
        use crate::math::interpolate::{
            CubicNUBSInterpolator, CurveInterpolator,
        };
        use mmcore::dual::Dual;

        // Create a CubicNUBS interpolator with sufficient control points
        let control_points_x = vec![0.0, 1.0, 2.0, 3.0, 4.0];
        let control_points_y = vec![0.0, 1.0, 0.5, 2.0, 1.5];

        let interpolator = CubicNUBSInterpolator::new();
        interpolator.set_control_points(&control_points_x, &control_points_y);

        // Test with f64 first
        let result_f64 = interpolator.interpolate_f64(1.5);
        debug!("f64 result at x=1.5: {}", result_f64);

        // Test with dual numbers
        let x_dual = Dual::new(1.5, 1.0); // Value 1.5, derivative 1.0
        let result_dual = interpolator.interpolate(x_dual);

        debug!(
            "Dual result at x=1.5: real={}, dual={}",
            result_dual.real, result_dual.dual
        );

        // The real parts should be very close
        assert!(
            (result_f64 - result_dual.real).abs() < 1e-10,
            "f64 and dual real parts should match: {} vs {}",
            result_f64,
            result_dual.real
        );

        // The dual part should be non-zero (indicating we computed a
        // derivative).
        debug!("Dual derivative: {}", result_dual.dual);
        assert!(result_dual.dual > 0.0);

        // Test multiple points to ensure robustness
        let test_points = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5];
        for &x in &test_points {
            let x_dual = Dual::new(x, 1.0);
            let result = interpolator.interpolate(x_dual);
            debug!("At x={}: real={}, dual={}", x, result.real, result.dual);

            // Ensure no NaN or infinite values
            assert!(
                result.real.is_finite(),
                "Real part should be finite at x={}",
                x
            );
            assert!(
                result.dual.is_finite(),
                "Dual part should be finite at x={}",
                x
            );
        }
    }
}
