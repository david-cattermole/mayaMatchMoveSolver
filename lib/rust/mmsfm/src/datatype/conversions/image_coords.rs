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

//! Image coordinate system conversions (UV <-> NDC <-> Pixel).
//!
//! This module provides conversions between image coordinate systems:
//! - **Pixel coordinates**: Image space with origin at (0,0) in pixels
//! - **UV coordinates**: Normalized texture coordinates [0,1]
//! - **NDC coordinates**: Normalized device coordinates [-1,1]

use nalgebra::{Point2, Vector2};
use std::ops::{Add, Div, Mul};

use crate::datatype::camera_coord_value::CameraCoordPoint2;
use crate::datatype::camera_intrinsics::CameraIntrinsics;
use crate::datatype::common::UnitValue;
use crate::datatype::image_size::ImageSize;
use crate::datatype::ndc_value::{NdcPoint2, NdcValue, NdcVector2};
use crate::datatype::pixel_value::{PixelPoint2, PixelValue, PixelVector2};
use crate::datatype::uv_value::{UvPoint2, UvValue, UvVector2};

// ============================================================================
// UV <-> NDC Point Conversions
// ============================================================================

/// Convert UV point to NDC point.
///
/// Transforms from UV coordinates [0,1] to NDC coordinates [-1,1]
/// where (0,0) in UV becomes (0,0) in NDC (both are center).
///
/// # Arguments
/// * `uv_point` - Point in UV coordinates [0,1]
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::{*, conversions::*};
///
/// let uv = UvValue::point2(0.5, 0.5);  // Center in UV
/// let ndc = convert_uv_to_ndc_point(uv);
/// assert_eq!(ndc.x.value(), 0.0);      // Center in NDC
/// assert_eq!(ndc.y.value(), 0.0);
/// ```
pub fn convert_uv_to_ndc_point<T>(uv_point: UvPoint2<T>) -> NdcPoint2<T>
where
    T: Copy
        + Add<T, Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    Point2::new(
        NdcValue((uv_point.x.value() + T::from(-0.5)) * T::from(2.0)),
        NdcValue((uv_point.y.value() + T::from(-0.5)) * T::from(2.0)),
    )
}

/// Convert NDC point to UV point.
///
/// Transforms from NDC coordinates [-1,1] to UV coordinates [0,1]
/// where (0,0) in NDC becomes (0.5,0.5) in UV (both are center).
///
/// # Arguments
/// * `ndc_point` - Point in NDC coordinates [-1,1]
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::{*, conversions::*};
///
/// let ndc = NdcValue::point2(0.0, 0.0);  // Center in NDC
/// let uv = convert_ndc_to_uv_point(ndc);
/// assert_eq!(uv.x.value(), 0.5);         // Center in UV
/// assert_eq!(uv.y.value(), 0.5);
/// ```
pub fn convert_ndc_to_uv_point<T>(ndc_point: NdcPoint2<T>) -> UvPoint2<T>
where
    T: Copy
        + Add<T, Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    Point2::new(
        UvValue(ndc_point.x.value() * T::from(0.5) + T::from(0.5)),
        UvValue(ndc_point.y.value() * T::from(0.5) + T::from(0.5)),
    )
}

// ============================================================================
// ImageSize-based Point Conversions
// ============================================================================

/// Convert pixel point to UV point using ImageSize.
///
/// Convenient wrapper that uses ImageSize for dimensions and pixel aspect ratio.
///
/// # Arguments
/// * `pixel_point` - Point in pixel coordinates
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
///
/// # Examples
/// ```rust
/// use mmsfm_rust::datatype::{*, conversions::*};
///
/// let image_size = ImageSize::from_pixels(1920.0, 1080.0);
/// let pixel = PixelValue::point2(960.0, 540.0);
/// let uv = convert_pixel_to_uv_point(pixel, &image_size);
/// assert_eq!(uv.x.value(), 0.5);
/// assert_eq!(uv.y.value(), 0.5);
/// ```
pub fn convert_pixel_to_uv_point<T>(
    pixel_point: PixelPoint2<T>,
    image_size: &ImageSize<T>,
) -> UvPoint2<T>
where
    T: Copy + Div<Output = T> + std::fmt::Debug + PartialEq + 'static,
{
    Point2::new(
        UvValue(pixel_point.x.value() / image_size.width.value()),
        UvValue(pixel_point.y.value() / image_size.height.value()),
    )
}

