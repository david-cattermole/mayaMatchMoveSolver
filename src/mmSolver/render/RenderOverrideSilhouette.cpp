/*
 * Copyright (C) 2021, 2023, 2024 David Cattermole.
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
 * mmSolver viewport 2.0 renderer override.
 *
 */

#include "RenderOverrideSilhouette.h"

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MGL.h>
#include <maya/MGlobal.h>
#include <maya/MItDependencyNodes.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MUiMessage.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/ops/ClearOperation.h"
#include "mmSolver/render/ops/HudRender.h"
#include "mmSolver/render/ops/PresentTarget.h"
#include "mmSolver/render/ops/SceneRender.h"
#include "mmSolver/render/ops/SilhouetteRender.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

const MString kClearOpName = MString("mmRendererSilhouette_clearPass");
const MString kBackgroundOpName =
    MString("mmRendererSilhouette_backgroundPass");
const MString kSceneOpName = MString("mmRendererSilhouette_scenePass");
const MString kSelectOpName = MString("mmRendererSilhouette_selectPass");
const MString kSilhouetteOpName =
    MString("mmRendererSilhouette_silhouettePass");
const MString kWireframeOpName = MString("mmRendererSilhouette_wireframePass");
const MString kPresentOpName = MString("mmRendererSilhouette_presentPass");

static MStatus create_render_globals_silhouette_node() {
    return MGlobal::executeCommand(kRendererSilhouetteCreateNodeCommand,
                                   /*displayEnabled*/ true,
                                   /*undoEnabled*/ true);
}

// Callback for tracking renderer changes
void RenderOverrideSilhouette::renderer_change_func(const MString &panel_name,
                                                    const MString &old_renderer,
                                                    const MString &new_renderer,
                                                    void * /*client_data*/) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("Renderer changed for panel '"
                      << panel_name.asChar() << "'. "
                      << "New renderer is '" << new_renderer.asChar() << "', "
                      << "old was '" << old_renderer.asChar() << "'.");

    if (new_renderer == MM_RENDERER_SILHOUETTE_NAME) {
        MStatus status = create_render_globals_silhouette_node();
        CHECK_MSTATUS(status);
    }
}

// Callback for tracking render override changes
void RenderOverrideSilhouette::render_override_change_func(
    const MString &panel_name, const MString &old_renderer,
    const MString &new_renderer, void * /*client_data*/) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("Render override changed for panel '"
                      << panel_name.asChar() << "'. "
                      << "New override is '" << new_renderer.asChar() << "', "
                      << "old was '" << old_renderer.asChar() << "'.");

    if (new_renderer == MM_RENDERER_SILHOUETTE_NAME) {
        MStatus status = create_render_globals_silhouette_node();
        CHECK_MSTATUS(status);
    }
}

