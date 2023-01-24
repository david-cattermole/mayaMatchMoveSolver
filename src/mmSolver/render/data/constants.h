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
 * Constant values used in the mmSolver renderer.
 */

#ifndef MM_SOLVER_RENDER_DATA_CONSTANTS_H
#define MM_SOLVER_RENDER_DATA_CONSTANTS_H

// Maya
#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "BackgroundStyle.h"
#include "DisplayStyle.h"
#include "EdgeDetectMode.h"
#include "LayerMode.h"
#include "RenderColorFormat.h"
#include "RenderMode.h"

namespace mmsolver {
namespace render {

// Enumerate the target indexing
enum TargetId {
    // Main render targets - where the final pixels will be
    // copied/blended and finally presented to the screen.
    kMainColorTarget = 0,
    kMainDepthTarget,

    // Layer render target buffers - where layers will be rendered
    // before being merged into the main render targets.
    kLayerColorTarget,
    kLayerDepthTarget,

    // A temporary render target to render and then blend/copy into
    // other targets.
    kTempColorTarget,

    // Always last field, used as 'number of items'.
    kTargetCount
};

// Renderer Target names.
#define kMainColorTargetName "__mmRenderer_MainColorTarget1__"
#define kMainDepthTargetName "__mmRenderer_MainDepthTarget1__"
#define kLayerColorTargetName "__mmRenderer_LayerColorTarget2__"
#define kLayerDepthTargetName "__mmRenderer_LayerDepthTarget2__"
#define kTempColorTargetName "__mmRenderer_TempColorTarget3__"

// Constant values
const char kRendererUiName[] = "mmRenderer (beta)";
const float kTransparentBlackColor[] = {0.0f, 0.0f, 0.0f, 0.0f};

// The node Maya uses to store all attributes that define how the
// hardware renderer works - such as formats/bit-depths and
// anti-aliasing options.
const MString kHardwareRenderGlobalsNodeName = "hardwareRenderingGlobals";

// The node that all Maya display layers are connected to - this node
// "manages" all display layers.
const MString kDisplayLayerManagerNodeName = "layerManager";

// Default parameters
const BackgroundStyle kBackgroundStyleDefault = BackgroundStyle::kMayaDefault;
const DisplayStyle kDisplayStyleDefault = DisplayStyle::kHiddenLine;
const EdgeDetectMode kEdgeDetectModeDefault = EdgeDetectMode::kSobel;
const LayerMode kLayerModeDefault = LayerMode::kZDepth;
const RenderColorFormat kRenderColorFormatDefault =
    RenderColorFormat::kRGBA16BitFloat;
const RenderMode kRenderModeDefault = RenderMode::kFour;
const bool kEdgeEnableDefault = false;
const bool kLayerDrawDebugDefault = false;
const bool kVisibilityDefault = true;
const float kEdgeAlphaDefault = 1.0f;
const float kEdgeColorDefault[] = {1.0f, 0.0f, 0.0f, 1.0f};
const float kEdgeThicknessDefault = 1.0f;
const float kEdgeThresholdDefault = 1.0f;
const float kLayerMixDefault = 1.0f;
const float kWireframeAlphaDefault = 1.0f;
const int32_t kDisplayOrderDefault = -1;

// Render Operation Pass Names
const MString kLayerCopyEndOpName = "mmRenderer_Layer_CopyEnd_";
const MString kLayerCopyStartOpName = "mmRenderer_Layer_CopyStart_";
const MString kLayerDepthPassName = "mmRenderer_Layer_DepthRender_";
const MString kLayerEdgeDetectOpName = "mmRenderer_Layer_EdgeDetectOp_";
const MString kLayerMergeOpName = "mmRenderer_Layer_Merge_";
const MString kLayerWireframeBlendOpName = "mmRenderer_Layer_WireframeBlend_";
const MString kLayerWireframePassName = "mmRenderer_Layer_WireframeRender_";
const MString kPresentOpName = "mmRenderer_PresentTarget";
const MString kSceneBackgroundPassName = "mmRenderer_SceneRender_Background";
const MString kSceneDepthPassName = "mmRenderer_SceneRender_DepthOnly";
const MString kSceneManipulatorPassName = "mmRenderer_SceneRender_Manipulator";
const MString kSceneSelectionPassName = "mmRenderer_SceneRender_Select";

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_DATA_CONSTANTS_H
