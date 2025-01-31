/*
 * Copyright (C) 2018, 2019, 2020, 2025 David Cattermole.
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
 * Calculates relationships and stats for bundle adjustment data structures.
 *
 */

#include "adjust_relationships.h"

// STL
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>
#include <ctime>
#include <fstream>
#include <iostream>
#include <limits>
#include <map>
#include <string>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MFloatMatrix.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnAttribute.h>
#include <maya/MFnCamera.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MGlobal.h>
#include <maya/MItDependencyGraph.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MProfiler.h>
#include <maya/MSelectionList.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MUuid.h>
#include <maya/MVector.h>

// MM Solver
#include "adjust_base.h"
#include "adjust_cminpack_base.h"
#include "adjust_cminpack_lmder.h"
#include "adjust_cminpack_lmdif.h"
#include "adjust_levmar_bc_dif.h"
#include "adjust_solveFunc.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/string_utils.h"

/*
 * Count up number of errors to be measured in the solve.
 */
uint32_t countUpNumberOfErrors(
    const MarkerPtrList &markerList, const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList, const MTimeArray &frameList,
    MarkerPtrList &out_validMarkerList, std::vector<MPoint> &out_markerPosList,
    std::vector<double> &out_markerWeightList,
    IndexPairList &out_errorToMarkerList, uint32_t &out_numberOfMarkerErrors,
    uint32_t &out_numberOfAttrStiffnessErrors,
    uint32_t &out_numberOfAttrSmoothnessErrors, MStatus &status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("countUpNumberOfErrors");

    status = MStatus::kSuccess;

    // For each marker on each frame that it is valid, we add
    // ERRORS_PER_MARKER errors.

    // For normalising the marker weight per-frame, create a mapping
    // data structure to use later.
    typedef std::map<int, double> FrameIndexDoubleMapping;
    typedef FrameIndexDoubleMapping::iterator FrameIndexDoubleMappingIt;
    FrameIndexDoubleMapping weightMaxPerFrame;
    FrameIndexDoubleMappingIt xit;

    // Reset data structures, because we assume we start with an empty
    // data structure.
    out_validMarkerList.clear();
    out_errorToMarkerList.clear();
    out_markerPosList.clear();
    out_markerWeightList.clear();
    out_numberOfMarkerErrors = 0;
    out_numberOfAttrStiffnessErrors = 0;
    out_numberOfAttrSmoothnessErrors = 0;

    const auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;

    // Get all the marker data
    int i = 0;
    for (MarkerPtrListCIt mit = markerList.cbegin(); mit != markerList.cend();
         ++mit) {
        MarkerPtr marker = *mit;
        for (int j = 0; j < (int)frameList.length(); ++j) {
            MTime frame = frameList[j];

            bool enable = false;
            status = marker->getEnable(enable, frame, timeEvalMode);
            CHECK_MSTATUS_AND_RETURN(status, out_numberOfMarkerErrors);

            double weight = 0.0;
            status = marker->getWeight(weight, frame, timeEvalMode);
            CHECK_MSTATUS_AND_RETURN(status, out_numberOfMarkerErrors);

            if (enable && (weight > 0.0)) {
                // First index is into 'markerList'
                // Second index is into 'frameList'
                IndexPair markerPair(i, j);
                out_errorToMarkerList.push_back(markerPair);
                out_numberOfMarkerErrors += ERRORS_PER_MARKER;

                out_validMarkerList.push_back(marker);

                // Add marker weights, into a cached list to be used
                // during solving for direct look-up.
                out_markerWeightList.push_back(weight);

                // Get maximum weight value of all marker weights
                // per-frame
                xit = weightMaxPerFrame.find(j);
                double weight_max = weight;
                if (xit != weightMaxPerFrame.end()) {
                    weight_max = xit->second;
                    if (weight > weight_max) {
                        weight_max = weight;
                    }
                    weightMaxPerFrame.erase(xit);
                }
                weightMaxPerFrame.insert(std::pair<int, double>(j, weight_max));

                // Get 'distorted' Marker positions, just the
                // translate X/Y values, with any overscan factors on
                // the MarkerGroup taken into account.
                double px = 0.0;
                double py = 0.0;
                bool applyOverscan = true;
                status = marker->getPosXY(px, py, frame, timeEvalMode,
                                          applyOverscan);
                CHECK_MSTATUS(status);
                MPoint marker_pos(px, py, 0.0);
                out_markerPosList.push_back(marker_pos);
            }
        }
        i++;
    }

    // Normalise the weights per-frame, using the weight 'max'
    // computed above.
    i = 0;
    for (IndexPairListCIt eit = out_errorToMarkerList.cbegin();
         eit != out_errorToMarkerList.cend(); ++eit) {
        double weight = out_markerWeightList[i];

        int frameIndex = eit->second;

        xit = weightMaxPerFrame.find(frameIndex);
        assert(xit != weightMaxPerFrame.end());
        const double weight_max = xit->second;

        weight = weight / weight_max;
        out_markerWeightList[i] = weight;
        ++i;
    }

    // Compute number of errors from Attributes.
    double stiffValue = 0.0;
    for (StiffAttrsPtrListCIt ait = stiffAttrsList.cbegin();
         ait != stiffAttrsList.cend(); ++ait) {
        StiffAttrsPtr stiffAttrs = *ait;

        // Determine if the attribute will use stiffness values. Don't
        // add stiffness to the solver unless it needs
        // to be calculated.
        AttrPtr weightAttr = stiffAttrs->weightAttr;
        weightAttr->getValue(stiffValue, timeEvalMode);
        const bool useStiffness = stiffValue > 0.0;
        if (useStiffness) {
            out_numberOfAttrStiffnessErrors++;
        }
    }

    double smoothValue = 0.0;
    for (SmoothAttrsPtrListCIt ait = smoothAttrsList.cbegin();
         ait != smoothAttrsList.cend(); ++ait) {
        SmoothAttrsPtr smoothAttrs = *ait;

        // Determine if the attribute will use smoothness values. Don't
        // add smoothness to the solver unless it needs
        // to be calculated.
        AttrPtr weightAttr = smoothAttrs->weightAttr;
        weightAttr->getValue(smoothValue, timeEvalMode);
        const bool useSmoothness = smoothValue > 0.0;
        if (useSmoothness) {
            out_numberOfAttrSmoothnessErrors++;
        }
    }

    const uint32_t numTotalErrors = out_numberOfMarkerErrors +
                                    out_numberOfAttrStiffnessErrors +
                                    out_numberOfAttrSmoothnessErrors;
    return numTotalErrors;
}

