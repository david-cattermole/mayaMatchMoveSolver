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

//! Utility functions for bundle adjustment operations

use std::collections::BTreeMap;

use anyhow::{bail, Result};
use mmcore::rand_prng_pcg::PCG;
use mmio::uvtrack_reader::{FrameNumber, MarkersData};
use nalgebra::Point3;

use mmoptimise::solver::common::OptimisationProblem;
use mmoptimise::solver::levenberg_marquardt::{
    LevenbergMarquardtConfig, LevenbergMarquardtSolver,
    LevenbergMarquardtWorkspace,
};
use mmoptimise::sparse::{
    SparseLevenbergMarquardtConfig, SparseLevenbergMarquardtSolver,
    SparseLevenbergMarquardtWorkspace,
};

use crate::bundle_adjust::{
    quaternion_from_vector_f64, quaternion_multiply,
    rotation_matrix_to_full_quaternion,
};
use crate::datatype::conversions::convert_uv_to_ndc_point;
use crate::datatype::{
    BundlePositions, CameraIntrinsics, CameraPoses, ImageSize, UnitValue,
    UvValue,
};
use crate::sfm_camera::config::BundleAdjustmentSolverType;
use crate::sfm_camera::validation::{
    validate_and_filter_bundles, BundleValidationConfig,
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

pub fn compute_diagonal_field_of_view_size_radian(
    camera_intrinsics: &CameraIntrinsics,
) -> f64 {
    let h_fov = camera_intrinsics.horizontal_fov_radians();
    let v_fov = camera_intrinsics.vertical_fov_radians();
    (h_fov + v_fov) / 2.0
}

/// Compute scene scale as median bundle distance from centroid.
///
/// Returns 1.0 if bundles are empty or degenerate.
pub fn compute_scene_scale(bundle_positions: &BundlePositions) -> f64 {
    if bundle_positions.is_empty() {
        return 1.0;
    }

    // Compute centroid.
    let mut sum = nalgebra::Vector3::<f64>::zeros();
    for point in bundle_positions.values() {
        sum += point.coords;
    }
    let centroid = Point3::from(sum / bundle_positions.len() as f64);

    // TODO: Avoid allocating a new vector for distances.
    // Compute median distance from centroid.
    let mut distances: Vec<f64> = bundle_positions
        .values()
        .map(|point| (point - centroid).norm())
        .collect();

    if distances.is_empty() {
        return 1.0;
    }

    distances
        .sort_by(|a, b| a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal));
    let median_idx = distances.len() / 2;

    let median = if distances.len().is_multiple_of(2) {
        (distances[median_idx - 1] + distances[median_idx]) / 2.0
    } else {
        distances[median_idx]
    };

    if median < 1e-10 {
        1.0
    } else {
        median
    }
}

/// Collect marker observations as NDC coordinate tuples `(camera_idx, point_idx, x, y)`.
pub fn collect_observations_ndc(
    markers: &MarkersData,
    marker_list: &[usize],
    marker_to_point_idx: &BTreeMap<usize, usize>,
    frame_to_camera_idx: &BTreeMap<FrameNumber, usize>,
) -> Vec<(usize, usize, f64, f64)> {
    let mut observations = Vec::new();
    for &marker_idx in marker_list {
        assert!(marker_idx < markers.frame_data.len());

        let frame_data = &markers.frame_data[marker_idx];
        let point_idx = marker_to_point_idx[&marker_idx];

        for (frame, camera_idx) in frame_to_camera_idx {
            if let Some(pos) =
                frame_data.frames.iter().position(|&f| f == *frame)
            {
                let u = frame_data.u_coords[pos];
                let v = frame_data.v_coords[pos];
                let uv_point = UvValue::point2(u, v);

                // Convert UV to NDC.
                let ndc_point = convert_uv_to_ndc_point(uv_point);

                observations.push((
                    *camera_idx,
                    point_idx,
                    ndc_point.x.value(),
                    ndc_point.y.value(),
                ));
            }
        }
    }
    observations
}

/// Create a dense LM solver config with the given iteration limit.
pub fn create_basic_dense_solver_config(
    max_iterations: usize,
) -> LevenbergMarquardtConfig {
    LevenbergMarquardtConfig {
        max_iterations,
        max_function_evaluations: max_iterations * 20,
        ..Default::default()
    }
}

/// Check that optimization result has finite cost and parameters.
pub fn validate_ba_result(
    result: &mmoptimise::solver::common::OptimisationResult,
    context: &str,
) -> Result<()> {
    // Check cost is finite
    if !result.cost.is_finite() {
        bail!("{} failed: cost is NaN/Inf ({})", context, result.cost);
    }

    // Validate all parameters are finite
    for (i, &param) in result.parameters.iter().enumerate() {
        if !param.is_finite() {
            bail!(
                "{} failed: parameter {} is NaN/Inf (value: {})",
                context,
                i,
                param
            );
        }
    }

    Ok(())
}

