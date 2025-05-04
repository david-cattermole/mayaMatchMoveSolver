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
 * Header for mmSolverSceneGraph Maya command.
 */

#ifndef MM_SOLVER_SCENE_GRAPH_CMD_H
#define MM_SOLVER_SCENE_GRAPH_CMD_H

// STL
#include <cmath>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPoint.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>

// MM Solver
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/core/frame_list.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_attr_list.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_marker_list.h"

// Command arguments:

// The type of mode for the mmSolverSceneGraph command.
#define COMMAND_MODE_FLAG "-md"
#define COMMAND_MODE_FLAG_LONG "-mode"

// Possible values for the 'mode' flag.
#define MODE_VALUE_DEBUG_CONSTRUCT "debugConstruct"

namespace mmsolver {

enum class CommandMode {
    kUndefined = 0,
    kDebugConstruct = 1,
    kNumSceneGraphCommandMode,
};

class MMSolverSceneGraphCmd : public MPxCommand {
public:
    MMSolverSceneGraphCmd() : m_commandMode(CommandMode::kUndefined){};

    virtual ~MMSolverSceneGraphCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    // The mode of this command.
    CommandMode m_commandMode;

    // Objects
    CameraPtrList m_cameraList;
    MarkerList m_markerList;
    BundlePtrList m_bundleList;
    AttrList m_attrList;
    StiffAttrsPtrList m_stiffAttrsList;
    SmoothAttrsPtrList m_smoothAttrsList;

    // Frames
    FrameList m_frameList;

    // Whhat Scene Graph to construct.
    SceneGraphMode m_sceneGraphMode;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_SCENE_GRAPH_CMD_H
