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

//! Marker observations data structure.
//!
//! This file is intended to crate a wrapper data structure that will
//! contain all the data that can be found in the
//! `lib/rust/mmio/src/uvtrack_reader.rs` file `MarkersData` struct
//! but providing a more ergonomic API, and laying-out the data in a
//! way that the incremental SfM camera solver expects.

use anyhow::Result;
use mmio::uvtrack_reader::{FrameRange, MarkersData};

use crate::datatype::{UvPoint2, UvValue};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// The index of a marker.
pub type MarkerIndex = usize;

pub type FrameNumber = u32;
pub type FrameCount = u32;

/// Efficient marker observations storage with O(1) frame lookup.
///
/// Stores marker UV coordinates in a dense 2D array format where:
/// - Rows = markers (indexed by marker_indices)
/// - Columns = frames (spanning full_frame_range)
/// - Missing observations = (NAN, NAN)
///
/// This provides O(1) lookup time vs O(n) linear search in MarkersData.
pub struct MarkerObservations {
    /// Marker indices (same as indices into MarkersData.frame_data)
    marker_indices: Vec<MarkerIndex>,

    /// Per-marker frame ranges (actual min/max frames with data)
    frame_ranges: Vec<FrameRange>,

    /// Overall frame range spanning all markers
    full_frame_range: FrameRange,

    /// Dense UV coordinate storage (row-major 2D array).
    /// Layout: [marker_0_frame_0, marker_0_frame_1, ..., marker_1_frame_0, ...]
    /// Index: marker_idx * frame_count + (frame - start_frame)
    /// Missing frames stored as (NAN, NAN)
    ///
    /// U coordinates: 0.0 = left, 1.0 = right
    /// V coordinates: 0.0 = bottom, 1.0 = top
    uv_coords: Vec<(f64, f64)>,
}

impl MarkerObservations {
    /// Create empty marker observations.
    pub fn new() -> MarkerObservations {
        MarkerObservations {
            marker_indices: Vec::new(),
            frame_ranges: Vec::new(),
            full_frame_range: FrameRange::new(0, 0),
            uv_coords: Vec::new(),
        }
    }

    /// Convert from MarkersData to dense array format.
    ///
    /// Creates a dense 2D array where each marker has entries for all frames
    /// in full_frame_range. Missing observations stored as (NAN, NAN).
    pub fn from_markers_data(markers: &MarkersData) -> Result<Self> {
        if markers.is_empty() {
            return Ok(Self::new());
        }

        let full_frame_range = markers.frame_range;
        let frame_count = full_frame_range.frame_count() as usize;
        let marker_count = markers.len();

        mm_debug_eprintln!(
            "MarkerObservations::from_markers_data: {} markers, {} frames",
            marker_count,
            frame_count
        );

        // Pre-allocate dense array
        let total_size = marker_count * frame_count;
        let mut uv_coords = vec![(f64::NAN, f64::NAN); total_size];

        let mut marker_indices = Vec::with_capacity(marker_count);
        let mut frame_ranges = Vec::with_capacity(marker_count);

        // Fill dense array from sparse MarkersData
        for (marker_idx, frame_data) in markers.frame_data.iter().enumerate() {
            marker_indices.push(marker_idx);
            frame_ranges.push(frame_data.frame_range);

            // Copy UV coords to dense array
            for (i, &frame) in frame_data.frames.iter().enumerate() {
                if frame >= full_frame_range.start_frame
                    && frame <= full_frame_range.end_frame
                {
                    let frame_offset =
                        (frame - full_frame_range.start_frame) as usize;
                    let dense_idx = marker_idx * frame_count + frame_offset;

                    uv_coords[dense_idx] =
                        (frame_data.u_coords[i], frame_data.v_coords[i]);
                }
            }
        }

        Ok(MarkerObservations {
            marker_indices,
            frame_ranges,
            full_frame_range,
            uv_coords,
        })
    }

    /// Clear all data.
    pub fn clear(&mut self) {
        self.marker_indices.clear();
        self.frame_ranges.clear();
        self.full_frame_range = FrameRange::new(0, 0);
        self.uv_coords.clear();
    }

    /// Number of markers.
    pub fn count_markers(&self) -> usize {
        self.marker_indices.len()
    }

    /// Check if empty.
    pub fn is_empty(&self) -> bool {
        self.marker_indices.is_empty()
    }

