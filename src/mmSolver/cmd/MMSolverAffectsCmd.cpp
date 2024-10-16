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
 * Command for running mmSolverAffects.
 *
 * Example usage (MEL):
 *
 *   mmSolverAffects
 *       -camera "camera1" "camera1Shape"
 *       -marker "myMarker" "camera1Shape" "myBundle"
 *       -attr "myBundle.translateX" "None" "None" "None" "None"
 *       -mode "addAttrsToMarkers";
 *
 * Note: The '-frame' argument is not required for this command. This
 * command only works with time-independent data.
 *
 */

#include "MMSolverAffectsCmd.h"

// STL
#include <cassert>
#include <cmath>
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MUuid.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/adjust/adjust_relationships.h"
#include "mmSolver/adjust/adjust_results.h"
#include "mmSolver/cmd/common_arg_flags.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

MMSolverAffectsCmd::~MMSolverAffectsCmd() {}

void *MMSolverAffectsCmd::creator() { return new MMSolverAffectsCmd(); }

MString MMSolverAffectsCmd::cmdName() { return MString("mmSolverAffects"); }

bool MMSolverAffectsCmd::hasSyntax() const { return true; }

bool MMSolverAffectsCmd::isUndoable() const { return true; }

MSyntax MMSolverAffectsCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(MODE_FLAG, MODE_FLAG_LONG, MSyntax::kString);

    createSolveObjectSyntax(syntax);
    return syntax;
}

MStatus MMSolverAffectsCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get 'Mode'
    MMSolverAffectsCmd::m_mode = "";
    if (argData.isFlagSet(MODE_FLAG)) {
        status =
            argData.getFlagArgument(MODE_FLAG, 0, MMSolverAffectsCmd::m_mode);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    parseSolveObjectArguments(argData, m_cameraList, m_markerList, m_bundleList,
                              m_attrList);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

/*
 * Create attributes representing the affects relationship, onto the
 * Marker nodes. This is a technique of persistent storageg, so that
 * many functions can re-use the (cached) data.
 */
MStatus setAttrsOnMarkers(MarkerPtrList markerList, AttrPtrList attrList,
                          BoolList2D markerToAttrMapping,
                          MDGModifier &addAttr_dgmod,
                          MDGModifier &setAttr_dgmod) {
    MStatus status = MStatus::kSuccess;

    const double defaultValue = 0;
    const MFnNumericData::Type unitType = MFnNumericData::Type::kByte;

    // Create all needed attributes
    for (AttrPtrListIt ait = attrList.begin(); ait != attrList.end(); ++ait) {
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
        status = constructAttrAffectsName(nodeAttrName, attrUuidStr, attrName);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        for (MarkerPtrListIt mit = markerList.begin(); mit != markerList.end();
             ++mit) {
            MarkerPtr marker = *mit;
            MObject markerObject = marker->getObject();
            MFnDependencyNode markerNodeFn(markerObject);

            MFnNumericAttribute markerAttrFn(markerObject);
            MObject attributeObj = markerAttrFn.create(
                attrName, attrName, unitType, defaultValue, &status);
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
         cit_outer != markerToAttrMapping.cend(); ++cit_outer) {
        int attrIndex = 0;
        std::vector<bool> inner = *cit_outer;
        for (cit_inner = inner.cbegin(); cit_inner != inner.cend();
             ++cit_inner) {
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
            status =
                constructAttrAffectsName(nodeAttrName, attrUuidStr, attrName);
            CHECK_MSTATUS_AND_RETURN_IT(status);

            bool wantNetworkedPlug = true;
            MPlug attrPlug =
                markerNodeFn.findPlug(attrName, wantNetworkedPlug, &status);

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

MStatus MMSolverAffectsCmd::doIt(const MArgList &args) {
    // Read all the flag arguments.
    MStatus status = MMSolverAffectsCmd::parseArgs(args);
    if (status != MStatus::kSuccess) {
        MMSOLVER_MAYA_ERR("Error parsing mmSolverAffects command arguments.");
        return status;
    }

    BoolList2D markerToAttrList;
    findMarkerToAttributeRelationship(m_markerList, m_attrList,
                                      markerToAttrList, status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (m_mode == MODE_VALUE_ADD_ATTRS_TO_MARKERS) {
        status = setAttrsOnMarkers(m_markerList, m_attrList, markerToAttrList,
                                   m_addAttr_dgmod, m_setAttr_dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    } else if (m_mode == MODE_VALUE_RETURN_STRING) {
        AffectsResult affectsResult;
        status = logResultsMarkerAffectsAttribute(
            m_markerList, m_attrList, markerToAttrList, affectsResult);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        MStringArray outResult;
        affectsResult.appendToMStringArray(outResult);
        MMSolverAffectsCmd::setResult(outResult);
    } else {
        MMSOLVER_MAYA_ERR("Mode value is invalid: mode=" << m_mode << "\n");
    }
    return status;
}

MStatus MMSolverAffectsCmd::redoIt() {
    MStatus status;
    m_addAttr_dgmod.doIt();
    m_setAttr_dgmod.doIt();
    return status;
}

MStatus MMSolverAffectsCmd::undoIt() {
    MStatus status;
    m_setAttr_dgmod.undoIt();
    m_addAttr_dgmod.undoIt();
    return status;
}

}  // namespace mmsolver
