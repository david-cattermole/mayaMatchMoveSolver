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

// Maya
#include <maya/MFnPlugin.h>
#include <maya/MObject.h>
#include <maya/MPxTransform.h>
#include <maya/MShaderManager.h>
#include <maya/MStatus.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// Build-Time constant values.
#include "mmSolver/buildConstant.h"

// Constant values.
#include "mmSolver/nodeTypeIds.h"

// Solver and nodes
#include "mmSolver/cmd/MMCameraPoseFromPointsCmd.h"
#include "mmSolver/cmd/MMCameraRelativePoseCmd.h"
#include "mmSolver/cmd/MMCameraSolveCmd.h"
#include "mmSolver/cmd/MMColorIOCmd.h"
#include "mmSolver/cmd/MMConvertImageCmd.h"
#include "mmSolver/cmd/MMImageCacheCmd.h"
#include "mmSolver/cmd/MMMarkerHomographyCmd.h"
#include "mmSolver/cmd/MMMemoryGPUCmd.h"
#include "mmSolver/cmd/MMMemorySystemCmd.h"
#include "mmSolver/cmd/MMReadImageCmd.h"
#include "mmSolver/cmd/MMReprojectionCmd.h"
#include "mmSolver/cmd/MMSolver2Cmd.h"
#include "mmSolver/cmd/MMSolverAffectsCmd.h"
#include "mmSolver/cmd/MMSolverCmd.h"
#include "mmSolver/cmd/MMSolverSceneGraphCmd.h"
#include "mmSolver/cmd/MMSolverTypeCmd.h"
#include "mmSolver/cmd/MMTestCameraMatrixCmd.h"
#include "mmSolver/node/MMCameraCalibrateNode.h"
#include "mmSolver/node/MMImagePlaneTransformNode.h"
#include "mmSolver/node/MMImageSequenceFrameLogicNode.h"
#include "mmSolver/node/MMLensData.h"
#include "mmSolver/node/MMLensDeformerNode.h"
#include "mmSolver/node/MMLensEvaluateNode.h"
#include "mmSolver/node/MMLensModel3deNode.h"
#include "mmSolver/node/MMLensModelToggleNode.h"
#include "mmSolver/node/MMLineBestFitNode.h"
#include "mmSolver/node/MMLineIntersectNode.h"
#include "mmSolver/node/MMLinePointIntersectNode.h"
#include "mmSolver/node/MMMarkerGroupTransformNode.h"
#include "mmSolver/node/MMMarkerScaleNode.h"
#include "mmSolver/node/MMMarkerTransformNode.h"
#include "mmSolver/node/MMReprojectionNode.h"

// Shape nodes.
#include "mmSolver/shape/BundleDrawOverride.h"
#include "mmSolver/shape/BundleShapeNode.h"
#include "mmSolver/shape/ImagePlaneGeometry2Override.h"
#include "mmSolver/shape/ImagePlaneGeometryOverride.h"
#include "mmSolver/shape/ImagePlaneShape2Node.h"
#include "mmSolver/shape/ImagePlaneShapeNode.h"
#include "mmSolver/shape/LineDrawOverride.h"
#include "mmSolver/shape/LineShapeNode.h"
#include "mmSolver/shape/MarkerDrawOverride.h"
#include "mmSolver/shape/MarkerShapeNode.h"
#include "mmSolver/shape/SkyDomeDrawOverride.h"
#include "mmSolver/shape/SkyDomeShapeNode.h"

// MM Renderer
#if MMSOLVER_BUILD_RENDERER == 1
#include "mmSolver/render/MMRendererBasicCmd.h"
#include "mmSolver/render/MMRendererSilhouetteCmd.h"
#include "mmSolver/render/RenderGlobalsBasicNode.h"
#include "mmSolver/render/RenderGlobalsSilhouetteNode.h"
#include "mmSolver/render/RenderOverrideBasic.h"
#include "mmSolver/render/RenderOverrideSilhouette.h"
#endif

#define REGISTER_COMMAND(plugin, name, creator, syntax, stat) \
    stat = plugin.registerCommand(name, creator, syntax);     \
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

#define REGISTER_DATA(plugin, name, id, creator, stat) \
    stat = plugin.registerData(name, id, creator);     \
    if (!stat) {                                       \
        stat.perror(MString(name) + ": registerData"); \
        return (stat);                                 \
    }

