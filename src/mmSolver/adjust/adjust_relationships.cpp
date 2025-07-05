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
#include "adjust_solveFunc.h"
#include "mmSolver/core/array_mask.h"
#include "mmSolver/core/matrix_bool_2d.h"
#include "mmSolver/core/matrix_bool_3d.h"
#include "mmSolver/mayahelper/maya_frame_utils.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

namespace {

bool getMarkerIsEnabled(MarkerPtr &marker, const MTime &time,
                        const int32_t timeEvalMode, bool &out_enable,
                        double &out_weight) {
    out_enable = true;
    marker->getEnable(out_enable, time, timeEvalMode);

    out_weight = 1.0;
    marker->getWeight(out_weight, time, timeEvalMode);

    const double weight = out_weight * static_cast<double>(out_enable);
    return weight > 0.0;
}

}  // namespace

/**
 * @brief Counts the number of errors to be measured in the solve
 * operation.
 *
 * This function determines all marker-related errors, attribute
 * stiffness and attribute smoothness errors to be used in the bundle
 * adjustment solve process.
 *
 * For each marker and frame where the marker is valid (enabled with
 * positive weight), ERRORS_PER_MARKER errors are added. The function
 * also normalizes marker weights per-frame and caches marker
 * positions for efficient evaluation during solving.
 *
 * @return Total number of errors (marker + stiffness + smoothness).
 */
Count32 countUpNumberOfErrors(
    const MarkerList &markerList, const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList, const FrameList &frameList,

    // Outputs
    std::vector<MPoint> &out_markerPosList,
    std::vector<double> &out_markerWeightList,
    IndexPairList &out_errorToMarkerList, Count32 &out_numberOfMarkerErrors,
    Count32 &out_numberOfAttrStiffnessErrors,
    Count32 &out_numberOfAttrSmoothnessErrors, MStatus &status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("countUpNumberOfErrors");

    status = MStatus::kSuccess;

    // For each marker on each frame that it is valid, we add
    // ERRORS_PER_MARKER errors.

    // For normalising the marker weight per-frame, create a mapping
    // data structure to use later.
    typedef std::map<FrameIndex, double> FrameIndexDoubleMapping;
    typedef FrameIndexDoubleMapping::iterator FrameIndexDoubleMappingIt;
    FrameIndexDoubleMapping weightMaxPerFrame;
    FrameIndexDoubleMappingIt xit;

    // Reset data structures, because we assume we start with an empty
    // data structure.
    out_errorToMarkerList.clear();
    out_markerPosList.clear();
    out_markerWeightList.clear();
    out_numberOfMarkerErrors = 0;
    out_numberOfAttrStiffnessErrors = 0;
    out_numberOfAttrSmoothnessErrors = 0;

    const auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    const auto uiUnit = MTime::uiUnit();

    MMSOLVER_MAYA_VRB("countUpNumberOfErrors: markerList enabled="
                      << markerList.count_enabled());
    MMSOLVER_MAYA_VRB("countUpNumberOfErrors: frameList enabled="
                      << frameList.count_enabled());

    // Get all the marker data.
    for (MarkerIndex markerIndex = 0; markerIndex < markerList.size();
         ++markerIndex) {
        const bool markerEnabled = markerList.get_enabled(markerIndex);
        if (!markerEnabled) {
            continue;
        }

        MarkerPtr marker = markerList.get_marker(markerIndex);

        for (FrameIndex frameIndex = 0; frameIndex < frameList.size();
             ++frameIndex) {
            const bool frameEnabled = frameList.get_enabled(frameIndex);
            if (!frameEnabled) {
                continue;
            }

            const FrameNumber frameNumber = frameList.get_frame(frameIndex);
            const MTime frame = convert_to_time(frameNumber, uiUnit);

            bool enable = false;
            double weight = 0.0;
            const bool markerIsEnabled =
                getMarkerIsEnabled(marker, frame, timeEvalMode, enable, weight);

            if (enable && (weight > 0.0)) {
                // First index is into 'markerList'
                // Second index is into 'frameList'
                IndexPair markerPair(markerIndex, frameIndex);
                out_errorToMarkerList.push_back(markerPair);
                out_numberOfMarkerErrors += ERRORS_PER_MARKER;

                // Add marker weights, into a cached list to be used
                // during solving for direct look-up.
                out_markerWeightList.push_back(weight);

                // Get maximum weight value of all marker weights
                // per-frame
                xit = weightMaxPerFrame.find(frameIndex);
                double weight_max = weight;
                if (xit != weightMaxPerFrame.end()) {
                    weight_max = xit->second;
                    if (weight > weight_max) {
                        weight_max = weight;
                    }
                    weightMaxPerFrame.erase(xit);
                }
                weightMaxPerFrame.insert(
                    std::pair<FrameIndex, double>(frameIndex, weight_max));

                // Get 'distorted' Marker positions, just the
                // translate X/Y values, with any overscan factors on
                // the MarkerGroup taken into account.
                double px = 0.0;
                double py = 0.0;
                bool applyOverscan = true;
                status = marker->getPosXY(px, py, frame, timeEvalMode,
                                          applyOverscan);
                MMSOLVER_CHECK_MSTATUS(status);
                MPoint marker_pos(px, py, 0.0);
                out_markerPosList.push_back(marker_pos);
            }
        }
    }

    // Normalise the weights per-frame, using the weight 'max'
    // computed above.
    ErrorIndex errorIndex = 0;
    for (IndexPairListCIt eit = out_errorToMarkerList.cbegin();
         eit != out_errorToMarkerList.cend(); ++eit) {
        const double weight = out_markerWeightList[errorIndex];

        const FrameIndex frameIndex = eit->second;

        xit = weightMaxPerFrame.find(frameIndex);
        MMSOLVER_ASSERT(
            xit != weightMaxPerFrame.end(),
            "The frame index must exist in 'out_errorToMarkerList'.");
        const double weight_max = xit->second;

        out_markerWeightList[errorIndex] = weight / weight_max;
        ++errorIndex;
    }

    // Compute number of errors from Attributes.
    //
    // TODO: Remove stiffness attributes.
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

    // TODO: Remove smoothness attributes.
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

    const Count32 numTotalErrors = out_numberOfMarkerErrors +
                                   out_numberOfAttrStiffnessErrors +
                                   out_numberOfAttrSmoothnessErrors;

    MMSOLVER_MAYA_VRB(
        "countUpNumberOfErrors: "
        "numTotalErrors="
        << numTotalErrors);
    MMSOLVER_MAYA_VRB(
        "countUpNumberOfErrors: "
        "out_numberOfMarkerErrors="
        << out_numberOfMarkerErrors);
    MMSOLVER_MAYA_VRB(
        "countUpNumberOfErrors: "
        "out_numberOfAttrStiffnessErrors="
        << out_numberOfAttrStiffnessErrors);
    MMSOLVER_MAYA_VRB(
        "countUpNumberOfErrors: "
        "out_numberOfAttrSmoothnessErrors="
        << out_numberOfAttrSmoothnessErrors);

    return numTotalErrors;
}

namespace {
bool nodeIsCameraType(MObject &node_object) {
    MStatus status = MS::kSuccess;
    bool result = false;
    if (node_object.apiType() == MFn::kTransform) {
        MFnDagNode dagNode(node_object);
        for (Count32 k = 0; k < dagNode.childCount(); ++k) {
            MObject childObj = dagNode.child(k, &status);
            if (status != MS::kSuccess) {
                MMSOLVER_MAYA_ERR(
                    "nodeIsCameraType: Invalid MDagNode.child() value.");
            }

            if (childObj.apiType() == MFn::kCamera) {
                result = true;
                break;
            }
        }
    } else if (node_object.apiType() == MFn::kCamera) {
        result = true;
    }
    return result;
}
}  // namespace

/**
 * @brief Counts the number of unknown parameters to be solved for.
 *
 * This function identifies both static and animated attributes that
 * will be modified during the solve process. It populates various
 * data structures needed for solving, including
 * parameter-to-attribute mappings, parameter bounds, and parameter
 * weights. It also categorizes attributes as either camera-related or
 * regular attributes.
 *
 * @return Total number of parameters to be solved.
 */
