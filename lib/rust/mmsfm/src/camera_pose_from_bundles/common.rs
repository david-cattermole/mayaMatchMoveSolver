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
use nalgebra::{Matrix3, Matrix3x4, Point3, Vector2, Vector3};
use thiserror::Error;

pub use crate::datatype::{CameraIntrinsics, CameraPose};
use crate::datatype::{CameraToSceneCorrespondence, UnitValue};

#[derive(Error, Debug)]
pub enum PnPError {
    #[error(
        "Insufficient points: need at least {min_points}, got {actual_points}"
    )]
    InsufficientPoints {
        min_points: usize,
        actual_points: usize,
    },
    #[error("Invalid input dimensions")]
    InvalidInput,
    #[error("Singular configuration")]
    SingularConfiguration,
    #[error("No valid solution found")]
    NoSolution,
    #[error("Point correspondence arrays must have the same length")]
    InvalidDimensions,
}

/// Type aliases for common matrix and vector types.
pub type Mat3 = Matrix3<f64>;
pub type Vec3 = Vector3<f64>;
pub type Point3D = Point3<f64>;
pub type Vec2 = Vector2<f64>;
pub type Mat34 = Matrix3x4<f64>;

/// Returns true if the 3D world point is in front of the camera.
pub fn is_point_in_front_of_camera(
    pose: &CameraPose,
    world_point: &Point3D,
) -> bool {
    pose.is_point_in_front(world_point)
}

/// Returns the reprojection error for a single 2D-3D correspondence.
///
/// Returns infinity if the point is behind the camera.
pub fn calculate_reprojection_error(
    pose: &CameraPose,
    intrinsics: &Mat3,
    correspondence: &CameraToSceneCorrespondence<f64>,
) -> f64 {
    let scene_coords = Point3::new(
        correspondence.scene_point.coords.x.value(),
        correspondence.scene_point.coords.y.value(),
        correspondence.scene_point.coords.z.value(),
    );
    let camera_point = pose.apply_transform(&scene_coords);

    if camera_point.z >= 0.0 {
        // Point is behind camera (Maya convention: negative Z is forward)
        return f64::INFINITY;
    }

    let projected_homogeneous = intrinsics * camera_point;
    let projected_2d = Vector2::new(
        projected_homogeneous.x / projected_homogeneous.z,
        projected_homogeneous.y / projected_homogeneous.z,
    );

    let camera_coords = Vector2::new(
        correspondence.camera_point.coords.x.value(),
        correspondence.camera_point.coords.y.value(),
    );
    (camera_coords - projected_2d).norm()
}

/// Returns the average reprojection error across all correspondences.
///
/// Points behind the camera are excluded from the average. Returns infinity
/// if no points are in front of the camera.
pub fn calculate_average_reprojection_error(
    pose: &CameraPose,
    intrinsics: &Mat3,
    correspondences: &[CameraToSceneCorrespondence<f64>],
) -> f64 {
    let mut total_error = 0.0;
    let mut valid_count = 0;

    for corr in correspondences {
        let error = calculate_reprojection_error(pose, intrinsics, corr);
        if error.is_finite() {
            total_error += error;
            valid_count += 1;
        }
    }

    if valid_count > 0 {
        total_error / valid_count as f64
    } else {
        f64::INFINITY
    }
}

/// Checks that correspondences contain no NaN/infinite values and no degenerate points.
pub fn validate_correspondences(
    correspondences: &[CameraToSceneCorrespondence<f64>],
) -> Result<(), PnPError> {
    if correspondences.is_empty() {
        return Err(PnPError::InvalidInput);
    }

    for corr in correspondences.iter() {
        if !corr.camera_point.coords.x.value().is_finite()
            || !corr.camera_point.coords.y.value().is_finite()
        {
            return Err(PnPError::InvalidInput);
        }

        if !corr.scene_point.coords.x.value().is_finite()
            || !corr.scene_point.coords.y.value().is_finite()
            || !corr.scene_point.coords.z.value().is_finite()
        {
            return Err(PnPError::InvalidInput);
        }

        // Reject degenerate points at the origin.
        let scene_coords = Vector3::new(
            corr.scene_point.coords.x.value(),
            corr.scene_point.coords.y.value(),
            corr.scene_point.coords.z.value(),
        );
        if scene_coords.norm() < 1e-15 {
            return Err(PnPError::InvalidInput);
        }
    }

    Ok(())
}

/// Returns true if the camera pose has a valid rotation matrix and finite camera center.
pub fn verify_camera_pose_properties(
    pose: &CameraPose,
    tolerance: f64,
) -> bool {
    let r = pose.rotation();

    // R * R^T should be identity (orthogonal matrix check).
    let should_be_identity = r * r.transpose();
    let identity = Mat3::identity();
    let orthogonal_error = (should_be_identity - identity).norm();

    if orthogonal_error > tolerance {
        return false;
    }

    // Determinant must be +1, not -1 (which would indicate a reflection).
    let det = r.determinant();
    if (det - 1.0).abs() > tolerance {
        return false;
    }

    let center = pose.center();
    if !center.x.is_finite() || !center.y.is_finite() || !center.z.is_finite() {
        return false;
    }

    true
}