#define REGISTER_DEFORMER_NODE(plugin, name, id, creator, initialize, type, \
                               stat)                                        \
    stat = plugin.registerNode(name, id, creator, initialize, type);        \
    if (!stat) {                                                            \
        stat.perror(MString(name) + ": registerDeformerNode");              \
        return (stat);                                                      \
    }

#define DEREGISTER_NODE(plugin, name, id, stat)          \
    stat = plugin.deregisterNode(id);                    \
    if (!stat) {                                         \
        stat.perror(MString(name) + ": deregisterNode"); \
        return (stat);                                   \
    }

#define DEREGISTER_DATA(plugin, name, id, stat)          \
    stat = plugin.deregisterData(id);                    \
    if (!stat) {                                         \
        stat.perror(MString(name) + ": deregisterData"); \
        return (stat);                                   \
    }

#define REGISTER_TRANSFORM(plugin, name, tfm_id, tfm_creator, tfm_initialize, \
                           mtx_id, mtx_creator, classification, stat)         \
    stat =                                                                    \
        plugin.registerTransform(name, tfm_id, &tfm_creator, &tfm_initialize, \
                                 &mtx_creator, mtx_id, &classification);      \
    if (!stat) {                                                              \
        stat.perror(MString(name) + ": registerTransform");                   \
        return (stat);                                                        \
    }

#define REGISTER_LOCATOR_NODE(plugin, name, id, creator, initialize, type, \
                              classification, stat)                        \
    stat = plugin.registerNode(name, id, creator, initialize, type,        \
                               classification);                            \
    if (!stat) {                                                           \
        stat.perror(MString(name) + ": registerNode");                     \
        return (stat);                                                     \
    }

// Same definition as 'DEREGISTER_NODE'.
#define DEREGISTER_LOCATOR_NODE(plugin, name, id, stat) \
    DEREGISTER_NODE(plugin, name, id, stat)

#define REGISTER_DRAW_OVERRIDE(classification, register_name, creator, stat)   \
    stat = MHWRender::MDrawRegistry::registerDrawOverrideCreator(              \
        classification, register_name, creator);                               \
    if (!stat) {                                                               \
        stat.perror(MString(register_name) + ": registerDrawOverrideCreator"); \
        return (stat);                                                         \
    }

#define DEREGISTER_DRAW_OVERRIDE(classification, register_name, stat) \
    stat = MHWRender::MDrawRegistry::deregisterDrawOverrideCreator(   \
        classification, register_name);                               \
    if (!stat) {                                                      \
        stat.perror("deregisterDrawOverrideCreator");                 \
        return stat;                                                  \
    }

#define REGISTER_GEOMETRY_OVERRIDE(classification, register_name, creator, \
                                   stat)                                   \
    stat = MHWRender::MDrawRegistry::registerGeometryOverrideCreator(      \
        classification, register_name, creator);                           \
    if (!stat) {                                                           \
        stat.perror(MString(register_name) +                               \
                    ": registerGeometryOverrideCreator");                  \
        return (stat);                                                     \
    }

#define DEREGISTER_GEOMETRY_OVERRIDE(classification, register_name, stat) \
    stat = MHWRender::MDrawRegistry::deregisterGeometryOverrideCreator(   \
        classification, register_name);                                   \
    if (!stat) {                                                          \
        stat.perror("deregisterDrawOverrideCreator");                     \
        return stat;                                                      \
    }

#undef PLUGIN_COMPANY  // Maya API defines this, we override it.
#define PLUGIN_COMPANY PROJECT_NAME
#define PLUGIN_VERSION PROJECT_VERSION

