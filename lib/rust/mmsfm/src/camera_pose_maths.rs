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

use nalgebra::{Matrix3, Matrix3x4, RealField, Vector3};

use crate::datatype::common::UnitValue;
use crate::datatype::{CameraIntrinsics, CameraPose};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Create a 3x4 camera projection matrix from pose and intrinsics.
pub fn create_projection_matrix(
    pose: &CameraPose,
    camera_intrinsics: &CameraIntrinsics,
) -> Matrix3x4<f64> {
    let focal_length_x = camera_intrinsics.focal_length_x;
    let focal_length_y = camera_intrinsics.focal_length_y;
    let principal_point_x = camera_intrinsics.principal_point.x.value();
    let principal_point_y = camera_intrinsics.principal_point.y.value();

    let intrinsic_matrix = Matrix3::new(
        focal_length_x,
        0.0,
        principal_point_x,
        0.0,
        focal_length_y,
        principal_point_y,
        0.0,
        0.0,
        1.0,
    );

    let extrinsic_matrix = pose.as_extrinsic_matrix();
    intrinsic_matrix * extrinsic_matrix
}

/// Decompose a 3x4 projection matrix into intrinsic matrix, rotation, and translation.
///
/// Uses RQ decomposition on the first 3x3 block to extract the upper-triangular
/// intrinsic matrix and orthogonal rotation matrix.
///
/// Returns `Some((intrinsics, rotation, translation))` or `None` if the matrix is singular.
fn decompose_projection_matrix<T: RealField + Copy>(
    projection_matrix: &Matrix3x4<T>,
) -> Option<(Matrix3<T>, Matrix3<T>, Vector3<T>)> {
    // Extract first 3x3 block (intrinsics * rotation).
    let intrinsic_rotation_block =
        projection_matrix.fixed_view::<3, 3>(0, 0).into_owned();

    // QR decomposition on the transpose gives us RQ decomposition.
    let qr = intrinsic_rotation_block.transpose().qr();
    let mut intrinsic_matrix = qr.r().transpose();
    let mut rotation = qr.q().transpose();

    // Ensure the intrinsic matrix diagonal is positive (sign convention).
    for i in 0..3 {
        if intrinsic_matrix[(i, i)] < T::zero() {
            for j in 0..3 {
                intrinsic_matrix[(i, j)] = -intrinsic_matrix[(i, j)];
            }
            for j in 0..3 {
                rotation[(j, i)] = -rotation[(j, i)];
            }
        }
    }

    // Normalize so the bottom-right entry is 1.
    let scale = intrinsic_matrix[(2, 2)];
    if scale.abs() < T::from_f64(1e-10).unwrap() {
        return None;
    }
    intrinsic_matrix /= scale;

    // Extract translation: t = K^-1 * last_column.
    let last_column = Vector3::new(
        projection_matrix[(0, 3)],
        projection_matrix[(1, 3)],
        projection_matrix[(2, 3)],
    );
    let intrinsic_inverse = intrinsic_matrix.try_inverse()?;
    let translation = intrinsic_inverse * last_column;

    Some((intrinsic_matrix, rotation, translation))
}

/// Compute the relative rotation and translation from camera A to camera B.
fn compute_relative_pose<T: RealField + Copy>(
    rotation_a: &Matrix3<T>,
    translation_a: &Vector3<T>,
    rotation_b: &Matrix3<T>,
    translation_b: &Vector3<T>,
) -> (Matrix3<T>, Vector3<T>) {
    // Camera centers in world space: C = -R^T * t.
    let center_a = -(rotation_a.transpose() * translation_a);
    let center_b = -(rotation_b.transpose() * translation_b);

    let relative_rotation = rotation_b * rotation_a.transpose();

    // Translate the difference in camera centers into camera B's frame.
    let relative_translation = rotation_b * (center_a - center_b);

    (relative_rotation, relative_translation)
}