uint32_t countUpNumberOfUnknownParameters(
    const AttrPtrList &attrList, const MTimeArray &frameList,
    AttrPtrList &out_camStaticAttrList, AttrPtrList &out_camAnimAttrList,
    AttrPtrList &out_staticAttrList, AttrPtrList &out_animAttrList,
    std::vector<double> &out_paramLowerBoundList,
    std::vector<double> &out_paramUpperBoundList,
    std::vector<double> &out_paramWeightList,
    IndexPairList &out_paramToAttrList,
    mmsolver::MatrixBool2D &out_paramFrameMatrix, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("countUpNumberOfUnknownParameters");

    out_status = MStatus::kSuccess;

    const auto frameCount = frameList.length();

    // Count up the type of attributes we have, because we need to
    // pre-allocate blocks of memory.
    uint32_t numAttrsAnimated = 0;
    uint32_t numAttrsStatic = 0;
    for (AttrPtrListCIt ait = attrList.cbegin(); ait != attrList.cend();
         ++ait) {
        AttrPtr attr = *ait;

        if (attr->isAnimated()) {
            numAttrsAnimated++;
        } else if (attr->isFreeToChange()) {
            numAttrsStatic++;
        } else {
            const MString attrName = attr->getName();
            MMSOLVER_MAYA_ERR(
                "countUpNumberOfUnknownParameters: Attribute is not animated "
                "or free: "
                << attrName.asChar());
            assert(false);
            return 0;
        }
    }
    uint32_t numTotalParams = (numAttrsAnimated * frameCount) + numAttrsStatic;

    // Reset data structures, because we assume we start with an empty
    // data structure.
    out_paramToAttrList.clear();
    out_paramFrameMatrix.reset(numTotalParams, frameCount, /*value=*/false);
    out_paramLowerBoundList.clear();
    out_paramUpperBoundList.clear();
    out_paramWeightList.clear();
    out_camStaticAttrList.clear();
    out_camAnimAttrList.clear();
    out_staticAttrList.clear();
    out_animAttrList.clear();

    // Count up number of unknown parameters
    uint32_t numUnknowns = 0;

    int parameterIndex = 0;
    int attrIndex = 0;
    for (AttrPtrListCIt ait = attrList.cbegin(); ait != attrList.cend();
         ++ait) {
        AttrPtr attr = *ait;
        MObject nodeObj = attr->getObject();

        bool attrIsPartOfCamera = false;
        if (nodeObj.apiType() == MFn::kTransform) {
            MFnDagNode dagNode(nodeObj);
            for (unsigned int k = 0; k < dagNode.childCount(); ++k) {
                MObject childObj = dagNode.child(k, &out_status);
                CHECK_MSTATUS(out_status);
                if (childObj.apiType() == MFn::kCamera) {
                    attrIsPartOfCamera = true;
                }
            }
        } else if (nodeObj.apiType() == MFn::kCamera) {
            attrIsPartOfCamera = true;
        }

        if (attr->isAnimated()) {
            // Animated parameter (affects a subset of frames -
            // usually only 1 frame).
            numUnknowns += frameCount;

            for (int frameIndex = 0; frameIndex < (int)frameCount;
                 ++frameIndex) {
                // first index is into 'attrList'
                // second index is into 'frameList'
                IndexPair attrPair(attrIndex, frameIndex);
                out_paramToAttrList.push_back(attrPair);

                // Frame to parameter index mapping.
                out_paramFrameMatrix.set(parameterIndex, frameIndex,
                                         /*value=*/true);

                // Min / max parameter bounds.
                const double minValue = attr->getMinimumValue();
                const double maxValue = attr->getMaximumValue();
                out_paramLowerBoundList.push_back(minValue);
                out_paramUpperBoundList.push_back(maxValue);

                // TODO: Get a weight value from the attribute. Currently
                // weights are not supported in the Maya mmSolver command.
                // This is not the same as Marker weights.
                out_paramWeightList.push_back(1.0);

                parameterIndex++;
            }

            if (attrIsPartOfCamera) {
                out_camAnimAttrList.push_back(attr);
            } else {
                out_animAttrList.push_back(attr);
            }
        } else if (attr->isFreeToChange()) {
            // Static parameter (affects all frames)
            ++numUnknowns;
            // first index is into 'attrList'
            // second index is into 'frameList', '-1' means a static value.
            IndexPair attrPair(attrIndex, -1);
            out_paramToAttrList.push_back(attrPair);

            // Frame to parameter index mapping.
            for (int frameIndex = 0; frameIndex < static_cast<int>(frameCount);
                 ++frameIndex) {
                out_paramFrameMatrix.set(parameterIndex, frameIndex,
                                         /*value=*/true);
            }

            // Min / max parameter bounds.
            double minValue = attr->getMinimumValue();
            double maxValue = attr->getMaximumValue();
            out_paramLowerBoundList.push_back(minValue);
            out_paramUpperBoundList.push_back(maxValue);

            // TODO: Get a weight value from the attribute. Currently
            // weights are not supported in the Maya mmSolver command.
            // This is not the same as Marker weights.
            out_paramWeightList.push_back(1.0);

            if (attrIsPartOfCamera) {
                out_camStaticAttrList.push_back(attr);
            } else {
                out_staticAttrList.push_back(attr);
            }

            parameterIndex++;
        } else {
            // Attributes are invalid if this happens.
            const MString attrName = attr->getName();
            MMSOLVER_MAYA_ERR(
                "countUpNumberOfUnknownParameters: "
                "Attribute is not animated or free: "
                << attrName.asChar());
            assert(false);
            return 0;
        }

        attrIndex++;
    }

    // We've basically recomputed the same value in two loops. Lets
    // make sure someone modifying the code doesn't break this
    // post-condition.
    assert(numUnknowns == numTotalParams);

    return numUnknowns;
}

