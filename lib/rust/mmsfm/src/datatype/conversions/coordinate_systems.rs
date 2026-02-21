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

//! Coordinate system conversions between Maya and Computer Vision conventions.
//!
//! This module handles transformations between:
//! - **Maya Convention:** Right-hand, +Y up, camera looks along -Z
//! - **Computer Vision Convention:** Right-hand, +Y down (typically), camera looks along +Z

use nalgebra::{Matrix3, Point3, Vector3};

// ============================================================================
// Maya <--> Computer Vision Coordinate System Conversions.
// ============================================================================

/// Convert 3D point from Maya coordinate system to Computer Vision coordinate system.
///
/// # Coordinate System Conventions
///
/// **Maya Convention:**
/// - Right-hand coordinate system
/// - +Y is world-up
/// - Camera looks along -Z axis
/// - Points in front of camera have negative Z coordinates
///
/// **Computer Vision Convention:**
/// - Right-hand coordinate system
/// - +Y typically points down in image
/// - Camera looks along +Z axis
/// - Points in front of camera have positive Z coordinates
///
/// # Transformation
///
/// The conversion flips the Z axis:
/// - `(x, y, z_maya)` -> `(x, y, -z_maya)`
///
/// # Arguments
/// * `maya_point` - 3D point in Maya coordinates
///
/// # Returns
/// 3D point in Computer Vision coordinates
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::conversions::*;
/// use nalgebra::Point3;
///
/// let maya_point = Point3::new(1.0, 2.0, -5.0); // Point 5 units in front of camera
/// let cv_point = convert_maya_to_cv_point3(maya_point);
/// assert_eq!(cv_point[0], 1.0);
/// assert_eq!(cv_point[1], 2.0);
/// assert_eq!(cv_point[2], 5.0); // Now positive (in front in CV convention)
/// ```
pub fn convert_maya_to_cv_point3<T>(maya_point: Point3<T>) -> Point3<T>
where
    T: Copy + std::ops::Neg<Output = T> + nalgebra::Scalar,
{
    Point3::new(maya_point[0], maya_point[1], -maya_point[2])
}

/// Convert 3D point from Computer Vision coordinate system to Maya coordinate system.
///
/// This is the inverse of `convert_maya_to_cv_point3`.
///
/// # Arguments
/// * `cv_point` - 3D point in Computer Vision coordinates
///
/// # Returns
/// 3D point in Maya coordinates
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::conversions::*;
/// use nalgebra::Point3;
///
/// let cv_point = Point3::new(1.0, 2.0, 5.0); // Point 5 units in front of camera
/// let maya_point = convert_cv_to_maya_point3(cv_point);
/// assert_eq!(maya_point[0], 1.0);
/// assert_eq!(maya_point[1], 2.0);
/// assert_eq!(maya_point[2], -5.0); // Now negative (in front in Maya convention)
/// ```
pub fn convert_cv_to_maya_point3<T>(cv_point: Point3<T>) -> Point3<T>
where
    T: Copy + std::ops::Neg<Output = T> + nalgebra::Scalar,
{
    Point3::new(cv_point[0], cv_point[1], -cv_point[2])
}

