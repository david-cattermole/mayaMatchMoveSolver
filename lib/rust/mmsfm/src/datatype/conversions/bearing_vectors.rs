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

//! Bearing vector conversions for structure from motion algorithms.
//!
//! This module provides conversions between camera coordinates and bearing/homogeneous vectors,
//! which are used by essential matrix algorithms.

use nalgebra::{Vector2, Vector3};

use crate::datatype::camera_coord_value::{
    CameraCoordValue, CameraCoordVector2,
};
use crate::datatype::common::UnitValue;

// ============================================================================
// Bearing Vector Conversions
// ============================================================================

/// Convert camera coordinate vector to normalized bearing vector.
///
/// Creates a normalized unit vector from camera coordinates by appending z=1.0
/// and normalizing. This is used by five-point and six-point essential matrix algorithms.
///
/// # Arguments
/// * `camera_coord_vector` - Camera coordinate vector (x, y)
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::{*, conversions::*};
///
/// let camera_coord = CameraCoordValue::vector2(-0.5_f64, 0.3_f64);
/// let bearing = convert_camera_coord_to_bearing_vector(camera_coord);
/// // Bearing vector is normalized: sqrt((-0.5)^2 + 0.3^2 + 1.0^2) = sqrt(1.34) ~= 1.158
/// assert!((bearing.norm() - 1.0_f64).abs() < 1e-10_f64);
/// ```
pub fn convert_camera_coord_to_bearing_vector<T>(
    camera_coord_vector: CameraCoordVector2<T>,
) -> Vector3<T>
where
    T: Copy
        + From<f64>
        + std::ops::Add<Output = T>
        + std::ops::Mul<Output = T>
        + num_traits::Float
        + std::fmt::Debug
        + nalgebra::ComplexField,
{
    let unnormalized = Vector3::new(
        camera_coord_vector[0].value(),
        camera_coord_vector[1].value(),
        <T as From<f64>>::from(1.0),
    );
    unnormalized.normalize()
}

/// Convert camera coordinate vector to homogeneous coordinates.
///
/// Creates homogeneous coordinates (z=1) from camera coordinates.
/// This is used by eight-point and eight-plus-point essential matrix algorithms.
///
/// # Arguments
/// * `camera_coord_vector` - Camera coordinate vector (x, y)
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::{*, conversions::*};
///
/// let camera_coord = CameraCoordValue::vector2(-0.5, 0.3);
/// let homogeneous = convert_camera_coord_to_homogeneous_vector(camera_coord);
/// assert_eq!(homogeneous.x, -0.5);
/// assert_eq!(homogeneous.y, 0.3);
/// assert_eq!(homogeneous.z, 1.0);
/// ```
pub fn convert_camera_coord_to_homogeneous_vector<T>(
    camera_coord_vector: CameraCoordVector2<T>,
) -> Vector3<T>
where
    T: Copy + From<f64>,
{
    Vector3::new(
        camera_coord_vector[0].value(),
        camera_coord_vector[1].value(),
        <T as From<f64>>::from(1.0),
    )
}

/// Convert normalized bearing vector to camera coordinate vector.
///
/// Extracts the x,y components from a normalized bearing vector by dividing by z.
/// This reverses the bearing vector creation process.
///
/// # Arguments
/// * `bearing_vector` - Normalized bearing vector (x, y, z)
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::{*, conversions::*};
/// use nalgebra::Vector3;
///
/// // Create a normalized bearing vector
/// let unnormalized = Vector3::new(-0.5_f64, 0.3_f64, 1.0_f64);
/// let bearing = unnormalized.normalize();
/// let camera_coord = convert_bearing_vector_to_camera_coord(bearing);
///
/// // Should recover original coordinates (within tolerance due to normalization)
/// assert!((camera_coord.x.value() + 0.5_f64).abs() < 1e-10_f64);
/// assert!((camera_coord.y.value() - 0.3_f64).abs() < 1e-10_f64);
/// ```
pub fn convert_bearing_vector_to_camera_coord<T>(
    bearing_vector: Vector3<T>,
) -> CameraCoordVector2<T>
where
    T: Copy + std::ops::Div<Output = T> + std::fmt::Debug + PartialEq + 'static,
{
    Vector2::new(
        CameraCoordValue(bearing_vector.x / bearing_vector.z),
        CameraCoordValue(bearing_vector.y / bearing_vector.z),
    )
}