// Register with Maya
MStatus initializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj, PLUGIN_COMPANY, PLUGIN_VERSION, "Any");
    bool verbose = false;

    MMSOLVER_MAYA_VRB("Loading " << MODULE_FULL_NAME);

    // Register data types first, so the nodes and commands below can
    // reference them.
    REGISTER_DATA(plugin, mmsolver::MMLensData::typeName(),
                  mmsolver::MMLensData::m_id, mmsolver::MMLensData::creator,
                  status);

    REGISTER_COMMAND(plugin, mmsolver::MMSolverCmd::cmdName(),
                     mmsolver::MMSolverCmd::creator,
                     mmsolver::MMSolverCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMSolver2Cmd::cmdName(),
                     mmsolver::MMSolver2Cmd::creator,
                     mmsolver::MMSolver2Cmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMSolverTypeCmd::cmdName(),
                     mmsolver::MMSolverTypeCmd::creator,
                     mmsolver::MMSolverTypeCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMReprojectionCmd::cmdName(),
                     mmsolver::MMReprojectionCmd::creator,
                     mmsolver::MMReprojectionCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMSolverAffectsCmd::cmdName(),
                     mmsolver::MMSolverAffectsCmd::creator,
                     mmsolver::MMSolverAffectsCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMSolverSceneGraphCmd::cmdName(),
                     mmsolver::MMSolverSceneGraphCmd::creator,
                     mmsolver::MMSolverSceneGraphCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMTestCameraMatrixCmd::cmdName(),
                     mmsolver::MMTestCameraMatrixCmd::creator,
                     mmsolver::MMTestCameraMatrixCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMCameraPoseFromPointsCmd::cmdName(),
                     mmsolver::MMCameraPoseFromPointsCmd::creator,
                     mmsolver::MMCameraPoseFromPointsCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMCameraRelativePoseCmd::cmdName(),
                     mmsolver::MMCameraRelativePoseCmd::creator,
                     mmsolver::MMCameraRelativePoseCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMCameraSolveCmd::cmdName(),
                     mmsolver::MMCameraSolveCmd::creator,
                     mmsolver::MMCameraSolveCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMColorIOCmd::cmdName(),
                     mmsolver::MMColorIOCmd::creator,
                     mmsolver::MMColorIOCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMConvertImageCmd::cmdName(),
                     mmsolver::MMConvertImageCmd::creator,
                     mmsolver::MMConvertImageCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMImageCacheCmd::cmdName(),
                     mmsolver::MMImageCacheCmd::creator,
                     mmsolver::MMImageCacheCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMMarkerHomographyCmd::cmdName(),
                     mmsolver::MMMarkerHomographyCmd::creator,
                     mmsolver::MMMarkerHomographyCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMMemoryGPUCmd::cmdName(),
                     mmsolver::MMMemoryGPUCmd::creator,
                     mmsolver::MMMemoryGPUCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMMemorySystemCmd::cmdName(),
                     mmsolver::MMMemorySystemCmd::creator,
                     mmsolver::MMMemorySystemCmd::newSyntax, status);

    REGISTER_COMMAND(plugin, mmsolver::MMReadImageCmd::cmdName(),
                     mmsolver::MMReadImageCmd::creator,
                     mmsolver::MMReadImageCmd::newSyntax, status);

    REGISTER_NODE(plugin, mmsolver::MMMarkerScaleNode::nodeName(),
                  mmsolver::MMMarkerScaleNode::m_id,
                  mmsolver::MMMarkerScaleNode::creator,
                  mmsolver::MMMarkerScaleNode::initialize, status);

    REGISTER_NODE(plugin, mmsolver::MMImageSequenceFrameLogicNode::nodeName(),
                  mmsolver::MMImageSequenceFrameLogicNode::m_id,
                  mmsolver::MMImageSequenceFrameLogicNode::creator,
                  mmsolver::MMImageSequenceFrameLogicNode::initialize, status);

    REGISTER_NODE(plugin, mmsolver::MMReprojectionNode::nodeName(),
                  mmsolver::MMReprojectionNode::m_id,
                  mmsolver::MMReprojectionNode::creator,
                  mmsolver::MMReprojectionNode::initialize, status);

    REGISTER_NODE(plugin, mmsolver::MMCameraCalibrateNode::nodeName(),
                  mmsolver::MMCameraCalibrateNode::m_id,
                  mmsolver::MMCameraCalibrateNode::creator,
                  mmsolver::MMCameraCalibrateNode::initialize, status);

    REGISTER_NODE(plugin, mmsolver::MMLineBestFitNode::nodeName(),
                  mmsolver::MMLineBestFitNode::m_id,
                  mmsolver::MMLineBestFitNode::creator,
                  mmsolver::MMLineBestFitNode::initialize, status);

    REGISTER_NODE(plugin, mmsolver::MMLineIntersectNode::nodeName(),
                  mmsolver::MMLineIntersectNode::m_id,
                  mmsolver::MMLineIntersectNode::creator,
                  mmsolver::MMLineIntersectNode::initialize, status);

    REGISTER_NODE(plugin, mmsolver::MMLinePointIntersectNode::nodeName(),
                  mmsolver::MMLinePointIntersectNode::m_id,
                  mmsolver::MMLinePointIntersectNode::creator,
                  mmsolver::MMLinePointIntersectNode::initialize, status);

    REGISTER_DEFORMER_NODE(plugin, mmsolver::MMLensDeformerNode::nodeName(),
                           mmsolver::MMLensDeformerNode::m_id,
                           mmsolver::MMLensDeformerNode::creator,
                           mmsolver::MMLensDeformerNode::initialize,
                           MPxNode::kDeformerNode, status);

    REGISTER_NODE(plugin, mmsolver::MMLensEvaluateNode::nodeName(),
                  mmsolver::MMLensEvaluateNode::m_id,
                  mmsolver::MMLensEvaluateNode::creator,
                  mmsolver::MMLensEvaluateNode::initialize, status);

    REGISTER_NODE(plugin, mmsolver::MMLensModel3deNode::nodeName(),
                  mmsolver::MMLensModel3deNode::m_id,
                  mmsolver::MMLensModel3deNode::creator,
                  mmsolver::MMLensModel3deNode::initialize, status);

    REGISTER_NODE(plugin, mmsolver::MMLensModelToggleNode::nodeName(),
                  mmsolver::MMLensModelToggleNode::m_id,
                  mmsolver::MMLensModelToggleNode::creator,
                  mmsolver::MMLensModelToggleNode::initialize, status);

    const MString bundleClassification = MM_BUNDLE_DRAW_CLASSIFY;
    const MString lineClassification = MM_LINE_DRAW_CLASSIFY;
    const MString markerClassification = MM_MARKER_DRAW_CLASSIFY;
    const MString skyDomeClassification = MM_SKY_DOME_DRAW_CLASSIFY;
    const MString imagePlaneShapeClassification =
        MM_IMAGE_PLANE_SHAPE_DRAW_CLASSIFY;
    const MString imagePlaneShape2Classification =
        MM_IMAGE_PLANE_SHAPE_2_DRAW_CLASSIFY;
    REGISTER_LOCATOR_NODE(plugin, mmsolver::MarkerShapeNode::nodeName(),
                          mmsolver::MarkerShapeNode::m_id,
                          mmsolver::MarkerShapeNode::creator,
                          mmsolver::MarkerShapeNode::initialize,
                          MPxNode::kLocatorNode, &markerClassification, status);
    REGISTER_LOCATOR_NODE(plugin, mmsolver::BundleShapeNode::nodeName(),
                          mmsolver::BundleShapeNode::m_id,
                          mmsolver::BundleShapeNode::creator,
                          mmsolver::BundleShapeNode::initialize,
                          MPxNode::kLocatorNode, &bundleClassification, status);
    REGISTER_LOCATOR_NODE(plugin, mmsolver::ImagePlaneShapeNode::nodeName(),
                          mmsolver::ImagePlaneShapeNode::m_id,
                          mmsolver::ImagePlaneShapeNode::creator,
                          mmsolver::ImagePlaneShapeNode::initialize,
                          MPxNode::kLocatorNode, &imagePlaneShapeClassification,
                          status);
    REGISTER_LOCATOR_NODE(plugin, mmsolver::ImagePlaneShape2Node::nodeName(),
                          mmsolver::ImagePlaneShape2Node::m_id,
                          mmsolver::ImagePlaneShape2Node::creator,
                          mmsolver::ImagePlaneShape2Node::initialize,
                          MPxNode::kLocatorNode,
                          &imagePlaneShape2Classification, status);
    REGISTER_LOCATOR_NODE(
        plugin, mmsolver::SkyDomeShapeNode::nodeName(),
        mmsolver::SkyDomeShapeNode::m_id, mmsolver::SkyDomeShapeNode::creator,
        mmsolver::SkyDomeShapeNode::initialize, MPxNode::kLocatorNode,
        &skyDomeClassification, status);
    REGISTER_LOCATOR_NODE(plugin, mmsolver::LineShapeNode::nodeName(),
                          mmsolver::LineShapeNode::m_id,
                          mmsolver::LineShapeNode::creator,
                          mmsolver::LineShapeNode::initialize,
                          MPxNode::kLocatorNode, &lineClassification, status);

    REGISTER_DRAW_OVERRIDE(mmsolver::MarkerShapeNode::m_draw_db_classification,
                           mmsolver::MarkerShapeNode::m_draw_registrant_id,
                           mmsolver::MarkerDrawOverride::Creator, status);
    REGISTER_DRAW_OVERRIDE(mmsolver::BundleShapeNode::m_draw_db_classification,
                           mmsolver::BundleShapeNode::m_draw_registrant_id,
                           mmsolver::BundleDrawOverride::Creator, status);
    REGISTER_GEOMETRY_OVERRIDE(
        mmsolver::ImagePlaneShapeNode::m_draw_db_classification,
        mmsolver::ImagePlaneShapeNode::m_draw_registrant_id,
        mmsolver::ImagePlaneGeometryOverride::Creator, status);
    REGISTER_GEOMETRY_OVERRIDE(
        mmsolver::ImagePlaneShape2Node::m_draw_db_classification,
        mmsolver::ImagePlaneShape2Node::m_draw_registrant_id,
        mmsolver::ImagePlaneGeometry2Override::Creator, status);
    REGISTER_DRAW_OVERRIDE(mmsolver::SkyDomeShapeNode::m_draw_db_classification,
                           mmsolver::SkyDomeShapeNode::m_draw_registrant_id,
                           mmsolver::SkyDomeDrawOverride::Creator, status);
    REGISTER_DRAW_OVERRIDE(mmsolver::LineShapeNode::m_draw_db_classification,
                           mmsolver::LineShapeNode::m_draw_registrant_id,
                           mmsolver::LineDrawOverride::Creator, status);

    // MM Marker Group transform
    const MString markerGroupClassification = MM_MARKER_GROUP_DRAW_CLASSIFY;
    REGISTER_TRANSFORM(plugin, mmsolver::MMMarkerGroupTransformNode::nodeName(),
                       mmsolver::MMMarkerGroupTransformNode::m_id,
                       mmsolver::MMMarkerGroupTransformNode::creator,
                       mmsolver::MMMarkerGroupTransformNode::initialize,
                       MPxTransformationMatrix::baseTransformationMatrixId,
                       MPxTransformationMatrix::creator,
                       markerGroupClassification, status);

    // MM Marker Group transform
    const MString imagePlaneTransformClassification =
        MM_IMAGE_PLANE_TRANSFORM_DRAW_CLASSIFY;
    REGISTER_TRANSFORM(plugin, mmsolver::MMImagePlaneTransformNode::nodeName(),
                       mmsolver::MMImagePlaneTransformNode::m_id,
                       mmsolver::MMImagePlaneTransformNode::creator,
                       mmsolver::MMImagePlaneTransformNode::initialize,
                       MPxTransformationMatrix::baseTransformationMatrixId,
                       MPxTransformationMatrix::creator,
                       imagePlaneTransformClassification, status);

    // Marker transform node and matrix
    const MString markerTfmClassification = "drawdb/geometry/transform";
    REGISTER_TRANSFORM(plugin, mmsolver::MMMarkerTransformNode::nodeName(),
                       mmsolver::MMMarkerTransformNode::m_id,
                       mmsolver::MMMarkerTransformNode::creator,
                       mmsolver::MMMarkerTransformNode::initialize,
                       mmsolver::MMMarkerTransformMatrix::m_id,
                       mmsolver::MMMarkerTransformMatrix::creator,
                       markerTfmClassification, status);

