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

// Maya 2020 and Visual Studio 2017 causes a conflict with the 'min()'
// method on MBoundingBox.
//
// https://stackoverflow.com/questions/1394132/macro-and-member-function-conflict
#define NOMINMAX

#include "RenderOverride.h"

// Maya
#include <maya/MBoundingBox.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MUiMessage.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "HudRender.h"
#include "PresentTarget.h"
#include "QuadRenderBlend.h"
#include "QuadRenderCopy.h"
#include "QuadRenderEdgeDetect.h"
#include "QuadRenderInvert.h"
#include "SceneRender.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

// Set up operations
RenderOverride::RenderOverride(const MString &name)
    : MRenderOverride(name)
    , m_ui_name(kRendererUiName)
    , m_renderer_change_callback(0)
    , m_render_override_change_callback(0)
    , m_globals_node()
    , m_pull_updates(true)
    , m_wireframe_alpha(kWireframeAlphaDefault)
    , m_edge_thickness(kEdgeThicknessDefault)
    , m_edge_threshold(kEdgeThresholdDefault) {
    // Remove any operations that already exist from Maya.
    mOperations.clear();

    // // TODO: Ensure a node named 'mmRenderGlobals' exists in the scene.
    // nodeExistsAndIsType(MString nodeName, MFn::Type nodeType);

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
    unsigned int sampleCount = 1;  // 1 == no multi-sampling
    // TODO: Allow user to control the raster format from a list of choices.
    MHWRender::MRasterFormat colorFormat = MHWRender::kR8G8B8A8_UNORM;
    // MHWRender::kR16G16B16A16_FLOAT;
    // MHWRender::kR32G32B32A32_FLOAT;
    MHWRender::MRasterFormat depthFormat = MHWRender::kD32_FLOAT;
    // MHWRender::MRasterFormat depthFormat = MHWRender::kD24S8;

    // Initalise the targets.
    for (auto i = 0; i < kTargetCount; ++i) {
        m_targets[i] = nullptr;
    }

    const auto default_width = 256;
    const auto default_height = 256;
    const auto array_slice_count = 0;
    const bool is_cube_map = false;

    // 1st Color target
    m_target_override_names[kMyColorTarget] = MString(kMyColorTargetName);
    m_target_descs[kMyColorTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kMyColorTarget], default_width, default_height,
        sampleCount, colorFormat, array_slice_count, is_cube_map);

    // 1st Depth target
    m_target_override_names[kMyDepthTarget] = MString(kMyDepthTargetName);
    m_target_descs[kMyDepthTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kMyDepthTarget], default_width, default_height,
        sampleCount, depthFormat, array_slice_count, is_cube_map);

    // 2nd Color target
    m_target_override_names[kMyAuxColorTarget] = MString(kMyAuxColorTargetName);
    m_target_descs[kMyAuxColorTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kMyAuxColorTarget], default_width,
        default_height, sampleCount, colorFormat, array_slice_count,
        is_cube_map);
}

