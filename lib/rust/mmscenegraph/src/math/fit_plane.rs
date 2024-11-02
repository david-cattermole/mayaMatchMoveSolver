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

use log::error;
use nalgebra::{Matrix3xX, Vector3};

/// Represents a 3D plane.
#[derive(Debug, Clone)]
pub struct PlaneFit {
    /// Centroid point that lies on the plane.
    pub position: Vector3<f64>,
    /// Normal vector.
    pub normal: Vector3<f64>,
    /// Root mean square error of the fit.
    pub rms_error: f64,
}

const NUMBER_OF_POINT_COMPONENTS: usize = 3;
const MINIMUM_POINT_COUNT: usize = 3;

/// Calculate the Root Mean Square (RMS) error of the fit.
fn calculate_rms_error(
    points: &[f64],
    normal: &Vector3<f64>,
    position: &Vector3<f64>,
) -> f64 {
    let mse = points
        .chunks_exact(NUMBER_OF_POINT_COMPONENTS)
        .map(|p| {
            let point = Vector3::new(p[0], p[1], p[2]);
            // Distance from point to the 3D plane, along the plane normal.
            let dist = (point - position).dot(normal);
            dist * dist
        })
        .sum::<f64>()
        / points.len() as f64;
    mse.sqrt()
}

/// Fits a 3D plane to a set of points using Singular Value Decomposition (SVD).
///
/// # Arguments
/// * `points` - A slice of 3D point components to fit the plane to.
///              Each value is expected to be part of a 3D point (XYZ).
///
/// # Returns
/// * `Option<PlaneFit>` - Returns None if fitting fails or input is empty.
//
// Based on:
// https://math.stackexchange.com/questions/99299/best-fitting-plane-given-a-set-of-points
//
pub fn fit_plane_to_points(points_xyz: &[f64]) -> Option<PlaneFit> {
    if points_xyz.len() < (NUMBER_OF_POINT_COMPONENTS * MINIMUM_POINT_COUNT) {
        error!("Need at least 3 points to define a plane.");
        return None;
    }
    let remainder = points_xyz.len().rem_euclid(NUMBER_OF_POINT_COMPONENTS);
    if remainder != 0 {
        error!("Number of point component values is not divisible by 3.");
        return None;
    }
    let point_count = points_xyz.len().div_euclid(NUMBER_OF_POINT_COMPONENTS);

    // Calculate centroid.
    let position = points_xyz
        .chunks_exact(NUMBER_OF_POINT_COMPONENTS)
        .fold(Vector3::zeros(), |acc, p| {
            acc + Vector3::new(p[0], p[1], p[2])
        })
        / point_count as f64;

    // Create matrix of points with centroid subtracted.
    let mut centered_points = Matrix3xX::zeros(point_count);
    for (i, point) in points_xyz
        .chunks_exact(NUMBER_OF_POINT_COMPONENTS)
        .enumerate()
    {
        let point = Vector3::new(point[0], point[1], point[2]);
        let centered = point - position;
        centered_points.set_column(i, &centered);
    }

    // Perform Singular Value Decomposition (SVD).
    let svd = centered_points.svd(true, true);
    match svd.u {
        Some(u_value) => {
            // The normal vector is the last left singular vector
            // (corresponding to smallest singular value).
            let normal = u_value.column(2).normalize();

            // Calculate RMS error.
            let rms_error = calculate_rms_error(points_xyz, &normal, &position);

            Some(PlaneFit {
                normal,
                position,
                rms_error,
            })
        }
        None => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    #[test]
    fn test_insufficient_points() {
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            0.0, 0.0, 0.0,
            // Point B.
            1.0, 0.0, 0.0,
        ];

        let result = fit_plane_to_points(&points);
        assert!(result.is_none());
    }

    #[test]
    fn test_perfect_plane() {
        // Points exactly on Z = 1 plane.
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            0.0, 0.0, 1.0,
            // Point B.
            1.0, 0.0, 1.0,
            // Point C.
            0.0, 1.0, 1.0,
            // Point D.
            1.0, 1.0, 1.0,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal should be (0, 0, 1) or (0, 0, -1).
        assert_relative_eq!(result.normal.x.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.z.abs(), 1.0, epsilon = 1e-10);

        // Error should be zero.
        assert_relative_eq!(result.rms_error, 0.0, epsilon = 1e-10);

        // Centroid should be at (0.5, 0.5, 1.0).
        assert_relative_eq!(result.position.x, 0.5, epsilon = 1e-10);
        assert_relative_eq!(result.position.y, 0.5, epsilon = 1e-10);
        assert_relative_eq!(result.position.z, 1.0, epsilon = 1e-10);
    }

    #[test]
    fn test_perfect_plane_xy() {
        // Points exactly on Z = 0 plane (XY plane).
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            0.0, 0.0, 0.0,
            // Point B.
            1.0, 0.0, 0.0,
            // Point C.
            0.0, 1.0, 0.0,
            // Point D.
            1.0, 1.0, 0.0,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        assert_relative_eq!(result.normal.x.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.z.abs(), 1.0, epsilon = 1e-10);
        assert_relative_eq!(result.rms_error, 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.position.z, 0.0, epsilon = 1e-10);
    }

    #[test]
    fn test_perfect_plane_yz() {
        // Points exactly on X = 0 plane (YZ plane).
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            0.0, 0.0, 0.0,
            // Point B.
            0.0, 1.0, 0.0,
            // Point C.
            0.0, 0.0, 1.0,
            // Point D.
            0.0, 1.0, 1.0,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        assert_relative_eq!(result.normal.x.abs(), 1.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.z.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.rms_error, 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.position.x, 0.0, epsilon = 1e-10);
    }

    #[test]
    fn test_noisy_plane() {
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            0.0, 0.0, 0.1, // Slightly off Z=0.
            // Point B.
            1.0, 0.0, -0.1,
            // Point C.
            0.0, 1.0, 0.05,
            // Point D.
            1.0, 1.0, -0.05,
            // Point E.
            0.5, 0.5, 0.02,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal should be approximately (0,0,1).
        assert_relative_eq!(result.normal.x.abs(), 0.0, epsilon = 0.2);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 0.2);
        assert_relative_eq!(result.normal.z.abs(), 1.0, epsilon = 0.2);

        // RMS error should be non-zero but small.
        assert!(result.rms_error > 0.0);
        assert!(result.rms_error < 0.1);
    }

    #[test]
    fn test_diagonal_plane() {
        // Points on a 45-degree plane in XZ plane.
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            0.0, 0.0, 0.0,
            // Point A.
            1.0, 0.0, 1.0,
            // Point A.
            0.0, 1.0, 0.0,
            // Point A.
            1.0, 1.0, 1.0,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal should be approximately (-0.707, 0, 0.707) or (0.707, 0, -0.707).
        let expected = 1.0 / (2.0_f64).sqrt();
        assert_relative_eq!(result.normal.x.abs(), expected, epsilon = 0.1);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 0.1);
        assert_relative_eq!(result.normal.z.abs(), expected, epsilon = 0.1);
    }

    #[test]
    fn test_diagonal_plane2() {
        // Non-basic set of data that should sit exactly on a single
        // plane (but not on a specific X, Y or Z axis).
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            0.23187438856586118,
            1.5294821321729188,
            3.96563929785732,
            // Point B.
            -1.9622161750992408,
            1.657941819388819,
            1.8128563375741764,
            // Point C.
            -1.7176317861440111,
            2.0976720852595037,
            3.840488903778578,
            // Point D.
            -0.3124119090726335,
            0.7355336125066458,
            0.1802607123005422,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        assert_relative_eq!(
            result.position.x,
            -0.9400963704375062,
            epsilon = 1e-9
        );
        assert_relative_eq!(
            result.position.y,
            1.5051574123319718,
            epsilon = 1e-9
        );
        assert_relative_eq!(
            result.position.z,
            2.4498113128776544,
            epsilon = 1e-9
        );

        assert_relative_eq!(
            result.normal.x.abs(),
            0.2858418422230164,
            epsilon = 1e-9
        );
        assert_relative_eq!(
            result.normal.y.abs(),
            0.9287860236344114,
            epsilon = 1e-9
        );
        assert_relative_eq!(
            result.normal.z.abs(),
            0.23590456446608005,
            epsilon = 1e-9
        );

        assert_relative_eq!(result.rms_error, 0.0, epsilon = 1e-9);
    }

    #[test]
    fn test_minimal_points() {
        // Test with exactly 3 points.
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            0.0, 0.0, 0.0,
            // Point B.
            1.0, 0.0, 0.0,
            // Point C.
            0.0, 1.0, 0.0,
        ];

        let result = fit_plane_to_points(&points);
        assert!(result.is_some());
    }

    #[test]
    fn test_colinear_points() {
        // Points in a straight line shouldn't define a unique plane.
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            0.0, 0.0, 0.0,
            // Point B.
            1.0, 1.0, 1.0,
            // Point C.
            2.0, 2.0, 2.0,
            // Point D.
            3.0, 3.0, 3.0,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // The fit should still work, but any plane containing the
        // line is valid.  We should just verify that the normal is
        // perpendicular to the line direction.
        let line_direction = Vector3::new(1.0, 1.0, 1.0).normalize();
        let dot_product = result.normal.dot(&line_direction).abs();
        assert_relative_eq!(dot_product, 0.0, epsilon = 1e-10);
    }

    #[test]
    fn test_large_scale_plane() {
        // Test with points at larger coordinates
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            1000.0, 1000.0, 1000.0,
            // Point B.
            1001.0, 1000.0, 1000.0,
            // Point C.
            1000.0, 1001.0, 1000.0,
            // Point D.
            1001.0, 1001.0, 1000.0,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal should still be well-behaved.
        assert_relative_eq!(result.normal.x.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.z.abs(), 1.0, epsilon = 1e-10);
    }

    #[test]
    fn test_normal_properties() {
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            1.0, 2.0, 3.0,
            // Point B.
            4.0, 5.0, 6.0,
            // Point C.
            7.0, 8.0, 9.0,
            // Point D.
            10.0, 11.0, 12.0,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal vector should be unit length.
        assert_relative_eq!(result.normal.norm(), 1.0, epsilon = 1e-10);

        // Normal should be perpendicular to any vector in the plane.
        let point_a = Vector3::new(points[0], points[1], points[2]);
        let point_b = Vector3::new(points[3], points[4], points[5]);
        let in_plane_vector = point_b - point_a;
        let dot_product = result.normal.dot(&in_plane_vector);
        assert_relative_eq!(dot_product, 0.0, epsilon = 1e-8);
    }

    #[test]
    fn test_position_centroid_property() {
        #[rustfmt::skip]
        let points = vec![
            // Point A.
            1.0, 0.0, 0.0,
            // Point B.
            -1.0, 0.0, 0.0,
            // Point C.
            0.0, 1.0, 0.0,
            // Point D.
            0.0, -1.0, 0.0,
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Position should be at centroid (0,0,0).
        assert_relative_eq!(result.position.x, 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.position.y, 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.position.z, 0.0, epsilon = 1e-10);
    }
}
