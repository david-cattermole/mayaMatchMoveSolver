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

#include "MMLineIntersectNode.h"

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
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MObjectArray.h>
#include <maya/MPlug.h>
#include <maya/MStreamUtils.h>

// MM Solver
#include <mmcore/mmcamera.h>
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

#include "mmSolver/calibrate/calibrate_common.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

MStatus getLineAttributeValues(MDataBlock &data, MObject &attr_pointAX,
                               MObject &attr_pointAY, MObject &attr_pointBX,
                               MObject &attr_pointBY, mmdata::Line2D &output) {
    MStatus status = MS::kUnknownParameter;

    ///////////////////////////////
    MDataHandle pointAXHandle = data.inputValue(attr_pointAX, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    double ax = pointAXHandle.asDouble();

    MDataHandle pointAYHandle = data.inputValue(attr_pointAY, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    double ay = pointAYHandle.asDouble();

    ///////////////////////////////
    MDataHandle pointBXHandle = data.inputValue(attr_pointBX, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    double bx = pointBXHandle.asDouble();

    MDataHandle pointBYHandle = data.inputValue(attr_pointBY, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    double by = pointBYHandle.asDouble();

    auto a = mmdata::Point2D(ax, ay);
    auto b = mmdata::Point2D(bx, by);
    output = mmdata::Line2D(a, b);
    return MS::kSuccess;
}

MTypeId MMLineIntersectNode::m_id(MM_LINE_INTERSECT_TYPE_ID);

// Input Attributes
MObject MMLineIntersectNode::a_pointA;
MObject MMLineIntersectNode::a_pointAX;
MObject MMLineIntersectNode::a_pointAY;

MObject MMLineIntersectNode::a_pointB;
MObject MMLineIntersectNode::a_pointBX;
MObject MMLineIntersectNode::a_pointBY;

MObject MMLineIntersectNode::a_pointC;
MObject MMLineIntersectNode::a_pointCX;
MObject MMLineIntersectNode::a_pointCY;

MObject MMLineIntersectNode::a_pointD;
MObject MMLineIntersectNode::a_pointDX;
MObject MMLineIntersectNode::a_pointDY;

// Output Attributes
MObject MMLineIntersectNode::a_outVanishingPoint;
MObject MMLineIntersectNode::a_outVanishingPointX;
MObject MMLineIntersectNode::a_outVanishingPointY;

MObject MMLineIntersectNode::a_outCosineAngle;

MMLineIntersectNode::MMLineIntersectNode() {}

MMLineIntersectNode::~MMLineIntersectNode() {}

MString MMLineIntersectNode::nodeName() {
    return MString(MM_LINE_INTERSECT_TYPE_NAME);
}

MStatus MMLineIntersectNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if ((plug == a_outVanishingPoint) || (plug == a_outVanishingPointX) ||
        (plug == a_outVanishingPointY)) {
        // Get Data Handles
        auto lineA = mmdata::Line2D();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(getLineAttributeValues(
            data, a_pointAX, a_pointAY, a_pointBX, a_pointBY, lineA));

        auto lineB = mmdata::Line2D();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(getLineAttributeValues(
            data, a_pointCX, a_pointCY, a_pointDX, a_pointDY, lineB));

        auto linePair = mmdata::LinePair2D(lineA, lineB);

        // If the lines are almost parallel then the lines will not be
        // helpful. We can detect parallel lines if the cosine of the angle
        // is close to 1.0.
        auto cosine_of_angle = mmmath::cosineAngleBetweenLines(linePair);

        // Calculate the input vanishing point
        auto vanishingPoint = mmdata::Point2D();
        auto ok =
            calibrate::calcVanishingPointFromLinePair(linePair, vanishingPoint);
        if (!ok) {
            MStreamUtils::stdErrorStream()
                << "Failed calculateVanishingPointFromLinePair." << '\n';
            status = MS::kFailure;
            return status;
        }

#ifdef DEBUG
        MStreamUtils::stdErrorStream()
            << "outCameraParameters vanishingPoint:"
            << " x=" << vanishingPoint.x_ << " y=" << vanishingPoint.y_ << '\n';
#endif

        // Output Vanishing Point
        MDataHandle outVanishingPointXHandle =
            data.outputValue(a_outVanishingPointX);
        MDataHandle outVanishingPointYHandle =
            data.outputValue(a_outVanishingPointY);
        outVanishingPointXHandle.setDouble(vanishingPoint.x_);
        outVanishingPointYHandle.setDouble(vanishingPoint.y_);
        outVanishingPointXHandle.setClean();
        outVanishingPointYHandle.setClean();

        // Output Cosine Angle
        MDataHandle outCosineAngleHandle = data.outputValue(a_outCosineAngle);
        outCosineAngleHandle.setDouble(cosine_of_angle);
        outCosineAngleHandle.setClean();
    }

    return status;
}

void *MMLineIntersectNode::creator() { return (new MMLineIntersectNode()); }

MStatus MMLineIntersectNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnCompoundAttribute compoundAttr;

    //////////////////////////////////////////////////////////////////////////

    {
        a_pointAX = numericAttr.create("pointAX", "pntax",
                                       MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_pointAY = numericAttr.create("pointAY", "pntay",
                                       MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_pointA = compoundAttr.create("pointA", "pnta", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_pointAX);
        compoundAttr.addChild(a_pointAY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_pointA));
    }

    {
        a_pointBX = numericAttr.create("pointBX", "pntbx",
                                       MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_pointBY = numericAttr.create("pointBY", "pntby",
                                       MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_pointB = compoundAttr.create("pointB", "pntb", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_pointBX);
        compoundAttr.addChild(a_pointBY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_pointB));
    }

    {
        a_pointCX = numericAttr.create("pointCX", "pntcx",
                                       MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_pointCY = numericAttr.create("pointCY", "pntcy",
                                       MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_pointC = compoundAttr.create("pointC", "pntc", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_pointCX);
        compoundAttr.addChild(a_pointCY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_pointC));
    }

    {
        a_pointDX = numericAttr.create("pointDX", "pntdx",
                                       MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_pointDY = numericAttr.create("pointDY", "pntdy",
                                       MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        a_pointD = compoundAttr.create("pointD", "pntd", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_pointDX);
        compoundAttr.addChild(a_pointDY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_pointD));
    }

    //////////////////////////////////////////////////////////////////////////

    // Out Vanishing Point
    {
        a_outVanishingPointX = numericAttr.create("outVanishingPointX", "ovpax",
                                                  MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        a_outVanishingPointY = numericAttr.create("outVanishingPointY", "ovpay",
                                                  MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        a_outVanishingPoint =
            compoundAttr.create("outVanishingPoint", "ovpa", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(a_outVanishingPointX);
        compoundAttr.addChild(a_outVanishingPointY);
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outVanishingPoint));
    }

    // Out Cosine Angle.
    {
        a_outCosineAngle = numericAttr.create("outCosineAngle", "ocsang",
                                              MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(a_outCosineAngle));
    }

    //////////////////////////////////////////////////////////////////////////

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(a_pointA);
    inputAttrs.append(a_pointAX);
    inputAttrs.append(a_pointAY);

    inputAttrs.append(a_pointB);
    inputAttrs.append(a_pointBX);
    inputAttrs.append(a_pointBY);

    inputAttrs.append(a_pointC);
    inputAttrs.append(a_pointCX);
    inputAttrs.append(a_pointCY);

    inputAttrs.append(a_pointD);
    inputAttrs.append(a_pointDX);
    inputAttrs.append(a_pointDY);

    MObjectArray outputAttrs;
    outputAttrs.append(a_outVanishingPoint);
    outputAttrs.append(a_outVanishingPointX);
    outputAttrs.append(a_outVanishingPointY);

    outputAttrs.append(a_outCosineAngle);

    MMSOLVER_CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return MS::kSuccess;
}

}  // namespace mmsolver
