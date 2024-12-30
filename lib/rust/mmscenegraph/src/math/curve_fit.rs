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

use anyhow::bail;
use anyhow::Result;
use argmin;
use argmin::core::Gradient;
use argmin::core::State;
use finitediff::FiniteDiff;
use log::debug;
use ndarray::{Array1, Array2};

use crate::constant::Real;
use crate::math::interpolate::linear_interpolate_y_value_at_value_x;
use crate::math::interpolate::CurveInterpolator;
use crate::math::interpolate::InterpolationMethod;
use crate::math::interpolate::Interpolator;
use crate::math::line::curve_fit_linear_regression_type1;

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

#[derive(Debug)]
struct CurveFitLinearN3Problem {
    // Curve values we are trying to fit to.
    reference_values: Vec<(f64, f64)>,
    reference_values_first_x: usize,
    // reference_values_last_x: usize,

    // These are parameters that are hard-coded.
    point_a_x: f64,
    point_b_x: f64,
    point_c_x: f64,
}

impl CurveFitLinearN3Problem {
    fn new(
        point_a_x: f64,
        point_b_x: f64,
        point_c_x: f64,
        reference_curve: &[(f64, f64)],
    ) -> Self {
        // let count = reference_curve.len();
        let x_first: usize = reference_curve[0].0.floor() as usize;
        // let x_last: usize = reference_curve[count - 1].0.ceil() as usize;

        let reference_values: Vec<(f64, f64)> =
            reference_curve.iter().map(|x| *x).collect();

        Self {
            reference_values,
            reference_values_first_x: x_first,
            // reference_values_last_x: x_last,
            point_a_x,
            point_b_x,
            point_c_x,
        }
    }

    fn parameter_count(&self) -> usize {
        // 3 x 2D points is 6, but the X axis values are always
        // locked, therefore 3 values are known, and we do not need to
        // solve for them.
        3
    }

    fn reference_y_value_at_value_x(&self, value_x: f64) -> f64 {
        let value_start = self.point_a_x.floor() as usize;
        let value_end = self.point_c_x.ceil() as usize;

        let mut value_index = value_x.round() as usize;
        if value_index < value_start {
            value_index = value_start;
        } else if value_index > value_end {
            value_index = value_end;
        }

        let mut index = value_index - self.reference_values_first_x;
        if index > self.reference_values.len() {
            index = self.reference_values.len();
        }

        self.reference_values[index].1
    }

    fn residuals(
        &self,
        point_a_y: f64,
        point_b_y: f64,
        point_c_y: f64,
    ) -> Vec<f64> {
        self.reference_values
            .iter()
            .map(|x| {
                let value_x = x.0;
                let curve_y = linear_interpolate_y_value_at_value_x(
                    value_x,
                    self.point_a_x,
                    point_a_y,
                    self.point_b_x,
                    point_b_y,
                    self.point_c_x,
                    point_c_y,
                );
                let data_y = self.reference_y_value_at_value_x(value_x);
                (curve_y - data_y).abs()
            })
            .collect()
    }
}

impl argmin::core::CostFunction for CurveFitLinearN3Problem {
    type Param = Array1<f64>;
    type Output = f64;

    fn cost(
        &self,
        parameters: &Self::Param,
    ) -> Result<Self::Output, argmin::core::Error> {
        debug!("Cost: parameters={parameters:?}");

        let parameter_count = self.parameter_count();
        assert_eq!(parameters.len(), parameter_count);

        let residuals_data =
            self.residuals(parameters[0], parameters[1], parameters[2]);
        let residuals = Array1::from_vec(residuals_data);

        let residuals_sum = residuals.sum();
        debug!("residuals_sum: {residuals_sum}");

        Ok(residuals_sum * residuals_sum)
    }
}

impl argmin::core::Gradient for CurveFitLinearN3Problem {
    type Param = Array1<f64>;
    type Gradient = Array1<f64>;

    fn gradient(
        &self,
        parameters: &Self::Param,
    ) -> Result<Self::Gradient, argmin::core::Error> {
        debug!("Gradient: parameters={parameters:?}");

        let parameter_count = self.parameter_count();
        assert_eq!(parameters.len(), parameter_count);

        let vector = (*parameters).forward_diff(&|x| {
            let sum: f64 = self.residuals(x[0], x[1], x[2]).into_iter().sum();
            debug!("forward_diff residuals_sum: {sum}");
            sum * sum
        });

        Ok(vector)
    }
}

impl argmin::core::Hessian for CurveFitLinearN3Problem {
    type Param = Array1<f64>;
    type Hessian = Array2<f64>;

    fn hessian(
        &self,
        parameters: &Self::Param,
    ) -> Result<Self::Hessian, argmin::core::Error> {
        debug!("Hessian: parameters={parameters:?}");

        let parameter_count = self.parameter_count();
        assert_eq!(parameters.len(), parameter_count);

        let matrix =
            (*parameters).forward_hessian(&|x| self.gradient(x).unwrap());

        Ok(matrix)
    }
}

