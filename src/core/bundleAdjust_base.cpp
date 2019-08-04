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
    solverType.first = SOLVER_TYPE_CMINPACK_LM_DIF;
    solverType.second = SOLVER_TYPE_CMINPACK_LM_DIF_NAME;
    solverTypes.push_back(solverType);
    
    solverType.first = SOLVER_TYPE_CMINPACK_LM_DER;
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
                          MTimeArray frameList,
                          MarkerPtrList &validMarkerList,
                          std::vector<MPoint> &markerPosList,
                          std::vector<double> &markerWeightList,
                          IndexPairList &errorToMarkerList,
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
    int numErrors = 0;
    for (MarkerPtrListIt mit = markerList.begin(); mit != markerList.end(); ++mit) {
        MarkerPtr marker = *mit;
        for (j = 0; j < (int) frameList.length(); ++j) {
            MTime frame = frameList[j];

            bool enable = false;
            status = marker->getEnable(enable, frame);
            CHECK_MSTATUS_AND_RETURN(status, numErrors);

            double weight = 0.0;
            status = marker->getWeight(weight, frame);
            CHECK_MSTATUS_AND_RETURN(status, numErrors);

            if ((enable == true) && (weight > 0.0)) {
                // First index is into 'markerList'
                // Second index is into 'frameList'
                IndexPair markerPair(i, j);
                errorToMarkerList.push_back(markerPair);
                numErrors += ERRORS_PER_MARKER;

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
                CHECK_MSTATUS(status);
                MPoint marker_pos;
                status = marker->getPos(marker_pos, frame);
                CHECK_MSTATUS(status);
                marker_pos = marker_pos * cameraWorldProjectionMatrix;
                marker_pos.cartesianize();
                markerPosList.push_back(marker_pos);
            }
        }
        i++;
    }

    // Normalise the weights per-frame, using the weight 'max'
    // computed above.
    i = 0;
    typedef IndexPairList::const_iterator IndexPairListCit;
    IndexPairListCit eit = errorToMarkerList.begin();
    for (; eit != errorToMarkerList.end(); ++eit) {
        double weight = markerWeightList[i];

        int markerIndex = eit->first;
        int frameIndex = eit->second;

        xit = weightMaxPerFrame.find(frameIndex);
        assert(xit != weightMaxPerFrame.end());
        double weight_max = xit->second;

        weight = weight / weight_max;
        markerWeightList[i] = weight;
        ++i;
    }
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
        value = (value * xscale) + xoffset;
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

        double offset = attr->getOffsetValue();
        double scale = attr->getScaleValue();
        double xmin = attr->getMinimumValue();
        double xmax = attr->getMaximumValue();
        double value = paramList[i];
        value = fromInternalToBounded(value, xmin, xmax, offset, scale);

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
bool compute_error_stats(int numberOfErrors,
                         SolverData &userData,
                         double &errorAvg,
                         double &errorMin,
                         double &errorMax){
    errorAvg = 0;
    errorMin = std::numeric_limits<double>::max();
    errorMax = -0.0;
    for (int i = 0; i < numberOfErrors; ++i) {
        // TODO: Shouldn't 'err' actually be the errorDistanceList
        // value?
        double err = userData.errorList[i];
        errorAvg += userData.errorDistanceList[i / ERRORS_PER_MARKER];
        if (err < errorMin) { errorMin = err; }
        if (err > errorMax) { errorMax = err; }
    }
    assert(numberOfErrors > 0);
    errorAvg /= (double) numberOfErrors;
    return true;
}


