//
// Copyright (C) 2022 David Cattermole.
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

use crate::cxxbridge::ffi::Point3 as ShimPoint3;
use mmscenegraph_rust::constant::Real as CoreReal;
use mmscenegraph_rust::math::line::fit_line_to_points_type2 as core_fit_line_to_points_type2;
use mmscenegraph_rust::math::line_intersect::line_point_intersection as core_line_point_intersection;
use mmscenegraph_rust::math::line_intersect::Point3 as CorePoint3;

pub fn shim_fit_line_to_points_type2(
    x: &[CoreReal],
    y: &[CoreReal],
    out_point_x: &mut CoreReal,
    out_point_y: &mut CoreReal,
    out_slope: &mut CoreReal,
) -> bool {
    core_fit_line_to_points_type2(x, y, out_point_x, out_point_y, out_slope)
}

pub fn shim_line_point_intersection(
    point: ShimPoint3,
    line_a: ShimPoint3,
    line_b: ShimPoint3,
    out_point: &mut ShimPoint3,
) -> bool {
    let point = CorePoint3 {
        x: point.x,
        y: point.y,
        z: point.z,
    };
    let line_a = CorePoint3 {
        x: line_a.x,
        y: line_a.y,
        z: line_a.z,
    };
    let line_b = CorePoint3 {
        x: line_b.x,
        y: line_b.y,
        z: line_b.z,
    };
    let out = core_line_point_intersection(point, line_a, line_b);
    match out {
        Some(value) => {
            out_point.x = value.x;
            out_point.y = value.y;
            out_point.z = value.z;
            true
        }
        None => false,
    }
}