/// Perform a non-linear least-squares fits for a line with 3 points.
///
/// The approach here is to start with a linear regression, to get a
/// starting point, and then refine the solution using a solver.
///
/// Rather than solve a direct solution we aim to solve successively
/// more difficult problem in multiple steps, as each one improves the
/// overall fit to the source data values.
///
/// In the future we may wish to allow different types of curve
/// interpolation between the 3 points.
pub fn nonlinear_line_n3(
    x_values: &[f64],
    y_values: &[f64],
) -> Result<(Point2, Point2, Point2)> {
    assert_eq!(x_values.len(), y_values.len());
    let value_count = x_values.len();
    assert!(value_count > 2);

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
    let y_first = y_values[0];
    let x_last = x_values[value_count - 1];
    let y_last = y_values[value_count - 1];
    let x_diff = (x_last - x_first) as f64 / 2.0;
    let y_diff = (y_last - y_first) as f64 / 2.0;
    debug!("x_first={x_first}");
    debug!("y_first={y_first}");
    debug!("x_last={x_last}");
    debug!("y_last={y_last}");
    debug!("x_diff={x_diff}");
    debug!("y_diff={y_diff}");

    // Scale up to X axis range.
    let dir_x = dir_x * x_diff;
    let dir_y = dir_y * x_diff;

    // Define initial parameter vector
    let point_a = Point2 {
        x: point_x - dir_x,
        y: point_y - dir_y,
    };
    let point_b = Point2 {
        x: point_x,
        y: point_y,
    };
    let point_c = Point2 {
        x: point_x + dir_x,
        y: point_y + dir_y,
    };
    // NOTE: point_a.x, point_b.x and point_c.x are omitted as these
    // are hard-coded as known parameters and do not need to be
    // solved.
    let initial_parameters_vec = vec![point_a.y, point_b.y, point_c.y];
    let initial_parameters: Array1<f64> = Array1::from(initial_parameters_vec);
    debug!("initial_parameters={initial_parameters:?}");

    // Define the problem
    let reference_values: Vec<(f64, f64)> = x_values
        .iter()
        .zip(y_values)
        .map(|x| (*x.0, *x.1))
        .collect();
    let problem = CurveFitLinearN3Problem::new(
        // Known parameters
        point_a.x,
        point_b.x,
        point_c.x,
        // Curve values to match-to.
        &reference_values,
    );

    // Set up solver.
    let epsilon = 1e-9;
    let condition =
        argmin::solver::linesearch::condition::ArmijoCondition::new(1e-5)?;
    let linesearch =
        argmin::solver::linesearch::BacktrackingLineSearch::new(condition)
            .rho(0.5)?;
    let solver = argmin::solver::quasinewton::BFGS::new(linesearch)
        .with_tolerance_cost(epsilon)?;

    // Run solver
    let initial_hessian: Array2<f64> = Array2::eye(3);
    let result = argmin::core::Executor::new(problem, solver)
        .configure(|state| {
            state
                .param(initial_parameters)
                .inv_hessian(initial_hessian)
                .max_iters(50)
        })
        .run()?;
    debug!("Solver Result: {result}");

    match result.state().get_best_param() {
        Some(parameters) => Ok((
            Point2 {
                x: point_a.x,
                y: parameters[0],
            },
            Point2 {
                x: point_b.x,
                y: parameters[1],
            },
            Point2 {
                x: point_c.x,
                y: parameters[2],
            },
        )),
        None => bail!("Solve failed."),
    }
}

#[derive(Debug)]
pub struct CurveFitLinearNPointsProblem {
    // Curve values we are trying to fit to.
    reference_values: Vec<(f64, f64)>,
    // X-coordinates of control points (fixed).
    control_points_x: Vec<f64>,
    // Interpolation method to use.
    interpolator: Interpolator,
}

impl CurveFitLinearNPointsProblem {
    fn new(
        control_points_x: Vec<f64>,
        reference_curve: &[(f64, f64)],
        interpolation_method: InterpolationMethod,
    ) -> Self {
        let reference_values: Vec<(f64, f64)> =
            reference_curve.iter().copied().collect();

        Self {
            reference_values,
            control_points_x,
            interpolator: Interpolator::from_method(interpolation_method),
        }
    }

    fn parameter_count(&self) -> usize {
        self.control_points_x.len()
    }

    fn interpolate_y_value_at_x(
        &self,
        value_x: f64,
        control_points_y: &[f64],
    ) -> f64 {
        self.interpolator.interpolate(
            value_x,
            &self.control_points_x,
            control_points_y,
        )
    }

    fn residuals(&self, control_points_y: &[f64]) -> Vec<f64> {
        self.reference_values
            .iter()
            .map(|&(value_x, data_y)| {
                let curve_y =
                    self.interpolate_y_value_at_x(value_x, control_points_y);
                (curve_y - data_y).abs()
            })
            .collect()
    }
}

impl argmin::core::CostFunction for CurveFitLinearNPointsProblem {
    type Param = Array1<f64>;
    type Output = f64;

