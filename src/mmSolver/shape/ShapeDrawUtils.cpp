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

// STL
#include <cmath>

// Maya
#include <maya/MDistance.h>
#include <maya/MPoint.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MVector.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>

// MM Solver
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

MStatus objectIsBelowCamera(const MDagPath &objPath, const MDagPath &cameraPath,
                            bool &belowCamera) {
    MStatus status = MS::kSuccess;
    belowCamera = false;

    MDagPath cameraTransformPath(cameraPath);
    MMSOLVER_CHECK_MSTATUS(cameraTransformPath.pop(1));
    MString cameraTransformName = cameraTransformPath.fullPathName();

    MString tfmName = "";
    MDagPath transformPath(objPath);
    while (true) {
        if (transformPath.length() == 0) {
            break;
        }
        MMSOLVER_CHECK_MSTATUS(transformPath.pop(1));
        tfmName = transformPath.fullPathName();
        if (cameraTransformName == tfmName) {
            belowCamera = true;
            break;
        }
    }
    return status;
}

MStatus getViewportScaleRatio(const MHWRender::MFrameContext &frameContext,
                              double &out_scale) {
    MStatus status = MS::kSuccess;

    // Use the camera position.
    MDoubleArray view_pos =
        frameContext.getTuple(MFrameContext::kViewPosition, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    MPoint camera_pos(view_pos[0], view_pos[1], view_pos[2]);

    // Get Viewport size
    int origin_x = 0;
    int origin_y = 0;
    int width = 0;
    int height = 0;
    frameContext.getViewportDimensions(origin_x, origin_y, width, height);

    // Convert viewport window into world-space near/far clipping
    // points.
    MPoint near_point1;
    MPoint near_point2;
    MPoint far_point1;
    MPoint far_point2;
    double origin_x_d = static_cast<double>(origin_x);
    double origin_y_d = static_cast<double>(origin_y);
    double width_d = static_cast<double>(width);
    double height_d = static_cast<double>(height);
    double midpoint_y = origin_y_d + (height_d * 0.5);
    frameContext.viewportToWorld(origin_x_d, midpoint_y, near_point1,
                                 far_point1);
    frameContext.viewportToWorld(width_d, midpoint_y, near_point2, far_point2);

    // Normalize the scale values.
    auto one_unit_vector1 =
        MVector(far_point1.x - camera_pos.x, far_point1.y - camera_pos.y,
                far_point1.z - camera_pos.z);
    auto one_unit_vector2 =
        MVector(far_point2.x - camera_pos.x, far_point2.y - camera_pos.y,
                far_point2.z - camera_pos.z);
    one_unit_vector1.normalize();
    one_unit_vector2.normalize();

    auto radian_angle = one_unit_vector1.angle(one_unit_vector2);
    out_scale = std::tan(radian_angle * 0.5);
    return status;
}

}  // namespace mmsolver
