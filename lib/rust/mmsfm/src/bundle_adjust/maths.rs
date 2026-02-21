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

use nalgebra::{
    Matrix3, Point3, Quaternion, Rotation3, UnitQuaternion, Vector3,
};
use num_traits::{Float, NumCast};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Reconstruct a full quaternion [w, x, y, z] from the vector part [qx, qy, qz].
///
/// Warning: has numerical issues when `||quat_vec|| >= 1`.
/// For large rotations where w is small, use `rotation_matrix_to_full_quaternion`.
#[inline]
pub fn quaternion_from_vector_f64(quat_vec: &[f64; 3]) -> [f64; 4] {
    let sum_sq = quat_vec[0] * quat_vec[0]
        + quat_vec[1] * quat_vec[1]
        + quat_vec[2] * quat_vec[2];

    let w = if sum_sq < 1.0 {
        (1.0 - sum_sq).sqrt()
    } else {
        0.0
    };

    [w, quat_vec[0], quat_vec[1], quat_vec[2]]
}

/// Convert a rotation matrix to a full quaternion [w, x, y, z].
///
/// Avoids numerical issues when w is close to zero by not using a
/// 3-parameter intermediate representation. Always returns w >= 0.
pub fn rotation_matrix_to_full_quaternion(rotation: &Matrix3<f64>) -> [f64; 4] {
    // Check orthogonality and re-orthogonalize if needed.
    const ORTHOGONALITY_TOLERANCE: f64 = 1e-6;
    let rotation_to_use = if !is_orthogonal(rotation, ORTHOGONALITY_TOLERANCE) {
        mm_debug_eprintln!(
            "WARNING: rotation_matrix_to_full_quaternion: input matrix is not orthogonal, re-orthogonalizing"
        );
        ensure_orthogonal_rotation(rotation)
    } else {
        *rotation
    };

    // Convert rotation matrix to unit quaternion using nalgebra.
    let rot3 = Rotation3::from_matrix_unchecked(rotation_to_use);
    let unit_quat = UnitQuaternion::from_rotation_matrix(&rot3);
    let quat = unit_quat.quaternion();

    // Ensure w >= 0 by negating if necessary (q and -q represent same rotation).
    if quat.w >= 0.0 {
        [quat.w, quat.i, quat.j, quat.k]
    } else {
        [-quat.w, -quat.i, -quat.j, -quat.k]
    }
}

/// Multiply two quaternions [w, x, y, z]: result = q1 * q2.
#[inline]
pub fn quaternion_multiply(q1: &[f64; 4], q2: &[f64; 4]) -> [f64; 4] {
    let (w1, x1, y1, z1) = (q1[0], q1[1], q1[2], q1[3]);
    let (w2, x2, y2, z2) = (q2[0], q2[1], q2[2], q2[3]);
    [
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2, // w
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2, // x
        w1 * y2 + y1 * w2 + z1 * x2 - x1 * z2, // y
        w1 * z2 + z1 * w2 + x1 * y2 - y1 * x2, // z
    ]
}

