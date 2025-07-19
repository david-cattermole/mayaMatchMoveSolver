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

#include "MMCameraCalibrateNode.h"

#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MEulerRotation.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MPlug.h>
#include <maya/MStreamUtils.h>
#include <maya/MTransformationMatrix.h>

// STL
#include <cmath>
#include <cstring>

// MM Solver Libs
#include <mmcore/mmcamera.h>
#include <mmcore/mmcoord.h>

// MM Solver
#include "mmSolver/calibrate/vanishing_point.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

// #define WITH_PRINCIPAL_POINT

namespace mmsolver {

MMatrix convertToMMatrix(mmdata::Matrix4x4 matrix) {
    const double matrix_values[4][4] = {
        // X
        {matrix.m00_, matrix.m10_, matrix.m20_, matrix.m30_},
        // Y
        {matrix.m01_, matrix.m11_, matrix.m21_, matrix.m31_},
        // Z
        {matrix.m02_, matrix.m12_, matrix.m22_, matrix.m32_},
        // W
        {matrix.m03_, matrix.m13_, matrix.m23_, matrix.m33_},
    };
    return MMatrix(matrix_values);
}

MStatus getPoint2DAttrValue(MDataBlock &data, MObject &attr_x, MObject &attr_y,
                            mmdata::Point2D &output) {
    MStatus status = MS::kUnknownParameter;

    MDataHandle xHandle = data.inputValue(attr_x, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    double x = xHandle.asDouble();

    MDataHandle yHandle = data.inputValue(attr_y, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    double y = yHandle.asDouble();

    output = mmdata::Point2D(x, y);
    return MS::kSuccess;
}

MStatus getVector3DAttrValue(MDataBlock &data, MObject &attr_x, MObject &attr_y,
                             MObject &attr_z, mmdata::Vector3D &output) {
    MStatus status = MS::kUnknownParameter;

    MDataHandle xHandle = data.inputValue(attr_x, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    double x = xHandle.asDouble();

    MDataHandle yHandle = data.inputValue(attr_y, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    double y = yHandle.asDouble();

    MDataHandle zHandle = data.inputValue(attr_z, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    double z = zHandle.asDouble();

    output = mmdata::Vector3D(x, y, z);
    return MS::kSuccess;
}

MTypeId MMCameraCalibrateNode::m_id(MM_CAMERA_CALIBRATE_TYPE_ID);

// Input Attributes
MObject MMCameraCalibrateNode::a_calibrationMode;

MObject MMCameraCalibrateNode::a_focalLength;

MObject MMCameraCalibrateNode::a_cameraApertureUnit;
MObject MMCameraCalibrateNode::a_cameraAperture;
MObject MMCameraCalibrateNode::a_horizontalFilmAperture;
MObject MMCameraCalibrateNode::a_verticalFilmAperture;

MObject MMCameraCalibrateNode::a_sceneScaleMode;
MObject MMCameraCalibrateNode::a_uniformScale;
MObject MMCameraCalibrateNode::a_cameraHeight;

MObject MMCameraCalibrateNode::a_originPoint;
MObject MMCameraCalibrateNode::a_originPointX;
MObject MMCameraCalibrateNode::a_originPointY;

MObject MMCameraCalibrateNode::a_rotatePlane;
MObject MMCameraCalibrateNode::a_rotatePlaneX;
MObject MMCameraCalibrateNode::a_rotatePlaneY;
MObject MMCameraCalibrateNode::a_rotatePlaneZ;
MObject MMCameraCalibrateNode::a_rotateOrder;

#ifdef WITH_PRINCIPAL_POINT
MObject MMCameraCalibrateNode::a_principalPoint;
MObject MMCameraCalibrateNode::a_principalPointX;
MObject MMCameraCalibrateNode::a_principalPointY;
#endif

MObject MMCameraCalibrateNode::a_horizonPointA;
MObject MMCameraCalibrateNode::a_horizonPointAX;
MObject MMCameraCalibrateNode::a_horizonPointAY;

MObject MMCameraCalibrateNode::a_horizonPointB;
MObject MMCameraCalibrateNode::a_horizonPointBX;
MObject MMCameraCalibrateNode::a_horizonPointBY;

MObject MMCameraCalibrateNode::a_vanishingPointA;
MObject MMCameraCalibrateNode::a_vanishingPointAX;
MObject MMCameraCalibrateNode::a_vanishingPointAY;

MObject MMCameraCalibrateNode::a_vanishingPointB;
MObject MMCameraCalibrateNode::a_vanishingPointBX;
MObject MMCameraCalibrateNode::a_vanishingPointBY;

// Output Attributes
MObject MMCameraCalibrateNode::a_outMatrixInverse;
MObject MMCameraCalibrateNode::a_outMatrix;

MObject MMCameraCalibrateNode::a_outFocalLength;

MObject MMCameraCalibrateNode::a_outCameraAperture;
MObject MMCameraCalibrateNode::a_outHorizontalFilmAperture;
MObject MMCameraCalibrateNode::a_outVerticalFilmAperture;

#ifdef WITH_PRINCIPAL_POINT
MObject MMCameraCalibrateNode::a_outFilmOffset;
MObject MMCameraCalibrateNode::a_outHorizontalFilmOffset;
MObject MMCameraCalibrateNode::a_outVerticalFilmOffset;

MObject MMCameraCalibrateNode::a_outPrincipalPoint;
MObject MMCameraCalibrateNode::a_outPrincipalPointX;
MObject MMCameraCalibrateNode::a_outPrincipalPointY;
#endif

MObject MMCameraCalibrateNode::a_outVanishingPointA;
MObject MMCameraCalibrateNode::a_outVanishingPointAX;
MObject MMCameraCalibrateNode::a_outVanishingPointAY;

MObject MMCameraCalibrateNode::a_outVanishingPointB;
MObject MMCameraCalibrateNode::a_outVanishingPointBX;
MObject MMCameraCalibrateNode::a_outVanishingPointBY;

MMCameraCalibrateNode::MMCameraCalibrateNode() {}

MMCameraCalibrateNode::~MMCameraCalibrateNode() {}

MString MMCameraCalibrateNode::nodeName() {
    return MString(MM_CAMERA_CALIBRATE_TYPE_NAME);
}

MStatus MMCameraCalibrateNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if ((plug == a_outMatrix) || (plug == a_outMatrixInverse)

        || (plug == a_outFocalLength)

        || (plug == a_outCameraAperture) ||
        (plug == a_outHorizontalFilmAperture) ||
        (plug == a_outVerticalFilmAperture)
#ifdef WITH_PRINCIPAL_POINT
        || (plug == a_outFilmOffset) || (plug == a_outHorizontalFilmOffset) ||
        (plug == a_outVerticalFilmOffset)

        || (plug == a_outPrincipalPoint) || (plug == a_outPrincipalPointX) ||
        (plug == a_outPrincipalPointY)
#endif

        || (plug == a_outVanishingPointA) || (plug == a_outVanishingPointAX) ||
        (plug == a_outVanishingPointAY)

        || (plug == a_outVanishingPointB) || (plug == a_outVanishingPointBX) ||
        (plug == a_outVanishingPointBY)) {

        // Get Data Handles
        //
        ///////////////////////////////
        MDataHandle calibrationModeHandle =
            data.inputValue(a_calibrationMode, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        auto calibrationMode =
            static_cast<CalibrationMode>(calibrationModeHandle.asShort());

        ///////////////////////////////
        MDataHandle sceneScaleModeHandle =
            data.inputValue(a_sceneScaleMode, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        auto sceneScaleMode = static_cast<calibrate::SceneScaleMode>(
            sceneScaleModeHandle.asShort());

        MDataHandle uniformScaleHandle =
            data.inputValue(a_uniformScale, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double uniformScale = uniformScaleHandle.asDouble();

        MDataHandle cameraHeightHandle =
            data.inputValue(a_cameraHeight, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double cameraHeight = cameraHeightHandle.asDouble();

        ///////////////////////////////
        MDataHandle focalLengthHandle = data.inputValue(a_focalLength, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double focalLength_mm = focalLengthHandle.asDouble();

        ///////////////////////////////
        MDataHandle cameraApertureUnitHandle =
            data.inputValue(a_cameraApertureUnit, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        auto cameraApertureUnit =
            static_cast<CameraApertureUnit>(cameraApertureUnitHandle.asShort());

        MDataHandle horizontalFilmApertureHandle =
            data.inputValue(a_horizontalFilmAperture, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double apertureWidth = horizontalFilmApertureHandle.asDouble();

        MDataHandle verticalFilmApertureHandle =
            data.inputValue(a_verticalFilmAperture, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double apertureHeight = verticalFilmApertureHandle.asDouble();

        ///////////////////////////////
        auto originPoint = mmdata::Point2D();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(getPoint2DAttrValue(
            data, a_originPointX, a_originPointY, originPoint));

        ///////////////////////////////
        auto rotatePlane = mmdata::Vector3D();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(getVector3DAttrValue(
            data, a_rotatePlaneX, a_rotatePlaneY, a_rotatePlaneZ, rotatePlane));
        rotatePlane.x_ *= DEGREES_TO_RADIANS;
        rotatePlane.y_ *= DEGREES_TO_RADIANS;
        rotatePlane.z_ *= DEGREES_TO_RADIANS;

        ///////////////////////////////
        MDataHandle rotateOrderHandle = data.inputValue(a_rotateOrder, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        auto rotateOrderValue = rotateOrderHandle.asShort();
        auto rotateOrder =
            static_cast<MEulerRotation::RotationOrder>(rotateOrderValue);

        ///////////////////////////////
        auto principalPoint = mmdata::Point2D();
#ifdef WITH_PRINCIPAL_POINT
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(getPoint2DAttrValue(
            data, a_principalPointX, a_principalPointY, principalPoint));
#endif

        ///////////////////////////////
        auto vanishingPointA = mmdata::Point2D();
        auto vanishingPointB = mmdata::Point2D();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(getPoint2DAttrValue(
            data, a_vanishingPointAX, a_vanishingPointAY, vanishingPointA));
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(getPoint2DAttrValue(
            data, a_vanishingPointBX, a_vanishingPointBY, vanishingPointB));

        // Camera Calibration
        auto filmBackWidth_mm = apertureWidth;
        auto filmBackHeight_mm = apertureHeight;
        if (cameraApertureUnit == CameraApertureUnit::Millimeters) {
            // Nothing to do, the values we got area already in
            // millimeters.
        } else if (cameraApertureUnit == CameraApertureUnit::Inches) {
            // Convert from inches to millimeters.
            filmBackWidth_mm = apertureWidth * 25.4;
            filmBackHeight_mm = apertureHeight * 25.4;
        } else {
            MMSOLVER_PANIC(
                "Invalid CameraApertureUnit value: cameraApertureUnit="
                << static_cast<int32_t>(cameraApertureUnit));
        }

        auto sceneScaleDistance = 1.0;
        if (sceneScaleMode == calibrate::SceneScaleMode::CameraHeight) {
            sceneScaleDistance = cameraHeight;
        } else if (sceneScaleMode == calibrate::SceneScaleMode::UniformScale) {
            sceneScaleDistance = uniformScale;
        } else {
            MMSOLVER_PANIC("Invalid SceneScaleMode value: sceneScaleMode="
                           << static_cast<int32_t>(sceneScaleMode));
        }

        auto outCameraParameters = calibrate::CameraParameters();
        // Ensure film back is correct, even if the 'calibrationMode' is
        // disabled, we will still have the correct camera film back.
        outCameraParameters.filmBackWidth_mm_ = filmBackWidth_mm;
        outCameraParameters.filmBackHeight_mm_ = filmBackHeight_mm;

        bool ok = false;
        if (calibrationMode == CalibrationMode::OneVanishingPoint) {
            // Flat Horizon Line
            auto horizonPointA = mmdata::Point2D(-1.0, 0.0);
            auto horizonPointB = mmdata::Point2D(1.0, 0.0);

            ok = oneVanishingPoint(focalLength_mm, filmBackWidth_mm,
                                   filmBackHeight_mm, originPoint,
                                   principalPoint, vanishingPointA,
                                   horizonPointA, horizonPointB, sceneScaleMode,
                                   sceneScaleDistance, outCameraParameters);
#ifdef MM_DEBUG
            MStreamUtils::stdErrorStream()
                << "oneVanishingPoint: " << ok << '\n';
#endif
        } else if (calibrationMode ==
                   CalibrationMode::OneVanishingPointAndHorizonLine) {
            // Use horizon line points.
            auto horizonPointA = mmdata::Point2D();
            auto horizonPointB = mmdata::Point2D();
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(getPoint2DAttrValue(
                data, a_horizonPointAX, a_horizonPointAY, horizonPointA));
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(getPoint2DAttrValue(
                data, a_horizonPointBX, a_horizonPointBY, horizonPointB));

            ok = calibrate::oneVanishingPoint(
                focalLength_mm, filmBackWidth_mm, filmBackHeight_mm,
                originPoint, principalPoint, vanishingPointA, horizonPointA,
                horizonPointB, sceneScaleMode, sceneScaleDistance,
                outCameraParameters);
#ifdef MM_DEBUG
            MStreamUtils::stdErrorStream()
                << "oneVanishingPoint: " << ok << '\n';
#endif
        } else if (calibrationMode == CalibrationMode::TwoVanishingPoints) {
            ok = calibrate::twoVanishingPoints(
                focalLength_mm, filmBackWidth_mm, filmBackHeight_mm,
                originPoint, principalPoint, vanishingPointA, vanishingPointB,
                sceneScaleMode, sceneScaleDistance, outCameraParameters);
#ifdef MM_DEBUG
            MStreamUtils::stdErrorStream()
                << "twoVanishingPoints: " << ok << '\n';
#endif
        } else {
            MStreamUtils::stdErrorStream()
                << "Calibration Mode is disabled. "
                << static_cast<int>(calibrationMode) << '\n';
        }
        auto cameraMatrix =
            convertToMMatrix(outCameraParameters.transformMatrix_);

        // Rotate the matrix.
        auto rotation = MEulerRotation(rotatePlane.x_, rotatePlane.y_,
                                       rotatePlane.z_, rotateOrder);
        auto orientTfmMatrix = MTransformationMatrix();
        auto space = MSpace::Space::kWorld;
        orientTfmMatrix.rotateBy(rotation, space, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        auto orientMatrix = orientTfmMatrix.asMatrix();

        auto outMatrix = cameraMatrix * orientMatrix;
        auto outMatrixInverse = outMatrix.inverse();
#ifdef MM_DEBUG
        MStreamUtils::stdErrorStream()
            << "outCameraParameters viewTransform: " << outMatrixInverse << '\n'
            << "outCameraParameters cameraTransform: " << outMatrix << '\n';
#endif

        auto outApertureWidth_mm = outCameraParameters.filmBackWidth_mm_;
        auto outApertureHeight_mm = outCameraParameters.filmBackHeight_mm_;
        auto outApertureWidth_inch = outApertureWidth_mm / 25.4;
        auto outApertureHeight_inch = outApertureHeight_mm / 25.4;
        auto outFocalLength_mm = outCameraParameters.focalLength_mm_;
#ifdef MM_DEBUG
        MStreamUtils::stdErrorStream()
            << "outCameraParameters Film Back Width (mm): "
            << outApertureWidth_mm << '\n'
            << "outCameraParameters Film Back Height (mm): "
            << outApertureHeight_mm << '\n'
            << "outCameraParameters Focal Length (mm): " << outFocalLength_mm
            << '\n';
#endif

#ifdef WITH_PRINCIPAL_POINT
        auto outPrincipalPointX = outCameraParameters.principalPoint_.x_;
        auto outPrincipalPointY = outCameraParameters.principalPoint_.y_;
        MStreamUtils::stdErrorStream() << "outCameraParameters principalPoint:"
                                       << " x=" << outPrincipalPointX
                                       << " y=" << outPrincipalPointY << '\n';

        auto outFilmOffset = mmcoord::convertPoint2D(
            mmcoord::Point2DSpace::Marker,
            mmcoord::Point2DSpace::CameraFilmBackInches,
            outCameraParameters.principalPoint_, outApertureWidth_inch,
            outApertureHeight_inch);
        auto outFilmOffsetX_inch = outFilmOffset.x_;
        auto outFilmOffsetY_inch = outFilmOffset.y_;
#endif

        auto vanishingPointAX = outCameraParameters.vanishingPointA_.x_;
        auto vanishingPointAY = outCameraParameters.vanishingPointA_.y_;
        auto vanishingPointBX = outCameraParameters.vanishingPointB_.x_;
        auto vanishingPointBY = outCameraParameters.vanishingPointB_.y_;
#ifdef MM_DEBUG
        MStreamUtils::stdErrorStream()
            << "outCameraParameters vanishingPointA:"
            << " x=" << vanishingPointAX << " y=" << vanishingPointAY << '\n'
            << "outCameraParameters vanishingPointB:"
            << " x=" << vanishingPointBX << " y=" << vanishingPointBY << '\n';
#endif

        // Output Lens Focal Length
        MDataHandle outFocalLengthHandle = data.outputValue(a_outFocalLength);
        outFocalLengthHandle.setDouble(outFocalLength_mm);
        outFocalLengthHandle.setClean();

        // Output Camera Film Back
        MDataHandle outHorizontalFilmApertureHandle =
            data.outputValue(a_outHorizontalFilmAperture);
        outHorizontalFilmApertureHandle.setDouble(outApertureWidth_inch);
        outHorizontalFilmApertureHandle.setClean();

        MDataHandle outVerticalFilmApertureHandle =
            data.outputValue(a_outVerticalFilmAperture);
        outVerticalFilmApertureHandle.setDouble(outApertureHeight_inch);
        outVerticalFilmApertureHandle.setClean();

#ifdef WITH_PRINCIPAL_POINT
        // Output Camera Film Offsets
        MDataHandle outHorizontalFilmOffsetHandle =
            data.outputValue(a_outHorizontalFilmOffset);
        outHorizontalFilmOffsetHandle.setDouble(outFilmOffsetX_inch);
        outHorizontalFilmOffsetHandle.setClean();

        MDataHandle outVerticalFilmOffsetHandle =
            data.outputValue(a_outVerticalFilmOffset);
        outVerticalFilmOffsetHandle.setDouble(outFilmOffsetY_inch);
        outVerticalFilmOffsetHandle.setClean();

        // Output Principal Point
        MDataHandle outPrincipalPointXHandle =
            data.outputValue(a_outPrincipalPointX);
        MDataHandle outPrincipalPointYHandle =
            data.outputValue(a_outPrincipalPointY);
        outPrincipalPointXHandle.setDouble(outPrincipalPointX);
        outPrincipalPointYHandle.setDouble(outPrincipalPointY);
        outPrincipalPointXHandle.setClean();
        outPrincipalPointYHandle.setClean();
#endif

        // Output Vanishing Point A
        MDataHandle outVanishingPointAXHandle =
            data.outputValue(a_outVanishingPointAX);
        MDataHandle outVanishingPointAYHandle =
            data.outputValue(a_outVanishingPointAY);
        outVanishingPointAXHandle.setDouble(vanishingPointAX);
        outVanishingPointAYHandle.setDouble(vanishingPointAY);
        outVanishingPointAXHandle.setClean();
        outVanishingPointAYHandle.setClean();

        // Output Vanishing Point B
        MDataHandle outVanishingPointBXHandle =
            data.outputValue(a_outVanishingPointBX);
        MDataHandle outVanishingPointBYHandle =
            data.outputValue(a_outVanishingPointBY);
        outVanishingPointBXHandle.setDouble(vanishingPointBX);
        outVanishingPointBYHandle.setDouble(vanishingPointBY);
        outVanishingPointBXHandle.setClean();
        outVanishingPointBYHandle.setClean();

        // Output Matrix
        MDataHandle outMatrixHandle = data.outputValue(a_outMatrix);
        outMatrixHandle.setMMatrix(outMatrix);
        outMatrixHandle.setClean();

        // Output Matrix Inverse
        MDataHandle outMatrixInverseHandle =
            data.outputValue(a_outMatrixInverse);
        outMatrixInverseHandle.setMMatrix(outMatrixInverse);
        outMatrixInverseHandle.setClean();

        if (!ok) {
            status = MS::kFailure;
        } else {
            status = MS::kSuccess;
        }
    }

    return status;
}

void *MMCameraCalibrateNode::creator() { return (new MMCameraCalibrateNode()); }

MStatus MMCameraCalibrateNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnEnumAttribute enumAttr;
    MFnMatrixAttribute matrixAttr;
    MFnCompoundAttribute compoundAttr;

    //////////////////////////////////////////////////////////////////////////

    {
        // Calibration mode.
        a_calibrationMode =
            enumAttr.create("calibrationMode", "clbrtmd", 0, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("Disabled", 0));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("OneVanishingPoint", 1));
        MMSOLVER_CHECK_MSTATUS(
            enumAttr.addField("OneVanishingPointAndHorizon", 2));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("TwoVanishingPoints", 3));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_calibrationMode));
    }

    {
        // Focal Length (millimeters)
        a_focalLength = numericAttr.create("focalLength", "fl",
                                           MFnNumericData::kDouble, 35.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_focalLength));

        auto width_mm = 36.0;
        auto height_mm = 24.0;

        // Film Aperture unit.
        //
        // Allow users to choose either
        //  mm or inches. mm is default.
        auto millimetersUnit =
            static_cast<short>(CameraApertureUnit::Millimeters);
        auto inchesUnit = static_cast<short>(CameraApertureUnit::Inches);
        a_cameraApertureUnit = enumAttr.create(
            "cameraApertureUnit", "cmraprtrunt", millimetersUnit, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(
            enumAttr.addField("Millimeters", millimetersUnit));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("Inches", inchesUnit));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_cameraApertureUnit));

        // Horizontal Film Aperture (inches)
        a_horizontalFilmAperture = numericAttr.create(
            "horizontalFilmAperture", "hfa", MFnNumericData::kDouble, width_mm);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Vertical Film Aperture (inches)
        a_verticalFilmAperture = numericAttr.create(
            "verticalFilmAperture", "vfa", MFnNumericData::kDouble, height_mm);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        // Camera Aperture (parent of *filmAperture attributes)
        a_cameraAperture =
            compoundAttr.create("cameraAperture", "cap", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_horizontalFilmAperture);
        compoundAttr.addChild(a_verticalFilmAperture);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_cameraAperture));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Scene Scale mode.
        a_sceneScaleMode =
            enumAttr.create("sceneScaleMode", "scnsclmd", 1, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("UniformScale", 1));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("CameraHeight", 2));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_sceneScaleMode));

        // Uniform Scale
        a_uniformScale = numericAttr.create("uniformScale", "unfscl",
                                            MFnNumericData::kDouble, 1.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_uniformScale));

        // Camera Height
        a_cameraHeight = numericAttr.create("cameraHeight", "cmrhght",
                                            MFnNumericData::kDouble, 1.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_cameraHeight));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // [0.0, 0.0] means the center of the camera.
        auto x = 0.0;
        auto y = 0.0;

        a_originPointX = numericAttr.create("originPointX", "orgptx",
                                            MFnNumericData::kDouble, x);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_originPointY = numericAttr.create("originPointY", "orgpty",
                                            MFnNumericData::kDouble, y);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_originPoint = compoundAttr.create("originPoint", "orgpt", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_originPointX);
        compoundAttr.addChild(a_originPointY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_originPoint));
    }

    {
        a_rotatePlaneX = numericAttr.create("rotatePlaneX", "rotplnx",
                                            MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_rotatePlaneY = numericAttr.create("rotatePlaneY", "rotplny",
                                            MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_rotatePlaneZ = numericAttr.create("rotatePlaneZ", "rotplnz",
                                            MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_rotatePlane = compoundAttr.create("rotatePlane", "rotpln", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_rotatePlaneX);
        compoundAttr.addChild(a_rotatePlaneY);
        compoundAttr.addChild(a_rotatePlaneZ);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_rotatePlane));

        // Rotate Order
        auto xyzMode = static_cast<short>(MEulerRotation::kXYZ);
        auto yzxMode = static_cast<short>(MEulerRotation::kYZX);
        auto zxyMode = static_cast<short>(MEulerRotation::kZXY);
        auto xzyMode = static_cast<short>(MEulerRotation::kXZY);
        auto yxzMode = static_cast<short>(MEulerRotation::kYXZ);
        auto zyxMode = static_cast<short>(MEulerRotation::kZYX);
        a_rotateOrder =
            enumAttr.create("rotateOrder", "rotordr", xyzMode, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("XYZ", xyzMode));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("YZX", yzxMode));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("ZXY", zxyMode));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("XZY", xzyMode));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("YXZ", yxzMode));
        MMSOLVER_CHECK_MSTATUS(enumAttr.addField("ZYX", zyxMode));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(enumAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_rotateOrder));
    }

    //////////////////////////////////////////////////////////////////////////

