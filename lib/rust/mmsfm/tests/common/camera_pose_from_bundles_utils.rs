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

//! Utilities for camera pose estimation using known 3D points (PnP).

use anyhow::bail;
use anyhow::Result;
use nalgebra::{Matrix3, Point3};
use plotters::{
    prelude::{
        BitMapBackend, ChartBuilder, IntoDrawingArea, LineSeries, PathElement,
        BLACK, BLUE, RED, WHITE,
    },
    style::Color,
};
use std::collections::HashMap;

use mmio::uvtrack_reader::MarkersData;
use mmsfm_rust::camera_pose_from_bundles::{
    calculate_reprojection_error, compute_sqpnp_poses, CameraIntrinsics,
    CameraPose, PnPError,
};
use mmsfm_rust::camera_residual_error::{
    compute_residual_statistics, ResidualStats,
};
use mmsfm_rust::datatype::conversions::uv_point_to_camera_coord_point;
use mmsfm_rust::datatype::{
    CameraFilmBack, CameraToSceneCorrespondence, ImageSize, MillimeterUnit,
    UnitValue, UvPoint2, UvValue,
};

use crate::common::visualization::scene;
use crate::common::{OutputFileNaming, ViewConfiguration, VisualizationType};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Camera pose estimation result for a single frame.
#[derive(Debug, Clone)]
pub struct PoseEstimationResult {
    pub frame: u32,
    pub pose: CameraPose,
    pub num_correspondences: usize,
    pub mean_reprojection_error: f64,
    pub max_reprojection_error: f64,
    pub all_points_in_front: bool,
}

/// Results of incremental pose estimation.
#[derive(Debug)]
pub struct IncrementalPoseResults {
    pub initial_frame_a: u32,
    pub initial_frame_b: u32,
    pub initial_pose_a: CameraPose,
    pub initial_pose_b: CameraPose,
    pub triangulated_points: Vec<Point3<f64>>,
    pub marker_ids: Vec<usize>,
    pub frame_results: Vec<PoseEstimationResult>,
}

/// Returns indices of markers that appear in both frames with valid data.
pub fn get_common_marker_ids(
    markers: &MarkersData,
    frame_a: u32,
    frame_b: u32,
) -> Result<Vec<usize>> {
    let mut common_ids = Vec::new();

    for (marker_idx, marker_data) in markers.frame_data.iter().enumerate() {
        let mut has_frame_a = false;
        let mut has_frame_b = false;

        for (i, &frame) in marker_data.frames.iter().enumerate() {
            if frame == frame_a && marker_data.weights[i] > 0.0 {
                has_frame_a = true;
            }
            if frame == frame_b && marker_data.weights[i] > 0.0 {
                has_frame_b = true;
            }
        }

        if has_frame_a && has_frame_b {
            common_ids.push(marker_idx);
        }
    }

    if common_ids.is_empty() {
        anyhow::bail!(
            "No common marker IDs found between frame {} and frame {}",
            frame_a,
            frame_b
        );
    }

    Ok(common_ids)
}

/// Extracts UV coordinates for specific marker indices in a given frame.
pub fn extract_uv_for_marker_ids(
    markers: &MarkersData,
    frame: u32,
    marker_ids: &[usize],
    image_size: &ImageSize<f64>,
) -> Result<Vec<Option<UvPoint2<f64>>>> {
    let mut uv_coords = Vec::with_capacity(marker_ids.len());

    for &marker_idx in marker_ids {
        if marker_idx >= markers.frame_data.len() {
            anyhow::bail!(
                "Marker index {} out of bounds (have {} markers)",
                marker_idx,
                markers.frame_data.len()
            );
        }

        let marker_data = &markers.frame_data[marker_idx];
        let mut found = None;

        for (i, &marker_frame) in marker_data.frames.iter().enumerate() {
            if marker_frame == frame && marker_data.weights[i] > 0.0 {
                // UV coordinates are already in 0-1 range in the data
                let u = marker_data.u_coords[i];
                let v = marker_data.v_coords[i];
                found = Some(UvPoint2::new(UvValue(u), UvValue(v)));
                break;
            }
        }

        uv_coords.push(found);
    }

    Ok(uv_coords)
}

