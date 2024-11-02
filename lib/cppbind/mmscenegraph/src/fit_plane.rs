//
// Copyright (C) 2024 David Cattermole.
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

use mmscenegraph_rust::constant::Real as CoreReal;
use mmscenegraph_rust::math::fit_plane::fit_plane_to_points as core_fit_plane_to_points;

pub fn shim_fit_plane_to_points(
    points_xyz: &[CoreReal],
    out_position_x: &mut CoreReal,
    out_position_y: &mut CoreReal,
    out_position_z: &mut CoreReal,
    out_normal_x: &mut CoreReal,
    out_normal_y: &mut CoreReal,
    out_normal_z: &mut CoreReal,
    out_rms_error: &mut CoreReal,
) -> bool {
    let plane_fit = core_fit_plane_to_points(points_xyz);
    match plane_fit {
        Some(value) => {
            *out_position_x = value.position.x;
            *out_position_y = value.position.y;
            *out_position_z = value.position.z;
            *out_normal_x = value.normal.x;
            *out_normal_y = value.normal.y;
            *out_normal_z = value.normal.z;
            *out_rms_error = value.rms_error;
            true
        }
        None => false,
    }
}
