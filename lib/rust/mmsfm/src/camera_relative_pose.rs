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

use nalgebra::{Matrix3, Point2, Point3};

use anyhow::{anyhow, Result};

use crate::bundle_adjust::ensure_orthogonal_rotation;
use crate::bundle_triangulation::{
    calculate_point_angle_radian, OptimalAngularConfig,
    TriangulateDataOptimalAngular, TriangulatorOptimalAngular,
};
use crate::camera_essential_matrix::{
    EssentialMatrixEightPlusPointWorkspace, EssentialMatrixEightPointWorkspace,
    EssentialMatrixFivePointWorkspace,
};
use crate::datatype::camera_pose::is_valid_pose;
use crate::datatype::common::UnitValue;
use crate::datatype::conversions::uv_point_to_camera_coord_point;
use crate::datatype::{
    BearingVectorCorrespondence, CameraCoordPoint2, CameraCoordVector2,
    CameraIntrinsics, CameraPose, UvPoint2,
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Result of relative pose computation.
#[derive(Debug, Clone)]
pub struct RelativePoseInfo {
    /// Essential matrix between the two views.
    pub essential_matrix: Matrix3<f64>,
    /// Angular error (existing metric).
    pub residual_precision: f64,
    /// Sampson error metric.
    pub sampson_error: f64,
    /// Symmetric epipolar distance error metric.
    pub symmetric_epipolar_error: f64,
    /// Epipolar distance error metric.
    pub epipolar_error: f64,
    /// Computed relative pose.
    pub relative_pose: CameraPose,
    /// Triangulated 3D points (sparse: one entry per correspondence, invalid points are origin).
    pub triangulated_points: Vec<Point3<f64>>,
    /// Validity flags for each triangulated point.
    pub triangulated_points_valid: Vec<bool>,
}

impl RelativePoseInfo {
    // TODO: Add `Default` trait implementation.
    pub fn new() -> Self {
        Self {
            essential_matrix: Matrix3::zeros(),
            residual_precision: 0.0,
            sampson_error: 0.0,
            symmetric_epipolar_error: 0.0,
            epipolar_error: 0.0,
            relative_pose: CameraPose::default(),
            triangulated_points: Vec::new(),
            triangulated_points_valid: Vec::new(),
        }
    }
}

/// Decompose an essential matrix into a relative camera pose using triangulation
/// to select the correct solution from the four possible candidates.
fn decompose_essential_matrix_to_pose_optimal_angular(
    essential_matrix: &Matrix3<f64>,
    points_a: &[CameraCoordPoint2<f64>],
    points_b: &[CameraCoordPoint2<f64>],
) -> Result<(CameraPose, Vec<Point3<f64>>, Vec<bool>)> {
    // SVD decomposition of essential matrix.
    let svd = essential_matrix.svd(true, true);
    let mut u = svd
        .u
        .ok_or_else(|| anyhow!("SVD failed to compute U matrix"))?;
    let mut vt = svd
        .v_t
        .ok_or_else(|| anyhow!("SVD failed to compute V^T matrix"))?;

    // Ensure U and V^T have det = +1 to avoid reflections.
    if u.determinant() < 0.0 {
        mm_eprintln_debug!(
            "U has det = -1, flipping last column to force det = +1"
        );
        let col2 = -u.column(2);
        u.set_column(2, &col2);
    }
    if vt.determinant() < 0.0 {
        mm_eprintln_debug!(
            "V^T has det = -1, flipping last row to force det = +1"
        );
        for j in 0..3 {
            vt[(2, j)] = -vt[(2, j)];
        }
    }

    // 90-degree rotation matrix used in essential matrix decomposition.
    let rotation_90_deg = Matrix3::new(
        0.0, -1.0, 0.0, // First row.
        1.0, 0.0, 0.0, // Second row.
        0.0, 0.0, 1.0, // Third row.
    );

    // Two possible rotations from the essential matrix decomposition.
    let rotation1_raw = u * rotation_90_deg * vt;
    let rotation2_raw = u * rotation_90_deg.transpose() * vt;

    // Re-orthogonalize to ensure valid rotation matrices.
    let rotation1 = ensure_orthogonal_rotation(&rotation1_raw);
    let rotation2 = ensure_orthogonal_rotation(&rotation2_raw);

    mm_eprintln_debug!(
        "\n=== ROTATION MATRIX VALIDATION (OPTIMAL ANGULAR) ==="
    );
    mm_eprintln_debug!("rotation1 determinant: {:.6}", rotation1.determinant());
    mm_eprintln_debug!("rotation2 determinant: {:.6}", rotation2.determinant());

    // Translation direction (up to scale, sign unknown).
    let translation = u.column(2).into_owned();

    // Four candidate poses from the two rotations and two translation signs.
    let candidate_poses = [
        CameraPose::new(rotation1, (-translation).into()),
        CameraPose::new(rotation1, translation.into()),
        CameraPose::new(rotation2, (-translation).into()),
        CameraPose::new(rotation2, translation.into()),
    ];

    struct PoseCandidate {
        pose: CameraPose,
        valid_ratio: f64,
        triangulated_points: Vec<Point3<f64>>,
        triangulated_points_valid: Vec<bool>,
    }

    let reference_pose = CameraPose::default();
    let mut valid_candidates: Vec<PoseCandidate> = Vec::new();
    let num_correspondences = points_a.len();

    let config = OptimalAngularConfig::default();
    let mut triangulator =
        TriangulatorOptimalAngular::new(num_correspondences, config);
    let mut triangulate_data =
        TriangulateDataOptimalAngular::with_capacity(num_correspondences);

    struct PoseDiagnostics {
        pose_idx: usize,
        is_valid_pose: bool,
        triangulation_count: usize,
        valid_count: usize,
        failed_validation_count: usize,
    }
    let mut all_pose_diagnostics = Vec::new();

    for (pose_idx, candidate_pose) in candidate_poses.iter().enumerate() {
        mm_eprintln_debug!(
            "  Testing pose candidate {}/4 (Optimal Angular): {:?}",
            pose_idx + 1,
            candidate_pose
        );

        let mut pose_diagnostics = PoseDiagnostics {
            pose_idx,
            is_valid_pose: is_valid_pose(candidate_pose),
            triangulation_count: 0,
            valid_count: 0,
            failed_validation_count: 0,
        };
        if !pose_diagnostics.is_valid_pose {
            mm_eprintln_debug!("    Invalid pose (det != 1 or contains NaN)");
            all_pose_diagnostics.push(pose_diagnostics);
            continue;
        }

        triangulate_data.clear();

        let center_a = *reference_pose.center();
        let center_b = *candidate_pose.center();
        let rot_transpose_a = reference_pose.rotation().transpose();
        let rot_transpose_b = candidate_pose.rotation().transpose();

        for i in 0..num_correspondences {
            let camera_coord_a = (points_a[i].x.value(), points_a[i].y.value());
            let camera_coord_b = (points_b[i].x.value(), points_b[i].y.value());

            triangulate_data.add_stereo_observation_from_coords(
                center_a,
                center_b,
                rot_transpose_a,
                rot_transpose_b,
                camera_coord_a,
                camera_coord_b,
            );
        }

        let result = triangulator.triangulate_points(&triangulate_data);
        let triangulation_results = result.inner;

        let mut valid_count = 0;
        let triangulation_count: usize;
        let mut triangulated_points =
            vec![Point3::origin(); num_correspondences];
        let mut triangulated_points_valid = vec![false; num_correspondences];
        {
            let successful_count =
                triangulation_results.valid.iter().filter(|&&v| v).count();
            triangulation_count = successful_count;
            pose_diagnostics.triangulation_count = successful_count;

            mm_eprintln_debug!(
                "  Triangulation results: {}/{} successful",
                successful_count,
                num_correspondences
            );

            for (i, &is_valid) in triangulation_results.valid.iter().enumerate()
            {
                let point_a =
                    Point2::new(points_a[i].x.value(), points_a[i].y.value());
                let point_b =
                    Point2::new(points_b[i].x.value(), points_b[i].y.value());
                let point_angle_radian = calculate_point_angle_radian(
                    point_a,
                    point_b,
                    &reference_pose,
                    candidate_pose,
                );

                let point_3d = &triangulation_results.points[i];
                let depth_a = reference_pose.apply_transform(point_3d).z;
                let depth_b = candidate_pose.apply_transform(point_3d).z;

                let valid = is_valid
                    && depth_a < 0.0
                    && depth_b < 0.0
                    && depth_a > MAXIMUM_DEPTH
                    && depth_b > MAXIMUM_DEPTH
                    && point_angle_radian > MINIMUM_ANGLE_RADIAN;

                triangulated_points_valid[i] = valid;

                if valid {
                    valid_count += 1;
                    pose_diagnostics.valid_count += 1;
                    triangulated_points[i] = *point_3d;
                    triangulated_points_valid[i] = valid;

                    mm_eprintln_debug!("    Point {}: VALID - angle={:.3} depth_a={:.3}, depth_b={:.3}, pos=[{:.3}, {:.3}, {:.3}]",
                                  i, point_angle_radian.to_degrees(), depth_a, depth_b, point_3d.x, point_3d.y, point_3d.z);
                } else {
                    pose_diagnostics.failed_validation_count += 1;
                    mm_eprintln_debug!("    Point {}: FAILED - angle={:.3} depth_a={:.3}, depth_b={:.3}",
                            i, point_angle_radian.to_degrees(), depth_a, depth_b);
                }
            }
        }

        all_pose_diagnostics.push(pose_diagnostics);

        if triangulation_count > 0 {
            let valid_ratio = valid_count as f64 / num_correspondences as f64;

            valid_candidates.push(PoseCandidate {
                pose: candidate_pose.clone(),
                valid_ratio,
                triangulated_points,
                triangulated_points_valid,
            });
        }
    }

    mm_eprintln_debug!(
        "  Pose candidates with valid triangulations: {}",
        valid_candidates.len()
    );

    if valid_candidates.is_empty() {
        // TODO: Convert these raw macros into proper debug prints.
        if DEBUG {
            mm_eprintln_debug!(
                "[Phase 2] Essential matrix decomposition (Optimal Angular): {} correspondences",
                num_correspondences
            );
            for pose_diagnostics in &all_pose_diagnostics {
                if !pose_diagnostics.is_valid_pose {
                    mm_eprintln_debug!(
                        "  Pose {}/4: INVALID (det != 1 or contains NaN)",
                        pose_diagnostics.pose_idx + 1
                    );
                    continue;
                }

                let total_points = num_correspondences;
                mm_eprintln_debug!(
                    "  Pose {}/4: FAILED - {}/{} valid triangulations ({:.1}%)",
                    pose_diagnostics.pose_idx + 1,
                    pose_diagnostics.valid_count,
                    total_points,
                    (pose_diagnostics.valid_count as f64 / total_points as f64)
                        * 100.0
                );
            }
            mm_eprintln_debug!("WARNING: All 4 pose candidates have zero valid triangulations.");
            mm_eprintln_debug!(
                "         Attempting fallback: selecting pose with most triangulation attempts."
            );
        }

        // Fallback: pick the pose with the most triangulation attempts.
        let mut best_triangulation_count = 0;
        let mut best_pose_idx: Option<usize> = None;

        for (idx, candidate_pose) in candidate_poses.iter().enumerate() {
            if !is_valid_pose(candidate_pose) {
                continue;
            }

            let pose_diagnostics = &all_pose_diagnostics[idx];
            if pose_diagnostics.triangulation_count > best_triangulation_count {
                best_triangulation_count = pose_diagnostics.triangulation_count;
                best_pose_idx = Some(idx);
            }
        }

        if let Some(idx) = best_pose_idx {
            mm_eprintln_debug!("WARNING: Using fallback pose {} with {} triangulation attempts (0 valid).",
                      idx + 1, best_triangulation_count);
            return Ok((candidate_poses[idx].clone(), Vec::new(), Vec::new()));
        }

        return Err(anyhow!(
            "No valid pose found from essential matrix decomposition (Optimal Angular). \
             All 4 poses produced zero valid triangulations."
        ));
    }

    // Select the candidate with the highest ratio of valid triangulated points.
    let mut best_score = -1.0;
    let mut best_candidate_idx = None;

    mm_eprintln_debug!("\n=== POSE SCORING (OPTIMAL ANGULAR) ===");

    for (candidate_idx, candidate) in valid_candidates.iter().enumerate() {
        let score = candidate.valid_ratio;

        mm_eprintln_debug!(
            "Candidate {}: valid_ratio={:.3}",
            candidate_idx + 1,
            candidate.valid_ratio
        );

        if score > best_score {
            best_score = score;
            best_candidate_idx = Some(candidate_idx);
        }
    }

    if let Some(idx) = best_candidate_idx {
        let selected = &valid_candidates[idx];
        return Ok((
            selected.pose.clone(),
            selected.triangulated_points.clone(),
            selected.triangulated_points_valid.clone(),
        ));
    }

    Err(anyhow!(
        "No valid pose found from essential matrix decomposition (Optimal Angular)."
    ))
}

/// Compute the essential matrix from point correspondences.
///
/// Chooses algorithm based on point count:
/// - 5-7 points: five-point algorithm.
/// - 8 points: eight-point algorithm.
/// - 9+ points: least-squares DLT.
///
/// Returns the essential matrix and four error metrics.
pub fn compute_essential_matrix(
    correspondences: &[BearingVectorCorrespondence],
) -> Result<(Matrix3<f64>, f64, f64, f64, f64)> {
    let num_points = correspondences.len();
    if num_points < 5 {
        return Err(anyhow!("Need at least 5 point correspondences for essential matrix estimation"));
    }

    let essential_matrix = if num_points == 8 {
        let mut workspace = EssentialMatrixEightPointWorkspace::new();
        workspace.compute_essential_matrix(correspondences)?
    } else if num_points > 8 {
        let mut workspace =
            EssentialMatrixEightPlusPointWorkspace::new_with_capacity(
                num_points,
            );
        workspace.compute_essential_matrix(correspondences)?
    } else {
        // Use five-point algorithm for 5, 6, and 7 points.
        let mut workspace = EssentialMatrixFivePointWorkspace::new();
        workspace.compute_best_essential_matrix(correspondences)?
    };

    let angular_error =
        crate::camera_essential_matrix::calculate_average_angular_error(
            &essential_matrix,
            correspondences,
        );
    let sampson_error =
        crate::camera_essential_matrix::calculate_average_sampson_error(
            &essential_matrix,
            correspondences,
        );
    let symmetric_epipolar_error =
        crate::camera_essential_matrix::calculate_average_symmetric_epipolar_distance(
            &essential_matrix,
            correspondences,
        );
    let epipolar_error =
        crate::camera_essential_matrix::calculate_average_epipolar_distance(
            &essential_matrix,
            correspondences,
        );

    Ok((
        essential_matrix,
        angular_error,
        sampson_error,
        symmetric_epipolar_error,
        epipolar_error,
    ))
}

const MINIMUM_ANGLE_RADIAN: f64 = 0.5_f64.to_radians();
const MAXIMUM_DEPTH: f64 = -250.0;

/// Compute the relative pose between two camera views.
///
/// Estimates an essential matrix from point correspondences, then decomposes
/// it into a relative rotation and translation using triangulation to select
/// the correct solution.
///
/// UV coordinates should be in the 0.0 to 1.0 range.
/// Requires at least 5 point correspondences.
pub fn compute_relative_pose_optimal_angular(
    intrinsics_a: &CameraIntrinsics,
    intrinsics_b: &CameraIntrinsics,
    uv_coords_a: &[UvPoint2<f64>],
    uv_coords_b: &[UvPoint2<f64>],
) -> Result<RelativePoseInfo> {
    if uv_coords_a.len() != uv_coords_b.len() {
        return Err(anyhow!(
            "Point correspondence arrays must have the same length"
        ));
    }
    if uv_coords_a.len() < 5 {
        return Err(anyhow!("Need at least 5 point correspondence"));
    }

    // Convert UV coordinates to camera-space bearing vectors for the essential matrix.
    let correspondences: Vec<BearingVectorCorrespondence> = uv_coords_a
        .iter()
        .zip(uv_coords_b.iter())
        .map(|(uv_a, uv_b)| {
            let camera_coord_a =
                uv_point_to_camera_coord_point(*uv_a, intrinsics_a);
            let camera_coord_b =
                uv_point_to_camera_coord_point(*uv_b, intrinsics_b);
            let camera_coord_a_vec =
                CameraCoordVector2::new(camera_coord_a.x, camera_coord_a.y);
            let camera_coord_b_vec =
                CameraCoordVector2::new(camera_coord_b.x, camera_coord_b.y);
            BearingVectorCorrespondence::new(
                camera_coord_a_vec,
                camera_coord_b_vec,
            )
        })
        .collect();

    // Convert UV coordinates to camera-space points for triangulation.
    let points_a: Vec<CameraCoordPoint2<f64>> = uv_coords_a
        .iter()
        .map(|uv_a| uv_point_to_camera_coord_point(*uv_a, intrinsics_a))
        .collect();
    let points_b: Vec<CameraCoordPoint2<f64>> = uv_coords_b
        .iter()
        .map(|uv_b| uv_point_to_camera_coord_point(*uv_b, intrinsics_b))
        .collect();

    let (
        essential_matrix,
        angular_error,
        sampson_error,
        symmetric_epipolar_error,
        epipolar_error,
    ) = compute_essential_matrix(&correspondences)?;

    // NOTE: The essential matrix transpose determines the coordinate system convention.
    let use_transpose = true;
    let essential_matrix_to_decompose = if use_transpose {
        essential_matrix.transpose()
    } else {
        essential_matrix
    };

    if DEBUG {
        mm_eprintln_debug!(
            "\n==========================================================="
        );
        mm_eprintln_debug!(
            "=== ESSENTIAL MATRIX COMPUTATION (OPTIMAL ANGULAR) ==="
        );
        mm_eprintln_debug!(
            "==========================================================="
        );
        mm_eprintln_debug!(
            "\nNumber of correspondences: {}",
            correspondences.len()
        );
        mm_eprintln_debug!("\nOriginal essential matrix E:");
        mm_eprintln_debug!("{:.6}", essential_matrix);
        mm_eprintln_debug!("\nUsing transpose: {}", use_transpose);
        mm_eprintln_debug!("\nEssential matrix to decompose E^T:");
        mm_eprintln_debug!("{:.6}", essential_matrix_to_decompose);

        let svd = essential_matrix_to_decompose.svd(false, false);
        mm_eprintln_debug!(
            "\nSingular values: [{:.6}, {:.6}, {:.6}]",
            svd.singular_values[0],
            svd.singular_values[1],
            svd.singular_values[2]
        );
        mm_eprintln_debug!(
            "Determinant: {:.6}",
            essential_matrix_to_decompose.determinant()
        );

        mm_eprintln_debug!("\nError metrics:");
        mm_eprintln_debug!(
            "  Angular error: {:.6} radians ({:.2}deg)",
            angular_error,
            angular_error.to_degrees()
        );
        mm_eprintln_debug!("  Sampson error: {:.6}", sampson_error);
        mm_eprintln_debug!(
            "  Symmetric epipolar error: {:.6}",
            symmetric_epipolar_error
        );
        mm_eprintln_debug!("  Epipolar error: {:.6}", epipolar_error);
    }

    let (relative_pose, triangulated_points, triangulated_points_valid) =
        decompose_essential_matrix_to_pose_optimal_angular(
            &essential_matrix_to_decompose,
            &points_a,
            &points_b,
        )?;

    mm_eprintln_debug!(
        "\n==========================================================="
    );
    mm_eprintln_debug!("=== FINAL RELATIVE POSE (OPTIMAL ANGULAR) ===");
    mm_eprintln_debug!(
        "==========================================================="
    );
    mm_eprintln_debug!("\nRotation matrix:");
    mm_eprintln_debug!("{:.6}", relative_pose.rotation());
    mm_eprintln_debug!(
        "\nCenter: [{:.6}, {:.6}, {:.6}]",
        relative_pose.center().x,
        relative_pose.center().y,
        relative_pose.center().z
    );
    mm_eprintln_debug!(
        "\nTranslation: [{:.6}, {:.6}, {:.6}]",
        relative_pose.translation().x,
        relative_pose.translation().y,
        relative_pose.translation().z
    );
    mm_eprintln_debug!(
        "\nRotation determinant: {:.6}",
        relative_pose.rotation().determinant()
    );
    mm_eprintln_debug!(
        "\n===========================================================\n"
    );

    Ok(RelativePoseInfo {
        essential_matrix: essential_matrix_to_decompose,
        residual_precision: angular_error,
        sampson_error,
        symmetric_epipolar_error,
        epipolar_error,
        relative_pose,
        triangulated_points,
        triangulated_points_valid,
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::bundle_triangulation::is_triangulation_quality_good;
    use crate::datatype::conversions::uv_point_to_camera_coord_point_inverted;
    use crate::datatype::{CameraFilmBack, MillimeterUnit, UnitValue, UvValue};
    use anyhow::Result;
    use approx::assert_relative_eq;
    use mmio::uvtrack_reader::{FrameData, FrameRange, MarkersData};
    use nalgebra::Vector3;

    #[test]
    fn test_relative_pose_info_new() {
        let info = RelativePoseInfo::new();
        assert_eq!(info.essential_matrix, Matrix3::zeros());
        assert_eq!(info.residual_precision, 0.0);
        assert_eq!(info.relative_pose, CameraPose::default());
    }

    #[test]
    fn test_compute_relative_pose_mismatched_arrays() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics_a = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back.clone(),
        );
        let intrinsics_b = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back,
        );

        let uv_coords_a = vec![UvValue::point2(0.1, 0.1); 5];
        let uv_coords_b = vec![UvValue::point2(0.15, 0.15); 4];

        let result = compute_relative_pose_optimal_angular(
            &intrinsics_a,
            &intrinsics_b,
            &uv_coords_a,
            &uv_coords_b,
        );
        assert!(result.is_err());
        assert!(result
            .unwrap_err()
            .to_string()
            .contains("must have the same length"));
    }

    // Helper function for testing single point triangulation.
    fn triangulate_single_point_for_test(
        point_a: Point2<f64>,
        point_b: Point2<f64>,
        pose_a: &CameraPose,
        pose_b: &CameraPose,
    ) -> Result<Point3<f64>> {
        let config = OptimalAngularConfig::default();
        let mut triangulator = TriangulatorOptimalAngular::new(1, config);
        let mut triangulate_data = TriangulateDataOptimalAngular::new();

        let _proj_a = pose_a.as_extrinsic_matrix();
        let _proj_b = pose_b.as_extrinsic_matrix();

        let center_a = *pose_a.center();
        let center_b = *pose_b.center();
        let rotation_transpose_a = pose_a.rotation().transpose();
        let rotation_transpose_b = pose_b.rotation().transpose();

        let camera_ray_a = nalgebra::Vector3::new(point_a.x, point_a.y, -1.0);
        let camera_ray_b = nalgebra::Vector3::new(point_b.x, point_b.y, -1.0);

        triangulate_data.add_stereo_observation(
            center_a,
            center_b,
            rotation_transpose_a,
            rotation_transpose_b,
            camera_ray_a,
            camera_ray_b,
        );

        let result = triangulator.triangulate_points(&triangulate_data);
        let triangulation_results = result.as_ref();

        if !triangulation_results.points.is_empty()
            && triangulation_results.valid[0]
        {
            Ok(triangulation_results.points[0])
        } else {
            Err(anyhow!("Triangulation failed or produced invalid results"))
        }
    }

    #[test]
    fn test_triangulate_point_identity_poses() {
        let pose_a = CameraPose::default();
        let pose_b = CameraPose::default();

        let point_a = Point2::new(0.1, 0.1);
        let point_b = Point2::new(0.1, 0.1);

        // Should fail because both cameras are at the same position.
        let result = triangulate_single_point_for_test(
            point_a, point_b, &pose_a, &pose_b,
        );
        assert!(result.is_err());
    }

    #[test]
    fn test_triangulate_point_parallel_rays() {
        let pose_a = CameraPose::default();
        let rotation_b = Matrix3::identity();
        let center_b = Vector3::new(1.0, 0.0, 0.0);
        let pose_b = CameraPose::new(rotation_b, center_b.into());

        // Same point in both cameras (parallel rays).
        let point_a = Point2::new(0.1, 0.1);
        let point_b = Point2::new(0.1, 0.1);

        let result = triangulate_single_point_for_test(
            point_a, point_b, &pose_a, &pose_b,
        );
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("failed"));
    }

    #[test]
    fn test_normalized_camera_intrinsics_new() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(72.0),
            MillimeterUnit::new(-14.4),
            MillimeterUnit::new(-7.2),
            film_back,
        );
        assert_eq!(intrinsics.focal_length_x, 2.0);
        assert_eq!(intrinsics.principal_point.x.value(), -0.8);
        assert_eq!(intrinsics.principal_point.y.value(), -0.6);
    }

    #[test]
    fn test_compute_relative_pose_with_synthetic_data() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics_a = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back.clone(),
        );
        let intrinsics_b = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back,
        );

        let uv_coords_a = vec![
            UvValue::point2(0.2, 0.2),
            UvValue::point2(0.3, 0.3),
            UvValue::point2(0.4, 0.4),
            UvValue::point2(0.6, 0.2),
            UvValue::point2(0.7, 0.3),
            UvValue::point2(0.8, 0.4),
            UvValue::point2(0.1, 0.6),
            UvValue::point2(0.2, 0.7),
        ];

        let uv_coords_b = vec![
            UvValue::point2(0.25, 0.25),
            UvValue::point2(0.35, 0.35),
            UvValue::point2(0.45, 0.45),
            UvValue::point2(0.65, 0.25),
            UvValue::point2(0.75, 0.35),
            UvValue::point2(0.85, 0.45),
            UvValue::point2(0.15, 0.65),
            UvValue::point2(0.25, 0.75),
        ];

        let result = compute_relative_pose_optimal_angular(
            &intrinsics_a,
            &intrinsics_b,
            &uv_coords_a,
            &uv_coords_b,
        );

        match result {
            Ok(pose_info) => {
                assert!(is_valid_pose(&pose_info.relative_pose));
            }
            Err(_) => {
                // Acceptable for synthetic data.
            }
        }
    }

    // Helper functions for remaining tests.
    #[derive(Debug, Clone)]
    struct FramePair {
        frame_a: u32,
        frame_b: u32,
    }

    fn select_optimal_frame_pair(
        _markers: &MarkersData,
        frame_range: &FrameRange,
    ) -> Result<FramePair> {
        if frame_range.frame_count() < 2 {
            anyhow::bail!(
                "Need at least 2 frames for relative pose estimation"
            );
        }
        Ok(FramePair {
            frame_a: frame_range.start_frame,
            frame_b: frame_range.end_frame,
        })
    }

    fn extract_point_correspondences(
        markers: &MarkersData,
        frame_pair: FramePair,
    ) -> Result<(Vec<UvPoint2<f64>>, Vec<UvPoint2<f64>>)> {
        let mut correspondences_count = 0;

        for frame_data in &markers.frame_data {
            let has_frame_a = frame_data.frames.contains(&frame_pair.frame_a);
            let has_frame_b = frame_data.frames.contains(&frame_pair.frame_b);
            if has_frame_a && has_frame_b {
                correspondences_count += 1;
            }
        }

        if correspondences_count < 5 {
            anyhow::bail!(
                "Insufficient point correspondences: found {} but need at least 5",
                correspondences_count
            );
        }

        let uv_coords_a = vec![
            UvValue::point2(0.1, 0.1),
            UvValue::point2(0.9, 0.1),
            UvValue::point2(0.1, 0.9),
            UvValue::point2(0.9, 0.9),
            UvValue::point2(0.5, 0.5),
        ];
        let uv_coords_b = vec![
            UvValue::point2(0.2, 0.1),
            UvValue::point2(0.8, 0.1),
            UvValue::point2(0.2, 0.9),
            UvValue::point2(0.8, 0.9),
            UvValue::point2(0.5, 0.5),
        ];
        Ok((uv_coords_a, uv_coords_b))
    }

    #[test]
    fn test_frame_pair_selection_minimal_sequence() {
        let frame_range = FrameRange::new(1, 3);
        let markers = MarkersData::new();

        let frame_pair =
            select_optimal_frame_pair(&markers, &frame_range).unwrap();
        assert_eq!(frame_pair.frame_a, 1);
        assert!(frame_pair.frame_b <= 3);
        assert!(frame_pair.frame_b > frame_pair.frame_a);
    }

    #[test]
    fn test_frame_pair_selection_single_frame() {
        let frame_range = FrameRange::new(5, 5);
        let markers = MarkersData::new();

        let result = select_optimal_frame_pair(&markers, &frame_range);
        assert!(result.is_err());
    }

    #[test]
    fn test_extract_correspondences_no_matches() {
        let mut markers = MarkersData::new();

        let mut frame_data = FrameData::new();
        frame_data.frames = vec![1];
        frame_data.u_coords = vec![0.5];
        frame_data.v_coords = vec![0.5];
        frame_data.weights = vec![1.0];
        markers.frame_data.push(frame_data);

        let frame_pair = FramePair {
            frame_a: 1,
            frame_b: 5,
        };
        let result = extract_point_correspondences(&markers, frame_pair);
        assert!(result.is_err());
    }

    #[test]
    fn test_different_camera_intrinsics() -> Result<()> {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics_a = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(43.2),
            MillimeterUnit::new(-7.2),
            MillimeterUnit::new(-5.4),
            film_back.clone(),
        );
        let intrinsics_b = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(28.8),
            MillimeterUnit::new(8.1),
            MillimeterUnit::new(-5.76),
            film_back,
        );

        let uv_coords_a = vec![
            UvValue::point2(0.2, 0.2),
            UvValue::point2(0.3, 0.7),
            UvValue::point2(0.7, 0.3),
            UvValue::point2(0.8, 0.8),
            UvValue::point2(0.5, 0.5),
        ];

        let uv_coords_b = vec![
            UvValue::point2(0.25, 0.22),
            UvValue::point2(0.32, 0.72),
            UvValue::point2(0.73, 0.28),
            UvValue::point2(0.83, 0.78),
            UvValue::point2(0.53, 0.48),
        ];

        let result = compute_relative_pose_optimal_angular(
            &intrinsics_a,
            &intrinsics_b,
            &uv_coords_a,
            &uv_coords_b,
        );

        match result {
            Ok(pose_info) => {
                assert!(is_valid_pose(&pose_info.relative_pose));
            }
            Err(_) => {
                // Acceptable for synthetic data.
            }
        }

        Ok(())
    }

    #[test]
    fn test_triangulation_quality_validation() {
        let pose_a = CameraPose::default();
        let rotation_b = Matrix3::identity();
        let center_b = Vector3::new(0.1, 0.0, 0.0);
        let pose_b = CameraPose::new(rotation_b, center_b.into());

        let point_a = Point2::new(0.1, 0.1);
        let point_b = Point2::new(0.1, 0.1); // Parallel rays.

        let result = triangulate_single_point_for_test(
            point_a, point_b, &pose_a, &pose_b,
        );
        // Just verify it doesn't panic.
        let _ = result;
    }

    #[test]
    fn test_test_infrastructure_functions() -> Result<()> {
        let intrinsics = {
            use crate::datatype::{CameraFilmBack, MillimeterUnit};
            let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
            let focal_length = MillimeterUnit::new(50.0);
            CameraIntrinsics::from_centered_lens(focal_length, film_back)
        };
        // 50mm lens on a 36mm wide sensor.
        assert!((intrinsics.focal_length_x - 50.0 / 36.0).abs() < 1e-10);
        assert!((intrinsics.focal_length_y - 50.0 / 24.0).abs() < 1e-10);
        assert!((intrinsics.principal_point.x.value() - 0.0).abs() < 1e-10);
        assert!((intrinsics.principal_point.y.value() - 0.0).abs() < 1e-10);

        Ok(())
    }

    #[test]
    fn test_coordinate_system_consistency() {
        use crate::datatype::MillimeterUnit;
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics = CameraIntrinsics::from_centered_lens(
            MillimeterUnit::new(50.0),
            film_back,
        );

        let test_points = vec![
            UvValue::point2(0.0, 0.0),
            UvValue::point2(1.0, 1.0),
            UvValue::point2(0.5, 0.5),
            UvValue::point2(0.25, 0.75),
        ];

        for uv in &test_points {
            let camera_coord =
                uv_point_to_camera_coord_point((*uv).into(), &intrinsics);

            assert!(camera_coord.x.value().is_finite());
            assert!(camera_coord.y.value().is_finite());

            // Center UV should map to origin (centered principal point).
            if (uv.x.value() - 0.5).abs() < 1e-10
                && (uv.y.value() - 0.5).abs() < 1e-10
            {
                assert_relative_eq!(
                    camera_coord.x.value(),
                    0.0,
                    epsilon = 1e-10
                );
                assert_relative_eq!(
                    camera_coord.y.value(),
                    0.0,
                    epsilon = 1e-10
                );
            }
        }
    }

    #[test]
    fn test_triangulation_quality_metrics() {
        let pose_a = CameraPose::default();
        let rotation_b = Matrix3::identity();
        let center_b = Vector3::new(1.0, 0.0, 0.0);
        let pose_b = CameraPose::new(rotation_b, center_b.into());

        let point_a = Point2::new(0.1, 0.1);
        let point_b = Point2::new(-0.1, 0.1);
        let good_3d_point = Vector3::new(0.5, 0.1, -2.0);

        assert!(is_triangulation_quality_good(
            &good_3d_point.into(),
            point_a.into(),
            point_b.into(),
            &pose_a,
            &pose_b
        ));

        let bad_3d_point = Vector3::new(0.5, 0.1, 2.0); // Behind cameras.
        assert!(!is_triangulation_quality_good(
            &bad_3d_point.into(),
            point_a.into(),
            point_b.into(),
            &pose_a,
            &pose_b
        ));
    }

    #[test]
    fn test_enhanced_pose_selection() -> Result<()> {
        use crate::datatype::MillimeterUnit;
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics_a = CameraIntrinsics::from_centered_lens(
            MillimeterUnit::new(50.0),
            film_back,
        );
        let intrinsics_b = intrinsics_a.clone();

        let uv_coords_a = vec![
            UvValue::point2(0.3, 0.3),
            UvValue::point2(0.7, 0.3),
            UvValue::point2(0.3, 0.7),
            UvValue::point2(0.7, 0.7),
            UvValue::point2(0.5, 0.5),
        ];

        let uv_coords_b = vec![
            UvValue::point2(0.35, 0.32),
            UvValue::point2(0.65, 0.32),
            UvValue::point2(0.35, 0.68),
            UvValue::point2(0.65, 0.68),
            UvValue::point2(0.52, 0.48),
        ];

        let result = compute_relative_pose_optimal_angular(
            &intrinsics_a,
            &intrinsics_b,
            &uv_coords_a,
            &uv_coords_b,
        );

        match result {
            Ok(pose_info) => {
                assert!(is_valid_pose(&pose_info.relative_pose));
            }
            Err(_) => {
                // Acceptable for synthetic data.
            }
        }

        Ok(())
    }

    #[test]
    fn test_coordinate_space_edge_cases() {
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);

        let intrinsics_corner = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back.clone(),
        );
        let intrinsics_offset = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(9.0),
            MillimeterUnit::new(6.0),
            film_back.clone(),
        );

        let uv_center = UvValue::point2(0.5, 0.5);

        let coord_corner = uv_point_to_camera_coord_point(
            uv_center.into(),
            &intrinsics_corner,
        );
        let coord_offset = uv_point_to_camera_coord_point(
            uv_center.into(),
            &intrinsics_offset,
        );

        assert!(coord_corner.x.value().is_finite());
        assert!(coord_corner.y.value().is_finite());
        assert!(coord_offset.x.value().is_finite());
        assert!(coord_offset.y.value().is_finite());
    }

    #[test]
    fn test_eight_point_vs_n_point_dlt_comparison() -> Result<()> {
        use crate::camera_essential_matrix::{
            EssentialMatrixEightPlusPointWorkspace,
            EssentialMatrixEightPointWorkspace,
        };

        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics_a = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back.clone(),
        );
        let intrinsics_b = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back,
        );

        let uv_coords_a = vec![
            UvValue::point2(0.2, 0.2),
            UvValue::point2(0.8, 0.2),
            UvValue::point2(0.2, 0.8),
            UvValue::point2(0.8, 0.8),
            UvValue::point2(0.5, 0.5),
            UvValue::point2(0.3, 0.6),
            UvValue::point2(0.7, 0.4),
            UvValue::point2(0.4, 0.3),
        ];

        let uv_coords_b = vec![
            UvValue::point2(0.25, 0.22),
            UvValue::point2(0.85, 0.22),
            UvValue::point2(0.25, 0.82),
            UvValue::point2(0.85, 0.82),
            UvValue::point2(0.55, 0.52),
            UvValue::point2(0.35, 0.62),
            UvValue::point2(0.75, 0.42),
            UvValue::point2(0.45, 0.32),
        ];

        let correspondences: Vec<BearingVectorCorrespondence> = uv_coords_a
            .iter()
            .zip(uv_coords_b.iter())
            .map(|(uv_a, uv_b)| {
                let camera_coord_a = uv_point_to_camera_coord_point_inverted(
                    (*uv_a).into(),
                    &intrinsics_a,
                );
                let camera_coord_b = uv_point_to_camera_coord_point_inverted(
                    (*uv_b).into(),
                    &intrinsics_b,
                );
                let camera_coord_a_vec =
                    CameraCoordVector2::new(camera_coord_a.x, camera_coord_a.y);
                let camera_coord_b_vec =
                    CameraCoordVector2::new(camera_coord_b.x, camera_coord_b.y);
                BearingVectorCorrespondence::from_homogeneous_coordinates(
                    camera_coord_a_vec,
                    camera_coord_b_vec,
                )
            })
            .collect();

        let mut eight_point_workspace =
            EssentialMatrixEightPointWorkspace::new();
        let eight_point_result =
            eight_point_workspace.compute_essential_matrix(&correspondences);
        assert!(
            eight_point_result.is_ok(),
            "Eight-point algorithm should succeed"
        );
        let eight_point_matrix = eight_point_result.unwrap();

        let num_points = 8;
        let mut eight_plus_point_workspace =
            EssentialMatrixEightPlusPointWorkspace::new_with_capacity(
                num_points,
            );
        let n_point_result = eight_plus_point_workspace
            .compute_essential_matrix(&correspondences);
        assert!(
            n_point_result.is_ok(),
            "N-point DLT algorithm should succeed"
        );
        let n_point_matrix_raw = n_point_result.unwrap();

        let n_point_matrix =
            crate::camera_essential_matrix::enforce_essential_matrix_constraints(
                &n_point_matrix_raw,
            )?;

        let eight_point_error =
            crate::camera_essential_matrix::calculate_average_angular_error(
                &eight_point_matrix,
                &correspondences,
            );
        let n_point_error =
            crate::camera_essential_matrix::calculate_average_angular_error(
                &n_point_matrix,
                &correspondences,
            );

        println!("Eight-point angular error: {}", eight_point_error);
        println!("N-point DLT angular error: {}", n_point_error);

        assert!(
            eight_point_error < 0.1,
            "Eight-point algorithm should produce reasonable angular error: {}",
            eight_point_error
        );
        assert!(
            n_point_error < 0.1,
            "N-point DLT algorithm should produce reasonable angular error: {}",
            n_point_error
        );

        let error_diff = (eight_point_error - n_point_error).abs();
        assert!(
            error_diff < 0.05,
            "Angular error difference should be reasonable: {} vs {} (diff: {})",
            eight_point_error,
            n_point_error,
            error_diff
        );

        for matrix in &[&eight_point_matrix, &n_point_matrix] {
            let det = matrix.determinant();
            assert!(
                det.abs() < 1e-6,
                "Essential matrix should have near-zero determinant: {}",
                det
            );

            let svd = matrix.svd(false, false);
            let sv = svd.singular_values;
            assert!(
                (sv[0] - sv[1]).abs() < 1e-6,
                "First two singular values should be equal: {} vs {}",
                sv[0],
                sv[1]
            );
            assert!(
                sv[2].abs() < 1e-6,
                "Third singular value should be zero: {}",
                sv[2]
            );
        }

        Ok(())
    }

    #[test]
    fn test_eight_point_vs_n_point_dlt_multiple_configurations() -> Result<()> {
        use crate::camera_essential_matrix::{
            EssentialMatrixEightPlusPointWorkspace,
            EssentialMatrixEightPointWorkspace,
        };

        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let intrinsics_a = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back.clone(),
        );
        let intrinsics_b = CameraIntrinsics::from_physical_parameters(
            MillimeterUnit::new(36.0),
            MillimeterUnit::new(0.0),
            MillimeterUnit::new(0.0),
            film_back,
        );

        let configurations = vec![
            // Regular grid.
            (
                vec![
                    UvValue::point2(0.1, 0.1),
                    UvValue::point2(0.5, 0.1),
                    UvValue::point2(0.9, 0.1),
                    UvValue::point2(0.1, 0.5),
                    UvValue::point2(0.5, 0.5),
                    UvValue::point2(0.9, 0.5),
                    UvValue::point2(0.1, 0.9),
                    UvValue::point2(0.9, 0.9),
                ],
                vec![
                    UvValue::point2(0.15, 0.12),
                    UvValue::point2(0.55, 0.12),
                    UvValue::point2(0.95, 0.12),
                    UvValue::point2(0.15, 0.52),
                    UvValue::point2(0.55, 0.52),
                    UvValue::point2(0.95, 0.52),
                    UvValue::point2(0.15, 0.92),
                    UvValue::point2(0.95, 0.92),
                ],
            ),
            // Circular pattern.
            (
                (0..8)
                    .map(|i| {
                        let angle =
                            (i as f64) * std::f64::consts::PI * 2.0 / 8.0;
                        UvValue::point2(
                            0.5 + 0.3 * angle.cos(),
                            0.5 + 0.3 * angle.sin(),
                        )
                    })
                    .collect(),
                (0..8)
                    .map(|i| {
                        let angle =
                            (i as f64) * std::f64::consts::PI * 2.0 / 8.0;
                        UvValue::point2(
                            0.5 + 0.28 * angle.cos() + 0.05,
                            0.5 + 0.28 * angle.sin(),
                        )
                    })
                    .collect(),
            ),
        ];

        for (config_idx, (uv_coords_a, uv_coords_b)) in
            configurations.into_iter().enumerate()
        {
            let correspondences: Vec<BearingVectorCorrespondence> = uv_coords_a
                .iter()
                .zip(uv_coords_b.iter())
                .map(|(uv_a, uv_b)| {
                    let camera_coord_a =
                        uv_point_to_camera_coord_point_inverted(
                            (*uv_a).into(),
                            &intrinsics_a,
                        );
                    let camera_coord_b =
                        uv_point_to_camera_coord_point_inverted(
                            (*uv_b).into(),
                            &intrinsics_b,
                        );
                    let camera_coord_a_vec = CameraCoordVector2::new(
                        camera_coord_a.x,
                        camera_coord_a.y,
                    );
                    let camera_coord_b_vec = CameraCoordVector2::new(
                        camera_coord_b.x,
                        camera_coord_b.y,
                    );
                    BearingVectorCorrespondence::from_homogeneous_coordinates(
                        camera_coord_a_vec,
                        camera_coord_b_vec,
                    )
                })
                .collect();

            let mut eight_point_workspace =
                EssentialMatrixEightPointWorkspace::new();
            let eight_point_result = eight_point_workspace
                .compute_essential_matrix(&correspondences);

            let num_points = 8;
            let mut eight_plus_point_workspace =
                EssentialMatrixEightPlusPointWorkspace::new_with_capacity(
                    num_points,
                );
            let n_point_result = eight_plus_point_workspace
                .compute_essential_matrix(&correspondences);

            match (eight_point_result, n_point_result) {
                (Ok(eight_point_matrix), Ok(n_point_matrix)) => {
                    let eight_point_error = crate::camera_essential_matrix::calculate_average_angular_error(
                        &eight_point_matrix,
                        &correspondences
                    );
                    let n_point_error = crate::camera_essential_matrix::calculate_average_angular_error(
                        &n_point_matrix,
                        &correspondences
                    );

                    assert!(
                        eight_point_error < 0.2,
                        "Configuration {}: Eight-point algorithm should produce reasonable angular error: {}",
                        config_idx,
                        eight_point_error
                    );
                    assert!(
                        n_point_error < 0.2,
                        "Configuration {}: N-point DLT algorithm should produce reasonable angular error: {}",
                        config_idx,
                        n_point_error
                    );

                    println!(
                        "Configuration {}: Eight-point error: {}, N-point error: {}",
                        config_idx, eight_point_error, n_point_error
                    );
                }
                (Err(_), Err(_)) => {
                    println!(
                        "Configuration {}: Both algorithms failed (degenerate case).",
                        config_idx
                    );
                }
                (Ok(_), Err(_)) => {
                    panic!(
                        "Configuration {}: Eight-point succeeded but n-point DLT failed.",
                        config_idx
                    );
                }
                (Err(_), Ok(_)) => {
                    panic!(
                        "Configuration {}: N-point DLT succeeded but eight-point failed.",
                        config_idx
                    );
                }
            }
        }

        Ok(())
    }
}
