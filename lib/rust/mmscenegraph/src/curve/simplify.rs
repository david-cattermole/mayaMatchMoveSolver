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
use crate::math::curve_fit::nonlinear_line_n3_with_initial;
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
    } else if control_point_count == 3 {
        // All 3-point cases use the dedicated N3 solver for better robustness
        if distribution == ControlPointDistribution::AutoKeypoints {
            // Use auto_keypoints with dedicated N3 solver
            match try_auto_keypoints_n3_simplify(
                values_x,
                values_y,
                interpolation_method,
            ) {
                Ok(eval_values_xy) => {
                    debug!("auto_keypoints N3 succeeded");
                    eval_values_xy
                }
                Err(e) => {
                    debug!("auto_keypoints N3 failed: {}, falling back to uniform N3", e);
                    error!("auto_keypoints N3 failed: {}, falling back to uniform N3", e);

                    // Fallback to uniform distribution with N3 solver
                    let (control_point_a, control_point_b, control_point_c) =
                        nonlinear_line_n3(values_x, values_y)?;
                    debug!("fallback N3 control_point_a={control_point_a:?}");
                    debug!("fallback N3 control_point_b={control_point_b:?}");
                    debug!("fallback N3 control_point_c={control_point_c:?}");

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
                }
            }
        } else {
            // Uniform distribution - use N3 solver with linear regression initialization
            let (control_point_a, control_point_b, control_point_c) =
                nonlinear_line_n3(values_x, values_y)?;
            debug!("uniform N3 control_point_a={control_point_a:?}");
            debug!("uniform N3 control_point_b={control_point_b:?}");
            debug!("uniform N3 control_point_c={control_point_c:?}");

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
        }
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
        // Try auto_keypoints first, fallback to uniform distribution if it fails
        match try_auto_keypoints_simplify(
            values_x,
            values_y,
            control_point_count,
            interpolation_method,
        ) {
            Ok(eval_values_xy) => {
                debug!("auto_keypoints succeeded");
                eval_values_xy
            }
            Err(e) => {
                debug!("auto_keypoints failed: {}, falling back to uniform distribution", e);
                error!("auto_keypoints failed: {}, falling back to uniform distribution", e);

                // Fallback to uniform distribution
                let control_points = nonlinear_line_n_points(
                    values_x,
                    values_y,
                    control_point_count,
                    interpolation_method,
                )?;
                debug!("fallback control_points={control_points:?}");

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
            }
        }
    } else {
        error!("Not implemented use case!");
        error!("target_control_points={control_point_count:?}");
        error!("interpolation_method={interpolation_method:?}");
        error!("distribution={distribution:?}");
        Vec::<(Real, Real)>::new()
    };

    Ok(eval_values_xy)
}

/// Attempts auto_keypoints simplification specifically for 3-point cases using the robust N3 solver.
/// Returns the evaluated curve points if successful, or an error if it fails.
fn try_auto_keypoints_n3_simplify(
    values_x: &[Real],
    values_y: &[Real],
    interpolation_method: Interpolation,
) -> Result<Vec<(Real, Real)>> {
    debug!("try_auto_keypoints_n3_simplify: using dedicated 3-point N3 solver");
    debug!(
        "try_auto_keypoints_n3_simplify: interpolation_method={:?}",
        interpolation_method
    );

    // Detect keypoints using pyramid analysis (always 3 points for this function)
    let control_points = analyze_curve(values_x, values_y, 3)?;
    debug!(
        "try_auto_keypoints_n3_simplify: detected {} keypoints",
        control_points.len()
    );

    let control_points_x: Vec<Real> =
        control_points.iter().map(|x| x.time as Real).collect();
    let control_points_y: Vec<Real> =
        control_points.iter().map(|x| x.value as Real).collect();

    // Validate keypoint positions for potential optimization issues
    if let Err(validation_error) =
        validate_keypoint_positions(&control_points_x, &control_points_y)
    {
        debug!(
            "try_auto_keypoints_n3_simplify: keypoint validation failed: {}",
            validation_error
        );
        return Err(validation_error);
    }

    // Use the dedicated N3 solver with detected keypoint positions
    let (control_point_a, control_point_b, control_point_c) =
        nonlinear_line_n3_with_initial(
            values_x,
            values_y,
            &control_points_x,
            &control_points_y,
        )?;
    debug!("try_auto_keypoints_n3_simplify: N3 optimization succeeded");
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

    let eval_values_xy = evaluate_curve_points(
        values_x,
        &control_points_x,
        &control_points_y,
        interpolation_method,
    );

    Ok(eval_values_xy)
}

