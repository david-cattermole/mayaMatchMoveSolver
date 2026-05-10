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

//! Dense Frame Graph (AKA "View Graph") for Structure from Motion (SfM) pipelines.
//!
//! Uses triangular matrix storage for O(1) access. Supports initial pair
//! selection and next-best-frame finding for incremental reconstruction.

use std::collections::{BTreeSet, HashSet};

use super::constants::RECOMENDED_MARKERS_FOR_PNP;
use super::constants::UNIFORMITY_GRID_SIZE_MAX;
use super::frame_score::calculate_uniformity;

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Unique identifier for a frame/image in the reconstruction.
pub type FrameId = u32;

/// Geometric relationship data between two frames.
///
/// Sentinel values: `f32` fields use `NaN`, `i32` fields use `0`.
#[derive(Debug, Clone, Copy)]
pub struct FrameEdge {
    num_observations: i32,
    parallax: f32,
}

impl FrameEdge {
    /// Creates a new edge with all metrics specified.
    pub fn new(num_observations: i32, parallax: f32) -> Self {
        Self {
            num_observations,
            parallax,
        }
    }

    /// Returns the observation count if present (non-zero).
    pub fn num_observations(&self) -> Option<i32> {
        if self.num_observations == 0 {
            None
        } else {
            Some(self.num_observations)
        }
    }

    /// Returns the parallax angle if present (non-NaN).
    pub fn parallax(&self) -> Option<f32> {
        if self.parallax.is_nan() {
            None
        } else {
            Some(self.parallax)
        }
    }

    /// Returns true if this edge has valid data (not a sentinel).
    pub fn is_valid(&self) -> bool {
        self.num_observations != 0
    }
}

impl Default for FrameEdge {
    fn default() -> Self {
        Self {
            num_observations: 0,
            parallax: f32::NAN,
        }
    }
}

/// Counts elements common to two sorted slices using a merge pass.
///
/// Both `a` and `b` must be sorted in ascending order.
fn sorted_intersection_count(a: &[usize], b: &[usize]) -> usize {
    let (mut i, mut j) = (0, 0);
    let mut count = 0;
    while i < a.len() && j < b.len() {
        match a[i].cmp(&b[j]) {
            std::cmp::Ordering::Less => i += 1,
            std::cmp::Ordering::Greater => j += 1,
            std::cmp::Ordering::Equal => {
                count += 1;
                i += 1;
                j += 1;
            }
        }
    }
    count
}

/// A dense frame graph using triangular matrix storage.
///
/// Memory usage is `N*(N-1)/2 * sizeof(FrameEdge)` bytes plus per-frame
/// marker index lists.
pub struct FrameGraph {
    num_frames: usize,
    edges: Vec<FrameEdge>,
    uniformity: Vec<f32>,
    /// Sorted marker indices visible in each frame.
    frame_markers: Vec<Vec<usize>>,
}

impl FrameGraph {
    /// Creates a new frame graph with a fixed number of frames.
    ///
    /// All edges are initialized to sentinel (invalid) state.
    ///
    /// # Panics
    /// Panics if `num_frames` is 0 or 1.
    pub fn new(num_frames: usize) -> Self {
        assert!(num_frames >= 2, "Frame graph requires at least 2 frames");
        let num_edges = num_frames * (num_frames - 1) / 2;
        Self {
            num_frames,
            edges: vec![FrameEdge::default(); num_edges],
            uniformity: vec![f32::NAN; num_frames],
            frame_markers: vec![Vec::new(); num_frames],
        }
    }

    /// Returns the number of frames (nodes) in the graph.
    pub fn num_frames(&self) -> usize {
        self.num_frames
    }

    /// Returns the number of valid (non-sentinel) edges.
    pub fn num_valid_edges(&self) -> usize {
        self.edges.iter().filter(|e| e.is_valid()).count()
    }

    /// Computes the storage index for an edge between frames `i` and `j`.
    #[inline]
    fn edge_index(&self, i: FrameId, j: FrameId) -> usize {
        let (lo, hi) = if i < j { (i, j) } else { (j, i) };
        let lo = lo as usize;
        let hi = hi as usize;
        debug_assert!(hi < self.num_frames, "Frame ID out of bounds");
        debug_assert!(lo != hi, "Self-edges are not allowed");
        lo * (2 * self.num_frames - lo - 1) / 2 + (hi - lo - 1)
    }

    /// Sets the edge data between two frames.
    pub fn set_edge(&mut self, i: FrameId, j: FrameId, data: FrameEdge) {
        let idx = self.edge_index(i, j);
        self.edges[idx] = data;
    }

    /// Retrieves the edge data between two frames.
    pub fn get_edge(&self, i: FrameId, j: FrameId) -> &FrameEdge {
        let idx = self.edge_index(i, j);
        &self.edges[idx]
    }

    /// Returns true if a valid edge exists between two frames.
    pub fn has_edge(&self, i: FrameId, j: FrameId) -> bool {
        self.get_edge(i, j).is_valid()
    }

    /// Sets the uniformity score for a frame.
    pub fn set_uniformity(&mut self, frame: FrameId, uniformity: f32) {
        if (frame as usize) < self.num_frames {
            self.uniformity[frame as usize] = uniformity;
        }
    }

    /// Gets the uniformity score for a frame.
    ///
    /// Returns `None` if the score is `NaN` or the frame ID is out of bounds.
    pub fn get_uniformity(&self, frame: FrameId) -> Option<f32> {
        self.uniformity
            .get(frame as usize)
            .copied()
            .filter(|u| !u.is_nan())
    }

    /// Calculates and sets the uniformity for a frame using the provided 2D points.
    pub fn calculate_and_set_uniformity(
        &mut self,
        frame: FrameId,
        points_x: &[f32],
        points_y: &[f32],
    ) {
        let grid_size = UNIFORMITY_GRID_SIZE_MAX as usize;
        let mut count_bins = vec![0u16; grid_size * grid_size];
        let uniformity = calculate_uniformity(
            points_x,
            points_y,
            points_x.len(),
            &mut count_bins,
        );
        self.set_uniformity(frame, uniformity);
    }

    /// Sets the sorted marker indices visible in a frame.
    ///
    /// `markers` **must** be sorted in ascending order.
    pub fn set_frame_markers(&mut self, frame: FrameId, markers: Vec<usize>) {
        if (frame as usize) < self.num_frames {
            debug_assert!(
                markers.windows(2).all(|w| w[0] < w[1]),
                "frame_markers must be sorted"
            );
            self.frame_markers[frame as usize] = markers;
        }
    }

    /// Returns `true` if any frame has marker data populated.
    pub fn has_marker_data(&self) -> bool {
        self.frame_markers.iter().any(|m| !m.is_empty())
    }

    /// Iterates over all valid edges with their frame IDs.
    pub fn iter_edges(
        &self,
    ) -> impl Iterator<Item = (FrameId, FrameId, &FrameEdge)> {
        let n = self.num_frames;
        (0..n as FrameId).flat_map(move |i| {
            ((i + 1)..n as FrameId).filter_map(move |j| {
                let idx = self.edge_index(i, j);
                let edge = &self.edges[idx];
                if edge.is_valid() {
                    Some((i, j, edge))
                } else {
                    None
                }
            })
        })
    }

