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

#include "MMLensEvaluateNode.h"

// STL
#include <cstring>
#include <cmath>

// Maya
#include <maya/MPlug.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MFnPluginData.h>

// MM Solver
#include "MMLensData.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

MTypeId MMLensEvaluateNode::m_id(MM_LENS_EVALUATE_TYPE_ID);

// Input Attributes
MObject MMLensEvaluateNode::a_inLens;
MObject MMLensEvaluateNode::a_inX;
MObject MMLensEvaluateNode::a_inY;

// Output Attributes
MObject MMLensEvaluateNode::a_outX;
MObject MMLensEvaluateNode::a_outY;
MObject MMLensEvaluateNode::a_outHash;


MMLensEvaluateNode::MMLensEvaluateNode() {}

MMLensEvaluateNode::~MMLensEvaluateNode() {}

MString MMLensEvaluateNode::nodeName() {
    return MString("mmLensEvaluate");
}

MStatus MMLensEvaluateNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if ((plug == a_outX) || (plug == a_outY) || (plug == a_outHash)) {
        // Get Input Positions
        MDataHandle inXHandle = data.inputValue(a_inX, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double x = inXHandle.asDouble();

        MDataHandle inYHandle = data.inputValue(a_inY, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double y = inYHandle.asDouble();

        double out_x = x;
        double out_y = y;
        int64_t out_hash = 0;

        // Get Input Lens
        MDataHandle inLensHandle = data.inputValue(a_inLens, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMLensData* inputLensData = (MMLensData*) inLensHandle.asPluginData();
        if (inputLensData != nullptr) {
            // Evaluate the lens distortion, at (x, y)
            std::shared_ptr<LensModel> lensModel = inputLensData->getValue();
            if (lensModel != nullptr) {
                double temp_out_x = out_x;
                double temp_out_y = out_y;
                lensModel->applyModelUndistort(x, y, temp_out_x, temp_out_y);
                if (std::isfinite(temp_out_x)) {
                    out_x = temp_out_x;
                }
                if (std::isfinite(temp_out_y)) {
                    out_y = temp_out_y;
                }

                out_hash = lensModel->hashValue();
            }
        }

        // Output
        MDataHandle outXHandle = data.outputValue(a_outX);
        MDataHandle outYHandle = data.outputValue(a_outY);
        MDataHandle outHashHandle = data.outputValue(a_outHash);
        outXHandle.setDouble(out_x);
        outYHandle.setDouble(out_y);
        outHashHandle.setInt64(out_hash);
        outXHandle.setClean();
        outYHandle.setClean();
        outHashHandle.setClean();
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

    // In X
    a_inX = numericAttr.create(
        "inX", "ix",
        MFnNumericData::kDouble, false);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_inX));

    // In Y
    a_inY = numericAttr.create(
        "inY", "iy",
        MFnNumericData::kDouble, false);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_inY));

    // Out X
    a_outX = numericAttr.create(
        "outX", "ox",
        MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(false));
    CHECK_MSTATUS(numericAttr.setKeyable(false));
    CHECK_MSTATUS(numericAttr.setReadable(true));
    CHECK_MSTATUS(numericAttr.setWritable(false));
    CHECK_MSTATUS(addAttribute(a_outX));

    // Out Y
    a_outY = numericAttr.create(
        "outY", "oy",
        MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(false));
    CHECK_MSTATUS(numericAttr.setKeyable(false));
    CHECK_MSTATUS(numericAttr.setReadable(true));
    CHECK_MSTATUS(numericAttr.setWritable(false));
    CHECK_MSTATUS(addAttribute(a_outY));

    // Out Hash
    a_outHash = numericAttr.create(
            "outHash", "outHash",
            MFnNumericData::kInt64, 0);
    CHECK_MSTATUS(numericAttr.setStorable(false));
    CHECK_MSTATUS(numericAttr.setKeyable(false));
    CHECK_MSTATUS(numericAttr.setReadable(true));
    CHECK_MSTATUS(numericAttr.setWritable(false));
    CHECK_MSTATUS(addAttribute(a_outHash));

    // Attribute Affects
    CHECK_MSTATUS(attributeAffects(a_inX, a_outX));
    CHECK_MSTATUS(attributeAffects(a_inX, a_outY));
    CHECK_MSTATUS(attributeAffects(a_inX, a_outHash));

    CHECK_MSTATUS(attributeAffects(a_inY, a_outX));
    CHECK_MSTATUS(attributeAffects(a_inY, a_outY));
    CHECK_MSTATUS(attributeAffects(a_inY, a_outHash));

    CHECK_MSTATUS(attributeAffects(a_inLens, a_outX));
    CHECK_MSTATUS(attributeAffects(a_inLens, a_outY));
    CHECK_MSTATUS(attributeAffects(a_inLens, a_outHash));

    return MS::kSuccess;
}

} // namespace mmsolver
