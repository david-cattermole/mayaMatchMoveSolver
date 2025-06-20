/*
 * Copyright (C) 2025 David Cattermole.
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

#ifndef MM_SOLVER_MM_SCENE_GRAPH_CURVE_SIMPLIFY_H
#define MM_SOLVER_MM_SCENE_GRAPH_CURVE_SIMPLIFY_H

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmscenegraph {

MMSCENEGRAPH_API_EXPORT
bool curve_simplify(rust::Slice<const Real> &values_x,
                    rust::Slice<const Real> &values_y,
                    const size_t control_point_count,
                    const ControlPointDistribution distribution,
                    const InterpolationMethod interpolation_method,
                    rust::Vec<Real> &out_values_x,
                    rust::Vec<Real> &out_values_y) noexcept;

}  // namespace mmscenegraph

#endif  // MM_SOLVER_MM_SCENE_GRAPH_CURVE_SIMPLIFY_H
