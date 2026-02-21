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

//! Bundle adjustment for Structure from Motion (SfM).
//!
//! Simultaneously refines camera poses and 3D point positions to minimize
//! reprojection error.
//!
//! ## Coordinate System
//!
//! Follows Autodesk Maya conventions:
//! - Right-hand coordinate system.
//! - +Y axis is world-up.
//! - Camera looks down -Z axis.
//!
//! ## Camera Parameterization
//!
//! - **Rotation**: Quaternion vector [qx, qy, qz] (3 params). The w component
//!   is reconstructed as `w = sqrt(1 - qx^2 - qy^2 - qz^2)`.
//! - **Translation**: 3D vector [tx, ty, tz] (3 params).
//! - **3D Points**: Cartesian coordinates [x, y, z] (3 params each).
//!
//! ## Solvers
//!
//! Two solver implementations are available:
//!
//! - **Dense** (Levenberg-Marquardt): best for small problems (< 50 cameras,
//!   < 500 points) or very dense observations.
//! - **Sparse** (Schur complement): recommended for larger problems; much
//!   faster when each point is seen by only a few cameras.

mod general_problem;
mod maths;
mod single_camera_problem;
mod single_point_problem;
mod two_camera_problem;

pub use crate::bundle_adjust::general_problem::GeneralBundleAdjustmentProblem;
pub use crate::bundle_adjust::maths::{
    camera_pose_to_quaternion_vector_and_translation, cartesian_to_spherical,
    ensure_orthogonal_rotation, project_point_generic,
    quaternion_from_vector_f64, quaternion_full_to_rotation_matrix,
    quaternion_multiply, quaternion_vector_and_translation_to_camera_pose,
    quaternion_vector_to_rotation_matrix,
    rotation_matrix_and_translation_to_camera_pose,
    rotation_matrix_to_full_quaternion, rotation_matrix_to_quaternion_vector,
    spherical_to_cartesian,
};
pub use crate::bundle_adjust::single_camera_problem::SingleCameraBAProblem;
pub use crate::bundle_adjust::single_point_problem::SinglePointBAProblem;
pub use crate::bundle_adjust::two_camera_problem::TwoCameraBAProblem;