Count32 countUpNumberOfUnknownParameters(
    const AttrList &attrList, const FrameList &frameList,

    // Outputs
    AttrList &out_camStaticAttrList, AttrList &out_camAnimAttrList,
    AttrList &out_staticAttrList, AttrList &out_animAttrList,
    std::vector<double> &out_paramLowerBoundList,
    std::vector<double> &out_paramUpperBoundList,
    std::vector<double> &out_paramWeightList,
    IndexPairList &out_paramToAttrList, MatrixBool2D &out_paramToFrameMatrix,
    MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("countUpNumberOfUnknownParameters");

    out_status = MStatus::kSuccess;

    const auto frameCount = static_cast<Count32>(frameList.size());
    const auto frameEnabledCount =
        static_cast<Count32>(frameList.count_enabled());
    MMSOLVER_MAYA_VRB("countUpNumberOfUnknownParameters: frameList.size()="
                      << frameList.size());
    MMSOLVER_MAYA_VRB(
        "countUpNumberOfUnknownParameters: frameList.count_enabled()="
        << frameList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "countUpNumberOfUnknownParameters: frameList.count_disabled()="
        << frameList.count_disabled());
    MMSOLVER_MAYA_VRB("countUpNumberOfUnknownParameters: attrList.size()="
                      << attrList.size());
    MMSOLVER_MAYA_VRB(
        "countUpNumberOfUnknownParameters: attrList.count_enabled()="
        << attrList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "countUpNumberOfUnknownParameters: attrList.count_disabled()="
        << attrList.count_disabled());

    // Count up the type of attributes we have, because we need to
    // pre-allocate blocks of memory.
    Count32 numAttrsAnimated = 0;
    Count32 numAttrsStatic = 0;
    for (AttrIndex attrIndex = 0; attrIndex < attrList.size(); ++attrIndex) {
        AttrPtr attr = attrList.get_attr(attrIndex);
        const bool attrEnabled = attrList.get_enabled(attrIndex);
        if (!attrEnabled) {
            continue;
        }

        if (attr->isAnimated()) {
            numAttrsAnimated++;
        } else if (attr->isFreeToChange()) {
            numAttrsStatic++;
        } else {
            const MString attrName = attr->getName();
            MMSOLVER_MAYA_ERR(
                "countUpNumberOfUnknownParameters: Attribute is not animated "
                "or free: \""
                << attrName.asChar() << "\"");
            MMSOLVER_PANIC("Attribute is not animated or free: \""
                           << attrName.asChar() << "\"");
            return 0;
        }
    }
    MMSOLVER_MAYA_VRB("countUpNumberOfUnknownParameters: numAttrsAnimated="
                      << numAttrsAnimated);
    MMSOLVER_MAYA_VRB(
        "countUpNumberOfUnknownParameters: numAttrsStatic=" << numAttrsStatic);
    MMSOLVER_MAYA_VRB(
        "countUpNumberOfUnknownParameters: frameCount=" << frameCount);
    const Count32 numTotalParams =
        (numAttrsAnimated * frameEnabledCount) + numAttrsStatic;

    // Reset data structures, because we assume we start with an empty
    // data structure.
    out_paramToAttrList.clear();
    out_paramToFrameMatrix.reset(numTotalParams, frameCount, /*value=*/false);
    out_paramLowerBoundList.clear();
    out_paramUpperBoundList.clear();
    out_paramWeightList.clear();
    out_camStaticAttrList.clear();
    out_camAnimAttrList.clear();
    out_staticAttrList.clear();
    out_animAttrList.clear();

    // Count up number of unknown parameters.
    Count32 numUnknowns = 0;

    ParamIndex parameterIndex = 0;
    for (AttrIndex attrIndex = 0; attrIndex < attrList.size(); ++attrIndex) {
        const bool attrEnabled = attrList.get_enabled(attrIndex);
        if (!attrEnabled) {
            continue;
        }

        AttrPtr attr = attrList.get_attr(attrIndex);
        MObject nodeObj = attr->getObject();
        bool attrIsPartOfCamera = nodeIsCameraType(nodeObj);

        if (attr->isAnimated()) {
            // Animated parameter (affects a subset of frames -
            // usually only 1 frame).
            numUnknowns += frameEnabledCount;

            for (FrameIndex frameIndex = 0; frameIndex < frameCount;
                 ++frameIndex) {
                const bool frameEnabled = frameList.get_enabled(frameIndex);
                if (!frameEnabled) {
                    continue;
                }

                // first index is into 'attrList'
                // second index is into 'frameList'
                IndexPair attrPair(attrIndex, frameIndex);
                out_paramToAttrList.push_back(attrPair);

                // Frame to parameter index mapping.
                out_paramToFrameMatrix.set(parameterIndex, frameIndex,
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
                out_camAnimAttrList.push_back(attr, /*enabled=*/true);
            } else {
                out_animAttrList.push_back(attr, /*enabled=*/true);
            }
        } else if (attr->isFreeToChange()) {
            // Static parameter (affects all frames)
            ++numUnknowns;
            // first index is into 'attrList'
            // second index is into 'frameList', '-1' means a static value.
            IndexPair attrPair(attrIndex, -1);
            out_paramToAttrList.push_back(attrPair);

            // Frame to parameter index mapping.
            for (FrameIndex frameIndex = 0;
                 frameIndex < static_cast<FrameIndex>(frameCount);
                 ++frameIndex) {
                const bool frameEnabled = frameList.get_enabled(frameIndex);
                if (!frameEnabled) {
                    continue;
                }

                out_paramToFrameMatrix.set(parameterIndex, frameIndex,
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
                out_camStaticAttrList.push_back(attr, /*enabled=*/true);
            } else {
                out_staticAttrList.push_back(attr, /*enabled=*/true);
            }

            parameterIndex++;
        } else {
            // Attributes are invalid if this happens.
            const MString attrName = attr->getName();
            MMSOLVER_MAYA_ERR(
                "countUpNumberOfUnknownParameters: Attribute is not animated "
                "or free: \""
                << attrName.asChar() << "\"");
            MMSOLVER_PANIC("Attribute is not animated or free: \""
                           << attrName.asChar() << "\"");
            return 0;
        }
    }

    // We've basically recomputed the same value in two loops. Lets
    // make sure someone modifying the code doesn't break this
    // post-condition.
    MMSOLVER_ASSERT(numUnknowns == numTotalParams,
                    "The re-computed value must be the same; numUnknowns="
                        << numUnknowns << " numTotalParams=" << numTotalParams);

    return numUnknowns;
}

/**
 * @brief Counts the number of markers that are enabled for the given
 * attr and frame indexes.
 *
 * @return Number of enabled markers for the given attr/frame pair.
 */
Count32 countEnabledMarkersForMarkerToAttrToFrameRelationship(
    const AttrIndex attrIndex, const FrameIndex frameIndex,
    const MatrixBool3D &markerToAttrToFrameMatrix) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("countEnabledMarkersForMarkerToAttrToFrameRelationship:"
                      << " attrIndex:" << attrIndex << " frameIndex:"
                      << frameIndex << " markerToAttrToFrameMatrix.width():"
                      << markerToAttrToFrameMatrix.width()
                      << " markerToAttrToFrameMatrix.height():"
                      << markerToAttrToFrameMatrix.height()
                      << " markerToAttrToFrameMatrix.depth():"
                      << markerToAttrToFrameMatrix.depth());

    const Count32 markerCount = markerToAttrToFrameMatrix.width();
    Count32 enabledMarkers = 0;
    for (MarkerIndex markerIndex = 0; markerIndex < markerCount;
         ++markerIndex) {
        const bool enabled =
            markerToAttrToFrameMatrix.at(markerIndex, attrIndex, frameIndex);
        enabledMarkers += static_cast<Count32>(enabled);
    }

    return enabledMarkers;
}

/**
 * @brief Counts the number of attrs that are enabled for the given
 * marker and frame indexes.
 *
 * @return Number of enabled attrs for the given marker/frame pair.
 */
Count32 countEnabledAttrsForMarkerToAttrToFrameRelationship(
    const MarkerIndex markerIndex, const FrameIndex frameIndex,
    const MatrixBool3D &markerToAttrToFrameMatrix) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("countEnabledAttrsForMarkerToAttrToFrameRelationship");

    const Count32 attrCount = markerToAttrToFrameMatrix.height();
    Count32 enabledAttrs = 0;
    for (AttrIndex attrIndex = 0; attrIndex < attrCount; ++attrIndex) {
        const bool enabled =
            markerToAttrToFrameMatrix.at(markerIndex, attrIndex, frameIndex);
        enabledAttrs += static_cast<Count32>(enabled);
    }

    return enabledAttrs;
}

