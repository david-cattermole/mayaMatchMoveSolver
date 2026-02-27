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

use std::collections::HashMap;

use anyhow::Result;
use mmcore::statistics::{
    SortedDataSliceOps, UnsortedDataSlice, UnsortedDataSliceOps,
};
use nalgebra::Point3;

use mmio::uvtrack_reader::{FrameNumber, MarkersData};

use crate::datatype::common::UnitValue;
use crate::datatype::conversions::{
    convert_ndc_to_uv_point, convert_uv_to_pixel_point,
};
use crate::datatype::{
    BundlePositions, CameraIntrinsics, CameraPose, CameraPoses, ImageSize,
    NdcValue, UvPoint2, UvValue,
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Project a 3D point to 2D using camera pose and intrinsics
///
/// # Arguments
/// * `point_3d` - 3D point in world coordinates
/// * `camera_pose` - Camera pose (world-to-camera transformation)
/// * `camera_intrinsics` - Camera intrinsics
///
/// # Returns
/// 2D UV coordinates (0.0 to 1.0 range)
pub fn project_scene_point_3d_to_uv_point_2d(
    // TODO: Change Point3 to ScenePoint3.
    scene_point_3d: &Point3<f64>,
    camera_pose: &CameraPose,
    camera_intrinsics: &CameraIntrinsics,
) -> Option<UvPoint2<f64>> {
    let camera_point_3d = camera_pose.apply_transform(scene_point_3d);

    // Check if point is in front of camera (Maya convention: -Z is forward).
    if camera_point_3d.z >= 0.0 {
        return None;
    }

    // Project to normalized image coordinates (perspective division).
    //
    // Maya convention: camera looks down -Z, so camera_point_3d.z is
    // already negative for points in front
    let camera_x = camera_point_3d.x / -camera_point_3d.z;
    let camera_y = camera_point_3d.y / -camera_point_3d.z;

    // Apply camera intrinsics to convert camera coordinates to NDC coordinates.
    //
    // This is the inverse of the conversion in `uv_point_to_camera_coord_point`.
    let ndc_x = camera_x * (2.0 * camera_intrinsics.focal_length_x);
    let ndc_y = camera_y * (2.0 * camera_intrinsics.focal_length_y);

    let principal_point_x_ndc = camera_intrinsics.principal_point.x.value();
    let principal_point_y_ndc = camera_intrinsics.principal_point.y.value();

    let final_ndc_x = ndc_x + principal_point_x_ndc;
    let final_ndc_y = ndc_y + principal_point_y_ndc;

    // Convert NDC coordinates to UV coordinates.
    let ndc_point_2d = NdcValue::point2(final_ndc_x, final_ndc_y);
    let uv_point_2d = convert_ndc_to_uv_point(ndc_point_2d);

    Some(uv_point_2d)
}

/// Reproject 3D points to 2D using camera pose and intrinsics with
/// proper camera projection.
pub fn reproject_3d_points_to_2d_uv_coordinates(
    // TODO: Convert Point3 to ScenePoint3 datatype.
    scene_points_3d: &[Point3<f64>],
    camera_pose: &CameraPose,
    camera_intrinsics: &CameraIntrinsics,
) -> Result<Vec<UvPoint2<f64>>> {
    let mut reprojected = Vec::with_capacity(scene_points_3d.len());
    let mut points_behind_camera = 0;

    for (i, scene_point_3d) in scene_points_3d.iter().enumerate() {
        if let Some(uv_point_2d) = project_scene_point_3d_to_uv_point_2d(
            &scene_point_3d,
            camera_pose,
            camera_intrinsics,
        ) {
            reprojected.push(uv_point_2d);

            mm_eprintln_debug!(
                "  Point {} reprojection: 3D({:.3}, {:.3}, {:.3}) -> UV({:.6}, {:.6})",
                i, scene_point_3d.x, scene_point_3d.y, scene_point_3d.z,
                uv_point_2d.x.value(), uv_point_2d.y.value()
            );
        } else {
            // Point is behind camera or invalid.
            //
            // f64::NAN is an sentinel value meaning it's invalid.
            reprojected.push(UvValue::point2(f64::NAN, f64::NAN));
            points_behind_camera += 1;

            mm_eprintln_debug!(
                "  Point {} behind camera (Maya: +Z is behind): 3D({:.3}, {:.3}, {:.3})",
                i, scene_point_3d.x, scene_point_3d.y, scene_point_3d.z,
            );
        }
    }

    if points_behind_camera > 0 {
        mm_eprintln_debug!(
            "  {} out of {} points are behind the camera",
            points_behind_camera,
            scene_points_3d.len()
        );
    }

    Ok(reprojected)
}

/// Statistics for residual error analysis.
#[derive(Debug, Clone)]
pub struct ResidualStats {
    pub mean: f64,
    pub median: f64,
    pub std_dev: f64,
    pub min: f64,
    pub max: f64,
    pub count: usize,
}

impl ResidualStats {
    pub fn new() -> Self {
        Self {
            mean: 0.0,
            median: 0.0,
            std_dev: 0.0,
            min: 0.0,
            max: 0.0,
            count: 0,
        }
    }
}

/// Compute reprojection residual errors for triangulated 3D points.
///
/// # Arguments
/// * `points_3d` - Triangulated 3D points in world coordinates.
/// * `uv_coords_observed_a` - Observed UV coordinates in camera A (0.0 to 1.0 range).
/// * `uv_coords_observed_b` - Observed UV coordinates in camera B (0.0 to 1.0 range).
/// * `pose_a` - Pose of camera A.
/// * `pose_b` - Pose of camera B.
/// * `intrinsics_a` - Intrinsics for camera A.
/// * `intrinsics_b` - Intrinsics for camera B.
/// * `image_size_a` - Image size for camera A.
/// * `image_size_b` - Image size for camera B.
///
/// # Returns
/// Vector of residual errors in pixels (one per 3D point, combining both camera views)
pub fn compute_reprojection_residuals(
    points_3d: &[Point3<f64>],
    uv_coords_observed_a: &[UvPoint2<f64>],
    uv_coords_observed_b: &[UvPoint2<f64>],
    camera_pose_a: &CameraPose,
    camera_pose_b: &CameraPose,
    camera_intrinsics_a: &CameraIntrinsics,
    camera_intrinsics_b: &CameraIntrinsics,
    image_size_a: &ImageSize<f64>,
    image_size_b: &ImageSize<f64>,
    residuals_output: &mut [f64],
) -> Result<()> {
    assert_eq!(points_3d.len(), uv_coords_observed_a.len());
    assert_eq!(points_3d.len(), uv_coords_observed_b.len());
    assert_eq!(points_3d.len(), residuals_output.len());

    for (i, point_3d) in points_3d.iter().enumerate() {
        let observed_a = uv_coords_observed_a[i];
        let observed_b = uv_coords_observed_b[i];

        // Project 3D point back to both cameras.
        let projected_a = project_scene_point_3d_to_uv_point_2d(
            point_3d,
            camera_pose_a,
            camera_intrinsics_a,
        );
        let projected_b = project_scene_point_3d_to_uv_point_2d(
            point_3d,
            camera_pose_b,
            camera_intrinsics_b,
        );

        match (projected_a, projected_b) {
            (Some(proj_a), Some(proj_b)) => {
                // Convert UV coordinates to pixel coordinates for
                // meaningful residual calculation.
                //
                // UV coordinates are already in [0.0, 1.0] range,
                // convert directly to pixels.
                let observed_uv_a =
                    UvValue::point2(observed_a.x.value(), observed_a.y.value());
                let projected_uv_a =
                    UvValue::point2(proj_a.x.value(), proj_a.y.value());
                let observed_pixel_a =
                    convert_uv_to_pixel_point(observed_uv_a, image_size_a);
                let projected_pixel_a =
                    convert_uv_to_pixel_point(projected_uv_a, image_size_a);

                let observed_uv_b =
                    UvValue::point2(observed_b.x.value(), observed_b.y.value());
                let projected_uv_b =
                    UvValue::point2(proj_b.x.value(), proj_b.y.value());
                let observed_pixel_b =
                    convert_uv_to_pixel_point(observed_uv_b, image_size_b);
                let projected_pixel_b =
                    convert_uv_to_pixel_point(projected_uv_b, image_size_b);

                // Calculate reprojection errors in pixels for both
                // cameras.
                let error_a_px = ((observed_pixel_a.x.value()
                    - projected_pixel_a.x.value())
                .powi(2)
                    + (observed_pixel_a.y.value()
                        - projected_pixel_a.y.value())
                    .powi(2))
                .sqrt();
                let error_b_px = ((observed_pixel_b.x.value()
                    - projected_pixel_b.x.value())
                .powi(2)
                    + (observed_pixel_b.y.value()
                        - projected_pixel_b.y.value())
                    .powi(2))
                .sqrt();

                // Combine errors from both cameras (RMS)
                let combined_error =
                    ((error_a_px * error_a_px + error_b_px * error_b_px) / 2.0)
                        .sqrt();
                residuals_output[i] = combined_error;
            }
            _ => {
                // Skip points that can't be projected (behind camera, etc.).
                residuals_output[i] = f64::NAN;
            }
        }
    }

    Ok(())
}

/// Compute statistical measures for residual errors
///
/// # Arguments
/// * `residuals` - Vector of residual errors (may contain NaN values)
///
/// # Returns
/// Statistical summary of the residuals
pub fn compute_residual_statistics(residuals: &[f64]) -> ResidualStats {
    // Filter out NaN values.
    let valid_residuals: Vec<f64> = residuals
        .iter()
        .filter(|&&x| x.is_finite())
        .copied()
        .collect();

    if valid_residuals.is_empty() {
        return ResidualStats::new();
    }

    let count = valid_residuals.len();

    let unsorted = UnsortedDataSlice::new(&valid_residuals, None)
        .expect("Non-empty valid data");
    let mean = unsorted.mean();

    let mut sort_workspace = vec![0.0; count];
    let sorted = unsorted
        .into_sorted(&mut sort_workspace)
        .expect("Sort workspace matches data length");
    let median = sorted.median();

    let std_dev =
        mmcore::statistics::calc_population_standard_deviation(&sorted)
            .unwrap_or(0.0);

    let min = sorted.data()[0];
    let max = sorted.data()[count - 1];

    ResidualStats {
        mean,
        median,
        std_dev,
        min,
        max,
        count,
    }
}

/// Compute per-frame, per-marker reprojection residuals
///
/// This function iterates through all solved frames and computes the
/// reprojection error for each marker in each frame.
///
/// # Arguments
/// * `markers` - Marker tracking data
/// * `solved_poses` - Camera poses for each frame
/// * `bundle_positions` - 3D positions of each bundle/marker
/// * `intrinsics` - Camera intrinsics
/// * `image_size` - Image size for pixel-based residual calculation
///
/// # Returns
/// * HashMap mapping frame number to vector of residual errors (one per
///   marker, in pixels). Markers that are not visible in a frame will
///   have NaN values.
/// * Overall statistics across all markers and frames
pub fn compute_per_frame_per_marker_residuals(
    markers: &MarkersData,
    solved_poses: &CameraPoses,
    bundle_positions: &BundlePositions,
    intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
    // TODO: Should we return a struct with the per-frame residual
    // data? Or just a HashMap?
) -> Result<(HashMap<FrameNumber, Vec<f64>>, ResidualStats)> {
    let mut per_frame_residuals: HashMap<FrameNumber, Vec<f64>> =
        HashMap::new();
    let mut all_residuals: Vec<f64> = Vec::new();

    let num_markers = markers.names.len();

    // Iterate through all solved frames.
    for (&frame, pose) in solved_poses.iter() {
        let mut frame_residuals = vec![f64::NAN; num_markers];

        // For each marker, compute its reprojection error in this frame.
        for (marker_idx, frame_data) in markers.frame_data.iter().enumerate() {
            // Find the index of this frame in the marker's frame data.
            if let Some(data_idx) =
                frame_data.frames.iter().position(|&f| f == frame)
            {
                // Check if this marker has a triangulated 3D position.
                if let Some(&bundle_pos) = bundle_positions.get(&marker_idx) {
                    // Get observed UV coordinates for this frame
                    let u = frame_data.u_coords[data_idx];
                    let v = frame_data.v_coords[data_idx];
                    let observed_uv = UvValue::point2(u, v);

                    // Project the 3D bundle position back to 2D.
                    if let Some(projected_uv) =
                        project_scene_point_3d_to_uv_point_2d(
                            &bundle_pos,
                            pose,
                            intrinsics,
                        )
                    {
                        // Convert both observed and projected UV to pixels.
                        let observed_px =
                            convert_uv_to_pixel_point(observed_uv, image_size);
                        let projected_px =
                            convert_uv_to_pixel_point(projected_uv, image_size);

                        // Compute Euclidean distance in pixel space.
                        let dx = observed_px.x.value() - projected_px.x.value();
                        let dy = observed_px.y.value() - projected_px.y.value();
                        let error_px = (dx * dx + dy * dy).sqrt();

                        frame_residuals[marker_idx] = error_px;
                        all_residuals.push(error_px);
                    }
                }
            }
        }

        per_frame_residuals.insert(frame, frame_residuals);
    }

    let stats = compute_residual_statistics(&all_residuals);

    Ok((per_frame_residuals, stats))
}
