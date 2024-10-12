/*
 * Copyright (C) 2021, 2024 David Cattermole.
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

// STL
#include <cstdint>

// Maya
#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "BackgroundStyle.h"
#include "CullFace.h"
#include "DisplayStyle.h"
#include "EdgeDetectMode.h"
#include "LayerMode.h"
#include "RenderColorFormat.h"
#include "RenderMode.h"
#include "mmSolver/nodeTypeIds.h"

namespace mmsolver {
namespace render {

// Constant values
const float kTransparentBlackColor[] = {0.0f, 0.0f, 0.0f, 0.0f};

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

// Default parameters
const BackgroundStyle kBackgroundStyleDefault = BackgroundStyle::kMayaDefault;
const RenderColorFormat kRenderColorFormatDefault =
    RenderColorFormat::kRGBA16BitFloat;

// Standard Renderer Constants
const MString kRenderGlobalsStandardNodeName = "mmRenderGlobalsStandard";
const MString kRendererStandardCmdName = "mmRendererStandard";
const char kRendererStandardName[] = "mmRendererStandard";
const char kRendererStandardUiName[] = "MM Standard Renderer";
const MString kRendererStandardCreateNodeCommand =
    "string $mm_globals_node = `createNode \"" +
    MString(MM_RENDER_GLOBALS_STANDARD_TYPE_NAME) + "\" -name \"" +
    MString(kRenderGlobalsStandardNodeName) + "\" -shared -skipSelect`;\n" +
    "if (size($mm_globals_node) > 0) {\n" +
    "    lockNode -lock on $mm_globals_node;\n" + "}\n";

// Silhouette Renderer Constants
const MString kRenderGlobalsSilhouetteNodeName = "mmRenderGlobalsSilhouette";
const MString kRendererSilhouetteCmdName = "mmRendererSilhouette";
const char kRendererSilhouetteName[] = "mmRendererSilhouette";
const char kRendererSilhouetteUiName[] = "MM Silhouette Renderer";
const MString kRendererSilhouetteCreateNodeCommand =
    "string $mm_globals_node = `createNode \"" +
    MString(MM_RENDER_GLOBALS_SILHOUETTE_TYPE_NAME) + "\" -name \"" +
    MString(kRenderGlobalsSilhouetteNodeName) + "\" -shared -skipSelect`;\n" +
    "if (size($mm_globals_node) > 0) {\n" +
    "    lockNode -lock on $mm_globals_node;\n" + "}\n";

// Silhouette Attribute Names
const MString kAttrNameSilhouetteEnable = "enable";
const MString kAttrNameSilhouetteOverrideColor = "overrideColor";
const MString kAttrNameSilhouetteDepthOffset = "depthOffset";
const MString kAttrNameSilhouetteWidth = "width";
const MString kAttrNameSilhouetteColor = "color";
const MString kAttrNameSilhouetteColorR = "colorR";
const MString kAttrNameSilhouetteColorG = "colorG";
const MString kAttrNameSilhouetteColorB = "colorB";
const MString kAttrNameSilhouetteAlpha = "alpha";
const MString kAttrNameSilhouetteCullFace = "cullFace";
const MString kAttrNameSilhouetteOperationNum = "operationNum";

// Silhouette Renderer Attribute Default Values
const bool kSilhouetteEnableDefault = true;
// We enable 'override color' by default, so that users with wireframe
// on shaded can see the obvious effect right away.
const bool kSilhouetteOverrideColorDefault = true;
const float kSilhouetteDepthOffsetDefault = -1.0f;
const float kSilhouetteWidthDefault = 2.0f;
const float kSilhouetteColorDefault[] = {0.0f, 1.0f, 0.0f};
const float kSilhouetteAlphaDefault = 1.0f;
const CullFace kSilhouetteCullFaceDefault = CullFace::kBack;
const uint8_t kSilhouetteOperationNumDefault = UINT8_MAX;

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_DATA_CONSTANTS_H
