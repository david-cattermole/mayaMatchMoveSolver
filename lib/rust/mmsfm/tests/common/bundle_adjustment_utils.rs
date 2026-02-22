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

//! Common bundle adjustment utilities for testing.

use anyhow::Result;
use nalgebra::Point3;
use std::time::Instant;

use mmio::uvtrack_reader::MarkersData;
use mmoptimise::solver::common::OptimisationProblem;
use mmoptimise::solver::levenberg_marquardt::{
    LevenbergMarquardtConfig, LevenbergMarquardtSolver,
    LevenbergMarquardtWorkspace,
};
use mmsfm_rust::bundle_adjust::{
    rotation_matrix_and_translation_to_camera_pose,
    rotation_matrix_to_full_quaternion, TwoCameraBAProblem,
};
use mmsfm_rust::bundle_triangulation::triangulate_points_from_relative_pose;
use mmsfm_rust::camera_relative_pose::compute_relative_pose_optimal_angular;
use mmsfm_rust::camera_relative_pose::{
    // compute_essential_matrix, create_bearing_vector_correspondences,
    RelativePoseInfo,
};
use mmsfm_rust::camera_residual_error::{
    compute_reprojection_residuals, compute_residual_statistics,
};
use mmsfm_rust::datatype::camera_pose::CameraPose;
use mmsfm_rust::datatype::conversions::convert_uv_to_ndc_point;
use mmsfm_rust::datatype::{
    CameraFilmBack, CameraIntrinsics, ImageSize, MillimeterUnit, UnitValue,
    UvPoint2,
};
use mmsfm_rust::sfm_camera::BundleAdjustmentSolverType;

use crate::common::extract_point_correspondences;
use crate::common::visualization::scene::{self, ViewConfiguration};
use crate::common::visualization::{reprojection, residuals};
use crate::common::{FramePair, OutputFileNaming, Stage, VisualizationType};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Converts UV coordinates to NDC observations for bundle adjustment, skipping invalid points.
fn create_observations(
    uv_coords_a: &[UvPoint2<f64>],
    uv_coords_b: &[UvPoint2<f64>],
    triangulated_valid: &[bool],
) -> Vec<(usize, usize, f64, f64)> {
    let mut observations = Vec::new();
    let mut filtered_idx = 0;

    for (point_idx, (&uv_a, &uv_b)) in
        uv_coords_a.iter().zip(uv_coords_b.iter()).enumerate()
    {
        if triangulated_valid[point_idx] {
            // Convert UV coordinates to NDC coordinates for bundle
            // adjustment.
            let ndc_a = convert_uv_to_ndc_point(uv_a);
            let ndc_b = convert_uv_to_ndc_point(uv_b);

            // Use filtered_idx to reference the position in the
            // filtered points array.
            observations.push((
                0,
                filtered_idx,
                ndc_a.x.value(),
                ndc_a.y.value(),
            ));
            observations.push((
                1,
                filtered_idx,
                ndc_b.x.value(),
                ndc_b.y.value(),
            ));

            filtered_idx += 1;
        }
    }

    observations
}