/**
 * @brief Counts the number of frames that are enabled for a given
 * marker and attribute indexes.
 *
 * This function traverses the relationship matrix to count how many
 * frames have a valid relationship between the specified marker and
 * attribute.
 *
 * @param markerIndex Index of the marker to check.
 * @param attrIndex Index of the attribute to check.
 * @param markerToAttrToFrameMatrix 3D matrix of marker-attribute-frame
 *        relationships.
 *
 * @return Number of enabled frames for the given marker/attribute pair.
 */
Count32 countEnabledFramesForMarkerToAttrToFrameRelationship(
    const MarkerIndex markerIndex, const AttrIndex attrIndex,
    const MatrixBool3D &markerToAttrToFrameMatrix) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("countEnabledFramesForMarkerToAttrToFrameRelationship");

    Count32 enabledFrames = 0;
    const Count32 frameCount = markerToAttrToFrameMatrix.depth();
    for (FrameIndex frameIndex = 0; frameIndex < frameCount; ++frameIndex) {
        const bool enabled =
            markerToAttrToFrameMatrix.at(markerIndex, attrIndex, frameIndex);
        enabledFrames += static_cast<Count32>(enabled);
    }

    return enabledFrames;
}

void frameListEnabledMaskForMarkerToAttrToFrameRelationship(
    const MarkerIndex markerIndex, const AttrIndex attrIndex,
    const MatrixBool3D &markerToAttrToFrameMatrix,
    ArrayMask &out_enabledFramesMask) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("frameListEnabledMaskForMarkerToAttrToFrameRelationship");

    const Count32 frameCount = markerToAttrToFrameMatrix.depth();
    MMSOLVER_ASSERT(frameCount == out_enabledFramesMask.size(),
                    "The mask must represent the same size as the frame list.");

    for (FrameIndex frameIndex = 0; frameIndex < frameCount; ++frameIndex) {
        const bool enabled =
            markerToAttrToFrameMatrix.at(markerIndex, attrIndex, frameIndex);
        out_enabledFramesMask.set(frameIndex, enabled);
    }
}

namespace {

void markFrameAffectedByAttribute(
    const MarkerIndex markerIndex, const AttrIndex attrIndex,
    const int32_t charIndex, const FrameList &frameList,
    const MString &affectsResultString,

    // Outputs
    MString &out_affectedFramesString, MStringArray &out_splitFrameStrings,
    MatrixBool3D &out_markerToAttrToFrameMatrix, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("markFrameAffectedByAttribute");

    MMSOLVER_MAYA_VRB("markFrameAffectedByAttribute: affectsResultString: \""
                      << affectsResultString << "\"");
    if (affectsResultString.length() == 0) {
        MMSOLVER_MAYA_WRN(
            "markFrameAffectedByAttribute: "
            "value is not valid; "
            "affectsResultString=\""
            << affectsResultString.asChar() << "\".");
        return;
    }

    MMSOLVER_MAYA_VRB("markFrameAffectedByAttribute: attrIndex: " << attrIndex);

    out_affectedFramesString = affectsResultString.substringW(
        charIndex + 1, static_cast<int32_t>(affectsResultString.length()) - 1);

    const int32_t commaCharIndex = out_affectedFramesString.indexW(',');
    if (commaCharIndex == -1) {
        out_splitFrameStrings.clear();
        out_splitFrameStrings.append(out_affectedFramesString);
    } else {
        out_status = out_affectedFramesString.split(',', out_splitFrameStrings);
        MMSOLVER_CHECK_MSTATUS(out_status);
        MMSOLVER_ASSERT(out_status == MS::kSuccess,
                        "Comma character is expected to exist in string; "
                        "out_affectedFramesString='"
                            << out_affectedFramesString.asChar() << "'");
    }

    for (FrameIndex frameIndex = 0;
         frameIndex < static_cast<FrameIndex>(frameList.size()); ++frameIndex) {
        const FrameNumber frameNumber = frameList.get_frame(frameIndex);

        for (Count32 j = 0; j < out_splitFrameStrings.length(); ++j) {
            MString frameMStr = out_splitFrameStrings[j];
            std::string frameStr(frameMStr.asChar());

            if (frameStr.empty()) {
                MMSOLVER_MAYA_WRN(
                    "markFrameAffectedByAttribute:"
                    "frame string value is not valid; "
                    "frameStr=\""
                    << frameStr.c_str()
                    << "\" "
                       "affectsResultString=\""
                    << affectsResultString.asChar() << "\".");
                continue;
            }

            const auto frameStringNumber =
                mmstring::stringToNumber<FrameNumber>(frameStr);
            if (frameStringNumber == frameNumber) {
                MMSOLVER_MAYA_VRB(
                    "markFrameAffectedByAttribute: Set TRUE "
                    "markerIndex="
                    << markerIndex << " attrIndex=" << attrIndex
                    << " frameIndex=" << frameIndex);
                // There is no need to set 'false', because we visit
                // each combination of indices only once, and the
                // default value of 'out_markerToAttrToFrameMatrix' is
                // false.
                out_markerToAttrToFrameMatrix.set(markerIndex, attrIndex,
                                                  frameIndex, true);
            }
        }
    }
}

/**
 * @brief Determine if the marker can affect the attribute.
 */
void parseMarkerAttributeRelationships(
    const MarkerIndex markerIndex, const AttrList &attrList,
    const FrameList &frameList, const MStringArray &bundleAffectsResult,
    const MStringArray &markerAffectsResult,

    // Outputs
    MatrixBool3D &out_markerToAttrToFrameMatrix, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("parseMarkerAttributeRelationships");

    out_status = MStatus::kSuccess;

    ArrayMask frameMask(frameList.size(), /*initial_value=*/false);

    MString affectedPlugName;
    MString affectedFramesString;
    MStringArray splitFrameStrings;
    for (AttrIndex attrIndex = 0; attrIndex < attrList.size(); attrIndex++) {
        AttrPtr attr = attrList.get_attr(attrIndex);

        // Reset frame mask.
        for (FrameIndex frameIndex = 0; frameIndex < frameList.size();
             ++frameIndex) {
            frameMask.set(frameIndex, false);
        }

        // Get attribute full path.
        MPlug plug = attr->getPlug();
        MObject attrNode = plug.node();
        MFnDagNode attrFnDagNode(attrNode);
        MString attrNodeName = attrFnDagNode.fullPathName();
        MString attrAttrName =
            plug.partialName(false, true, true, false, false, true);
        MString attrName = attrNodeName + "." + attrAttrName;

        // Example bundleAffectsResult output:
        //
        // x = nodeaffects.find_plugs_affecting_bundle("|bundle2_tfm",
        // "marker2_tfm", None, frames=[1, 2])
        // ['|bundle2_tfm.scalePivotTranslateZ#1',
        //  '|bundle2_tfm.scalePivotTranslateY#1',
        //  '|bundle2_tfm.scalePivotTranslateX#1',
        //  '|bundle2_tfm.scalePivotX#1',
        //  '|bundle2_tfm.scalePivotY#1',
        //  '|bundle2_tfm.scalePivotZ#1',
        //  ...
        //  '|bundle2_tfm.rotateY#1',
        //  '|bundle2_tfm.rotateX#1',
        //  '|bundle2_tfm.rotateZ#1',
        //  '|bundle2_tfm.scaleZ#1',
        //  '|bundle2_tfm.scaleY#1',
        //  '|bundle2_tfm.scaleX#1',
        //  '|bundle2_tfm.shearYZ#1',
        //  ...
        //  '|bundle2_tfm.translateZ#1',
        //  '|bundle2_tfm.translateY#1',
        //  '|bundle2_tfm.translateX#1',
        //  '|bundle2_tfm.shearXY#1',
        //  '|bundle2_tfm.shearXZ#1']

        // Bundle affects attribute
        for (Count32 i = 0; i < bundleAffectsResult.length(); ++i) {
            // The strings are expected to look like this:
            // "|node_parent|node1.attr#1,2,3,42"
            MMSOLVER_MAYA_VRB("Bundle affects attribute (raw): \""
                              << bundleAffectsResult[i] << "\"");

            const int32_t charIndex = bundleAffectsResult[i].indexW('#');
            MMSOLVER_ASSERT(
                charIndex > 0,
                "The character '#' is in the affects output strings.");
            affectedPlugName =
                bundleAffectsResult[i].substringW(0, charIndex - 1);
            MMSOLVER_MAYA_VRB("Bundle affects attribute      : \""
                              << affectedPlugName << "\"");

            if (attrName == affectedPlugName) {
                MMSOLVER_MAYA_VRB("Bundle markFrameAffectedByAttribute!");
                markFrameAffectedByAttribute(
                    markerIndex, attrIndex, charIndex, frameList,
                    bundleAffectsResult[i], affectedFramesString,
                    splitFrameStrings, out_markerToAttrToFrameMatrix,
                    out_status);
                if (out_status != MS::kSuccess) {
                    MMSOLVER_CHECK_MSTATUS(out_status);
                    return;
                }

                break;
            }
        }

        // Example markerAffectsResult output:
        //
        // x = nodeaffects.find_plugs_affected_by_marker("marker2_tfm",
        // "|cam_tfm", frames=[1])
        // ['|cam_tfm|marker_group|marker2_tfm.rotatePivotTranslateY#1',
        //  '|cam_tfm|marker_group|marker2_tfm.rotatePivotTranslateX#1',
        //  '|cam_tfm|marker_group|marker2_tfm.rotateAxisZ#1',
        //  '|cam_tfm|marker_group|marker2_tfm.rotatePivotTranslateZ#1',
        //  '|cam_tfm|marker_group|marker2_tfm.rotateY#1',
        //  '|cam_tfm|marker_group|marker2_tfm.rotateX#1',
        //  '|cam_tfm|marker_group.rotatePivotTranslateY#1',
        //  '|cam_tfm|marker_group|marker2_tfm.rotateAxisY#1',
        //  ... ]

        // Marker (or camera) affects attribute
        for (Count32 i = 0; i < markerAffectsResult.length(); ++i) {
            // The strings are expected to look like this:
            // "|node_parent|node1.attr#1,2,3,42"
            MMSOLVER_MAYA_VRB("Marker affects attribute (raw): \""
                              << markerAffectsResult[i] << "\"");

            const int32_t charIndex = markerAffectsResult[i].indexW('#');
            MMSOLVER_ASSERT(
                charIndex > 0,
                "The character '#' is in the affects output strings.");
            affectedPlugName =
                markerAffectsResult[i].substringW(0, charIndex - 1);
            MMSOLVER_MAYA_VRB("Marker affects attribute      : \""
                              << affectedPlugName << "\"");

            if (attrName == affectedPlugName) {
                MMSOLVER_MAYA_VRB("Marker markFrameAffectedByAttribute!");
                markFrameAffectedByAttribute(
                    markerIndex, attrIndex, charIndex, frameList,
                    markerAffectsResult[i], affectedFramesString,
                    splitFrameStrings, out_markerToAttrToFrameMatrix,
                    out_status);
                if (out_status != MS::kSuccess) {
                    MMSOLVER_CHECK_MSTATUS(out_status);
                    return;
                }

                break;
            }
        }
    }
}

}  // namespace

