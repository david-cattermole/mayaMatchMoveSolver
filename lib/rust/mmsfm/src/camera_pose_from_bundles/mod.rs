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

// Perspective-N-Points (PnP) solvers.

mod common;
mod sqpnp;

pub use crate::camera_pose_from_bundles::common::{
    calculate_average_reprojection_error, calculate_reprojection_error,
    is_point_in_front_of_camera, projection_matrix_from_krt,
    validate_correspondences, verify_camera_pose_properties, CameraIntrinsics,
    CameraPose, Mat3, Mat34, PnPError, Vec2, Vec3,
};

// Re-export PnP solvers.
pub use crate::camera_pose_from_bundles::sqpnp::compute_sqpnp_poses;
