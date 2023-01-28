/*
 * Copyright (C) 2023 David Cattermole.
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
 */

#include "DisplayLayer.h"

// Maya
#include <maya/MObject.h>
#include <maya/MShaderManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/ops/QuadRenderBlend.h"
#include "mmSolver/render/ops/QuadRenderEdgeDetect.h"
#include "mmSolver/render/ops/QuadRenderLayerMerge.h"
#include "mmSolver/render/ops/SceneRender.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

static MShaderInstance *create_depth_shader(const float depth_offset) {
    const bool verbose = false;

    MMSOLVER_VRB("create_depth_shader: Compile Depth Main shader...");
    const MString file_name = "mmDepth";
    const MString main_technique = "Main";
    MHWRender::MShaderInstance *shader_instance =
        compile_shader_file(file_name, main_technique);

    if (shader_instance) {
        MMSOLVER_VRB("create_depth_shader: Assign Depth shader parameters...");
        CHECK_MSTATUS(
            shader_instance->setParameter("gDepthOffset", depth_offset));
    }

    return shader_instance;
}

DisplayLayer::DisplayLayer()
    : m_name()
    , m_display_order(-1)
    , m_layer_mode(kLayerModeDefault)
    , m_layer_mix(kLayerMixDefault)
    , m_layer_draw_debug(kLayerDrawDebugDefault)
    , m_object_display_style(kObjectDisplayStyleDefault)
    , m_object_display_textures(kObjectDisplayTexturesDefault)
    , m_object_alpha(kObjectAlphaDefault)
    , m_edge_enable(kEdgeEnableDefault)
    , m_edge_detect_mode(kEdgeDetectModeDefault)
    , m_edge_color(kEdgeColorDefault)
    , m_edge_alpha(kEdgeAlphaDefault)
    , m_edge_thickness(kEdgeThicknessDefault)
    , m_edge_threshold(kEdgeThresholdDefault) {
    for (auto i = 0; i < DisplayLayerPasses::kLayerPassesCount; ++i) {
        m_ops[i] = nullptr;
    }
}

DisplayLayer::~DisplayLayer() {
    // Delete all the operations. This will release any references to
    // other resources user per operation.
    for (auto i = 0; i < DisplayLayerPasses::kLayerPassesCount; ++i) {
        delete m_ops[i];
        m_ops[i] = nullptr;
    }
}

MStatus DisplayLayer::updateRenderOperations() {
    const bool verbose = false;
    MMSOLVER_VRB("DisplayLayer::updateRenderOperations: " << m_name.asChar());

    if (m_ops[DisplayLayerPasses::kSceneRenderPass] != nullptr) {
        // render operations are already up-to-date.
        return MS::kSuccess;
    }

    // Clear Masks
    const auto clear_mask_none =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearNone);
    const auto clear_mask_all =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearAll);
    const auto clear_mask_depth =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearDepth);
    const auto clear_mask_color =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearColor);

    // Display modes
    const auto display_mode_shaded =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded);
    const auto display_mode_shaded_textured =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded |
            MHWRender::MSceneRender::kTextured);
    const auto display_mode_wireframe =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kWireFrame);
    const auto display_mode_shaded_wireframe =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded |
            MHWRender::MSceneRender::kWireFrame);
    const auto display_mode_shaded_wireframe_textured =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded |
            MHWRender::MSceneRender::kWireFrame |
            MHWRender::MSceneRender::kTextured);

    // Draw these objects for transparency.
    const auto wire_draw_object_types =
        ~(MHWRender::MFrameContext::kExcludeMeshes |
          MHWRender::MFrameContext::kExcludeNurbsCurves |
          MHWRender::MFrameContext::kExcludeNurbsSurfaces |
          MHWRender::MFrameContext::kExcludeSubdivSurfaces);

    // Draw all non-geometry normally.
    const auto non_wire_draw_object_types =
        ((~wire_draw_object_types) |
         MHWRender::MFrameContext::kExcludeImagePlane |
         MHWRender::MFrameContext::kExcludePluginShapes);

    // What objects types to draw for depth buffer?
    const auto depth_draw_object_types =
        wire_draw_object_types | MHWRender::MFrameContext::kExcludeImagePlane;

    // Draw image planes in the background always.
    const auto bg_draw_object_types =
        ~(MHWRender::MFrameContext::kExcludeImagePlane |
          MHWRender::MFrameContext::kExcludePluginShapes);

    // We assume the depth buffer has at least 24 bits for the depth
    // value.
    //
    // Smaller Z-Depth values are nearer the camera, and larger values
    // are farther away.
    const float depthValueRange = 1048576.0f;  // (2 ^ 24) / 16
    const float depthValueStep = 1.0f / depthValueRange;
    const float depthOffset = depthValueStep * 4;
    // Shader to push depth away from camera.
    auto depthShader1 = create_depth_shader(-depthOffset);

    const MString depthSceneOpName = MString(kLayerDepthPassName) + m_name;
    auto depthPassOp = new SceneRender(depthSceneOpName);
    depthPassOp->setClearMask(clear_mask_all);
    depthPassOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    depthPassOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    depthPassOp->setExcludeTypes(depth_draw_object_types);
    depthPassOp->setDisplayModeOverride(display_mode_shaded);
    depthPassOp->setShaderOverride(depthShader1);
    depthPassOp->setDrawObjects(DrawObjects::kOnlyNamedLayerObjects);
    depthPassOp->setLayerName(m_name);
    m_ops[DisplayLayerPasses::kSceneDepthPass] = depthPassOp;

    // Apply edge detect.
    const MString edgeDetectOpName = MString(kLayerEdgeDetectOpName) + m_name;
    auto edgeDetectOp = new QuadRenderEdgeDetect(edgeDetectOpName);
    edgeDetectOp->setClearMask(clear_mask_all);
    edgeDetectOp->setThreshold(m_edge_threshold);
    edgeDetectOp->setThickness(m_edge_thickness);
    m_ops[DisplayLayerPasses::kEdgeDetectOp] = edgeDetectOp;

    // Scene Object Render pass.
    const MString scenePassOpName = MString(kLayerObjectPassName) + m_name;
    auto scenePassOp = new SceneRender(scenePassOpName);
    scenePassOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    scenePassOp->setClearMask(clear_mask_none);
    scenePassOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    scenePassOp->setExcludeTypes(wire_draw_object_types);
    scenePassOp->setDrawObjects(DrawObjects::kOnlyNamedLayerObjects);
    scenePassOp->setLayerName(m_name);
    m_ops[DisplayLayerPasses::kSceneRenderPass] = scenePassOp;

    // Merge the result into the main color and depth targets.
    const MString layerMergeOpName = MString(kLayerMergeOpName) + m_name;
    auto layerMergeOp = new QuadRenderLayerMerge(layerMergeOpName);
    layerMergeOp->setClearMask(clear_mask_none);
    layerMergeOp->setLayerMode(m_layer_mode);
    layerMergeOp->setLayerMix(m_layer_mix);
    layerMergeOp->setAlphaA(m_object_alpha);
    m_ops[DisplayLayerPasses::kLayerMergeOp] = layerMergeOp;

    return MS::kSuccess;
}