// Set up operations
RenderOverrideSilhouette::RenderOverrideSilhouette(const MString &name)
    : MRenderOverride(name)
    , m_ui_name(kRendererSilhouetteUiName)
    , m_renderer_change_callback(0)
    , m_render_override_change_callback(0)
    , m_globals_node()
    , m_enable(kSilhouetteEnableDefault)
    , m_override_color(kSilhouetteOverrideColorDefault)
    , m_depth_offset(kSilhouetteDepthOffsetDefault)
    , m_width(kSilhouetteWidthDefault)
    , m_color{kSilhouetteColorDefault[0], kSilhouetteColorDefault[1],
              kSilhouetteColorDefault[2]}
    , m_alpha(kSilhouetteAlphaDefault)
    , m_cull_face(kSilhouetteCullFaceDefault)
    , m_operation_num(255) {
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_ERR(
            "MM Renderer Silhouette Render Override: "
            "Failed to get renderer.");
    }

    const uint32_t sample_count = 4;  // Multi-Sample Anti-Aliasing (MSAA) x4.
    const MHWRender::MRasterFormat color_format =
        MHWRender::kR32G32B32A32_FLOAT;
    const MHWRender::MRasterFormat depth_format = MHWRender::kD24S8;
    const auto is_cube_map = false;
    const auto array_slice_count = 0;

    {
        const SilhouetteTargetId target_id = SilhouetteTargetId::kColorTarget;
        m_target_override_names[target_id] =
            MHWRender::MRenderOperation::kColorTargetName;
        m_target_descriptions[target_id] =
            new MHWRender::MRenderTargetDescription(
                m_target_override_names[target_id], 256, 256, sample_count,
                color_format, array_slice_count, is_cube_map);
        m_targets[target_id] = nullptr;
    }

    {
        const SilhouetteTargetId target_id = SilhouetteTargetId::kDepthTarget;
        m_target_override_names[target_id] =
            MHWRender::MRenderOperation::kDepthTargetName;
        m_target_descriptions[target_id] =
            new MHWRender::MRenderTargetDescription(
                m_target_override_names[target_id], 256, 256, sample_count,
                depth_format, array_slice_count, is_cube_map);
        m_targets[target_id] = nullptr;
    }

    // Only draw imagePlane and plugin shapes.
    const auto draw_only_image_plane_object_types =
        static_cast<MUint64>(~(MHWRender::MFrameContext::kExcludeImagePlane |
                               MHWRender::MFrameContext::kExcludePluginShapes));

    // Draw everything except imagePlane and plugin shapes.
    const auto draw_all_except_image_plane_object_types =
        static_cast<MUint64>(MHWRender::MFrameContext::kExcludeImagePlane |
                             MHWRender::MFrameContext::kExcludePluginShapes);

    // Passes
    //
    // Draw normal, exclude imageplane from depth rendering.
    //
    // The principle here is to draw the things we don't want to shade
    // for depth here and exclude the things we want to draw. If a
    // render item is in the depth buffer, it won't be drawn later.
    m_sceneOp = new SceneRender(kSceneOpName);
    m_sceneOp->setEnabled(true);
    m_sceneOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    // TODO: For silhouette rendering - override the shader to be
    // useBackground.
    m_sceneOp->setClearMask(CLEAR_MASK_DEPTH);

    // TODO: Don't use exclude types, but instead detect the objects
    // in the scene.
    m_sceneOp->setExcludeTypes(draw_all_except_image_plane_object_types);
    m_sceneOp->setSceneFilter(
        static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
            MHWRender::MSceneRender::kRenderShadedItems));
    m_sceneOp->setDisplayModeOverride(
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kWireFrame |
            MHWRender::MSceneRender::kShaded));

    // We want to draw both a background imageplane and an imageplane
    // in the viewport here. Add a separate pass for background only.
    m_backgroundOp = new SceneRender(kBackgroundOpName);
    m_backgroundOp->setEnabled(true);
    m_backgroundOp->setBackgroundStyle(BackgroundStyle::kMayaDefault);
    m_backgroundOp->setClearMask(CLEAR_MASK_ALL);
    m_backgroundOp->setExcludeTypes(draw_only_image_plane_object_types);

    // - kRenderPreSceneUIItems - Grid or user added pre-scene UI items.
    // - kRenderShadedItems - all shaded items.
    // - kRenderPostSceneUIItems - Wireframe and components for
    //                             surfaces as well as non-surface
    //                             objects. kRenderUIItems - both
    //                             pre/post scene UI items.
    // - kRenderAllItems - ALL the items.
    //
    // kRenderShadedItems is needed to render normal objects (meshes,
    // NURBS curves, etc).
    //
    // kRenderPostSceneUIItems is needed to render the
    // 'mmImagePlaneShape'.
    const auto mesh_and_image_plane_scene_filter =
        static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
            MHWRender::MSceneRender::kRenderShadedItems |
            MHWRender::MSceneRender::kRenderPostSceneUIItems);
    m_backgroundOp->setSceneFilter(mesh_and_image_plane_scene_filter);

    // Draw manip and excluded objects
    //
    // We want to use depth buffer to prevent drawing items we
    // wanted "hidden line".
    //
    // Notice that we allow free image plane to be rendered normally
    // here. You could remove it later.
    //
    // TODO: Stop this operation from rendering wireframes for
    // selected objects.
    m_selectOp = new SceneRender(kSelectOpName);
    m_selectOp->setEnabled(true);
    m_selectOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    m_selectOp->setClearMask(CLEAR_MASK_NONE);
    m_selectOp->setSceneFilter(mesh_and_image_plane_scene_filter);

    m_silhouetteOp = new SilhouetteRender(kSilhouetteOpName);
    m_silhouetteOp->setEnabled(false);

    m_wireframeOp = new SceneRender(kWireframeOpName);
    m_wireframeOp->setEnabled(true);
    m_wireframeOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    m_wireframeOp->setClearMask(CLEAR_MASK_NONE);
    m_wireframeOp->setSceneFilter(
        static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
            MHWRender::MSceneRender::kRenderUIItems));

    m_hudOp = new HudRender();
    m_hudOp->setEnabled(true);

    m_presentOp = new PresentTarget(kPresentOpName);
    m_presentOp->setEnabled(true);

    // Get the default set of operations.
    MHWRender::MRenderer::theRenderer()->getStandardViewportOperations(
        mOperations);

    // Clear the unneeded standard operations.
    MHWRender::MRenderOverride::mOperations.clear();

    // Place the new render operations in a specific order.
    //
    // The "mOperations" list owns the allocated objects and will
    // clean them up when needed.
    MHWRender::MRenderOverride::mOperations.append(m_sceneOp);
    MHWRender::MRenderOverride::mOperations.append(m_backgroundOp);
    MHWRender::MRenderOverride::mOperations.append(m_selectOp);
    MHWRender::MRenderOverride::mOperations.append(m_silhouetteOp);
    MHWRender::MRenderOverride::mOperations.append(m_wireframeOp);
    MHWRender::MRenderOverride::mOperations.append(m_hudOp);
    MHWRender::MRenderOverride::mOperations.append(m_presentOp);
}

