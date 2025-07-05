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
 * Simple computation node to keep markers in screen-space when the camera
 * filmback/focal length is modified.
 */

#include "MMMarkerScaleNode.h"

// STL
#include <cmath>
#include <cstring>

// Maya
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MObjectArray.h>
#include <maya/MPlug.h>

// MM Solver
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

MTypeId MMMarkerScaleNode::m_id(MM_MARKER_SCALE_TYPE_ID);

// Input Attributes
MObject MMMarkerScaleNode::a_focalLength;
MObject MMMarkerScaleNode::a_cameraAperture;
MObject MMMarkerScaleNode::a_horizontalFilmAperture;
MObject MMMarkerScaleNode::a_verticalFilmAperture;
MObject MMMarkerScaleNode::a_filmOffset;
MObject MMMarkerScaleNode::a_horizontalFilmOffset;
MObject MMMarkerScaleNode::a_verticalFilmOffset;
MObject MMMarkerScaleNode::a_depth;
MObject MMMarkerScaleNode::a_overscanMode;
MObject MMMarkerScaleNode::a_overscan;
MObject MMMarkerScaleNode::a_overscanX;
MObject MMMarkerScaleNode::a_overscanY;
MObject MMMarkerScaleNode::a_overscanInverse;
MObject MMMarkerScaleNode::a_overscanInverseX;
MObject MMMarkerScaleNode::a_overscanInverseY;

// Output Attributes
MObject MMMarkerScaleNode::a_outTranslate;
MObject MMMarkerScaleNode::a_outTranslateX;
MObject MMMarkerScaleNode::a_outTranslateY;
MObject MMMarkerScaleNode::a_outTranslateZ;
MObject MMMarkerScaleNode::a_outScale;
MObject MMMarkerScaleNode::a_outScaleX;
MObject MMMarkerScaleNode::a_outScaleY;
MObject MMMarkerScaleNode::a_outScaleZ;

MMMarkerScaleNode::MMMarkerScaleNode() {}

MMMarkerScaleNode::~MMMarkerScaleNode() {}

MString MMMarkerScaleNode::nodeName() {
    return MString(MM_MARKER_SCALE_TYPE_NAME);
}

