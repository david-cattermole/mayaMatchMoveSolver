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

//! Read UVTrack file format data from an input file or string in
//! memory.
//!
//! Supports version 1 (ASCII) and versions 2-5 (JSON) .uv file
//! formats.
//!
//! See ./python/mmSolver/utils/loadmarker/formats/uvtrack.py for
//! details of the '.uv' file format.

mod types;
mod v1_parser;
mod v2_v5_parser;

pub use types::*;
pub use v1_parser::UVTrackV1Parser;

use std::fs;
use std::path::Path;

use anyhow::{Context, Result};

use crate::json_parser::parse_json;

/// High-level: parse a v1 file. Kept for backwards compatibility.
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
        // Try JSON (v2+)
        if line.trim().starts_with('{') {
            if let Ok(json) = parse_json(content) {
                return v2_v5_parser::determine_format_version_from_json(&json);
            }
            return UVTrackFormatVersion::Unknown;
        }

        // Try integer (v1)
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

/// Parse any UV track file (v1-v5), auto-detecting the version.
pub fn parse_file<P: AsRef<Path>>(
    file_path: P,
) -> Result<(FileInfo, MarkersData)> {
    let content = fs::read_to_string(&file_path).with_context(|| {
        format!("Failed to read file: {:?}", file_path.as_ref())
    })?;
    parse_string(&content)
}

/// Parse any UV track string (v1-v5), auto-detecting the version.
pub fn parse_string(content: &str) -> Result<(FileInfo, MarkersData)> {
    let version = determine_format_version_from_string(content);
    match version {
        UVTrackFormatVersion::Version1 => {
            UVTrackV1Parser::parse_string(content)
        }
        UVTrackFormatVersion::Version2
        | UVTrackFormatVersion::Version3
        | UVTrackFormatVersion::Version4
        | UVTrackFormatVersion::Version5 => {
            v2_v5_parser::parse_json_string(content)
        }
        _ => Err(UVTrackError::InvalidFormat(
            "Could not determine UV track file version".to_string(),
        )
        .into()),
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::{bail, Result};
    use std::fs::File;
    use std::io::Read;
    use std::path::PathBuf;

    fn find_data_dir() -> Result<PathBuf> {
        let mut directory = PathBuf::from(std::env::current_exe().unwrap());
        assert!(directory.pop());
        assert!(directory.pop());
        assert!(directory.pop());
        assert!(directory.pop());
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
        base_dir: &std::path::Path,
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

    fn read_ascii_file(file_name: &std::ffi::OsStr) -> Result<String> {
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

        let (_, markers) = UVTrackV1Parser::parse_string(content)?;

        assert_eq!(markers.len(), 1);
        let frame_data = &markers.frame_data[0];
        assert_eq!(frame_data.len(), 3);
        assert_eq!(frame_data.frames[0], 1001);
        assert_eq!(frame_data.frames[2], 1003);

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

        let (_, markers) = UVTrackV1Parser::parse_string(content)?;
        let frame_data = &markers.frame_data[0];
        assert_eq!(frame_data.len(), 2);

        Ok(())
    }

    #[test]
    fn test_parse_v1_corners() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path =
            construct_input_file_path(&data_dir, "loadmarker_corners.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        let (_, markers) = UVTrackV1Parser::parse_string(&content)?;

        assert_eq!(markers.len(), 4);
        assert_eq!(markers.names[0], "TopLeft");
        assert_eq!(markers.names[1], "TopRight");
        assert_eq!(markers.names[2], "BottomLeft");
        assert_eq!(markers.names[3], "BottomRight");

        let frame_data_top_left = &markers.frame_data[0];
        assert_eq!(frame_data_top_left.frames[0], 1);
        assert_eq!(frame_data_top_left.u_coords[0], 0.0);
        assert_eq!(frame_data_top_left.v_coords[0], 1.0);
        assert_eq!(frame_data_top_left.weights[0], 1.0);

        Ok(())
    }

    #[test]
    fn test_parse_v1_multiple_markers() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path = construct_input_file_path(&data_dir, "test_v1.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        let (_, markers) = UVTrackV1Parser::parse_string(&content)?;

        assert_eq!(markers.len(), 2);
        assert_eq!(markers.names[0], "12");
        assert_eq!(markers.names[1], "25");

        let marker_12_frame_data = &markers.frame_data[0];
        let marker_25_frame_data = &markers.frame_data[1];
        assert_eq!(marker_12_frame_data.len(), 17);
        assert_eq!(marker_25_frame_data.len(), 36);

        assert_eq!(marker_12_frame_data.frames[0], 216);
        assert_eq!(marker_12_frame_data.u_coords[0], 0.134825273667837);

        Ok(())
    }

    #[test]
    fn test_determine_format_version_v1() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path = construct_input_file_path(&data_dir, "test_v1.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        let version = determine_format_version_from_string(&content);
        assert_eq!(version, UVTrackFormatVersion::Version1);

        Ok(())
    }

    #[test]
    fn test_determine_format_version_v2() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path = construct_input_file_path(&data_dir, "stA.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        let version = determine_format_version_from_string(&content);
        assert_eq!(version, UVTrackFormatVersion::Version2);

        Ok(())
    }

    #[test]
    fn test_determine_format_version_v3() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path = construct_input_file_path(&data_dir, "test_v3.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        let version = determine_format_version_from_string(&content);
        assert_eq!(version, UVTrackFormatVersion::Version3);

        Ok(())
    }

    #[test]
    fn test_determine_format_version_v4() -> Result<()> {
        let data_dir = find_data_dir()?;
        let in_file_path = construct_input_file_path(&data_dir, "test_v4.uv")?;
        let content = read_ascii_file(&in_file_path.into_os_string())?;

        let version = determine_format_version_from_string(&content);
        assert_eq!(version, UVTrackFormatVersion::Version4);

        Ok(())
    }

    #[test]
    fn test_parse_file_auto_detect_v1() -> Result<()> {
        let data_dir = find_data_dir()?;
        let path = construct_input_file_path(&data_dir, "test_v1.uv")?;

        let (file_info, markers) = parse_file(&path)?;
        assert_eq!(file_info.version, UVTrackFormatVersion::Version1);
        assert_eq!(markers.len(), 2);

        Ok(())
    }

    #[test]
    fn test_parse_file_auto_detect_v2() -> Result<()> {
        let data_dir = find_data_dir()?;
        let path = construct_input_file_path(&data_dir, "stA.uv")?;

        let (file_info, markers) = parse_file(&path)?;
        assert_eq!(file_info.version, UVTrackFormatVersion::Version2);
        assert_eq!(markers.len(), 14);

        Ok(())
    }
}