/// Convert UV point to pixel point using ImageSize.
///
/// # Arguments
/// * `uv_point` - Point in UV coordinates [0,1]
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
pub fn convert_uv_to_pixel_point<T>(
    uv_point: UvPoint2<T>,
    image_size: &ImageSize<T>,
) -> PixelPoint2<T>
where
    T: Copy + Mul<Output = T> + std::fmt::Debug + PartialEq + 'static,
{
    Point2::new(
        PixelValue(uv_point.x.value() * image_size.width.value()),
        PixelValue(uv_point.y.value() * image_size.height.value()),
    )
}

/// Convert pixel point to NDC point using ImageSize.
///
/// # Arguments
/// * `pixel_point` - Point in pixel coordinates
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
pub fn convert_pixel_to_ndc_point<T>(
    pixel_point: PixelPoint2<T>,
    image_size: &ImageSize<T>,
) -> NdcPoint2<T>
where
    T: Copy
        + Add<T, Output = T>
        + Div<Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    // TODO: Remove the UvValue as an intermediate computation.
    let uv_point = convert_pixel_to_uv_point(pixel_point, image_size);
    convert_uv_to_ndc_point(uv_point)
}

/// Convert NDC point to pixel point using ImageSize.
///
/// # Arguments
/// * `ndc_point` - Point in NDC coordinates [-1,1]
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
pub fn convert_ndc_to_pixel_point<T>(
    ndc_point: NdcPoint2<T>,
    image_size: &ImageSize<T>,
) -> PixelPoint2<T>
where
    T: Copy
        + Add<T, Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    // TODO: Remove the UvValue as an intermediate computation.
    let uv_point = convert_ndc_to_uv_point(ndc_point);
    convert_uv_to_pixel_point(uv_point, image_size)
}

/// Convert UV coordinates (0.0 to 1.0) to normalized camera coordinates
///
/// # Arguments
/// * `uv` - UV coordinate in 0.0 to 1.0 space
/// * `intrinsics` - Camera intrinsics in normalized units
///
/// # Returns
/// Normalized camera coordinate
pub fn uv_point_to_camera_coord_point(
    uv: UvPoint2<f64>,
    intrinsics: &CameraIntrinsics,
) -> CameraCoordPoint2<f64> {
    // Convert UV coordinates [0.0, 1.0] to NDC coordinates [-1.0, 1.0]
    let ndc = convert_uv_to_ndc_point(uv);

    // Import the conversion function from camera_coords module
    use super::convert_ndc_to_camera_coord_point;

    // Apply camera intrinsics to NDC coordinates using centralized conversion function
    convert_ndc_to_camera_coord_point(
        ndc,
        intrinsics.principal_point.x.value(),
        intrinsics.principal_point.y.value(),
        intrinsics.focal_length_x,
        intrinsics.focal_length_y,
    )
}

/// Convert UV point to camera coordinate point using camera intrinsics (inverted).
///
/// This inverted version negates both X and Y coordinates, which is required
/// for some triangulation methods (e.g., Hartley-Sturm, DLT) where the
/// coordinate convention differs.
///
/// # Arguments
/// * `uv` - UV coordinate (0.0 to 1.0)
/// * `intrinsics` - Camera intrinsics in normalized units
///
/// # Returns
/// Normalized camera coordinate with inverted X and Y
pub fn uv_point_to_camera_coord_point_inverted(
    uv: UvPoint2<f64>,
    intrinsics: &CameraIntrinsics,
) -> CameraCoordPoint2<f64> {
    // Convert UV coordinates [0.0, 1.0] to NDC coordinates [-1.0, 1.0]
    let ndc = convert_uv_to_ndc_point(uv);

    // Import the inverted conversion function from camera_coords module
    use super::convert_ndc_to_camera_coord_point_inverted;

    // Apply camera intrinsics with inverted signs for triangulation methods
    convert_ndc_to_camera_coord_point_inverted(
        ndc,
        intrinsics.principal_point.x.value(),
        intrinsics.principal_point.y.value(),
        intrinsics.focal_length_x,
        intrinsics.focal_length_y,
    )
}

// ============================================================================
// Vector Conversions
// ============================================================================

/// Convert pixel vector to UV vector.
///
/// # Arguments
/// * `pixel_vector` - Vector in pixel coordinates
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
pub fn convert_pixel_to_uv_vector<T>(
    pixel_vector: PixelVector2<T>,
    image_size: &ImageSize<T>,
) -> UvVector2<T>
where
    T: Copy + Div<Output = T> + std::fmt::Debug + PartialEq + 'static,
{
    Vector2::new(
        UvValue(pixel_vector[0].value() / image_size.width.value()),
        UvValue(pixel_vector[1].value() / image_size.height.value()),
    )
}