RenderOverride::~RenderOverride() {
    MHWRender::MRenderer *theRenderer = MHWRender::MRenderer::theRenderer();
    if (!theRenderer) {
        return;
    }

    // Release targets
    const MHWRender::MRenderTargetManager *targetManager =
        theRenderer->getRenderTargetManager();
    for (auto i = 0; i < kTargetCount; ++i) {
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

    // Clean up callbacks
    if (m_renderer_change_callback) {
        MMessage::removeCallback(m_renderer_change_callback);
    }
    if (m_render_override_change_callback) {
        MMessage::removeCallback(m_render_override_change_callback);
    }
}

// What type of Draw APIs are supported?
//
// All of them; OpenGL, DirectX, etc.
MHWRender::DrawAPI RenderOverride::supportedDrawAPIs() const {
    return MHWRender::kAllDevices;
}

bool RenderOverride::startOperationIterator() {
    m_current_op = 0;
    return true;
}

MHWRender::MRenderOperation *RenderOverride::renderOperation() {
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

bool RenderOverride::nextRenderOperation() {
    m_current_op++;
    return m_current_op < kNumberOfOps;
}

// Read node plug attributes and set the values.
MStatus RenderOverride::updateParameters() {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::updateParameters: ");

    MStatus status = MS::kSuccess;
    if (!m_pull_updates) {
        return status;
    }

    status = MS::kFailure;
    if (!m_globals_node.isValid()) {
        // Get the node and cache the handle in an 'MObjectHandle'
        // instance.
        MObject node_obj;
        MString node_name = "mmRenderGlobals1";
        status = getAsObject(node_name, node_obj);

        if (!node_obj.isNull()) {
            m_globals_node = node_obj;
        } else {
            // Could not find a valid render globals node.
            // CHECK_MSTATUS(status);
            return status;
        }
    }

    MObject node_obj = m_globals_node.object();
    MFnDependencyNode depends_node(node_obj, &status);
    CHECK_MSTATUS(status);

    bool want_networked_plug = true;
    MPlug render_mode_plug =
        depends_node.findPlug("renderMode", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status != MStatus::kSuccess) {
        m_render_mode = RenderMode::kFour;
    } else {
        m_render_mode = static_cast<RenderMode>(render_mode_plug.asShort());
    }
    MMSOLVER_VRB("RenderOverride mode: " << static_cast<short>(m_render_mode));

    MPlug render_format_plug =
        depends_node.findPlug("renderFormat", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        short value = render_format_plug.asShort();
        m_render_format = static_cast<RenderFormat>(value);
    }
    MMSOLVER_VRB("RenderOverride render_format: "
                 << static_cast<short>(m_render_format));

    MPlug wire_alpha_plug =
        depends_node.findPlug("wireframeAlpha", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        m_wireframe_alpha = wire_alpha_plug.asDouble();
    }

    MPlug edge_thickness_plug =
        depends_node.findPlug("edgeThickness", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        m_edge_thickness = edge_thickness_plug.asDouble();
    }

    MPlug edge_threshold_plug =
        depends_node.findPlug("edgeThreshold", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        m_edge_threshold = edge_threshold_plug.asDouble();
    }

    return MS::kSuccess;
}

MStatus RenderOverride::updateRenderOperations() {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::updateRenderOperations: ");

    if (m_ops[kPresentOp] != nullptr) {
        // render operations are already up-to-date.
        return MS::kSuccess;
    }

    // Create operations for the first time.
    MFloatPoint rect;
    rect[0] = 0.0f;
    rect[1] = 0.0f;
    rect[2] = 1.0f;
    rect[3] = 1.0f;

    // Clear Masks
    auto clear_mask_none =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearNone);
    auto clear_mask_all =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearAll);
    auto clear_mask_depth =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearDepth);

    // Display modes
    auto display_mode_shaded =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded);
    auto display_mode_wireframe =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kWireFrame);

    // Operation names
    m_op_names[kSceneDepthPass] = "mmRenderer_SceneRender_DepthOnly";
    m_op_names[kSceneBackgroundPass] = "mmRenderer_SceneRender_Background";
    m_op_names[kSceneSelectionPass] = "mmRenderer_SceneRender_Select";
    m_op_names[kCopyOp] = "mmRenderer_Copy";
    m_op_names[kSceneWireframePass] = "mmRenderer_SceneRender_Wireframe";
    m_op_names[kEdgeDetectOp] = "mmRenderer_EdgeDetectOp1";
    m_op_names[kWireframeBlendOp] = "mmRenderer_WireframeBlend";
    m_op_names[kInvertOp] = "mmRenderer_InvertOp2";
    m_op_names[kSceneManipulatorPass] = "mmRenderer_SceneRender_Manipulator";
    m_op_names[kPresentOp] = "mmRenderer_PresentTarget";

    SceneRender *sceneOp = nullptr;

    // Depth pass.
    sceneOp = new SceneRender(m_op_names[kSceneDepthPass]);
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
    sceneOp = new SceneRender(m_op_names[kSceneBackgroundPass]);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    // override drawn objects to only image planes under cameras.
    sceneOp->setDoSelectable(true);
    sceneOp->setDoBackground(true);
    sceneOp->setClearMask(clear_mask_all);
    m_ops[kSceneBackgroundPass] = sceneOp;

    // Select pass.
    sceneOp = new SceneRender(m_op_names[kSceneSelectionPass]);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    // override drawn objects to all image planes not under cameras.
    sceneOp->setDoSelectable(true);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_none);
    m_ops[kSceneSelectionPass] = sceneOp;

    // Copy select pass to another target for blending later.
    auto copyOp = new QuadRenderCopy(m_op_names[kCopyOp]);
    copyOp->setViewRectangle(rect);
    copyOp->setClearMask(clear_mask_none);
    m_ops[kCopyOp] = copyOp;

    // Wireframe pass.
    sceneOp = new SceneRender(m_op_names[kSceneWireframePass]);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderUIItems);
    sceneOp->setExcludeTypes(MHWRender::MFrameContext::kExcludeManipulators);
    sceneOp->setDisplayModeOverride(display_mode_wireframe);
    // do not override objects to be drawn.
    sceneOp->setDoSelectable(false);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_none);
    m_ops[kSceneWireframePass] = sceneOp;

    // Apply edge detect.
    auto edgeDetectOp = new QuadRenderEdgeDetect(m_op_names[kEdgeDetectOp]);
    edgeDetectOp->setViewRectangle(rect);
    edgeDetectOp->setClearMask(clear_mask_none);
    edgeDetectOp->setThreshold(static_cast<float>(m_edge_threshold));
    edgeDetectOp->setThickness(static_cast<float>(m_edge_thickness));
    m_ops[kEdgeDetectOp] = edgeDetectOp;

    // Blend between 'no-wireframe' and 'wireframe'.
    auto wireBlendOp = new QuadRenderBlend(m_op_names[kWireframeBlendOp]);
    wireBlendOp->setViewRectangle(rect);
    wireBlendOp->setClearMask(clear_mask_none);
    wireBlendOp->setBlend(static_cast<float>(m_wireframe_alpha));
    m_ops[kWireframeBlendOp] = wireBlendOp;

    // Apply invert.
    auto invertOp = new QuadRenderInvert(m_op_names[kInvertOp]);
    invertOp->setViewRectangle(rect);
    invertOp->setClearMask(clear_mask_none);
    m_ops[kInvertOp] = invertOp;

    // Manipulators pass.
    sceneOp = new SceneRender(m_op_names[kSceneManipulatorPass]);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderUIItems);
    sceneOp->setExcludeTypes(~MHWRender::MFrameContext::kExcludeManipulators);
    sceneOp->setDoSelectable(false);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_none);
    m_ops[kSceneManipulatorPass] = sceneOp;

    // A preset 2D HUD render operation
    auto hudOp = new HudRender();
    m_ops[kHudPass] = hudOp;
    m_op_names[kHudPass] = hudOp->name();

    // "Present" operation which will display the target for
    // viewports.  Operation is a no-op for batch rendering as
    // there is no on-screen buffer to send the result to.
    auto presentOp = new PresentTarget(m_op_names[kPresentOp]);
    m_ops[kPresentOp] = presentOp;
    return MS::kSuccess;
}

