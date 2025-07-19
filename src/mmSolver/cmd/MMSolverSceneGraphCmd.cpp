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
 * Command for running mmSolverSceneGraph.
 *
 * This command mimics the 'mmSolver' command's flags, and validate
 * the given objects for creating a scene graph.
 *
 * This command is intended to be used for detecting if a scene graph
 * will be valid when created with input objects. For example if
 * 'mmscenegraph' is requested, but the input objects return a
 * failure, the user could revert to a scene graph that is known to
 * work (such as the 'Maya DAG').
 *
 * Example usage (MEL):
 *
 *   mmSolverSceneGraph
 *       -camera "camera1" "camera1Shape"
 *       -marker "myMarker" "camera1Shape" "myBundle"
 *       -attr "myBundle.translateX" "None" "None" "None" "None"
 *       -frame 1
 *       -sceneGraphMode 1  // 1 == "mmscenegraph"
 *       -mode "addAttrsToMarkers";
 *
 */

#include "MMSolverSceneGraphCmd.h"

// STL
#include <cmath>
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MUuid.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/adjust/adjust_relationships.h"
#include "mmSolver/cmd/common_arg_flags.h"
#include "mmSolver/core/array_mask.h"
#include "mmSolver/mayahelper/maya_scene_graph.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsg = mmscenegraph;

namespace mmsolver {

MMSolverSceneGraphCmd::~MMSolverSceneGraphCmd() {}

void *MMSolverSceneGraphCmd::creator() { return new MMSolverSceneGraphCmd(); }

MString MMSolverSceneGraphCmd::cmdName() {
    return MString("mmSolverSceneGraph");
}

bool MMSolverSceneGraphCmd::hasSyntax() const { return true; }

bool MMSolverSceneGraphCmd::isUndoable() const { return false; }

MSyntax MMSolverSceneGraphCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(COMMAND_MODE_FLAG, COMMAND_MODE_FLAG_LONG, MSyntax::kString);

    createSolveObjectSyntax(syntax);
    createSolveFramesSyntax(syntax);
    createSolveSceneGraphSyntax(syntax);
    return syntax;
}

MStatus MMSolverSceneGraphCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get 'Mode'
    m_commandMode = CommandMode::kUndefined;
    if (argData.isFlagSet(COMMAND_MODE_FLAG)) {
        MString string = "";
        status = argData.getFlagArgument(COMMAND_MODE_FLAG, 0, string);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        if (string == MODE_VALUE_DEBUG_CONSTRUCT) {
            m_commandMode = CommandMode::kDebugConstruct;
        } else {
            MMSOLVER_MAYA_ERR("Mode value is invalid: "
                              << "mode=" << string.asChar());
        }
    }

    status = parseSolveObjectArguments(argData, m_cameraList, m_markerList,
                                       m_bundleList, m_attrList);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveFramesArguments(argData, m_frameList);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveSceneGraphArguments(argData, m_sceneGraphMode);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus MMSolverSceneGraphCmd::doIt(const MArgList &args) {
    // Command Outputs
    auto outResult = true;

    // Read all the flag arguments.
    MStatus status = parseArgs(args);
    if (status != MStatus::kSuccess) {
        MMSOLVER_MAYA_ERR(
            "Error parsing mmSolverSceneGraph command arguments.");
        return status;
    }

    // kDebugConstruct is the only command mode that is supported, for now.
    if (m_commandMode != CommandMode::kDebugConstruct) {
        MMSOLVER_MAYA_ERR("Mode value is invalid: m_commandMode="
                          << static_cast<int>(m_commandMode));
        status = MStatus::kFailure;
        return status;
    }

    if (m_sceneGraphMode == SceneGraphMode::kMayaDag) {
        // Maya DAG succeeds because we don't need to do anything.
        MMSolverSceneGraphCmd::setResult(outResult);
    } else if (m_sceneGraphMode == SceneGraphMode::kMMSceneGraph) {
        const int timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;

        // The variables are never used outside function, they are
        // temporary and only used to test if the scene graph can be
        // constructed.
        auto frameList = std::vector<mmsg::FrameValue>();
        auto sceneGraph = mmsg::SceneGraph();
        auto attrDataBlock = mmsg::AttrDataBlock();
        auto flatScene = mmsg::FlatScene();
        auto cameraNodes = std::vector<mmsg::CameraNode>();
        auto bundleNodes = std::vector<mmsg::BundleNode>();
        auto markerNodes = std::vector<mmsg::MarkerNode>();
        auto attrIdList = std::vector<mmsg::AttrId>();

        status = construct_scene_graph(m_cameraList, m_markerList, m_bundleList,
                                       m_attrList, m_frameList, timeEvalMode,

                                       // Outputs
                                       sceneGraph, attrDataBlock, flatScene,
                                       frameList, cameraNodes, bundleNodes,
                                       markerNodes, attrIdList);
        if (status != MS::kSuccess) {
            MMSOLVER_CHECK_MSTATUS(status);
            // Do not allow this command to fail, we want to allow the
            // script interpeter to continue with the value 'false'
            // instead.
            status = MS::kSuccess;
            outResult = false;
        }
        MMSolverSceneGraphCmd::setResult(outResult);
    } else {
        MMSOLVER_MAYA_ERR("Scene Graph Mode value is invalid: value="
                          << static_cast<int>(m_sceneGraphMode));
        status = MS::kFailure;
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

}  // namespace mmsolver
