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
 *
 * To create this node using MEL, select deformable objects and run:
 *
 *   deformer -type mmLensDeformer
 *
 */


#include <maya/MFnTypedAttribute.h>

#include <nodeTypeIds.h>

#include <MMLensData.h>
#include <MMLensDeformerNode.h>


MTypeId MMLensDeformerNode::m_id(MM_LENS_DEFORMER_TYPE_ID);

MObject MMLensDeformerNode::a_inLens;


MMLensDeformerNode::MMLensDeformerNode() {}

MMLensDeformerNode::~MMLensDeformerNode() {}

void* MMLensDeformerNode::creator() {
    return new MMLensDeformerNode();
}

MStatus MMLensDeformerNode::initialize() {
    MFnTypedAttribute typedAttr;

    // In Lens
    MTypeId data_type_id(MM_LENS_DATA_TYPE_ID);
    a_inLens = typedAttr.create(
        "inLens", "ilns",
        data_type_id);
    CHECK_MSTATUS(typedAttr.setStorable(false));
    CHECK_MSTATUS(typedAttr.setKeyable(false));
    CHECK_MSTATUS(typedAttr.setReadable(true));
    CHECK_MSTATUS(typedAttr.setWritable(true));
    CHECK_MSTATUS(addAttribute(a_inLens));

    attributeAffects(MMLensDeformerNode::a_inLens, MMLensDeformerNode::outputGeom);
    return MS::kSuccess;
}

MString MMLensDeformerNode::nodeName() {
    return MString("mmLensDeformer");
}

// Linear interpolation function, aka 'mix' function
inline
double lerp(double a, double b, double x) {
    return ((1-x) * a) + (x * b);
}

MStatus
MMLensDeformerNode::deform(MDataBlock& data,
                           MItGeometry& iter,
                           const MMatrix& /*m*/,
                           unsigned int /*multiIndex*/) {
//
// Description:   Deform the point with a MMLensDeformer algorithm
//
// Arguments:
//   data		: the datablock of the node
//	 iter		: an iterator for the geometry to be deformed
//   m          : matrix to transform the point into world space
//	 multiIndex : the index of the geometry that we are deforming
//
    MStatus status = MS::kSuccess;

    // Query the envelope (the global multiplier factor for the
    // deformer)
    MDataHandle envData = data.inputValue(envelope, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    float env = envData.asFloat();
    if (env <= 0.0) {
        return status;
    }

    // Get Input Lens
    MDataHandle inLensHandle = data.inputValue(a_inLens, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    MMLensData* inputLensData = (MMLensData*) inLensHandle.asPluginData();
    if (inputLensData != NULL) {
        // Get the underlying lens model.
        LensModel* lensModel = (LensModel*) inputLensData->getValue();

        // Deform each point on the input geometry.
        for ( ; !iter.isDone(); iter.next()) {
            MPoint pt = iter.position();

            // Evaluate the lens distortion at (pt.x, pt.y).
            double out_x = pt.x;
            double out_y = pt.y;
            if (lensModel != NULL) {
                lensModel->applyModel(pt.x, pt.y, out_x, out_y);
            }
            pt.x = lerp(pt.x, out_x, env);
            pt.y = lerp(pt.y, out_y, env);

            iter.setPosition(pt);
        }
    }
    return status;
}