/**
 * @brief Determines the relationship between markers, attributes, and
 * frames using Maya's DG.
 *
 * This function uses the Maya dependency graph to analyse which
 * attributes affect which markers at specific frames. It executes
 * Python commands to query these relationships and builds a 3D
 * boolean matrix representing the connections. For each marker, it
 * finds attributes that affect its bundle and attributes that are
 * affected by the marker or its camera.
 *
 * Uses the Maya DG graph structure to determine the
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
 */
void analyseDependencyGraphRelationships(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList,

    // Outputs
    MatrixBool3D &out_markerToAttrToFrameMatrix, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("analyseDependencyGraphRelationships");

    out_status = MStatus::kSuccess;

    // Command execution options
    const bool display = false;   // print out what happens in the python
                                  // command.
    const bool undoable = false;  // we won't modify the scene in any way,
                                  // only make queries.
    MString cmd = "";
    MStringArray bundleAffectsResult = MStringArray();
    MStringArray markerAffectsResult = MStringArray();

    const std::string frame_numbers_string =
        create_string_sorted_frame_numbers_enabled(frameList);
    const MString frame_numbers_mstring = MString(frame_numbers_string.c_str());
    const FrameCount frameEnabledCount = frameList.count_enabled();
    MMSOLVER_MAYA_VRB(
        "analyseDependencyGraphRelationships: "
        "frame_numbers_string='"
        << frame_numbers_string.c_str() << "'");
    MMSOLVER_MAYA_VRB(
        "analyseDependencyGraphRelationships: "
        "frameEnabledCount="
        << frameEnabledCount);

    // The attribute's 'affect' is assumed to be false if the plug
    // cannot be found. We go by "assumed guilty until proven
    // innocent".
    const bool defaultValue = false;

    // Calculate the relationship between attributes and markers.
    out_markerToAttrToFrameMatrix.reset(markerList.size(), attrList.size(),
                                        frameList.size(),
                                        /*fill_value=*/defaultValue);
    for (MarkerIndex markerIndex = 0; markerIndex < markerList.size();
         markerIndex++) {
        MarkerPtr marker = markerList.get_marker(markerIndex);
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
        cmd += "nodeaffects.find_plugs_affecting_bundle(";
        cmd += "\"";
        cmd += bundleName;
        if (frameEnabledCount == 0) {
            // TODO: Can we add multiple cameras here?
            cmd += "\", None, None);";
        } else {
            cmd += "\", \"";
            cmd += markerName;
            cmd += "\", None, ";
            cmd += "frames=[";
            cmd += frame_numbers_mstring;
            cmd += "]);";
        }
        MMSOLVER_MAYA_VRB("analyseDependencyGraphRelationships: Running: " +
                          cmd);
        out_status = MGlobal::executePythonCommand(cmd, bundleAffectsResult,
                                                   display, undoable);
        MMSOLVER_CHECK_MSTATUS(out_status);

        // Find list of plug names that are affected by the marker
        // (and camera projection matrix).
        cmd = "";
        cmd += "import mmSolver.utils.nodeaffects as nodeaffects;";
        cmd += "nodeaffects.find_plugs_affected_by_marker(";
        cmd += "\"";
        cmd += markerName;
        cmd += "\", \"";
        cmd += camName;
        if (frameEnabledCount == 0) {
            cmd += "\");";
        } else {
            cmd += "\", ";
            cmd += "frames=[";
            cmd += frame_numbers_mstring;
            cmd += "]);";
        }

        MMSOLVER_MAYA_VRB("analyseDependencyGraphRelationships: Running: " +
                          cmd);
        out_status = MGlobal::executePythonCommand(cmd, markerAffectsResult,
                                                   display, undoable);
        MMSOLVER_CHECK_MSTATUS(out_status);

        parseMarkerAttributeRelationships(
            markerIndex, attrList, frameList, bundleAffectsResult,
            markerAffectsResult,

            // Outputs
            out_markerToAttrToFrameMatrix, out_status);
        if (out_status != MS::kSuccess) {
            MMSOLVER_CHECK_MSTATUS(out_status);
            return;
        }
    }
}

/**
 * @brief Determines the relationship between markers, attributes, and
 * frames using only known details of the objects, and does not
 * evaluate Maya's DG.
 *
 * This is a simplified (and therefore less accurate) than the
 * `analyseDependencyGraphRelationships()` function. This function can
 * be used in cases where it is known that the Maya DG does not need
 * to be evaluated in order to determine the "sparsity structure" of
 * the scene graph to be solved.
 */
