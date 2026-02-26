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

//! Common camera solve utilities for testing.

use anyhow::Result;
use nalgebra::Point3;
use plotters::{
    prelude::{
        BitMapBackend, ChartBuilder, Circle, Cross, IntoDrawingArea,
        LineSeries, PathElement, Rectangle, Text, BLACK, BLUE, GREEN, MAGENTA,
        RED, WHITE,
    },
    style::Color,
};
use rayon::prelude::*;
use std::collections::{HashMap, HashSet};
use std::time::Instant;

use mmio::uvtrack_reader::{FrameNumber, FrameRange, MarkersData};
use mmsfm_rust::camera_residual_error::{
    compute_per_frame_per_marker_residuals,
    project_scene_point_3d_to_uv_point_2d, ResidualStats,
};
use mmsfm_rust::datatype::conversions::convert_uv_to_pixel_point;
use mmsfm_rust::datatype::{
    BundlePositions, CameraFilmBack, CameraIntrinsics, CameraPose, CameraPoses,
    ImageSize, MillimeterUnit, UnitValue, UvValue,
};
use mmsfm_rust::sfm_camera::{
    camera_solve, CameraSolveConfig, GlobalAdjustmentConfig,
    SolveQualityMetrics,
};

use crate::common::visualization::scene::{self, ViewConfiguration};
use crate::common::visualization::{reprojection, residuals};
use crate::common::{OutputFileNaming, VisualizationType};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Converts camera poses to a sorted trajectory vector.
fn camera_poses_to_trajectory(
    poses: &CameraPoses,
    initial_frames: &[FrameNumber],
) -> Vec<scene::CameraPoseWithFrame> {
    let mut trajectory: Vec<scene::CameraPoseWithFrame> = poses
        .iter()
        .map(|(&frame, pose)| scene::CameraPoseWithFrame {
            frame,
            pose: pose.clone(),
            is_initial: initial_frames.contains(&frame),
        })
        .collect();

    // Sort by frame number for coherent trajectory.
    trajectory.sort_by_key(|entry| entry.frame);

    trajectory
}

/// Converts bundle positions map to a sorted vector.
fn bundle_map_to_vec(bundles: &BundlePositions) -> Vec<Point3<f64>> {
    let mut bundle_vec: Vec<(usize, Point3<f64>)> =
        bundles.iter().map(|(&idx, &pos)| (idx, pos)).collect();

    bundle_vec.sort_by_key(|(idx, _)| *idx);

    bundle_vec.into_iter().map(|(_, pos)| pos).collect()
}

/// Computes a map from frame number to the set of visible bundle indices.
fn compute_bundle_visibility(
    markers: &MarkersData,
    bundle_positions: &BundlePositions,
) -> scene::BundleVisibilityMap {
    let mut marker_indices: Vec<usize> =
        bundle_positions.keys().copied().collect();
    marker_indices.sort();

    let marker_to_vec_idx: HashMap<usize, usize> = marker_indices
        .iter()
        .enumerate()
        .map(|(vec_idx, &marker_idx)| (marker_idx, vec_idx))
        .collect();

    let mut visibility_map: scene::BundleVisibilityMap = HashMap::new();

    for &marker_idx in &marker_indices {
        let frame_data = &markers.frame_data[marker_idx];
        let vec_idx = marker_to_vec_idx[&marker_idx];

        for &frame in &frame_data.frames {
            visibility_map
                .entry(frame)
                .or_insert_with(HashSet::new)
                .insert(vec_idx);
        }
    }

    visibility_map
}

