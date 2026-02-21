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

//! Scene unit data type for 3D software coordinate systems.

use nalgebra::{Point2, Point3, Vector2, Vector3};
use std::fmt;

use crate::{impl_arithmetic_ops, impl_unit_value};

/// Scene units in Maya or other 3D software.
///
/// This unit type represents coordinates and measurements in the
/// coordinate system of a 3D scene, which may have arbitrary scale
/// relative to real-world units.
#[derive(Debug, Clone, Copy, PartialEq, PartialOrd)]
#[repr(transparent)]
pub struct SceneUnit<T>(pub T);

// Implement the core traits
impl_unit_value!(SceneUnit);
impl_arithmetic_ops!(SceneUnit);

/// 2D point type using scene coordinates.
pub type ScenePoint2<T> = Point2<SceneUnit<T>>;

/// 3D point type using scene coordinates.
pub type ScenePoint3<T> = Point3<SceneUnit<T>>;

/// 2D vector type using scene coordinates.
pub type SceneVector2<T> = Vector2<SceneUnit<T>>;

/// 3D vector type using scene coordinates.
pub type SceneVector3<T> = Vector3<SceneUnit<T>>;

/// Convenience functions for creating 2D points and vectors.
impl<T> SceneUnit<T>
where
    T: Clone + fmt::Debug + PartialEq + 'static,
{
    /// Create a 2D point in scene units.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let point = SceneUnit::point2(100.0, 200.0);
    /// assert_eq!(point.x.value(), 100.0);
    /// assert_eq!(point.y.value(), 200.0);
    /// ```
    pub fn point2(x: T, y: T) -> ScenePoint2<T> {
        Point2::new(SceneUnit(x), SceneUnit(y))
    }

    /// Create a 2D vector in scene units.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let vector = SceneUnit::vector2(50.0, 75.0);
    /// assert_eq!(vector.x.value(), 50.0);
    /// assert_eq!(vector.y.value(), 75.0);
    /// ```
    pub fn vector2(x: T, y: T) -> SceneVector2<T> {
        Vector2::new(SceneUnit(x), SceneUnit(y))
    }

    /// Create a 3D point in scene units.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let point = SceneUnit::point3(100.0, 200.0, 300.0);
    /// assert_eq!(point.x.value(), 100.0);
    /// assert_eq!(point.y.value(), 200.0);
    /// assert_eq!(point.z.value(), 300.0);
    /// ```
    pub fn point3(x: T, y: T, z: T) -> ScenePoint3<T> {
        Point3::new(SceneUnit(x), SceneUnit(y), SceneUnit(z))
    }

    /// Create a 3D vector in scene units.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let vector = SceneUnit::vector3(50.0, 75.0, 100.0);
    /// assert_eq!(vector.x.value(), 50.0);
    /// assert_eq!(vector.y.value(), 75.0);
    /// assert_eq!(vector.z.value(), 100.0);
    /// ```
    pub fn vector3(x: T, y: T, z: T) -> SceneVector3<T> {
        Vector3::new(SceneUnit(x), SceneUnit(y), SceneUnit(z))
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::common::UnitValue;

    #[test]
    fn test_scene_unit_creation() {
        let scene = SceneUnit::new(100.0);
        assert_eq!(scene.value(), 100.0);
    }

    #[test]
    fn test_scene_arithmetic_operations() {
        let a = SceneUnit::new(100.0);
        let b = SceneUnit::new(50.0);

        assert_eq!((a + b).value(), 150.0);
        assert_eq!((a - b).value(), 50.0);
        assert_eq!((a * 2.0).value(), 200.0);
        assert_eq!((a / 2.0).value(), 50.0);
        assert_eq!((-a).value(), -100.0);
    }

    #[test]
    fn test_scene_point_creation() {
        let scene_point = SceneUnit::point2(100.0, 200.0);
        assert_eq!(scene_point.x.value(), 100.0);
        assert_eq!(scene_point.y.value(), 200.0);
    }

    #[test]
    fn test_scene_vector_creation() {
        let scene_vector = SceneUnit::vector2(50.0, 75.0);
        assert_eq!(scene_vector.x.value(), 50.0);
        assert_eq!(scene_vector.y.value(), 75.0);
    }

    #[test]
    fn test_scene_point3_creation() {
        let scene_point = SceneUnit::point3(100.0, 200.0, 300.0);
        assert_eq!(scene_point.x.value(), 100.0);
        assert_eq!(scene_point.y.value(), 200.0);
        assert_eq!(scene_point.z.value(), 300.0);
    }

    #[test]
    fn test_scene_vector3_creation() {
        let scene_vector = SceneUnit::vector3(50.0, 75.0, 100.0);
        assert_eq!(scene_vector.x.value(), 50.0);
        assert_eq!(scene_vector.y.value(), 75.0);
        assert_eq!(scene_vector.z.value(), 100.0);
    }

    #[test]
    fn test_scene_zero_cost_abstraction() {
        use std::mem;

        // Ensure unit types have the same size as their inner type
        assert_eq!(mem::size_of::<SceneUnit<f64>>(), mem::size_of::<f64>());
        assert_eq!(mem::size_of::<SceneUnit<f32>>(), mem::size_of::<f32>());

        // Test that points with unit types have the same size as regular points
        assert_eq!(
            mem::size_of::<Point2<SceneUnit<f64>>>(),
            mem::size_of::<Point2<f64>>()
        );
        assert_eq!(
            mem::size_of::<Point3<SceneUnit<f64>>>(),
            mem::size_of::<Point3<f64>>()
        );
    }

    #[test]
    fn test_scene_display_formatting() {
        let scene = SceneUnit::new(100.0);
        assert_eq!(format!("{}", scene), "100");
    }
}
