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

use nalgebra::Vector3;

use crate::datatype::camera_coord_value::CameraCoordVector2;
use crate::datatype::common::UnitValue;

/// Represents a point correspondence between two camera frames using
/// normalized bearing vectors.
///
/// The bearing vectors are constructed from normalized camera coordinates
/// which are the result of applying camera intrinsics transformation:
/// `(ndc_coord - principal_point) / focal_length`
///
/// This type is specifically designed for algorithms that work with bearing
/// vectors, such as essential matrix estimation and relative pose computation.
#[derive(Debug, Clone, Copy)]
pub struct BearingVectorCorrespondence {
    /// Bearing vector from camera A (normalized camera coordinates).
    // TODO: Convert this Vector3 into a CameraCoordVector3 data type.
    pub camera_a: Vector3<f64>,
    /// Bearing vector from camera B (normalized camera coordinates).
    // TODO: Convert this Vector3 into a CameraCoordVector3 data type.
    pub camera_b: Vector3<f64>,
}

impl BearingVectorCorrespondence {
    /// Create a new bearing vector correspondence from camera coordinate vectors.
    ///
    /// This method creates normalized unit vectors (bearing vectors) required by
    /// the five-point essential matrix algorithm.
    ///
    /// # Arguments
    /// * `camera_coord_a` - Camera coordinate vector for camera A
    /// * `camera_coord_b` - Camera coordinate vector for camera B
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let coord_a = CameraCoordValue::vector2(-0.5, 0.3);
    /// let coord_b = CameraCoordValue::vector2(-0.4, 0.35);
    /// let correspondence = BearingVectorCorrespondence::new(coord_a, coord_b);
    /// ```
    ///
    /// # Algorithm Requirements
    /// - **Five-point algorithm**: Uses this method (unit bearing vectors)
    /// - **Six/Seven/Eight-point algorithms**: Use `from_homogeneous_coordinates()` instead
    pub fn new(
        // TODO: Are these Vectors? Shouldn't they be Points?
        camera_coord_a: CameraCoordVector2<f64>,
        camera_coord_b: CameraCoordVector2<f64>,
    ) -> Self {
        // Create normalized unit vectors (bearing vectors) from camera coordinates
        // Five-point algorithm requires unit vectors
        let unnormalized_a = Vector3::new(
            camera_coord_a.x.value(),
            camera_coord_a.y.value(),
            1.0,
        );
        let unnormalized_b = Vector3::new(
            camera_coord_b.x.value(),
            camera_coord_b.y.value(),
            1.0,
        );

        Self {
            camera_a: unnormalized_a.normalize(),
            camera_b: unnormalized_b.normalize(),
        }
    }

    /// Create a new bearing vector correspondence from homogeneous camera coordinates.
    ///
    /// This method creates homogeneous coordinates (z=1) required by algorithms that
    /// use Hartley normalization for numerical stability.
    ///
    /// # Arguments
    /// * `camera_coord_a` - Camera coordinate vector for camera A
    /// * `camera_coord_b` - Camera coordinate vector for camera B
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let coord_a = CameraCoordValue::vector2(-0.5, 0.3);
    /// let coord_b = CameraCoordValue::vector2(-0.4, 0.35);
    /// let correspondence = BearingVectorCorrespondence::from_homogeneous_coordinates(coord_a, coord_b);
    /// ```
    ///
    /// # Algorithm Requirements
    /// - **Six-point algorithm**: Uses this method (Hartley normalization)
    /// - **Seven-point algorithm**: Uses this method (Hartley normalization)
    /// - **Eight-point algorithm**: Uses this method (Hartley normalization)
    /// - **Eight-plus-point algorithm**: Uses this method (Hartley normalization)
    /// - **Five-point algorithm**: Use `new()` instead (no normalization needed)
    pub fn from_homogeneous_coordinates(
        // TODO: Are these Vectors? Shouldn't they be Points?
        camera_coord_a: CameraCoordVector2<f64>,
        camera_coord_b: CameraCoordVector2<f64>,
    ) -> Self {
        // Create homogeneous coordinates (z=1) from camera coordinates
        // Eight-point and eight-plus-point algorithms expect homogeneous coordinates
        Self {
            camera_a: Vector3::new(
                camera_coord_a.x.value(),
                camera_coord_a.y.value(),
                1.0,
            ),
            camera_b: Vector3::new(
                camera_coord_b.x.value(),
                camera_coord_b.y.value(),
                1.0,
            ),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::CameraCoordValue;

    #[test]
    fn test_bearing_vector_correspondence_creation() {
        use approx::assert_relative_eq;

        let coord_a = CameraCoordValue::vector2(-0.5, -0.5);
        let coord_b = CameraCoordValue::vector2(-0.4, -0.6);
        let corr = BearingVectorCorrespondence::new(coord_a, coord_b);

        // Verify that the vectors are normalized to unit length
        assert_relative_eq!(corr.camera_a.norm(), 1.0, epsilon = 1e-10);
        assert_relative_eq!(corr.camera_b.norm(), 1.0, epsilon = 1e-10);

        // Calculate expected normalized values for camera_a: (-0.5, -0.5, 1.0)
        let length_a = (0.5_f64 * 0.5 + 0.5 * 0.5 + 1.0 * 1.0).sqrt(); // sqrt(1.5) ≈ 1.224744871
        let expected_a_x = -0.5 / length_a;
        let expected_a_y = -0.5 / length_a;
        let expected_a_z = 1.0 / length_a;

        assert_relative_eq!(corr.camera_a.x, expected_a_x, epsilon = 1e-10);
        assert_relative_eq!(corr.camera_a.y, expected_a_y, epsilon = 1e-10);
        assert_relative_eq!(corr.camera_a.z, expected_a_z, epsilon = 1e-10);

        // Calculate expected normalized values for camera_b: (-0.4, -0.6, 1.0)
        let length_b = (0.4_f64 * 0.4 + 0.6 * 0.6 + 1.0 * 1.0).sqrt(); // sqrt(1.52) ≈ 1.233287108
        let expected_b_x = -0.4 / length_b;
        let expected_b_y = -0.6 / length_b;
        let expected_b_z = 1.0 / length_b;

        assert_relative_eq!(corr.camera_b.x, expected_b_x, epsilon = 1e-10);
        assert_relative_eq!(corr.camera_b.y, expected_b_y, epsilon = 1e-10);
        assert_relative_eq!(corr.camera_b.z, expected_b_z, epsilon = 1e-10);
    }

    #[test]
    fn test_bearing_vector_correspondence_from_homogeneous() {
        let coord_a = CameraCoordValue::vector2(-0.5, -0.5);
        let coord_b = CameraCoordValue::vector2(-0.4, -0.6);
        let corr = BearingVectorCorrespondence::from_homogeneous_coordinates(
            coord_a, coord_b,
        );

        // Verify that the vectors have z=1.0 (homogeneous coordinates)
        assert_eq!(corr.camera_a.z, 1.0);
        assert_eq!(corr.camera_b.z, 1.0);

        // Verify the x and y coordinates are preserved
        assert_eq!(corr.camera_a.x, -0.5);
        assert_eq!(corr.camera_a.y, -0.5);
        assert_eq!(corr.camera_b.x, -0.4);
        assert_eq!(corr.camera_b.y, -0.6);

        // Verify these are NOT unit vectors
        let norm_a = corr.camera_a.norm();
        let norm_b = corr.camera_b.norm();
        assert!(norm_a > 1.0); // Should be approximately 1.224
        assert!(norm_b > 1.0); // Should be approximately 1.233
    }
}
