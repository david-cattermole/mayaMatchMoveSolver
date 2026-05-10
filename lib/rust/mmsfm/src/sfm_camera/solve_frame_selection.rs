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

//! Frame selection and ordering for camera solving

use anyhow::{anyhow, Result};

use std::collections::{BTreeSet, HashMap};
use std::time::Instant;

use mmio::uvtrack_reader::{FrameNumber, FrameRange, MarkersData};

use super::constants::RECOMENDED_MARKERS_FOR_PNP;
use super::frame_graph::{FrameEdge, FrameGraph, FrameId};
use super::frame_score::{compute_parallax_residual, FrameAnalysisResult};
use crate::datatype::{
    BundlePositions, FrameMarkerIndex, FrameMarkerIndexBuilder,
    MarkerObservations,
};
use crate::sfm_camera::solve_utils::format_frame_list;

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Build a FrameGraph from marker data for initial pair selection.
///
/// Edges represent shared marker observations, parallax (motion between
/// frames), and uniformity (spatial distribution of markers).
///
pub fn build_frame_graph_for_initial_pair(
    markers: &MarkersData,
    marker_indices: &[usize],
    common_frame_numbers: &[FrameNumber],
) -> FrameGraph {
    let num_frames = common_frame_numbers.len();
    let mut graph = FrameGraph::new(num_frames.max(2));

    if num_frames < 2 {
        return graph;
    }

    mm_eprintln_debug!(
        "Building FrameGraph for {} common frames",
        common_frame_numbers.len()
    );

    // Pre-compute uniformity for each frame.
    for (i, &frame_num) in common_frame_numbers.iter().enumerate() {
        let mut points_x = Vec::new();
        let mut points_y = Vec::new();

        for &marker_idx in marker_indices {
            if marker_idx >= markers.frame_data.len() {
                continue;
            }
            let frame_data = &markers.frame_data[marker_idx];
            for (k, &f) in frame_data.frames.iter().enumerate() {
                if f == frame_num {
                    points_x.push(frame_data.u_coords[k] as f32 - 0.5);
                    points_y.push(frame_data.v_coords[k] as f32 - 0.5);
                    break;
                }
            }
        }

        graph.calculate_and_set_uniformity(i as u32, &points_x, &points_y);
    }

    // Build edges between all pairs of common frames.
    for i in 0..num_frames {
        for j in (i + 1)..num_frames {
            let frame_a = common_frame_numbers[i];
            let frame_b = common_frame_numbers[j];

            // Count shared observations and compute basic metrics.
            let mut num_observations = 0;
            let mut points_a = Vec::new();
            let mut points_b = Vec::new();

            for &marker_idx in marker_indices {
                if marker_idx >= markers.frame_data.len() {
                    continue;
                }

                let frame_data = &markers.frame_data[marker_idx];
                let mut has_a = None;
                let mut has_b = None;

                for (k, &frame_num) in frame_data.frames.iter().enumerate() {
                    if frame_num == frame_a {
                        has_a = Some((
                            frame_data.u_coords[k] as f32 - 0.5,
                            frame_data.v_coords[k] as f32 - 0.5,
                        ));
                    } else if frame_num == frame_b {
                        has_b = Some((
                            frame_data.u_coords[k] as f32 - 0.5,
                            frame_data.v_coords[k] as f32 - 0.5,
                        ));
                    }
                }

                if let (Some(pt_a), Some(pt_b)) = (has_a, has_b) {
                    num_observations += 1;
                    points_a.push(pt_a);
                    points_b.push(pt_b);
                }
            }

            if (num_observations as usize) < RECOMENDED_MARKERS_FOR_PNP {
                continue;
            }

            // Compute simple parallax metric (mean displacement).
            let parallax = compute_parallax_residual(&points_a, &points_b);

            let edge = FrameEdge::new(num_observations, parallax);
            graph.set_edge(i as u32, j as u32, edge);
        }
    }

    mm_eprintln_debug!(
        "  FrameGraph built with {} valid edges",
        graph.num_valid_edges()
    );

    graph
}

