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

#include "arg_flags_solve_frames.h"

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// Internal Objects
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

void createSolveFramesSyntax(MSyntax &syntax) {
    syntax.addFlag(FRAME_FLAG, FRAME_FLAG_LONG, MSyntax::kLong);
    syntax.makeFlagMultiUse(FRAME_FLAG);
    return;
}

MStatus parseSolveFramesArguments(const MArgDatabase &argData,
                                  FrameList &out_frameList) {
    MStatus status = MStatus::kSuccess;

    // Get 'Frames'
    FrameCount framesCount = argData.numberOfFlagUses(FRAME_FLAG);
    out_frameList.clear();
    out_frameList.reserve(framesCount);
    for (unsigned int i = 0; i < framesCount; ++i) {
        MArgList frameArgs;
        status = argData.getFlagArgumentList(FRAME_FLAG, i, frameArgs);
        if (status == MStatus::kSuccess) {
            if (frameArgs.length() != 1) {
                MMSOLVER_MAYA_ERR(
                    "Attribute argument list must have 1 argument; \"frame\".");
                continue;
            }
            const FrameNumber value = frameArgs.asInt(0, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            out_frameList.push_back(value, /*enabled=*/true);
        }
    }

    // Make sure we have a frame list.
    if (out_frameList.is_empty()) {
        status = MS::kFailure;
        status.perror("Frame List length is 0, must have a frame to solve.");
    }

    return status;
}

}  // namespace mmsolver
