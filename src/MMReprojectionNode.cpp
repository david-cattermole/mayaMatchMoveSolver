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

#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnMatrixData.h>

#include <utilities/debugUtils.h>
#include <utilities/numberUtils.h>

#include <cstring>
#include <cmath>

#include <nodeTypeIds.h>

#include <MMReprojectionNode.h>
#include <Camera.h>  // getProjectionMatrix, computeFrustumCoordinates
#include <reprojection.h>


MTypeId MMReprojectionNode::m_id(MM_REPROJECTION_TYPE_ID);

// Input Attributes
MObject MMReprojectionNode::a_transformWorldMatrix;
MObject MMReprojectionNode::a_cameraWorldMatrix;
MObject MMReprojectionNode::a_applyMatrix;
MObject MMReprojectionNode::a_overrideScreenX;
MObject MMReprojectionNode::a_overrideScreenY;
MObject MMReprojectionNode::a_overrideScreenZ;
MObject MMReprojectionNode::a_screenX;
MObject MMReprojectionNode::a_screenY;
MObject MMReprojectionNode::a_screenZ;
MObject MMReprojectionNode::a_depthScale;
MObject MMReprojectionNode::a_focalLength;
MObject MMReprojectionNode::a_cameraAperture;
MObject MMReprojectionNode::a_horizontalFilmAperture;
MObject MMReprojectionNode::a_verticalFilmAperture;
MObject MMReprojectionNode::a_filmOffset;
MObject MMReprojectionNode::a_horizontalFilmOffset;
MObject MMReprojectionNode::a_verticalFilmOffset;
MObject MMReprojectionNode::a_filmFit;
MObject MMReprojectionNode::a_nearClipPlane;
MObject MMReprojectionNode::a_farClipPlane;
MObject MMReprojectionNode::a_cameraScale;
MObject MMReprojectionNode::a_imageWidth;
MObject MMReprojectionNode::a_imageHeight;

// Output Attributes
MObject MMReprojectionNode::a_outCoord;
MObject MMReprojectionNode::a_outCoordX;
MObject MMReprojectionNode::a_outCoordY;
MObject MMReprojectionNode::a_outNormCoord;
MObject MMReprojectionNode::a_outNormCoordX;
MObject MMReprojectionNode::a_outNormCoordY;
MObject MMReprojectionNode::a_outMarkerCoord;
MObject MMReprojectionNode::a_outMarkerCoordX;
MObject MMReprojectionNode::a_outMarkerCoordY;
MObject MMReprojectionNode::a_outMarkerCoordZ;
MObject MMReprojectionNode::a_outPixel;
MObject MMReprojectionNode::a_outPixelX;
MObject MMReprojectionNode::a_outPixelY;
MObject MMReprojectionNode::a_outInsideFrustum;
MObject MMReprojectionNode::a_outPoint;
MObject MMReprojectionNode::a_outPointX;
MObject MMReprojectionNode::a_outPointY;
MObject MMReprojectionNode::a_outPointZ;
MObject MMReprojectionNode::a_outWorldPoint;
MObject MMReprojectionNode::a_outWorldPointX;
MObject MMReprojectionNode::a_outWorldPointY;
MObject MMReprojectionNode::a_outWorldPointZ;
MObject MMReprojectionNode::a_outMatrix;
MObject MMReprojectionNode::a_outWorldMatrix;
MObject MMReprojectionNode::a_outCameraProjectionMatrix;
MObject MMReprojectionNode::a_outInverseCameraProjectionMatrix;
MObject MMReprojectionNode::a_outWorldCameraProjectionMatrix;
MObject MMReprojectionNode::a_outWorldInverseCameraProjectionMatrix;
MObject MMReprojectionNode::a_outPan;
MObject MMReprojectionNode::a_outHorizontalPan;
MObject MMReprojectionNode::a_outVerticalPan;


MMReprojectionNode::MMReprojectionNode() {}

MMReprojectionNode::~MMReprojectionNode() {}

MString MMReprojectionNode::nodeName() {
    return MString("mmReprojection");
}

