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

#ifndef MM_SOLVER_MM_SCENE_GRAPH_FIT_PLANE_H
#define MM_SOLVER_MM_SCENE_GRAPH_FIT_PLANE_H

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"

namespace mmscenegraph {

MMSCENEGRAPH_API_EXPORT
bool fit_plane_to_points(rust::Slice<const Real> &points_xyz,
                         Real &out_position_x, Real &out_position_y,
                         Real &out_position_z, Real &out_normal_x,
                         Real &out_normal_y, Real &out_normal_z,
                         Real &out_scale, Real &out_rms_error) noexcept;

}  // namespace mmscenegraph

#endif  // MM_SOLVER_MM_SCENE_GRAPH_FIT_PLANE_H