    /// Get overall frame range.
    pub fn frame_range(&self) -> FrameRange {
        self.full_frame_range
    }

    /// Get frame range for specific marker.
    pub fn marker_frame_range(
        &self,
        marker_idx: MarkerIndex,
    ) -> Option<FrameRange> {
        self.frame_ranges.get(marker_idx).copied()
    }

    /// Get UV coordinates at specific frame - O(1) lookup.
    ///
    /// Returns Some((u, v)) if marker is visible at frame, None otherwise.
    pub fn get_uv_at_frame(
        &self,
        marker_idx: MarkerIndex,
        frame: FrameNumber,
    ) -> Option<(f64, f64)> {
        if marker_idx >= self.marker_indices.len() {
            return None;
        }

        if frame < self.full_frame_range.start_frame
            || frame > self.full_frame_range.end_frame
        {
            return None;
        }

        let frame_count = self.full_frame_range.frame_count() as usize;
        let frame_offset = (frame - self.full_frame_range.start_frame) as usize;
        let dense_idx = marker_idx * frame_count + frame_offset;

        let (u, v) = self.uv_coords[dense_idx];
        if u.is_nan() || v.is_nan() {
            None
        } else {
            Some((u, v))
        }
    }

    /// Check if marker is visible at frame - O(1) check.
    pub fn is_visible(
        &self,
        marker_idx: MarkerIndex,
        frame: FrameNumber,
    ) -> bool {
        self.get_uv_at_frame(marker_idx, frame).is_some()
    }

    /// Extract UV correspondences for a frame pair - optimized version.
    ///
    /// Returns parallel arrays of UV coords for markers visible in both frames.
    /// Replaces linear search with O(1) lookups.
    pub fn extract_correspondences_for_frame_pair(
        &self,
        marker_indices: &[MarkerIndex],
        frame_a: FrameNumber,
        frame_b: FrameNumber,
    ) -> (Vec<UvPoint2<f64>>, Vec<UvPoint2<f64>>) {
        let mut uv_coords_a = Vec::new();
        let mut uv_coords_b = Vec::new();

        for &marker_idx in marker_indices {
            if let (Some((u_a, v_a)), Some((u_b, v_b))) = (
                self.get_uv_at_frame(marker_idx, frame_a),
                self.get_uv_at_frame(marker_idx, frame_b),
            ) {
                uv_coords_a.push(UvValue::point2(u_a, v_a));
                uv_coords_b.push(UvValue::point2(u_b, v_b));
            }
        }

        (uv_coords_a, uv_coords_b)
    }

    /// Iterate visible frames for a marker.
    ///
    /// Returns iterator of (frame, u, v) tuples.
    pub fn iter_visible_frames(
        &self,
        marker_idx: MarkerIndex,
    ) -> impl Iterator<Item = (FrameNumber, f64, f64)> + '_ {
        let frame_count = self.full_frame_range.frame_count() as usize;
        let start_frame = self.full_frame_range.start_frame;

        (0..frame_count).filter_map(move |frame_offset| {
            let frame = start_frame + frame_offset as u32;
            let dense_idx = marker_idx * frame_count + frame_offset;

            let (u, v) = self.uv_coords[dense_idx];
            if u.is_nan() || v.is_nan() {
                None
            } else {
                Some((frame, u, v))
            }
        })
    }

    /// Get visible frames for marker as Vec.
    pub fn get_visible_frames(
        &self,
        marker_idx: MarkerIndex,
    ) -> Vec<FrameNumber> {
        self.iter_visible_frames(marker_idx)
            .map(|(frame, _, _)| frame)
            .collect()
    }

    /// Count visible observations for marker.
    pub fn count_visible_frames(&self, marker_idx: MarkerIndex) -> usize {
        self.iter_visible_frames(marker_idx).count()
    }
}

impl Default for MarkerObservations {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use mmio::uvtrack_reader::FrameData;

    #[test]
    fn test_empty() {
        let obs = MarkerObservations::new();
        assert!(obs.is_empty());
        assert_eq!(obs.count_markers(), 0);
    }