void analyseObjectRelationships(const MarkerList &markerList,
                                const AttrList &attrList,
                                const FrameList &frameList,

                                // Outputs
                                MatrixBool3D &out_markerToAttrToFrameMatrix,
                                MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("analyseObjectRelationships");

    out_status = MStatus::kSuccess;

    const std::string frame_numbers_string =
        create_string_sorted_frame_numbers_enabled(frameList);
    const MString frame_numbers_mstring = MString(frame_numbers_string.c_str());
    const FrameCount frameEnabledCount = frameList.count_enabled();
    MMSOLVER_MAYA_VRB(
        "analyseObjectRelationships: "
        "frame_numbers_string='"
        << frame_numbers_string.c_str() << "'");
    MMSOLVER_MAYA_VRB(
        "analyseObjectRelationships: "
        "frameEnabledCount="
        << frameEnabledCount);

    const auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    const auto uiUnit = MTime::uiUnit();

    // The attribute's 'affect' is assumed to be false if the plug
    // cannot be found. We go by "assumed guilty until proven
    // innocent".
    const bool defaultValue = false;

    MatrixBool2D markerToAttrMatrix;
    markerToAttrMatrix.reset(markerList.size(), attrList.size(),
                             /*fill_value=*/defaultValue);
    for (MarkerIndex markerIndex = 0; markerIndex < markerList.size();
         markerIndex++) {
        MarkerPtr marker = markerList.get_marker(markerIndex);
        CameraPtr cam = marker->getCamera();
        BundlePtr bundle = marker->getBundle();
        const MString bundleNodeName = bundle->getNodeName();
        // const char *bundleName = bundleNodeName.asChar();

        for (AttrIndex attrIndex = 0; attrIndex < attrList.size();
             attrIndex++) {
            AttrPtr attr = attrList.get_attr(attrIndex);

            MPlug plug = attr->getPlug();
            MObject attrNode = plug.node();
            MFnDagNode attrFnDagNode(attrNode);
            MString attrNodeName = attrFnDagNode.fullPathName();

            bool value = false;
            if (bundleNodeName == attrNodeName) {
                value = true;
            } else {
                MObject nodeObj = attr->getObject();
                value = nodeIsCameraType(nodeObj);
            }

            markerToAttrMatrix.set(markerIndex, attrIndex, value);
        }
    }

    // Calculate the relationship between attributes and markers.append
    out_markerToAttrToFrameMatrix.reset(markerList.size(), attrList.size(),
                                        frameList.size(),
                                        /*fill_value=*/defaultValue);
    for (MarkerIndex markerIndex = 0; markerIndex < markerList.size();
         markerIndex++) {
        MarkerPtr marker = markerList.get_marker(markerIndex);

        for (FrameIndex frameIndex = 0; frameIndex < frameList.size();
             frameIndex++) {
            const FrameNumber markerFrameNumber =
                frameList.get_frame(frameIndex);
            const MTime markerFrame =
                convert_to_time(markerFrameNumber, uiUnit);

            bool enable = false;
            double weight = 0.0;
            const bool markerIsEnabled = getMarkerIsEnabled(
                marker, markerFrame, timeEvalMode, enable, weight);

            if (!markerIsEnabled) {
                // All attributes must be unaffected by this marker.
                continue;
            }

            for (AttrIndex attrIndex = 0; attrIndex < attrList.size();
                 attrIndex++) {
                const bool markerAffectsAttr =
                    markerToAttrMatrix.at(markerIndex, attrIndex);

                out_markerToAttrToFrameMatrix.set(
                    markerIndex, attrIndex, frameIndex,
                    markerIsEnabled || markerAffectsAttr);
            }
        }
    }
}

/**
 * @brief Reads pre-computed marker-attribute-frame relationships from
 * Maya nodes.
 *
 * This function assumes that marker nodes have attributes storing
 * their relationships with solver attributes (created by
 * 'mmSolverAffects' with the 'addAttrsToMarkers' flag). It reads
 * these attributes for each marker/attribute pair and builds a 3D
 * boolean matrix representing the connections.
 *
 * Read the relationship of Marker to Attributes to Frame from parsing
 * the given Markers/Attributes directly on specific frames.
 *
 * This function assumes the use of 'mmSolverAffects' with the
 * 'addAttrsToMarkers' mode flag has already been run.
 */
void readStoredRelationships(const MarkerList &markerList,
                             const AttrList &attrList,
                             const FrameList &frameList,

                             // Outputs
                             Count32 &out_relationshipAttrsExistCount,
                             MatrixBool3D &out_markerToAttrToFrameMatrix,
                             MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("readStoredRelationships");

    MMSOLVER_MAYA_VRB(
        "readStoredRelationships: "
        "markerList.count_enabled()="
        << markerList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "readStoredRelationships: "
        "markerList.count_disabled()="
        << markerList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "readStoredRelationships: "
        "attrList.count_enabled()="
        << attrList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "readStoredRelationships: "
        "attrList.count_disabled()="
        << attrList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "readStoredRelationships: "
        "frameList.count_enabled()="
        << frameList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "readStoredRelationships: "
        "frameList.count_disabled()="
        << frameList.count_disabled());

    out_status = MStatus::kSuccess;
    out_relationshipAttrsExistCount = 0;

    // The attribute's 'affect' is assumed to be false if the plug
    // cannot be found. We go by "assumed guilty until proven
    // innocent".
    const bool defaultValue = false;

    // Calculate the relationship between markers, attributes and
    // frames.
    out_markerToAttrToFrameMatrix.reset(markerList.size(), attrList.size(),
                                        frameList.size(),
                                        /*fill_value=*/defaultValue);

    for (MarkerIndex markerIndex = 0; markerIndex != markerList.size();
         ++markerIndex) {
        MarkerPtr marker = markerList.get_marker(markerIndex);
        MObject markerObject = marker->getObject();
        MFnDependencyNode markerNodeFn(markerObject);

        // Determine if the marker can affect the attribute.
        for (AttrIndex attrIndex = 0; attrIndex < attrList.size();
             ++attrIndex) {
            AttrPtr attr = attrList.get_attr(attrIndex);

            // Get Attribute's Node Name.
            MObject attrNodeObject = attr->getObject();
            MFnDependencyNode attrNodeFn(attrNodeObject);
            MObject attrObject = attr->getAttribute();
            MUuid attrUuid = attrNodeFn.uuid(&out_status);
            MMSOLVER_CHECK_MSTATUS(out_status);
            MString attrUuidStr = attrUuid.asString();

            // Get Attribute's Name.
            MFnAttribute attrAttrFn(attrObject);
            MString nodeAttrName = attrAttrFn.name();

            // Calculate the naming format that is expected to be on
            // the Marker transform node.
            MString attrName = "";
            out_status =
                constructAttrAffectsName(nodeAttrName, attrUuidStr, attrName);
            MMSOLVER_CHECK_MSTATUS(out_status);

            // Get plug value
            bool value = defaultValue;
            MPlug plug = markerNodeFn.findPlug(
                attrName, /*wantNetworkedPlug=*/true, &out_status);
            if (out_status != MS::kSuccess) {
                if (verbose) {
                    MMSOLVER_CHECK_MSTATUS(out_status);
                    const MString markerNodeName = marker->getNodeName();
                    MMSOLVER_MAYA_VRB(
                        "readStoredRelationships: "
                        "invalid marker MPlug;\n"
                        "- markerNodeName=\""
                        << markerNodeName.asChar()
                        << "\"\n"
                           "- nodeAttrName=\""
                        << nodeAttrName.asChar()
                        << "\"\n"
                           "- attrUuidStr=\""
                        << attrUuidStr.asChar()
                        << "\"\n"
                           "- attrName=\""
                        << attrName.asChar() << "\";");
                }
                continue;
            }

            const bool attrExists = plug.isNull() == false;
            out_relationshipAttrsExistCount += static_cast<Count32>(attrExists);
            if (attrExists) {
                MMSOLVER_MAYA_VRB(
                    "readStoredRelationships: "
                    "attrExists! "
                    << attrExists);

                // Evaluate animated or static value; connected
                // attributes are not supported for performance
                // reasons.
                MFnAnimCurve curveFn(plug, &out_status);
                if (out_status == MS::kSuccess) {
                    // Plug is assumed to be animated with an
                    // animCurve.
                    for (FrameIndex frameIndex = 0;
                         frameIndex < static_cast<FrameIndex>(frameList.size());
                         ++frameIndex) {
                        const FrameNumber frameNumber =
                            frameList.get_frame(frameIndex);
                        const MTime frame = convert_to_time(frameNumber);

                        double curveValue = 0;
                        out_status = curveFn.evaluate(frame, curveValue);
                        if (out_status != MS::kSuccess) {
                            MMSOLVER_CHECK_MSTATUS(out_status);
                            return;
                        }

                        const auto integer_value =
                            static_cast<int32_t>(curveValue);
                        const auto affects_state =
                            static_cast<MarkerAttrAffectsState>(integer_value);
                        value = affects_state == MarkerAttrAffectsState::kUsed;

                        MMSOLVER_MAYA_VRB(
                            "readStoredRelationships: ANIMATED "
                            "markerIndex="
                            << markerIndex << " attrIndex=" << attrIndex
                            << " frameIndex=" << frameIndex << " integer_value="
                            << integer_value << " value=" << value);

                        out_markerToAttrToFrameMatrix.set(
                            markerIndex, attrIndex, frameIndex, value);
                    }
                } else {
                    // A static value is available.
                    out_status = MS::kSuccess;
                    const int32_t integer_value = plug.asInt();
                    const MarkerAttrAffectsState affects_state =
                        static_cast<MarkerAttrAffectsState>(integer_value);
                    value = affects_state == MarkerAttrAffectsState::kUsed;

                    MMSOLVER_MAYA_VRB(
                        "readStoredRelationships: STATIC "
                        "markerIndex="
                        << markerIndex << " attrIndex=" << attrIndex
                        << " integer_value=" << integer_value
                        << " value=" << value);

                    for (FrameIndex frameIndex = 0;
                         frameIndex < static_cast<FrameIndex>(frameList.size());
                         ++frameIndex) {
                        out_markerToAttrToFrameMatrix.set(
                            markerIndex, attrIndex, frameIndex, value);
                    }
                }
            }
        }
    }

    MMSOLVER_MAYA_VRB(
        "readStoredRelationships: "
        "out_relationshipAttrsExistCount="
        << out_relationshipAttrsExistCount);
}

