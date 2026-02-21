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

//! Coordinate system conversion functions.
//!
//! This module provides a complete set of conversion functions between different
//! coordinate systems used in computer vision, graphics, and photogrammetry:
//!
//! ## Image Coordinate Systems
//! - **Pixel coordinates**: Image space with origin at (0,0) in pixels
//! - **UV coordinates**: Normalized texture coordinates [0,1]
//! - **NDC coordinates**: Normalized device coordinates [-1,1]
//!
//! ## Physical Coordinate Systems
//! - **Millimeter units**: Physical measurements in mm
//! - **Scene units**: Maya/application scene units
//! - **Camera intrinsics**: Physical <-> normalized camera parameters
//!
//! ## Design Principles
//! - All functions operate on Point2 and Vector2 types for type safety
//! - Clear, descriptive function names indicate source -> destination
//! - Support for both individual and batch conversions
//! - ImageSize integration for practical workflows
//! - Comprehensive test coverage with round-trip validation

pub mod bearing_vectors;
pub mod camera_coords;
pub mod coordinate_systems;
pub mod image_coords;
pub mod ray_conversions;

// Re-export all conversion functions from submodules.
pub use bearing_vectors::{
    convert_bearing_vector_to_camera_coord,
    convert_camera_coord_to_bearing_vector,
    convert_camera_coord_to_homogeneous_vector,
    convert_homogeneous_vector_to_camera_coord,
};
pub use camera_coords::{
    convert_camera_coord_to_ndc_point,
    convert_camera_coord_to_ndc_point_with_intrinsics,
    convert_ndc_to_camera_coord_point,
    convert_ndc_to_camera_coord_point_inverted,
    convert_ndc_to_camera_coord_point_with_intrinsics,
    convert_ndc_to_camera_coord_point_with_intrinsics_inverted,
};
pub use coordinate_systems::{
    convert_cv_to_maya_point3, convert_cv_to_maya_rotation,
    convert_cv_to_maya_translation, convert_maya_to_cv_point3,
};
pub use image_coords::{
    convert_ndc_to_pixel_point, convert_ndc_to_pixel_points,
    convert_ndc_to_pixel_vector, convert_ndc_to_uv_point,
    convert_ndc_to_uv_points, convert_ndc_to_uv_vector,
    convert_pixel_to_ndc_point, convert_pixel_to_ndc_points,
    convert_pixel_to_ndc_vector, convert_pixel_to_uv_point,
    convert_pixel_to_uv_points, convert_pixel_to_uv_vector,
    convert_uv_to_ndc_point, convert_uv_to_ndc_points,
    convert_uv_to_ndc_vector, convert_uv_to_pixel_point,
    convert_uv_to_pixel_points, convert_uv_to_pixel_vector,
    uv_point_to_camera_coord_point, uv_point_to_camera_coord_point_inverted,
};
pub use ray_conversions::{
    convert_ndc_points_to_camera_rays, convert_ndc_to_ray_direction,
};