#if MMSOLVER_BUILD_RENDERER == 1
    REGISTER_COMMAND(plugin, mmsolver::render::MMRendererBasicCmd::cmdName(),
                     mmsolver::render::MMRendererBasicCmd::creator,
                     mmsolver::render::MMRendererBasicCmd::newSyntax, status);
    REGISTER_COMMAND(
        plugin, mmsolver::render::MMRendererSilhouetteCmd::cmdName(),
        mmsolver::render::MMRendererSilhouetteCmd::creator,
        mmsolver::render::MMRendererSilhouetteCmd::newSyntax, status);

    REGISTER_NODE(plugin, mmsolver::render::RenderGlobalsBasicNode::nodeName(),
                  mmsolver::render::RenderGlobalsBasicNode::m_id,
                  mmsolver::render::RenderGlobalsBasicNode::creator,
                  mmsolver::render::RenderGlobalsBasicNode::initialize, status);
    REGISTER_NODE(
        plugin, mmsolver::render::RenderGlobalsSilhouetteNode::nodeName(),
        mmsolver::render::RenderGlobalsSilhouetteNode::m_id,
        mmsolver::render::RenderGlobalsSilhouetteNode::creator,
        mmsolver::render::RenderGlobalsSilhouetteNode::initialize, status);

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
            MString warning_message = MString(
                "mmSolver: Shader Manager is unavailable, cannot load Viewport "
                "Renderer.");
            MGlobal::displayWarning(warning_message);
            MMSOLVER_MAYA_WRN(warning_message.asChar());
        } else {
            MString shader_location;
            MString cmd =
                MString("getModulePath -moduleName \"mayaMatchMoveSolver\";");
            if (!MGlobal::executeCommand(cmd, shader_location, false)) {
                MString warning_message = MString(
                    "mmSolver: Could not get module path, looking up env var.");
                MGlobal::displayWarning(warning_message);
                shader_location = MString(std::getenv("MMSOLVER_LOCATION"));
            }
            shader_location += MString("/shader");
            shader_manager->addShaderPath(shader_location);

            mmsolver::render::RenderOverrideBasic* default_renderer_ptr =
                new mmsolver::render::RenderOverrideBasic(
                    MM_RENDERER_BASIC_NAME);
            renderer->registerOverride(default_renderer_ptr);

            mmsolver::render::RenderOverrideSilhouette*
                silhouette_renderer_ptr =
                    new mmsolver::render::RenderOverrideSilhouette(
                        MM_RENDERER_SILHOUETTE_NAME);
            renderer->registerOverride(silhouette_renderer_ptr);
        }
    }