RenderOverrideSilhouette::~RenderOverrideSilhouette() {
    // These operations are cleaned up automatically because the
    // MRenderOperations are owned by the mOperations list.
    m_backgroundOp = nullptr;
    m_sceneOp = nullptr;
    m_selectOp = nullptr;
    m_silhouetteOp = nullptr;
    m_wireframeOp = nullptr;
    m_hudOp = nullptr;
    m_presentOp = nullptr;

    RenderOverrideSilhouette::cleanup();

    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (renderer) {
        const MHWRender::MRenderTargetManager *target_manager =
            renderer->getRenderTargetManager();
        if (target_manager) {
            // Delete any targets created
            for (auto id = 0; id < SilhouetteTargetId::kTargetCount; ++id) {
                if (m_target_descriptions[id]) {
                    delete m_target_descriptions[id];
                    m_target_descriptions[id] = nullptr;
                }

                if (m_targets[id]) {
                    if (target_manager) {
                        target_manager->releaseRenderTarget(m_targets[id]);
                    }
                    m_targets[id] = nullptr;
                }
            }
        }
    }

    // Clean up callbacks
    if (m_renderer_change_callback) {
        MMessage::removeCallback(m_renderer_change_callback);
    }
    if (m_render_override_change_callback) {
        MMessage::removeCallback(m_render_override_change_callback);
    }
}

MHWRender::DrawAPI RenderOverrideSilhouette::supportedDrawAPIs() const {
    // The SilhouetteRender only works on OpenGL, so we cannot support
    // DirectX on Windows or Metal on Apple.
    return MHWRender::kOpenGLCoreProfile;
}