/// Build a FrameGraph from marker data for the full frame range.
///
/// Similar to `build_frame_graph_for_initial_pair` but operates on all frames.
pub fn build_frame_graph_for_full_range(
    markers: &MarkersData,
    marker_indices: &[usize],
    scene_frame_range: &FrameRange,
) -> FrameGraph {
    let start_time = Instant::now();

    let frame_numbers: Vec<FrameNumber> =
        (scene_frame_range.start_frame..=scene_frame_range.end_frame).collect();
    let num_frames = frame_numbers.len();
    let mut graph = FrameGraph::new(num_frames.max(2));

    if num_frames < 2 {
        return graph;
    }

    mm_eprintln_debug!(
        "Building FrameGraph for {} frames in full range",
        frame_numbers.len()
    );

    // Maximum frame distance to consider for edges.
    //
    // Frames further apart are unlikely to share enough observations.
    //
    // This reduces the number of pairs from O(n^2) to O(n x max_distance).
    let max_frame_distance = if num_frames > 500 {
        // For large datasets, limit to reasonable temporal window.
        500
    } else {
        // For small datasets, consider all pairs.
        num_frames
    };

    let build_start = Instant::now();

    // Build FrameMarkerIndex.
    let start_frame = scene_frame_range.start_frame;
    let end_frame = scene_frame_range.end_frame;
    let mut frame_marker_index_builder =
        FrameMarkerIndexBuilder::new(num_frames);
    for &marker_idx in marker_indices {
        if marker_idx >= markers.frame_data.len() {
            continue;
        }
        let frame_data = &markers.frame_data[marker_idx];
        for (k, &frame_num) in frame_data.frames.iter().enumerate() {
            if frame_num < start_frame || frame_num > end_frame {
                continue;
            }
            let frame_idx = (frame_num - start_frame) as usize;
            let u = frame_data.u_coords[k] as f32 - 0.5;
            let v = frame_data.v_coords[k] as f32 - 0.5;
            frame_marker_index_builder.push(frame_idx, marker_idx, u, v);
        }
    }
    let frame_marker_index: FrameMarkerIndex =
        frame_marker_index_builder.build();

    mm_eprintln_debug!(
        "  Index build: {:.3}s",
        build_start.elapsed().as_secs_f64()
    );

    let uniformity_start = Instant::now();

    // Pre-compute uniformity and populate per-frame marker index.
    let mut marker_idx_buffer = Vec::new();
    for i in 0..num_frames {
        // Uniformity: collect (u, v) coordinates for this frame.
        let (points_x, points_y): (Vec<f32>, Vec<f32>) =
            frame_marker_index.iter_coords(i).unzip();
        graph.calculate_and_set_uniformity(i as u32, &points_x, &points_y);

        // Marker index list (sorted) for graph intersection queries.
        frame_marker_index.marker_indices(i, &mut marker_idx_buffer);
        graph.set_frame_markers(i as u32, marker_idx_buffer.clone());
    }

    mm_eprintln_debug!(
        "  Uniformity + markers: {:.3}s",
        uniformity_start.elapsed().as_secs_f64()
    );

    let edge_build_start = Instant::now();
    let mut pairs_considered = 0usize;

    // Build edges between pairs of frames within max_frame_distance.
    let mut points_a: Vec<(f32, f32)> = Vec::new();
    let mut points_b: Vec<(f32, f32)> = Vec::new();
    for i in 0..num_frames {
        if frame_marker_index.is_empty(i) {
            continue;
        }

        let max_j = (i + max_frame_distance + 1).min(num_frames);
        for j in (i + 1)..max_j {
            pairs_considered += 1;

            if frame_marker_index.is_empty(j) {
                continue;
            }

            // Fills points_a and points_b with paired (u, v)
            // coordinates for shared markers.
            frame_marker_index.intersect_coords(
                i,
                j,
                &mut points_a,
                &mut points_b,
            );

            if points_a.len() < RECOMENDED_MARKERS_FOR_PNP {
                continue;
            }

            let num_observations = points_a.len() as i32;
            let parallax = compute_parallax_residual(&points_a, &points_b);
            graph.set_edge(
                i as u32,
                j as u32,
                FrameEdge::new(num_observations, parallax),
            );
        }
    }

    let pairs_skipped_distance =
        (num_frames * (num_frames - 1) / 2) - pairs_considered;

    mm_eprintln_debug!(
        "  Edge building: {:.3}s ({} pairs considered, {} skipped due to distance > {})",
        edge_build_start.elapsed().as_secs_f64(),
        pairs_considered,
        pairs_skipped_distance,
        max_frame_distance
    );
    mm_eprintln_debug!(
        "  FrameGraph built with {} valid edges",
        graph.num_valid_edges()
    );
    mm_eprintln_debug!(
        "  Total time: {:.3}s",
        start_time.elapsed().as_secs_f64()
    );

    graph
}

