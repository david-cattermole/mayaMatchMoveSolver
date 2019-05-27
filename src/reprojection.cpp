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


// Internal
#include <Camera.h>  // getProjectionMatrix, computeFrustumCoordinates

// STL
#include <cmath>

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MMatrix.h>


MStatus reprojection(MMatrix tfmMatrix,
                     MMatrix camMatrix,

                     // Camera
                     double focalLength,
                     double horizontalFilmAperture,
                     double verticalFilmAperture,
                     double horizontalFilmOffset,
                     double verticalFilmOffset,
                     short filmFit,
                     double nearClipPlane,
                     double farClipPlane,
                     double cameraScale,

                     // Image
                     double imageWidth,
                     double imageHeight,

                     // Manipulation
                     MMatrix applyMatrix,
                     bool overrideScreenX, bool overrideScreenY, bool overrideScreenZ,
                     double screenX, double screenY, double screenZ,
                     double depthScale,

                     // Outputs
                     double &outCoordX, double &outCoordY,
                     double &outNormCoordX, double &outNormCoordY,
                     double &outMarkerCoordX, double &outMarkerCoordY, double &outMarkerCoordZ,
                     double &outPixelX, double &outPixelY,
                     bool &outInsideFrustum,
                     double &outPointX, double &outPointY, double &outPointZ,
                     double &outWorldPointX, double &outWorldPointY, double &outWorldPointZ,
                     MMatrix &outMatrix,
                     MMatrix &outWorldMatrix,
                     MMatrix &outCameraProjectionMatrix,
                     MMatrix &outInverseCameraProjectionMatrix,
                     MMatrix &outWorldCameraProjectionMatrix,
                     MMatrix &outWorldInverseCameraProjectionMatrix,
                     double &outHorizontalPan,
                     double &outVerticalPan) {
    MStatus status = MStatus::kSuccess;

    // Use frustum coordinates to calculate coordinates values.
    double left = 0.0;
    double right = 0.0;
    double top = 0.0;
    double bottom = 0.0;
    computeFrustumCoordinates(
            focalLength,
            horizontalFilmAperture, verticalFilmAperture,
            horizontalFilmOffset, verticalFilmOffset,
            nearClipPlane, cameraScale,
            left, right, top, bottom);

    // Get Camera Projection Matrix
    MMatrix camProjMatrix;
    status = getProjectionMatrix(
            focalLength,
            horizontalFilmAperture, verticalFilmAperture,
            horizontalFilmOffset, verticalFilmOffset,
            imageWidth, imageHeight,
            filmFit,
            nearClipPlane, farClipPlane,
            cameraScale,
            camProjMatrix);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Camera World Projection Matrix
    MMatrix camWorldProjMatrix = camMatrix.inverse() * camProjMatrix;

    // Convert to screen-space
    tfmMatrix = tfmMatrix * camWorldProjMatrix;

    // Do screen-space overrides
    if (overrideScreenX) {
        tfmMatrix[3][0] = screenX;
    }
    if (overrideScreenY) {
        tfmMatrix[3][1] = screenY;
    }
    if (overrideScreenZ) {
        tfmMatrix[3][2] = screenZ;
    }

    // Apply screen-space matrix
    tfmMatrix = tfmMatrix * applyMatrix;

    // Scale the screen-space depth.
    tfmMatrix *= depthScale;

    // Get (screen-space) point
    MPoint posScreen(tfmMatrix[3][0],
                     tfmMatrix[3][1],
                     tfmMatrix[3][2],
                     tfmMatrix[3][3]);
    posScreen.cartesianize();
    MPoint coord(posScreen.x,
                 posScreen.y,
                 0.0,
                 1.0);

    // Is the point inside the frustum of the camera?
    bool insideFrustum = true;
    if ((coord.x < -1.0)
        || (coord.x > 1.0)
        || (coord.y < -1.0)
        || (coord.y > 1.0)) {
        insideFrustum = false;
    }

    // Convert back to world space
    MMatrix worldTfmMatrix = tfmMatrix * camWorldProjMatrix.inverse();
    MPoint worldPos(worldTfmMatrix[3][0],
                    worldTfmMatrix[3][1],
                    worldTfmMatrix[3][2],
                    1.0);

    // Convert world to camera space
    MMatrix cameraTfmMatrix = worldTfmMatrix * camMatrix.inverse();
    MPoint posCamera(cameraTfmMatrix[3][0],
                     cameraTfmMatrix[3][1],
                     cameraTfmMatrix[3][2],
                     cameraTfmMatrix[3][3]);
    posCamera.cartesianize();

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
    outMatrix = tfmMatrix;

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