// Update the render targets that are required for the entire
// override.  References to these targets are set on the individual
// operations as required so that they will send their output to the
// appropriate location.
MStatus RenderOverride::updateRenderTargets() {
    MStatus status = MS::kSuccess;

    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::updateRenderTargets");

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
        // TODO: Get and set the multi-sample count.
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
    // color and depth targets, but shaders may internally reference
    // specific render targets.

    if (m_render_mode == RenderMode::kZero) {
        MMSOLVER_VRB("RenderOverride::mode = ZERO");
        // Blend edge detect on/off.

        // Draw scene (without image plane) into the depth channel.
        auto depthPassOp = dynamic_cast<SceneRender *>(m_ops[kSceneDepthPass]);
        if (depthPassOp) {
            depthPassOp->setEnabled(true);
            depthPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw viewport background (with image plane).
        auto backgroundPassOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneBackgroundPass]);
        if (backgroundPassOp) {
            backgroundPassOp->setEnabled(true);
            // Note: Only render to the color target, depth is ignored.
            backgroundPassOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        // Allow selection of objects.
        auto selectSceneOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneSelectionPass]);
        if (selectSceneOp) {
            selectSceneOp->setEnabled(true);
            selectSceneOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw edge detection.
        auto edgeDetectOp =
            dynamic_cast<QuadRenderEdgeDetect *>(m_ops[kEdgeDetectOp]);
        if (edgeDetectOp) {
            edgeDetectOp->setEnabled(true);
            edgeDetectOp->setInputTarget(kMyDepthTarget);
            edgeDetectOp->setRenderTargets(m_targets, kMyColorTarget, 1);
            edgeDetectOp->setThreshold(static_cast<float>(m_edge_threshold));
            edgeDetectOp->setThickness(static_cast<float>(m_edge_thickness));
        }

        // Copy kMyColorTarget to kMyAuxColorTarget.
        auto copyOp = dynamic_cast<QuadRenderCopy *>(m_ops[kCopyOp]);
        if (copyOp) {
            copyOp->setEnabled(true);
            copyOp->setInputTarget(kMyColorTarget);
            copyOp->setRenderTargets(m_targets, kMyAuxColorTarget, 1);
        }

        // Render wireframe into kMyColorTarget.
        auto wireframePassOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneWireframePass]);
        if (wireframePassOp) {
            wireframePassOp->setEnabled(true);
            wireframePassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Blend between kMyColorTarget and kMyAuxColorTarget, and output
        // to kMyColorTarget.
        auto wireBlendOp =
            dynamic_cast<QuadRenderBlend *>(m_ops[kWireframeBlendOp]);
        if (wireBlendOp) {
            wireBlendOp->setEnabled(true);
            wireBlendOp->setInputTarget1(kMyColorTarget);
            wireBlendOp->setInputTarget2(kMyAuxColorTarget);
            wireBlendOp->setRenderTargets(m_targets, kMyColorTarget, 1);
            wireBlendOp->setBlend(static_cast<float>(m_wireframe_alpha));
        }

        // Invert kMyColorTarget image, and output to kMyColorTarget.
        auto invertOp = dynamic_cast<QuadRenderInvert *>(m_ops[kInvertOp]);
        if (invertOp) {
            invertOp->setEnabled(false);
        }

        // Draw manipulators over the top of all objects.
        auto manipulatorPassOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneManipulatorPass]);
        if (manipulatorPassOp) {
            manipulatorPassOp->setEnabled(true);
            manipulatorPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw the HUD on kMyColorTarget.
        auto hudOp = dynamic_cast<HudRender *>(m_ops[kHudPass]);
        if (hudOp) {
            hudOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Display kMyColorTarget to the screen.
        auto presentOp = dynamic_cast<PresentTarget *>(m_ops[kPresentOp]);
        if (presentOp) {
            presentOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

    } else if (m_render_mode == RenderMode::kOne) {
        // Blending wireframes.
        MMSOLVER_VRB("RenderOverride::mode = ONE");

        auto depthPassOp = dynamic_cast<SceneRender *>(m_ops[kSceneDepthPass]);
        if (depthPassOp) {
            depthPassOp->setEnabled(true);
            depthPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto backgroundPassOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneBackgroundPass]);
        if (backgroundPassOp) {
            backgroundPassOp->setEnabled(true);
            // Note: Only render to the color target, depth is ignored.
            backgroundPassOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        auto selectSceneOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneSelectionPass]);
        if (selectSceneOp) {
            selectSceneOp->setEnabled(true);
            selectSceneOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto edgeDetectOp =
            dynamic_cast<QuadRenderEdgeDetect *>(m_ops[kEdgeDetectOp]);
        if (edgeDetectOp) {
            edgeDetectOp->setEnabled(false);
            edgeDetectOp->setInputTarget(kMyDepthTarget);
            edgeDetectOp->setRenderTargets(m_targets, kMyColorTarget, 1);
            edgeDetectOp->setThreshold(static_cast<float>(m_edge_threshold));
            edgeDetectOp->setThickness(static_cast<float>(m_edge_thickness));
        }

        auto copyOp = dynamic_cast<QuadRenderCopy *>(m_ops[kCopyOp]);
        if (copyOp) {
            copyOp->setEnabled(true);
            copyOp->setInputTarget(kMyColorTarget);
            copyOp->setRenderTargets(m_targets, kMyAuxColorTarget, 1);
        }

        auto wireframePassOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneWireframePass]);
        if (wireframePassOp) {
            wireframePassOp->setEnabled(true);
            wireframePassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto wireBlendOp =
            dynamic_cast<QuadRenderBlend *>(m_ops[kWireframeBlendOp]);
        if (wireBlendOp) {
            wireBlendOp->setEnabled(true);
            wireBlendOp->setInputTarget1(kMyColorTarget);
            wireBlendOp->setInputTarget2(kMyAuxColorTarget);
            wireBlendOp->setRenderTargets(m_targets, kMyColorTarget, 1);
            wireBlendOp->setBlend(static_cast<float>(m_wireframe_alpha));
        }

        auto invertOp = dynamic_cast<QuadRenderInvert *>(m_ops[kInvertOp]);
        if (invertOp) {
            invertOp->setEnabled(false);
        }

        // Draw manipulators over the top of all objects.
        auto manipulatorPassOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneManipulatorPass]);
        if (manipulatorPassOp) {
            manipulatorPassOp->setEnabled(true);
            manipulatorPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto hudOp = dynamic_cast<HudRender *>(m_ops[kHudPass]);
        if (hudOp) {
            hudOp->setEnabled(true);
            hudOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto presentOp = dynamic_cast<PresentTarget *>(m_ops[kPresentOp]);
        if (presentOp) {
            presentOp->setEnabled(true);
            presentOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

    } else {
        // No blending or post operations.
        MMSOLVER_VRB("RenderOverride::renderMode = RenderMode::kFour");

        auto depthPassOp = dynamic_cast<SceneRender *>(m_ops[kSceneDepthPass]);
        if (depthPassOp) {
            depthPassOp->setEnabled(true);
            depthPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto backgroundPassOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneBackgroundPass]);
        if (backgroundPassOp) {
            backgroundPassOp->setEnabled(true);
            // Note: Only render to the color target, depth is ignored.
            backgroundPassOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        auto selectSceneOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneSelectionPass]);
        if (selectSceneOp) {
            selectSceneOp->setEnabled(true);
            selectSceneOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto copyOp = dynamic_cast<QuadRenderCopy *>(m_ops[kCopyOp]);
        if (copyOp) {
            copyOp->setEnabled(false);
            copyOp->setInputTarget(0);
            copyOp->setRenderTargets(nullptr, 0, 0);
        }

        auto wireframePassOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneWireframePass]);
        if (wireframePassOp) {
            wireframePassOp->setEnabled(true);
            wireframePassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto edgeDetectOp =
            dynamic_cast<QuadRenderEdgeDetect *>(m_ops[kEdgeDetectOp]);
        if (edgeDetectOp) {
            edgeDetectOp->setEnabled(false);
            edgeDetectOp->setInputTarget(0);
            edgeDetectOp->setRenderTargets(nullptr, 0, 0);
            edgeDetectOp->setThreshold(static_cast<float>(m_edge_threshold));
            edgeDetectOp->setThickness(static_cast<float>(m_edge_thickness));
        }

        auto wireBlendOp =
            dynamic_cast<QuadRenderBlend *>(m_ops[kWireframeBlendOp]);
        if (wireBlendOp) {
            wireBlendOp->setEnabled(false);
            wireBlendOp->setInputTarget1(0);
            wireBlendOp->setInputTarget2(0);
            wireBlendOp->setRenderTargets(nullptr, 0, 0);
            wireBlendOp->setBlend(static_cast<float>(m_wireframe_alpha));
        }

        auto edgeBlendOp =
            dynamic_cast<QuadRenderBlend *>(m_ops[kWireframeBlendOp]);
        if (edgeBlendOp) {
            edgeBlendOp->setEnabled(false);
            edgeBlendOp->setInputTarget1(0);
            edgeBlendOp->setInputTarget2(0);
            edgeBlendOp->setRenderTargets(nullptr, 0, 0);
            edgeBlendOp->setBlend(static_cast<float>(m_wireframe_alpha));
        }

        auto invertOp = dynamic_cast<QuadRenderInvert *>(m_ops[kInvertOp]);
        if (invertOp) {
            invertOp->setEnabled(false);
            invertOp->setInputTarget(kMyColorTarget);
            invertOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        auto manipulatorPassOp =
            dynamic_cast<SceneRender *>(m_ops[kSceneManipulatorPass]);
        if (manipulatorPassOp) {
            manipulatorPassOp->setEnabled(true);
            manipulatorPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto hudOp = dynamic_cast<HudRender *>(m_ops[kHudPass]);
        if (hudOp) {
            hudOp->setEnabled(true);
            hudOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto presentOp = dynamic_cast<PresentTarget *>(m_ops[kPresentOp]);
        if (presentOp) {
            presentOp->setEnabled(true);
            presentOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }
    }

    status = MS::kFailure;
    if (m_targets[kMyColorTarget] && m_targets[kMyDepthTarget] &&
        m_targets[kMyAuxColorTarget]) {
        status = MS::kSuccess;
    }
    return status;
}

MStatus RenderOverride::setPanelNames(const MString &name) {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::setPanelNames: " << name.asChar());

    // Set the name of the panel on operations which may use the panel
    // name to find out the associated M3dView.
    if (m_ops[kSceneDepthPass]) {
        auto op = dynamic_cast<SceneRender *>(m_ops[kSceneDepthPass]);
        op->setPanelName(name);
    }

    if (m_ops[kSceneBackgroundPass]) {
        auto op = dynamic_cast<SceneRender *>(m_ops[kSceneBackgroundPass]);
        op->setPanelName(name);
    }

    if (m_ops[kSceneSelectionPass]) {
        auto op = dynamic_cast<SceneRender *>(m_ops[kSceneSelectionPass]);
        op->setPanelName(name);
    }

    if (m_ops[kSceneWireframePass]) {
        auto op = dynamic_cast<SceneRender *>(m_ops[kSceneWireframePass]);
        op->setPanelName(name);
    }

    if (m_ops[kSceneManipulatorPass]) {
        auto op = dynamic_cast<SceneRender *>(m_ops[kSceneManipulatorPass]);
        op->setPanelName(name);
    }
    return MS::kSuccess;
}

MStatus RenderOverride::setup(const MString &destination) {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::setup: " << destination.asChar());

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
    updateParameters();

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
MStatus RenderOverride::cleanup() {
    const bool verbose = false;
    MMSOLVER_VRB("RenderOverride::cleanup: ");

    // Reset the active view
    m_panel_name.clear();

    // Reset current operation
    m_current_op = -1;

    return MStatus::kSuccess;
}

// Callback for tracking renderer changes
void RenderOverride::renderer_change_func(const MString &panel_name,
                                          const MString &old_renderer,
                                          const MString &new_renderer,
                                          void * /*client_data*/) {
    const bool verbose = false;
    MMSOLVER_VRB("Renderer changed for panel '"
                 << panel_name.asChar() << "'. "
                 << "New renderer is '" << new_renderer.asChar() << "', "
                 << "old was '" << old_renderer.asChar() << "'.");
}

// Callback for tracking render override changes
void RenderOverride::render_override_change_func(const MString &panel_name,
                                                 const MString &old_renderer,
                                                 const MString &new_renderer,
                                                 void * /*client_data*/) {
    const bool verbose = false;
    // TODO: When the 'new_renderer' is MM_RENDERER_NAME, we must forcibly
    //  create a new 'mmRenderGlobals' node.
    MMSOLVER_VRB("Render override changed for panel '"
                 << panel_name.asChar() << "'. "
                 << "New override is '" << new_renderer.asChar() << "', "
                 << "old was '" << old_renderer.asChar() << "'.");
}

}  // namespace render
}  // namespace mmsolver
