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

use anyhow::{bail, Result};
use nalgebra::Point3;

use mmio::uvtrack_reader::FrameNumber;

use crate::datatype::{camera_pose::CameraPose, BundlePositions, CameraPoses};

/// Compile-time flag to enable verbose debug output.
#[allow(dead_code)]
const DEBUG: bool = false;

/// Transform the reconstruction so the origin frame's camera is at the world
/// origin, then scale so the furthest camera is at distance `scene_scale`.
///
/// Both cameras and bundles are transformed using the same logic:
/// `computed_scale * R_o * (x - C_o)`. This preserves reprojection errors.
/// Returns an error if the origin frame was not solved.
pub fn transform_to_origin_frame(
    origin_frame: FrameNumber,
    scene_scale: f64,
    solved_camera_poses: &mut CameraPoses,
    bundle_positions: &mut BundlePositions,
) -> Result<()> {
    let actual_origin_frame = if solved_camera_poses.contains_key(&origin_frame)
    {
        origin_frame
    } else {
        let min_frame = solved_camera_poses.keys().min().copied();
        match min_frame {
            Some(frame) => {
                mm_debug_eprintln!(
                    "  Warning: Origin frame {} not solved, using first solved frame {} instead.",
                    origin_frame, frame
                );
                frame
            }
            None => {
                bail!("No camera poses were solved, cannot transform to origin frame.");
            }
        }
    };

    // Clone the pose to avoid borrowing issues.
    let origin_pose = solved_camera_poses[&actual_origin_frame].clone();
    let r_origin = origin_pose.rotation();
    let c_origin = origin_pose.center();

    // Step 1: Calculate maximum extent of camera positions after
    // transformation to origin frame.
    let mut max_extent = 0.0_f64;
    for pose in solved_camera_poses.values() {
        let c_i = pose.center();
        // Transform to origin frame (without scaling).
        let transformed_center = r_origin * (c_i.coords - c_origin.coords);
        let distance = transformed_center.norm();
        max_extent = max_extent.max(distance);
    }

    // Step 2: Compute scale factor to achieve desired maximum extent.
    let computed_scale = if max_extent > 1e-10 {
        scene_scale / max_extent
    } else {
        1.0 // If all cameras are at origin, no scaling needed.
    };

    mm_debug_eprintln!(
        "  Max camera extent before scaling: {:.6}, computed scale factor: {:.6}",
        max_extent, computed_scale
    );

    // Step 3: Transform camera poses to new coordinate system with
    // computed scale Mathematical derivation:
    //   - Old: p_cam = R_i * (P - C_i)
    //   - New: p_cam = R_i' * (P' - C_i') where P' = R_o * (P - C_o)
    //   - Solving: R_i' = R_i * R_o^T, C_i' = computed_scale * R_o * (C_i - C_o)
    for pose in solved_camera_poses.values_mut() {
        let r_i = pose.rotation().clone();
        let c_i = pose.center().clone();

        let new_rotation = r_i * r_origin.transpose();

        // Transform to origin frame, then apply computed scale.
        let new_center_transformed = r_origin * (c_i.coords - c_origin.coords);
        let new_center = Point3::from(new_center_transformed * computed_scale);

        *pose = CameraPose::new(new_rotation, new_center);
    }

    // Step 4: Transform bundle positions to new coordinate system.
    //
    // Use SAME explicit logic as cameras (not apply_transform).
    // P_new = computed_scale * R_origin * (P_old - C_origin)
    for point in bundle_positions.values_mut() {
        // Transform to origin frame (explicit computation).
        let transformed = r_origin * (point.coords - c_origin.coords);

        // Apply computed scale uniformly.
        *point = Point3::from(transformed * computed_scale);
    }

    mm_debug_eprintln!(
        "  Transformed to origin frame {} with target max extent {}",
        actual_origin_frame,
        scene_scale
    );

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::camera_residual_error::project_scene_point_3d_to_uv_point_2d;
    use crate::datatype::common::UnitValue;
    use crate::datatype::{
        BundlePositions, CameraFilmBack, CameraIntrinsics, MillimeterUnit,
    };
    use nalgebra::{Matrix3, Point3};

    #[test]
    fn test_transform_preserves_reprojection() {
        // Create test camera poses
        let mut camera_poses = CameraPoses::new();
        let pose1 =
            CameraPose::new(Matrix3::identity(), Point3::new(0.0, 0.0, 10.0));
        let pose2 =
            CameraPose::new(Matrix3::identity(), Point3::new(5.0, 0.0, 10.0));
        camera_poses.insert(1, pose1);
        camera_poses.insert(2, pose2);

        // Create test bundle positions.
        let mut bundle_positions = BundlePositions::new();
        bundle_positions.insert(0, Point3::new(1.0, 2.0, 0.0));
        bundle_positions.insert(1, Point3::new(-1.0, 1.0, -2.0));

        // Setup camera intrinsics.
        let focal_length = MillimeterUnit::new(35.0);
        let film_back = CameraFilmBack::from_millimeters(36.0, 24.0);
        let camera_intrinsics =
            CameraIntrinsics::from_centered_lens(focal_length, film_back);

        // Calculate reprojection BEFORE transform.
        let uv_before = project_scene_point_3d_to_uv_point_2d(
            &bundle_positions[&0],
            &camera_poses[&1],
            &camera_intrinsics,
        )
        .unwrap();

        // Apply transformation.
        let origin_frame = 1;
        let scene_scale = 2.5;
        transform_to_origin_frame(
            origin_frame,
            scene_scale,
            &mut camera_poses,
            &mut bundle_positions,
        )
        .unwrap();

        // Calculate reprojection AFTER transform.
        let uv_after = project_scene_point_3d_to_uv_point_2d(
            &bundle_positions[&0],
            &camera_poses[&1],
            &camera_intrinsics,
        )
        .unwrap();

        // Assert UV coordinates are identical (within numerical precision).
        // UV points use .x and .y fields (not .u and .v).
        const EPSILON: f64 = 1e-10;
        let u_diff = (uv_before.x.value() - uv_after.x.value()).abs();
        let v_diff = (uv_before.y.value() - uv_after.y.value()).abs();

        assert!(
            u_diff < EPSILON,
            "U coordinate changed: before={}, after={}, diff={}",
            uv_before.x.value(),
            uv_after.x.value(),
            u_diff
        );
        assert!(
            v_diff < EPSILON,
            "V coordinate changed: before={}, after={}, diff={}",
            uv_before.y.value(),
            uv_after.y.value(),
            v_diff
        );
    }
}
