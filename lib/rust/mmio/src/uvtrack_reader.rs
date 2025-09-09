//
// Copyright (C) 2025 David Cattermole.
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

//! Read UVTrack file format data from an input file or string in
//! memory.
//!
//! This supports only the version 1 .uv file format, which just uses
//! ASCII text files.
//!
//! See ./python/mmSolver/utils/loadmarker/formats/uvtrack.py for
//! details of the '.uv' file format.

use std::fs;
use std::path::Path;

use anyhow::{Context, Result};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum UVTrackError {
    #[error("Invalid file format: {0}")]
    InvalidFormat(String),

    #[error("Parse error: {0}")]
    ParseError(String),

    #[error("No points exist in file")]
    NoPoints,

    #[error("Unexpected end of data")]
    UnexpectedEOF,
}

/// UV Track format versions matching the Python implementation
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum UVTrackFormatVersion {
    /// Unknown or invalid format
    Unknown = -1,
    /// Version 1 - ASCII format
    Version1 = 1,
    /// Version 2 - JSON format
    Version2 = 2,
    /// Version 3 - JSON format with 3D data
    Version3 = 3,
    /// Version 4 - JSON format with camera data
    Version4 = 4,
    /// Version 5 - JSON format with scene and point group data
    Version5 = 5,
}

impl UVTrackFormatVersion {
    /// Convert from integer value
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

    /// Convert to integer value
    pub fn to_i32(self) -> i32 {
        self as i32
    }
}

/// Stores data for individual frames.
#[derive(Debug, Clone)]
pub struct FrameData {
    /// Frame numbers for all data points
    pub frames: Vec<i32>,
    /// U coordinates (0.0 = left, 1.0 = right)
    pub u_coords: Vec<f64>,
    /// V coordinates (0.0 = bottom, 1.0 = top)
    pub v_coords: Vec<f64>,
    /// Weights for each frame
    pub weights: Vec<f64>,
    /// Enable flags for each frame (1.0 = enabled, 0.0 = disabled)
    pub enables: Vec<f64>,
}

impl FrameData {
    pub fn new() -> Self {
        Self {
            frames: Vec::new(),
            u_coords: Vec::new(),
            v_coords: Vec::new(),
            weights: Vec::new(),
            enables: Vec::new(),
        }
    }

    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            frames: Vec::with_capacity(capacity),
            u_coords: Vec::with_capacity(capacity),
            v_coords: Vec::with_capacity(capacity),
            weights: Vec::with_capacity(capacity),
            enables: Vec::with_capacity(capacity),
        }
    }

    pub fn push(
        &mut self,
        frame: i32,
        u: f64,
        v: f64,
        weight: f64,
        enable: f64,
    ) {
        self.frames.push(frame);
        self.u_coords.push(u);
        self.v_coords.push(v);
        self.weights.push(weight);
        self.enables.push(enable);
    }

    pub fn len(&self) -> usize {
        self.frames.len()
    }

    pub fn is_empty(&self) -> bool {
        self.frames.is_empty()
    }
}

/// Markers are stored in this data structure.
#[derive(Debug, Clone)]
pub struct MarkersData {
    /// Marker names.
    pub names: Vec<String>,
    /// Frame data for each marker.
    pub frame_data: Vec<FrameData>,
}

impl MarkersData {
    pub fn new() -> Self {
        Self {
            names: Vec::new(),
            frame_data: Vec::new(),
        }
    }

    pub fn with_capacity(capacity: usize) -> Self {
        Self {
            names: Vec::with_capacity(capacity),
            frame_data: Vec::with_capacity(capacity),
        }
    }

    pub fn push_marker(&mut self, name: String, frame_data: FrameData) {
        self.names.push(name);
        self.frame_data.push(frame_data);
    }

    pub fn len(&self) -> usize {
        self.names.len()
    }

    pub fn is_empty(&self) -> bool {
        self.names.is_empty()
    }
}

/// File format information
#[derive(Debug, Clone)]
pub struct FileInfo {
    pub marker_undistorted: bool,
    pub marker_distorted: bool,
    pub bundle_positions: bool,
}

impl FileInfo {
    pub fn for_v1() -> Self {
        Self {
            marker_undistorted: true,
            marker_distorted: false,
            bundle_positions: false,
        }
    }
}

/// Parser for UVTrack v1 format.
pub struct UVTrackV1Parser;

