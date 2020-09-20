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
 * Command for running mmAffects.
 *
 * Example usage (MEL):
 *
 *   mmAffects
 *       -camera "camera1" "camera1Shape"
 *       -marker "myMarker"
 *       -attr "myBundle.translateX"
 *       -frame 1
 *       -frame 42
 *       -frame 120
 *       -attrStiffness "myBundle.translateX"
 *       -attrSmoothness "myBundle.translateX"
 *       -mode "addAttrsToMarkers";
 *
 */


// Internal
#include <MMAffectsCmd.h>
#include <commonArgFlags.h>
#include <mayaUtils.h>
#include <core/bundleAdjust_defines.h>
#include <core/bundleAdjust_data.h>
#include <core/bundleAdjust_base.h>
#include <core/bundleAdjust_relationships.h>

// STL
#include <vector>
#include <cmath>
#include <cassert>

// Utils
#include <utilities/debugUtils.h>
#include <utilities/stringUtils.h>

// Maya
#include <maya/MSyntax.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MUuid.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>


MMAffectsCmd::~MMAffectsCmd() {}

void *MMAffectsCmd::creator() {
    return new MMAffectsCmd();
}

MString MMAffectsCmd::cmdName() {
    return MString("mmAffects");
}


bool MMAffectsCmd::hasSyntax() const {
    return true;
}


bool MMAffectsCmd::isUndoable() const {
    return true;
}


MSyntax MMAffectsCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(MODE_FLAG, MODE_FLAG_LONG, MSyntax::kString);

    createSolveObjectSyntax(syntax);
    return syntax;
}


MStatus MMAffectsCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get 'Mode'
    MMAffectsCmd::m_mode = "";
    if (argData.isFlagSet(MODE_FLAG)) {
        status = argData.getFlagArgument(MODE_FLAG, 0, MMAffectsCmd::m_mode);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    parseSolveObjectArguments(
        argData,
        m_cameraList,
        m_markerList,
        m_bundleList,
        m_attrList,
        m_frameList,
        m_stiffAttrsList,
        m_smoothAttrsList);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}


