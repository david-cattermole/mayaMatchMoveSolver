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
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/QuadRenderBlend.h"
#include "mmSolver/render/QuadRenderCopy.h"
#include "mmSolver/render/QuadRenderEdgeDetect.h"
#include "mmSolver/render/QuadRenderLayerMerge.h"
#include "mmSolver/render/SceneRender.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

static MShaderInstance *create_depth_shader(const float depth_offset) {
    const bool verbose = false;

    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        return nullptr;
    }
    const MHWRender::MShaderManager *shader_manager =
        renderer->getShaderManager();
    if (!shader_manager) {
        return nullptr;
    }

    // Compile Main shader
    MMSOLVER_VRB("create_depth_shader: Compile Depth Main shader...");
    const MString file_name = "mmDepth";
    const MString main_technique = "Main";
    MHWRender::MShaderInstance *shader_instance =
        shader_manager->getEffectsFileShader(file_name.asChar(),
                                             main_technique.asChar());

    // Set default parameters
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
    , m_display_style(kDisplayStyleDefault)
    , m_layer_mode(kLayerModeDefault)
    , m_layer_mix(kLayerMixDefault)
    , m_layer_draw_debug(kLayerDrawDebugDefault)
    , m_wireframe_alpha(kWireframeAlphaDefault)
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

    if (m_ops[DisplayLayerPasses::kSceneWireframePass] != nullptr) {
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
    const auto display_mode_wireframe =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kWireFrame);
    const auto display_mode_shaded_wireframe =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded | display_mode_wireframe);

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
    const float depthOffset = depthValueStep * 2;
    // Shader to push depth away from camera.
    auto depthShader1 = create_depth_shader(depthOffset);
    MHWRender::MShaderInstance *depthShader2 = nullptr;
    // auto depthShader2 = create_depth_shader(-depthOffset);

    // const MString copyLayerStartOpName =
    //     MString(kLayerCopyStartOpName) + m_name;
    // auto copyLayerStartOp = new QuadRenderCopy(copyLayerStartOpName);
    // copyLayerStartOp->setClearMask(clear_mask_all);
    // m_ops[DisplayLayerPasses::kLayerCopyStartOp] = copyLayerStartOp;

    const MString depthSceneOpName = MString(kLayerDepthPassName) + m_name;
    auto depthPassOp = new SceneRender(depthSceneOpName);
    depthPassOp->setClearMask(clear_mask_all);
    depthPassOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    depthPassOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    depthPassOp->setExcludeTypes(depth_draw_object_types);
    depthPassOp->setDisplayModeOverride(display_mode_shaded);
    depthPassOp->setShaderOverride(depthShader1);
    depthPassOp->setDoSelectable(false);
    depthPassOp->setDoBackground(false);
    depthPassOp->setUseLayer(true);
    depthPassOp->setLayerName(m_name);
    m_ops[DisplayLayerPasses::kSceneDepthPass] = depthPassOp;

    // // Apply edge detect.
    // const MString edgeDetectOpName = MString(kLayerEdgeDetectOpName) +
    // m_name; auto edgeDetectOp = new QuadRenderEdgeDetect(edgeDetectOpName);
    // edgeDetectOp->setClearMask(clear_mask_none);
    // edgeDetectOp->setThreshold(m_edge_threshold);
    // edgeDetectOp->setThickness(m_edge_thickness);
    // m_ops[DisplayLayerPasses::kEdgeDetectOp] = edgeDetectOp;

    // const MString copyLayerEndOpName = MString(kLayerCopyEndOpName) + m_name;
    // auto copyLayerEndOp = new QuadRenderCopy(copyLayerEndOpName);
    // copyLayerEndOp->setClearMask(~clear_mask_color);
    // m_ops[DisplayLayerPasses::kLayerCopyEndOp] = copyLayerEndOp;

    // Wireframe pass.
    const MString wirePassOpName = MString(kLayerWireframePassName) + m_name;
    auto wirePassOp = new SceneRender(wirePassOpName);
    wirePassOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    wirePassOp->setClearMask(clear_mask_none);
    // wirePassOp->setSceneFilter(
    //     MHWRender::MSceneRender::kRenderPostSceneUIItems);
    // wirePassOp->setSceneFilter(MHWRender::MSceneRender::kRenderUIItems);
    wirePassOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    wirePassOp->setExcludeTypes(wire_draw_object_types);
    // wirePassOp->setShaderOverride(depthShader2);
    wirePassOp->setDoSelectable(false);
    wirePassOp->setDoBackground(false);
    wirePassOp->setUseLayer(true);
    wirePassOp->setLayerName(m_name);
    m_ops[DisplayLayerPasses::kSceneWireframePass] = wirePassOp;

    // // Blend between 'no-wireframe' and 'wireframe'.
    // const MString wireBlendOpName =
    //     MString(kLayerWireframeBlendOpName) + m_name;
    // auto wireBlendOp = new QuadRenderBlend(wireBlendOpName);
    // wireBlendOp->setClearMask(clear_mask_none);
    // wireBlendOp->setBlend(m_wireframe_alpha);
    // m_ops[DisplayLayerPasses::kWireframeBlendOp] = wireBlendOp;

    // Merge the result into the main color and depth targets.
    const MString layerMergeOpName = MString(kLayerMergeOpName) + m_name;
    auto layerMergeOp = new QuadRenderLayerMerge(layerMergeOpName);
    layerMergeOp->setClearMask(clear_mask_none);
    layerMergeOp->setLayerMode(m_layer_mode);
    layerMergeOp->setLayerMix(m_layer_mix);
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

    // auto copyLayerStartOp = dynamic_cast<QuadRenderCopy *>(
    //     m_ops[DisplayLayerPasses::kLayerCopyStartOp]);
    auto depthPassOp =
        dynamic_cast<SceneRender *>(m_ops[DisplayLayerPasses::kSceneDepthPass]);
    // auto edgeDetectOp = dynamic_cast<QuadRenderEdgeDetect *>(
    //     m_ops[DisplayLayerPasses::kEdgeDetectOp]);
    // auto copyLayerEndOp = dynamic_cast<QuadRenderCopy *>(
    //     m_ops[DisplayLayerPasses::kLayerCopyEndOp]);
    auto wirePassOp = dynamic_cast<SceneRender *>(
        m_ops[DisplayLayerPasses::kSceneWireframePass]);
    // auto wireBlendOp = dynamic_cast<QuadRenderBlend *>(
    //     m_ops[DisplayLayerPasses::kWireframeBlendOp]);
    auto layerMergeOp = dynamic_cast<QuadRenderLayerMerge *>(
        m_ops[DisplayLayerPasses::kLayerMergeOp]);

    if (                 // !copyLayerStartOp ||
        !depthPassOp ||  // !edgeDetectOp || !copyLayerEndOp ||
        !wirePassOp ||   // !wireBlendOp ||
        !layerMergeOp) {
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
    const auto display_mode_wireframe =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kWireFrame);
    const auto display_mode_shaded_wireframe =
        static_cast<MHWRender::MSceneRender::MDisplayMode>(
            MHWRender::MSceneRender::kShaded |
            MHWRender::MSceneRender::kWireFrame);

    if (m_display_style == DisplayStyle::kHiddenLine) {
        // // Copy kMainColorTarget to kLayerColorTarget.
        // copyLayerStartOp->setEnabled(true);
        // copyLayerStartOp->setInputTarget(kMainColorTarget);
        // copyLayerStartOp->setRenderTargets(targets, kLayerColorTarget, 1);

        // Render object depth into kLayerColorTarget and
        // kLayerDepthTarget.
        depthPassOp->setEnabled(true);
        depthPassOp->setClearMask(clear_mask_all);
        depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

        // // Detect edges using kLayerDepthTarget, and draw in
        // // kLayerColorTarget.
        // edgeDetectOp->setEnabled(m_edge_enable);
        // edgeDetectOp->setInputColorTarget(kLayerColorTarget);
        // edgeDetectOp->setInputDepthTarget(kLayerDepthTarget);
        // edgeDetectOp->setRenderTargets(targets, kLayerColorTarget, 1);
        // edgeDetectOp->setThreshold(m_edge_threshold);
        // edgeDetectOp->setThickness(m_edge_thickness);
        // edgeDetectOp->setEdgeAlpha(m_edge_alpha);
        // edgeDetectOp->setEdgeColor(m_edge_color.r, m_edge_color.g,
        // m_edge_color.b); edgeDetectOp->setEdgeDetectMode(m_edge_detect_mode);

        // // Copy kLayerColorTarget to kTempColorTarget.
        // copyLayerEndOp->setEnabled(true);
        // copyLayerEndOp->setInputTarget(kLayerColorTarget);
        // copyLayerEndOp->setRenderTargets(targets, kTempColorTarget, 1);

        // Render wireframe into kLayerColorTarget and kLayerDepthTarget.
        wirePassOp->setEnabled(true);
        wirePassOp->setClearMask(clear_mask_none);
        wirePassOp->setRenderTargets(targets, kLayerColorTarget, 2);
        wirePassOp->setDisplayModeOverride(display_mode_wireframe);

        // // Blend between kLayerColorTarget and kTempColorTarget, and output
        // // to kLayerColorTarget.
        // wireBlendOp->setEnabled(false);
        // wireBlendOp->setInputTarget1(kLayerColorTarget);
        // wireBlendOp->setInputTarget2(kTempColorTarget);
        // wireBlendOp->setRenderTargets(targets, kLayerColorTarget, 1);
        // wireBlendOp->setBlend(m_wireframe_alpha);
    } else if (m_display_style == DisplayStyle::kShaded) {
        // Render object depth into kLayerColorTarget and
        // kLayerDepthTarget.
        depthPassOp->setEnabled(false);
        depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

        // Render wireframe into kLayerColorTarget and kLayerDepthTarget.
        wirePassOp->setEnabled(true);
        wirePassOp->setClearMask(clear_mask_all);
        wirePassOp->setRenderTargets(targets, kLayerColorTarget, 2);
        wirePassOp->setDisplayModeOverride(display_mode_shaded);
    } else if (m_display_style == DisplayStyle::kWireframe) {
        // Render object depth into kLayerColorTarget and
        // kLayerDepthTarget.
        depthPassOp->setEnabled(false);
        depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

        // Render wireframe into kLayerColorTarget and kLayerDepthTarget.
        wirePassOp->setEnabled(true);
        wirePassOp->setClearMask(clear_mask_all);
        wirePassOp->setRenderTargets(targets, kLayerColorTarget, 2);
        wirePassOp->setDisplayModeOverride(display_mode_wireframe);
    } else if (m_display_style == DisplayStyle::kWireframeOnShaded) {
        // Render object depth into kLayerColorTarget and
        // kLayerDepthTarget.
        depthPassOp->setEnabled(false);
        depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

        // Render wireframe into kLayerColorTarget and kLayerDepthTarget.
        wirePassOp->setEnabled(true);
        wirePassOp->setClearMask(clear_mask_all);
        wirePassOp->setRenderTargets(targets, kLayerColorTarget, 2);
        wirePassOp->setDisplayModeOverride(display_mode_shaded_wireframe);
    } else {
        MMSOLVER_ERR("DisplayLayer::updateRenderTargets: Display Layer \""
                     << m_name.asChar() << "\" has an invalid Display Style: "
                     << static_cast<short>(m_display_style));
    }

    // Merge kLayerColorTarget over kMainColorTarget, and output to
    // kMainColorTarget. Depth targets are used if the Layer Merge is set to
    // Z-Depth mode.
    layerMergeOp->setEnabled(true);
    layerMergeOp->setColorTargetA(kLayerColorTarget);
    layerMergeOp->setDepthTargetA(kLayerDepthTarget);
    layerMergeOp->setColorTargetB(kMainColorTarget);
    layerMergeOp->setDepthTargetB(kMainDepthTarget);
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
        m_ops[DisplayLayerPasses::kSceneWireframePass];
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
