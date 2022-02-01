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

// Do not define 'min' and 'max' macros on MS Windows (with MSVC),
// added to fix errors with LDPK.
#define NOMINMAX

#include "mmSolver/MMLensModel3deClassicNode.h"

// STL
#include <cstring>
#include <cmath>
#include <algorithm>

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
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/lens/lens_model_3de_classic.h"
#include "mmSolver/MMLensData.h"

MTypeId MMLensModel3deClassicNode::m_id(MM_LENS_MODEL_3DE_CLASSIC_TYPE_ID);

// Input Attributes
MObject MMLensModel3deClassicNode::a_inLens;
MObject MMLensModel3deClassicNode::a_enable;
MObject MMLensModel3deClassicNode::a_distortion;
MObject MMLensModel3deClassicNode::a_anamorphicSqueeze;
MObject MMLensModel3deClassicNode::a_curvatureX;
MObject MMLensModel3deClassicNode::a_curvatureY;
MObject MMLensModel3deClassicNode::a_quarticDistortion;

// Output Attributes
MObject MMLensModel3deClassicNode::a_outLens;


MMLensModel3deClassicNode::MMLensModel3deClassicNode() {}

MMLensModel3deClassicNode::~MMLensModel3deClassicNode() {}

MString MMLensModel3deClassicNode::nodeName() {
    return MString("mmLensModel3deClassic");
}

MStatus MMLensModel3deClassicNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if (plug == a_outLens) {
        // Enable Attribute toggle
        MDataHandle enableHandle = data.inputValue(a_enable, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        bool enable = enableHandle.asBool();

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
        LensModel* inputLensModel = nullptr;
        if (inputLensData != nullptr) {
            inputLensModel = (LensModel*) inputLensData->getValue();
        }

        // Output Lens
        MDataHandle outLensHandle = data.outputValue(a_outLens);
        MMLensData* newLensData = (MMLensData*) fnPluginData.data(&status);
        if (enable) {

            // Distortion Attribute
            MDataHandle distortionHandle = data.inputValue(a_distortion, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            double distortion = distortionHandle.asDouble();

            // Anamorphic Squeeze Attribute
            MDataHandle anamorphicSqueezeHandle =
                    data.inputValue(a_anamorphicSqueeze, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            double anamorphicSqueeze = anamorphicSqueezeHandle.asDouble();

            // Curvature X Attribute
            MDataHandle curvatureXHandle = data.inputValue(a_curvatureX, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            double curvatureX = curvatureXHandle.asDouble();

            // Curvature Y Attribute
            MDataHandle curvatureYHandle = data.inputValue(a_curvatureY, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            double curvatureY = curvatureYHandle.asDouble();

            // Quartic Distortion Attribute
            MDataHandle k2Handle = data.inputValue(a_quarticDistortion, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            double quarticDistortion = k2Handle.asDouble();

            // Create a lens distortion function to be passed to the
            // MMLensData.
            LensModel3deClassic* newLensModel = new LensModel3deClassic();
            // Connect the input lens to the newly created lens object.
            newLensModel->setInputLensModel(inputLensModel);
            newLensModel->setDistortion(distortion);
            newLensModel->setAnamorphicSqueeze(anamorphicSqueeze);
            newLensModel->setCurvatureX(curvatureX);
            newLensModel->setCurvatureY(curvatureY);
            newLensModel->setQuarticDistortion(quarticDistortion);

            newLensData->setValue(newLensModel);
        } else {
            newLensData->setValue(nullptr);
        }
        outLensHandle.setMPxData(newLensData);
        outLensHandle.setClean();
        status = MS::kSuccess;
    }

    return status;
}

void *MMLensModel3deClassicNode::creator() {
    return (new MMLensModel3deClassicNode());
}

MStatus MMLensModel3deClassicNode::initialize() {
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

    // Enable
    a_enable = numericAttr.create(
            "enable", "enb",
            MFnNumericData::kBoolean, true);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_enable));

    // Distortion
    a_distortion = numericAttr.create(
            "distortion", "distortion",
            MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_distortion));

    // Anamorphic Squeeze
    a_anamorphicSqueeze = numericAttr.create(
        "anamorphicSqueeze", "anamorphicSqueeze",
        MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(numericAttr.setMin(0.0));
    CHECK_MSTATUS(numericAttr.setSoftMax(2.0));
    CHECK_MSTATUS(addAttribute(a_anamorphicSqueeze));

    // Curvature
    a_curvatureX = numericAttr.create(
            "curvatureX", "curvatureX",
            MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_curvatureX));

    // Curvature
    a_curvatureY = numericAttr.create(
            "curvatureY", "curvatureY",
            MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_curvatureY));

    // Quartic Distortion
    a_quarticDistortion = numericAttr.create(
            "quarticDistortion", "quarticDistortion",
            MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_quarticDistortion));

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
    CHECK_MSTATUS(attributeAffects(a_distortion, a_outLens));
    CHECK_MSTATUS(attributeAffects(a_anamorphicSqueeze, a_outLens));
    CHECK_MSTATUS(attributeAffects(a_curvatureX, a_outLens));
    CHECK_MSTATUS(attributeAffects(a_curvatureY, a_outLens));
    CHECK_MSTATUS(attributeAffects(a_quarticDistortion, a_outLens));
    CHECK_MSTATUS(attributeAffects(a_enable, a_outLens));
    CHECK_MSTATUS(attributeAffects(a_inLens, a_outLens));

    return MS::kSuccess;
}
