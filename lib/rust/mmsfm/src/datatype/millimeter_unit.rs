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

//! Millimeter unit data type for physical measurements.

use nalgebra::{Point2, Point3, Vector2, Vector3};
use std::fmt;

use crate::{impl_arithmetic_ops, impl_unit_value};

/// Physical measurements in millimeters.
///
/// This unit type represents real-world distances and measurements
/// in millimeters, commonly used for camera calibration and 3D
/// reconstruction tasks.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
#[repr(transparent)]
pub struct MillimeterUnit<T>(pub T);

// Implement the core traits
impl_unit_value!(MillimeterUnit);
impl_arithmetic_ops!(MillimeterUnit);

/// 2D point type using millimeter coordinates.
pub type MillimeterPoint2<T> = Point2<MillimeterUnit<T>>;

/// 3D point type using millimeter coordinates.
pub type MillimeterPoint3<T> = Point3<MillimeterUnit<T>>;

/// 2D vector type using millimeter coordinates.
pub type MillimeterVector2<T> = Vector2<MillimeterUnit<T>>;

/// 3D vector type using millimeter coordinates.
pub type MillimeterVector3<T> = Vector3<MillimeterUnit<T>>;

/// Convenience functions for creating 2D points and vectors.
impl<T> MillimeterUnit<T>
where
    T: Clone + fmt::Debug + PartialEq + 'static,
{
    /// Create a 2D point in millimeter units.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let point = MillimeterUnit::point2(10.0, 20.0);
    /// assert_eq!(point.x.value(), 10.0);
    /// assert_eq!(point.y.value(), 20.0);
    /// ```
    pub fn point2(x: T, y: T) -> MillimeterPoint2<T> {
        Point2::new(MillimeterUnit(x), MillimeterUnit(y))
    }

    /// Create a 2D vector in millimeter units.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let vector = MillimeterUnit::vector2(5.0, 10.0);
    /// assert_eq!(vector.x.value(), 5.0);
    /// assert_eq!(vector.y.value(), 10.0);
    /// ```
    pub fn vector2(x: T, y: T) -> MillimeterVector2<T> {
        Vector2::new(MillimeterUnit(x), MillimeterUnit(y))
    }

    /// Create a 3D point in millimeter units.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let point = MillimeterUnit::point3(10.0, 20.0, 30.0);
    /// assert_eq!(point.x.value(), 10.0);
    /// assert_eq!(point.y.value(), 20.0);
    /// assert_eq!(point.z.value(), 30.0);
    /// ```
    pub fn point3(x: T, y: T, z: T) -> MillimeterPoint3<T> {
        Point3::new(MillimeterUnit(x), MillimeterUnit(y), MillimeterUnit(z))
    }

    /// Create a 3D vector in millimeter units.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let vector = MillimeterUnit::vector3(5.0, 10.0, 15.0);
    /// assert_eq!(vector.x.value(), 5.0);
    /// assert_eq!(vector.y.value(), 10.0);
    /// assert_eq!(vector.z.value(), 15.0);
    /// ```
    pub fn vector3(x: T, y: T, z: T) -> MillimeterVector3<T> {
        Vector3::new(MillimeterUnit(x), MillimeterUnit(y), MillimeterUnit(z))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::common::UnitValue;

    #[test]
    fn test_millimeter_unit_creation() {
        let mm = MillimeterUnit::new(25.4);
        assert_eq!(mm.value(), 25.4);
    }

    #[test]
    fn test_millimeter_arithmetic_operations() {
        let a = MillimeterUnit::new(10.0);
        let b = MillimeterUnit::new(5.0);

        assert_eq!((a + b).value(), 15.0);
        assert_eq!((a - b).value(), 5.0);
        assert_eq!((a * 2.0).value(), 20.0);
        assert_eq!((a / 2.0).value(), 5.0);
        assert_eq!((-a).value(), -10.0);
    }

    #[test]
    fn test_millimeter_point_creation() {
        let mm_point = MillimeterUnit::point2(10.0, 20.0);
        assert_eq!(mm_point.x.value(), 10.0);
        assert_eq!(mm_point.y.value(), 20.0);
    }

    #[test]
    fn test_millimeter_vector_creation() {
        let mm_vector = MillimeterUnit::vector2(5.0, 10.0);
        assert_eq!(mm_vector.x.value(), 5.0);
        assert_eq!(mm_vector.y.value(), 10.0);
    }

    #[test]
    fn test_millimeter_zero_cost_abstraction() {
        use std::mem;

        // Ensure unit types have the same size as their inner type
        assert_eq!(
            mem::size_of::<MillimeterUnit<f64>>(),
            mem::size_of::<f64>()
        );
        assert_eq!(
            mem::size_of::<MillimeterUnit<f32>>(),
            mem::size_of::<f32>()
        );

        // Test that points with unit types have the same size as regular points
        assert_eq!(
            mem::size_of::<Point2<MillimeterUnit<f64>>>(),
            mem::size_of::<Point2<f64>>()
        );
    }

    #[test]
    fn test_millimeter_display_formatting() {
        let mm = MillimeterUnit::new(25.4);
        assert_eq!(format!("{}", mm), "25.4");
    }
}
