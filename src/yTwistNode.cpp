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
 * Lens Distortion Deformer.
 */


#include <nodeTypeIds.h>
#include <yTwistNode.h>


MTypeId yTwistNode::m_id(MM_LENS_DISTORTION_DEFORMER_TYPE_ID);
MObject yTwistNode::a_angle;


yTwistNode::yTwistNode() {}

yTwistNode::~yTwistNode() {}

void* yTwistNode::creator()
{
    return new yTwistNode();
}

MStatus yTwistNode::initialize()
{
    MFnNumericAttribute nAttr;
    a_angle = nAttr.create("angle", "fa", MFnNumericData::kDouble);
        nAttr.setDefault(0.0);
        nAttr.setKeyable(true);
    addAttribute(a_angle);

    attributeAffects(yTwistNode::a_angle, yTwistNode::outputGeom);
    return MS::kSuccess;
}

MString yTwistNode::nodeName() {
    return MString("yTwist");
}

MStatus
yTwistNode::deform(MDataBlock& block,
                   MItGeometry& iter,
                   const MMatrix& /*m*/,
                   unsigned int /*multiIndex*/)
//
// Method: deform
//
// Description:   Deform the point with a yTwist algorithm
//
// Arguments:
//   block		: the datablock of the node
//	 iter		: an iterator for the geometry to be deformed
//   m          : matrix to transform the point into world space
//	 multiIndex : the index of the geometry that we are deforming
//
//
{
    MStatus status = MS::kSuccess;

    // determine the angle of the yTwist
    MDataHandle angleData = block.inputValue(a_angle, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    double magnitude = angleData.asDouble();

    // determine the envelope (this is a global scale factor)
    MDataHandle envData = block.inputValue(envelope, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    float env = envData.asFloat();

    // iterate through each point in the geometry
    //
    for ( ; !iter.isDone(); iter.next()) {
        MPoint pt = iter.position();

        // do the twist
        //
        double ff = magnitude * pt.y * env;
        if (ff != 0.0) {
            double cct = cos(ff);
            double cst = sin(ff);
            double tt = pt.x * cct - pt.z * cst;
            pt.z = pt.x * cst + pt.z * cct;
            pt.x = tt;;
        }

        iter.setPosition(pt);
    }
    return status;
}