    fn cost(
        &self,
        parameters: &Self::Param,
    ) -> Result<Self::Output, argmin::core::Error> {
        debug!("Cost: parameters={parameters:?}");
        assert_eq!(parameters.len(), self.parameter_count());

        let residuals_data = self.residuals(parameters.as_slice().unwrap());
        let residuals = Array1::from_vec(residuals_data);

        let residuals_sum = residuals.sum();
        debug!("residuals_sum: {residuals_sum}");

        Ok(residuals_sum * residuals_sum)
    }
}

impl argmin::core::Gradient for CurveFitLinearNPointsProblem {
    type Param = Array1<f64>;
    type Gradient = Array1<f64>;

    fn gradient(
        &self,
        parameters: &Self::Param,
    ) -> Result<Self::Gradient, argmin::core::Error> {
        debug!("Gradient: parameters={parameters:?}");
        assert_eq!(parameters.len(), self.parameter_count());

        let vector = (*parameters).forward_diff(&|x| {
            let sum: f64 =
                self.residuals(x.as_slice().unwrap()).into_iter().sum();
            debug!("forward_diff residuals_sum: {sum}");
            sum * sum
        });

        Ok(vector)
    }
}

impl argmin::core::Hessian for CurveFitLinearNPointsProblem {
    type Param = Array1<f64>;
    type Hessian = Array2<f64>;

    fn hessian(
        &self,
        parameters: &Self::Param,
    ) -> Result<Self::Hessian, argmin::core::Error> {
        debug!("Hessian: parameters={parameters:?}");
        assert_eq!(parameters.len(), self.parameter_count());

        let matrix =
            (*parameters).forward_hessian(&|x| self.gradient(x).unwrap());

        Ok(matrix)
    }
}

fn control_point_guess_from_linear_regression(
    x_values: &[f64],
    y_values: &[f64],
    out_point_x: &mut f64,
    out_point_y: &mut f64,
    out_dir_x: &mut f64,
    out_dir_y: &mut f64,
) {
    // First get initial guess using linear regression
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

    // Calculate the range of x values
    let x_first = x_values[0];
    let x_last = x_values[x_values.len() - 1];
    let x_range = x_last - x_first;

    // Generate evenly spaced control points along x-axis
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
    interpolation_method: InterpolationMethod,
) -> Result<Vec<Point2>> {
    assert!(x_values.len() > 2);
    assert_eq!(
        x_values.len(),
        y_values.len(),
        "X and Y values must match length."
    );
    assert!(
        x_initial_control_points.len() >= 3,
        "Must have at least 3 control points."
    );
    assert_eq!(
        x_initial_control_points.len(),
        y_initial_control_points.len(),
        "X and Y control point values must match length."
    );
    let control_point_count = x_initial_control_points.len();

    // Create reference values.
    let reference_values: Vec<(f64, f64)> = x_values
        .iter()
        .zip(y_values)
        .map(|(&x, &y)| (x, y))
        .collect();

    // Define the problem.
    let problem = CurveFitLinearNPointsProblem::new(
        x_initial_control_points.to_vec(),
        &reference_values,
        interpolation_method,
    );

    // Set up solver
    let epsilon = 1e-3;
    let condition =
        argmin::solver::linesearch::condition::ArmijoCondition::new(1e-5)?;
    let linesearch =
        argmin::solver::linesearch::BacktrackingLineSearch::new(condition)
            .rho(0.5)?;
    let solver = argmin::solver::quasinewton::BFGS::new(linesearch)
        .with_tolerance_cost(epsilon)?;

    // Run solver
    let initial_parameters = Array1::from(y_initial_control_points.to_vec());
    let initial_hessian: Array2<f64> = Array2::eye(control_point_count);
    let result = argmin::core::Executor::new(problem, solver)
        .configure(|state| {
            state
                .param(initial_parameters)
                .inv_hessian(initial_hessian)
                .max_iters(50)
        })
        .run()?;

    debug!("Solver Result: {result}");

    match result.state().get_best_param() {
        Some(parameters) => {
            let mut control_points = Vec::with_capacity(control_point_count);
            for i in 0..control_point_count {
                control_points.push(Point2 {
                    x: x_initial_control_points[i],
                    y: parameters[i],
                });
            }
            Ok(control_points)
        }
        None => bail!("Solve failed."),
    }
}

pub fn nonlinear_line_n_points(
    x_values: &[f64],
    y_values: &[f64],
    control_point_count: usize,
    interpolation: InterpolationMethod,
) -> Result<Vec<Point2>> {
    assert_eq!(x_values.len(), y_values.len());
    let value_count = x_values.len();
    assert!(value_count > 2);
    assert!(
        control_point_count >= 3,
        "Must have at least 3 control points"
    );

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

    let (x_initial_control_points, y_initial_control_points) =
        generate_evenly_space_control_points(
            x_values,
            control_point_count,
            point_x,
            point_y,
            dir_x,
            dir_y,
        )?;

    nonlinear_line_n_points_with_initial(
        x_values,
        y_values,
        &x_initial_control_points,
        &y_initial_control_points,
        interpolation,
    )
}
