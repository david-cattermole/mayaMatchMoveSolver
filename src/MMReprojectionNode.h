/*
 * Copyright (C) 2018, 2019 David Cattermole.
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
 * Computes reprojection from 3D space into 2D camera-space.
 */

#ifndef MM_REPROJECTION_NODE_H
#define MM_REPROJECTION_NODE_H

#include <maya/MPxNode.h>

#include <maya/MString.h>
#include <maya/MObject.h>
#include <maya/MTime.h>

#include <maya/MFnDependencyNode.h>
#include <maya/MTypeId.h>


class MMReprojectionNode : public MPxNode {
public:
    MMReprojectionNode();

    virtual ~MMReprojectionNode();

    virtual MStatus compute(const MPlug &plug, MDataBlock &data);

    static void *creator();

    static MStatus initialize();

    static MString nodeName();

    static MTypeId m_id;

    // Input Attributes
    // The transform matrix to sample
    static MObject a_transformWorldMatrix;

    // The camera world space matrix
    static MObject a_cameraWorldMatrix;

    // 'Apply matrix'; a matrix we apply when in screen-space.
     static MObject a_applyMatrix;

    // Force a new screen-space position
    static MObject a_overrideScreenX;
    static MObject a_overrideScreenY;
    static MObject a_overrideScreenZ;
    static MObject a_screenX;    // Overrides the screenX to this number.
    static MObject a_screenY;    // Overrides the screenY to this number.
    static MObject a_screenZ;    // Overrides the screenZ to this number.
    static MObject a_depthScale; // Multiply the calculated depth value

    // The camera attributes to calculate camera projection matrix
    static MObject a_focalLength;
    static MObject a_cameraAperture;
    static MObject a_horizontalFilmAperture;
    static MObject a_verticalFilmAperture;
    static MObject a_filmOffset;
    static MObject a_horizontalFilmOffset;
    static MObject a_verticalFilmOffset;
    static MObject a_filmFit;
    static MObject a_nearClipPlane;
    static MObject a_farClipPlane;
    static MObject a_cameraScale;

    // Render Settings
    static MObject a_imageWidth;
    static MObject a_imageHeight;

    // Output Attributes
    // Screen Coordinates (-1.0 to 1.0)
    static MObject a_outCoord;
    static MObject a_outCoordX;
    static MObject a_outCoordY;

    // Screen Coordinates (0.0 to 1.0) (lower-left is 0.0, 0.0)
    static MObject a_outNormCoord;
    static MObject a_outNormCoordX;
    static MObject a_outNormCoordY;
    
    // Output Attributes
    // Marker Coordinates (-0.5 to 0.5)
    static MObject a_outMarkerCoord;
    static MObject a_outMarkerCoordX;
    static MObject a_outMarkerCoordY;
    static MObject a_outMarkerCoordZ;
    
    // Image Coordinates (0.0 to imageWidth or 0.0 to imageHeight)
    // (lower-left is 0.0, 0.0)
    static MObject a_outPixel;
    static MObject a_outPixelX;
    static MObject a_outPixelY;

    // Inside or Outside Frustum
    static MObject a_outInsideFrustum;

    // Camera-space Point
    static MObject a_outPoint;
    static MObject a_outPointX;
    static MObject a_outPointY;
    static MObject a_outPointZ;

    // World-space Point, with modified depth.
    static MObject a_outWorldPoint;
    static MObject a_outWorldPointX;
    static MObject a_outWorldPointY;
    static MObject a_outWorldPointZ;

    // A camera-space matrix that will only differ in depth (if changed via
    // the depth attribute).
    static MObject a_outMatrix;
    static MObject a_outWorldMatrix;

    // Camera Projection Matrix
    static MObject a_outCameraProjectionMatrix;
    static MObject a_outInverseCameraProjectionMatrix;

    // World Camera Projection Matrix
    static MObject a_outWorldCameraProjectionMatrix;
    static MObject a_outWorldInverseCameraProjectionMatrix;

    // Connect to camera.pan attr
    // TODO: Make a another node that allows adding pan compound attrs
    // together, we could then centre on a transform, and allow user
    // given offsets on top.
    static MObject a_outPan;
    static MObject a_outHorizontalPan;
    static MObject a_outVerticalPan;

};


#endif // MM_REPROJECTION_NODE_H