/*
 * Use the Maya DG graph structure to determine the
 * sparsity structure, a relation of cause and effect; which
 * attributes affect which markers.
 *
 * Answer this question: 'for each marker, determine which
 * attributes can affect it's bundle.'
 *
 * Detect inputs and outputs for marker-bundle relationships. For each
 * marker, get the bundle, then find all the attributes that affect the bundle
 * (and it's parent nodes). If the bundle cannot be affected by any attribute
 * in the solver, print a warning and remove it from the solve list.
 *
 * This relationship building will be the basis for the Ceres
 * residual/parameter block creation. Note we do not need to worry
 * about time in our relationship building, connections cannot be made
 * at different times (and if they did, that would be nonsensical).
 * This relationship building could mean we only need to measure a
 * limited number of bundles, hence improving performance.
 *
 * There are special cases for detecting inputs/outputs between
 * markers and attributes.
 *
 * - Any transform node/attribute above the marker in the DAG that
 *   affects the world transform.
 *
 * - Cameras; transform attributes and focal length will affect all
 *   markers
 *
 */
void findMarkerToAttributeRelationship(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    mmsolver::MatrixBool2D &out_markerToAttrMatrix, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("findMarkerToAttributeRelationship");

    out_status = MStatus::kSuccess;

    // Command execution options
    bool display = false;   // print out what happens in the python
                            // command.
    bool undoable = false;  // we won't modify the scene in any way,
                            // only make queries.
    MString cmd = "";
    MStringArray bundleAffectsResult;
    MStringArray markerAffectsResult;

    // Calculate the relationship between attributes and markers.
    out_markerToAttrMatrix.reset(markerList.size(), attrList.size(), false);
    int markerIndex = 0;
    for (MarkerPtrListCIt mit = markerList.cbegin(); mit != markerList.cend();
         ++mit) {
        MarkerPtr marker = *mit;
        CameraPtr cam = marker->getCamera();
        BundlePtr bundle = marker->getBundle();

        // Get node names.
        const MString markerNodeName = marker->getNodeName();
        const MString camNodeName = cam->getTransformNodeName();
        const MString bundleNodeName = bundle->getNodeName();
        const char *markerName = markerNodeName.asChar();
        const char *camName = camNodeName.asChar();
        const char *bundleName = bundleNodeName.asChar();

        // Find list of plug names that are affected by the bundle.
        cmd = "";
        cmd += "import mmSolver.utils.nodeaffects as nodeaffects;";
        cmd += "nodeaffects.find_plugs_affecting_transform(";
        cmd += "\"";
        cmd += bundleName;
        cmd += "\", None);";
        MMSOLVER_MAYA_VRB("Running: " + cmd);
        out_status = MGlobal::executePythonCommand(cmd, bundleAffectsResult,
                                                   display, undoable);
        CHECK_MSTATUS(out_status);

        // Find list of plug names that are affected by the marker
        // (and camera projection matrix).
        cmd = "";
        cmd += "import mmSolver.utils.nodeaffects as nodeaffects;";
        cmd += "nodeaffects.find_plugs_affecting_transform(";
        cmd += "\"";
        cmd += markerName;
        cmd += "\", \"";
        cmd += camName;
        cmd += "\"";
        cmd += ");";
        MMSOLVER_MAYA_VRB("Running: " + cmd);
        out_status = MGlobal::executePythonCommand(cmd, markerAffectsResult,
                                                   display, undoable);
        CHECK_MSTATUS(out_status);

        // Determine if the marker can affect the attribute.
        int attrIndex = 0;
        MString affectedPlugName;
        for (AttrPtrListCIt ait = attrList.begin(); ait != attrList.end();
             ++ait) {
            AttrPtr attr = *ait;

            // Get attribute full path.
            MPlug plug = attr->getPlug();
            MObject attrNode = plug.node();
            MFnDagNode attrFnDagNode(attrNode);
            MString attrNodeName = attrFnDagNode.fullPathName();
            MString attrAttrName =
                plug.partialName(false, true, true, false, false, true);
            MString attrName = attrNodeName + "." + attrAttrName;

            // Bundle affects attribute
            for (unsigned int k = 0; k < bundleAffectsResult.length(); ++k) {
                affectedPlugName = bundleAffectsResult[k];
                if (attrName == affectedPlugName) {
                    out_markerToAttrMatrix.set(markerIndex, attrIndex, true);
                    break;
                }
            }

            // Marker (or camera) affects attribute
            for (unsigned int k = 0; k < markerAffectsResult.length(); ++k) {
                affectedPlugName = markerAffectsResult[k];
                if (attrName == affectedPlugName) {
                    out_markerToAttrMatrix.set(markerIndex, attrIndex, true);
                    break;
                }
            }
            ++attrIndex;
        }
        ++markerIndex;
    }
    return;
}

