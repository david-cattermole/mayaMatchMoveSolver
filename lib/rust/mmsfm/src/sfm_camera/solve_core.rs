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

//! Core incremental camera solver implementation.

use std::collections::BTreeSet;
use std::sync::Arc;
use std::time::{Duration, Instant};

use anyhow::{bail, Result};

use mmio::uvtrack_reader::{FrameNumber, FrameRange, MarkersData};

use super::bundle_adjustment::run_general_bundle_adjustment;
use super::bundle_adjustment::run_two_camera_bundle_adjustment;
use super::camera_pnp::collect_all_camera_pnp_results;
use super::config::{CameraSolveConfig, SolveQuality, SolveQualityMetrics};
use super::constants::{
    ORIGIN_FRAME_TOLERANCE_PIXELS, SKELETON_DENSIFY_ITERATIONS,
};
use super::frame_graph::FrameGraph;
use super::frame_score::analyze_frame_scoring_and_marker_selection;
use super::intermediate_writer::IntermediateResultWriter;
use super::reprojection::{
    calculate_reprojection_errors, ReprojectionErrorStats,
};
use super::solve_frame_selection::find_best_next_unsolved_frames;
use super::solve_frame_selection::{
    build_frame_graph_for_full_range, build_frame_graph_skeleton_frames,
    find_best_frame_pair,
};
use super::solve_retriangulate::expand_marker_selection_and_retriangulate;
use super::solve_timing::RoundTimingData;
use super::solve_timing::{print_timing_breakdown, TimingData};
use super::solve_utils::{
    format_frame_list, progress_row, progress_table_header, progress_text,
};
use super::transforms::transform_to_origin_frame;
use super::triangulation_fixed_depth::{
    fixed_depth_triangulation, triangulate_missing_bundles_at_fixed_depth,
};
use super::validation::BundleValidationConfig;
use crate::camera_relative_pose::compute_relative_pose_optimal_angular;
use crate::datatype::camera_pose::CameraPose;
use crate::datatype::{
    BundlePositions, CameraIntrinsics, CameraPoses, ImageSize,
    MarkerObservations,
};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Compile-time flag to enable detailed timing output.
#[allow(dead_code)]
const SUMMARY: bool = true;

/// Compile-time flag to enable detailed timing output.
#[allow(dead_code)]
const TIMING: bool = false;

/// Compile-time flag to enable solver-progress output.
#[allow(dead_code)]
const PROGRESS: bool = true;

/// Results from the Phase 3 incremental camera addition loop.
#[derive(Default)]
pub(crate) struct IncrementalLoopResult {
    pub total_camera_pnp_duration: Duration,
    pub total_phase3_ba_duration: Duration,
    pub total_phase3_marker_expansion_duration: Duration,
    pub round_timings: Vec<RoundTimingData>,
    pub total_frames_unsolved_count: u32,
}

impl IncrementalLoopResult {
    /// Merge another result into this one, accumulating timings and
    /// taking the latest unsolved count.
    pub fn merge(&mut self, other: IncrementalLoopResult) {
        self.total_camera_pnp_duration += other.total_camera_pnp_duration;
        self.total_phase3_ba_duration += other.total_phase3_ba_duration;
        self.total_phase3_marker_expansion_duration +=
            other.total_phase3_marker_expansion_duration;
        self.round_timings.extend(other.round_timings);
        self.total_frames_unsolved_count = other.total_frames_unsolved_count;
    }
}

