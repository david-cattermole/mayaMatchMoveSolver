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

//! Marker expansion and retriangulation for camera solving.

use anyhow::{bail, Result};
use mmio::uvtrack_reader::{FrameNumber, MarkersData};
use nalgebra::Point3;

use super::constants::MARKER_EXPANSION_MAX_ERROR_PX;
use super::triangulation_fixed_depth::{
    calculate_mean_depth_for_scene,
    triangulate_bundle_with_visible_frames_fixed_depth,
};
use crate::camera_residual_error::project_scene_point_3d_to_uv_point_2d;
use crate::datatype::conversions::convert_uv_to_pixel_point;
use crate::datatype::{
    BundlePositions, CameraIntrinsics, CameraPoses, ImageSize, UnitValue,
    UvValue,
};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Number of BA iterations for single-point refinement during marker expansion.
const MARKER_EXPANSION_REFINE_ITERATIONS: usize = 8;

// Validate a triangulated point by checking reprojection error across all visible frames.
fn validate_triangulated_bundle_with_visible_frames(
    triangulated_point: &Point3<f64>,
    visible_frames: &[FrameNumber],
    camera_poses: &CameraPoses,
    frame_data: &mmio::uvtrack_reader::FrameData,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
) -> (bool, f64) {
    let mut error_sum_squared = 0.0;
    let mut observation_count = 0;
    let mut valid = true;

    for &frame in visible_frames {
        if let Some(idx) = frame_data.frames.iter().position(|&f| f == frame) {
            let u_observed = frame_data.u_coords[idx];
            let v_observed = frame_data.v_coords[idx];
            let uv_observed = UvValue::point2(u_observed, v_observed);

            // Project bundle to this camera.
            let pose = &camera_poses[&frame];
            let uv_projected = match project_scene_point_3d_to_uv_point_2d(
                triangulated_point,
                pose,
                camera_intrinsics,
            ) {
                Some(uv) => uv,
                None => {
                    // Point behind camera.
                    valid = false;
                    break;
                }
            };

            // Convert UV to pixels for error calculation.
            let px_observed =
                convert_uv_to_pixel_point(uv_observed, image_size);
            let px_projected =
                convert_uv_to_pixel_point(uv_projected, image_size);

            // Calculate L2 distance in pixel space.
            let dx = px_projected.x.value() - px_observed.x.value();
            let dy = px_projected.y.value() - px_observed.y.value();
            let error_squared = dx * dx + dy * dy;

            error_sum_squared += error_squared;
            observation_count += 1;
        }
    }

    if !valid || observation_count == 0 {
        (false, f64::NAN)
    } else {
        let mean_error_squared = error_sum_squared / observation_count as f64;
        let rms_error = mean_error_squared.sqrt();
        (true, rms_error)
    }
}

/// Triangulate additional markers not in the original selection.
///
/// After cameras are solved, some markers excluded from the initial selection
/// can now be triangulated. Returns the number of markers added.
pub fn expand_marker_selection_and_retriangulate(
    markers: &MarkersData,
    marker_indices: &mut Vec<usize>,
    camera_poses: &CameraPoses,
    bundle_positions: &mut BundlePositions,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
) -> Result<usize> {
    if camera_poses.len() < 2 {
        bail!("Need at least 2 cameras to triangulate.");
    }

    let markers_before = marker_indices.len();
    let bundles_before = bundle_positions.len();

    // Get sorted list of solved frames for deterministic processing.
    let mut sorted_frames: Vec<FrameNumber> =
        camera_poses.keys().copied().collect();
    sorted_frames.sort_unstable();

    // Calculate mean depth for fixed-depth triangulation.
    let mean_depth =
        calculate_mean_depth_for_scene(bundle_positions, camera_poses);

    let mut newly_added_markers = Vec::new();

    // For each marker not in marker_indices.
    for marker_idx in 0..markers.frame_data.len() {
        // Skip if already selected.
        if marker_indices.contains(&marker_idx) {
            continue;
        }
        assert!(!bundle_positions.contains_key(&marker_idx));

        let frame_data = &markers.frame_data[marker_idx];

        // Find which solved frames have this marker visible.
        let mut visible_frames = Vec::new();
        for &frame in &sorted_frames {
            if frame_data.frames.contains(&frame) {
                visible_frames.push(frame);
            }
        }

        // Need at least 2 views to triangulate.
        if visible_frames.len() < 2 {
            continue;
        }

        let triangulated_point =
            triangulate_bundle_with_visible_frames_fixed_depth(
                &visible_frames,
                camera_poses,
                frame_data,
                camera_intrinsics,
                mean_depth,
                MARKER_EXPANSION_REFINE_ITERATIONS,
            );
        if triangulated_point.is_none() {
            continue;
        }
        let triangulated_point =
            triangulated_point.expect("Triangulated point is Some here.");

        let (valid, rms_error) =
            validate_triangulated_bundle_with_visible_frames(
                &triangulated_point,
                &visible_frames,
                camera_poses,
                frame_data,
                camera_intrinsics,
                image_size,
            );
        if !valid {
            continue;
        }

        // Check if error is within threshold.
        if rms_error <= MARKER_EXPANSION_MAX_ERROR_PX {
            // Add to selection and bundles.
            bundle_positions.insert(marker_idx, triangulated_point);
            newly_added_markers.push(marker_idx);
        }
    }

    // Add newly triangulated markers to selection.
    marker_indices.extend(newly_added_markers.iter().copied());

    let markers_added = newly_added_markers.len();
    let markers_after = marker_indices.len();
    let bundles_after = bundle_positions.len();

    if DEBUG && markers_added > 0 {
        println!(
            "  [Marker Expansion] Added {} markers to selection ({} -> {}, bundles: {} -> {})",
            markers_added, markers_before, markers_after, bundles_before, bundles_after
        );
    }

    Ok(markers_added)
}
