/*
 * Copyright (C) 2018, 2019, 2020 David Cattermole.
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
 * A transform node that can have translate values offset with lens
 * distortion models.
 */

#include "mmSolver/MMMarkerTransformNode.h"

// Maya
#include <maya/MTypeId.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnPluginData.h>
#include <maya/MPxTransformationMatrix.h>
#include <maya/MGlobal.h>

// MM Solver
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/lens/lens_model.h"
#include "mmSolver/MMLensData.h"

MTypeId MMMarkerTransformNode::m_id(MM_MARKER_TRANSFORM_TYPE_ID);

// Input Attributes
MObject MMMarkerTransformNode::a_inLens;

MString MMMarkerTransformNode::nodeName() {
    return MString("mmMarkerTransform");
}

MMMarkerTransformNode::MMMarkerTransformNode() : MPxTransform() {}

#if MAYA_API_VERSION < 20200000
MMMarkerTransformNode::MMMarkerTransformNode(MPxTransformationMatrix *tm) : MPxTransform(tm) {}
#endif

void MMMarkerTransformNode::postConstructor() {
    MPxTransform::postConstructor();
#if MAYA_API_VERSION < 20190000
    if (baseTransformationMatrix == nullptr) {
        baseTransformationMatrix = new MMMarkerTransformMatrix();
    }
#endif
}

MMMarkerTransformNode::~MMMarkerTransformNode() {
    // Empty function body rather than '= default', to allow compiling
    // under Visual Studio 2012.
};


void *MMMarkerTransformNode::creator() {
    return (new MMMarkerTransformNode());
}


MStatus MMMarkerTransformNode::initialize() {
    MStatus status;
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

    mustCallValidateAndSet(a_inLens);

    return MS::kSuccess;
}

void MMMarkerTransformNode::resetTransformation (const MMatrix &m)
{
    ParentClass::resetTransformation(m);
}

void MMMarkerTransformNode::resetTransformation (MPxTransformationMatrix *resetMatrix )
{
    ParentClass::resetTransformation(resetMatrix);
}

// Ensure each plug value is validated and is used to set internal
// data.
#if MAYA_API_VERSION < 20180000
MStatus MMMarkerTransformNode::validateAndSetValue(const MPlug& plug,
                                                   const MDataHandle& handle,
                                                   const MDGContext& context) {
#else
MStatus MMMarkerTransformNode::validateAndSetValue(const MPlug& plug,
                                                   const MDataHandle& handle) {
#endif
    // Make sure that there is something interesting to process.
    if (plug.isNull()) {
        return MS::kFailure;
    }

    if (plug == a_inLens) {
        MStatus status = MS::kSuccess;

#if MAYA_API_VERSION < 20180000
        MDataBlock data = forceCache(*(MDGContext*)&context);
#else
        MDataBlock data = forceCache();
#endif
        MDataHandle dataHandle = data.outputValue(plug, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Create initial plug-in data structure. We don't need to
        // 'new' the data type directly.
        MFnPluginData fnPluginData;
        MTypeId data_type_id(MM_LENS_DATA_TYPE_ID);
        fnPluginData.create(data_type_id, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Get Input Lens
        MMLensData* inputLensData = (MMLensData*) dataHandle.asPluginData();
        LensModel* inputLensModel = nullptr;
        if (inputLensData != nullptr) {
            inputLensModel = (LensModel*) inputLensData->getValue();
        }

        // Update our new lens data
        MMLensData* newLensData = (MMLensData*) fnPluginData.data(&status);
        newLensData->setValue(inputLensModel);
        dataHandle.setMPxData(newLensData);

        // Update the custom transformation matrix with new values.
        MMMarkerTransformMatrix *ltm = getMarkerTransformMatrix();
        if (ltm) {
            ltm->setLensModel(inputLensModel);
        } else {
            MGlobal::displayError("Failed to get marker transform matrix");
        }

        dataHandle.setClean();

        // Mark the matrix as dirty so that DG information
        // will update.
        dirtyMatrix();

        return status;
    }

    // Allow processing for other attributes
#if MAYA_API_VERSION < 20180000
    return ParentClass::validateAndSetValue(plug, handle, context);
#else
    return ParentClass::validateAndSetValue(plug, handle);
#endif
}

MMMarkerTransformMatrix *MMMarkerTransformNode::getMarkerTransformMatrix() {
#if MAYA_API_VERSION < 20190000
    MMMarkerTransformMatrix *ltm = (MMMarkerTransformMatrix *) baseTransformationMatrix;
#elif MAYA_API_VERSION >= 20190000
    MMMarkerTransformMatrix *ltm = (MMMarkerTransformMatrix *) transformationMatrixPtr();
#endif
    return ltm;
}
