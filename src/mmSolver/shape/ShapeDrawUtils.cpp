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

// Maya
#include <maya/MDistance.h>
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MTransformationMatrix.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>

namespace mmsolver {

MStatus objectIsBelowCamera(
    const MDagPath &objPath,
    const MDagPath &cameraPath,
    bool &belowCamera
) {
    MStatus status = MS::kSuccess;
    belowCamera = false;

    MDagPath cameraTransformPath(cameraPath);
    CHECK_MSTATUS(cameraTransformPath.pop(1));
    MString cameraTransformName = cameraTransformPath.fullPathName();

    MString tfmName = "";
    MDagPath transformPath(objPath);
    while (true) {
        if (transformPath.length() == 0) {
            break;
        }
        CHECK_MSTATUS(transformPath.pop(1));
        tfmName = transformPath.fullPathName();
        if (cameraTransformName == tfmName) {
            belowCamera = true;
            break;
        }
    }
    return status;
}

MStatus getViewportScaleRatio(
    const MHWRender::MFrameContext &frameContext,
    double &out_scale)
{
    MStatus status = MS::kSuccess;

    // Use the camera position.
    MDoubleArray view_pos = frameContext.getTuple(
        MFrameContext::kViewPosition, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MPoint camera_pos(view_pos[0], view_pos[1], view_pos[2]);

    // Get Viewport size
    int originX = 0;
    int originY = 0;
    int width = 0;
    int height = 0;
    frameContext.getViewportDimensions(originX, originY, width, height);

    // Convert viewport window into world-space near/far clipping
    // points.
    MPoint nearPoint1;
    MPoint nearPoint2;
    MPoint farPoint1;
    MPoint farPoint2;
    double originXd = static_cast<double>(originX);
    double originYd = static_cast<double>(originY);
    double widthd = static_cast<double>(width);
    double heightd = static_cast<double>(height);
    double y = originYd + (heightd * 0.5);
    frameContext.viewportToWorld(originXd, y, nearPoint1, farPoint1);
    frameContext.viewportToWorld(widthd, y, nearPoint2, farPoint2);

    // Normalize the scale values.
    auto oneUnitVector1 = MVector(
        camera_pos.x - nearPoint1.x,
        camera_pos.y - nearPoint1.y,
        camera_pos.z - nearPoint1.z);
    auto oneUnitVector2 = MVector(
        camera_pos.x - nearPoint2.x,
        camera_pos.y - nearPoint2.y,
        camera_pos.z - nearPoint2.z);
    oneUnitVector1.normalize();
    oneUnitVector2.normalize();
    auto oneUnitPoint1 = MPoint(oneUnitVector1);
    auto oneUnitPoint2 = MPoint(oneUnitVector2);
    out_scale = oneUnitPoint1.distanceTo(oneUnitPoint2);
    return status;
}

} // namespace mmsolver
