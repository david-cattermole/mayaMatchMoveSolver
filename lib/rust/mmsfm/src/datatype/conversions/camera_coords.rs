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

//! Camera coordinate system conversions.
//!
//! This module provides conversions between NDC (Normalized Device Coordinates)
//! and camera coordinate systems, accounting for camera intrinsics.

use nalgebra::Point2;

use crate::datatype::camera_coord_value::{
    CameraCoordPoint2, CameraCoordValue,
};
use crate::datatype::camera_intrinsics::CameraIntrinsics;
use crate::datatype::common::UnitValue;
use crate::datatype::ndc_value::{NdcPoint2, NdcValue};

// ============================================================================
// NDC <-> Camera Coordinate Conversions
// ============================================================================

/// Convert NDC point to camera coordinate point using principal point and focal lengths.
///
/// Transforms from NDC coordinates [-1,1] to camera coordinates using camera intrinsics.
/// The transformation accounts for:
/// - NDC range of 2.0 units (from -1 to +1)
/// - Separate focal lengths for X and Y dimensions
///
/// The formula is:
/// - `camera_x = (ndc.x - principal_point_x) / (2.0 * focal_length_x)`
/// - `camera_y = (ndc.y - principal_point_y) / (2.0 * focal_length_y)`
///
/// # Arguments
/// * `ndc_point` - Point in NDC coordinates [-1,1]
/// * `principal_point_x` - Principal point X offset in NDC
/// * `principal_point_y` - Principal point Y offset in NDC
/// * `focal_length_x` - Focal length in X direction, normalized by film-back width (focal_length_mm / film_back_width_mm)
/// * `focal_length_y` - Focal length in Y direction, normalized by film-back height (focal_length_mm / film_back_height_mm)
///
pub fn convert_ndc_to_camera_coord_point<T>(
    ndc_point: NdcPoint2<T>,
    principal_point_x: T,
    principal_point_y: T,
    focal_length_x: T,
    focal_length_y: T,
) -> CameraCoordPoint2<T>
where
    T: Copy
        + std::ops::Sub<Output = T>
        + std::ops::Div<Output = T>
        + std::ops::Mul<Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    // NDC space is [-1, 1] (range of 2.0) in both dimensions.
    let two = T::from(2.0);
    Point2::new(
        CameraCoordValue(
            (ndc_point.x.value() - principal_point_x) / (two * focal_length_x),
        ),
        CameraCoordValue(
            (ndc_point.y.value() - principal_point_y) / (two * focal_length_y),
        ),
    )
}

// TODO: Why is this needed for *some* of the triangulation methods,
// but not line-line?
pub fn convert_ndc_to_camera_coord_point_inverted<T>(
    ndc_point: NdcPoint2<T>,
    principal_point_x: T,
    principal_point_y: T,
    focal_length_x: T,
    focal_length_y: T,
) -> CameraCoordPoint2<T>
where
    T: Copy
        + std::ops::Sub<Output = T>
        + std::ops::Div<Output = T>
        + std::ops::Mul<Output = T>
        + std::ops::Neg<Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    // NDC space is [-1, 1] (range of 2.0) in both dimensions.
    let two = T::from(2.0);
    Point2::new(
        CameraCoordValue(
            -(ndc_point.x.value() - principal_point_x) / (two * focal_length_x),
        ),
        CameraCoordValue(
            -(ndc_point.y.value() - principal_point_y) / (two * focal_length_y),
        ),
    )
}

