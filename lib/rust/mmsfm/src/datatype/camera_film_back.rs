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

//! Camera film back data type for physical sensor dimensions.

use std::fmt;

use crate::datatype::common::UnitValue;
use crate::datatype::millimeter_unit::MillimeterUnit;

/// Camera film back representing physical sensor dimensions.
///
/// This struct represents the physical dimensions of a camera's film back
/// or digital sensor in millimeters. It's used for camera calibration and
/// 3D reconstruction tasks where the physical sensor size is important
/// for accurate scale and perspective calculations.
///
/// # Examples
///
/// ```rust
/// use mmsfm_rust::datatype::*;
///
/// // Create a full-frame 35mm sensor (36mm x 24mm)
/// let full_frame = CameraFilmBack::new(
///     MillimeterUnit::new(36.0),
///     MillimeterUnit::new(24.0)
/// );
///
/// assert_eq!(full_frame.aspect_ratio(), 1.5);
///
/// // Create an APS-C sensor (approximately 23.6mm x 15.7mm)
/// let aps_c = CameraFilmBack::new(
///     MillimeterUnit::new(23.6),
///     MillimeterUnit::new(15.7)
/// );
///
/// assert!((aps_c.aspect_ratio() - 1.503_f64).abs() < 0.01);
/// ```
#[derive(Debug, Copy, Clone, PartialEq)]
pub struct CameraFilmBack<T> {
    /// Width of the film back/sensor in millimeters.
    // TODO: Change the field name to `width_mm`.
    pub width: MillimeterUnit<T>,
    /// Height of the film back/sensor in millimeters.
    // TODO: Change the field name to `height_mm`.
    pub height: MillimeterUnit<T>,
}

impl<T> CameraFilmBack<T>
where
    T: Copy + fmt::Debug + PartialEq,
{
    /// Create a new camera film back with specified dimensions.
    ///
    /// # Arguments
    /// * `width` - Width of the sensor in millimeters.
    /// * `height` - Height of the sensor in millimeters.
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let film_back = CameraFilmBack::new(
    ///     MillimeterUnit::new(36.0),
    ///     MillimeterUnit::new(24.0)
    /// );
    /// assert_eq!(film_back.width.value(), 36.0);
    /// assert_eq!(film_back.height.value(), 24.0);
    /// ```
    pub fn new(width: MillimeterUnit<T>, height: MillimeterUnit<T>) -> Self {
        Self { width, height }
    }

    /// Create a new camera film back from raw millimeter values.
    ///
    /// # Arguments
    /// * `width_mm` - Width of the sensor in millimeters
    /// * `height_mm` - Height of the sensor in millimeters
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
    /// assert_eq!(film_back.width.value(), 36.0);
    /// assert_eq!(film_back.height.value(), 24.0);
    /// ```
    pub fn from_millimeters(width_mm: T, height_mm: T) -> Self {
        Self {
            width: MillimeterUnit::new(width_mm),
            height: MillimeterUnit::new(height_mm),
        }
    }
}

impl<T> CameraFilmBack<T>
where
    T: Copy + std::ops::Div<Output = T> + fmt::Debug + PartialEq,
{
    /// Calculate the aspect ratio of the film back (width / height).
    ///
    /// # Returns
    /// Aspect ratio as width divided by height
    ///
    /// # Examples
    /// ```rust
    /// use mmsfm_rust::datatype::*;
    ///
    /// // Full frame 35mm: 36mm x 24mm = 1.5 aspect ratio
    /// let full_frame = CameraFilmBack::from_millimeters(36.0, 24.0);
    /// assert_eq!(full_frame.aspect_ratio(), 1.5);
    ///
    /// // Square sensor: 20mm x 20mm = 1.0 aspect ratio
    /// let square = CameraFilmBack::from_millimeters(20.0, 20.0);
    /// assert_eq!(square.aspect_ratio(), 1.0);
    /// ```
    pub fn aspect_ratio(&self) -> T {
        self.width.value() / self.height.value()
    }
}

impl<T> fmt::Display for CameraFilmBack<T>
where
    T: fmt::Display + Copy + fmt::Debug + PartialEq,
{
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(f, "{}mm x {}mm", self.width, self.height)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;

    #[test]
    fn test_camera_film_back_creation() {
        let film_back = CameraFilmBack::new(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(24.0),
        );
        assert_eq!(film_back.width.value(), 36.0);
        assert_eq!(film_back.height.value(), 24.0);
    }

    #[test]
    fn test_camera_film_back_from_millimeters() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        assert_eq!(film_back.width.value(), 36.0);
        assert_eq!(film_back.height.value(), 24.0);
    }

    #[test]
    fn test_camera_film_back_aspect_ratio() {
        // Full frame 35mm
        let full_frame = CameraFilmBack::from_millimeters(36.0, 24.0);
        assert_relative_eq!(full_frame.aspect_ratio(), 1.5, epsilon = 1e-10);

        // Square sensor
        let square = CameraFilmBack::from_millimeters(20.0, 20.0);
        assert_relative_eq!(square.aspect_ratio(), 1.0, epsilon = 1e-10);
    }

    #[test]
    fn test_camera_film_back_equality() {
        let film_back_a = CameraFilmBack::from_millimeters(36.0, 24.0);
        let film_back_b = CameraFilmBack::from_millimeters(36.0, 24.0);
        let film_back_c = CameraFilmBack::from_millimeters(22.3, 14.9);

        assert_eq!(film_back_a, film_back_b);
        assert_ne!(film_back_a, film_back_c);
    }

    #[test]
    fn test_camera_film_back_display() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        assert_eq!(format!("{}", film_back), "36mm x 24mm");
    }

    #[test]
    fn test_camera_film_back_debug() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let debug_str = format!("{:?}", film_back);
        assert!(debug_str.contains("36"));
        assert!(debug_str.contains("24"));
    }

    #[test]
    fn test_camera_film_back_with_different_numeric_types() {
        // Test with f32
        let film_back_f32 =
            CameraFilmBack::from_millimeters(36.0_f32, 24.0_f32);
        assert_relative_eq!(
            film_back_f32.aspect_ratio(),
            1.5_f32,
            epsilon = 1e-6
        );

        // Test with f64
        let film_back_f64 =
            CameraFilmBack::from_millimeters(36.0_f64, 24.0_f64);
        assert_relative_eq!(
            film_back_f64.aspect_ratio(),
            1.5_f64,
            epsilon = 1e-10
        );
    }
}