    /// Iterates over all neighbors of a given frame that have valid edges.
    pub fn neighbors(
        &self,
        frame: FrameId,
    ) -> impl Iterator<Item = (FrameId, &FrameEdge)> {
        let n = self.num_frames as FrameId;
        let v = frame;
        (0..n).filter_map(move |other| {
            if other == v {
                return None;
            }
            let edge = self.get_edge(v, other);
            if edge.is_valid() {
                Some((other, edge))
            } else {
                None
            }
        })
    }

    /// Print diagnostic metrics for the graph structure.
    pub fn print_metrics(&self, label: &str) {
        let n = self.num_frames;

        // Degree distribution.
        let mut degrees: Vec<usize> = (0..n as FrameId)
            .map(|v| self.neighbors(v).count())
            .collect();
        degrees.sort_unstable();

        let total_edges = self.num_valid_edges();
        let isolated = degrees.iter().filter(|&&d| d == 0).count();
        let leaves = degrees.iter().filter(|&&d| d == 1).count();
        let internal = degrees.iter().filter(|&&d| d >= 2).count();

        let min_deg = degrees.first().copied().unwrap_or(0);
        let max_deg = degrees.last().copied().unwrap_or(0);
        let mean_deg = if n > 0 {
            degrees.iter().sum::<usize>() as f64 / n as f64
        } else {
            0.0
        };
        let median_deg = if n > 0 { degrees[n / 2] } else { 0 };

        // Uniformity coverage.
        let valid_uniformity = (0..n as FrameId)
            .filter(|&v| self.get_uniformity(v).is_some())
            .count();
        let zero_uniformity = (0..n as FrameId)
            .filter(|&v| self.get_uniformity(v) == Some(0.0))
            .count();

        // Component structure.
        let all_vertices: Vec<FrameId> = (0..n as FrameId).collect();
        let components =
            Self::find_components(&all_vertices, |a, b| self.has_edge(a, b));
        let component_sizes: Vec<usize> =
            components.iter().map(|c| c.len()).collect();
        let largest = component_sizes.iter().max().copied().unwrap_or(0);

        mm_eprintln_debug!(
            "    [{}] {} vertices, {} edges",
            label,
            n,
            total_edges
        );
        mm_eprintln_debug!(
            "    [{}] degree: min={}, max={}, mean={:.1}, median={}",
            label,
            min_deg,
            max_deg,
            mean_deg,
            median_deg
        );
        mm_eprintln_debug!(
            "    [{}] isolated={}, leaves={}, internal={}",
            label,
            isolated,
            leaves,
            internal
        );
        mm_eprintln_debug!(
            "    [{}] uniformity: {}/{} valid, {} zero",
            label,
            valid_uniformity,
            n,
            zero_uniformity
        );
        mm_eprintln_debug!(
            "    [{}] components: {}, largest={}",
            label,
            components.len(),
            largest
        );
    }

    /// Debug: sample some edge heuristic scores.
    pub fn print_edge_heuristic(&self, first_n_edges: usize) {
        let mut positive_heuristic = 0usize;
        let mut zero_heuristic = 0usize;
        let mut negative_heuristic = 0usize;
        let mut sample_scores = Vec::new();
        for (i, j, edge) in self.iter_edges() {
            let observation_count = edge.num_observations().unwrap_or(0);
            let parallax = edge.parallax().unwrap_or(0.0);
            let uniformity_i = self.get_uniformity(i);
            let uniformity_j = self.get_uniformity(j);
            // Replicate heuristic logic.
            let uniformity_value_i = uniformity_i.unwrap_or(0.0).max(0.01);
            let uniformity_value_j = uniformity_j.unwrap_or(0.0).max(0.01);
            let score = if (observation_count as usize) < first_n_edges {
                -1.0
            } else {
                observation_count as f32
                    * uniformity_value_i
                    * uniformity_value_j
                    * parallax
            };
            if score > 0.0 {
                positive_heuristic += 1;
            } else if score == 0.0 {
                zero_heuristic += 1;
            } else {
                negative_heuristic += 1;
            }
            if sample_scores.len() < first_n_edges {
                sample_scores.push((
                    i,
                    j,
                    observation_count,
                    parallax,
                    uniformity_i,
                    uniformity_j,
                    score,
                ));
            }
        }

        mm_eprintln_debug!(
            "  Edge heuristic scores: {} positive, {} zero, {} negative",
            positive_heuristic,
            zero_heuristic,
            negative_heuristic
        );
        for (
            i,
            j,
            observation_count,
            parallax,
            uniformity_value_i,
            uniformity_value_j,
            sc,
        ) in &sample_scores
        {
            mm_eprintln_debug!(
                "    edge({},{}): observation_count={}, parallax={:.4}, uniformity=({:?},{:?}), score={:.6}",
                i, j, observation_count, parallax, uniformity_value_i, uniformity_value_j, sc
            );
        }
    }

    /// Score an edge by combining observation count, uniformity, and parallax.
    ///
    /// Returns -1.0 for invalid edges or edges with insufficient observations.
    fn edge_heuristic(&self, i: FrameId, j: FrameId, edge: &FrameEdge) -> f32 {
        let observation_count: usize =
            edge.num_observations().unwrap_or(0) as usize;
        let parallax = edge.parallax().unwrap_or(0.0);
        let uniformity_i = self.get_uniformity(i).unwrap_or(0.0);
        let uniformity_j = self.get_uniformity(j).unwrap_or(0.0);
        let uniformity = uniformity_i * uniformity_j;

        // Filter out pairs with insufficient data.
        if observation_count < RECOMENDED_MARKERS_FOR_PNP {
            return -1.0;
        }

        (observation_count as f32) * uniformity * parallax
    }

    /// Prim's Maximum Spanning Tree using a caller-supplied edge weight function.
    ///
    /// Shared implementation for both observation-count and parallax variants.
    /// Returns an empty graph if there are no valid edges or fewer than 2 frames.
    fn maximum_spanning_tree_impl<F>(&self, weight_fn: F) -> Self
    where
        F: Fn(&FrameEdge) -> Option<f32>,
    {
        let n = self.num_frames;
        let mut mst = FrameGraph::new(n);

        if n < 2 {
            return mst;
        }

        mst.uniformity.copy_from_slice(&self.uniformity);
        mst.frame_markers = self.frame_markers.clone();

        // Start from the highest-degree vertex.
        let mut start: FrameId = 0;
        let mut start_degree = 0usize;
        for v in 0..n as FrameId {
            let deg = self.neighbors(v).count();
            if deg > start_degree {
                start_degree = deg;
                start = v;
            }
        }

        if start_degree == 0 {
            return mst;
        }

        let mut in_mst = vec![false; n];
        // best_weight[j] = (best score to reach j from MST, source frame).
        let mut best_weight: Vec<(f32, FrameId)> = vec![(0.0, 0); n];

        in_mst[start as usize] = true;

        for j in 0..n {
            if j == start as usize {
                continue;
            }
            let edge = self.get_edge(start, j as FrameId);
            if let Some(w) = weight_fn(edge) {
                if w > best_weight[j].0 {
                    best_weight[j] = (w, start);
                }
            }
        }

        for _ in 0..(n - 1) {
            let mut best_score = 0.0f32;
            let mut best_node = None;

            for (node, &(score, _)) in best_weight.iter().enumerate() {
                if !in_mst[node] && score > best_score {
                    best_score = score;
                    best_node = Some(node);
                }
            }

            let Some(new_node) = best_node else {
                break;
            };

            in_mst[new_node] = true;
            let (_, source) = best_weight[new_node];
            let edge_data = *self.get_edge(source, new_node as FrameId);
            mst.set_edge(source, new_node as FrameId, edge_data);

            for j in 0..n {
                if in_mst[j] {
                    continue;
                }
                let edge = self.get_edge(new_node as FrameId, j as FrameId);
                if let Some(w) = weight_fn(edge) {
                    if w > best_weight[j].0 {
                        best_weight[j] = (w, new_node as FrameId);
                    }
                }
            }
        }

        mst
    }

