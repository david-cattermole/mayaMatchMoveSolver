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
 * Common utilities for Lines, with mmSolver nodes.
 */

#ifndef MM_SOLVER_NODE_LINE_UTILS_H
#define MM_SOLVER_NODE_LINE_UTILS_H

// Maya
#include <maya/MArrayDataHandle.h>
#include <maya/MMatrix.h>
#include <maya/MStatus.h>
#include <maya/MString.h>

// MM Solver
#include "mmSolver/core/mmdata.h"

// MM SceneGraph
#include <mmscenegraph/mmscenegraph.h>

namespace mmsolver {

// Get object-space point data from an array transform matrix plugs.
MStatus query_line_point_data(const MMatrix parentInverseMatrix,
                              MArrayDataHandle &transformArrayHandle,
                              rust::Vec<mmscenegraph::Real> &out_point_data_x,
                              rust::Vec<mmscenegraph::Real> &out_point_data_y,
                              const bool verbose = false);

// Computes 2D line best fit - from a list of points a "best-fit"
// straight line is estimated.
MStatus fit_line_to_points(const mmscenegraph::Real line_length,
                           const rust::Vec<mmscenegraph::Real> &point_data_x,
                           const rust::Vec<mmscenegraph::Real> &point_data_y,
                           mmdata::Point2D &out_line_center,
                           mmscenegraph::Real &out_line_slope,
                           mmscenegraph::Real &out_line_angle,
                           mmdata::Vector2D &out_line_dir,
                           mmdata::Point2D &out_line_point_a,
                           mmdata::Point2D &out_line_point_b,
                           const bool verbose = false);

}  // namespace mmsolver

#endif  // MM_SOLVER_NODE_LINE_UTILS_H