MStatus setAttrsOnMarkers(MarkerPtrList markerList,
                          AttrPtrList attrList,
                          BoolList2D markerToAttrMapping,
                          MDGModifier &addAttr_dgmod,
                          MDGModifier &setAttr_dgmod) {
    MStatus status = MStatus::kSuccess;

    const double defaultValue = 0;
    const MFnNumericData::Type unitType = MFnNumericData::Type::kByte;

    // Create all needed attributes
    for (AttrPtrListIt ait = attrList.begin();
         ait != attrList.end(); ++ait) {
        AttrPtr attr = *ait;
        MObject attrNodeObject = attr->getObject();
        MFnDependencyNode attrNodeFn(attrNodeObject);
        MObject attrObject = attr->getAttribute();

        MUuid attrUuid = attrNodeFn.uuid(&status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MString attrUuidStr = attrUuid.asString();

        MString attrName = "";
        MFnAttribute attrAttrFn(attrObject);
        MString nodeAttrName = attrAttrFn.name();
        status = constructAttrAffectsName(
            nodeAttrName,
            attrUuidStr,
            attrName);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        for (MarkerPtrListIt mit = markerList.begin();
             mit != markerList.end(); ++mit) {
            MarkerPtr marker = *mit;
            MObject markerObject = marker->getObject();
            MFnDependencyNode markerNodeFn(markerObject);

            MFnNumericAttribute markerAttrFn(markerObject);
            MObject attributeObj = markerAttrFn.create(
                attrName, attrName,
                unitType, defaultValue,
                &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            bool hasAttr = markerNodeFn.hasAttribute(attrName, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            if (hasAttr == false) {
                status = addAttr_dgmod.addAttribute(markerObject, attributeObj);
                CHECK_MSTATUS_AND_RETURN_IT(status);
            }
        }
    }
    addAttr_dgmod.doIt();

    std::vector<bool>::const_iterator cit_inner;
    BoolList2D::const_iterator cit_outer;
    int markerIndex = 0;
    for (cit_outer = markerToAttrMapping.cbegin();
         cit_outer != markerToAttrMapping.cend();
         ++cit_outer){

        int attrIndex = 0;
        std::vector<bool> inner = *cit_outer;
        for (cit_inner = inner.cbegin();
             cit_inner != inner.cend();
             ++cit_inner){

            MarkerPtr marker = markerList[markerIndex];
            AttrPtr attr = attrList[attrIndex];

            MObject markerObject = marker->getObject();
            MFnDependencyNode markerNodeFn(markerObject);
            MString markerName = markerNodeFn.name();

            MObject attrNodeObject = attr->getObject();
            MFnDependencyNode attrNodeFn(attrNodeObject);
            MUuid attrUuid = attrNodeFn.uuid(&status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            MString attrUuidStr = attrUuid.asString();
            MObject attrObject = attr->getAttribute();

            MString attrName = "";
            MFnAttribute attrFn(attrObject);
            MString nodeAttrName = attrFn.name();
            status = constructAttrAffectsName(
                nodeAttrName,
                attrUuidStr,
                attrName);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            bool wantNetworkedPlug = true;
            MPlug attrPlug = markerNodeFn.findPlug(attrName, wantNetworkedPlug, &status);

            bool value = *cit_inner;
            int plugValue = static_cast<int>(value);

            status = setAttr_dgmod.newPlugValueInt(attrPlug, plugValue);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            ++attrIndex;
        }
        ++markerIndex;
    }

    setAttr_dgmod.doIt();
    return status;
}


MStatus MMAffectsCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Command Outputs
    MStringArray outResult;

    // Read all the flag arguments.
    status = MMAffectsCmd::parseArgs(args);
    if (status != MStatus::kSuccess) {
        ERR("Error parsing mmAffects command arguments.");
        return status;
    }

    IndexPairList paramToAttrList;
    IndexPairList errorToMarkerList;
    std::vector<MPoint> markerPosList;
    std::vector<double> markerWeightList;
    std::vector<double> errorList(1);
    std::vector<double> paramList(1);
    std::vector<double> initialParamList(1);
    std::vector<double> jacobianList(1);

    int numberOfErrors = 0;
    int numberOfMarkerErrors = 0;
    int numberOfAttrStiffnessErrors = 0;
    int numberOfAttrSmoothnessErrors = 0;
    MarkerPtrList validMarkerList;
    numberOfErrors = countUpNumberOfErrors(
            m_markerList,
            m_stiffAttrsList,
            m_smoothAttrsList,
            m_frameList,
            validMarkerList,
            markerPosList,
            markerWeightList,
            errorToMarkerList,
            numberOfMarkerErrors,
            numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors,
            status
    );
    CHECK_MSTATUS_AND_RETURN_IT(status);
    assert(numberOfErrors == (
            numberOfMarkerErrors
            + numberOfAttrStiffnessErrors
            + numberOfAttrSmoothnessErrors));

    int numberOfParameters = 0;
    AttrPtrList camStaticAttrList;
    AttrPtrList camAnimAttrList;
    AttrPtrList staticAttrList;
    AttrPtrList animAttrList;
    std::vector<double> paramLowerBoundList;
    std::vector<double> paramUpperBoundList;
    std::vector<double> paramWeightList;
    BoolList2D paramFrameList;
    numberOfParameters = countUpNumberOfUnknownParameters(
            m_attrList,
            m_frameList,
            camStaticAttrList,
            camAnimAttrList,
            staticAttrList,
            animAttrList,
            paramLowerBoundList,
            paramUpperBoundList,
            paramWeightList,
            paramToAttrList,
            paramFrameList,
            status
    );
    CHECK_MSTATUS_AND_RETURN_IT(status);
    assert(paramLowerBoundList.size() == numberOfParameters);
    assert(paramUpperBoundList.size() == numberOfParameters);
    assert(paramWeightList.size() == numberOfParameters);
    assert(numberOfParameters >= attrList.size());

    BoolList2D markerToAttrMapping;
    findMarkerToAttributeRelationship(
            m_markerList,
            m_attrList,
            markerToAttrMapping,
            status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    BoolList2D errorToParamMapping;
    findErrorToParameterRelationship(
        m_markerList,
        m_attrList,
        m_frameList,
        numberOfParameters,
        numberOfErrors,
        paramToAttrList,
        errorToMarkerList,
        markerToAttrMapping,
        errorToParamMapping,
        status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (m_mode == MODE_VALUE_ADD_ATTRS_TO_MARKERS) {
        status = setAttrsOnMarkers(
            m_markerList,
            m_attrList,
            markerToAttrMapping,
            m_addAttr_dgmod,
            m_setAttr_dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    } else if (m_mode == MODE_VALUE_RETURN_STRING) {
        status = logResultsMarkerAffectsAttribute(
            m_markerList,
            m_attrList,
            markerToAttrMapping,
            outResult);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMAffectsCmd::setResult(outResult);
    } else {
        ERR("Mode value is invalid: mode=" << m_mode << "\n");
    }
    return status;
}

MStatus MMAffectsCmd::redoIt() {
    MStatus status;
    m_addAttr_dgmod.doIt();
    m_setAttr_dgmod.doIt();
    return status;
}

MStatus MMAffectsCmd::undoIt() {
    MStatus status;
    m_setAttr_dgmod.undoIt();
    m_addAttr_dgmod.undoIt();
    return status;
}