/// Convert NDC point to camera coordinate point using camera intrinsics.
///
/// Convenient wrapper that extracts principal point and focal lengths from intrinsics.
///
/// # Arguments
/// * `ndc_point` - Point in NDC coordinates [-1,1]
/// * `intrinsics` - Camera intrinsics containing focal lengths and principal point
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::{*, conversions::*};
///
/// let ndc = NdcValue::point2(1.0, 1.0);
/// let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
/// let focal_length_mm = MillimeterUnit::new(50.0);
/// let intrinsics = CameraIntrinsics::from_centered_lens(focal_length_mm, film_back);
/// let camera_coord = convert_ndc_to_camera_coord_point_with_intrinsics(ndc, &intrinsics);
/// // For 50mm lens on 36x24mm sensor:
/// // focal_length_x = 50/36 = 1.389
/// // focal_length_y = 50/24 = 2.083
/// // camera_x = 1.0 / (2.0 * 1.389) = 0.36
/// // camera_y = 1.0 / (2.0 * 2.083) = 0.24
/// ```
pub fn convert_ndc_to_camera_coord_point_with_intrinsics<T>(
    ndc_point: NdcPoint2<T>,
    intrinsics: &CameraIntrinsics,
) -> CameraCoordPoint2<T>
where
    T: From<f64>
        + Copy
        + std::ops::Sub<Output = T>
        + std::ops::Div<Output = T>
        + std::ops::Mul<Output = T>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    let principal_point_x = T::from(intrinsics.principal_point.x.value());
    let principal_point_y = T::from(intrinsics.principal_point.y.value());
    let focal_length_x = T::from(intrinsics.focal_length_x);
    let focal_length_y = T::from(intrinsics.focal_length_y);

    convert_ndc_to_camera_coord_point(
        ndc_point,
        principal_point_x,
        principal_point_y,
        focal_length_x,
        focal_length_y,
    )
}

// TODO: Why is this needed for *some* of the triangulation methods,
// but not line-line?
pub fn convert_ndc_to_camera_coord_point_with_intrinsics_inverted<T>(
    ndc_point: NdcPoint2<T>,
    intrinsics: &CameraIntrinsics,
) -> CameraCoordPoint2<T>
where
    T: From<f64>
        + Copy
        + std::ops::Sub<Output = T>
        + std::ops::Div<Output = T>
        + std::ops::Mul<Output = T>
        + std::ops::Neg<Output = T>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    let principal_point_x = T::from(intrinsics.principal_point.x.value());
    let principal_point_y = T::from(intrinsics.principal_point.y.value());
    let focal_length_x = T::from(intrinsics.focal_length_x);
    let focal_length_y = T::from(intrinsics.focal_length_y);

    convert_ndc_to_camera_coord_point_inverted(
        ndc_point,
        principal_point_x,
        principal_point_y,
        focal_length_x,
        focal_length_y,
    )
}

/// Convert camera coordinate point to NDC point using principal point and focal lengths.
///
/// Inverse transformation that accounts for:
/// - NDC range of 2.0 units (from -1 to +1)
/// - Separate focal lengths for X and Y dimensions
///
/// The formula is:
/// - `ndc.x = camera_x * (2.0 * focal_length_x) + principal_point_x`
/// - `ndc.y = camera_y * (2.0 * focal_length_y) + principal_point_y`
///
/// # Arguments
/// * `camera_coord_point` - Point in camera coordinates
/// * `principal_point_x` - Principal point X offset in NDC
/// * `principal_point_y` - Principal point Y offset in NDC
/// * `focal_length_x` - Focal length in X direction, normalized by film-back width
/// * `focal_length_y` - Focal length in Y direction, normalized by film-back height
///
pub fn convert_camera_coord_to_ndc_point<T>(
    camera_coord_point: CameraCoordPoint2<T>,
    principal_point_x: T,
    principal_point_y: T,
    focal_length_x: T,
    focal_length_y: T,
) -> NdcPoint2<T>
where
    T: Copy
        + std::ops::Add<Output = T>
        + std::ops::Mul<Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    // Inverse of convert_ndc_to_camera_coord_point.
    let two = T::from(2.0);
    Point2::new(
        NdcValue(
            camera_coord_point.x.value() * (two * focal_length_x)
                + principal_point_x,
        ),
        NdcValue(
            camera_coord_point.y.value() * (two * focal_length_y)
                + principal_point_y,
        ),
    )
}

