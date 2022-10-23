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
 * Calculates camera translation, rotation and focal length from 1 or
 * 2 vanishing points in a single image.
 */

#ifndef MM_CAMERA_CALIBRATION_NODE_H
#define MM_CAMERA_CALIBRATION_NODE_H

#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MPxNode.h>
#include <maya/MString.h>
#include <maya/MTime.h>
#include <maya/MTypeId.h>

namespace mmsolver {

enum class CameraApertureUnit {
    Millimeters = 0,
    Inches = 1,
};

enum class CalibrationMode {
    // Disable calibration.
    Disable = 0,

    // 1 point perspective (parallel lines)
    OneVanishingPoint = 1,

    // 1 point perspective + horizon line (parallel lines and horizon)
    OneVanishingPointAndHorizonLine = 2,

    // 2 point perspective (rectangle)
    TwoVanishingPoints = 3,
};

class MMCameraCalibrateNode : public MPxNode {
public:
    MMCameraCalibrateNode();

    virtual ~MMCameraCalibrateNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    //
    // Calibration mode to use.
    static MObject a_calibrationMode;

    // Camera attributes
    static MObject a_focalLength;
    static MObject a_cameraApertureUnit;
    static MObject a_cameraAperture;
    static MObject a_horizontalFilmAperture;
    static MObject a_verticalFilmAperture;

    // Scene Scale
    static MObject a_sceneScaleMode;
    static MObject a_uniformScale;
    static MObject a_cameraHeight;

    // Origin
    static MObject a_originPoint;
    static MObject a_originPointX;
    static MObject a_originPointY;

    static MObject a_rotatePlaneX;
    static MObject a_rotatePlaneY;
    static MObject a_rotatePlaneZ;
    static MObject a_rotatePlane;
    static MObject a_rotateOrder;

#if 0
    // Principal Point
    static MObject a_principalPoint;
    static MObject a_principalPointX;
    static MObject a_principalPointY;
#endif

    // Horizon Line
    static MObject a_horizonPointA;
    static MObject a_horizonPointAX;
    static MObject a_horizonPointAY;

    static MObject a_horizonPointB;
    static MObject a_horizonPointBX;
    static MObject a_horizonPointBY;

    // Vanishing Points
    static MObject a_vanishingPointA;
    static MObject a_vanishingPointAX;
    static MObject a_vanishingPointAY;

    static MObject a_vanishingPointB;
    static MObject a_vanishingPointBX;
    static MObject a_vanishingPointBY;

    // Output Attributes
    static MObject a_outMatrixInverse;
    static MObject a_outMatrix;

    static MObject a_outFocalLength;

    static MObject a_outCameraAperture;
    static MObject a_outHorizontalFilmAperture;
    static MObject a_outVerticalFilmAperture;

#if 0
    static MObject a_outFilmOffset;
    static MObject a_outHorizontalFilmOffset;
    static MObject a_outVerticalFilmOffset;

    static MObject a_outPrincipalPoint;
    static MObject a_outPrincipalPointX;
    static MObject a_outPrincipalPointY;
#endif

    static MObject a_outVanishingPointA;
    static MObject a_outVanishingPointAX;
    static MObject a_outVanishingPointAY;

    static MObject a_outVanishingPointB;
    static MObject a_outVanishingPointBX;
    static MObject a_outVanishingPointBY;
};

}  // namespace mmsolver

#endif  // MM_CAMERA_CALIBRATION_NODE_H
