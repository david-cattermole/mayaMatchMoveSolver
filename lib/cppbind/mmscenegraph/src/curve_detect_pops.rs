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
use mmscenegraph_rust::curve::detect::pops::detect_curve_pops as core_detect_curve_pops;
use mmscenegraph_rust::curve::detect::pops::filter_curve_pops as core_filter_curve_pops;

pub fn shim_detect_curve_pops(
    x_values: &[CoreReal],
    y_values: &[CoreReal],
    threshold: CoreReal,
    out_x_values: &mut Vec<CoreReal>,
    out_y_values: &mut Vec<CoreReal>,
) -> bool {
    let result = core_detect_curve_pops(&x_values, &y_values, threshold);
    match result {
        Ok(values) => {
            let new_x_capacity =
                values.len().saturating_sub(out_x_values.capacity());
            let new_y_capacity =
                values.len().saturating_sub(out_y_values.capacity());
            out_x_values.reserve_exact(new_x_capacity);
            out_y_values.reserve_exact(new_y_capacity);
            out_x_values.clear();
            out_y_values.clear();

            for value in values.iter() {
                let x = value.0;
                let y = value.1;
                out_x_values.push(x);
                out_y_values.push(y);
            }

            true
        }
        Err(_) => false,
    }
}

pub fn shim_filter_curve_pops(
    x_values: &[CoreReal],
    y_values: &[CoreReal],
    threshold: CoreReal,
    out_x_values: &mut Vec<CoreReal>,
    out_y_values: &mut Vec<CoreReal>,
) -> bool {
    let result = core_filter_curve_pops(&x_values, &y_values, threshold);
    match result {
        Ok(values) => {
            let new_x_capacity =
                values.len().saturating_sub(out_x_values.capacity());
            let new_y_capacity =
                values.len().saturating_sub(out_y_values.capacity());
            out_x_values.reserve_exact(new_x_capacity);
            out_y_values.reserve_exact(new_y_capacity);
            out_x_values.clear();
            out_y_values.clear();

            for value in values.iter() {
                let x = value.0;
                let y = value.1;
                out_x_values.push(x);
                out_y_values.push(y);
            }

            true
        }
        Err(_) => false,
    }
}
