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
 * A simple lens to enable or disable a lens hierarchy.
 */

#include "MMLensModelToggleNode.h"

// STL
#include <cmath>
#include <cstring>

// Maya
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnPluginData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>

// MM Solver
#include <mmlens/lens_model.h>

#include "MMLensData.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

MTypeId MMLensModelToggleNode::m_id(MM_LENS_MODEL_TOGGLE_TYPE_ID);

// Input Attributes
MObject MMLensModelToggleNode::a_inLens;
MObject MMLensModelToggleNode::a_enable;

// Output Attributes
MObject MMLensModelToggleNode::a_outLens;

MMLensModelToggleNode::MMLensModelToggleNode() {}

MMLensModelToggleNode::~MMLensModelToggleNode() {}

MString MMLensModelToggleNode::nodeName() {
    return MString("mmLensModelToggle");
}

MStatus MMLensModelToggleNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if (plug == a_outLens) {
        // Enable Attribute toggle
        MDataHandle enableHandle = data.inputValue(a_enable, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        bool enable = enableHandle.asBool();

        // Create initial plug-in data structure. We don't need to
        // 'new' the data type directly.
        MFnPluginData fnPluginData;
        MTypeId data_type_id(MM_LENS_DATA_TYPE_ID);
        fnPluginData.create(data_type_id, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        // Get Input Lens
        MDataHandle inLensHandle = data.inputValue(a_inLens, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        MMLensData *inputLensData = (MMLensData *)inLensHandle.asPluginData();
        std::shared_ptr<mmlens::LensModel> inputLensModel;
        if (inputLensData != nullptr) {
            inputLensModel = inputLensData->getValue();
        }

        // Output Lens
        MDataHandle outLensHandle = data.outputValue(a_outLens);
        MMLensData *newLensData = (MMLensData *)fnPluginData.data(&status);
        if (enable) {
            newLensData->setValue(inputLensModel);
        } else {
            newLensData->setValue(nullptr);
        }
        outLensHandle.setMPxData(newLensData);
        outLensHandle.setClean();
        status = MS::kSuccess;
    }

    return status;
}

void *MMLensModelToggleNode::creator() { return (new MMLensModelToggleNode()); }

MStatus MMLensModelToggleNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnTypedAttribute typedAttr;

    // In Lens
    MTypeId data_type_id(MM_LENS_DATA_TYPE_ID);
    a_inLens = typedAttr.create("inLens", "ilns", data_type_id);
    MMSOLVER_CHECK_MSTATUS(typedAttr.setStorable(false));
    MMSOLVER_CHECK_MSTATUS(typedAttr.setKeyable(false));
    MMSOLVER_CHECK_MSTATUS(typedAttr.setReadable(true));
    MMSOLVER_CHECK_MSTATUS(typedAttr.setWritable(true));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_inLens));

    // Enable
    a_enable =
        numericAttr.create("enable", "enb", MFnNumericData::kBoolean, true);
    MMSOLVER_CHECK_MSTATUS(numericAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(numericAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_enable));

    // Out Lens
    a_outLens = typedAttr.create("outLens", "olns", data_type_id);
    MMSOLVER_CHECK_MSTATUS(typedAttr.setStorable(false));
    MMSOLVER_CHECK_MSTATUS(typedAttr.setKeyable(false));
    MMSOLVER_CHECK_MSTATUS(typedAttr.setReadable(true));
    MMSOLVER_CHECK_MSTATUS(typedAttr.setWritable(false));
    MMSOLVER_CHECK_MSTATUS(addAttribute(a_outLens));

    // Attribute Affects
    MMSOLVER_CHECK_MSTATUS(attributeAffects(a_enable, a_outLens));
    MMSOLVER_CHECK_MSTATUS(attributeAffects(a_inLens, a_outLens));

    return MS::kSuccess;
}

}  // namespace mmsolver
