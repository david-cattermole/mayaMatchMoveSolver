/*
 * Copyright (C) 2022 David Cattermole.
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

#include "MMLineBestFitNode.h"

// STL
#include <cmath>
#include <cstring>

// Maya
#include <maya/MArrayDataHandle.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MFnMessageAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MPlug.h>
#include <maya/MStreamUtils.h>

// MM Solver
#include "mmSolver/calibrate/calibrate_common.h"
#include "mmSolver/core/mmcamera.h"
#include "mmSolver/core/mmdata.h"
#include "mmSolver/core/mmmath.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

// MM SceneGraph
#include <mmscenegraph/mmscenegraph.h>

namespace mmsg = mmscenegraph;

namespace mmsolver {

MTypeId MMLineBestFitNode::m_id(MM_LINE_BEST_FIT_TYPE_ID);

// Input Attributes
MObject MMLineBestFitNode::m_transformMatrix;
MObject MMLineBestFitNode::m_parentInverseMatrix;
MObject MMLineBestFitNode::m_lineLength;

// Output Attributes
MObject MMLineBestFitNode::m_outPointA;
MObject MMLineBestFitNode::m_outPointAX;
MObject MMLineBestFitNode::m_outPointAY;

MObject MMLineBestFitNode::m_outPointB;
MObject MMLineBestFitNode::m_outPointBX;
MObject MMLineBestFitNode::m_outPointBY;

MObject MMLineBestFitNode::m_outLine;
MObject MMLineBestFitNode::m_outLineCenterX;
MObject MMLineBestFitNode::m_outLineCenterY;
MObject MMLineBestFitNode::m_outLineSlope;
MObject MMLineBestFitNode::m_outLineAngle;

MMLineBestFitNode::MMLineBestFitNode() {}

MMLineBestFitNode::~MMLineBestFitNode() {}

MString MMLineBestFitNode::nodeName() {
    return MString(MM_LINE_BEST_FIT_TYPE_NAME);
}

MStatus MMLineBestFitNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    // When 'true', verbose will print out additional details for
    // debugging.
    bool verbose = false;

    if ((plug == m_outPointA) || (plug == m_outPointAX) ||
        (plug == m_outPointAY) || (plug == m_outPointB) ||
        (plug == m_outPointBX) || (plug == m_outPointBY) ||
        (plug == m_outLine) || (plug == m_outLineCenterX) ||
        (plug == m_outLineCenterY) || (plug == m_outLineSlope) ||
        (plug == m_outLineAngle)) {
        m_data_x.clear();
        m_data_y.clear();

        // Get Parent Inverse Matrix
        MDataHandle parentInverseMatrixHandle =
            data.inputValue(m_parentInverseMatrix, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix parentInverseMatrix = parentInverseMatrixHandle.asMatrix();

        MArrayDataHandle transformArrayHandle =
            data.inputArrayValue(m_transformMatrix, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        status = transformArrayHandle.jumpToArrayElement(0);
        if (status == MStatus::kSuccess) {
            do {
                MDataHandle transformArrayHandleElement =
                    transformArrayHandle.inputValue(&status);
                CHECK_MSTATUS(status);

                MMatrix transformMatrix =
                    transformArrayHandleElement.asMatrix();

                mmsg::Real x = transformMatrix[3][0];
                mmsg::Real y = transformMatrix[3][1];
                mmsg::Real z = transformMatrix[3][2];

                auto point = MPoint(x, y, z);
                point = point * parentInverseMatrix;

                if (verbose) {
                    uint32_t element_index =
                        transformArrayHandle.elementIndex(&status);
                    CHECK_MSTATUS(status);
                    MMSOLVER_VRB("Point X: " << element_index << " : "
                                             << point.x);
                    MMSOLVER_VRB("Point Y: " << element_index << " : "
                                             << point.y);
                }

                m_data_x.push_back(point.x);
                m_data_y.push_back(point.y);

            } while (transformArrayHandle.next() == MStatus::kSuccess);
        }

        auto point_a = mmdata::Point2D();
        auto point_b = mmdata::Point2D();

        auto line_center_x = 0.0;
        auto line_center_y = 0.0;
        auto line_slope = 0.0;
        auto line_angle = 0.0;

        MDataHandle lineLengthHandle = data.inputValue(m_lineLength, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        auto line_length = lineLengthHandle.asDouble() * 0.5;

        if (m_data_x.size() > 2) {
            rust::Slice<const mmsg::Real> x_slice{m_data_x.data(),
                                                  m_data_x.size()};
            rust::Slice<const mmsg::Real> y_slice{m_data_y.data(),
                                                  m_data_y.size()};
            auto ok = mmsg::fit_line_to_points_type2(
                x_slice, y_slice, line_center_x, line_center_y, line_slope);

            if (!ok) {
                MMSOLVER_WRN("Failed to fit a line to data points; Node Name="
                             << MPxNode::name().asChar());
                status = MS::kFailure;
                return status;
            }

            auto line_angle_radian = std::atan(-line_slope);
            line_angle = line_angle_radian * RADIANS_TO_DEGREES;
            MMSOLVER_VRB("MM Scene Graph: Center X: " << line_center_x);
            MMSOLVER_VRB("MM Scene Graph: Center Y: " << line_center_y);
            MMSOLVER_VRB("MM Scene Graph: Slope  : " << line_slope);
            MMSOLVER_VRB("MM Scene Graph: Angle  : " << line_angle);

            // Convert line center point and slope to 2 points to make
            // up a line we can draw between.
            point_a.x_ =
                line_center_x + (std::sin(-line_angle_radian) * line_length);
            point_a.y_ =
                line_center_y + (std::cos(-line_angle_radian) * line_length);
            point_b.x_ =
                line_center_x - (std::sin(-line_angle_radian) * line_length);
            point_b.y_ =
                line_center_y - (std::cos(-line_angle_radian) * line_length);
        }

        // Output Points
        MDataHandle outPointAXHandle = data.outputValue(m_outPointAX);
        MDataHandle outPointAYHandle = data.outputValue(m_outPointAY);
        outPointAXHandle.setDouble(point_a.x_);
        outPointAYHandle.setDouble(point_a.y_);
        outPointAXHandle.setClean();
        outPointAYHandle.setClean();

        MDataHandle outPointBXHandle = data.outputValue(m_outPointBX);
        MDataHandle outPointBYHandle = data.outputValue(m_outPointBY);
        outPointBXHandle.setDouble(point_b.x_);
        outPointBYHandle.setDouble(point_b.y_);
        outPointBXHandle.setClean();
        outPointBYHandle.setClean();

        // Output Line
        MDataHandle outLineCenterXHandle = data.outputValue(m_outLineCenterX);
        MDataHandle outLineCenterYHandle = data.outputValue(m_outLineCenterY);
        MDataHandle outLineSlopeHandle = data.outputValue(m_outLineSlope);
        MDataHandle outLineAngleHandle = data.outputValue(m_outLineAngle);
        outLineCenterXHandle.setDouble(line_center_x);
        outLineCenterYHandle.setDouble(line_center_y);
        outLineSlopeHandle.setDouble(line_slope);
        outLineAngleHandle.setDouble(line_angle);
        outLineCenterXHandle.setClean();
        outLineCenterYHandle.setClean();
        outLineSlopeHandle.setClean();
        outLineAngleHandle.setClean();
    }

    return status;
}

void *MMLineBestFitNode::creator() { return (new MMLineBestFitNode()); }

MStatus MMLineBestFitNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnCompoundAttribute compoundAttr;
    MFnMatrixAttribute matrixAttr;
    MFnMessageAttribute msgAttr;

    //////////////////////////////////////////////////////////////////////////

    {
        // (World-space) Transform Matrices.
        m_transformMatrix = matrixAttr.create(
            "transformMatrix", "tfmmtx", MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(true));
        CHECK_MSTATUS(matrixAttr.setConnectable(true));
        CHECK_MSTATUS(matrixAttr.setArray(true));
        CHECK_MSTATUS(matrixAttr.setDisconnectBehavior(
            MFnAttribute::DisconnectBehavior::kDelete));
        CHECK_MSTATUS(addAttribute(m_transformMatrix));
    }

    // Parent Inverse Matrix
    //
    // Used to Move the 'm_transformMatrix' world-space matrices into
    // local space.
    {
        m_parentInverseMatrix =
            matrixAttr.create("parentInverseMatrix", "pinvm",
                              MFnMatrixAttribute::kDouble, &status);
        CHECK_MSTATUS(status);
        CHECK_MSTATUS(matrixAttr.setStorable(true));
        CHECK_MSTATUS(matrixAttr.setConnectable(true));
        CHECK_MSTATUS(addAttribute(m_parentInverseMatrix));
    }

    // Line Length
    {
        m_lineLength = numericAttr.create("lineLength", "lnlgth",
                                          MFnNumericData::kDouble, 1.0);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setConnectable(true));
        CHECK_MSTATUS(addAttribute(m_lineLength));
    }

    //////////////////////////////////////////////////////////////////////////

    // Out Line Point A
    {
        m_outPointAX = numericAttr.create("outPointAX", "opax",
                                          MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outPointAY = numericAttr.create("outPointAY", "opay",
                                          MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outPointA = compoundAttr.create("outPointA", "opa", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(m_outPointAX);
        compoundAttr.addChild(m_outPointAY);
        CHECK_MSTATUS(addAttribute(m_outPointA));
    }

    // Out Line Point B
    {
        m_outPointBX = numericAttr.create("outPointBX", "opbx",
                                          MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outPointBY = numericAttr.create("outPointBY", "opby",
                                          MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outPointB = compoundAttr.create("outPointB", "opb", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(m_outPointBX);
        compoundAttr.addChild(m_outPointBY);
        CHECK_MSTATUS(addAttribute(m_outPointB));
    }

    //////////////////////////////////////////////////////////////////////////

    {
        // Out Line Center X
        m_outLineCenterX = numericAttr.create("outLineX", "olncx",
                                              MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Line Center Y
        m_outLineCenterY = numericAttr.create("outLineY", "olncy",
                                              MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Line Slope
        m_outLineSlope = numericAttr.create("outLineSlope", "olnslp",
                                            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Line Angle
        m_outLineAngle = numericAttr.create("outLineAngle", "olnagl",
                                            MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Coord (parent of outLine* attributes)
        m_outLine = compoundAttr.create("outLine", "oln", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(m_outLineCenterX);
        compoundAttr.addChild(m_outLineCenterY);
        compoundAttr.addChild(m_outLineSlope);
        compoundAttr.addChild(m_outLineAngle);
        CHECK_MSTATUS(addAttribute(m_outLine));
    }

    //////////////////////////////////////////////////////////////////////////

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(m_transformMatrix);
    inputAttrs.append(m_parentInverseMatrix);
    inputAttrs.append(m_lineLength);

    MObjectArray outputAttrs;
    outputAttrs.append(m_outPointA);
    outputAttrs.append(m_outPointAX);
    outputAttrs.append(m_outPointAY);

    outputAttrs.append(m_outPointB);
    outputAttrs.append(m_outPointBX);
    outputAttrs.append(m_outPointBY);

    outputAttrs.append(m_outLine);
    outputAttrs.append(m_outLineCenterX);
    outputAttrs.append(m_outLineCenterY);
    outputAttrs.append(m_outLineSlope);
    outputAttrs.append(m_outLineAngle);

    CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return MS::kSuccess;
}

}  // namespace mmsolver
