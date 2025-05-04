/*
 * Copyright (C) 2018, 2019 David Cattermole.
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

#include "arg_flags_attr_details.h"

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MArgParser.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// Internal Objects
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/adjust/adjust_relationships.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_attr_list.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

void createAttributeDetailsSyntax(MSyntax &syntax) {
    syntax.addFlag(STIFFNESS_FLAG, STIFFNESS_FLAG_LONG, MSyntax::kString,
                   MSyntax::kString, MSyntax::kString, MSyntax::kString);
    syntax.addFlag(SMOOTHNESS_FLAG, SMOOTHNESS_FLAG_LONG, MSyntax::kString,
                   MSyntax::kString, MSyntax::kString, MSyntax::kString);

    syntax.makeFlagMultiUse(STIFFNESS_FLAG);
    syntax.makeFlagMultiUse(SMOOTHNESS_FLAG);
    return;
}

MStatus parseAttributeDetailsArguments(
    const MArgDatabase &argData, const AttrList &attrList,
    StiffAttrsPtrList &out_stiffAttrsList,
    SmoothAttrsPtrList &out_smoothAttrsList) {
    MStatus status = MStatus::kSuccess;

    out_stiffAttrsList.clear();
    out_smoothAttrsList.clear();

    // Get Stiffness Values
    unsigned int stiffnessNum = argData.numberOfFlagUses(STIFFNESS_FLAG);
    for (unsigned int i = 0; i < stiffnessNum; ++i) {
        MArgList stiffnessArgs;
        status = argData.getFlagArgumentList(STIFFNESS_FLAG, i, stiffnessArgs);
        if (status == MStatus::kSuccess) {
            if (stiffnessArgs.length() != 4) {
                MMSOLVER_MAYA_ERR(
                    "Attribute Stiffness argument list must have 4 argument; "
                    << "\"node.attribute\", "
                    << "\"node.attributeStiffWeight\", "
                    << "\"node.attributeStiffVariance\", "
                    << "\"node.attributeStiffValue\".");
                continue;
            }

            // Find the already created Attribute.
            MString nodeAttrName = stiffnessArgs.asString(0);
            AttrPtr foundAttr;
            AttrIndex foundIndex = 0;
            for (AttrIndex attrIndex = 0; attrIndex < attrList.size();
                 ++attrIndex) {
                AttrPtr attr = attrList.get_attr(attrIndex);
                if (nodeAttrName == attr->getName()) {
                    foundAttr = attr;
                    break;
                }
                foundIndex++;
            }
            if (foundAttr->getName() == ".") {
                MMSOLVER_MAYA_ERR(
                    "Attribute Stiffness name is not a declared attribute; "
                    << nodeAttrName);
                continue;
            }
            AttrPtr stiffWeightAttr = AttrPtr(new Attr());
            MString weightNodeAttrName = stiffnessArgs.asString(1);
            stiffWeightAttr->setName(weightNodeAttrName);

            AttrPtr stiffVarianceAttr = AttrPtr(new Attr());
            MString varianceNodeAttrName = stiffnessArgs.asString(2);
            stiffVarianceAttr->setName(varianceNodeAttrName);

            AttrPtr stiffValueAttr = AttrPtr(new Attr());
            MString valueNodeAttrName = stiffnessArgs.asString(3);
            stiffValueAttr->setName(valueNodeAttrName);

            StiffAttrsPtr stiffAttrs = StiffAttrsPtr(new StiffAttrs());
            stiffAttrs->attrIndex = foundIndex;
            stiffAttrs->weightAttr = stiffWeightAttr;
            stiffAttrs->varianceAttr = stiffVarianceAttr;
            stiffAttrs->valueAttr = stiffValueAttr;

            out_stiffAttrsList.push_back(stiffAttrs);
        }
    }

    // Get Smoothness Values
    unsigned int smoothnessNum = argData.numberOfFlagUses(SMOOTHNESS_FLAG);
    for (unsigned int i = 0; i < smoothnessNum; ++i) {
        MArgList smoothnessArgs;
        status =
            argData.getFlagArgumentList(SMOOTHNESS_FLAG, i, smoothnessArgs);
        if (status == MStatus::kSuccess) {
            if (smoothnessArgs.length() != 4) {
                MMSOLVER_MAYA_ERR(
                    "Attribute Smoothness argument list must have 4 argument; "
                    << "\"node.attribute\", "
                    << "\"node.attributeSmoothWeight\", "
                    << "\"node.attributeSmoothVariance\", "
                    << "\"node.attributeSmoothValue\".");
                continue;
            }

            // Find the already created Attribute.
            MString nodeAttrName = smoothnessArgs.asString(0);
            AttrPtr foundAttr;
            AttrIndex foundIndex = 0;
            for (AttrIndex attrIndex = 0; attrIndex < attrList.size();
                 ++attrIndex) {
                AttrPtr attr = attrList.get_attr(attrIndex);
                if (nodeAttrName == attr->getName()) {
                    foundAttr = attr;
                    break;
                }
                foundIndex++;
            }
            if (foundAttr->getName() == ".") {
                MMSOLVER_MAYA_ERR(
                    "Attribute Smoothness name is not a declared attribute; "
                    << nodeAttrName);
                continue;
            }
            AttrPtr smoothWeightAttr = AttrPtr(new Attr());
            MString weightNodeAttrName = smoothnessArgs.asString(1);
            smoothWeightAttr->setName(weightNodeAttrName);

            AttrPtr smoothVarianceAttr = AttrPtr(new Attr());
            MString varianceNodeAttrName = smoothnessArgs.asString(2);
            smoothVarianceAttr->setName(varianceNodeAttrName);

            AttrPtr smoothValueAttr = AttrPtr(new Attr());
            MString valueNodeAttrName = smoothnessArgs.asString(3);
            smoothValueAttr->setName(valueNodeAttrName);

            SmoothAttrsPtr smoothAttrs = SmoothAttrsPtr(new SmoothAttrs());
            smoothAttrs->attrIndex = foundIndex;
            smoothAttrs->weightAttr = smoothWeightAttr;
            smoothAttrs->varianceAttr = smoothVarianceAttr;
            smoothAttrs->valueAttr = smoothValueAttr;

            out_smoothAttrsList.push_back(smoothAttrs);
        }
    }

    return status;
}

}  // namespace mmsolver
