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

use anyhow::Result;

use mmio::uvtrack_reader::{FrameData, FrameNumber, FrameRange, MarkersData};

use crate::sfm_camera::constants::UNIFORMITY_GRID_SIZE_MAX;

pub type FrameCount = u16;

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

// Point coordinate system constants.
const POINT_MIN_X: f32 = -0.5;
const POINT_MIN_Y: f32 = -0.5;
const POINT_MAX_X: f32 = 0.5;
const POINT_MAX_Y: f32 = 0.5;
const POINT_WIDTH: f32 = 1.0;
const POINT_HEIGHT: f32 = 1.0;

// Algorithm configuration constants.
const MIN_MARKER_COUNT: usize = 6;
const MIN_MARKERS_FOR_PARALLAX: usize = 6;
const MIN_MARKERS_FOR_UNIFORMITY: usize = 6;

const MAXIMUM_MARKER_COUNT: FrameCount = 8;

/// Calculate grid-based uniformity.
///
/// Grid-based point counting is based on the paper
/// "Structure-from-Motion Revisited" by Johannes L. Schonberger
/// and Jan-Michael Frahm, published in 2016, section
/// "4.2. Next Best View Selection".
///
/// Returns a value between 0.0 (highly clustered) and 1.0 (perfectly uniform).
pub fn calculate_uniformity(
    // TODO: Iterate over &[(f32, f32)] rather than individual arrays.
    points_x: &[f32],
    points_y: &[f32],
    point_count: usize,
    count_bins: &mut [FrameCount],
) -> f32 {
    if point_count == 0 {
        return 0.0; // No points to analyze.
    }
    if point_count == 1 {
        return 1.0; // Single point is considered uniform.
    }
    assert!(!points_x.is_empty());
    assert!(!points_y.is_empty());

    let count_bins_count_max =
        UNIFORMITY_GRID_SIZE_MAX as usize * UNIFORMITY_GRID_SIZE_MAX as usize;
    assert!(count_bins.len() == count_bins_count_max);

    // For typical use cases of 10-20 points, this will return 3-4
    // (3x3 or 4x4).
    let grid_size: u8 = if point_count <= 6 {
        2
    } else if point_count <= 12 {
        3
    } else if point_count <= 30 {
        4
    } else {
        5
    };
    let count_bins_count = grid_size as usize * grid_size as usize;

    // Count points in each grid cell.
    //
    // Clear bins.
    for count in count_bins[0..count_bins_count].iter_mut() {
        *count = 0;
    }

    let cell_width = POINT_WIDTH / grid_size as f32;
    let cell_height = POINT_HEIGHT / grid_size as f32;

    for (point_x, point_y) in points_x.iter().zip(points_y) {
        if point_x.is_nan() || point_y.is_nan() {
            continue;
        }
        if !(*point_x >= POINT_MIN_X
            && *point_x <= POINT_MAX_X
            && *point_y >= POINT_MIN_Y
            && *point_y <= POINT_MAX_Y)
        {
            // TODO: Put the point in the closest bin.
            continue;
        }

        // Calculate which cell this point belongs to.
        let col = ((point_x - POINT_MIN_X) / cell_width) as u8;
        let row = ((point_y - POINT_MIN_Y) / cell_height) as u8;

        // Clamp to grid bounds (handles edge cases with points exactly on boundary).
        let col = col.min(grid_size - 1);
        let row = row.min(grid_size - 1);

        let index = row * grid_size + col;
        count_bins[index as usize] += 1;
    }

    // Calculate coefficient of variation from counts.
    let cv = if count_bins_count == 0 {
        0.0
    } else {
        // Calculate mean.
        let sum: u16 = count_bins[0..count_bins_count].iter().sum();
        let mean = sum as f32 / count_bins_count as f32;

        if mean == 0.0 {
            0.0
        } else {
            // Calculate standard deviation.
            let variance = count_bins[0..count_bins_count]
                .iter()
                .map(|&count| {
                    let diff = count as f32 - mean;
                    diff * diff
                })
                .sum::<f32>()
                / count_bins_count as f32;

            let std_dev = variance.sqrt();

            // Coefficient of variation.
            std_dev / mean
        }
    };

    // Convert CV to uniformity score [0, 1].
    //
    // Using exp(-cv) gives a smooth decay from 1 to 0 as CV
    // increases.
    f32::exp(-cv)
}

type MarkerCount = u16;

#[derive(Debug, Clone)]
pub struct FrameAnalysisResult {
    /// Per-frame uniformity scores (0.0 = clustered, 1.0 = uniform).
    pub uniformity_scores: Vec<f32>,
    /// Number of markers visible per frame.
    pub per_frame_marker_counts: Vec<MarkerCount>,
    /// Indices of selected optimal markers.
    pub selected_marker_indices: Vec<usize>,
    /// Frame numbers where all selected markers are visible.
    pub common_frame_numbers: Vec<FrameNumber>,
    /// U coordinates for all markers across all frames (may contain NaN).
    pub marker_frame_u_data: Vec<f32>,
    /// V coordinates for all markers across all frames (may contain NaN).
    pub marker_frame_v_data: Vec<f32>,
    /// The two frame numbers with highest parallax from selected markers (None if less than 2 frames).
    pub highest_parallax_frame_pair: Option<(FrameNumber, FrameNumber)>,
    /// Parallax residual between the two highest parallax frames (0.0 if no valid pair).
    pub parallax_residual: f32,
}

#[derive(Debug, Clone)]
struct MarkerAnalysisData {
    marker_frame_counts: Vec<FrameCount>,
    marker_actual_counts: Vec<FrameCount>,
    marker_available_frames: Vec<bool>,
}

