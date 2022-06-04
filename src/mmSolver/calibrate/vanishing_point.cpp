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
 */

#include "vanishing_point.h"

// STL
#include <cmath>

// MM Solver
#include "mmSolver/calibrate/calibrate_common.h"
#include "mmSolver/core/mmcamera.h"
#include "mmSolver/core/mmcoord.h"
#include "mmSolver/core/mmdata.h"
#include "mmSolver/core/mmmath.h"
#include "mmSolver/utilities/debug_utils.h"

namespace calibrate {

// Most research papers focus on two vanishing points, and this
// example only has one.  With only one vanishing point we must
// estimate the second vanishing point, and then continue with the two
// vanishing point maths.
//
// fSpy (https://github.com/stuffmatic/fSpy) was used as inspiration
// for this function.
//
// See paper "Using vanishing points for camera calibration and coarse
// 3D reconstruction from a single image" (2000), section 3
// "Calibration using two vanishing points".
//
bool oneVanishingPoint(double focalLength_mm, double filmBackWidth_mm,
                       double filmBackHeight_mm, mmdata::Point2D originPoint,
                       mmdata::Point2D principalPoint,
                       mmdata::Point2D vanishingPointA,
                       mmdata::Point2D horizonPointA,
                       mmdata::Point2D horizonPointB,
                       SceneScaleMode sceneScaleMode, double sceneScaleDistance,
                       CameraParameters &outCameraParameters) {
    originPoint = mmcoord::convertPoint2D(
        mmcoord::Point2DSpace::Marker, mmcoord::Point2DSpace::ImageNormalized,
        originPoint, filmBackWidth_mm, filmBackHeight_mm);

    vanishingPointA = mmcoord::convertPoint2D(
        mmcoord::Point2DSpace::Marker, mmcoord::Point2DSpace::ImageNormalized,
        vanishingPointA, filmBackWidth_mm, filmBackHeight_mm);

    principalPoint = mmcoord::convertPoint2D(
        mmcoord::Point2DSpace::Marker, mmcoord::Point2DSpace::ImageNormalized,
        principalPoint, filmBackWidth_mm, filmBackHeight_mm);

    // This is an estimate of the camera's roll.
    auto horizonStart = mmcoord::convertPoint2D(
        mmcoord::Point2DSpace::Marker, mmcoord::Point2DSpace::ImageNormalized,
        horizonPointA, filmBackWidth_mm, filmBackHeight_mm);
    auto horizonEnd = mmcoord::convertPoint2D(
        mmcoord::Point2DSpace::Marker, mmcoord::Point2DSpace::ImageNormalized,
        horizonPointB, filmBackWidth_mm, filmBackHeight_mm);
    auto horizonDirection = mmmath::normalize(mmdata::Point2D(
        horizonEnd.x_ - horizonStart.x_, horizonEnd.y_ - horizonStart.y_));

    // Initialize focal length with user given focal length, and
    // convert into a relative focal length.
    auto focalLengthRatio = 2.0 * (focalLength_mm / filmBackWidth_mm);

    // Guess the second vanishing point from the first vanishing point
    // and horizon direction.
    auto vanishingPointB = estimateSecondVanishingPoint(
        vanishingPointA, principalPoint, horizonDirection, focalLengthRatio);

    auto ok = calcCameraParameters(
        originPoint, principalPoint, vanishingPointA, vanishingPointB,
        sceneScaleMode, sceneScaleDistance, focalLengthRatio, filmBackWidth_mm,
        filmBackHeight_mm, outCameraParameters);
    return ok;
}

// See paper "Camera calibration using two or three vanishing points"
// (2012), section 2 "Camera calibration using two vanishing points".
//
// See paper "Using vanishing points for camera calibration and coarse
// 3D reconstruction from a single image" (2000), section 3
// "Calibration using two vanishing points".
//
bool twoVanishingPoints(double focalLength_mm, double filmBackWidth_mm,
                        double filmBackHeight_mm, mmdata::Point2D originPoint,
                        mmdata::Point2D principalPoint,
                        mmdata::Point2D vanishingPointA,
                        mmdata::Point2D vanishingPointB,
                        SceneScaleMode sceneScaleMode,
                        double sceneScaleDistance_cm,
                        CameraParameters &outCameraParameters) {
    vanishingPointA = mmcoord::convertPoint2D(
        mmcoord::Point2DSpace::Marker, mmcoord::Point2DSpace::ImageNormalized,
        vanishingPointA, filmBackWidth_mm, filmBackHeight_mm);

    vanishingPointB = mmcoord::convertPoint2D(
        mmcoord::Point2DSpace::Marker, mmcoord::Point2DSpace::ImageNormalized,
        vanishingPointB, filmBackWidth_mm, filmBackHeight_mm);

    originPoint = mmcoord::convertPoint2D(
        mmcoord::Point2DSpace::Marker, mmcoord::Point2DSpace::ImageNormalized,
        originPoint, filmBackWidth_mm, filmBackHeight_mm);

    principalPoint = mmcoord::convertPoint2D(
        mmcoord::Point2DSpace::Marker, mmcoord::Point2DSpace::ImageNormalized,
        principalPoint, filmBackWidth_mm, filmBackHeight_mm);

    // Initialize focal length with user given focal length, and
    // convert into a relative focal length.
    auto focalLengthRatio = 2.0 * (focalLength_mm / filmBackWidth_mm);

    auto ok = calcFocalLength(vanishingPointA, vanishingPointB, principalPoint,
                              focalLengthRatio);
    if (!ok) {
        MMSOLVER_ERR("Failed to calculate focal length.");
        return false;
    }

    ok = calcCameraParameters(
        originPoint, principalPoint, vanishingPointA, vanishingPointB,
        sceneScaleMode, sceneScaleDistance_cm, focalLengthRatio,
        filmBackWidth_mm, filmBackHeight_mm, outCameraParameters);
    return ok;
};

}  // namespace calibrate
