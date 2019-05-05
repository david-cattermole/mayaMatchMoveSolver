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
 * Main Maya plugin entry point.
 */


#include <maya/MFnPlugin.h>
#include <maya/MPxTransform.h>
#include <maya/MString.h>
#include <maya/MStatus.h>
#include <maya/MObject.h>

// Build-Time constant values.
#include <buildConstant.h>

#include <MMSolverCmd.h>
#include <MMSolverTypeCmd.h>
#include <MMTestCameraMatrixCmd.h>
#include <MMMarkerScaleNode.h>
#include <MMReprojectionNode.h>
#include <MMMarkerGroupTransformNode.h>
#include <MMReprojectionCmd.h>


#define REGISTER_COMMAND(plugin, name, creator, syntax, stat) \
    stat = plugin.registerCommand( name, creator, syntax);    \
    if (!stat) {                                              \
        stat.perror(MString(name) + ": registerCommand");     \
        return status;                                        \
    }

#define DEREGISTER_COMMAND(plugin, name, stat)              \
    stat = plugin.deregisterCommand(name);                  \
    if (!stat) {                                            \
        stat.perror(MString(name) + ": deregisterCommand"); \
        return stat;                                        \
    }

#define REGISTER_NODE(plugin, name, id, creator, initialize, stat) \
    stat = plugin.registerNode(name, id, creator, initialize);     \
    if (!stat) {                                                   \
        stat.perror(MString(name) + ": registerNode");             \
        return (stat);                                             \
    }

#define DEREGISTER_NODE(plugin, name, id, stat)          \
    stat = plugin.deregisterNode(id);                    \
    if (!stat) {                                         \
        stat.perror(MString(name) + ": deregisterNode"); \
        return (stat);                                   \
    }

#define REGISTER_TRANSFORM(plugin, name,                        \
                           tfm_id, tfm_creator, tfm_initialize, \
                           mtx_id, mtx_creator,                 \
                           classification,                      \
                           stat)                                \
    stat = plugin.registerTransform(name,                       \
                                  tfm_id,                       \
                                  &tfm_creator,                 \
                                  &tfm_initialize,              \
                                  &mtx_creator,                 \
                                  mtx_id,                       \
                                  &classification);             \
    if (!stat) {                                                \
            stat.perror(MString(name) + ": registerTransform"); \
            return (stat);                                      \
    }


#undef PLUGIN_COMPANY  // Maya API defines this, we override it.
#define PLUGIN_COMPANY PROJECT_NAME
#define PLUGIN_VERSION PROJECT_VERSION


// Register with Maya
MStatus initializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj, PLUGIN_COMPANY, PLUGIN_VERSION, "Any");

    REGISTER_COMMAND(plugin,
                     MMSolverCmd::cmdName(),
                     MMSolverCmd::creator,
                     MMSolverCmd::newSyntax,
                     status);

    REGISTER_COMMAND(plugin,
                     MMSolverTypeCmd::cmdName(),
                     MMSolverTypeCmd::creator,
                     MMSolverTypeCmd::newSyntax,
                     status);

    REGISTER_COMMAND(plugin,
                     MMReprojectionCmd::cmdName(),
                     MMReprojectionCmd::creator,
                     MMReprojectionCmd::newSyntax,
                     status);
    
    REGISTER_COMMAND(plugin,
                     MMTestCameraMatrixCmd::cmdName(),
                     MMTestCameraMatrixCmd::creator,
                     MMTestCameraMatrixCmd::newSyntax,
                     status);

    REGISTER_NODE(plugin,
                  MMMarkerScaleNode::nodeName(),
                  MMMarkerScaleNode::m_id,
                  MMMarkerScaleNode::creator,
                  MMMarkerScaleNode::initialize,
                  status);
    REGISTER_NODE(plugin,
                  MMReprojectionNode::nodeName(),
                  MMReprojectionNode::m_id,
                  MMReprojectionNode::creator,
                  MMReprojectionNode::initialize,
                  status);

    // MM Marker Group transform
    const MString markerGroupClassification = "drawdb/geometry/transform";
    REGISTER_TRANSFORM(plugin,
                       MMMarkerGroupTransformNode::nodeName(),
                       MMMarkerGroupTransformNode::m_id,
                       MMMarkerGroupTransformNode::creator,
                       MMMarkerGroupTransformNode::initialize,
                       MPxTransformationMatrix::baseTransformationMatrixId,
                       MPxTransformationMatrix::creator,
                       markerGroupClassification,
                       status)

    // Run the Python startup function when the plug-in loads.
    bool displayEnabled = false;
    bool undoEnabled = false;
    MString command;
    command += "import maya.utils;\n";
    command += "global MMSOLVER_STARTED\n";
    command += "if 'mmsolver_startup' in dir() and MMSOLVER_STARTED is False:\n";
    command += "    maya.utils.executeDeferred(mmsolver_startup);\n";
    status = MGlobal::executePythonCommand(
            command,
            displayEnabled,
            undoEnabled
    );

    return status;
}


// Deregister with Maya
MStatus uninitializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj);

    DEREGISTER_COMMAND(plugin, MMSolverCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMSolverTypeCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMReprojectionCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMTestCameraMatrixCmd::cmdName(), status);

    DEREGISTER_NODE(plugin, MMMarkerScaleNode::nodeName(), 
                    MMMarkerScaleNode::m_id, status);

    DEREGISTER_NODE(plugin, MMReprojectionNode::nodeName(), 
                    MMReprojectionNode::m_id, status);

    DEREGISTER_NODE(plugin, MMMarkerGroupTransformNode::nodeName(), 
                    MMMarkerGroupTransformNode::m_id, status);
    return status;
}
