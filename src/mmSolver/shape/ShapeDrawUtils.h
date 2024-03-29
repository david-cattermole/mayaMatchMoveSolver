/*
 * Copyright (C) 2022 David Cattermole.
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

#ifndef MM_MARKER_DRAW_UTILS_H
#define MM_MARKER_DRAW_UTILS_H

// Maya
#include <maya/MDistance.h>
#include <maya/MPoint.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MVector.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>

namespace mmsolver {

MStatus objectIsBelowCamera(const MDagPath &objPath, const MDagPath &cameraPath,
                            bool &belowCamera);

MStatus getViewportScaleRatio(const MHWRender::MFrameContext &frameContext,
                              double &out_scale);

}  // namespace mmsolver

#endif  // MM_MARKER_DRAW_UTILS_H