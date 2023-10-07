/*
 * Copyright (C) 2021, 2023 David Cattermole.
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
#include "mmSolver/render/ops/SceneRender.h"
#include "mmSolver/render/ops/SilhouetteRender.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

static MStatus create_render_globals_node() {
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
        MStatus status = create_render_globals_node();
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
        MStatus status = create_render_globals_node();
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
    , m_silhouette_enable(kSilhouetteEnableDefault)
    , m_silhouette_depth_offset(kSilhouetteDepthOffsetDefault)
    , m_silhouette_width(kSilhouetteWidthDefault)
    , m_silhouette_color{kSilhouetteColorDefault[0], kSilhouetteColorDefault[1],
                         kSilhouetteColorDefault[2]}
    , m_silhouette_alpha(kSilhouetteAlphaDefault) {
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_ERR(
            "MM Renderer Silhouette Render Override: "
            "Failed to get renderer.");
    }

    const MString kBackgroundOpName =
        MString("mmRendererSilhouette_backgroundPass");
    const MString kSceneOpName = MString("mmRendererSilhouette_scenePass");
    const MString kSelectOpName = MString("mmRendererSilhouette_selectPass");
    const MString kSilhouetteOpName =
        MString("mmRendererSilhouette_silhouettePass");
    const MString kWireframeOpName =
        MString("mmRendererSilhouette_wireframePass");

    m_backgroundOp = new SceneRender(kBackgroundOpName);
    m_backgroundOp->setEnabled(true);
    m_backgroundOp->setBackgroundStyle(BackgroundStyle::kMayaDefault);
    m_backgroundOp->setClearMask(CLEAR_MASK_ALL);
    m_backgroundOp->setExcludeTypes(MHWRender::MFrameContext::kExcludeNone);
    m_backgroundOp->setSceneFilter(
        static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
            MHWRender::MSceneRender::kRenderShadedItems));

    m_sceneOp = new SceneRender(kSceneOpName);
    m_sceneOp->setEnabled(true);
    m_sceneOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    // TODO: For silhouette rendering - override the shader to be
    // useBackground.
    m_sceneOp->setClearMask(CLEAR_MASK_DEPTH);
    m_sceneOp->setSceneFilter(
        static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
            MHWRender::MSceneRender::kRenderShadedItems));

    m_selectOp = new SceneRender(kSelectOpName);
    m_selectOp->setEnabled(true);
    m_selectOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    m_selectOp->setClearMask(CLEAR_MASK_NONE);
    m_selectOp->setSceneFilter(
        static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
            MHWRender::MSceneRender::kRenderShadedItems));

    m_silhouetteOp = new SilhouetteRender(kSilhouetteOpName);
    m_silhouetteOp->setEnabled(false);

    m_wireframeOp = new SceneRender(kWireframeOpName);
    m_wireframeOp->setEnabled(true);
    m_wireframeOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    m_wireframeOp->setClearMask(CLEAR_MASK_NONE);
    m_wireframeOp->setSceneFilter(
        static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
            MHWRender::MSceneRender::kRenderUIItems));

    // Get the default set of operations.
    MHWRender::MRenderer::theRenderer()->getStandardViewportOperations(
        mOperations);

    // Clear the unneeded standard operations and place the new render
    // operations in a specific order.
    MHWRender::MRenderOverride::mOperations.replace(
        MHWRender::MRenderOperation::kStandardBackgroundName, m_backgroundOp);
    MHWRender::MRenderOverride::mOperations.replace(
        MHWRender::MRenderOperation::kStandardSceneName, m_sceneOp);

    MHWRender::MRenderOverride::mOperations.insertAfter(kSceneOpName,
                                                        m_selectOp);
    MHWRender::MRenderOverride::mOperations.insertAfter(kSelectOpName,
                                                        m_silhouetteOp);
    MHWRender::MRenderOverride::mOperations.insertAfter(kSilhouetteOpName,
                                                        m_wireframeOp);
}

RenderOverrideSilhouette::~RenderOverrideSilhouette() {
    m_backgroundOp = nullptr;
    m_sceneOp = nullptr;
    m_selectOp = nullptr;
    m_silhouetteOp = nullptr;
    m_wireframeOp = nullptr;

    RenderOverrideSilhouette::cleanup();

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
static MStatus update_parameters(
    MObjectHandle &out_globals_node, bool &out_silhouette_enable,
    float &out_silhouette_depth_offset, float &out_silhouette_width,
    float &out_silhouette_color_r, float &out_silhouette_color_g,
    float &out_silhouette_color_b, float &out_silhouette_alpha) {
    const bool verbose = false;
    MStatus status = MS::kSuccess;
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette::update_parameters");

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
            status = create_render_globals_node();
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
            "RenderOverrideSilhouette update_parameters: Could not find \"" +
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

    return MS::kSuccess;
}

// Perform any setup required before render operations are to be executed.
MStatus RenderOverrideSilhouette::setup(const MString &destination) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("RenderOverrideSilhouette::setup: start "
                      << destination.asChar());

    MStatus status = MS::kSuccess;

    // Track changes to the renderer and override for this viewport (nothing
    // will be printed unless mDebugOverride is true)
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

    // Get override values.
    status = update_parameters(m_globals_node, m_silhouette_enable,
                               m_silhouette_depth_offset, m_silhouette_width,
                               m_silhouette_color[0], m_silhouette_color[1],
                               m_silhouette_color[2], m_silhouette_alpha);
    CHECK_MSTATUS(status);

    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_backgroundOp=" << m_backgroundOp);
    if (m_backgroundOp) {
        m_image_plane_nodes.clear();
        status = add_all_image_planes(m_image_plane_nodes);
        MMSOLVER_MAYA_VRB(
            "RenderOverrideSilhouette::setup: m_image_plane_nodes.length()="
            << m_image_plane_nodes.length());
        CHECK_MSTATUS_AND_RETURN_IT(status);

        m_backgroundOp->setObjectSetOverride(&m_image_plane_nodes);
    }

    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_sceneOp=" << m_sceneOp);
    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_selectOp=" << m_selectOp);

    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_silhouetteOp=" << m_silhouetteOp);
    if (m_silhouetteOp) {
        m_silhouetteOp->setPanelName(destination);

        m_silhouetteOp->setEnabled(m_silhouette_enable);
        m_silhouetteOp->setSilhouetteDepthOffset(m_silhouette_depth_offset);
        m_silhouetteOp->setSilhouetteWidth(m_silhouette_width);
        m_silhouetteOp->setSilhouetteColor(m_silhouette_color[0],
                                           m_silhouette_color[1],
                                           m_silhouette_color[2]);
        m_silhouetteOp->setSilhouetteAlpha(m_silhouette_alpha);
    }

    // if (m_wireframeOp) {
    //     if (m_silhouette_enable) {
    //         m_wireframeOp->setDisplayModeOverride(
    //             MHWRender::MSceneRender::kNoDisplayModeOverride);
    //     } else {
    //         m_wireframeOp->setDisplayModeOverride(
    //             MHWRender::MSceneRender::kWireFrame);
    //     }
    // }

    MMSOLVER_MAYA_VRB(
        "RenderOverrideSilhouette::setup: m_wireframeOp=" << m_wireframeOp);

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

    return MRenderOverride::cleanup();
}

}  // namespace render
}  // namespace mmsolver
