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
#include "EdgeDetectMode.h"
#include "HudRender.h"
#include "PresentTarget.h"
#include "QuadRenderBlend.h"
#include "QuadRenderCopy.h"
#include "QuadRenderEdgeDetect.h"
#include "RenderColorFormat.h"
#include "SceneRender.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

const MString kSceneDepthPassName = "mmRenderer_SceneRender_DepthOnly";
const MString kSceneBackgroundPassName = "mmRenderer_SceneRender_Background";
const MString kSceneSelectionPassName = "mmRenderer_SceneRender_Select";
const MString kEdgeDetectOpName = "mmRenderer_EdgeDetectOp";
const MString kEdgeCopyOpName = "mmRenderer_EdgeCopy";
const MString kSceneWireframePassName = "mmRenderer_SceneRender_Wireframe";
const MString kWireframeBlendOpName = "mmRenderer_WireframeBlend";
const MString kSceneManipulatorPassName = "mmRenderer_SceneRender_Manipulator";
const MString kPresentOpName = "mmRenderer_PresentTarget";

// Set up operations
RenderOverride::RenderOverride(const MString &name)
    : MRenderOverride(name)
    , m_ui_name(kRendererUiName)
    , m_renderer_change_callback(0)
    , m_render_override_change_callback(0)
    , m_globals_node()
    , m_pull_updates(true)
    , m_multi_sample_enable(false)
    , m_multi_sample_count(1)
    , m_wireframe_alpha(kWireframeAlphaDefault)
    , m_edge_detect_mode(kEdgeDetectModeDefault)
    , m_edge_thickness(kEdgeThicknessDefault)
    , m_edge_threshold(kEdgeThresholdDefault) {
    // Remove any operations that already exist from Maya.
    mOperations.clear();

    // Initialise the operations for this override.
    for (auto i = 0; i < PassesStart::kPassesStartCount; ++i) {
        m_ops_start[i] = nullptr;
    }
    for (auto i = 0; i < PassesLayer::kPassesLayerCount; ++i) {
        m_ops_layer[i] = nullptr;
    }
    for (auto i = 0; i < PassesEnd::kPassesEndCount; ++i) {
        m_ops_end[i] = nullptr;
    }
    m_current_pass = Pass::kUninitialized;
    m_current_op = -1;
    m_panel_name.clear();

    // Init target information for the override.
    MHWRender::MRasterFormat color_format = MHWRender::kR8G8B8A8_UNORM;
    MHWRender::MRasterFormat depth_format = MHWRender::kD32_FLOAT;
    // MHWRender::MRasterFormat depth_format = MHWRender::kD24S8;

    // Initialise the targets.
    for (auto i = 0; i < kTargetCount; ++i) {
        m_targets[i] = nullptr;
    }

    // Default values, width, height and samples will be over-written
    // by parameters, as needed.
    const auto sample_count = 1;  // 1 == no multi-sampling.
    const auto default_width = 256;
    const auto default_height = 256;
    const auto array_slice_count = 0;
    const auto is_cube_map = false;

    // 1st Color target
    m_target_override_names[kMyColorTarget] = MString(kMyColorTargetName);
    m_target_descs[kMyColorTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kMyColorTarget], default_width, default_height,
        sample_count, color_format, array_slice_count, is_cube_map);

    // 1st Depth target
    m_target_override_names[kMyDepthTarget] = MString(kMyDepthTargetName);
    m_target_descs[kMyDepthTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kMyDepthTarget], default_width, default_height,
        sample_count, depth_format, array_slice_count, is_cube_map);

    // 2nd Color target
    m_target_override_names[kMyAuxColorTarget] = MString(kMyAuxColorTargetName);
    m_target_descs[kMyAuxColorTarget] = new MHWRender::MRenderTargetDescription(
        m_target_override_names[kMyAuxColorTarget], default_width,
        default_height, sample_count, color_format, array_slice_count,
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

    RenderOverride::cleanup();

    // Delete all the operations. This will release any references to
    // other resources user per operation.
    for (auto i = 0; i < PassesStart::kPassesStartCount; ++i) {
        delete m_ops_start[i];
        m_ops_start[i] = nullptr;
    }
    for (auto i = 0; i < PassesLayer::kPassesLayerCount; ++i) {
        delete m_ops_layer[i];
        m_ops_layer[i] = nullptr;
    }
    for (auto i = 0; i < PassesEnd::kPassesEndCount; ++i) {
        delete m_ops_end[i];
        m_ops_end[i] = nullptr;
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
    m_current_pass = Pass::kStart;
    return true;
}

MHWRender::MRenderOperation *RenderOverride::getOperationFromList(
    int32_t &current_op, MRenderOperation **ops, const int32_t count) {
    if (current_op >= 0 && current_op < count) {
        while (!ops[current_op] || !ops[current_op]->enabled()) {
            current_op++;
            if (current_op >= count) {
                return nullptr;
            }
        }
        if (ops[current_op]) {
            return ops[current_op];
        }
    }
    return nullptr;
}

MHWRender::MRenderOperation *RenderOverride::renderOperation() {
    if (m_current_pass == Pass::kStart) {
        const auto count = PassesStart::kPassesStartCount;
        auto op = getOperationFromList(m_current_op, m_ops_start, count);
        if (op != nullptr) {
            return op;
        } else {
            m_current_pass = Pass::kLayer;
        }
    }

    if (m_current_pass == Pass::kLayer) {
        const auto count = PassesLayer::kPassesLayerCount;
        auto op = getOperationFromList(m_current_op, m_ops_layer, count);
        if (op != nullptr) {
            return op;
        } else {
            m_current_pass = Pass::kEnd;
        }
    }

    if (m_current_pass == Pass::kEnd) {
        const auto count = PassesEnd::kPassesEndCount;
        auto op = getOperationFromList(m_current_op, m_ops_end, count);
        if (op != nullptr) {
            return op;
        }
    }

    return nullptr;
}

bool RenderOverride::nextRenderOperation() {
    if (m_current_pass == Pass::kUninitialized) {
        return false;
    }

    m_current_op++;

    if (m_current_pass == Pass::kStart) {
        const auto count = PassesStart::kPassesStartCount;
        if (m_current_op >= count) {
            m_current_op = 0;
            m_current_pass = Pass::kLayer;
        }
    }

    if (m_current_pass == Pass::kLayer) {
        const auto count = PassesLayer::kPassesLayerCount;
        if (m_current_op >= count) {
            m_current_op = 0;
            m_current_pass = Pass::kEnd;
        }
    }

    if (m_current_pass == Pass::kEnd) {
        const auto count = PassesEnd::kPassesEndCount;
        if (m_current_op >= count) {
            m_current_op = -1;
            m_current_pass = Pass::kUninitialized;
        }
    }

    return m_current_op >= 0;
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
            //
            // TODO: Run a MEL/Python command callback that will
            // create a mmRenderGlobals node, when no node can be
            // found.
            return status;
        }
    }

    MObject globals_node_obj = m_globals_node.object();
    MFnDependencyNode depends_node(globals_node_obj, &status);
    CHECK_MSTATUS(status);

    if (!m_maya_hardware_globals_node.isValid()) {
        // Get the node and cache the handle in an 'MObjectHandle'
        // instance.
        MObject node_obj;
        MString node_name = "hardwareRenderingGlobals";
        status = getAsObject(node_name, node_obj);

        if (!node_obj.isNull()) {
            m_maya_hardware_globals_node = node_obj;
        } else {
            // Could not find a valid 'hardwareRenderingGlobals' node,
            // which should always succeed because that node always
            // exists in the Maya scene.
            return status;
        }
    }

    MObject maya_hardware_globals_node_obj =
        m_maya_hardware_globals_node.object();
    MFnDependencyNode maya_hardware_globals_depends_node(
        maya_hardware_globals_node_obj, &status);
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

    MPlug render_color_format_plug = depends_node.findPlug(
        "renderColorFormat", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        short value = render_color_format_plug.asShort();
        m_render_color_format = static_cast<RenderColorFormat>(value);
    }
    MMSOLVER_VRB("RenderOverride render_color_format: "
                 << static_cast<short>(m_render_color_format));

    m_multi_sample_enable = false;
    MPlug sample_enable_plug = maya_hardware_globals_depends_node.findPlug(
        "multiSampleEnable", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        m_multi_sample_enable = sample_enable_plug.asInt();
    }

    m_multi_sample_count = 1;
    if (m_multi_sample_enable) {
        MPlug sample_count_plug = maya_hardware_globals_depends_node.findPlug(
            "multiSampleCount", want_networked_plug, &status);
        CHECK_MSTATUS(status);
        if (status == MStatus::kSuccess) {
            m_multi_sample_count = sample_count_plug.asInt();
        }
    }

    MPlug wire_alpha_plug =
        depends_node.findPlug("wireframeAlpha", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        m_wireframe_alpha = wire_alpha_plug.asDouble();
    }

    MPlug edge_detect_mode_plug =
        depends_node.findPlug("edgeDetectMode", want_networked_plug, &status);
    CHECK_MSTATUS(status);
    if (status == MStatus::kSuccess) {
        short value = edge_detect_mode_plug.asShort();
        m_edge_detect_mode = static_cast<EdgeDetectMode>(value);
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

    if (m_ops_end[PassesEnd::kPresentOp] != nullptr) {
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

    // Draw these objects for transparency.
    auto wire_draw_object_types =
        ~(MHWRender::MFrameContext::kExcludeMeshes |
          MHWRender::MFrameContext::kExcludeNurbsCurves |
          MHWRender::MFrameContext::kExcludeNurbsSurfaces |
          MHWRender::MFrameContext::kExcludeSubdivSurfaces);

    // Draw all non-geometry normally.
    auto non_wire_draw_object_types =
        ((~wire_draw_object_types) |
         MHWRender::MFrameContext::kExcludeImagePlane |
         MHWRender::MFrameContext::kExcludePluginShapes);

    // What objects types to draw for depth buffer?
    auto depth_draw_object_types =
        wire_draw_object_types | MHWRender::MFrameContext::kExcludeImagePlane;

    // Draw image planes in the background always.
    auto bg_draw_object_types =
        ~(MHWRender::MFrameContext::kExcludeImagePlane |
          MHWRender::MFrameContext::kExcludePluginShapes);

    SceneRender *sceneOp = nullptr;

    // Depth pass.
    sceneOp = new SceneRender(kSceneDepthPassName);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    sceneOp->setExcludeTypes(depth_draw_object_types);
    sceneOp->setDisplayModeOverride(display_mode_shaded);
    // do not override objects to be drawn.
    sceneOp->setDoSelectable(false);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_depth);
    m_ops_start[PassesStart::kSceneDepthPass] = sceneOp;

    // Background pass.
    sceneOp = new SceneRender(kSceneBackgroundPassName);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    // sceneOp->setExcludeTypes(bg_draw_object_types);
    // override drawn objects to only image planes under cameras.
    sceneOp->setDoSelectable(true);
    sceneOp->setDoBackground(true);
    sceneOp->setClearMask(clear_mask_all);
    m_ops_start[PassesStart::kSceneBackgroundPass] = sceneOp;

    // Select pass.
    sceneOp = new SceneRender(kSceneSelectionPassName);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    // override drawn objects to all image planes not under cameras.
    sceneOp->setDoSelectable(true);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_none);
    m_ops_start[PassesStart::kSceneSelectionPass] = sceneOp;

    // Copy select pass to another target for blending later.
    auto copyOp = new QuadRenderCopy(kEdgeCopyOpName);
    copyOp->setViewRectangle(rect);
    copyOp->setClearMask(clear_mask_none);
    m_ops_layer[PassesLayer::kEdgeCopyOp] = copyOp;

    // Wireframe pass.
    sceneOp = new SceneRender(kSceneWireframePassName);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderUIItems);
    sceneOp->setExcludeTypes(wire_draw_object_types);
    sceneOp->setDisplayModeOverride(display_mode_wireframe);
    // do not override objects to be drawn.
    sceneOp->setDoSelectable(false);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_none);
    m_ops_layer[PassesLayer::kSceneWireframePass] = sceneOp;

    // Apply edge detect.
    auto edgeDetectOp = new QuadRenderEdgeDetect(kEdgeDetectOpName);
    edgeDetectOp->setViewRectangle(rect);
    edgeDetectOp->setClearMask(clear_mask_none);
    edgeDetectOp->setThreshold(static_cast<float>(m_edge_threshold));
    edgeDetectOp->setThickness(static_cast<float>(m_edge_thickness));
    m_ops_layer[PassesLayer::kEdgeDetectOp] = edgeDetectOp;

    // Blend between 'no-wireframe' and 'wireframe'.
    auto wireBlendOp = new QuadRenderBlend(kWireframeBlendOpName);
    wireBlendOp->setViewRectangle(rect);
    wireBlendOp->setClearMask(clear_mask_none);
    wireBlendOp->setBlend(static_cast<float>(m_wireframe_alpha));
    m_ops_layer[PassesLayer::kWireframeBlendOp] = wireBlendOp;

    // Manipulators pass.
    sceneOp = new SceneRender(kSceneManipulatorPassName);
    sceneOp->setViewRectangle(rect);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderUIItems);
    sceneOp->setExcludeTypes(non_wire_draw_object_types);
    sceneOp->setDoSelectable(false);
    sceneOp->setDoBackground(false);
    sceneOp->setClearMask(clear_mask_none);
    m_ops_end[PassesEnd::kSceneManipulatorPass] = sceneOp;

    // A preset 2D HUD render operation
    auto hudOp = new HudRender();
    m_ops_end[PassesEnd::kHudPass] = hudOp;

    // "Present" operation which will display the target for
    // viewports.  Operation is a no-op for batch rendering as
    // there is no on-screen buffer to send the result to.
    auto presentOp = new PresentTarget(kPresentOpName);
    m_ops_end[PassesEnd::kPresentOp] = presentOp;
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
        m_target_descs[target_id]->setMultiSampleCount(m_multi_sample_count);
    }

    // Set the bit-depth for color buffers.
    MHWRender::MRasterFormat color_format = MHWRender::kR8G8B8A8_UNORM;
    if (m_render_color_format == RenderColorFormat::kRGBA8BitInt) {
        color_format = MHWRender::kR8G8B8A8_UNORM;
    } else if (m_render_color_format == RenderColorFormat::kRGBA16BitFloat) {
        color_format = MHWRender::kR16G16B16A16_FLOAT;
    } else if (m_render_color_format == RenderColorFormat::kRGBA32BitFloat) {
        color_format = MHWRender::kR32G32B32A32_FLOAT;
    } else {
        MMSOLVER_ERR("Invalid RenderColorFormat given: "
                     << static_cast<short>(m_render_color_format));
    }
    m_target_descs[kMyColorTarget]->setRasterFormat(color_format);
    m_target_descs[kMyAuxColorTarget]->setRasterFormat(color_format);

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
        auto depthPassOp = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneDepthPass]);
        if (depthPassOp) {
            depthPassOp->setEnabled(true);
            depthPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw viewport background (with image plane).
        auto backgroundPassOp = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneBackgroundPass]);
        if (backgroundPassOp) {
            backgroundPassOp->setEnabled(true);
            // Note: Only render to the color target, depth is ignored.
            backgroundPassOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        // Allow selection of objects.
        auto selectSceneOp = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneSelectionPass]);
        if (selectSceneOp) {
            selectSceneOp->setEnabled(true);
            selectSceneOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw edge detection.
        auto edgeDetectOp = dynamic_cast<QuadRenderEdgeDetect *>(
            m_ops_layer[PassesLayer::kEdgeDetectOp]);
        if (edgeDetectOp) {
            edgeDetectOp->setEnabled(true);
            edgeDetectOp->setInputColorTarget(kMyColorTarget);
            edgeDetectOp->setInputDepthTarget(kMyDepthTarget);
            edgeDetectOp->setRenderTargets(m_targets, kMyColorTarget, 1);
            edgeDetectOp->setThreshold(static_cast<float>(m_edge_threshold));
            edgeDetectOp->setThickness(static_cast<float>(m_edge_thickness));
            edgeDetectOp->setEdgeDetectMode(m_edge_detect_mode);
        }

        // Copy kMyColorTarget to kMyAuxColorTarget.
        auto copyOp = dynamic_cast<QuadRenderCopy *>(
            m_ops_layer[PassesLayer::kEdgeCopyOp]);
        if (copyOp) {
            copyOp->setEnabled(true);
            copyOp->setInputTarget(kMyColorTarget);
            copyOp->setRenderTargets(m_targets, kMyAuxColorTarget, 1);
        }

        // Render wireframe into kMyColorTarget.
        auto wireframePassOp = dynamic_cast<SceneRender *>(
            m_ops_layer[PassesLayer::kSceneWireframePass]);
        if (wireframePassOp) {
            wireframePassOp->setEnabled(true);
            wireframePassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Blend between kMyColorTarget and kMyAuxColorTarget, and output
        // to kMyColorTarget.
        auto wireBlendOp = dynamic_cast<QuadRenderBlend *>(
            m_ops_layer[PassesLayer::kWireframeBlendOp]);
        if (wireBlendOp) {
            wireBlendOp->setEnabled(true);
            wireBlendOp->setInputTarget1(kMyColorTarget);
            wireBlendOp->setInputTarget2(kMyAuxColorTarget);
            wireBlendOp->setRenderTargets(m_targets, kMyColorTarget, 1);
            wireBlendOp->setBlend(static_cast<float>(m_wireframe_alpha));
        }

        // Draw manipulators over the top of all objects.
        auto manipulatorPassOp = dynamic_cast<SceneRender *>(
            m_ops_end[PassesEnd::kSceneManipulatorPass]);
        if (manipulatorPassOp) {
            manipulatorPassOp->setEnabled(true);
            manipulatorPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw the HUD on kMyColorTarget.
        auto hudOp = dynamic_cast<HudRender *>(m_ops_end[PassesEnd::kHudPass]);
        if (hudOp) {
            hudOp->setEnabled(true);
            hudOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Display kMyColorTarget to the screen.
        auto presentOp =
            dynamic_cast<PresentTarget *>(m_ops_end[PassesEnd::kPresentOp]);
        if (presentOp) {
            presentOp->setEnabled(true);
            presentOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

    } else if (m_render_mode == RenderMode::kOne) {
        // Blending wireframes.
        MMSOLVER_VRB("RenderOverride::mode = ONE");

        // Draw scene (without image plane) into the depth channel.
        auto depthPassOp = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneDepthPass]);
        if (depthPassOp) {
            depthPassOp->setEnabled(true);
            depthPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw viewport background (with image plane).
        auto backgroundPassOp = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneBackgroundPass]);
        if (backgroundPassOp) {
            backgroundPassOp->setEnabled(true);
            // Note: Only render to the color target, depth is ignored.
            backgroundPassOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        // Allow selection of objects.
        auto selectSceneOp = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneSelectionPass]);
        if (selectSceneOp) {
            selectSceneOp->setEnabled(true);
            selectSceneOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto edgeDetectOp = dynamic_cast<QuadRenderEdgeDetect *>(
            m_ops_layer[PassesLayer::kEdgeDetectOp]);
        if (edgeDetectOp) {
            edgeDetectOp->setEnabled(false);
            edgeDetectOp->setInputColorTarget(0);
            edgeDetectOp->setInputDepthTarget(0);
            edgeDetectOp->setRenderTargets(nullptr, 0, 0);
        }

        auto copyOp = dynamic_cast<QuadRenderCopy *>(
            m_ops_layer[PassesLayer::kEdgeCopyOp]);
        if (copyOp) {
            copyOp->setEnabled(true);
            copyOp->setInputTarget(kMyColorTarget);
            copyOp->setRenderTargets(m_targets, kMyAuxColorTarget, 1);
        }

        auto wireframePassOp = dynamic_cast<SceneRender *>(
            m_ops_layer[PassesLayer::kSceneWireframePass]);
        if (wireframePassOp) {
            wireframePassOp->setEnabled(true);
            wireframePassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto wireBlendOp = dynamic_cast<QuadRenderBlend *>(
            m_ops_layer[PassesLayer::kWireframeBlendOp]);
        if (wireBlendOp) {
            wireBlendOp->setEnabled(true);
            wireBlendOp->setInputTarget1(kMyColorTarget);
            wireBlendOp->setInputTarget2(kMyAuxColorTarget);
            wireBlendOp->setRenderTargets(m_targets, kMyColorTarget, 1);
            wireBlendOp->setBlend(static_cast<float>(m_wireframe_alpha));
        }

        // Draw manipulators over the top of all objects.
        auto manipulatorPassOp = dynamic_cast<SceneRender *>(
            m_ops_end[PassesEnd::kSceneManipulatorPass]);
        if (manipulatorPassOp) {
            manipulatorPassOp->setEnabled(true);
            manipulatorPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw the HUD on kMyColorTarget.
        auto hudOp = dynamic_cast<HudRender *>(m_ops_end[PassesEnd::kHudPass]);
        if (hudOp) {
            hudOp->setEnabled(true);
            hudOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Display kMyColorTarget to the screen.
        auto presentOp =
            dynamic_cast<PresentTarget *>(m_ops_end[PassesEnd::kPresentOp]);
        if (presentOp) {
            presentOp->setEnabled(true);
            presentOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

    } else {
        // No blending or post operations.
        MMSOLVER_VRB("RenderOverride::renderMode = RenderMode::kFour");

        // Draw scene (without image plane) into the depth channel.
        auto depthPassOp = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneDepthPass]);
        if (depthPassOp) {
            depthPassOp->setEnabled(true);
            depthPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw viewport background (with image plane).
        auto backgroundPassOp = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneBackgroundPass]);
        if (backgroundPassOp) {
            backgroundPassOp->setEnabled(true);
            // Note: Only render to the color target, depth is ignored.
            backgroundPassOp->setRenderTargets(m_targets, kMyColorTarget, 1);
        }

        // Allow selection of objects.
        auto selectSceneOp = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneSelectionPass]);
        if (selectSceneOp) {
            selectSceneOp->setEnabled(true);
            selectSceneOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto copyOp = dynamic_cast<QuadRenderCopy *>(
            m_ops_layer[PassesLayer::kEdgeCopyOp]);
        if (copyOp) {
            copyOp->setEnabled(true);
            copyOp->setInputTarget(kMyColorTarget);
            copyOp->setRenderTargets(m_targets, kMyAuxColorTarget, 1);
        }

        auto wireframePassOp = dynamic_cast<SceneRender *>(
            m_ops_layer[PassesLayer::kSceneWireframePass]);
        if (wireframePassOp) {
            wireframePassOp->setEnabled(true);
            wireframePassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        auto edgeDetectOp = dynamic_cast<QuadRenderEdgeDetect *>(
            m_ops_layer[PassesLayer::kEdgeDetectOp]);
        if (edgeDetectOp) {
            edgeDetectOp->setEnabled(false);
            edgeDetectOp->setInputColorTarget(0);
            edgeDetectOp->setInputDepthTarget(0);
            edgeDetectOp->setRenderTargets(nullptr, 0, 0);
        }

        auto wireBlendOp = dynamic_cast<QuadRenderBlend *>(
            m_ops_layer[PassesLayer::kWireframeBlendOp]);
        if (wireBlendOp) {
            wireBlendOp->setEnabled(true);
            wireBlendOp->setInputTarget1(kMyColorTarget);
            wireBlendOp->setInputTarget2(kMyAuxColorTarget);
            wireBlendOp->setRenderTargets(m_targets, kMyColorTarget, 1);
            wireBlendOp->setBlend(1.0f);
        }

        // Draw manipulators over the top of all objects.
        auto manipulatorPassOp = dynamic_cast<SceneRender *>(
            m_ops_end[PassesEnd::kSceneManipulatorPass]);
        if (manipulatorPassOp) {
            manipulatorPassOp->setEnabled(true);
            manipulatorPassOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Draw the HUD on kMyColorTarget.
        auto hudOp = dynamic_cast<HudRender *>(m_ops_end[PassesEnd::kHudPass]);
        if (hudOp) {
            hudOp->setEnabled(true);
            hudOp->setRenderTargets(m_targets, kMyColorTarget, 2);
        }

        // Display kMyColorTarget to the screen.
        auto presentOp =
            dynamic_cast<PresentTarget *>(m_ops_end[PassesEnd::kPresentOp]);
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
    if (m_ops_start[PassesStart::kSceneDepthPass]) {
        auto op = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneDepthPass]);
        op->setPanelName(name);
    }

    if (m_ops_start[PassesStart::kSceneBackgroundPass]) {
        auto op = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneBackgroundPass]);
        op->setPanelName(name);
    }

    if (m_ops_start[PassesStart::kSceneSelectionPass]) {
        auto op = dynamic_cast<SceneRender *>(
            m_ops_start[PassesStart::kSceneSelectionPass]);
        op->setPanelName(name);
    }

    if (m_ops_layer[PassesLayer::kSceneWireframePass]) {
        auto op = dynamic_cast<SceneRender *>(
            m_ops_layer[PassesLayer::kSceneWireframePass]);
        op->setPanelName(name);
    }

    if (m_ops_end[PassesEnd::kSceneManipulatorPass]) {
        auto op = dynamic_cast<SceneRender *>(
            m_ops_end[PassesEnd::kSceneManipulatorPass]);
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
    RenderOverride::updateParameters();

    // Construct the render operations.
    status = RenderOverride::updateRenderOperations();
    CHECK_MSTATUS(status);

    // Update any of the render targets which will be required
    status = RenderOverride::updateRenderTargets();
    CHECK_MSTATUS(status);

    // The panel name, used to get the current 3d view (M3dView).
    m_panel_name.set(destination.asChar());
    status = RenderOverride::setPanelNames(m_panel_name);
    CHECK_MSTATUS(status);

    m_current_pass = Pass::kUninitialized;
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
    m_current_pass = Pass::kUninitialized;
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
