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
#include "mmSolver/render/ops/ClearOperation.h"
#include "mmSolver/render/ops/QuadRenderBlend.h"
#include "mmSolver/render/ops/QuadRenderCopy.h"
#include "mmSolver/render/ops/QuadRenderEdgeDetect.h"
#include "mmSolver/render/ops/QuadRenderLayerMerge.h"
#include "mmSolver/render/ops/SceneDepthRender.h"
#include "mmSolver/render/ops/SceneEdgeRender.h"
#include "mmSolver/render/ops/SceneRender.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

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
    , m_edge_thickness(kEdgeThicknessDefault)
    , m_edge_color(kEdgeColorDefault)
    , m_edge_alpha(kEdgeAlphaDefault)
    , m_edge_threshold_color(kEdgeThresholdColorDefault)
    , m_edge_threshold_alpha(kEdgeThresholdAlphaDefault)
    , m_edge_threshold_depth(kEdgeThresholdDepthDefault) {
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

MStatus DisplayLayer::updateRenderOperations(
    const MSelectionList *drawable_nodes) {
    const bool verbose = false;
    MMSOLVER_VRB("DisplayLayer::updateRenderOperations: " << m_name.asChar());

    if (m_ops[DisplayLayerPasses::kSceneRenderPass] != nullptr) {
        // render operations are already up-to-date.
        return MS::kSuccess;
    }

    // Clear kLayerColorTarget and kLayerDepthTarget to defaults.
    const MString clearLayerTargetOpName =
        MString(kLayerClearLayerTargetOpName) + m_name;
    auto clearLayerTargetOp = new ClearOperation(clearLayerTargetOpName);
    clearLayerTargetOp->setMask(CLEAR_MASK_ALL);
    m_ops[DisplayLayerPasses::kClearLayerTargetOp] = clearLayerTargetOp;

    // Clear kTempColorTarget and kTempDepthTarget to defaults.
    const MString clearTempTargetOpName =
        MString(kLayerClearTempTargetOpName) + m_name;
    auto clearTempTargetOp = new ClearOperation(clearTempTargetOpName);
    clearTempTargetOp->setMask(CLEAR_MASK_ALL);
    m_ops[DisplayLayerPasses::kClearTempTargetOp] = clearTempTargetOp;

    // Copy kMainDepthTarget to kTempDepthTarget.
    const MString copyOpName = MString(kLayerCopyOpName) + m_name;
    auto copyOp = new QuadRenderCopy(copyOpName);
    copyOp->setClearMask(CLEAR_MASK_NONE);
    copyOp->setUseColorTarget(false);
    copyOp->setUseDepthTarget(true);
    m_ops[DisplayLayerPasses::kCopyOp] = copyOp;

    // Render Depth Scene into kLayerColorTarget and kLayerDepthTarget.
    //
    // kLayerColorTarget will be rendered with normals, facing ratio
    // and alpha values used for 2D edge detection.
    const MString depthSceneOpName = MString(kLayerDepthPassName) + m_name;
    auto depthPassOp = new SceneDepthRender(depthSceneOpName);
    depthPassOp->setClearMask(CLEAR_MASK_NONE);
    depthPassOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    depthPassOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    depthPassOp->setDisplayModeOverride(DISPLAY_MODE_SHADED);
    depthPassOp->setDepthPriority(-4.0);  // push Z-depth away from camera.
    depthPassOp->setObjectSetOverride(drawable_nodes);
    m_ops[DisplayLayerPasses::kSceneDepthPass] = depthPassOp;

    // if EdgeDetectMode is k3dSilhouette:
    //     Render Scene Depth to kTempDepthTarget (on top of
    //     kMainDepthTarget);
    //
    // else:
    //     Render Scene Color to kTempColorTarget (using
    //     kMainDepthTarget for depth testing);
    //
    //     Render Scene Depth to kTempDepthTarget (on top of
    //     kMainDepthTarget);
    const MString depthSceneOpName2 = MString(kLayerDepthPassName) + m_name;
    auto depthPassOp2 = new SceneDepthRender(depthSceneOpName2);
    depthPassOp2->setClearMask(CLEAR_MASK_NONE);
    depthPassOp2->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    depthPassOp2->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    depthPassOp2->setDisplayModeOverride(DISPLAY_MODE_SHADED);
    depthPassOp2->setDepthPriority(-4.0);  // push Z-depth away from camera.
    depthPassOp2->setObjectSetOverride(drawable_nodes);
    m_ops[DisplayLayerPasses::kSceneDepthPass2] = depthPassOp2;

    // if EdgeDetectMode is k3dSilhouette:
    //     Copy kLayerDepthTarget to kTempDepthTarget.
    // else:
    //     Copy kLayerColorTarget to kTempColorTarget.
    //     Copy kLayerDepthTarget to kTempDepthTarget.
    const MString copyEdgeOpName = MString(kLayerCopyEdgeOpName) + m_name;
    auto copyEdgeOp = new QuadRenderCopy(copyEdgeOpName);
    copyEdgeOp->setClearMask(CLEAR_MASK_ALL);
    m_ops[DisplayLayerPasses::kCopyEdgeOp] = copyEdgeOp;

    // Render the scene 3D geometry as silhouette edges. Runs only if
    // 3D silhouette edge is used (if EdgeDetectMode is
    // k3dSilhouette).
    //
    // Render Scene into kTempColorTarget and kTempDepthTarget.
    //
    // The kTempColorTarget input will be empty/blank.
    //
    // The kTempDepthTarget input will contain the contents of
    // kLayerDepthTarget, as rendered in the 'depthPassOp'.
    const MString sceneEdgeOpName = MString(kLayerEdgePassOpName) + m_name;
    auto sceneEdgeOp = new SceneEdgeRender(sceneEdgeOpName);
    sceneEdgeOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    sceneEdgeOp->setClearMask(CLEAR_MASK_COLOR);
    sceneEdgeOp->setSceneFilter(MHWRender::MSceneRender::kRenderShadedItems);
    sceneEdgeOp->setCullingOverride(MHWRender::MSceneRender::kCullFrontFaces);
    sceneEdgeOp->setDisplayModeOverride(DISPLAY_MODE_SHADED);
    sceneEdgeOp->setObjectSetOverride(drawable_nodes);
    m_ops[DisplayLayerPasses::kSceneEdgePass] = sceneEdgeOp;

    // Apply edge detect. Runs only if 2D edge detection is used (if
    // EdgeDetectMode is not k3dSilhouette).
    //
    // 1) Reads kLayerColorTarget and kLayerDepthTarget.
    //
    // 2) Performs 2D edge detection on kLayerColorTarget and
    //    kLayerDepthTarget.
    //
    // 3) Outputs to kTempColorTarget and kTempDepthTarget.
    const MString edgeDetectOpName = MString(kLayerEdgeDetectOpName) + m_name;
    auto edgeDetectOp = new QuadRenderEdgeDetect(edgeDetectOpName);
    edgeDetectOp->setClearMask(CLEAR_MASK_ALL);
    m_ops[DisplayLayerPasses::kEdgeDetectOp] = edgeDetectOp;

    // Scene Object Render pass, with whatever shading type is asked
    // for by the user (via default viewport settings or the
    // DisplayLayer override given).
    //
    // Renders the scene objects to kLayerColorTarget and
    // kLayerDepthTarget.
    const MString scenePassOpName = MString(kLayerObjectPassName) + m_name;
    auto scenePassOp = new SceneRender(scenePassOpName);
    scenePassOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    scenePassOp->setClearMask(CLEAR_MASK_NONE);
    scenePassOp->setObjectSetOverride(drawable_nodes);
    m_ops[DisplayLayerPasses::kSceneRenderPass] = scenePassOp;

    // Merge the result into the main color and depth targets.
    //
    // 1) Reads all targets; kMain*Target, kLayer*Target and
    //    kTemp*Target.
    //
    // - kMain*Target contains the previous layer's result.
    // - kLayer*Target contains the current layer's result (except edges)
    // - kTemp*Target contains the current layer's edges only.
    //
    // 2) Applies merge logic.
    //
    // 3) Outputs to kMainColorTarget and kMainDepthTarget.
    //
    // After this Operation, the iteration starts again at the top, or
    // continues to the EndPasses.
    const MString layerMergeOpName = MString(kLayerMergeOpName) + m_name;
    auto layerMergeOp = new QuadRenderLayerMerge(layerMergeOpName);
    layerMergeOp->setClearMask(CLEAR_MASK_NONE);
    layerMergeOp->setAlphaCurrentLayer(m_object_alpha);
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

    auto clearLayerTargetOp = dynamic_cast<ClearOperation *>(
        m_ops[DisplayLayerPasses::kClearLayerTargetOp]);
    auto clearTempTargetOp = dynamic_cast<ClearOperation *>(
        m_ops[DisplayLayerPasses::kClearTempTargetOp]);
    auto copyOp =
        dynamic_cast<QuadRenderCopy *>(m_ops[DisplayLayerPasses::kCopyOp]);
    auto depthPassOp = dynamic_cast<SceneDepthRender *>(
        m_ops[DisplayLayerPasses::kSceneDepthPass]);
    auto depthPassOp2 = dynamic_cast<SceneDepthRender *>(
        m_ops[DisplayLayerPasses::kSceneDepthPass2]);
    auto copyEdgeOp =
        dynamic_cast<QuadRenderCopy *>(m_ops[DisplayLayerPasses::kCopyEdgeOp]);
    auto edgeDetectOp = dynamic_cast<QuadRenderEdgeDetect *>(
        m_ops[DisplayLayerPasses::kEdgeDetectOp]);
    auto sceneEdgeOp = dynamic_cast<SceneEdgeRender *>(
        m_ops[DisplayLayerPasses::kSceneEdgePass]);
    auto scenePassOp = dynamic_cast<SceneRender *>(
        m_ops[DisplayLayerPasses::kSceneRenderPass]);
    auto layerMergeOp = dynamic_cast<QuadRenderLayerMerge *>(
        m_ops[DisplayLayerPasses::kLayerMergeOp]);

    if (!clearLayerTargetOp || !clearTempTargetOp || !copyOp || !depthPassOp ||
        !depthPassOp2 || !copyEdgeOp || !sceneEdgeOp || !edgeDetectOp ||
        !scenePassOp || !layerMergeOp) {
        return MS::kFailure;
    }

    clearLayerTargetOp->setRenderTargets(targets, kLayerColorTarget, 2);
    clearTempTargetOp->setRenderTargets(targets, kTempColorTarget, 2);

    copyOp->setColorTarget(kMainColorTarget);
    copyOp->setDepthTarget(kMainDepthTarget);
    copyOp->setRenderTargets(targets, kTempColorTarget, 2);

    depthPassOp->setRenderTargets(targets, kLayerColorTarget, 2);

    copyEdgeOp->setColorTarget(kLayerColorTarget);
    copyEdgeOp->setDepthTarget(kLayerDepthTarget);

    // Implement multi-pass silhouette rendering, adapted to Maya
    // Viewport 2.0, using render targets, rather than OpenGL state.
    //
    // This implementation is also different from the slides, since I
    // (David Cattermole - 2023-03-05) was unable to work out how to
    // render the given shader as lines(wireframe) inside the Maya
    // Viewport 2.0 API. Switching the draw mode to wireframe did not
    // render the intended shader on the wireframe at all.
    //
    // Additionally, a limitation of modern OpenGL is the inability to
    // adjust the line width, since that is deprecated in modern OpenGL.
    //
    // See "SIGGRAPH Asia 2008 Modern OpenGL", Page 97-98:
    // https://www.slideshare.net/Mark_Kilgard/sigraph-asia-2008-modern-opengl-presentation
    //
    sceneEdgeOp->setRenderTargets(targets, kTempColorTarget, 2);
    sceneEdgeOp->setEdgeThickness(m_edge_thickness);
    sceneEdgeOp->setEdgeAlpha(m_edge_alpha);
    sceneEdgeOp->setEdgeColor(m_edge_color.r, m_edge_color.g, m_edge_color.b);

    edgeDetectOp->setInputColorTarget(kLayerColorTarget);
    edgeDetectOp->setInputDepthTarget(kLayerDepthTarget);
    edgeDetectOp->setRenderTargets(targets, kTempColorTarget, 1);
    edgeDetectOp->setThickness(m_edge_thickness);
    edgeDetectOp->setThresholdColor(m_edge_threshold_color);
    edgeDetectOp->setThresholdAlpha(m_edge_threshold_alpha);
    edgeDetectOp->setThresholdDepth(m_edge_threshold_depth);
    edgeDetectOp->setEdgeAlpha(m_edge_alpha);
    edgeDetectOp->setEdgeColor(m_edge_color.r, m_edge_color.g, m_edge_color.b);
    edgeDetectOp->setEdgeDetectMode(m_edge_detect_mode);

    depthPassOp2->setRenderTargets(targets, kTempColorTarget, 2);
    if (!m_edge_enable) {
        copyEdgeOp->setEnabled(false);
        depthPassOp2->setEnabled(false);
        sceneEdgeOp->setEnabled(false);
        edgeDetectOp->setEnabled(false);
    } else {
        copyEdgeOp->setEnabled(true);
        depthPassOp2->setEnabled(true);

        if (m_edge_detect_mode == EdgeDetectMode::k3dSilhouette) {
            copyEdgeOp->setUseColorTarget(false);
            copyEdgeOp->setUseDepthTarget(true);
            depthPassOp2->setRenderTargets(targets, kTempDepthTarget, 1);
            sceneEdgeOp->setEnabled(true);
            edgeDetectOp->setEnabled(false);
        } else {
            copyEdgeOp->setUseColorTarget(true);
            copyEdgeOp->setUseDepthTarget(true);
            depthPassOp2->setRenderTargets(targets, kTempColorTarget, 2);
            sceneEdgeOp->setEnabled(false);
            edgeDetectOp->setEnabled(true);
        }
    }

    scenePassOp->setRenderTargets(targets, kLayerColorTarget, 2);

    float object_alpha = m_object_alpha;
    bool depthPassEnabled = true;
    bool hold_out = false;
    if (m_object_display_style == DisplayStyle::kHiddenLine) {
        scenePassOp->setClearMask(CLEAR_MASK_COLOR);
        scenePassOp->setDisplayModeOverride(DISPLAY_MODE_WIREFRAME);
        scenePassOp->setSceneFilter(
            MHWRender::MSceneRender::kRenderPostSceneUIItems);

    } else if (m_object_display_style == DisplayStyle::kShaded) {
        scenePassOp->setClearMask(CLEAR_MASK_ALL);
        scenePassOp->setSceneFilter(
            static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
                MHWRender::MSceneRender::kRenderShadedItems |
                MHWRender::MSceneRender::kRenderPostSceneUIItems));
        if (!m_object_display_textures) {
            scenePassOp->setDisplayModeOverride(DISPLAY_MODE_SHADED);
        } else {
            scenePassOp->setDisplayModeOverride(DISPLAY_MODE_SHADED_TEXTURED);
        }
    } else if (m_object_display_style == DisplayStyle::kHoldOut) {
        scenePassOp->setClearMask(CLEAR_MASK_NONE);
        scenePassOp->setDisplayModeOverride(DISPLAY_MODE_SHADED);
        scenePassOp->setSceneFilter(
            static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
                MHWRender::MSceneRender::kRenderShadedItems));
        hold_out = true;
    } else if (m_object_display_style == DisplayStyle::kWireframe) {
        depthPassEnabled = false;

        scenePassOp->setClearMask(CLEAR_MASK_ALL);
        scenePassOp->setDisplayModeOverride(DISPLAY_MODE_WIREFRAME);
        scenePassOp->setSceneFilter(
            MHWRender::MSceneRender::kRenderPostSceneUIItems);
    } else if (m_object_display_style == DisplayStyle::kWireframeOnShaded) {
        scenePassOp->setClearMask(CLEAR_MASK_ALL);
        scenePassOp->setSceneFilter(
            static_cast<MHWRender::MSceneRender::MSceneFilterOption>(
                MHWRender::MSceneRender::kRenderShadedItems |
                MHWRender::MSceneRender::kRenderPostSceneUIItems));
        if (!m_object_display_textures) {
            scenePassOp->setDisplayModeOverride(DISPLAY_MODE_SHADED_WIREFRAME);
        } else {
            scenePassOp->setDisplayModeOverride(
                DISPLAY_MODE_SHADED_WIREFRAME_TEXTURED);
        }
    } else {
        MMSOLVER_ERR("DisplayLayer::updateRenderTargets: Display Layer \""
                     << m_name.asChar() << "\" has an invalid Display Style: "
                     << static_cast<short>(m_object_display_style));
    }

    depthPassOp->setEnabled(depthPassEnabled);
    layerMergeOp->setHoldOut(hold_out);

    layerMergeOp->setColorTargetPreviousLayer(kMainColorTarget);
    layerMergeOp->setDepthTargetPreviousLayer(kMainDepthTarget);
    layerMergeOp->setAlphaPreviousLayer(1.0f);

    layerMergeOp->setColorTargetCurrentLayer(kLayerColorTarget);
    layerMergeOp->setDepthTargetCurrentLayer(kLayerDepthTarget);
    layerMergeOp->setAlphaCurrentLayer(object_alpha);

    layerMergeOp->setColorTargetEdges(kTempColorTarget);
    layerMergeOp->setDepthTargetEdges(kTempDepthTarget);
    layerMergeOp->setAlphaEdges(1.0f);
    layerMergeOp->setUseColorTargetEdges(m_edge_enable);

    layerMergeOp->setColorTargetBackground(kBackgroundColorTarget);
    layerMergeOp->setDepthTargetBackground(kBackgroundDepthTarget);
    layerMergeOp->setAlphaBackground(1.0f);

    layerMergeOp->setRenderTargets(targets, kMainColorTarget, 2);
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
    const bool verbose = false;
    MMSOLVER_VRB("DisplayLayer::getOperation: "
                 << m_name.asChar() << " current_op: " << current_op);
    const auto count = DisplayLayerPasses::kLayerPassesCount;
    if (current_op >= 0 && current_op < count) {
        return DisplayLayer::m_ops[current_op];
    }
    return nullptr;
}

}  // namespace render
}  // namespace mmsolver
