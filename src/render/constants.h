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

#ifndef MAYA_MM_SOLVER_RENDER_CONSTANTS_H
#define MAYA_MM_SOLVER_RENDER_CONSTANTS_H

#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MRenderTargetManager.h>

namespace mmsolver {
namespace render {

// Enumerate the target indexing
enum TargetId
{
    kMyColorTarget = 0,
    kMyDepthTarget,
    kMyAuxColorTarget,

    // Always last field, used as 'number of items'.
    kTargetCount
};

// Renderer Target names.
#define kMyColorTargetName  "__mmRenderer_ColorTarget1__"
#define kMyDepthTargetName  "__mmRenderer_DepthTarget1__"
#define kMyAuxColorTargetName  "__mmRenderer_ColorTarget2__"

// Constant values
const char kRendererUiName[] = "mmRenderer (beta)";
const float kTransparentBlackColor[] = {0.0f, 0.0f, 0.0f, 0.0f};

// Default parameters
const float kEdgeColorDefault[] = {1.0f, 0.0f, 0.0f, 1.0f};
const float kWireframeAlphaDefault = 1.0f;
const float kEdgeThicknessDefault = 1.5f;
const float kEdgeThresholdDefault = 0.05f;

} // namespace render
} // namespace mmsolver

#endif // MAYA_MM_SOLVER_RENDER_CONSTANTS_H
