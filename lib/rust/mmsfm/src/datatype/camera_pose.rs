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

//! Camera pose representation using center-based parameterization.
//!
//! This module provides a camera pose representation using the center of rotation
//! as the primary parameterization, following Maya's coordinate system conventions.
//!
//! ## Maya Coordinate System
//!
//! This implementation follows Maya's coordinate system conventions:
//! - **Right-hand coordinate system**: Uses the standard mathematical right-hand rule
//! - **+Y axis is world-up**: The positive Y-axis points upward in world space
//! - **Camera view direction is -Z**: When looking through a camera, the view direction is along the negative Z-axis
//! - **Points with negative Z coordinates are in front of cameras**
//!
//! ## Center vs Translation Representation
//!
//! This struct uses a center-based representation where:
//! - `center`: The 3D position of the camera in world coordinates
//! - `rotation`: The orientation matrix from world to camera coordinates
//! - Translation is computed as: `t = -R * C`
//!
//! This is in contrast to the translation-based representation used by [`CameraPoseAlternate`](crate::datatype::CameraPoseAlternate).

use nalgebra::{Matrix3, Point3, Vector3};
use std::f64::consts::PI;
use std::ops::Mul;

/// Check if a pose is valid (contains no NaN values)
///
/// This function checks for NaN values in:
/// - The pose center coordinates
/// - The pose translation coordinates
/// - All rotation matrix elements
///
/// # Arguments
/// * `pose` - The pose to validate
///
/// # Returns
/// `true` if the pose is valid (contains no NaN values), `false` otherwise
pub fn is_valid_pose(pose: &CameraPose) -> bool {
    let center = pose.center();
    let translation = pose.translation();
    let rotation = pose.rotation();

    // Check center for NaN values
    let center_has_nan =
        center.x.is_nan() || center.y.is_nan() || center.z.is_nan();

    // Check translation for NaN values
    let translation_has_nan = translation[0].is_nan()
        || translation[1].is_nan()
        || translation[2].is_nan();

    // Check rotation matrix for NaN values
    let rotation_has_nan = rotation[(0, 0)].is_nan()
        || rotation[(0, 1)].is_nan()
        || rotation[(0, 2)].is_nan()
        || rotation[(1, 0)].is_nan()
        || rotation[(1, 1)].is_nan()
        || rotation[(1, 2)].is_nan()
        || rotation[(2, 0)].is_nan()
        || rotation[(2, 1)].is_nan()
        || rotation[(2, 2)].is_nan();

    // Return false if any component has NaN, true otherwise
    !(center_has_nan || translation_has_nan || rotation_has_nan)
}

/// Create a camera pose from Maya-style transform values
///
/// Mathematical reference: Based on mmscenegraph::transform::calculate_matrix()
/// which is the proven correct implementation for Maya coordinate system.
///
/// Maya conventions:
/// - Right-hand coordinate system
/// - +Y axis is world-up
/// - Camera looks down -Z axis
/// - ZXY rotation order (Maya camera default)
///
/// # Arguments
/// * `translate_x` - Translation in X axis (world units)
/// * `translate_y` - Translation in Y axis (world units)
/// * `translate_z` - Translation in Z axis (world units)
/// * `rotate_x_degrees` - Rotation around X axis in degrees
/// * `rotate_y_degrees` - Rotation around Y axis in degrees
/// * `rotate_z_degrees` - Rotation around Z axis in degrees
///
/// # Returns
/// CameraPose with the specified transform
pub fn create_camera_pose_from_maya_transform(
    translate_x: f64,
    translate_y: f64,
    translate_z: f64,
    rotate_x_degrees: f64,
    rotate_y_degrees: f64,
    rotate_z_degrees: f64,
) -> CameraPose {
    // Convert degrees to radians.
    let rx = rotate_x_degrees * PI / 180.0;
    let ry = rotate_y_degrees * PI / 180.0;
    let rz = rotate_z_degrees * PI / 180.0;

    // Create individual rotation matrices following Maya convention.
    let (sin_rx, cos_rx) = rx.sin_cos();
    let (sin_ry, cos_ry) = ry.sin_cos();
    let (sin_rz, cos_rz) = rz.sin_cos();

    let rotx = Matrix3::new(
        1.0, 0.0, 0.0, //
        0.0, cos_rx, -sin_rx, //
        0.0, sin_rx, cos_rx, //
    );
    let roty = Matrix3::new(
        cos_ry, 0.0, sin_ry, //
        0.0, 1.0, 0.0, //
        -sin_ry, 0.0, cos_ry, //
    );
    let rotz = Matrix3::new(
        cos_rz, -sin_rz, 0.0, //
        sin_rz, cos_rz, 0.0, //
        0.0, 0.0, 1.0, //
    );

    // ZXY rotation order.
    //
    // Note: mmscenegraph comment states "rotation order is reversed
    // because nalgebra stores matrices as column-major".
    let maya_object_rotation = roty * rotx * rotz; // Maya object transform

    // For CameraPose, we need world-to-camera transformation.
    let camera_rotation = maya_object_rotation.transpose();

    // Set camera center position.
    let center = Point3::new(translate_x, translate_y, translate_z);

    CameraPose::new(camera_rotation, center)
}

