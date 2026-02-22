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

//! Camera Pose-from-Points (PnP) method implementations and selection.

use anyhow::Result;
use nalgebra::Point3;

use crate::camera_pose_from_bundles::compute_sqpnp_poses;
use crate::datatype::camera_pose::CameraPose;
use crate::datatype::{
    CameraIntrinsics, CameraToSceneCorrespondence, UnitValue,
};

/// Compile-time flag to enable verbose debug output.
const DEBUG: bool = false;

/// Result from a PnP estimation.
#[derive(Clone, Debug)]
pub struct PnPMethodResult {
    /// The computed camera pose.
    pub pose: CameraPose,
    /// Mean reprojection error in normalised camera coordinates.
    pub reprojection_error: f64,
    /// Number of correspondences used.
    pub num_correspondences: usize,
}

/// Compute the mean reprojection error for a pose.
///
/// Each 3D point is projected into the camera and compared against
/// the observed 2D position in normalised camera coordinates.
fn calculate_pose_reprojection_error(
    pose: &CameraPose,
    correspondences: &[CameraToSceneCorrespondence<f64>],
    _camera_intrinsics: &CameraIntrinsics,
) -> f64 {
    let mut total_distance = 0.0;
    let mut num_points = 0;

    for corr in correspondences {
        let scene_point = Point3::new(
            corr.scene_point.coords.x.value(),
            corr.scene_point.coords.y.value(),
            corr.scene_point.coords.z.value(),
        );

        let camera_point_3d = pose.apply_transform(&scene_point);

        // Skip points behind the camera (Maya: -Z is forward).
        if camera_point_3d.z >= 0.0 {
            continue;
        }

        // Perspective-divide to get normalised camera coordinates.
        let projected_x_norm = camera_point_3d.x / camera_point_3d.z.abs();
        let projected_y_norm = camera_point_3d.y / camera_point_3d.z.abs();

        let observed_x = corr.camera_point.coords.x.value();
        let observed_y = corr.camera_point.coords.y.value();

        let error_x = projected_x_norm - observed_x;
        let error_y = projected_y_norm - observed_y;
        let distance = (error_x * error_x + error_y * error_y).sqrt();

        total_distance += distance;
        num_points += 1;
    }

    if num_points > 0 {
        total_distance / num_points as f64
    } else {
        f64::INFINITY
    }
}

/// Count how many 3D points project behind the camera for a given pose.
///
/// A valid pose should have zero points behind the camera.
fn count_points_behind_camera(
    pose: &CameraPose,
    correspondences: &[CameraToSceneCorrespondence<f64>],
) -> usize {
    let mut behind_count = 0;

    for corr in correspondences {
        let scene_coords = Point3::new(
            corr.scene_point.coords.x.value(),
            corr.scene_point.coords.y.value(),
            corr.scene_point.coords.z.value(),
        );
        let camera_point = pose.apply_transform(&scene_coords);

        // Point is behind camera when z >= 0.0 (Maya: -Z is forward).
        if camera_point.z >= 0.0 {
            behind_count += 1;
        }
    }

    behind_count
}

/// Estimate camera pose from 2D-3D correspondences using SQPnP.
///
/// Returns the best-scoring pose, or `None` if all candidates fail
/// the cheirality check (i.e. have points behind the camera).
pub fn compute_camera_pose_with_method(
    correspondences: &[CameraToSceneCorrespondence<f64>],
    camera_intrinsics: &CameraIntrinsics,
) -> Result<Option<PnPMethodResult>> {
    let num_correspondences = correspondences.len();

    if num_correspondences < 3 {
        mm_debug_eprintln!(
            "      SQPnP: insufficient points ({} < 3)",
            num_correspondences
        );
        return Ok(None);
    }

    match compute_sqpnp_poses(correspondences) {
        Ok(poses) if !poses.is_empty() => {
            // SQPnP may return multiple candidates; pick the one with
            // the lowest reprojection error that passes cheirality.
            let mut best_result: Option<PnPMethodResult> = None;
            let mut best_error = f64::INFINITY;

            for pose in poses {
                let behind_count =
                    count_points_behind_camera(&pose, correspondences);
                if behind_count > 0 {
                    continue;
                }

                let error = calculate_pose_reprojection_error(
                    &pose,
                    correspondences,
                    camera_intrinsics,
                );

                if error < best_error {
                    best_error = error;
                    best_result = Some(PnPMethodResult {
                        pose,
                        reprojection_error: error,
                        num_correspondences,
                    });
                }
            }

            if DEBUG {
                if let Some(ref result) = best_result {
                    mm_debug_eprintln!(
                        "      SQPnP: success, error={:.6}",
                        result.reprojection_error
                    );
                } else {
                    mm_debug_eprintln!(
                        "      SQPnP: all solutions failed cheirality"
                    );
                }
            }

            Ok(best_result)
        }
        Ok(_) => {
            mm_debug_eprintln!("      SQPnP: returned empty solutions");
            Ok(None)
        }
        Err(e) => {
            mm_debug_eprintln!("      SQPnP: failed with error: {:?}", e);
            Ok(None)
        }
    }
}
