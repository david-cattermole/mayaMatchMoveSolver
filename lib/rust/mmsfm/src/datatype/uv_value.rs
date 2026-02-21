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

//! UV value data type for normalized texture coordinates.

use nalgebra::{Point2, Vector2};
use num_traits::Signed;
use std::fmt;

use crate::{impl_arithmetic_ops, impl_unit_value};

/// UV values.
///
/// This unit type represents normalized UV values typically in the
/// range [0.0, 1.0], commonly used for texture mapping and normalized
/// device coordinates.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
#[repr(transparent)]
pub struct UvValue<T>(pub T);

// Implement the core traits
impl_unit_value!(UvValue);
impl_arithmetic_ops!(UvValue);

// Implement mathematical operations for floating-point calculations
impl<T> UvValue<T>
where
    T: Signed,
{
    /// Returns the absolute value of the UV coordinate.
    pub fn abs(self) -> Self {
        UvValue(self.0.abs())
    }

    /// Returns the signum of the UV coordinate.
    pub fn signum(self) -> Self {
        UvValue(self.0.signum())
    }

    /// Returns true if the UV coordinate is positive.
    pub fn is_positive(&self) -> bool {
        self.0.is_positive()
    }

    /// Returns true if the UV coordinate is negative.
    pub fn is_negative(&self) -> bool {
        self.0.is_negative()
    }
}

/// 2D point type using UV values.
pub type UvPoint2<T> = Point2<UvValue<T>>;

/// 2D vector type using UV values.
pub type UvVector2<T> = Vector2<UvValue<T>>;

/// Convenience functions for creating 2D points and vectors.
impl<T> UvValue<T>
where
    T: Clone + fmt::Debug + PartialEq + 'static,
{
    /// Create a 2D point using UV values.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let point = UvValue::point2(0.5, 0.5);
    /// assert_eq!(point.x.value(), 0.5);
    /// assert_eq!(point.y.value(), 0.5);
    /// ```
    pub fn point2(x: T, y: T) -> UvPoint2<T> {
        Point2::new(UvValue(x), UvValue(y))
    }

    /// Create a 2D vector using UV values.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let vector = UvValue::vector2(0.1, 0.2);
    /// assert_eq!(vector.x.value(), 0.1);
    /// assert_eq!(vector.y.value(), 0.2);
    /// ```
    pub fn vector2(x: T, y: T) -> UvVector2<T> {
        Vector2::new(UvValue(x), UvValue(y))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::common::UnitValue;
    use approx::assert_relative_eq;

    #[test]
    fn test_uv_value_creation() {
        let uv = UvValue::new(0.5);
        assert_eq!(uv.value(), 0.5);
    }

    #[test]
    fn test_uv_arithmetic_operations() {
        let a = UvValue::new(0.8);
        let b = UvValue::new(0.3);

        assert_relative_eq!((a + b).value(), 1.1, epsilon = 1e-10);
        assert_relative_eq!((a - b).value(), 0.5, epsilon = 1e-10);
        assert_relative_eq!((a * 2.0).value(), 1.6, epsilon = 1e-10);
        assert_relative_eq!((a / 2.0).value(), 0.4, epsilon = 1e-10);
        assert_relative_eq!((-a).value(), -0.8, epsilon = 1e-10);
    }

    #[test]
    fn test_uv_point_creation() {
        let uv_point = UvValue::point2(0.5, 0.5);
        assert_eq!(uv_point.x.value(), 0.5);
        assert_eq!(uv_point.y.value(), 0.5);
    }

    #[test]
    fn test_uv_vector_creation() {
        let uv_vector = UvValue::vector2(0.1, 0.2);
        assert_eq!(uv_vector.x.value(), 0.1);
        assert_eq!(uv_vector.y.value(), 0.2);
    }

    #[test]
    fn test_uv_zero_cost_abstraction() {
        use std::mem;

        // Ensure unit types have the same size as their inner type
        assert_eq!(mem::size_of::<UvValue<f64>>(), mem::size_of::<f64>());
        assert_eq!(mem::size_of::<UvValue<f32>>(), mem::size_of::<f32>());

        // Test that points with unit types have the same size as regular points
        assert_eq!(
            mem::size_of::<Point2<UvValue<f64>>>(),
            mem::size_of::<Point2<f64>>()
        );
    }

    #[test]
    fn test_uv_display_formatting() {
        let uv = UvValue::new(0.5);
        assert_eq!(format!("{}", uv), "0.5");
    }
}
