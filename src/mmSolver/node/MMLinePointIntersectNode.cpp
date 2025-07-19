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

#include "MMLinePointIntersectNode.h"

// STL
#include <cmath>
#include <cstring>

// Maya
#include <maya/MArrayDataHandle.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnCompoundAttribute.h>
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

MTypeId MMLinePointIntersectNode::m_id(MM_LINE_POINT_INTERSECT_TYPE_ID);

// Input Attributes
MObject MMLinePointIntersectNode::m_inPoint;
MObject MMLinePointIntersectNode::m_inPointX;
MObject MMLinePointIntersectNode::m_inPointY;
MObject MMLinePointIntersectNode::m_inPointZ;
MObject MMLinePointIntersectNode::m_linePointA;
MObject MMLinePointIntersectNode::m_linePointAX;
MObject MMLinePointIntersectNode::m_linePointAY;
MObject MMLinePointIntersectNode::m_linePointAZ;
MObject MMLinePointIntersectNode::m_linePointB;
MObject MMLinePointIntersectNode::m_linePointBX;
MObject MMLinePointIntersectNode::m_linePointBY;
MObject MMLinePointIntersectNode::m_linePointBZ;

// Output Attributes
MObject MMLinePointIntersectNode::m_outPoint;
MObject MMLinePointIntersectNode::m_outPointX;
MObject MMLinePointIntersectNode::m_outPointY;
MObject MMLinePointIntersectNode::m_outPointZ;
MObject MMLinePointIntersectNode::m_outDistance;

MMLinePointIntersectNode::MMLinePointIntersectNode() {}

MMLinePointIntersectNode::~MMLinePointIntersectNode() {}

MString MMLinePointIntersectNode::nodeName() {
    return MString(MM_LINE_POINT_INTERSECT_TYPE_NAME);
}