/// Compute the fundamental matrix relating corresponding points between two camera views.
///
/// For corresponding points `x` in camera A and `x'` in camera B:
/// `x'^T * F * x = 0`
///
/// Returns `Some(F)` or `None` if the computation fails.
pub fn compute_fundamental_matrix<T: RealField + Copy>(
    camera_a: &Matrix3x4<T>,
    camera_b: &Matrix3x4<T>,
) -> Option<Matrix3<T>> {
    mm_debug_eprintln!("\n[DEBUG compute_fundamental_matrix]");
    mm_debug_eprintln!("camera_a = {:?}", camera_a);
    mm_debug_eprintln!("camera_b = {:?}", camera_b);

    let (intrinsic_a, rotation_a, translation_a) =
        decompose_projection_matrix(camera_a)?;
    let (intrinsic_b, rotation_b, translation_b) =
        decompose_projection_matrix(camera_b)?;

    mm_debug_eprintln!("intrinsic_a = {:?}", intrinsic_a);
    mm_debug_eprintln!("rotation_a = {:?}", rotation_a);
    mm_debug_eprintln!("translation_a = {:?}", translation_a);
    mm_debug_eprintln!("intrinsic_b = {:?}", intrinsic_b);
    mm_debug_eprintln!("rotation_b = {:?}", rotation_b);
    mm_debug_eprintln!("translation_b = {:?}", translation_b);

    let (relative_rotation, relative_translation) = compute_relative_pose(
        &rotation_a,
        &translation_a,
        &rotation_b,
        &translation_b,
    );

    // Essential matrix: E = [t]x * R.
    let translation_cross = relative_translation.cross_matrix();
    let essential_matrix = translation_cross * relative_rotation;

    // F = K_b^-T * E * K_a^-1.
    let intrinsic_a_inv = intrinsic_a.try_inverse()?;
    let intrinsic_b_inv = intrinsic_b.try_inverse()?;
    let fundamental =
        intrinsic_b_inv.transpose() * essential_matrix * intrinsic_a_inv;

    // Fundamental matrix should have rank 2 (determinant near zero).
    let det = fundamental.determinant();
    let norm = fundamental.norm();

    if norm < T::from_f64(1e-12).unwrap() || norm > T::from_f64(1e12).unwrap() {
        return None;
    }

    // Determinant scales with norm^3 for a 3x3 matrix.
    let tolerance = T::from_f64(1e-6).unwrap() * norm * norm * norm;
    if det.abs() > tolerance {
        // Enforce rank-2 constraint via SVD.
        let svd = fundamental.svd(true, true);
        let u = svd.u.unwrap();
        let vt = svd.v_t.unwrap();

        let mut singular_values = svd.singular_values;
        let mut indices: Vec<usize> = (0..3).collect();
        indices.sort_by(|&i, &j| {
            singular_values[j]
                .partial_cmp(&singular_values[i])
                .unwrap_or(std::cmp::Ordering::Equal)
        });
        singular_values[indices[2]] = T::zero();

        let sigma = Matrix3::from_diagonal(&singular_values);
        return Some(u * sigma * vt);
    }

    Some(fundamental)
}

#[cfg(test)]
mod tests {
    use super::*;
    use nalgebra::{Matrix3, Matrix3x4};

    fn create_simple_test_cameras<T: RealField + Copy>(
    ) -> (Matrix3x4<T>, Matrix3x4<T>, Matrix3<T>) {
        // Create two simple cameras looking at the same scene.
        let mut camera_a = Matrix3x4::zeros();
        camera_a[(0, 0)] = T::from_f64(100.0).unwrap();
        camera_a[(1, 1)] = T::from_f64(100.0).unwrap();
        camera_a[(2, 2)] = T::one();

        let mut camera_b = Matrix3x4::zeros();
        camera_b[(0, 0)] = T::from_f64(100.0).unwrap();
        camera_b[(1, 1)] = T::from_f64(100.0).unwrap();
        camera_b[(2, 2)] = T::one();
        camera_b[(0, 3)] = T::from_f64(-200.0).unwrap(); // Baseline.

        // Simple fundamental matrix for test.
        let mut fundamental = Matrix3::zeros();
        fundamental[(1, 2)] = T::from_f64(0.01).unwrap();
        fundamental[(2, 1)] = T::from_f64(-0.01).unwrap();

        (camera_a, camera_b, fundamental)
    }

    #[test]
    fn test_compute_fundamental_matrix_basic() {
        let (camera_a, camera_b, _) = create_simple_test_cameras::<f64>();

        let fundamental = compute_fundamental_matrix(&camera_a, &camera_b);

        assert!(
            fundamental.is_some(),
            "Fundamental matrix computation should succeed"
        );

        let f = fundamental.unwrap();

        // Verify rank-2 property: determinant should be close to zero.
        let det = f.determinant();
        assert!(
            det.abs() < 1e-6,
            "Fundamental matrix should have rank 2 (det ~= 0), got det = {}",
            det
        );

        let norm = f.norm();
        assert!(
            norm > 1e-12 && norm < 1e12,
            "Fundamental matrix should be well-conditioned, got norm = {}",
            norm
        );
    }