    /// Computes a Maximum Spanning Tree using observation count as the edge weight.
    ///
    /// Unlike `maximum_spanning_tree()`, only requires valid edges with observation
    /// counts, making it suitable for skeleton frame selection where zero-parallax
    /// frames should still be connected.
    pub fn maximum_spanning_tree_by_observations(&self) -> Self {
        self.maximum_spanning_tree_impl(|e| {
            e.num_observations().map(|n| n as f32)
        })
    }

    /// Computes a Maximum Spanning Tree using `parallax * ln(1 + observations)` as weight.
    ///
    /// Prefers edges with high parallax AND many observations, selecting geometrically
    /// diverse frames over temporally adjacent (near-zero-parallax) frames.
    /// Only edges with parallax > 0 contribute non-zero weight; falls back to
    /// `maximum_spanning_tree_by_observations()` if no such edges exist.
    pub fn maximum_spanning_tree_by_parallax(&self) -> Self {
        // Fall back to observation-count MST when no parallax data is available.
        let has_parallax = self
            .edges
            .iter()
            .any(|e| e.parallax().map_or(false, |p| p > 0.0));
        if !has_parallax {
            return self.maximum_spanning_tree_by_observations();
        }

        self.maximum_spanning_tree_impl(|e| {
            let obs = e.num_observations()?;
            let p = e.parallax().filter(|&p| p > 0.0)?;
            Some(p * (1.0 + obs as f32).ln())
        })
    }

    /// Farthest-First Traversal to select `target_count` geometrically diverse frames.
    ///
    /// Starting from `seed_frames`, iteratively picks the unseen frame that minimises
    /// maximum similarity to any already-selected frame, where
    /// `similarity(u, v) = overlap(u, v) / (1 + parallax(u, v))`.
    ///
    /// Lower maximum similarity = less similar to the closest selected frame = more diverse.
    /// Connected frames (with at least one edge to a selected frame) are preferred over
    /// isolated frames (picked last). Always returns at least the seed frames. Never panics.
    pub fn farthest_first_traversal(
        &self,
        seed_frames: &[FrameId],
        target_count: usize,
    ) -> Vec<FrameId> {
        let n = self.num_frames;
        if n == 0 || seed_frames.is_empty() {
            return Vec::new();
        }

        let has_markers = self.has_marker_data();
        let mut selected: Vec<FrameId> = Vec::new();
        let mut in_selected = vec![false; n];

        for &f in seed_frames {
            let idx = f as usize;
            if idx < n && !in_selected[idx] {
                in_selected[idx] = true;
                selected.push(f);
            }
        }

        if selected.is_empty() || selected.len() >= target_count {
            return selected;
        }

        // max_sim[c] = maximum similarity from c to any selected frame.
        // Sentinel f32::MAX = "no edge to any selected frame" (isolated - pick last).
        // Frames with actual edges start at 0.0 and grow.
        // Pick the frame with MINIMUM max_sim:
        //   low max_sim = not similar to even its closest selected neighbour = most diverse.
        let sentinel = f32::MAX;
        let mut max_sim = vec![sentinel; n];

        // Initialise from seed frames.
        for &seed in &selected {
            for candidate in 0..n as FrameId {
                if in_selected[candidate as usize] {
                    continue;
                }
                if let Some(sim) =
                    self.pairwise_similarity(candidate, seed, has_markers)
                {
                    let cur = &mut max_sim[candidate as usize];
                    if *cur == sentinel {
                        *cur = sim;
                    } else {
                        *cur = cur.max(sim);
                    }
                }
            }
        }

        while selected.len() < target_count {
            // Prefer connected frames (max_sim != sentinel).
            // Among connected frames, pick the one with the lowest max_sim (most diverse).
            // Fall back to any unselected isolated frame when no connected ones remain.
            let best_connected = (0..n as FrameId)
                .filter(|&c| {
                    !in_selected[c as usize] && max_sim[c as usize] != sentinel
                })
                .min_by(|&a, &b| {
                    max_sim[a as usize]
                        .partial_cmp(&max_sim[b as usize])
                        .unwrap_or(std::cmp::Ordering::Equal)
                });

            let best_candidate = best_connected.or_else(|| {
                (0..n as FrameId).find(|&c| !in_selected[c as usize])
            });

            let Some(new_frame) = best_candidate else {
                break;
            };

            // Update max_sim: adding new_frame to selected can only increase
            // another frame's maximum similarity to the selected set.
            for candidate in 0..n as FrameId {
                let cidx = candidate as usize;
                if in_selected[cidx] || candidate == new_frame {
                    continue;
                }
                if let Some(sim) =
                    self.pairwise_similarity(candidate, new_frame, has_markers)
                {
                    let cur = &mut max_sim[cidx];
                    if *cur == sentinel {
                        *cur = sim;
                    } else {
                        *cur = cur.max(sim);
                    }
                }
            }

            in_selected[new_frame as usize] = true;
            selected.push(new_frame);
        }

        selected
    }

    /// Find the best initial frame pair to start reconstruction.
    ///
    /// Returns `Some((frame_i, frame_j, score))` for the highest-scoring pair,
    /// or `None` if no valid edges exist.
    pub fn find_initial_pair(&self) -> Option<(FrameId, FrameId, f32)> {
        let mut best: Option<(FrameId, FrameId, f32)> = None;

        for (i, j, edge) in self.iter_edges() {
            let score = self.edge_heuristic(i, j, edge);
            if score.is_nan() || score <= 0.0 {
                continue;
            }

            match best {
                None => best = Some((i, j, score)),
                Some((_, _, best_score)) if score > best_score => {
                    best = Some((i, j, score));
                }
                _ => {}
            }
        }

        best
    }