// Read node plug attributes and set the values.
MStatus update_parameters_silhouette(
    MObjectHandle &out_globals_node, bool &out_silhouette_enable,
    bool &out_silhouette_override_color, float &out_silhouette_depth_offset,
    float &out_silhouette_width, float &out_silhouette_color_r,
    float &out_silhouette_color_g, float &out_silhouette_color_b,
    float &out_silhouette_alpha, CullFace &out_silhouette_cull_face,
    uint8_t &out_operation_num) {
    const bool verbose = false;
    MStatus status = MS::kSuccess;
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette::update_parameters_silhouette");

    if (!out_globals_node.isValid()) {
        // Get the node and cache the handle in an 'MObjectHandle'
        // instance.
        MObject node_obj;
        status = getAsObject(kRenderGlobalsSilhouetteNodeName, node_obj,
                             /*quiet=*/true);

        if (!node_obj.isNull()) {
            out_globals_node = node_obj;
        } else {
            MMSOLVER_MAYA_VRB(
                "MM Renderer: "
                "Could not find \""
                << MM_RENDER_GLOBALS_SILHOUETTE_TYPE_NAME
                << "\" node, creating node.");
            status = create_render_globals_silhouette_node();
            CHECK_MSTATUS(status);

            if (status == MS::kSuccess) {
                status = getAsObject(kRenderGlobalsSilhouetteNodeName, node_obj,
                                     /*quiet=*/true);
                if (!node_obj.isNull()) {
                    out_globals_node = node_obj;
                } else {
                    return MS::kSuccess;
                }
            } else {
                return MS::kSuccess;
            }
        }
    }
    if (status != MS::kSuccess) {
        return MS::kSuccess;
    }

    MObject globals_node_obj = out_globals_node.object();
    if (globals_node_obj.isNull()) {
        MMSOLVER_MAYA_WRN(
            "RenderOverrideSilhouette update_parameters_silhouette: Could not "
            "find \"" +
            kRenderGlobalsSilhouetteNodeName + "\" node.");
        return MS::kSuccess;
    }
    MFnDependencyNode depends_node(globals_node_obj, &status);
    CHECK_MSTATUS(status);

    const bool want_networked_plug = true;

    // Enable Silhouette render.
    out_silhouette_enable = kSilhouetteEnableDefault;
    MPlug silhouette_enable_plug = depends_node.findPlug(
        kAttrNameSilhouetteEnable, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        out_silhouette_enable = silhouette_enable_plug.asBool();
    }
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette Silhouette Enable: "
                      << static_cast<int>(out_silhouette_enable));

    // Override Color Silhouette render.
    out_silhouette_override_color = kSilhouetteOverrideColorDefault;
    MPlug silhouette_override_color_plug = depends_node.findPlug(
        kAttrNameSilhouetteOverrideColor, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        out_silhouette_override_color = silhouette_override_color_plug.asBool();
    }
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette Silhouette Override Color: "
                      << static_cast<int>(out_silhouette_override_color));

    // Silhouette Depth Offset
    out_silhouette_depth_offset = kSilhouetteDepthOffsetDefault;
    MPlug silhouette_depth_offset_plug = depends_node.findPlug(
        kAttrNameSilhouetteDepthOffset, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        out_silhouette_depth_offset = silhouette_depth_offset_plug.asFloat();
    }
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette Silhouette Depth Offset: "
                      << out_silhouette_depth_offset);

    // Silhouette Width
    out_silhouette_width = kSilhouetteWidthDefault;
    MPlug silhouette_width_plug = depends_node.findPlug(
        kAttrNameSilhouetteWidth, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        out_silhouette_width = silhouette_width_plug.asFloat();
    }
    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette Silhouette Width: " << out_silhouette_width);

    // Silhouette Color. The color for detected silhouettes.
    out_silhouette_color_r = kSilhouetteColorDefault[0];
    out_silhouette_color_g = kSilhouetteColorDefault[1];
    out_silhouette_color_b = kSilhouetteColorDefault[2];
    MPlug silhouette_color_r_plug = depends_node.findPlug(
        kAttrNameSilhouetteColorR, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        out_silhouette_color_r = silhouette_color_r_plug.asFloat();
    }
    MPlug silhouette_color_g_plug = depends_node.findPlug(
        kAttrNameSilhouetteColorG, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        out_silhouette_color_g = silhouette_color_g_plug.asFloat();
    }
    MPlug silhouette_color_b_plug = depends_node.findPlug(
        kAttrNameSilhouetteColorB, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        out_silhouette_color_b = silhouette_color_b_plug.asFloat();
    }
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette Silhouette Color: R="
                      << out_silhouette_color_r
                      << " G=" << out_silhouette_color_g
                      << " B=" << out_silhouette_color_b);

    // Silhouette Alpha - The alpha for detected silhouettes.
    out_silhouette_alpha = kSilhouetteAlphaDefault;
    MPlug silhouette_alpha_plug = depends_node.findPlug(
        kAttrNameSilhouetteAlpha, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        out_silhouette_alpha = silhouette_alpha_plug.asFloat();
    }
    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette Silhouette Alpha: " << out_silhouette_alpha);

    // Silhouette Cull Face - Which faces to cull? 'Back', 'Front' or
    // 'Back and Front'?
    out_silhouette_cull_face = kSilhouetteCullFaceDefault;
    MPlug silhouette_cull_face_plug = depends_node.findPlug(
        kAttrNameSilhouetteCullFace, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        const auto value =
            static_cast<CullFace>(silhouette_cull_face_plug.asShort());
        out_silhouette_cull_face = value;
    }
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette Silhouette Cull Face: "
                      << static_cast<int>(out_silhouette_cull_face));

    // Operation Number.
    out_operation_num = kSilhouetteOperationNumDefault;
    MPlug operation_num_plug = depends_node.findPlug(
        kAttrNameSilhouetteOperationNum, want_networked_plug, &status);
    if (status == MStatus::kSuccess) {
        out_operation_num = static_cast<uint8_t>(operation_num_plug.asInt());
    }
    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette Operation Number: " << out_operation_num);

    return MS::kSuccess;
}

