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
 * - Add edge silhouette draw mode for specific objects, with blend factor.
 *
 */

#include "MMRendererMainOverride.h"
#include "QuadRenderEdgeDetect.h"
#include "QuadRenderBlend.h"
#include "QuadRenderInvert.h"
#include "MMRendererSceneRender.h"
#include "MMRendererHudRender.h"
#include "MMRendererPresentTarget.h"

#include <maya/MShaderManager.h>

namespace mmsolver {
namespace renderer {

// Set up operations
MMRendererMainOverride::MMRendererMainOverride(const MString &name)
        : MRenderOverride(name), m_ui_name("mmSolver Renderer") {
    // Remove any operations that already exist from Maya.
    mOperations.clear();

    // Initalise the operations for this override.
    for (auto i = 0; i < kNumberOfOps; ++i) {
        m_ops[i] = nullptr;
    }
    m_current_op = -1;
    m_panel_name.clear();

    // Init target information for the override.
    //
    // TODO: control the MSAA sample count (to allow users to change
    // quality)
    unsigned int sampleCount = 1; // 1 == no multi-sampling
    MHWRender::MRasterFormat colorFormat = MHWRender::kR8G8B8A8_UNORM;;
    MHWRender::MRasterFormat depthFormat = MHWRender::kD24S8;

    // Initalise the targets.
    for (auto i = 0; i < kTargetCount; ++i) {
        m_targets[i] = nullptr;
    }

    // 1st Color target
    m_target_override_names[kMyColorTarget] = MString(kMyColorTargetName);
    m_target_descs[kMyColorTarget] =
        new MHWRender::MRenderTargetDescription(
            m_target_override_names[kMyColorTarget],
            256, 256, sampleCount, colorFormat,
            /*arraySliceCount=*/ 0,
            /*isCubeMap=*/ false);

    // 1st Depth target
    m_target_override_names[kMyDepthTarget] = MString(kMyDepthTargetName);
    m_target_descs[kMyDepthTarget] =
        new MHWRender::MRenderTargetDescription(
            m_target_override_names[kMyDepthTarget],
            256, 256, sampleCount, depthFormat,
            /*arraySliceCount=*/ 0,
            /*isCubeMap=*/ false);

    // 2nd Color target
    m_target_override_names[kMyAuxColorTarget] = MString(kMyAuxColorTargetName);
    m_target_descs[kMyAuxColorTarget] =
        new MHWRender::MRenderTargetDescription(
            m_target_override_names[kMyAuxColorTarget],
            256, 256, sampleCount, colorFormat,
            /*arraySliceCount=*/ 0,
            /*isCubeMap=*/ false);
}

MMRendererMainOverride::~MMRendererMainOverride() {
    MHWRender::MRenderer *theRenderer = MHWRender::MRenderer::theRenderer();
    if (!theRenderer) {
        return;
    }

    // Release targets
    const MHWRender::MRenderTargetManager* targetManager =
        theRenderer->getRenderTargetManager();
    for (auto i=0; i<kTargetCount; ++i) {
        if (m_target_descs[i]) {
            delete m_target_descs[i];
            m_target_descs[i] = nullptr;
        }

        if (m_targets[i]) {
            if (targetManager) {
                targetManager->releaseRenderTarget(m_targets[i]);
            }
            m_targets[i] = nullptr;
        }
    }

    cleanup();

    // Delete all the operations. This will release any references to
    // other resources user per operation.
    for (auto i = 0; i < kNumberOfOps; ++i) {
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
        while (!m_ops[m_current_op] || !m_ops[m_current_op]->enabled()) {
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

MStatus
MMRendererMainOverride::updateRenderOperations() {
    if (m_ops[kPresentOp] != nullptr) {
        // render opations are already up-to-date.
        return MS::kSuccess;
    }

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
            MHWRender::MSceneRender::kShaded
            | MHWRender::MSceneRender::kWireFrame);

    // Operatation names
    m_op_names[kSceneDepthPass] = "mmRenderer_SceneRender_Standard";
    m_op_names[kSceneBackgroundPass] = "mmRenderer_SceneRender_Background";
    m_op_names[kSceneSelectionPass] = "mmRenderer_SceneRender_Select";
    m_op_names[kSceneWireframePass] = "mmRenderer_SceneRender_Wireframe";
    m_op_names[kPostOperation1] = "mmRenderer_PostOp1";
    m_op_names[kBlendOp] = "mmRenderer_EdgeDetectBlend";
    m_op_names[kPostOperation2] = "mmRenderer_PostOp2";
    m_op_names[kPresentOp] = "mmRenderer_PresentTarget";

    MMRendererSceneRender *sceneOp = nullptr;

    // Depth pass.
    sceneOp = new MMRendererSceneRender(m_op_names[kSceneDepthPass]);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    sceneOp->setExcludeTypes(MHWRender::MFrameContext::kExcludeImagePlane);
    sceneOp->setDisplayModeOverride(display_mode_shaded);
    // do not override objects to be drawn.
    sceneOp->setDoSelectable(false);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_depth);
    m_ops[kSceneDepthPass] = sceneOp;

    // Background pass.
    sceneOp = new MMRendererSceneRender(m_op_names[kSceneBackgroundPass]);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    // override drawn objects to only image planes under cameras.
    sceneOp->setDoSelectable(true);
    sceneOp->setDoBackground(true);
    sceneOp->setClearMask(clear_mask_all);
    m_ops[kSceneBackgroundPass] = sceneOp;

    // Select pass.
    sceneOp = new MMRendererSceneRender(m_op_names[kSceneSelectionPass]);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    // override drawn objects to all image planes not under cameras.
    sceneOp->setDoSelectable(true);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_none);
    m_ops[kSceneSelectionPass] = sceneOp;

    // Wireframe pass.
    sceneOp = new MMRendererSceneRender(m_op_names[kSceneWireframePass]);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderUIItems);
    sceneOp->setDisplayModeOverride(display_mode_wireframe_on_shaded);
    // do not override objects to be drawn.
    sceneOp->setDoSelectable(false);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_none);
    m_ops[kSceneWireframePass] = sceneOp;

