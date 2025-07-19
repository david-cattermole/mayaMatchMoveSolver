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

#include "MMReprojectionNode.h"

// STL
#include <cmath>
#include <cstring>

// Maya
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MPlug.h>

// MM Solver
#include "mmSolver/core/reprojection.h"
#include "mmSolver/mayahelper/maya_camera.h"  // getProjectionMatrix, computeFrustumCoordinates
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

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
MObject MMReprojectionNode::a_outCameraDirectionRatio;

MMReprojectionNode::MMReprojectionNode() {}

MMReprojectionNode::~MMReprojectionNode() {}

MString MMReprojectionNode::nodeName() {
    return MString(MM_REPROJECTION_TYPE_NAME);
}

MStatus MMReprojectionNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if ((plug == a_outCoord) || (plug == a_outCoordX) ||
        (plug == a_outCoordY) || (plug == a_outNormCoord) ||
        (plug == a_outNormCoordX) || (plug == a_outNormCoordY) ||
        (plug == a_outMarkerCoord) || (plug == a_outMarkerCoordX) ||
        (plug == a_outMarkerCoordY) || (plug == a_outMarkerCoordZ) ||
        (plug == a_outPixel) || (plug == a_outPixelX) ||
        (plug == a_outPixelY) || (plug == a_outInsideFrustum) ||
        (plug == a_outPoint) || (plug == a_outPointX) ||
        (plug == a_outPointY) || (plug == a_outPointZ) ||
        (plug == a_outWorldPoint) || (plug == a_outWorldPointX) ||
        (plug == a_outWorldPointY) || (plug == a_outWorldPointZ) ||
        (plug == a_outMatrix) || (plug == a_outWorldMatrix) ||
        (plug == a_outCameraProjectionMatrix) ||
        (plug == a_outInverseCameraProjectionMatrix) ||
        (plug == a_outWorldCameraProjectionMatrix) ||
        (plug == a_outWorldInverseCameraProjectionMatrix) ||
        (plug == a_outPan) || (plug == a_outHorizontalPan) ||
        (plug == a_outVerticalPan) || (plug == a_outCameraDirectionRatio)) {
        // Get Data Handles
        MDataHandle tfmMatrixHandle =
            data.inputValue(a_transformWorldMatrix, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix tfmMatrix = tfmMatrixHandle.asMatrix();

        MDataHandle camMatrixHandle =
            data.inputValue(a_cameraWorldMatrix, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix camMatrix = camMatrixHandle.asMatrix();

        MDataHandle applyMatrixHandle = data.inputValue(a_applyMatrix, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix applyMatrix = applyMatrixHandle.asMatrix();

        MDataHandle focalLengthHandle = data.inputValue(a_focalLength, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double focalLength = focalLengthHandle.asDouble();

        MDataHandle horizontalFilmApertureHandle =
            data.inputValue(a_horizontalFilmAperture, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double horizontalFilmAperture = horizontalFilmApertureHandle.asDouble();

        MDataHandle verticalFilmApertureHandle =
            data.inputValue(a_verticalFilmAperture, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double verticalFilmAperture = verticalFilmApertureHandle.asDouble();

        MDataHandle horizontalFilmOffsetHandle =
            data.inputValue(a_horizontalFilmOffset, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double horizontalFilmOffset = horizontalFilmOffsetHandle.asDouble();

        MDataHandle verticalFilmOffsetHandle =
            data.inputValue(a_verticalFilmOffset, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double verticalFilmOffset = verticalFilmOffsetHandle.asDouble();

        MDataHandle filmFitHandle = data.inputValue(a_filmFit, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        short filmFit = filmFitHandle.asShort();

        // MDataHandle nearClipPlaneHandle = data.inputValue(a_nearClipPlane,
        //                                                   &status);
        // MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        // double nearClipPlane = nearClipPlaneHandle.asDouble();

        // TODO: near clip plane forced to 0.1, otherwise reprojection
        // does't work. Why? No idea.
        double nearClipPlane = 0.1;

        MDataHandle farClipPlaneHandle =
            data.inputValue(a_farClipPlane, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double farClipPlane = farClipPlaneHandle.asDouble();

        MDataHandle cameraScaleHandle = data.inputValue(a_cameraScale, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double cameraScale = cameraScaleHandle.asDouble();

        MDataHandle imageWidthHandle = data.inputValue(a_imageWidth, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double imageWidth = imageWidthHandle.asDouble();

        MDataHandle imageHeightHandle = data.inputValue(a_imageHeight, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double imageHeight = imageHeightHandle.asDouble();

        MDataHandle overrideScreenXHandle =
            data.inputValue(a_overrideScreenX, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        bool overrideScreenX = overrideScreenXHandle.asBool();

        MDataHandle overrideScreenYHandle =
            data.inputValue(a_overrideScreenY, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        bool overrideScreenY = overrideScreenYHandle.asBool();

        MDataHandle overrideScreenZHandle =
            data.inputValue(a_overrideScreenZ, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        bool overrideScreenZ = overrideScreenZHandle.asBool();

        MDataHandle screenXHandle = data.inputValue(a_screenX, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double screenX = screenXHandle.asDouble();

        MDataHandle screenYHandle = data.inputValue(a_screenY, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double screenY = screenYHandle.asDouble();

        MDataHandle screenZHandle = data.inputValue(a_screenZ, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double screenZ = screenZHandle.asDouble();

        MDataHandle depthScaleHandle = data.inputValue(a_depthScale, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
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
            tfmMatrix, camMatrix,

            // Camera
            focalLength, horizontalFilmAperture, verticalFilmAperture,
            horizontalFilmOffset, verticalFilmOffset, filmFit, nearClipPlane,
            farClipPlane, cameraScale,

            // Image
            imageWidth, imageHeight,

            // Manipulation
            applyMatrix, overrideScreenX, overrideScreenY, overrideScreenZ,
            screenX, screenY, screenZ, depthScale,

            // Outputs
            outCoordX, outCoordY, outNormCoordX, outNormCoordY, outMarkerCoordX,
            outMarkerCoordY, outMarkerCoordZ, outPixelX, outPixelY,
            outInsideFrustum, outPointX, outPointY, outPointZ, outWorldPointX,
            outWorldPointY, outWorldPointZ, outMatrix, outWorldMatrix,
            outCameraProjectionMatrix, outInverseCameraProjectionMatrix,
            outWorldCameraProjectionMatrix,
            outWorldInverseCameraProjectionMatrix, outHorizontalPan,
            outVerticalPan);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        // Camera Direction Ratio - A.K.A. dot product of camera
        // direction and direction from camera to reprojected point.
        double outCameraDirectionRatio = 0.0;
        status = calculateCameraFacingRatio(tfmMatrix, camMatrix,
                                            outCameraDirectionRatio);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

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
        MDataHandle outInsideFrustumHandle =
            data.outputValue(a_outInsideFrustum);
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
        MDataHandle outCameraProjectionMatrixHandle =
            data.outputValue(a_outCameraProjectionMatrix);
        outCameraProjectionMatrixHandle.setMMatrix(outCameraProjectionMatrix);
        outCameraProjectionMatrixHandle.setClean();

        // Output Inverse Camera Projection Matrix
        MDataHandle outInverseCameraProjectionMatrixHandle =
            data.outputValue(a_outInverseCameraProjectionMatrix);
        outInverseCameraProjectionMatrixHandle.setMMatrix(
            outInverseCameraProjectionMatrix);
        outInverseCameraProjectionMatrixHandle.setClean();

        // Output World Camera Projection Matrix
        MDataHandle outWorldCameraProjectionMatrixHandle =
            data.outputValue(a_outWorldCameraProjectionMatrix);
        outWorldCameraProjectionMatrixHandle.setMMatrix(
            outWorldCameraProjectionMatrix);
        outWorldCameraProjectionMatrixHandle.setClean();

        // Output World Inverse Camera Projection Matrix
        MDataHandle outWorldInverseCameraProjectionMatrixHandle =
            data.outputValue(a_outWorldInverseCameraProjectionMatrix);
        outWorldInverseCameraProjectionMatrixHandle.setMMatrix(
            outWorldInverseCameraProjectionMatrix);
        outWorldInverseCameraProjectionMatrixHandle.setClean();

        // Output Pan
        MDataHandle outHorizontalPanHandle =
            data.outputValue(a_outHorizontalPan);
        MDataHandle outVerticalPanHandle = data.outputValue(a_outVerticalPan);
        outHorizontalPanHandle.setDouble(outHorizontalPan);
        outVerticalPanHandle.setDouble(outVerticalPan);
        outHorizontalPanHandle.setClean();
        outVerticalPanHandle.setClean();

        // Output Camera Direction Ratio
        MDataHandle outCameraDirectionRatioHandle =
            data.outputValue(a_outCameraDirectionRatio);
        outCameraDirectionRatioHandle.setDouble(outCameraDirectionRatio);
        outCameraDirectionRatioHandle.setClean();

        status = MS::kSuccess;
    }

    return status;
}

void *MMReprojectionNode::creator() { return (new MMReprojectionNode()); }

MStatus MMReprojectionNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnEnumAttribute enumAttr;
    MFnMatrixAttribute matrixAttr;
    MFnCompoundAttribute compoundAttr;

    {
        // Transform World Matrix
        a_transformWorldMatrix =
            matrixAttr.create("transformWorldMatrix", "twm",
                              MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setConnectable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_transformWorldMatrix));

        // Camera World Matrix
        a_cameraWorldMatrix = matrixAttr.create(
            "cameraWorldMatrix", "cwm", MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setConnectable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_cameraWorldMatrix));

        // Apply Matrix
        a_applyMatrix = matrixAttr.create("applyMatrix", "aplym",
                                          MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setConnectable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_applyMatrix));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Override Screen X
        a_overrideScreenX = numericAttr.create("overrideScreenX", "ovrdscx",
                                               MFnNumericData::kBoolean, false);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_overrideScreenX));

        // Override Screen Y
        a_overrideScreenY = numericAttr.create("overrideScreenY", "ovrdscy",
                                               MFnNumericData::kBoolean, false);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_overrideScreenY));

        // Override Screen Z
        a_overrideScreenZ = numericAttr.create("overrideScreenZ", "ovrdscz",
                                               MFnNumericData::kBoolean, false);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_overrideScreenZ));

        // ScreenX (Left-Right)
        a_screenX =
            numericAttr.create("screenX", "scx", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_screenX));

        // ScreenY (Up-Down)
        a_screenY =
            numericAttr.create("screenY", "scy", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_screenY));

        // ScreenZ (Depth)
        a_screenZ =
            numericAttr.create("screenZ", "scz", MFnNumericData::kDouble, 1.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_screenZ));

        // Depth Scale
        a_depthScale = numericAttr.create("depthScale", "dptscl",
                                          MFnNumericData::kDouble, 1.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_depthScale));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Focal Length (millimetres)
        a_focalLength = numericAttr.create("focalLength", "fl",
                                           MFnNumericData::kDouble, 35.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_focalLength));

        // Horizontal Film Aperture (inches)
        a_horizontalFilmAperture = numericAttr.create(
            "horizontalFilmAperture", "hfa", MFnNumericData::kDouble, 1.41732);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Vertical Film Aperture (inches)
        a_verticalFilmAperture = numericAttr.create(
            "verticalFilmAperture", "vfa", MFnNumericData::kDouble, 0.94488);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Film Offset (parent of filmOffset* attributes)
        a_cameraAperture =
            compoundAttr.create("cameraAperture", "cap", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_horizontalFilmAperture);
        compoundAttr.addChild(a_verticalFilmAperture);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_cameraAperture));

        // Horizontal Film Offset (inches)
        a_horizontalFilmOffset = numericAttr.create(
            "horizontalFilmOffset", "hfo", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Vertical Film Offset (inches)
        a_verticalFilmOffset = numericAttr.create("verticalFilmOffset", "vfo",
                                                  MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Film Offset (parent of filmOffset* attributes)
        a_filmOffset = compoundAttr.create("filmOffset", "fio", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_horizontalFilmOffset);
        compoundAttr.addChild(a_verticalFilmOffset);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_filmOffset));

        // Film Fit; 0=fill, 1=horizontal, 2=vertical, 3=overscan
        a_filmFit = enumAttr.create("filmFit", "ff", 0, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("Fit", 0));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("Horizontal", 1));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("Vertical", 2));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("Overscan", 3));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_filmFit));

        // Near Clip Plane
        a_nearClipPlane = numericAttr.create("nearClipPlane", "ncp",
                                             MFnNumericData::kDouble, 0.1);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_nearClipPlane));

        // Far Clip Plane
        a_farClipPlane = numericAttr.create("farClipPlane", "fcp",
                                            MFnNumericData::kDouble, 10000.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_farClipPlane));

        // Camera Scale
        a_cameraScale = numericAttr.create("cameraScale", "cs",
                                           MFnNumericData::kDouble, 1.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_cameraScale));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Image Width
        a_imageWidth = numericAttr.create("imageWidth", "iw",
                                          MFnNumericData::kDouble, 1920.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_imageWidth));

        // Image Height
        a_imageHeight = numericAttr.create("imageHeight", "ih",
                                           MFnNumericData::kDouble, 1080.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_imageHeight));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Coord X
        a_outCoordX = numericAttr.create("outCoordX", "ocdx",
                                         MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Coord Y
        a_outCoordY = numericAttr.create("outCoordY", "ocdy",
                                         MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Coord (parent of outCoord* attributes)
        a_outCoord = compoundAttr.create("outCoord", "ocd", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outCoordX);
        compoundAttr.addChild(a_outCoordY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outCoord));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Normalised Coord X
        a_outNormCoordX = numericAttr.create("outNormCoordX", "oncdx",
                                             MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Normalised Coord Y
        a_outNormCoordY = numericAttr.create("outNormCoordY", "oncdy",
                                             MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Normalised Coord (parent of outNormCoord* attributes)
        a_outNormCoord = compoundAttr.create("outNormCoord", "oncd", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outNormCoordX);
        compoundAttr.addChild(a_outNormCoordY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outNormCoord));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Marker Coord X
        a_outMarkerCoordX = numericAttr.create("outMarkerCoordX", "omcdx",
                                               MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Marker Coord Y
        a_outMarkerCoordY = numericAttr.create("outMarkerCoordY", "omcdy",
                                               MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Marker Coord Z
        a_outMarkerCoordZ = numericAttr.create("outMarkerCoordZ", "omcdz",
                                               MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Marker Coord (parent of outMarkerCoord* attributes)
        a_outMarkerCoord =
            compoundAttr.create("outMarkerCoord", "omcd", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outMarkerCoordX);
        compoundAttr.addChild(a_outMarkerCoordY);
        compoundAttr.addChild(a_outMarkerCoordZ);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outMarkerCoord));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Pixel Coord X
        a_outPixelX = numericAttr.create("outPixelX", "opixx",
                                         MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Pixel Coord Y
        a_outPixelY = numericAttr.create("outPixelY", "opixy",
                                         MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Pixel Coord (parent of outPixel* attributes)
        a_outPixel = compoundAttr.create("outPixel", "opix", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outPixelX);
        compoundAttr.addChild(a_outPixelY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outPixel));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Inside Frustum
        a_outInsideFrustum = numericAttr.create(
            "outInsideFrustum", "oinftm", MFnNumericData::kBoolean, false);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outInsideFrustum));
    }

    /////////////////////////////////////////////////////////////////////////

    {
        // Out Point X
        a_outPointX = numericAttr.create("outPointX", "opx",
                                         MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Y
        a_outPointY = numericAttr.create("outPointY", "opy",
                                         MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Z
        a_outPointZ = numericAttr.create("outPointZ", "opz",
                                         MFnNumericData::kDouble, 0.0, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point (parent of outPoint* attributes)
        a_outPoint = compoundAttr.create("outPoint", "op", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outPointX);
        compoundAttr.addChild(a_outPointY);
        compoundAttr.addChild(a_outPointZ);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outPoint));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Point X (world-space)
        a_outWorldPointX = numericAttr.create("outWorldPointX", "owpx",
                                              MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Y (world-space)
        a_outWorldPointY = numericAttr.create("outWorldPointY", "owpy",
                                              MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point Z (world-space)
        a_outWorldPointZ = numericAttr.create(
            "outWorldPointZ", "owpz", MFnNumericData::kDouble, 0.0, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Point (parent of outWorldPoint* attributes)
        a_outWorldPoint = compoundAttr.create("outWorldPoint", "owp", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outWorldPointX);
        compoundAttr.addChild(a_outWorldPointY);
        compoundAttr.addChild(a_outWorldPointZ);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outWorldPoint));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Matrix (camera-space)
        a_outMatrix = matrixAttr.create("outMatrix", "omt",
                                        MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outMatrix));

        // Out World Matrix (world-space)
        a_outWorldMatrix = matrixAttr.create(
            "outWorldMatrix", "owmt", MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outWorldMatrix));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Camera Projection Matrix (camera-space)
        a_outCameraProjectionMatrix =
            matrixAttr.create("outCameraProjectionMatrix", "ocpmt",
                              MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outCameraProjectionMatrix));

        // Out Inverse Camera Projection Matrix (camera-space)
        a_outInverseCameraProjectionMatrix =
            matrixAttr.create("outInverseCameraProjectionMatrix", "oicpmt",
                              MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(
            addAttribute(a_outInverseCameraProjectionMatrix));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out World Camera Projection Matrix (world-space)
        a_outWorldCameraProjectionMatrix =
            matrixAttr.create("outWorldCameraProjectionMatrix", "owcpmt",
                              MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outWorldCameraProjectionMatrix));

        // Out World Inverse Camera Projection Matrix (world-space)
        a_outWorldInverseCameraProjectionMatrix =
            matrixAttr.create("outWorldInverseCameraProjectionMatrix",
                              "owicpmt", MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(
            addAttribute(a_outWorldInverseCameraProjectionMatrix));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Horizontal Pan
        a_outHorizontalPan = numericAttr.create("outHorizonalPan", "ohpn",
                                                MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Vertical Pan
        a_outVerticalPan = numericAttr.create("outVerticalPan", "ovpn",
                                              MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Pan (parent of out*Pan attributes)
        a_outPan = compoundAttr.create("outPan", "opn", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outHorizontalPan);
        compoundAttr.addChild(a_outVerticalPan);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outPan));
    }

    {
        // Out Camera Direction Ratio
        a_outCameraDirectionRatio = numericAttr.create(
            "outCameraDirectionRatio", "ocdr", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outCameraDirectionRatio));
    }

    //////////////////////////////////////////////////////////////////////////

    // Attribute Affects
    // TODO: Check and make sure there are no unneeded attribute affects
    // relationships.

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(a_transformWorldMatrix);
    inputAttrs.append(a_cameraWorldMatrix);
    inputAttrs.append(a_applyMatrix);
    inputAttrs.append(a_overrideScreenX);
    inputAttrs.append(a_overrideScreenY);
    inputAttrs.append(a_overrideScreenZ);
    inputAttrs.append(a_screenX);
    inputAttrs.append(a_screenY);
    inputAttrs.append(a_screenZ);
    inputAttrs.append(a_depthScale);
    inputAttrs.append(a_focalLength);
    inputAttrs.append(a_cameraAperture);
    inputAttrs.append(a_horizontalFilmAperture);
    inputAttrs.append(a_verticalFilmAperture);
    inputAttrs.append(a_filmOffset);
    inputAttrs.append(a_horizontalFilmOffset);
    inputAttrs.append(a_verticalFilmOffset);
    inputAttrs.append(a_filmFit);
    inputAttrs.append(a_nearClipPlane);
    inputAttrs.append(a_farClipPlane);
    inputAttrs.append(a_cameraScale);
    inputAttrs.append(a_imageWidth);
    inputAttrs.append(a_imageHeight);

    MObjectArray outputAttrs;
    outputAttrs.append(a_outCoord);
    outputAttrs.append(a_outCoordX);
    outputAttrs.append(a_outCoordY);
    outputAttrs.append(a_outNormCoord);
    outputAttrs.append(a_outNormCoordX);
    outputAttrs.append(a_outNormCoordY);
    outputAttrs.append(a_outMarkerCoord);
    outputAttrs.append(a_outMarkerCoordX);
    outputAttrs.append(a_outMarkerCoordY);
    outputAttrs.append(a_outMarkerCoordZ);
    outputAttrs.append(a_outPixel);
    outputAttrs.append(a_outPixelX);
    outputAttrs.append(a_outPixelY);
    outputAttrs.append(a_outInsideFrustum);
    outputAttrs.append(a_outPoint);
    outputAttrs.append(a_outPointX);
    outputAttrs.append(a_outPointY);
    outputAttrs.append(a_outPointZ);
    outputAttrs.append(a_outWorldPoint);
    outputAttrs.append(a_outWorldPointX);
    outputAttrs.append(a_outWorldPointY);
    outputAttrs.append(a_outWorldPointZ);
    outputAttrs.append(a_outMatrix);
    outputAttrs.append(a_outWorldMatrix);
    outputAttrs.append(a_outCameraProjectionMatrix);
    outputAttrs.append(a_outInverseCameraProjectionMatrix);
    outputAttrs.append(a_outWorldCameraProjectionMatrix);
    outputAttrs.append(a_outWorldInverseCameraProjectionMatrix);
    outputAttrs.append(a_outPan);
    outputAttrs.append(a_outHorizontalPan);
    outputAttrs.append(a_outVerticalPan);
    outputAttrs.append(a_outCameraDirectionRatio);

    MMSOLVER_CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return MS::kSuccess;
}

}  // namespace mmsolver