/// Creates 2D-3D correspondences from UV coordinates and 3D points, filtering out invisible markers.
pub fn create_2d_3d_correspondences(
    uv_coords: &[Option<UvPoint2<f64>>],
    points_3d: &[Point3<f64>],
    intrinsics: &CameraIntrinsics,
    _image_size: &ImageSize<f64>,
) -> Vec<CameraToSceneCorrespondence<f64>> {
    assert_eq!(uv_coords.len(), points_3d.len());

    uv_coords
        .iter()
        .zip(points_3d.iter())
        .filter_map(|(uv_opt, point_3d)| {
            uv_opt.as_ref().map(|uv| {
                // Convert UV (0-1) to normalized camera coordinates
                // using the standard conversion: UV -> NDC -> camera coordinates
                let camera_coord =
                    uv_point_to_camera_coord_point(*uv, intrinsics);

                CameraToSceneCorrespondence::new(
                    camera_coord.x.value(),
                    camera_coord.y.value(),
                    point_3d.x,
                    point_3d.y,
                    point_3d.z,
                )
            })
        })
        .collect()
}

/// Computes reprojection errors in pixels for a PnP result.
pub fn compute_pnp_reprojection_errors(
    pose: &CameraPose,
    correspondences: &[CameraToSceneCorrespondence<f64>],
    intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
) -> Result<(Vec<f64>, ResidualStats)> {
    let mut residuals = Vec::with_capacity(correspondences.len());

    let camera_matrix = Matrix3::new(
        intrinsics.focal_length_x,
        0.0,
        intrinsics.principal_point.x.value(),
        0.0,
        intrinsics.focal_length_y,
        intrinsics.principal_point.y.value(),
        0.0,
        0.0,
        1.0,
    );

    for corr in correspondences {
        // Get the error in normalized coordinates
        let error_norm =
            calculate_reprojection_error(pose, &camera_matrix, corr);

        // Scale by average focal length to convert to pixel error.
        let avg_focal_length =
            (intrinsics.focal_length_x + intrinsics.focal_length_y) / 2.0;
        let error_pixels = error_norm * avg_focal_length;

        residuals.push(error_pixels);
    }

    let stats = compute_residual_statistics(&residuals);

    Ok((residuals, stats))
}

/// Returns true if all 3D points are in front of the camera and the camera position is valid.
pub fn validate_pnp_pose(
    pose: &CameraPose,
    points_3d: &[Point3<f64>],
) -> Result<bool> {
    for point in points_3d {
        if !pose.is_point_in_front(point) {
            return Ok(false);
        }
    }

    let center = pose.center();
    let distance_from_origin = center.coords.norm();
    if distance_from_origin < 0.001 {
        return Ok(false);
    }

    Ok(true)
}

/// Estimates camera pose using SQPnP, selecting the solution closest to the previous pose.
fn estimate_camera_pose(
    correspondences: &[CameraToSceneCorrespondence<f64>],
    previous_pose: Option<&CameraPose>,
) -> Result<CameraPose> {
    let num_corr = correspondences.len();

    if num_corr < 3 {
        anyhow::bail!(
            "Need at least 3 correspondences for PnP, got {}",
            num_corr
        );
    }

    // Use SQPnP for pose estimation.
    match compute_sqpnp_poses(correspondences) {
        Ok(poses) if !poses.is_empty() => {
            // Select best solution.
            let best_pose = if let Some(prev_pose) = previous_pose {
                // Choose closest to previous frame for temporal coherence.
                select_closest_pose(&poses, prev_pose)
            } else {
                // No previous pose; use first solution.
                poses[0].clone()
            };
            Ok(best_pose)
        }
        Ok(_) => todo!(),
        Err(_) => {
            bail!("SQPnP failed!")
        }
    }
}

/// Selects the pose closest to the reference pose.
fn select_closest_pose(
    poses: &[CameraPose],
    reference_pose: &CameraPose,
) -> CameraPose {
    let ref_center = reference_pose.center();

    poses
        .iter()
        .min_by(|a, b| {
            let dist_a = (a.center() - ref_center).norm();
            let dist_b = (b.center() - ref_center).norm();
            dist_a
                .partial_cmp(&dist_b)
                .unwrap_or(std::cmp::Ordering::Equal)
        })
        .unwrap()
        .clone()
}

