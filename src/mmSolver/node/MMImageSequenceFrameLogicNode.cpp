/*
 * Copyright (C) 2024 David Cattermole.
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
 *
 */

#include "MMImageSequenceFrameLogicNode.h"

// STL
#include <cmath>
#include <cstring>

// Maya
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MObjectArray.h>
#include <maya/MPlug.h>

// MM Solver
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

MTypeId MMImageSequenceFrameLogicNode::m_id(
    MM_IMAGE_SEQUENCE_FRAME_LOGIC_TYPE_ID);

// Input Attributes
MObject MMImageSequenceFrameLogicNode::a_inFrame;
MObject MMImageSequenceFrameLogicNode::a_firstFrame;
MObject MMImageSequenceFrameLogicNode::a_startFrame;
MObject MMImageSequenceFrameLogicNode::a_endFrame;

// Output Attributes
MObject MMImageSequenceFrameLogicNode::a_outFrame;

MMImageSequenceFrameLogicNode::MMImageSequenceFrameLogicNode() {}

MMImageSequenceFrameLogicNode::~MMImageSequenceFrameLogicNode() {}

MString MMImageSequenceFrameLogicNode::nodeName() {
    return MString(MM_IMAGE_SEQUENCE_FRAME_LOGIC_TYPE_NAME);
}

MStatus MMImageSequenceFrameLogicNode::compute(const MPlug &plug,
                                               MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    if (plug == a_outFrame) {
        // Get Data Handles
        MDataHandle inFrameHandle = data.inputValue(a_inFrame);
        MDataHandle firstFrameHandle = data.inputValue(a_firstFrame);
        MDataHandle startFrameHandle = data.inputValue(a_startFrame);
        MDataHandle endFrameHandle = data.inputValue(a_endFrame);

        // Get Values
        double inFrame = inFrameHandle.asDouble();
        double firstFrame = firstFrameHandle.asDouble();
        double startFrame = startFrameHandle.asDouble();
        double endFrame = endFrameHandle.asDouble();

        // Clamp to start and end frames.
        double outFrame = (startFrame - firstFrame) + inFrame;
        if (outFrame < startFrame) {
            outFrame = startFrame;
        } else if (outFrame > endFrame) {
            outFrame = endFrame;
        }

        // Output Frame
        MDataHandle outFrameHandle = data.outputValue(a_outFrame);
        outFrameHandle.setDouble(outFrame);
        outFrameHandle.setClean();

        status = MS::kSuccess;
    }
    return status;
}

void *MMImageSequenceFrameLogicNode::creator() {
    return (new MMImageSequenceFrameLogicNode());
}

MStatus MMImageSequenceFrameLogicNode::initialize() {
    MStatus status;
    MFnNumericAttribute numericAttr;
    MFnEnumAttribute enumAttr;
    MFnCompoundAttribute compoundAttr;

    // In Frame
    a_inFrame =
        numericAttr.create("inFrame", "ifrm", MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_inFrame));

    // Frame First
    a_firstFrame = numericAttr.create("firstFrame", "fstfrm",
                                      MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_firstFrame));

    // Frame Start
    a_startFrame =
        numericAttr.create("startFrame", "stfrm", MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_startFrame));

    // Frame End
    a_endFrame =
        numericAttr.create("endFrame", "edfrm", MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(true));
    CHECK_MSTATUS(numericAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(a_endFrame));

    // Out Frame
    a_outFrame =
        numericAttr.create("outFrame", "ofrm", MFnNumericData::kDouble, 0.0);
    CHECK_MSTATUS(numericAttr.setStorable(false));
    CHECK_MSTATUS(numericAttr.setKeyable(false));
    CHECK_MSTATUS(numericAttr.setReadable(true));
    CHECK_MSTATUS(numericAttr.setWritable(false));
    CHECK_MSTATUS(addAttribute(a_outFrame));

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(a_inFrame);
    inputAttrs.append(a_firstFrame);
    inputAttrs.append(a_startFrame);
    inputAttrs.append(a_endFrame);

    MObjectArray outputAttrs;
    outputAttrs.append(a_outFrame);

    CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return (MS::kSuccess);
}

}  // namespace mmsolver
