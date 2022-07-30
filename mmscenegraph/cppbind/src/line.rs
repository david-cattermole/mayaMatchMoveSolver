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

use mmscenegraph_rust::constant::Real as CoreReal;
use mmscenegraph_rust::math::line::fit_line_to_points_type2 as core_fit_line_to_points_type2;

pub fn shim_fit_line_to_points_type2(
    x: &[CoreReal],
    y: &[CoreReal],
    out_point_x: &mut CoreReal,
    out_point_y: &mut CoreReal,
    out_slope: &mut CoreReal,
) -> bool {
    core_fit_line_to_points_type2(x, y, out_point_x, out_point_y, out_slope)
}