/*
 * Read the relationship of Marker to Attributes from parsing the
 * given Markers/Attributes directly.
 *
 * This function assumes the use of 'mmSolverAffects' with the
 * 'addAttrsToMarkers' mode flag has already been run.
 */
void getMarkerToAttributeRelationship(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    mmsolver::MatrixBool2D &out_markerToAttrMatrix, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("getMarkerToAttributeRelationship");

    out_status = MStatus::kSuccess;

    // The attribute's 'affect' is assumed to be true if the plug
    // cannot be found. We go by "assumed innocent until proven
    // guilty", because an incorrect 'true' value will reduce
    // performance, but an incorrect 'false' value will lead to
    // incorrect solver results.
    const bool defaultValue = true;

    // Calculate the relationship between attributes and markers.
    out_markerToAttrMatrix.reset(markerList.size(), attrList.size(),
                                 /*fill_value=*/defaultValue);
    int markerIndex = 0;
    for (MarkerPtrListCIt mit = markerList.cbegin(); mit != markerList.cend();
         ++mit) {
        MarkerPtr marker = *mit;
        MObject markerObject = marker->getObject();
        MFnDependencyNode markerNodeFn(markerObject);

        // Determine if the marker can affect the attribute.
        int attrIndex = 0;
        for (AttrPtrListCIt ait = attrList.begin(); ait != attrList.end();
             ++ait) {
            AttrPtr attr = *ait;

            // Get Attribute's Node Name.
            MObject attrNodeObject = attr->getObject();
            MFnDependencyNode attrNodeFn(attrNodeObject);
            MObject attrObject = attr->getAttribute();
            MUuid attrUuid = attrNodeFn.uuid(&out_status);
            CHECK_MSTATUS(out_status);
            MString attrUuidStr = attrUuid.asString();

            // Get Attribute's Name.
            MFnAttribute attrAttrFn(attrObject);
            MString nodeAttrName = attrAttrFn.name();

            // Calculate the naming format that is expected to be on
            // the Marker transform node.
            MString attrName = "";
            out_status =
                constructAttrAffectsName(nodeAttrName, attrUuidStr, attrName);
            CHECK_MSTATUS(out_status);

            // Get plug value
            bool value = defaultValue;
            MPlug plug = markerNodeFn.findPlug(attrName, true);
            const bool attrExists = plug.isNull() == false;
            if (attrExists) {
                // The Maya attribute is expected to be an integer,
                // however only -1, 0 and 1 values are currently used.
                // In the future we may use values other than -1, 0
                // and 1.
                //
                // 1 == 'used'
                // -1 == 'not used'
                // 0 == 'unknown'
                value = plug.asInt() == 1;
            }
            out_markerToAttrMatrix.set(markerIndex, attrIndex, value);
            ++attrIndex;
        }
        ++markerIndex;
    }

    return;
}

