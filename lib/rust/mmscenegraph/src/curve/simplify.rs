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

use anyhow::Result;
use log::debug;
use log::error;

use crate::constant::Real;
use crate::curve::detect::keypoints::analyze_curve;
use crate::math::curve_fit::linear_regression;
use crate::math::curve_fit::nonlinear_line_n3;
use crate::math::curve_fit::nonlinear_line_n_points;
use crate::math::curve_fit::nonlinear_line_n_points_with_initial;
use crate::math::interpolate::evaluate_curve_points;
use crate::math::interpolate::Interpolation;

#[repr(u8)]
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum ControlPointDistribution {
    Uniform = 1,
    AutoKeypoints = 2,
}

pub fn simplify(
    values_x: &[Real],
    values_y: &[Real],
    control_point_count: usize,
    distribution: ControlPointDistribution,
    interpolation_method: Interpolation,
) -> Result<Vec<(Real, Real)>> {
    debug!("target_control_points={control_point_count:?}");
    debug!("interpolation_method={interpolation_method:?}");
    debug!("distribution={distribution:?}");

    let eval_values_xy = if control_point_count == 2 {
        assert!(
            interpolation_method == Interpolation::Linear,
            "It only makes sense to have a linear line with two keypoints."
        );

        // Linear - 2 points.
        let (point, slope) = linear_regression(values_x, values_y)?;
        debug!("point={point:?} slope={slope:?}");

        let x_first = values_x[0];
        let x_last = values_x[values_x.len() - 1];
        let x_diff = (x_last - x_first) as Real / 2.0;

        let (dir_x, dir_y) = slope.as_direction();

        // Scale up to X axis range.
        let dir_x = dir_x * x_diff;
        let dir_y = dir_y * x_diff;

        let control_points_x: Vec<Real> =
            vec![point.x() - dir_x, point.x() + dir_x];
        let control_points_y: Vec<Real> =
            vec![point.y() - dir_y, point.y() + dir_y];

        evaluate_curve_points(
            values_x,
            &control_points_x,
            &control_points_y,
            interpolation_method,
        )
    } else if control_point_count == 3
        && interpolation_method == Interpolation::Linear
    {
        // Linear - 3 points.
        let (control_point_a, control_point_b, control_point_c) =
            nonlinear_line_n3(values_x, values_y)?;
        debug!("control_point_a={control_point_a:?}");
        debug!("control_point_b={control_point_b:?}");
        debug!("control_point_c={control_point_c:?}");

        let control_points_x: Vec<Real> = vec![
            control_point_a.x(),
            control_point_b.x(),
            control_point_c.x(),
        ];
        let control_points_y: Vec<Real> = vec![
            control_point_a.y(),
            control_point_b.y(),
            control_point_c.y(),
        ];

        evaluate_curve_points(
            values_x,
            &control_points_x,
            &control_points_y,
            interpolation_method,
        )
    } else if distribution == ControlPointDistribution::Uniform {
        let control_points = nonlinear_line_n_points(
            values_x,
            values_y,
            control_point_count,
            interpolation_method,
        )?;
        debug!("control_points={control_points:?}");

        let control_points_x: Vec<Real> =
            control_points.iter().map(|p| p.x() as Real).collect();
        let control_points_y: Vec<Real> =
            control_points.iter().map(|p| p.y() as Real).collect();

        evaluate_curve_points(
            values_x,
            &control_points_x,
            &control_points_y,
            interpolation_method,
        )
    } else if distribution == ControlPointDistribution::AutoKeypoints {
        let control_points =
            analyze_curve(values_x, values_y, control_point_count)?;
        let control_points_x: Vec<Real> =
            control_points.iter().map(|x| x.time as Real).collect();
        let control_points_y: Vec<Real> =
            control_points.iter().map(|x| x.value as Real).collect();

        let control_points = nonlinear_line_n_points_with_initial(
            values_x,
            values_y,
            &control_points_x,
            &control_points_y,
            interpolation_method,
        )?;
        debug!("control_points={control_points:?}");
        assert_eq!(control_points.len(), control_points_x.len());

        let control_points_x: Vec<Real> =
            control_points.iter().map(|p| p.x() as Real).collect();
        let control_points_y: Vec<Real> =
            control_points.iter().map(|p| p.y() as Real).collect();

        evaluate_curve_points(
            values_x,
            &control_points_x,
            &control_points_y,
            interpolation_method,
        )
    } else {
        error!("Not implemented use case!");
        error!("target_control_points={control_point_count:?}");
        error!("interpolation_method={interpolation_method:?}");
        error!("distribution={distribution:?}");
        Vec::<(Real, Real)>::new()
    };

    Ok(eval_values_xy)
}
