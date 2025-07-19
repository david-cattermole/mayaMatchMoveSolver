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

#include "arg_flags_solve_scene_graph.h"

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MArgParser.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// Internal Objects
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

void createSolveSceneGraphSyntax(MSyntax &syntax) {
    syntax.addFlag(SCENE_GRAPH_MODE_FLAG, SCENE_GRAPH_MODE_FLAG_LONG,
                   MSyntax::kUnsigned);
    return;
}

MStatus parseSolveSceneGraphArguments(const MArgDatabase &argData,
                                      SceneGraphMode &out_sceneGraphMode) {
    MStatus status = MStatus::kSuccess;

    // Get 'Scene Graph Mode'
    uint32_t sceneGraphMode = SCENE_GRAPH_MODE_DEFAULT_VALUE;
    if (argData.isFlagSet(SCENE_GRAPH_MODE_FLAG)) {
        status =
            argData.getFlagArgument(SCENE_GRAPH_MODE_FLAG, 0, sceneGraphMode);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    out_sceneGraphMode = static_cast<SceneGraphMode>(sceneGraphMode);

    return status;
}

}  // namespace mmsolver