fn build_marker_analysis_data(
    markers: &MarkersData,
    scene_frame_range: FrameRange,
    maximum_marker_count: FrameCount,
) -> MarkerAnalysisData {
    let marker_count = markers.frame_data.len();
    let scene_frame_count = scene_frame_range.frame_count() as usize;

    let mut marker_frame_counts = vec![0; marker_count];
    let mut marker_available_frames =
        vec![false; marker_count * scene_frame_count];

    // Build availability matrix.
    for (marker_index, frame_data) in
        markers.frame_data.iter().enumerate().take(marker_count)
    {
        for &frame_number in &frame_data.frames {
            if frame_number >= scene_frame_range.start_frame
                && frame_number <= scene_frame_range.end_frame
            {
                let frame_index =
                    (frame_number - scene_frame_range.start_frame) as usize;
                let matrix_index =
                    marker_index * scene_frame_count + frame_index;
                marker_available_frames[matrix_index] = true;
            }
        }
    }

    // Count marker frequencies.
    let mut marker_actual_counts = vec![0 as FrameCount; marker_count];
    for marker_index in 0..marker_count {
        let mut count = 0 as FrameCount;
        let row_start = marker_index * scene_frame_count;
        for frame_index in 0..scene_frame_count {
            if marker_available_frames[row_start + frame_index] {
                count += 1;
            }
        }
        marker_actual_counts[marker_index] = count; // Store actual count.
        marker_frame_counts[marker_index] = count.min(maximum_marker_count); // Capped count.
    }

    MarkerAnalysisData {
        marker_frame_counts,
        marker_actual_counts,
        marker_available_frames,
    }
}

fn extract_frame_marker_positions(
    selected_markers: &[bool],
    markers: &MarkersData,
    frame_index: usize,
    scene_frame_range: FrameRange,
    // TODO: Combine both of these X and Y data into a single Vec
    // array.
    points_x: &mut Vec<f32>,
    points_y: &mut Vec<f32>,
) {
    points_x.clear();
    points_y.clear();

    for (marker_index, &is_selected) in selected_markers.iter().enumerate() {
        if !is_selected {
            continue;
        }

        let frame_data = &markers.frame_data[marker_index];
        let target_frame =
            scene_frame_range.start_frame + frame_index as FrameNumber;

        // Find the frame in this marker's data.
        for (data_index, &frame_number) in frame_data.frames.iter().enumerate()
        {
            if frame_number == target_frame {
                // Convert from 0.0-1.0 to -0.5 to +0.5 space.
                let u = frame_data.u_coords[data_index] as f32 - 0.5;
                let v = frame_data.v_coords[data_index] as f32 - 0.5;
                points_x.push(u);
                points_y.push(v);
                break;
            }
        }
    }
}

fn calculate_common_frames_for_markers(
    selected_markers: &[bool],
    analysis_data: &MarkerAnalysisData,
    scene_frame_count: usize,
) -> Vec<bool> {
    let mut common_frames = vec![true; scene_frame_count];
    let mut first_marker = true;

    for (marker_index, &is_selected) in selected_markers.iter().enumerate() {
        if !is_selected {
            continue;
        }

        let row_start = marker_index * scene_frame_count;
        if first_marker {
            for frame_index in 0..scene_frame_count {
                common_frames[frame_index] = analysis_data
                    .marker_available_frames[row_start + frame_index];
            }
            first_marker = false;
        } else {
            for frame_index in 0..scene_frame_count {
                let marker_has_frame = analysis_data.marker_available_frames
                    [row_start + frame_index];
                common_frames[frame_index] =
                    common_frames[frame_index] && marker_has_frame;
            }
        }
    }

    common_frames
}

fn remove_temporal_outlier_marker(
    selected_markers: &mut [bool],
    markers: &MarkersData,
) -> bool {
    // Find the marker whose temporal range is most distant from others.
    let selected_indices: Vec<usize> = selected_markers
        .iter()
        .enumerate()
        .filter_map(|(idx, &sel)| if sel { Some(idx) } else { None })
        .collect();

    if selected_indices.is_empty() {
        return false;
    }

    // Calculate median start and end frames.
    let mut start_frames: Vec<FrameNumber> = Vec::new();
    let mut end_frames: Vec<FrameNumber> = Vec::new();
    for &marker_idx in &selected_indices {
        let frame_data = &markers.frame_data[marker_idx];
        if !frame_data.frames.is_empty() {
            start_frames.push(*frame_data.frames.first().unwrap());
            end_frames.push(*frame_data.frames.last().unwrap());
        }
    }

    if start_frames.is_empty() {
        return false;
    }

    start_frames.sort_unstable();
    end_frames.sort_unstable();
    let median_start = start_frames[start_frames.len() / 2];
    let median_end = end_frames[end_frames.len() / 2];

    // Find marker with maximum distance from median range.
    let mut max_distance = 0;
    let mut outlier_marker = None;

    for &marker_idx in &selected_indices {
        let frame_data = &markers.frame_data[marker_idx];
        if frame_data.frames.is_empty() {
            continue;
        }

        let start = *frame_data.frames.first().unwrap();
        let end = *frame_data.frames.last().unwrap();

        // Calculate distance from median range.
        let start_dist =
            (start as i64 - median_start as i64).unsigned_abs() as u32;
        let end_dist = (end as i64 - median_end as i64).unsigned_abs() as u32;
        let total_dist = start_dist + end_dist;

        if total_dist > max_distance {
            max_distance = total_dist;
            outlier_marker = Some(marker_idx);
        }
    }

    if let Some(marker_index) = outlier_marker {
        if DEBUG {
            let frame_data = &markers.frame_data[marker_index];
            let start = frame_data.frames.first().unwrap_or(&0);
            let end = frame_data.frames.last().unwrap_or(&0);
            mm_eprintln_debug!("    Removing temporal outlier marker {} (frames {}-{}, distance={})",
                     marker_index, start, end, max_distance);
        }
        selected_markers[marker_index] = false;
        true
    } else {
        false
    }
}