/// Attempts auto_keypoints simplification with detailed error handling.
/// Returns the evaluated curve points if successful, or an error if it fails.
fn try_auto_keypoints_simplify(
    values_x: &[Real],
    values_y: &[Real],
    control_point_count: usize,
    interpolation_method: Interpolation,
) -> Result<Vec<(Real, Real)>> {
    debug!(
        "try_auto_keypoints_simplify: control_point_count={}",
        control_point_count
    );
    debug!(
        "try_auto_keypoints_simplify: interpolation_method={:?}",
        interpolation_method
    );

    // Detect keypoints using pyramid analysis
    let control_points =
        analyze_curve(values_x, values_y, control_point_count)?;
    debug!(
        "try_auto_keypoints_simplify: detected {} keypoints",
        control_points.len()
    );

    let control_points_x: Vec<Real> =
        control_points.iter().map(|x| x.time as Real).collect();
    let control_points_y: Vec<Real> =
        control_points.iter().map(|x| x.value as Real).collect();

    // Validate keypoint positions for potential optimization issues
    if let Err(validation_error) =
        validate_keypoint_positions(&control_points_x, &control_points_y)
    {
        debug!(
            "try_auto_keypoints_simplify: keypoint validation failed: {}",
            validation_error
        );
        return Err(validation_error);
    }

    // Attempt optimization with the detected keypoints
    let control_points = nonlinear_line_n_points_with_initial(
        values_x,
        values_y,
        &control_points_x,
        &control_points_y,
        interpolation_method,
    )?;
    debug!("try_auto_keypoints_simplify: optimization succeeded, control_points={:?}", control_points);
    assert_eq!(control_points.len(), control_points_x.len());

    let control_points_x: Vec<Real> =
        control_points.iter().map(|p| p.x() as Real).collect();
    let control_points_y: Vec<Real> =
        control_points.iter().map(|p| p.y() as Real).collect();

    let eval_values_xy = evaluate_curve_points(
        values_x,
        &control_points_x,
        &control_points_y,
        interpolation_method,
    );

    Ok(eval_values_xy)
}

/// Validates keypoint positions to detect potential optimization issues.
fn validate_keypoint_positions(
    control_points_x: &[Real],
    control_points_y: &[Real],
) -> Result<()> {
    if control_points_x.len() != control_points_y.len() {
        anyhow::bail!("Mismatched control point array lengths");
    }

    if control_points_x.len() < 2 {
        anyhow::bail!("Insufficient control points for optimization");
    }

    // Check for minimum spacing between control points
    let total_range =
        control_points_x[control_points_x.len() - 1] - control_points_x[0];
    let min_spacing = total_range / (control_points_x.len() as Real * 10.0); // 10% of average spacing

    for i in 1..control_points_x.len() {
        let spacing = control_points_x[i] - control_points_x[i - 1];
        if spacing < min_spacing {
            anyhow::bail!(
                "Control points too close together: spacing={}, min_spacing={}",
                spacing,
                min_spacing
            );
        }
    }

    // Check for extreme Y values that might cause numerical issues
    for &y in control_points_y {
        if !y.is_finite() {
            anyhow::bail!("Non-finite Y value detected: {}", y);
        }
        if y.abs() > 1e6 {
            anyhow::bail!("Extreme Y value detected: {}", y);
        }
    }

    Ok(())
}