/// Compose a small rotation perturbation with a fixed initial rotation.
///
/// Takes a 3-param perturbation vector [qx, qy, qz] and a fixed full
/// quaternion [w, x, y, z], and returns the composed full
/// quaternion. Keeping the perturbation small (near identity) avoids
/// numerical issues during optimization.
///
/// The composition is `perturbation * initial` (left multiplication).
#[inline]
pub fn compose_rotation_generic<T>(
    perturbation: &[T; 3],
    initial: &[f64; 4],
) -> [T; 4]
where
    T: Float + Copy + NumCast,
{
    // Reconstruct the perturbation w component from the unit quaternion constraint.
    let sum_sq = perturbation[0] * perturbation[0]
        + perturbation[1] * perturbation[1]
        + perturbation[2] * perturbation[2];
    let w_perturb = if sum_sq < T::one() {
        (T::one() - sum_sq).sqrt()
    } else {
        T::zero()
    };

    if DEBUG {
        let sum_sq_f64: f64 = NumCast::from(sum_sq).unwrap_or(f64::NAN);
        let w_perturb_f64: f64 = NumCast::from(w_perturb).unwrap_or(f64::NAN);
        if sum_sq_f64 >= 0.95 {
            eprintln!(
                "[BA_MATHS] WARNING: perturbation norm close to 1: ||perturb||^2={:.6}, w_perturb={:.6}",
                sum_sq_f64, w_perturb_f64
            );
        }
    }

    // Initial rotation components (convert f64 to T).
    let w_init: T = NumCast::from(initial[0]).unwrap();
    let x_init: T = NumCast::from(initial[1]).unwrap();
    let y_init: T = NumCast::from(initial[2]).unwrap();
    let z_init: T = NumCast::from(initial[3]).unwrap();

    // Hamilton product: perturbation * initial (left multiplication).
    let w_result = w_perturb * w_init
        - perturbation[0] * x_init
        - perturbation[1] * y_init
        - perturbation[2] * z_init;
    let x_result = w_perturb * x_init
        + perturbation[0] * w_init
        + perturbation[1] * z_init
        - perturbation[2] * y_init;
    let y_result = w_perturb * y_init - perturbation[0] * z_init
        + perturbation[1] * w_init
        + perturbation[2] * x_init;
    let z_result = w_perturb * z_init + perturbation[0] * y_init
        - perturbation[1] * x_init
        + perturbation[2] * w_init;

    // Normalize to handle accumulated floating-point errors.
    let norm = (w_result * w_result
        + x_result * x_result
        + y_result * y_result
        + z_result * z_result)
        .sqrt();

    if DEBUG {
        let norm_f64: f64 = NumCast::from(norm).unwrap_or(f64::NAN);
        if (norm_f64 - 1.0).abs() > 0.01 {
            eprintln!(
                "[BA_MATHS] WARNING: composed quaternion norm far from 1: norm={:.6}",
                norm_f64
            );
        }
    }

    [
        w_result / norm,
        x_result / norm,
        y_result / norm,
        z_result / norm,
    ]
}

/// Rotate a 3D point by a full unit quaternion [w, x, y, z].
fn quaternion_rotate_full<T>(point: &[T; 3], quat_full: &[T; 4]) -> [T; 3]
where
    T: Float + Copy,
{
    let (w, x, y, z) = (quat_full[0], quat_full[1], quat_full[2], quat_full[3]);

    // Compute intermediate products.
    let t2 = w * x; // w*x
    let t3 = w * y; // w*y
    let t4 = w * z; // w*z
    let t5 = -x * x; // -x^2
    let t6 = x * y; // x*y
    let t7 = x * z; // x*z
    let t8 = -y * y; // -y^2
    let t9 = y * z; // y*z
    let t1 = -z * z; // -z^2

    let two = T::from(2.0).unwrap();

    [
        two * ((t8 + t1) * point[0]
            + (t6 - t4) * point[1]
            + (t3 + t7) * point[2])
            + point[0],
        two * ((t4 + t6) * point[0]
            + (t5 + t1) * point[1]
            + (t9 - t2) * point[2])
            + point[1],
        two * ((t7 - t3) * point[0]
            + (t2 + t9) * point[1]
            + (t5 + t8) * point[2])
            + point[2],
    ]
}

