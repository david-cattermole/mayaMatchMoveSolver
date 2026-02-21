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

//! Parser for UVTrack v1 (ASCII) format.

use anyhow::{Context, Result};

use super::types::*;

/// Parser for UVTrack v1 format.
pub struct UVTrackV1Parser;

impl UVTrackV1Parser {
    /// Parse UVTrack v1 ASCII format from a string.
    pub fn parse_string(content: &str) -> Result<(FileInfo, MarkersData)> {
        let mut lines = content.lines();

        let first_line = lines.next().ok_or(UVTrackError::UnexpectedEOF)?;

        let num_points: usize = first_line.trim().parse().map_err(|e| {
            UVTrackError::ParseError(format!("Invalid number of points: {e}"))
        })?;

        if num_points < 1 {
            return Err(UVTrackError::NoPoints.into());
        }

        log::debug!("Parsing {} points", num_points);

        let mut marker_data = MarkersData::with_capacity(num_points);

        for _point_idx in 0..num_points {
            let marker_name = lines
                .next()
                .ok_or(UVTrackError::UnexpectedEOF)?
                .trim()
                .to_string();

            log::debug!("Parsing marker: {}", marker_name);

            let num_frames_line =
                lines.next().ok_or(UVTrackError::UnexpectedEOF)?;

            let num_frames: usize =
                num_frames_line.trim().parse().map_err(|e| {
                    UVTrackError::ParseError(format!(
                        "Invalid number of frames for marker '{marker_name}': {e}",
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

            for _frame_idx in 0..num_frames {
                let frame_line =
                    lines.next().ok_or(UVTrackError::UnexpectedEOF)?;

                let frame_line = frame_line.trim();
                if frame_line.is_empty() {
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

                let frame: FrameNumber = parts[0].parse().map_err(|e| {
                    UVTrackError::ParseError(format!(
                        "Invalid frame number: {e}",
                    ))
                })?;

                let mkr_u: f64 = parts[1].parse().map_err(|e| {
                    UVTrackError::ParseError(format!(
                        "Invalid U coordinate: {e}",
                    ))
                })?;

                let mkr_v: f64 = parts[2].parse().map_err(|e| {
                    UVTrackError::ParseError(format!(
                        "Invalid V coordinate: {e}",
                    ))
                })?;

                let mkr_weight: f64 = parts[3].parse().map_err(|e| {
                    UVTrackError::ParseError(format!("Invalid weight: {e}"))
                })?;

                frame_data.push(frame, mkr_u, mkr_v, mkr_weight);
            }

            marker_data.push_marker(marker_name, frame_data);
        }

        let file_info = FileInfo::for_v1();
        Ok((file_info, marker_data))
    }

    /// Parse UVTrack v1 ASCII format from bytes.
    pub fn parse_bytes(content: &[u8]) -> Result<(FileInfo, MarkersData)> {
        let content_str =
            std::str::from_utf8(content).context("Invalid UTF-8 in file.")?;
        Self::parse_string(content_str)
    }
}