/// Convert UV vector to pixel vector.
///
/// # Arguments
/// * `uv_vector` - Vector in UV coordinates
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
pub fn convert_uv_to_pixel_vector<T>(
    uv_vector: UvVector2<T>,
    image_size: &ImageSize<T>,
) -> PixelVector2<T>
where
    T: Copy + Mul<Output = T> + std::fmt::Debug + PartialEq + 'static,
{
    Vector2::new(
        PixelValue(uv_vector[0].value() * image_size.width.value()),
        PixelValue(uv_vector[1].value() * image_size.height.value()),
    )
}

/// Convert UV vector to NDC vector.
pub fn convert_uv_to_ndc_vector<T>(uv_vector: UvVector2<T>) -> NdcVector2<T>
where
    T: Copy + Add<T, Output = T> + Mul<T, Output = T> + From<f64>,
{
    Vector2::new(
        NdcValue((uv_vector[0].value() + T::from(-0.5)) * T::from(2.0)),
        NdcValue((uv_vector[1].value() + T::from(-0.5)) * T::from(2.0)),
    )
}

/// Convert NDC vector to UV vector.
pub fn convert_ndc_to_uv_vector<T>(ndc_vector: NdcVector2<T>) -> UvVector2<T>
where
    T: Copy + Add<T, Output = T> + Mul<T, Output = T> + From<f64>,
{
    Vector2::new(
        UvValue(ndc_vector[0].value() * T::from(0.5) + T::from(0.5)),
        UvValue(ndc_vector[1].value() * T::from(0.5) + T::from(0.5)),
    )
}

/// Convert pixel vector to NDC vector.
pub fn convert_pixel_to_ndc_vector<T>(
    pixel_vector: PixelVector2<T>,
    image_size: &ImageSize<T>,
) -> NdcVector2<T>
where
    T: Copy
        + Add<T, Output = T>
        + Div<Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    // TODO: Remove the UvValue as an intermediate computation.
    let uv_vector = convert_pixel_to_uv_vector(pixel_vector, image_size);
    convert_uv_to_ndc_vector(uv_vector)
}

/// Convert NDC vector to pixel vector.
pub fn convert_ndc_to_pixel_vector<T>(
    ndc_vector: NdcVector2<T>,
    image_size: &ImageSize<T>,
) -> PixelVector2<T>
where
    T: Copy
        + Add<T, Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    // TODO: Remove the UvValue as an intermediate computation.
    let uv_vector = convert_ndc_to_uv_vector(ndc_vector);
    convert_uv_to_pixel_vector(uv_vector, image_size)
}

// ============================================================================
// Batch Conversions
// ============================================================================
// TODO: The batch conversion functions currently all return a newly
// allocated Vec datatype. although this is convenient, it is not
// performant, due to the allocation. Instead, I would like to
// refactor the batch functions to only return Result data types if
// there is a possibility of conversion failure, however all the batch
// functions should require the use of an input mutable slice of the
// expected data-type, allocated with the exact length that is
// required for the resulting object. This will remove all heap
// allocations during conversions.

/// Convert a slice of UV points to NDC points.
///
/// # Arguments
/// * `uv_points` - Slice of points in UV coordinates
///
/// # Returns
/// Vector of NDC points
// TODO: Refactor function to use mutable slice for output data.
pub fn convert_uv_to_ndc_points<T>(
    uv_points: &[UvPoint2<T>],
) -> Vec<NdcPoint2<T>>
where
    T: Copy
        + Add<T, Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    uv_points
        .iter()
        .map(|&point| convert_uv_to_ndc_point(point))
        .collect()
}

/// Convert a slice of NDC points to UV points.
///
/// # Arguments
/// * `ndc_points` - Slice of points in NDC coordinates
///
/// # Returns
/// Vector of UV points
// TODO: Refactor function to use mutable slice for output data.
pub fn convert_ndc_to_uv_points<T>(
    ndc_points: &[NdcPoint2<T>],
) -> Vec<UvPoint2<T>>
where
    T: Copy
        + Add<T, Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    ndc_points
        .iter()
        .map(|&point| convert_ndc_to_uv_point(point))
        .collect()
}