    /// Compute an approximate Minimum Connected Dominating Set (MCDS) for skeleton
    /// frame selection.
    ///
    /// Uses the Guha-Khuller greedy algorithm. Returns sorted frame IDs covering
    /// the entire frame graph with minimal redundancy. Returns empty if the graph
    /// is disconnected or has no valid edges.
    pub fn compute_connected_dominating_set(&self) -> Vec<FrameId> {
        let frame_count = self.num_frames;
        if frame_count < 2 {
            return Vec::new();
        }

        // Check if there are any valid edges at all.
        if self.num_valid_edges() == 0 {
            return Vec::new();
        }

        // Find the largest connected component and only compute CDS
        // on that. Isolated vertices or small disconnected clusters are
        // ignored since a CDS requires connectivity.
        let all_vertices: Vec<FrameId> = (0..frame_count as FrameId).collect();
        let components =
            Self::find_components(&all_vertices, |a, b| self.has_edge(a, b));
        if components.is_empty() {
            return Vec::new();
        }

        // Find the largest component.
        let largest_component =
            components.iter().max_by_key(|c| c.len()).unwrap();
        if largest_component.len() < 2 {
            return Vec::new();
        }

        let component_set: BTreeSet<FrameId> =
            largest_component.iter().copied().collect();
        mm_eprintln_debug!(
            "    CDS: {} components, largest has {} vertices (of {} total)",
            components.len(),
            largest_component.len(),
            frame_count
        );

        // Phase I: Greedy Dominating Set (on largest component only).
        //
        // Colour states: 0=White, 1=Gray, 2=Black.
        const WHITE: u8 = 0;
        const GRAY: u8 = 1;
        const BLACK: u8 = 2;
        let mut colours = vec![WHITE; frame_count];

        // Mark vertices NOT in the largest component as Gray (excluded).
        for frame_index in 0..frame_count {
            if !component_set.contains(&(frame_index as FrameId)) {
                colours[frame_index] = GRAY; // Gray = already dominated / excluded.
            }
        }

        let mut dominating_set: BTreeSet<FrameId> = BTreeSet::new();
        loop {
            // Check if any white vertices remain.
            let has_white = colours.contains(&WHITE);
            if !has_white {
                break;
            }

            // Score each vertex:
            // black -> 0, gray/white -> count of white neighbors.
            let mut best_score: i32 = -1;
            let mut best_tiebreak: f32 = f32::NEG_INFINITY;
            let mut best_frame_index: Option<FrameId> = None;

            for frame_index in 0..frame_count {
                if colours[frame_index] == BLACK {
                    // Already black (in D), score 0.
                    continue;
                }

                let frame_id = frame_index as FrameId;
                let mut white_neighbor_count: i32 = 0;
                let mut heuristic_sum: f32 = 0.0;

                for other_frame_index in 0..frame_count {
                    if other_frame_index == frame_index {
                        continue;
                    }
                    if colours[other_frame_index] != WHITE {
                        continue; // Not white.
                    }
                    let other_id = other_frame_index as FrameId;
                    if self.has_edge(frame_id, other_id) {
                        white_neighbor_count += 1;
                        let edge = self.get_edge(frame_id, other_id);
                        let h = self.edge_heuristic(frame_id, other_id, edge);
                        if h > 0.0 && !h.is_nan() {
                            heuristic_sum += h;
                        }
                    }
                }

                // Also count self if white (adding self to D dominates self).
                if colours[frame_index] == WHITE {
                    white_neighbor_count += 1;
                }

                if white_neighbor_count > best_score
                    || (white_neighbor_count == best_score
                        && heuristic_sum > best_tiebreak)
                {
                    best_score = white_neighbor_count;
                    best_tiebreak = heuristic_sum;
                    best_frame_index = Some(frame_id);
                }
            }

            let Some(chosen) = best_frame_index else {
                break;
            };
            if best_score <= 0 {
                break;
            }

            // Mark chosen as Black, add to D.
            colours[chosen as usize] = BLACK;
            dominating_set.insert(chosen);

            // Mark white neighbors as Gray.
            for other_frame_index in 0..frame_count {
                if other_frame_index == chosen as usize {
                    continue;
                }
                if colours[other_frame_index] == WHITE
                    && self.has_edge(chosen, other_frame_index as FrameId)
                {
                    colours[other_frame_index] = GRAY;
                }
            }
        }

        if dominating_set.is_empty() {
            return Vec::new();
        }

        let phase1_size = dominating_set.len();
        mm_eprintln_debug!(
            "    CDS Phase I: {} vertices in dominating set",
            phase1_size
        );

        // Phase II: Connect components of D.
        //
        // Find connected components of the subgraph induced by D,
        // then merge them by adding connector vertices.
        loop {
            // BFS to find connected components within D.
            let d_vec: Vec<FrameId> = dominating_set.iter().copied().collect();
            let components =
                Self::find_components(&d_vec, |a, b| self.has_edge(a, b));

            if components.len() <= 1 {
                break;
            }

            let mut merged = false;

            // Try single non-D vertex connecting two different components.
            'single: for frame_index in 0..frame_count as FrameId {
                if dominating_set.contains(&frame_index) {
                    continue;
                }

                let mut touches: BTreeSet<usize> = BTreeSet::new();
                for (comp_idx, comp) in components.iter().enumerate() {
                    for &d_node in comp {
                        if self.has_edge(frame_index, d_node) {
                            touches.insert(comp_idx);
                            break;
                        }
                    }
                }

                if touches.len() >= 2 {
                    dominating_set.insert(frame_index);
                    merged = true;
                    break 'single;
                }
            }

            if merged {
                // Rebuild d_vec and re-check components.
                continue;
            }

            // Try pairs of non-D vertices that connect different components.
            let non_d: Vec<FrameId> = (0..frame_count as FrameId)
                .filter(|frame_index| !dominating_set.contains(frame_index))
                .collect();

            'pair: for (idx_a, &connector_a) in non_d.iter().enumerate() {
                // Find which component connector_a touches.
                let mut component_a: Option<usize> = None;
                for (comp_idx, comp) in components.iter().enumerate() {
                    for &d_node in comp {
                        if self.has_edge(connector_a, d_node) {
                            component_a = Some(comp_idx);
                            break;
                        }
                    }
                    if component_a.is_some() {
                        break;
                    }
                }
                let Some(component1) = component_a else {
                    continue;
                };

                for &connector_b in &non_d[idx_a + 1..] {
                    if !self.has_edge(connector_a, connector_b) {
                        continue;
                    }

                    // Find which component connector_b touches.
                    let mut component_b: Option<usize> = None;
                    for (comp_idx, comp) in components.iter().enumerate() {
                        for &d_node in comp {
                            if self.has_edge(connector_b, d_node) {
                                component_b = Some(comp_idx);
                                break;
                            }
                        }
                        if component_b.is_some() {
                            break;
                        }
                    }
                    let Some(component2) = component_b else {
                        continue;
                    };

                    if component1 != component2 {
                        dominating_set.insert(connector_a);
                        dominating_set.insert(connector_b);
                        merged = true;
                        break 'pair;
                    }
                }
            }