MStatus MMMarkerScaleNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if ((plug == a_outTranslate) || (plug == a_outTranslateX) ||
        (plug == a_outTranslateY) || (plug == a_outTranslateZ) ||
        (plug == a_outScale) || (plug == a_outScaleX) ||
        (plug == a_outScaleY) || (plug == a_outScaleZ)) {
        // Get Data Handles
        MDataHandle focalLengthHandle = data.inputValue(a_focalLength);
        MDataHandle filmBackXHandle = data.inputValue(a_horizontalFilmAperture);
        MDataHandle filmBackYHandle = data.inputValue(a_verticalFilmAperture);
        MDataHandle filmBackOffsetXHandle =
            data.inputValue(a_horizontalFilmOffset);
        MDataHandle filmBackOffsetYHandle =
            data.inputValue(a_verticalFilmOffset);
        MDataHandle depthHandle = data.inputValue(a_depth);
        MDataHandle overscanModeHandle =
            data.inputValue(a_overscanMode, &status);
        MDataHandle overscanHandle = data.inputValue(a_overscan);
        MDataHandle overscanXHandle = data.inputValue(a_overscanX);
        MDataHandle overscanYHandle = data.inputValue(a_overscanY);
        MDataHandle overscanInvHandle = data.inputValue(a_overscanInverse);
        MDataHandle overscanInvXHandle = data.inputValue(a_overscanInverseX);
        MDataHandle overscanInvYHandle = data.inputValue(a_overscanInverseY);

        // Get value
        double focalLength = focalLengthHandle.asDouble();
        double filmBackX = filmBackXHandle.asDouble() * INCH_TO_MM;
        double filmBackY = filmBackYHandle.asDouble() * INCH_TO_MM;
        double filmBackOffsetX = filmBackOffsetXHandle.asDouble() * INCH_TO_MM;
        double filmBackOffsetY = filmBackOffsetYHandle.asDouble() * INCH_TO_MM;
        double depth = depthHandle.asDouble();
        short overscanMode = overscanModeHandle.asShort();
        double overscan = overscanHandle.asDouble();
        double overscanX = overscanXHandle.asDouble();
        double overscanY = overscanYHandle.asDouble();
        double overscanInverse = 1.0 / overscanInvHandle.asDouble();
        double overscanInverseX = 1.0 / overscanInvXHandle.asDouble();
        double overscanInverseY = 1.0 / overscanInvYHandle.asDouble();

        double scale = 0.0;
        getCameraPlaneScale(filmBackX, focalLength, scale);

        double translateX =
            scale * depth * (filmBackOffsetX / (filmBackX * 0.5));
        double translateY = scale * depth *
                            (filmBackOffsetY / (filmBackY * 0.5)) *
                            (filmBackY / filmBackX);
        double translateZ = 0.0;

        double scaleX = scale * depth * 2.0;
        double scaleY = scale * depth * 2.0 * (filmBackY / filmBackX);
        double scaleZ = depth;

        // Apply Overscan factor
        if (overscanMode == 0) {
            // Uniform overscan
            translateX *= overscan;
            translateY *= overscan;
            scaleX *= overscan;
            scaleY *= overscan;
        } else if (overscanMode == 1) {
            // overscan X and Y
            translateX *= overscanX;
            translateY *= overscanY;
            scaleX *= overscanX;
            scaleY *= overscanY;
        } else {
            MMSOLVER_MAYA_ERR("invalid overscan value: " << overscanMode);
        }

        // Apply Overscan Inverse factor
        //
        // Reduces the size of the "display box", therefore adding
        // empty areas to the plate.
        //
        if (overscanMode == 0) {
            // Uniform overscan
            translateX *= overscanInverse;
            translateY *= overscanInverse;
            scaleX *= overscanInverse;
            scaleY *= overscanInverse;
        } else if (overscanMode == 1) {
            // overscan X and Y
            translateX *= overscanInverseX;
            translateY *= overscanInverseY;
            scaleX *= overscanInverseX;
            scaleY *= overscanInverseY;
        } else {
            MMSOLVER_MAYA_ERR("invalid overscan value: " << overscanMode);
        }

        // Output Translate
        MDataHandle outTranslateXHandle = data.outputValue(a_outTranslateX);
        MDataHandle outTranslateYHandle = data.outputValue(a_outTranslateY);
        MDataHandle outTranslateZHandle = data.outputValue(a_outTranslateZ);
        outTranslateXHandle.setDouble(translateX);
        outTranslateYHandle.setDouble(translateY);
        outTranslateZHandle.setDouble(translateZ);
        outTranslateXHandle.setClean();
        outTranslateYHandle.setClean();
        outTranslateZHandle.setClean();

        // Output Scale
        MDataHandle outScaleXHandle = data.outputValue(a_outScaleX);
        MDataHandle outScaleYHandle = data.outputValue(a_outScaleY);
        MDataHandle outScaleZHandle = data.outputValue(a_outScaleZ);
        outScaleXHandle.setDouble(scaleX);
        outScaleYHandle.setDouble(scaleY);
        outScaleZHandle.setDouble(scaleZ);
        outScaleXHandle.setClean();
        outScaleYHandle.setClean();
        outScaleZHandle.setClean();

        status = MS::kSuccess;
    }
    return status;
}

void *MMMarkerScaleNode::creator() { return (new MMMarkerScaleNode()); }

