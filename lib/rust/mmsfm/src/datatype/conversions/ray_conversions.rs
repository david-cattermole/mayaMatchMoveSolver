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

//! Ray conversion functions for triangulation and structure from motion.
//!
//! This module provides conversions from NDC (Normalized Device Coordinates)
//! to camera rays in world space, which are used for triangulation operations.

use nalgebra::Vector3;

use crate::datatype::camera_intrinsics::CameraIntrinsics;
use crate::datatype::camera_pose::CameraPose;
use crate::datatype::common::UnitValue;
use crate::datatype::ndc_value::NdcPoint2;
use crate::datatype::{ScenePoint3, SceneUnit, SceneVector3};

use super::convert_ndc_to_camera_coord_point_with_intrinsics;

// ============================================================================
// NDC to Ray Direction Conversions
// ============================================================================

/// Convert NDC point to normalized ray direction in world space.
///
/// This function transforms a 2D NDC point to a 3D ray direction in world space
/// by:
/// 1. Converting NDC to camera coordinates using intrinsics
/// 2. Creating a ray in camera space (Maya convention: -Z forward)
/// 3. Transforming the ray to world space using the camera pose
/// 4. Normalizing the result
///
/// # Arguments
/// * `ndc_point` - Point in NDC coordinates [-1,1]
/// * `camera_pose` - Camera pose (position and orientation) in world space
/// * `camera_intrinsics` - Camera intrinsics (focal length, principal point)
///
/// # Returns
/// Normalized ray direction vector in world space
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::{*, conversions::*};
/// use nalgebra::Point3;
///
/// let ndc = NdcValue::point2(0.0, 0.0);
/// let camera_pose = CameraPose::default(); // Identity pose at origin
/// let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
/// let focal_length = MillimeterUnit::new(50.0);
/// let intrinsics = CameraIntrinsics::from_centered_lens(focal_length, film_back);
///
/// let ray_dir = convert_ndc_to_ray_direction(ndc, &camera_pose, &intrinsics);
/// // For centered NDC (0,0) with identity pose, ray should point down -Z
/// assert!((ray_dir.z + 1.0).abs() < 1e-6);
/// assert!(ray_dir.norm() - 1.0 < 1e-10); // Normalized
/// ```
pub fn convert_ndc_to_ray_direction(
    ndc_point: NdcPoint2<f64>,
    camera_pose: &CameraPose,
    camera_intrinsics: &CameraIntrinsics,
) -> Vector3<f64> {
    let camera_coord_point = convert_ndc_to_camera_coord_point_with_intrinsics(
        ndc_point,
        camera_intrinsics,
    );

    // Create normalized ray direction in camera space (Maya convention: -Z forward).
    let camera_ray = Vector3::new(
        camera_coord_point.x.value(),
        camera_coord_point.y.value(),
        -1.0, // Maya convention: camera looks down -Z axis.
    );

    // Transform ray from camera space to world space.
    let ray_direction = camera_pose.apply_transform_to_vector(&camera_ray);
    ray_direction.normalize()
}