            if !merged {
                // Cannot connect components - graph is disconnected.
                return Vec::new();
            }
        }

        mm_eprintln_debug!(
            "    CDS Phase II: {} vertices added as connectors ({} total)",
            dominating_set.len() - phase1_size,
            dominating_set.len()
        );

        let mut result: Vec<FrameId> = dominating_set.into_iter().collect();
        result.sort_unstable();

        mm_eprintln_debug!("    CDS Frames: {:?}", result);

        result
    }

    /// Find connected components among a set of vertices using BFS.
    pub(crate) fn find_components<F>(
        vertices: &[FrameId],
        has_edge: F,
    ) -> Vec<Vec<FrameId>>
    where
        F: Fn(FrameId, FrameId) -> bool,
    {
        let vertex_set: BTreeSet<FrameId> = vertices.iter().copied().collect();
        let mut visited: BTreeSet<FrameId> = BTreeSet::new();
        let mut components = Vec::new();

        for &start in vertices {
            if visited.contains(&start) {
                continue;
            }

            let mut component = Vec::new();
            let mut queue = std::collections::VecDeque::new();
            queue.push_back(start);
            visited.insert(start);

            while let Some(current) = queue.pop_front() {
                component.push(current);
                for &other in &vertex_set {
                    if !visited.contains(&other) && has_edge(current, other) {
                        visited.insert(other);
                        queue.push_back(other);
                    }
                }
            }

            components.push(component);
        }

        components
    }

    /// Find the most diverse frame strictly between two frame indices.
    ///
    /// Selects the frame in `(frame_a+1)..frame_b` that minimizes similarity to
    /// both endpoints using `similarity(u, v) = overlap(u, v) / (1 + parallax(u, v))`.
    /// Ties are broken by higher uniformity. Returns `None` if no valid candidate exists.
    pub fn find_most_diverse_frame_between(
        &self,
        frame_a: FrameId,
        frame_b: FrameId,
    ) -> Option<FrameId> {
        let lo = frame_a.min(frame_b);
        let hi = frame_a.max(frame_b);
        if hi - lo <= 1 {
            return None; // No frames between adjacent pair.
        }

        let has_markers = self.has_marker_data();
        let mut best: Option<(FrameId, f32, f32)> = None; // (id, max_sim, uniformity)

        for candidate in (lo + 1)..hi {
            if candidate as usize >= self.num_frames {
                continue;
            }

            // Compute similarity to each endpoint.
            let sim_a =
                self.pairwise_similarity(candidate, frame_a, has_markers);
            let sim_b =
                self.pairwise_similarity(candidate, frame_b, has_markers);

            // Must have valid edges to at least one endpoint.
            if sim_a.is_none() && sim_b.is_none() {
                continue;
            }

            let max_sim = sim_a.unwrap_or(0.0).max(sim_b.unwrap_or(0.0));
            let uniformity = self.get_uniformity(candidate).unwrap_or(0.0);

            let dominated = match best {
                None => false,
                Some((_, best_sim, best_uni)) => {
                    max_sim > best_sim
                        || (max_sim == best_sim && uniformity <= best_uni)
                }
            };
            if !dominated {
                best = Some((candidate, max_sim, uniformity));
            }
        }

        best.map(|(id, _, _)| id)
    }

    /// Compute pairwise similarity between two frames.
    ///
    /// Returns `None` if no valid edge exists.
    fn pairwise_similarity(
        &self,
        a: FrameId,
        b: FrameId,
        has_markers: bool,
    ) -> Option<f32> {
        let edge = self.get_edge(a, b);
        if !edge.is_valid() {
            return None;
        }
        let parallax = edge.parallax().unwrap_or(0.0);
        let overlap = if has_markers {
            sorted_intersection_count(
                &self.frame_markers[a as usize],
                &self.frame_markers[b as usize],
            )
        } else {
            edge.num_observations().unwrap_or(0) as usize
        };
        if overlap == 0 {
            return None;
        }
        Some(overlap as f32 / (1.0 + parallax))
    }

    /// Compute a complete frame traversal using the Max-Seed, Max-Diversity strategy.
    ///
    /// Phase I seeds with the highest-scoring frame pair. Phase II iteratively selects
    /// the unvisited frame that maximizes diversity relative to the visited set, using
    /// `similarity(u, v) = overlap(u, v) / (1 + parallax(u, v))` where overlap is
    /// the count of shared marker indices. Connectivity is determined by cumulative
    /// marker overlap with the visited set. Disconnected frames are appended at the end.
    ///
    /// Falls back to edge observation counts when no per-frame marker data is set.
    /// Complexity: O(N^2 x M) where M is the average marker count per frame.
    pub fn compute_max_diversity_traversal(
        &self,
        min_marker_overlap_count: usize,
    ) -> Vec<FrameId> {
        let frame_count = self.num_frames;
        if frame_count == 0 {
            return Vec::new();
        }
        if frame_count == 1 {
            return vec![0];
        }

        // Phase I: Seed pair.
        let (seed_a, seed_b) = match self.find_initial_pair() {
            Some((i, j, _)) => (i, j),
            None => return (0..frame_count as FrameId).collect(),
        };

        let has_markers = self.has_marker_data();

        let mut traversal = Vec::with_capacity(frame_count);
        let mut in_visited = vec![false; frame_count];

        traversal.push(seed_a);
        traversal.push(seed_b);
        in_visited[seed_a as usize] = true;
        in_visited[seed_b as usize] = true;

        // Union of marker indices seen by any visited frame.
        let mut visited_markers: HashSet<usize> = HashSet::new();
        if has_markers {
            for &seed in &[seed_a, seed_b] {
                visited_markers
                    .extend(self.frame_markers[seed as usize].iter());
            }
        }

        // Per-frame cached maximum similarity to any visited frame.
        // NEG_INFINITY means "no edge to any visited frame yet".
        let mut max_similarity = vec![f32::NEG_INFINITY; frame_count];

        // Initialize from both seed frames.
        for &seed in &[seed_a, seed_b] {
            self.update_similarity_cache(
                seed,
                &in_visited,
                has_markers,
                &mut max_similarity,
            );
        }

        // Phase II: Greedy max-min dissimilarity.
        while traversal.len() < frame_count {
            let chosen = self.select_most_diverse_frame(
                &in_visited,
                &max_similarity,
                has_markers,
                &visited_markers,
                min_marker_overlap_count,
            );

            match chosen {
                Some(frame_id) => {
                    traversal.push(frame_id);
                    in_visited[frame_id as usize] = true;

                    // Grow visited marker set.
                    if has_markers {
                        visited_markers.extend(
                            self.frame_markers[frame_id as usize].iter(),
                        );
                    }

                    // Incrementally update similarity cache.
                    self.update_similarity_cache(
                        frame_id,
                        &in_visited,
                        has_markers,
                        &mut max_similarity,
                    );
                }
                None => {
                    // No reachable frames remain; append the rest in
                    // index order.
                    for u in 0..frame_count as FrameId {
                        if !in_visited[u as usize] {
                            traversal.push(u);
                            in_visited[u as usize] = true;
                        }
                    }
                    break;
                }
            }
        }

        traversal
    }

    /// Update the per-frame `max_similarity` cache after adding `new_frame` to the
    /// visited set.
    fn update_similarity_cache(
        &self,
        new_frame: FrameId,
        in_visited: &[bool],
        has_markers: bool,
        max_similarity: &mut [f32],
    ) {
        let n = self.num_frames;
        for u in 0..n as FrameId {
            if in_visited[u as usize] {
                continue;
            }
            let edge = self.get_edge(u, new_frame);
            if !edge.is_valid() {
                continue;
            }

            let parallax = edge.parallax().unwrap_or(0.0);

            let overlap = if has_markers {
                sorted_intersection_count(
                    &self.frame_markers[u as usize],
                    &self.frame_markers[new_frame as usize],
                )
            } else {
                edge.num_observations().unwrap_or(0) as usize
            };

            if overlap == 0 {
                continue;
            }

            let similarity = overlap as f32 / (1.0 + parallax);
            if similarity > max_similarity[u as usize] {
                max_similarity[u as usize] = similarity;
            }
        }
    }

    /// Select the unvisited, connected frame with the lowest max-similarity (most diverse).
    ///
    /// Uses uniformity as a tiebreaker, then lower marker overlap as a tertiary criterion.
    fn select_most_diverse_frame(
        &self,
        in_visited: &[bool],
        max_similarity: &[f32],
        has_markers: bool,
        visited_markers: &HashSet<usize>,
        min_marker_overlap_count: usize,
    ) -> Option<FrameId> {
        let mut best: Option<(FrameId, f32, f32, usize)> = None;

        for frame_id in 0..self.num_frames as FrameId {
            if in_visited[frame_id as usize] {
                continue;
            }

            // Must have at least one edge to the visited set.
            if max_similarity[frame_id as usize] == f32::NEG_INFINITY {
                continue;
            }

            // Connectivity check.
            let marker_overlap_count = if has_markers {
                self.frame_markers[frame_id as usize]
                    .iter()
                    .filter(|m| visited_markers.contains(m))
                    .count()
            } else {
                min_marker_overlap_count
            };
            if marker_overlap_count < min_marker_overlap_count {
                continue;
            }

            let similarity = max_similarity[frame_id as usize];
            let uniformity = self.get_uniformity(frame_id).unwrap_or(0.0);

            let dominated = match best {
                None => false,
                Some((
                    _,
                    best_similarity,
                    best_uniformity,
                    best_marker_overlap_count,
                )) => {
                    // Primary: lower similarity is better (more diverse).
                    similarity > best_similarity
                        || (similarity == best_similarity && {
                            // Secondary: higher uniformity is better.
                            uniformity < best_uniformity
                                || (uniformity == best_uniformity && {
                                    // Tertiary: lower marker overlap is better (more diverse).
                                    marker_overlap_count
                                        > best_marker_overlap_count
                                })
                        })
                }
            };
            if !dominated {
                best = Some((
                    frame_id,
                    similarity,
                    uniformity,
                    marker_overlap_count,
                ));
            }
        }

        best.map(|(id, _, _, _)| id)
    }
}

