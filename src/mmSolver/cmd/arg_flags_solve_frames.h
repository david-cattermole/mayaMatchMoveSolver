/*
 * Copyright (C) 2018, 2019 David Cattermole.
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

#ifndef MM_SOLVER_ARG_FLAGS_SOLVE_FRAMES_H
#define MM_SOLVER_ARG_FLAGS_SOLVE_FRAMES_H

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// Internal Objects
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/core/frame_list.h"
#include "mmSolver/utilities/debug_utils.h"

// Command arguments
#define FRAME_FLAG "-f"
#define FRAME_FLAG_LONG "-frame"

namespace mmsolver {

// Add flags for solver frames to the command syntax.
void createSolveFramesSyntax(MSyntax &syntax);

// Parse arguments into solver frames.
MStatus parseSolveFramesArguments(const MArgDatabase &argData,
                                  FrameList &out_frameList);

}  // namespace mmsolver

#endif  // MM_SOLVER_ARG_FLAGS_SOLVE_FRAMES_H