fn remove_marker_with_fewest_frames(
    selected_markers: &mut [bool],
    analysis_data: &MarkerAnalysisData,
    use_actual_counts: bool,
) -> bool {
    let mut min_frame_count = FrameCount::MAX;
    let mut marker_to_remove = None;

    // Find marker with minimum frame count among selected markers.
    for (marker_index, &is_selected) in selected_markers.iter().enumerate() {
        if is_selected {
            // Use actual or capped counts depending on context.
            let frame_count = if use_actual_counts {
                analysis_data.marker_actual_counts[marker_index]
            } else {
                analysis_data.marker_frame_counts[marker_index]
            };

            if frame_count < min_frame_count {
                min_frame_count = frame_count;
                marker_to_remove = Some(marker_index);
            }
        }
    }

    if let Some(marker_index) = marker_to_remove {
        if DEBUG {
            let count_type = if use_actual_counts {
                "actual"
            } else {
                "capped"
            };
            let count_value = if use_actual_counts {
                analysis_data.marker_actual_counts[marker_index]
            } else {
                analysis_data.marker_frame_counts[marker_index]
            };
            mm_eprintln_debug!(
                "    Removing marker {} with {} frames ({} count)",
                marker_index,
                count_value,
                count_type
            );
        }
        selected_markers[marker_index] = false;
        true
    } else {
        false
    }
}

fn filter_frames_by_uniformity(
    selected_markers: &[bool],
    markers: &MarkersData,
    common_frame_indices: &[usize],
    scene_frame_range: FrameRange,
) -> Vec<usize> {
    if common_frame_indices.len() <= 2 {
        // With very few frames, don't filter - we need them all.
        return common_frame_indices.to_vec();
    }

    let mut frame_uniformities = Vec::new();
    // TODO: Use a single Vec for X and Y, rather than two different
    // vectors.
    let mut points_x = Vec::new();
    let mut points_y = Vec::new();

    // Calculate uniformity for each common frame.
    for &frame_index in common_frame_indices {
        extract_frame_marker_positions(
            selected_markers,
            markers,
            frame_index,
            scene_frame_range,
            &mut points_x,
            &mut points_y,
        );

        let uniformity = if points_x.len() > MIN_MARKERS_FOR_UNIFORMITY {
            let grid_count = UNIFORMITY_GRID_SIZE_MAX as usize
                * UNIFORMITY_GRID_SIZE_MAX as usize;
            let mut count_bins = vec![0; grid_count];

            calculate_uniformity(
                &points_x,
                &points_y,
                points_x.len(),
                &mut count_bins,
            )
        } else {
            0.0 // Low uniformity for frames with insufficient markers.
        };

        frame_uniformities.push((frame_index, uniformity));
    }

    // Calculate median uniformity.
    let mut uniformity_values: Vec<f32> = frame_uniformities
        .iter()
        .map(|(_, uniformity)| *uniformity)
        .collect();
    uniformity_values.sort_by(|a, b| a.partial_cmp(b).unwrap());

    let median_uniformity = if uniformity_values.is_empty() {
        0.0
    } else {
        let mid = uniformity_values.len() / 2;
        uniformity_values[mid]
    };

    // Filter frames with uniformity >= median.
    let filtered_frames: Vec<usize> = frame_uniformities
        .into_iter()
        .filter(|(_, uniformity)| *uniformity >= median_uniformity)
        .map(|(frame_index, _)| frame_index)
        .collect();

    // Ensure we have at least 2 frames for parallax computation.
    if filtered_frames.len() >= 2 {
        filtered_frames
    } else {
        // Fallback: return all frames if filtering removes too many.
        common_frame_indices.to_vec()
    }
}

fn compute_all_parallax_and_find_best(
    selected_markers: &[bool],
    markers: &MarkersData,
    common_frames: &[bool],
    scene_frame_range: FrameRange,
) -> (Vec<f32>, Option<(usize, usize, f32)>) {
    let mut all_parallax_values = Vec::new();
    let mut best_parallax = 0.0;
    let mut best_frame_pair = None;

    let common_frame_indices: Vec<usize> = common_frames
        .iter()
        .enumerate()
        .filter_map(|(i, &is_common)| if is_common { Some(i) } else { None })
        .collect();

    if common_frame_indices.len() < 2 {
        return (all_parallax_values, None);
    }

    // Filter frames by uniformity to reduce computational load.
    let filtered_frame_indices = filter_frames_by_uniformity(
        selected_markers,
        markers,
        &common_frame_indices,
        scene_frame_range,
    );

    // Debug information about filtering effectiveness.
    let original_pairs =
        (common_frame_indices.len() * (common_frame_indices.len() - 1)) / 2;
    let filtered_pairs =
        (filtered_frame_indices.len() * (filtered_frame_indices.len() - 1)) / 2;
    let reduction_percent = if original_pairs > 0 {
        100.0 * (1.0 - filtered_pairs as f32 / original_pairs as f32)
    } else {
        0.0
    };
    mm_eprintln_debug!("Uniformity filtering: {} -> {} frames ({:.1}% reduction in frame pairs: {} -> {})",
                  common_frame_indices.len(),
                  filtered_frame_indices.len(),
                  reduction_percent,
                  original_pairs,
                  filtered_pairs);
    if filtered_frame_indices.len() < 2 {
        return (all_parallax_values, None);
    }

    // Single pass: compute all parallax values and track the best.
    for i in 0..filtered_frame_indices.len() {
        for j in (i + 1)..filtered_frame_indices.len() {
            let frame_a = filtered_frame_indices[i];
            let frame_b = filtered_frame_indices[j];

            // Extract marker positions for both frames.
            let mut points_a_x = Vec::new();
            let mut points_a_y = Vec::new();
            let mut points_b_x = Vec::new();
            let mut points_b_y = Vec::new();

            extract_frame_marker_positions(
                selected_markers,
                markers,
                frame_a,
                scene_frame_range,
                &mut points_a_x,
                &mut points_a_y,
            );
            extract_frame_marker_positions(
                selected_markers,
                markers,
                frame_b,
                scene_frame_range,
                &mut points_b_x,
                &mut points_b_y,
            );

            // Convert to coordinate pairs and compute parallax.
            let points_a: Vec<(f32, f32)> = points_a_x
                .iter()
                .zip(points_a_y.iter())
                .map(|(&x, &y)| (x, y))
                .collect();
            let points_b: Vec<(f32, f32)> = points_b_x
                .iter()
                .zip(points_b_y.iter())
                .map(|(&x, &y)| (x, y))
                .collect();

            let parallax = compute_parallax_residual(&points_a, &points_b);
            if parallax > 0.0 {
                all_parallax_values.push(parallax);

                // Track the best frame pair.
                if parallax > best_parallax {
                    best_parallax = parallax;
                    best_frame_pair = Some((frame_a, frame_b, parallax));
                }
            }
        }
    }

    (all_parallax_values, best_frame_pair)
}

