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
use nalgebra::Point3;

use mmio::uvtrack_reader::{parse_file, FrameNumber, FrameRange, MarkersData};
use mmsfm_rust::bundle_triangulation::triangulate_points_from_relative_pose;
use mmsfm_rust::camera_relative_pose::RelativePoseInfo;
use mmsfm_rust::camera_residual_error::{
    compute_reprojection_residuals, compute_residual_statistics,
};
use mmsfm_rust::datatype::camera_pose::CameraPose;
use mmsfm_rust::datatype::{CameraIntrinsics, ImageSize, UvPoint2};
use mmsfm_rust::sfm_camera::analyze_frame_scoring_and_marker_selection;

use crate::common::marker_utils::extract_point_correspondences;
use crate::common::utils::directory::{
    construct_uvtrack_input_file_path, find_data_dir,
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

pub use mmsfm_rust::visualization::FramePair;

/// Loads marker data from a uvtrack file.
pub fn load_marker_data(file_name: &str) -> Result<(MarkersData, FrameRange)> {
    let data_dir = find_data_dir()?;
    let in_file_path = construct_uvtrack_input_file_path(&data_dir, file_name)?;
    let (_file_info, markers) = parse_file(&in_file_path)?;

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

    Ok((markers, scene_frame_range))
}

/// Selects the best frame pair for pose estimation.
pub fn select_optimal_frame_pair(
    markers: &MarkersData,
    frame_range: &FrameRange,
) -> Result<FramePair> {
    if frame_range.frame_count() < 2 {
        anyhow::bail!("Need at least 2 frames for relative pose estimation");
    }

    let analysis_result =
        analyze_frame_scoring_and_marker_selection(*frame_range, markers)?;

    if let Some((frame_a, frame_b)) =
        analysis_result.highest_parallax_frame_pair
    {
        Ok(FramePair { frame_a, frame_b })
    } else {
        // TODO: Remove this fallback. If it fails, the function should error.
        //
        // Fallback to simple heuristic if analysis doesn't find a good pair
        let start_frame = frame_range.start_frame;
        let frame_count = frame_range.frame_count();
        let optimal_separation = (frame_count as f64 * 0.25).max(5.0) as u32;
        let frame_b =
            (start_frame + optimal_separation).min(frame_range.end_frame);

        Ok(FramePair {
            frame_a: start_frame,
            frame_b,
        })
    }
}

/// Triangulate points and filter out any that failed.
fn triangulate_and_filter_correspondences(
    intrinsics_a: &CameraIntrinsics,
    intrinsics_b: &CameraIntrinsics,
    uv_coords_a: &[UvPoint2<f64>],
    uv_coords_b: &[UvPoint2<f64>],
    relative_pose_info: &RelativePoseInfo,
) -> Result<(Vec<UvPoint2<f64>>, Vec<UvPoint2<f64>>, Vec<Point3<f64>>)> {
    let num_input = uv_coords_a.len();

    let mut triangulated_points: Vec<Point3<f64>> =
        vec![Point3::origin(); num_input];
    let mut triangulated_points_valid: Vec<bool> = vec![false; num_input];
    let triangulated_point_count = triangulate_points_from_relative_pose(
        intrinsics_a,
        intrinsics_b,
        uv_coords_a,
        uv_coords_b,
        relative_pose_info,
        &mut triangulated_points,
        &mut triangulated_points_valid,
    )?;

    if triangulated_point_count == num_input {
        if DEBUG {
            println!(
                "Triangulation: {} input points -> {} successfully triangulated (all points)",
                num_input, triangulated_point_count
            );
        }
        return Ok((
            uv_coords_a.to_vec(),
            uv_coords_b.to_vec(),
            triangulated_points,
        ));
    }

    if DEBUG {
        // Some points failed triangulation. Since we can't easily determine which ones,
        // we'll take the first N points as a reasonable approximation for most cases.
        // This is not perfect but works for the majority of real-world scenarios where
        // failures are due to outliers at the end of the sequence.

        println!(
            "Triangulation: {} input points -> {} successfully triangulated (using first N approximation)",
            num_input,
            triangulated_point_count
        );
    }

    let mut filtered_uv_a = Vec::with_capacity(triangulated_point_count);
    let mut filtered_uv_b = Vec::with_capacity(triangulated_point_count);
    let mut filtered_points_3d = Vec::with_capacity(triangulated_point_count);

    for (valid, ((uv_coord_a, uv_coord_b), point_3d)) in
        triangulated_points_valid.iter().zip(
            uv_coords_a
                .iter()
                .zip(uv_coords_b)
                .zip(&triangulated_points),
        )
    {
        if *valid {
            filtered_uv_a.push(*uv_coord_a);
            filtered_uv_b.push(*uv_coord_b);
            filtered_points_3d.push(*point_3d);
        }
    }

    Ok((filtered_uv_a, filtered_uv_b, filtered_points_3d))
}