/// Compute rotation and translation noise scales from scene properties.
///
/// Returns `(rotation_noise_scale, translation_noise_scale)`.
pub fn compute_noise_scales(
    camera_intrinsics: &CameraIntrinsics,
    bundle_positions: &BundlePositions,
    rotation_noise_scale_factor: f64,
    translation_noise_scale_factor: f64,
) -> (f64, f64) {
    // Rotation noise: factor * angular field of view.
    let fov_diagonal =
        compute_diagonal_field_of_view_size_radian(camera_intrinsics);
    let rotation_scale = rotation_noise_scale_factor * fov_diagonal;

    // Translation noise: factor * median scene distance.
    let scene_scale = compute_scene_scale(bundle_positions);
    let translation_scale = scene_scale * translation_noise_scale_factor;

    (rotation_scale, translation_scale)
}

/// Convert camera poses to (quaternion, translation) format with optional noise.
pub fn convert_and_noise_camera_poses(
    camera_poses: &CameraPoses,
    frame_list: &[FrameNumber],
    locked_camera_idx: Option<usize>,
    rotation_noise_scale: f64,
    translation_noise_scale: f64,
    rng: &mut PCG,
    debug_prefix: &str,
) -> Vec<([f64; 4], [f64; 3])> {
    let mut initial_cameras = Vec::new();

    for (i, &frame) in frame_list.iter().enumerate() {
        let pose = &camera_poses[&frame];
        let rotation_matrix = *pose.rotation();
        let mut quaternion =
            rotation_matrix_to_full_quaternion(&rotation_matrix);

        let translation_vector = pose.translation();
        let mut translation = [
            translation_vector.x,
            translation_vector.y,
            translation_vector.z,
        ];

        // Apply noise only if unlocked (not the locked camera).
        let is_locked = locked_camera_idx == Some(i);
        let is_unlocked = !is_locked;

        if rotation_noise_scale > 0.0 && is_unlocked {
            // Rotation noise via quaternion perturbation.
            let perturbation = [
                (rng.next_f64() * 2.0 - 1.0) * rotation_noise_scale,
                (rng.next_f64() * 2.0 - 1.0) * rotation_noise_scale,
                (rng.next_f64() * 2.0 - 1.0) * rotation_noise_scale,
            ];
            let perturbation_quat = quaternion_from_vector_f64(&perturbation);
            quaternion = quaternion_multiply(&perturbation_quat, &quaternion);

            // Normalize quaternion.
            let norm = (quaternion[0] * quaternion[0]
                + quaternion[1] * quaternion[1]
                + quaternion[2] * quaternion[2]
                + quaternion[3] * quaternion[3])
                .sqrt();
            for j in 0..4 {
                quaternion[j] /= norm;
            }
        }

        if translation_noise_scale > 0.0 && is_unlocked {
            // Translation noise.
            for j in 0..3 {
                translation[j] +=
                    (rng.next_f64() * 2.0 - 1.0) * translation_noise_scale;
            }
        }

        mm_debug_eprintln!(
            "  {} Initial camera {} (frame {}): translation = ({:.6}, {:.6}, {:.6}), unlocked = {}",
            debug_prefix, i, frame, translation[0], translation[1], translation[2], is_unlocked
        );

        initial_cameras.push((quaternion, translation));
    }

    initial_cameras
}

/// Convert bundle positions to array format with optional noise.
pub fn convert_and_noise_bundle_positions(
    bundle_positions: &BundlePositions,
    marker_list: &[usize],
    translation_noise_scale: f64,
    rng: &mut PCG,
    debug_prefix: &str,
) -> Vec<[f64; 3]> {
    let mut initial_points = Vec::new();

    for (i, &marker_idx) in marker_list.iter().enumerate() {
        let point = bundle_positions[&marker_idx];
        let mut noisy_point = [point.x, point.y, point.z];

        if translation_noise_scale > 0.0 {
            for j in 0..3 {
                noisy_point[j] +=
                    (rng.next_f64() * 2.0 - 1.0) * translation_noise_scale;
            }
        }

        mm_debug_eprintln!(
            "  {} Initial bundle {}: point = ({:.6}, {:.6}, {:.6}) -> ({:.6}, {:.6}, {:.6})",
            debug_prefix, i, point[0], point[1], point[2],
            noisy_point[0], noisy_point[1], noisy_point[2],
        );

        initial_points.push(noisy_point);
    }

    initial_points
}