#[derive(Debug, Clone)]
struct MarkerSelectionResult {
    selected_markers: Vec<bool>,
    common_frames: Vec<bool>,
    selected_count: usize,
}

fn select_markers_with_combined_scoring(
    analysis_data: &MarkerAnalysisData,
    markers: &MarkersData,
    scene_frame_range: FrameRange,
    min_marker_count: usize,
) -> MarkerSelectionResult {
    let marker_count = analysis_data.marker_frame_counts.len();
    let scene_frame_count = scene_frame_range.frame_count() as usize;

    // Step 1: Start with all markers selected, but ensure we start
    // with a feasible set.
    let mut selected_markers = vec![true; marker_count];
    let mut selected_count = marker_count;

    // Remove markers with zero frame count.
    for (marker_index, &frame_count) in
        analysis_data.marker_frame_counts.iter().enumerate()
    {
        if frame_count == 0 {
            selected_markers[marker_index] = false;
            selected_count -= 1;
        }
    }

    mm_eprintln_debug!(
        "Initial selection: {} markers after removing zero-count markers",
        selected_count
    );

    // If starting with all markers leads to no common frames,
    // gradually reduce until we have some common frames.
    loop {
        // Step 2: Calculate common frames for current selection.
        let common_frames = calculate_common_frames_for_markers(
            &selected_markers,
            analysis_data,
            scene_frame_count,
        );

        // Count common frames.
        let common_frame_count = common_frames.iter().filter(|&&x| x).count();

        if common_frame_count >= 2 {
            // We have enough common frames, now try to optimize for
            // parallax.
            let mut current_common_frames = common_frames;
            loop {
                // Step 3: Compute all parallax values AND find best
                // frame pair in one pass.
                let (all_parallax_values, best_frame_result) =
                    compute_all_parallax_and_find_best(
                        &selected_markers,
                        markers,
                        &current_common_frames,
                        scene_frame_range,
                    );

                if let Some((_frame_a, _frame_b, best_parallax)) =
                    best_frame_result
                {
                    // Step 4: Calculate dynamic threshold using 75th percentile.
                    let dynamic_threshold = {
                        let smallest_parallax_value = 0.00001;
                        if all_parallax_values.is_empty() {
                            // Fallback threshold.
                            smallest_parallax_value
                        } else {
                            let mut sorted = all_parallax_values.clone();
                            sorted.sort_by(|a, b| a.partial_cmp(b).unwrap());

                            let percentile = 0.75;
                            let index = ((sorted.len() as f32 * percentile)
                                .round()
                                as usize)
                                .min(sorted.len() - 1);

                            // Ensure minimum threshold to avoid degenerate cases.
                            sorted[index].max(smallest_parallax_value)
                        }
                    };

                    // Step 5: Check if best parallax exceeds threshold.
                    if best_parallax > dynamic_threshold {
                        // Sufficient parallax found - return current selection.
                        return MarkerSelectionResult {
                            selected_markers,
                            common_frames: current_common_frames,
                            selected_count,
                        };
                    }
                }

                // Step 5: Remove marker with fewest frames and continue.
                if selected_count <= min_marker_count {
                    // Can't remove more markers - return current
                    // selection even if parallax is insufficient.
                    return MarkerSelectionResult {
                        selected_markers,
                        common_frames: current_common_frames,
                        selected_count,
                    };
                }

                // Use actual counts when optimizing with common frames.
                let removed = remove_marker_with_fewest_frames(
                    &mut selected_markers,
                    analysis_data,
                    true, // use_actual_counts
                );
                if removed {
                    selected_count -= 1;
                } else {
                    // No more markers to remove.
                    return MarkerSelectionResult {
                        selected_markers,
                        common_frames: current_common_frames,
                        selected_count,
                    };
                }

                // Recalculate common frames after removing a marker.
                current_common_frames = calculate_common_frames_for_markers(
                    &selected_markers,
                    analysis_data,
                    scene_frame_count,
                );

                let new_common_frame_count =
                    current_common_frames.iter().filter(|&&x| x).count();
                if new_common_frame_count < 2 {
                    // If we lost too many common frames, break and
                    // return what we have.
                    return MarkerSelectionResult {
                        selected_markers,
                        common_frames: current_common_frames,
                        selected_count,
                    };
                }
            }
        } else {
            // Not enough common frames, remove a marker to try to get
            // some overlap.
            mm_eprintln_debug!("  Not enough common frames ({}), trying to remove a marker (selected_count={})", common_frame_count, selected_count);

            if selected_count <= min_marker_count {
                // Can't remove more markers - return what we have
                // even if no common frames.
                mm_eprintln_debug!("  Reached minimum marker count, returning with {} common frames", common_frame_count);
                return MarkerSelectionResult {
                    selected_markers,
                    common_frames,
                    selected_count,
                };
            }

            // When seeking initial overlap, remove temporal outliers first.
            let removed =
                remove_temporal_outlier_marker(&mut selected_markers, markers);
            if removed {
                selected_count -= 1;
            } else {
                // No more markers to remove.
                return MarkerSelectionResult {
                    selected_markers,
                    common_frames,
                    selected_count,
                };
            }
        }
    }
}

