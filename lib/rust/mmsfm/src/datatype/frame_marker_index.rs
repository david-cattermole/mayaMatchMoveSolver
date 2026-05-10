//
// Copyright (C) 2026 David Cattermole.
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

//! Per-frame marker index with UV coordinates.
//!
//! [`FrameMarkerIndex`] maps frame positions to the markers visible
//! in each frame, together with their image-space (u, v)
//! coordinates. It uses a flat CSR-style (Compressed Sparse Row)
//! memory layout so that per-frame marker data is contiguous in
//! memory and intersection between two frames is an O(M) merge pass
//! on sorted, contiguous slices.

#[derive(Debug, Clone, Copy)]
struct Entry {
    marker_idx: usize,
    u: f32,
    v: f32,
}

/// Per-frame marker observations with UV coordinates.
///
/// Uses flat CSR-style storage:
///
/// `data[frame_offsets[i]..frame_offsets[i+1]]` contains all entries
/// for frame `i`, sorted by `marker_idx`.
///
/// Build with [`FrameMarkerIndexBuilder`].
#[derive(Debug, Clone)]
pub struct FrameMarkerIndex {
    /// Frame offsets into `data`.  Length is `num_frames + 1`.
    /// Frame `i`'s slice is `data[frame_offsets[i]..frame_offsets[i+1]]`.
    frame_offsets: Vec<usize>,
    /// Flat `(marker_idx, u, v)` entries; frames are concatenated and sorted
    /// by `marker_idx` within each frame.
    data: Vec<Entry>,
}

impl FrameMarkerIndex {
    /// Number of frames this index covers.
    pub fn num_frames(&self) -> usize {
        self.frame_offsets.len().saturating_sub(1)
    }

    /// Total number of observations across all frames.
    pub fn total_observations(&self) -> usize {
        self.data.len()
    }

    /// Returns `true` if no markers are visible in `frame_idx`.
    pub fn is_empty(&self, frame_idx: usize) -> bool {
        self.frame_offsets[frame_idx] == self.frame_offsets[frame_idx + 1]
    }

    /// Returns a slice over the raw entries for `frame_idx`.
    fn frame_slice(&self, frame_idx: usize) -> &[Entry] {
        &self.data
            [self.frame_offsets[frame_idx]..self.frame_offsets[frame_idx + 1]]
    }

    /// Copy sorted marker indices for `frame_idx` into `out_marker_indices`.
    ///
    /// The caller should pass a pre-allocated `Vec` to avoid allocation per
    /// call. `out_marker_indices` is cleared before writing.
    pub fn marker_indices(
        &self,
        frame_idx: usize,
        out_marker_indices: &mut Vec<usize>,
    ) {
        out_marker_indices.clear();
        out_marker_indices
            .extend(self.frame_slice(frame_idx).iter().map(|e| e.marker_idx));
    }

    /// Iterate `(u, v)` coordinates for all markers in `frame_idx`.
    ///
    /// Useful for computing per-frame uniformity scores.
    pub fn iter_coords(
        &self,
        frame_idx: usize,
    ) -> impl Iterator<Item = (f32, f32)> + '_ {
        self.frame_slice(frame_idx).iter().map(|e| (e.u, e.v))
    }

    /// Merge-style intersection.
    ///
    /// Fill `out_coords_a` / `out_coords_b` with paired `(u, v)` coordinates for
    /// every marker visible in both frames.
    ///
    /// `out_coords_a[k]` and `out_coords_b[k]` correspond to the same marker.
    ///
    /// The caller passes pre-allocated `Vec`s to avoid per-pair
    /// allocation.
    pub fn intersect_coords(
        &self,
        frame_a: usize,
        frame_b: usize,
        out_coords_a: &mut Vec<(f32, f32)>,
        out_coords_b: &mut Vec<(f32, f32)>,
    ) {
        out_coords_a.clear();
        out_coords_b.clear();

        let entries_a = self.frame_slice(frame_a);
        let entries_b = self.frame_slice(frame_b);

        let (mut pos_a, mut pos_b) = (0, 0);
        while pos_a < entries_a.len() && pos_b < entries_b.len() {
            let Entry {
                marker_idx: marker_id_a,
                u: u_a,
                v: v_a,
            } = entries_a[pos_a];
            let Entry {
                marker_idx: marker_id_b,
                u: u_b,
                v: v_b,
            } = entries_b[pos_b];
            match marker_id_a.cmp(&marker_id_b) {
                std::cmp::Ordering::Less => pos_a += 1,
                std::cmp::Ordering::Greater => pos_b += 1,
                std::cmp::Ordering::Equal => {
                    out_coords_a.push((u_a, v_a));
                    out_coords_b.push((u_b, v_b));
                    pos_a += 1;
                    pos_b += 1;
                }
            }
        }
    }
}

#[derive(Debug, Clone, Copy)]
struct StagingEntry {
    frame_idx: usize,
    marker_idx: usize,
    u: f32,
    v: f32,
}

/// Accumulates per-frame marker observations and builds a [`FrameMarkerIndex`].
///
/// Push all observations with [`push`](Self::push), then call
/// [`build`](Self::build) to produce the sorted, flat index.
pub struct FrameMarkerIndexBuilder {
    num_frames: usize,
    /// Unsorted staging buffer of [`StagingEntry`] values.
    staging: Vec<StagingEntry>,
}

