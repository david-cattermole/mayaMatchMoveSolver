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

#include "RenderOverride.h"

// Maya
#include <maya/MFnDependencyNode.h>
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
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

// Set up operations
RenderOverride::RenderOverride(const MString &name)
    : MRenderOverride(name), m_ui_name(kRendererUiName) {
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_ERR(
            "MM Renderer RenderOverride: "
            "Failed to get renderer.");
    }

    // Create a new set of operations as required
    MHWRender::MRenderer::theRenderer()->getStandardViewportOperations(
        mOperations);

    const MString backgroundOpName = MString("mmRenderer_sceneBackground");
    m_backgroundOp = new SceneRender(backgroundOpName);
    m_backgroundOp->setEnabled(true);
    m_backgroundOp->setBackgroundStyle(BackgroundStyle::kMayaDefault);
    m_backgroundOp->setClearMask(CLEAR_MASK_ALL);
    m_backgroundOp->setExcludeTypes(MHWRender::MFrameContext::kExcludeNone);
    m_backgroundOp->setSceneFilter(
        static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
            MHWRender::MSceneRender::kRenderPreSceneUIItems |
            MHWRender::MSceneRender::kRenderShadedItems |
            MHWRender::MSceneRender::kRenderPostSceneUIItems));

    // By replacing the standard viewport background operation we are
    // able to "trick" the native Maya useBackground shader to
    // treating the output from our custom background as the
    // background for the assigned objects.
    mOperations.replace(MHWRender::MRenderOperation::kStandardBackgroundName,
                        m_backgroundOp);
}

RenderOverride::~RenderOverride() {
    m_backgroundOp = nullptr;

    RenderOverride::cleanup();
}

MHWRender::DrawAPI RenderOverride::supportedDrawAPIs() const {
    return MHWRender::kAllDevices;
}

// Perform any setup required before render operations are to be executed.
MStatus RenderOverride::setup(const MString &destination) {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::setup: start " << destination.asChar());

    MStatus status = MS::kSuccess;

    if (m_backgroundOp) {
        m_image_plane_nodes.clear();
        status = add_all_image_planes(m_image_plane_nodes);
        MMSOLVER_VRB("RenderOverride::setup: m_image_plane_nodes.length()="
                     << m_image_plane_nodes.length());
        CHECK_MSTATUS_AND_RETURN_IT(status);

        m_backgroundOp->setObjectSetOverride(&m_image_plane_nodes);
    }

    MMSOLVER_VRB("RenderOverride::setup: end " << destination.asChar());
    return MRenderOverride::setup(destination);
}

// Perform any cleanup required following the execution of render operations.
//
// End of frame cleanup. Clears out any data on operations which may
// change from frame to frame (render target, output panel name etc).
MStatus RenderOverride::cleanup() {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::cleanup: ");

    return MRenderOverride::cleanup();
}

}  // namespace render
}  // namespace mmsolver
