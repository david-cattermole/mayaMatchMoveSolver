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

use std::collections::BTreeMap;
use std::time::Instant;

use anyhow::{bail, Result};
use mmcore::rand_prng_pcg::PCG;
use mmio::uvtrack_reader::{FrameNumber, MarkersData};
use nalgebra::Point3;

use mmoptimise::solver::common::OptimisationProblem;
use mmoptimise::solver::levenberg_marquardt::{
    LevenbergMarquardtSolver, LevenbergMarquardtWorkspace,
};

use crate::bundle_adjust::{
    rotation_matrix_and_translation_to_camera_pose,
    rotation_matrix_to_full_quaternion, GeneralBundleAdjustmentProblem,
    TwoCameraBAProblem,
};
use crate::datatype::{
    BundlePositions, CameraIntrinsics, CameraPoses, ImageSize, UnitValue,
};
use crate::sfm_camera::bundle_adjustment_utils::{
    collect_observations_ndc, compute_noise_scales,
    convert_and_noise_bundle_positions, convert_and_noise_camera_poses,
    create_basic_dense_solver_config, create_sorted_indices,
    execute_bundle_adjustment_solver, run_post_ba_validation,
    run_pre_ba_validation, validate_ba_result,
};
use crate::sfm_camera::config::CameraSolveConfig;
use crate::sfm_camera::validation::{
    detect_camera_position_collapse, BundleValidationConfig,
};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Run bundle adjustment for 2-camera SfM initialization.
///
/// Camera A is fixed at origin, camera B is optimized with a unit-length
/// translation using spherical reparameterization.
pub fn run_two_camera_bundle_adjustment(
    markers: &MarkersData,
    camera_poses: &mut CameraPoses,
    bundle_positions: &mut BundlePositions,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
    max_iterations: usize,
    pre_ba_validation: Option<&BundleValidationConfig>,
    post_ba_validation: Option<&BundleValidationConfig>,
) -> Result<()> {
    if camera_poses.len() != 2 {
        bail!(
            "run_two_camera_bundle_adjustment requires exactly 2 cameras, got {}",
            camera_poses.len()
        );
    }

    if camera_poses.is_empty() || bundle_positions.is_empty() {
        return Ok(());
    }

    mm_eprintln_debug!(
        "  [2-Camera BA] Starting specialized bundle adjustment"
    );
    mm_eprintln_debug!(
        "    Cameras: {}, Points: {}",
        camera_poses.len(),
        bundle_positions.len()
    );

    // Sort frames; A is earliest, B is second.
    let mut frame_list: Vec<FrameNumber> =
        camera_poses.keys().copied().collect();
    frame_list.sort_unstable();
    let frame_a = frame_list[0];
    let frame_b = frame_list[1];

    mm_eprintln_debug!("    Frame A (fixed): {}", frame_a);
    mm_eprintln_debug!("    Frame B (optimized): {}", frame_b);

    let mut marker_list: Vec<usize> =
        bundle_positions.keys().copied().collect();
    marker_list.sort_unstable();

    // Pre-BA validation (optional bundle filtering).
    run_pre_ba_validation(
        bundle_positions,
        &mut marker_list,
        markers,
        camera_poses,
        camera_intrinsics,
        image_size,
        pre_ba_validation,
        "[2-Camera BA]",
    );

    let marker_to_point_idx: BTreeMap<usize, usize> = marker_list
        .iter()
        .enumerate()
        .map(|(idx, &marker)| (marker, idx))
        .collect();

    // Frame A maps to camera index 0, frame B to index 1.
    let frame_to_camera_idx: BTreeMap<FrameNumber, usize> =
        [(frame_a, 0), (frame_b, 1)].iter().copied().collect();

    // Collect observations in NDC coordinates.
    let observations = collect_observations_ndc(
        markers,
        &marker_list,
        &marker_to_point_idx,
        &frame_to_camera_idx,
    );

    if observations.is_empty() {
        return Ok(());
    }

    // Extract focal lengths and principal point.
    let focal_length_x = camera_intrinsics.focal_length_x;
    let focal_length_y = camera_intrinsics.focal_length_y;
    let principal_point = (
        camera_intrinsics.principal_point.x.value(),
        camera_intrinsics.principal_point.y.value(),
    );

    // Get camera B initial pose.
    let pose_b = &camera_poses[&frame_b];
    let rotation_matrix_b = *pose_b.rotation();
    let camera_b_quaternion =
        rotation_matrix_to_full_quaternion(&rotation_matrix_b);
    let translation_b = pose_b.translation();
    let camera_b_translation =
        [translation_b.x, translation_b.y, translation_b.z];

    if DEBUG {
        let norm = (camera_b_translation[0] * camera_b_translation[0]
            + camera_b_translation[1] * camera_b_translation[1]
            + camera_b_translation[2] * camera_b_translation[2])
            .sqrt();
        mm_eprintln_debug!(
            "    Initial camera B translation: [{:.4}, {:.4}, {:.4}] (norm: {:.4})",
            camera_b_translation[0],
            camera_b_translation[1],
            camera_b_translation[2],
            norm
        );
    }

    // Convert bundle positions to array format.
    let initial_points: Vec<[f64; 3]> = marker_list
        .iter()
        .map(|&marker_idx| {
            let point = bundle_positions[&marker_idx];
            [point.x, point.y, point.z]
        })
        .collect();

    // Create the 2-camera bundle adjustment problem.
    let problem = TwoCameraBAProblem::new(
        observations,
        focal_length_x,
        focal_length_y,
        principal_point,
        camera_b_quaternion,
        camera_b_translation,
        &initial_points,
    );

    let num_parameters = problem.parameter_count();
    let num_residuals = problem.residual_count();
    if num_residuals < num_parameters {
        mm_eprintln_debug!(
            "  [2-Camera BA] Skipping: insufficient observations ({} residuals < {} parameters)",
            num_residuals, num_parameters
        );
        return Ok(());
    }

    mm_eprintln_debug!(
        "  [2-Camera BA] Problem: {} parameters, {} residuals",
        num_parameters,
        num_residuals
    );

    let problem_start = Instant::now();

    let initial_params = problem.pack_parameters();
    let solver_config = create_basic_dense_solver_config(max_iterations);

    mm_eprintln_debug!(
        "  [2-Camera BA] Using dense Levenberg-Marquardt solver"
    );

    let solver = LevenbergMarquardtSolver::new(solver_config);
    let mut workspace =
        LevenbergMarquardtWorkspace::new(&problem, &initial_params)?;
    let result = solver.solve_problem(&problem, &mut workspace)?;

    mm_eprintln_debug!(
        "  [2-Camera BA] Problem finished in {:.6}s.",
        problem_start.elapsed().as_secs_f64()
    );

    // Validate result.
    validate_ba_result(&result, "Two-camera bundle adjustment")?;

    // Extract optimized camera B pose.
    let optimized_rotation =
        problem.extract_camera_b_rotation_matrix(&result.parameters);
    let optimized_translation =
        problem.extract_camera_b_translation(&result.parameters);

    if DEBUG {
        let norm = (optimized_translation[0] * optimized_translation[0]
            + optimized_translation[1] * optimized_translation[1]
            + optimized_translation[2] * optimized_translation[2])
            .sqrt();
        mm_eprintln_debug!(
            "  [2-Camera BA] Optimized camera B translation: [{:.4}, {:.4}, {:.4}] (norm: {:.4})",
            optimized_translation[0],
            optimized_translation[1],
            optimized_translation[2],
            norm
        );
    }

    let optimized_pose_b = rotation_matrix_and_translation_to_camera_pose(
        &optimized_rotation,
        &optimized_translation,
    );
    camera_poses.insert(frame_b, optimized_pose_b);

    // Extract optimized bundle positions.
    for (i, &marker_idx) in marker_list.iter().enumerate() {
        let offset = 5 + i * 3; // 5 camera B params, then 3 per point.
        let optimized_point = Point3::new(
            result.parameters[offset],
            result.parameters[offset + 1],
            result.parameters[offset + 2],
        );
        bundle_positions.insert(marker_idx, optimized_point);
    }

    // Post-BA validation (optional bundle filtering).
    run_post_ba_validation(
        bundle_positions,
        markers,
        camera_poses,
        camera_intrinsics,
        image_size,
        post_ba_validation,
        "[2-Camera BA]",
    );

    // Detect camera position collapse.
    //
    // Even though 2-camera BA uses spherical parameterization, we
    // still check for degenerate solutions where cameras have
    // converged.
    detect_camera_position_collapse(camera_poses)?;

    // NOTE: Do NOT call normalize_reconstruction here.
    //
    // The 2-camera BA uses spherical parameterization to enforce unit
    // baseline. If we normalize based on median bundle distance (which
    // could be very large if scene depth >> baseline), we would collapse
    // the baseline to near-zero, causing scale collapse.
    //
    // The unit baseline constraint is sufficient gauge fixing for the
    // 2-camera case.

    mm_eprintln_debug!(
        "  [2-Camera BA] Complete: {} iterations, final cost: {:.6}",
        result.iterations,
        result.cost
    );

    Ok(())
}