impl Default for FrameGraph {
    fn default() -> Self {
        Self::new(2)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    /// Helper: verify that a set of vertices forms a valid CDS.
    ///
    /// Checks:
    /// 1. Every vertex is either in the CDS or adjacent to a CDS vertex (domination).
    /// 2. The CDS subgraph is connected.
    fn verify_cds(graph: &FrameGraph, cds: &[FrameId]) {
        let n = graph.num_frames();
        let cds_set: BTreeSet<FrameId> = cds.iter().copied().collect();

        // Check domination: every vertex must be in CDS or adjacent to one.
        for v in 0..n as FrameId {
            if cds_set.contains(&v) {
                continue;
            }
            let dominated = cds.iter().any(|&d| graph.has_edge(v, d));
            assert!(
                dominated,
                "Vertex {} is not dominated by CDS {:?}",
                v, cds
            );
        }

        // Check connectivity of CDS subgraph.
        if cds.len() <= 1 {
            return;
        }
        let components =
            FrameGraph::find_components(cds, |a, b| graph.has_edge(a, b));
        assert_eq!(
            components.len(),
            1,
            "CDS is not connected: {} components for {:?}",
            components.len(),
            cds
        );
    }

    #[test]
    fn test_cds_simple_chain() {
        // 5-node chain: 0-1-2-3-4
        let mut graph = FrameGraph::new(5);
        for i in 0..5 {
            graph.set_uniformity(i, 0.8);
        }
        graph.set_edge(0, 1, FrameEdge::new(50, 2.0));
        graph.set_edge(1, 2, FrameEdge::new(50, 2.0));
        graph.set_edge(2, 3, FrameEdge::new(50, 2.0));
        graph.set_edge(3, 4, FrameEdge::new(50, 2.0));

        let cds = graph.compute_connected_dominating_set();
        assert!(!cds.is_empty(), "CDS should not be empty for chain");
        verify_cds(&graph, &cds);
    }

    #[test]
    fn test_cds_complete_graph() {
        // 5-node complete graph
        let mut graph = FrameGraph::new(5);
        for i in 0..5 {
            graph.set_uniformity(i, 0.8);
        }
        for i in 0..5u32 {
            for j in (i + 1)..5u32 {
                graph.set_edge(i, j, FrameEdge::new(50, 2.0));
            }
        }

        let cds = graph.compute_connected_dominating_set();
        assert!(
            !cds.is_empty(),
            "CDS should not be empty for complete graph"
        );
        verify_cds(&graph, &cds);
        // For a complete graph, CDS should be small (1 vertex suffices).
        assert!(
            cds.len() <= 2,
            "CDS too large for complete graph: {:?}",
            cds
        );
    }

    #[test]
    fn test_cds_star_graph() {
        // Star: hub=0, spokes=1,2,3,4
        let mut graph = FrameGraph::new(5);
        for i in 0..5 {
            graph.set_uniformity(i, 0.8);
        }
        for spoke in 1..5u32 {
            graph.set_edge(0, spoke, FrameEdge::new(50, 2.0));
        }

        let cds = graph.compute_connected_dominating_set();
        assert!(!cds.is_empty(), "CDS should not be empty for star graph");
        verify_cds(&graph, &cds);
        // Hub alone should dominate everything.
        assert!(
            cds.contains(&0),
            "CDS should contain hub vertex 0: {:?}",
            cds
        );
    }

    #[test]
    fn test_cds_disconnected() {
        // Two isolated clusters: {0,1} and {2,3}, no edges between them.
        // CDS is computed on the largest component only.
        let mut graph = FrameGraph::new(4);
        for i in 0..4 {
            graph.set_uniformity(i, 0.8);
        }
        graph.set_edge(0, 1, FrameEdge::new(50, 2.0));
        graph.set_edge(2, 3, FrameEdge::new(50, 2.0));

        let cds = graph.compute_connected_dominating_set();
        // Should produce a CDS for the largest component (both
        // have size 2, so one is picked). The CDS dominates that
        // component but NOT the other cluster.
        assert!(
            !cds.is_empty(),
            "CDS should cover largest component, got empty"
        );
        // All CDS vertices should be from one component.
        let all_in_first = cds.iter().all(|&v| v <= 1);
        let all_in_second = cds.iter().all(|&v| v >= 2);
        assert!(
            all_in_first || all_in_second,
            "CDS should be from one component only: {:?}",
            cds
        );
    }

    #[test]
    fn test_find_initial_pair() {
        let mut graph = FrameGraph::new(5);

        // Set uniformities.
        graph.set_uniformity(0, 0.7); // Frame 0.
        graph.set_uniformity(1, 0.7); // Frame 1.
        graph.set_uniformity(2, 0.9); // Frame 2: Best.
        graph.set_uniformity(3, 0.8); // Frame 3.

        // Create edges with varying quality.
        graph.set_edge(0, 1, FrameEdge::new(100, 3.0));
        graph.set_edge(0, 2, FrameEdge::new(150, 5.0)); // Best: high parallax + uniformity.
        graph.set_edge(1, 2, FrameEdge::new(80, 2.0));
        graph.set_edge(2, 3, FrameEdge::new(120, 4.0));

        let result = graph.find_initial_pair();
        assert!(result.is_some());

        let (i, j, _score) = result.unwrap();
        // Should pick (0, 2) as the best initial pair.
        assert!((i == 0 && j == 2) || (i == 2 && j == 0));
    }

    // ---- Max-Diversity Traversal tests ----

    #[test]
    fn test_traversal_unique_visitation() {
        // Every frame appears exactly once in the traversal.
        let mut graph = FrameGraph::new(8);
        for i in 0..8u32 {
            graph.set_uniformity(i, 0.8);
        }
        // Chain with skip-1 connections.
        for i in 0..8u32 {
            for j in (i + 1)..8u32 {
                if j - i <= 3 {
                    let obs = 50 + (j - i) as i32 * 10;
                    let parallax = (j - i) as f32 * 1.5;
                    graph.set_edge(i, j, FrameEdge::new(obs, parallax));
                }
            }
        }

        let traversal = graph.compute_max_diversity_traversal(6);
        assert_eq!(traversal.len(), 8);

        let mut seen = BTreeSet::new();
        for &f in &traversal {
            assert!(
                seen.insert(f),
                "Frame {} appears more than once in traversal",
                f
            );
        }
    }

    #[test]
    fn test_traversal_seed_pair_is_best() {
        // First two frames should match find_initial_pair.
        let mut graph = FrameGraph::new(5);
        for i in 0..5u32 {
            graph.set_uniformity(i, 0.8);
        }
        // Make (1, 3) the best pair by giving it highest score.
        graph.set_edge(0, 1, FrameEdge::new(50, 1.0));
        graph.set_edge(1, 2, FrameEdge::new(60, 2.0));
        graph.set_edge(1, 3, FrameEdge::new(200, 8.0)); // Best pair.
        graph.set_edge(2, 3, FrameEdge::new(70, 2.5));
        graph.set_edge(3, 4, FrameEdge::new(80, 3.0));
        graph.set_edge(0, 4, FrameEdge::new(40, 1.0));

        let initial = graph.find_initial_pair().unwrap();
        let traversal = graph.compute_max_diversity_traversal(6);

        assert_eq!(traversal.len(), 5);
        let seed_set: BTreeSet<FrameId> =
            [traversal[0], traversal[1]].iter().copied().collect();
        let expected_set: BTreeSet<FrameId> =
            [initial.0, initial.1].iter().copied().collect();
        assert_eq!(seed_set, expected_set);
    }

    #[test]
    fn test_traversal_diversity_ordering() {
        // 5 frames in a line: 0--1--2--3--4.
        // Parallax increases with distance.
        // After seeding with the best pair, the next frame chosen
        // should be the one most dissimilar to everything visited.
        let mut graph = FrameGraph::new(5);
        for i in 0..5u32 {
            graph.set_uniformity(i, 0.8);
        }
        for i in 0..5u32 {
            for j in (i + 1)..5u32 {
                let distance = (j - i) as f32;
                let parallax = distance * 2.0;
                let obs = 100 - (j - i) as i32 * 5;
                graph.set_edge(i, j, FrameEdge::new(obs.max(20), parallax));
            }
        }

        let traversal = graph.compute_max_diversity_traversal(6);
        assert_eq!(traversal.len(), 5);

        // Third frame should NOT be adjacent to both seed frames;
        // it should be the frame with the lowest max-similarity
        // (highest minimum parallax) to the seed pair.
        let seed_a = traversal[0];
        let seed_b = traversal[1];
        let third = traversal[2];

        // The third frame should be far from at least one seed.
        let parallax_to_a =
            graph.get_edge(third, seed_a).parallax().unwrap_or(0.0);
        let parallax_to_b =
            graph.get_edge(third, seed_b).parallax().unwrap_or(0.0);
        let min_parallax = parallax_to_a.min(parallax_to_b);

        // Verify the chosen frame's min-parallax is >= all other
        // candidates' min-parallax (max-min criterion).
        for u in 0..5u32 {
            if u == seed_a || u == seed_b || u == third {
                continue;
            }
            let pa = graph.get_edge(u, seed_a).parallax().unwrap_or(0.0);
            let pb = graph.get_edge(u, seed_b).parallax().unwrap_or(0.0);
            let candidate_min = pa.min(pb);
            // similarity = 1/(1+parallax), so lower parallax = higher
            // similarity. Max-min dissimilarity picks the frame whose
            // max similarity (= min parallax) is lowest. That means
            // the chosen frame should have the *highest* minimum
            // parallax.
            assert!(
                min_parallax >= candidate_min - 0.01,
                "Frame {} (min_par={:.2}) beat chosen {} (min_par={:.2})",
                u,
                candidate_min,
                third,
                min_parallax
            );
        }
    }

    #[test]
    fn test_traversal_disconnected_appended() {
        // Frames 3 and 4 have no edges to anything.
        let mut graph = FrameGraph::new(5);
        for i in 0..5u32 {
            graph.set_uniformity(i, 0.8);
        }
        graph.set_edge(0, 1, FrameEdge::new(100, 5.0));
        graph.set_edge(1, 2, FrameEdge::new(80, 3.0));
        graph.set_edge(0, 2, FrameEdge::new(90, 4.0));
        // 3 and 4 are isolated.

        let traversal = graph.compute_max_diversity_traversal(6);
        assert_eq!(traversal.len(), 5);

        // First 3 should be {0, 1, 2} in some order.
        let connected: BTreeSet<FrameId> =
            traversal[..3].iter().copied().collect();
        assert_eq!(
            connected,
            [0, 1, 2].iter().copied().collect::<BTreeSet<_>>()
        );

        // Last 2 should be {3, 4}.
        let disconnected: BTreeSet<FrameId> =
            traversal[3..].iter().copied().collect();
        assert_eq!(
            disconnected,
            [3, 4].iter().copied().collect::<BTreeSet<_>>()
        );
    }

    #[test]
    fn test_traversal_no_valid_edges() {
        // No edges at all - should return frames in index order.
        let graph = FrameGraph::new(4);
        let traversal = graph.compute_max_diversity_traversal(6);
        assert_eq!(traversal, vec![0, 1, 2, 3]);
    }

    #[test]
    fn test_traversal_two_frames() {
        let mut graph = FrameGraph::new(2);
        graph.set_uniformity(0, 0.8);
        graph.set_uniformity(1, 0.8);
        graph.set_edge(0, 1, FrameEdge::new(100, 5.0));

        let traversal = graph.compute_max_diversity_traversal(6);
        assert_eq!(traversal.len(), 2);
        let set: BTreeSet<_> = traversal.iter().copied().collect();
        assert_eq!(set, [0, 1].iter().copied().collect::<BTreeSet<_>>());
    }

    #[test]
    fn test_traversal_20_frame_sequence() {
        // Simulates a video sequence of 20 frames with temporal
        // connectivity (nearby frames share observations).
        let mut graph = FrameGraph::new(20);
        for i in 0..20u32 {
            graph.set_uniformity(i, 0.7 + 0.01 * i as f32);
        }
        for i in 0..20u32 {
            for j in (i + 1)..20u32 {
                let dist = j - i;
                if dist <= 5 {
                    let parallax = dist as f32 * 1.5;
                    let obs = (120 - dist as i32 * 10).max(20);
                    graph.set_edge(i, j, FrameEdge::new(obs, parallax));
                }
            }
        }

        let traversal = graph.compute_max_diversity_traversal(6);
        assert_eq!(traversal.len(), 20);

        // Check uniqueness.
        let set: BTreeSet<_> = traversal.iter().copied().collect();
        assert_eq!(set.len(), 20);

        // The traversal should spread out quickly, not go linearly
        // through consecutive frames. Check that the first 5 chosen
        // frames span a reasonable range.
        let first_5: Vec<u32> = traversal[..5].to_vec();
        let min_f = *first_5.iter().min().unwrap();
        let max_f = *first_5.iter().max().unwrap();
        assert!(
            max_f - min_f >= 4,
            "First 5 frames should spread out: {:?}",
            first_5
        );
    }

    #[test]
    fn test_traversal_with_marker_overlap() {
        // 6 frames where per-edge observation counts are identical
        // but marker overlap patterns differ. Marker data should
        // drive both connectivity and similarity.
        //
        // Markers 0..9 are shared broadly; markers 10..19 are
        // unique to distant frames, creating diversity.
        let mut graph = FrameGraph::new(6);
        for i in 0..6u32 {
            graph.set_uniformity(i, 0.8);
        }

        // All pairs within distance 3 share 20 observations and
        // moderate parallax.
        for i in 0..6u32 {
            for j in (i + 1)..6u32 {
                if j - i <= 3 {
                    let parallax = (j - i) as f32 * 2.0;
                    graph.set_edge(i, j, FrameEdge::new(20, parallax));
                }
            }
        }

        // Marker assignments:
        //   Frame 0: markers {0,1,2,3,4,5}
        //   Frame 1: markers {0,1,2,3,4,6}    (high overlap with 0)
        //   Frame 2: markers {0,1,2,7,8,9}    (moderate overlap with 0)
        //   Frame 3: markers {0,1,10,11,12,13} (low overlap with 0)
        //   Frame 4: markers {0,14,15,16,17,18} (very low overlap with 0)
        //   Frame 5: markers {0,1,2,3,4,5}    (identical to 0)
        graph.set_frame_markers(0, vec![0, 1, 2, 3, 4, 5]);
        graph.set_frame_markers(1, vec![0, 1, 2, 3, 4, 6]);
        graph.set_frame_markers(2, vec![0, 1, 2, 7, 8, 9]);
        graph.set_frame_markers(3, vec![0, 1, 10, 11, 12, 13]);
        graph.set_frame_markers(4, vec![0, 14, 15, 16, 17, 18]);
        graph.set_frame_markers(5, vec![0, 1, 2, 3, 4, 5]);

        assert!(graph.has_marker_data());

        let traversal = graph.compute_max_diversity_traversal(1);
        assert_eq!(traversal.len(), 6);

        // Uniqueness.
        let set: BTreeSet<_> = traversal.iter().copied().collect();
        assert_eq!(set.len(), 6);

        // Frame 5 (identical markers to 0) and frame 1 (high
        // overlap) should appear later than frame 4 (low overlap)
        // and frame 3 (low overlap), because the algorithm prefers
        // diversity.
        let pos = |f: FrameId| -> usize {
            traversal.iter().position(|&x| x == f).unwrap()
        };

        // Frame 4 has the least marker overlap with the seed pair
        // so it should be selected earlier than the highly-similar
        // frames 1 and 5.
        assert!(
            pos(4) < pos(5),
            "Frame 4 (diverse) should appear before frame 5 (identical to seed): {:?}",
            traversal
        );
        assert!(
            pos(4) < pos(1),
            "Frame 4 (diverse) should appear before frame 1 (high overlap): {:?}",
            traversal
        );
    }

    #[test]
    fn test_traversal_cumulative_overlap_connectivity() {
        // Frame 3 has no direct edge to the seed pair but becomes
        // connected via cumulative marker overlap once frame 2 is
        // added.
        let mut graph = FrameGraph::new(4);
        for i in 0..4u32 {
            graph.set_uniformity(i, 0.8);
        }

        // Edges: 0-1 (seed), 0-2, 1-2, 2-3.
        // Frame 3 only connects to frame 2.
        graph.set_edge(0, 1, FrameEdge::new(20, 5.0));
        graph.set_edge(0, 2, FrameEdge::new(20, 3.0));
        graph.set_edge(1, 2, FrameEdge::new(20, 3.0));
        graph.set_edge(2, 3, FrameEdge::new(20, 4.0));

        // Markers:
        //   Frame 0: {0,1,2,3,4,5,6,7}
        //   Frame 1: {0,1,2,3,8,9,10,11}
        //   Frame 2: {2,3,4,5,12,13,14,15}
        //   Frame 3: {4,5,12,13,16,17,18,19}
        graph.set_frame_markers(0, vec![0, 1, 2, 3, 4, 5, 6, 7]);
        graph.set_frame_markers(1, vec![0, 1, 2, 3, 8, 9, 10, 11]);
        graph.set_frame_markers(2, vec![2, 3, 4, 5, 12, 13, 14, 15]);
        graph.set_frame_markers(3, vec![4, 5, 12, 13, 16, 17, 18, 19]);

        // Frame 3's markers {4,5,12,13,16,17,18,19}:
        //   Overlap with frame 0 alone: {4,5} = 2
        //   Overlap with frame 1 alone: {} = 0
        //   Overlap with visited_markers after adding frame 2:
        //     visited = {0..15} -> overlap = {4,5,12,13} = 4
        //
        // With min_overlap=3, frame 3 is unreachable from the seed
        // pair alone but becomes connected once frame 2 is visited.
        let traversal = graph.compute_max_diversity_traversal(3);
        assert_eq!(traversal.len(), 4);

        let set: BTreeSet<_> = traversal.iter().copied().collect();
        assert_eq!(set.len(), 4);

        // Frame 2 must appear before frame 3 (enables connectivity).
        let pos = |f: FrameId| -> usize {
            traversal.iter().position(|&x| x == f).unwrap()
        };
        assert!(
            pos(2) < pos(3),
            "Frame 2 must be visited before frame 3: {:?}",
            traversal
        );
    }
}