/// Generates per-frame 2D images showing observed vs reprojected markers.
fn generate_per_frame_marker_reprojections_2d(
    markers: &MarkersData,
    solved_poses: &CameraPoses,
    bundle_positions: &BundlePositions,
    intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
    base_naming: &OutputFileNaming,
    step_by: usize,
) -> Result<()> {
    let mut frame_list: Vec<_> = solved_poses.keys().copied().collect();
    frame_list.sort();

    if DEBUG {
        println!(
            "  Generating per-frame 2D marker reprojection visualizations..."
        );
    }

    if let Some(&first_frame) = frame_list.first() {
        let example_naming = base_naming
            .clone_with_visualization(VisualizationType::MarkerReprojection2d)
            .clone_with_frame(first_frame);
        if let Ok(example_path) = example_naming.full_path() {
            print!("Generating 2D reprojections: {} ", example_path.display());
            let _ = std::io::Write::flush(&mut std::io::stdout());
        }
    }

    frame_list.par_iter().step_by(step_by).try_for_each(
        |&frame| -> Result<()> {
            let pose = &solved_poses[&frame];

            let mut observed_pixels = Vec::new();
            let mut reprojected_pixels = Vec::new();
            let mut marker_names = Vec::new();

            for (marker_idx, frame_data) in
                markers.frame_data.iter().enumerate()
            {
                if let Some(data_idx) =
                    frame_data.frames.iter().position(|&f| f == frame)
                {
                    if let Some(&bundle_pos) = bundle_positions.get(&marker_idx)
                    {
                        let u = frame_data.u_coords[data_idx];
                        let v = frame_data.v_coords[data_idx];
                        let observed_uv = UvValue::point2(u, v);
                        let observed_px =
                            convert_uv_to_pixel_point(observed_uv, image_size);

                        if let Some(projected_uv) =
                            project_scene_point_3d_to_uv_point_2d(
                                &bundle_pos,
                                pose,
                                intrinsics,
                            )
                        {
                            let projected_px = convert_uv_to_pixel_point(
                                projected_uv,
                                image_size,
                            );

                            observed_pixels.push((
                                observed_px.x.value(),
                                observed_px.y.value(),
                            ));
                            reprojected_pixels.push((
                                projected_px.x.value(),
                                projected_px.y.value(),
                            ));
                            marker_names
                                .push(markers.names[marker_idx].clone());
                        }
                    }
                }
            }

            if observed_pixels.is_empty() {
                return Ok(());
            }

            let frame_naming = base_naming
                .clone_with_visualization(
                    VisualizationType::MarkerReprojection2d,
                )
                .clone_with_frame(frame);
            let file_path = frame_naming.full_path()?;

            let resolution = (1920u32, 1080u32);
            let area =
                BitMapBackend::new(&file_path, resolution).into_drawing_area();
            area.fill(&WHITE)?;

            let image_width = image_size.width.value();
            let image_height = image_size.height.value();
            let x_min = -image_width * 0.1;
            let x_max = image_width * 1.1;
            let y_min = -image_height * 0.1;
            let y_max = image_height * 1.1;

            let mut chart = ChartBuilder::on(&area)
                .caption(
                    &format!("Frame {} - Marker Reprojections", frame),
                    ("sans-serif", 30),
                )
                .margin(60)
                .x_label_area_size(50)
                .y_label_area_size(80)
                .build_cartesian_2d(x_min..x_max, y_min..y_max)?;

            chart
                .configure_mesh()
                .x_desc("X (pixels, 0=left)")
                .y_desc("Y (pixels, 0=bottom)")
                .draw()?;

            // Draw image boundary
            let boundary_style = MAGENTA.mix(0.6).stroke_width(2);
            chart.draw_series(LineSeries::new(
                vec![
                    (0.0, 0.0),
                    (image_width, 0.0),
                    (image_width, image_height),
                    (0.0, image_height),
                    (0.0, 0.0),
                ],
                boundary_style,
            ))?;

            // Draw error vectors
            for (obs, reproj) in
                observed_pixels.iter().zip(reprojected_pixels.iter())
            {
                if obs.0.is_finite()
                    && obs.1.is_finite()
                    && reproj.0.is_finite()
                    && reproj.1.is_finite()
                {
                    chart.draw_series(LineSeries::new(
                        vec![*obs, *reproj],
                        GREEN.mix(0.5).stroke_width(1),
                    ))?;
                }
            }

            // Draw observed markers (blue circles)
            chart
                .draw_series(
                    observed_pixels
                        .iter()
                        .filter(|pt| pt.0.is_finite() && pt.1.is_finite())
                        .map(|pt| Circle::new(*pt, 5, BLUE.filled())),
                )?
                .label("Observed")
                .legend(|(x, y)| Circle::new((x + 10, y), 5, BLUE.filled()));

            // Draw reprojected markers (red crosses)
            chart
                .draw_series(
                    reprojected_pixels
                        .iter()
                        .filter(|pt| pt.0.is_finite() && pt.1.is_finite())
                        .map(|pt| Cross::new(*pt, 5, RED.stroke_width(2))),
                )?
                .label("Reprojected")
                .legend(|(x, y)| {
                    Cross::new((x + 10, y), 5, RED.stroke_width(2))
                });

            chart
                .configure_series_labels()
                .background_style(&WHITE.mix(0.8))
                .border_style(&BLACK)
                .draw()?;

            area.present()?;

            print!(".");
            let _ = std::io::Write::flush(&mut std::io::stdout());

            Ok(())
        },
    )?;

    println!();

    if DEBUG {
        println!(
            "    Generated {} 2D marker reprojection frames",
            frame_list.len()
        );
    }

    Ok(())
}

