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
 * Sets up the Bundle Adjustment data and sends it off to the bundling algorithm.
 *
 */

// STL
#include <ctime>
#include <cmath>
#include <iostream>
#include <fstream>
#include <string>
#include <vector>
#include <cassert>
#include <limits>
#include <algorithm>
#include <cstdlib>

// Utils
#include <utilities/debugUtils.h>
#include <utilities/stringUtils.h>
#include <utilities/numberUtils.h>

// Maya
#include <maya/MGlobal.h>
#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MSelectionList.h>
#include <maya/MItDependencyGraph.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MMatrix.h>
#include <maya/MFloatMatrix.h>
#include <maya/MFnCamera.h>
#include <maya/MComputation.h>
#include <maya/MProfiler.h>

// Local
#include <core/bundleAdjust_base.h>
#include <core/bundleAdjust_levmar_bc_dif.h>
#include <core/bundleAdjust_cminpack_base.h>
#include <core/bundleAdjust_cminpack_lmdif.h>
#include <core/bundleAdjust_cminpack_lmder.h>
#include <core/bundleAdjust_solveFunc.h>
#include <mayaUtils.h>


// Get a list of all available solver types (index and name).
//
// This list may change in different plug-ins, as the compiled
// dependencies may differ.
std::vector<SolverTypePair> getSolverTypes() {
    std::vector<std::pair<int, std::string> > solverTypes;
    std::pair<int, std::string> solverType;
#ifdef USE_SOLVER_LEVMAR
    solverType.first = SOLVER_TYPE_LEVMAR;
    solverType.second = SOLVER_TYPE_LEVMAR_NAME;
    solverTypes.push_back(solverType);
#endif

#ifdef USE_SOLVER_CMINPACK
    solverType.first = SOLVER_TYPE_CMINPACK_LMDIF;
    solverType.second = SOLVER_TYPE_CMINPACK_LM_DIF_NAME;
    solverTypes.push_back(solverType);

    solverType.first = SOLVER_TYPE_CMINPACK_LMDER;
    solverType.second = SOLVER_TYPE_CMINPACK_LM_DER_NAME;
    solverTypes.push_back(solverType);
#endif
    return solverTypes;
}


// Determine the default solver.
SolverTypePair getSolverTypeDefault() {
    int solverTypeIndex = SOLVER_TYPE_DEFAULT_VALUE;
    std::string solverTypeName = "";

    std::vector<SolverTypePair> solverTypes = getSolverTypes();

    const char* defaultSolver_ptr = std::getenv("MMSOLVER_DEFAULT_SOLVER");
    if (defaultSolver_ptr != NULL) {
        // The memory may change under our feet, we copy the data into a
        // string for save keeping.
        std::string defaultSolver(defaultSolver_ptr);

        std::vector<SolverTypePair>::const_iterator cit;
        for (cit = solverTypes.cbegin(); cit != solverTypes.cend(); ++cit){
            int index = cit->first;
            std::string name = cit->second;

            if (defaultSolver == name) {
                solverTypeIndex = index;
                solverTypeName = name;
            }
        }
        if (solverTypeName == "") {
            ERR("MMSOLVER_DEFAULT_SOLVER environment variable is invalid. "
                << "Value may be "
                << "\"cminpack_lm\", "
                << "\"cminpack_lmder\", "
                << "or \"levmar\"; "
                << "; value=" << defaultSolver);
        }
    }
    SolverTypePair solverType(solverTypeIndex, solverTypeName);
    return solverType;
}


int countUpNumberOfErrors(MarkerPtrList markerList,
                          StiffAttrsPtrList stiffAttrsList,
                          SmoothAttrsPtrList smoothAttrsList,
                          MTimeArray frameList,
                          MarkerPtrList &validMarkerList,
                          std::vector<MPoint> &markerPosList,
                          std::vector<double> &markerWeightList,
                          IndexPairList &errorToMarkerList,
                          int &numberOfMarkerErrors,
                          int &numberOfAttrStiffnessErrors,
                          int &numberOfAttrSmoothnessErrors,
                          MStatus &status) {
    // Count up number of errors.
    //
    // For each marker on each frame that it is valid, we add
    // ERRORS_PER_MARKER errors.
    int i = 0;
    int j = 0;

    // For normalising the marker weight per-frame, create a mapping
    // data structure to use later.
    typedef std::map<int, double> FrameIndexDoubleMapping;
    typedef FrameIndexDoubleMapping::iterator FrameIndexDoubleMappingIt;
    FrameIndexDoubleMapping weightMaxPerFrame;
    FrameIndexDoubleMappingIt xit;

    // Get all the marker data
    numberOfMarkerErrors = 0;
    for (MarkerPtrListIt mit = markerList.begin(); mit != markerList.end(); ++mit) {
        MarkerPtr marker = *mit;
        for (j = 0; j < (int) frameList.length(); ++j) {
            MTime frame = frameList[j];

            bool enable = false;
            status = marker->getEnable(enable, frame);
            CHECK_MSTATUS_AND_RETURN(status, numberOfMarkerErrors);

            double weight = 0.0;
            status = marker->getWeight(weight, frame);
            CHECK_MSTATUS_AND_RETURN(status, numberOfMarkerErrors);

            if ((enable == true) && (weight > 0.0)) {
                // First index is into 'markerList'
                // Second index is into 'frameList'
                IndexPair markerPair(i, j);
                errorToMarkerList.push_back(markerPair);
                numberOfMarkerErrors += ERRORS_PER_MARKER;

                validMarkerList.push_back(marker);

                // Add marker weights, into a cached list to be used
                // during solving for direct look-up.
                markerWeightList.push_back(weight);

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

                // Get Marker Position.
                MMatrix cameraWorldProjectionMatrix;
                CameraPtr camera = marker->getCamera();
                status = camera->getWorldProjMatrix(cameraWorldProjectionMatrix, frame);
                double filmBackWidth = camera->getFilmbackWidthValue(frame);
                double filmBackHeight = camera->getFilmbackHeightValue(frame);
                double filmBackInvAspect = filmBackHeight / filmBackWidth;
                // double filmBackAspect = filmBackWidth / filmBackHeight;
                CHECK_MSTATUS(status);
                MPoint marker_pos;
                status = marker->getPos(marker_pos, frame);
                CHECK_MSTATUS(status);
                marker_pos = marker_pos * cameraWorldProjectionMatrix;
                marker_pos.cartesianize();
                // convert to -0.5 to 0.5, maintaining the aspect
                // ratio of the film back.
                marker_pos[0] *= 0.5;
                marker_pos[1] *= 0.5 * filmBackInvAspect;
                markerPosList.push_back(marker_pos);
            }
        }
        i++;
    }

    // Normalise the weights per-frame, using the weight 'max'
    // computed above.
    i = 0;
    typedef IndexPairList::const_iterator IndexPairListCit;
    for (IndexPairListCit eit = errorToMarkerList.begin();
         eit != errorToMarkerList.end(); ++eit) {
        double weight = markerWeightList[i];

        int frameIndex = eit->second;

        xit = weightMaxPerFrame.find(frameIndex);
        assert(xit != weightMaxPerFrame.end());
        double weight_max = xit->second;

        weight = weight / weight_max;
        markerWeightList[i] = weight;
        ++i;
    }

    // Compute number of errors from Attributes.
    double stiffValue = 0.0;
    for (StiffAttrsPtrListIt ait = stiffAttrsList.begin(); ait != stiffAttrsList.end(); ++ait) {
        StiffAttrsPtr stiffAttrs = *ait;

        // Determine if the attribute will use stiffness values. Don't
        // add stiffness to the solver unless it needs
        // to be calculated.
        AttrPtr weightAttr = stiffAttrs->weightAttr;
        weightAttr->getValue(stiffValue);
        bool useStiffness = static_cast<bool>(stiffValue);
        if (useStiffness) {
            numberOfAttrStiffnessErrors++;
        }
    }

    double smoothValue = 0.0;
    for (SmoothAttrsPtrListIt ait = smoothAttrsList.begin(); ait != smoothAttrsList.end(); ++ait) {
        SmoothAttrsPtr smoothAttrs = *ait;

        // Determine if the attribute will use smoothness values. Don't
        // add smoothness to the solver unless it needs
        // to be calculated.
        AttrPtr weightAttr = smoothAttrs->weightAttr;
        weightAttr->getValue(smoothValue);
        bool useSmoothness = static_cast<bool>(smoothValue);
        if (useSmoothness) {
            numberOfAttrSmoothnessErrors++;
        }
    }

    int numErrors = numberOfMarkerErrors;
    numErrors += numberOfAttrStiffnessErrors;
    numErrors += numberOfAttrSmoothnessErrors;
    return numErrors;
}