MStatus DisplayLayer::updateRenderTargets(MHWRender::MRenderTarget **targets) {
    const bool verbose = false;
    MMSOLVER_VRB("DisplayLayer::updateRenderTargets: " << m_name.asChar());

    // Update the render targets on the individual operations.
    //
    // This section will determine the outputs of each operation.  The
    // input of each operation is assumed to be the Maya provided
    // color and depth targets, but shaders may internally reference
    // specific render targets.

    auto depthPassOp =
        dynamic_cast<SceneRender *>(m_ops[DisplayLayerPasses::kSceneDepthPass]);
    auto edgeDetectOp = dynamic_cast<QuadRenderEdgeDetect *>(
        m_ops[DisplayLayerPasses::kEdgeDetectOp]);
    auto scenePassOp = dynamic_cast<SceneRender *>(
        m_ops[DisplayLayerPasses::kSceneRenderPass]);
    auto layerMergeOp = dynamic_cast<QuadRenderLayerMerge *>(
        m_ops[DisplayLayerPasses::kLayerMergeOp]);

    if (!depthPassOp || !edgeDetectOp || !scenePassOp || !layerMergeOp) {
        return MS::kFailure;
    }

    // Clear Masks
    const auto clear_mask_none =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearNone);
    const auto clear_mask_all =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearAll);
    const auto clear_mask_depth =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearDepth);
    const auto clear_mask_color =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearColor);

    // Display modes
    const auto display_mode_shaded =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded);
    const auto display_mode_shaded_textured =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded |
            MHWRender::MSceneRender::kTextured);
    const auto display_mode_wireframe =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kWireFrame);
    const auto display_mode_shaded_wireframe =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded |
            MHWRender::MSceneRender::kWireFrame);
    const auto display_mode_shaded_wireframe_textured =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded |
            MHWRender::MSceneRender::kWireFrame |
            MHWRender::MSceneRender::kTextured);

    const float edge_alpha = m_edge_alpha * static_cast<float>(m_edge_enable);
    edgeDetectOp->setEnabled(true);
    edgeDetectOp->setInputColorTarget(kLayerColorTarget);
    edgeDetectOp->setInputDepthTarget(kLayerDepthTarget);
    edgeDetectOp->setRenderTargets(targets, kTempColorTarget, 1);
    edgeDetectOp->setThreshold(m_edge_threshold);
    edgeDetectOp->setThickness(m_edge_thickness);
    edgeDetectOp->setEdgeAlpha(edge_alpha);
    edgeDetectOp->setEdgeColor(m_edge_color.r, m_edge_color.g, m_edge_color.b);
    edgeDetectOp->setEdgeDetectMode(m_edge_detect_mode);

    if (m_object_display_style == DisplayStyle::kHiddenLine) {
        depthPassOp->setEnabled(true);
        depthPassOp->setClearMask(clear_mask_all);
        depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

        scenePassOp->setEnabled(true);
        scenePassOp->setClearMask(clear_mask_color);
        scenePassOp->setRenderTargets(targets, kLayerColorTarget, 2);
        scenePassOp->setDisplayModeOverride(display_mode_wireframe);

        layerMergeOp->setAlphaA(m_object_alpha);
    } else if (m_object_display_style == DisplayStyle::kShaded) {
        depthPassOp->setEnabled(m_edge_enable);
        depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

        scenePassOp->setEnabled(true);
        scenePassOp->setClearMask(clear_mask_all);
        scenePassOp->setRenderTargets(targets, kLayerColorTarget, 2);
        if (!m_object_display_textures) {
            scenePassOp->setDisplayModeOverride(display_mode_shaded);
        } else {
            scenePassOp->setDisplayModeOverride(display_mode_shaded_textured);
        }
    } else if (m_object_display_style == DisplayStyle::kHoldOut) {
        depthPassOp->setEnabled(true);
        depthPassOp->setClearMask(clear_mask_all);
        depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

        scenePassOp->setEnabled(true);
        scenePassOp->setClearMask(clear_mask_color);
        scenePassOp->setRenderTargets(targets, kLayerColorTarget, 2);
        scenePassOp->setDisplayModeOverride(display_mode_wireframe);

        layerMergeOp->setAlphaA(0.0);
    } else if (m_object_display_style == DisplayStyle::kWireframe) {
        depthPassOp->setEnabled(m_edge_enable);
        depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

        scenePassOp->setEnabled(true);
        scenePassOp->setClearMask(clear_mask_all);
        scenePassOp->setRenderTargets(targets, kLayerColorTarget, 2);
        scenePassOp->setDisplayModeOverride(display_mode_wireframe);

        layerMergeOp->setAlphaA(m_object_alpha);
    } else if (m_object_display_style == DisplayStyle::kWireframeOnShaded) {
        depthPassOp->setEnabled(m_edge_enable);
        depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

        scenePassOp->setEnabled(true);
        scenePassOp->setClearMask(clear_mask_all);
        scenePassOp->setRenderTargets(targets, kLayerColorTarget, 2);
        if (!m_object_display_textures) {
            scenePassOp->setDisplayModeOverride(display_mode_shaded_wireframe);
        } else {
            scenePassOp->setDisplayModeOverride(
                display_mode_shaded_wireframe_textured);
        }

        layerMergeOp->setAlphaA(m_object_alpha);
    } else {
        MMSOLVER_ERR("DisplayLayer::updateRenderTargets: Display Layer \""
                     << m_name.asChar() << "\" has an invalid Display Style: "
                     << static_cast<short>(m_object_display_style));
    }

    layerMergeOp->setEnabled(true);
    layerMergeOp->setColorTargetA(kLayerColorTarget);
    layerMergeOp->setDepthTargetA(kLayerDepthTarget);
    layerMergeOp->setColorTargetB(kMainColorTarget);
    layerMergeOp->setDepthTargetB(kMainDepthTarget);
    layerMergeOp->setColorTargetC(kTempColorTarget);
    layerMergeOp->setUseColorTargetC(m_edge_enable);
    layerMergeOp->setRenderTargets(targets, kMainColorTarget, 1);
    layerMergeOp->setLayerMode(m_layer_mode);
    layerMergeOp->setLayerMix(m_layer_mix);
    layerMergeOp->setDebug(m_layer_draw_debug);

    return MS::kSuccess;
}

MStatus DisplayLayer::setPanelNames(const MString &name) {
    const bool verbose = false;
    MMSOLVER_VRB("DisplayLayer::setPanelNames: "
                 << m_name.asChar() << " panelName: " << name.asChar());

    MHWRender::MRenderOperation *base_op =
        m_ops[DisplayLayerPasses::kSceneRenderPass];
    if (base_op) {
        auto op = dynamic_cast<SceneRender *>(base_op);
        op->setPanelName(name);
    }

    return MS::kSuccess;
}

MHWRender::MRenderOperation *DisplayLayer::getOperation(size_t &current_op) {
    const auto count = DisplayLayerPasses::kLayerPassesCount;
    if (current_op >= 0 && current_op < count) {
        return DisplayLayer::m_ops[current_op];
    }
    return nullptr;
}

}  // namespace render
}  // namespace mmsolver
