//
// Copyright (C) 2025, 2026 David Cattermole.
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
use nalgebra::{Matrix3, SMatrix, Vector2, Vector3};
use thiserror::Error;

use crate::datatype::BearingVectorCorrespondence;

#[derive(Error, Debug)]
pub enum CameraEssentialMatrixError {
    #[error(
        "Need at least 8 point correspondences to compute essential matrix with 8-point algorithm."
    )]
    InsufficientPointsForEightPoint,
    #[error(
        "Need at least 7 point correspondences to compute essential matrix with 7-point algorithm."
    )]
    InsufficientPointsForSevenPoint,
    #[error(
        "Need at least 6 point correspondences to compute essential matrix with 6-point algorithm."
    )]
    InsufficientPointsForSixPoint,
    #[error(
        "Need exactly 5 point correspondences to compute essential matrix with 5-point algorithm."
    )]
    InvalidPointCountForFivePoint,
    #[error(
        "Need exactly 6 point correspondences to compute essential matrix with 6-point algorithm."
    )]
    InvalidPointCountForSixPoint,
    #[error(
        "Need exactly 7 point correspondences to compute essential matrix with 7-point algorithm."
    )]
    InvalidPointCountForSevenPoint,
    #[error("Cannot compute essential matrix: singular matrix encountered.")]
    SingularMatrix,
    #[error("Invalid input for the algorithm.")]
    InvalidInput,
    #[error("Point correspondence arrays must have the same length.")]
    InvalidDimensions,
    #[error("No valid essential matrix solution found.")]
    NoValidSolution,
}

/// Returns true if a matrix satisfies essential matrix properties.
pub fn is_valid_essential_matrix(essential: &Matrix3<f64>) -> bool {
    if !essential.iter().all(|&x| x.is_finite()) {
        return false;
    }

    let norm = essential.norm();
    if norm < 1e-12 || norm > 1e12 {
        return false;
    }

    let svd = essential.svd(false, false);
    let s = &svd.singular_values;

    if s.len() != 3 {
        return false;
    }

    let mut sorted_s = [s[0], s[1], s[2]];
    sorted_s
        .sort_by(|a, b| b.partial_cmp(a).unwrap_or(std::cmp::Ordering::Equal));

    let s1 = sorted_s[0];
    let s2 = sorted_s[1];
    let s3 = sorted_s[2];

    if s1 < 1e-8 {
        return false;
    }

    // First two singular values should be approximately equal (within 50%),
    // and the third should be much smaller (< 10%).
    let ratio_first_two = (s1 - s2) / s1;
    let ratio_third = s3 / s1;
    ratio_first_two.abs() < 0.5 && ratio_third < 0.1
}

/// Enforce the essential matrix constraint using SVD.
///
/// Reconstructs the matrix with corrected singular values (sigma, sigma, 0).
pub fn enforce_essential_matrix_constraints(
    candidate_matrix: &Matrix3<f64>,
) -> Result<Matrix3<f64>, CameraEssentialMatrixError> {
    let svd_result = candidate_matrix.svd(true, true);
    if let (Some(u), Some(vt)) = (svd_result.u, svd_result.v_t) {
        let singular_values = svd_result.singular_values;

        assert!(
            singular_values.len() == 3,
            "Essential matrix must have exactly 3 singular values"
        );
        assert!(
            singular_values[0] >= singular_values[1]
                && singular_values[1] >= singular_values[2],
            "Singular values must be in descending order"
        );

        let sigma = (singular_values[0] + singular_values[1]) / 2.0;
        assert!(
            sigma > 1e-12,
            "Average of first two singular values must be positive: {}",
            sigma
        );

        let corrected_singular_values = Vector3::new(sigma, sigma, 0.0);
        let diagonal_matrix =
            Matrix3::from_diagonal(&corrected_singular_values);
        let corrected_matrix = u * diagonal_matrix * vt;

        let det = corrected_matrix.determinant();
        assert!(
            det.abs() < 1e-8,
            "Essential matrix determinant should be close to zero after correction: {}",
            det
        );

        Ok(corrected_matrix)
    } else {
        Err(CameraEssentialMatrixError::SingularMatrix)
    }
}

