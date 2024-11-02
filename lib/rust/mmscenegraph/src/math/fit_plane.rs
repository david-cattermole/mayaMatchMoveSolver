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

use nalgebra as na;
use nalgebra::{DMatrix, Matrix3xX, Vector3};

/// Represents a 3D plane.
#[derive(Debug, Clone)]
pub struct PlaneFit {
    /// Normal vector.
    pub normal: Vector3<f64>,
    /// Centroid point that lies on the plane.
    pub position: Vector3<f64>,
    /// Root mean square error of the fit.
    pub rms_error: f64,
}

/// Calculate the RMS error of the fit.
fn calculate_rms_error(
    points: &[Vector3<f64>],
    normal: &Vector3<f64>,
    position: &Vector3<f64>,
) -> f64 {
    let squared_errors: Vec<f64> = points
        .iter()
        .map(|p| {
            let dist = (p - position).dot(normal);
            dist * dist
        })
        .collect();

    let mse = squared_errors.iter().sum::<f64>() / points.len() as f64;
    mse.sqrt()
}

/// Fits a 3D plane to a set of points using Singular Value Decomposition (SVD).
///
/// # Arguments
/// * `points` - A slice of 3D points to fit the plane to. Each point should be a Vector3.
///
/// # Returns
/// * `Option<PlaneFit>` - Returns None if fitting fails or input is empty.
//
// Based on:
// https://math.stackexchange.com/questions/99299/best-fitting-plane-given-a-set-of-points
//
pub fn fit_plane_to_points(points: &[Vector3<f64>]) -> Option<PlaneFit> {
    if points.len() < 3 {
        return None; // Need at least 3 points to define a plane
    }

    // Calculate centroid
    let position = points.iter().fold(Vector3::zeros(), |acc, p| acc + p)
        / points.len() as f64;

    // Create matrix of points with centroid subtracted
    let mut centered_points = Matrix3xX::zeros(points.len());
    for (i, point) in points.iter().enumerate() {
        let centered = point - position;
        centered_points.set_column(i, &centered);
    }

    // Perform SVD
    let svd = centered_points.svd(true, true);
    match svd.u {
        Some(u_value) => {
            // The normal vector is the last left singular vector
            // (corresponding to smallest singular value)
            let normal = u_value.column(2).normalize();

            // Calculate RMS error
            let rms_error = calculate_rms_error(points, &normal, &position);

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
        let points =
            vec![Vector3::new(0.0, 0.0, 0.0), Vector3::new(1.0, 0.0, 0.0)];

        let result = fit_plane_to_points(&points);
        assert!(result.is_none());
    }

    #[test]
    fn test_perfect_plane() {
        // Points exactly on Z = 1 plane
        let points = vec![
            Vector3::new(0.0, 0.0, 1.0),
            Vector3::new(1.0, 0.0, 1.0),
            Vector3::new(0.0, 1.0, 1.0),
            Vector3::new(1.0, 1.0, 1.0),
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal should be (0, 0, 1) or (0, 0, -1).
        assert_relative_eq!(result.normal.x.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.z.abs(), 1.0, epsilon = 1e-10);

        // Error should be zero
        assert_relative_eq!(result.rms_error, 0.0, epsilon = 1e-10);

        // Centroid should be at (0.5, 0.5, 1.0)
        assert_relative_eq!(result.position.x, 0.5, epsilon = 1e-10);
        assert_relative_eq!(result.position.y, 0.5, epsilon = 1e-10);
        assert_relative_eq!(result.position.z, 1.0, epsilon = 1e-10);
    }

    #[test]
    fn test_perfect_plane_xy() {
        // Points exactly on Z = 0 plane (XY plane)
        let points = vec![
            Vector3::new(0.0, 0.0, 0.0),
            Vector3::new(1.0, 0.0, 0.0),
            Vector3::new(0.0, 1.0, 0.0),
            Vector3::new(1.0, 1.0, 0.0),
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
        // Points exactly on X = 0 plane (YZ plane)
        let points = vec![
            Vector3::new(0.0, 0.0, 0.0),
            Vector3::new(0.0, 1.0, 0.0),
            Vector3::new(0.0, 0.0, 1.0),
            Vector3::new(0.0, 1.0, 1.0),
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
        let points = vec![
            Vector3::new(0.0, 0.0, 0.1), // Slightly off Z=0
            Vector3::new(1.0, 0.0, -0.1),
            Vector3::new(0.0, 1.0, 0.05),
            Vector3::new(1.0, 1.0, -0.05),
            Vector3::new(0.5, 0.5, 0.02),
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal should be approximately (0,0,1)
        assert_relative_eq!(result.normal.x.abs(), 0.0, epsilon = 0.2);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 0.2);
        assert_relative_eq!(result.normal.z.abs(), 1.0, epsilon = 0.2);

        // RMS error should be non-zero but small
        assert!(result.rms_error > 0.0);
        assert!(result.rms_error < 0.1);
    }

    #[test]
    fn test_diagonal_plane() {
        // Points on a 45-degree plane in XZ plane
        let points = vec![
            Vector3::new(0.0, 0.0, 0.0),
            Vector3::new(1.0, 0.0, 1.0),
            Vector3::new(0.0, 1.0, 0.0),
            Vector3::new(1.0, 1.0, 1.0),
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal should be approximately (-0.707, 0, 0.707) or (0.707, 0, -0.707)
        let expected = 1.0 / (2.0_f64).sqrt();
        assert_relative_eq!(result.normal.x.abs(), expected, epsilon = 0.1);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 0.1);
        assert_relative_eq!(result.normal.z.abs(), expected, epsilon = 0.1);
    }

    #[test]
    fn test_minimal_points() {
        // Test with exactly 3 points
        let points = vec![
            Vector3::new(0.0, 0.0, 0.0),
            Vector3::new(1.0, 0.0, 0.0),
            Vector3::new(0.0, 1.0, 0.0),
        ];

        let result = fit_plane_to_points(&points);
        assert!(result.is_some());
    }

    #[test]
    fn test_colinear_points() {
        // Points in a straight line shouldn't define a unique plane
        let points = vec![
            Vector3::new(0.0, 0.0, 0.0),
            Vector3::new(1.0, 1.0, 1.0),
            Vector3::new(2.0, 2.0, 2.0),
            Vector3::new(3.0, 3.0, 3.0),
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // The fit should still work, but any plane containing the line is valid
        // We should just verify that the normal is perpendicular to the line direction
        let line_direction = Vector3::new(1.0, 1.0, 1.0).normalize();
        let dot_product = result.normal.dot(&line_direction).abs();
        assert_relative_eq!(dot_product, 0.0, epsilon = 1e-10);
    }

    #[test]
    fn test_large_scale_plane() {
        // Test with points at larger coordinates
        let points = vec![
            Vector3::new(1000.0, 1000.0, 1000.0),
            Vector3::new(1001.0, 1000.0, 1000.0),
            Vector3::new(1000.0, 1001.0, 1000.0),
            Vector3::new(1001.0, 1001.0, 1000.0),
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal should still be well-behaved
        assert_relative_eq!(result.normal.x.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.y.abs(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.normal.z.abs(), 1.0, epsilon = 1e-10);
    }

    #[test]
    fn test_normal_properties() {
        let points = vec![
            Vector3::new(1.0, 2.0, 3.0),
            Vector3::new(4.0, 5.0, 6.0),
            Vector3::new(7.0, 8.0, 9.0),
            Vector3::new(10.0, 11.0, 12.0),
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Normal vector should be unit length
        assert_relative_eq!(result.normal.norm(), 1.0, epsilon = 1e-10);

        // Normal should be perpendicular to any vector in the plane
        let in_plane_vector = points[1] - points[0];
        let dot_product = result.normal.dot(&in_plane_vector);
        assert_relative_eq!(dot_product, 0.0, epsilon = 1e-8);
    }

    #[test]
    fn test_position_centroid_property() {
        let points = vec![
            Vector3::new(1.0, 0.0, 0.0),
            Vector3::new(-1.0, 0.0, 0.0),
            Vector3::new(0.0, 1.0, 0.0),
            Vector3::new(0.0, -1.0, 0.0),
        ];

        let result =
            fit_plane_to_points(&points).expect("Plane fitting failed");

        // Position should be at centroid (0,0,0)
        assert_relative_eq!(result.position.x, 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.position.y, 0.0, epsilon = 1e-10);
        assert_relative_eq!(result.position.z, 0.0, epsilon = 1e-10);
    }
}