// Perform any setup required before render operations are to be executed.
MStatus RenderOverrideSilhouette::setup(const MString &destination) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette::setup: start "
                      << destination.asChar());

    MStatus status = MS::kSuccess;

    // Track changes to the renderer and override for this viewport.
    if (!m_renderer_change_callback) {
        void *client_data = nullptr;
        m_renderer_change_callback =
            MUiMessage::add3dViewRendererChangedCallback(
                destination, renderer_change_func, client_data);
    }
    if (!m_render_override_change_callback) {
        void *client_data = nullptr;
        m_render_override_change_callback =
            MUiMessage::add3dViewRenderOverrideChangedCallback(
                destination, render_override_change_func, client_data);
    }

    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_ERR(
            "MM Renderer Silhouette Render Override: "
            "Failed to get renderer.");
        return MS::kFailure;
    }

    const MHWRender::MRenderTargetManager *target_manager =
        renderer->getRenderTargetManager();
    if (!target_manager) {
        MMSOLVER_MAYA_ERR(
            "MM Renderer Silhouette Render Override: "
            "Failed to get Render Target Manager.");
        return MS::kFailure;
    }

    // Update Render Targets
    {
        MMSOLVER_MAYA_VRB(
            "RenderOverrideSilhouette::update_render_targets_silhouette");

        uint32_t target_width = 0;
        uint32_t target_height = 0;
        status = renderer->outputTargetSize(target_width, target_height);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        const bool resize_occured =
            (m_target_descriptions[SilhouetteTargetId::kColorTarget]->width() !=
                 target_width ||
             m_target_descriptions[SilhouetteTargetId::kDepthTarget]
                     ->height() != target_height);

        for (uint32_t target_id = 0;
             target_id < SilhouetteTargetId::kTargetCount; ++target_id) {
            m_target_descriptions[target_id]->setWidth(target_width);
            m_target_descriptions[target_id]->setHeight(target_height);
        }

        for (uint32_t target_id = 0;
             target_id < SilhouetteTargetId::kTargetCount; ++target_id) {
            MMSOLVER_MAYA_VRB("create_or_resize_target: "
                              << "SilhouetteTargetId::" << target_id);

            if (m_target_descriptions[target_id]) {
                if (!m_targets[target_id]) {
                    m_targets[target_id] = target_manager->acquireRenderTarget(
                        *(m_target_descriptions[target_id]));
                } else {
                    m_targets[target_id]->updateDescription(
                        *(m_target_descriptions[target_id]));
                }
            }
        }
    }

    if (!m_backgroundOp || !m_sceneOp || !m_silhouetteOp || !m_selectOp ||
        !m_wireframeOp || !m_hudOp || !m_presentOp) {
        MMSOLVER_MAYA_ERR(
            "MM Renderer Silhouette Render Override: "
            "Failed to get all render operations.");
        return MS::kFailure;
    }

    // Operations use the Render Targets defined.
    m_sceneOp->setRenderTargets(m_targets, 0, 2);
    m_backgroundOp->setRenderTargets(m_targets, 0, 1);  // Only color buffer.
    m_selectOp->setRenderTargets(m_targets, 0, 2);
    m_silhouetteOp->setRenderTargets(m_targets);
    m_wireframeOp->setRenderTargets(m_targets, 0, 2);
    m_hudOp->setRenderTargets(m_targets, 0, 2);
    m_presentOp->setRenderTargets(m_targets, 0, 2);

    // Get override values.
    status = update_parameters_silhouette(
        m_globals_node, m_enable, m_override_color, m_depth_offset, m_width,
        m_color[0], m_color[1], m_color[2], m_alpha, m_cull_face,
        m_operation_num);
    CHECK_MSTATUS(status);

    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_backgroundOp=" << m_backgroundOp);
    m_image_plane_nodes.clear();
    status = add_all_image_planes(m_image_plane_nodes);
    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_image_plane_nodes.length()="
        << m_image_plane_nodes.length());
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_backgroundOp->setObjectSetOverride(&m_image_plane_nodes);

    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_sceneOp=" << m_sceneOp);
    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_selectOp=" << m_selectOp);

    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_silhouetteOp=" << m_silhouetteOp);
    m_silhouetteOp->setPanelName(destination);

    m_silhouetteOp->setEnabled(m_enable);
    m_silhouetteOp->setSilhouetteOverrideColor(m_override_color);
    m_silhouetteOp->setSilhouetteDepthOffset(m_depth_offset);
    m_silhouetteOp->setSilhouetteWidth(m_width);
    m_silhouetteOp->setSilhouetteColor(m_color[0], m_color[1], m_color[2]);
    m_silhouetteOp->setSilhouetteAlpha(m_alpha);
    m_silhouetteOp->setSilhouetteCullFace(m_cull_face);

    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_wireframeOp=" << m_wireframeOp);
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette::setup: m_hudOp=" << m_hudOp);
    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_presentOp=" << m_presentOp);

    // For debugging what each render operation is doing.
    m_sceneOp->setEnabled(m_operation_num >= 1);
    m_backgroundOp->setEnabled(m_operation_num >= 2);
    m_selectOp->setEnabled(m_operation_num >= 3);
    m_silhouetteOp->setEnabled((m_operation_num >= 4) && m_enable);
    m_wireframeOp->setEnabled(m_operation_num >= 5);
    m_hudOp->setEnabled(m_operation_num >= 6);
    m_presentOp->setEnabled(true);

    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette::setup: end "
                      << destination.asChar());
    return MRenderOverride::setup(destination);
}

// Perform any cleanup required following the execution of render
// operations.
//
// End of frame cleanup. Clears out any data on operations which may
// change from frame to frame (render target, output panel name etc).
MStatus RenderOverrideSilhouette::cleanup() {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette::cleanup: ");

    if (m_backgroundOp) {
        m_backgroundOp->setRenderTargets(nullptr, 0, 0);
    }

    if (m_sceneOp) {
        m_sceneOp->setRenderTargets(nullptr, 0, 0);
    }

    if (m_selectOp) {
        m_selectOp->setRenderTargets(nullptr, 0, 0);
    }

    if (m_silhouetteOp) {
        m_silhouetteOp->setRenderTargets(nullptr);
    }

    if (m_wireframeOp) {
        m_wireframeOp->setRenderTargets(nullptr, 0, 0);
    }

    if (m_hudOp) {
        m_hudOp->setRenderTargets(nullptr, 0, 0);
    }

    if (m_presentOp) {
        m_presentOp->setRenderTargets(nullptr, 0, 0);
    }

    return MRenderOverride::cleanup();
}

}  // namespace render
}  // namespace mmsolver
