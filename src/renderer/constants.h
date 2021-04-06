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

#ifndef MAYA_MM_SOLVER_MM_RENDERER_CONSTANTS_H
#define MAYA_MM_SOLVER_MM_RENDERER_CONSTANTS_H

#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MRenderTargetManager.h>

namespace mmsolver {
namespace renderer {

// Enumerate the target indexing
enum TargetId
{
    kMyColorTarget = 0,
    kMyDepthTarget,
    kMyAuxColorTarget,
    // Always last field, used as 'number of items'.
    kTargetCount
};

#define kMyColorTargetName  "__mmRenderer_ColorTarget1__"
#define kMyDepthTargetName  "__mmRenderer_DepthTarget1__"
#define kMyAuxColorTargetName  "__mmRenderer_ColorTarget2__"

} // namespace renderer
} // namespace mmsolver

#endif // MAYA_MM_SOLVER_MM_RENDERER_CONSTANTS_H
