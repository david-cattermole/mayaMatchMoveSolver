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

//! Data types for UV Track file format.

use thiserror::Error;

#[derive(Error, Debug)]
pub enum UVTrackError {
    #[error("Invalid file format: {0}")]
    InvalidFormat(String),

    #[error("Parse error: {0}")]
    ParseError(String),

    #[error("No points exist in file.")]
    NoPoints,

    #[error("Unexpected end of data.")]
    UnexpectedEOF,
}

pub type FrameNumber = u32;
pub type FrameCount = u32;

#[derive(Copy, Debug, Clone)]
pub struct FrameRange {
    pub start_frame: FrameNumber,
    pub end_frame: FrameNumber,
}

impl FrameRange {
    pub fn new(start_frame: FrameNumber, end_frame: FrameNumber) -> FrameRange {
        FrameRange {
            start_frame,
            end_frame,
        }
    }

    pub fn empty() -> FrameRange {
        FrameRange {
            start_frame: FrameNumber::MAX,
            end_frame: FrameNumber::MIN,
        }
    }

    pub fn frame_count(&self) -> FrameCount {
        let count: isize =
            (self.end_frame as isize - self.start_frame as isize) + 1;
        count.max(0) as FrameCount
    }
}

/// UV Track format versions matching the Python implementation
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum UVTrackFormatVersion {
    /// Unknown or invalid format.
    Unknown = -1,
    /// Version 1 - ASCII format.
    Version1 = 1,
    /// Version 2 - JSON format.
    Version2 = 2,
    /// Version 3 - JSON format with 3D data.
    Version3 = 3,
    /// Version 4 - JSON format with camera data.
    Version4 = 4,
    /// Version 5 - JSON format with scene and point group data.
    Version5 = 5,
}

impl UVTrackFormatVersion {
    pub fn from_i32(value: i32) -> Self {
        match value {
            1 => Self::Version1,
            2 => Self::Version2,
            3 => Self::Version3,
            4 => Self::Version4,
            5 => Self::Version5,
            _ => Self::Unknown,
        }
    }

    pub fn to_i32(self) -> i32 {
        self as i32
    }
}

/// Stores data for individual frames.
#[derive(Debug, Clone)]
pub struct FrameData {
    pub frame_range: FrameRange,
    pub frames: Vec<FrameNumber>,
    /// U coordinates (0.0 = left, 1.0 = right) - undistorted.
    pub u_coords: Vec<f64>,
    /// V coordinates (0.0 = bottom, 1.0 = top) - undistorted.
    pub v_coords: Vec<f64>,
    pub weights: Vec<f64>,
    /// Distorted U coordinates (v3+), if available.
    pub u_coords_dist: Vec<f64>,
    /// Distorted V coordinates (v3+), if available.
    pub v_coords_dist: Vec<f64>,
}

impl FrameData {
    pub fn new() -> Self {
        Self {
            frame_range: FrameRange::empty(),
            frames: Vec::new(),
            u_coords: Vec::new(),
            v_coords: Vec::new(),
            weights: Vec::new(),
            u_coords_dist: Vec::new(),
            v_coords_dist: Vec::new(),
        }
    }

    pub fn with_capacity(frame_count_capacity: usize) -> Self {
        Self {
            frame_range: FrameRange::empty(),
            frames: Vec::with_capacity(frame_count_capacity),
            u_coords: Vec::with_capacity(frame_count_capacity),
            v_coords: Vec::with_capacity(frame_count_capacity),
            weights: Vec::with_capacity(frame_count_capacity),
            u_coords_dist: Vec::new(),
            v_coords_dist: Vec::new(),
        }
    }

    pub fn push(&mut self, frame: FrameNumber, u: f64, v: f64, weight: f64) {
        if frame < self.frame_range.start_frame {
            self.frame_range.start_frame = frame;
        }
        if frame > self.frame_range.end_frame {
            self.frame_range.end_frame = frame;
        }

        self.frames.push(frame);
        self.u_coords.push(u);
        self.v_coords.push(v);
        self.weights.push(weight);
    }

    pub fn push_with_distorted(
        &mut self,
        frame: FrameNumber,
        u: f64,
        v: f64,
        weight: f64,
        u_dist: f64,
        v_dist: f64,
    ) {
        self.push(frame, u, v, weight);
        self.u_coords_dist.push(u_dist);
        self.v_coords_dist.push(v_dist);
    }

    pub fn len(&self) -> usize {
        self.frames.len()
    }

    pub fn is_empty(&self) -> bool {
        self.frames.is_empty()
    }

    pub fn has_distorted(&self) -> bool {
        !self.u_coords_dist.is_empty()
    }
}