/// Project a 3D world point to a 2D NDC image position using a pinhole camera.
///
/// Uses Maya camera convention: camera looks down -Z axis.
pub fn project_point_generic<T>(
    point_3d: &[T; 3],
    rotation: &[T; 4],
    translation: &[T; 3],
    focal_length_x: T,
    focal_length_y: T,
    principal_point: (T, T),
) -> (T, T)
where
    T: Float + Copy,
{
    // Apply quaternion rotation and translation to transform point to
    // 3D camera space position.
    let rotated = quaternion_rotate_full(point_3d, rotation);
    let camera_point_xyz = [
        rotated[0] + translation[0],
        rotated[1] + translation[1],
        rotated[2] + translation[2],
    ];

    if DEBUG {
        // Convert to f64 for debug printing.
        //
        // This will work for f64, but approximate for Dual.
        let cam_z: f64 = NumCast::from(camera_point_xyz[2]).unwrap_or(f64::NAN);
        // Warn if point is behind camera (positive Z in Maya
        // convention).
        if cam_z >= 0.0 {
            eprintln!(
                "[BA_MATHS] WARNING: point behind camera: cam_z={:.6} (should be negative)",
                cam_z
            );
        }
    }

    // Project onto image plane (Maya: camera looks down -Z)
    //
    // Perspective division: project onto Z=-1 plane.
    //
    // Guard against points at or behind the camera plane (Z >= 0).
    // The perspective divisor is -Z; when the point is in front of
    // the camera -Z > 0.  Clamp to a small positive epsilon so that
    // behind-camera points produce large-but-finite projections that
    // steer the optimizer away, rather than inf/NaN from division by
    // zero or sign flip.
    let neg_z = -camera_point_xyz[2];
    let epsilon = T::from(1e-6).unwrap();
    let neg_z_safe = if neg_z < epsilon { epsilon } else { neg_z };
    let proj_x = camera_point_xyz[0] / neg_z_safe;
    let proj_y = camera_point_xyz[1] / neg_z_safe;

    // Apply intrinsics to get image coordinates.
    let two = T::from(2.0).unwrap();
    let ndc_x = (two * focal_length_x * proj_x) + principal_point.0;
    let ndc_y = (two * focal_length_y * proj_y) + principal_point.1;

    (ndc_x, ndc_y)
}

/// Project a matrix onto SO(3) using SVD, producing a valid rotation matrix.
///
/// Handles numerical drift where accumulated errors make the matrix non-orthogonal.
/// Uses SVD: `R_ortho = U * V^T`.
pub fn ensure_orthogonal_rotation(matrix: &Matrix3<f64>) -> Matrix3<f64> {
    let svd = matrix.svd(true, true);
    let u = svd.u.expect("SVD should always succeed on 3x3 matrix");
    let vt = svd.v_t.expect("SVD should always succeed on 3x3 matrix");

    // Reconstruct with unit singular values to enforce orthogonality.
    let mut r_ortho = u * vt;

    // Ensure proper rotation (det = +1, not -1 which is a reflection).
    if r_ortho.determinant() < 0.0 {
        let col2 = -r_ortho.column(2);
        r_ortho.set_column(2, &col2);
    }

    r_ortho
}

/// Check if a matrix is orthogonal (R * R^T ~= I).
fn is_orthogonal(matrix: &Matrix3<f64>, tolerance: f64) -> bool {
    let rrt = matrix * matrix.transpose();
    let identity = Matrix3::identity();
    (rrt - identity).norm() < tolerance
}

/// Convert a rotation matrix to a 3-component quaternion vector [qx, qy, qz].
///
/// The full quaternion is [w, qx, qy, qz] where `w = sqrt(1 - qx^2 - qy^2 - qz^2)`.
/// Always returns w >= 0. Re-orthogonalizes the input if it has numerical drift.
pub fn rotation_matrix_to_quaternion_vector(
    rotation: &Matrix3<f64>,
) -> [f64; 3] {
    if DEBUG {
        // Validate input rotation matrix is finite.
        for &v in rotation.iter() {
            if !v.is_finite() {
                eprintln!(
                    "ERROR: rotation_matrix_to_quaternion_vector: input matrix contains NaN/Inf"
                );
                eprintln!("  Input matrix:\n{}", rotation);
                return [f64::NAN, f64::NAN, f64::NAN];
            }
        }
    }

    // Check orthogonality and re-orthogonalize if needed.
    //
    // This handles numerical drift from matrix multiplications or
    // rotation matrices from algorithms that don't enforce
    // orthogonality.
    const ORTHOGONALITY_TOLERANCE: f64 = 1e-6;
    let rotation_to_use = if !is_orthogonal(rotation, ORTHOGONALITY_TOLERANCE) {
        mm_debug_eprintln!(
            "WARNING: rotation_matrix_to_quaternion_vector: input matrix is not orthogonal, re-orthogonalizing"
        );
        mm_debug_eprintln!("  Input matrix:\n{}", rotation);
        ensure_orthogonal_rotation(rotation)
    } else {
        *rotation
    };

    // Convert rotation matrix to unit quaternion using nalgebra.
    let rot3 = Rotation3::from_matrix_unchecked(rotation_to_use);
    let unit_quat = UnitQuaternion::from_rotation_matrix(&rot3);
    let quat = unit_quat.quaternion();

    // Extract components (nalgebra uses [w, i, j, k] internally).
    //
    // Ensure w >= 0 by negating if necessary (q and -q represent same rotation).
    let (x, y, z) = if quat.w >= 0.0 {
        (quat.i, quat.j, quat.k)
    } else {
        (-quat.i, -quat.j, -quat.k)
    };
    let result = [x, y, z];

    if DEBUG {
        // Validate output is finite
        for (i, &v) in result.iter().enumerate() {
            if !v.is_finite() {
                eprintln!(
                    "ERROR: rotation_matrix_to_quaternion_vector: output[{}] is NaN/Inf: {}",
                    i, v
                );
                eprintln!("  Input matrix:\n{}", rotation);
            }
        }
    }

    result
}

