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

#ifndef MAYA_MM_SOLVER_REPROJECTION_H
#define MAYA_MM_SOLVER_REPROJECTION_H


// Maya
#include <maya/MMatrix.h>
#include <maya/MStatus.h>


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
                     double &outMarkerCoordX, double &outMarkerCoordY, double &outMarkerCoord,
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
                     double &outVerticalPan);


#endif // MAYA_MM_SOLVER_REPROJECTION_H