/// 3D point data for a marker (v3+).
#[derive(Debug, Clone)]
pub struct Point3dData {
    pub x: Option<f64>,
    pub y: Option<f64>,
    pub z: Option<f64>,
    pub x_lock: Option<bool>,
    pub y_lock: Option<bool>,
    pub z_lock: Option<bool>,
}

/// Camera data (v4+).
#[derive(Debug, Clone)]
pub struct CameraData {
    /// Image resolution [width, height] in pixels.
    pub resolution: [u32; 2],
    /// Film back size [width, height] in centimeters.
    pub film_back_cm: [f64; 2],
    /// Lens center offset [x, y] in centimeters.
    pub lens_center_offset_cm: [f64; 2],
    /// Per-frame focal lengths: (frame, focal_length_cm).
    pub focal_lengths: Vec<(FrameNumber, f64)>,
}

/// Scene data (v5).
#[derive(Debug, Clone)]
pub struct SceneData {
    /// 4x4 transform matrix in row-major order (16 elements).
    pub transform: [f64; 16],
}

/// Point group data (v5).
#[derive(Debug, Clone)]
pub struct PointGroupData {
    pub name: String,
    /// "CAMERA" or "OBJECT"
    pub group_type: String,
    /// Per-frame 4x4 transforms: frame_number -> [f64; 16] row-major.
    pub transforms: Vec<(FrameNumber, [f64; 16])>,
}

/// Markers are stored in this data structure.
#[derive(Debug, Clone)]
pub struct MarkersData {
    pub names: Vec<String>,
    pub frame_data: Vec<FrameData>,
    pub frame_range: FrameRange,
    /// Optional set_name per marker (v2+).
    pub set_names: Vec<Option<String>>,
    /// Optional marker IDs (v3+).
    pub ids: Vec<Option<String>>,
    /// Optional 3D data per marker (v3+).
    pub point_3d: Vec<Option<Point3dData>>,
}

impl MarkersData {
    pub fn new() -> Self {
        Self {
            names: Vec::new(),
            frame_data: Vec::new(),
            frame_range: FrameRange::empty(),
            set_names: Vec::new(),
            ids: Vec::new(),
            point_3d: Vec::new(),
        }
    }

    pub fn with_capacity(marker_count_capacity: usize) -> Self {
        Self {
            names: Vec::with_capacity(marker_count_capacity),
            frame_data: Vec::with_capacity(marker_count_capacity),
            frame_range: FrameRange::empty(),
            set_names: Vec::with_capacity(marker_count_capacity),
            ids: Vec::with_capacity(marker_count_capacity),
            point_3d: Vec::with_capacity(marker_count_capacity),
        }
    }

    pub fn push_marker(&mut self, name: String, frame_data: FrameData) {
        let frame_data_start_frame = frame_data.frame_range.start_frame;
        let frame_data_end_frame = frame_data.frame_range.end_frame;
        if frame_data_start_frame < self.frame_range.start_frame {
            self.frame_range.start_frame = frame_data_start_frame
        }
        if frame_data_end_frame > self.frame_range.end_frame {
            self.frame_range.end_frame = frame_data_end_frame;
        }

        self.names.push(name);
        self.frame_data.push(frame_data);
        self.set_names.push(None);
        self.ids.push(None);
        self.point_3d.push(None);
    }

    pub fn push_marker_full(
        &mut self,
        name: String,
        frame_data: FrameData,
        set_name: Option<String>,
        id: Option<String>,
        point_3d: Option<Point3dData>,
    ) {
        let frame_data_start_frame = frame_data.frame_range.start_frame;
        let frame_data_end_frame = frame_data.frame_range.end_frame;
        if frame_data_start_frame < self.frame_range.start_frame {
            self.frame_range.start_frame = frame_data_start_frame
        }
        if frame_data_end_frame > self.frame_range.end_frame {
            self.frame_range.end_frame = frame_data_end_frame;
        }

        self.names.push(name);
        self.frame_data.push(frame_data);
        self.set_names.push(set_name);
        self.ids.push(id);
        self.point_3d.push(point_3d);
    }

    pub fn len(&self) -> usize {
        self.names.len()
    }

    pub fn is_empty(&self) -> bool {
        self.names.is_empty()
    }
}

/// File format information.
#[derive(Debug, Clone)]
pub struct FileInfo {
    pub version: UVTrackFormatVersion,
    pub marker_undistorted: bool,
    pub marker_distorted: bool,
    pub bundle_positions: bool,
    pub camera: Option<CameraData>,
    pub scene: Option<SceneData>,
    pub point_group: Option<PointGroupData>,
}

impl FileInfo {
    pub fn for_v1() -> Self {
        Self {
            version: UVTrackFormatVersion::Version1,
            marker_undistorted: true,
            marker_distorted: false,
            bundle_positions: false,
            camera: None,
            scene: None,
            point_group: None,
        }
    }
}