/// Convert a slice of pixel points to UV points using ImageSize.
///
/// # Arguments
/// * `pixel_points` - Slice of points in pixel coordinates
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
///
/// # Returns
/// Vector of UV points
// TODO: Refactor function to use mutable slice for output data.
pub fn convert_pixel_to_uv_points<T>(
    pixel_points: &[PixelPoint2<T>],
    image_size: &ImageSize<T>,
) -> Vec<UvPoint2<T>>
where
    T: Copy + Div<Output = T> + std::fmt::Debug + PartialEq + 'static,
{
    pixel_points
        .iter()
        .map(|&point| convert_pixel_to_uv_point(point, image_size))
        .collect()
}

/// Convert a slice of UV points to pixel points using ImageSize.
///
/// # Arguments
/// * `uv_points` - Slice of points in UV coordinates
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
///
/// # Returns
/// Vector of pixel points
// TODO: Refactor function to use mutable slice for output data.
pub fn convert_uv_to_pixel_points<T>(
    uv_points: &[UvPoint2<T>],
    image_size: &ImageSize<T>,
) -> Vec<PixelPoint2<T>>
where
    T: Copy + Mul<Output = T> + std::fmt::Debug + PartialEq + 'static,
{
    uv_points
        .iter()
        .map(|&point| convert_uv_to_pixel_point(point, image_size))
        .collect()
}

/// Convert a slice of pixel points to NDC points using ImageSize.
///
/// # Arguments
/// * `pixel_points` - Slice of points in pixel coordinates
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
///
/// # Returns
/// Vector of NDC points
// TODO: Refactor function to use mutable slice for output data.
pub fn convert_pixel_to_ndc_points<T>(
    pixel_points: &[PixelPoint2<T>],
    image_size: &ImageSize<T>,
) -> Vec<NdcPoint2<T>>
where
    T: Copy
        + Add<T, Output = T>
        + Div<Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    pixel_points
        .iter()
        .map(|&point| convert_pixel_to_ndc_point(point, image_size))
        .collect()
}