/// A camera pose using center-based parameterization.
///
/// This struct represents a camera pose using the camera center position
/// and rotation matrix, following Maya's coordinate system conventions.
///
/// ## Coordinate System
///
/// Follows Maya coordinate system convention:
/// - Right-hand coordinate system
/// - +Y axis is world-up
/// - Camera view direction is along negative Z-axis
/// - Points with negative Z coordinates are in front of cameras
///
/// ## Mathematical Representation
///
/// - `rotation`: 3x3 rotation matrix R from world to camera coordinates
/// - `center`: 3D position C of camera in world coordinates
/// - Translation computed as: `t = -R * C`
/// - Point transformation: `p_cam = R * (p_world - C)`
#[derive(Debug, Clone, PartialEq)]
pub struct CameraPose {
    /// Orientation matrix from world to camera coordinates
    rotation: Matrix3<f64>,

    /// Center of rotation in world coordinates
    center: Point3<f64>,
}

impl CameraPose {
    /// Constructor
    ///
    /// # Arguments
    /// * `rotation` - Rotation matrix (defaults to Identity)
    /// * `center` - Center of rotation (defaults to Zero)
    pub fn new(rotation: Matrix3<f64>, center: Point3<f64>) -> Self {
        Self { rotation, center }
    }

    /// Get immutable reference to rotation matrix
    pub fn rotation(&self) -> &Matrix3<f64> {
        &self.rotation
    }

    /// Get mutable reference to rotation matrix
    pub fn rotation_mut(&mut self) -> &mut Matrix3<f64> {
        &mut self.rotation
    }

    /// Get immutable reference to center of rotation
    pub fn center(&self) -> &Point3<f64> {
        &self.center
    }

    /// Get mutable reference to center of rotation
    pub fn center_mut(&mut self) -> &mut Point3<f64> {
        &mut self.center
    }

    /// Get translation vector
    ///
    /// TODO: Explain what the translation/displacement vector is and
    /// what it represents.
    ///
    /// # Returns
    /// Translation vector t = -R * C
    pub fn translation(&self) -> Vector3<f64> {
        -(self.rotation * self.center.coords)
    }

    /// Apply pose transformation to a 3D point
    ///
    /// Transforms a point from world coordinates to camera coordinates.
    ///
    /// In Maya's coordinate system, points with negative Z are in front of the camera.
    ///
    /// # Arguments
    /// * `point` - 3D point to transform in world coordinates
    ///
    /// # Returns
    /// Transformed point in camera coordinates = R * (p - C)
    pub fn apply_transform(&self, point: &Point3<f64>) -> Point3<f64> {
        Point3::from(self.rotation * (point.coords - self.center.coords))
    }

    /// Transform a vector from camera space to world space
    ///
    /// Transforms a direction vector from camera coordinates to world coordinates.
    /// Unlike point transformation, vector transformation does not involve translation
    /// (the camera center), only rotation.
    ///
    /// This is the inverse transformation compared to `apply_transform`, which
    /// transforms from world to camera space.
    ///
    /// # Arguments
    /// * `camera_vector` - Direction vector in camera coordinates
    ///
    /// # Returns
    /// Transformed vector in world coordinates = R^T * v
    ///
    /// # Example
    /// ```
    /// use nalgebra::{Matrix3, Point3, Vector3};
    /// use mmsfm_rust::datatype::camera_pose::CameraPose;
    ///
    /// let pose = CameraPose::default();
    /// let camera_ray = Vector3::new(0.0, 0.0, -1.0); // Looking down -Z in camera space
    /// let world_ray = pose.apply_transform_to_vector(&camera_ray);
    /// // For identity pose, camera and world space are the same
    /// assert_eq!(world_ray, camera_ray);
    /// ```
    pub fn apply_transform_to_vector(
        &self,
        camera_vector: &Vector3<f64>,
    ) -> Vector3<f64> {
        self.rotation.transpose() * camera_vector
    }