/// Maps marker names to ground truth 3D positions, returning marker indices and 3D points.
fn create_marker_to_3d_mapping(
    markers: &MarkersData,
    ground_truth_3d: &HashMap<&str, Point3<f64>>,
) -> Result<(Vec<usize>, Vec<Point3<f64>>)> {
    let mut marker_ids = Vec::new();
    let mut points_3d = Vec::new();

    for (marker_idx, marker_name) in markers.names.iter().enumerate() {
        if let Some(point_3d) = ground_truth_3d.get(marker_name.as_str()) {
            marker_ids.push(marker_idx);
            points_3d.push(*point_3d);
        }
    }

    if marker_ids.is_empty() {
        anyhow::bail!(
            "No markers found matching the expected names. Available markers: {:?}",
            markers.names
        );
    }

    Ok((marker_ids, points_3d))
}

/// Generates 3D trajectory visualizations for all camera poses.
fn generate_trajectory_visualizations(
    frame_results: &[PoseEstimationResult],
    points_3d: &[Point3<f64>],
    intrinsics: &CameraIntrinsics,
    dataset_name: &str,
    base_naming: &OutputFileNaming,
    views: Vec<ViewConfiguration>,
) -> Result<()> {
    if DEBUG {
        println!("  Generating 3D trajectory views...");
    }

    let mut all_camera_poses = Vec::new();

    for result in frame_results {
        all_camera_poses.push(scene::CameraPoseWithFrame {
            frame: result.frame,
            pose: result.pose.clone(),
            is_initial: false, // All poses are equal, no special "initial" frames
        });
    }

    all_camera_poses.sort_by_key(|cpf| cpf.frame);

    if DEBUG {
        println!("    Visualizing {} camera poses", all_camera_poses.len());
    }
    let step_by_frames = 10;
    scene::visualize_sfm_trajectory_views(
        &all_camera_poses,
        points_3d,
        dataset_name,
        base_naming,
        views,
        intrinsics,
        step_by_frames,
        None, // No visibility filtering
    )?;

    if DEBUG {
        println!("    3D trajectory views generated");
    }
    Ok(())
}

/// Generates reprojection error and correspondence count plots over time.
fn generate_error_plots(
    frame_results: &[PoseEstimationResult],
    base_naming: &OutputFileNaming,
) -> Result<()> {
    if DEBUG {
        println!("  Generating error plots...");
    }

    // Create error vs frame plot
    let naming_errors =
        base_naming.clone_with_visualization(VisualizationType::ErrorsLinePlot);
    let error_plot_path = naming_errors.full_path()?;

    let resolution = (1920, 1080);
    let area =
        BitMapBackend::new(&error_plot_path, resolution).into_drawing_area();
    area.fill(&WHITE)?;

    let frames: Vec<u32> = frame_results.iter().map(|r| r.frame).collect();
    let errors: Vec<f64> = frame_results
        .iter()
        .map(|r| r.mean_reprojection_error)
        .collect();

    // TODO: For "clean" tests, this seems to get a value of '2', not
    // '1' as I would expect. Therefore the output images are `0002`,
    // `0012`, etc.
    let min_frame = *frames.first().unwrap_or(&1);
    let max_frame = *frames.last().unwrap_or(&100);
    let max_error = errors.iter().fold(0.0f64, |a, &b| a.max(b)).max(0.001);

    let mut chart = ChartBuilder::on(&area)
        .caption(
            "Camera Pose from Bundles - Reprojection Errors",
            ("sans-serif", 24),
        )
        .margin(60)
        .x_label_area_size(50)
        .y_label_area_size(80)
        .build_cartesian_2d(min_frame..max_frame, 0.0..max_error * 1.1)?;

    chart
        .configure_mesh()
        .x_desc("Frame Number")
        .y_desc("Mean Reprojection Error (pixels)")
        .draw()?;

    chart
        .draw_series(LineSeries::new(
            frames.iter().zip(errors.iter()).map(|(&f, &e)| (f, e)),
            BLUE.stroke_width(2),
        ))?
        .label("Mean Error")
        .legend(|(x, y)| {
            PathElement::new(vec![(x, y), (x + 10, y)], BLUE.stroke_width(2))
        });

    chart
        .configure_series_labels()
        .background_style(&WHITE.mix(0.8))
        .border_style(&BLACK)
        .draw()?;

    area.present()?;
    if DEBUG {
        println!("    Error plot saved to: {}", error_plot_path.display());
    }

    // Create correspondence count plot
    let naming_corr = base_naming
        .clone_with_visualization(VisualizationType::CorrespondencesLinePlot);
    let corr_plot_path = naming_corr.full_path()?;

    let area =
        BitMapBackend::new(&corr_plot_path, resolution).into_drawing_area();
    area.fill(&WHITE)?;

    let correspondences: Vec<usize> = frame_results
        .iter()
        .map(|r| r.num_correspondences)
        .collect();

    let max_corr = correspondences.iter().max().unwrap_or(&8);

    let mut chart = ChartBuilder::on(&area)
        .caption(
            "Camera Pose from Bundles - Correspondence Count",
            ("sans-serif", 24),
        )
        .margin(60)
        .x_label_area_size(50)
        .y_label_area_size(80)
        .build_cartesian_2d(min_frame..max_frame, 0..*max_corr + 1)?;

    chart
        .configure_mesh()
        .x_desc("Frame Number")
        .y_desc("Number of Correspondences")
        .draw()?;

    chart
        .draw_series(LineSeries::new(
            frames
                .iter()
                .zip(correspondences.iter())
                .map(|(&f, &c)| (f, c)),
            RED.stroke_width(2),
        ))?
        .label("Correspondences")
        .legend(|(x, y)| {
            PathElement::new(vec![(x, y), (x + 10, y)], RED.stroke_width(2))
        });

    chart
        .configure_series_labels()
        .background_style(&WHITE.mix(0.8))
        .border_style(&BLACK)
        .draw()?;

    area.present()?;
    if DEBUG {
        println!(
            "    Correspondence plot saved to: {}",
            corr_plot_path.display()
        );
    }

    Ok(())
}