/**
 * @brief Calculates the relationship between errors and parameters.
 *
 * This function maps which errors (marker deviations) are affected by
 * which parameters (attribute values). It uses the
 * marker-attribute-frame relationship matrix to determine these
 * connections, taking into account whether attributes are static or
 * animated, and matching time values properly.
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
 * markerToAttrToFrameMatrix is already true, otherwise we can assume
 * such error/parameter combinations will not be required.
 */
void mapErrorsToParameters(const MarkerList &markerList,
                           const AttrList &attrList, const FrameList &frameList,
                           const Count32 numParameters,
                           const Count32 numMarkerErrors,
                           const IndexPairList &paramToAttrList,
                           const IndexPairList &errorToMarkerList,
                           const MatrixBool3D &markerToAttrToFrameMatrix,

                           // Outputs
                           MatrixBool2D &out_errorToParamMatrix,
                           MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("mapErrorsToParameters");

    out_status = MStatus::kSuccess;

    MMSOLVER_ASSERT(
        markerToAttrToFrameMatrix.width() == markerList.size(),
        "markerToAttrToFrameMatrix data structure is expected to be "
        "consistent with the markerList size; "
        "markerToAttrToFrameMatrix.width()="
            << markerToAttrToFrameMatrix.width()
            << " markerList.size()=" << markerList.size());
    MMSOLVER_ASSERT(
        markerToAttrToFrameMatrix.height() == attrList.size(),
        "markerToAttrToFrameMatrix data structure is expected to be "
        "consistent with the attrList size;"
        "markerToAttrToFrameMatrix.height()="
            << markerToAttrToFrameMatrix.height()
            << " attrList.size()=" << attrList.size());
    MMSOLVER_ASSERT(
        markerToAttrToFrameMatrix.depth() == frameList.size(),
        "markerToAttrToFrameMatrix data structure is expected to be "
        "consistent with the frameList size;"
        "markerToAttrToFrameMatrix.depth()="
            << markerToAttrToFrameMatrix.depth()
            << " frameList.size()=" << frameList.size());

    const auto timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    const auto uiUnit = MTime::uiUnit();

    // Attributes are assumed not to affect any marker, until
    // proven otherwise.
    const bool defaultValue = false;

    const Count32 numberOfMarkers = numMarkerErrors / ERRORS_PER_MARKER;
    out_errorToParamMatrix.reset(numberOfMarkers, numParameters,
                                 /*fill_value=*/defaultValue);
    for (ErrorIndex errorIndex = 0; errorIndex < numberOfMarkers;
         ++errorIndex) {
        const IndexPair markerIndexPair = errorToMarkerList[errorIndex];
        const MarkerIndex markerIndex = markerIndexPair.first;
        const FrameIndex markerFrameIndex = markerIndexPair.second;

        const bool mkrEnabled = markerList.get_enabled(markerIndex);
        if (!mkrEnabled) {
            continue;
        }

        MarkerPtr marker = markerList.get_marker(markerIndex);
        const FrameNumber markerFrameNumber =
            frameList.get_frame(markerFrameIndex);
        const MTime markerFrame = convert_to_time(markerFrameNumber, uiUnit);

        // TODO: Can we compute this value once per markerList and
        // per-frame and then re-use it?
        bool enable = false;
        double weight = 0.0;
        const bool markerIsEnabled = getMarkerIsEnabled(
            marker, markerFrame, timeEvalMode, enable, weight);

        if (!markerIsEnabled) {
            // All parameters must be unaffected by this marker.
            continue;
        }

        // Determine if the marker can affect the attribute.
        for (ParamIndex paramIndex = 0; paramIndex < numParameters;
             ++paramIndex) {
            const IndexPair attrIndexPair = paramToAttrList[paramIndex];

            const AttrIndex attrIndex = attrIndexPair.first;
            const FrameIndex attrFrameIndex = attrIndexPair.second;

            const bool attrEnabled = attrList.get_enabled(attrIndex);

            bool paramAffectsError = false;

            // If the attrFrameIndex is -1, then the attribute is
            // static, not animated.
            FrameNumber attrFrameNumber = -1;
            bool frameEnabled = false;
            if (attrFrameIndex >= 0) {
                frameEnabled = frameList.get_enabled(attrFrameIndex);
                attrFrameNumber = frameList.get_frame(attrFrameIndex);
            } else {
                const auto enabledCount =
                    countEnabledFramesForMarkerToAttrToFrameRelationship(
                        markerIndex, attrIndex, markerToAttrToFrameMatrix);
                frameEnabled = enabledCount > 0;
            }
            paramAffectsError = attrEnabled && frameEnabled;

            if (paramAffectsError) {
                // Time based mapping information.
                // Only markers on the current frame can affect the current
                // attribute.
                if (attrFrameIndex >= 0) {
                    paramAffectsError = markerFrameNumber == attrFrameNumber;
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
}

void calculateMarkerAndParameterCountAllFramesAtOnce(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList, const Count32 numParameters,
    const Count32 numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const MatrixBool3D &markerToAttrToFrameMatrix,

    // Outputs
    FrameList &out_validFrameList, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountAllFramesAtOnce");

    out_status = MStatus::kSuccess;

    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountAllFramesAtOnce: A");

    Count32 totalErrorCount = 0;
    const Count32 frameCount = frameList.size();
    for (FrameIndex frameIndex = 0; frameIndex < frameCount; ++frameIndex) {
        const FrameNumber frameNumber = frameList.get_frame(frameIndex);

        Count32 markerEnabledCount = 0;
        for (MarkerIndex markerIndex = 0;
             markerIndex < markerToAttrToFrameMatrix.width(); ++markerIndex) {
            const Count32 enabledAttrs =
                countEnabledAttrsForMarkerToAttrToFrameRelationship(
                    markerIndex, frameIndex, markerToAttrToFrameMatrix);
            markerEnabledCount += static_cast<uint32_t>(enabledAttrs > 0);

            MMSOLVER_MAYA_VRB(
                "calculateMarkerAndParameterCountAllFramesAtOnce: A"
                " markerIndex="
                << markerIndex << " frameIndex=" << frameIndex
                << " enabledAttrs=" << static_cast<bool>(enabledAttrs));
        }

        const Count32 errorCount = markerEnabledCount * ERRORS_PER_MARKER;
        totalErrorCount += errorCount;
    }

    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountAllFramesAtOnce: B");

    // For all-frames mode, count both static and animated
    // parameters.
    Count32 totalParamCount = 0;

    // Reused in the loop. Allocated outside the loop to avoid
    // allocations.
    ArrayMask enabledFramesMask(frameList.size(), /*initial_value=*/false);

    const Count32 markerCount = markerToAttrToFrameMatrix.width();
    for (AttrIndex attrIndex = 0; attrIndex < attrList.size(); ++attrIndex) {
        const AttrPtr attr = attrList.get_attr(attrIndex);

        const bool attr_is_frame_to_change = attr->isFreeToChange();
        const bool attr_is_animated = attr->isAnimated();
        MMSOLVER_MAYA_VRB(
            "calculateMarkerAndParameterCountAllFramesAtOnce:"
            " attrIndex="
            << attrIndex
            << " | attr_is_free_to_change=" << attr_is_frame_to_change
            << " attr_is_animated=" << attr_is_animated);

        if (attr_is_animated) {
            enabledFramesMask.set_all(false);
            for (MarkerIndex markerIndex = 0; markerIndex < markerCount;
                 ++markerIndex) {
                frameListEnabledMaskForMarkerToAttrToFrameRelationship(
                    markerIndex, attrIndex, markerToAttrToFrameMatrix,
                    enabledFramesMask);
            }
            const Count32 enabledFrameCount = enabledFramesMask.count_enabled();

            MMSOLVER_MAYA_VRB(
                "calculateMarkerAndParameterCountAllFramesAtOnce:"
                " attrIndex="
                << attrIndex
                << " | ANIMATED enabledFrameCount=" << enabledFrameCount);

            totalParamCount += enabledFrameCount;
        } else if (attr_is_frame_to_change) {
            Count32 enabledFrameCount = 0;
            for (MarkerIndex markerIndex = 0; markerIndex < markerCount;
                 ++markerIndex) {
                enabledFrameCount +=
                    countEnabledFramesForMarkerToAttrToFrameRelationship(
                        markerIndex, attrIndex, markerToAttrToFrameMatrix);
            }

            MMSOLVER_MAYA_VRB(
                "calculateMarkerAndParameterCountAllFramesAtOnce:"
                " attrIndex="
                << attrIndex << " | STATIC enabledFrames="
                << static_cast<bool>(enabledFrameCount));

            // Because as long as one frame affects a static
            // parameter, then it's considered valid.
            totalParamCount += static_cast<Count32>(enabledFrameCount > 0);
        }
    }

    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountAllFramesAtOnce: C");

    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCountAllFramesAtOnce: "
        "totalErrorCount="
        << totalErrorCount);
    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCountAllFramesAtOnce: "
        "totalParamCount="
        << totalParamCount);

    // Determine valid/invalid frames.
    for (FrameIndex frameIndex = 0; frameIndex < frameCount; ++frameIndex) {
        const bool frame_is_valid = totalErrorCount >= totalParamCount;
        out_validFrameList.set_enabled(frameIndex, frame_is_valid);
    }

    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountAllFramesAtOnce: D");
}

void calculateMarkerAndParameterCountPerFrame(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList, const Count32 numParameters,
    const Count32 numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const MatrixBool3D &markerToAttrToFrameMatrix,

    // Outputs
    FrameList &out_validFrameList, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountPerFrame");

    out_status = MStatus::kSuccess;

    // Calculate parameter counts.
    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountPerFrame: A");

    Count32 totalErrorCount = 0;
    const Count32 frameCount = frameList.size();
    std::unordered_map<int32_t, uint32_t> errorCountPerFrame;
    for (FrameIndex frameIndex = 0; frameIndex < frameCount; ++frameIndex) {
        MMSOLVER_MAYA_VRB(
            "calculateMarkerAndParameterCountPerFrame: A frameIndex="
            << frameIndex);

        const FrameNumber frameNumber = frameList.get_frame(frameIndex);

        Count32 markerEnabledCount = 0;
        for (AttrIndex attrIndex = 0;
             attrIndex < markerToAttrToFrameMatrix.height(); ++attrIndex) {
            MMSOLVER_MAYA_VRB(
                "calculateMarkerAndParameterCountPerFrame: A attrIndex="
                << attrIndex);

            for (MarkerIndex markerIndex = 0;
                 markerIndex < markerToAttrToFrameMatrix.width();
                 ++markerIndex) {
                MMSOLVER_MAYA_VRB(
                    "calculateMarkerAndParameterCountPerFrame: A "
                    "markerIndex="
                    << markerIndex);

                const bool enabled = markerToAttrToFrameMatrix.at(
                    markerIndex, attrIndex, frameIndex);
                markerEnabledCount += static_cast<uint32_t>(enabled);

                MMSOLVER_MAYA_VRB(
                    "calculateMarkerAndParameterCountPerFrame: A"
                    " markerIndex="
                    << markerIndex << " attrIndex=" << attrIndex
                    << " frameIndex=" << frameIndex << " enabled=" << enabled);
            }
        }

        const Count32 errorCount = markerEnabledCount * ERRORS_PER_MARKER;
        errorCountPerFrame[frameNumber] = errorCount;
        totalErrorCount += errorCount;
    }

    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountPerFrame: B");

    // For per-frame mode, only count animated parameters.
    std::unordered_map<FrameIndex, Count32> paramCountPerFrame;
    for (FrameIndex frameIndex = 0; frameIndex < frameCount; ++frameIndex) {
        const FrameNumber frameNumber = frameList.get_frame(frameIndex);

        Count32 frameParamCount = 0;
        for (AttrIndex attrIndex = 0; attrIndex < attrList.size();
             ++attrIndex) {
            const AttrPtr attr = attrList.get_attr(attrIndex);

            const bool attr_is_frame_to_change = attr->isFreeToChange();
            const bool attr_is_animated = attr->isAnimated();
            MMSOLVER_MAYA_VRB(
                "calculateMarkerAndParameterCountPerFrame:"
                " frame="
                << frameNumber << " | attrIndex=" << attrIndex
                << " | attr_is_free_to_change=" << attr_is_frame_to_change);
            MMSOLVER_MAYA_VRB(
                "calculateMarkerAndParameterCountPerFrame:"
                " frame="
                << frameNumber << " | attrIndex=" << attrIndex
                << " | attr_is_animated=" << attr_is_animated);

            if (attr_is_frame_to_change || attr_is_animated) {
                frameParamCount++;
            }
        }
        paramCountPerFrame[frameNumber] = frameParamCount;
    }

    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountPerFrame: C");

    // Determine valid/invalid frames.
    for (FrameIndex frameIndex = 0; frameIndex < frameCount; ++frameIndex) {
        const FrameNumber frameNumber = frameList.get_frame(frameIndex);

        const Count32 errorCount = errorCountPerFrame[frameNumber];
        const Count32 paramCount = paramCountPerFrame[frameNumber];

        MMSOLVER_MAYA_VRB(
            "calculateMarkerAndParameterCountPerFrame: "
            "frame="
            << frameNumber << " | errorCount=" << errorCount);
        MMSOLVER_MAYA_VRB(
            "calculateMarkerAndParameterCountPerFrame: "
            "frame="
            << frameNumber << " | paramCount=" << paramCount);

        const bool frame_is_valid = errorCount >= paramCount;
        out_validFrameList.set_enabled(frameIndex, frame_is_valid);
    }

    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCountPerFrame: D");
}

/**
 * @brief Determines which frames are valid for solving.
 *
 * This function analyses the marker-attribute-frame relationships to
 * determine which frames have sufficient constraints for solving. A
 * frame is valid if the number of errors (constraints) is greater
 * than or equal to the number of parameters (unknowns) at that
 * frame. The validation strategy differs based on the frame solve
 * mode.
 *
 * @param markerList List of markers generating errors.
 * @param attrList List of attributes used as parameters.
 * @param frameList List of frames to evaluate.
 * @param numParameters Number of parameters in the solve.
 * @param numMarkerErrors Number of marker-related errors.
 * @param paramToAttrList Mapping from parameter index to attribute/frame
 * pairs.
 * @param errorToMarkerList Mapping from error index to marker/frame pairs.
 * @param markerToAttrToFrameMatrix 3D matrix of marker-attribute-frame
 *        relationships.
 * @param frameSolveMode Mode determining how frames are solved (all at once
 * or per frame).
 * @param out_validFrameList Output frame list with enabled/disabled states.
 * @param out_status Maya status code, set to failure if any operation
 * fails.
 */
void calculateMarkerAndParameterCount(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList, const Count32 numParameters,
    const Count32 numMarkerErrors, const IndexPairList &paramToAttrList,
    const IndexPairList &errorToMarkerList,
    const MatrixBool3D &markerToAttrToFrameMatrix,
    const FrameSolveMode frameSolveMode,

    // Outputs
    FrameList &out_validFrameList, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCount");

    out_status = MStatus::kSuccess;

    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "markerList.size()="
        << markerList.size());
    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "markerList.count_enabled()="
        << markerList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "markerList.count_disabled()="
        << markerList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "attrList.size()="
        << attrList.size());
    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "attrList.count_enabled()="
        << attrList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "attrList.count_disabled()="
        << attrList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "frameList.size()="
        << frameList.size());
    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "frameList.count_enabled()="
        << frameList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "frameList.count_disabled()="
        << frameList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "markerToAttrToFrameMatrix.width()="
        << markerToAttrToFrameMatrix.width());
    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "markerToAttrToFrameMatrix.height()="
        << markerToAttrToFrameMatrix.height());
    MMSOLVER_MAYA_VRB(
        "calculateMarkerAndParameterCount: "
        "markerToAttrToFrameMatrix.depth()="
        << markerToAttrToFrameMatrix.depth());

    MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCount: A");

    MMSOLVER_ASSERT(
        markerToAttrToFrameMatrix.width() == markerList.size(),
        "markerToAttrToFrameMatrix data structure is expected to be "
        "consistent with the markerList size; "
        "markerToAttrToFrameMatrix.width()="
            << markerToAttrToFrameMatrix.width()
            << " markerList.size()=" << markerList.size());
    MMSOLVER_ASSERT(
        markerToAttrToFrameMatrix.height() == attrList.size(),
        "markerToAttrToFrameMatrix data structure is expected to be "
        "consistent with the attrList size;"
        "markerToAttrToFrameMatrix.height()="
            << markerToAttrToFrameMatrix.height()
            << " attrList.size()=" << attrList.size());
    MMSOLVER_ASSERT(
        markerToAttrToFrameMatrix.depth() == frameList.size(),
        "markerToAttrToFrameMatrix data structure is expected to be "
        "consistent with the frameList size;"
        "markerToAttrToFrameMatrix.depth()="
            << markerToAttrToFrameMatrix.depth()
            << " frameList.size()=" << frameList.size());

    // Calculate parameter counts.
    if (frameSolveMode == FrameSolveMode::kAllFrameAtOnce) {
        MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCount: C0");
        calculateMarkerAndParameterCountAllFramesAtOnce(
            markerList, attrList, frameList, numParameters, numMarkerErrors,
            paramToAttrList, errorToMarkerList, markerToAttrToFrameMatrix,
            out_validFrameList, out_status);
        MMSOLVER_CHECK_MSTATUS(out_status);
    } else if (frameSolveMode == FrameSolveMode::kPerFrame) {
        MMSOLVER_MAYA_VRB("calculateMarkerAndParameterCount: D0");
        calculateMarkerAndParameterCountPerFrame(
            markerList, attrList, frameList, numParameters, numMarkerErrors,
            paramToAttrList, errorToMarkerList, markerToAttrToFrameMatrix,
            out_validFrameList, out_status);
        MMSOLVER_CHECK_MSTATUS(out_status);
    } else {
        const auto frameSolveModeValue = static_cast<int32_t>(frameSolveMode);
        MMSOLVER_MAYA_ERR(
            "calculateMarkerAndParameterCount: "
            "Invalid 'frameSolveMode' value;"
            << frameSolveModeValue);
        MMSOLVER_PANIC("Invalid 'frameSolveMode' value: frameSolveMode="
                       << frameSolveModeValue);
    }
}