/// Convert rotation matrix from Computer Vision to Maya coordinate system.
///
/// # Transformation
///
/// Given coordinate transform matrix S = diag(1, 1, -1):
/// - `R_maya = S x R_cv x S`
///
/// This negates:
/// - Third column elements: r13, r23
/// - Third row elements: r31, r32
/// - Element r33 remains unchanged
///
/// # Arguments
/// * `cv_rotation` - 3x3 rotation matrix in Computer Vision coordinates
///
/// # Returns
/// 3x3 rotation matrix in Maya coordinates
///
/// # Examples
/// ```rust
/// # use mmsfm_rust::datatype::conversions::*;
/// # use nalgebra::Matrix3;
///
/// let cv_rotation = Matrix3::<f64>::identity();
/// let maya_rotation = convert_cv_to_maya_rotation(cv_rotation);
/// assert_eq!(maya_rotation, Matrix3::<f64>::identity());
/// ```
pub fn convert_cv_to_maya_rotation<T>(cv_rotation: Matrix3<T>) -> Matrix3<T>
where
    T: Copy + std::ops::Neg<Output = T> + nalgebra::Scalar,
{
    // Apply S x R x S where S = diag(1, 1, -1)
    // This negates the third row and third column (except r33 which gets negated twice)
    Matrix3::new(
        cv_rotation[(0, 0)],
        cv_rotation[(0, 1)],
        -cv_rotation[(0, 2)], // Negate third column
        cv_rotation[(1, 0)],
        cv_rotation[(1, 1)],
        -cv_rotation[(1, 2)], // Negate third column
        -cv_rotation[(2, 0)], // Negate third row
        -cv_rotation[(2, 1)], // Negate third row
        cv_rotation[(2, 2)],  // r33 unchanged (negated twice)
    )
}

/// Convert translation vector from Computer Vision to Maya coordinate system.
///
/// # Transformation
///
/// The conversion flips the Z component:
/// - `t_maya = S x t_cv` where S = diag(1, 1, -1)
/// - `(tx, ty, tz_cv)` -> `(tx, ty, -tz_cv)`
///
/// # Arguments
/// * `cv_translation` - Translation vector in Computer Vision coordinates
///
/// # Returns
/// Translation vector in Maya coordinates
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::conversions::*;
/// use nalgebra::Vector3;
///
/// let cv_translation = Vector3::new(1.0, 2.0, 5.0);
/// let maya_translation = convert_cv_to_maya_translation(cv_translation);
/// assert_eq!(maya_translation[0], 1.0);
/// assert_eq!(maya_translation[1], 2.0);
/// assert_eq!(maya_translation[2], -5.0);
/// ```
pub fn convert_cv_to_maya_translation<T>(
    cv_translation: Vector3<T>,
) -> Vector3<T>
where
    T: Copy + std::ops::Neg<Output = T> + nalgebra::Scalar,
{
    Vector3::new(cv_translation[0], cv_translation[1], -cv_translation[2])
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_maya_to_cv_point_conversion() {
        let maya_point = Point3::new(1.0, 2.0, -5.0);
        let cv_point = convert_maya_to_cv_point3(maya_point);
        assert_eq!(cv_point[0], 1.0);
        assert_eq!(cv_point[1], 2.0);
        assert_eq!(cv_point[2], 5.0);
    }

    #[test]
    fn test_cv_to_maya_point_conversion() {
        let cv_point = Point3::new(1.0, 2.0, 5.0);
        let maya_point = convert_cv_to_maya_point3(cv_point);
        assert_eq!(maya_point[0], 1.0);
        assert_eq!(maya_point[1], 2.0);
        assert_eq!(maya_point[2], -5.0);
    }

    #[test]
    fn test_point_conversion_round_trip() {
        let original = Point3::new(3.0, 4.0, -10.0);
        let cv = convert_maya_to_cv_point3(original);
        let back = convert_cv_to_maya_point3(cv);
        assert_eq!(back, original);
    }

    #[test]
    fn test_cv_to_maya_rotation_identity() {
        let cv_rotation = Matrix3::<f64>::identity();
        let maya_rotation = convert_cv_to_maya_rotation(cv_rotation);
        assert_eq!(maya_rotation, Matrix3::<f64>::identity());
    }

    #[test]
    fn test_cv_to_maya_translation() {
        let cv_translation = Vector3::new(1.0, 2.0, 5.0);
        let maya_translation = convert_cv_to_maya_translation(cv_translation);
        assert_eq!(maya_translation[0], 1.0);
        assert_eq!(maya_translation[1], 2.0);
        assert_eq!(maya_translation[2], -5.0);
    }
}