pub fn build_frame_graph_skeleton_frames(
    frame_graph: &FrameGraph,
    scene_frame_range: &FrameRange,
    initial_frame_pair: Option<(FrameNumber, FrameNumber)>,
    densify_iterations: u32,
) -> Option<BTreeSet<FrameNumber>> {
    mm_eprintln_debug!(
        "  Connected Dominating Set input: {} frames, {} valid edges in frame graph",
        frame_graph.num_frames(),
        frame_graph.num_valid_edges()
    );

    if DEBUG {
        frame_graph.print_metrics("Full graph");
        frame_graph.print_edge_heuristic(5);
    }

    // Build a Maximum Spanning Tree from geometrically strong connections
    // (high parallax * many observations), then find a Connected Dominating
    // Set - a small subset of frames that "covers" all others.
    let spanning_tree = frame_graph.maximum_spanning_tree_by_parallax();
    if DEBUG {
        frame_graph.print_metrics("Full graph");
        spanning_tree
            .print_metrics("Maximum Spanning Tree (parallax-weighted)");
    }

    let dominating_set = spanning_tree.compute_connected_dominating_set();
    mm_eprintln_debug!(
        "  Connected Dominating Set result: {} vertices in dominating set",
        dominating_set.len()
    );

    // Compute frame number list before potential FFT fallback so both branches share it.
    let all_frame_numbers: Vec<FrameNumber> =
        (scene_frame_range.start_frame..=scene_frame_range.end_frame).collect();

    let mut frame_numbers: BTreeSet<FrameNumber> = if dominating_set.is_empty()
    {
        // CDS failed (graph disconnected or all-zero-parallax MST): fall back to
        // Farthest-First Traversal which always produces a valid diverse skeleton.
        mm_eprintln_debug!(
            "  Connected Dominating Set returned empty - falling back to Farthest-First Traversal."
        );

        let seed_indices: Vec<FrameId> = {
            let mut seeds = Vec::new();
            if let Some((a, b)) = initial_frame_pair {
                if let Some(ia) = all_frame_numbers.iter().position(|&f| f == a)
                {
                    seeds.push(ia as FrameId);
                }
                if let Some(ib) = all_frame_numbers.iter().position(|&f| f == b)
                {
                    seeds.push(ib as FrameId);
                }
            }
            seeds
        };

        let n = frame_graph.num_frames();
        let target_count = ((n as f32).sqrt() as usize + 1).max(3).min(n);
        let fft_indices =
            frame_graph.farthest_first_traversal(&seed_indices, target_count);

        let fft_frames: BTreeSet<FrameNumber> = fft_indices
            .iter()
            .filter_map(|&idx| all_frame_numbers.get(idx as usize).copied())
            .collect();

        if fft_frames.is_empty() {
            mm_eprintln_debug!(
                "  Farthest-First Traversal also returned empty - no skeleton possible."
            );
            return None;
        }

        mm_eprintln_debug!(
            "  Skeleton frames (FFT fallback): {} frames",
            fft_frames.len()
        );
        fft_frames
    } else {
        dominating_set
            .iter()
            .filter_map(|&idx| all_frame_numbers.get(idx as usize).copied())
            .collect()
    };
    mm_eprintln_debug!(
        "  Skeleton frames (CDS on MST before initial pair): {} frames: {}",
        frame_numbers.len(),
        format_frame_list(
            &frame_numbers.iter().copied().collect::<Vec<FrameNumber>>()
        )
    );

    // Add initial frame pair if provided.
    if let Some((frame_a, frame_b)) = initial_frame_pair {
        frame_numbers.insert(frame_a);
        frame_numbers.insert(frame_b);
        mm_eprintln_debug!(
            "  Added initial frame pair ({}, {}) to skeleton frames.",
            frame_a,
            frame_b
        );
    }
    mm_eprintln_debug!(
        "  Skeleton frames (CDS on MST): {} frames: {}",
        frame_numbers.len(),
        format_frame_list(
            &frame_numbers.iter().copied().collect::<Vec<FrameNumber>>()
        )
    );

    // Densify skeleton by iteratively inserting the most diverse
    // frame between each consecutive pair.
    if densify_iterations > 0 {
        // Build mapping from frame number to graph index.
        let frame_to_index: HashMap<FrameNumber, u32> = all_frame_numbers
            .iter()
            .enumerate()
            .map(|(i, &f)| (f, i as u32))
            .collect();

        for iteration in 0..densify_iterations {
            let sorted_frames: Vec<FrameNumber> =
                frame_numbers.iter().copied().collect();
            if sorted_frames.len() < 2 {
                break;
            }

            let mut new_frames = Vec::new();
            for pair in sorted_frames.windows(2) {
                let frame_a = pair[0];
                let frame_b = pair[1];

                let Some(&idx_a) = frame_to_index.get(&frame_a) else {
                    continue;
                };
                let Some(&idx_b) = frame_to_index.get(&frame_b) else {
                    continue;
                };

                if let Some(mid_idx) =
                    frame_graph.find_most_diverse_frame_between(idx_a, idx_b)
                {
                    if let Some(&mid_frame) =
                        all_frame_numbers.get(mid_idx as usize)
                    {
                        if !frame_numbers.contains(&mid_frame) {
                            new_frames.push(mid_frame);
                        }
                    }
                }
            }

            let added = new_frames.len();
            for f in new_frames {
                frame_numbers.insert(f);
            }

            mm_eprintln_debug!(
                "  Skeleton densify iteration {}: added {} frames, total {} frames: {}",
                iteration + 1,
                added,
                frame_numbers.len(),
                format_frame_list(&frame_numbers.iter().copied().collect::<Vec<FrameNumber>>())
            );

            if added == 0 {
                break;
            }
        }
    }

    Some(frame_numbers)
}

