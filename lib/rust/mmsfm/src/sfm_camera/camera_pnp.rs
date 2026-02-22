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

//! Camera pose estimation using Perspective-n-Point (PnP) solvers.

use anyhow::Result;
use mmio::uvtrack_reader::FrameNumber;

use mmoptimise::solver::levenberg_marquardt::{
    LevenbergMarquardtConfig, LevenbergMarquardtSolver,
    LevenbergMarquardtWorkspace,
};

use crate::bundle_adjust::{
    rotation_matrix_and_translation_to_camera_pose,
    rotation_matrix_to_full_quaternion, SingleCameraBAProblem,
};
use crate::datatype::camera_pose::CameraPose;
use crate::datatype::common::UnitValue;
use crate::datatype::conversions::uv_point_to_camera_coord_point;
use crate::datatype::{
    convert_camera_coord_to_ndc_point_with_intrinsics, BundlePositions,
    CameraIntrinsics, CameraToSceneCorrespondence, MarkerObservations,
    ScenePoint3, SceneUnit, UvValue,
};
use crate::sfm_camera::camera_pnp_methods::compute_camera_pose_with_method;
use crate::sfm_camera::constants::MIN_MARKERS_FOR_PNP;
use crate::sfm_camera::constants::RECOMENDED_MARKERS_FOR_PNP;

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Refine a camera pose using bundle adjustment with the 3D bundle
/// positions fixed (only the camera moves).
///
/// Returns a tuple of (refined pose, mean reprojection error) or an
/// error if the optimisation fails.
pub fn refine_camera_pose_with_fixed_bundles(
    initial_pose: &CameraPose,
    correspondences: &[CameraToSceneCorrespondence<f64>],
    camera_intrinsics: &CameraIntrinsics,
    observations_buf: &mut Vec<(usize, f64, f64)>,
    points_buf: &mut Vec<[f64; 3]>,
    workspace: &mut Option<LevenbergMarquardtWorkspace>,
) -> Result<(CameraPose, f64)> {
    let rotation_matrix = *initial_pose.rotation();
    let translation_vec = initial_pose.translation();
    let translation = [translation_vec.x, translation_vec.y, translation_vec.z];

    // Build (point_index, observed_x, observed_y) tuples in NDC space.
    observations_buf.clear();
    for (point_idx, corr) in correspondences.iter().enumerate() {
        let ndc_point = convert_camera_coord_to_ndc_point_with_intrinsics(
            corr.camera_point,
            camera_intrinsics,
        );
        observations_buf.push((
            point_idx,
            ndc_point.x.value(),
            ndc_point.y.value(),
        ));
    }

    let focal_length_x = camera_intrinsics.focal_length_x;
    let focal_length_y = camera_intrinsics.focal_length_y;
    let principal_point = (
        camera_intrinsics.principal_point.x.value(),
        camera_intrinsics.principal_point.y.value(),
    );

    let quaternion = rotation_matrix_to_full_quaternion(&rotation_matrix);

    points_buf.clear();
    for corr in correspondences {
        points_buf.push([
            corr.scene_point.coords.x.value(),
            corr.scene_point.coords.y.value(),
            corr.scene_point.coords.z.value(),
        ]);
    }

    // Points are fixed; only the camera pose is optimised.
    let problem = SingleCameraBAProblem::new(
        observations_buf,
        focal_length_x,
        focal_length_y,
        principal_point,
        quaternion,
        translation,
        points_buf,
    );

    let initial_params = problem.pack_parameters();

    let config = LevenbergMarquardtConfig {
        max_iterations: 10,
        ..Default::default()
    };
    let solver = LevenbergMarquardtSolver::new(config);

    let needs_new = match workspace.as_mut() {
        Some(ws) => ws.reuse_with(&problem, &initial_params).is_err(),
        None => true,
    };
    if needs_new {
        *workspace =
            Some(LevenbergMarquardtWorkspace::new(&problem, &initial_params)?);
    }
    let result = solver.solve_problem(&problem, workspace.as_mut().unwrap())?;

    // Each observation contributes two residuals (x, y) in NDC units.
    // Compute mean Euclidean distance across all observations.
    let num_observations = result.residuals.len() / 2;
    let mean_error = if num_observations > 0 {
        let mut total_distance = 0.0;
        for i in 0..num_observations {
            let res_x = result.residuals[i * 2];
            let res_y = result.residuals[i * 2 + 1];
            let distance = (res_x * res_x + res_y * res_y).sqrt();
            total_distance += distance;
        }
        total_distance / num_observations as f64
    } else {
        f64::INFINITY
    };

    mm_debug_eprintln!("  [Refinement] Final RMSE (NDC): {:.6}", mean_error);
    mm_debug_eprintln!("  [Refinement] Iterations: {}", result.iterations);

    let refined_rotation_matrix =
        problem.extract_camera_rotation_matrix(&result.parameters);
    let refined_translation =
        problem.extract_camera_translation(&result.parameters);

    let refined_pose = rotation_matrix_and_translation_to_camera_pose(
        &refined_rotation_matrix,
        &refined_translation,
    );

    Ok((refined_pose, mean_error))
}