#[derive(Debug, Clone)]
struct SimilarityTransform2D {
    translation: (f32, f32), // tx, ty
    rotation: f32,           // angle in radians.
    scale: f32,              // uniform scale factor.
}

impl SimilarityTransform2D {
    fn new(translation: (f32, f32), rotation: f32, scale: f32) -> Self {
        Self {
            translation,
            rotation,
            scale,
        }
    }

    fn transform_point(&self, point: (f32, f32)) -> (f32, f32) {
        let cos_r = self.rotation.cos();
        let sin_r = self.rotation.sin();
        // Apply scale, then rotation, then translation.
        let x = self.scale * (cos_r * point.0 - sin_r * point.1)
            + self.translation.0;
        let y = self.scale * (sin_r * point.0 + cos_r * point.1)
            + self.translation.1;
        (x, y)
    }
}

pub fn compute_parallax_residual(
    points_a: &[(f32, f32)],
    points_b: &[(f32, f32)],
) -> f32 {
    if points_a.len() != points_b.len()
        || points_a.len() < MIN_MARKERS_FOR_PARALLAX
    {
        return 0.0;
    }
    assert!(!points_a.is_empty());
    assert!(!points_b.is_empty());

    // Fit similarity transform (translation + rotation + scale).
    let similarity_transform = if points_a.len() < 2 {
        SimilarityTransform2D::new((0.0, 0.0), 0.0, 1.0)
    } else {
        // Compute centroids.
        let centroid_a = {
            let sum_x: f32 = points_a.iter().map(|p| p.0).sum();
            let sum_y: f32 = points_a.iter().map(|p| p.1).sum();
            let n = points_a.len() as f32;
            (sum_x / n, sum_y / n)
        };

        let centroid_b = {
            let sum_x: f32 = points_b.iter().map(|p| p.0).sum();
            let sum_y: f32 = points_b.iter().map(|p| p.1).sum();
            let n = points_b.len() as f32;
            (sum_x / n, sum_y / n)
        };

        // Center point sets.
        let centered_a: Vec<(f32, f32)> = points_a
            .iter()
            .map(|p| (p.0 - centroid_a.0, p.1 - centroid_a.1))
            .collect();
        let centered_b: Vec<(f32, f32)> = points_b
            .iter()
            .map(|p| (p.0 - centroid_b.0, p.1 - centroid_b.1))
            .collect();

        // Compute cross-covariance matrix elements and scale factors.
        let mut sum_xx = 0.0f32;
        let mut sum_xy = 0.0f32;
        let mut sum_yx = 0.0f32;
        let mut sum_yy = 0.0f32;
        let mut sq_sum_a = 0.0f32;
        let mut sq_sum_b = 0.0f32;

        for (pa, pb) in centered_a.iter().zip(centered_b.iter()) {
            sum_xx += pa.0 * pb.0;
            sum_xy += pa.0 * pb.1;
            sum_yx += pa.1 * pb.0;
            sum_yy += pa.1 * pb.1;
            sq_sum_a += pa.0 * pa.0 + pa.1 * pa.1;
            sq_sum_b += pb.0 * pb.0 + pb.1 * pb.1;
        }

        // Rotation angle from cross-correlation matrix.
        let rotation = f32::atan2(sum_xy - sum_yx, sum_xx + sum_yy);

        // Scale factor from the ratio of point cloud magnitudes.
        let scale = if sq_sum_a > 0.0 {
            (sq_sum_b / sq_sum_a).sqrt()
        } else {
            1.0
        };

        // Translation is difference in centroids.
        let translation =
            (centroid_b.0 - centroid_a.0, centroid_b.1 - centroid_a.1);

        SimilarityTransform2D::new(translation, rotation, scale)
    };

    // Compute residuals after similarity transform compensation.
    let residuals: Vec<f32> = points_a
        .iter()
        .zip(points_b.iter())
        .map(|(pa, pb)| {
            let transformed = similarity_transform.transform_point(*pa);
            const RESIDUAL_SCALE: f32 = 100.0;
            let dx = (transformed.0 - pb.0) * RESIDUAL_SCALE;
            let dy = (transformed.1 - pb.1) * RESIDUAL_SCALE;
            (dx * dx + dy * dy).sqrt()
        })
        .collect();

    // Compute mean and variance of the residuals.
    let count = residuals.len() as f32;
    let mean = residuals.iter().sum::<f32>() / count;

    let variance = residuals
        .iter()
        .map(|&r| {
            let diff = r - mean;
            diff * diff
        })
        .sum::<f32>()
        / count;

    // Use both mean and variance for the score. Higher variance indicates
    // more "structure" in the residual (parallax), rather than just
    // uniform noise or misalignment.
    mean.abs() * variance.abs()
}