/// Determine best frame pair - either from frame_score or frame_graph.
pub fn find_best_frame_pair(
    markers: &MarkersData,
    marker_indices: &[usize],
    frame_analysis_result: &FrameAnalysisResult,
) -> Result<(FrameNumber, FrameNumber)> {
    mm_eprintln_debug!("\nUsing FrameGraph for initial pair selection...");

    // Build frame graph from selected markers.
    let frame_graph = build_frame_graph_for_initial_pair(
        markers,
        marker_indices,
        &frame_analysis_result.common_frame_numbers,
    );

    // Find best initial pair using frame graph.
    let graph_result = frame_graph
        .find_initial_pair()
        .ok_or_else(|| anyhow!("FrameGraph found no valid frame pair"))?;

    // Convert from graph indices to frame numbers.
    let frame_idx_a = graph_result.0 as usize;
    let frame_idx_b = graph_result.1 as usize;
    let frame_a = frame_analysis_result.common_frame_numbers[frame_idx_a];
    let frame_b = frame_analysis_result.common_frame_numbers[frame_idx_b];

    mm_eprintln_debug!(
        "  FrameGraph selected pair: frames {} and {} (score: {:.4})",
        frame_a,
        frame_b,
        graph_result.2
    );

    Ok((frame_a, frame_b))
}