/// Calculate angular reprojection error for a single point correspondence.
///
/// Returns the angle (radians) between the epipolar line and the bearing vector,
/// in the range [0, pi/2].
pub fn calculate_angular_reprojection_error(
    essential_matrix: &Matrix3<f64>,
    x1: &Vector3<f64>,
    x2: &Vector3<f64>,
) -> f64 {
    assert!(x1.norm() > 1e-12, "Input vector x1 must be non-zero");
    assert!(x2.norm() > 1e-12, "Input vector x2 must be non-zero");

    let epipolar_line = essential_matrix * x1;
    assert!(
        epipolar_line.norm() > 1e-12,
        "Epipolar line must be non-zero"
    );

    let normalized_line = epipolar_line / epipolar_line.norm();
    let dot_product = x2.dot(&normalized_line);
    let clamped_dot = dot_product.clamp(-1.0, 1.0);
    let angular_error = clamped_dot.abs().asin();

    assert!(
        angular_error >= 0.0
            && angular_error <= std::f64::consts::PI / 2.0 + 1e-10,
        "Angular error must be in range [0, pi/2]: {}",
        angular_error
    );

    angular_error
}

/// Calculate the average angular reprojection error over a set of correspondences.
pub fn calculate_average_angular_error(
    essential_matrix: &Matrix3<f64>,
    correspondences: &[BearingVectorCorrespondence],
) -> f64 {
    let mut total_error = 0.0;
    for corr in correspondences {
        total_error += calculate_angular_reprojection_error(
            essential_matrix,
            &corr.camera_a,
            &corr.camera_b,
        );
    }
    total_error / correspondences.len() as f64
}

/// Calculate Sampson error for a single point correspondence.
///
/// A first-order approximation to reprojection error.
/// Formula: `(x2^T * E * x1)^2 / (||E*x1||^2 + ||E^T*x2||^2)`
/// where the norms use only the first two (x, y) components.
pub fn calculate_sampson_error(
    essential_matrix: &Matrix3<f64>,
    x1: &Vector3<f64>,
    x2: &Vector3<f64>,
) -> f64 {
    assert!(x1.norm() > 1e-12, "Input vector x1 must be non-zero");
    assert!(x2.norm() > 1e-12, "Input vector x2 must be non-zero");

    let e_x1 = essential_matrix * x1;
    let et_x2 = essential_matrix.transpose() * x2;
    let algebraic_error = x2.dot(&e_x1);
    let e_x1_norm_sq = e_x1.x * e_x1.x + e_x1.y * e_x1.y;
    let et_x2_norm_sq = et_x2.x * et_x2.x + et_x2.y * et_x2.y;
    let denom = e_x1_norm_sq + et_x2_norm_sq;

    if denom < 1e-12 {
        return f64::MAX;
    }

    (algebraic_error * algebraic_error) / denom
}

/// Calculate the average Sampson error over a set of correspondences.
pub fn calculate_average_sampson_error(
    essential_matrix: &Matrix3<f64>,
    correspondences: &[BearingVectorCorrespondence],
) -> f64 {
    let mut total_error = 0.0;
    for corr in correspondences {
        total_error += calculate_sampson_error(
            essential_matrix,
            &corr.camera_a,
            &corr.camera_b,
        );
    }
    total_error / correspondences.len() as f64
}

/// Calculate symmetric epipolar distance for a single point correspondence.
///
/// Measures transfer error in both images symmetrically.
/// Formula: `(x2^T * E * x1)^2 * (1/||E*x1||^2 + 1/||E^T*x2||^2) / 4`
/// where the norms use only the first two (x, y) components.
pub fn calculate_symmetric_epipolar_distance(
    essential_matrix: &Matrix3<f64>,
    x1: &Vector3<f64>,
    x2: &Vector3<f64>,
) -> f64 {
    assert!(x1.norm() > 1e-12, "Input vector x1 must be non-zero");
    assert!(x2.norm() > 1e-12, "Input vector x2 must be non-zero");

    let e_x1 = essential_matrix * x1;
    let et_x2 = essential_matrix.transpose() * x2;
    let algebraic_error = x2.dot(&e_x1);
    let e_x1_norm_sq = e_x1.x * e_x1.x + e_x1.y * e_x1.y;
    let et_x2_norm_sq = et_x2.x * et_x2.x + et_x2.y * et_x2.y;

    if e_x1_norm_sq < 1e-12 || et_x2_norm_sq < 1e-12 {
        return f64::MAX;
    }

    let squared_error = algebraic_error * algebraic_error;
    let symmetric_term = (1.0 / e_x1_norm_sq) + (1.0 / et_x2_norm_sq);
    (squared_error * symmetric_term) / 4.0
}