    #[test]
    fn test_from_markers_data_basic() -> Result<()> {
        let mut markers = MarkersData::new();

        // Marker 0: frames 1, 3, 5
        let mut frame_data_0 = FrameData::new();
        frame_data_0.push(1, 0.1, 0.2, 1.0);
        frame_data_0.push(3, 0.3, 0.4, 1.0);
        frame_data_0.push(5, 0.5, 0.6, 1.0);
        markers.push_marker("marker0".to_string(), frame_data_0);

        // Marker 1: frames 2, 4
        let mut frame_data_1 = FrameData::new();
        frame_data_1.push(2, 0.7, 0.8, 1.0);
        frame_data_1.push(4, 0.9, 1.0, 1.0);
        markers.push_marker("marker1".to_string(), frame_data_1);

        let obs = MarkerObservations::from_markers_data(&markers)?;

        assert_eq!(obs.count_markers(), 2);
        let fr = obs.frame_range();
        assert_eq!(fr.start_frame, 1);
        assert_eq!(fr.end_frame, 5);

        // Check marker 0 visibility
        assert_eq!(obs.get_uv_at_frame(0, 1), Some((0.1, 0.2)));
        assert_eq!(obs.get_uv_at_frame(0, 2), None);
        assert_eq!(obs.get_uv_at_frame(0, 3), Some((0.3, 0.4)));
        assert_eq!(obs.get_uv_at_frame(0, 4), None);
        assert_eq!(obs.get_uv_at_frame(0, 5), Some((0.5, 0.6)));

        // Check marker 1 visibility
        assert_eq!(obs.get_uv_at_frame(1, 1), None);
        assert_eq!(obs.get_uv_at_frame(1, 2), Some((0.7, 0.8)));
        assert_eq!(obs.get_uv_at_frame(1, 3), None);
        assert_eq!(obs.get_uv_at_frame(1, 4), Some((0.9, 1.0)));
        assert_eq!(obs.get_uv_at_frame(1, 5), None);

        Ok(())
    }

    #[test]
    fn test_extract_correspondences() -> Result<()> {
        let mut markers = MarkersData::new();

        // Marker 0: visible in frames 1, 2
        let mut frame_data_0 = FrameData::new();
        frame_data_0.push(1, 0.1, 0.2, 1.0);
        frame_data_0.push(2, 0.3, 0.4, 1.0);
        markers.push_marker("marker0".to_string(), frame_data_0);

        // Marker 1: visible only in frame 1
        let mut frame_data_1 = FrameData::new();
        frame_data_1.push(1, 0.5, 0.6, 1.0);
        markers.push_marker("marker1".to_string(), frame_data_1);

        // Marker 2: visible in both frames
        let mut frame_data_2 = FrameData::new();
        frame_data_2.push(1, 0.7, 0.8, 1.0);
        frame_data_2.push(2, 0.9, 1.0, 1.0);
        markers.push_marker("marker2".to_string(), frame_data_2);

        let obs = MarkerObservations::from_markers_data(&markers)?;
        let marker_indices = vec![0, 1, 2];

        let (uv_a, uv_b) =
            obs.extract_correspondences_for_frame_pair(&marker_indices, 1, 2);

        // Should only get markers 0 and 2 (both visible in frames 1 and 2)
        assert_eq!(uv_a.len(), 2);
        assert_eq!(uv_b.len(), 2);

        assert_eq!(uv_a[0], UvValue::point2(0.1, 0.2)); // marker 0 @ frame 1
        assert_eq!(uv_b[0], UvValue::point2(0.3, 0.4)); // marker 0 @ frame 2

        assert_eq!(uv_a[1], UvValue::point2(0.7, 0.8)); // marker 2 @ frame 1
        assert_eq!(uv_b[1], UvValue::point2(0.9, 1.0)); // marker 2 @ frame 2

        Ok(())
    }

    #[test]
    fn test_iter_visible_frames() -> Result<()> {
        let mut markers = MarkersData::new();

        let mut frame_data = FrameData::new();
        frame_data.push(1, 0.1, 0.2, 1.0);
        frame_data.push(3, 0.3, 0.4, 1.0);
        frame_data.push(5, 0.5, 0.6, 1.0);
        markers.push_marker("marker0".to_string(), frame_data);

        let obs = MarkerObservations::from_markers_data(&markers)?;

        let visible: Vec<_> = obs.iter_visible_frames(0).collect();

        assert_eq!(visible.len(), 3);
        assert_eq!(visible[0], (1, 0.1, 0.2));
        assert_eq!(visible[1], (3, 0.3, 0.4));
        assert_eq!(visible[2], (5, 0.5, 0.6));

        Ok(())
    }
}
