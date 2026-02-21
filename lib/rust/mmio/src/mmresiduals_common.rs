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

//! Common data types for the `.mmresiduals` file format.

/// Per-frame, per-marker reprojection residual data.
#[derive(Debug, Clone, PartialEq)]
pub struct MmResidualsData {
    pub marker_names: Vec<String>,
    pub frame_numbers: Vec<i64>,
    pub image_width: Option<i64>,
    pub image_height: Option<i64>,
    pub statistics: MmResidualsStatistics,
    pub per_frame_per_marker: Vec<MmResidualsFrameData>,
}

/// Summary statistics for residual errors.
#[derive(Debug, Clone, PartialEq)]
pub struct MmResidualsStatistics {
    pub mean: f64,
    pub median: f64,
    pub std_dev: f64,
    pub min: f64,
    pub max: f64,
    pub count: usize,
}

/// Residual errors for a single frame.
#[derive(Debug, Clone, PartialEq)]
pub struct MmResidualsFrameData {
    pub frame: i64,
    /// One error per marker. NaN if the marker is not visible.
    pub errors: Vec<f64>,
}