MStatus MMLinePointIntersectNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    // When 'true', verbose will print out additional details for
    // debugging.
    bool verbose = false;

    if ((plug == m_outPoint) || (plug == m_outPointX) ||
        (plug == m_outPointY) || (plug == m_outPointZ) ||
        (plug == m_outDistance)) {
        // Point
        MDataHandle in_pointXHandle = data.inputValue(m_inPointX, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MDataHandle in_pointYHandle = data.inputValue(m_inPointY, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MDataHandle in_pointZHandle = data.inputValue(m_inPointZ, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double in_pointX = in_pointXHandle.asDouble();
        double in_pointY = in_pointYHandle.asDouble();
        double in_pointZ = in_pointZHandle.asDouble();
        mmsg::Point3 in_point{in_pointX, in_pointY, in_pointZ};
        MMSOLVER_MAYA_VRB("Point: " << in_point.x << ", " << in_point.y << ", "
                                    << in_point.z);

        // Line Point A
        MDataHandle linePointAXHandle = data.inputValue(m_linePointAX, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MDataHandle linePointAYHandle = data.inputValue(m_linePointAY, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MDataHandle linePointAZHandle = data.inputValue(m_linePointAZ, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double linePointAX = linePointAXHandle.asDouble();
        double linePointAY = linePointAYHandle.asDouble();
        double linePointAZ = linePointAZHandle.asDouble();
        mmsg::Point3 line_a{linePointAX, linePointAY, linePointAZ};
        MMSOLVER_MAYA_VRB("Line Point A: " << line_a.x << ", " << line_a.y
                                           << ", " << line_a.z);

        // Line Point B
        MDataHandle linePointBXHandle = data.inputValue(m_linePointBX, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MDataHandle linePointBYHandle = data.inputValue(m_linePointBY, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MDataHandle linePointBZHandle = data.inputValue(m_linePointBZ, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        double linePointBX = linePointBXHandle.asDouble();
        double linePointBY = linePointBYHandle.asDouble();
        double linePointBZ = linePointBZHandle.asDouble();
        mmsg::Point3 line_b{linePointBX, linePointBY, linePointBZ};
        MMSOLVER_MAYA_VRB("Line Point B: " << line_b.x << ", " << line_b.y
                                           << ", " << line_b.z);

        mmdata::Point2D line_point_start(line_a.x, line_a.y, line_a.z);
        mmdata::Point2D line_point_end(line_b.x, line_b.y, line_b.z);
        auto line_distance = mmmath::distance(line_point_start, line_point_end);

        double out_distance = 0.0;
        mmsg::Point3 out_point{0.0, 0.0, 0.0};
        if (line_distance > 0) {
            auto ok =
                line_point_intersection(in_point, line_a, line_b, out_point);
            MMSOLVER_MAYA_VRB("MMLinePointIntersectNode ok: " << ok);
            if (ok) {
                mmdata::Point2D start_point(in_point.x, in_point.y, in_point.z);
                mmdata::Point2D end_point(out_point.x, out_point.y,
                                          out_point.z);
                out_distance = mmmath::distance(start_point, end_point);
            }
        }
        MMSOLVER_MAYA_VRB("Out Point: " << out_point.x << ", " << out_point.y
                                        << ", " << out_point.z);
        MMSOLVER_MAYA_VRB("Out Distance: " << out_distance);

        // Output Points
        MDataHandle outPointXHandle = data.outputValue(m_outPointX);
        MDataHandle outPointYHandle = data.outputValue(m_outPointY);
        MDataHandle outPointZHandle = data.outputValue(m_outPointZ);
        outPointXHandle.setDouble(out_point.x);
        outPointYHandle.setDouble(out_point.y);
        outPointZHandle.setDouble(out_point.z);
        outPointXHandle.setClean();
        outPointYHandle.setClean();
        outPointZHandle.setClean();

        // Output Distance
        MDataHandle outDistanceHandle = data.outputValue(m_outDistance);
        outDistanceHandle.setDouble(out_distance);
        outDistanceHandle.setClean();
    }

    return status;
}

void *MMLinePointIntersectNode::creator() {
    return (new MMLinePointIntersectNode());
}

MStatus MMLinePointIntersectNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnCompoundAttribute compoundAttr;

    //////////////////////////////////////////////////////////////////////////

    // Input Point
    {
        m_inPointX = numericAttr.create("inPointX", "inpntx",
                                        MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        m_inPointY = numericAttr.create("inPointY", "inpnty",
                                        MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        m_inPointZ = numericAttr.create("inPointZ", "inpntz",
                                        MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        m_inPoint = compoundAttr.create("inPoint", "inpnt", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(m_inPointX);
        compoundAttr.addChild(m_inPointY);
        compoundAttr.addChild(m_inPointZ);
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_inPoint));
    }

    // Line Point A
    {
        m_linePointAX = numericAttr.create("linePointAX", "lnpntax",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        m_linePointAY = numericAttr.create("linePointAY", "lnpntay",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        m_linePointAZ = numericAttr.create("linePointAZ", "lnpntaz",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        m_linePointA = compoundAttr.create("linePointA", "lnpnta", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(m_linePointAX);
        compoundAttr.addChild(m_linePointAY);
        compoundAttr.addChild(m_linePointAZ);
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_linePointA));
    }

    // Line Point B
    {
        m_linePointBX = numericAttr.create("linePointBX", "lnpntbx",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        m_linePointBY = numericAttr.create("linePointBY", "lnpntby",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        m_linePointBZ = numericAttr.create("linePointBZ", "lnpntbz",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));

        m_linePointB = compoundAttr.create("linePointB", "lnpntb", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(m_linePointBX);
        compoundAttr.addChild(m_linePointBY);
        compoundAttr.addChild(m_linePointBZ);
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_linePointB));
    }

    //////////////////////////////////////////////////////////////////////////

    // Output Point
    {
        m_outPointX = numericAttr.create("outPointX", "opntx",
                                         MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outPointY = numericAttr.create("outPointY", "opnty",
                                         MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outPointZ = numericAttr.create("outPointZ", "opntz",
                                         MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));

        m_outPoint = compoundAttr.create("outPoint", "opnt", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(m_outPointX);
        compoundAttr.addChild(m_outPointY);
        compoundAttr.addChild(m_outPointZ);
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_outPoint));
    }

    // Output Distance
    {
        m_outDistance = numericAttr.create("outDistance", "odist",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(numericAttr.setWritable(false));
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_outDistance));
    }

    //////////////////////////////////////////////////////////////////////////

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(m_inPoint);
    inputAttrs.append(m_inPointX);
    inputAttrs.append(m_inPointY);
    inputAttrs.append(m_inPointZ);

    inputAttrs.append(m_linePointA);
    inputAttrs.append(m_linePointAX);
    inputAttrs.append(m_linePointAY);
    inputAttrs.append(m_linePointAZ);

    inputAttrs.append(m_linePointB);
    inputAttrs.append(m_linePointBX);
    inputAttrs.append(m_linePointBY);
    inputAttrs.append(m_linePointBZ);

    MObjectArray outputAttrs;
    outputAttrs.append(m_outPoint);
    outputAttrs.append(m_outPointX);
    outputAttrs.append(m_outPointY);
    outputAttrs.append(m_outPointZ);
    outputAttrs.append(m_outDistance);

    MMSOLVER_CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return MS::kSuccess;
}

}  // namespace mmsolver
