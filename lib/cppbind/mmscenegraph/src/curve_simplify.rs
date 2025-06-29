//
// Copyright (C) 2025 David Cattermole.
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

use crate::cxxbridge::ffi::ControlPointDistribution as BindControlPointDistribution;
use crate::cxxbridge::ffi::Interpolation as BindInterpolation;
use crate::math::bind_to_core_interpolation_method;
use crate::math::bind_to_core_control_point_distribution;
use crate::shim_utilities::copy_vec_xy_to_x_y;

use mmscenegraph_rust::constant::Real as CoreReal;
use mmscenegraph_rust::curve::simplify::simplify as core_simplify;

pub fn shim_curve_simplify(
    values_x: &[CoreReal],
    values_y: &[CoreReal],
    control_point_count: usize,
    distribution: BindControlPointDistribution,
    interpolation_method: BindInterpolation,
    out_values_x: &mut Vec<CoreReal>,
    out_values_y: &mut Vec<CoreReal>,
) -> bool {
    let core_interpolation_method =
        bind_to_core_interpolation_method(interpolation_method);
    let core_distribution =
        bind_to_core_control_point_distribution(distribution);
    let result = core_simplify(
        values_x,
        values_y,
        control_point_count,
        core_distribution,
        core_interpolation_method,
    );
    match result {
        Ok(values) => {
            copy_vec_xy_to_x_y(&values, out_values_x, out_values_y);
            true
        }
        Err(_) => false,
    }
}