int countUpNumberOfUnknownParameters(AttrPtrList attrList,
                                     MTimeArray frameList,
                                     AttrPtrList &camStaticAttrList,
                                     AttrPtrList &camAnimAttrList,
                                     AttrPtrList &staticAttrList,
                                     AttrPtrList &animAttrList,
                                     std::vector<double> &paramLowerBoundList,
                                     std::vector<double> &paramUpperBoundList,
                                     std::vector<double> &paramWeightList,
                                     IndexPairList &paramToAttrList,
                                     MStatus &status) {
    // Count up number of unknown parameters
    int i = 0;      // index of marker
    int j = 0;      // index of frame
    int numUnknowns = 0;

    for (AttrPtrListIt ait = attrList.begin(); ait != attrList.end(); ++ait) {
        AttrPtr attr = *ait;
        MObject nodeObj = attr->getObject();

        bool attrIsPartOfCamera = false;
        MFnDependencyNode dependNode(nodeObj);
        if (nodeObj.apiType() == MFn::kTransform) {
            MFnDagNode dagNode(nodeObj);
            for (unsigned int k = 0; k < dagNode.childCount(); ++k) {
                MObject childObj = dagNode.child(k, &status);
                CHECK_MSTATUS(status);
                if (childObj.apiType() == MFn::kCamera) {
                    attrIsPartOfCamera = true;
                }
            }
        } else if (nodeObj.apiType() == MFn::kCamera) {
            attrIsPartOfCamera = true;
        }

        if (attr->isAnimated()) {
            numUnknowns += frameList.length();
            for (j = 0; j < (int) frameList.length(); ++j) {
                // first index is into 'attrList'
                // second index is into 'frameList'
                IndexPair attrPair(i, j);
                paramToAttrList.push_back(attrPair);

                // Min / max parameter bounds.
                double minValue = attr->getMinimumValue();
                double maxValue = attr->getMaximumValue();
                paramLowerBoundList.push_back(minValue);
                paramUpperBoundList.push_back(maxValue);

                // TODO: Get a weight value from the attribute. Currently
                // weights are not supported in the Maya mmSolver command.
                // This is not the same as Marker weights.
                paramWeightList.push_back(1.0);
            }

            if (attrIsPartOfCamera) {
                camAnimAttrList.push_back(attr);
            } else {
                animAttrList.push_back(attr);
            }
        } else if (attr->isFreeToChange()) {
            ++numUnknowns;
            // first index is into 'attrList'
            // second index is into 'frameList', '-1' means a static value.
            IndexPair attrPair(i, -1);
            paramToAttrList.push_back(attrPair);

            // Min / max parameter bounds.
            double minValue = attr->getMinimumValue();
            double maxValue = attr->getMaximumValue();
            paramLowerBoundList.push_back(minValue);
            paramUpperBoundList.push_back(maxValue);

            // TODO: Get a weight value from the attribute. Currently
            // weights are not supported in the Maya mmSolver command.
            // This is not the same as Marker weights.
            paramWeightList.push_back(1.0);

            if (attrIsPartOfCamera) {
                camStaticAttrList.push_back(attr);
            } else {
                staticAttrList.push_back(attr);
            }
        } else {
            const char *attrName = attr->getName().asChar();
            ERR("attr is not animated or free: " << attrName);
        }
        i++;
    }
    return numUnknowns;
}