/**
 * @brief Generates lists of valid markers, attributes, and frames.
 *
 * This function analyses the marker-attribute-frame relationships to
 * identify which markers, attributes, and frames are actually used in
 * the solve process.  It marks elements as enabled if they
 * participate in at least one valid relationship.
 */
void generateValidMarkerAttrFrameLists(
    const MarkerList &markerList, const AttrList &attrList,
    const FrameList &frameList, const MatrixBool3D &markerToAttrToFrameMatrix,

    // Outputs
    MarkerList &out_validMarkerList, AttrList &out_validAttrList,
    FrameList &out_validFrameList, MStatus &out_status) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("generateMarkerAttrFrameLists");

    out_status = MStatus::kSuccess;

    MMSOLVER_ASSERT(
        (markerToAttrToFrameMatrix.width() == markerList.size()),
        "markerToAttrToFrameMatrix data structure is expected to be "
        "consistent with the markerList size.");
    MMSOLVER_ASSERT(
        (markerToAttrToFrameMatrix.height() == attrList.size()),
        "markerToAttrToFrameMatrix data structure is expected to be "
        "consistent with the attrList size.");
    MMSOLVER_ASSERT(
        (markerToAttrToFrameMatrix.depth() == frameList.size()),
        "markerToAttrToFrameMatrix data structure is expected to be "
        "consistent with the frameList size.");

    out_validMarkerList = MarkerList(markerList);
    out_validAttrList = AttrList(attrList);
    out_validFrameList = FrameList(frameList);

    MMSOLVER_MAYA_VRB("generateMarkerAttrFrameLists: A");

    const Count32 markerCount = markerToAttrToFrameMatrix.width();
    const Count32 attrCount = markerToAttrToFrameMatrix.height();
    const Count32 frameCount = markerToAttrToFrameMatrix.depth();

    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: "
        "markerCount="
        << markerCount);
    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: "
        "attrCount="
        << attrCount);
    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: "
        "frameCount="
        << frameCount);

    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: BEFORE "
        "out_validMarkerList.count_enabled()="
        << out_validMarkerList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: BEFORE "
        "out_validMarkerList.count_disabled()="
        << out_validMarkerList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: BEFORE "
        "out_validAttrList.count_enabled()="
        << out_validAttrList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: BEFORE "
        "out_validAttrList.count_disabled()="
        << out_validAttrList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: BEFORE "
        "out_validFrameList.count_enabled()="
        << out_validFrameList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: BEFORE "
        "out_validFrameList.count_disabled()="
        << out_validFrameList.count_disabled());

    // A Marker is valid if at least one attribute is affected by it
    // on at least one frame.
    for (MarkerIndex markerIndex = 0; markerIndex < markerCount;
         ++markerIndex) {
        Count32 enabledAttrs = 0;
        for (AttrIndex attrIndex = 0; attrIndex < attrCount; ++attrIndex) {
            Count32 enabledFrames = 0;
            for (FrameIndex frameIndex = 0; frameIndex < frameCount;
                 ++frameIndex) {
                const bool enabledFrame = markerToAttrToFrameMatrix.at(
                    markerIndex, attrIndex, frameIndex);
                enabledFrames += static_cast<Count32>(enabledFrame);
            }

            const bool enabledAttr = enabledFrames > 0;
            enabledAttrs += static_cast<Count32>(enabledAttr);
        }

        const bool enabledMarker = enabledAttrs > 0;
        out_validMarkerList.set_enabled(markerIndex, enabledMarker);
    }

    // An Attribute is valid if at least one marker affects it on at
    // least one frame.
    for (AttrIndex attrIndex = 0; attrIndex < attrCount; ++attrIndex) {
        Count32 enabledMarkers = 0;
        for (MarkerIndex markerIndex = 0; markerIndex < markerCount;
             ++markerIndex) {
            Count32 enabledFrames = 0;
            for (FrameIndex frameIndex = 0; frameIndex < frameCount;
                 ++frameIndex) {
                const bool enabledFrame = markerToAttrToFrameMatrix.at(
                    markerIndex, attrIndex, frameIndex);
                enabledFrames += static_cast<Count32>(enabledFrame);
            }

            const bool enabledMarker = enabledFrames > 0;
            enabledMarkers += static_cast<Count32>(enabledMarker);
        }

        const bool enabledAttr = enabledMarkers > 0;
        out_validAttrList.set_enabled(attrIndex, enabledAttr);
    }

    // A Frame is valid if at least one attribute is affected by one
    // marker on the frame.
    for (FrameIndex frameIndex = 0; frameIndex < frameCount; ++frameIndex) {
        Count32 enabledMarkers = 0;
        for (MarkerIndex markerIndex = 0; markerIndex < markerCount;
             ++markerIndex) {
            Count32 enabledAttrs = 0;
            for (AttrIndex attrIndex = 0; attrIndex < attrCount; ++attrIndex) {
                const bool enabledAttr = markerToAttrToFrameMatrix.at(
                    markerIndex, attrIndex, frameIndex);
                enabledAttrs += static_cast<Count32>(enabledAttr);
            }

            const bool enabledMarker = enabledAttrs > 0;
            enabledMarkers += static_cast<Count32>(enabledMarker);
        }

        const bool enabledFrame = enabledMarkers > 0;
        out_validFrameList.set_enabled(frameIndex, enabledFrame);
    }

    MMSOLVER_MAYA_VRB("generateMarkerAttrFrameLists: B");

    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: AFTER "
        "out_validMarkerList.count_enabled()="
        << out_validMarkerList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: AFTER "
        "out_validMarkerList.count_disabled()="
        << out_validMarkerList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: AFTER "
        "out_validAttrList.count_enabled()="
        << out_validAttrList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: AFTER "
        "out_validAttrList.count_disabled()="
        << out_validAttrList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: AFTER "
        "out_validFrameList.count_enabled()="
        << out_validFrameList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "generateMarkerAttrFrameLists: AFTER "
        "out_validFrameList.count_disabled()="
        << out_validFrameList.count_disabled());
}

}  // namespace mmsolver
