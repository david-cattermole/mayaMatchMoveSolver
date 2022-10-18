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

#ifndef MM_SOLVER_MM_SCENE_GRAPH_LINE_H
#define MM_SOLVER_MM_SCENE_GRAPH_LINE_H

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmscenegraph {

MMSCENEGRAPH_API_EXPORT
bool fit_line_to_points_type2(rust::Slice<const Real> &x,
                              rust::Slice<const Real> &y, Real &out_point_x,
                              Real &out_point_y, Real &out_slope) noexcept;

MMSCENEGRAPH_API_EXPORT
bool line_point_intersection(const Point3 &point, const Point3 &line_a,
                             const Point3 &line_b, Point3 &out_point) noexcept;

}  // namespace mmscenegraph

#endif  // MM_SOLVER_MM_SCENE_GRAPH_LINE_H