///*
// * Use the Maya DG graph structure to determine the
// * sparsity structure, a relation of cause and effect; which
// * attributes affect which markers.
// *
// * Answer this question: 'for each marker, determine which
// * attributes can affect it's bundle.'
// *
// * Detect inputs and outputs for marker-bundle relationships. For each
// * marker, get the bundle, then find all the attributes that affect the bundle
// * (and it's parent nodes). If the bundle cannot be affected by any attribute
// * in the solver, print a warning and remove it from the solve list.
// *
// * This relationship building will be the basis for the Ceres
// * residual/parameter block creation. Note we do not need to worry about time
// * in our relationship building, connections cannot be made at different
// * times (and if they did, that would be stupid). This relationship building
// * could mean we only need to measure a limited number of bundles, hence
// * improving performance.
// *
// * There are special cases for detecting inputs/outputs between
// * markers and attributes.
// *
// * - Any transform node/attribute above the marker in the DAG that
// *   affects the world transform.
// *
// * - Cameras; transform attributes and focal length will affect all
// *   markers
// *
// */
//void findErrorToParameterRelationship(MarkerPtrList markerList,
//                                      AttrPtrList attrList,
//                                      MTimeArray frameList,
//                                      int numParameters,
//                                      int numErrors,
//                                      IndexPairList paramToAttrList,
//                                      IndexPairList errorToMarkerList,
//                                      BoolList2D &markerToAttrMapping,
//                                      BoolList2D &errorToParamMapping,
//                                      MStatus &status) {
//    int i, j;
//
//    // Command execution options
//    bool display = false;  // print out what happens in the python
//    // command.
//    bool undoable = false;  // we won't modify the scene in any way,
//    // only make queries.
//    MString cmd = "";
//    MStringArray result1;
//    MStringArray result2;
//
//    // Calculate the relationship between attributes and markers.
//    markerToAttrMapping.resize(markerList.size());
//    i = 0;      // index of marker
//    for (MarkerPtrListCIt mit = markerList.begin(); mit != markerList.end(); ++mit) {
//        MarkerPtr marker = *mit;
//        CameraPtr cam = marker->getCamera();
//        BundlePtr bundle = marker->getBundle();
//
//        // Get node names.
//        const char *markerName = marker->getNodeName().asChar();
//        const char *camName = cam->getTransformNodeName().asChar();
//        const char *bundleName = bundle->getNodeName().asChar();
//
//        // Find list of plug names that are affected by the bundle.
//        cmd = "";
//        cmd += "import mmSolver.api as mmapi;";
//        cmd += "mmapi.find_attrs_affecting_transform(";
//        cmd += "\"";
//        cmd += bundleName;
//        cmd += "\"";
//        cmd += ");";
//        DBG("Running: " + cmd);
//        status = MGlobal::executePythonCommand(cmd, result1, display, undoable);
//        DBG("Python result1 num: " << result1.length());
//
//        // Find list of plug names that are affected by the marker
//        // (and camera projection matrix).
//        cmd = "";
//        cmd += "import mmSolver.api as mmapi;";
//        cmd += "mmapi.find_attrs_affecting_transform(";
//        cmd += "\"";
//        cmd += markerName;
//        cmd += "\", ";
//        cmd += "cam_tfm=\"";
//        cmd += camName;
//        cmd += "\"";
//        cmd += ");";
//        DBG("Running: " + cmd);
//        status = MGlobal::executePythonCommand(cmd, result2, display, undoable);
//        DBG("Python result2 num: " << result2.length());
//
//        // Determine if the marker can affect the attribute.
//        j = 0;      // index of attribute
//        MString affectedPlugName;
//        markerToAttrMapping[i].resize(attrList.size(), false);
//        for (AttrPtrListCIt ait = attrList.begin(); ait != attrList.end(); ++ait) {
//            AttrPtr attr = *ait;
//
//            // Get attribute full path.
//            MPlug plug = attr->getPlug();
//            MObject attrNode = plug.node();
//            MFnDagNode attrFnDagNode(attrNode);
//            MString attrNodeName = attrFnDagNode.fullPathName();
//            MString attrAttrName = plug.partialName(false, true, true, false, false, true);
//            MString attrName = attrNodeName + "." + attrAttrName;
//
//            // Bundle affects attribute
//            for (int k = 0; k < result1.length(); ++k) {
//                affectedPlugName = result1[k];
//                if (attrName == affectedPlugName) {
//                    markerToAttrMapping[i][j] = true;
//                    break;
//                }
//            }
//
//            // Marker (or camera) affects attribute
//            for (int k = 0; k < result2.length(); ++k) {
//                affectedPlugName = result2[k];
//                if (attrName == affectedPlugName) {
//                    markerToAttrMapping[i][j] = true;
//                    break;
//                }
//            }
//            ++j;
//        }
//        ++i;
//    }
//
//    // Calculate the relationship between errors and parameters.
//    /*
//     * For each error, work out which parameters can affect
//     * it. The parameters may be static or animated and thereby each
//     * parameter may affect one or more errors. A single parameter
//     * will affect a range of time values, a static parameter affects
//     * all time values, but a dynamic parameter will be split into
//     * many parameters at different frames, each of those dynamic
//     * parameters will only affect a small number of errors. Our goal
//     * is to compute a boolean for each error and parameter
//     * combination, if the boolean is true the relationship is
//     * positive, if false, the computation is skipped and the error
//     * returned is zero.  This combination is only relevant if the
//     * markerToAttrMapping is already true, otherwise we can assume
//     * such error/parameter combinations will not be required.
//     */
//    int markerIndex = 0;
//    int markerFrameIndex = 0;
//    int attrIndex = 0;
//    int attrFrameIndex = 0;
//    IndexPair markerIndexPair;
//    IndexPair attrIndexPair;
//    errorToParamMapping.resize(numErrors);
//
//    i = 0;      // index of error
//    j = 0;      // index of parameter
//    for (i = 0; i < (numErrors / ERRORS_PER_MARKER); ++i) {
//        markerIndexPair = errorToMarkerList[i];
//        markerIndex = markerIndexPair.first;
//        markerFrameIndex = markerIndexPair.second;
//
//        MarkerPtr marker = markerList[markerIndex];
//        CameraPtr cam = marker->getCamera();
//        BundlePtr bundle = marker->getBundle();
//        MTime markerFrame = frameList[markerFrameIndex];
//
//        // Get node names.
//        const char *markerName = marker->getNodeName().asChar();
//        const char *camName = cam->getTransformNodeName().asChar();
//        const char *bundleName = bundle->getNodeName().asChar();
//
//        // Determine if the marker can affect the attribute.
//        errorToParamMapping[i].resize(numParameters, false);
//        for (j = 0; j < numParameters; ++j) {
//            attrIndexPair = paramToAttrList[j];
//            attrIndex = attrIndexPair.first;
//            attrFrameIndex = attrIndexPair.second;
//
//            // If the attrFrameIndex is -1, then the attribute is
//            // static, not animated.
//            AttrPtr attr = attrList[attrIndex];
//            MTime attrFrame(-1.0, MTime::uiUnit());
//            if (attrFrameIndex >= 0) {
//                attrFrame = frameList[attrFrameIndex];
//            }
//            const char *attrName = attr->getName().asChar();
//
//            bool markerAffectsAttr = markerToAttrMapping[markerIndex][attrIndex];
//            bool paramAffectsError = markerAffectsAttr;
//            if (paramAffectsError == true) {
//                // Time based mapping information.
//                // Only markers on the current frame can affect the current attribute.
//                if (attrFrameIndex >= 0) {
//                    paramAffectsError = false;
//                    if (number::floatApproxEqual(markerFrame.value(), attrFrame.value())) {
//                        paramAffectsError = true;
//                    }
//                } else {
//                    paramAffectsError = true;
//                }
//            }
//            errorToParamMapping[i][j] = paramAffectsError;
//        }
//    }
//
//    return;
//}


