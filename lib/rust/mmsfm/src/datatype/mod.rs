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

//! Type-safe data types for different numeric types and coordinate systems.
//!
//! This module provides zero-cost wrapper types that prevent accidental mixing
//! of different units while maintaining full runtime performance. Each unit type
//! wraps a numeric value (f32 or f64) and provides safe conversion methods
//! between compatible units.
//!
//! # Unit Types
//!
//! - [`MillimeterUnit<T>`] - Physical measurements in millimeters
//! - [`PixelValue<T>`] - Pixel values
//! - [`UvValue<T>`] - UV values (0.0-1.0 range)
//! - [`NdcValue<T>`] - NDC values (-1.0-1.0 range)
//! - [`CameraCoordValue<T>`] - Normalized camera coordinates (post-intrinsics)
//! - [`SceneUnit<T>`] - Maya scene units
//!
//! # Camera and Image Types
//!
//! - [`CameraFilmBack<T>`] - Physical camera sensor dimensions in millimeters
//! - [`ImageSize<T>`] - Image pixel dimensions with pixel aspect ratio support
//!
//! # Examples
//!
//! ```rust
//! use mmsfm_rust::datatype::*;
//!
//! // Create values with specific units
//! let distance = MillimeterUnit::new(25.4);
//! let pixel = PixelValue::new(100.0);
//! let uv = UvValue::new(0.5);
//! let ndc = NdcValue::new(0.0);
//! let camera_coord = CameraCoordValue::new(-0.3);
//!
//! // Convert between units with conversion functions
//! let mm_point = MillimeterUnit::point2(distance.value(), 0.0);
//! let pixel_point = PixelValue::point2(pixel.value(), 540.0);
//! let image_size = ImageSize::from_pixels(1920.0, 1080.0);
//! let normalized_uv = conversions::convert_pixel_to_uv_point(pixel_point, &image_size);
//!
//! // Create 2D points with type safety
//! let mm_point = MillimeterUnit::point2(10.0, 20.0);
//! let img_point = PixelValue::point2(960.0, 540.0);
//! let ndc_point = NdcValue::point2(0.0, 0.0);
//! let camera_coord_point = CameraCoordValue::point2(-0.5, 0.3);
//!
//! // Create camera and image specifications
//! let film_back = CameraFilmBack::from_millimeters(36.0, 24.0); // Full-frame 35mm
//! let image_size = ImageSize::from_pixels(1920.0, 1080.0); // Full HD
//! let anamorphic = ImageSize::from_pixels_with_aspect(1920.0, 1080.0, 2.0); // 2:1 anamorphic
//!
//! // Calculate aspect ratios
//! let sensor_aspect = film_back.aspect_ratio(); // 1.5 (3:2 ratio)
//! let image_aspect = image_size.aspect_ratio(); // ~1.778 (16:9 ratio)
//! let anamorphic_aspect = anamorphic.aspect_ratio(); // ~3.556 (32:9 ratio)
//! ```
//!
//! # Type Safety Benefits
//!
//! - Prevents mixing incompatible units (compile-time errors)
//! - Enforces explicit conversions between unit types
//! - Maintains runtime performance (zero overhead)
//! - Improves code readability and self-documentation

pub mod bearing_vector_correspondence;
pub mod bundle_positions;
pub mod camera_coord_value;
pub mod camera_film_back;
pub mod camera_frustum;
pub mod camera_intrinsics;
pub mod camera_pose;
pub mod camera_poses;
pub mod camera_to_scene_correspondence;
pub mod common;
pub mod conversions;
pub mod image_size;
pub mod marker_observations;
pub mod millimeter_unit;
pub mod ndc_value;
pub mod pixel_value;
pub mod scene_unit;
pub mod uv_point_correspondence;
pub mod uv_value;

// Re-export common traits
pub use common::UnitValue;

// Re-export all unit types and camera pose types.
pub use bearing_vector_correspondence::BearingVectorCorrespondence;
pub use bundle_positions::BundlePositions;
pub use camera_coord_value::{
    CameraCoordPoint2, CameraCoordValue, CameraCoordVector2,
};
pub use camera_film_back::CameraFilmBack;
pub use camera_frustum::CameraFrustum;
pub use camera_intrinsics::CameraIntrinsics;
pub use camera_pose::{is_valid_pose, CameraPose};
pub use camera_poses::CameraPoses;
pub use camera_to_scene_correspondence::CameraToSceneCorrespondence;
pub use image_size::ImageSize;
pub use marker_observations::MarkerObservations;
pub use millimeter_unit::{
    MillimeterPoint2, MillimeterPoint3, MillimeterUnit, MillimeterVector2,
    MillimeterVector3,
};
pub use ndc_value::{NdcPoint2, NdcValue, NdcVector2};
pub use pixel_value::{PixelPoint2, PixelValue, PixelVector2};
pub use scene_unit::{
    ScenePoint2, ScenePoint3, SceneUnit, SceneVector2, SceneVector3,
};
pub use uv_point_correspondence::UvPointCorrespondence;
pub use uv_value::{UvPoint2, UvValue, UvVector2};