/*
 * Calculate the relationship between errors and parameters.
 *
 * For each error, work out which parameters can affect
 * it. The parameters may be static or animated and thereby each
 * parameter may affect one or more errors. A single parameter
 * will affect a range of time values, a static parameter affects
 * all time values, but a dynamic parameter will be split into
 * many parameters at different frames, each of those dynamic
 * parameters will only affect a small number of errors. Our goal
 * is to compute a boolean for each error and parameter
 * combination, if the boolean is true the relationship is
 * positive, if false, the computation is skipped and the error
 * returned is zero.  This combination is only relevant if the
 * markerToAttrMatrix is already true, otherwise we can assume
 * such error/parameter combinations will not be required.
 */
void findErrorToParameterRelationship(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    const MTimeArray &frameList, const uint32_t numParameters,
    const uint32_t numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const mmsolver::MatrixBool2D &markerToAttrMatrix,
    mmsolver::MatrixBool2D &out_errorToParamMatrix, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("findErrorToParameterRelationship");

    out_status = MStatus::kSuccess;

    const auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;

    // Attributes are assumed not to affect any marker, until
    // proven otherwise.
    const bool defaultValue = false;

    const uint32_t numberOfMarkers = numMarkerErrors / ERRORS_PER_MARKER;
    out_errorToParamMatrix.reset(numberOfMarkers, numParameters,
                                 /*fill_value=*/defaultValue);
    for (uint32_t errorIndex = 0; errorIndex < numberOfMarkers; ++errorIndex) {
        const IndexPair markerIndexPair = errorToMarkerList[errorIndex];
        const int markerIndex = markerIndexPair.first;
        const int markerFrameIndex = markerIndexPair.second;

        const MarkerPtr mkr = markerList[markerIndex];
        const MTime markerFrame = frameList[markerFrameIndex];

        bool markerEnable = true;
        mkr->getEnable(markerEnable, markerFrame, timeEvalMode);

        double markerWeight = 1.0;
        mkr->getWeight(markerWeight, markerFrame, timeEvalMode);

        markerWeight *= static_cast<double>(markerEnable);
        // TODO: Can we compute this value once per markerList and
        // per-frame and then re-use it?
        const bool markerIsEnabled = markerWeight > 0;
        if (!markerIsEnabled) {
            // All parameters must be unaffected by this marker.
            continue;
        }

        // Determine if the marker can affect the attribute.
        for (uint32_t paramIndex = 0; paramIndex < numParameters;
             ++paramIndex) {
            const IndexPair attrIndexPair = paramToAttrList[paramIndex];
            const int attrIndex = attrIndexPair.first;
            const int attrFrameIndex = attrIndexPair.second;

            // If the attrFrameIndex is -1, then the attribute is
            // static, not animated.
            MTime attrFrame(-1.0, MTime::uiUnit());
            if (attrFrameIndex >= 0) {
                attrFrame = frameList[attrFrameIndex];
            }

            bool paramAffectsError =
                markerToAttrMatrix.at(markerIndex, attrIndex);
            if (paramAffectsError) {
                // Time based mapping information.
                // Only markers on the current frame can affect the current
                // attribute.
                if (attrFrameIndex >= 0) {
                    paramAffectsError = number::isApproxEqual<double>(
                        markerFrame.value(), attrFrame.value());
                } else {
                    // TODO: This may not always be the case. If an
                    // attribute is static, but the marker is animated
                    // the marker may not be able to affect the
                    // attribute.
                    paramAffectsError = true;
                }
            }
            out_errorToParamMatrix.set(errorIndex, paramIndex,
                                       paramAffectsError);
        }
    }
    return;
}

