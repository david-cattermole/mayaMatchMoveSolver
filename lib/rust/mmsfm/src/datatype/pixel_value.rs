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

//! Pixel value data type for pixel-based measurements.

use nalgebra::{Point2, Vector2};
use std::fmt;

use crate::{impl_arithmetic_ops, impl_unit_value};

/// Pixel values.
///
/// This unit type represents pixel values in image space, typically
/// measured in pixels from the top-left corner of an image.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
#[repr(transparent)]
pub struct PixelValue<T>(pub T);

// Implement the core traits
impl_unit_value!(PixelValue);
impl_arithmetic_ops!(PixelValue);

/// 2D point type using pixel values.
pub type PixelPoint2<T> = Point2<PixelValue<T>>;

/// 2D vector type using pixel values.
pub type PixelVector2<T> = Vector2<PixelValue<T>>;

/// Convenience functions for creating 2D points and vectors.
impl<T> PixelValue<T>
where
    T: Clone + fmt::Debug + PartialEq + 'static,
{
    /// Create a 2D point in image coordinates.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let point = PixelValue::point2(1920.0, 1080.0);
    /// assert_eq!(point.x.value(), 1920.0);
    /// assert_eq!(point.y.value(), 1080.0);
    /// ```
    pub fn point2(x: T, y: T) -> PixelPoint2<T> {
        Point2::new(PixelValue(x), PixelValue(y))
    }

    /// Create a 2D vector in image coordinates.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let vector = PixelValue::vector2(100.0, 200.0);
    /// assert_eq!(vector.x.value(), 100.0);
    /// assert_eq!(vector.y.value(), 200.0);
    /// ```
    pub fn vector2(x: T, y: T) -> PixelVector2<T> {
        Vector2::new(PixelValue(x), PixelValue(y))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::common::UnitValue;

    #[test]
    fn test_pixel_value_creation() {
        let img = PixelValue::new(1920.0);
        assert_eq!(img.value(), 1920.0);
    }

    #[test]
    fn test_pixel_arithmetic_operations() {
        let a = PixelValue::new(100.0);
        let b = PixelValue::new(50.0);

        assert_eq!((a + b).value(), 150.0);
        assert_eq!((a - b).value(), 50.0);
        assert_eq!((a * 2.0).value(), 200.0);
        assert_eq!((a / 2.0).value(), 50.0);
        assert_eq!((-a).value(), -100.0);
    }

    #[test]
    fn test_pixel_point_creation() {
        let img_point = PixelValue::point2(1920.0, 1080.0);
        assert_eq!(img_point.x.value(), 1920.0);
        assert_eq!(img_point.y.value(), 1080.0);
    }

    #[test]
    fn test_pixel_vector_creation() {
        let img_vector = PixelValue::vector2(100.0, 200.0);
        assert_eq!(img_vector.x.value(), 100.0);
        assert_eq!(img_vector.y.value(), 200.0);
    }

    #[test]
    fn test_pixel_zero_cost_abstraction() {
        use std::mem;

        // Ensure unit types have the same size as their inner type
        assert_eq!(mem::size_of::<PixelValue<f64>>(), mem::size_of::<f64>());
        assert_eq!(mem::size_of::<PixelValue<f32>>(), mem::size_of::<f32>());

        // Test that points with unit types have the same size as regular points
        assert_eq!(
            mem::size_of::<Point2<PixelValue<f64>>>(),
            mem::size_of::<Point2<f64>>()
        );
    }

    #[test]
    fn test_pixel_display_formatting() {
        let img = PixelValue::new(1920.0);
        assert_eq!(format!("{}", img), "1920");
    }
}