/// Generates per-frame 3D trajectory visualizations with camera history.
fn generate_per_frame_3d_trajectory(
    markers: &MarkersData,
    solved_poses: &CameraPoses,
    bundle_positions: &BundlePositions,
    base_naming: &OutputFileNaming,
    views: &[ViewConfiguration],
    intrinsics: &CameraIntrinsics,
    step_by: usize,
) -> Result<()> {
    if DEBUG {
        println!("  Generating per-frame 3D trajectory visualizations with history...");
    }

    let mut trajectory: Vec<scene::CameraPoseWithFrame> = solved_poses
        .iter()
        .map(|(&frame, pose)| {
            // Mark the first two frames as initial poses.
            let is_initial = frame == 1 || frame == 2;
            scene::CameraPoseWithFrame {
                frame,
                pose: pose.clone(),
                is_initial,
            }
        })
        .collect();

    trajectory.sort_by_key(|cpf| cpf.frame);

    let bundle_points = bundle_map_to_vec(bundle_positions);

    let bundle_visibility =
        compute_bundle_visibility(markers, bundle_positions);

    scene::visualize_sfm_trajectory_views(
        &mmlogger::NoOpLogger,
        &trajectory,
        &bundle_points,
        "Camera Solve",
        base_naming,
        views.to_vec(),
        intrinsics,
        step_by,
        Some(&bundle_visibility),
    )?;

    if DEBUG {
        println!(
            "  Per-frame 3D trajectory visualizations with history generated"
        );
    }

    Ok(())
}