void lossFunctionTrivial(double z,
                         double &rho0,
                         double &rho1,
                         double &rho2) {
    // Trivial - 'no op' loss function.
    rho0 = z;
    rho1 = 1.0;
    rho2 = 0.0;
};


void lossFunctionSoftL1(double z,
                        double &rho0,
                        double &rho1,
                        double &rho2) {
    // Soft L1
    double t = 1.0 + z;
    rho0 = 2.0 * (std::pow(t, 0.5 - 1.0));
    rho1 = std::pow(t, -0.5);
    rho2 = -0.5 * std::pow(t, -1.5);
};


void lossFunctionCauchy(double z,
                        double &rho0,
                        double &rho1,
                        double &rho2) {
    // Cauchy
    // TODO: replace with 'std::log1p(z)', with C++11.
    rho0 = std::log(1.0 + z);
    double t = 1.0 + z;
    rho1 = 1.0 / t;
    rho2 = -1.0 / std::pow(t, 2.0);
};


void applyLossFunctionToErrors(int numberOfErrors,
                               double *f,
                               int loss_type,
                               double loss_scale) {
    for (int i = 0; i < numberOfErrors; ++i) {
        // The loss function
        double z = std::pow(f[i] / loss_scale, 2);
        double rho0 = z;
        double rho1 = 1.0;
        double rho2 = 0.0;
        if (loss_type == ROBUST_LOSS_TYPE_TRIVIAL) {
            lossFunctionTrivial(z, rho0, rho1, rho2);
        } else if (loss_type == ROBUST_LOSS_TYPE_SOFT_L_ONE) {
            lossFunctionSoftL1(z, rho0, rho1, rho2);
        } else if (loss_type == ROBUST_LOSS_TYPE_CAUCHY) {
            lossFunctionCauchy(z, rho0, rho1, rho2);
        } else {
            DBG("Invalid Robust Loss Type given; value=" << loss_type);
        }
        rho0 *= std::pow(loss_scale, 2.0);
        rho2 /= std::pow(loss_scale, 2.0);

        double J_scale = rho1 + 2.0 * rho2 * std::pow(f[i], 2.0);
        const double eps = std::numeric_limits<double>::epsilon();
        if (J_scale < eps) {
            J_scale = eps;
        }
        J_scale = std::pow(J_scale, 0.5);
        f[i] *= rho1 / J_scale;
    }
    return;
}


// Convert an unbounded parameter value (that has already run through
// 'parameterBoundFromExternalToInternal') into a bounded value where:
//    xmin < value < xmax
//
// Implements Box Constraints; Issue #64.
double parameterBoundFromInternalToExternal(double value,
                                            double xmin, double xmax,
                                            double offset, double scale) {
    const double float_max = std::numeric_limits<float>::max();
    if ((xmin <= -float_max) && (xmax >= float_max)) {
        // No bounds!
        value = (value / scale) - offset;
        value = std::max<double>(value, xmin);
        value = std::min<double>(value, xmax);
        return value;
    }
    else if (xmax >= float_max) {
        // Lower bound only.
        value = xmin - (1.0 + std::sqrt(value * value + 1.0));
    }
    else if (xmin <= -float_max) {
        // Upper bound only.
        value = xmax + (1.0 - std::sqrt(value * value + 1.0));
    } else {
        // Both lower and upper bounds.
        value = xmin + ((xmax - xmin) / 2.0) * (std::sin(value) + 1.0);
    }

    value = (value / scale) - offset;
    value = std::max<double>(value, xmin);
    value = std::min<double>(value, xmax);
    return value;
}


// Convert a bounded parameter value, into an unbounded value.
//
// Implements Box Constraints; Issue #64.
double parameterBoundFromExternalToInternal(double value,
                                            double xmin, double xmax,
                                            double offset, double scale){
    double initial_value = value;
    double initial_xmin = xmin;
    double initial_xmax = xmax;
    double reconvert_value = 0.0;

    value = std::max<double>(value, xmin);
    value = std::min<double>(value, xmax);
    value = (value * scale) + offset;
    xmin = (xmin * scale) + offset;
    xmax = (xmax * scale) + offset;

    const double float_max = std::numeric_limits<float>::max();
    if ((xmin <= float_max) && (xmax >= float_max)) {
        // No bounds!
        reconvert_value = parameterBoundFromInternalToExternal(
                value,
                initial_xmin, initial_xmax,
                offset, scale);
        return value;
    }
    else if (xmax >= float_max) {
        // Lower bound only.
        value = std::sqrt(std::pow(((value - xmin) + 1.0), 2.0) - 1.0);
    }
    else if (xmin <= -float_max) {
        // Upper bound only.
        value = std::sqrt(std::pow((xmax - value) + 1.0, 2.0) - 1.0);
    } else {
        // Both lower and upper bounds.
        value = std::asin((2.0 * (value - xmin) / (xmax - xmin)) - 1.0);
    }

    reconvert_value = parameterBoundFromInternalToExternal(
            value,
            initial_xmin, initial_xmax,
            offset, scale);
    return value;
}


