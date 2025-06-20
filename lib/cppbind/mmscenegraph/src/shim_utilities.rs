//
// Copyright (C) 2024, 2025 David Cattermole.
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

pub fn copy_vec_xy_to_x_y(
    values_xy: &[(CoreReal, CoreReal)],
    out_values_x: &mut Vec<CoreReal>,
    out_values_y: &mut Vec<CoreReal>,
) {
    let new_capacity_x =
        values_xy.len().saturating_sub(out_values_x.capacity());
    let new_capacity_y =
        values_xy.len().saturating_sub(out_values_y.capacity());
    out_values_x.reserve_exact(new_capacity_x);
    out_values_y.reserve_exact(new_capacity_y);
    out_values_x.clear();
    out_values_y.clear();

    for value in values_xy.iter() {
        let x = value.0;
        let y = value.1;
        out_values_x.push(x);
        out_values_y.push(y);
    }
}