/// Runs a camera solve test on a dataset, including visualizations.
pub fn run_camera_solve_dataset_test(
    markers: &MarkersData,
    frame_range: FrameRange,
    dataset_name: &str,
    base_naming: &OutputFileNaming,
    views: Vec<ViewConfiguration>,
    focal_length: MillimeterUnit<f64>,
    film_back: CameraFilmBack<f64>,
    image_size: ImageSize<f64>,
    config: CameraSolveConfig,
    global_adjustment_config: Option<&GlobalAdjustmentConfig>,
    step_by: usize,
) -> Result<()> {
    let test_start_time = Instant::now();

    if DEBUG {
        println!(
            "\n=== Camera Solve Test with {} Dataset ===\n",
            dataset_name
        );
        println!("Solver type: {:?}", config.bundle_solver_type);
    }
    if DEBUG {
        println!("Step 1: Setting up initial camera intrinsics...");
    }
    let initial_intrinsics =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);
    if DEBUG {
        println!("  Initial focal length: {} mm", focal_length.value());
        println!(
            "  Principal point: ({}, {})",
            initial_intrinsics.principal_point.x.value(),
            initial_intrinsics.principal_point.y.value()
        );
    }

    if DEBUG {
        println!("\nStep 2: Running camera solve...");
    }
    let camera_solve_start = Instant::now();
    let mut solved_poses = CameraPoses::new();
    let mut bundle_positions = BundlePositions::new();
    let mut metrics = SolveQualityMetrics::default();

    let mut noop_logger = mmlogger::NoOpLogger;
    camera_solve(
        &mut noop_logger,
        frame_range,
        markers,
        &initial_intrinsics,
        &film_back,
        &image_size,
        &config,
        global_adjustment_config,
        None, // No intermediate writer in tests.
        &mut solved_poses,
        &mut bundle_positions,
        &mut metrics,
    )?;
    let camera_solve_time_ms =
        camera_solve_start.elapsed().as_secs_f64() * 1000.0;

    if DEBUG {
        println!("  Camera solve completed");
        println!("  Camera solve time: {:.2} ms", camera_solve_time_ms);
        println!("  Frames solved: {}", metrics.frames_solved);
        println!("  Frames unsolved: {}", metrics.frames_unsolved);
        println!(
            "  Bundles triangulated: {}",
            metrics.total_bundles_triangulated
        );
    }

    // Use the optimised focal length if global adjustment was performed.
    let intrinsics = if let Some(optimized_fl_mm) =
        metrics.optimized_focal_length_mm
    {
        let optimized_focal_length = MillimeterUnit::new(optimized_fl_mm);
        if DEBUG {
            println!(
                "  Using optimized focal length: {:.2} mm (initial was {:.2} mm)",
                optimized_fl_mm,
                focal_length.value()
            );
        }
        CameraIntrinsics::from_centered_lens(optimized_focal_length, film_back)
    } else {
        if DEBUG {
            println!(
                "  Using initial focal length: {:.2} mm",
                focal_length.value()
            );
        }
        initial_intrinsics
    };

    if DEBUG {
        println!("\nStep 3: Preparing data for visualization...");
    }
    let initial_frames = vec![frame_range.start_frame, frame_range.end_frame];
    let camera_trajectory =
        camera_poses_to_trajectory(&solved_poses, &initial_frames);
    let bundle_points = bundle_map_to_vec(&bundle_positions);

    if DEBUG {
        println!("  Camera trajectory: {} poses", camera_trajectory.len());
        println!("  Bundle points: {}", bundle_points.len());
    }

    if DEBUG {
        println!("\nStep 4: Computing and visualizing residual errors...");
    }

    let (per_frame_residuals, residual_stats) =
        compute_per_frame_per_marker_residuals(
            markers,
            &solved_poses,
            &bundle_positions,
            &intrinsics,
            &image_size,
        )?;

    if DEBUG {
        println!(
            "  Computed residuals for {} frames",
            per_frame_residuals.len()
        );
        println!("  Overall residual statistics:");
        println!("    Mean: {:.4} px", residual_stats.mean);
        println!("    Median: {:.4} px", residual_stats.median);
        println!("    Std Dev: {:.4} px", residual_stats.std_dev);
        println!("    Min: {:.4} px", residual_stats.min);
        println!("    Max: {:.4} px", residual_stats.max);
    }

    let title_residuals =
        format!("{} - Per-Frame Reprojection Errors", dataset_name);
    let naming_residuals = base_naming
        .clone_with_visualization(VisualizationType::ResidualsLinePlot);

    residuals::visualize_multi_frame_residuals_per_marker(
        &mmlogger::NoOpLogger,
        &per_frame_residuals,
        Some(&markers.names),
        &residual_stats,
        &title_residuals,
        &naming_residuals,
    )?;

    if DEBUG {
        println!("  Per-frame residual timeline visualization generated");
    }

    if DEBUG {
        println!("\nStep 6: Generating per-frame 2D marker reprojection visualizations...");
    }
    generate_per_frame_marker_reprojections_2d(
        markers,
        &solved_poses,
        &bundle_positions,
        &intrinsics,
        &image_size,
        base_naming,
        step_by,
    )?;

    if DEBUG {
        println!(
            "\nStep 7: Generating per-frame 3D trajectory visualizations..."
        );
    }
    generate_per_frame_3d_trajectory(
        markers,
        &solved_poses,
        &bundle_positions,
        base_naming,
        &views,
        &intrinsics,
        step_by,
    )?;

    if DEBUG {
        println!("\n=== Camera Solve Test Complete ===\n");
    }

    assert!(
        solved_poses.len() >= 2,
        "Should solve at least 2 frames, got {}",
        solved_poses.len()
    );
    assert!(
        bundle_positions.len() >= 5,
        "Should triangulate at least 5 bundles, got {}",
        bundle_positions.len()
    );

    Ok(())
}