    // Apply edge detect.
    auto quadOp = new QuadRenderEdgeDetect(m_op_names[kPostOperation1]);
    quadOp->setViewRectangle(rect);
    quadOp->setClearMask(clear_mask_none);
    m_ops[kPostOperation1] = quadOp;

    // Blend between 'edge detect' and 'non-edge detect'.
    auto blendOp = new QuadRenderBlend(m_op_names[kBlendOp]);
    blendOp->setViewRectangle(rect);
    blendOp->setClearMask(clear_mask_none);
    m_ops[kBlendOp] = blendOp;

    // Apply invert.
    auto invertOp = new QuadRenderInvert(m_op_names[kPostOperation2]);
    invertOp->setViewRectangle(rect);
    invertOp->setClearMask(clear_mask_none);
    m_ops[kPostOperation2] = invertOp;

    // A preset 2D HUD render operation
    m_ops[kHudPass] = new MMRendererHudRender();
    m_op_names[kHudPass] = (m_ops[kHudPass])->name();

    // "Present" operation which will display the target for
    // viewports.  Operation is a no-op for batch rendering as
    // there is no on-screen buffer to send the result to.
    m_ops[kPresentOp] = new MMRendererPresentTarget(m_op_names[kPresentOp]);
    return MS::kSuccess;
}