bool set_initial_parameters(int numberOfParameters,
                            std::vector<double> &paramList,
                            std::vector<std::pair<int, int> > &paramToAttrList,
                            AttrPtrList &attrList,
                            MTimeArray &frameList,
                            MStringArray &outResult) {
    std::string resultStr;
    MStatus status = MS::kSuccess;
    MTime currentFrame = MAnimControl::currentTime();
    for (int i = 0; i < numberOfParameters; ++i) {
        IndexPair attrPair = paramToAttrList[i];
        AttrPtr attr = attrList[attrPair.first];

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1) {
            frame = frameList[attrPair.second];
        }

        double value = 0.0;
        status = attr->getValue(value, frame);
        CHECK_MSTATUS(status);
        if (status != MS::kSuccess) {
            resultStr = "success=0";
            outResult.append(MString(resultStr.c_str()));
            return false;
        }

        double xoffset = attr->getOffsetValue();
        double xscale = attr->getScaleValue();
        double xmin = attr->getMinimumValue();
        double xmax = attr->getMaximumValue();
        value = parameterBoundFromExternalToInternal(
            value,
            xmin, xmax,
            xoffset, xscale);
        paramList[i] = value;
    }
    return true;
}


bool set_maya_attribute_values(int numberOfParameters,
                               std::vector<std::pair<int, int> > &paramToAttrList,
                               AttrPtrList &attrList,
                               std::vector<double> &paramList,
                               MTimeArray &frameList,
                               MDGModifier &dgmod,
                               MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;
    MTime currentFrame = MAnimControl::currentTime();
    for (int i = 0; i < numberOfParameters; ++i) {
        IndexPair attrPair = paramToAttrList[i];
        AttrPtr attr = attrList[attrPair.first];

        double xoffset = attr->getOffsetValue();
        double xscale = attr->getScaleValue();
        double xmin = attr->getMinimumValue();
        double xmax = attr->getMaximumValue();
        double value = paramList[i];
        value = parameterBoundFromInternalToExternal(
            value,
            xmin, xmax,
            xoffset, xscale);

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1) {
            frame = frameList[attrPair.second];
        }

        status = attr->setValue(value, frame, dgmod, curveChange);
        CHECK_MSTATUS(status);
    }
    dgmod.doIt();  // Commit changed data into Maya
    return true;
}


// Compute the average error based on the error values
// the solve function last computed.
bool compute_error_stats(int numberOfMarkerErrors,
                         SolverData &userData,
                         double &errorAvg,
                         double &errorMin,
                         double &errorMax){
    errorAvg = 0;
    errorMin = std::numeric_limits<double>::max();
    errorMax = -0.0;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        double err = userData.errorDistanceList[i];
        errorAvg += err;
        if (err < errorMin) { errorMin = err; }
        if (err > errorMax) { errorMax = err; }
    }
    assert(numberOfMarkerErrors > 0);
    errorAvg /= (double) (numberOfMarkerErrors / ERRORS_PER_MARKER);
    return true;
}


