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
    //
    // This is also the previous layer's result, that the current layer is
    // rendered on top of.
    kMainColorTarget = 0,
    kMainDepthTarget,

    // Layer render target buffers - where layers will be rendered
    // before being merged into the main render targets.
    kLayerColorTarget,
    kLayerDepthTarget,

    // A temporary render target to render and then blend/copy into
    // other targets.
    kTempColorTarget,
    kTempDepthTarget,

    // The Maya background, and image planes.
    kBackgroundColorTarget,
    kBackgroundDepthTarget,

    // Always last field, used as 'number of items'.
    kTargetCount
};

// Renderer Target names.
#define kMainColorTargetName "__mmRenderer_MainColorTarget1__"
#define kMainDepthTargetName "__mmRenderer_MainDepthTarget1__"
#define kLayerColorTargetName "__mmRenderer_LayerColorTarget2__"
#define kLayerDepthTargetName "__mmRenderer_LayerDepthTarget2__"
#define kTempColorTargetName "__mmRenderer_TempColorTarget3__"
#define kTempDepthTargetName "__mmRenderer_TempDepthTarget3__"
#define kBackgroundColorTargetName "__mmRenderer_BackgroundColorTarget4__"
#define kBackgroundDepthTargetName "__mmRenderer_BackgroundDepthTarget4__"

// Constant values
const char kRendererUiName[] = "mmRenderer (beta)";
const float kTransparentBlackColor[] = {0.0f, 0.0f, 0.0f, 0.0f};

const MString kRenderGlobalsNodeName = "mmRenderGlobals";

// The node Maya uses to store all attributes that define how the
// hardware renderer works - such as formats/bit-depths and
// anti-aliasing options.
const MString kHardwareRenderGlobalsNodeName = "hardwareRenderingGlobals";

// The node that all Maya display layers are connected to - this node
// "manages" all display layers.
const MString kDisplayLayerManagerNodeName = "layerManager";

// Default parameters
const BackgroundStyle kBackgroundStyleDefault = BackgroundStyle::kMayaDefault;
const RenderColorFormat kRenderColorFormatDefault =
    RenderColorFormat::kRGBA16BitFloat;

const bool kLayerVisibilityDefault = true;
const int32_t kLayerDisplayOrderDefault = -1;
const LayerMode kLayerModeDefault = LayerMode::kZDepth;
const float kLayerMixDefault = 1.0f;
const bool kLayerDrawDebugDefault = false;

const DisplayStyle kObjectDisplayStyleDefault =
    DisplayStyle::kNoDisplayStyleOverride;
const bool kObjectDisplayTexturesDefault = false;
const float kObjectAlphaDefault = 1.0f;

const bool kEdgeEnableDefault = false;
const float kEdgeColorDefault[] = {1.0f, 0.0f, 0.0f, 1.0f};
const float kEdgeAlphaDefault = 1.0f;
const EdgeDetectMode kEdgeDetectModeDefault = EdgeDetectMode::k3dSilhouette;
const float kEdgeThicknessDefault = 1.0f;
const float kEdgeThresholdDefault = 1.0f;
const float kEdgeThresholdColorDefault = 1.0f;
const float kEdgeThresholdAlphaDefault = 1.0f;
const float kEdgeThresholdDepthDefault = 1.0f;

// Render Operation Pass Names
const MString kBeginClearMainTargetOpName = "mmRenderer_ClearMainTarget";
const MString kBeginClearBackgroundTargetOpName = "mmRenderer_ClearBackgroundTarget";
const MString kLayerClearLayerTargetOpName = "mmRenderer_Layer_ClearLayerTarget_";
const MString kLayerClearTempTargetOpName = "mmRenderer_Layer_ClearTempTarget_";
const MString kLayerCopyEdgeOpName = "mmRenderer_Layer_CopyEdge_";
const MString kLayerCopyOpName = "mmRenderer_Layer_Copy_";
const MString kLayerDepthPassName = "mmRenderer_Layer_DepthRender_";
const MString kLayerEdgeDetectOpName = "mmRenderer_Layer_EdgeDetectOp_";
const MString kLayerEdgePassOpName = "mmRenderer_Layer_EdgeRender_";
const MString kLayerMergeOpName = "mmRenderer_Layer_Merge_";
const MString kLayerObjectPassName = "mmRenderer_Layer_ObjectRender_";
const MString kPresentOpName = "mmRenderer_PresentTarget";
const MString kSceneBackgroundPassName = "mmRenderer_SceneRender_Background";
const MString kSceneManipulatorPassName = "mmRenderer_SceneRender_Manipulator";