pub fn analyze_frame_scoring_and_marker_selection(
    scene_frame_range: FrameRange,
    markers: &MarkersData,
) -> Result<FrameAnalysisResult> {
    let frames_data: &[FrameData] = &markers.frame_data;

    // Handle empty marker data case.
    if frames_data.is_empty() {
        // TODO: Should this just return an error?
        let scene_frame_count = scene_frame_range.frame_count() as usize;
        return Ok(FrameAnalysisResult {
            uniformity_scores: vec![0.0; scene_frame_count],
            per_frame_marker_counts: vec![0; scene_frame_count],
            selected_marker_indices: Vec::new(),
            common_frame_numbers: Vec::new(),
            marker_frame_u_data: Vec::new(),
            marker_frame_v_data: Vec::new(),
            highest_parallax_frame_pair: None,
            parallax_residual: 0.0,
        });
    }

    let scene_frame_count = scene_frame_range.frame_count() as usize;
    let mut uniformity_scores: Vec<f32> = vec![0.0; scene_frame_count];

    // Per-frame Marker count.
    let mut per_frame_marker_counts: Vec<MarkerCount> =
        vec![0; scene_frame_count];

    // Create a big array of f32 (marker_count * frame_count), then
    // fill it with data, and use that.
    let marker_count = frames_data.len();
    let uv_data_count = marker_count * scene_frame_count;
    // TODO: Use a single Vec for U and V, rather than two different
    // vectors.
    let mut marker_frame_u_data: Vec<f32> = vec![f32::NAN; uv_data_count];
    let mut marker_frame_v_data: Vec<f32> = vec![f32::NAN; uv_data_count];

    for (marker_index, frame_data) in frames_data.iter().enumerate() {
        for (frames_index, frame_number) in frame_data.frames.iter().enumerate()
        {
            if *frame_number < scene_frame_range.start_frame
                || *frame_number > scene_frame_range.end_frame
            {
                // Skip frames outside the desired range.
                continue;
            }

            let scene_frame_index: usize =
                (*frame_number - scene_frame_range.start_frame) as usize;

            // The U and V coordinates are in 0.0-1.0 space, but we
            // want it to be centered on 0.0; with -0.5 to +0.5.
            let u = frame_data.u_coords[frames_index] as f32 - 0.5_f32;
            let v = frame_data.v_coords[frames_index] as f32 - 0.5_f32;
            let uv_data_index =
                (scene_frame_index * marker_count) + marker_index;
            marker_frame_u_data[uv_data_index] = u;
            marker_frame_v_data[uv_data_index] = v;

            per_frame_marker_counts[scene_frame_index] += 1;
        }
    }

    let grid_count =
        UNIFORMITY_GRID_SIZE_MAX as usize * UNIFORMITY_GRID_SIZE_MAX as usize;
    let mut count_bins = vec![0; grid_count];

    for frame_number in
        scene_frame_range.start_frame..=scene_frame_range.end_frame
    {
        let scene_frame_index: usize =
            (frame_number - scene_frame_range.start_frame) as usize;
        let per_frame_marker_count = per_frame_marker_counts[scene_frame_index];

        let uv_data_index_min = scene_frame_index * marker_count;
        let uv_data_index_max = uv_data_index_min + marker_count;
        let u_slice =
            &marker_frame_u_data[uv_data_index_min..uv_data_index_max];
        let v_slice =
            &marker_frame_v_data[uv_data_index_min..uv_data_index_max];

        let uniformity = calculate_uniformity(
            u_slice,
            v_slice,
            per_frame_marker_count as usize,
            &mut count_bins,
        );
        uniformity_scores[scene_frame_index] = uniformity;
    }

    // Find the largest set of markers that are simultaneously visible
    // across the maximum number of frames, requiring at least 6 markers.
    let analysis_data: MarkerAnalysisData = build_marker_analysis_data(
        markers,
        scene_frame_range,
        MAXIMUM_MARKER_COUNT,
    );

    // Test with uniformity-enhanced selection.
    let combined_result: MarkerSelectionResult =
        select_markers_with_combined_scoring(
            &analysis_data,
            markers,
            scene_frame_range,
            MIN_MARKER_COUNT,
        );
    let combined_selected_indices: Vec<usize> = combined_result
        .selected_markers
        .iter()
        .enumerate()
        .filter_map(
            |(index, &is_selected)| {
                if is_selected {
                    Some(index)
                } else {
                    None
                }
            },
        )
        .collect();
    let combined_common_frame_numbers: Vec<FrameNumber> = combined_result
        .common_frames
        .iter()
        .enumerate()
        .filter_map(|(frame_index, &is_common)| {
            if is_common {
                Some(scene_frame_range.start_frame + frame_index as FrameNumber)
            } else {
                None
            }
        })
        .collect();

    if DEBUG {
        mm_eprintln_debug!(
            "Combined scoring: Selected {} markers {:?} across {} frames",
            combined_result.selected_count,
            combined_selected_indices,
            combined_common_frame_numbers.len()
        );

        // Debug: Show frame ranges for selected markers.
        for &marker_idx in &combined_selected_indices {
            let frame_data = &markers.frame_data[marker_idx];
            let min_frame = frame_data.frames.iter().min().unwrap_or(&0);
            let max_frame = frame_data.frames.iter().max().unwrap_or(&0);
            let count = frame_data.frames.len();
            mm_eprintln_debug!(
                "  Marker {}: frames {}-{} ({} observations)",
                marker_idx,
                min_frame,
                max_frame,
                count
            );
        }
    }

    // Use the combined results as the final output.
    let (_selected_marker_count, selected_marker_indices, common_frame_numbers) = (
        combined_result.selected_count,
        combined_selected_indices,
        combined_common_frame_numbers,
    );

    // Calculate the highest uniformity frame pair and parallax residual for selected markers.
    let selected_markers_mask: Vec<bool> = (0..marker_count)
        .map(|i| selected_marker_indices.contains(&i))
        .collect();

    let (highest_parallax_frame_pair, parallax_residual) =
        if common_frame_numbers.len() >= 2 {
            // Calculate common frames for selected markers.
            let analysis_data = build_marker_analysis_data(
                markers,
                scene_frame_range,
                MAXIMUM_MARKER_COUNT,
            );
            let common_frames = calculate_common_frames_for_markers(
                &selected_markers_mask,
                &analysis_data,
                scene_frame_count,
            );

            // Find the two highest parallax frames.
            let (_all_parallax_values, best_frame_result) =
                compute_all_parallax_and_find_best(
                    &selected_markers_mask,
                    markers,
                    &common_frames,
                    scene_frame_range,
                );

            if let Some((frame_a, frame_b, _parallax)) = best_frame_result {
                // Extract marker positions for the two selected frames.
                let mut points_a_x = Vec::new();
                let mut points_a_y = Vec::new();
                let mut points_b_x = Vec::new();
                let mut points_b_y = Vec::new();

                extract_frame_marker_positions(
                    &selected_markers_mask,
                    markers,
                    frame_a,
                    scene_frame_range,
                    &mut points_a_x,
                    &mut points_a_y,
                );

                extract_frame_marker_positions(
                    &selected_markers_mask,
                    markers,
                    frame_b,
                    scene_frame_range,
                    &mut points_b_x,
                    &mut points_b_y,
                );

                // Convert to coordinate pairs for parallax calculation.
                let points_a: Vec<(f32, f32)> = points_a_x
                    .iter()
                    .zip(points_a_y.iter())
                    .map(|(&x, &y)| (x, y))
                    .collect();
                let points_b: Vec<(f32, f32)> = points_b_x
                    .iter()
                    .zip(points_b_y.iter())
                    .map(|(&x, &y)| (x, y))
                    .collect();

                // Calculate parallax.
                let parallax = compute_parallax_residual(&points_a, &points_b);

                // Convert frame indices to frame numbers.
                let frame_number_a =
                    scene_frame_range.start_frame + frame_a as FrameNumber;
                let frame_number_b =
                    scene_frame_range.start_frame + frame_b as FrameNumber;

                (Some((frame_number_a, frame_number_b)), parallax)
            } else {
                (None, 0.0)
            }
        } else {
            (None, 0.0)
        };

    Ok(FrameAnalysisResult {
        uniformity_scores,
        per_frame_marker_counts,
        selected_marker_indices,
        common_frame_numbers,
        marker_frame_u_data,
        marker_frame_v_data,
        highest_parallax_frame_pair,
        parallax_residual,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use anyhow::bail;
    use std::path::Path;
    use std::path::PathBuf;

    use mmio::uvtrack_reader::parse_v1_file;

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

    fn construct_uvtrack_input_file_path(
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

    fn load_test_data(file_name: &str) -> Result<(FrameRange, MarkersData)> {
        let data_dir = find_data_dir()?;
        let in_file_path =
            construct_uvtrack_input_file_path(&data_dir, file_name)?;
        let (_file_info, markers) =
            parse_v1_file(&in_file_path.into_os_string())?;

        // Determine frame range from the data.
        let mut min_frame = u32::MAX;
        let mut max_frame = 0;
        for frame_data in &markers.frame_data {
            if let (Some(&first), Some(&last)) =
                (frame_data.frames.first(), frame_data.frames.last())
            {
                min_frame = min_frame.min(first);
                max_frame = max_frame.max(last);
            }
        }
        let scene_frame_range = FrameRange::new(min_frame, max_frame);

        Ok((scene_frame_range, markers))
    }

    fn validate_analysis_result(
        result: &FrameAnalysisResult,
        expected_marker_count: usize,
        expected_frame_count: usize,
    ) {
        assert_eq!(result.uniformity_scores.len(), expected_frame_count);
        assert_eq!(result.per_frame_marker_counts.len(), expected_frame_count);
        assert!(
            result.selected_marker_indices.len() >= MIN_MARKER_COUNT,
            "Should find at least {} markers, found {}",
            MIN_MARKER_COUNT,
            result.selected_marker_indices.len()
        );
        assert!(
            !result.common_frame_numbers.is_empty(),
            "Should find common frames"
        );

        // Validate that all selected marker indices are valid.
        for &marker_idx in &result.selected_marker_indices {
            assert!(
                marker_idx < expected_marker_count,
                "Marker index {} should be less than total markers {}",
                marker_idx,
                expected_marker_count
            );
        }
    }

    // Helper function to reduce code duplication in dataset tests.
    fn run_dataset_analysis(
        filename: &str,
        expected_marker_count: usize,
        dataset_name: &str,
    ) -> Result<()> {
        let (scene_frame_range, markers) = load_test_data(filename)?;
        assert_eq!(markers.len(), expected_marker_count);

        let analysis_result = analyze_frame_scoring_and_marker_selection(
            scene_frame_range,
            &markers,
        )?;
        let scene_frame_count = scene_frame_range.frame_count() as usize;
        validate_analysis_result(
            &analysis_result,
            expected_marker_count,
            scene_frame_count,
        );

        // Report basic statistics.
        println!("{} dataset analysis:", dataset_name);
        println!(
            "  - Selected {} optimal markers from {} total",
            analysis_result.selected_marker_indices.len(),
            expected_marker_count
        );
        println!(
            "  - Common frames: {} out of {}",
            analysis_result.common_frame_numbers.len(),
            scene_frame_count
        );

        // Report the chosen highest uniformity frames and parallax.
        if let Some((frame_a, frame_b)) =
            analysis_result.highest_parallax_frame_pair
        {
            println!(
                "  - Highest parallax frame pair: {} and {} (parallax residual: {:.4})",
                frame_a, frame_b, analysis_result.parallax_residual
            );

            // Display comprehensive parallax statistics for better context.
            let selected_markers_mask: Vec<bool> = (0..markers
                .frame_data
                .len())
                .map(|i| analysis_result.selected_marker_indices.contains(&i))
                .collect();

            let analysis_data = build_marker_analysis_data(
                &markers,
                scene_frame_range,
                MAXIMUM_MARKER_COUNT,
            );
            let common_frames = calculate_common_frames_for_markers(
                &selected_markers_mask,
                &analysis_data,
                scene_frame_count,
            );

            let (all_parallax_values, _) = compute_all_parallax_and_find_best(
                &selected_markers_mask,
                &markers,
                &common_frames,
                scene_frame_range,
            );

            if !all_parallax_values.is_empty() {
                println!(
                    "  - Parallax analysis: {} frame pairs",
                    all_parallax_values.len()
                );
            }
        } else {
            println!("  - No valid frame pair found for uniformity analysis");
        }

        // Check uniformity scores are reasonable.
        println!(
            "  - Uniformity scores count: {}",
            analysis_result.uniformity_scores.len()
        );

        // Verify marker counts per frame are reasonable.
        let max_markers_per_frame = analysis_result
            .per_frame_marker_counts
            .iter()
            .max()
            .unwrap_or(&0);
        println!(
            "  - Maximum markers visible in single frame: {}",
            max_markers_per_frame
        );

        // Test per-frame uniformity for selected markers (sample a few frames).
        let selected_markers_mask: Vec<bool> = (0..markers.frame_data.len())
            .map(|i| analysis_result.selected_marker_indices.contains(&i))
            .collect();

        let sample_frames =
            vec![0, scene_frame_count / 2, scene_frame_count - 1]; // First, middle, last.
        let mut uniformity_samples = Vec::new();
        let mut points_x = Vec::new();
        let mut points_y = Vec::new();

        for &frame_index in &sample_frames {
            if frame_index < scene_frame_count {
                extract_frame_marker_positions(
                    &selected_markers_mask,
                    &markers,
                    frame_index,
                    scene_frame_range,
                    &mut points_x,
                    &mut points_y,
                );

                if points_x.len() > 1 {
                    let grid_count = UNIFORMITY_GRID_SIZE_MAX as usize
                        * UNIFORMITY_GRID_SIZE_MAX as usize;
                    let mut count_bins = vec![0; grid_count];
                    let uniformity = calculate_uniformity(
                        &points_x,
                        &points_y,
                        points_x.len(),
                        &mut count_bins,
                    );
                    uniformity_samples.push(uniformity);
                }
            }
        }

        if !uniformity_samples.is_empty() {
            let avg_sample_uniformity: f32 =
                uniformity_samples.iter().sum::<f32>()
                    / uniformity_samples.len() as f32;
            println!(
                "  - Sample per-frame uniformity (selected markers): {:.4}",
                avg_sample_uniformity
            );
        }

        Ok(())
    }

    #[test]
    fn test_blasterwalk() -> Result<()> {
        let result = run_dataset_analysis(
            "blasterwalk_camera_2dtracks_v1_format.uv",
            50,
            "Blasterwalk",
        );
        result
    }

    #[test]
    fn test_operahouse() -> Result<()> {
        let result =
            run_dataset_analysis("operahouse_v1_format.uv", 31, "Opera House");
        result
    }

    #[test]
    fn test_stA() -> Result<()> {
        let result = run_dataset_analysis("stA_v1_format.uv", 14, "stA");
        result
    }

    // Unit tests for individual functions.

    #[test]
    fn test_calculate_uniformity_perfect_grid() {
        // Test with perfectly uniform 4-point grid (corners of a square).
        let points_x = vec![-0.25, 0.25, -0.25, 0.25];
        let points_y = vec![-0.25, -0.25, 0.25, 0.25];
        let mut count_bins = vec![
            0;
            UNIFORMITY_GRID_SIZE_MAX as usize
                * UNIFORMITY_GRID_SIZE_MAX as usize
        ];

        let uniformity =
            calculate_uniformity(&points_x, &points_y, 4, &mut count_bins);

        // Perfect grid should have very high uniformity (close to 1.0).
        assert!(
            uniformity > 0.8,
            "Perfect grid should have high uniformity, got {}",
            uniformity
        );
    }

    #[test]
    fn test_calculate_uniformity_clustered_points() {
        // Test with clustered points (all very close together).
        let points_x = vec![0.0, 0.01, 0.02, 0.01];
        let points_y = vec![0.0, 0.01, 0.00, 0.02];
        let mut count_bins = vec![
            0;
            UNIFORMITY_GRID_SIZE_MAX as usize
                * UNIFORMITY_GRID_SIZE_MAX as usize
        ];

        let uniformity =
            calculate_uniformity(&points_x, &points_y, 4, &mut count_bins);

        // Clustered points should have low uniformity.
        assert!(
            uniformity < 0.5,
            "Clustered points should have low uniformity, got {}",
            uniformity
        );
    }

    #[test]
    fn test_calculate_uniformity_single_point() {
        // Test with single point (should return 1.0).
        let points_x = vec![0.0];
        let points_y = vec![0.0];
        let mut count_bins = vec![
            0;
            UNIFORMITY_GRID_SIZE_MAX as usize
                * UNIFORMITY_GRID_SIZE_MAX as usize
        ];

        let uniformity =
            calculate_uniformity(&points_x, &points_y, 1, &mut count_bins);

        assert_eq!(
            uniformity, 1.0,
            "Single point should have uniformity of 1.0"
        );
    }
}