/// Result of a PnP camera pose estimation.
#[derive(Clone, Debug)]
pub struct PnPSolveResult {
    /// The frame that was solved.
    pub frame: FrameNumber,
    /// The estimated camera pose.
    pub pose: CameraPose,
    /// Mean reprojection error in normalised camera coordinates.
    pub rmse: f64,
}

/// Solve camera pose for a single frame using PnP, given known 3D bundle positions.
///
/// Returns `None` if there are too few 2D-3D correspondences.
fn solve_frame_with_pnp(
    marker_observations: &MarkerObservations,
    selected_marker_indices: &[usize],
    frame: FrameNumber,
    bundle_positions: &BundlePositions,
    camera_intrinsics: &CameraIntrinsics,
    observations_buf: &mut Vec<(usize, f64, f64)>,
    points_buf: &mut Vec<[f64; 3]>,
    workspace: &mut Option<LevenbergMarquardtWorkspace>,
) -> Option<PnPSolveResult> {
    let mut correspondences = Vec::new();
    let mut bundle_indices_used = Vec::new();
    let mut visible_markers_count = 0;
    let mut markers_with_bundles_count = 0;

    for &marker_idx in selected_marker_indices {
        if let Some(&point_3d) = bundle_positions.get(&marker_idx) {
            markers_with_bundles_count += 1;

            if let Some((u, v)) =
                marker_observations.get_uv_at_frame(marker_idx, frame)
            {
                visible_markers_count += 1;
                let uv_point = UvValue::point2(u, v);

                let cam_coord_point =
                    uv_point_to_camera_coord_point(uv_point, camera_intrinsics);

                let scene_point = ScenePoint3::new(
                    SceneUnit(point_3d.x),
                    SceneUnit(point_3d.y),
                    SceneUnit(point_3d.z),
                );

                let correspondence = CameraToSceneCorrespondence::from_points(
                    cam_coord_point,
                    scene_point,
                );

                correspondences.push(correspondence);
                bundle_indices_used.push(marker_idx);
            }
        }
    }

    mm_debug_eprintln!(
        "    Frame {}: {} markers with bundles, {} visible, {} correspondences",
        frame,
        markers_with_bundles_count,
        visible_markers_count,
        correspondences.len()
    );

    if correspondences.len() < MIN_MARKERS_FOR_PNP {
        mm_debug_eprintln!(
            "    Frame {}: FAILED - insufficient correspondences ({} < {})",
            frame,
            correspondences.len(),
            MIN_MARKERS_FOR_PNP
        );
        return None;
    }

    match compute_camera_pose_with_method(&correspondences, camera_intrinsics) {
        Ok(Some(method_result)) => {
            mm_debug_eprintln!(
                "    Frame {}: PnP succeeded with {} correspondences, initial error: {:.6}",
                frame, method_result.num_correspondences, method_result.reprojection_error
            );

            let mut best_pose = method_result.pose;
            let valid_correspondences = method_result.num_correspondences;
            let total_correspondences = correspondences.len();

            // Refine the pose with bundle adjustment (bundles fixed).
            let rmse = {
                match refine_camera_pose_with_fixed_bundles(
                    &best_pose,
                    &correspondences,
                    camera_intrinsics,
                    observations_buf,
                    points_buf,
                    workspace,
                ) {
                    Ok((refined_pose, rmse)) => {
                        mm_debug_eprintln!(
                            "    Frame {}: pose refinement succeeded, RMSE: {:.6}",
                            frame, rmse
                        );
                        best_pose = refined_pose;
                        rmse
                    }
                    Err(e) => {
                        mm_debug_eprintln!(
                            "    Frame {}: WARNING - pose refinement failed: {:?}, using unrefined pose",
                            frame, e
                        );
                        method_result.reprojection_error
                    }
                }
            };

            const MAX_RMSE: f64 = f64::INFINITY;
            if rmse >= MAX_RMSE {
                mm_debug_eprintln!(
                    "    Frame {}: REJECTED - RMSE too high ({:.6} > {:.4} threshold)",
                    frame, rmse, MAX_RMSE
                );
                return None;
            }

            if DEBUG {
                let camera_center = best_pose.center();
                mm_debug_eprintln!(
                    "    Frame {}: SUCCESS - SQPnP at ({:.3}, {:.3}, {:.3}) RMSE: {:.6}, using {}/{} correspondences",
                    frame,
                    camera_center.x,
                    camera_center.y,
                    camera_center.z,
                    rmse, valid_correspondences, total_correspondences
                );
            }

            let result = PnPSolveResult {
                frame,
                pose: best_pose.clone(),
                rmse,
            };

            Some(result)
        }
        Ok(None) => {
            mm_debug_eprintln!(
                "    Frame {}: FAILED - SQPnP returned no valid poses",
                frame,
            );
            None
        }
        Err(e) => {
            mm_debug_eprintln!(
                "    Frame {}: FAILED - SQPnP error: {:?}",
                frame,
                e
            );
            None
        }
    }
}

