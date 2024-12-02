/*
 * Copyright (C) 2024 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 */

#include <mmscenegraph/_cxx.h>
#include <mmscenegraph/_cxxbridge.h>
#include <mmscenegraph/curve_detect_pops.h>

namespace mmscenegraph {

MMSCENEGRAPH_API_EXPORT
bool detect_curve_pops(rust::Slice<const Real> &x_values,
                       rust::Slice<const Real> &y_values, const Real threshold,
                       rust::Vec<Real> &out_x_values,
                       rust::Vec<Real> &out_y_values) noexcept {
    return shim_detect_curve_pops(x_values, y_values, threshold, out_x_values,
                                  out_y_values);
}

MMSCENEGRAPH_API_EXPORT
bool filter_curve_pops(rust::Slice<const Real> &x_values,
                       rust::Slice<const Real> &y_values, const Real threshold,
                       rust::Vec<Real> &out_x_values,
                       rust::Vec<Real> &out_y_values) noexcept {
    return shim_filter_curve_pops(x_values, y_values, threshold, out_x_values,
                                  out_y_values);
}

}  // namespace mmscenegraph
