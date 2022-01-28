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
 * Common functions used for camera calibration.
 */

#ifndef MAYA_MM_SOLVER_CORE_CALIBRATE_COMMON_H
#define MAYA_MM_SOLVER_CORE_CALIBRATE_COMMON_H

// Internal
#include "core/mmdata.h"

namespace calibrate {

// How to orient the camera calibration to a specific plane.
enum class OrientationPlane {
    ZX = 0,
    XZ = 1,
    XY = 2,
    YX = 3,
    ZY = 4,
    YZ = 5,
};

// How to scale the camera calibration.
enum class SceneScaleMode {
    // An invalid state. This should not be used.
    Unknown = 0,

    // Scale the scene uniformly.
    UniformScale = 1,

    // Scale the scene based on the camera's height (Y) axis.
    CameraHeight = 2,
};

struct CameraParameters {
    double focalLength_mm_;
    double filmBackWidth_mm_;
    double filmBackHeight_mm_;
    mmdata::Point2D principalPoint_;
    mmdata::Matrix4x4 transformMatrix_;
    mmdata::Point2D vanishingPointA_;
    mmdata::Point2D vanishingPointB_;

    CameraParameters()
            : focalLength_mm_(35.0)
            , filmBackWidth_mm_(36.0)
            , filmBackHeight_mm_(24.0)
            , principalPoint_()
            , transformMatrix_()
            , vanishingPointA_(0.0, 1.0)
            , vanishingPointB_(1.0, 0.0) {}
};

// Intersection of two parallel 2D lines in a projective camera,
// creating a vanishing point.
bool
calcVanishingPointFromLinePair(
    mmdata::LinePair2D linePair,
    mmdata::Point2D &outPoint);

// With a single vanishing point (vpA), and a direction of the horizon
// line, and the focal length we can re-arrange and estimate a second
// vanishing point.
mmdata::Point2D
estimateSecondVanishingPoint(
    mmdata::Point2D vpA,
    mmdata::Point2D principalPoint,
    mmdata::Point2D horizonDirection,
    double focalLengthFactor);

// Compute the focal length from two vanishing points.
bool
calcFocalLength(
    mmdata::Point2D vpA,
    mmdata::Point2D vpB,
    mmdata::Point2D principalPoint,
    double &outFocalLength);

// Calculate the rotation matrix from two vanishing points.
bool
calcCameraRotationMatrix(
    mmdata::Point2D vpA,
    mmdata::Point2D vpB,
    mmdata::Point2D principalPoint,
    double focalLengthFactor,
    mmdata::Matrix4x4 &outMatrix);

// Create an orientation matrix, to align the camera calibration.
mmdata::Matrix4x4
createOrientationMatrix(
    OrientationPlane orientPlane,
    bool flipX,
    bool flipY,
    bool flipZ);

// Calculate the translation of the camera.
bool
calcTranslationVector(
    mmdata::Point2D originPoint,
    mmdata::Point2D principalPoint,
    double angleOfView_radians,
    mmdata::Vector3D &outVector);

// Scale the camera transform based on the scene scale logic and a
// single distance value.
bool
applySceneScale(
    mmdata::Matrix4x4 cameraTransform,
    SceneScaleMode sceneScaleMode,
    double distance_cm,
    mmdata::Matrix4x4 &outCameraTransform);

// Calculate the camera parameters, both intrinsic (angle of view) and
// extrinsic (rotations and translations).
//
// The scale is arbitrary, but the 'sceneScaleMode' can be used to
// scale the camera.
bool
calcCameraParameters(
    mmdata::Point2D originPoint,
    mmdata::Point2D principalPoint,
    mmdata::Point2D vanishingPointA,
    mmdata::Point2D vanishingPointB,
    SceneScaleMode sceneScaleMode,
    double sceneScaleDistance_cm,
    double focalLengthFactor,
    double filmBackWidth_mm,
    double filmBackHeight_mm,
    CameraParameters &outCameraParameters);

} // namespace calibrate

#endif //MAYA_MM_SOLVER_CORE_CALIBRATE_COMMON_H
