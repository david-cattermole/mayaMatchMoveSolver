/*
 * Copyright (C) 2021 David Cattermole.
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
 * TODO:
 *
 * - Add blend factor between wireframe on shaded or not.
 *
 * - Add edge silhouette draw mode for specific objects.
 *
 */

#include "MMRendererMainOverride.h"
#include "MMRendererQuadRender.h"
#include "MMRendererSceneRender.h"
#include "MMRendererHudRender.h"
#include "MMRendererPresentTarget.h"

#include <maya/MShaderManager.h>

// Set up operations
MMRendererMainOverride::MMRendererMainOverride(const MString &name)
        : MRenderOverride(name), m_ui_name("mmSolver Renderer") {
    // Remove any operations that already exist from Maya.
    mOperations.clear();

    // Initalise the operations for this override.
    for (auto i = 0; i < kNumberOfOps; i++) {
        m_ops[i] = nullptr;
    }
    m_current_op = -1;
    m_panel_name.clear();

    // Init target information for the override.
    //
    // TODO: control the MSAA sample count (to allow users to change
    // quality)
    unsigned int sampleCount = 4; // 1 == no multi-sampling
    MHWRender::MRasterFormat colorFormat = MHWRender::kR32G32B32A32_FLOAT;
    MHWRender::MRasterFormat depthFormat = MHWRender::kD24S8;

    // Color target
    m_target_override_names[kMyColorTarget] = MString("mmRenderer_ColorTarget");
    m_target_descs[kMyColorTarget] =
            new MHWRender::MRenderTargetDescription(
                    m_target_override_names[kMyColorTarget],
                    256, 256, sampleCount, colorFormat,
                    /*arraySliceCount=*/ 0,
                    /*isCubeMap=*/ false);
    m_targets[kMyColorTarget] = NULL;

    // Depth target
    m_target_override_names[kMyDepthTarget] = MString("mmRenderer_DepthTarget");
    m_target_descs[kMyDepthTarget] =
            new MHWRender::MRenderTargetDescription(
                    m_target_override_names[kMyDepthTarget],
                    256, 256, sampleCount, depthFormat,
                    /*arraySliceCount=*/ 0,
                    /*isCubeMap=*/ false);
    m_targets[kMyDepthTarget] = NULL;
}


MMRendererMainOverride::~MMRendererMainOverride() {
    cleanup();

    // Delete all the operations. This will release any references to
    // other resources user per operation.
    for (auto i = 0; i < kNumberOfOps; i++) {
        delete m_ops[i];
        m_ops[i] = nullptr;
    }
}

// What type of Draw APIs are supported?
//
// All of them; OpenGL, DirectX, etc.
MHWRender::DrawAPI
MMRendererMainOverride::supportedDrawAPIs() const {
    return MHWRender::kAllDevices;
}

bool
MMRendererMainOverride::startOperationIterator() {
    m_current_op = 0;
    return true;
}

MHWRender::MRenderOperation *
MMRendererMainOverride::renderOperation() {
    if (m_current_op >= 0 && m_current_op < kNumberOfOps) {
        while (!m_ops[m_current_op]) {
            m_current_op++;
            if (m_current_op >= kNumberOfOps) {
                return nullptr;
            }
        }
        if (m_ops[m_current_op]) {
            return m_ops[m_current_op];
        }
    }
    return nullptr;
}

bool
MMRendererMainOverride::nextRenderOperation() {
    m_current_op++;
    if (m_current_op < kNumberOfOps) {
        return true;
    }
    return false;
}