void print_details(
        SolverResult &solverResult,
        SolverData &userData,
        SolverTimer &timer,
        int numberOfParameters,
        int numberOfMarkerErrors,
        int numberOfAttrStiffnessErrors,
        int numberOfAttrSmoothnessErrors,
        bool verbose,
        std::vector<double> &paramList,
        MStringArray &outResult) {
    int numberOfErrors = numberOfMarkerErrors;
    numberOfErrors += numberOfAttrStiffnessErrors;
    numberOfErrors += numberOfAttrSmoothnessErrors;

    VRB("Results:");
    if (solverResult.success) {
        VRB("Solver returned SUCCESS in " << solverResult.iterations << " iterations");
    } else {
        VRB("Solver returned FAILURE in " << solverResult.iterations << " iterations");
    }

    int reasonNum = solverResult.reason_number;
    VRB("Reason: " << solverResult.reason);
    VRB("Reason number: " << solverResult.reason_number);

    VRB(std::endl << "Solve Information:");
    VRB("Maximum Error: " << solverResult.errorMax);
    VRB("Average Error: " << solverResult.errorAvg);
    VRB("Minimum Error: " << solverResult.errorMin);

    VRB("Iterations: " << solverResult.iterations);
    VRB("Function Evaluations: " << solverResult.functionEvals);
    VRB("Jacobian Evaluations: " << solverResult.jacobianEvals);

    if (verbose == false) {
        if (solverResult.success) {
            std::cerr << "Solver returned SUCCESS   | ";
        } else {
            std::cerr << "Solver returned FAILURE   | ";
        }
        fprintf(
            stderr,
            "error avg %8.4f   min %8.4f   max %8.4f  iterations %03u\n",
            solverResult.errorAvg,
            solverResult.errorMin,
            solverResult.errorMax,
            solverResult.iterations);
        fflush(stderr);
    }

    // Add all the data into the output string from the Maya command.
    std::string resultStr;
    std::string value = string::numberToString<int>(solverResult.success);
    resultStr = "success=" + value;
    outResult.append(MString(resultStr.c_str()));

    resultStr = "reason_string=" + levmarReasons[reasonNum];
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<int>(reasonNum);
    resultStr = "reason_num=" + value;
    outResult.append(MString(resultStr.c_str()));

//    value = string::numberToString<double>(solverResult.errorInitial);
//    resultStr = "error_initial=" + value;
//    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<double>(solverResult.errorFinal);
    resultStr = "error_final=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<double>(solverResult.errorAvg);
    resultStr = "error_final_average=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<double>(solverResult.errorMax);
    resultStr = "error_final_maximum=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<double>(solverResult.errorMin);
    resultStr = "error_final_minimum=" + value;
    outResult.append(MString(resultStr.c_str()));

//    value = string::numberToString<double>(solverResult.errorJt);
//    resultStr = "error_jt=" + value;
//    outResult.append(MString(resultStr.c_str()));

//    value = string::numberToString<double>(solverResult.errorDp);
//    resultStr = "error_dp=" + value;
//    outResult.append(MString(resultStr.c_str()));

//    value = string::numberToString<double>(solverResult.errorMaximum);
//    resultStr = "error_maximum=" + value;
//    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<int>(solverResult.iterations);
    resultStr = "iteration_num=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<int>(solverResult.functionEvals);
    resultStr = "iteration_function_num=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<int>(solverResult.jacobianEvals);
    resultStr = "iteration_jacobian_num=" + value;
    outResult.append(MString(resultStr.c_str()));

//    value = string::numberToString<int>(solverResult.iterationAttempts);
//    resultStr = "iteration_attempt_num=" + value;
//    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<int>((bool) userData.userInterrupted);
    resultStr = "user_interrupted=" + value;
    outResult.append(MString(resultStr.c_str()));

    if (verbose) {
        unsigned int total_num = userData.iterNum + userData.jacIterNum;
        assert(total_num > 0);
        timer.solveBenchTimer.print("Solve Time", 1);
        timer.funcBenchTimer.print("Func Time", 1);
        timer.jacBenchTimer.print("Jacobian Time", 1);
        timer.paramBenchTimer.print("Param Time", total_num);
        timer.errorBenchTimer.print("Error Time", total_num);
        timer.funcBenchTimer.print("Func Time", total_num);

        timer.solveBenchTicks.print("Solve Ticks", 1);
        timer.funcBenchTicks.print("Func Ticks", 1);
        timer.jacBenchTicks.print("Jacobian Ticks", 1);
        timer.paramBenchTicks.print("Param Ticks", total_num);
        timer.errorBenchTicks.print("Error Ticks", total_num);
        timer.funcBenchTicks.print("Func Ticks", total_num);
    }

    value = string::numberToString<double>(timer.solveBenchTimer.get_seconds());
    resultStr = "timer_solve=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<double>(timer.funcBenchTimer.get_seconds());
    resultStr = "timer_function=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<double>(timer.jacBenchTimer.get_seconds());
    resultStr = "timer_jacobian=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<double>(timer.paramBenchTimer.get_seconds());
    resultStr = "timer_parameter=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<double>(timer.paramBenchTimer.get_seconds());
    resultStr = "timer_error=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<debug::Ticks>(timer.solveBenchTicks.get_ticks());
    resultStr = "ticks_solve=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<debug::Ticks>(timer.funcBenchTicks.get_ticks());
    resultStr = "ticks_function=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<debug::Ticks>(timer.jacBenchTicks.get_ticks());
    resultStr = "ticks_jacobian=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<debug::Ticks>(timer.paramBenchTicks.get_ticks());
    resultStr = "ticks_parameter=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = string::numberToString<debug::Ticks>(timer.paramBenchTicks.get_ticks());
    resultStr = "ticks_error=" + value;
    outResult.append(MString(resultStr.c_str()));

    resultStr = "solve_parameter_list=";
    for (int i = 0; i < numberOfParameters; ++i) {
        resultStr += string::numberToString<double>(paramList[i]);
        resultStr += CMD_RESULT_SPLIT_CHAR;
    }
    outResult.append(MString(resultStr.c_str()));

    resultStr = "solve_error_list=";
    for (int i = 0; i < numberOfErrors; ++i) {
        double err = userData.errorList[i];
        resultStr += string::numberToString<double>(err);
        resultStr += CMD_RESULT_SPLIT_CHAR;
    }
    outResult.append(MString(resultStr.c_str()));

    // Marker-Frame-Error relationship
    typedef std::pair<int, double> ErrorPair;
    typedef std::map<int, ErrorPair> TimeErrorMapping;
    typedef TimeErrorMapping::iterator TimeErrorMappingIt;
    TimeErrorMapping frameErrorMapping;
    TimeErrorMappingIt ait;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        IndexPair markerPair = userData.errorToMarkerList[i];
        MarkerPtr marker = userData.markerList[markerPair.first];
        MTime frame = userData.frameList[markerPair.second];
        const char *markerName = marker->getNodeName().asChar();
        double d = userData.errorDistanceList[i];

        ait = frameErrorMapping.find(markerPair.second);
        ErrorPair pair;
        if (ait != frameErrorMapping.end()) {
            pair = ait->second;
            pair.first += 1;
            pair.second += d;
            frameErrorMapping.erase(ait);
        } else {
            pair.first = 1;
            pair.second = d;
        }
        frameErrorMapping.insert(std::pair<int, ErrorPair>(markerPair.second, pair));

        resultStr = "error_per_marker_per_frame=";
        resultStr += markerName;
        resultStr += CMD_RESULT_SPLIT_CHAR;
        resultStr += string::numberToString<double>(frame.asUnits(MTime::uiUnit()));
        resultStr += CMD_RESULT_SPLIT_CHAR;
        resultStr += string::numberToString<double>(d);
        outResult.append(MString(resultStr.c_str()));
    }

    for (TimeErrorMappingIt mit = frameErrorMapping.begin();
         mit != frameErrorMapping.end(); ++mit) {
        int frameIndex = mit->first;
        MTime frame = userData.frameList[frameIndex];
        ait = frameErrorMapping.find(frameIndex);
        double num = 0;
        double d = 0;
        if (ait != frameErrorMapping.end()) {
            ErrorPair pair = ait->second;
            num = pair.first;
            d = pair.second;
        } else {
            continue;
        }

        resultStr = "error_per_frame=";
        resultStr += string::numberToString<double>(frame.asUnits(MTime::uiUnit()));
        resultStr += CMD_RESULT_SPLIT_CHAR;
        resultStr += string::numberToString<double>(d / num);
        outResult.append(MString(resultStr.c_str()));
    }
};


/*! Solve everything!
 *
 * This function is responsible for taking the given cameras, markers,
 * bundles and solver options, and modifying the current Maya scene,
 * saving changes in the 'dgmod' variable, and returning the results
 * in the outResult string.
 *
 */