/// Calculate the average symmetric epipolar distance over a set of correspondences.
pub fn calculate_average_symmetric_epipolar_distance(
    essential_matrix: &Matrix3<f64>,
    correspondences: &[BearingVectorCorrespondence],
) -> f64 {
    let mut total_error = 0.0;
    for corr in correspondences {
        total_error += calculate_symmetric_epipolar_distance(
            essential_matrix,
            &corr.camera_a,
            &corr.camera_b,
        );
    }
    total_error / correspondences.len() as f64
}

/// Calculate epipolar distance for a single point correspondence.
///
/// Measures the distance from a point in image 2 to its epipolar line.
/// Formula: `(x2^T * E * x1)^2 / ||E*x1||^2`
/// where the norm uses only the first two (x, y) components.
pub fn calculate_epipolar_distance(
    essential_matrix: &Matrix3<f64>,
    x1: &Vector3<f64>,
    x2: &Vector3<f64>,
) -> f64 {
    assert!(x1.norm() > 1e-12, "Input vector x1 must be non-zero");
    assert!(x2.norm() > 1e-12, "Input vector x2 must be non-zero");

    let e_x1 = essential_matrix * x1;
    let algebraic_error = x2.dot(&e_x1);
    let e_x1_norm_sq = e_x1.x * e_x1.x + e_x1.y * e_x1.y;

    if e_x1_norm_sq < 1e-12 {
        return f64::MAX;
    }

    (algebraic_error * algebraic_error) / e_x1_norm_sq
}

/// Calculate the average epipolar distance over a set of correspondences.
pub fn calculate_average_epipolar_distance(
    essential_matrix: &Matrix3<f64>,
    correspondences: &[BearingVectorCorrespondence],
) -> f64 {
    let mut total_error = 0.0;
    for corr in correspondences {
        total_error += calculate_epipolar_distance(
            essential_matrix,
            &corr.camera_a,
            &corr.camera_b,
        );
    }
    total_error / correspondences.len() as f64
}

/// Validate that correspondences are unit bearing vectors.
pub fn validate_correspondences(
    correspondences: &[BearingVectorCorrespondence],
) -> Result<(), CameraEssentialMatrixError> {
    assert!(
        !correspondences.is_empty(),
        "Correspondences array cannot be empty"
    );

    for (i, corr) in correspondences.iter().enumerate() {
        let norm_a = corr.camera_a.norm();
        let norm_b = corr.camera_b.norm();

        assert!(
            (norm_a - 1.0).abs() < 1e-10,
            "Correspondence {} camera_a should be a unit vector (norm=1.0): actual norm={}",
            i,
            norm_a
        );
        assert!(
            (norm_b - 1.0).abs() < 1e-10,
            "Correspondence {} camera_b should be a unit vector (norm=1.0): actual norm={}",
            i,
            norm_b
        );
        assert!(
            norm_a > 1e-12,
            "Correspondence {} camera_a vector must be non-zero",
            i
        );
        assert!(
            norm_b > 1e-12,
            "Correspondence {} camera_b vector must be non-zero",
            i
        );
    }

    Ok(())
}

/// Validate that correspondences have non-zero camera coordinate vectors.
pub fn validate_correspondences_homogeneous(
    correspondences: &[BearingVectorCorrespondence],
) -> Result<(), CameraEssentialMatrixError> {
    assert!(
        !correspondences.is_empty(),
        "Correspondences array cannot be empty"
    );

    for (i, corr) in correspondences.iter().enumerate() {
        assert!(
            corr.camera_a.norm() > 1e-12,
            "Correspondence {} camera_a vector must be non-zero",
            i
        );
        assert!(
            corr.camera_b.norm() > 1e-12,
            "Correspondence {} camera_b vector must be non-zero",
            i
        );
    }

    Ok(())
}

/// Returns true if a matrix has valid essential matrix properties.
///
/// Checks that the matrix has rank 2 (determinant close to zero)
/// and the correct singular value structure.
pub fn verify_essential_matrix_properties(
    essential_matrix: &Matrix3<f64>,
    tolerance: f64,
) -> bool {
    let det = essential_matrix.determinant();
    if det.abs() > tolerance {
        return false;
    }

    let svd = essential_matrix.svd(false, false);
    let singular_values = svd.singular_values;

    if singular_values[2] > 0.1 * singular_values[0] {
        return false;
    }

    let ratio =
        (singular_values[0] - singular_values[1]).abs() / singular_values[0];
    if ratio > 0.5 {
        return false;
    }

    true
}