/// Convert camera coordinate point to NDC point using camera intrinsics.
///
/// Convenient wrapper that extracts principal point and focal lengths from intrinsics.
///
/// # Arguments
/// * `camera_coord_point` - Point in camera coordinates
/// * `intrinsics` - Camera intrinsics containing focal lengths and principal point
pub fn convert_camera_coord_to_ndc_point_with_intrinsics<T>(
    camera_coord_point: CameraCoordPoint2<T>,
    intrinsics: &CameraIntrinsics,
) -> NdcPoint2<T>
where
    T: From<f64>
        + Copy
        + std::ops::Add<Output = T>
        + std::ops::Mul<Output = T>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    let principal_point_x = T::from(intrinsics.principal_point.x.value());
    let principal_point_y = T::from(intrinsics.principal_point.y.value());
    let focal_length_x = T::from(intrinsics.focal_length_x);
    let focal_length_y = T::from(intrinsics.focal_length_y);

    convert_camera_coord_to_ndc_point(
        camera_coord_point,
        principal_point_x,
        principal_point_y,
        focal_length_x,
        focal_length_y,
    )
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::common::UnitValue;
    use crate::datatype::{
        CameraFilmBack, CameraIntrinsics, MillimeterUnit, NdcValue,
    };
    use approx::assert_relative_eq;

    #[test]
    fn test_ndc_to_camera_coord_conversions() {
        let ndc = NdcValue::point2(1.0, -0.5);
        let focal_length_x = 1.0;
        let focal_length_y = 1.0;
        let camera_coord = convert_ndc_to_camera_coord_point(
            ndc,
            0.0,
            0.0,
            focal_length_x,
            focal_length_y,
        );
        assert_relative_eq!(camera_coord.x.value(), 0.5, epsilon = 1e-10);
        assert_relative_eq!(camera_coord.y.value(), -0.25, epsilon = 1e-10);

        // Test with principal point offset
        let camera_coord_offset = convert_ndc_to_camera_coord_point(
            ndc,
            0.2,
            -0.1,
            focal_length_x,
            focal_length_y,
        );
        assert_relative_eq!(
            camera_coord_offset.x.value(),
            0.4,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            camera_coord_offset.y.value(),
            -0.2,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_ndc_to_camera_coord_with_intrinsics() {
        let ndc = NdcValue::point2(0.6, -0.8);
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(54.0),  // 1.5 * 36.0
            MillimeterUnit::new(-14.4), // -0.8 * 36.0 * 0.5
            MillimeterUnit::new(10.8),  // 0.9 * 24.0 * 0.5
            film_back,
        );
        let camera_coord =
            convert_ndc_to_camera_coord_point_with_intrinsics(ndc, &intrinsics);

        assert_relative_eq!(camera_coord.x.value(), 1.4 / 3.0, epsilon = 1e-10);
        assert_relative_eq!(
            camera_coord.y.value(),
            -1.7 / 4.5,
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_camera_coord_to_ndc_round_trip() {
        let original_ndc = NdcValue::point2(0.5, -0.3);
        let principal_x = 0.1;
        let principal_y = -0.05;
        let focal_length = 1.8;
        let aspect_ratio = 1.0;

        let camera_coord = convert_ndc_to_camera_coord_point(
            original_ndc,
            principal_x,
            principal_y,
            focal_length,
            aspect_ratio,
        );
        let back_to_ndc = convert_camera_coord_to_ndc_point(
            camera_coord,
            principal_x,
            principal_y,
            focal_length,
            aspect_ratio,
        );

        assert_relative_eq!(back_to_ndc.x.value(), 0.5, epsilon = 1e-10);
        assert_relative_eq!(back_to_ndc.y.value(), -0.3, epsilon = 1e-10);
    }

    #[test]
    fn test_camera_coord_to_ndc_with_intrinsics_round_trip() {
        let original_ndc = NdcValue::point2(-0.7, 0.4);
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(90.0), // 2.5 * 36.0
            MillimeterUnit::new(5.4),  // 0.3 * 36.0 * 0.5
            MillimeterUnit::new(-2.4), // -0.2 * 24.0 * 0.5
            film_back,
        );

        let camera_coord = convert_ndc_to_camera_coord_point_with_intrinsics(
            original_ndc,
            &intrinsics,
        );
        let back_to_ndc = convert_camera_coord_to_ndc_point_with_intrinsics(
            camera_coord,
            &intrinsics,
        );

        assert_relative_eq!(back_to_ndc.x.value(), -0.7, epsilon = 1e-10);
        assert_relative_eq!(back_to_ndc.y.value(), 0.4, epsilon = 1e-10);
    }
}