impl FrameMarkerIndexBuilder {
    /// Create a builder for `num_frames` frames.
    pub fn new(num_frames: usize) -> Self {
        Self {
            num_frames,
            staging: Vec::new(),
        }
    }

    /// Reserve space for at least `additional` observations (optional hint).
    pub fn reserve(&mut self, additional: usize) {
        self.staging.reserve(additional);
    }

    /// Record that marker `marker_idx` is visible in `frame_idx` at `(u, v)`.
    ///
    /// `frame_idx` must be less than `num_frames`.
    pub fn push(
        &mut self,
        frame_idx: usize,
        marker_idx: usize,
        u: f32,
        v: f32,
    ) {
        debug_assert!(frame_idx < self.num_frames);
        self.staging.push(StagingEntry {
            frame_idx,
            marker_idx,
            u,
            v,
        });
    }

    /// Sort observations and produce the final [`FrameMarkerIndex`].
    pub fn build(mut self) -> FrameMarkerIndex {
        // Runs in O(N log N) where N is the number of pushed observations.

        // Sort by (frame_idx, marker_idx) so entries are grouped per frame
        // and sorted by marker within each frame.
        self.staging
            .sort_unstable_by_key(|e| (e.frame_idx, e.marker_idx));

        let num_frames = self.num_frames;

        // Compute per-frame counts for the prefix-sum pass.
        let mut counts = vec![0usize; num_frames];
        for e in &self.staging {
            counts[e.frame_idx] += 1;
        }

        // Build offsets array from counts (prefix sum).
        let mut frame_offsets = vec![0usize; num_frames + 1];
        for i in 0..num_frames {
            frame_offsets[i + 1] = frame_offsets[i] + counts[i];
        }

        // Strip frame_idx; keep (marker_idx, u, v).
        let data: Vec<Entry> = self
            .staging
            .into_iter()
            .map(|e| Entry {
                marker_idx: e.marker_idx,
                u: e.u,
                v: e.v,
            })
            .collect();

        FrameMarkerIndex {
            frame_offsets,
            data,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn build_simple() -> FrameMarkerIndex {
        let mut b = FrameMarkerIndexBuilder::new(3);
        // Frame 0: markers 1, 3, 5
        b.push(0, 1, 0.1, 0.2);
        b.push(0, 5, 0.5, 0.6);
        b.push(0, 3, 0.3, 0.4);
        // Frame 1: markers 3, 5, 7
        b.push(1, 7, 0.7, 0.8);
        b.push(1, 3, 0.31, 0.41);
        b.push(1, 5, 0.51, 0.61);
        // Frame 2: empty
        b.build()
    }

    #[test]
    fn test_num_frames() {
        let idx = build_simple();
        assert_eq!(idx.num_frames(), 3);
    }

    #[test]
    fn test_is_empty() {
        let idx = build_simple();
        assert!(!idx.is_empty(0));
        assert!(!idx.is_empty(1));
        assert!(idx.is_empty(2));
    }

    #[test]
    fn test_marker_indices_sorted() {
        let idx = build_simple();
        let mut out = Vec::new();
        idx.marker_indices(0, &mut out);
        assert_eq!(out, vec![1, 3, 5]);
        idx.marker_indices(1, &mut out);
        assert_eq!(out, vec![3, 5, 7]);
        idx.marker_indices(2, &mut out);
        assert!(out.is_empty());
    }

    #[test]
    fn test_iter_coords() {
        let idx = build_simple();
        let coords: Vec<(f32, f32)> = idx.iter_coords(0).collect();
        // Frame 0 markers in sorted order: 1, 3, 5
        assert_eq!(coords, vec![(0.1, 0.2), (0.3, 0.4), (0.5, 0.6)]);
    }

    #[test]
    fn test_intersect_coords() {
        let idx = build_simple();
        let mut out_coords_a = Vec::new();
        let mut out_coords_b = Vec::new();
        // Frame 0 intersection Frame 1 = markers {3, 5}
        idx.intersect_coords(0, 1, &mut out_coords_a, &mut out_coords_b);
        assert_eq!(out_coords_a, vec![(0.3, 0.4), (0.5, 0.6)]);
        assert_eq!(out_coords_b, vec![(0.31, 0.41), (0.51, 0.61)]);
    }

    #[test]
    fn test_intersect_disjoint() {
        let mut b = FrameMarkerIndexBuilder::new(2);
        b.push(0, 1, 0.0, 0.0);
        b.push(1, 2, 0.0, 0.0);
        let idx = b.build();
        let mut out_coords_a = Vec::new();
        let mut out_coords_b = Vec::new();
        idx.intersect_coords(0, 1, &mut out_coords_a, &mut out_coords_b);
        assert!(out_coords_a.is_empty());
        assert!(out_coords_b.is_empty());
    }

    #[test]
    fn test_total_observations() {
        let idx = build_simple();
        assert_eq!(idx.total_observations(), 6); // 3 + 3 + 0
    }

    #[test]
    fn test_reuse_output_vecs() {
        // Verify that marker_indices and intersect_coords clear out
        // before writing.
        let idx = build_simple();
        let mut out = vec![99usize; 10];
        idx.marker_indices(2, &mut out); // frame 2 is empty
        assert!(out.is_empty());

        let mut a = vec![(9.0f32, 9.0f32); 5];
        let mut b = vec![(9.0f32, 9.0f32); 5];
        idx.intersect_coords(0, 2, &mut a, &mut b); // frame 2 is empty -> no intersection
        assert!(a.is_empty());
        assert!(b.is_empty());
    }
}