/// Common workspace trait for essential matrix algorithms.
pub trait EssentialMatrixWorkspace {
    /// Create a new workspace with pre-allocated memory.
    fn new() -> Self;

    /// Clear all workspace memory to zero.
    fn clear(&mut self);

    /// Clear the workspace and run the given closure.
    fn reuse_with<F, R>(&mut self, f: F) -> R
    where
        F: FnOnce(&mut Self) -> R;
}

/// Compute Hartley's isotropic normalization transform for a set of 2D points.
///
/// Translates the centroid to the origin and scales so the standard deviation
/// equals 1 per axis. Improves numerical stability of linear solvers.
#[allow(dead_code)]
pub fn compute_hartley_normalization_transform(
    points: &[Vector3<f64>],
) -> Matrix3<f64> {
    assert!(
        !points.is_empty(),
        "Need at least one point for normalization"
    );

    let n = points.len() as f64;
    if n == 0.0 {
        return Matrix3::identity();
    }

    let mut centroid = Vector2::zeros();
    for p in points.iter() {
        if p.z.abs() > 1e-12 {
            centroid.x += p.x / p.z;
            centroid.y += p.y / p.z;
        }
    }
    centroid /= n;

    let mut std_dev_x = 0.0;
    let mut std_dev_y = 0.0;
    for p in points.iter() {
        if p.z.abs() > 1e-12 {
            let x = p.x / p.z - centroid.x;
            let y = p.y / p.z - centroid.y;
            std_dev_x += x * x;
            std_dev_y += y * y;
        }
    }
    std_dev_x = (std_dev_x / n).sqrt();
    std_dev_y = (std_dev_y / n).sqrt();

    let scale_x = if std_dev_x > 1e-12 {
        1.0 / std_dev_x
    } else {
        1.0
    };
    let scale_y = if std_dev_y > 1e-12 {
        1.0 / std_dev_y
    } else {
        1.0
    };

    // Transform: [sx, 0, -sx*cx; 0, sy, -sy*cy; 0, 0, 1]
    Matrix3::new(
        scale_x,
        0.0,
        0.0,
        0.0,
        scale_y,
        0.0,
        -scale_x * centroid.x,
        -scale_y * centroid.y,
        1.0,
    )
}

/// Apply a Hartley normalization transform to a slice of 3D homogeneous points.
// TODO: Refactor function to use mutable slice for output data.
#[allow(dead_code)]
pub fn apply_hartley_transform_to_points(
    points: &[Vector3<f64>],
    transform: &Matrix3<f64>,
) -> Vec<Vector3<f64>> {
    points.iter().map(|p| transform * p).collect()
}

/// Select the essential matrix candidate with the lowest average angular error.
pub fn select_best_candidate_by_angular_error_dynamic(
    candidates: &[Matrix3<f64>],
    correspondences: &[BearingVectorCorrespondence],
) -> Result<Matrix3<f64>, CameraEssentialMatrixError> {
    if candidates.is_empty() {
        return Err(CameraEssentialMatrixError::SingularMatrix);
    }

    let mut best_error = f64::MAX;
    let mut best_matrix = Matrix3::zeros();

    for candidate in candidates {
        let avg_error =
            calculate_average_angular_error(candidate, correspondences);
        if avg_error < best_error {
            best_error = avg_error;
            best_matrix = *candidate;
        }
    }

    if best_error == f64::MAX {
        return Err(CameraEssentialMatrixError::SingularMatrix);
    }

    Ok(best_matrix)
}