/// Run general bundle adjustment to refine all camera poses and bundle positions.
pub fn run_general_bundle_adjustment(
    markers: &MarkersData,
    camera_poses: &mut CameraPoses,
    bundle_positions: &mut BundlePositions,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
    max_iterations: usize,
    config: &CameraSolveConfig,
    pre_ba_validation: Option<&BundleValidationConfig>,
    post_ba_validation: Option<&BundleValidationConfig>,
) -> Result<()> {
    if camera_poses.is_empty() || bundle_positions.is_empty() {
        return Ok(());
    }

    mm_eprintln_debug!(
        "\n  [General BA] Starting final general bundle adjustment"
    );
    mm_eprintln_debug!(
        "    Cameras: {}, Points: {}",
        camera_poses.len(),
        bundle_positions.len()
    );

    // Create sorted indices for frames and markers.
    let (
        frame_list,
        frame_to_camera_idx,
        mut marker_list,
        mut marker_to_point_idx,
    ) = create_sorted_indices(camera_poses, bundle_positions);

    // Pre-BA validation (optional bundle filtering).
    let pre_ba_performed = run_pre_ba_validation(
        bundle_positions,
        &mut marker_list,
        markers,
        camera_poses,
        camera_intrinsics,
        image_size,
        pre_ba_validation,
        "[General BA]",
    );

    // Recreate marker_to_point_idx if validation updated marker_list.
    if pre_ba_performed {
        marker_to_point_idx = marker_list
            .iter()
            .enumerate()
            .map(|(idx, &marker)| (marker, idx))
            .collect();
    }

    // Collect observations in NDC coordinates.
    let observations = collect_observations_ndc(
        markers,
        &marker_list,
        &marker_to_point_idx,
        &frame_to_camera_idx,
    );

    if observations.is_empty() {
        return Ok(());
    }

    // Extract focal lengths and principal point.
    let focal_length_x = camera_intrinsics.focal_length_x;
    let focal_length_y = camera_intrinsics.focal_length_y;
    let principal_point = (
        camera_intrinsics.principal_point.x.value(),
        camera_intrinsics.principal_point.y.value(),
    );

    // NOTE: Adding noise to the input parameters can allow an
    // existing solve that is close to perfect to force a
    // re-adjustment.
    //
    // The seed is fixed because we want the solver to be
    // deterministic.
    let mut rng = PCG::new_from_seed(42);

    // Compute noise scales.
    let (rotation_noise_scale, translation_noise_scale) = if config.enable_noise
    {
        compute_noise_scales(
            camera_intrinsics,
            bundle_positions,
            config.rotation_noise_scale_factor,
            config.translation_noise_scale_factor,
        )
    } else {
        (0.0, 0.0)
    };

    // Convert camera poses to (quaternion, translation) format with noise.
    let initial_cameras = convert_and_noise_camera_poses(
        camera_poses,
        &frame_list,
        None, // All cameras unlocked.
        rotation_noise_scale,
        translation_noise_scale,
        &mut rng,
        "[General BA]",
    );

    // Convert bundle positions to array format with noise.
    let initial_points = convert_and_noise_bundle_positions(
        bundle_positions,
        &marker_list,
        translation_noise_scale,
        &mut rng,
        "[General BA]",
    );

    // Create the general bundle adjustment problem (all cameras and points unlocked).
    let problem = GeneralBundleAdjustmentProblem::new(
        observations,
        focal_length_x,
        focal_length_y,
        principal_point,
        &initial_cameras,
        &initial_points,
    );

    let num_parameters = problem.parameter_count();
    let num_residuals = problem.residual_count();
    if num_residuals < num_parameters {
        mm_eprintln_debug!(
            "  [General BA] Skipping: insufficient observations ({} residuals < {} parameters)",
            num_residuals, num_parameters
        );
        return Ok(());
    }
    mm_eprintln_debug!(
        "  [General BA] Problem: {} parameters, {} residuals",
        num_parameters,
        num_residuals
    );

    let problem_start = Instant::now();

    let initial_params = problem.pack_parameters();
    let solver_config = create_basic_dense_solver_config(max_iterations);

    // Run optimization.
    let result = execute_bundle_adjustment_solver(
        &problem,
        &initial_params,
        &solver_config,
        &config.bundle_solver_type,
        "[General BA]",
    )?;

    mm_eprintln_debug!(
        "  [General BA] Problem finished in {:.6}s.",
        problem_start.elapsed().as_secs_f64()
    );

    // Validate result quality.
    validate_ba_result(&result, "General bundle adjustment")?;

    // Extract optimized camera poses.
    for (i, &frame) in frame_list.iter().enumerate() {
        let rotation_matrix =
            problem.extract_camera_rotation_matrix(&result.parameters, i);

        let param_offset = i * 6;
        let translation = [
            result.parameters[param_offset + 3],
            result.parameters[param_offset + 4],
            result.parameters[param_offset + 5],
        ];

        let optimized_pose = rotation_matrix_and_translation_to_camera_pose(
            &rotation_matrix,
            &translation,
        );
        camera_poses.insert(frame, optimized_pose);
    }

    // Extract optimized bundle positions.
    let point_offset = frame_list.len() * 6;
    for (i, &marker_idx) in marker_list.iter().enumerate() {
        let param_idx = point_offset + i * 3;
        let optimized_point = Point3::new(
            result.parameters[param_idx],
            result.parameters[param_idx + 1],
            result.parameters[param_idx + 2],
        );
        bundle_positions.insert(marker_idx, optimized_point);
    }

    // Post-BA validation (optional bundle filtering).
    run_post_ba_validation(
        bundle_positions,
        markers,
        camera_poses,
        camera_intrinsics,
        image_size,
        post_ba_validation,
        "[General BA]",
    );

    mm_eprintln_debug!(
        "  [General BA] Complete: {} iterations, final cost: {:.6}",
        result.iterations,
        result.cost
    );
    mm_eprintln_debug!("  [General BA] Status: {:?}", result.status);

    Ok(())
}