impl UVTrackV1Parser {
    /// Parse UVTrack v1 ASCII format from a string.
    pub fn parse_string(content: &str) -> Result<(FileInfo, MarkersData)> {
        let mut lines = content.lines();

        // Read first line - number of points
        let first_line = lines.next().ok_or(UVTrackError::UnexpectedEOF)?;

        let num_points: usize = first_line.trim().parse().map_err(|e| {
            UVTrackError::ParseError(format!("Invalid number of points: {}", e))
        })?;

        if num_points < 1 {
            return Err(UVTrackError::NoPoints.into());
        }

        log::debug!("Parsing {} points", num_points);

        let mut marker_data = MarkersData::with_capacity(num_points);

        for _point_idx in 0..num_points {
            // Read marker name
            let marker_name = lines
                .next()
                .ok_or(UVTrackError::UnexpectedEOF)?
                .trim()
                .to_string();

            log::debug!("Parsing marker: {}", marker_name);

            // Read number of frames
            let num_frames_line =
                lines.next().ok_or(UVTrackError::UnexpectedEOF)?;

            let num_frames: usize =
                num_frames_line.trim().parse().map_err(|e| {
                    UVTrackError::ParseError(format!(
                        "Invalid number of frames for marker '{}': {}",
                        marker_name, e
                    ))
                })?;

            let mut frame_data = if num_frames > 0 {
                FrameData::with_capacity(num_frames)
            } else {
                FrameData::new()
            };

            if num_frames == 0 {
                log::warn!("Point has no data: marker_name={:?}", marker_name);
                marker_data.push_marker(marker_name, frame_data);
                continue;
            }

            // Parse frame data.
            for _frame_idx in 0..num_frames {
                let frame_line =
                    lines.next().ok_or(UVTrackError::UnexpectedEOF)?;

                let frame_line = frame_line.trim();
                if frame_line.is_empty() {
                    // End of data reached.
                    break;
                }

                let parts: Vec<&str> = frame_line.split_whitespace().collect();
                if parts.len() != 4 {
                    return Err(UVTrackError::InvalidFormat(format!(
                        "Expected 4 values per frame line, got {}: '{}'",
                        parts.len(),
                        frame_line
                    ))
                    .into());
                }

                let frame: i32 = parts[0].parse().map_err(|e| {
                    UVTrackError::ParseError(format!(
                        "Invalid frame number: {}",
                        e
                    ))
                })?;

                let mkr_u: f64 = parts[1].parse().map_err(|e| {
                    UVTrackError::ParseError(format!(
                        "Invalid U coordinate: {}",
                        e
                    ))
                })?;

                let mkr_v: f64 = parts[2].parse().map_err(|e| {
                    UVTrackError::ParseError(format!(
                        "Invalid V coordinate: {}",
                        e
                    ))
                })?;

                let mkr_weight: f64 = parts[3].parse().map_err(|e| {
                    UVTrackError::ParseError(format!("Invalid weight: {}", e))
                })?;

                frame_data.push(frame, mkr_u, mkr_v, mkr_weight, 1.0);
            }

            marker_data.push_marker(marker_name, frame_data);
        }

        let file_info = FileInfo::for_v1();
        Ok((file_info, marker_data))
    }

    /// Parse UVTrack v1 ASCII format from bytes
    pub fn parse_bytes(content: &[u8]) -> Result<(FileInfo, MarkersData)> {
        let content_str =
            std::str::from_utf8(content).context("Invalid UTF-8 in file")?;
        Self::parse_string(content_str)
    }
}

/// High-level file operations.
pub fn parse_v1_file<P: AsRef<Path>>(
    file_path: P,
) -> Result<(FileInfo, MarkersData)> {
    let content = fs::read_to_string(&file_path).with_context(|| {
        format!("Failed to read file: {:?}", file_path.as_ref())
    })?;
    UVTrackV1Parser::parse_string(&content)
}

/// Determine format version from file content.
pub fn determine_format_version_from_string(
    content: &str,
) -> UVTrackFormatVersion {
    let first_line = content.lines().next();

    if let Some(line) = first_line {
        // Try to parse as JSON (v2+)
        if line.trim().starts_with('{') {
            // For now, we can't distinguish between v2-v5 without parsing JSON
            return UVTrackFormatVersion::Unknown;
        }

        // Try to parse as integer (v1)
        if line.trim().parse::<i32>().is_ok() {
            return UVTrackFormatVersion::Version1;
        }
    }

    UVTrackFormatVersion::Unknown
}