/// Build the epipolar constraint matrix from bearing vector correspondences.
///
/// Each correspondence contributes one row such that
/// `constraint_matrix * e = 0` where `e` is the vectorised essential matrix.
/// Requires at least 8 correspondences.
pub fn build_constraint_matrix_bearing_vectors(
    correspondences: &[BearingVectorCorrespondence],
    constraint_matrix: &mut nalgebra::DMatrix<f64>,
) -> Result<(), &'static str> {
    let n_points = correspondences.len();
    if n_points < 8 {
        return Err("Need at least 8 point correspondences");
    }

    if constraint_matrix.nrows() < n_points || constraint_matrix.ncols() != 9 {
        return Err("Constraint matrix has incorrect dimensions");
    }

    for (i, corr) in correspondences.iter().enumerate() {
        let x1 = corr.camera_a.x;
        let y1 = corr.camera_a.y;
        let z1 = corr.camera_a.z;
        let x2 = corr.camera_b.x;
        let y2 = corr.camera_b.y;
        let z2 = corr.camera_b.z;

        constraint_matrix[(i, 0)] = x2 * x1;
        constraint_matrix[(i, 1)] = x2 * y1;
        constraint_matrix[(i, 2)] = x2 * z1;
        constraint_matrix[(i, 3)] = y2 * x1;
        constraint_matrix[(i, 4)] = y2 * y1;
        constraint_matrix[(i, 5)] = y2 * z1;
        constraint_matrix[(i, 6)] = z2 * x1;
        constraint_matrix[(i, 7)] = z2 * y1;
        constraint_matrix[(i, 8)] = z2 * z1;

        let row_norm = constraint_matrix.row(i).norm();
        if !row_norm.is_finite() {
            return Err("Constraint matrix row should be finite");
        }
        if row_norm <= 1e-12 {
            return Err("Constraint matrix row should not be zero");
        }
    }

    Ok(())
}