/// Select unsolved frames for the final pass using max-diversity traversal.
///
/// Walks the pre-computed global diversity order and returns unsolved frames
/// up to `max_candidates`, skipping any already in `solved_frames`.
fn generate_unsolved_frames_from_frame_graph(
    frame_graph: &FrameGraph,
    scene_frame_range: &FrameRange,
    solved_frames: &BTreeSet<FrameNumber>,
    max_candidates: usize,
) -> Vec<FrameNumber> {
    let frame_numbers: Vec<FrameNumber> =
        (scene_frame_range.start_frame..=scene_frame_range.end_frame).collect();

    mm_eprintln_debug!("    [all frames] Using max-diversity traversal");

    let traversal =
        frame_graph.compute_max_diversity_traversal(RECOMENDED_MARKERS_FOR_PNP);

    let candidates: Vec<FrameNumber> = traversal
        .iter()
        .map(|&id| frame_numbers[id as usize])
        .filter(|f| !solved_frames.contains(f))
        .take(max_candidates)
        .collect();

    mm_eprintln_debug!(
        "    [all frames] traversal: {} total, {} unsolved candidates = {}",
        traversal.len(),
        candidates.len(),
        format_frame_list(&candidates)
    );

    candidates
}

/// Find unsolved frames ordered by count of solvable (triangulated) bundles visible.
///
/// When `candidate_pool` is `Some`, only frames in that set are considered;
/// this lets the draft pass restrict selection to skeleton frames while still
/// ordering them by actual reconstruction solvability rather than static graph
/// metrics. Returns at most `max_candidates` frames where
/// solvable_count >= min_solvable, sorted descending by count.
pub fn find_next_frames_by_solvability(
    scene_frame_range: &FrameRange,
    solved_frames: &BTreeSet<FrameNumber>,
    observations: &MarkerObservations,
    bundle_positions: &BundlePositions,
    marker_indices: &[usize],
    min_solvable: usize,
    max_candidates: usize,
    candidate_pool: Option<&BTreeSet<FrameNumber>>,
) -> Vec<FrameNumber> {
    let mut frame_scores: Vec<(FrameNumber, usize)> = Vec::new();

    for frame in scene_frame_range.start_frame..=scene_frame_range.end_frame {
        if solved_frames.contains(&frame) {
            continue;
        }
        if let Some(pool) = candidate_pool {
            if !pool.contains(&frame) {
                continue;
            }
        }
        let mut count = 0usize;
        for &marker_idx in marker_indices {
            if bundle_positions.contains_key(&marker_idx)
                && observations.is_visible(marker_idx, frame)
            {
                count += 1;
            }
        }
        if count >= min_solvable {
            frame_scores.push((frame, count));
        }
    }

    // Sort descending by solvable count: highest solvability first.
    frame_scores.sort_unstable_by(|a, b| b.1.cmp(&a.1));

    frame_scores
        .into_iter()
        .take(max_candidates)
        .map(|(f, _)| f)
        .collect()
}

/// Find the best next unsolved frames for the final pass.
///
/// Uses max-diversity traversal ordering when a frame graph is available;
/// falls back to sequential ordering otherwise.
pub fn find_best_next_unsolved_frames(
    scene_frame_range: &FrameRange,
    solved_frames: &BTreeSet<FrameNumber>,
    frame_graph: Option<&FrameGraph>,
) -> Vec<FrameNumber> {
    if let Some(graph) = frame_graph {
        let max_candidates = scene_frame_range.frame_count() as usize;
        let candidates = generate_unsolved_frames_from_frame_graph(
            graph,
            scene_frame_range,
            solved_frames,
            max_candidates,
        );
        if candidates.len() > 1 {
            return candidates;
        }
    }
    (scene_frame_range.start_frame..=scene_frame_range.end_frame)
        .filter(|f| !solved_frames.contains(f))
        .collect()
}