#endif

    // Register a custom selection mask with priority 2 (same as
    // locators by default).
    MString mel_cmd = "";
    auto selection_priority = 2;
    MSelectionMask::registerSelectionType(
        mmsolver::MarkerShapeNode::m_selection_type_name, selection_priority);
    mel_cmd += "selectType -byName \"";
    mel_cmd += mmsolver::MarkerShapeNode::m_selection_type_name;
    mel_cmd += "\" 1;";

    MSelectionMask::registerSelectionType(
        mmsolver::BundleShapeNode::m_selection_type_name, selection_priority);
    mel_cmd += "selectType -byName \"";
    mel_cmd += mmsolver::BundleShapeNode::m_selection_type_name;
    mel_cmd += "\" 1;";

    MSelectionMask::registerSelectionType(
        mmsolver::ImagePlaneShapeNode::m_selection_type_name,
        selection_priority);
    mel_cmd += "selectType -byName \"";
    mel_cmd += mmsolver::ImagePlaneShapeNode::m_selection_type_name;
    mel_cmd += "\" 1;";

    MSelectionMask::registerSelectionType(
        mmsolver::ImagePlaneShape2Node::m_selection_type_name,
        selection_priority);
    mel_cmd = "selectType -byName \"";
    mel_cmd += mmsolver::ImagePlaneShape2Node::m_selection_type_name;
    mel_cmd += "\" 1;";

    MSelectionMask::registerSelectionType(
        mmsolver::SkyDomeShapeNode::m_selection_type_name, selection_priority);
    mel_cmd = "selectType -byName \"";
    mel_cmd += mmsolver::SkyDomeShapeNode::m_selection_type_name;
    mel_cmd += "\" 1;";

    MSelectionMask::registerSelectionType(
        mmsolver::LineShapeNode::m_selection_type_name, selection_priority);
    mel_cmd = "selectType -byName \"";
    mel_cmd += mmsolver::LineShapeNode::m_selection_type_name;
    mel_cmd += "\" 1;";

    // Register selection types.
    status = MGlobal::executeCommand(mel_cmd);
    CHECK_MSTATUS(status);

    // Register plugin display filter.
    // The filter is registered in both interactive and batch mode
    // (Hardware 2.0)
    plugin.registerDisplayFilter(
        mmsolver::MarkerShapeNode::m_display_filter_name,
        mmsolver::MarkerShapeNode::m_display_filter_label,
        mmsolver::MarkerShapeNode::m_draw_db_classification);
    plugin.registerDisplayFilter(
        mmsolver::BundleShapeNode::m_display_filter_name,
        mmsolver::BundleShapeNode::m_display_filter_label,
        mmsolver::BundleShapeNode::m_draw_db_classification);
    plugin.registerDisplayFilter(
        mmsolver::ImagePlaneShapeNode::m_display_filter_name,
        mmsolver::ImagePlaneShapeNode::m_display_filter_label,
        mmsolver::ImagePlaneShapeNode::m_draw_db_classification);
    plugin.registerDisplayFilter(
        mmsolver::ImagePlaneShape2Node::m_display_filter_name,
        mmsolver::ImagePlaneShape2Node::m_display_filter_label,
        mmsolver::ImagePlaneShape2Node::m_draw_db_classification);
    plugin.registerDisplayFilter(
        mmsolver::SkyDomeShapeNode::m_display_filter_name,
        mmsolver::SkyDomeShapeNode::m_display_filter_label,
        mmsolver::SkyDomeShapeNode::m_draw_db_classification);
    plugin.registerDisplayFilter(
        mmsolver::LineShapeNode::m_display_filter_name,
        mmsolver::LineShapeNode::m_display_filter_label,
        mmsolver::LineShapeNode::m_draw_db_classification);

    // Run the Python startup function when the plug-in loads.
    bool displayEnabled = true;
    bool undoEnabled = false;
    MString startup_cmd;
    startup_cmd += "global proc mmsolver_startup() ";
    startup_cmd += "{ ";
    startup_cmd +=
        "python(\"import mmSolver.startup; "
        "mmSolver.startup.mmsolver_startup()\"); ";
    startup_cmd += "} ";
    startup_cmd += "evalDeferred(\"mmsolver_startup\");";
    status = MGlobal::executeCommand(startup_cmd, displayEnabled, undoEnabled);
    CHECK_MSTATUS(status);

    MMSOLVER_MAYA_INFO("Loaded " << MODULE_FULL_NAME);

    return status;
}

