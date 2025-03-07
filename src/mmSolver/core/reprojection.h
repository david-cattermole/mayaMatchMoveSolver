/*
 * Copyright (C) 2019 David Cattermole.
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
 * Define the reprojection functions.
 */

#ifndef MM_SOLVER_CORE_REPROJECTION_H
#define MM_SOLVER_CORE_REPROJECTION_H

// STL
#include <memory>

// Maya
#include <maya/MMatrix.h>
#include <maya/MStatus.h>

// MM Solver Libs
#include <mmlens/lens_model.h>

enum class ReprojectionDistortMode : short {
    // No change at all.
    kNone = 0,

    // Assumes the point is distorted and will undistort the point.
    kUndistort = 1,

    // Assumes the point is undistorted, and will recover the
    // distorted point.
    kRedistort = 2,
};

// Standard reprojection - no special handling of lens distortion in
// this function.
MStatus reprojection(
    const MMatrix tfmMatrix, const MMatrix camMatrix,

    // Camera
    const double focalLength, const double horizontalFilmAperture,
    const double verticalFilmAperture, const double horizontalFilmOffset,
    const double verticalFilmOffset, const short filmFit,
    const double nearClipPlane, const double farClipPlane,
    const double cameraScale,

    // Image Resolution - so we can give values as pixels
    const double imageWidth, const double imageHeight,

    // Manipulation
    const MMatrix applyMatrix, const bool overrideScreenX,
    const bool overrideScreenY, const bool overrideScreenZ,
    const double screenX, const double screenY, const double screenZ,
    const double depthScale,

    // Outputs
    double &outCoordX, double &outCoordY, double &outNormCoordX,
    double &outNormCoordY, double &outMarkerCoordX, double &outMarkerCoordY,
    double &outMarkerCoord, double &outPixelX, double &outPixelY,
    bool &outInsideFrustum, double &outPointX, double &outPointY,
    double &outPointZ, double &outWorldPointX, double &outWorldPointY,
    double &outWorldPointZ, MMatrix &outMatrix, MMatrix &outWorldMatrix,
    MMatrix &outCameraProjectionMatrix,
    MMatrix &outInverseCameraProjectionMatrix,
    MMatrix &outWorldCameraProjectionMatrix,
    MMatrix &outWorldInverseCameraProjectionMatrix, double &outHorizontalPan,
    double &outVerticalPan);

// Reprojection with extra lens distortion parameters, so that the
// reprojection can undistort/redistort the reprojected point.
MStatus reprojection(
    const MMatrix tfmMatrix, const MMatrix camMatrix,

    // Camera
    const double focalLength, const double horizontalFilmAperture,
    const double verticalFilmAperture, const double horizontalFilmOffset,
    const double verticalFilmOffset, const short filmFit,
    const double nearClipPlane, const double farClipPlane,
    const double cameraScale,

    // Image Resolution - so we can give values as pixels
    const double imageWidth, const double imageHeight,

    // Lens Distortion
    const ReprojectionDistortMode distortMode,
    std::shared_ptr<mmlens::LensModel> lensModel,

    // Manipulation
    //
    // These are applied *before* the point is adjusted by the lens
    // distortion.
    const MMatrix applyMatrix, const bool overrideScreenX,
    const bool overrideScreenY, const bool overrideScreenZ,
    const double screenX, const double screenY, const double screenZ,
    const double depthScale,

    // Outputs
    double &outCoordX, double &outCoordY, double &outNormCoordX,
    double &outNormCoordY, double &outMarkerCoordX, double &outMarkerCoordY,
    double &outMarkerCoord, double &outPixelX, double &outPixelY,
    bool &outInsideFrustum, double &outPointX, double &outPointY,
    double &outPointZ, double &outWorldPointX, double &outWorldPointY,
    double &outWorldPointZ, MMatrix &outMatrix, MMatrix &outWorldMatrix,
    MMatrix &outCameraProjectionMatrix,
    MMatrix &outInverseCameraProjectionMatrix,
    MMatrix &outWorldCameraProjectionMatrix,
    MMatrix &outWorldInverseCameraProjectionMatrix, double &outHorizontalPan,
    double &outVerticalPan);

MStatus calculateCameraFacingRatio(MMatrix tfmMatrix, MMatrix camMatrix,
                                   double &outCameraDirRatio);

#endif  // MM_SOLVER_CORE_REPROJECTION_H
