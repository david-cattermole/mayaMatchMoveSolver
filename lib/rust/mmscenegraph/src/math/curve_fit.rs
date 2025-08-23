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
use log::info;
use nalgebra::{DMatrix, DVector};

use crate::constant::Real;
use crate::math::interpolate::linear_interpolate_y_value_at_value_x;
use crate::math::interpolate::CurveInterpolator;
use crate::math::interpolate::Interpolation;
use crate::math::interpolate::Interpolator;
use crate::math::line::curve_fit_linear_regression_type1;
use mmoptimise::solver::{
    LevenbergMarquardt, OptimisationProblem, SolverConfig, SolverWorkspace,
};

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
        &x_values,
        &y_values,
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
    fn residuals(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> anyhow::Result<()> {
        if parameters.len() != 3 {
            return Err(anyhow::anyhow!(
                "N3 problem requires exactly 3 parameters (Y values)"
            ));
        }

        let point_a_y = parameters[0];
        let point_b_y = parameters[1];
        let point_c_y = parameters[2];

        for i in 0..self.residual_count() {
            let data_x = self.reference_values[i].0;
            let data_y = self.reference_values[i].1;

            let curve_y = linear_interpolate_y_value_at_value_x(
                data_x,
                self.point_a_x,
                point_a_y,
                self.point_b_x,
                point_b_y,
                self.point_c_x,
                point_c_y,
            );
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
    interpolator: Interpolator,
}

impl NPointsCurveFitProblem {
    fn new(
        control_points_x: Vec<f64>,
        reference_values: Vec<(f64, f64)>,
        interpolation_method: Interpolation,
    ) -> anyhow::Result<Self> {
        let interpolator = Interpolator::from_method(interpolation_method);
        interpolator.set_control_points_x(&control_points_x);

        Ok(Self {
            reference_values,
            control_points_x,
            interpolator,
        })
    }
}

impl OptimisationProblem for NPointsCurveFitProblem {
    fn residuals(
        &self,
        parameters: &[f64],
        out_residuals: &mut [f64],
    ) -> anyhow::Result<()> {
        if parameters.len() != self.control_points_x.len() {
            return Err(anyhow::anyhow!(
                "Parameter count must match control point count"
            ));
        }

        self.interpolator.set_control_points_y(parameters);

        for i in 0..self.residual_count() {
            let data_x = self.reference_values[i].0;
            let data_y = self.reference_values[i].1;
            let curve_y = self.interpolator.interpolate(data_x);
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

    info!("nonlinear_line_n3_with_initial: using custom initial positions");
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

    // Use LevenbergMarquardt solver with good tolerances for N3.
    let config = SolverConfig {
        ftol: 1e-8,
        xtol: 1e-8,
        gtol: 1e-8,
        max_iterations: 300,
        step_bound: 100.0,
        verbose: false,
    };

    let solver = LevenbergMarquardt::new(config);
    let mut workspace =
        SolverWorkspace::new(&problem, &initial_parameters_vec).unwrap();
    let result = solver.solve_problem(&problem, &mut workspace).unwrap();

    info!(
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
///
/// The approach uses a 3-stage optimization process:
/// 1. Polynomial least-squares initialization for better starting points.
/// 2. Coarse non-linear optimization with relaxed tolerances.
/// 3. Fine-tuning optimization with tighter tolerances.
///
/// This multi-stage approach provides better convergence and higher
/// quality fits compared to single-stage optimization.
pub fn nonlinear_line_n3(
    x_values: &[f64],
    y_values: &[f64],
) -> Result<(Point2, Point2, Point2)> {
    assert_eq!(x_values.len(), y_values.len());
    let value_count = x_values.len();
    assert!(value_count > 2);

    info!("nonlinear_line_n3: Starting multi-stage optimization");

    // Calculate control point X positions using linear regression
    // approach.
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

    let x_first = x_values[0];
    let x_last = x_values[value_count - 1];
    let x_diff = (x_last - x_first) / 2.0;
    debug!("x_first={x_first}, x_last={x_last}, x_diff={x_diff}");

    // Scale up to X axis range.
    let dir_x = dir_x * x_diff;

    // Define control point X coordinates.
    let point_a_x = point_x - dir_x;
    let point_b_x = point_x;
    let point_c_x = point_x + dir_x;

    debug!(
        "Control point X coordinates: a={}, b={}, c={}",
        point_a_x, point_b_x, point_c_x
    );

    // Use multi-stage optimization.
    multi_stage_nonlinear_n3(
        x_values, y_values, point_a_x, point_b_x, point_c_x,
    )
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

    // Generate evenly spaced control points along x-axis.
    let mut x_initial_control_points = Vec::with_capacity(control_point_count);
    let mut y_initial_control_points = Vec::with_capacity(control_point_count);
    for i in 0..control_point_count {
        let mix = i as f64 / (control_point_count - 1) as f64;
        let x = (x_first + (mix * x_range)).floor();
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

    info!("nonlinear_line_n_points_with_initial: Starting multi-stage optimization with {} control points", x_initial_control_points.len());
    info!("Interpolation method: {:?}", interpolation_method);

    // Use multi-stage optimization (ignoring the provided Y initial
    // values as Stage 1 will compute better initialization).
    multi_stage_nonlinear_npoints(
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
fn polynomial_least_squares_fit_with_interpolation(
    x_values: &[f64],
    y_values: &[f64],
    control_points_x: &[f64],
    interpolation_method: Interpolation,
) -> Result<Vec<f64>> {
    assert_eq!(x_values.len(), y_values.len());
    assert!(x_values.len() > 2);

    let n_points = control_points_x.len();
    info!("polynomial_least_squares_fit_with_interpolation: n_points={}, method={:?}", n_points, interpolation_method);

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

    info!("Using polynomial degree: {}", degree);

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

    info!("Polynomial coefficients: {:?}", coefficients);

    // Convert polynomial coefficients to control point Y-values.
    let mut control_points_y = Vec::with_capacity(n_points);
    for &x in control_points_x {
        let mut y = 0.0;
        for (i, &coeff) in coefficients.iter().enumerate() {
            y += coeff * x.powi(i as i32);
        }
        control_points_y.push(y);
    }

    info!(
        "Initial control points Y from polynomial fit: {:?}",
        control_points_y
    );
    Ok(control_points_y)
}

/// N3 curve fitting using LevenbergMarquardt solver with polynomial
/// initialization.
fn multi_stage_nonlinear_n3(
    x_values: &[f64],
    y_values: &[f64],
    point_a_x: f64,
    point_b_x: f64,
    point_c_x: f64,
) -> Result<(Point2, Point2, Point2)> {
    info!("multi_stage_nonlinear_n3: Starting LevenbergMarquardt optimization");

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
    let polynomial_y_initial = polynomial_least_squares_fit_with_interpolation(
        x_values,
        y_values,
        &control_points_x,
        Interpolation::Linear, // N3 always uses linear interpolation.
    );

    // Use polynomial fit if available, otherwise fall back to linear
    // regression.
    let initial_parameters = match polynomial_y_initial {
        Ok(poly_y) => {
            info!("Using polynomial initialization: {:?}", poly_y);
            poly_y
        }
        Err(e) => {
            info!("Polynomial fitting failed ({}), falling back to linear regression", e);
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

            let x_first = x_values[0];
            let x_last = x_values[x_values.len() - 1];
            let x_diff = (x_last - x_first) / 2.0;
            let dir_y = dir_y * x_diff;

            vec![point_y - dir_y, point_y, point_y + dir_y]
        }
    };

    // LevenbergMarquardt optimization with good tolerances.
    let config = SolverConfig {
        ftol: 1e-8,
        xtol: 1e-8,
        gtol: 1e-8,
        max_iterations: 300,
        step_bound: 100.0,
        verbose: false,
    };

    let solver = LevenbergMarquardt::new(config);
    let mut workspace =
        SolverWorkspace::new(&problem, &initial_parameters).unwrap();
    let result = solver.solve_problem(&problem, &mut workspace).unwrap();

    info!("LevenbergMarquardt result: status={:?}, cost={:.6e}, iterations={}, nfev={}",
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

/// N-points curve fitting using LevenbergMarquardt solver with
/// polynomial initialization.
fn multi_stage_nonlinear_npoints(
    x_values: &[f64],
    y_values: &[f64],
    x_initial_control_points: &[f64],
    interpolation_method: Interpolation,
) -> Result<Vec<Point2>> {
    info!("multi_stage_nonlinear_npoints: Starting LevenbergMarquardt optimization with {:?}", interpolation_method);

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

    // Polynomial initialization with proper interpolation method.
    let polynomial_y_initial = polynomial_least_squares_fit_with_interpolation(
        x_values,
        y_values,
        x_initial_control_points,
        interpolation_method,
    );

    // Use polynomial fit if available, otherwise fall back to linear regression.
    let initial_parameters = match polynomial_y_initial {
        Ok(poly_y) => {
            info!("Using polynomial initialization: {:?}", poly_y);
            poly_y
        }
        Err(e) => {
            info!("Polynomial fitting failed ({}), falling back to linear regression", e);
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

    let (ftol, xtol, gtol) = (1e-6, 1e-6, 1e-6);
    let max_iter = 100;

    info!("Using tolerances ftol={}, xtol={}, gtol={}, max_iter={} for {} control points",
           ftol, xtol, gtol, max_iter, control_point_count);

    let config = SolverConfig {
        ftol,
        xtol,
        gtol,
        max_iterations: max_iter,
        step_bound: 100.0,
        verbose: false,
    };

    let solver = LevenbergMarquardt::new(config);
    let mut workspace =
        SolverWorkspace::new(&problem, &initial_parameters).unwrap();
    let result = solver.solve_problem(&problem, &mut workspace).unwrap();

    info!("LevenbergMarquardt result: status={:?}, cost={:.6e}, iterations={}, nfev={}",
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

    info!("nonlinear_line_n_points: Starting multi-stage optimization with {} control points", control_point_count);
    info!("Interpolation method: {:?}", interpolation);

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

    multi_stage_nonlinear_npoints(
        x_values,
        y_values,
        &x_initial_control_points,
        interpolation,
    )
}