/// Convert a slice of NDC points to pixel points using ImageSize.
///
/// # Arguments
/// * `ndc_points` - Slice of points in NDC coordinates
/// * `image_size` - ImageSize containing width, height, and pixel aspect ratio
///
/// # Returns
/// Vector of pixel points
// TODO: Refactor function to use mutable slice for output data.
pub fn convert_ndc_to_pixel_points<T>(
    ndc_points: &[NdcPoint2<T>],
    image_size: &ImageSize<T>,
) -> Vec<PixelPoint2<T>>
where
    T: Copy
        + Add<T, Output = T>
        + Mul<T, Output = T>
        + From<f64>
        + std::fmt::Debug
        + PartialEq
        + 'static,
{
    ndc_points
        .iter()
        .map(|&point| convert_ndc_to_pixel_point(point, image_size))
        .collect()
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::datatype::common::UnitValue;
    use crate::datatype::{
        CameraFilmBack, CameraIntrinsics, ImageSize, MillimeterUnit, NdcValue,
        PixelValue, UvValue,
    };
    use approx::assert_relative_eq;

    #[test]
    fn test_uv_to_normalized_camera_coord() {
        // Create realistic test camera intrinsics: 50mm lens on full-frame 35mm sensor
        let intrinsics = {
            let film_back = CameraFilmBack::from_millimeters(36.0, 24.0); // 36mm x 24mm
            let focal_length = MillimeterUnit::new(50.0);
            CameraIntrinsics::from_centered_lens(focal_length, film_back)
        };

        let uv_center = UvValue::point2(0.5, 0.5);
        let normalized =
            uv_point_to_camera_coord_point(uv_center.into(), &intrinsics);
        assert_relative_eq!(normalized.x.value(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(normalized.y.value(), 0.0, epsilon = 1e-10);

        let uv_corner = UvValue::point2(1.0, 1.0);
        let normalized =
            uv_point_to_camera_coord_point(uv_corner.into(), &intrinsics);
        assert_relative_eq!(
            normalized.x.value(),
            1.0 / (2.0 * intrinsics.focal_length_x),
            epsilon = 1e-10
        );
        assert_relative_eq!(
            normalized.y.value(),
            1.0 / (2.0 * intrinsics.focal_length_y),
            epsilon = 1e-10
        );
    }

    #[test]
    fn test_convert_pixel_to_uv_point() {
        let pixel_point = PixelValue::point2(960.0, 540.0);
        let image_size = ImageSize::from_pixels(1920.0, 1080.0);
        let uv_point = convert_pixel_to_uv_point(pixel_point, &image_size);
        assert_relative_eq!(uv_point.x.value(), 0.5, epsilon = 1e-10);
        assert_relative_eq!(uv_point.y.value(), 0.5, epsilon = 1e-10);
    }

    #[test]
    fn test_convert_uv_to_pixel_point() {
        let uv_point = UvValue::point2(0.5, 0.5);
        let image_size = ImageSize::from_pixels(1920.0, 1080.0);
        let pixel_point = convert_uv_to_pixel_point(uv_point, &image_size);
        assert_relative_eq!(pixel_point.x.value(), 960.0, epsilon = 1e-10);
        assert_relative_eq!(pixel_point.y.value(), 540.0, epsilon = 1e-10);
    }

    #[test]
    fn test_convert_uv_to_ndc_point() {
        let uv_point = UvValue::point2(0.5, 0.5);
        let ndc_point = convert_uv_to_ndc_point(uv_point);
        assert_relative_eq!(ndc_point.x.value(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(ndc_point.y.value(), 0.0, epsilon = 1e-10);

        let uv_min = UvValue::point2(0.0, 0.0);
        let ndc_min = convert_uv_to_ndc_point(uv_min);
        assert_relative_eq!(ndc_min.x.value(), -1.0, epsilon = 1e-10);
        assert_relative_eq!(ndc_min.y.value(), -1.0, epsilon = 1e-10);

        let uv_max = UvValue::point2(1.0, 1.0);
        let ndc_max = convert_uv_to_ndc_point(uv_max);
        assert_relative_eq!(ndc_max.x.value(), 1.0, epsilon = 1e-10);
        assert_relative_eq!(ndc_max.y.value(), 1.0, epsilon = 1e-10);
    }

    #[test]
    fn test_convert_ndc_to_uv_point() {
        let ndc_point = NdcValue::point2(0.0, 0.0);
        let uv_point = convert_ndc_to_uv_point(ndc_point);
        assert_relative_eq!(uv_point.x.value(), 0.5, epsilon = 1e-10);
        assert_relative_eq!(uv_point.y.value(), 0.5, epsilon = 1e-10);
    }

    #[test]
    fn test_round_trip_conversions() {
        let image_size = ImageSize::from_pixels(1920.0, 1080.0);

        // Test UV -> NDC -> UV round trip
        let original_uv = UvValue::point2(0.25, 0.75);
        let ndc = convert_uv_to_ndc_point(original_uv);
        let back_to_uv = convert_ndc_to_uv_point(ndc);
        assert_relative_eq!(back_to_uv.x.value(), 0.25, epsilon = 1e-10);
        assert_relative_eq!(back_to_uv.y.value(), 0.75, epsilon = 1e-10);

        // Test Pixel -> UV -> Pixel round trip
        let original_pixel = PixelValue::point2(480.0, 270.0);
        let uv = convert_pixel_to_uv_point(original_pixel, &image_size);
        let back_to_pixel = convert_uv_to_pixel_point(uv, &image_size);
        assert_relative_eq!(back_to_pixel.x.value(), 480.0, epsilon = 1e-10);
        assert_relative_eq!(back_to_pixel.y.value(), 270.0, epsilon = 1e-10);
    }

    #[test]
    fn test_batch_conversions() {
        let image_size = ImageSize::from_pixels(1920.0, 1080.0);

        let pixel_points = vec![
            PixelValue::point2(0.0, 0.0),
            PixelValue::point2(960.0, 540.0),
            PixelValue::point2(1920.0, 1080.0),
        ];
        let uv_points = convert_pixel_to_uv_points(&pixel_points, &image_size);

        assert_relative_eq!(uv_points[0].x.value(), 0.0, epsilon = 1e-10);
        assert_relative_eq!(uv_points[1].x.value(), 0.5, epsilon = 1e-10);
        assert_relative_eq!(uv_points[2].x.value(), 1.0, epsilon = 1e-10);
    }

    #[test]
    fn test_vector_conversions() {
        let image_size = ImageSize::from_pixels(1920.0, 1080.0);
        let pixel_vector = PixelValue::vector2(100.0, 50.0);
        let uv_vector = convert_pixel_to_uv_vector(pixel_vector, &image_size);

        assert_relative_eq!(
            uv_vector[0].value(),
            100.0 / 1920.0,
            epsilon = 1e-10
        );
        assert_relative_eq!(
            uv_vector[1].value(),
            50.0 / 1080.0,
            epsilon = 1e-10
        );

        // Test round trip
        let back_to_pixel = convert_uv_to_pixel_vector(uv_vector, &image_size);
        assert_relative_eq!(back_to_pixel[0].value(), 100.0, epsilon = 1e-10);
        assert_relative_eq!(back_to_pixel[1].value(), 50.0, epsilon = 1e-10);
    }
}
