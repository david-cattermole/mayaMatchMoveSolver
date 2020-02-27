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
 * Define a lens. The lens is a simple brownian model.
 */

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

#include <utilities/debugUtils.h>
#include <utilities/numberUtils.h>

#include <cstring>
#include <cmath>

#include <nodeTypeIds.h>

#include <core/lensModelBasic.h>
#include <MMLensData.h>
#include <MMLensBasicNode.h>


MTypeId MMLensBasicNode::m_id(MM_LENS_BASIC_TYPE_ID);

// Input Attributes
MObject MMLensBasicNode::a_inLens;
MObject MMLensBasicNode::a_k1;
MObject MMLensBasicNode::a_k2;

// Output Attributes
MObject MMLensBasicNode::a_outLens;


MMLensBasicNode::MMLensBasicNode() {}

MMLensBasicNode::~MMLensBasicNode() {}

MString MMLensBasicNode::nodeName() {
    return MString("mmLensBasic");
}

MStatus MMLensBasicNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if (plug == a_outLens) {
        // K1
        MDataHandle k1Handle = data.inputValue(a_k1, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double k1 = k1Handle.asDouble();

        // K2
        MDataHandle k2Handle = data.inputValue(a_k2, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        double k2 = k2Handle.asDouble();

        // Create initial plug-in data structure. We don't need to
        // 'new' the data type directly.
        MFnPluginData fnPluginData;
        MTypeId data_type_id(MM_LENS_DATA_TYPE_ID);
        fnPluginData.create(data_type_id, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Get Input Lens
        MDataHandle inLensHandle = data.inputValue(a_inLens, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMLensData* inputLensData = (MMLensData*) inLensHandle.asPluginData();
        LensModel* inputLensModel = NULL;
        if (inputLensData != NULL) {
            inputLensModel = (LensModel*) inputLensData->getValue();
        }

        // Create a lens distortion function to be passed to the
        // MMLensData.
        LensModelBasic* newLensModel = new LensModelBasic();
        // Connect the input lens to the newly created lens object.
        newLensModel->setInputLensModel(inputLensModel);
        newLensModel->setK1(k1);
        newLensModel->setK2(k2);

        // Output Lens
        MDataHandle outLensHandle = data.outputValue(a_outLens);
        MMLensData* newLensData = (MMLensData*) fnPluginData.data(&status);

        // Note: MMLensData::setValue takes ownership of the lens
        // model.
        newLensData->setValue(newLensModel);

        outLensHandle.setMPxData(newLensData);
        outLensHandle.setClean();

        status = MS::kSuccess;
    }

    return status;
}

void *MMLensBasicNode::creator() {
    return (new MMLensBasicNode());
}

MStatus MMLensBasicNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnTypedAttribute typedAttr;

    // K1
    a_k1 = numericAttr.create(
        "k1", "k1",
        MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_k1));

    // K2
    a_k2 = numericAttr.create(
        "k2", "k2",
        MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_k2));

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

    // Out Lens
    a_outLens = typedAttr.create(
        "outLens", "olns",
        data_type_id);
    CHECK_MSTATUS(typedAttr.setStorable(false));
    CHECK_MSTATUS(typedAttr.setKeyable(false));
    CHECK_MSTATUS(typedAttr.setReadable(true));
    CHECK_MSTATUS(typedAttr.setWritable(false));
    CHECK_MSTATUS(addAttribute(a_outLens));

    // Attribute Affects
    CHECK_MSTATUS(attributeAffects(a_k1, a_outLens));
    CHECK_MSTATUS(attributeAffects(a_k2, a_outLens));
    CHECK_MSTATUS(attributeAffects(a_inLens, a_outLens));

    return MS::kSuccess;
}