/// Convert homogeneous coordinate vector to camera coordinate vector.
///
/// Extracts the x,y components from a homogeneous vector (which should have z=1).
///
/// # Arguments
/// * `homogeneous_vector` - Homogeneous coordinate vector (x, y, 1)
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::{*, conversions::*};
/// use nalgebra::Vector3;
///
/// let homogeneous = Vector3::new(-0.5, 0.3, 1.0);
/// let camera_coord = convert_homogeneous_vector_to_camera_coord(homogeneous);
/// assert_eq!(camera_coord.x.value(), -0.5);
/// assert_eq!(camera_coord.y.value(), 0.3);
/// ```
pub fn convert_homogeneous_vector_to_camera_coord<T>(
    homogeneous_vector: Vector3<T>,
) -> CameraCoordVector2<T>
where
    T: Copy + std::ops::Div<Output = T> + std::fmt::Debug + PartialEq + 'static,
{
    Vector2::new(
        CameraCoordValue(homogeneous_vector.x / homogeneous_vector.z),
        CameraCoordValue(homogeneous_vector.y / homogeneous_vector.z),
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::common::UnitValue;
    use approx::assert_relative_eq;

    #[test]
    fn test_camera_coord_to_bearing_vector() {
        let camera_coord = CameraCoordValue::vector2(-0.5, 0.3);
        let bearing = convert_camera_coord_to_bearing_vector(camera_coord);

        // Verify that the vector is normalized
        assert_relative_eq!(bearing.norm(), 1.0, epsilon = 1e-10);

        // Calculate expected normalized values: (-0.5, 0.3, 1.0)
        let length = (0.5_f64 * 0.5 + 0.3 * 0.3 + 1.0 * 1.0).sqrt();
        let expected_x = -0.5 / length;
        let expected_y = 0.3 / length;
        let expected_z = 1.0 / length;

        assert_relative_eq!(bearing.x, expected_x, epsilon = 1e-10);
        assert_relative_eq!(bearing.y, expected_y, epsilon = 1e-10);
        assert_relative_eq!(bearing.z, expected_z, epsilon = 1e-10);
    }

    #[test]
    fn test_camera_coord_to_homogeneous_vector() {
        let camera_coord = CameraCoordValue::vector2(-0.5, 0.3);
        let homogeneous =
            convert_camera_coord_to_homogeneous_vector(camera_coord);

        assert_eq!(homogeneous.x, -0.5);
        assert_eq!(homogeneous.y, 0.3);
        assert_eq!(homogeneous.z, 1.0);

        // Verify this is NOT a unit vector
        let norm = homogeneous.norm();
        assert!(norm > 1.0);
    }

    #[test]
    fn test_bearing_vector_to_camera_coord_round_trip() {
        let original_camera_coord = CameraCoordValue::vector2(-0.5, 0.3);

        let bearing =
            convert_camera_coord_to_bearing_vector(original_camera_coord);
        let back_to_camera_coord =
            convert_bearing_vector_to_camera_coord(bearing);

        assert_relative_eq!(
            back_to_camera_coord.x.value(),
            -0.5,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            back_to_camera_coord.y.value(),
            0.3,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_homogeneous_vector_to_camera_coord_round_trip() {
        let original_camera_coord = CameraCoordValue::vector2(-0.5, 0.3);

        let homogeneous =
            convert_camera_coord_to_homogeneous_vector(original_camera_coord);
        let back_to_camera_coord =
            convert_homogeneous_vector_to_camera_coord(homogeneous);

        assert_eq!(back_to_camera_coord.x.value(), -0.5);
        assert_eq!(back_to_camera_coord.y.value(), 0.3);
    }

    #[test]
    fn test_camera_coord_bearing_vector_consistency() {
        let test_coords = vec![
            CameraCoordValue::vector2(0.0, 0.0),
            CameraCoordValue::vector2(1.0, 0.0),
            CameraCoordValue::vector2(0.0, 1.0),
            CameraCoordValue::vector2(-1.0, -1.0),
            CameraCoordValue::vector2(0.5, -0.7),
        ];

        for coord in test_coords {
            let bearing = convert_camera_coord_to_bearing_vector(coord);
            assert_relative_eq!(bearing.norm(), 1.0, epsilon = 1e-10);
            let recovered_coord =
                convert_bearing_vector_to_camera_coord(bearing);
            assert_relative_eq!(
                recovered_coord.x.value(),
                coord.x.value(),
                epsilon = 1e-10
            );
            assert_relative_eq!(
                recovered_coord.y.value(),
                coord.y.value(),
                epsilon = 1e-10
            );

            let homogeneous = convert_camera_coord_to_homogeneous_vector(coord);
            assert_eq!(homogeneous.z, 1.0);
            let recovered_coord_h =
                convert_homogeneous_vector_to_camera_coord(homogeneous);
            assert_eq!(recovered_coord_h.x.value(), coord.x.value());
            assert_eq!(recovered_coord_h.y.value(), coord.y.value());
        }
    }
}
