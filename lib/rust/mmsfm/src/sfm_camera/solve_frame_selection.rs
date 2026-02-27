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

use std::collections::{BTreeSet, HashMap, HashSet};
use std::time::Instant;

use mmio::uvtrack_reader::{FrameNumber, FrameRange, MarkersData};

use super::constants::RECOMENDED_MARKERS_FOR_PNP;
use super::frame_graph::{FrameEdge, FrameGraph};
use super::frame_score::{compute_parallax_residual, FrameAnalysisResult};
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
    // Frames further apart are unlikely to share enough observations.
    // This reduces the number of pairs from O(n^2) to O(n x max_distance).
    let max_frame_distance = if num_frames > 500 {
        // For large datasets, limit to reasonable temporal window.
        500
    } else {
        // For small datasets, consider all pairs.
        num_frames
    };

    let index_build_start = Instant::now();

    // Build index structures for O(1) lookups.
    // Map: frame_number -> set of marker indices visible in that frame.
    let mut frame_to_markers: HashMap<FrameNumber, HashSet<usize>> =
        HashMap::new();
    // Map: (marker_idx, frame_number) -> (u, v) coordinates.
    let mut marker_coords: HashMap<(usize, FrameNumber), (f32, f32)> =
        HashMap::new();

    for &marker_idx in marker_indices {
        if marker_idx >= markers.frame_data.len() {
            continue;
        }
        let frame_data = &markers.frame_data[marker_idx];
        for (k, &frame_num) in frame_data.frames.iter().enumerate() {
            // Add to frame_to_markers mapping.
            frame_to_markers
                .entry(frame_num)
                .or_insert_with(HashSet::new)
                .insert(marker_idx);

            // Store coordinates.
            let u = frame_data.u_coords[k] as f32 - 0.5;
            let v = frame_data.v_coords[k] as f32 - 0.5;
            marker_coords.insert((marker_idx, frame_num), (u, v));
        }
    }

    mm_eprintln_debug!(
        "  Index build: {:.3}s",
        index_build_start.elapsed().as_secs_f64()
    );

    let uniformity_start = Instant::now();

    // Pre-compute uniformity for each frame.
    for (i, &frame_num) in frame_numbers.iter().enumerate() {
        let mut points_x = Vec::new();
        let mut points_y = Vec::new();

        if let Some(visible_markers) = frame_to_markers.get(&frame_num) {
            for &marker_idx in visible_markers {
                if let Some(&(u, v)) =
                    marker_coords.get(&(marker_idx, frame_num))
                {
                    points_x.push(u);
                    points_y.push(v);
                }
            }
        }

        graph.calculate_and_set_uniformity(i as u32, &points_x, &points_y);
    }

    // Populate per-frame marker indices (sorted).
    for (i, &frame_num) in frame_numbers.iter().enumerate() {
        if let Some(visible_markers) = frame_to_markers.get(&frame_num) {
            let mut sorted: Vec<usize> =
                visible_markers.iter().copied().collect();
            sorted.sort_unstable();
            graph.set_frame_markers(i as u32, sorted);
        }
    }

    mm_eprintln_debug!(
        "  Uniformity + markers: {:.3}s",
        uniformity_start.elapsed().as_secs_f64()
    );

    let edge_build_start = Instant::now();
    let mut pairs_considered = 0usize;

    // Build edges between pairs of frames within max_frame_distance.
    // NOTE: This could be parallelized with rayon for even faster performance (currently single-threaded).
    for i in 0..num_frames {
        let frame_a = frame_numbers[i];

        // Early exit if frame_a has no markers.
        let markers_a = match frame_to_markers.get(&frame_a) {
            Some(m) if !m.is_empty() => m,
            _ => continue,
        };

        let max_j = (i + max_frame_distance + 1).min(num_frames);
        for j in (i + 1)..max_j {
            pairs_considered += 1;

            let frame_b = frame_numbers[j];

            // Find shared markers using set intersection.
            let markers_b = match frame_to_markers.get(&frame_b) {
                Some(m) if !m.is_empty() => m,
                _ => continue,
            };

            let shared_markers: Vec<usize> =
                markers_a.intersection(markers_b).copied().collect();

            let num_observations = shared_markers.len();
            if num_observations < RECOMENDED_MARKERS_FOR_PNP {
                continue;
            }

            // Collect points for parallax computation.
            let mut points_a = Vec::with_capacity(num_observations);
            let mut points_b = Vec::with_capacity(num_observations);

            for marker_idx in shared_markers {
                if let Some(&pt_a) = marker_coords.get(&(marker_idx, frame_a)) {
                    if let Some(&pt_b) =
                        marker_coords.get(&(marker_idx, frame_b))
                    {
                        points_a.push(pt_a);
                        points_b.push(pt_b);
                    }
                }
            }

            // Compute simple parallax metric (mean displacement).
            let parallax = compute_parallax_residual(&points_a, &points_b);

            let edge = FrameEdge::new(num_observations as i32, parallax);
            graph.set_edge(i as u32, j as u32, edge);
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

    // Build a Maximum Spanning Tree from the strongest frame connections,
    // then find a Connected Dominating Set - a small subset of frames that
    // "covers" all others. Uses observation count as weight since nearby
    // frames often have zero parallax.
    let spanning_tree = frame_graph.maximum_spanning_tree_by_observations();
    if DEBUG {
        frame_graph.print_metrics("Full graph");
        spanning_tree.print_metrics("Maximum Spanning Tree (observations)");
    }

    let dominating_set = spanning_tree.compute_connected_dominating_set();
    mm_eprintln_debug!(
        "  Connected Dominating Set result: {} vertices in dominating set",
        dominating_set.len()
    );
    if dominating_set.is_empty() {
        mm_eprintln_debug!(
            "  Connected Dominating Set returned empty - Maximum Spanning Tree may be disconnected."
        );
        return None;
    }
    let all_frame_numbers: Vec<FrameNumber> =
        (scene_frame_range.start_frame..=scene_frame_range.end_frame).collect();
    let mut frame_numbers: BTreeSet<FrameNumber> = dominating_set
        .iter()
        .filter_map(|&idx| all_frame_numbers.get(idx as usize).copied())
        .collect();
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

fn generate_unsolved_frames_full_frame_range(
    scene_frame_range: &FrameRange,
    solved_frames: &BTreeSet<FrameNumber>,
) -> Vec<FrameNumber> {
    (scene_frame_range.start_frame..=scene_frame_range.end_frame)
        .filter(|f| !solved_frames.contains(&(*f as FrameNumber)))
        .collect()
}

/// Select unsolved frames using the frame graph.
///
/// Prioritises skeleton frames first; falls back to all unsolved frames if
/// none are available. Returns (frame numbers, skeleton_frames_were_tried).
fn generate_unsolved_frames_from_frame_graph(
    frame_graph: &FrameGraph,
    scene_frame_range: &FrameRange,
    solved_frames: &BTreeSet<FrameNumber>,
    min_connections: usize,
    max_candidates: usize,
    skeleton_frames: Option<&BTreeSet<FrameNumber>>,
    final_rounds: bool,
) -> (Vec<FrameNumber>, bool) {
    // Convert solved frame numbers to frame graph indices.
    let frame_numbers: Vec<FrameNumber> =
        (scene_frame_range.start_frame..=scene_frame_range.end_frame).collect();

    // Build mapping from frame number to graph index.
    let frame_to_index: HashMap<FrameNumber, u32> = frame_numbers
        .iter()
        .enumerate()
        .map(|(i, &f)| (f, i as u32))
        .collect();

    // Convert solved frames to graph indices.
    let solved_indices: Vec<u32> = solved_frames
        .iter()
        .filter_map(|&f| frame_to_index.get(&f).copied())
        .collect();
    if solved_indices.is_empty() {
        return (Vec::new(), false);
    }

    // If skeleton frames provided, try them first.
    if !final_rounds {
        if let Some(skeleton) = skeleton_frames {
            let unsolved_skeleton_frames: BTreeSet<FrameNumber> = skeleton
                .iter()
                .filter(|f| !solved_frames.contains(f))
                .copied()
                .collect();

            mm_eprintln_debug!(
                "    [skeleton] total={}, unsolved={}",
                skeleton.len(),
                unsolved_skeleton_frames.len(),
            );

            if !unsolved_skeleton_frames.is_empty() {
                // Try skeleton frames with caller's min_connections.
                let candidates = frame_graph.find_next_frames_batch(
                    &solved_indices,
                    min_connections,
                    max_candidates,
                    0.3,
                );
                mm_eprintln_debug!(
                    "    [skeleton] candidates with min_connections={}: {} total",
                    min_connections,
                    candidates.len()
                );
                let filtered: Vec<FrameNumber> = candidates
                    .iter()
                    .map(|c| frame_numbers[c.frame_id as usize])
                    .filter(|f| unsolved_skeleton_frames.contains(f))
                    .collect();
                mm_eprintln_debug!(
                    "    [skeleton] after filter: {} frames = {}",
                    filtered.len(),
                    format_frame_list(&filtered)
                );
                if !filtered.is_empty() {
                    mm_eprintln_debug!(
                        "    [skeleton] Returning skeleton frames"
                    );
                    return (filtered, true);
                }

                // Relax to min_connections=1.
                if min_connections != 1 {
                    let candidates = frame_graph.find_next_frames_batch(
                        &solved_indices,
                        1,
                        max_candidates,
                        0.3,
                    );
                    mm_eprintln_debug!(
                        "    [skeleton] relaxed candidates with min_connections=1: {} total",
                        candidates.len()
                    );
                    let filtered: Vec<FrameNumber> = candidates
                        .iter()
                        .map(|c| frame_numbers[c.frame_id as usize])
                        .filter(|f| unsolved_skeleton_frames.contains(f))
                        .collect();
                    mm_eprintln_debug!(
                        "    [skeleton] after relaxed filter: {} frames = {}",
                        filtered.len(),
                        format_frame_list(&filtered)
                    );
                    if !filtered.is_empty() {
                        mm_eprintln_debug!(
                            "    [skeleton] Returning skeleton frames (relaxed)"
                        );
                        return (filtered, true);
                    }
                }

                mm_eprintln_debug!("    [skeleton] No skeleton frames found in frame graph, signalling skeleton exhausted");
                // Skeleton was attempted but no candidates connected
                // to solved frames - signal this so the caller can
                // switch to the final pass.
                return (Vec::new(), true);
            } else {
                // All skeleton frames already solved - draft pass is
                // complete, signal to switch to final.
                mm_eprintln_debug!(
                    "    [skeleton] All skeleton frames solved, signalling draft complete"
                );
                return (Vec::new(), true);
            }
        }
    }

    let result: Vec<FrameNumber> = {
        // Fall back to all unsolved frames using max-diversity
        // traversal ordering.
        mm_eprintln_debug!("    [all frames] Using max-diversity traversal");

        let traversal = frame_graph
            .compute_max_diversity_traversal(RECOMENDED_MARKERS_FOR_PNP);

        // Walk the pre-computed diversity order, skip solved frames,
        // return up to max_candidates.
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
    };

    if DEBUG && !result.is_empty() {
        mm_eprintln_debug!(
            "    [all frames] returning {} frames = {}",
            result.len(),
            format_frame_list(&result)
        );
    }

    (result, false)
}

/// Find the best next unsolved frames to attempt solving.
///
/// Prioritises skeleton frames; falls back to all unsolved frames if needed.
/// Returns (frame numbers to attempt, skeleton_frames_were_tried).
pub fn find_best_next_unsolved_frames(
    scene_frame_range: &FrameRange,
    solved_frames: &BTreeSet<FrameNumber>,
    frame_graph: Option<&FrameGraph>,
    skeleton_frames: Option<&BTreeSet<FrameNumber>>,
    final_rounds: bool,
) -> (Vec<FrameNumber>, bool) {
    // Use frame graph for intelligent frame selection.
    if let Some(graph) = frame_graph {
        let min_connections = 2;
        let max_candidates = scene_frame_range.frame_count() as usize;
        let (candidates, skeleton_tried) =
            generate_unsolved_frames_from_frame_graph(
                graph,
                scene_frame_range,
                solved_frames,
                min_connections,
                max_candidates,
                skeleton_frames,
                final_rounds,
            );

        if candidates.len() > 1 || skeleton_tried {
            // Return candidates (possibly empty if skeleton
            // pass is exhausted - the caller will handle it).
            (candidates, skeleton_tried)
        } else {
            // Fallback if frame graph returns nothing.
            (
                generate_unsolved_frames_full_frame_range(
                    scene_frame_range,
                    solved_frames,
                ),
                false,
            )
        }
    } else {
        // Fallback if frame graph not built.
        (
            generate_unsolved_frames_full_frame_range(
                scene_frame_range,
                solved_frames,
            ),
            false,
        )
    }
}
