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

//! NDC value data type for Normalized Device Coordinates.

use nalgebra::{Point2, Vector2};
use num_traits::Signed;
use std::fmt;

use crate::{impl_arithmetic_ops, impl_unit_value};

/// NDC (Normalized Device Coordinate) values.
///
/// This unit type represents normalized device coordinates typically in the
/// range [-1.0, 1.0], commonly used in graphics pipelines after perspective
/// projection but before viewport transformation.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
#[repr(transparent)]
pub struct NdcValue<T>(pub T);

// Implement the core traits
impl_unit_value!(NdcValue);
impl_arithmetic_ops!(NdcValue);

// Implement mathematical operations for floating-point calculations
impl<T> NdcValue<T>
where
    T: Signed,
{
    /// Returns the absolute value of the NDC coordinate.
    pub fn abs(self) -> Self {
        NdcValue(self.0.abs())
    }

    /// Returns the signum of the NDC coordinate.
    pub fn signum(self) -> Self {
        NdcValue(self.0.signum())
    }

    /// Returns true if the NDC coordinate is positive.
    pub fn is_positive(&self) -> bool {
        self.0.is_positive()
    }

    /// Returns true if the NDC coordinate is negative.
    pub fn is_negative(&self) -> bool {
        self.0.is_negative()
    }
}

/// 2D point type using NDC values.
pub type NdcPoint2<T> = Point2<NdcValue<T>>;

/// 2D vector type using NDC values.
pub type NdcVector2<T> = Vector2<NdcValue<T>>;

/// Convenience functions for creating 2D points and vectors.
impl<T> NdcValue<T>
where
    T: Clone + fmt::Debug + PartialEq + 'static,
{
    /// Create a 2D point using NDC values.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let point = NdcValue::point2(0.0, 0.0);
    /// assert_eq!(point.x.value(), 0.0);
    /// assert_eq!(point.y.value(), 0.0);
    /// ```
    pub fn point2(x: T, y: T) -> NdcPoint2<T> {
        Point2::new(NdcValue(x), NdcValue(y))
    }

    /// Create a 2D vector using NDC values.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let vector = NdcValue::vector2(-1.0, 1.0);
    /// assert_eq!(vector.x.value(), -1.0);
    /// assert_eq!(vector.y.value(), 1.0);
    /// ```
    pub fn vector2(x: T, y: T) -> NdcVector2<T> {
        Vector2::new(NdcValue(x), NdcValue(y))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::common::UnitValue;
    use approx::assert_relative_eq;

    #[test]
    fn test_ndc_value_creation() {
        let ndc = NdcValue::new(0.0);
        assert_eq!(ndc.value(), 0.0);

        let ndc_min = NdcValue::new(-1.0);
        assert_eq!(ndc_min.value(), -1.0);

        let ndc_max = NdcValue::new(1.0);
        assert_eq!(ndc_max.value(), 1.0);
    }

    #[test]
    fn test_ndc_arithmetic_operations() {
        let a = NdcValue::new(0.5);
        let b = NdcValue::new(-0.3);

        assert_relative_eq!((a + b).value(), 0.2, epsilon = 1e-10);
        assert_relative_eq!((a - b).value(), 0.8, epsilon = 1e-10);
        assert_relative_eq!((a * 2.0).value(), 1.0, epsilon = 1e-10);
        assert_relative_eq!((a / 2.0).value(), 0.25, epsilon = 1e-10);
        assert_relative_eq!((-a).value(), -0.5, epsilon = 1e-10);
    }

    #[test]
    fn test_ndc_point_creation() {
        let ndc_point = NdcValue::point2(0.0, 0.0);
        assert_eq!(ndc_point.x.value(), 0.0);
        assert_eq!(ndc_point.y.value(), 0.0);
    }

    #[test]
    fn test_ndc_vector_creation() {
        let ndc_vector = NdcValue::vector2(-1.0, 1.0);
        assert_eq!(ndc_vector.x.value(), -1.0);
        assert_eq!(ndc_vector.y.value(), 1.0);
    }

    #[test]
    fn test_ndc_mathematical_operations() {
        let ndc = NdcValue::new(-0.5);

        // Test absolute value
        assert_relative_eq!(ndc.abs().value(), 0.5, epsilon = 1e-10);

        // Test signum
        assert_relative_eq!(ndc.signum().value(), -1.0, epsilon = 1e-10);

        // Test is_positive/is_negative
        assert!(!ndc.is_positive());
        assert!(ndc.is_negative());

        let ndc_pos = NdcValue::new(0.5);
        assert!(ndc_pos.is_positive());
        assert!(!ndc_pos.is_negative());
    }

    #[test]
    fn test_ndc_zero_cost_abstraction() {
        use std::mem;

        // Ensure unit types have the same size as their inner type
        assert_eq!(mem::size_of::<NdcValue<f64>>(), mem::size_of::<f64>());
        assert_eq!(mem::size_of::<NdcValue<f32>>(), mem::size_of::<f32>());

        // Test that points with unit types have the same size as regular points
        assert_eq!(
            mem::size_of::<Point2<NdcValue<f64>>>(),
            mem::size_of::<Point2<f64>>()
        );
    }

    #[test]
    fn test_ndc_display_formatting() {
        let ndc = NdcValue::new(0.0);
        assert_eq!(format!("{}", ndc), "0");

        let ndc_neg = NdcValue::new(-1.0);
        assert_eq!(format!("{}", ndc_neg), "-1");
    }

    #[test]
    fn test_ndc_coordinate_range_validation() {
        // Test typical NDC range values using new centralized functions
        use crate::datatype::conversions::*;

        let values = [-1.0, -0.5, 0.0, 0.5, 1.0];
        for &val in &values {
            let ndc_point = NdcValue::point2(val, val);
            let uv_point = convert_ndc_to_uv_point(ndc_point);
            let back_to_ndc = convert_uv_to_ndc_point(uv_point);
            assert_relative_eq!(back_to_ndc.x.value(), val, epsilon = 1e-10);
            assert_relative_eq!(back_to_ndc.y.value(), val, epsilon = 1e-10);
        }
    }

    #[test]
    fn test_round_trip_conversions() {
        // These round trip tests are now handled by the centralized conversion functions
        // and tested comprehensively in conversions.rs
        use crate::datatype::conversions::*;

        // Test NDC -> UV -> NDC round trip using new point-based functions
        let original_ndc = NdcValue::point2(0.25, -0.5);
        let uv_point = convert_ndc_to_uv_point(original_ndc);
        let back_to_ndc = convert_uv_to_ndc_point(uv_point);
        assert_relative_eq!(back_to_ndc.x.value(), 0.25, epsilon = 1e-10);
        assert_relative_eq!(back_to_ndc.y.value(), -0.5, epsilon = 1e-10);
    }
}