/// Determine format version from file.
pub fn determine_format_version_from_file<P: AsRef<Path>>(
    file_path: P,
) -> Result<UVTrackFormatVersion> {
    let content = fs::read_to_string(&file_path)?;
    Ok(determine_format_version_from_string(&content))
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::bail;
    use anyhow::Result;
    use std::ffi::OsStr;
    use std::fs::File;
    use std::io::Read;
    use std::path::Path;
    use std::path::PathBuf;

    fn find_data_dir() -> Result<PathBuf> {
        // "<project_root>/target/debug/deps/curve_curvature-a1543a4f123cfc9f"
        let mut directory = PathBuf::from(std::env::current_exe().unwrap());

        // "<project_root>/target/debug/deps"
        assert!(directory.pop());

        // "<project_root>/target/debug"
        assert!(directory.pop());

        // "<project_root>/target"
        assert!(directory.pop());

        // "<project_root>"
        assert!(directory.pop());

        // "<project_root>/tests/data/uvtrack/"
        directory.push("tests");
        directory.push("data");
        directory.push("uvtrack");

        if directory.is_dir() {
            Ok(directory)
        } else {
            bail!("Could not find data directory {:?}.", directory)
        }
    }

    fn construct_input_file_path(
        base_dir: &Path,
        file_name: &str,
    ) -> Result<PathBuf> {
        let mut file_path = PathBuf::new();
        file_path.push(base_dir);
        file_path.push(file_name);
        if !file_path.is_file() {
            bail!("Could not find file name {:?}", file_path);
        }
        Ok(file_path)
    }

    fn read_ascii_file(file_name: &OsStr) -> Result<String> {
        let mut file = File::open(file_name)?;
        let mut buffer = String::new();
        file.read_to_string(&mut buffer)?;
        Ok(buffer)
    }

    #[test]
    fn test_parse_v1_simple() -> Result<()> {
        let content = r#"1
My Point Name
1
1 0.0 1.0 1.0
        "#;

        println!("File data:");
        println!("{}", content);

        let (file_info, markers) = UVTrackV1Parser::parse_string(content)?;

        assert!(file_info.marker_undistorted);
        assert!(!file_info.marker_distorted);
        assert_eq!(markers.len(), 1);

        assert_eq!(markers.names[0], "My Point Name");

        let frame_data = &markers.frame_data[0];
        assert_eq!(frame_data.frames[0], 1);
        assert_eq!(frame_data.u_coords[0], 0.0);
        assert_eq!(frame_data.v_coords[0], 1.0);
        assert_eq!(frame_data.weights[0], 1.0);
        assert_eq!(frame_data.enables[0], 1.0);

        Ok(())
    }

    #[test]
    fn test_parse_v1_multiple_frames() -> Result<()> {
        let content = r#"1
TestMarker
3
1001 0.25 0.75 1.0
1002 0.30 0.70 0.9
1003 0.35 0.65 0.8
        "#;

        println!("File data:");
        println!("{}", content);

        let (_, markers) = UVTrackV1Parser::parse_string(content)?;

        assert_eq!(markers.len(), 1);
        assert_eq!(markers.names[0], "TestMarker");

        let frame_data = &markers.frame_data[0];
        assert_eq!(frame_data.len(), 3);

        // Check first frame.
        assert_eq!(frame_data.frames[0], 1001);
        assert_eq!(frame_data.u_coords[0], 0.25);
        assert_eq!(frame_data.v_coords[0], 0.75);
        assert_eq!(frame_data.weights[0], 1.0);

        // Check last frame.
        assert_eq!(frame_data.frames[2], 1003);
        assert_eq!(frame_data.u_coords[2], 0.35);
        assert_eq!(frame_data.v_coords[2], 0.65);
        assert_eq!(frame_data.weights[2], 0.8);

        Ok(())
    }

    #[test]
    fn test_parse_v1_occluded_frames() -> Result<()> {
        let content = r#"1
TestMarker
2
1001 0.25 0.75 1.0
1003 0.35 0.65 0.8
        "#;

        println!("File data:");
        println!("{}", content);

        let (_, markers) = UVTrackV1Parser::parse_string(content)?;

        let frame_data = &markers.frame_data[0];
        // Should not include frame 1002 because it's occluded.
        assert_eq!(frame_data.len(), 2);

        Ok(())
    }

    #[test]
    fn test_parse_v1_corners() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path =
            construct_input_file_path(&data_dir, "loadmarker_corners.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        println!("File data:");
        println!("{}", content);

        let (_, markers) = UVTrackV1Parser::parse_string(&content)?;

        assert_eq!(markers.len(), 4);
        assert_eq!(markers.names[0], "TopLeft");
        assert_eq!(markers.names[1], "TopRight");
        assert_eq!(markers.names[2], "BottomLeft");
        assert_eq!(markers.names[3], "BottomRight");

        let frame_data_top_left = &markers.frame_data[0];
        let frame_data_top_right = &markers.frame_data[1];
        let frame_data_bottom_left = &markers.frame_data[2];
        let frame_data_bottom_right = &markers.frame_data[3];
        assert_eq!(frame_data_top_left.len(), 1);
        assert_eq!(frame_data_top_right.len(), 1);
        assert_eq!(frame_data_bottom_left.len(), 1);
        assert_eq!(frame_data_bottom_right.len(), 1);

        assert_eq!(frame_data_top_left.frames[0], 1);
        assert_eq!(frame_data_top_left.u_coords[0], 0.0);
        assert_eq!(frame_data_top_left.v_coords[0], 1.0);
        assert_eq!(frame_data_top_left.weights[0], 1.0);

        assert_eq!(frame_data_top_right.frames[0], 1);
        assert_eq!(frame_data_top_right.u_coords[0], 1.0);
        assert_eq!(frame_data_top_right.v_coords[0], 1.0);
        assert_eq!(frame_data_top_right.weights[0], 1.0);

        assert_eq!(frame_data_bottom_left.frames[0], 1);
        assert_eq!(frame_data_bottom_left.u_coords[0], 0.0);
        assert_eq!(frame_data_bottom_left.v_coords[0], 0.0);
        assert_eq!(frame_data_bottom_left.weights[0], 1.0);

        assert_eq!(frame_data_bottom_right.frames[0], 1);
        assert_eq!(frame_data_bottom_right.u_coords[0], 1.0);
        assert_eq!(frame_data_bottom_right.v_coords[0], 0.0);
        assert_eq!(frame_data_bottom_right.weights[0], 1.0);

        Ok(())
    }

    #[test]
    fn test_parse_v1_multiple_markers() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path = construct_input_file_path(&data_dir, "test_v1.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        println!("File data:");
        println!("{}", content);

        let (_, markers) = UVTrackV1Parser::parse_string(&content)?;

        assert_eq!(markers.len(), 2);
        assert_eq!(markers.names[0], "12");
        assert_eq!(markers.names[1], "25");

        let marker_12_frame_data = &markers.frame_data[0];
        let marker_25_frame_data = &markers.frame_data[1];
        assert_eq!(marker_12_frame_data.len(), 17);
        assert_eq!(marker_25_frame_data.len(), 36);

        // Check first frame of Marker "12".
        assert_eq!(marker_12_frame_data.frames[0], 216);
        assert_eq!(marker_12_frame_data.u_coords[0], 0.134825273667837);
        assert_eq!(marker_12_frame_data.v_coords[0], -0.022942275722851);
        assert_eq!(marker_12_frame_data.weights[0], 1.0);

        // Check last frame of Marker "12".
        assert_eq!(marker_12_frame_data.frames[16], 232);
        assert_eq!(marker_12_frame_data.u_coords[16], 0.185812798577091);
        assert_eq!(marker_12_frame_data.v_coords[16], 0.083019738470496);
        assert_eq!(marker_12_frame_data.weights[16], 1.0);

        // Check first frame of Marker "25".
        assert_eq!(marker_25_frame_data.frames[0], 197);
        assert_eq!(marker_25_frame_data.u_coords[0], 0.064565437585185);
        assert_eq!(marker_25_frame_data.v_coords[0], -0.019454388413890);
        assert_eq!(marker_25_frame_data.weights[0], 1.0);

        // Check last frame of Marker "25".
        assert_eq!(marker_25_frame_data.frames[35], 232);
        assert_eq!(marker_25_frame_data.u_coords[35], 0.121295453993212);
        assert_eq!(marker_25_frame_data.v_coords[35], 0.170159006068965);
        assert_eq!(marker_25_frame_data.weights[35], 1.0);

        Ok(())
    }

    #[test]
    fn test_determine_format_version_v1() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path = construct_input_file_path(&data_dir, "test_v1.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        println!("File data:");
        println!("{}", content);

        let version = determine_format_version_from_string(&content);
        assert_eq!(version, UVTrackFormatVersion::Version1);

        Ok(())
    }

    #[test]
    fn test_determine_format_version_v3() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path = construct_input_file_path(&data_dir, "test_v3.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        println!("File data:");
        println!("{}", content);

        let version = determine_format_version_from_string(&content);
        // Currently, we do not support reading v3 format.
        assert_eq!(version, UVTrackFormatVersion::Unknown);

        Ok(())
    }
}
