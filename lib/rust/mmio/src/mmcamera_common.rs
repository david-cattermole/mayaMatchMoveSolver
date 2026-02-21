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

//! Common data types for the `.mmcamera` file format.

/// Camera data from an `.mmcamera` file.
#[derive(Debug, Clone, PartialEq)]
pub struct MmCameraData {
    pub name: String,
    pub start_frame: i64,
    pub end_frame: i64,
    pub image: MmCameraImageData,
    pub attr: MmCameraAttrData,
}

/// Image metadata from an `.mmcamera` file.
#[derive(Debug, Clone, PartialEq)]
pub struct MmCameraImageData {
    pub file_path: Option<String>,
    pub width: Option<i64>,
    pub height: Option<i64>,
    pub pixel_aspect_ratio: Option<f64>,
}

/// Per-frame camera attribute data from an `.mmcamera` file.
///
/// Each field is a list of `(frame, value)` pairs.
#[derive(Debug, Clone, PartialEq)]
pub struct MmCameraAttrData {
    pub translate_x: Vec<(i64, f64)>,
    pub translate_y: Vec<(i64, f64)>,
    pub translate_z: Vec<(i64, f64)>,
    pub rotate_x: Vec<(i64, f64)>,
    pub rotate_y: Vec<(i64, f64)>,
    pub rotate_z: Vec<(i64, f64)>,
    pub focal_length: Vec<(i64, f64)>,
    pub film_back_width: Vec<(i64, f64)>,
    pub film_back_height: Vec<(i64, f64)>,
    pub film_back_offset_x: Vec<(i64, f64)>,
    pub film_back_offset_y: Vec<(i64, f64)>,
}