// Attribute Names
const MString kAttrNameLayerVisibility = "visibility";
const MString kAttrNameLayerDisplayOrder = "displayOrder";
const MString kAttrNameLayerMode = "mmLayerMode";
const MString kAttrNameLayerMix = "mmLayerMix";
const MString kAttrNameLayerDrawDebug = "mmLayerDrawDebug";

const MString kAttrNameObjectDisplayStyle = "mmObjectDisplayStyle";
const MString kAttrNameObjectAlpha = "mmObjectAlpha";

const MString kAttrNameEdgeEnable = "mmEdgeEnable";
const MString kAttrNameEdgeColorR = "mmEdgeColorR";
const MString kAttrNameEdgeColorG = "mmEdgeColorG";
const MString kAttrNameEdgeColorB = "mmEdgeColorB";
const MString kAttrNameEdgeAlpha = "mmEdgeAlpha";
const MString kAttrNameEdgeDetectMode = "mmEdgeDetectMode";
const MString kAttrNameEdgeThickness = "mmEdgeThickness";
const MString kAttrNameEdgeThreshold = "mmEdgeThreshold";
const MString kAttrNameEdgeThresholdColor = "mmEdgeThresholdColor";
const MString kAttrNameEdgeThresholdAlpha = "mmEdgeThresholdAlpha";
const MString kAttrNameEdgeThresholdDepth = "mmEdgeThresholdDepth";

// Clear Masks
const auto CLEAR_MASK_NONE =
    static_cast<uint32_t>(MHWRender::MClearOperation::kClearNone);
const auto CLEAR_MASK_ALL =
    static_cast<uint32_t>(MHWRender::MClearOperation::kClearAll);
const auto CLEAR_MASK_DEPTH =
    static_cast<uint32_t>(MHWRender::MClearOperation::kClearDepth);
const auto CLEAR_MASK_COLOR =
    static_cast<uint32_t>(MHWRender::MClearOperation::kClearColor);

// Display modes
const auto DISPLAY_MODE_SHADED =
    static_cast<MHWRender::MSceneRender::MDisplayMode>(
        MHWRender::MSceneRender::kShaded);
const auto DISPLAY_MODE_SHADED_TEXTURED =
    static_cast<MHWRender::MSceneRender::MDisplayMode>(
        MHWRender::MSceneRender::kShaded | MHWRender::MSceneRender::kTextured);
const auto DISPLAY_MODE_WIREFRAME =
    static_cast<MHWRender::MSceneRender::MDisplayMode>(
        MHWRender::MSceneRender::kWireFrame);
const auto DISPLAY_MODE_SHADED_WIREFRAME =
    static_cast<MHWRender::MSceneRender::MDisplayMode>(
        MHWRender::MSceneRender::kShaded | MHWRender::MSceneRender::kWireFrame);
const auto DISPLAY_MODE_SHADED_WIREFRAME_TEXTURED =
    static_cast<MHWRender::MSceneRender::MDisplayMode>(
        MHWRender::MSceneRender::kShaded | MHWRender::MSceneRender::kWireFrame |
            MHWRender::MSceneRender::kTextured);

// Draw these objects for transparency.
const auto WIRE_DRAW_OBJECT_TYPES =
    ~(MHWRender::MFrameContext::kExcludeMeshes |
        MHWRender::MFrameContext::kExcludeNurbsCurves |
        MHWRender::MFrameContext::kExcludeNurbsSurfaces |
        MHWRender::MFrameContext::kExcludeSubdivSurfaces);

// Draw all non-geometry normally.
const auto NON_WIRE_DRAW_OBJECT_TYPES =
    ((~WIRE_DRAW_OBJECT_TYPES) | MHWRender::MFrameContext::kExcludeImagePlane |
        MHWRender::MFrameContext::kExcludePluginShapes);

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_DATA_CONSTANTS_H