/// Convert multiple NDC points to camera rays for triangulation.
///
/// This batch function converts NDC point correspondences from two views
/// into ray origins and directions suitable for line-line triangulation.
///
/// # Arguments
/// * `ndc_points_a` - NDC points from camera A
/// * `ndc_points_b` - NDC points from camera B
/// * `camera_pose_a` - Camera A pose in world space
/// * `camera_pose_b` - Camera B pose in world space
/// * `camera_intrinsics_a` - Camera A intrinsics
/// * `camera_intrinsics_b` - Camera B intrinsics
///
/// # Returns
/// Tuple of (origins_a, directions_a, origins_b, directions_b) all in SceneUnit types
///
/// # Panics
/// Panics if the input slices have different lengths or are empty.
// TODO: Do not allocate Vec in this function at all, instead make the
// calling function do that.
// TODO: Refactor function to use mutable slice for output data.
pub fn convert_ndc_points_to_camera_rays(
    ndc_points_a: &[NdcPoint2<f64>],
    ndc_points_b: &[NdcPoint2<f64>],
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    camera_intrinsics_a: &CameraIntrinsics,
    camera_intrinsics_b: &CameraIntrinsics,
) -> (
    Vec<ScenePoint3<f64>>,
    Vec<SceneVector3<f64>>,
    Vec<ScenePoint3<f64>>,
    Vec<SceneVector3<f64>>,
) {
    assert_eq!(ndc_points_a.len(), ndc_points_b.len());
    assert!(!ndc_points_a.is_empty());
    let num_points = ndc_points_a.len();

    let mut ray_origins_a = Vec::with_capacity(num_points);
    let mut ray_directions_a = Vec::with_capacity(num_points);
    let mut ray_origins_b = Vec::with_capacity(num_points);
    let mut ray_directions_b = Vec::with_capacity(num_points);

    for i in 0..num_points {
        // Convert camera A
        let ray_origin_a_raw = *camera_pose_a.center();
        let ray_direction_a_raw = convert_ndc_to_ray_direction(
            ndc_points_a[i],
            camera_pose_a,
            camera_intrinsics_a,
        );

        // Wrap raw values in SceneUnit types
        let ray_origin_a = ScenePoint3::new(
            SceneUnit(ray_origin_a_raw.x),
            SceneUnit(ray_origin_a_raw.y),
            SceneUnit(ray_origin_a_raw.z),
        );
        let ray_direction_a = SceneVector3::new(
            SceneUnit(ray_direction_a_raw.x),
            SceneUnit(ray_direction_a_raw.y),
            SceneUnit(ray_direction_a_raw.z),
        );
        ray_origins_a.push(ray_origin_a);
        ray_directions_a.push(ray_direction_a);

        // Convert camera B
        let ray_origin_b_raw = *camera_pose_b.center();
        let ray_direction_b_raw = convert_ndc_to_ray_direction(
            ndc_points_b[i],
            camera_pose_b,
            camera_intrinsics_b,
        );

        let ray_origin_b = ScenePoint3::new(
            SceneUnit(ray_origin_b_raw.x),
            SceneUnit(ray_origin_b_raw.y),
            SceneUnit(ray_origin_b_raw.z),
        );
        let ray_direction_b = SceneVector3::new(
            SceneUnit(ray_direction_b_raw.x),
            SceneUnit(ray_direction_b_raw.y),
            SceneUnit(ray_direction_b_raw.z),
        );
        ray_origins_b.push(ray_origin_b);
        ray_directions_b.push(ray_direction_b);
    }

    (
        ray_origins_a,
        ray_directions_a,
        ray_origins_b,
        ray_directions_b,
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::camera_pose::create_camera_pose_from_maya_transform;
    use crate::datatype::{
        CameraFilmBack, CameraIntrinsics, MillimeterUnit, NdcValue,
    };
    use approx::assert_relative_eq;

    #[test]
    fn test_convert_ndc_to_ray_direction_identity_pose() {
        let ndc = NdcValue::point2(0.0, 0.0);
        let camera_pose = CameraPose::default(); // Identity pose
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        let ray_dir =
            convert_ndc_to_ray_direction(ndc, &camera_pose, &intrinsics);

        // For centered NDC with identity pose, ray should point down -Z
        assert_relative_eq!(ray_dir.x, 0.0, epsilon = 1e-10);
        assert_relative_eq!(ray_dir.y, 0.0, epsilon = 1e-10);
        assert!(ray_dir.z < 0.0); // Should be negative Z
        assert_relative_eq!(ray_dir.norm(), 1.0, epsilon = 1e-10); // Normalized
    }

    #[test]
    fn test_convert_ndc_to_ray_direction_off_center() {
        let ndc = NdcValue::point2(0.5, -0.3);
        let camera_pose = CameraPose::default();
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        let ray_dir =
            convert_ndc_to_ray_direction(ndc, &camera_pose, &intrinsics);

        // Ray should be normalized
        assert_relative_eq!(ray_dir.norm(), 1.0, epsilon = 1e-10);
        // For positive NDC x (right side), ray should point in positive X direction
        assert!(ray_dir.x > 0.0);
        // For negative NDC y (bottom), ray should point in negative Y direction
        assert!(ray_dir.y < 0.0);
        // Should still have negative Z component
        assert!(ray_dir.z < 0.0);
    }

    #[test]
    fn test_convert_ndc_to_ray_direction_with_rotation() {
        let ndc = NdcValue::point2(0.0, 0.0);
        // Rotate camera 90 degrees around Y axis (left-hand turn from Maya)
        let camera_pose = create_camera_pose_from_maya_transform(
            0.0, 0.0, 0.0, // position
            0.0, 90.0, 0.0, // rotation (degrees)
        );
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        let ray_dir =
            convert_ndc_to_ray_direction(ndc, &camera_pose, &intrinsics);

        // After 90deg Y rotation in Maya (right-hand system, Y-up), camera's -Z becomes world -X
        assert_relative_eq!(ray_dir.norm(), 1.0, epsilon = 1e-10);
        assert_relative_eq!(ray_dir.x, -1.0, epsilon = 1e-6); // Should point in -X
        assert_relative_eq!(ray_dir.y, 0.0, epsilon = 1e-10);
        assert_relative_eq!(ray_dir.z, 0.0, epsilon = 1e-6);
    }

    #[test]
    fn test_convert_ndc_points_to_camera_rays() {
        let ndc_points_a =
            vec![NdcValue::point2(0.0, 0.0), NdcValue::point2(0.5, -0.3)];
        let ndc_points_b =
            vec![NdcValue::point2(0.1, 0.2), NdcValue::point2(-0.2, 0.4)];

        let camera_pose_a = CameraPose::default();
        let camera_pose_b = create_camera_pose_from_maya_transform(
            5.0, 0.0, 0.0, // Translate in X
            0.0, -15.0, 0.0, // Rotate Y
        );

        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let intrinsics_a =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);
        let intrinsics_b =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        let (origins_a, directions_a, origins_b, directions_b) =
            convert_ndc_points_to_camera_rays(
                &ndc_points_a,
                &ndc_points_b,
                &camera_pose_a,
                &camera_pose_b,
                &intrinsics_a,
                &intrinsics_b,
            );

        // Verify we got the right number of rays
        assert_eq!(origins_a.len(), 2);
        assert_eq!(directions_a.len(), 2);
        assert_eq!(origins_b.len(), 2);
        assert_eq!(directions_b.len(), 2);

        // Verify camera A origins are at the camera center (origin)
        assert_relative_eq!(origins_a[0].x.0, 0.0, epsilon = 1e-10);
        assert_relative_eq!(origins_a[0].y.0, 0.0, epsilon = 1e-10);
        assert_relative_eq!(origins_a[0].z.0, 0.0, epsilon = 1e-10);

        // Verify camera B origins are at (5, 0, 0)
        assert_relative_eq!(origins_b[0].x.0, 5.0, epsilon = 1e-10);
        assert_relative_eq!(origins_b[0].y.0, 0.0, epsilon = 1e-10);
        assert_relative_eq!(origins_b[0].z.0, 0.0, epsilon = 1e-10);

        // Verify directions are normalized
        for i in 0..2 {
            let norm_a = (directions_a[i].x.0.powi(2)
                + directions_a[i].y.0.powi(2)
                + directions_a[i].z.0.powi(2))
            .sqrt();
            assert_relative_eq!(norm_a, 1.0, epsilon = 1e-10);

            let norm_b = (directions_b[i].x.0.powi(2)
                + directions_b[i].y.0.powi(2)
                + directions_b[i].z.0.powi(2))
            .sqrt();
            assert_relative_eq!(norm_b, 1.0, epsilon = 1e-10);
        }
    }

    #[test]
    #[should_panic(expected = "assertion `left == right` failed")]
    fn test_convert_ndc_points_to_camera_rays_mismatched_lengths() {
        let ndc_points_a = vec![NdcValue::point2(0.0, 0.0)];
        let ndc_points_b =
            vec![NdcValue::point2(0.1, 0.2), NdcValue::point2(-0.2, 0.4)];

        let camera_pose_a = CameraPose::default();
        let camera_pose_b = CameraPose::default();
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let focal_length = MillimeterUnit::new(50.0);
        let intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        let _ = convert_ndc_points_to_camera_rays(
            &ndc_points_a,
            &ndc_points_b,
            &camera_pose_a,
            &camera_pose_b,
            &intrinsics,
            &intrinsics,
        );
    }
}
