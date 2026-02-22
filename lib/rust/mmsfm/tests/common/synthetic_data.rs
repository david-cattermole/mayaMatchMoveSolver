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

use nalgebra::Matrix4;

use mmsfm_rust::datatype::UvPointCorrespondence;

/// Returns 4 UV point correspondences with no transformation applied.
pub fn create_identity_correspondences() -> Vec<UvPointCorrespondence<f64>> {
    vec![
        UvPointCorrespondence::new(0.0, 0.0, 0.0, 0.0),
        UvPointCorrespondence::new(1.0, 0.0, 1.0, 0.0),
        UvPointCorrespondence::new(0.0, 1.0, 0.0, 1.0),
        UvPointCorrespondence::new(1.0, 1.0, 1.0, 1.0),
    ]
}

/// Returns 4 UV point correspondences translated by the given offset.
pub fn create_translation_correspondences(
    offset_x: f64,
    offset_y: f64,
) -> Vec<UvPointCorrespondence<f64>> {
    vec![
        UvPointCorrespondence::new(0.0, 0.0, offset_x, offset_y),
        UvPointCorrespondence::new(1.0, 0.0, 1.0 + offset_x, offset_y),
        UvPointCorrespondence::new(0.0, 1.0, offset_x, 1.0 + offset_y),
        UvPointCorrespondence::new(1.0, 1.0, 1.0 + offset_x, 1.0 + offset_y),
    ]
}

/// Returns 4 UV point correspondences scaled by the given factor around the origin.
pub fn create_scale_correspondences(
    scale_factor: f64,
) -> Vec<UvPointCorrespondence<f64>> {
    vec![
        UvPointCorrespondence::new(0.0, 0.0, 0.0, 0.0),
        UvPointCorrespondence::new(1.0, 0.0, scale_factor, 0.0),
        UvPointCorrespondence::new(0.0, 1.0, 0.0, scale_factor),
        UvPointCorrespondence::new(1.0, 1.0, scale_factor, scale_factor),
    ]
}

/// Returns 4 UV point correspondences rotated 90 degrees counter-clockwise.
pub fn create_rotation_90_correspondences() -> Vec<UvPointCorrespondence<f64>> {
    vec![
        UvPointCorrespondence::new(1.0, 0.0, 0.0, 1.0), // (1,0) -> (0,1)
        UvPointCorrespondence::new(0.0, 1.0, -1.0, 0.0), // (0,1) -> (-1,0)
        UvPointCorrespondence::new(-1.0, 0.0, 0.0, -1.0), // (-1,0) -> (0,-1)
        UvPointCorrespondence::new(0.0, -1.0, 1.0, 0.0), // (0,-1) -> (1,0)
    ]
}

/// Returns a 4x4 translation matrix.
pub fn create_translation_matrix4(x: f64, y: f64, z: f64) -> Matrix4<f64> {
    Matrix4::new(
        1.0, 0.0, 0.0, x, 0.0, 1.0, 0.0, y, 0.0, 0.0, 1.0, z, 0.0, 0.0, 0.0,
        1.0,
    )
}
