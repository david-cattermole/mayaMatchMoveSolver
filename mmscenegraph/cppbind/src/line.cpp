/*
 * Copyright (C) 2022 David Cattermole.
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
#include <mmscenegraph/line.h>

namespace mmscenegraph {

MMSCENEGRAPH_API_EXPORT
bool fit_line_to_points_type2(rust::Slice<const Real> &x,
                              rust::Slice<const Real> &y, double &out_point_x,
                              double &out_point_y, double &out_slope) noexcept {
    return shim_fit_line_to_points_type2(x, y, out_point_x, out_point_y,
                                         out_slope);
}

MMSCENEGRAPH_API_EXPORT
bool line_point_intersection(const Point3 &point, const Point3 &line_a,
                             const Point3 &line_b, Point3 &out_point) noexcept {
    return shim_line_point_intersection(point, line_a, line_b, out_point);
}

}  // namespace mmscenegraph
