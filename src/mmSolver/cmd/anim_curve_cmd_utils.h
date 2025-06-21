/*
 * Copyright (C) 2024, 2025 David Cattermole.
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
 *
 */

#ifndef MM_SOLVER_ANIM_CURVE_CMD_UTILS_H
#define MM_SOLVER_ANIM_CURVE_CMD_UTILS_H

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MAnimUtil.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MGlobal.h>
#include <maya/MTime.h>

// MM Solver
#include "mmSolver/core/frame.h"

// // MM Solver Libs
// #include <mmcore/mmdata.h>
// #include <mmcore/mmmath.h>

// MM Scene Graph
#include "mmscenegraph/mmscenegraph.h"

namespace mmsolver {

MStatus evaluate_curve(const FrameNumber start_frame,
                       const FrameNumber end_frame,
                       const MTime::Unit &time_unit,
                       MFnAnimCurve &anim_curve_fn,
                       rust::Vec<mmscenegraph::Real> &out_values_x,
                       rust::Vec<mmscenegraph::Real> &out_values_y);

const MStatus set_anim_curve_keys(
    rust::Slice<const mmscenegraph::Real> &values_x,
    rust::Slice<const mmscenegraph::Real> &values_y,
    const MTime::Unit &time_unit, MFnAnimCurve &anim_curve_fn,
    MAnimCurveChange &curve_change);

}  // namespace mmsolver

#endif  // MM_SOLVER_ANIM_CURVE_CMD_UTILS_H