// Update the render targets that are required for the entire
// override.  References to these targets are set on the individual
// operations as required so that they will send their output to the
// appropriate location.
MStatus
MMRendererMainOverride::updateRenderTargets() {
    // MStreamUtils::stdOutStream()
    //     << "MMRendererMainOverride::updateRenderTargets\n";
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
    for (auto target_id = 0; target_id < kTargetCount; ++target_id) {
        // Update size value for all target descriptions kept
        m_target_descs[target_id]->setWidth(target_width);
        m_target_descs[target_id]->setHeight(target_height);
    }

    // Either acquire a new target if it didn't exist before, resize
    // the current target.
    const MHWRender::MRenderTargetManager *targetManager =
        theRenderer->getRenderTargetManager();
    if (!targetManager) {
        return MS::kFailure;
    }
    for (auto target_id = 0; target_id < kTargetCount; ++target_id) {
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
    //
    // This section will determine the outputs of each operation.  The
    // input of each operation is assumed to be the Maya provided
    // color and depth targets, but shaders may interally reference
    // specific render targets.

    // FIXME: If 'use_blend' is true the render targets only update
    // once and then fail. With 'use_blend' is false, the render
    // targets update as expected.
    auto use_blend = false;
    if (use_blend) {
        auto depthPassOp = (MMRendererSceneRender *) m_ops[kSceneDepthPass];
        if (depthPassOp) {
            depthPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto backgroundPassOp = (MMRendererSceneRender *) m_ops[kSceneBackgroundPass];
        if (backgroundPassOp) {
            // Note: Only render to the color target, depth is ignored.
            backgroundPassOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        auto selectSceneOp = (MMRendererSceneRender *) m_ops[kSceneSelectionPass];
        if (selectSceneOp) {
            selectSceneOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto wireframePassOp = (MMRendererSceneRender *) m_ops[kSceneWireframePass];
        if (wireframePassOp) {
            wireframePassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto quadOp = (QuadRenderEdgeDetect *) m_ops[kPostOperation1];
        if (quadOp) {
            quadOp->setEnabled(true);
            quadOp->setInputTarget(kMyColorTarget);
            quadOp->setRenderTargets(m_targets, kMyAuxColorTarget, 1);
        }

        auto blendOp = (QuadRenderBlend *) m_ops[kBlendOp];
        if (blendOp) {
            blendOp->setEnabled(true);
            blendOp->setInputTarget1(kMyColorTarget);
            blendOp->setInputTarget2(kMyAuxColorTarget);
            blendOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        auto invertOp = (QuadRenderInvert *) m_ops[kPostOperation2];
        if (invertOp) {
            invertOp->setEnabled(false);
            invertOp->setInputTarget(kMyColorTarget);
            invertOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        auto hudOp = (MMRendererHudRender *) m_ops[kHudPass];
        if (hudOp) {
            hudOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto presentOp = (MMRendererPresentTarget *) m_ops[kPresentOp];
        if (presentOp) {
            presentOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

    } else {
        auto depthPassOp = (MMRendererSceneRender *) m_ops[kSceneDepthPass];
        if (depthPassOp) {
            depthPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto backgroundPassOp = (MMRendererSceneRender *) m_ops[kSceneBackgroundPass];
        if (backgroundPassOp) {
            // Note: Only render to the color target, depth is ignored.
            backgroundPassOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        auto selectSceneOp = (MMRendererSceneRender *) m_ops[kSceneSelectionPass];
        if (selectSceneOp) {
            selectSceneOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto wireframePassOp = (MMRendererSceneRender *) m_ops[kSceneWireframePass];
        if (wireframePassOp) {
            wireframePassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto quadOp = (QuadRenderEdgeDetect *) m_ops[kPostOperation1];
        if (quadOp) {
            quadOp->setEnabled(false);
            quadOp->setInputTarget(0);
            quadOp->setRenderTargets(nullptr, 0, 0);
        }

        auto blendOp = (QuadRenderBlend *) m_ops[kBlendOp];
        if (blendOp) {
            blendOp->setEnabled(false);
            blendOp->setInputTarget1(0);
            blendOp->setInputTarget2(0);
            blendOp->setRenderTargets(nullptr, 0, 0);
        }

        auto invertOp = (QuadRenderInvert *) m_ops[kPostOperation2];
        if (invertOp) {
            invertOp->setEnabled(false);
            invertOp->setInputTarget(kMyColorTarget);
            invertOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        auto hudOp = (MMRendererHudRender *) m_ops[kHudPass];
        if (hudOp) {
            hudOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto presentOp = (MMRendererPresentTarget *) m_ops[kPresentOp];
        if (presentOp) {
            presentOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }
    }

    MStatus status = MS::kFailure;
    if (m_targets[kMyColorTarget]
        && m_targets[kMyDepthTarget]
        && m_targets[kMyAuxColorTarget]) {
        status = MS::kSuccess;
    }
    return status;
}

MStatus MMRendererMainOverride::setPanelNames(const MString &name) {
    // Set the name of the panel on operations which may use the panel
    // name to find out the associated M3dView.
    if (m_ops[kSceneDepthPass]) {
        auto op = (MMRendererSceneRender *) m_ops[kSceneDepthPass];
        op->setPanelName(name);
    }

    if (m_ops[kSceneBackgroundPass]) {
        auto op = (MMRendererSceneRender *) m_ops[kSceneBackgroundPass];
        op->setPanelName(name);
    }

    if (m_ops[kSceneSelectionPass]) {
        auto op = (MMRendererSceneRender *) m_ops[kSceneSelectionPass];
        op->setPanelName(name);
    }

    if (m_ops[kSceneWireframePass]) {
        auto op = (MMRendererSceneRender *) m_ops[kSceneWireframePass];
        op->setPanelName(name);
    }
    return MS::kSuccess;
}

MStatus
MMRendererMainOverride::setup(const MString &destination) {
    MStatus status = MS::kSuccess;

    // Construct the render operations.
    status = updateRenderOperations();
    CHECK_MSTATUS(status);

    // Update any of the render targets which will be required
    status = updateRenderTargets();
    CHECK_MSTATUS(status);

    // The panel name, used to get the current 3d view (M3dView).
    m_panel_name.set(destination.asChar());
    status = setPanelNames(m_panel_name);
    CHECK_MSTATUS(status);

    m_current_op = -1;
    return status;
}

// End of frame cleanup. Clears out any data on operations which may
// change from frame to frame (render target, output panel name etc).
MStatus
MMRendererMainOverride::cleanup() {
    if (m_ops[kPostOperation2]) {
        auto op = (QuadRenderInvert *) m_ops[kPostOperation2];
        op->setRenderTargets(nullptr, 0, 0);
    }

    // Reset the active view
    m_panel_name.clear();

    // Reset current operation
    m_current_op = -1;

    return MStatus::kSuccess;
}

} // namespace renderer
} // namespace mmsolver
