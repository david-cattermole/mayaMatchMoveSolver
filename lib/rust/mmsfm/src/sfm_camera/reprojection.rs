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

//! Core solving operations: frame solving, triangulation, bundle adjustment, and transformations

use mmcore::statistics::{
    SortedDataSliceOps, UnsortedDataSlice, UnsortedDataSliceOps,
};
use mmio::uvtrack_reader::MarkersData;

use crate::camera_residual_error::project_scene_point_3d_to_uv_point_2d;
use crate::datatype::{
    BundlePositions, CameraIntrinsics, CameraPoses, ImageSize, UnitValue,
    UvValue,
};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Statistics for reprojection errors.
#[derive(Debug, Clone)]
pub struct ReprojectionErrorStats {
    /// Mean reprojection error in pixels.
    pub mean: f64,
    /// Median reprojection error in pixels.
    pub median: f64,
}

/// Calculate reprojection errors for all solved cameras and return summary statistics.
pub fn calculate_reprojection_errors(
    stage_name: &str,
    markers: &MarkersData,
    selected_marker_indices: &[usize],
    solved_camera_poses: &CameraPoses,
    bundle_positions: &BundlePositions,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
    previous_stats: Option<&ReprojectionErrorStats>,
) -> ReprojectionErrorStats {
    if solved_camera_poses.is_empty() || bundle_positions.is_empty() {
        mm_eprintln_debug!(
            "[Reprojection Errors] {}: No data to evaluate",
            stage_name
        );
        return ReprojectionErrorStats {
            mean: 0.0,
            median: 0.0,
        };
    }

    let mut all_errors = Vec::new();
    let mut total_observations = 0;

    // Calculate errors for each solved frame.
    for (&frame, pose) in solved_camera_poses.iter() {
        let mut frame_errors = Vec::new();

        for &marker_idx in selected_marker_indices {
            if let Some(&point_3d) = bundle_positions.get(&marker_idx) {
                // Check if this marker is visible in this frame.
                if marker_idx >= markers.frame_data.len() {
                    continue;
                }

                let frame_data = &markers.frame_data[marker_idx];
                if let Some(pos) =
                    frame_data.frames.iter().position(|&f| f == frame)
                {
                    let u_observed = frame_data.u_coords[pos];
                    let v_observed = frame_data.v_coords[pos];
                    let uv_observed = UvValue::point2(u_observed, v_observed);

                    // Project 3D point to UV coordinates.
                    //
                    // Note: project_scene_point_3d_to_uv_point_2d expects Point3<f64>, not ScenePoint3.
                    if let Some(uv_projected) =
                        project_scene_point_3d_to_uv_point_2d(
                            &point_3d,
                            pose,
                            camera_intrinsics,
                        )
                    {
                        // Convert UV to pixel coordinates for meaningful error.
                        let px_observed_x =
                            uv_observed.x.value() * image_size.width.value();
                        let px_observed_y =
                            uv_observed.y.value() * image_size.height.value();
                        let px_projected_x =
                            uv_projected.x.value() * image_size.width.value();
                        let px_projected_y =
                            uv_projected.y.value() * image_size.height.value();

                        // Calculate L2 error in pixels.
                        let dx = px_projected_x - px_observed_x;
                        let dy = px_projected_y - px_observed_y;
                        let error = (dx * dx + dy * dy).sqrt();

                        frame_errors.push(error);
                        all_errors.push(error);
                        total_observations += 1;
                    }
                }
            }
        }
    }

    // Filter out NaN and Inf values before calculating statistics.
    all_errors.retain(|&e| e.is_finite());

    if all_errors.is_empty() {
        mm_eprintln_debug!(
            "[Reprojection Errors] {}: No valid observations (all NaN/Inf)",
            stage_name
        );
        return ReprojectionErrorStats {
            mean: 0.0,
            median: 0.0,
        };
    }

    // Calculate statistics.
    let unsorted = UnsortedDataSlice::new(&all_errors, None)
        .expect("Non-empty finite data");
    let mean = unsorted.mean();

    let mut sort_workspace = vec![0.0; all_errors.len()];
    let sorted = unsorted
        .into_sorted(&mut sort_workspace)
        .expect("Sort workspace matches data length");
    let median = sorted.median();

    let std_dev =
        mmcore::statistics::calc_population_standard_deviation(&sorted)
            .unwrap_or(0.0);

    let min = sorted.data()[0];
    let max = sorted.data()[all_errors.len() - 1];

    // Print header with improvement/degradation.
    if DEBUG {
        if let Some(prev_stats) = previous_stats {
            let change = mean - prev_stats.mean;
            let change_str = if change < 0.0 {
                format!("improvement: {:.3} px", -change)
            } else {
                format!("degradation: +{:.3} px", change)
            };
            mm_eprintln_debug!(
                "[Reprojection Errors] {} ({}):",
                stage_name,
                change_str
            );
        } else {
            mm_eprintln_debug!("[Reprojection Errors] {}:", stage_name);
        }
    }

    // Print summary statistics.
    mm_eprintln_debug!(
        "  Cameras: {}, Observations: {}",
        solved_camera_poses.len(),
        total_observations
    );
    mm_eprintln_debug!(
        "  Mean: {:.3} px, Median: {:.3} px, Std Dev: {:.3} px",
        mean,
        median,
        std_dev
    );
    mm_eprintln_debug!("  Min: {:.3} px, Max: {:.3} px", min, max);

    ReprojectionErrorStats { mean, median }
}