/// Count how many markers are both visible in `frame` and have a known 3D position.
///
/// A higher score means more correspondences are available for PnP, which
/// generally produces a more accurate camera pose.
pub fn calculate_overlap_score(
    marker_observations: &MarkerObservations,
    selected_marker_indices: &[usize],
    frame: FrameNumber,
    bundle_positions: &BundlePositions,
) -> usize {
    let mut overlap_count = 0;

    for &marker_idx in selected_marker_indices {
        if !bundle_positions.contains_key(&marker_idx) {
            continue;
        }
        if marker_observations.is_visible(marker_idx, frame) {
            overlap_count += 1;
        }
    }

    overlap_count
}

/// Attempt PnP solving for every frame and return the successful results.
pub fn collect_all_camera_pnp_results(
    frames: &[FrameNumber],
    marker_observations: &MarkerObservations,
    marker_indices: &[usize],
    bundle_positions: &mut BundlePositions,
    camera_intrinsics: &CameraIntrinsics,
) -> Vec<PnPSolveResult> {
    let mut pnp_results = Vec::new();

    // Buffers and workspace reused across frames to avoid repeated allocation.
    let mut observations_buf: Vec<(usize, f64, f64)> = Vec::new();
    let mut points_buf: Vec<[f64; 3]> = Vec::new();
    let mut workspace: Option<LevenbergMarquardtWorkspace> = None;

    for frame in frames {
        let frame = *frame;
        let marker_count_overlap = calculate_overlap_score(
            marker_observations,
            marker_indices,
            frame,
            bundle_positions,
        );

        if marker_count_overlap < RECOMENDED_MARKERS_FOR_PNP {
            mm_debug_eprintln!(
                "    Frame {}: Skipped (overlap={} < min_required={})",
                frame,
                marker_count_overlap,
                RECOMENDED_MARKERS_FOR_PNP
            );
            continue;
        }

        match solve_frame_with_pnp(
            marker_observations,
            marker_indices,
            frame,
            bundle_positions,
            camera_intrinsics,
            &mut observations_buf,
            &mut points_buf,
            &mut workspace,
        ) {
            Some(result) => {
                mm_debug_eprintln!(
                    "    Frame {}: PnP succeeded (overlap={}, RMSE={:.6})",
                    frame,
                    marker_count_overlap,
                    result.rmse
                );
                pnp_results.push(result);
            }
            None => {
                mm_debug_eprintln!("    Frame {}: PnP failed", frame);
            }
        }
    }

    mm_debug_eprintln!("  PnP results: {}", pnp_results.len());

    pnp_results
}
