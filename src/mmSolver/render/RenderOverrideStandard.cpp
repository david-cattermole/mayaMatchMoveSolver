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

#include "RenderOverrideStandard.h"

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
    return MGlobal::executeCommand(kRendererStandardCreateNodeCommand,
                                   /*displayEnabled*/ true,
                                   /*undoEnabled*/ true);
}

// Callback for tracking renderer changes
void RenderOverrideStandard::renderer_change_func(const MString &panel_name,
                                                  const MString &old_renderer,
                                                  const MString &new_renderer,
                                                  void * /*client_data*/) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("Renderer changed for panel '"
                      << panel_name.asChar() << "'. "
                      << "New renderer is '" << new_renderer.asChar() << "', "
                      << "old was '" << old_renderer.asChar() << "'.");

    if (new_renderer == MM_RENDERER_STANDARD_NAME) {
        MStatus status = create_render_globals_node();
        CHECK_MSTATUS(status);
    }
}

// Callback for tracking render override changes
void RenderOverrideStandard::render_override_change_func(
    const MString &panel_name, const MString &old_renderer,
    const MString &new_renderer, void * /*client_data*/) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("Render override changed for panel '"
                      << panel_name.asChar() << "'. "
                      << "New override is '" << new_renderer.asChar() << "', "
                      << "old was '" << old_renderer.asChar() << "'.");

    if (new_renderer == MM_RENDERER_STANDARD_NAME) {
        MStatus status = create_render_globals_node();
        CHECK_MSTATUS(status);
    }
}

// Set up operations
RenderOverrideStandard::RenderOverrideStandard(const MString &name)
    : MRenderOverride(name)
    , m_ui_name(kRendererStandardUiName)
    , m_renderer_change_callback(0)
    , m_render_override_change_callback(0)
    , m_globals_node() {
    const MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_ERR(
            "MM Renderer Standard Render Override: "
            "Failed to get renderer.");
    }

    const MString kBackgroundOpName =
        MString("mmRendererStandard_backgroundPass");

    m_backgroundOp = new SceneRender(kBackgroundOpName);
    m_backgroundOp->setEnabled(true);
    m_backgroundOp->setBackgroundStyle(BackgroundStyle::kMayaDefault);
    m_backgroundOp->setClearMask(CLEAR_MASK_ALL);

    // Only draw imagePlane and plugin shapes.
    const auto draw_only_image_plane_object_types =
        static_cast<MUint64>(~(MHWRender::MFrameContext::kExcludeImagePlane |
                               MHWRender::MFrameContext::kExcludePluginShapes));
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

    // Get the default set of operations.
    MHWRender::MRenderer::theRenderer()->getStandardViewportOperations(
        mOperations);

    // Clear the unneeded standard operations and place the new render
    // operations in a specific order.
    MHWRender::MRenderOverride::mOperations.replace(
        MHWRender::MRenderOperation::kStandardBackgroundName, m_backgroundOp);
}

RenderOverrideStandard::~RenderOverrideStandard() {
    m_backgroundOp = nullptr;

    RenderOverrideStandard::cleanup();

    // Clean up callbacks
    if (m_renderer_change_callback) {
        MMessage::removeCallback(m_renderer_change_callback);
    }
    if (m_render_override_change_callback) {
        MMessage::removeCallback(m_render_override_change_callback);
    }
}

MHWRender::DrawAPI RenderOverrideStandard::supportedDrawAPIs() const {
    // The SilhouetteRender only works on OpenGL, so we cannot support
    // DirectX on Windows or Metal on Apple.
    return MHWRender::kOpenGLCoreProfile;
}

// Perform any setup required before render operations are to be executed.
MStatus RenderOverrideStandard::setup(const MString &destination) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("RenderOverrideStandard::setup: start "
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

    MMSOLVER_MAYA_VRB(
        "RenderOverrideStandard::setup: m_backgroundOp=" << m_backgroundOp);
    if (m_backgroundOp) {
        m_image_plane_nodes.clear();
        status = add_all_image_planes(m_image_plane_nodes);
        MMSOLVER_MAYA_VRB(
            "RenderOverrideStandard::setup: m_image_plane_nodes.length()="
            << m_image_plane_nodes.length());
        CHECK_MSTATUS_AND_RETURN_IT(status);

        m_backgroundOp->setObjectSetOverride(&m_image_plane_nodes);
    }

    MMSOLVER_MAYA_VRB("RenderOverrideStandard::setup: end "
                      << destination.asChar());
    return MRenderOverride::setup(destination);
}

// Perform any cleanup required following the execution of render
// operations.
//
// End of frame cleanup. Clears out any data on operations which may
// change from frame to frame (render target, output panel name etc).
MStatus RenderOverrideStandard::cleanup() {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("RenderOverrideStandard::cleanup: ");

    return MRenderOverride::cleanup();
}

}  // namespace render
}  // namespace mmsolver
