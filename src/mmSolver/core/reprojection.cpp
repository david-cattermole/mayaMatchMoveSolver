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
 * Functions to compute a 3D transform reprojection onto a 2D camera
 * film back.
 */

#include "reprojection.h"

// STL
#include <cmath>
#include <memory>

// Maya
#include <maya/MMatrix.h>

// MM Solver
#include <mmlens/lens_model.h>

#include "mmSolver/mayahelper/maya_camera.h"  // getProjectionMatrix, computeFrustumCoordinates
#include "mmSolver/utilities/debug_utils.h"

MStatus reprojection(
    const MMatrix tfmMatrix, const MMatrix camMatrix,

    // Camera
    const double focalLength, const double horizontalFilmAperture,
    const double verticalFilmAperture, const double horizontalFilmOffset,
    const double verticalFilmOffset, const short filmFit,
    const double nearClipPlane, const double farClipPlane,
    const double cameraScale,

    // Image
    const double imageWidth, const double imageHeight,

    // Manipulation
    const MMatrix applyMatrix, const bool overrideScreenX,
    const bool overrideScreenY, const bool overrideScreenZ,
    const double screenX, const double screenY, const double screenZ,
    const double depthScale,

    // Outputs
    double &outCoordX, double &outCoordY, double &outNormCoordX,
    double &outNormCoordY, double &outMarkerCoordX, double &outMarkerCoordY,
    double &outMarkerCoordZ, double &outPixelX, double &outPixelY,
    bool &outInsideFrustum, double &outPointX, double &outPointY,
    double &outPointZ, double &outWorldPointX, double &outWorldPointY,
    double &outWorldPointZ, MMatrix &outMatrix, MMatrix &outWorldMatrix,
    MMatrix &outCameraProjectionMatrix,
    MMatrix &outInverseCameraProjectionMatrix,
    MMatrix &outWorldCameraProjectionMatrix,
    MMatrix &outWorldInverseCameraProjectionMatrix, double &outHorizontalPan,
    double &outVerticalPan) {
    std::shared_ptr<mmlens::LensModel> lensModel;
    const auto distortMode = ReprojectionDistortMode::kNone;
    return reprojection(
        tfmMatrix, camMatrix,

        // Camera
        focalLength, horizontalFilmAperture, verticalFilmAperture,
        horizontalFilmOffset, verticalFilmOffset, filmFit, nearClipPlane,
        farClipPlane, cameraScale,

        // Image
        imageWidth, imageHeight,

        // Lens Distortion
        distortMode, lensModel,

        // Manipulation
        applyMatrix, overrideScreenX, overrideScreenY, overrideScreenZ, screenX,
        screenY, screenZ, depthScale,

        // Outputs
        outCoordX, outCoordY, outNormCoordX, outNormCoordY, outMarkerCoordX,
        outMarkerCoordY, outMarkerCoordZ, outPixelX, outPixelY,
        outInsideFrustum, outPointX, outPointY, outPointZ, outWorldPointX,
        outWorldPointY, outWorldPointZ, outMatrix, outWorldMatrix,
        outCameraProjectionMatrix, outInverseCameraProjectionMatrix,
        outWorldCameraProjectionMatrix, outWorldInverseCameraProjectionMatrix,
        outHorizontalPan, outVerticalPan);
}

