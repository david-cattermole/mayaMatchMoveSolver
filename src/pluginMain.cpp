/*
 * Copyright (C) 2018, 2019, 2021 David Cattermole.
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
#include <maya/MViewport2Renderer.h>
#include <maya/MShaderManager.h>

// Build-Time constant values.
#include <buildConstant.h>

// Constant values.
#include <nodeTypeIds.h>

// Solver and nodes
#include <MMSolverCmd.h>
#include <MMSolverTypeCmd.h>
#include <MMTestCameraMatrixCmd.h>
#include <MMMarkerScaleNode.h>
#include <MMReprojectionNode.h>
#include <MMMarkerGroupTransformNode.h>
#include <MMReprojectionCmd.h>
#include <MMSolverAffectsCmd.h>
#include <MMCameraCalibrateNode.h>
#include <MMLineIntersectNode.h>
#include <MMCameraSolveCmd.h>

// Shape nodes.
#include <shape/MarkerShapeNode.h>
#include <shape/MarkerDrawOverride.h>
#include <shape/BundleShapeNode.h>
#include <shape/BundleDrawOverride.h>
#include <shape/SkyDomeShapeNode.h>
#include <shape/SkyDomeDrawOverride.h>
#include <shape/LineShapeNode.h>
#include <shape/LineDrawOverride.h>

// MM Renderer
#include <render/RenderOverride.h>
#include <render/MMRendererCmd.h>
#include <render/RenderGlobalsNode.h>


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

#define REGISTER_LOCATOR_NODE(plugin, name, id, creator, initialize, \
                              type, classification, stat)            \
    stat = plugin.registerNode(                                      \
        name, id, creator, initialize, type, classification);        \
    if (!stat) {                                                     \
        stat.perror(MString(name) + ": registerNode");               \
        return (stat);                                               \
    }

// Same definition as 'DEREGISTER_NODE'.
#define DEREGISTER_LOCATOR_NODE(plugin, name, id, stat) \
    DEREGISTER_NODE(plugin, name, id, stat)

#define REGISTER_DRAW_OVERRIDE(classification, register_name, creator, stat) \
    stat = MHWRender::MDrawRegistry::registerDrawOverrideCreator(       \
        classification,                                                 \
        register_name,                                                  \
        creator);                                                       \
    if (!stat) {                                                        \
        stat.perror(                                                    \
            MString(register_name) + ": registerDrawOverrideCreator");  \
        return (stat);                                                  \
    }

#define DEREGISTER_DRAW_OVERRIDE(classification, register_name, stat)   \
    stat = MHWRender::MDrawRegistry::deregisterDrawOverrideCreator(     \
        classification,                                                 \
        register_name);                                                 \
    if (!stat) {                                                        \
        stat.perror("deregisterDrawOverrideCreator");                   \
        return stat;                                                    \
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
                     MMSolverAffectsCmd::cmdName(),
                     MMSolverAffectsCmd::creator,
                     MMSolverAffectsCmd::newSyntax,
                     status);

    REGISTER_COMMAND(plugin,
                     MMTestCameraMatrixCmd::cmdName(),
                     MMTestCameraMatrixCmd::creator,
                     MMTestCameraMatrixCmd::newSyntax,
                     status);

    REGISTER_COMMAND(plugin,
                     MMCameraSolveCmd::cmdName(),
                     MMCameraSolveCmd::creator,
                     MMCameraSolveCmd::newSyntax,
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

    REGISTER_NODE(plugin,
                  MMCameraCalibrateNode::nodeName(),
                  MMCameraCalibrateNode::m_id,
                  MMCameraCalibrateNode::creator,
                  MMCameraCalibrateNode::initialize,
                  status);

    REGISTER_NODE(plugin,
                  MMLineIntersectNode::nodeName(),
                  MMLineIntersectNode::m_id,
                  MMLineIntersectNode::creator,
                  MMLineIntersectNode::initialize,
                  status);

    REGISTER_NODE(plugin,
                  mmsolver::render::RenderGlobalsNode::nodeName(),
                  mmsolver::render::RenderGlobalsNode::m_id,
                  mmsolver::render::RenderGlobalsNode::creator,
                  mmsolver::render::RenderGlobalsNode::initialize,
                  status);

    const MString markerClassification = MM_MARKER_DRAW_CLASSIFY;
    const MString bundleClassification = MM_BUNDLE_DRAW_CLASSIFY;
    const MString skyDomeClassification = MM_SKY_DOME_DRAW_CLASSIFY;
    const MString lineClassification = MM_LINE_DRAW_CLASSIFY;
    REGISTER_LOCATOR_NODE(
        plugin,
        mmsolver::MarkerShapeNode::nodeName(),
        mmsolver::MarkerShapeNode::m_id,
        mmsolver::MarkerShapeNode::creator,
        mmsolver::MarkerShapeNode::initialize,
        MPxNode::kLocatorNode,
        &markerClassification,
        status);
    REGISTER_LOCATOR_NODE(
        plugin,
        mmsolver::BundleShapeNode::nodeName(),
        mmsolver::BundleShapeNode::m_id,
        mmsolver::BundleShapeNode::creator,
        mmsolver::BundleShapeNode::initialize,
        MPxNode::kLocatorNode,
        &bundleClassification,
        status);
    REGISTER_LOCATOR_NODE(
        plugin,
        mmsolver::SkyDomeShapeNode::nodeName(),
        mmsolver::SkyDomeShapeNode::m_id,
        mmsolver::SkyDomeShapeNode::creator,
        mmsolver::SkyDomeShapeNode::initialize,
        MPxNode::kLocatorNode,
        &skyDomeClassification,
        status);
    REGISTER_LOCATOR_NODE(
        plugin,
        mmsolver::LineShapeNode::nodeName(),
        mmsolver::LineShapeNode::m_id,
        mmsolver::LineShapeNode::creator,
        mmsolver::LineShapeNode::initialize,
        MPxNode::kLocatorNode,
        &lineClassification,
        status);

    REGISTER_DRAW_OVERRIDE(
        mmsolver::MarkerShapeNode::m_draw_db_classification,
        mmsolver::MarkerShapeNode::m_draw_registrant_id,
        mmsolver::MarkerDrawOverride::Creator,
        status);
    REGISTER_DRAW_OVERRIDE(
        mmsolver::BundleShapeNode::m_draw_db_classification,
        mmsolver::BundleShapeNode::m_draw_registrant_id,
        mmsolver::BundleDrawOverride::Creator,
        status);
    REGISTER_DRAW_OVERRIDE(
        mmsolver::SkyDomeShapeNode::m_draw_db_classification,
        mmsolver::SkyDomeShapeNode::m_draw_registrant_id,
        mmsolver::SkyDomeDrawOverride::Creator,
        status);
    REGISTER_DRAW_OVERRIDE(
        mmsolver::LineShapeNode::m_draw_db_classification,
        mmsolver::LineShapeNode::m_draw_registrant_id,
        mmsolver::LineDrawOverride::Creator,
        status);

    // MM Marker Group transform
    const MString markerGroupClassification = MM_MARKER_GROUP_DRAW_CLASSIFY;
    REGISTER_TRANSFORM(
        plugin,
        MMMarkerGroupTransformNode::nodeName(),
        MMMarkerGroupTransformNode::m_id,
        MMMarkerGroupTransformNode::creator,
        MMMarkerGroupTransformNode::initialize,
        MPxTransformationMatrix::baseTransformationMatrixId,
        MPxTransformationMatrix::creator,
        markerGroupClassification,
        status);

    // Register MM Solver Viewport Renderer.
    //
    // Note: There is no need to initialize viewport 2.0 just to
    // register an override, it just adds to Maya start-up time.
    auto initialize_renderer = false;
    MHWRender::MRenderer* renderer =
        MHWRender::MRenderer::theRenderer(initialize_renderer);
    if (renderer) {
        // Add mmSolver 'shader' directory into the search path.
        const MHWRender::MShaderManager* shader_manager =
            renderer->getShaderManager();
        if (!shader_manager) {
            // If we cannot add shaders, return plug-in initialisation
            // failure.
            return MStatus::kFailure;
        }
        MString shader_location;
        MString cmd = MString("getModulePath -moduleName \"mayaMatchMoveSolver\";");
        if (!MGlobal::executeCommand(cmd, shader_location, false)) {
            MString warning_message = MString(
                "mmSolver: Could not get module path, looking up env var.");
            MGlobal::displayWarning(warning_message);
            shader_location = MString(std::getenv("MMSOLVER_LOCATION"));
        }
        shader_location += MString("/shader");
        shader_manager->addShaderPath(shader_location);

        mmsolver::render::RenderOverride *ptr =
            new mmsolver::render::RenderOverride(MM_RENDERER_NAME);
        renderer->registerOverride(ptr);

        REGISTER_COMMAND(plugin,
                         mmsolver::render::MMRendererCmd::cmdName(),
                         mmsolver::render::MMRendererCmd::creator,
                         mmsolver::render::MMRendererCmd::newSyntax,
                         status);
    }

    MString mel_cmd = "";

    // Register a custom selection mask with priority 2 (same as
    // locators by default).
    MSelectionMask::registerSelectionType(
        mmsolver::MarkerShapeNode::m_selection_type_name, 2);
    mel_cmd = "selectType -byName \"";
    mel_cmd += mmsolver::MarkerShapeNode::m_selection_type_name;
    mel_cmd += "\" 1";
    CHECK_MSTATUS(MGlobal::executeCommand(mel_cmd));

    MSelectionMask::registerSelectionType(
        mmsolver::BundleShapeNode::m_selection_type_name, 2);
    mel_cmd = "selectType -byName \"";
    mel_cmd += mmsolver::BundleShapeNode::m_selection_type_name;
    mel_cmd += "\" 1";
    CHECK_MSTATUS(MGlobal::executeCommand(mel_cmd));

    MSelectionMask::registerSelectionType(
        mmsolver::SkyDomeShapeNode::m_selection_type_name, 2);
    mel_cmd = "selectType -byName \"";
    mel_cmd += mmsolver::SkyDomeShapeNode::m_selection_type_name;
    mel_cmd += "\" 1";
    CHECK_MSTATUS(MGlobal::executeCommand(mel_cmd));

    MSelectionMask::registerSelectionType(
        mmsolver::LineShapeNode::m_selection_type_name, 2);
    mel_cmd = "selectType -byName \"";
    mel_cmd += mmsolver::LineShapeNode::m_selection_type_name;
    mel_cmd += "\" 1";
    CHECK_MSTATUS(MGlobal::executeCommand(mel_cmd));

    // Register plugin display filter.
    // The filter is registered in both interactive and batch mode (Hardware 2.0)
    plugin.registerDisplayFilter(
        mmsolver::MarkerShapeNode::m_display_filter_name,
        mmsolver::MarkerShapeNode::m_display_filter_label,
        mmsolver::MarkerShapeNode::m_draw_db_classification);
    plugin.registerDisplayFilter(
        mmsolver::BundleShapeNode::m_display_filter_name,
        mmsolver::BundleShapeNode::m_display_filter_label,
        mmsolver::BundleShapeNode::m_draw_db_classification);
    plugin.registerDisplayFilter(
        mmsolver::SkyDomeShapeNode::m_display_filter_name,
        mmsolver::SkyDomeShapeNode::m_display_filter_label,
        mmsolver::SkyDomeShapeNode::m_draw_db_classification);
    plugin.registerDisplayFilter(
        mmsolver::LineShapeNode::m_display_filter_name,
        mmsolver::LineShapeNode::m_display_filter_label,
        mmsolver::LineShapeNode::m_draw_db_classification);

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

    MHWRender::MRenderer* renderer = MHWRender::MRenderer::theRenderer();
    if (renderer)
    {
        // Find override with the given name and deregister
        const MHWRender::MRenderOverride* ptr =
            renderer->findRenderOverride(MM_RENDERER_NAME);
        if (ptr) {
            renderer->deregisterOverride(ptr);
            delete ptr;
        }
        DEREGISTER_COMMAND(plugin,
                           mmsolver::render::MMRendererCmd::cmdName(),
                           status);
    }

    DEREGISTER_COMMAND(plugin, MMSolverCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMSolverTypeCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMReprojectionCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMSolverAffectsCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMTestCameraMatrixCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, MMCameraSolveCmd::cmdName(), status);

    DEREGISTER_DRAW_OVERRIDE(
        mmsolver::MarkerShapeNode::m_draw_db_classification,
        mmsolver::MarkerShapeNode::m_draw_registrant_id,
        status);
    DEREGISTER_DRAW_OVERRIDE(
        mmsolver::BundleShapeNode::m_draw_db_classification,
        mmsolver::BundleShapeNode::m_draw_registrant_id,
        status);
    DEREGISTER_DRAW_OVERRIDE(
        mmsolver::SkyDomeShapeNode::m_draw_db_classification,
        mmsolver::SkyDomeShapeNode::m_draw_registrant_id,
        status);

    DEREGISTER_LOCATOR_NODE(
        plugin,
        mmsolver::MarkerShapeNode::nodeName(),
        mmsolver::MarkerShapeNode::m_id,
        status);
    DEREGISTER_LOCATOR_NODE(
        plugin,
        mmsolver::BundleShapeNode::nodeName(),
        mmsolver::BundleShapeNode::m_id,
        status);
    DEREGISTER_LOCATOR_NODE(
        plugin,
        mmsolver::SkyDomeShapeNode::nodeName(),
        mmsolver::SkyDomeShapeNode::m_id,
        status);

    DEREGISTER_NODE(plugin,
                    mmsolver::render::RenderGlobalsNode::nodeName(),
                    mmsolver::render::RenderGlobalsNode::m_id, status);

    DEREGISTER_NODE(plugin, MMMarkerScaleNode::nodeName(),
                    MMMarkerScaleNode::m_id, status);

    DEREGISTER_NODE(plugin, MMReprojectionNode::nodeName(),
                    MMReprojectionNode::m_id, status);

    DEREGISTER_NODE(plugin, MMCameraCalibrateNode::nodeName(),
                    MMCameraCalibrateNode::m_id, status);

    DEREGISTER_NODE(plugin, MMLineIntersectNode::nodeName(),
                    MMLineIntersectNode::m_id, status);

    DEREGISTER_NODE(plugin, MMMarkerGroupTransformNode::nodeName(),
                    MMMarkerGroupTransformNode::m_id, status);
    return status;
}