/// Build the epipolar constraint matrix using static allocation.
///
/// Same as `build_constraint_matrix_bearing_vectors` but uses a statically-sized
/// matrix. Requires at least 8 correspondences and at most `N`.
pub fn build_constraint_matrix_bearing_vectors_static<const N: usize>(
    correspondences: &[BearingVectorCorrespondence],
    constraint_matrix: &mut SMatrix<f64, N, 9>,
) -> Result<(), &'static str> {
    let n_points = correspondences.len();
    if n_points < 8 {
        return Err("Need at least 8 point correspondences");
    }

    if n_points > N {
        return Err("Number of correspondences exceeds static matrix capacity");
    }

    for (i, corr) in correspondences.iter().enumerate() {
        let x1 = corr.camera_a.x;
        let y1 = corr.camera_a.y;
        let z1 = corr.camera_a.z;
        let x2 = corr.camera_b.x;
        let y2 = corr.camera_b.y;
        let z2 = corr.camera_b.z;

        constraint_matrix[(i, 0)] = x2 * x1;
        constraint_matrix[(i, 1)] = x2 * y1;
        constraint_matrix[(i, 2)] = x2 * z1;
        constraint_matrix[(i, 3)] = y2 * x1;
        constraint_matrix[(i, 4)] = y2 * y1;
        constraint_matrix[(i, 5)] = y2 * z1;
        constraint_matrix[(i, 6)] = z2 * x1;
        constraint_matrix[(i, 7)] = z2 * y1;
        constraint_matrix[(i, 8)] = z2 * z1;

        let row_norm = constraint_matrix.row(i).norm();
        if !row_norm.is_finite() {
            return Err("Constraint matrix row should be finite");
        }
        if row_norm <= 1e-12 {
            return Err("Constraint matrix row should not be zero");
        }
    }

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::camera_coord_value::CameraCoordValue;

    #[test]
    fn test_validate_correspondences_valid() {
        let correspondences = vec![
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(-0.5, -0.5),
                CameraCoordValue::vector2(-0.4, -0.6),
            ),
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(0.5, -0.5),
                CameraCoordValue::vector2(0.4, -0.6),
            ),
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(-0.5, 0.5),
                CameraCoordValue::vector2(-0.4, 0.4),
            ),
        ];

        let result = validate_correspondences(&correspondences);
        assert!(result.is_ok());
    }

    #[test]
    fn test_angular_error_calculation() {
        let essential_matrix =
            Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0);

        let x1 = Vector3::new(0.0, 0.0, 1.0);
        let x2 = Vector3::new(0.1, 0.0, 1.0);

        let error =
            calculate_angular_reprojection_error(&essential_matrix, &x1, &x2);

        assert!(error < 1.0, "Angular error should be reasonable: {}", error);
        assert!(error >= 0.0, "Angular error should be non-negative");
    }

    #[test]
    fn test_essential_matrix_constraint_enforcement() {
        let candidate =
            Matrix3::new(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9);

        let result = enforce_essential_matrix_constraints(&candidate);
        assert!(result.is_ok());

        let corrected = result.unwrap();

        assert!(verify_essential_matrix_properties(&corrected, 1e-6));

        let det = corrected.determinant();
        assert!(
            det.abs() < 1e-8,
            "Determinant should be close to zero: {}",
            det
        );
    }

    #[test]
    fn test_verify_essential_matrix_properties() {
        let essential_matrix =
            Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, -0.1, 0.0, 0.1, 0.0);

        assert!(verify_essential_matrix_properties(&essential_matrix, 1e-6));

        let bad_matrix = Matrix3::identity();
        assert!(!verify_essential_matrix_properties(&bad_matrix, 1e-6));
    }

    #[test]
    fn test_sampson_error_calculation() {
        let essential_matrix =
            Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0);

        let x1 = Vector3::new(0.0, 0.0, 1.0);
        let x2 = Vector3::new(0.1, 0.0, 1.0);

        let error = calculate_sampson_error(&essential_matrix, &x1, &x2);

        assert!(error >= 0.0, "Sampson error should be non-negative");
        assert!(error.is_finite(), "Sampson error should be finite");
    }

    #[test]
    fn test_symmetric_epipolar_distance_calculation() {
        let essential_matrix =
            Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0);

        let x1 = Vector3::new(0.0, 0.0, 1.0);
        let x2 = Vector3::new(0.1, 0.0, 1.0);

        let error =
            calculate_symmetric_epipolar_distance(&essential_matrix, &x1, &x2);

        assert!(
            error >= 0.0,
            "Symmetric epipolar error should be non-negative"
        );
        assert!(
            error.is_finite(),
            "Symmetric epipolar error should be finite"
        );
    }

    #[test]
    fn test_epipolar_distance_calculation() {
        let essential_matrix =
            Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.0);

        let x1 = Vector3::new(0.0, 0.0, 1.0);
        let x2 = Vector3::new(0.1, 0.0, 1.0);

        let error = calculate_epipolar_distance(&essential_matrix, &x1, &x2);

        assert!(error >= 0.0, "Epipolar error should be non-negative");
        assert!(error.is_finite(), "Epipolar error should be finite");
    }

    #[test]
    fn test_error_metrics_comparison() {
        use crate::datatype::camera_coord_value::CameraCoordValue;

        let correspondences = vec![
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(-0.5, -0.5),
                CameraCoordValue::vector2(-0.4, -0.6),
            ),
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(0.5, -0.5),
                CameraCoordValue::vector2(0.4, -0.6),
            ),
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(-0.5, 0.5),
                CameraCoordValue::vector2(-0.4, 0.4),
            ),
        ];

        let essential_matrix =
            Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, -0.1, 0.0, 0.1, 0.0);

        let angular_error = calculate_average_angular_error(
            &essential_matrix,
            &correspondences,
        );
        let sampson_error = calculate_average_sampson_error(
            &essential_matrix,
            &correspondences,
        );
        let symmetric_error = calculate_average_symmetric_epipolar_distance(
            &essential_matrix,
            &correspondences,
        );
        let epipolar_error = calculate_average_epipolar_distance(
            &essential_matrix,
            &correspondences,
        );

        assert!(angular_error.is_finite() && angular_error >= 0.0);
        assert!(sampson_error.is_finite() && sampson_error >= 0.0);
        assert!(symmetric_error.is_finite() && symmetric_error >= 0.0);
        assert!(epipolar_error.is_finite() && epipolar_error >= 0.0);

        println!("Angular error: {:.6}", angular_error);
        println!("Sampson error: {:.6}", sampson_error);
        println!("Symmetric epipolar error: {:.6}", symmetric_error);
        println!("Epipolar error: {:.6}", epipolar_error);
    }

    #[test]
    fn test_select_best_candidate_by_angular_error() {
        let candidates = vec![
            Matrix3::new(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9),
            Matrix3::new(0.0, 0.0, 0.0, 0.0, 0.0, -0.1, 0.0, 0.1, 0.0),
        ];

        use crate::datatype::camera_coord_value::CameraCoordValue;
        let correspondences = vec![
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(-0.5, -0.5),
                CameraCoordValue::vector2(-0.4, -0.6),
            ),
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(0.5, -0.5),
                CameraCoordValue::vector2(0.4, -0.6),
            ),
            BearingVectorCorrespondence::new(
                CameraCoordValue::vector2(-0.5, 0.5),
                CameraCoordValue::vector2(-0.4, 0.4),
            ),
        ];

        let result = select_best_candidate_by_angular_error_dynamic(
            &candidates,
            &correspondences,
        );

        assert!(result.is_ok(), "Should select a candidate");
    }
}