bool solve(SolverOptions &solverOptions,
           CameraPtrList &cameraList,
           MarkerPtrList &markerList,
           BundlePtrList &bundleList,
           AttrPtrList &attrList,
           MTimeArray &frameList,
           StiffAttrsPtrList &stiffAttrsList,
           SmoothAttrsPtrList &smoothAttrsList,
           MDGModifier &dgmod,
           MAnimCurveChange &curveChange,
           MComputation &computation,
           MString &debugFile,
           MStringArray &printStatsList,
           bool with_verbosity,
           MStringArray &outResult) {
    MStatus status;
    std::string resultStr;
    int ret = 1;
    MGlobal::MMayaState mayaSessionState = MGlobal::mayaState(&status);

    bool verbose = with_verbosity;
    bool printStats = false;
    bool printStatsInput = false;
    // bool printStatsAffects = false;  // TODO: Print 'affects' statistics.
    bool printStatsDeviation = false;
    if (printStatsList.length() > 0) {
        for (unsigned int i = 0; i < printStatsList.length(); ++i) {
            if (printStatsList[i] == PRINT_STATS_MODE_INPUTS) {
                printStatsInput = true;
                printStats = true;
            // } else if (printStatsList[i] == PRINT_STATS_MODE_AFFECTS) {
            //     printStatsAffects = true;
            //     printStats = true;
            } else if (printStatsList[i] == PRINT_STATS_MODE_DEVIATION) {
                printStatsDeviation = true;
                printStats = true;
            }
        }
    }
    if (printStats == true) {
        // When printing statistics, turn off verbosity.
        verbose = false;
    }

#ifdef MAYA_PROFILE
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope profilingScope(profileCategory,
                                   MProfiler::kColorC_L3,
                                   "solve");
#endif

    IndexPairList paramToAttrList;
    IndexPairList errorToMarkerList;
    std::vector<MPoint> markerPosList;
    std::vector<double> markerWeightList;
    std::vector<double> errorList(1);
    std::vector<double> paramList(1);
    std::vector<double> jacobianList(1);

    int numberOfErrors = 0;
    int numberOfMarkerErrors = 0;
    int numberOfAttrStiffnessErrors = 0;
    int numberOfAttrSmoothnessErrors = 0;
    MarkerPtrList validMarkerList;
    numberOfErrors = countUpNumberOfErrors(
            markerList,
            stiffAttrsList,
            smoothAttrsList,
            frameList,
            validMarkerList,
            markerPosList,
            markerWeightList,
            errorToMarkerList,
            numberOfMarkerErrors,
            numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors,
            status
    );
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
    numberOfParameters = countUpNumberOfUnknownParameters(
            attrList,
            frameList,
            camStaticAttrList,
            camAnimAttrList,
            staticAttrList,
            animAttrList,
            paramLowerBoundList,
            paramUpperBoundList,
            paramWeightList,
            paramToAttrList,
            status
    );
    assert(paramLowerBoundList.size() == numberOfParameters);
    assert(paramUpperBoundList.size() == numberOfParameters);
    assert(paramWeightList.size() == numberOfParameters);
    assert(numberOfParameters >= attrList.size());

    if (printStatsInput == true) {
         resultStr = "numberOfParameters=";
         resultStr += string::numberToString<int>(numberOfParameters);
         outResult.append(MString(resultStr.c_str()));

         resultStr = "numberOfErrors=";
         resultStr += string::numberToString<int>(numberOfErrors);
         outResult.append(MString(resultStr.c_str()));

         resultStr = "numberOfMarkerErrors=";
         resultStr += string::numberToString<int>(numberOfMarkerErrors);
         outResult.append(MString(resultStr.c_str()));

         resultStr = "numberOfAttrStiffnessErrors=";
         resultStr += string::numberToString<int>(numberOfAttrStiffnessErrors);
         outResult.append(MString(resultStr.c_str()));

         resultStr = "numberOfAttrSmoothnessErrors=";
         resultStr += string::numberToString<int>(numberOfAttrSmoothnessErrors);
         outResult.append(MString(resultStr.c_str()));
    }

    VRB("Number of Parameters; " << numberOfParameters);
    VRB("Number of Frames; " << frameList.length());
    VRB("Number of Marker Errors; " << numberOfMarkerErrors);
    VRB("Number of Attribute Stiffness Errors; " << numberOfAttrStiffnessErrors);
    VRB("Number of Attribute Smoothness Errors; " << numberOfAttrSmoothnessErrors);
    VRB("Number of Total Errors; " << numberOfErrors);
    if (numberOfParameters > numberOfErrors) {
        if (printStats == true) {
            // If the user is asking to print statistics, then we have
            // successfully achieved that goal and we cannot continue
            // to generate statistics, because of an invalid number of
            // parameters/errors.
            return true;
        }
        ERR("Solver failure; cannot solve for more attributes (\"parameters\") "
            << "than number of markers (\"errors\"). "
            << "parameters=" << numberOfParameters << " "
            << "errors=" << numberOfErrors);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        return false;
    }

    paramList.resize((unsigned long) numberOfParameters, 0);
    errorList.resize((unsigned long) numberOfErrors, 0);
    jacobianList.resize((unsigned long) numberOfParameters * numberOfErrors, 0);

    std::vector<double> errorDistanceList;
    errorDistanceList.resize((unsigned long) numberOfMarkerErrors / ERRORS_PER_MARKER, 0);
    assert(errorToMarkerList.size() == errorDistanceList.size());

    VRB("Solving...");
    VRB("Solver Type=" << solverOptions.solverType);
    VRB("Maximum Iterations=" << solverOptions.iterMax);
    VRB("Tau=" << solverOptions.tau);
    VRB("Epsilon1=" << solverOptions.eps1);
    VRB("Epsilon2=" << solverOptions.eps2);
    VRB("Epsilon3=" << solverOptions.eps3);
    VRB("Delta=" << fabs(solverOptions.delta));
    VRB("Auto Differencing Type=" << solverOptions.autoDiffType);

    if ((verbose == false) && (printStats == false)) {
        std::stringstream ss;
        ss << "Solving... frames:";
        for (int i = 0; i < frameList.length(); i++) {
            MTime frame(frameList[i]);
            ss << " " << frame;
        }
        std::string tmp_string = ss.str();

        int num = 100 - tmp_string.size();
        if (num < 0) {
            num = 0;
        }
        std::string pad_chars(num, '=');

        std::cerr << tmp_string << " " << pad_chars << std::endl;
    }

    // MComputation helper.
    bool showProgressBar = true;
    bool isInterruptable = true;
    bool useWaitCursor = true;
    if (printStats != true) {
        computation.setProgressRange(0, solverOptions.iterMax);
        computation.beginComputation(showProgressBar, isInterruptable, useWaitCursor);
    }

    // Start Solving
    SolverTimer timer;
    if (printStats != true) {
        timer.solveBenchTimer.start();
        timer.solveBenchTicks.start();
    }

    // Solving Objects.
    SolverData userData;
    userData.cameraList = cameraList;
    userData.markerList = markerList;
    userData.bundleList = bundleList;
    userData.attrList = attrList;
    userData.frameList = frameList;
    userData.smoothAttrsList = smoothAttrsList;
    userData.stiffAttrsList = stiffAttrsList;

    userData.paramToAttrList = paramToAttrList;
    userData.errorToMarkerList = errorToMarkerList;
    userData.markerPosList = markerPosList;
    userData.markerWeightList = markerWeightList;

    userData.paramList = paramList;
    userData.errorList = errorList;
    userData.errorDistanceList = errorDistanceList;
    userData.jacobianList = jacobianList;
    userData.funcEvalNum = 0;  // number of function evaluations.
    userData.iterNum = 0;
    userData.jacIterNum = 0;
    userData.imageWidth = 2048.0;  // TODO: Get actual image plane resolution.
    userData.numberOfMarkerErrors = numberOfMarkerErrors;
    userData.numberOfAttrStiffnessErrors = numberOfAttrStiffnessErrors;
    userData.numberOfAttrSmoothnessErrors = numberOfAttrSmoothnessErrors;

    userData.isJacobianCall = false;
    userData.isNormalCall = true;
    userData.isPrintCall = false;
    userData.doCalcJacobian = false;

    userData.solverOptions = &solverOptions;

    userData.timer = timer;

    userData.dgmod = &dgmod;
    userData.curveChange = &curveChange;

    // Allow user to exit out of solve.
    userData.computation = &computation;
    userData.userInterrupted = false;

    // Maya is running as an interactive or batch?
    userData.mayaSessionState = mayaSessionState;

    // Verbosity
    userData.verbose = verbose;
    userData.debugFileName = debugFile;

    // Calculate errors and return.
    if (printStatsDeviation == true) {
        SolverResult solveResult;

        double errorAvg = 0;
        double errorMin = 0;
        double errorMax = 0;
        // Never write debug data during statistics gathering.
        const bool writeDebug = false;
        std::ofstream debugFile;
        measureErrors(
                numberOfParameters,
                numberOfErrors,
                numberOfMarkerErrors,
                numberOfAttrStiffnessErrors,
                numberOfAttrSmoothnessErrors,
                &errorList[0],
                &userData,
                errorAvg,
                errorMax,
                errorMin,
                writeDebug,
                debugFile,
                status);

        solveResult.success = true;
        solveResult.reason_number = 0;
        solveResult.reason = "";
        solveResult.iterations = 0;
        solveResult.functionEvals = 0;
        solveResult.jacobianEvals = 0;
        solveResult.errorFinal = 0.0;

        errorAvg = 0;
        errorMin = 0;
        errorMax = 0;
        compute_error_stats(
                numberOfMarkerErrors, userData,
                errorAvg, errorMin, errorMax);
        solveResult.errorAvg = errorAvg;
        solveResult.errorMin = errorMin;
        solveResult.errorMax = errorMax;

        print_details(
                solveResult,
                userData,
                timer,
                numberOfParameters,
                numberOfMarkerErrors,
                numberOfAttrStiffnessErrors,
                numberOfAttrSmoothnessErrors,
                verbose,
                paramList,
                outResult);
    }
    if (printStats == true) {
        return true;
    }

    std::ofstream file;
    if (debugFile.length() > 0) {
        const char *debugFileNameChar = debugFile.asChar();
        file.open(debugFileNameChar);
        if (file.is_open() == true) {
             file << std::endl;
             file.close();
        }
    }

    // Set Initial parameters
    VRB("Set Initial parameters...");
    set_initial_parameters(numberOfParameters,
                           paramList,
                           paramToAttrList,
                           attrList,
                           frameList,
                           outResult);

    VRB("Initial Parameters: ");
    for (int i = 0; i < numberOfParameters; ++i) {
        VRB("-> " << paramList[i]);
    }

    SolverResult solveResult;
    if (solverOptions.solverType == SOLVER_TYPE_LEVMAR) {

#ifndef USE_SOLVER_LEVMAR

        ERR("Solver Type is not supported by this compiled plug-in. "
            << "solverType=" << solverOptions.solverType);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        return false;

#else // USE_SOLVER_LEVMAR is defined.

        solve_3d_levmar_bc_dif(
                solverOptions,
                numberOfParameters,
                numberOfErrors,
                paramList,
                errorList,
                paramLowerBoundList,
                paramUpperBoundList,
                paramWeightList,
                userData,
                solveResult,
                outResult);

#endif // USE_SOLVER_LEVMAR

    } else if (solverOptions.solverType == SOLVER_TYPE_CMINPACK_LMDIF) {

#ifndef USE_SOLVER_CMINPACK

        ERR("Solver Type is not supported by this compiled plug-in. "
            << "solverType=" << solverOptions.solverType);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        return false;

#else // USE_SOLVER_CMINPACK is defined.

        solve_3d_cminpack_lmdif(
                solverOptions,
                numberOfParameters,
                numberOfErrors,
                paramList,
                errorList,
                paramLowerBoundList,
                paramUpperBoundList,
                paramWeightList,
                userData,
                solveResult,
                outResult);

#endif // USE_SOLVER_CMINPACK

    } else if (solverOptions.solverType == SOLVER_TYPE_CMINPACK_LMDER) {

#ifndef USE_SOLVER_CMINPACK

        ERR("Solver Type is not supported by this compiled plug-in. "
            << "solverType=" << solverOptions.solverType);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        return false;

#else // USE_SOLVER_CMINPACK is defined.

        solve_3d_cminpack_lmder(
                solverOptions,
                numberOfParameters,
                numberOfErrors,
                paramList,
                errorList,
                paramLowerBoundList,
                paramUpperBoundList,
                paramWeightList,
                userData,
                solveResult,
                outResult);

#endif // USE_SOLVER_CMINPACK

    } else {
        ERR("Solver Type is invalid. solverType="
            << solverOptions.solverType);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        return false;
    }

    timer.solveBenchTicks.stop();
    timer.solveBenchTimer.stop();
    computation.endComputation();

    // Set the solved parameters
    VRB("Setting Parameters...");
    set_maya_attribute_values(
            numberOfParameters,
            paramToAttrList,
            attrList,
            paramList,
            frameList,
            dgmod,
            curveChange);
    VRB("Solved Parameters:");
    for (int i = 0; i < numberOfParameters; ++i) {
        VRB("-> " << paramList[i]);
    }

    double errorAvg = 0;
    double errorMin = 0;
    double errorMax = 0;
    compute_error_stats(
            numberOfMarkerErrors, userData,
            errorAvg, errorMin, errorMax);
    solveResult.errorAvg = errorAvg;
    solveResult.errorMin = errorMin;
    solveResult.errorMax = errorMax;

    print_details(
            solveResult,
            userData,
            timer,
            numberOfParameters,
            numberOfMarkerErrors,
            numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors,
            verbose,
            paramList,
            outResult);
    return solveResult.success;
};
