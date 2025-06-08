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
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MPlug.h>
#include <maya/MStreamUtils.h>

// MM Solver
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/node/node_line_utils.h"
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
MObject MMLineBestFitNode::m_outLinePointA;
MObject MMLineBestFitNode::m_outLinePointAX;
MObject MMLineBestFitNode::m_outLinePointAY;

MObject MMLineBestFitNode::m_outLinePointB;
MObject MMLineBestFitNode::m_outLinePointBX;
MObject MMLineBestFitNode::m_outLinePointBY;

MObject MMLineBestFitNode::m_outLine;
MObject MMLineBestFitNode::m_outLineCenterX;
MObject MMLineBestFitNode::m_outLineCenterY;
MObject MMLineBestFitNode::m_outLineDirX;
MObject MMLineBestFitNode::m_outLineDirY;
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

    if ((plug == m_outLinePointA) || (plug == m_outLinePointAX) ||
        (plug == m_outLinePointAY) || (plug == m_outLinePointB) ||
        (plug == m_outLinePointBX) || (plug == m_outLinePointBY) ||
        (plug == m_outLine) || (plug == m_outLineCenterX) ||
        (plug == m_outLineCenterY) || (plug == m_outLineDirX) ||
        (plug == m_outLineDirY) || (plug == m_outLineSlope) ||
        (plug == m_outLineAngle)) {
        m_point_data_x.clear();
        m_point_data_y.clear();

        // Get Parent Inverse Matrix
        MDataHandle parentInverseMatrixHandle =
            data.inputValue(m_parentInverseMatrix, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMatrix parentInverseMatrix = parentInverseMatrixHandle.asMatrix();

        MArrayDataHandle transformArrayHandle =
            data.inputArrayValue(m_transformMatrix, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Get Transform Positions
        status =
            query_line_point_data(parentInverseMatrix, transformArrayHandle,
                                  m_point_data_x, m_point_data_y, verbose);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        MDataHandle lineLengthHandle = data.inputValue(m_lineLength, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        auto line_length = lineLengthHandle.asDouble() * 0.5;

        auto line_center = mmdata::Point2D();
        auto line_slope = 0.0;
        auto line_angle = 0.0;
        auto line_dir = mmdata::Vector2D(0.0, 1.0);
        auto line_point_a = mmdata::Point2D();
        auto line_point_b = mmdata::Point2D();

        status =
            fit_line_to_points(line_length, m_point_data_x, m_point_data_y,
                               line_center, line_slope, line_angle, line_dir,
                               line_point_a, line_point_b, verbose);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Output Points
        MDataHandle outLinePointAXHandle = data.outputValue(m_outLinePointAX);
        MDataHandle outLinePointAYHandle = data.outputValue(m_outLinePointAY);
        outLinePointAXHandle.setDouble(line_point_a.x_);
        outLinePointAYHandle.setDouble(line_point_a.y_);
        outLinePointAXHandle.setClean();
        outLinePointAYHandle.setClean();

        MDataHandle outLinePointBXHandle = data.outputValue(m_outLinePointBX);
        MDataHandle outLinePointBYHandle = data.outputValue(m_outLinePointBY);
        outLinePointBXHandle.setDouble(line_point_b.x_);
        outLinePointBYHandle.setDouble(line_point_b.y_);
        outLinePointBXHandle.setClean();
        outLinePointBYHandle.setClean();

        // Output Line
        MDataHandle outLineCenterXHandle = data.outputValue(m_outLineCenterX);
        MDataHandle outLineCenterYHandle = data.outputValue(m_outLineCenterY);
        MDataHandle outLineDirXHandle = data.outputValue(m_outLineDirX);
        MDataHandle outLineDirYHandle = data.outputValue(m_outLineDirY);
        MDataHandle outLineSlopeHandle = data.outputValue(m_outLineSlope);
        MDataHandle outLineAngleHandle = data.outputValue(m_outLineAngle);
        outLineCenterXHandle.setDouble(line_center.x_);
        outLineCenterYHandle.setDouble(line_center.y_);
        outLineDirXHandle.setDouble(line_dir.x_);
        outLineDirYHandle.setDouble(line_dir.y_);
        outLineSlopeHandle.setDouble(line_slope);
        outLineAngleHandle.setDouble(line_angle);
        outLineCenterXHandle.setClean();
        outLineCenterYHandle.setClean();
        outLineDirXHandle.setClean();
        outLineDirYHandle.setClean();
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
        m_outLinePointAX = numericAttr.create("outLinePointAX", "opax",
                                              MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outLinePointAY = numericAttr.create("outLinePointAY", "opay",
                                              MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outLinePointA = compoundAttr.create("outLinePointA", "opa", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(m_outLinePointAX);
        compoundAttr.addChild(m_outLinePointAY);
        CHECK_MSTATUS(addAttribute(m_outLinePointA));
    }

    // Out Line Point B
    {
        m_outLinePointBX = numericAttr.create("outLinePointBX", "opbx",
                                              MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outLinePointBY = numericAttr.create("outLinePointBY", "opby",
                                              MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outLinePointB = compoundAttr.create("outLinePointB", "opb", &status);
        CHECK_MSTATUS(status);
        compoundAttr.addChild(m_outLinePointBX);
        compoundAttr.addChild(m_outLinePointBY);
        CHECK_MSTATUS(addAttribute(m_outLinePointB));
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

        // Out Line Direction X
        m_outLineDirX = numericAttr.create("outLineDirX", "olndrx",
                                           MFnNumericData::kDouble, 0.0);
        CHECK_MSTATUS(numericAttr.setStorable(false));
        CHECK_MSTATUS(numericAttr.setKeyable(false));
        CHECK_MSTATUS(numericAttr.setReadable(true));
        CHECK_MSTATUS(numericAttr.setWritable(false));

        // Out Line Direction Y
        m_outLineDirY = numericAttr.create("outLineDirY", "olndry",
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
        compoundAttr.addChild(m_outLineDirX);
        compoundAttr.addChild(m_outLineDirY);
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
    outputAttrs.append(m_outLine);
    outputAttrs.append(m_outLinePointA);
    outputAttrs.append(m_outLinePointAX);
    outputAttrs.append(m_outLinePointAY);
    outputAttrs.append(m_outLinePointB);
    outputAttrs.append(m_outLinePointBX);
    outputAttrs.append(m_outLinePointBY);
    outputAttrs.append(m_outLineCenterX);
    outputAttrs.append(m_outLineCenterY);
    outputAttrs.append(m_outLineDirX);
    outputAttrs.append(m_outLineDirY);
    outputAttrs.append(m_outLineSlope);
    outputAttrs.append(m_outLineAngle);

    CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return MS::kSuccess;
}

}  // namespace mmsolver
