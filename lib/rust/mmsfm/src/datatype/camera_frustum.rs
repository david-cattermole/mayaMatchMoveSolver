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

//! Camera frustum visualization utility
//!
//! This module provides the `CameraFrustum` type for representing and working with
//! camera viewing frustums in 3D space. Frustums are useful for visualizing camera
//! field-of-view and for various geometric computations.
//!
//! The frustum follows Maya's coordinate system conventions:
//! - Right-hand coordinate system
//! - +Y axis is world-up
//! - Camera looks down -Z axis (negative Z is forward/in front of camera)

use crate::datatype::camera_pose::CameraPose;
use crate::datatype::CameraIntrinsics;
use nalgebra::Point3;
use std::convert::TryInto;

#[derive(Debug, Clone)]
pub struct CameraFrustum {
    pub position: Point3<f64>,
    pub corners: [Point3<f64>; 4], // Four corners of the far plane
}

impl CameraFrustum {
    /// Validate that the frustum follows Maya coordinate conventions
    ///
    /// This function checks that:
    /// - All frustum corners are in front of the camera (negative Z relative to camera center)
    /// - The frustum is properly oriented
    pub fn validate_maya_conventions(&self, pose: &CameraPose) -> bool {
        // Check that all corners are in front of the camera.
        for corner in &self.corners {
            if !pose.is_point_in_front(corner) {
                return false;
            }
        }
        true
    }

    /// Create camera frustum from camera pose and intrinsics.
    ///
    /// This method uses actual camera parameters to calculate proper
    /// frustum geometry.
    ///
    /// # Arguments
    /// * `pose` - Camera pose in world space
    /// * `intrinsics` - Camera intrinsics with film back information
    /// * `frustum_depth` - Depth of the frustum visualization (in world units)
    ///
    /// # Returns
    /// A CameraFrustum with corners calculated from actual FoV and aspect ratio
    pub fn from_camera_intrinsics(
        pose: &CameraPose,
        intrinsics: &CameraIntrinsics,
        frustum_depth: f64,
    ) -> Self {
        let position = *pose.center();

        // Calculate frustum dimensions from actual camera parameters.
        let horizontal_fov = intrinsics.horizontal_fov_radians();
        let vertical_fov = intrinsics.vertical_fov_radians();

        // Calculate half-widths at the frustum depth.
        //
        // Maya coordinate system: negative Z is forward (in front of camera).
        let half_width = frustum_depth * (horizontal_fov * 0.5).tan();
        let half_height = frustum_depth * (vertical_fov * 0.5).tan();

        let corners_camera = [
            Point3::new(-half_width, -half_height, -frustum_depth), // Bottom-left
            Point3::new(half_width, -half_height, -frustum_depth), // Bottom-right
            Point3::new(half_width, half_height, -frustum_depth),  // Top-right
            Point3::new(-half_width, half_height, -frustum_depth), // Top-left
        ];

        // Transform corners to world space.
        let corners: [Point3<f64>; 4] = corners_camera
            .iter()
            .map(|corner| {
                Point3::from(
                    // pose.rotation() is world-to-camera, so we need
                    // its transpose for camera-to-world.
                    pose.rotation().transpose() * corner.coords
                        + position.coords,
                )
            })
            .collect::<Vec<_>>()
            .try_into()
            .unwrap();

        Self { position, corners }
    }

    pub fn get_lines(&self) -> Vec<(Point3<f64>, Point3<f64>)> {
        let mut lines = Vec::new();

        // Lines from camera position to each corner
        for corner in &self.corners {
            lines.push((self.position, *corner));
        }

        // Lines connecting the corners (far plane)
        for i in 0..4 {
            let next = (i + 1) % 4;
            lines.push((self.corners[i], self.corners[next]));
        }

        lines
    }
}