// Deregister with Maya
MStatus uninitializePlugin(MObject obj) {
    MStatus status;
    MFnPlugin plugin(obj);
    bool verbose = false;

    MMSOLVER_MAYA_VRB("Uninitializing " << MODULE_FULL_NAME);

#if MMSOLVER_BUILD_RENDERER == 1
    MHWRender::MRenderer* renderer = MHWRender::MRenderer::theRenderer();
    if (renderer) {
        // Find override with the given name and deregister
        const MHWRender::MRenderOverride* default_renderer_ptr =
            renderer->findRenderOverride(MM_RENDERER_BASIC_NAME);
        if (default_renderer_ptr) {
            renderer->deregisterOverride(default_renderer_ptr);
            delete default_renderer_ptr;
        }

        const MHWRender::MRenderOverride* silhouette_renderer_ptr =
            renderer->findRenderOverride(MM_RENDERER_SILHOUETTE_NAME);
        if (silhouette_renderer_ptr) {
            renderer->deregisterOverride(silhouette_renderer_ptr);
            delete silhouette_renderer_ptr;
        }
    }

    DEREGISTER_COMMAND(plugin, mmsolver::render::MMRendererBasicCmd::cmdName(),
                       status);
    DEREGISTER_COMMAND(
        plugin, mmsolver::render::MMRendererSilhouetteCmd::cmdName(), status);

    DEREGISTER_NODE(plugin,
                    mmsolver::render::RenderGlobalsBasicNode::nodeName(),
                    mmsolver::render::RenderGlobalsBasicNode::m_id, status);
    DEREGISTER_NODE(
        plugin, mmsolver::render::RenderGlobalsSilhouetteNode::nodeName(),
        mmsolver::render::RenderGlobalsSilhouetteNode::m_id, status);
#endif

    DEREGISTER_COMMAND(plugin, mmsolver::MMSolverCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMSolver2Cmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMSolverTypeCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMReprojectionCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMSolverAffectsCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMSolverSceneGraphCmd::cmdName(),
                       status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMTestCameraMatrixCmd::cmdName(),
                       status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMCameraPoseFromPointsCmd::cmdName(),
                       status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMCameraRelativePoseCmd::cmdName(),
                       status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMCameraSolveCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMColorIOCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMImageCacheCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMConvertImageCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMMarkerHomographyCmd::cmdName(),
                       status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMMemoryGPUCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMMemorySystemCmd::cmdName(), status);
    DEREGISTER_COMMAND(plugin, mmsolver::MMReadImageCmd::cmdName(), status);

    DEREGISTER_DRAW_OVERRIDE(
        mmsolver::MarkerShapeNode::m_draw_db_classification,
        mmsolver::MarkerShapeNode::m_draw_registrant_id, status);
    DEREGISTER_DRAW_OVERRIDE(
        mmsolver::BundleShapeNode::m_draw_db_classification,
        mmsolver::BundleShapeNode::m_draw_registrant_id, status);
    DEREGISTER_GEOMETRY_OVERRIDE(
        mmsolver::ImagePlaneShapeNode::m_draw_db_classification,
        mmsolver::ImagePlaneShapeNode::m_draw_registrant_id, status);
    DEREGISTER_GEOMETRY_OVERRIDE(
        mmsolver::ImagePlaneShape2Node::m_draw_db_classification,
        mmsolver::ImagePlaneShape2Node::m_draw_registrant_id, status);
    DEREGISTER_DRAW_OVERRIDE(
        mmsolver::SkyDomeShapeNode::m_draw_db_classification,
        mmsolver::SkyDomeShapeNode::m_draw_registrant_id, status);
    DEREGISTER_DRAW_OVERRIDE(mmsolver::LineShapeNode::m_draw_db_classification,
                             mmsolver::LineShapeNode::m_draw_registrant_id,
                             status);

    DEREGISTER_LOCATOR_NODE(plugin, mmsolver::MarkerShapeNode::nodeName(),
                            mmsolver::MarkerShapeNode::m_id, status);
    DEREGISTER_LOCATOR_NODE(plugin, mmsolver::BundleShapeNode::nodeName(),
                            mmsolver::BundleShapeNode::m_id, status);
    DEREGISTER_LOCATOR_NODE(plugin, mmsolver::ImagePlaneShapeNode::nodeName(),
                            mmsolver::ImagePlaneShapeNode::m_id, status);
    DEREGISTER_LOCATOR_NODE(plugin, mmsolver::ImagePlaneShape2Node::nodeName(),
                            mmsolver::ImagePlaneShape2Node::m_id, status);
    DEREGISTER_LOCATOR_NODE(plugin, mmsolver::SkyDomeShapeNode::nodeName(),
                            mmsolver::SkyDomeShapeNode::m_id, status);
    DEREGISTER_LOCATOR_NODE(plugin, mmsolver::LineShapeNode::nodeName(),
                            mmsolver::LineShapeNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMMarkerScaleNode::nodeName(),
                    mmsolver::MMMarkerScaleNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMReprojectionNode::nodeName(),
                    mmsolver::MMReprojectionNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMCameraCalibrateNode::nodeName(),
                    mmsolver::MMCameraCalibrateNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMLineBestFitNode::nodeName(),
                    mmsolver::MMLineBestFitNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMLineIntersectNode::nodeName(),
                    mmsolver::MMLineIntersectNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMLinePointIntersectNode::nodeName(),
                    mmsolver::MMLinePointIntersectNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMMarkerGroupTransformNode::nodeName(),
                    mmsolver::MMMarkerGroupTransformNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMImageSequenceFrameLogicNode::nodeName(),
                    mmsolver::MMImageSequenceFrameLogicNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMImagePlaneTransformNode::nodeName(),
                    mmsolver::MMImagePlaneTransformNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMMarkerTransformNode::nodeName(),
                    mmsolver::MMMarkerTransformNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMLensDeformerNode::nodeName(),
                    mmsolver::MMLensDeformerNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMLensEvaluateNode::nodeName(),
                    mmsolver::MMLensEvaluateNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMLensModel3deNode::nodeName(),
                    mmsolver::MMLensModel3deNode::m_id, status);

    DEREGISTER_NODE(plugin, mmsolver::MMLensModelToggleNode::nodeName(),
                    mmsolver::MMLensModelToggleNode::m_id, status);

    // Unloaded last, so that all nodes needing it are unloaded first
    // and we won't get a potential crash.
    DEREGISTER_DATA(plugin, mmsolver::MMLensData::typeName(),
                    mmsolver::MMLensData::m_id, status);

    MMSOLVER_MAYA_INFO(MODULE_FULL_NAME << " Unloaded");

    return status;
}