MStatus reprojection(
    const MMatrix tfmMatrix, const MMatrix camMatrix,

    // Camera
    const double focalLength, const double horizontalFilmAperture,
    const double verticalFilmAperture, const double horizontalFilmOffset,
    const double verticalFilmOffset, const short filmFit,
    const double nearClipPlane, const double farClipPlane,
    const double cameraScale,

    // Image
    const double imageWidth, const double imageHeight,
    // Lens Distortion
    const ReprojectionDistortMode distortMode,
    std::shared_ptr<mmlens::LensModel> lensModel,

    // Manipulation
    const MMatrix applyMatrix, const bool overrideScreenX,
    const bool overrideScreenY, const bool overrideScreenZ,
    const double screenX, const double screenY, const double screenZ,
    const double depthScale,

    // Outputs
    double &outCoordX, double &outCoordY, double &outNormCoordX,
    double &outNormCoordY, double &outMarkerCoordX, double &outMarkerCoordY,
    double &outMarkerCoordZ, double &outPixelX, double &outPixelY,
    bool &outInsideFrustum, double &outPointX, double &outPointY,
    double &outPointZ, double &outWorldPointX, double &outWorldPointY,
    double &outWorldPointZ, MMatrix &outMatrix, MMatrix &outWorldMatrix,
    MMatrix &outCameraProjectionMatrix,
    MMatrix &outInverseCameraProjectionMatrix,
    MMatrix &outWorldCameraProjectionMatrix,
    MMatrix &outWorldInverseCameraProjectionMatrix, double &outHorizontalPan,
    double &outVerticalPan) {
    // Get Camera Projection Matrix
    MMatrix camProjMatrix;
    MStatus status = getProjectionMatrix(
        focalLength, horizontalFilmAperture, verticalFilmAperture,
        horizontalFilmOffset, verticalFilmOffset, imageWidth, imageHeight,
        filmFit, nearClipPlane, farClipPlane, cameraScale, camProjMatrix);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Camera World Projection Matrix
    MMatrix camWorldProjMatrix = camMatrix.inverse() * camProjMatrix;

    // Convert to screen-space
    MMatrix matrix = tfmMatrix * camWorldProjMatrix;

    // Do screen-space overrides
    if (overrideScreenX) {
        matrix[3][0] = screenX;
    }
    if (overrideScreenY) {
        matrix[3][1] = screenY;
    }
    if (overrideScreenZ) {
        matrix[3][2] = screenZ;
    }

    // Apply screen-space matrix
    matrix = matrix * applyMatrix;

    // Scale the screen-space depth.
    matrix *= depthScale;

    // Get (screen-space) point. Screen-space is also called NDC
    // (normalised device coordinates) space.
    MPoint posScreen(matrix[3][0], matrix[3][1], matrix[3][2], matrix[3][3]);

    // Correct the screen position to remove the embedded scaling that
    // comes from the 'getProjectionMatrix' function.
    const double filmBackAspect = horizontalFilmAperture / verticalFilmAperture;
    const double imageAspect =
        static_cast<double>(imageWidth) / static_cast<double>(imageHeight);
    applyFilmFitCorrectionScaleForward(filmFit, filmBackAspect, imageAspect,
                                       posScreen.x, posScreen.y);

    // Distort the input transform's screen-space position.
    MPoint coord(0.0, 0.0, 0.0, 1.0);
    if (!lensModel || distortMode == ReprojectionDistortMode::kNone) {
        // Convert from 'P(W*x, W*y, W*z, W)' to 'P(x, y, z, 1)'.
        posScreen.cartesianize();
        coord.x = posScreen.x;
        coord.y = posScreen.y;
    } else {
        // Convert from 'P(W*x, W*y, W*z, W)' to 'P(x, y, z, W)'.
        posScreen.rationalize();

        double input_x = posScreen.x * 0.5;
        double input_y = posScreen.y * 0.5;

        double output_x = input_x;
        double output_y = input_y;
        // Applying Lens distortion can result in NaN or infinite
        // values, so we avoid applying such values if they are
        // computed.
        if (distortMode == ReprojectionDistortMode::kUndistort) {
            double temp_x = input_x;
            double temp_y = input_y;
            lensModel->applyModelUndistort(input_x, input_y, temp_x, temp_y);
            if (std::isfinite(temp_x)) {
                output_x = temp_x;
            }
            if (std::isfinite(temp_y)) {
                output_y = temp_y;
            }
        } else if (distortMode == ReprojectionDistortMode::kRedistort) {
            double temp_x = input_x;
            double temp_y = input_y;
            lensModel->applyModelDistort(input_x, input_y, temp_x, temp_y);
            if (std::isfinite(temp_x)) {
                output_x = temp_x;
            }
            if (std::isfinite(temp_y)) {
                output_y = temp_y;
            }
        }

        output_x *= 2.0;
        output_y *= 2.0;

        coord.x = output_x;
        coord.y = output_y;
        posScreen.x = output_x;
        posScreen.y = output_y;

        // Reverse the screen position to add the scaling that comes
        // from the 'getProjectionMatrix' function, to put these back
        // to how they were.
        applyFilmFitCorrectionScaleBackward(
            filmFit, filmBackAspect, imageAspect, posScreen.x, posScreen.y);

        // Reverses the '.rationalize()', so we can maintain the same
        // space for 'matrix' as it was.
        //
        // Convert from 'P(x, y, z, W)' to 'P(W*x, W*y, W*z, W)'.
        posScreen.homogenize();

        matrix[3][0] = posScreen.x;
        matrix[3][1] = posScreen.y;
        matrix[3][2] = posScreen.z;
        matrix[3][3] = posScreen.w;

        // Convert from 'P(W*x, W*y, W*z, W)' to 'P(x, y, z, 1)'.
        posScreen.cartesianize();
    }

    // Is the point inside the frustum of the camera?
    bool insideFrustum = true;
    if ((coord.x < -1.0) || (coord.x > 1.0) || (coord.y < -1.0) ||
        (coord.y > 1.0)) {
        insideFrustum = false;
    }

    // Convert back to world space
    MMatrix worldTfmMatrix = matrix * camWorldProjMatrix.inverse();
    MPoint worldPos(worldTfmMatrix[3][0], worldTfmMatrix[3][1],
                    worldTfmMatrix[3][2], 1.0);

    // Convert world to camera space
    MMatrix cameraTfmMatrix = worldTfmMatrix * camMatrix.inverse();
    MPoint posCamera(cameraTfmMatrix[3][0], cameraTfmMatrix[3][1],
                     cameraTfmMatrix[3][2], cameraTfmMatrix[3][3]);
    posCamera.rationalize();

    // Output Coordinates (-1.0 to 1.0; lower-left corner is -1.0, -1.0)
    outCoordX = coord.x;
    outCoordY = coord.y;

    // Output Normalised Coordinates (0.0 to 1.0; lower-left
    // corner is 0.0, 0.0)
    outNormCoordX = (coord.x + 1.0) * 0.5;
    outNormCoordY = (coord.y + 1.0) * 0.5;

    // Output Coordinates (-0.5 to 0.5; lower-left corner is -0.5, -0.5)
    outMarkerCoordX = coord.x * 0.5;
    outMarkerCoordY = coord.y * 0.5;
    outMarkerCoordZ = posCamera.z * -1.0;

    // Output Pixel Coordinates (0.0 to width; 0.0 to height;
    // lower-left corner is 0.0, 0.0)
    outPixelX = (coord.x + 1.0) * 0.5 * imageWidth;
    outPixelY = (coord.y + 1.0) * 0.5 * imageHeight;

    // Output 'Inside Frustum'; is the input matrix inside the
    // camera frustrum or not?
    outInsideFrustum = insideFrustum;

    // Output Point (camera-space)
    outPointX = posCamera.x;
    outPointY = posCamera.y;
    outPointZ = posCamera.z;

    // Output Point (world-space)
    outWorldPointX = worldPos.x;
    outWorldPointY = worldPos.y;
    outWorldPointZ = worldPos.z;

    // Output Matrix (camera-space)
    outMatrix = matrix;

    // Output Matrix (world-space)
    outWorldMatrix = worldTfmMatrix;

    // Output Camera Projection Matrix
    outCameraProjectionMatrix = camProjMatrix;

    // Output Inverse Camera Projection Matrix
    outInverseCameraProjectionMatrix = camProjMatrix.inverse();

    // Output World Camera Projection Matrix
    outWorldCameraProjectionMatrix = camWorldProjMatrix;

    // Output World Inverse Camera Projection Matrix
    outWorldInverseCameraProjectionMatrix = camWorldProjMatrix.inverse();

    // Output Pan
    outHorizontalPan = coord.x * 0.5 * horizontalFilmAperture;
    outVerticalPan = coord.y * 0.5 * verticalFilmAperture;

    return status;
}

MStatus calculateCameraFacingRatio(MMatrix tfmMatrix, MMatrix camMatrix,
                                   double &outCameraDirRatio) {
    MStatus status = MStatus::kSuccess;

    MPoint tfmPos;
    tfmPos.x = tfmMatrix[3][0];
    tfmPos.y = tfmMatrix[3][1];
    tfmPos.z = tfmMatrix[3][2];

    MPoint camPos;
    camPos.x = camMatrix[3][0];
    camPos.y = camMatrix[3][1];
    camPos.z = camMatrix[3][2];

    MVector tfmDir;
    tfmDir = tfmPos - camPos;
    tfmDir.normalize();

    MVector camDir;
    MVector cameraForwardVector(0.0, 0.0, -1.0);
    camDir = cameraForwardVector * camMatrix;
    camDir.normalize();

    outCameraDirRatio = camDir * tfmDir;
    return status;
}