MStatus MMMarkerScaleNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnEnumAttribute enumAttr;
    MFnCompoundAttribute compoundAttr;

    // Focal Length (millimetres)
    a_focalLength =
        numericAttr.create("focalLength", "fl", MFnNumericData::kDouble, 35.0);
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
    a_cameraAperture = compoundAttr.create("cameraAperture", "cap", &status);
    MMSOLVER_CHECK_MSTATUS(status);
    compoundAttr.addChild(a_horizontalFilmAperture);
    compoundAttr.addChild(a_verticalFilmAperture);
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_cameraAperture));

    // Horizontal Film Offset (inches)
    a_horizontalFilmOffset = numericAttr.create("horizontalFilmOffset", "hfo",
                                                MFnNumericData::kDouble, 0.0);
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

    // Depth
    a_depth = numericAttr.create("depth", "dpt", MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_depth));

    // Overscan Mode; 0='uniform', 1='overscan x and y'
    a_overscanMode = enumAttr.create("overscanMode", "ovrscnmd", 0, &status);
    MMSOLVER_CHECK_MSTATUS(status);
    MMSOLVER_CHECK_MSTATUS(enumAttr.addField("Uniform", 0));
    MMSOLVER_CHECK_MSTATUS(enumAttr.addField("Overscan X and Y", 1));
    MMSOLVER_CHECK_MSTATUS(enumAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(enumAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_overscanMode));

    // Overscan
    a_overscan =
        numericAttr.create("overscan", "ovrscn", MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setHidden(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setNiceNameOverride("Uniform Overscan"));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_overscan));

    // Overscan X
    a_overscanX = numericAttr.create("overscanX", "ovrscnx",
                                     MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setHidden(true));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_overscanX));

    // Overscan Y
    a_overscanY = numericAttr.create("overscanY", "ovrscny",
                                     MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setHidden(true));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_overscanY));

    // Overscan Inverse
    a_overscanInverse = numericAttr.create("overscanInverse", "ovrscninv",
                                           MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(
        numericAttr.setNiceNameOverride("Uniform Overscan Inverse"));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_overscanInverse));

    // Overscan Inverse X
    a_overscanInverseX = numericAttr.create("overscanInverseX", "ovrscninvx",
                                            MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_overscanInverseX));

    // Overscan Inverse Y
    a_overscanInverseY = numericAttr.create("overscanInverseY", "ovrscninvy",
                                            MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_overscanInverseY));

    // Out Translate X
    a_outTranslateX = numericAttr.create("outTranslateX", "otx",
                                         MFnNumericData::kDouble, 0.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

    // Out Translate Y
    a_outTranslateY = numericAttr.create("outTranslateY", "oty",
                                         MFnNumericData::kDouble, 0.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

    // Out Translate Z
    a_outTranslateZ = numericAttr.create("outTranslateZ", "otz",
                                         MFnNumericData::kDouble, 0.0, &status);
    MMSOLVER_CHECK_MSTATUS(status);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

    // Out Translate (parent of outTranslate* attributes)
    a_outTranslate = compoundAttr.create("outTranslate", "ot", &status);
    MMSOLVER_CHECK_MSTATUS(status);
    compoundAttr.addChild(a_outTranslateX);
    compoundAttr.addChild(a_outTranslateY);
    compoundAttr.addChild(a_outTranslateZ);
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_outTranslate));

    // Out Scale X
    a_outScaleX =
        numericAttr.create("outScaleX", "osx", MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

    // Out Scale Y
    a_outScaleY =
        numericAttr.create("outScaleY", "osy", MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

    // Out Scale Z
    a_outScaleZ = numericAttr.create("outScaleZ", "osz",
                                     MFnNumericData::kDouble, 1.0, &status);
    MMSOLVER_CHECK_MSTATUS(status);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));

    // Out Scale (parent of outScale* attributes)
    a_outScale = compoundAttr.create("outScale", "os", &status);
    MMSOLVER_CHECK_MSTATUS(status);
    compoundAttr.addChild(a_outScaleX);
    compoundAttr.addChild(a_outScaleY);
    compoundAttr.addChild(a_outScaleZ);
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_outScale));

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(a_focalLength);
    inputAttrs.append(a_cameraAperture);
    inputAttrs.append(a_horizontalFilmAperture);
    inputAttrs.append(a_verticalFilmAperture);
    inputAttrs.append(a_filmOffset);
    inputAttrs.append(a_horizontalFilmOffset);
    inputAttrs.append(a_verticalFilmOffset);
    inputAttrs.append(a_overscanMode);
    inputAttrs.append(a_overscan);
    inputAttrs.append(a_overscanX);
    inputAttrs.append(a_overscanY);
    inputAttrs.append(a_overscanInverse);
    inputAttrs.append(a_overscanInverseX);
    inputAttrs.append(a_overscanInverseY);
    inputAttrs.append(a_depth);

    MObjectArray outputAttrs;
    outputAttrs.append(a_outTranslate);
    outputAttrs.append(a_outTranslateX);
    outputAttrs.append(a_outTranslateY);
    outputAttrs.append(a_outTranslateZ);
    outputAttrs.append(a_outScale);
    outputAttrs.append(a_outScaleX);
    outputAttrs.append(a_outScaleY);
    outputAttrs.append(a_outScaleZ);

    MMSOLVER_CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return (MS::kSuccess);
}

}  // namespace mmsolver
