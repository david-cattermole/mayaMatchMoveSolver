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

#ifndef MAYA_MM_SOLVER_CORE_CALIBRATE_VANISHING_POINT_H
#define MAYA_MM_SOLVER_CORE_CALIBRATE_VANISHING_POINT_H


// Internal
#include "core/mmdata.h"
#include "calibrate_common.h"

namespace calibrate {

// One point perspective.
//
// Using two vanishing points, calculate the camera parameters; camera
// translation, and camera rotation.
//
// Note: The aspect ratio from the film back width and height must be
// consistent and accurate for the given camera.  If the image
// resolution 1920 x 1080, with aspect ratio 16:9, then the film back
// must have the exact same aspect ratio.
//
bool oneVanishingPoint(
    double focalLength_mm,
    double filmBackWidth_mm,
    double filmBackHeight_mm,
    mmdata::Point2D originPoint,
    mmdata::Point2D principalPoint,
    mmdata::Point2D vanishingPointA,
    mmdata::Point2D horizonPointA,
    mmdata::Point2D horizonPointB,
    SceneScaleMode sceneScaleMode,
    double sceneScaleDistance,
    CameraParameters &outCameraParameters);

// Two point perspective.
//
// Using two vanishing points, calculate the camera parameters; camera
// translation, camera rotation, and lens angle of view.
//
// Note: The aspect ratio from the film back width and height must be
// consistent and accurate for the given camera.  If the image
// resolution 1920 x 1080, with aspect ratio 16:9, then the film back
// must have the exact same aspect ratio.
//
bool twoVanishingPoints(
    double focalLength_mm,
    double filmBackWidth_mm,
    double filmBackHeight_mm,
    mmdata::Point2D originPoint,
    mmdata::Point2D principalPoint,
    mmdata::Point2D vanishingPointA,
    mmdata::Point2D vanishingPointB,
    SceneScaleMode sceneScaleMode,
    double sceneScaleDistance_cm,
    CameraParameters &outCameraParameters);


} // namespace calibrate

#endif //MAYA_MM_SOLVER_CORE_CALIBRATE_VANISHING_POINT_H
