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

pub mod camera_coord_value;
pub mod common;
pub mod conversions;
pub mod millimeter_unit;
pub mod ndc_value;
pub mod pixel_value;
pub mod scene_unit;
pub mod uv_value;
pub use camera_coord_value::{
    CameraCoordPoint2, CameraCoordValue, CameraCoordVector2,
};
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

