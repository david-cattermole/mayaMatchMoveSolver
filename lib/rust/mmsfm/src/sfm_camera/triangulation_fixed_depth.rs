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

//! Fixed-depth triangulation for the camera solver.
//!
//! Places 3D points at a fixed depth along camera viewing rays, used as a
//! fallback when geometric triangulation fails.

use nalgebra::{Point3, Vector3};
use std::collections::BTreeMap;

use mmio::uvtrack_reader::{FrameData, FrameNumber, MarkersData};
use mmoptimise::solver::common::OptimisationProblem;
use mmoptimise::solver::levenberg_marquardt::{
    LevenbergMarquardtConfig, LevenbergMarquardtSolver,
    LevenbergMarquardtWorkspace,
};

use crate::bundle_adjust::rotation_matrix_to_full_quaternion;
use crate::bundle_adjust::SinglePointBAProblem;
use crate::bundle_triangulation::{
    AggregationMode, DepthAverageConfig, TriangulateDataDepthAverage,
    TriangulatorDepthAverage,
};
use crate::datatype::camera_pose::CameraPose;
use crate::datatype::conversions::{
    convert_ndc_to_ray_direction, convert_uv_to_ndc_point,
};
use crate::datatype::{
    BundlePositions, CameraIntrinsics, CameraPoses, NdcPoint2, UnitValue,
    UvValue,
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Number of BA iterations for single-point refinement during fixed-depth triangulation.
const FIXED_DEPTH_REFINE_ITERATIONS: usize = 8;

// ============================================================================
// Mean Depth Calculation
// ============================================================================

/// Calculate mean depth of existing bundles from the midpoint between two cameras.
///
/// Returns mean depth, or 10x baseline distance if no bundles exist.
pub fn calculate_mean_depth_from_bundles(
    bundle_positions: &BundlePositions,
    pose_a: &CameraPose,
    pose_b: &CameraPose,
) -> f64 {
    let center_a = pose_a.center();
    let center_b = pose_b.center();
    let baseline = (center_a - center_b).norm();
    let fallback_depth = baseline * 10.0;

    if bundle_positions.is_empty() {
        return fallback_depth;
    }

    let mut total_depth = 0.0;
    let mut count = 0;

    for point in bundle_positions.values() {
        let distance_a = (point.coords - center_a.coords).norm();
        let distance_b = (point.coords - center_b.coords).norm();
        // Use maximum distance to ensure bundle is never behind
        // either camera.
        total_depth += distance_a.max(distance_b);
        count += 1;
    }

    if count == 0 {
        fallback_depth
    } else {
        total_depth / count as f64
    }
}

/// Calculate mean depth for the scene based on existing bundles.
///
/// Returns mean depth, or a fallback if no bundles exist.
pub fn calculate_mean_depth_for_scene(
    bundle_positions: &BundlePositions,
    camera_poses: &CameraPoses,
) -> f64 {
    if camera_poses.is_empty() || bundle_positions.is_empty() {
        return 10.0; // Default fallback depth.
    }

    let camera_centers: Vec<_> =
        camera_poses.values().map(|pose| pose.center()).collect();

    // Calculate baseline as max distance between any two cameras.
    let mut max_baseline: f64 = 0.0;
    for i in 0..camera_centers.len() {
        for j in (i + 1)..camera_centers.len() {
            let dist = (camera_centers[i] - camera_centers[j]).norm();
            max_baseline = max_baseline.max(dist);
        }
    }

    let fallback_depth = if max_baseline > 0.01 {
        max_baseline * 10.0
    } else {
        10.0
    };

    // Calculate mean distance from all cameras to all bundles.
    let mut total_depth = 0.0;
    let mut count = 0;

    for point in bundle_positions.values() {
        for center in &camera_centers {
            total_depth += (point.coords - center.coords).norm();
            count += 1;
        }
    }

    if count == 0 {
        fallback_depth
    } else {
        total_depth / count as f64
    }
}

// ============================================================================
// Geometric Utilities
// ============================================================================

/// Compute geometric median of 3D points using Weiszfeld's algorithm.
///
/// Robust to outliers, minimizing the sum of Euclidean distances to all points.
fn compute_geometric_median(points: &[Point3<f64>]) -> Point3<f64> {
    if points.is_empty() {
        return Point3::origin();
    }
    if points.len() == 1 {
        return points[0];
    }

    // Initialize with centroid.
    let mut sum = Vector3::zeros();
    for p in points {
        sum += p.coords;
    }
    let n = points.len() as f64;
    let mut estimate = Point3::from(sum / n);

    const EPS: f64 = 1e-10;
    const MAX_ITERATIONS: usize = 100;
    const TOLERANCE: f64 = 1e-8;

    for _ in 0..MAX_ITERATIONS {
        let mut numerator = Vector3::zeros();
        let mut denominator = 0.0;

        for point in points {
            let diff = point.coords - estimate.coords;
            let distance = diff.norm();

            if distance > EPS {
                let weight = 1.0 / distance;
                numerator += point.coords * weight;
                denominator += weight;
            }
        }

        if denominator < EPS {
            break;
        }

        let new_estimate = Point3::from(numerator / denominator);
        let change = (new_estimate.coords - estimate.coords).norm();
        estimate = new_estimate;

        if change < TOLERANCE {
            break;
        }
    }

    estimate
}

/// Unproject NDC coordinates to world space at a fixed depth.
fn unproject_ndc_to_world_at_depth(
    ndc: NdcPoint2<f64>,
    pose: &CameraPose,
    camera_intrinsics: &CameraIntrinsics,
    depth: f64,
) -> Point3<f64> {
    let center = pose.center();
    let ray_direction =
        convert_ndc_to_ray_direction(ndc, pose, camera_intrinsics);
    Point3::from(center.coords + ray_direction * depth)
}

// ============================================================================
// Single-Point Bundle Adjustment Refinement
// ============================================================================

/// Refine a single 3D point using Levenberg-Marquardt to minimize reprojection error.
///
/// Returns the refined point, or None if refinement fails.
pub fn refine_single_point_with_ba(
    initial_point: Point3<f64>,
    observations: &[(usize, f64, f64)],
    camera_rotations: &[[f64; 4]],
    camera_translations: &[[f64; 3]],
    camera_intrinsics: &CameraIntrinsics,
    max_iterations: usize,
) -> Option<Point3<f64>> {
    // Need at least 2 observations for meaningful refinement.
    if observations.len() < 2 {
        return None;
    }

    let focal_length_x = camera_intrinsics.focal_length_x;
    let focal_length_y = camera_intrinsics.focal_length_y;
    let principal_point = (
        camera_intrinsics.principal_point.x.value(),
        camera_intrinsics.principal_point.y.value(),
    );

    let initial_point_arr = [initial_point.x, initial_point.y, initial_point.z];
    let problem = SinglePointBAProblem::new(
        observations.to_vec(),
        focal_length_x,
        focal_length_y,
        principal_point,
        camera_rotations,
        camera_translations,
        initial_point_arr,
    );

    let num_residuals = problem.residual_count();
    let num_params = problem.parameter_count();
    if num_residuals < num_params {
        return None;
    }

    let config = LevenbergMarquardtConfig {
        max_iterations,
        max_function_evaluations: max_iterations * 10,
        gradient_tolerance: 1e-10,
        parameter_tolerance: 1e-10,
        function_tolerance: 1e-10,
        ..Default::default()
    };

    let solver = LevenbergMarquardtSolver::new(config);
    let initial_params = problem.pack_parameters();

    let mut workspace =
        LevenbergMarquardtWorkspace::new(&problem, &initial_params).ok()?;
    let result = solver.solve_problem(&problem, &mut workspace).ok()?;

    let refined = problem.extract_point(&result.parameters);

    if refined.iter().all(|&x| x.is_finite()) {
        Some(Point3::new(refined[0], refined[1], refined[2]))
    } else {
        None
    }
}

// ============================================================================
// Core Triangulation Functions
// ============================================================================

/// Helper to build camera pose arrays for bundle adjustment.
fn build_camera_pose_arrays(
    sorted_frames: &[FrameNumber],
    camera_poses: &CameraPoses,
) -> (Vec<[f64; 4]>, Vec<[f64; 3]>) {
    let rotations: Vec<[f64; 4]> = sorted_frames
        .iter()
        .map(|f| {
            let pose = &camera_poses[f];
            rotation_matrix_to_full_quaternion(pose.rotation())
        })
        .collect();

    let translations: Vec<[f64; 3]> = sorted_frames
        .iter()
        .map(|f| {
            let pose = &camera_poses[f];
            let t = pose.translation();
            [t.x, t.y, t.z]
        })
        .collect();

    (rotations, translations)
}

/// Triangulate a single bundle using fixed-depth projection and optional BA refinement.
///
/// Projects observations at a fixed depth, computes the geometric median, then
/// optionally refines the result with bundle adjustment.
pub fn triangulate_bundle_with_visible_frames_fixed_depth(
    visible_frames: &[FrameNumber],
    camera_poses: &CameraPoses,
    frame_data: &FrameData,
    camera_intrinsics: &CameraIntrinsics,
    mean_depth: f64,
    refine_iterations: usize,
) -> Option<Point3<f64>> {
    if visible_frames.len() < 2 {
        return None;
    }

    // Build frame indexing.
    let mut sorted_frames: Vec<FrameNumber> = visible_frames.to_vec();
    sorted_frames.sort_unstable();

    let frame_to_idx: BTreeMap<FrameNumber, usize> = sorted_frames
        .iter()
        .enumerate()
        .map(|(i, &f)| (f, i))
        .collect();

    let (camera_rotations, camera_translations) =
        build_camera_pose_arrays(&sorted_frames, camera_poses);

    // Collect projected points and observations.
    let mut projected_points: Vec<Point3<f64>> =
        Vec::with_capacity(visible_frames.len());
    let mut observations_ndc: Vec<(usize, f64, f64)> =
        Vec::with_capacity(visible_frames.len());

    for &frame in visible_frames {
        let pose = &camera_poses[&frame];

        let idx = frame_data.frames.iter().position(|&f| f == frame)?;

        let uv =
            UvValue::point2(frame_data.u_coords[idx], frame_data.v_coords[idx]);
        let ndc = convert_uv_to_ndc_point(uv);

        let projected_point = unproject_ndc_to_world_at_depth(
            ndc,
            pose,
            camera_intrinsics,
            mean_depth,
        );
        projected_points.push(projected_point);

        if let Some(&cam_idx) = frame_to_idx.get(&frame) {
            observations_ndc.push((cam_idx, ndc.x.value(), ndc.y.value()));
        }
    }

    if projected_points.len() < 2 {
        return None;
    }

    // Compute geometric median.
    let initial_point = compute_geometric_median(&projected_points);

    if !initial_point.coords.iter().all(|&x| x.is_finite()) {
        return None;
    }

    // Optionally refine using bundle adjustment.
    if refine_iterations > 0 {
        refine_single_point_with_ba(
            initial_point,
            &observations_ndc,
            &camera_rotations,
            &camera_translations,
            camera_intrinsics,
            refine_iterations,
        )
        .or(Some(initial_point))
    } else {
        Some(initial_point)
    }
}

/// Triangulate markers at fixed depth using n-view projection and geometric median.
///
/// For each marker without a bundle, projects observations at a fixed depth,
/// computes the geometric median, and refines using single-point bundle adjustment.
/// Returns the number of new bundles placed.
pub fn triangulate_missing_bundles_at_fixed_depth(
    markers: &MarkersData,
    marker_indices: &[usize],
    camera_poses: &CameraPoses,
    bundle_positions: &mut BundlePositions,
    camera_intrinsics: &CameraIntrinsics,
) -> usize {
    let mean_depth =
        calculate_mean_depth_for_scene(bundle_positions, camera_poses);

    mm_eprintln_debug!(
        "    Fixed-depth triangulation: mean_depth={:.4}, {} existing bundles, {} camera poses",
        mean_depth,
        bundle_positions.len(),
        camera_poses.len()
    );

    // Build sorted frame list for consistent indexing.
    let mut sorted_frames: Vec<FrameNumber> =
        camera_poses.keys().copied().collect();
    sorted_frames.sort_unstable();

    let frame_to_idx: BTreeMap<FrameNumber, usize> = sorted_frames
        .iter()
        .enumerate()
        .map(|(i, &f)| (f, i))
        .collect();

    let (camera_rotations, camera_translations) =
        build_camera_pose_arrays(&sorted_frames, camera_poses);

    let mut fixed_count = 0;
    let mut refined_count = 0;
    for &marker_idx in marker_indices {
        if bundle_positions.contains_key(&marker_idx) {
            continue;
        }

        if marker_idx >= markers.frame_data.len() {
            continue;
        }

        let frame_data = &markers.frame_data[marker_idx];

        // Collect all cameras where marker is visible.
        let mut projected_points: Vec<Point3<f64>> = Vec::new();
        let mut observations_ndc: Vec<(usize, f64, f64)> = Vec::new();

        for (j, &frame) in frame_data.frames.iter().enumerate() {
            if let Some(&cam_idx) = frame_to_idx.get(&frame) {
                let pose = &camera_poses[&frame];
                let uv = UvValue::point2(
                    frame_data.u_coords[j],
                    frame_data.v_coords[j],
                );
                let ndc = convert_uv_to_ndc_point(uv);

                let point_3d = unproject_ndc_to_world_at_depth(
                    ndc,
                    pose,
                    camera_intrinsics,
                    mean_depth,
                );
                projected_points.push(point_3d);

                observations_ndc.push((cam_idx, ndc.x.value(), ndc.y.value()));
            }
        }

        if projected_points.len() < 2 {
            continue;
        }

        let initial_point = compute_geometric_median(&projected_points);

        if !initial_point.coords.iter().all(|&x| x.is_finite()) {
            continue;
        }

        // Refine using bundle adjustment.
        let final_point = match refine_single_point_with_ba(
            initial_point,
            &observations_ndc,
            &camera_rotations,
            &camera_translations,
            camera_intrinsics,
            FIXED_DEPTH_REFINE_ITERATIONS,
        ) {
            Some(refined) => {
                refined_count += 1;
                refined
            }
            None => initial_point,
        };

        if final_point.coords.iter().all(|&x| x.is_finite()) {
            bundle_positions.insert(marker_idx, final_point);
            fixed_count += 1;
        }
    }

    if DEBUG && fixed_count > 0 {
        eprintln!(
            "    Fixed-depth triangulation: placed {} new bundles ({} refined via BA, total: {})",
            fixed_count,
            refined_count,
            bundle_positions.len()
        );
    }

    fixed_count
}

// ============================================================================
// Two-View Fixed-Depth Triangulation (Phase 2)
// ============================================================================

/// Two-view fixed-depth triangulation for markers that failed geometric triangulation.
///
/// Places points at the mean scene depth using the TriangulatorDepthAverage algorithm.
pub fn fixed_depth_triangulation(
    triangulated_points_valid: &Vec<bool>,
    bundle_positions: &mut BundlePositions,
    pose_a: &CameraPose,
    pose_b: &CameraPose,
    marker_indices: &[usize],
    markers: &MarkersData,
    frame_a: FrameNumber,
    frame_b: FrameNumber,
) {
    let failed_count =
        triangulated_points_valid.iter().filter(|&&v| !v).count();
    if failed_count == 0 {
        return;
    }

    mm_eprintln_debug!(
        "  Attempting fixed-depth placement for {} failed triangulations...",
        failed_count
    );

    let mean_depth =
        calculate_mean_depth_from_bundles(bundle_positions, pose_a, pose_b);

    let config = DepthAverageConfig {
        depth: mean_depth,
        aggregation_mode: AggregationMode::GeometricMedian {
            max_iterations: 8,
            tolerance: 1e-6,
        },
    };
    let mut triangulator = TriangulatorDepthAverage::new(failed_count, config);

    let mut data = TriangulateDataDepthAverage::with_capacity(failed_count);
    let mut failed_marker_indices = Vec::with_capacity(failed_count);

    for (i, &marker_idx) in marker_indices.iter().enumerate() {
        // Skip already valid triangulations.
        if i < triangulated_points_valid.len() && triangulated_points_valid[i] {
            continue;
        }
        // Skip if already has bundle position.
        if bundle_positions.contains_key(&marker_idx) {
            continue;
        }
        if marker_idx >= markers.frame_data.len() {
            continue;
        }

        let frame_data = &markers.frame_data[marker_idx];

        // Get UV coordinates for this marker in both frames.
        let mut uv_a = None;
        let mut uv_b = None;
        for (j, &frame) in frame_data.frames.iter().enumerate() {
            if frame == frame_a {
                uv_a = Some(UvValue::point2(
                    frame_data.u_coords[j],
                    frame_data.v_coords[j],
                ));
            } else if frame == frame_b {
                uv_b = Some(UvValue::point2(
                    frame_data.u_coords[j],
                    frame_data.v_coords[j],
                ));
            }
        }

        if let (Some(uv_coord_a), Some(uv_coord_b)) = (uv_a, uv_b) {
            let ndc_a = convert_uv_to_ndc_point(uv_coord_a);
            let ndc_b = convert_uv_to_ndc_point(uv_coord_b);
            data.add_stereo_observation(
                pose_a.clone(),
                pose_b.clone(),
                ndc_a,
                ndc_b,
            );
            failed_marker_indices.push(marker_idx);
        }
    }

    let result = triangulator.triangulate_points(&data);

    let mut fixed_depth_count = 0;
    for (i, (&point, &is_valid)) in result
        .inner
        .points
        .iter()
        .zip(result.inner.valid.iter())
        .enumerate()
    {
        if is_valid {
            let marker_idx = failed_marker_indices[i];
            bundle_positions.insert(marker_idx, point);
            fixed_depth_count += 1;
        }
    }

    mm_eprintln_debug!(
        "  Placed {} points at fixed depth ({} total bundles now)",
        fixed_depth_count,
        bundle_positions.len()
    );
}
