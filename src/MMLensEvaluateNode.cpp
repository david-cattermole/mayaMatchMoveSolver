/*
 * Copyright (C) 2020 David Cattermole.
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
 * Evaluate a lens distortion node to compute new coordinates.
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

#include <MMLensEvaluateNode.h>


MTypeId MMLensEvaluateNode::m_id(MM_LENS_EVALUATE_TYPE_ID);

// Input Attributes
MObject MMLensEvaluateNode::a_inPointX;
MObject MMLensEvaluateNode::a_inPointY;
MObject MMLensEvaluateNode::a_inPointZ;

// Output Attributes
MObject MMLensEvaluateNode::a_outPoint;
MObject MMLensEvaluateNode::a_outPointX;
MObject MMLensEvaluateNode::a_outPointY;
MObject MMLensEvaluateNode::a_outPointZ;


MMLensEvaluateNode::MMLensEvaluateNode() {}

MMLensEvaluateNode::~MMLensEvaluateNode() {}

MString MMLensEvaluateNode::nodeName() {
    return MString("mmLensEvaluate");
}

MStatus MMLensEvaluateNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if ((plug == a_outPoint)
        || (plug == a_outPointX)
        || (plug == a_outPointY)
        || (plug == a_outPointZ)) {
        // Get Data Handles
        MDataHandle inPointXHandle = data.inputValue(
            a_inPointX, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double inPointX = inPointXHandle.asBool();

        MDataHandle inPointYHandle = data.inputValue(
            a_inPointY, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double inPointY = inPointYHandle.asBool();

        MDataHandle inPointZHandle = data.inputValue(
            a_inPointZ, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double inPointZ = inPointZHandle.asBool();

        // TODO: Query the lens distortion.
        double outPointX = 0.5;
        double outPointY = 0.5;
        double outPointZ = 0.5;

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

        status = MS::kSuccess;
    }

    return status;
}

void *MMLensEvaluateNode::creator() {
    return (new MMLensEvaluateNode());
}

MStatus MMLensEvaluateNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnEnumAttribute enumAttr;
    MFnMatrixAttribute matrixAttr;
    MFnCompoundAttribute compoundAttr;

    // TODO: Create a "lens model" attribute.

    {
        // In Point X
        a_inPointX = numericAttr.create(
                "inPointX", "ipx",
                MFnNumericData::kDouble, false);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_inPointX));

        // In Point Y
        a_inPointY = numericAttr.create(
                "inPointY", "ipy",
                MFnNumericData::kDouble, false);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_inPointY));

        // In Point Z
        a_inPointZ = numericAttr.create(
                "inPointZ", "ipz",
                MFnNumericData::kDouble, false);
        CHECK_MSTATUS(numericAttr.setStorable(true));
        CHECK_MSTATUS(numericAttr.setKeyable(true));
        CHECK_MSTATUS(addAttribute(a_inPointZ));
    }

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

    // Attribute Affects
    CHECK_MSTATUS(attributeAffects(a_inPointX, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_inPointX, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_inPointX, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_inPointX, a_outPointZ));

    CHECK_MSTATUS(attributeAffects(a_inPointY, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_inPointY, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_inPointY, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_inPointY, a_outPointZ));

    CHECK_MSTATUS(attributeAffects(a_inPointZ, a_outPoint));
    CHECK_MSTATUS(attributeAffects(a_inPointZ, a_outPointX));
    CHECK_MSTATUS(attributeAffects(a_inPointZ, a_outPointY));
    CHECK_MSTATUS(attributeAffects(a_inPointZ, a_outPointZ));

    return MS::kSuccess;
}