/// Run pre-BA bundle validation and update marker list.
///
/// Returns true if validation was performed, false if skipped.
pub fn run_pre_ba_validation(
    bundle_positions: &mut BundlePositions,
    marker_list: &mut Vec<usize>,
    markers: &MarkersData,
    camera_poses: &CameraPoses,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
    validation_config: Option<&BundleValidationConfig>,
    debug_prefix: &str,
) -> bool {
    let Some(validation_config) = validation_config else {
        return false;
    };

    mm_debug_eprintln!(
        "  {} Running pre-BA validation ({} bundles)...",
        debug_prefix,
        bundle_positions.len()
    );

    let result = validate_and_filter_bundles(
        bundle_positions,
        markers,
        marker_list,
        camera_poses,
        camera_intrinsics,
        image_size,
        validation_config,
    );

    if DEBUG && result.total_removed() > 0 {
        eprintln!(
            "  {} Pre-BA validation: {} -> {} bundles ({:.1}% retained)",
            debug_prefix,
            result.initial_bundle_count,
            result.final_bundle_count,
            result.retention_percentage()
        );
    }

    // Update marker_list after filtering
    *marker_list = bundle_positions.keys().copied().collect();
    marker_list.sort_unstable();

    true
}

/// Run post-BA bundle validation.
pub fn run_post_ba_validation(
    bundle_positions: &mut BundlePositions,
    markers: &MarkersData,
    camera_poses: &CameraPoses,
    camera_intrinsics: &CameraIntrinsics,
    image_size: &ImageSize<f64>,
    validation_config: Option<&BundleValidationConfig>,
    debug_prefix: &str,
) {
    let Some(validation_config) = validation_config else {
        return;
    };

    mm_debug_eprintln!(
        "  {} Running post-BA validation ({} bundles)...",
        debug_prefix,
        bundle_positions.len()
    );

    let marker_list: Vec<usize> = bundle_positions.keys().copied().collect();
    let result = validate_and_filter_bundles(
        bundle_positions,
        markers,
        &marker_list,
        camera_poses,
        camera_intrinsics,
        image_size,
        validation_config,
    );

    if DEBUG && result.total_removed() > 0 {
        eprintln!(
            "  {} Post-BA validation: {} -> {} bundles ({:.1}% retained)",
            debug_prefix,
            result.initial_bundle_count,
            result.final_bundle_count,
            result.retention_percentage()
        );
    }
}

/// Create sorted frame/marker lists and their index mappings.
///
/// Returns `(frame_list, frame_to_camera_idx, marker_list, marker_to_point_idx)`.
pub fn create_sorted_indices(
    camera_poses: &CameraPoses,
    bundle_positions: &BundlePositions,
    // TODO: Convert this return into multiple input arguments, or
    // into a struct that is returned.
) -> (
    Vec<FrameNumber>,
    BTreeMap<FrameNumber, usize>,
    Vec<usize>,
    BTreeMap<usize, usize>,
) {
    // Create sorted frame list and mapping.
    let mut frame_list: Vec<FrameNumber> =
        camera_poses.keys().copied().collect();
    frame_list.sort_unstable();
    let frame_to_camera_idx: BTreeMap<FrameNumber, usize> = frame_list
        .iter()
        .enumerate()
        .map(|(idx, &frame)| (frame, idx))
        .collect();

    // Create sorted marker list and mapping.
    let mut marker_list: Vec<usize> =
        bundle_positions.keys().copied().collect();
    marker_list.sort_unstable();
    let marker_to_point_idx: BTreeMap<usize, usize> = marker_list
        .iter()
        .enumerate()
        .map(|(idx, &marker)| (marker, idx))
        .collect();

    (
        frame_list,
        frame_to_camera_idx,
        marker_list,
        marker_to_point_idx,
    )
}

/// Run bundle adjustment using the chosen solver type.
pub fn execute_bundle_adjustment_solver<P>(
    problem: &P,
    initial_params: &[f64],
    solver_config: &LevenbergMarquardtConfig,
    solver_type: &BundleAdjustmentSolverType,
    debug_prefix: &str,
) -> Result<mmoptimise::solver::common::OptimisationResult>
where
    P: OptimisationProblem + mmoptimise::sparse::SparseOptimisationProblem,
{
    match solver_type {
        BundleAdjustmentSolverType::DenseLM => {
            mm_debug_eprintln!(
                "  {} Using dense Levenberg-Marquardt solver",
                debug_prefix
            );
            let solver = LevenbergMarquardtSolver::new(solver_config.clone());
            let mut workspace =
                LevenbergMarquardtWorkspace::new(problem, initial_params)?;
            solver.solve_problem(problem, &mut workspace)
        }
        BundleAdjustmentSolverType::SparseLevenbergMarquardt => {
            mm_debug_eprintln!(
                "  {} Using sparse Levenberg-Marquardt solver (direct CHOLMOD)",
                debug_prefix
            );

            let sparse_lm_config = SparseLevenbergMarquardtConfig {
                max_iterations: solver_config.max_iterations,
                max_function_evaluations: solver_config
                    .max_function_evaluations,
                function_tolerance: solver_config.function_tolerance,
                parameter_tolerance: solver_config.parameter_tolerance,
                gradient_tolerance: solver_config.gradient_tolerance,
                ..Default::default()
            };

            let solver = SparseLevenbergMarquardtSolver::new(sparse_lm_config);
            let mut workspace = SparseLevenbergMarquardtWorkspace::new(
                problem,
                initial_params,
            )?;
            solver.solve_problem(problem, &mut workspace)
        }
    }
}