    #[test]
    fn test_decompose_projection_matrix() {
        let intrinsic_matrix =
            Matrix3::new(100.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 1.0);
        let rotation = Matrix3::identity();
        let translation = nalgebra::Vector3::new(-1.0, 0.0, 0.0);

        let extrinsic = Matrix3x4::from_columns(&[
            rotation.column(0).into(),
            rotation.column(1).into(),
            rotation.column(2).into(),
            translation,
        ]);
        let projection = intrinsic_matrix * extrinsic;

        let result = decompose_projection_matrix(&projection);
        assert!(result.is_some(), "Decomposition should succeed");

        let (intrinsic_decomp, rotation_decomp, translation_decomp) =
            result.unwrap();

        let intrinsic_diff = (intrinsic_matrix - intrinsic_decomp).norm();
        assert!(
            intrinsic_diff < 1e-10,
            "K should match, got diff = {}",
            intrinsic_diff
        );

        let rotation_diff = (rotation - rotation_decomp).norm();
        assert!(
            rotation_diff < 1e-10,
            "R should match, got diff = {}",
            rotation_diff
        );

        let translation_diff = (translation - translation_decomp).norm();
        assert!(
            translation_diff < 1e-10,
            "t should match, got diff = {}",
            translation_diff
        );

        // Verify round-trip.
        let extrinsic_recomp = Matrix3x4::from_columns(&[
            rotation_decomp.column(0).into(),
            rotation_decomp.column(1).into(),
            rotation_decomp.column(2).into(),
            translation_decomp,
        ]);
        let projection_recomp = intrinsic_decomp * extrinsic_recomp;
        let recomp_diff = (projection - projection_recomp).norm();
        assert!(
            recomp_diff < 1e-10,
            "Round-trip should match, got diff = {}",
            recomp_diff
        );
    }

    #[test]
    fn test_compute_fundamental_matrix_with_known_pose() {
        use nalgebra::{Point3, Vector3};

        let intrinsic_matrix =
            Matrix3::new(100.0, 0.0, 0.0, 0.0, 100.0, 0.0, 0.0, 0.0, 1.0);

        let rotation_a = Matrix3::identity();
        let translation_a = Vector3::zeros();
        let extrinsic_a = Matrix3x4::from_columns(&[
            rotation_a.column(0).into(),
            rotation_a.column(1).into(),
            rotation_a.column(2).into(),
            translation_a,
        ]);
        let camera_a = intrinsic_matrix * extrinsic_a;

        // Camera B: pure translation along X-axis.
        let rotation_b = Matrix3::identity();
        let center_b = Point3::new(1.0, 0.0, 0.0);
        let translation_b = -(rotation_b * center_b.coords);
        let extrinsic_b = Matrix3x4::from_columns(&[
            rotation_b.column(0).into(),
            rotation_b.column(1).into(),
            rotation_b.column(2).into(),
            translation_b,
        ]);
        let camera_b = intrinsic_matrix * extrinsic_b;

        let fundamental = compute_fundamental_matrix(&camera_a, &camera_b);
        assert!(
            fundamental.is_some(),
            "Fundamental matrix should be computed"
        );

        let f = fundamental.unwrap();

        // For pure translation, F should be anti-symmetric.
        let antisymmetric_test = f + f.transpose();
        let antisym_norm = antisymmetric_test.norm();
        assert!(
            antisym_norm < 1e-6,
            "For pure translation, F should be anti-symmetric, got ||F + F^T|| = {}",
            antisym_norm
        );

        // Verify rank-2.
        let det: f64 = f.determinant();
        assert!(
            det.abs() < 1e-6,
            "Fundamental matrix should have det ~= 0, got {}",
            det
        );

        // Test epipolar constraint with a 3D point.
        let point_3d = Point3::new(0.5, 0.5, -5.0);

        let projected_a = camera_a * point_3d.to_homogeneous();
        let point_in_a = Vector3::new(
            projected_a[0] / projected_a[2],
            projected_a[1] / projected_a[2],
            1.0,
        );

        let projected_b = camera_b * point_3d.to_homogeneous();
        let point_in_b = Vector3::new(
            projected_b[0] / projected_b[2],
            projected_b[1] / projected_b[2],
            1.0,
        );

        // Epipolar constraint: x_b^T * F * x_a ~= 0.
        let constraint = point_in_b.transpose() * f * point_in_a;
        println!("Epipolar constraint value: {}", constraint[0]);
        assert!(
            constraint[0].abs() < 1e-6,
            "Epipolar constraint should be satisfied, got {}",
            constraint[0]
        );
    }
}