/// Phase 3: Iterative multi-round camera addition and refinement.
///
/// Incrementally adds cameras, runs bundle adjustment each round,
/// and expands the marker selection. When `final_rounds` is `false`,
/// prefers skeleton frames; when `true`, attempts all remaining frames.
#[allow(clippy::too_many_arguments)]
fn run_incremental_loop(
    scene_frame_range: &FrameRange,
    markers: &MarkersData,
    marker_indices: &mut Vec<usize>,
    camera_poses: &mut CameraPoses,
    bundle_positions: &mut BundlePositions,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
    config: &CameraSolveConfig,
    print_summary: bool,
    solve_start: Instant,
    observations: &MarkerObservations,
    frame_graph: Option<&FrameGraph>,
    skeleton_frame_numbers: Option<&BTreeSet<FrameNumber>>,
    final_rounds: bool,
    previous_stats: &mut Option<ReprojectionErrorStats>,
    intermediate_writer: &Option<Arc<dyn IntermediateResultWriter>>,
) -> Result<IncrementalLoopResult> {
    let mut total_camera_pnp_duration = Duration::ZERO;
    let mut total_phase3_ba_duration = Duration::ZERO;
    let mut total_phase3_marker_expansion_duration = Duration::ZERO;
    let mut round_timings: Vec<RoundTimingData> = Vec::new();
    let mut total_frames_unsolved_count: u32 = 0;

    let pass_label = if final_rounds { "final" } else { "draft" };

    mm_debug_eprintln!(
        "\nPhase 3 [{}]: Iterative multi-round camera addition and refinement...",
        pass_label
    );

    // Track which frames have been solved across all rounds.
    let mut solved_frames: BTreeSet<FrameNumber> = BTreeSet::new();
    for &frame in camera_poses.keys() {
        solved_frames.insert(frame);
    }

    if DEBUG {
        match &skeleton_frame_numbers {
            Some(skeleton) => {
                mm_debug_eprintln!(
                    "  Skeleton frame count: {}",
                    skeleton.len()
                );
            }
            None => {
                mm_debug_eprintln!(
                    "  Skeleton: None (Connected Dominating Set computation failed or returned empty)"
                );
            }
        }
    }

    mm_debug_eprintln!(
        "  {} potential frames to solve.",
        scene_frame_range.frame_count() - solved_frames.len() as u32,
    );

    // Continue rounds until no new cameras are added.
    let mut total_frames_solved_count: u32 = solved_frames.len() as u32;
    let mut consecutive_failures: usize = 0;
    let mut round_number = 0;
    while total_frames_solved_count != scene_frame_range.frame_count() {
        round_number += 1;
        let round_start = Instant::now();
        if DEBUG {
            mm_debug_eprintln!(
                "\n=== Round {} ({}) ===",
                round_number,
                pass_label
            );
            let mut solved_sorted_frames: Vec<FrameNumber> =
                solved_frames.iter().copied().collect();
            solved_sorted_frames.sort_unstable();
            let formatted_solved_frames =
                format_frame_list(&solved_sorted_frames);
            mm_debug_eprintln!("  solved_frames={}", formatted_solved_frames);
        }

        // Select frames to attempt this round.
        let (unsolved_frames, skeleton_frames_tried): (Vec<FrameNumber>, bool) =
            find_best_next_unsolved_frames(
                scene_frame_range,
                &solved_frames,
                frame_graph,
                skeleton_frame_numbers,
                final_rounds,
            );

        if DEBUG {
            let formatted_unsolved_frames = format_frame_list(&unsolved_frames);
            mm_debug_eprintln!(
                "  unsolved_frames={}",
                formatted_unsolved_frames
            );
        }
        if unsolved_frames.is_empty() {
            mm_debug_eprintln!("  No more frames to attempt - stopping.");
            break;
        }

        mm_debug_eprintln!(
            "  Attempting {} unsolved frames with {} bundles available.",
            unsolved_frames.len(),
            bundle_positions.len()
        );

        // Camera PNP step.
        let camera_pnp_start = Instant::now();
        let camera_pnp_results = collect_all_camera_pnp_results(
            &unsolved_frames,
            observations,
            marker_indices,
            bundle_positions,
            camera_intrinsics,
        );
        let camera_pnp_duration = camera_pnp_start.elapsed();
        total_camera_pnp_duration += camera_pnp_duration;

        // Insert filtered camera poses.
        let mut cameras_added_this_round: u32 = 0;
        for camera_pnp_result in camera_pnp_results {
            camera_poses.insert(
                camera_pnp_result.frame,
                camera_pnp_result.pose.clone(),
            );
            solved_frames.insert(camera_pnp_result.frame);
            cameras_added_this_round += 1;

            mm_debug_eprintln!(
                "    Frame {}: Added after filtering ({} total cameras)",
                camera_pnp_result.frame,
                camera_poses.len()
            );
        }

        let cameras_failed_this_round: u32 =
            unsolved_frames.len() as u32 - cameras_added_this_round;

        mm_debug_eprintln!(
            "\n  Round {} ({}) camera addition: {} succeeded, {} failed.",
            round_number,
            pass_label,
            cameras_added_this_round,
            cameras_failed_this_round
        );

        total_frames_solved_count += cameras_added_this_round;
        total_frames_unsolved_count =
            scene_frame_range.frame_count() - solved_frames.len() as u32;

        // If skeleton frames were tried but none succeeded, stop
        // this loop so the caller can decide what to do next
        // (e.g. run a second pass without skeleton).
        if skeleton_frames_tried && cameras_added_this_round == 0 {
            mm_debug_eprintln!(
                "  Skeleton frames failed to add cameras - stopping loop."
            );
            break;
        }

        // No point with more steps if no cameras were added.
        if cameras_added_this_round == 0 {
            consecutive_failures += 1;
            if consecutive_failures >= 3 {
                mm_debug_eprintln!(
                    "  Failed to add cameras even with fallback - stopping."
                );
                break;
            }

            mm_debug_eprintln!(
                "  No new cameras added - trying again (failures: {}).",
                consecutive_failures
            );
            continue;
        }
        consecutive_failures = 0;

        // Calculate reprojection errors after camera additions.
        let stats = calculate_reprojection_errors(
            &format!("Round {} - After Camera Additions", round_number),
            markers,
            marker_indices,
            camera_poses,
            bundle_positions,
            camera_intrinsics,
            image_size,
            previous_stats.as_ref(),
        );
        if PROGRESS && print_summary {
            progress_row(
                3,
                solve_start,
                stats.mean,
                stats.median,
                camera_poses.len(),
                bundle_positions.len(),
                &format!(
                    "Round {} ({}): PnP +{} cameras",
                    round_number, pass_label, cameras_added_this_round
                ),
            );
        }
        *previous_stats = Some(stats);

        // Bundle Adjustment.
        mm_debug_eprintln!(
            "\n  Round {} ({}): Running global bundle adjustment...",
            round_number,
            pass_label
        );
        let ba_start = Instant::now();
        let validation_config = BundleValidationConfig::default();
        run_general_bundle_adjustment(
            markers,
            camera_poses,
            bundle_positions,
            camera_intrinsics,
            image_size,
            config.bundle_iter_num,
            config,
            Some(&validation_config),
            Some(&validation_config),
        )?;
        let ba_duration = ba_start.elapsed();
        total_phase3_ba_duration += ba_duration;

        // Calculate reprojection errors after global bundle
        // adjustment.
        let stats = calculate_reprojection_errors(
            &format!("Round {} - After Global Bundle Adjustment", round_number),
            markers,
            marker_indices,
            camera_poses,
            bundle_positions,
            camera_intrinsics,
            image_size,
            previous_stats.as_ref(),
        );
        if PROGRESS && print_summary {
            progress_row(
                3,
                solve_start,
                stats.mean,
                stats.median,
                camera_poses.len(),
                bundle_positions.len(),
                &format!("Round {} ({}): BA", round_number, pass_label),
            );
        }
        *previous_stats = Some(stats.clone());

        // Write intermediate results in the background if a writer
        // is configured.
        if let Some(ref writer) = *intermediate_writer {
            let w = Arc::clone(writer);
            let poses = camera_poses.clone();
            let bundles = bundle_positions.clone();
            let s = stats;
            rayon::spawn(move || w.write_intermediate(poses, bundles, s));
        }

        mm_debug_eprintln!(
            "\nPhase 3: Transforming to origin frame and scaling..."
        );

        let stats = calculate_reprojection_errors(
            "Final Reprojection Error",
            markers,
            marker_indices,
            camera_poses,
            bundle_positions,
            camera_intrinsics,
            image_size,
            previous_stats.as_ref(),
        );

        let stats_before_transform = stats.clone();

        transform_to_origin_frame(
            config.origin_frame,
            config.scene_scale,
            camera_poses,
            bundle_positions,
        )?;

        let stats = calculate_reprojection_errors(
            "After Transformation to Origin Frame",
            markers,
            marker_indices,
            camera_poses,
            bundle_positions,
            camera_intrinsics,
            image_size,
            previous_stats.as_ref(),
        );
        let mean_diff = (stats.mean - stats_before_transform.mean).abs();
        assert!(mean_diff <= ORIGIN_FRAME_TOLERANCE_PIXELS);

        // Expand marker selection after global BA.
        let marker_expansion_start = Instant::now();
        mm_debug_eprintln!(
            "  Round {} ({}): Expanding marker selection...",
            round_number,
            pass_label
        );
        expand_marker_selection_and_retriangulate(
            markers,
            marker_indices,
            camera_poses,
            bundle_positions,
            camera_intrinsics,
            image_size,
        )?;
        let marker_expansion_duration = marker_expansion_start.elapsed();
        total_phase3_marker_expansion_duration += marker_expansion_duration;

        let round_duration = round_start.elapsed();

        round_timings.push(RoundTimingData {
            round_number,
            total_cameras: camera_poses.len(),
            cameras_added: cameras_added_this_round,
            camera_pnp_duration,
            ba_duration,
            marker_expansion_duration,
            round_duration,
        });
    }

    mm_debug_eprintln!(
        "\n  Multi-round solving ({}) complete: {} rounds, {} cameras solved, {} unsolved",
        pass_label, round_number, total_frames_solved_count, total_frames_unsolved_count
    );

    Ok(IncrementalLoopResult {
        total_camera_pnp_duration,
        total_phase3_ba_duration,
        total_phase3_marker_expansion_duration,
        round_timings,
        total_frames_unsolved_count,
    })
}