// Update the render targets that are required for the entire
// override.  References to these targets are set on the individual
// operations as required so that they will send their output to the
// appropriate location.
MStatus
MMRendererMainOverride::updateRenderTargets() {
    MHWRender::MRenderer *theRenderer = MHWRender::MRenderer::theRenderer();
    if (!theRenderer) {
        return MS::kFailure;
    }

    // Get the current output target size as specified by the
    // renderer. If it has changed then the targets need to be resized
    // to match.
    uint32_t target_width = 0;
    uint32_t target_height = 0;
    theRenderer->outputTargetSize(target_width, target_height);

    // Either acquire a new target if it didn't exist before, resize
    // the current target.
    const MHWRender::MRenderTargetManager *targetManager =
        theRenderer->getRenderTargetManager();
    if (!targetManager) {
        return MS::kFailure;
    }
    for (uint32_t target_id = 0; target_id < kTargetCount; ++target_id) {
        // Update size value for all target descriptions kept
        m_target_descs[target_id]->setWidth(target_width);
        m_target_descs[target_id]->setHeight(target_height);

        // Create a new target.
        if (!m_targets[target_id]) {
            m_targets[target_id] = targetManager->acquireRenderTarget(
                *(m_target_descs[target_id]));
        } else {
            // "Update" using a description will resize as necessary.
            m_targets[target_id]->updateDescription(
                *(m_target_descs[target_id]));
        }
    }

    // Update the render targets on the individual operations.
    auto standardPassOp = (MMRendererSceneRender *) m_ops[kSceneStandardPass];
    if (standardPassOp) {
        standardPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
    }

    auto backgroundPassOp = (MMRendererSceneRender *) m_ops[kSceneBackgroundPass];
    if (backgroundPassOp) {
        // Note: Only render to the color target, depth is ignored.
        backgroundPassOp->setRenderTargets(m_targets, kMyColorTarget, 1);
    }

    auto selectSceneOp = (MMRendererSceneRender *) m_ops[kSceneSelectPass];
    if (selectSceneOp) {
        selectSceneOp->setRenderTargets(m_targets, kMyColorTarget, 2);
    }

    auto wireframePassOp = (MMRendererSceneRender *) m_ops[kSceneWireframePass];
    if (wireframePassOp) {
        wireframePassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
    }

    auto hudOp = (MMRendererHudRender *) m_ops[kHudPass];
    if (hudOp) {
        hudOp->setRenderTargets(m_targets, kMyColorTarget, 2);
    }

    auto presentOp = (MMRendererPresentTarget *) m_ops[kPresentOp];
    if (presentOp) {
        presentOp->setRenderTargets(m_targets, kMyColorTarget, 2);
    }

    MStatus status = MS::kFailure;
    if (m_targets[kMyColorTarget] && m_targets[kMyDepthTarget]) {
        status = MS::kSuccess;
    }
    return status;
}


