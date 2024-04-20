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

#ifndef MM_SOLVER_ARG_FLAGS_SOLVE_SCENE_GRAPH_H
#define MM_SOLVER_ARG_FLAGS_SOLVE_SCENE_GRAPH_H

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

// The Scene Graph used for evaluation.
#define SCENE_GRAPH_MODE_FLAG "-sgm"
#define SCENE_GRAPH_MODE_FLAG_LONG "-sceneGraphMode"

namespace mmsolver {

// Add flags for solver scene graph to the command syntax.
void createSolveSceneGraphSyntax(MSyntax &syntax);

// Parse arguments into solver scene graph.
MStatus parseSolveSceneGraphArguments(const MArgDatabase &argData,
                                      SceneGraphMode &out_sceneGraphMode);

}  // namespace mmsolver

#endif  // MM_SOLVER_ARG_FLAGS_SOLVE_SCENE_GRAPH_H