/// Runs a complete bundle adjustment test on a dataset, including visualizations.
pub fn run_bundle_adjustment_dataset_test(
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
    solver_type: BundleAdjustmentSolverType,
    point_indices: Option<Vec<usize>>,
) -> Result<()> {
    let test_start_time = Instant::now();

    if DEBUG {
        println!(
            "\n=== Bundle Adjustment Test with {} Dataset ===\n",
            dataset_name
        );
        println!("Solver type: {:?}", solver_type);

        // 1. Validate marker data.
        println!("Step 1: Validating marker data...");
    }
    assert!(
        markers.frame_data.len() >= expected_min_markers,
        "Expected at least {} markers, found {}",
        expected_min_markers,
        markers.frame_data.len()
    );
    if DEBUG {
        println!("  Total markers: {}", markers.frame_data.len());
        println!(
            "  Using frame pair: {} -> {}",
            frame_pair.frame_a, frame_pair.frame_b
        );

        // 2. Setup camera intrinsics.
        println!("\nStep 2: Setting up camera intrinsics...");
    }
    let intrinsics_a =
        CameraIntrinsics::from_centered_lens(focal_length, film_back);
    let intrinsics_b = intrinsics_a.clone();
    if DEBUG {
        println!("  Focal length: {} mm", focal_length.value());
        println!(
            "  Principal point: ({}, {})",
            intrinsics_a.principal_point.x.value(),
            intrinsics_a.principal_point.y.value()
        );

        // 3. Extract point correspondences.
        println!("\nStep 3: Extracting point correspondences...");
    }
    let (uv_coords_a, uv_coords_b) = extract_point_correspondences(
        markers,
        frame_pair.clone(),
        point_indices,
    )?;
    if DEBUG {
        println!("  Point correspondences extracted: {}", uv_coords_a.len());

        // 4. Compute initial relative pose.
        println!("\nStep 4: Computing initial relative pose...");
    }
    let relative_pose_start = Instant::now();
    let pose_info = compute_relative_pose_optimal_angular(
        &intrinsics_a,
        &intrinsics_b,
        &uv_coords_a,
        &uv_coords_b,
    )?;
    let relative_pose_time_ms =
        relative_pose_start.elapsed().as_secs_f64() * 1000.0;
    if DEBUG {
        println!("  Relative pose computed successfully");
        println!("  Time: {:.2} ms", relative_pose_time_ms);

        // 5. Triangulate initial 3D points.
        println!("\nStep 5: Triangulating initial 3D points...");
    }
    let triangulation_1_start = Instant::now();
    let mut triangulated_points = vec![Point3::origin(); uv_coords_a.len()];
    let mut triangulated_valid = vec![false; uv_coords_a.len()];
    let triangulated_count = triangulate_points_from_relative_pose(
        &intrinsics_a,
        &intrinsics_b,
        &uv_coords_a,
        &uv_coords_b,
        &pose_info,
        &mut triangulated_points,
        &mut triangulated_valid,
    )?;
    let triangulation_1_time_ms =
        triangulation_1_start.elapsed().as_secs_f64() * 1000.0;
    if DEBUG {
        println!(
            "  Triangulated {}/{} points successfully",
            triangulated_count,
            uv_coords_a.len()
        );
        println!("  Time: {:.2} ms", triangulation_1_time_ms);

        // 6. Generate visualizations with INITIAL state.
        println!("\nStep 6: Generating visualizations with initial state...");
    }
    let visualization_start = Instant::now();

    // Filter to only valid triangulated points.
    let mut filtered_uv_a_initial = Vec::new();
    let mut filtered_uv_b_initial = Vec::new();
    let mut filtered_points_3d_initial = Vec::new();
    for (i, &is_valid) in triangulated_valid.iter().enumerate() {
        if is_valid {
            filtered_uv_a_initial.push(uv_coords_a[i]);
            filtered_uv_b_initial.push(uv_coords_b[i]);
            filtered_points_3d_initial.push(triangulated_points[i]);
        }
    }

    let pose_a = CameraPose::default(); // Identity pose.
    let pose_b = &pose_info.relative_pose;

    let title_initial =
        format!("{} - Bundle Adjustment (Initial)", dataset_name);
    let output_image_size = ImageSize::full_hd();

    // Create stage-specific naming objects
    let naming_initial_scene = base_naming
        .clone_with_stage(Stage::Initial)
        .clone_with_visualization(VisualizationType::Scene3d);
    let naming_initial_marker_2d = base_naming
        .clone_with_stage(Stage::Initial)
        .clone_with_visualization(VisualizationType::MarkerReprojection2d);
    let naming_initial_residuals = base_naming
        .clone_with_stage(Stage::Initial)
        .clone_with_visualization(VisualizationType::ResidualsLinePlot);

    // Generate all initial visualizations in parallel
    let initial_stats_viz = std::thread::scope(|s| {
        // Task 1: 3D scene views
        let handle_3d = s.spawn(|| {
            scene::visualize_sfm_scene_views(
                &pose_a,
                &pose_b,
                &filtered_points_3d_initial,
                &title_initial,
                &naming_initial_scene,
                views.clone(),
                &intrinsics_a,
                &intrinsics_b,
            )
        });

        // Task 2: 2D marker reprojection
        let handle_2d = s.spawn(|| {
            reprojection::visualize_marker_reprojections_2d_scatter(
                &filtered_uv_a_initial,
                &filtered_uv_b_initial,
                &filtered_points_3d_initial,
                &pose_a,
                &pose_b,
                &intrinsics_a,
                &intrinsics_b,
                &image_size_a,
                &image_size_b,
                &frame_pair,
                &title_initial,
                &output_image_size,
                &naming_initial_marker_2d,
            )
        });

        // Task 3: Residual errors computation and visualization
        let handle_residuals = s.spawn(|| {
            let mut initial_residuals_viz =
                vec![0.0; filtered_points_3d_initial.len()];
            compute_reprojection_residuals(
                &filtered_points_3d_initial,
                &filtered_uv_a_initial,
                &filtered_uv_b_initial,
                &pose_a,
                &pose_b,
                &intrinsics_a,
                &intrinsics_b,
                &image_size_a,
                &image_size_b,
                &mut initial_residuals_viz,
            )?;

            let stats = compute_residual_statistics(&initial_residuals_viz);

            residuals::visualize_residual_errors_line_plot(
                &initial_residuals_viz,
                &stats,
                &format!("{} - Residual Errors", title_initial),
                &naming_initial_residuals,
            )?;

            Ok::<_, anyhow::Error>(stats)
        });

        // Wait for all tasks to complete
        handle_3d.join().unwrap()?;
        handle_2d.join().unwrap()?;
        let stats = handle_residuals.join().unwrap()?;

        Ok::<_, anyhow::Error>(stats)
    })?;

    let mut visualization_time_ms =
        visualization_start.elapsed().as_secs_f64() * 1000.0;

    if DEBUG {
        println!("  Initial visualizations generated in parallel");
        println!(
            "  Initial mean residual error: {:.4} pixels",
            initial_stats_viz.mean
        );
        println!(
            "  Initial median residual error: {:.4} pixels",
            initial_stats_viz.median
        );
        println!(
            "  Initial standard deviation: {:.4} pixels",
            initial_stats_viz.std_dev
        );
        println!("  Visualization time: {:.2} ms", visualization_time_ms);

        // 7. Convert to bundle adjustment format
        println!("\nStep 7: Preparing bundle adjustment problem...");
    }

    // Create observations only for valid triangulated points
    let observations =
        create_observations(&uv_coords_a, &uv_coords_b, &triangulated_valid);
    if DEBUG {
        println!("  Total observations: {}", observations.len());
    }

    let cam_b_rot = rotation_matrix_to_full_quaternion(pose_b.rotation());
    let cam_b_trans = [
        pose_b.translation().x,
        pose_b.translation().y,
        pose_b.translation().z,
    ];

    let initial_points: Vec<[f64; 3]> = filtered_points_3d_initial
        .iter()
        .map(|p| [p.x, p.y, p.z])
        .collect();

    // 8. Setup optimization (camera A fixed at identity, camera B optimized)
    if DEBUG {
        println!("  Camera A: fixed at identity");
        println!("  Camera B: optimized (5 params)");
        println!("  Points: {}", initial_points.len());
    }

    let problem = TwoCameraBAProblem::new(
        observations,
        intrinsics_a.focal_length_x,
        intrinsics_a.focal_length_y,
        (
            intrinsics_a.principal_point.x.value(),
            intrinsics_a.principal_point.y.value(),
        ),
        cam_b_rot,
        cam_b_trans,
        &initial_points,
    );

    if DEBUG {
        println!(
            "  Problem size: {} parameters, {} residuals",
            OptimisationProblem::parameter_count(&problem),
            OptimisationProblem::residual_count(&problem)
        );

        // 9. Compute initial cost
        println!("\nStep 9: Computing initial cost...");
    }
    let initial_params = problem.pack_parameters();
    let mut initial_residuals =
        vec![0.0; OptimisationProblem::residual_count(&problem)];
    problem.residuals(&initial_params, &mut initial_residuals)?;
    let initial_cost =
        0.5 * initial_residuals.iter().map(|r| r.powi(2)).sum::<f64>();
    if DEBUG {
        println!("  Initial cost: {:.6e}", initial_cost);

        let initial_rms =
            (2.0 * initial_cost / initial_residuals.len() as f64).sqrt();
        println!("  Initial RMS error: {:.4} pixels", initial_rms);

        // 10. Run bundle adjustment
        println!("\nStep 10: Running bundle adjustment optimization...");
    }
    let bundle_adjustment_1_start = Instant::now();

    // Always use dense LM solver (TwoCameraBAProblem has only 5+3N params).
    let result = {
        if DEBUG {
            println!("  Using Dense QR-based Levenberg-Marquardt solver");
        }
        let mut config = LevenbergMarquardtConfig::default();
        config.max_iterations = 500;
        config.max_function_evaluations = 10000;

        let solver = LevenbergMarquardtSolver::new(config);
        let mut workspace =
            LevenbergMarquardtWorkspace::new(&problem, &initial_params)?;
        solver.solve_problem(&problem, &mut workspace)?
    };
    let bundle_adjustment_1_time_ms =
        bundle_adjustment_1_start.elapsed().as_secs_f64() * 1000.0;

    // 11. Verify improvement
    if DEBUG {
        println!("\nStep 11: Analyzing results...");
        println!("  Status: {:?}", result.status);
        println!("  Iterations: {}", result.iterations);
        println!("  Function evaluations: {}", result.function_evaluations);
        println!("  Final cost: {:.6e}", result.cost);
    }

    let final_rms: f64 =
        (2.0_f64 * result.cost / result.residuals.len() as f64).sqrt();
    if DEBUG {
        println!("  Final RMS error: {:.4} pixels", final_rms);

        let cost_reduction =
            ((initial_cost - result.cost) / initial_cost) * 100.0;
        println!("  Cost reduction: {:.2}%", cost_reduction);
        println!(
            "  Bundle adjustment time: {:.2} ms",
            bundle_adjustment_1_time_ms
        );

        // 12. Extract optimized parameters
        println!("\nStep 12: Extracting optimized parameters...");
    }

    let optimized_params = &result.parameters;

    // Extract optimised camera poses.
    // Camera A is fixed at identity.
    let optimized_pose_a = pose_a.clone();

    // Camera B rotation and translation from TwoCameraBAProblem params.
    let rotation_matrix_b =
        problem.extract_camera_b_rotation_matrix(optimized_params);
    let translation_b = problem.extract_camera_b_translation(optimized_params);
    let optimized_pose_b = rotation_matrix_and_translation_to_camera_pose(
        &rotation_matrix_b,
        &translation_b,
    );

    let optimized_cameras = vec![optimized_pose_a, optimized_pose_b];

    // Extract optimized 3D points (start at param offset 5)
    let mut optimized_points: Vec<Point3<f64>> = Vec::new();
    let mut param_idx = 5;
    for _ in 0..triangulated_count {
        let point = Point3::new(
            optimized_params[param_idx],
            optimized_params[param_idx + 1],
            optimized_params[param_idx + 2],
        );
        optimized_points.push(point);
        param_idx += 3;
    }

    if DEBUG {
        println!("  Extracted {} optimized cameras", optimized_cameras.len());
        println!("  Extracted {} optimized 3D points", optimized_points.len());

        // 13-15. Generate OPTIMISED visualizations in parallel
        println!(
            "\nSteps 13-15: Generating optimised visualizations in parallel..."
        );
    }
    let viz_optimised_start = Instant::now();

    // Filter correspondences to match the valid triangulated points.
    let mut filtered_uv_a_optimised = Vec::new();
    let mut filtered_uv_b_optimised = Vec::new();
    for (i, &is_valid) in triangulated_valid.iter().enumerate() {
        if is_valid {
            filtered_uv_a_optimised.push(uv_coords_a[i]);
            filtered_uv_b_optimised.push(uv_coords_b[i]);
        }
    }

    let title_optimised =
        format!("{} - Bundle Adjustment (Optimised)", dataset_name);

    // Create stage-specific naming objects
    let naming_optimised_scene = base_naming
        .clone_with_stage(Stage::Optimised)
        .clone_with_visualization(VisualizationType::Scene3d);
    let naming_optimised_marker_2d = base_naming
        .clone_with_stage(Stage::Optimised)
        .clone_with_visualization(VisualizationType::MarkerReprojection2d);
    let naming_optimised_residuals = base_naming
        .clone_with_stage(Stage::Optimised)
        .clone_with_visualization(VisualizationType::ResidualsLinePlot);

    // Generate all optimised visualizations in parallel
    let final_stats = std::thread::scope(|s| {
        // Task 1: 3D scene views
        let handle_3d = s.spawn(|| {
            scene::visualize_sfm_scene_views(
                &optimized_cameras[0],
                &optimized_cameras[1],
                &optimized_points,
                &title_optimised,
                &naming_optimised_scene,
                views.clone(),
                &intrinsics_a,
                &intrinsics_b,
            )
        });

        // Task 2: 2D marker reprojection
        let handle_2d = s.spawn(|| {
            reprojection::visualize_marker_reprojections_2d_scatter(
                &filtered_uv_a_optimised,
                &filtered_uv_b_optimised,
                &optimized_points,
                &optimized_cameras[0],
                &optimized_cameras[1],
                &intrinsics_a,
                &intrinsics_b,
                &image_size_a,
                &image_size_b,
                &frame_pair,
                &title_optimised,
                &output_image_size,
                &naming_optimised_marker_2d,
            )
        });

        // Task 3: Residual errors computation and visualization
        let handle_residuals = s.spawn(|| {
            let mut final_residuals = vec![0.0; optimized_points.len()];
            compute_reprojection_residuals(
                &optimized_points,
                &filtered_uv_a_optimised,
                &filtered_uv_b_optimised,
                &optimized_cameras[0],
                &optimized_cameras[1],
                &intrinsics_a,
                &intrinsics_b,
                &image_size_a,
                &image_size_b,
                &mut final_residuals,
            )?;

            let stats = compute_residual_statistics(&final_residuals);

            residuals::visualize_residual_errors_line_plot(
                &final_residuals,
                &stats,
                &format!("{} - Residual Errors", title_optimised),
                &naming_optimised_residuals,
            )?;

            Ok::<_, anyhow::Error>(stats)
        });

        // Wait for all tasks to complete
        handle_3d.join().unwrap()?;
        handle_2d.join().unwrap()?;
        let stats = handle_residuals.join().unwrap()?;

        Ok::<_, anyhow::Error>(stats)
    })?;
    visualization_time_ms +=
        viz_optimised_start.elapsed().as_secs_f64() * 1000.0;

    if DEBUG {
        println!("  Optimised visualizations generated in parallel");
        println!(
            "  Optimised mean residual error: {:.4} pixels",
            final_stats.mean
        );
        println!(
            "  Optimised median residual error: {:.4} pixels",
            final_stats.median
        );
        println!(
            "  Optimised standard deviation: {:.4} pixels",
            final_stats.std_dev
        );
        println!(
            "  Optimised max residual error: {:.4} pixels",
            final_stats.max
        );
        println!(
            "  Optimised min residual error: {:.4} pixels",
            final_stats.min
        );

        // 16. Re-triangulate points with optimized camera poses
        println!(
            "\nStep 16: Re-triangulating points with optimized camera poses..."
        );
    }
    let triangulation_2_start = Instant::now();

    let mut retriangulated_points = vec![Point3::origin(); uv_coords_a.len()];
    let mut retriangulated_valid = vec![false; uv_coords_a.len()];

    // Create pose info structure with optimized poses for triangulation
    let optimized_pose_info = RelativePoseInfo {
        essential_matrix: pose_info.essential_matrix.clone(),
        residual_precision: pose_info.residual_precision,
        sampson_error: pose_info.sampson_error,
        symmetric_epipolar_error: pose_info.symmetric_epipolar_error,
        epipolar_error: pose_info.epipolar_error,
        relative_pose: optimized_cameras[1].clone(),
        triangulated_points: Vec::new(),
        triangulated_points_valid: Vec::new(),
    };

    let retriangulated_count = triangulate_points_from_relative_pose(
        &intrinsics_a,
        &intrinsics_b,
        &uv_coords_a,
        &uv_coords_b,
        &optimized_pose_info,
        &mut retriangulated_points,
        &mut retriangulated_valid,
    )?;
    let triangulation_2_time_ms =
        triangulation_2_start.elapsed().as_secs_f64() * 1000.0;

    let original_valid_count =
        triangulated_valid.iter().filter(|&&v| v).count();
    let new_valid_count = retriangulated_valid.iter().filter(|&&v| v).count();

    if DEBUG {
        println!(
            "  Re-triangulated {}/{} points (original: {}/{})",
            retriangulated_count,
            uv_coords_a.len(),
            original_valid_count,
            uv_coords_a.len()
        );
    }

    // Count how many points changed from invalid to valid
    let mut newly_valid_count = 0;
    for i in 0..triangulated_valid.len() {
        if !triangulated_valid[i] && retriangulated_valid[i] {
            newly_valid_count += 1;
        }
    }

    if newly_valid_count > 0 && DEBUG {
        println!(
            "  {} additional points became valid after re-triangulation",
            newly_valid_count
        );
    }

    let mut bundle_adjustment_2_time_ms = 0.0;

    // Run a second bundle adjustment if re-triangulation recovered more points.
    if new_valid_count > original_valid_count {
        if DEBUG {
            println!(
                "\nStep 17: Running second bundle adjustment with {} total valid points...",
                new_valid_count
            );
        }

        // Filter valid re-triangulated points for second BA
        let mut filtered_uv_a_second = Vec::new();
        let mut filtered_uv_b_second = Vec::new();
        let mut filtered_points_3d_second = Vec::new();
        for (i, &is_valid) in retriangulated_valid.iter().enumerate() {
            if is_valid {
                filtered_uv_a_second.push(uv_coords_a[i]);
                filtered_uv_b_second.push(uv_coords_b[i]);
                filtered_points_3d_second.push(retriangulated_points[i]);
            }
        }

        let observations_second = create_observations(
            &uv_coords_a,
            &uv_coords_b,
            &retriangulated_valid,
        );
        if DEBUG {
            println!(
                "  Total observations for second BA: {}",
                observations_second.len()
            );
        }

        let cam_b_rot_second =
            rotation_matrix_to_full_quaternion(optimized_cameras[1].rotation());
        let cam_b_trans_second = [
            optimized_cameras[1].translation().x,
            optimized_cameras[1].translation().y,
            optimized_cameras[1].translation().z,
        ];

        let points_second: Vec<[f64; 3]> = filtered_points_3d_second
            .iter()
            .map(|p| [p.x, p.y, p.z])
            .collect();

        let problem_second = TwoCameraBAProblem::new(
            observations_second,
            intrinsics_a.focal_length_x,
            intrinsics_a.focal_length_y,
            (
                intrinsics_a.principal_point.x.value(),
                intrinsics_a.principal_point.y.value(),
            ),
            cam_b_rot_second,
            cam_b_trans_second,
            &points_second,
        );

        // Compute cost before second BA
        let params_before_second = problem_second.pack_parameters();
        let mut residuals_before_second =
            vec![0.0; OptimisationProblem::residual_count(&problem_second)];
        problem_second
            .residuals(&params_before_second, &mut residuals_before_second)?;
        let cost_before_second = 0.5
            * residuals_before_second
                .iter()
                .map(|r| r.powi(2))
                .sum::<f64>();

        if DEBUG {
            println!(
                "  Second BA problem size: {} parameters, {} residuals",
                OptimisationProblem::parameter_count(&problem_second),
                OptimisationProblem::residual_count(&problem_second)
            );

            let rms_before_second = (2.0 * cost_before_second
                / residuals_before_second.len() as f64)
                .sqrt();
            println!("  Cost before second BA: {:.6e}", cost_before_second);
            println!("  RMS before second BA: {:.4} pixels", rms_before_second);
        }

        // Run second bundle adjustment (always dense LM)
        let bundle_adjustment_2_start = Instant::now();
        let result_second = {
            let mut config_second = LevenbergMarquardtConfig::default();
            config_second.max_iterations = 500;
            config_second.max_function_evaluations = 20000;

            let solver_second = LevenbergMarquardtSolver::new(config_second);
            let mut workspace_second = LevenbergMarquardtWorkspace::new(
                &problem_second,
                &params_before_second,
            )?;
            solver_second
                .solve_problem(&problem_second, &mut workspace_second)?
        };
        bundle_adjustment_2_time_ms =
            bundle_adjustment_2_start.elapsed().as_secs_f64() * 1000.0;

        if DEBUG {
            println!("  Second BA status: {:?}", result_second.status);
            println!("  Second BA iterations: {}", result_second.iterations);
            println!(
                "  Second BA function evaluations: {}",
                result_second.function_evaluations
            );
            println!(
                "  Final cost after second BA: {:.6e}",
                result_second.cost
            );

            let final_rms_second: f64 = (2.0_f64 * result_second.cost
                / result_second.residuals.len() as f64)
                .sqrt();
            println!(
                "  Final RMS after second BA: {:.4} pixels",
                final_rms_second
            );

            let cost_reduction_second = ((cost_before_second
                - result_second.cost)
                / cost_before_second)
                * 100.0;
            println!(
                "  Second BA cost reduction: {:.2}%",
                cost_reduction_second
            );
            println!("  Second BA time: {:.2} ms", bundle_adjustment_2_time_ms);

            // Extract final optimized parameters
            println!("\n  Extracting final optimized parameters...");
        }

        let optimized_params_final = &result_second.parameters;

        // Extract final optimized camera poses.
        // Camera A is fixed at identity.
        let final_pose_a = optimized_cameras[0].clone();

        // Camera B from TwoCameraBAProblem params.
        let rotation_matrix_b_final = problem_second
            .extract_camera_b_rotation_matrix(optimized_params_final);
        let translation_b_final =
            problem_second.extract_camera_b_translation(optimized_params_final);
        let final_pose_b = rotation_matrix_and_translation_to_camera_pose(
            &rotation_matrix_b_final,
            &translation_b_final,
        );

        let final_cameras = vec![final_pose_a, final_pose_b];

        // Extract final optimized 3D points (start at param offset 5)
        let mut final_points: Vec<Point3<f64>> = Vec::new();
        let mut param_idx = 5;
        for _ in 0..new_valid_count {
            let point = Point3::new(
                optimized_params_final[param_idx],
                optimized_params_final[param_idx + 1],
                optimized_params_final[param_idx + 2],
            );
            final_points.push(point);
            param_idx += 3;
        }

        if DEBUG {
            println!(
                "  Extracted {} final optimized cameras",
                final_cameras.len()
            );
            println!(
                "  Extracted {} final optimized 3D points",
                final_points.len()
            );

            // Generate FINAL 3D scene visualizations
            println!("\n  Generating final 3D scene visualizations...");
        }
        let viz_final_start = Instant::now();

        let title_final =
            format!("{} - Bundle Adjustment (Final)", dataset_name);

        // Create stage-specific naming objects
        let naming_final_scene = base_naming
            .clone_with_stage(Stage::Final)
            .clone_with_visualization(VisualizationType::Scene3d);
        let naming_final_marker_2d = base_naming
            .clone_with_stage(Stage::Final)
            .clone_with_visualization(VisualizationType::MarkerReprojection2d);
        let naming_final_residuals = base_naming
            .clone_with_stage(Stage::Final)
            .clone_with_visualization(VisualizationType::ResidualsLinePlot);

        scene::visualize_sfm_scene_views(
            &final_cameras[0],
            &final_cameras[1],
            &final_points,
            &title_final,
            &naming_final_scene,
            views,
            &intrinsics_a,
            &intrinsics_b,
        )?;

        if DEBUG {
            println!("  Final 3D scene visualizations generated");

            // Generate FINAL 2D marker reprojection visualization
            println!(
                "\n  Generating final 2D marker reprojection visualization..."
            );
        }

        reprojection::visualize_marker_reprojections_2d_scatter(
            &filtered_uv_a_second,
            &filtered_uv_b_second,
            &final_points,
            &final_cameras[0],
            &final_cameras[1],
            &intrinsics_a,
            &intrinsics_b,
            &image_size_a,
            &image_size_b,
            &frame_pair,
            &title_final,
            &output_image_size,
            &naming_final_marker_2d,
        )?;

        if DEBUG {
            println!("  Final 2D marker reprojection visualization generated");

            // Compute and visualize FINAL residual errors
            println!("\n  Computing and visualizing final residual errors...");
        }

        let mut final_residuals_second = vec![0.0; final_points.len()];
        compute_reprojection_residuals(
            &final_points,
            &filtered_uv_a_second,
            &filtered_uv_b_second,
            &final_cameras[0],
            &final_cameras[1],
            &intrinsics_a,
            &intrinsics_b,
            &image_size_a,
            &image_size_b,
            &mut final_residuals_second,
        )?;

        let final_stats_second =
            compute_residual_statistics(&final_residuals_second);

        residuals::visualize_residual_errors_line_plot(
            &final_residuals_second,
            &final_stats_second,
            &format!("{} - Residual Errors", title_final),
            &naming_final_residuals,
        )?;
        visualization_time_ms +=
            viz_final_start.elapsed().as_secs_f64() * 1000.0;

        if DEBUG {
            println!(
                "  Final mean residual error: {:.4} pixels",
                final_stats_second.mean
            );
            println!(
                "  Final median residual error: {:.4} pixels",
                final_stats_second.median
            );
            println!(
                "  Final standard deviation: {:.4} pixels",
                final_stats_second.std_dev
            );
            println!(
                "  Final max residual error: {:.4} pixels",
                final_stats_second.max
            );
            println!(
                "  Final min residual error: {:.4} pixels",
                final_stats_second.min
            );
        }

        assert!(
            result_second.status.is_success(),
            "Second bundle adjustment should converge successfully"
        );
        assert!(
            result_second.cost <= cost_before_second,
            "Second bundle adjustment should reduce cost. Before: {:.6e}, After: {:.6e}",
            cost_before_second,
            result_second.cost
        );
    } else {
        if DEBUG {
            println!("\n  No additional points became valid - skipping second bundle adjustment");
        }
    }

    assert!(
        result.status.is_success(),
        "Dense LM solver should converge successfully. Status: {:?}",
        result.status
    );

    if DEBUG {
        println!("\n=== Bundle Adjustment Test Passed ===\n");
    }

    Ok(())
}