MStatus
MMRendererMainOverride::setup(const MString &destination) {
    MStatus status = MS::kSuccess;

    // The panel name, used to get the current 3d view (M3dView).
    m_panel_name.set(destination.asChar());

    if (m_ops[kPresentOp] == nullptr) {
        // Create operations for the first time.
        MFloatPoint rect;
        rect[0] = 0.0f;
        rect[1] = 0.0f;
        rect[2] = 1.0f;
        rect[3] = 1.0f;

        // Clear Masks
        auto clear_mask_none = static_cast<uint32_t>(
            MHWRender::MClearOperation::kClearNone);
        auto clear_mask_all = static_cast<uint32_t>(
            MHWRender::MClearOperation::kClearAll);
        auto clear_mask_depth = static_cast<uint32_t>(
            MHWRender::MClearOperation::kClearDepth);

        // Display modes
        auto display_mode_shaded =
            static_cast<MHWRender::MSceneRender::MDisplayMode>(
                MHWRender::MSceneRender::kShaded);
        auto display_mode_wireframe_on_shaded =
            static_cast<MHWRender::MSceneRender::MDisplayMode>(
                MHWRender::MSceneRender::kWireFrame
                | MHWRender::MSceneRender::kShaded);

        m_op_names[kSceneStandardPass] = "mmRenderer_SceneRender_Standard";
        m_op_names[kSceneBackgroundPass] = "mmRenderer_SceneRender_Background";
        m_op_names[kSceneSelectPass] = "mmRenderer_SceneRender_Select";
        m_op_names[kSceneWireframePass] = "mmRenderer_SceneRender_Wireframe";

        MMRendererSceneRender *sceneOp = nullptr;

        // Standard pass.
        //
        // Draw normal, exclude imageplane from depth rendering.
        //
        // The principle here is to draw the things we don't want to
        // shade for depth here and exclude the things we want to
        // draw. If a render item is in the depth buffer, it won't be
        // drawn later.
        sceneOp = new MMRendererSceneRender(m_op_names[kSceneStandardPass]);
        sceneOp->setViewRectangle(rect);
        sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
        sceneOp->setExcludeTypes(MHWRender::MFrameContext::kExcludeImagePlane);
        sceneOp->setDisplayModeOverride(display_mode_shaded);
        sceneOp->setDoSelectable(false);
        sceneOp->setDoBackground(false);
        sceneOp->setClearMask(clear_mask_depth);
        m_ops[kSceneStandardPass] = sceneOp;

        // Background pass.
        //
        // Draw both background and an imageplane in the viewport
        // here.
        //
        // The render targets used for this pass is only the colour,
        // so the depth is ignored.
        sceneOp = new MMRendererSceneRender(m_op_names[kSceneBackgroundPass]);
        sceneOp->setViewRectangle(rect);
        sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
        sceneOp->setDoSelectable(true);
        sceneOp->setDoBackground(true);
        sceneOp->setClearMask(clear_mask_all);
        m_ops[kSceneBackgroundPass] = sceneOp;

        // Select pass.
        //
        // Draw manip and excluded objects
        //
        // We want to use depth buffer to prevent drawing items we
        // wanted "hidden line". Notice that I allow free image plane
        // to be rendered normally here.
        sceneOp = new MMRendererSceneRender(m_op_names[kSceneSelectPass]);
        sceneOp->setViewRectangle(rect);
        sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
        sceneOp->setDoSelectable(true);
        sceneOp->setDoBackground(false);
        sceneOp->setClearMask(clear_mask_none);
        m_ops[kSceneSelectPass] = sceneOp;

        // Wireframe pass.
        sceneOp = new MMRendererSceneRender(m_op_names[kSceneWireframePass]);
        sceneOp->setViewRectangle(rect);
        sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderUIItems);
        sceneOp->setDisplayModeOverride(display_mode_wireframe_on_shaded);
        sceneOp->setDoSelectable(false);
        sceneOp->setDoBackground(false);
        sceneOp->setClearMask(clear_mask_none);
        m_ops[kSceneWireframePass] = sceneOp;

        // A preset 2D HUD render operation
        m_ops[kHudPass] = new MMRendererHudRender();
        m_op_names[kHudPass] = (m_ops[kHudPass])->name();

        // "Present" operation which will display the target for
        // viewports.  Operation is a no-op for batch rendering as
        // there is no on-screen buffer to send the result to.
        m_op_names[kPresentOp] = "mmRenderer_PresentTarget";
        m_ops[kPresentOp] = new MMRendererPresentTarget(m_op_names[kPresentOp]);
        m_op_names[kPresentOp] = (m_ops[kPresentOp])->name();
    }

    // Update any of the render targets which will be required
    status = updateRenderTargets();
    CHECK_MSTATUS(status);

    // Set the name of the panel on operations which may use the panel
    // name to find out the associated M3dView.
    if (m_ops[kSceneStandardPass]) {
        auto render_op = (MMRendererSceneRender *) m_ops[kSceneStandardPass];
        render_op->setPanelName(m_panel_name);
    }
    if (m_ops[kSceneBackgroundPass]) {
        auto render_op = (MMRendererSceneRender *) m_ops[kSceneBackgroundPass];
        render_op->setPanelName(m_panel_name);
    }
    if (m_ops[kSceneSelectPass]) {
        auto render_op = (MMRendererSceneRender *) m_ops[kSceneSelectPass];
        render_op->setPanelName(m_panel_name);
    }
    if (m_ops[kSceneWireframePass]) {
        auto render_op = (MMRendererSceneRender *) m_ops[kSceneWireframePass];
        render_op->setPanelName(m_panel_name);
    }
    m_current_op = -1;

    return status;
}

// End of frame cleanup. For now just clears out any data on
// operations which may change from frame to frame (render target,
// output panel name etc).
MStatus
MMRendererMainOverride::cleanup() {
    // Reset the active view
    m_panel_name.clear();

    // Reset current operation
    m_current_op = -1;
    return MStatus::kSuccess;
}