/// Convert a 3-component quaternion vector [qx, qy, qz] to a rotation matrix.
pub fn quaternion_vector_to_rotation_matrix(
    quat_vec: &[f64; 3],
) -> Matrix3<f64> {
    // Reconstruct w from unit quaternion constraint.
    let sum_sq = quat_vec[0] * quat_vec[0]
        + quat_vec[1] * quat_vec[1]
        + quat_vec[2] * quat_vec[2];
    let w = if sum_sq < 1.0 {
        (1.0 - sum_sq).sqrt()
    } else {
        0.0
    };

    // Create quaternion and convert to rotation matrix.
    let quat = Quaternion::new(w, quat_vec[0], quat_vec[1], quat_vec[2]);
    let unit_quat = UnitQuaternion::from_quaternion(quat);
    *unit_quat.to_rotation_matrix().matrix()
}

/// Convert a full quaternion [w, x, y, z] to a rotation matrix.
pub fn quaternion_full_to_rotation_matrix(quat: &[f64; 4]) -> Matrix3<f64> {
    let q = Quaternion::new(quat[0], quat[1], quat[2], quat[3]);
    let unit_quat = UnitQuaternion::from_quaternion(q);
    *unit_quat.to_rotation_matrix().matrix()
}

/// Convert a `CameraPose` to a quaternion vector [qx, qy, qz] and translation vector.
///
/// Translation is `-R * C` (camera centre to translation form).
pub fn camera_pose_to_quaternion_vector_and_translation(
    pose: &crate::datatype::camera_pose::CameraPose,
) -> ([f64; 3], [f64; 3]) {
    let rotation = rotation_matrix_to_quaternion_vector(pose.rotation());
    let translation_vector = pose.translation(); // t = -R * C
    let translation = [
        translation_vector.x,
        translation_vector.y,
        translation_vector.z,
    ];
    (rotation, translation)
}

/// Convert a quaternion vector [qx, qy, qz] and translation to a `CameraPose`.
pub fn quaternion_vector_and_translation_to_camera_pose(
    rotation: &[f64; 3],
    translation: &[f64; 3],
) -> crate::datatype::camera_pose::CameraPose {
    let rotation_matrix = quaternion_vector_to_rotation_matrix(rotation);
    let translation_vector =
        Vector3::new(translation[0], translation[1], translation[2]);
    // Compute center: C = -R^T * t
    let center_vector = -(rotation_matrix.transpose() * translation_vector);
    let center = Point3::from(center_vector);
    crate::datatype::camera_pose::CameraPose::new(rotation_matrix, center)
}

/// Convert a rotation matrix and translation to a `CameraPose`.
pub fn rotation_matrix_and_translation_to_camera_pose(
    rotation_matrix: &Matrix3<f64>,
    translation: &[f64; 3],
) -> crate::datatype::camera_pose::CameraPose {
    let translation_vector =
        Vector3::new(translation[0], translation[1], translation[2]);
    // Compute center: C = -R^T * t
    let center_vector = -(rotation_matrix.transpose() * translation_vector);
    let center = Point3::from(center_vector);
    crate::datatype::camera_pose::CameraPose::new(*rotation_matrix, center)
}

