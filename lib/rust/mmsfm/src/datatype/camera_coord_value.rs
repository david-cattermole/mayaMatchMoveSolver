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

//! Camera coordinate value data type for normalized camera coordinates.

use std::fmt;

use nalgebra::{Point2, Vector2};

use crate::{impl_arithmetic_ops, impl_unit_value};

/// Camera coordinate values.
///
/// This unit type represents normalized camera coordinates after applying
/// camera intrinsics transformation. These are computed as:
/// `(ndc_coord - principal_point) / focal_length`
///
/// Camera coordinates are used in computer vision algorithms such as
/// essential matrix estimation and 3D reconstruction.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
#[repr(transparent)]
pub struct CameraCoordValue<T>(pub T);

// Implement the core traits
impl_unit_value!(CameraCoordValue);
impl_arithmetic_ops!(CameraCoordValue);

/// 2D point type using camera coordinate values.
pub type CameraCoordPoint2<T> = Point2<CameraCoordValue<T>>;

/// 2D vector type using camera coordinate values.
pub type CameraCoordVector2<T> = Vector2<CameraCoordValue<T>>;

/// Convenience functions for creating 2D points and vectors.
impl<T> CameraCoordValue<T>
where
    T: Clone + fmt::Debug + PartialEq + 'static,
{
    /// Create a 2D point using camera coordinate values.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let point = CameraCoordValue::point2(-0.5, 0.3);
    /// assert_eq!(point.x.value(), -0.5);
    /// assert_eq!(point.y.value(), 0.3);
    /// ```
    pub fn point2(x: T, y: T) -> CameraCoordPoint2<T> {
        Point2::new(CameraCoordValue(x), CameraCoordValue(y))
    }

    /// Create a 2D vector using camera coordinate values.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let vector = CameraCoordValue::vector2(-0.2, 0.4);
    /// assert_eq!(vector.x.value(), -0.2);
    /// assert_eq!(vector.y.value(), 0.4);
    /// ```
    pub fn vector2(x: T, y: T) -> CameraCoordVector2<T> {
        Vector2::new(CameraCoordValue(x), CameraCoordValue(y))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::common::UnitValue;
    use approx::assert_relative_eq;
    use approx::{AbsDiffEq, RelativeEq};

    impl<T> AbsDiffEq for CameraCoordValue<T>
    where
        T: AbsDiffEq,
        T::Epsilon: Clone,
    {
        type Epsilon = T::Epsilon;

        fn default_epsilon() -> T::Epsilon {
            T::default_epsilon()
        }

        fn abs_diff_eq(&self, other: &Self, epsilon: T::Epsilon) -> bool {
            T::abs_diff_eq(&self.0, &other.0, epsilon)
        }
    }

    impl<T> RelativeEq for CameraCoordValue<T>
    where
        T: RelativeEq,
        T::Epsilon: Clone,
    {
        fn default_max_relative() -> T::Epsilon {
            T::default_max_relative()
        }

        fn relative_eq(
            &self,
            other: &Self,
            epsilon: T::Epsilon,
            max_relative: T::Epsilon,
        ) -> bool {
            T::relative_eq(&self.0, &other.0, epsilon, max_relative)
        }
    }

    #[test]
    fn test_camera_coord_value_creation() {
        let coord = CameraCoordValue::new(-0.5);
        assert_eq!(coord.value(), -0.5);
    }

    #[test]
    fn test_camera_coord_arithmetic_operations() {
        let a = CameraCoordValue::new(-0.3);
        let b = CameraCoordValue::new(0.2);

        assert_relative_eq!((a + b).value(), -0.1, epsilon = 1e-10);
        assert_relative_eq!((a - b).value(), -0.5, epsilon = 1e-10);
        assert_relative_eq!((a * 2.0).value(), -0.6, epsilon = 1e-10);
        assert_relative_eq!((a / 2.0).value(), -0.15, epsilon = 1e-10);
        assert_relative_eq!((-a).value(), 0.3, epsilon = 1e-10);
    }

    #[test]
    fn test_camera_coord_point_creation() {
        let point = CameraCoordValue::point2(-0.5, 0.3);
        assert_eq!(point.x.value(), -0.5);
        assert_eq!(point.y.value(), 0.3);
    }

    #[test]
    fn test_camera_coord_vector_creation() {
        let vector = CameraCoordValue::vector2(-0.2, 0.4);
        assert_eq!(vector.x.value(), -0.2);
        assert_eq!(vector.y.value(), 0.4);
    }

    #[test]
    fn test_camera_coord_zero_cost_abstraction() {
        use std::mem;

        // Ensure unit types have the same size as their inner type
        assert_eq!(
            mem::size_of::<CameraCoordValue<f64>>(),
            mem::size_of::<f64>()
        );
        assert_eq!(
            mem::size_of::<CameraCoordValue<f32>>(),
            mem::size_of::<f32>()
        );

        // Test that points with unit types have the same size as regular points
        assert_eq!(
            mem::size_of::<Point2<CameraCoordValue<f64>>>(),
            mem::size_of::<Point2<f64>>()
        );
    }

    #[test]
    fn test_camera_coord_display_formatting() {
        let coord = CameraCoordValue::new(-0.3);
        assert_eq!(format!("{}", coord), "-0.3");
    }
}