    /// Transform a vector from world space to camera space
    ///
    /// Transforms a direction vector from world coordinates to camera coordinates.
    /// Unlike point transformation, vector transformation does not involve translation
    /// (the camera center), only rotation.
    ///
    /// This is the complement to `apply_transform_to_vector`, which transforms
    /// from camera to world space. Together they provide symmetric vector
    /// transformations in both directions.
    ///
    /// # Arguments
    /// * `world_vector` - Direction vector in world coordinates
    ///
    /// # Returns
    /// Transformed vector in camera coordinates = R * v
    ///
    /// # Example
    /// ```
    /// use nalgebra::{Matrix3, Point3, Vector3};
    /// use mmsfm_rust::datatype::camera_pose::CameraPose;
    ///
    /// let pose = CameraPose::default();
    /// let world_direction = Vector3::new(0.0, 0.0, -1.0);
    /// let camera_direction = pose.transform_vector_to_camera(&world_direction);
    /// // For identity pose, camera and world space are the same
    /// assert_eq!(camera_direction, world_direction);
    /// ```
    pub fn transform_vector_to_camera(
        &self,
        world_vector: &Vector3<f64>,
    ) -> Vector3<f64> {
        self.rotation * world_vector
    }

    /// Check if a 3D point is in front of the camera
    ///
    /// Uses Maya's coordinate system convention where negative Z is forward.
    ///
    /// # Arguments
    /// * `world_point` - 3D point in world coordinates
    ///
    /// # Returns
    /// * `bool` - True if the point is in front of the camera (negative Z)
    pub fn is_point_in_front(&self, world_point: &Point3<f64>) -> bool {
        let camera_point = self.apply_transform(world_point);
        // Maya convention: negative Z is forward.
        camera_point.z < 0.0
    }

    /// Get inverse of the pose
    ///
    /// For a center-based camera pose with rotation R and center C:
    /// - Forward transform: p_cam = R * (p_world - C)
    /// - Inverse transform: p_world = R^T * p_cam + C
    ///
    /// To maintain the same representation form, the inverse pose has:
    /// - Rotation: R^T (transpose of the original rotation)
    /// - Center: -R * C (derived from inverse transformation requirements)
    ///
    /// # Returns
    /// Inverse pose
    pub fn inverse(&self) -> CameraPose {
        let rotation_transpose = self.rotation.transpose();
        let new_center = Point3::from(-(self.rotation * self.center.coords));
        CameraPose::new(rotation_transpose, new_center)
    }

    /// Returns the 3x4 extrinsic matrix [R|t] for this pose.
    ///
    /// This matrix performs the world-to-camera transformation.
    /// It is composed of the rotation matrix `R` and the translation vector `t`,
    /// where `t = -R * C`.
    ///
    /// A 3D point in world coordinates `p_world` can be transformed to
    /// camera coordinates `p_cam` by `p_cam = R * p_world + t`.
    ///
    /// # Returns
    /// 3x4 matrix representing the pose as `[R | -R*C]`.
    pub fn as_extrinsic_matrix(&self) -> nalgebra::Matrix3x4<f64> {
        let translation = self.translation();
        nalgebra::Matrix3x4::new(
            self.rotation[(0, 0)],
            self.rotation[(0, 1)],
            self.rotation[(0, 2)],
            translation[0],
            self.rotation[(1, 0)],
            self.rotation[(1, 1)],
            self.rotation[(1, 2)],
            translation[1],
            self.rotation[(2, 0)],
            self.rotation[(2, 1)],
            self.rotation[(2, 2)],
            translation[2],
        )
    }
}