/// Runs camera pose estimation from known 3D bundle positions across all frames.
pub fn run_camera_pose_from_bundles_dataset_test(
    markers: &MarkersData,
    ground_truth_3d: HashMap<&str, Point3<f64>>,
    min_expected_markers: usize,
    dataset_name: &str,
    base_naming: &OutputFileNaming,
    views: Vec<ViewConfiguration>,
    focal_length: MillimeterUnit<f64>,
    film_back: CameraFilmBack<f64>,
    image_size: ImageSize<f64>,
    min_success_rate_percent: Option<usize>,
    max_mean_error_pixels: Option<f64>,
    max_max_error_pixels: Option<f64>,
) -> Result<()> {
    if DEBUG {
        println!("\nCamera Pose from Bundles Test - {}", dataset_name);
        println!("=====================================================\n");
    }

    let intrinsics =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);

    if DEBUG {
        println!("Phase 1: Setting up 3D points from ground truth");
        println!("------------------------------------------------");
    }

    let (marker_ids, points_3d) =
        create_marker_to_3d_mapping(markers, &ground_truth_3d)?;

    if DEBUG {
        println!(
            "  Loaded {} 3D points for {} markers",
            points_3d.len(),
            marker_ids.len()
        );
    }

    if marker_ids.len() < min_expected_markers {
        anyhow::bail!(
            "Expected at least {} markers, but found only {}",
            min_expected_markers,
            marker_ids.len()
        );
    }

    if DEBUG {
        for (i, marker_id) in marker_ids.iter().enumerate() {
            let pt = &points_3d[i];
            println!(
                "    Marker {}: {} -> ({:.2}, {:.2}, {:.2})",
                marker_id, markers.names[*marker_id], pt.x, pt.y, pt.z
            );
        }
        println!();
    }

    if DEBUG {
        println!("Phase 2: Incremental pose estimation (frames 1-101)");
        println!("----------------------------------------------------");
    }

    let mut frame_results: Vec<PoseEstimationResult> = Vec::new();
    let mut previous_pose: Option<CameraPose> = None;

    for frame in 1..=101 {
        // Extract UV coordinates for each tracked marker.
        let uv_coords_opt = extract_uv_for_marker_ids(
            markers,
            frame,
            &marker_ids,
            &image_size,
        )?;

        // Create 2D-3D correspondences.
        let correspondences = create_2d_3d_correspondences(
            &uv_coords_opt,
            &points_3d,
            &intrinsics,
            &image_size,
        );

        if correspondences.is_empty() {
            if DEBUG {
                println!("  Frame {}: No correspondences, skipping.", frame);
            }
            continue;
        }

        if correspondences.len() < 3 {
            if DEBUG {
                println!(
                    "  Frame {}: Only {} correspondences, need at least 3, skipping.",
                    frame,
                    correspondences.len()
                );
            }
            continue;
        }

        let estimated_pose = match estimate_camera_pose(
            &correspondences,
            previous_pose.as_ref(),
        ) {
            Ok(result) => result,
            Err(e) => {
                if DEBUG {
                    println!(
                        "  Frame {}: Pose estimation failed: {}",
                        frame, e
                    );
                }
                continue;
            }
        };

        let is_valid = validate_pnp_pose(&estimated_pose, &points_3d)?;
        if !is_valid {
            if DEBUG {
                println!("  Frame {}: Pose validation failed, skipping", frame);
            }
            continue;
        }

        let (residuals, stats) = compute_pnp_reprojection_errors(
            &estimated_pose,
            &correspondences,
            &intrinsics,
            &image_size,
        )?;

        let all_in_front = points_3d
            .iter()
            .all(|pt| estimated_pose.is_point_in_front(pt));

        let result = PoseEstimationResult {
            frame,
            pose: estimated_pose.clone(),
            num_correspondences: correspondences.len(),
            mean_reprojection_error: stats.mean,
            max_reprojection_error: stats.max,
            all_points_in_front: all_in_front,
        };

        frame_results.push(result);
        previous_pose = Some(estimated_pose);

        // Print progress every 10 frames.
        if DEBUG {
            if frame % 10 == 0 || frame == 1 {
                println!(
                    "  Frame {}: {} correspondences, mean error: {:.6} px, max error: {:.6} px",
                    frame,
                    correspondences.len(),
                    stats.mean,
                    stats.max,
                );
            }
        }
    }

    if DEBUG {
        println!();
    }

    if DEBUG {
        println!("Phase 3: Validation");
        println!("-------------------");
    }

    let expected_frames = 101; // frames 1-101
    let successful_frames = frame_results.len();

    if DEBUG {
        println!("  Expected frames: {}", expected_frames);
        println!("  Successful frames: {}", successful_frames);
        println!(
            "  Success rate: {:.1}%",
            (successful_frames as f64 / expected_frames as f64) * 100.0
        );
    }

    let all_mean_errors: Vec<f64> = frame_results
        .iter()
        .map(|r| r.mean_reprojection_error)
        .collect();
    let all_max_errors: Vec<f64> = frame_results
        .iter()
        .map(|r| r.max_reprojection_error)
        .collect();

    let overall_mean =
        all_mean_errors.iter().sum::<f64>() / all_mean_errors.len() as f64;
    let overall_max = all_max_errors.iter().fold(0.0f64, |a, &b| a.max(b));

    if DEBUG {
        println!(
            "  Overall mean reprojection error: {:.6} pixels",
            overall_mean
        );
        println!(
            "  Overall max reprojection error: {:.6} pixels",
            overall_max
        );
    }

    let all_valid = frame_results.iter().all(|r| r.all_points_in_front);
    if DEBUG {
        println!("  All points in front of cameras: {}", all_valid);

        println!();
    }

    let min_success_rate = min_success_rate_percent.unwrap_or(95);
    let max_mean_error = max_mean_error_pixels.unwrap_or(1.0);
    let max_max_error = max_max_error_pixels.unwrap_or(5.0);

    assert!(
        successful_frames >= expected_frames * min_success_rate / 100,
        "Should successfully estimate at least {}% of frames with known 3D points, got {}/{} ({:.1}%)",
        min_success_rate,
        successful_frames,
        expected_frames,
        (successful_frames as f64 / expected_frames as f64) * 100.0
    );

    assert!(
        overall_mean < max_mean_error,
        "Mean reprojection error should be < {} pixels, got {:.6}",
        max_mean_error,
        overall_mean
    );

    assert!(
        overall_max < max_max_error,
        "Max reprojection error should be < {} pixels, got {:.6}",
        max_max_error,
        overall_max
    );

    assert!(
        all_valid,
        "All points should be in front of all estimated camera poses"
    );

    if DEBUG {
        println!("Phase 4: Generating visualizations");
        println!("----------------------------------");
    }

    generate_trajectory_visualizations(
        &frame_results,
        &points_3d,
        &intrinsics,
        dataset_name,
        base_naming,
        views,
    )?;

    generate_error_plots(&frame_results, base_naming)?;

    if DEBUG {
        println!("\nTest completed successfully!");
        println!("  Estimated poses for {} frames", successful_frames);
        println!("  Mean reprojection error: {:.6} pixels", overall_mean);
        println!("  Max reprojection error: {:.6} pixels", overall_max);
    }

    Ok(())
}