void calculateMarkerAndParameterCount(
    const MarkerPtrList &markerList, const AttrPtrList &attrList,
    const MTimeArray &frameList, const uint32_t numParameters,
    const uint32_t numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const mmsolver::MatrixBool2D &markerToAttrMatrix,
    const FrameSolveMode frameSolveMode,
    std::unordered_set<int32_t> &out_valid_frames,
    std::unordered_set<int32_t> &out_invalid_frames, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCount");

    out_status = MStatus::kSuccess;
    const auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    const auto uiUnit = MTime::uiUnit();

    std::unordered_map<int32_t, uint32_t> errorCountPerFrame;
    std::unordered_map<int32_t, uint32_t> paramCountPerFrame;

    // Calculate enabled marker count per frame.
    for (int frameIndex = 0; frameIndex < frameList.length(); ++frameIndex) {
        const MTime frame = frameList[frameIndex];

        uint32_t markerEnabledCount = 0;
        for (const auto &mkr : markerList) {
            bool enable = true;
            mkr->getEnable(enable, frame, timeEvalMode);

            double weight = 1.0;
            mkr->getWeight(weight, frame, timeEvalMode);

            const bool markerIsEnabled = (enable && weight > 0.0);
            markerEnabledCount += static_cast<uint32_t>(markerIsEnabled);
        }

        const int32_t frameNumber = static_cast<int32_t>(frame.asUnits(uiUnit));
        errorCountPerFrame[frameNumber] =
            markerEnabledCount * ERRORS_PER_MARKER;
    }

    // Calculate parameter counts.
    if (frameSolveMode == FrameSolveMode::kAllFrameAtOnce) {
        // For all-frames mode, count both static and animated
        // parameters.
        uint32_t totalParamCount = 0;

        for (int attrIndex = 0; attrIndex < attrList.size(); ++attrIndex) {
            const AttrPtr &attr = attrList[attrIndex];

            const bool attr_is_frame_to_change = attr->isFreeToChange();
            const bool attr_is_animated = attr->isAnimated();
            MMSOLVER_MAYA_VRB(
                "calculateMarkerAndParameterCount:"
                " attrIndex="
                << attrIndex
                << " | attr_is_free_to_change=" << attr_is_frame_to_change);
            MMSOLVER_MAYA_VRB(
                "calculateMarkerAndParameterCount:"
                " attrIndex="
                << attrIndex << " | attr_is_animated=" << attr_is_animated);

            if (attr_is_frame_to_change || attr_is_animated) {
                totalParamCount++;
            }
        }

        // Apply same parameter count to all frames.
        for (int frameIndex = 0; frameIndex < frameList.length();
             ++frameIndex) {
            const MTime frame = frameList[frameIndex];
            const int32_t frameNumber =
                static_cast<int32_t>(frame.asUnits(uiUnit));

            paramCountPerFrame[frameNumber] = totalParamCount;
        }
    } else if (frameSolveMode == FrameSolveMode::kPerFrame) {
        // For per-frame mode, only count animated parameters.
        for (int frameIndex = 0; frameIndex < frameList.length();
             ++frameIndex) {
            const MTime frame = frameList[frameIndex];
            const int32_t frameNumber =
                static_cast<int32_t>(frame.asUnits(uiUnit));

            uint32_t frameParamCount = 0;
            for (int attrIndex = 0; attrIndex < attrList.size(); ++attrIndex) {
                const AttrPtr &attr = attrList[attrIndex];

                const bool attr_is_frame_to_change = attr->isFreeToChange();
                const bool attr_is_animated = attr->isAnimated();
                MMSOLVER_MAYA_VRB(
                    "calculateMarkerAndParameterCount:"
                    " frame="
                    << frameNumber << " | attrIndex=" << attrIndex
                    << " | attr_is_free_to_change=" << attr_is_frame_to_change);
                MMSOLVER_MAYA_VRB(
                    "calculateMarkerAndParameterCount:"
                    " frame="
                    << frameNumber << " | attrIndex=" << attrIndex
                    << " | attr_is_animated=" << attr_is_animated);

                if (attr_is_frame_to_change || attr_is_animated) {
                    frameParamCount++;
                }
            }
            paramCountPerFrame[frameNumber] = frameParamCount;
        }
    } else {
        MMSOLVER_MAYA_ERR(
            "calculateMarkerAndParameterCount: "
            "Invalid 'frameSolveMode' value;"
            << static_cast<uint32_t>(frameSolveMode));
        assert(false && "Invalid 'frameSolveMode' value.");
    }

    // Determine valid/invalid frames.
    for (int frameIndex = 0; frameIndex < frameList.length(); ++frameIndex) {
        const MTime frame = frameList[frameIndex];
        const int32_t frameNumber = static_cast<int32_t>(frame.asUnits(uiUnit));

        const uint32_t errorCount = errorCountPerFrame[frameNumber];
        const uint32_t paramCount = paramCountPerFrame[frameNumber];

        MMSOLVER_MAYA_VRB(
            "calculateMarkerAndParameterCount: "
            "frame="
            << frameNumber << " | errorCount=" << errorCount);
        MMSOLVER_MAYA_VRB(
            "calculateMarkerAndParameterCount: "
            "frame="
            << frameNumber << " | paramCount=" << paramCount);

        if (errorCount >= paramCount) {
            out_valid_frames.insert(frameNumber);
        } else {
            out_invalid_frames.insert(frameNumber);
        }
    }

    return;
}