#ifdef WITH_PRINCIPAL_POINT
    {
        // [0.0, 0.0] means the center of the camera.
        auto x = 0.0;
        auto y = 0.0;

        a_principalPointX = numericAttr.create("principalPointX", "ppntx",
                                               MFnNumericData::kDouble, x);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_principalPointY = numericAttr.create("principalPointY", "ppnty",
                                               MFnNumericData::kDouble, y);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_principalPoint =
            compoundAttr.create("principalPoint", "ppnt", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_principalPointX);
        compoundAttr.addChild(a_principalPointY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_principalPoint));
    }
#endif

    //////////////////////////////////////////////////////////////////////////

    {
        a_horizonPointAX = numericAttr.create("horizonPointAX", "horpntax",
                                              MFnNumericData::kDouble, -1.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_horizonPointAY = numericAttr.create("horizonPointAY", "horpntay",
                                              MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_horizonPointA =
            compoundAttr.create("horizonPointA", "horpnta", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_horizonPointAX);
        compoundAttr.addChild(a_horizonPointAY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_horizonPointA));
    }

    {
        a_horizonPointBX = numericAttr.create("horizonPointBX", "horpntbx",
                                              MFnNumericData::kDouble, 1.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_horizonPointBY = numericAttr.create("horizonPointBY", "horpntby",
                                              MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_horizonPointB =
            compoundAttr.create("horizonPointB", "horpntb", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_horizonPointBX);
        compoundAttr.addChild(a_horizonPointBY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_horizonPointB));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        a_vanishingPointAX = numericAttr.create("vanishingPointAX", "vpax",
                                                MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_vanishingPointAY = numericAttr.create("vanishingPointAY", "vpay",
                                                MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_vanishingPointA =
            compoundAttr.create("vanishingPointA", "vpa", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_vanishingPointAX);
        compoundAttr.addChild(a_vanishingPointAY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_vanishingPointA));
    }

    {
        a_vanishingPointBX = numericAttr.create("vanishingPointBX", "vpbx",
                                                MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_vanishingPointBY = numericAttr.create("vanishingPointBY", "vpby",
                                                MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_vanishingPointB =
            compoundAttr.create("vanishingPointB", "vpb", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_vanishingPointBX);
        compoundAttr.addChild(a_vanishingPointBY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_vanishingPointB));
    }

    //////////////////////////////////////////////////////////////////////////

    // Out Matrix
    {
        a_outMatrix = matrixAttr.create("outMatrix", "omtx",
                                        MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outMatrix));
    }

    // Out Matrix Inverse
    {
        a_outMatrixInverse =
            matrixAttr.create("outMatrixInverse", "omtxinv",
                              MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outMatrixInverse));
    }

    // Camera Focal Length (millimetres)
    {
        a_outFocalLength = numericAttr.create("outFocalLength", "ofl",
                                              MFnNumericData::kDouble, 35.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outFocalLength));
    }

    // Camera Film Back (inches)
    {
        a_outHorizontalFilmAperture = numericAttr.create(
            "outHorizontalFilmAperture", "ohfa", MFnNumericData::kDouble, 35.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outHorizontalFilmAperture));

        a_outVerticalFilmAperture = numericAttr.create(
            "outVerticalFilmAperture", "ovfa", MFnNumericData::kDouble, 35.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outVerticalFilmAperture));

        // Camera Aperture (parent of *FilmAperture attributes)
        a_outCameraAperture =
            compoundAttr.create("outCameraAperture", "ocap", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outHorizontalFilmAperture);
        compoundAttr.addChild(a_outVerticalFilmAperture);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outCameraAperture));
    }

