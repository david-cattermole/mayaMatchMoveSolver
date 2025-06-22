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

// MM Scene Graph
#include "mmscenegraph/mmscenegraph.h"

namespace mmsolver {

bool validate_anim_curve(
    const char *cmd_name, const FrameNumber input_start_frame,
    const FrameNumber input_end_frame, const FrameCount min_keyframe_count,
    const FrameCount min_frame_count, const MFnAnimCurve &anim_curve_fn,
    FrameNumber &out_start_frame, FrameNumber &out_end_frame);

MStatus evaluate_curve(const FrameNumber start_frame,
                       const FrameNumber end_frame,
                       const MTime::Unit &time_unit,
                       MFnAnimCurve &anim_curve_fn,
                       rust::Vec<mmscenegraph::Real> &out_values_x,
                       rust::Vec<mmscenegraph::Real> &out_values_y);

void append_curve_values_to_command_result(
    rust::Slice<const mmscenegraph::Real> &values_x,
    rust::Slice<const mmscenegraph::Real> &values_y, MDoubleArray &out_array);

MStatus set_anim_curve_keys(rust::Slice<const mmscenegraph::Real> &values_x,
                            rust::Slice<const mmscenegraph::Real> &values_y,
                            const MTime::Unit &time_unit,
                            MFnAnimCurve &anim_curve_fn,
                            MAnimCurveChange &curve_change);

}  // namespace mmsolver

#endif  // MM_SOLVER_ANIM_CURVE_CMD_UTILS_H