MStatus MMReprojectionNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if ((plug == a_outCoord)
        || (plug == a_outCoordX)
        || (plug == a_outCoordY)
        || (plug == a_outNormCoord)
        || (plug == a_outNormCoordX)
        || (plug == a_outNormCoordY)
        || (plug == a_outMarkerCoord)
        || (plug == a_outMarkerCoordX)
        || (plug == a_outMarkerCoordY)
        || (plug == a_outMarkerCoordZ)
        || (plug == a_outPixel)
        || (plug == a_outPixelX)
        || (plug == a_outPixelY)
        || (plug == a_outInsideFrustum)
        || (plug == a_outPoint)
        || (plug == a_outPointX)
        || (plug == a_outPointY)
        || (plug == a_outPointZ)
        || (plug == a_outWorldPoint)
        || (plug == a_outWorldPointX)
        || (plug == a_outWorldPointY)
        || (plug == a_outWorldPointZ)
        || (plug == a_outMatrix)
        || (plug == a_outWorldMatrix)
        || (plug == a_outCameraProjectionMatrix)
        || (plug == a_outInverseCameraProjectionMatrix)
        || (plug == a_outWorldCameraProjectionMatrix)
        || (plug == a_outWorldInverseCameraProjectionMatrix)
        || (plug == a_outPan)
        || (plug == a_outHorizontalPan)
        || (plug == a_outVerticalPan)) {
        // Get Data Handles
        MDataHandle tfmMatrixHandle = data.inputValue(a_transformWorldMatrix,
                                                      &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix tfmMatrix = tfmMatrixHandle.asMatrix();

        MDataHandle camMatrixHandle = data.inputValue(a_cameraWorldMatrix,
                                                      &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix camMatrix = camMatrixHandle.asMatrix();

        MDataHandle applyMatrixHandle = data.inputValue(a_applyMatrix, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix applyMatrix = applyMatrixHandle.asMatrix();

        MDataHandle focalLengthHandle = data.inputValue(a_focalLength, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double focalLength = focalLengthHandle.asDouble();

        MDataHandle horizontalFilmApertureHandle = data.inputValue(a_horizontalFilmAperture,
                                                                   &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double horizontalFilmAperture = horizontalFilmApertureHandle.asDouble();

        MDataHandle verticalFilmApertureHandle = data.inputValue(a_verticalFilmAperture,
                                                                 &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double verticalFilmAperture = verticalFilmApertureHandle.asDouble();

        MDataHandle horizontalFilmOffsetHandle = data.inputValue(a_horizontalFilmOffset,
                                                                 &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double horizontalFilmOffset = horizontalFilmOffsetHandle.asDouble();

        MDataHandle verticalFilmOffsetHandle = data.inputValue(a_verticalFilmOffset,
                                                               &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double verticalFilmOffset = verticalFilmOffsetHandle.asDouble();

        MDataHandle filmFitHandle = data.inputValue(a_filmFit, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        short filmFit = filmFitHandle.asShort();

        // MDataHandle nearClipPlaneHandle = data.inputValue(a_nearClipPlane,
        //                                                   &status);
        // CHECK_MSTATUS_AND_RETURN_IT(status);
        // double nearClipPlane = nearClipPlaneHandle.asDouble();

        // TODO: near clip plane forced to 0.1, otherwise reprojection
        // does't work. Why? No idea.
        double nearClipPlane = 0.1;

        MDataHandle farClipPlaneHandle = data.inputValue(a_farClipPlane,
                                                         &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double farClipPlane = farClipPlaneHandle.asDouble();

        MDataHandle cameraScaleHandle = data.inputValue(a_cameraScale, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double cameraScale = cameraScaleHandle.asDouble();

        MDataHandle imageWidthHandle = data.inputValue(a_imageWidth, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double imageWidth = imageWidthHandle.asDouble();

        MDataHandle imageHeightHandle = data.inputValue(a_imageHeight, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double imageHeight = imageHeightHandle.asDouble();

        MDataHandle overrideScreenXHandle = data.inputValue(a_overrideScreenX,
                                                            &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        bool overrideScreenX = overrideScreenXHandle.asDouble();

        MDataHandle overrideScreenYHandle = data.inputValue(a_overrideScreenY,
                                                            &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        bool overrideScreenY = overrideScreenYHandle.asDouble();

        MDataHandle overrideScreenZHandle = data.inputValue(a_overrideScreenZ,
                                                            &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        bool overrideScreenZ = overrideScreenZHandle.asDouble();

        MDataHandle screenXHandle = data.inputValue(a_screenX, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double screenX = screenXHandle.asDouble();

        MDataHandle screenYHandle = data.inputValue(a_screenY, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double screenY = screenYHandle.asDouble();

        MDataHandle screenZHandle = data.inputValue(a_screenZ, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double screenZ = screenZHandle.asDouble();

        MDataHandle depthScaleHandle = data.inputValue(a_depthScale, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double depthScale = depthScaleHandle.asDouble();

        // Reprojection Outputs
        double outCoordX;
        double outCoordY;
        double outNormCoordX;
        double outNormCoordY;
        double outMarkerCoordX;
        double outMarkerCoordY;
        double outMarkerCoordZ;
        double outPixelX;
        double outPixelY;
        bool outInsideFrustum;
        double outPointX;
        double outPointY;
        double outPointZ;
        double outWorldPointX;
        double outWorldPointY;
        double outWorldPointZ;
        MMatrix outMatrix;
        MMatrix outWorldMatrix;
        MMatrix outCameraProjectionMatrix;
        MMatrix outInverseCameraProjectionMatrix;
        MMatrix outWorldCameraProjectionMatrix;
        MMatrix outWorldInverseCameraProjectionMatrix;
        double outHorizontalPan;
        double outVerticalPan;

        // Query the reprojection.
        status = reprojection(
                tfmMatrix,
                camMatrix,

                // Camera
                focalLength,
                horizontalFilmAperture,
                verticalFilmAperture,
                horizontalFilmOffset,
                verticalFilmOffset,
                filmFit,
                nearClipPlane,
                farClipPlane,
                cameraScale,

                // Image
                imageWidth,
                imageHeight,

                // Manipulation
                applyMatrix,
                overrideScreenX,
                overrideScreenY,
                overrideScreenZ,
                screenX,
                screenY,
                screenZ,
                depthScale,

                // Outputs
                outCoordX, outCoordY,
                outNormCoordX, outNormCoordY,
                outMarkerCoordX, outMarkerCoordY, outMarkerCoordZ,
                outPixelX, outPixelY,
                outInsideFrustum,
                outPointX, outPointY, outPointZ,
                outWorldPointX, outWorldPointY, outWorldPointZ,
                outMatrix,
                outWorldMatrix,
                outCameraProjectionMatrix,
                outInverseCameraProjectionMatrix,
                outWorldCameraProjectionMatrix,
                outWorldInverseCameraProjectionMatrix,
                outHorizontalPan,
                outVerticalPan);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Output Coordinates (-1.0 to 1.0; lower-left corner is -1.0, -1.0)
        MDataHandle outCoordXHandle = data.outputValue(a_outCoordX);
        MDataHandle outCoordYHandle = data.outputValue(a_outCoordY);
        outCoordXHandle.setDouble(outCoordX);
        outCoordYHandle.setDouble(outCoordY);
        outCoordXHandle.setClean();
        outCoordYHandle.setClean();

        // Output Normalised Coordinates (0.0 to 1.0; lower-left
        // corner is 0.0, 0.0)
        MDataHandle outNormCoordXHandle = data.outputValue(a_outNormCoordX);
        MDataHandle outNormCoordYHandle = data.outputValue(a_outNormCoordY);
        outNormCoordXHandle.setDouble(outNormCoordX);
        outNormCoordYHandle.setDouble(outNormCoordY);
        outNormCoordXHandle.setClean();
        outNormCoordYHandle.setClean();

        // Output Coordinates (-0.5 to 0.5; lower-left corner is -0.5, -0.5)
        MDataHandle outMarkerCoordXHandle = data.outputValue(a_outMarkerCoordX);
        MDataHandle outMarkerCoordYHandle = data.outputValue(a_outMarkerCoordY);
        MDataHandle outMarkerCoordZHandle = data.outputValue(a_outMarkerCoordZ);
        outMarkerCoordXHandle.setDouble(outMarkerCoordX);
        outMarkerCoordYHandle.setDouble(outMarkerCoordY);
        outMarkerCoordZHandle.setDouble(outMarkerCoordZ);
        outMarkerCoordXHandle.setClean();
        outMarkerCoordYHandle.setClean();
        outMarkerCoordZHandle.setClean();
        
        // Output Pixel Coordinates (0.0 to width; 0.0 to height;
        // lower-left corner is 0.0, 0.0)
        MDataHandle outPixelXHandle = data.outputValue(a_outPixelX);
        MDataHandle outPixelYHandle = data.outputValue(a_outPixelY);
        outPixelXHandle.setDouble(outPixelX);
        outPixelYHandle.setDouble(outPixelY);
        outPixelXHandle.setClean();
        outPixelYHandle.setClean();

        // Output 'Inside Frustum'; is the input matrix inside the
        // camera frustrum or not?
        MDataHandle outInsideFrustumHandle = data.outputValue(a_outInsideFrustum);
        outInsideFrustumHandle.setBool(outInsideFrustum);
        outInsideFrustumHandle.setClean();

        // Output Point (camera-space)
        MDataHandle outPointXHandle = data.outputValue(a_outPointX);
        MDataHandle outPointYHandle = data.outputValue(a_outPointY);
        MDataHandle outPointZHandle = data.outputValue(a_outPointZ);
        outPointXHandle.setDouble(outPointX);
        outPointYHandle.setDouble(outPointY);
        outPointZHandle.setDouble(outPointZ);
        outPointXHandle.setClean();
        outPointYHandle.setClean();
        outPointZHandle.setClean();

        // Output Point (world-space)
        MDataHandle outWorldPointXHandle = data.outputValue(a_outWorldPointX);
        MDataHandle outWorldPointYHandle = data.outputValue(a_outWorldPointY);
        MDataHandle outWorldPointZHandle = data.outputValue(a_outWorldPointZ);
        outWorldPointXHandle.setDouble(outWorldPointX);
        outWorldPointYHandle.setDouble(outWorldPointY);
        outWorldPointZHandle.setDouble(outWorldPointZ);
        outWorldPointXHandle.setClean();
        outWorldPointYHandle.setClean();
        outWorldPointZHandle.setClean();

        // Output Matrix (camera-space)
        MDataHandle outMatrixHandle = data.outputValue(a_outMatrix);
        outMatrixHandle.setMMatrix(outMatrix);
        outMatrixHandle.setClean();

        // Output Matrix (world-space)
        MDataHandle outWorldMatrixHandle = data.outputValue(a_outWorldMatrix);
        outWorldMatrixHandle.setMMatrix(outWorldMatrix);
        outWorldMatrixHandle.setClean();

        // Output Camera Projection Matrix
        MDataHandle outCameraProjectionMatrixHandle = data.outputValue(a_outCameraProjectionMatrix);
        outCameraProjectionMatrixHandle.setMMatrix(outCameraProjectionMatrix);
        outCameraProjectionMatrixHandle.setClean();

        // Output Inverse Camera Projection Matrix
        MDataHandle outInverseCameraProjectionMatrixHandle = data.outputValue(a_outInverseCameraProjectionMatrix);
        outInverseCameraProjectionMatrixHandle.setMMatrix(outInverseCameraProjectionMatrix);
        outInverseCameraProjectionMatrixHandle.setClean();

        // Output World Camera Projection Matrix
        MDataHandle outWorldCameraProjectionMatrixHandle = data.outputValue(a_outWorldCameraProjectionMatrix);
        outWorldCameraProjectionMatrixHandle.setMMatrix(outWorldCameraProjectionMatrix);
        outWorldCameraProjectionMatrixHandle.setClean();

        // Output World Inverse Camera Projection Matrix
        MDataHandle outWorldInverseCameraProjectionMatrixHandle = data.outputValue(
                a_outWorldInverseCameraProjectionMatrix);
        outWorldInverseCameraProjectionMatrixHandle.setMMatrix(outWorldInverseCameraProjectionMatrix);
        outWorldInverseCameraProjectionMatrixHandle.setClean();

        // Output Pan
        MDataHandle outHorizontalPanHandle = data.outputValue(a_outHorizontalPan);
        MDataHandle outVerticalPanHandle = data.outputValue(a_outVerticalPan);
        outHorizontalPanHandle.setDouble(outHorizontalPan);
        outVerticalPanHandle.setDouble(outVerticalPan);
        outHorizontalPanHandle.setClean();
        outVerticalPanHandle.setClean();

        status = MS::kSuccess;
    }

    return status;
}

void *MMReprojectionNode::creator() {
    return (new MMReprojectionNode());
}

MStatus MMReprojectionNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnEnumAttribute enumAttr;
    MFnMatrixAttribute matrixAttr;
    MFnCompoundAttribute compoundAttr;

    {
        // Transform World Matrix
        a_transformWorldMatrix = matrixAttr.create(
                "transformWorldMatrix", "twm",
                MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(true));
        CHECK_MSTATUS(matrixAttr.setConnectable(true));
        CHECK_MSTATUS(addAttribute(a_transformWorldMatrix));

        // Camera World Matrix
        a_cameraWorldMatrix = matrixAttr.create(
                "cameraWorldMatrix", "cwm",
                MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(true));
        CHECK_MSTATUS(matrixAttr.setConnectable(true));
        CHECK_MSTATUS(addAttribute(a_cameraWorldMatrix));

        // Apply Matrix
        a_applyMatrix = matrixAttr.create(
                "applyMatrix", "aplym",
                MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(true));
        CHECK_MSTATUS(matrixAttr.setConnectable(true));
        CHECK_MSTATUS(addAttribute(a_applyMatrix));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Override Screen X
        a_overrideScreenX = numericAttr.create(
                "overrideScreenX", "ovrdscx",
                MFnNumericData::kBoolean, false);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_overrideScreenX));

        // Override Screen Y
        a_overrideScreenY = numericAttr.create(
                "overrideScreenY", "ovrdscy",
                MFnNumericData::kBoolean, false);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_overrideScreenY));

        // Override Screen Z
        a_overrideScreenZ = numericAttr.create(
                "overrideScreenZ", "ovrdscz",
                MFnNumericData::kBoolean, false);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_overrideScreenZ));

        // ScreenX (Left-Right)
        a_screenX = numericAttr.create(
                "screenX", "scx",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_screenX));

        // ScreenY (Up-Down)
        a_screenY = numericAttr.create(
                "screenY", "scy",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_screenY));

        // ScreenZ (Depth)
        a_screenZ = numericAttr.create(
                "screenZ", "scz",
                MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_screenZ));

        // Depth Scale
        a_depthScale = numericAttr.create(
                "depthScale", "dptscl",
                MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_depthScale));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Focal Length (millimetres)
        a_focalLength = numericAttr.create(
                "focalLength", "fl",
                MFnNumericData::kDouble, 35.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_focalLength));

        // Horizontal Film Aperture (inches)
        a_horizontalFilmAperture = numericAttr.create(
                "horizontalFilmAperture", "hfa",
                MFnNumericData::kDouble, 1.41732);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Vertical Film Aperture (inches)
        a_verticalFilmAperture = numericAttr.create(
                "verticalFilmAperture", "vfa",
                MFnNumericData::kDouble, 0.94488);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Film Offset (parent of filmOffset* attributes)
        a_cameraAperture = compoundAttr.create(
                "cameraAperture", "cap",
                &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_horizontalFilmAperture);
        compoundAttr.addChild(a_verticalFilmAperture);
        CHECK_MSTATUS(addAttribute(a_cameraAperture));

        // Horizontal Film Offset (inches)
        a_horizontalFilmOffset = numericAttr.create(
                "horizontalFilmOffset", "hfo",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Vertical Film Offset (inches)
        a_verticalFilmOffset = numericAttr.create(
                "verticalFilmOffset", "vfo",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Film Offset (parent of filmOffset* attributes)
        a_filmOffset = compoundAttr.create(
                "filmOffset", "fio",
                &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_horizontalFilmOffset);
        compoundAttr.addChild(a_verticalFilmOffset);
        CHECK_MSTATUS(addAttribute(a_filmOffset));

        // Film Fit; 0=fill, 1=horizontal, 2=vertical, 3=overscan
        a_filmFit = enumAttr.create(
                "filmFit", "ff", 0, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(enumAttr.addField("Fit", 0));
        CHECK_MSTATUS(enumAttr.addField("Horizontal", 1));
        CHECK_MSTATUS(enumAttr.addField("Vertical", 2));
        CHECK_MSTATUS(enumAttr.addField("Overscan", 3));
        CHECK_MSTATUS(enumAttr.setStorable(true));
        CHECK_MSTATUS(enumAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_filmFit));

        // Near Clip Plane
        a_nearClipPlane = numericAttr.create(
                "nearClipPlane", "ncp",
                MFnNumericData::kDouble, 0.1);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_nearClipPlane));

        // Far Clip Plane
        a_farClipPlane = numericAttr.create(
                "farClipPlane", "fcp",
                MFnNumericData::kDouble, 10000.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_farClipPlane));

        // Camera Scale
        a_cameraScale = numericAttr.create(
                "cameraScale", "cs",
                MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_cameraScale));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Image Width
        a_imageWidth = numericAttr.create(
                "imageWidth", "iw",
                MFnNumericData::kDouble, 1920.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_imageWidth));

        // Image Height
        a_imageHeight = numericAttr.create(
                "imageHeight", "ih",
                MFnNumericData::kDouble, 1080.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_imageHeight));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Coord X
        a_outCoordX = numericAttr.create(
                "outCoordX", "ocdx",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Coord Y
        a_outCoordY = numericAttr.create(
                "outCoordY", "ocdy",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Coord (parent of outCoord* attributes)
        a_outCoord = compoundAttr.create("outCoord", "ocd", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outCoordX);
        compoundAttr.addChild(a_outCoordY);
        CHECK_MSTATUS(addAttribute(a_outCoord));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Normalised Coord X
        a_outNormCoordX = numericAttr.create(
                "outNormCoordX", "oncdx",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Normalised Coord Y
        a_outNormCoordY = numericAttr.create(
                "outNormCoordY", "oncdy",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Normalised Coord (parent of outNormCoord* attributes)
        a_outNormCoord = compoundAttr.create("outNormCoord", "oncd", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outNormCoordX);
        compoundAttr.addChild(a_outNormCoordY);
        CHECK_MSTATUS(addAttribute(a_outNormCoord));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Marker Coord X
        a_outMarkerCoordX = numericAttr.create(
                "outMarkerCoordX", "omcdx",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Marker Coord Y
        a_outMarkerCoordY = numericAttr.create(
                "outMarkerCoordY", "omcdy",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Marker Coord Z
        a_outMarkerCoordZ = numericAttr.create(
                "outMarkerCoordZ", "omcdz",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Marker Coord (parent of outMarkerCoord* attributes)
        a_outMarkerCoord = compoundAttr.create("outMarkerCoord", "omcd", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outMarkerCoordX);
        compoundAttr.addChild(a_outMarkerCoordY);
        compoundAttr.addChild(a_outMarkerCoordZ);
        CHECK_MSTATUS(addAttribute(a_outMarkerCoord));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Pixel Coord X
        a_outPixelX = numericAttr.create(
                "outPixelX", "opixx",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Pixel Coord Y
        a_outPixelY = numericAttr.create(
                "outPixelY", "opixy",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Pixel Coord (parent of outPixel* attributes)
        a_outPixel = compoundAttr.create("outPixel", "opix", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outPixelX);
        compoundAttr.addChild(a_outPixelY);
        CHECK_MSTATUS(addAttribute(a_outPixel));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Inside Frustum
        a_outInsideFrustum = numericAttr.create(
                "outInsideFrustum", "oinftm",
                MFnNumericData::kBoolean, false);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));
        CHECK_MSTATUS(addAttribute(a_outInsideFrustum));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Point X
        a_outPointX = numericAttr.create(
                "outPointX", "opx",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Y
        a_outPointY = numericAttr.create(
                "outPointY", "opy",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Z
        a_outPointZ = numericAttr.create(
                "outPointZ", "opz",
                MFnNumericData::kDouble, 0.0, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point (parent of outPoint* attributes)
        a_outPoint = compoundAttr.create("outPoint", "op", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outPointX);
        compoundAttr.addChild(a_outPointY);
        compoundAttr.addChild(a_outPointZ);
        CHECK_MSTATUS(addAttribute(a_outPoint));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Point X (world-space)
        a_outWorldPointX = numericAttr.create(
                "outWorldPointX", "owpx",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Y (world-space)
        a_outWorldPointY = numericAttr.create(
                "outWorldPointY", "owpy",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Z (world-space)
        a_outWorldPointZ = numericAttr.create(
                "outWorldPointZ", "owpz",
                MFnNumericData::kDouble, 0.0, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point (parent of outWorldPoint* attributes)
        a_outWorldPoint = compoundAttr.create("outWorldPoint", "owp", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outWorldPointX);
        compoundAttr.addChild(a_outWorldPointY);
        compoundAttr.addChild(a_outWorldPointZ);
        CHECK_MSTATUS(addAttribute(a_outWorldPoint));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Matrix (camera-space)
        a_outMatrix = matrixAttr.create(
                "outMatrix", "omt",
                MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(false));
        CHECK_MSTATUS(matrixAttr.setKeyable(false));
        CHECK_MSTATUS(matrixAttr.setReadable(true));
        CHECK_MSTATUS(matrixAttr.setWritable(false));
        CHECK_MSTATUS(addAttribute(a_outMatrix));

        // Out World Matrix (world-space)
        a_outWorldMatrix = matrixAttr.create(
                "outWorldMatrix", "owmt",
                MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(false));
        CHECK_MSTATUS(matrixAttr.setKeyable(false));
        CHECK_MSTATUS(matrixAttr.setReadable(true));
        CHECK_MSTATUS(matrixAttr.setWritable(false));
        CHECK_MSTATUS(addAttribute(a_outWorldMatrix));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Camera Projection Matrix (camera-space)
        a_outCameraProjectionMatrix = matrixAttr.create(
                "outCameraProjectionMatrix", "ocpmt",
                MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(false));
        CHECK_MSTATUS(matrixAttr.setKeyable(false));
        CHECK_MSTATUS(matrixAttr.setReadable(true));
        CHECK_MSTATUS(matrixAttr.setWritable(false));
        CHECK_MSTATUS(addAttribute(a_outCameraProjectionMatrix));

        // Out Inverse Camera Projection Matrix (camera-space)
        a_outInverseCameraProjectionMatrix = matrixAttr.create(
                "outInverseCameraProjectionMatrix", "oicpmt",
                MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(false));
        CHECK_MSTATUS(matrixAttr.setKeyable(false));
        CHECK_MSTATUS(matrixAttr.setReadable(true));
        CHECK_MSTATUS(matrixAttr.setWritable(false));
        CHECK_MSTATUS(addAttribute(a_outInverseCameraProjectionMatrix));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out World Camera Projection Matrix (world-space)
        a_outWorldCameraProjectionMatrix = matrixAttr.create(
                "outWorldCameraProjectionMatrix", "owcpmt",
                MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(false));
        CHECK_MSTATUS(matrixAttr.setKeyable(false));
        CHECK_MSTATUS(matrixAttr.setReadable(true));
        CHECK_MSTATUS(matrixAttr.setWritable(false));
        CHECK_MSTATUS(addAttribute(a_outWorldCameraProjectionMatrix));

        // Out World Inverse Camera Projection Matrix (world-space)
        a_outWorldInverseCameraProjectionMatrix = matrixAttr.create(
                "outWorldInverseCameraProjectionMatrix", "owicpmt",
                MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(false));
        CHECK_MSTATUS(matrixAttr.setKeyable(false));
        CHECK_MSTATUS(matrixAttr.setReadable(true));
        CHECK_MSTATUS(matrixAttr.setWritable(false));
        CHECK_MSTATUS(addAttribute(a_outWorldInverseCameraProjectionMatrix));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Horizontal Pan
        a_outHorizontalPan = numericAttr.create(
                "outHorizonalPan", "ohpn",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Vertical Pan
        a_outVerticalPan = numericAttr.create(
                "outVerticalPan", "ovpn",
                MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Pan (parent of out*Pan attributes)
        a_outPan = compoundAttr.create("outPan", "opn", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outHorizontalPan);
        compoundAttr.addChild(a_outVerticalPan);
        CHECK_MSTATUS(addAttribute(a_outPan));
    }

    //////////////////////////////////////////////////////////////////////////

    // Attribute Affects
    // TODO: Check and make sure there are no unneeded attribute affects relationships.
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_transformWorldMatrix, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_cameraWorldMatrix, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_applyMatrix, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenX, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenY, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_overrideScreenZ, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_screenX, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_screenX, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_screenY, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_screenY, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_screenZ, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_depthScale, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_focalLength, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_cameraAperture, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmAperture, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmAperture, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_filmOffset, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_horizontalFilmOffset, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_verticalFilmOffset, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_filmFit, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_nearClipPlane, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_farClipPlane, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_cameraScale, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_imageWidth, a_outVerticalPan));

    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outCoord));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outCoordX));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outCoordY));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outNormCoord));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outNormCoordX));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outNormCoordY));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outMarkerCoord));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outMarkerCoordX));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outMarkerCoordY));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outMarkerCoordZ));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outPixel));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outPixelX));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outPixelY));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outInsideFrustum));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outPointZ));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outWorldPoint));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outWorldPointX));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outWorldPointY));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outWorldPointZ));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outWorldMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outWorldCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outWorldInverseCameraProjectionMatrix));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outPan));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outHorizontalPan));
    CHECK_MSTATUS(attributeAffects(a_imageHeight, a_outVerticalPan));

    return MS::kSuccess;
}