void print_details(
        SolverResult &solverResult,
        SolverData &userData,
        SolverTimer &timer,
        int numberOfParameters,
        int numberOfErrors,
        std::vector<double> &paramList,
        MStringArray &outResult) {
    bool verbose = false;

    VRB("Results:");
    VRB("Solver returned " << solverResult.success << " in " << solverResult.iterations
                           << " iterations");

    int reasonNum = solverResult.reason_number;
    VRB("Reason: " << solverResult.reason);
    VRB("Reason number: " << solverResult.reason_number);
    VRB("");

    VRB(std::endl << std::endl << "Solve Information:");
    VRB("Maximum Error: " << solverResult.errorMax);
    VRB("Average Error: " << solverResult.errorAvg);
    VRB("Minimum Error: " << solverResult.errorMin);

    VRB("Iterations: " << solverResult.iterations);
    VRB("Termination Reason: " << solverResult.reason);
    VRB("Function Evaluations: " << solverResult.functionEvals);
    VRB("Jacobian Evaluations: " << solverResult.jacobianEvals);

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
    for (int i = 0; i < (numberOfErrors / ERRORS_PER_MARKER); ++i) {
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
 * in the outResult.
 *
 */
bool solve(int iterMax,
           double tau,
           double eps1,
           double eps2,
           double eps3,
           double delta,
           int autoDiffType,
           int autoParamScale,
           int solverType,
           CameraPtrList &cameraList,
           MarkerPtrList &markerList,
           BundlePtrList &bundleList,
           AttrPtrList &attrList,
           MTimeArray &frameList,
           MDGModifier &dgmod,
           MAnimCurveChange &curveChange,
           MComputation &computation,
           MString &debugFile,
           MStringArray &printStatsList,
           bool verbose,
           MStringArray &outResult) {
    MStatus status;
    std::string resultStr;
    int ret = 1;
    MGlobal::MMayaState mayaSessionState = MGlobal::mayaState(&status);

    bool printStats = false;
    bool printStatsInput = false;
    bool printStatsAffects = false;
    if (printStatsList.length() > 0) {
         for (int i = 0; i < printStatsList.length(); ++i) {
              if (printStatsList[i] == PRINT_STATS_MODE_INPUTS) {
                   printStatsInput = true;
                   printStats = true;
              } else if (printStatsList[i] == PRINT_STATS_MODE_AFFECTS) {
                   printStatsAffects = true;
                   printStats = true;
              }
         }
    }

#ifdef MAYA_PROFILE
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope profilingScope(profileCategory,
                                   MProfiler::kColorC_L3,
                                   "solve");
#endif

    SolverOptions solverOptions;
    solverOptions.iterMax = iterMax;
    solverOptions.tau = tau;
    solverOptions.eps1 = eps1;
    solverOptions.eps2 = eps2;
    solverOptions.eps3 = eps3;
    solverOptions.delta = delta;
    solverOptions.autoDiffType = autoDiffType;
    solverOptions.autoParamScale = autoParamScale;
    solverOptions.solverType = solverType;

    IndexPairList paramToAttrList;
    IndexPairList errorToMarkerList;
    std::vector<MPoint> markerPosList;
    std::vector<double> markerWeightList;
    std::vector<double> errorList(1);
    std::vector<double> paramList(1);
    std::vector<double> jacobianList(1);

    int numberOfErrors = 0;
    MarkerPtrList validMarkerList;
    numberOfErrors = countUpNumberOfErrors(
            markerList,
            frameList,
            validMarkerList,
            markerPosList,
            markerWeightList,
            errorToMarkerList,
            status
    );

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
    }
    if (printStats == true) {
         return true;
    }

    VRB("Number of Parameters; numberOfParameters=" << numberOfParameters);
    VRB("Number of Errors; numberOfErrors=" << numberOfErrors);
    if (numberOfParameters > numberOfErrors) {
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
    errorDistanceList.resize((unsigned long) numberOfErrors / ERRORS_PER_MARKER, 0);
    assert(errorToMarkerList.size() == errorDistanceList.size());

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

    VRB("Solving...");
    VRB("Solver Type=" << solverType);
    VRB("Maximum Iterations=" << iterMax);
    VRB("Tau=" << tau);
    VRB("Epsilon1=" << eps1);
    VRB("Epsilon2=" << eps2);
    VRB("Epsilon3=" << eps3);
    VRB("Delta=" << fabs(delta));
    VRB("Auto Differencing Type=" << autoDiffType);

    // MComputation helper.
    bool showProgressBar = true;
    bool isInterruptable = true;
    bool useWaitCursor = true;
    computation.setProgressRange(0, iterMax);
    computation.beginComputation(showProgressBar, isInterruptable, useWaitCursor);

    // Start Solving
    SolverTimer timer;
    timer.solveBenchTimer.start();
    timer.solveBenchTicks.start();

    // Solving Objects.
    SolverData userData;
    userData.cameraList = cameraList;
    userData.markerList = markerList;
    userData.bundleList = bundleList;
    userData.attrList = attrList;
    userData.frameList = frameList;

    userData.paramToAttrList = paramToAttrList;
    userData.errorToMarkerList = errorToMarkerList;
    userData.markerPosList = markerPosList;
    userData.markerWeightList = markerWeightList;

    userData.paramList = paramList;
    userData.errorList = errorList;
    userData.errorDistanceList = errorDistanceList;
    userData.jacobianList = jacobianList;
    userData.iterNum = 0;
    userData.jacIterNum = 0;
    userData.imageWidth = 2048.0;  // TODO: Get actual image plane resolution.

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

    std::ofstream file;
    if (debugFile.length() > 0) {
        const char *debugFileNameChar = debugFile.asChar();
        file.open(debugFileNameChar);
        if (file.is_open() == true) {
             file << std::endl;
             file.close();
        }
    }

    SolverResult solveResult;
    if (solverType == SOLVER_TYPE_LEVMAR) {

#ifndef USE_SOLVER_LEVMAR

        ERR("Solver Type is not supported by this compiled plug-in. "
            << "solverType=" << solverType);
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

    } else if (solverType == SOLVER_TYPE_CMINPACK_LM_DIF) {

#ifndef USE_SOLVER_CMINPACK

        ERR("Solver Type is not supported by this compiled plug-in. "
            << "solverType=" << solverType);
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

    } else if (solverType == SOLVER_TYPE_CMINPACK_LM_DER) {

#ifndef USE_SOLVER_CMINPACK

        ERR("Solver Type is not supported by this compiled plug-in. "
            << "solverType=" << solverType);
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
        ERR("Solver Type is invalid. solverType=" << solverType);
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
            numberOfErrors, userData,
            errorAvg, errorMin, errorMax);
    solveResult.errorAvg = errorAvg;
    solveResult.errorMin = errorMin;
    solveResult.errorMax = errorMax;

    print_details(
            solveResult,
            userData,
            timer,
            numberOfParameters,
            numberOfErrors,
            paramList,
            outResult);
    return ret != -1;
};