/// Core incremental camera solve, without global focal length adjustment.
///
/// Solves camera poses and 3D bundle positions from 2D marker tracks:
/// 1. Analyse frames and pick the best starting frame pair.
/// 2. Build initial reconstruction from that pair.
/// 3. Incrementally add remaining cameras and run bundle adjustment.
/// 4. Final bundle adjustment and origin-frame transform.
pub(crate) fn camera_solve_inner(
    scene_frame_range: FrameRange,
    markers: &MarkersData,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
    config: &CameraSolveConfig,
    solve_quality: SolveQuality,
    print_summary: bool,
    intermediate_writer: Option<Arc<dyn IntermediateResultWriter>>,
    camera_poses: &mut CameraPoses,
    bundle_positions: &mut BundlePositions,
    quality_metrics: &mut SolveQualityMetrics,
) -> Result<()> {
    let solve_start = Instant::now();

    mm_debug_eprintln!("Starting camera solve...");
    mm_debug_eprintln!(
        "  Frame range: {} to {}",
        scene_frame_range.start_frame,
        scene_frame_range.end_frame
    );
    mm_debug_eprintln!("  Total markers: {}", markers.len());

    // Clear outputs.
    camera_poses.clear();
    bundle_positions.clear();
    *quality_metrics = SolveQualityMetrics::default();

    if PROGRESS && print_summary {
        eprintln!(
            "[Phase 0] {:>5} | Solve: {} total frames, {} total markers",
            "Time",
            scene_frame_range.frame_count(),
            markers.len()
        );
        eprintln!(
            "[Phase 0] {:>5} | Frame range: {} to {}",
            "-----", scene_frame_range.start_frame, scene_frame_range.end_frame
        );
    }

    // Convert markers to efficient observation format for O(1) frame lookups.
    let observations = MarkerObservations::from_markers_data(markers)?;
    mm_debug_eprintln!(
        "  Converted to MarkerObservations: {} markers, frame range {}-{}",
        observations.count_markers(),
        observations.frame_range().start_frame,
        observations.frame_range().end_frame
    );

    // Phase 1: Frame Analysis & Selection.
    mm_debug_eprintln!(
        "\nPhase 1: Analyzing frames and selecting optimal markers..."
    );
    let phase1_start = Instant::now();
    let frame_analysis_result =
        analyze_frame_scoring_and_marker_selection(scene_frame_range, markers)?;
    let phase1_duration = phase1_start.elapsed();

    // Extract selected_marker_indices as mutable - will be expanded
    // during solve.
    let mut marker_indices =
        frame_analysis_result.selected_marker_indices.clone();

    if marker_indices.is_empty() {
        bail!("No markers selected after frame analysis.");
    }
    if frame_analysis_result.common_frame_numbers.len() < 2 {
        bail!(
            "Need at least 2 common frames, found {}.",
            frame_analysis_result.common_frame_numbers.len()
        );
    }

    if PROGRESS && print_summary {
        progress_text(
            1,
            solve_start,
            &format!(
                "Frame analysis: {} markers selected, {} common frames.",
                marker_indices.len(),
                frame_analysis_result.common_frame_numbers.len()
            ),
        );
    }

    // Determine best frame pair.
    let frame_pair_start = Instant::now();
    let best_frame_pair: (FrameNumber, FrameNumber) =
        find_best_frame_pair(markers, &marker_indices, &frame_analysis_result)?;
    let frame_pair_duration = frame_pair_start.elapsed();

    if PROGRESS && print_summary {
        progress_text(
            2,
            solve_start,
            &format!(
                "Initial reconstruction: frame pair ({}, {})",
                best_frame_pair.0, best_frame_pair.1,
            ),
        );
    }

    mm_debug_eprintln!(
        "  Selected {} markers across {} frames.",
        marker_indices.len(),
        frame_analysis_result.common_frame_numbers.len()
    );
    mm_debug_eprintln!(
        "  Best initialization pair: frames {} and {}",
        best_frame_pair.0,
        best_frame_pair.1,
    );
    // Phase 2: Initial Reconstruction.
    mm_debug_eprintln!("\nPhase 2: Initial reconstruction from frame pair...");

    let phase2_start = Instant::now();

    // Extract UV correspondences for the best frame pair.
    let (frame_a, frame_b) = best_frame_pair;
    let (uv_coords_a, uv_coords_b) = observations
        .extract_correspondences_for_frame_pair(
            &marker_indices,
            frame_a,
            frame_b,
        );
    mm_debug_eprintln!(
        "  Extracted {} point correspondences between frames {} and {}.",
        uv_coords_a.len(),
        frame_a,
        frame_b
    );

    // NOTE: We assume that the camera intrinsics is the same for all
    // frames.
    let relative_pose_start = Instant::now();
    let relative_pose_info = compute_relative_pose_optimal_angular(
        camera_intrinsics,
        camera_intrinsics,
        &uv_coords_a,
        &uv_coords_b,
    )?;
    let relative_pose_duration = relative_pose_start.elapsed();
    mm_debug_eprintln!(
        "  Relative pose computed with residual precision: {:.6}",
        relative_pose_info.residual_precision
    );

    // Set first camera at origin (identity pose).
    let pose_a = CameraPose::default();
    let pose_b = relative_pose_info.relative_pose.clone();

    // Store initial camera poses.
    camera_poses.insert(frame_a, pose_a.clone());
    camera_poses.insert(frame_b, pose_b.clone());

    mm_debug_eprintln!(
        "  Stored camera poses for frames {} and {}.",
        frame_a,
        frame_b
    );

    // Reuse triangulated points directly from relative pose
    // computation.
    let num_correspondences = uv_coords_a.len();
    let triangulated_points = relative_pose_info.triangulated_points.clone();
    let triangulated_points_valid =
        relative_pose_info.triangulated_points_valid;

    // Validate array sizes match expectations.
    assert_eq!(
        triangulated_points.len(),
        num_correspondences,
        "Triangulated points array size mismatch"
    );
    assert_eq!(
        triangulated_points_valid.len(),
        num_correspondences,
        "Triangulated points validity array size mismatch"
    );

    let successful_count =
        triangulated_points_valid.iter().filter(|&&v| v).count();

    mm_debug_eprintln!(
        "  Triangulated {} / {} initial 3D points successfully ({} failed: {:.1}% success rate).",
        successful_count,
        num_correspondences,
        num_correspondences - successful_count,
        (successful_count as f64 / num_correspondences as f64) * 100.0
    );

    if PROGRESS && print_summary {
        progress_text(
            2,
            solve_start,
            &format!(
                "Triangulated {}/{} bundles ({:.0}%)",
                successful_count,
                num_correspondences,
                (successful_count as f64 / num_correspondences as f64) * 100.0
            ),
        );
    }

    // Store bundle positions (only valid triangulations).
    for (i, (point_3d, &is_valid)) in triangulated_points
        .iter()
        .zip(triangulated_points_valid.iter())
        .enumerate()
    {
        if is_valid {
            let marker_idx = marker_indices[i];
            bundle_positions.insert(marker_idx, *point_3d);
        }
    }

    // Fixed-depth fallback for failed triangulations.
    //
    // For markers that failed geometric triangulation, place them at
    // the mean scene depth to provide bundle adjustment with reasonable
    // starting positions to refine.
    let fixed_depth_phase2_start = Instant::now();
    fixed_depth_triangulation(
        &triangulated_points_valid,
        bundle_positions,
        &pose_a,
        &pose_b,
        &marker_indices,
        markers,
        frame_a,
        frame_b,
    );
    let fixed_depth_phase2_duration = fixed_depth_phase2_start.elapsed();

    mm_debug_eprintln!(
        "  Initial reconstruction complete: {} bundles",
        bundle_positions.len()
    );

    // Calculate initial reprojection errors before bundle adjustment.
    let stats = calculate_reprojection_errors(
        "After Initial Triangulation (before BA)",
        markers,
        &marker_indices,
        camera_poses,
        bundle_positions,
        camera_intrinsics,
        image_size,
        None, // no previous error to compare.
    );
    if PROGRESS && print_summary {
        progress_table_header(2, solve_start);
        progress_row(
            2,
            solve_start,
            stats.mean,
            stats.median,
            camera_poses.len(),
            bundle_positions.len(),
            "Root frame pair",
        );
    }
    let mut previous_stats: Option<ReprojectionErrorStats> = Some(stats);

    // Refine initial reconstruction with bundle adjustment.
    let initial_ba_start = Instant::now();
    mm_debug_eprintln!(
        "  Refining initial reconstruction with bundle adjustment..."
    );

    // Run initial BA with pre/post validation for 2-camera
    // initialization.
    let validation_config = BundleValidationConfig::default();
    run_two_camera_bundle_adjustment(
        markers,
        camera_poses,
        bundle_positions,
        camera_intrinsics,
        image_size,
        config.root_iter_num,
        Some(&validation_config), // pre-BA validation.
        Some(&validation_config), // post-BA validation.
    )?;

    // Calculate reprojection errors after initial bundle
    // adjustment.
    let stats = calculate_reprojection_errors(
        "After Initial Bundle Adjustment",
        markers,
        &marker_indices,
        camera_poses,
        bundle_positions,
        camera_intrinsics,
        image_size,
        previous_stats.as_ref(),
    );
    if PROGRESS && print_summary {
        progress_row(
            2,
            solve_start,
            stats.mean,
            stats.median,
            camera_poses.len(),
            bundle_positions.len(),
            "Root frame pair BA",
        );
    }
    previous_stats = Some(stats);
    let initial_ba_duration = initial_ba_start.elapsed();
    let phase2_duration = phase2_start.elapsed();

    // Phase 3: Iterative Multi-Round Camera Addition and Refinement.
    let phase3_start = Instant::now();
    let phase3_result = {
        // Build frame graph and skeleton frames for Phase 3 selection.
        mm_debug_eprintln!(
            "  Building frame graph for Phase 3 frame selection..."
        );
        let frame_graph_for_phase3 = Some(build_frame_graph_for_full_range(
            markers,
            &marker_indices,
            &scene_frame_range,
        ));

        let skeleton_frame_numbers: Option<BTreeSet<FrameNumber>> =
            frame_graph_for_phase3.as_ref().and_then(|graph| {
                build_frame_graph_skeleton_frames(
                    graph,
                    &scene_frame_range,
                    Some(best_frame_pair),
                    SKELETON_DENSIFY_ITERATIONS,
                )
            });

        // Pass 1: Solve skeleton frames first.
        let mut phase3_result = run_incremental_loop(
            &scene_frame_range,
            markers,
            &mut marker_indices,
            camera_poses,
            bundle_positions,
            camera_intrinsics,
            image_size,
            config,
            print_summary,
            solve_start,
            &observations,
            frame_graph_for_phase3.as_ref(),
            skeleton_frame_numbers.as_ref(),
            false, // final_rounds = false: use skeleton frames.
            &mut previous_stats,
            &intermediate_writer,
        )?;

        // Pass 2: Solve remaining (non-skeleton) frames, unless this
        // is a draft solve which only needs skeleton frames.
        if solve_quality != SolveQuality::Draft
            && camera_poses.len() < scene_frame_range.frame_count() as usize
        {
            let pass2_result = run_incremental_loop(
                &scene_frame_range,
                markers,
                &mut marker_indices,
                camera_poses,
                bundle_positions,
                camera_intrinsics,
                image_size,
                config,
                print_summary,
                solve_start,
                &observations,
                frame_graph_for_phase3.as_ref(),
                skeleton_frame_numbers.as_ref(),
                true, // final_rounds = true: solve remaining frames.
                &mut previous_stats,
                &intermediate_writer,
            )?;
            phase3_result.merge(pass2_result);
        }

        phase3_result
    };
    let phase3_duration = phase3_start.elapsed();

    // Phase 4: General Bundle Adjustment.
    //
    // Run final general bundle adjustment with all cameras and points
    // unlocked for maximum refinement before transforming to origin
    // frame.
    let phase4_start = Instant::now();
    let phase4_pre_fixed_depth_start = Instant::now();
    let fixed_depth_count = triangulate_missing_bundles_at_fixed_depth(
        markers,
        &marker_indices,
        camera_poses,
        bundle_positions,
        camera_intrinsics,
    );
    if DEBUG && fixed_depth_count > 0 {
        eprintln!(
                    "  Placed {} bundles at fixed depth before Phase 4 general bundle adjustment.",
                    fixed_depth_count
                );
    }
    let phase4_pre_fixed_depth_duration =
        phase4_pre_fixed_depth_start.elapsed();

    let phase4_ba_start = Instant::now();
    mm_debug_eprintln!("\nPhase 4: Running final general bundle adjustment...");

    let mut third_ba_config = config.clone();
    third_ba_config.enable_noise = true;
    let validation_config = BundleValidationConfig::default();
    run_general_bundle_adjustment(
        markers,
        camera_poses,
        bundle_positions,
        camera_intrinsics,
        image_size,
        config.bundle_iter_num,
        &third_ba_config,
        Some(&validation_config), // pre-BA validation.
        Some(&validation_config), // post-BA validation.
    )?;

    // Calculate reprojection errors after general BA.
    let stats = calculate_reprojection_errors(
        "After General Bundle Adjustment",
        markers,
        &marker_indices,
        camera_poses,
        bundle_positions,
        camera_intrinsics,
        image_size,
        previous_stats.as_ref(),
    );
    if PROGRESS && print_summary {
        progress_row(
            4,
            solve_start,
            stats.mean,
            stats.median,
            camera_poses.len(),
            bundle_positions.len(),
            "Global BA",
        );
    }
    previous_stats = Some(stats);
    let phase4_ba_duration = phase4_ba_start.elapsed();

    let phase4_post_fixed_depth_start = Instant::now();
    let fixed_depth_count = triangulate_missing_bundles_at_fixed_depth(
        markers,
        &marker_indices,
        camera_poses,
        bundle_positions,
        camera_intrinsics,
    );
    if DEBUG && fixed_depth_count > 0 {
        eprintln!(
                    "  Placed {} bundles at fixed depth before Phase 4 general bundle adjustment.",
                    fixed_depth_count
                );
    }
    let phase4_post_fixed_depth_duration =
        phase4_post_fixed_depth_start.elapsed();

    let phase4_duration = phase4_start.elapsed();

    // Phase 5: Final Summary.
    //
    // Calculate final reprojection errors.
    let phase5_start = Instant::now();
    let stats = calculate_reprojection_errors(
        "Final Reprojection Error",
        markers,
        &marker_indices,
        camera_poses,
        bundle_positions,
        camera_intrinsics,
        image_size,
        previous_stats.as_ref(),
    );

    if PROGRESS && print_summary {
        progress_row(
            5,
            solve_start,
            stats.mean,
            stats.median,
            camera_poses.len(),
            bundle_positions.len(),
            "Final result",
        );
    }

    // Store residual error before transformation for validation.
    let stats_before_transform = stats;

    // Origin.
    let origin_transform_start = Instant::now();
    if PROGRESS && print_summary {
        progress_text(
            5,
            solve_start,
            &format!("Transforming to origin frame {}.", config.origin_frame),
        );
    }
    // Phase 6: Origin Frame & Scaling
    mm_debug_eprintln!(
        "\nPhase 6: Transforming to origin frame and scaling..."
    );
    transform_to_origin_frame(
        config.origin_frame,
        config.scene_scale,
        camera_poses,
        bundle_positions,
    )?;

    // Calculate final reprojection errors after transformation.
    let stats = calculate_reprojection_errors(
        "After Transformation to Origin Frame",
        markers,
        &marker_indices,
        camera_poses,
        bundle_positions,
        camera_intrinsics,
        image_size,
        previous_stats.as_ref(),
    );
    let mean_diff = (stats.mean - stats_before_transform.mean).abs();
    assert!(mean_diff <= ORIGIN_FRAME_TOLERANCE_PIXELS);
    let origin_transform_duration = origin_transform_start.elapsed();
    let phase5_duration = phase5_start.elapsed();

    let solve_total_duration = solve_start.elapsed();

    if PROGRESS && print_summary {
        progress_text(6, solve_start, "Camera solve completed!");
    }

    // Update metrics.
    quality_metrics.frames_solved = camera_poses.len();
    quality_metrics.frames_unsolved =
        phase3_result.total_frames_unsolved_count as usize;
    quality_metrics.total_bundles_triangulated = bundle_positions.len();
    quality_metrics.mean_reprojection_error = stats.mean;
    quality_metrics.median_reprojection_error = stats.median;

    if SUMMARY && print_summary {
        eprintln!("\nCamera solve completed!");
        eprintln!("  Solve time: {:.3}s", solve_total_duration.as_secs_f64(),);
        eprintln!("  Frames solved: {}", quality_metrics.frames_solved);
        eprintln!("  Frames unsolved: {}", quality_metrics.frames_unsolved);
        eprintln!(
            "  Bundles triangulated: {}",
            quality_metrics.total_bundles_triangulated
        );
        eprintln!(
            "  Final reprojection error: mean={:.3} px, median={:.3} px",
            quality_metrics.mean_reprojection_error,
            quality_metrics.median_reprojection_error
        );

        // List all solved frames.
        let mut solved_frame_list: Vec<FrameNumber> =
            camera_poses.keys().copied().collect();
        solved_frame_list.sort_unstable();

        // Format as ranges for consecutive frames.
        let formatted_frames = format_frame_list(&solved_frame_list);
        eprintln!("  Solved frames: {}", formatted_frames);
        // TODO: Add list of unsolved frames too.
    }

    if TIMING && print_summary {
        let timing = TimingData {
            solve_total_duration,
            phase1_duration,
            frame_pair_duration,
            phase2_duration,
            relative_pose_duration,
            fixed_depth_phase2_duration,
            initial_ba_duration,
            phase3_duration,
            total_camera_pnp_duration: phase3_result.total_camera_pnp_duration,
            total_phase3_ba_duration: phase3_result.total_phase3_ba_duration,
            total_phase3_marker_expansion_duration: phase3_result
                .total_phase3_marker_expansion_duration,
            round_timings: phase3_result.round_timings,
            phase4_duration,
            phase4_pre_fixed_depth_duration,
            phase4_ba_duration,
            phase4_post_fixed_depth_duration,
            phase5_duration,
            origin_transform_duration,
        };
        print_timing_breakdown(&timing);
    }

    Ok(())
}