/// Convert a Cartesian translation vector to spherical angles (theta, phi).
///
/// Used for gauge fixing to enforce a unit-length translation constraint.
///
/// The spherical parameterization is:
/// - `tx = cos(phi) * sin(theta)`
/// - `ty = sin(phi)`
/// - `tz = cos(phi) * cos(theta)`
pub fn cartesian_to_spherical(t: &[f64; 3]) -> (f64, f64) {
    let norm = (t[0] * t[0] + t[1] * t[1] + t[2] * t[2]).sqrt();
    if norm < 1e-10 {
        // Degenerate case: return default direction (+Z)
        return (0.0, 0.0);
    }

    // Normalize to unit vector.
    let tx = t[0] / norm;
    let ty = t[1] / norm;
    let tz = t[2] / norm;

    // phi (elevation): angle from XZ plane, range [-pi/2, pi/2]
    // ty = sin(phi), so phi = asin(ty)
    let phi = ty.asin();

    // theta (azimuth): angle in XZ plane from +Z toward +X
    // tx = cos(phi) * sin(theta)
    // tz = cos(phi) * cos(theta)
    // So theta = atan2(tx, tz)
    let theta = tx.atan2(tz);

    (theta, phi)
}

/// Convert spherical angles to a unit Cartesian translation vector.
#[inline]
pub fn spherical_to_cartesian<T>(theta: T, phi: T) -> [T; 3]
where
    T: Float + Copy,
{
    let cos_phi = phi.cos();
    let sin_phi = phi.sin();
    let cos_theta = theta.cos();
    let sin_theta = theta.sin();

    [
        cos_phi * sin_theta, // tx
        sin_phi,             // ty
        cos_phi * cos_theta, // tz
    ]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_spherical_cartesian_roundtrip() {
        // Test that converting to spherical and back gives original unit vector.
        let test_cases = [
            [1.0, 0.0, 0.0],       // +X
            [0.0, 1.0, 0.0],       // +Y (near pole)
            [0.0, 0.0, 1.0],       // +Z
            [-1.0, 0.0, 0.0],      // -X
            [0.0, -1.0, 0.0],      // -Y (near pole)
            [0.0, 0.0, -1.0],      // -Z
            [0.577, 0.577, 0.577], // Diagonal
        ];

        for original in &test_cases {
            let (theta, phi) = cartesian_to_spherical(original);
            let recovered = spherical_to_cartesian::<f64>(theta, phi);

            // Check unit length
            let norm = (recovered[0] * recovered[0]
                + recovered[1] * recovered[1]
                + recovered[2] * recovered[2])
                .sqrt();
            assert!(
                (norm - 1.0).abs() < 1e-10,
                "Recovered vector should be unit length."
            );

            // Normalize original for comparison
            let orig_norm = (original[0] * original[0]
                + original[1] * original[1]
                + original[2] * original[2])
                .sqrt();
            let orig_unit = [
                original[0] / orig_norm,
                original[1] / orig_norm,
                original[2] / orig_norm,
            ];

            // Check direction matches.
            for i in 0..3 {
                assert!(
                    (recovered[i] - orig_unit[i]).abs() < 1e-6,
                    "Direction should match: expected {:?}, got {:?}",
                    orig_unit,
                    recovered
                );
            }
        }
    }

    #[test]
    fn test_spherical_always_unit_length() {
        // Test that any spherical angles give unit length.
        use std::f64::consts::PI;

        for theta_deg in (-180..=180).step_by(30) {
            for phi_deg in (-90..=90).step_by(30) {
                let theta = (theta_deg as f64) * PI / 180.0;
                let phi = (phi_deg as f64) * PI / 180.0;

                let t = spherical_to_cartesian::<f64>(theta, phi);
                let norm = (t[0] * t[0] + t[1] * t[1] + t[2] * t[2]).sqrt();

                assert!(
                    (norm - 1.0).abs() < 1e-14,
                    "Spherical coords ({}, {}) should give unit vector, got norm {}",
                    theta_deg,
                    phi_deg,
                    norm
                );
            }
        }
    }
}