/// Builds the 3x4 projection matrix P = K * [R | t].
pub fn projection_matrix_from_krt(
    intrinsics: &Mat3,
    rotation: &Mat3,
    translation: &Vec3,
) -> Mat34 {
    let mut rt = Mat34::zeros();
    rt.fixed_view_mut::<3, 3>(0, 0).copy_from(rotation);
    rt.fixed_view_mut::<3, 1>(0, 3).copy_from(translation);
    intrinsics * rt
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_point_in_front_of_camera() {
        let r = Mat3::identity();
        let center = Point3D::origin();
        let pose = CameraPose::new(r, center);

        // Negative Z is in front of the camera in Maya convention.
        let point_in_front = Point3D::new(0.0, 0.0, -10.0);
        let point_behind = Point3D::new(0.0, 0.0, 1.0);

        assert!(is_point_in_front_of_camera(&pose, &point_in_front));
        assert!(!is_point_in_front_of_camera(&pose, &point_behind));
    }

    #[test]
    fn test_validate_correspondences_valid() {
        let correspondences = vec![
            CameraToSceneCorrespondence::new(-0.5, -0.5, 1.0, 0.0, 5.0),
            CameraToSceneCorrespondence::new(0.5, -0.5, -1.0, 0.0, 5.0),
            CameraToSceneCorrespondence::new(-0.5, 0.5, 1.0, 1.0, 5.0),
        ];

        let result = validate_correspondences(&correspondences);
        assert!(result.is_ok());
    }

    #[test]
    fn test_validate_correspondences_empty() {
        let correspondences = vec![];
        let result = validate_correspondences(&correspondences);
        assert!(matches!(result, Err(PnPError::InvalidInput)));
    }

    #[test]
    fn test_validate_correspondences_invalid_values() {
        let correspondences = vec![CameraToSceneCorrespondence::new(
            f64::NAN,
            0.0,
            1.0,
            0.0,
            5.0,
        )];
        let result = validate_correspondences(&correspondences);
        assert!(matches!(result, Err(PnPError::InvalidInput)));
    }

    #[test]
    fn test_verify_camera_pose_properties_valid() {
        let r = Mat3::identity();
        let center = Point3D::new(1.0, 2.0, 3.0);
        let pose = CameraPose::new(r, center);

        assert!(verify_camera_pose_properties(&pose, 1e-10));
    }

    #[test]
    fn test_verify_camera_pose_properties_invalid_rotation() {
        // Non-orthogonal matrix.
        let r = Mat3::new(1.0, 0.1, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0);
        let center = Point3D::new(1.0, 2.0, 3.0);
        let pose = CameraPose::new(r, center);

        assert!(!verify_camera_pose_properties(&pose, 1e-10));
    }

    #[test]
    fn test_projection_matrix_construction() {
        let k = Mat3::new(500.0, 0.0, 320.0, 0.0, 500.0, 240.0, 0.0, 0.0, 1.0);
        let r = Mat3::identity();
        let t = Vec3::new(1.0, 2.0, 3.0);

        let p = projection_matrix_from_krt(&k, &r, &t);

        // Check dimensions
        assert_eq!(p.nrows(), 3);
        assert_eq!(p.ncols(), 4);

        // K * [R|t] = K * [I|t] = [K|Kt].
        let expected_p = Mat34::new(
            500.0, 0.0, 320.0, 1460.0, // 500*1 + 0*2 + 320*3 = 1460
            0.0, 500.0, 240.0, 1720.0, // 0*1 + 500*2 + 240*3 = 1720
            0.0, 0.0, 1.0, 3.0, // 0*1 + 0*2 + 1*3 = 3
        );

        let diff = (p - expected_p).norm();
        assert!(diff < 1e-10, "Projection matrix mismatch: diff = {}", diff);
    }

    #[test]
    fn test_reprojection_error_calculation() {
        let r = Mat3::identity();
        let center = Point3D::origin();
        let pose = CameraPose::new(r, center);

        let k = Mat3::identity();

        // Point at (0, 0, -1) should project to (0, 0).
        let corr = CameraToSceneCorrespondence::new(0.0, 0.0, 0.0, 0.0, -1.0);
        let error = calculate_reprojection_error(&pose, &k, &corr);

        assert!(
            error < 1e-10,
            "Reprojection error should be near zero: {}",
            error
        );
    }

    #[test]
    fn test_reprojection_error_behind_camera() {
        let r = Mat3::identity();
        let center = Point3D::origin();
        let pose = CameraPose::new(r, center);

        let k = Mat3::identity();

        // Positive Z is behind the camera.
        let corr = CameraToSceneCorrespondence::new(0.0, 0.0, 0.0, 0.0, 1.0);
        let error = calculate_reprojection_error(&pose, &k, &corr);

        assert!(error.is_infinite());
    }

    #[test]
    fn test_maya_coordinate_system_validation() {
        let r = Mat3::identity();
        let center = Point3D::origin();
        let pose = CameraPose::new(r, center);

        // Negative Z is in front of the camera, positive Z is behind.
        let point_in_front_1 = Point3D::new(0.0, 0.0, -5.0);
        let point_in_front_2 = Point3D::new(1.0, 1.0, -10.0);
        let point_behind_1 = Point3D::new(0.0, 0.0, 5.0);
        let point_behind_2 = Point3D::new(-1.0, 1.0, 2.0);

        assert!(is_point_in_front_of_camera(&pose, &point_in_front_1));
        assert!(is_point_in_front_of_camera(&pose, &point_in_front_2));
        assert!(!is_point_in_front_of_camera(&pose, &point_behind_1));
        assert!(!is_point_in_front_of_camera(&pose, &point_behind_2));

        let k = Mat3::identity();

        let corr_front =
            CameraToSceneCorrespondence::new(0.0, 0.0, 0.0, 0.0, -1.0);
        let error_front = calculate_reprojection_error(&pose, &k, &corr_front);
        assert!(error_front.is_finite());

        let corr_behind =
            CameraToSceneCorrespondence::new(0.0, 0.0, 0.0, 0.0, 1.0);
        let error_behind =
            calculate_reprojection_error(&pose, &k, &corr_behind);
        assert!(error_behind.is_infinite());
    }
}
