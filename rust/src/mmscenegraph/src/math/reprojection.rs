//
// Copyright (C) 2020, 2021 David Cattermole.
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

use crate::constant::Matrix14;
use crate::constant::Matrix44;

// TODO: Re-write this function to take just a 4x4 matrix, and 3 float
// values. This will reduce the amount of required data, and allow us
// to concatenate matrices and re-use matrix multiplications.
#[inline]
pub fn reproject(
    camera_projection_matrix: Matrix44,
    camera_transform_matrix: Matrix44,
    point: Matrix44,
) -> Matrix14 {
    // Camera World Projection Matrix
    let camera_projection_matrix_inv =
        match camera_projection_matrix.try_inverse() {
            Some(x) => x,
            None => Matrix44::new_scaling(1.0),
        };

    let camera_world_proj_matrix =
        camera_transform_matrix * camera_projection_matrix_inv;

    // Convert to screen-space Homogeneous coordinates
    let screen_point = camera_world_proj_matrix * point;

    Matrix14::new(
        screen_point.index((0, 3)) / screen_point.index((3, 3)),
        screen_point.index((1, 3)) / screen_point.index((3, 3)),
        screen_point.index((2, 3)) / screen_point.index((3, 3)),
        1.0,
    )
}

#[inline]
pub fn reproject_as_normalised_coord(
    camera_projection_matrix: Matrix44,
    camera_transform_matrix: Matrix44,
    point: Matrix44,
) -> Matrix14 {
    let screen_point =
        reproject(camera_projection_matrix, camera_transform_matrix, point);
    Matrix14::new(screen_point.x * 0.5, screen_point.y * 0.5, 0.0, 1.0)
}
