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

use mmio::uvtrack_reader::MarkersData;
use mmsfm_rust::bundle_triangulation::triangulate_points_from_relative_pose;
use mmsfm_rust::camera_relative_pose::compute_relative_pose_optimal_angular;
use mmsfm_rust::camera_residual_error::{
    compute_reprojection_residuals, compute_residual_statistics,
};
use mmsfm_rust::datatype::camera_pose::{is_valid_pose, CameraPose};
use mmsfm_rust::datatype::{
    CameraFilmBack, CameraIntrinsics, ImageSize, MillimeterUnit, UnitValue,
};

use super::visualization::reprojection::visualize_marker_reprojections_2d_scatter;
use super::visualization::residuals::visualize_residual_errors_line_plot;
use super::visualization::scene::visualize_sfm_scene_views;
use super::visualization::scene::ViewConfiguration;
use crate::common::extract_point_correspondences;
use crate::common::visualization::scene;
use crate::common::visualization::{reprojection, residuals};
use crate::common::FramePair;
use crate::common::OutputFileNaming;
use crate::common::Stage;
use crate::common::VisualizationType;

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Runs a relative pose estimation test on a dataset, including triangulation and visualizations.
pub fn run_relative_pose_dataset_test(
    markers: &MarkersData,
    frame_pair: &FramePair,
    expected_min_markers: usize,
    dataset_name: &str,
    base_naming: &OutputFileNaming,
    views: Vec<ViewConfiguration>,
    focal_length: MillimeterUnit<f64>,
    film_back: CameraFilmBack<f64>,
    image_size_a: ImageSize<f64>,
    image_size_b: ImageSize<f64>,
) -> Result<()> {
    if DEBUG {
        println!("{} dataset analysis:", dataset_name);
        println!("  Total markers: {}", markers.frame_data.len());
        println!(
            "  Using frame pair: {} -> {} (separation: {})",
            frame_pair.frame_a,
            frame_pair.frame_b,
            frame_pair.frame_b - frame_pair.frame_a
        );
    }

    assert!(
        markers.frame_data.len() >= expected_min_markers,
        "Expected at least {} markers, found {}",
        expected_min_markers,
        markers.frame_data.len()
    );

    let (uv_coords_a, uv_coords_b) =
        extract_point_correspondences(markers, frame_pair.clone(), None)?;
    if DEBUG {
        println!("  Point correspondences: {}", uv_coords_a.len());
    }

    let intrinsics_a =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);
    let intrinsics_b =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);

    let pose_info = compute_relative_pose_optimal_angular(
        &intrinsics_a,
        &intrinsics_b,
        &uv_coords_a,
        &uv_coords_b,
    )?;

    assert!(
        is_valid_pose(&pose_info.relative_pose),
        "Computed pose should be valid (no NaN values)"
    );

    if DEBUG {
        println!("  Essential matrix computed successfully");
        println!(
            "  Relative pose translation magnitude: {:.6}",
            pose_info.relative_pose.translation().norm()
        );
    }

    let mut triangulated_points: Vec<Point3<f64>> =
        vec![Point3::origin(); uv_coords_a.len()];
    let mut triangulated_points_valid: Vec<bool> =
        vec![false; uv_coords_a.len()];
    let num_points_3d = triangulate_points_from_relative_pose(
        &intrinsics_a,
        &intrinsics_b,
        &uv_coords_a,
        &uv_coords_b,
        &pose_info,
        &mut triangulated_points,
        &mut triangulated_points_valid,
    )?;

    if DEBUG {
        println!("  Triangulated {} 3D points", num_points_3d);
    }
    assert!(
        num_points_3d > 0,
        "Should triangulate at least some 3D points"
    );

    let pose_a = CameraPose::default();
    let pose_b = &pose_info.relative_pose;

    let title = format!("{} - Relative Pose", dataset_name);

    // Filter to only valid triangulated points.
    let valid_triangulated_points: Vec<Point3<f64>> = triangulated_points
        .iter()
        .zip(triangulated_points_valid.iter())
        .filter(|(_, &is_valid)| is_valid)
        .map(|(&p, _)| p)
        .collect();

    let naming_scene = base_naming.clone_with_stage(Stage::Initial);
    visualize_sfm_scene_views(
        &pose_a,
        &pose_b,
        &valid_triangulated_points,
        &title,
        &naming_scene,
        views,
        &intrinsics_a,
        &intrinsics_b,
    )?;

    let mut filtered_uv_a = Vec::new();
    let mut filtered_uv_b = Vec::new();
    let mut filtered_points_3d = Vec::new();
    for (i, &is_valid) in triangulated_points_valid.iter().enumerate() {
        if is_valid {
            filtered_uv_a.push(uv_coords_a[i]);
            filtered_uv_b.push(uv_coords_b[i]);
            filtered_points_3d.push(triangulated_points[i]);
        }
    }

    if filtered_points_3d.is_empty() {
        if DEBUG {
            println!(
                "No points were successfully triangulated, skipping residual and reprojection visualizations."
            );
        }
        return Ok(());
    }

    let output_image_size = ImageSize::full_hd();
    let naming_marker_2d = base_naming
        .clone_with_visualization(VisualizationType::MarkerReprojection2d);

    visualize_marker_reprojections_2d_scatter(
        &filtered_uv_a,
        &filtered_uv_b,
        &filtered_points_3d,
        &pose_a,
        &pose_b,
        &intrinsics_a,
        &intrinsics_b,
        &image_size_a,
        &image_size_b,
        frame_pair,
        &title,
        &output_image_size,
        &naming_marker_2d,
    )?;

    let mut residuals = vec![0.0; filtered_points_3d.len()];
    compute_reprojection_residuals(
        &filtered_points_3d,
        &filtered_uv_a,
        &filtered_uv_b,
        &pose_a,
        &pose_b,
        &intrinsics_a,
        &intrinsics_b,
        &image_size_a,
        &image_size_b,
        &mut residuals,
    )?;

    let stats = compute_residual_statistics(&residuals);

    let naming_residuals = base_naming
        .clone_with_visualization(VisualizationType::ResidualsLinePlot);
    visualize_residual_errors_line_plot(
        &residuals,
        &stats,
        &format!("{} - Residual Errors", title),
        &naming_residuals,
    )?;

    if DEBUG {
        println!("  Mean residual error: {:.4} pixels", stats.mean);
        println!("  Median residual error: {:.4} pixels", stats.median);
        println!("  Standard deviation: {:.4} pixels", stats.std_dev);
    }

    Ok(())
}
