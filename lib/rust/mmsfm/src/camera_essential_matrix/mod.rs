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

mod common;
mod eight_plus_point;
mod eight_point;
mod five_point;

// Re-export.
pub use crate::camera_essential_matrix::common::{
    calculate_angular_reprojection_error, calculate_average_angular_error,
    calculate_average_epipolar_distance, calculate_average_sampson_error,
    calculate_average_symmetric_epipolar_distance,
    enforce_essential_matrix_constraints, validate_correspondences,
    verify_essential_matrix_properties, CameraEssentialMatrixError,
};
pub use crate::camera_essential_matrix::eight_plus_point::EssentialMatrixEightPlusPointWorkspace;
pub use crate::camera_essential_matrix::eight_point::EssentialMatrixEightPointWorkspace;
pub use crate::camera_essential_matrix::five_point::five_point_relative_pose;
pub use crate::camera_essential_matrix::five_point::EssentialMatrixFivePointWorkspace;
pub use crate::camera_essential_matrix::five_point::{
    find_real_roots_sturm, Polynomial, SturmChain,
};
pub use crate::datatype::BearingVectorCorrespondence;
