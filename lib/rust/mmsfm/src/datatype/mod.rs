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

pub mod bearing_vector_correspondence;
pub mod camera_coord_value;
pub mod camera_film_back;
pub mod camera_frustum;
pub mod camera_intrinsics;
pub mod camera_to_scene_correspondence;
pub mod common;
pub mod conversions;
pub mod image_size;
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
pub use camera_coord_value::{
    CameraCoordPoint2, CameraCoordValue, CameraCoordVector2,
};
pub use camera_film_back::CameraFilmBack;
pub use camera_frustum::CameraFrustum;
pub use camera_intrinsics::CameraIntrinsics;
pub use camera_to_scene_correspondence::CameraToSceneCorrespondence;
pub use image_size::ImageSize;
pub use millimeter_unit::{
    MillimeterPoint2, MillimeterPoint3, MillimeterUnit, MillimeterVector2,
    MillimeterVector3,
};
pub use ndc_value::{NdcPoint2, NdcValue, NdcVector2};
pub use pixel_value::{PixelPoint2, PixelValue, PixelVector2};
pub use scene_unit::{
    ScenePoint2, ScenePoint3, SceneUnit, SceneVector2, SceneVector3,
};
pub use uv_value::{UvPoint2, UvValue, UvVector2};

