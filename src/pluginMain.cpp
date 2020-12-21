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
#include <MMMarkerTransformNode.h>
#include <MMLensDeformerNode.h>
#include <MMLensEvaluateNode.h>
#include <MMLensModelBasicNode.h>
#include <MMLensModelToggleNode.h>
#include <MMLensData.h>
#include <MMReprojectionCmd.h>
#include <MMSolverAffectsCmd.h>


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

#define REGISTER_DATA(plugin, name,                     \
                      id, creator,                      \
                      stat)                             \
    stat = plugin.registerData(name,                    \
                               id, creator);            \
    if (!stat) {                                        \
        stat.perror(MString(name) + ": registerData");  \
        return (stat);                                  \
    }

#define REGISTER_DEFORMER_NODE(plugin, name,                    \
                               id, creator,                     \
                               initialize,                      \
                               type, stat)                      \
    stat = plugin.registerNode(name,                            \
                               id, creator,                     \
                               initialize,                      \
                               type);                           \
    if (!stat) {                                                \
        stat.perror(MString(name) + ": registerDeformerNode");  \
        return (stat);                                          \
    }


#define DEREGISTER_NODE(plugin, name, id, stat)          \
    stat = plugin.deregisterNode(id);                    \
    if (!stat) {                                         \
        stat.perror(MString(name) + ": deregisterNode"); \
        return (stat);                                   \
    }

#define DEREGISTER_DATA(plugin, name, id, stat)             \
    stat = plugin.deregisterData(id);                       \
    if (!stat) {                                            \
        stat.perror(MString(name) + ": deregisterData");    \
        return (stat);                                      \
    }

#define REGISTER_TRANSFORM(plugin, name,                        \
                           tfm_id, tfm_creator, tfm_initialize, \
                           mtx_id, mtx_creator,                 \
                           classification,                      \
                           stat)                                \
    stat = plugin.registerTransform(name,                       \
                                    tfm_id,                     \
                                    &tfm_creator,               \
                                    &tfm_initialize,            \
                                    &mtx_creator,               \
                                    mtx_id,                     \
                                    &classification);           \
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

    // Register data types first, so the nodes and commands below can
    // reference them.
    REGISTER_DATA(plugin,
                  MMLensData::typeName(),
                  MMLensData::m_id,
                  MMLensData::creator,
                  status);

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
                     MMSolverAffectsCmd::cmdName(),
                     MMSolverAffectsCmd::creator,
                     MMSolverAffectsCmd::newSyntax,
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

    REGISTER_DEFORMER_NODE(plugin,
                           MMLensDeformerNode::nodeName(),
                           MMLensDeformerNode::m_id,
                           MMLensDeformerNode::creator,
                           MMLensDeformerNode::initialize,
                           MPxNode::kDeformerNode,
                           status);

    REGISTER_NODE(plugin,
                  MMLensEvaluateNode::nodeName(),
                  MMLensEvaluateNode::m_id,
                  MMLensEvaluateNode::creator,
                  MMLensEvaluateNode::initialize,
                  status);

    REGISTER_NODE(plugin,
                  MMLensModelBasicNode::nodeName(),
                  MMLensModelBasicNode::m_id,
                  MMLensModelBasicNode::creator,
                  MMLensModelBasicNode::initialize,
                  status);

    REGISTER_NODE(plugin,
                  MMLensModelToggleNode::nodeName(),
                  MMLensModelToggleNode::m_id,
                  MMLensModelToggleNode::creator,
                  MMLensModelToggleNode::initialize,
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

    // Marker transform node and matrix
    const MString markerTfmClassification = "drawdb/geometry/transform";
    REGISTER_TRANSFORM(plugin,
                       MMMarkerTransformNode::nodeName(),
                       MMMarkerTransformNode::m_id,
                       MMMarkerTransformNode::creator,
                       MMMarkerTransformNode::initialize,
                       MMMarkerTransformMatrix::m_id,
                       MMMarkerTransformMatrix::creator,
                       markerTfmClassification,
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
    DEREGISTER_COMMAND(plugin, MMSolverAffectsCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMTestCameraMatrixCmd::cmdName(), status);

    DEREGISTER_NODE(plugin, MMMarkerScaleNode::nodeName(),
                    MMMarkerScaleNode::m_id, status);

    DEREGISTER_NODE(plugin, MMReprojectionNode::nodeName(),
                    MMReprojectionNode::m_id, status);

    DEREGISTER_NODE(plugin, MMMarkerGroupTransformNode::nodeName(),
                    MMMarkerGroupTransformNode::m_id, status);

    DEREGISTER_NODE(plugin, MMMarkerTransformNode::nodeName(),
                    MMMarkerTransformNode::m_id, status);

    DEREGISTER_NODE(plugin, MMLensDeformerNode::nodeName(),
                    MMLensDeformerNode::m_id, status);

    DEREGISTER_NODE(plugin, MMLensEvaluateNode::nodeName(),
                    MMLensEvaluateNode::m_id, status);

    DEREGISTER_NODE(plugin, MMLensModelBasicNode::nodeName(),
                    MMLensModelBasicNode::m_id, status);

    DEREGISTER_NODE(plugin, MMLensModelToggleNode::nodeName(),
                    MMLensModelToggleNode::m_id, status);

    // Unloaded last, so that all nodes needing it are unloaded first
    // and we won't get a potential crash.
    DEREGISTER_DATA(plugin, MMLensData::typeName(),
                    MMLensData::m_id, status);
    return status;
}