impl Default for CameraPose {
    /// Default constructor creates an Identity pose
    fn default() -> Self {
        Self {
            rotation: Matrix3::identity(),
            center: Point3::origin(),
        }
    }
}

impl Mul<CameraPose> for CameraPose {
    type Output = CameraPose;

    /// Composition of poses
    ///
    /// # Arguments
    /// * `rhs` - Another pose to compose with
    ///
    /// # Returns
    /// Composition of current pose and parameter pose
    fn mul(self, rhs: CameraPose) -> Self::Output {
        let new_rotation = self.rotation * rhs.rotation;
        let new_center = Point3::from(
            rhs.center.coords + rhs.rotation.transpose() * self.center.coords,
        );
        CameraPose::new(new_rotation, new_center)
    }
}

impl Mul<&CameraPose> for &CameraPose {
    type Output = CameraPose;

    /// Composition of poses (reference version)
    fn mul(self, rhs: &CameraPose) -> Self::Output {
        let new_rotation = self.rotation * rhs.rotation;
        let new_center = Point3::from(
            rhs.center.coords + rhs.rotation.transpose() * self.center.coords,
        );
        CameraPose::new(new_rotation, new_center)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    #[test]
    fn test_pose3_default() {
        let pose = CameraPose::default();

        // Should be identity rotation and zero center
        assert_eq!(*pose.rotation(), Matrix3::identity());
        assert_eq!(*pose.center(), Point3::origin());

        // Translation should also be zero for identity pose
        assert_eq!(pose.translation(), Vector3::zeros());
    }

    #[test]
    fn test_pose3_translation() {
        // Create a simple pose with rotation and center
        let rotation = Matrix3::identity();
        let center = Point3::new(1.0, 2.0, 3.0);
        let pose = CameraPose::new(rotation, center);

        // For identity rotation: t = -R * C = -I * C = -C
        let expected_translation = Vector3::new(-1.0, -2.0, -3.0);
        assert_relative_eq!(
            pose.translation(),
            expected_translation,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_pose3_apply_transform() {
        let rotation = Matrix3::identity();
        let center = Point3::new(1.0, 0.0, 0.0);
        let pose = CameraPose::new(rotation, center);

        let point = Point3::new(2.0, 1.0, 0.0);

        // For identity rotation: result = R * (p - C) = I * (p - C) = p - C
        let expected = Point3::new(1.0, 1.0, 0.0);
        assert_relative_eq!(
            pose.apply_transform(&point),
            expected,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_pose3_inverse() {
        let rotation = Matrix3::identity();
        let center = Point3::new(1.0, 2.0, 3.0);
        let pose = CameraPose::new(rotation, center);

        let inverse = pose.inverse();

        // For identity rotation, inverse should have:
        // - rotation = I^T = I
        // - center = -(R * C) = -(I * C) = -C
        assert_relative_eq!(
            *inverse.rotation(),
            Matrix3::identity(),
            epsilon = 1e-10
        );
        assert_relative_eq!(
            *inverse.center(),
            Point3::new(-1.0, -2.0, -3.0),
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_pose3_composition() {
        let pose1 = CameraPose::default(); // Identity
        let rotation2 = Matrix3::identity();
        let center2 = Point3::new(1.0, 0.0, 0.0);
        let pose2 = CameraPose::new(rotation2, center2);

        // Composing identity with another pose should yield the other pose
        let result = pose1 * pose2.clone();
        assert_relative_eq!(
            *result.rotation(),
            *pose2.rotation(),
            epsilon = 1e-10
        );
        assert_relative_eq!(*result.center(), *pose2.center(), epsilon = 1e-10);
    }

    #[test]
    fn test_pose3_as_extrinsic_matrix() {
        let rotation = Matrix3::identity();
        let center = Point3::new(1.0, 2.0, 3.0);
        let pose = CameraPose::new(rotation, center);

        let matrix = pose.as_extrinsic_matrix();

        // Should be [I | -C] for identity rotation (3x4 matrix)
        assert_relative_eq!(matrix[(0, 0)], 1.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(1, 1)], 1.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(2, 2)], 1.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(0, 3)], -1.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(1, 3)], -2.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(2, 3)], -3.0, epsilon = 1e-10);

        // Verify off-diagonal rotation elements are zero
        assert_relative_eq!(matrix[(0, 1)], 0.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(0, 2)], 0.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(1, 0)], 0.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(1, 2)], 0.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(2, 0)], 0.0, epsilon = 1e-10);
        assert_relative_eq!(matrix[(2, 1)], 0.0, epsilon = 1e-10);
    }

    #[test]
    fn test_is_valid_pose_with_valid_pose() {
        // Test with a valid pose (identity)
        let pose = CameraPose::default();
        assert!(is_valid_pose(&pose));

        // Test with a valid pose with non-zero values
        let rotation =
            Matrix3::new(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0);
        let center = Point3::new(1.0, 2.0, 3.0);
        let pose = CameraPose::new(rotation, center);
        assert!(is_valid_pose(&pose));
    }

    #[test]
    fn test_is_valid_pose_with_nan_in_center() {
        let rotation = Matrix3::identity();

        // Test NaN in center x-coordinate
        let center = Point3::new(f64::NAN, 0.0, 0.0);
        let pose = CameraPose::new(rotation, center);
        assert!(!is_valid_pose(&pose));

        // Test NaN in center y-coordinate
        let center = Point3::new(0.0, f64::NAN, 0.0);
        let pose = CameraPose::new(rotation, center);
        assert!(!is_valid_pose(&pose));

        // Test NaN in center z-coordinate
        let center = Point3::new(0.0, 0.0, f64::NAN);
        let pose = CameraPose::new(rotation, center);
        assert!(!is_valid_pose(&pose));
    }

    #[test]
    fn test_is_valid_pose_with_nan_in_rotation() {
        let center = Point3::origin();

        // Test NaN in rotation matrix (0,0)
        let rotation =
            Matrix3::new(f64::NAN, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0);
        let pose = CameraPose::new(rotation, center);
        assert!(!is_valid_pose(&pose));

        // Test NaN in rotation matrix (1,1)
        let rotation =
            Matrix3::new(1.0, 0.0, 0.0, 0.0, f64::NAN, 0.0, 0.0, 0.0, 1.0);
        let pose = CameraPose::new(rotation, center);
        assert!(!is_valid_pose(&pose));

        // Test NaN in rotation matrix (2,2)
        let rotation =
            Matrix3::new(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, f64::NAN);
        let pose = CameraPose::new(rotation, center);
        assert!(!is_valid_pose(&pose));

        // Test NaN in rotation matrix off-diagonal element (0,1)
        let rotation =
            Matrix3::new(1.0, f64::NAN, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0);
        let pose = CameraPose::new(rotation, center);
        assert!(!is_valid_pose(&pose));
    }

    #[test]
    fn test_is_valid_pose_with_infinity() {
        // Test case where infinity in center causes NaN in translation computation
        // Even with identity matrix, nalgebra matrix multiplication can produce NaN
        let rotation = Matrix3::identity();
        let center = Point3::new(f64::INFINITY, 0.0, 0.0);
        let pose = CameraPose::new(rotation, center);
        // Matrix multiplication with infinity can produce NaN, making the pose invalid
        assert!(!is_valid_pose(&pose));

        // Test with infinity in rotation matrix and zero center
        // This produces NaN because inf * 0 = NaN in the translation computation
        let center = Point3::origin();
        let rotation =
            Matrix3::new(f64::INFINITY, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0);
        let pose = CameraPose::new(rotation, center);
        // Translation computation will produce NaN because inf * 0 = NaN
        assert!(!is_valid_pose(&pose));

        // Test with infinity in rotation matrix and non-zero center
        // This should produce infinity in translation (inf * non-zero = inf)
        let center = Point3::new(1.0, 0.0, 0.0);
        let rotation =
            Matrix3::new(f64::INFINITY, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0);
        let pose = CameraPose::new(rotation, center);
        // Translation will be [inf, 0, 0], which contains infinity but not NaN
        assert!(is_valid_pose(&pose)); // Should be valid since no NaN is produced

        // Test a normal case for comparison
        let center = Point3::new(1.0, 2.0, 3.0);
        let rotation =
            Matrix3::new(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0);
        let pose = CameraPose::new(rotation, center);
        assert!(is_valid_pose(&pose)); // Normal case should be valid
    }

    #[test]
    fn test_is_valid_pose_with_multiple_nans() {
        // Test with multiple NaN values
        let rotation = Matrix3::new(
            f64::NAN,
            0.0,
            0.0,
            0.0,
            f64::NAN,
            0.0,
            0.0,
            0.0,
            f64::NAN,
        );
        let center = Point3::new(f64::NAN, f64::NAN, f64::NAN);
        let pose = CameraPose::new(rotation, center);
        assert!(!is_valid_pose(&pose));
    }

    #[test]
    fn test_maya_coordinate_system_validation() {
        // Test Maya coordinate system conventions
        let pose = CameraPose::default(); // Camera at origin

        // Test points at various Z coordinates
        let point_in_front_1 = Point3::new(0.0, 0.0, -5.0); // Negative Z = in front
        let point_in_front_2 = Point3::new(1.0, 1.0, -10.0); // Negative Z = in front
        let point_behind_1 = Point3::new(0.0, 0.0, 5.0); // Positive Z = behind
        let point_behind_2 = Point3::new(-1.0, 1.0, 2.0); // Positive Z = behind

        // Verify Maya convention: negative Z is in front of camera
        assert!(pose.is_point_in_front(&point_in_front_1));
        assert!(pose.is_point_in_front(&point_in_front_2));
        assert!(!pose.is_point_in_front(&point_behind_1));
        assert!(!pose.is_point_in_front(&point_behind_2));
    }

    #[test]
    fn test_camera_transform_with_maya_conventions() {
        // Test camera transformation with specific Z coordinates
        let pose = CameraPose::default(); // Identity pose

        // Point in front of camera (negative Z)
        let world_point = Point3::new(1.0, 2.0, -5.0);
        let camera_point = pose.apply_transform(&world_point);

        // For identity pose, camera_point should equal world_point
        assert_relative_eq!(camera_point, world_point, epsilon = 1e-10);

        // Verify it's considered in front
        assert!(
            camera_point.z < 0.0,
            "Point should be in front (negative Z)"
        );
        assert!(pose.is_point_in_front(&world_point));
    }

    #[test]
    fn test_maya_coordinate_system_y_rotation() {
        // Test that Maya +90° Y rotation makes camera look towards -X axis
        //
        // Reference for mathematical correctness with Maya:
        // ./lib/rust/mmscenegraph/src/math/transform.rs

        // Maya camera rotated +90° around Y axis should look towards -X axis
        // This follows the right-hand coordinate system where:
        // - +Y is up
        // - Camera normally looks down -Z
        // - +90° Y rotation turns camera to look down -X

        // Create rotation matrix for +90° Y rotation using Maya conventions
        let ry_rad = 90.0 * std::f64::consts::PI / 180.0;
        let (sin_ry, cos_ry) = ry_rad.sin_cos();

        // Maya object transform for +90° Y rotation
        let maya_object_rotation = Matrix3::new(
            cos_ry, 0.0, sin_ry, // [0, 0, 1]
            0.0, 1.0, 0.0, // [0, 1, 0]
            -sin_ry, 0.0, cos_ry, // [-1, 0, 0]
        );

        // For camera pose, we need world-to-camera transform (inverse)
        let camera_rotation = maya_object_rotation.transpose();
        let center = Point3::new(0.0, 0.0, 0.0);
        let pose = CameraPose::new(camera_rotation, center);

        // Point at -X should be in front of +90° Y-rotated camera
        let point_in_front = Point3::new(-5.0, 0.0, 0.0);
        assert!(
            pose.is_point_in_front(&point_in_front),
            "Maya camera rotated +90° Y should look towards -X axis"
        );

        // Point at +X should be behind +90° Y-rotated camera
        let point_behind = Point3::new(5.0, 0.0, 0.0);
        assert!(
            !pose.is_point_in_front(&point_behind),
            "Point at +X should be behind +90° Y-rotated Maya camera"
        );
    }

    #[test]
    fn test_apply_transform_to_vector_with_identity() {
        // Test vector transformation with identity pose
        let pose = CameraPose::default();
        let camera_vector = Vector3::new(1.0, 2.0, 3.0);

        // For identity rotation, camera and world vectors should be the same
        let world_vector = pose.apply_transform_to_vector(&camera_vector);
        assert_relative_eq!(world_vector, camera_vector, epsilon = 1e-10);
    }

    #[test]
    fn test_apply_transform_to_vector_camera_forward_ray() {
        // Test that camera forward direction (-Z in camera space)
        // transforms correctly for identity pose
        let pose = CameraPose::default();
        let camera_forward = Vector3::new(0.0, 0.0, -1.0);

        let world_forward = pose.apply_transform_to_vector(&camera_forward);

        // For identity pose, camera -Z maps to world -Z
        assert_relative_eq!(
            world_forward,
            Vector3::new(0.0, 0.0, -1.0),
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_apply_transform_to_vector_with_y_rotation() {
        // Test vector transformation with +90° Y rotation
        // Camera rotated +90° Y looks down -X axis in world space

        let ry_rad = 90.0 * std::f64::consts::PI / 180.0;
        let (sin_ry, cos_ry) = ry_rad.sin_cos();

        // Maya object transform for +90° Y rotation
        let maya_object_rotation = Matrix3::new(
            cos_ry, 0.0, sin_ry, 0.0, 1.0, 0.0, -sin_ry, 0.0, cos_ry,
        );

        // For camera pose, we need world-to-camera transform
        let camera_rotation = maya_object_rotation.transpose();
        let center = Point3::origin();
        let pose = CameraPose::new(camera_rotation, center);

        // Camera forward direction is -Z in camera space
        let camera_forward = Vector3::new(0.0, 0.0, -1.0);
        let world_forward = pose.apply_transform_to_vector(&camera_forward);

        // After +90° Y rotation, camera -Z points to world -X
        assert_relative_eq!(
            world_forward,
            Vector3::new(-1.0, 0.0, 0.0),
            epsilon = 1e-10
        );

        // Camera right direction is +X in camera space
        let camera_right = Vector3::new(1.0, 0.0, 0.0);
        let world_right = pose.apply_transform_to_vector(&camera_right);

        // After +90° Y rotation, camera +X points to world -Z
        assert_relative_eq!(
            world_right,
            Vector3::new(0.0, 0.0, -1.0),
            epsilon = 1e-10
        );

        // Camera up direction is +Y in camera space (unchanged by Y rotation)
        let camera_up = Vector3::new(0.0, 1.0, 0.0);
        let world_up = pose.apply_transform_to_vector(&camera_up);

        // Y rotation doesn't affect Y axis
        assert_relative_eq!(
            world_up,
            Vector3::new(0.0, 1.0, 0.0),
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_apply_transform_to_vector_inverse_of_rotation() {
        // Test that apply_transform_to_vector is the inverse of
        // applying rotation directly to world vectors

        let ry_rad = 45.0 * std::f64::consts::PI / 180.0;
        let (sin_ry, cos_ry) = ry_rad.sin_cos();

        let maya_object_rotation = Matrix3::new(
            cos_ry, 0.0, sin_ry, 0.0, 1.0, 0.0, -sin_ry, 0.0, cos_ry,
        );

        let camera_rotation = maya_object_rotation.transpose();
        let center = Point3::origin();
        let pose = CameraPose::new(camera_rotation, center);

        // Start with a world vector
        let world_vector = Vector3::new(1.0, 2.0, 3.0);

        // Transform world → camera using rotation directly
        let camera_vector = pose.rotation() * world_vector;

        // Transform camera → world using our method
        let world_vector_reconstructed =
            pose.apply_transform_to_vector(&camera_vector);

        // Should get back the original world vector
        assert_relative_eq!(
            world_vector_reconstructed,
            world_vector,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_transform_vector_to_camera_with_identity() {
        // Test vector transformation with identity pose
        let pose = CameraPose::default();
        let world_vector = Vector3::new(1.0, 2.0, 3.0);

        // For identity rotation, camera and world vectors should be the same
        let camera_vector = pose.transform_vector_to_camera(&world_vector);
        assert_relative_eq!(camera_vector, world_vector, epsilon = 1e-10);
    }

    #[test]
    fn test_transform_vector_to_camera_world_forward() {
        // Test that world -Z direction transforms correctly to camera space
        let pose = CameraPose::default();
        let world_forward = Vector3::new(0.0, 0.0, -1.0);

        let camera_forward = pose.transform_vector_to_camera(&world_forward);

        // For identity pose, world -Z maps to camera -Z
        assert_relative_eq!(
            camera_forward,
            Vector3::new(0.0, 0.0, -1.0),
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_transform_vector_to_camera_with_y_rotation() {
        // Test vector transformation with +90° Y rotation
        // Camera rotated +90° Y looks down -X axis in world space

        let ry_rad = 90.0 * std::f64::consts::PI / 180.0;
        let (sin_ry, cos_ry) = ry_rad.sin_cos();

        // Maya object transform for +90° Y rotation
        let maya_object_rotation = Matrix3::new(
            cos_ry, 0.0, sin_ry, 0.0, 1.0, 0.0, -sin_ry, 0.0, cos_ry,
        );

        // For camera pose, we need world-to-camera transform
        let camera_rotation = maya_object_rotation.transpose();
        let center = Point3::origin();
        let pose = CameraPose::new(camera_rotation, center);

        // World -X direction (where camera is looking after +90° Y rotation)
        let world_forward = Vector3::new(-1.0, 0.0, 0.0);
        let camera_direction = pose.transform_vector_to_camera(&world_forward);

        // World -X should map to camera -Z (forward in camera space)
        assert_relative_eq!(
            camera_direction,
            Vector3::new(0.0, 0.0, -1.0),
            epsilon = 1e-10
        );

        // World -Z direction
        let world_z = Vector3::new(0.0, 0.0, -1.0);
        let camera_z = pose.transform_vector_to_camera(&world_z);

        // World -Z should map to camera +X (right in camera space)
        assert_relative_eq!(
            camera_z,
            Vector3::new(1.0, 0.0, 0.0),
            epsilon = 1e-10
        );

        // World +Y direction (up, unchanged by Y rotation)
        let world_up = Vector3::new(0.0, 1.0, 0.0);
        let camera_up = pose.transform_vector_to_camera(&world_up);

        // Y rotation doesn't affect Y axis
        assert_relative_eq!(
            camera_up,
            Vector3::new(0.0, 1.0, 0.0),
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_transform_vector_to_camera_is_inverse_of_apply_transform_to_vector()
    {
        // Test that transform_vector_to_camera and apply_transform_to_vector
        // are inverses of each other

        let ry_rad = 45.0 * std::f64::consts::PI / 180.0;
        let (sin_ry, cos_ry) = ry_rad.sin_cos();

        let maya_object_rotation = Matrix3::new(
            cos_ry, 0.0, sin_ry, 0.0, 1.0, 0.0, -sin_ry, 0.0, cos_ry,
        );

        let camera_rotation = maya_object_rotation.transpose();
        let center = Point3::origin();
        let pose = CameraPose::new(camera_rotation, center);

        // Start with a world vector
        let world_vector_original = Vector3::new(1.0, 2.0, 3.0);

        // Transform world → camera
        let camera_vector =
            pose.transform_vector_to_camera(&world_vector_original);

        // Transform camera → world
        let world_vector_reconstructed =
            pose.apply_transform_to_vector(&camera_vector);

        // Should get back the original world vector
        assert_relative_eq!(
            world_vector_reconstructed,
            world_vector_original,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_vector_transformation_roundtrip() {
        // Test complete roundtrip: world → camera → world and camera → world → camera

        let ry_rad = 60.0 * std::f64::consts::PI / 180.0;
        let (sin_ry, cos_ry) = ry_rad.sin_cos();

        let maya_object_rotation = Matrix3::new(
            cos_ry, 0.0, sin_ry, 0.0, 1.0, 0.0, -sin_ry, 0.0, cos_ry,
        );

        let camera_rotation = maya_object_rotation.transpose();
        let center = Point3::origin();
        let pose = CameraPose::new(camera_rotation, center);

        // Test roundtrip starting from world space
        let world_vector = Vector3::new(3.0, 4.0, 5.0);
        let to_camera = pose.transform_vector_to_camera(&world_vector);
        let back_to_world = pose.apply_transform_to_vector(&to_camera);
        assert_relative_eq!(back_to_world, world_vector, epsilon = 1e-10);

        // Test roundtrip starting from camera space
        let camera_vector = Vector3::new(0.5, 1.5, -2.0);
        let to_world = pose.apply_transform_to_vector(&camera_vector);
        let back_to_camera = pose.transform_vector_to_camera(&to_world);
        assert_relative_eq!(back_to_camera, camera_vector, epsilon = 1e-10);
    }
}