#ifdef WITH_PRINCIPAL_POINT
    // Camera Film Back Offsets (inches)
    {
        a_outHorizontalFilmOffset = numericAttr.create(
            "outHorizontalFilmOffset", "ohfo", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outHorizontalFilmOffset));

        a_outVerticalFilmOffset = numericAttr.create(
            "outVerticalFilmOffset", "ovfo", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outVerticalFilmOffset));

        // Film Offset (parent of *FilmOffset attributes)
        a_outFilmOffset = compoundAttr.create("outFilmOffset", "ofo", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outHorizontalFilmOffset);
        compoundAttr.addChild(a_outVerticalFilmOffset);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outFilmOffset));
    }

    // Out Principal Point
    {
        a_outPrincipalPointX = numericAttr.create("outPrincipalPointX", "oppx",
                                                  MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        a_outPrincipalPointY = numericAttr.create("outPrincipalPointY", "oppy",
                                                  MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        a_outPrincipalPoint =
            compoundAttr.create("outPrincipalPoint", "opp", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outPrincipalPointX);
        compoundAttr.addChild(a_outPrincipalPointY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outPrincipalPoint));
    }
#endif

    // Out Vanishing Point A
    {
        a_outVanishingPointAX = numericAttr.create(
            "outVanishingPointAX", "ovpax", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        a_outVanishingPointAY = numericAttr.create(
            "outVanishingPointAY", "ovpay", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        a_outVanishingPointA =
            compoundAttr.create("outVanishingPointA", "ovpa", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outVanishingPointAX);
        compoundAttr.addChild(a_outVanishingPointAY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outVanishingPointA));
    }

    // Out Vanishing Point B
    {
        a_outVanishingPointBX = numericAttr.create(
            "outVanishingPointBX", "ovpbx", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        a_outVanishingPointBY = numericAttr.create(
            "outVanishingPointBY", "ovpby", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        a_outVanishingPointB =
            compoundAttr.create("outVanishingPointB", "ovpb", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outVanishingPointBX);
        compoundAttr.addChild(a_outVanishingPointBY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outVanishingPointB));
    }

    //////////////////////////////////////////////////////////////////////////

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(a_calibrationMode);

    inputAttrs.append(a_focalLength);

    inputAttrs.append(a_cameraApertureUnit);
    inputAttrs.append(a_cameraAperture);
    inputAttrs.append(a_horizontalFilmAperture);
    inputAttrs.append(a_verticalFilmAperture);

    inputAttrs.append(a_sceneScaleMode);
    inputAttrs.append(a_uniformScale);
    inputAttrs.append(a_cameraHeight);

    inputAttrs.append(a_originPoint);
    inputAttrs.append(a_originPointX);
    inputAttrs.append(a_originPointY);

    inputAttrs.append(a_rotatePlane);
    inputAttrs.append(a_rotatePlaneX);
    inputAttrs.append(a_rotatePlaneY);
    inputAttrs.append(a_rotatePlaneZ);
    inputAttrs.append(a_rotateOrder);

#ifdef WITH_PRINCIPAL_POINT
    inputAttrs.append(a_principalPoint);
    inputAttrs.append(a_principalPointX);
    inputAttrs.append(a_principalPointY);
#endif

    inputAttrs.append(a_horizonPointA);
    inputAttrs.append(a_horizonPointAX);
    inputAttrs.append(a_horizonPointAY);

    inputAttrs.append(a_horizonPointB);
    inputAttrs.append(a_horizonPointBX);
    inputAttrs.append(a_horizonPointBY);

    inputAttrs.append(a_vanishingPointA);
    inputAttrs.append(a_vanishingPointAX);
    inputAttrs.append(a_vanishingPointAY);

    inputAttrs.append(a_vanishingPointB);
    inputAttrs.append(a_vanishingPointBX);
    inputAttrs.append(a_vanishingPointBY);

    MObjectArray outputAttrs;
    outputAttrs.append(a_outMatrix);
    outputAttrs.append(a_outMatrixInverse);

    outputAttrs.append(a_outFocalLength);

    outputAttrs.append(a_outCameraAperture);
    outputAttrs.append(a_outHorizontalFilmAperture);
    outputAttrs.append(a_outVerticalFilmAperture);

#ifdef WITH_PRINCIPAL_POINT
    outputAttrs.append(a_outFilmOffset);
    outputAttrs.append(a_outHorizontalFilmOffset);
    outputAttrs.append(a_outVerticalFilmOffset);

    outputAttrs.append(a_outPrincipalPoint);
    outputAttrs.append(a_outPrincipalPointX);
    outputAttrs.append(a_outPrincipalPointY);
#endif

    outputAttrs.append(a_outVanishingPointA);
    outputAttrs.append(a_outVanishingPointAX);
    outputAttrs.append(a_outVanishingPointAY);

    outputAttrs.append(a_outVanishingPointB);
    outputAttrs.append(a_outVanishingPointBX);
    outputAttrs.append(a_outVanishingPointBY);

    MMSOLVER_CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return MS::kSuccess;
}

}  // namespace mmsolver

#undef MM_DEBUG
#undef WITH_PRINCIPAL_POINT
