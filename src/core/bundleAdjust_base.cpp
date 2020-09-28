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
#include <map>

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
#include <maya/MStreamUtils.h>
#include <maya/MFnAttribute.h>
#include <maya/MDagPath.h>

// Solver Utilities
#include <mayaUtils.h>
#include <Camera.h>
#include <Attr.h>
#include <Marker.h>

// Local
#include <core/bundleAdjust_base.h>
#include <core/bundleAdjust_relationships.h>
#include <core/bundleAdjust_levmar_bc_dif.h>
#include <core/bundleAdjust_cminpack_base.h>
#include <core/bundleAdjust_cminpack_lmdif.h>
#include <core/bundleAdjust_cminpack_lmder.h>
#include <core/bundleAdjust_solveFunc.h>



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
};


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


bool get_initial_parameters(int numberOfParameters,
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


void logResultsSolveDetails(
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
            MStreamUtils::stdErrorStream() << "Solver returned SUCCESS    | ";
        } else {
            MStreamUtils::stdErrorStream() << "Solver returned FAILURE    | ";
        }

        char formatBuffer[128];
        sprintf(
            formatBuffer,
            "error avg %8.4f   min %8.4f   max %8.4f  iterations %03u",
            solverResult.errorAvg,
            solverResult.errorMin,
            solverResult.errorMax,
            solverResult.iterations);
        // Note: We use std::endl to flush the stream, and ensure an
        //  update for the user.
        MStreamUtils::stdErrorStream() << std::string(formatBuffer)
                                       << std::endl;
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


MStatus logResultsObjectCounts(int numberOfParameters,
                               int numberOfErrors,
                               int numberOfMarkerErrors,
                               int numberOfAttrStiffnessErrors,
                               int numberOfAttrSmoothnessErrors,
                               MStringArray &outResult) {
    MStatus status = MStatus::kSuccess;

    std::string resultStr;
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

    // TODO: List all the frame numbers that are valid for solving,
    //  and invalid for solving.
    return status;
}


/*
 * Print out the marker-to-attribute 'affects' relationship.
 *
 * markerToAttrList is expected to be pre-computed from the function
 * 'getMarkerToAttributeRelationship'.
 */
MStatus logResultsMarkerAffectsAttribute(MarkerPtrList markerList,
                                         AttrPtrList attrList,
                                         BoolList2D markerToAttrList,
                                         MStringArray &outResult) {
    MStatus status = MStatus::kSuccess;
    std::string resultStr;

    std::vector<bool>::const_iterator cit_inner;
    BoolList2D::const_iterator cit_outer;
    int markerIndex = 0;
    for (cit_outer = markerToAttrList.cbegin();
         cit_outer != markerToAttrList.cend();
         ++cit_outer){

        int attrIndex = 0;
        std::vector<bool> inner = *cit_outer;
        for (cit_inner = inner.cbegin();
             cit_inner != inner.cend();
             ++cit_inner){
            MarkerPtr marker = markerList[markerIndex];
            AttrPtr attr = attrList[attrIndex];

            // Get node names.
            const char *markerName = marker->getNodeName().asChar();

            // Get attribute full path.
            MPlug plug = attr->getPlug();
            MObject attrNode = plug.node();
            MFnDagNode attrFnDagNode(attrNode);
            MString attrNodeName = attrFnDagNode.fullPathName();
            MString attrAttrName = plug.partialName(
                false, true, true, false, false, true);
            MString attrNameString = attrNodeName + "." + attrAttrName;
            const char *attrName = attrNameString.asChar();

            int value = *cit_inner;
            resultStr = "marker_affects_attribute=";
            resultStr += markerName;
            resultStr += CMD_RESULT_SPLIT_CHAR;
            resultStr += attrName;
            resultStr += CMD_RESULT_SPLIT_CHAR;
            resultStr += string::numberToString<int>(value);
            outResult.append(MString(resultStr.c_str()));

            ++attrIndex;
        }

        ++markerIndex;
    }
    return status;
}


/*
 * Print out if objects added to the solve (such as markers and
 * attributes) are being used, or are unused.
 */
MStatus logResultsSolveObjectUsage(MarkerPtrList usedMarkerList,
                                   MarkerPtrList unusedMarkerList,
                                   AttrPtrList usedAttrList,
                                   AttrPtrList unusedAttrList,
                                   MStringArray &outResult) {
    MStatus status = MStatus::kSuccess;
    std::string resultStr;

    // Append a string with all the *used* marker names.
    resultStr = "markers_used=";
    for (MarkerPtrListCIt mit = usedMarkerList.cbegin();
         mit != usedMarkerList.cend();
         ++mit){
        MarkerPtr marker = *mit;
        const char *markerName = marker->getLongNodeName().asChar();
        resultStr += markerName;
        resultStr += CMD_RESULT_SPLIT_CHAR;
    }
    outResult.append(MString(resultStr.c_str()));

    // Append a string with all the *unused* marker names.
    resultStr = "markers_unused=";
    for (MarkerPtrListCIt mit = unusedMarkerList.cbegin();
         mit != unusedMarkerList.cend();
         ++mit){
        MarkerPtr marker = *mit;
        const char *markerName = marker->getLongNodeName().asChar();
        resultStr += markerName;
        resultStr += CMD_RESULT_SPLIT_CHAR;
    }
    outResult.append(MString(resultStr.c_str()));

    // Append a string with all the *used* attribute names.
    resultStr = "attributes_used=";
    for (AttrPtrListCIt ait = usedAttrList.cbegin();
         ait != usedAttrList.cend();
         ++ait){
        AttrPtr attr = *ait;
        const char *attrName = attr->getLongName().asChar();
        resultStr += attrName;
        resultStr += CMD_RESULT_SPLIT_CHAR;
    }
    outResult.append(MString(resultStr.c_str()));

    // Append a string with all the *unused* attribute names.
    resultStr = "attributes_unused=";
    for (AttrPtrListCIt ait = unusedAttrList.cbegin();
         ait != unusedAttrList.cend();
         ++ait){
        AttrPtr attr = *ait;
        // const char *attrName = attr->getName().asChar();
        const char *attrName = attr->getLongName().asChar();
        resultStr += attrName;
        resultStr += CMD_RESULT_SPLIT_CHAR;
    }
    outResult.append(MString(resultStr.c_str()));

    return status;
}

typedef std::map<int, int> IndexCountMap;
typedef IndexCountMap::iterator IndexCountMapIt;

/*
 * Loop over original list contents and add the objects into the
 * respective output list, based on how much it was used (using
 * indexCountMap).
 */
template <class _V, class _T>
void _splitIntoUsedAndUnusedLists(_T inputList,
                                  IndexCountMap indexCountMap,
                                  _T &usedList,
                                  _T &unusedList) {
    // Reset data structures
    usedList.clear();
    unusedList.clear();

    for (int i = 0; i < inputList.size(); ++i) {
        bool used = false;
        _V object = inputList[i];
        IndexCountMapIt it = indexCountMap.find(i);
        if (it != indexCountMap.end()) {
            int count = it->second;
            if (count > 0) {
                used = true;
            }
        }
        if (used == true) {
            usedList.push_back(object);
        } else {
            unusedList.push_back(object);
        }
    }
    return;
}


/*
 * Increment the value of key in the indexCountMap, by 1.
 *
 */
IndexCountMap _incrementMapIndex(int key, IndexCountMap indexCountMap) {
    IndexCountMapIt it = indexCountMap.find(key);
    int temp;
    if (it != indexCountMap.end()) {
        // Update the value.
        temp = it->second + 1;
        indexCountMap.erase(it);
    } else {
        // This is the first value to be inserted.
        temp = 1;
    }
    indexCountMap.insert(std::pair<int, int>(key, temp));
    return indexCountMap;
}


/*
 * Split the given Markers and Attributes into both used and unused
 * objects.
 */
MStatus splitUsedMarkersAndAttributes(MarkerPtrList markerList,
                                      AttrPtrList attrList,
                                      BoolList2D markerToAttrList,
                                      MarkerPtrList &out_usedMarkerList,
                                      MarkerPtrList &out_unusedMarkerList,
                                      AttrPtrList &out_usedAttrList,
                                      AttrPtrList &out_unusedAttrList) {
    MStatus status = MStatus::kSuccess;

    IndexCountMap markerIndexUsedCount;
    IndexCountMap attrIndexUsedCount;

    std::vector<bool>::const_iterator cit_inner;
    BoolList2D::const_iterator cit_outer;
    int markerIndex = 0;
    for (cit_outer = markerToAttrList.cbegin();
         cit_outer != markerToAttrList.cend();
         ++cit_outer){

        int attrIndex = 0;
        std::vector<bool> inner = *cit_outer;
        for (cit_inner = inner.cbegin();
             cit_inner != inner.cend();
             ++cit_inner){
            MarkerPtr marker = markerList[markerIndex];
            AttrPtr attr = attrList[attrIndex];

            int value = *cit_inner;
            if (value == 1){
                markerIndexUsedCount = _incrementMapIndex(
                        markerIndex, markerIndexUsedCount);
                attrIndexUsedCount = _incrementMapIndex(
                        attrIndex, attrIndexUsedCount);
            }

            ++attrIndex;
        }
        ++markerIndex;
    }

    _splitIntoUsedAndUnusedLists<MarkerPtr, MarkerPtrList>(
        markerList,
        markerIndexUsedCount,
        out_usedMarkerList,
        out_unusedMarkerList);
    _splitIntoUsedAndUnusedLists<AttrPtr, AttrPtrList>(
        attrList,
        attrIndexUsedCount,
        out_usedAttrList,
        out_unusedAttrList);
    return status;
}


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
    MGlobal::MMayaState mayaSessionState = MGlobal::mayaState(&status);

    bool verbose = with_verbosity;
    bool printStats = false;
    bool printStatsInput = false;
    bool printStatsAffects = false;
    bool printStatsUsedSolveObjects = false;
    bool printStatsDeviation = false;
    if (printStatsList.length() > 0) {
        for (unsigned int i = 0; i < printStatsList.length(); ++i) {
            if (printStatsList[i] == PRINT_STATS_MODE_INPUTS) {
                printStatsInput = true;
                printStats = true;
            } else if (printStatsList[i] == PRINT_STATS_MODE_AFFECTS) {
                printStatsAffects = true;
                printStats = true;
            } else if (printStatsList[i] == PRINT_STATS_MODE_USED_SOLVE_OBJECTS) {
                printStatsUsedSolveObjects = true;
                printStats = true;
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

    // Query the relationship by pre-computed attributes on the
    // Markers. If the attributes do not exist, we assume all markers
    // affect all attributes (and therefore suffer a performance
    // problem).
    BoolList2D markerToAttrList;
    getMarkerToAttributeRelationship(
            markerList,
            attrList,
            markerToAttrList,
            status);
    CHECK_MSTATUS(status);

    // Split the used and unused markers and attributes.
    MarkerPtrList usedMarkerList;
    MarkerPtrList unusedMarkerList;
    AttrPtrList usedAttrList;
    AttrPtrList unusedAttrList;
    splitUsedMarkersAndAttributes(
            markerList,
            attrList,
            markerToAttrList,
            usedMarkerList,
            unusedMarkerList,
            usedAttrList,
            unusedAttrList);

    // Print warnings about unused solve objects.
    if (unusedMarkerList.size() > 0) {
        WRN("Unused Markers detected and ignored:");
        for (MarkerPtrListCIt mit = unusedMarkerList.cbegin();
             mit != unusedMarkerList.cend();
             ++mit) {
            MarkerPtr marker = *mit;
            const char *markerName = marker->getLongNodeName().asChar();
            WRN("-> " << markerName);
        }
    }
    if (unusedAttrList.size() > 0) {
        WRN("Unused Attributes detected and ignored:");
        for (AttrPtrListCIt ait = unusedAttrList.cbegin();
             ait != unusedAttrList.cend();
             ++ait) {
            AttrPtr attr = *ait;
            const char *attrName = attr->getLongName().asChar();
            WRN("-> " << attrName);
        }
    }

    // Change the list of Markers and Attributes to filter out unused
    // objects.
    bool usedObjectsChanged = false;
    if (solverOptions.removeUnusedMarkers == false) {
        usedMarkerList = markerList;
    } else {
        usedObjectsChanged = true;
    }
    if (solverOptions.removeUnusedAttributes == false) {
        usedAttrList = attrList;
    }
    else {
        usedObjectsChanged = true;
    }
    if (usedObjectsChanged == true) {
        getMarkerToAttributeRelationship(
                usedMarkerList,
                usedAttrList,
                markerToAttrList,
                status);
        CHECK_MSTATUS(status);
    }

    IndexPairList paramToAttrList;
    IndexPairList errorToMarkerList;
    std::vector<MPoint> markerPosList;
    std::vector<double> markerWeightList;
    std::vector<double> errorList(1);
    std::vector<double> paramList(1);
    std::vector<double> previousParamList(1);
    std::vector<double> jacobianList(1);

    int numberOfErrors = 0;
    int numberOfMarkerErrors = 0;
    int numberOfAttrStiffnessErrors = 0;
    int numberOfAttrSmoothnessErrors = 0;
    MarkerPtrList validMarkerList;
    numberOfErrors = countUpNumberOfErrors(
            usedMarkerList,
            stiffAttrsList,
            smoothAttrsList,
            frameList,

            // Outputs
            validMarkerList,
            markerPosList,
            markerWeightList,
            errorToMarkerList,
            numberOfMarkerErrors,
            numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors,
            status);
    CHECK_MSTATUS(status);
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
            usedAttrList,
            frameList,

            // Outputs
            camStaticAttrList,
            camAnimAttrList,
            staticAttrList,
            animAttrList,
            paramLowerBoundList,
            paramUpperBoundList,
            paramWeightList,
            paramToAttrList,
            paramFrameList,
            status);
    CHECK_MSTATUS(status);
    assert(paramLowerBoundList.size() == numberOfParameters);
    assert(paramUpperBoundList.size() == numberOfParameters);
    assert(paramWeightList.size() == numberOfParameters);
    assert(numberOfParameters >= usedAttrList.size());

    // Expand the 'Marker to Attribute' relationship into errors and
    // parameter relationships.
    BoolList2D errorToParamList;
    findErrorToParameterRelationship(
            usedMarkerList,
            usedAttrList,
            frameList,
            numberOfParameters,
            numberOfMarkerErrors,
            paramToAttrList,
            errorToMarkerList,
            markerToAttrList,

            // Outputs
            errorToParamList,
            status);
    CHECK_MSTATUS(status);

    if (printStatsInput == true) {
        assert(printStats == true);
        status = logResultsObjectCounts(
            numberOfParameters,
            numberOfErrors,
            numberOfMarkerErrors,
            numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors,
            outResult);
        CHECK_MSTATUS(status);
    }

    if (printStatsUsedSolveObjects == true) {
        assert(printStats == true);
        status = logResultsSolveObjectUsage(
            usedMarkerList,
            unusedMarkerList,
            usedAttrList,
            unusedAttrList,
            outResult);
        CHECK_MSTATUS(status);
    }

    if (printStatsAffects == true) {
        assert(printStats == true);
        status = logResultsMarkerAffectsAttribute(
                usedMarkerList,
                usedAttrList,
                markerToAttrList,
                outResult);
        CHECK_MSTATUS(status);
    }

    VRB("Number of Markers; used="
        << usedMarkerList.size() << " | unused="
        << unusedMarkerList.size());
    VRB("Number of Attributes; used="
        << usedAttrList.size() << " | unused="
        << unusedAttrList.size());
    VRB("Number of Parameters; " << numberOfParameters);
    VRB("Number of Frames; " << frameList.length());
    VRB("Number of Marker Errors; " << numberOfMarkerErrors);
    VRB("Number of Attribute Stiffness Errors; " << numberOfAttrStiffnessErrors);
    VRB("Number of Attribute Smoothness Errors; " << numberOfAttrSmoothnessErrors);
    VRB("Number of Total Errors; " << numberOfErrors);

    // Bail out of solve if we don't have enough used markers or
    // attributes.
    if ((usedMarkerList.size() == 0) || (usedAttrList.size() == 0)) {
        if (printStats == true) {
            // If the user is asking to print statistics, then we have
            // successfully achieved that goal and we cannot continue
            // to generate statistics, because not enought markers or
            // attributes were used.
            return true;
        }
        ERR("Solver failure; not enough markers or attributes are not used by solver "
            << "used markers=" << usedMarkerList.size() << " "
            << "used attributes=" << usedAttrList.size());
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        return false;
    }

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
    assert(numberOfErrors > 0);
    assert(numberOfParameters > 0);

    paramList.resize((unsigned long) numberOfParameters, 0);
    previousParamList.resize((unsigned long) numberOfParameters, 0);
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
        for (unsigned int i = 0; i < frameList.length(); i++) {
            MTime frame(frameList[i]);
            ss << " " << frame;
        }
        std::string tmp_string = ss.str();

        size_t num = 100 - tmp_string.size();
        if (num < 0) {
            num = 0;
        }
        std::string pad_chars(num, '=');

        MStreamUtils::stdErrorStream() << tmp_string << " " << pad_chars << std::endl;
    }

    // MComputation helper.
    bool showProgressBar = true;
    bool isInterruptable = true;
    bool useWaitCursor = true;
    if (printStats == false) {
        computation.setProgressRange(0, solverOptions.iterMax);
        computation.beginComputation(showProgressBar, isInterruptable, useWaitCursor);
    }

    // Start Solving
    SolverTimer timer;
    if (printStats == false) {
        timer.solveBenchTimer.start();
        timer.solveBenchTicks.start();
    }

    // Solving Objects.
    SolverData userData;
    userData.cameraList = cameraList;
    userData.markerList = usedMarkerList;
    userData.bundleList = bundleList;
    userData.attrList = usedAttrList;
    userData.frameList = frameList;
    userData.smoothAttrsList = smoothAttrsList;
    userData.stiffAttrsList = stiffAttrsList;

    userData.paramToAttrList = paramToAttrList;
    userData.errorToMarkerList = errorToMarkerList;
    userData.markerPosList = markerPosList;
    userData.markerWeightList = markerWeightList;
    userData.paramFrameList = paramFrameList;
    userData.errorToParamList = errorToParamList;

    userData.paramList = paramList;
    userData.previousParamList = previousParamList;
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

    // Calculate initial errors.
    double initialErrorAvg = 0;
    double initialErrorMin = 0;
    double initialErrorMax = 0;
    if (solverOptions.acceptOnlyBetter || printStatsDeviation) {
        // Never write debug data during statistics gathering.
        std::ofstream *debugFileStream = NULL;

        std::vector<bool> frameIndexEnable(frameList.length(), 1);
        std::vector<bool> skipErrorMeasurements(numberOfErrors, 1);
        measureErrors(
            numberOfErrors,
            numberOfMarkerErrors,
            numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors,
            frameIndexEnable,
            skipErrorMeasurements,
            &errorList[0],
            &userData,
            initialErrorAvg,
            initialErrorMax,
            initialErrorMin,
            debugFileStream,
            status);
        CHECK_MSTATUS(status);

        initialErrorAvg = 0;
        initialErrorMin = 0;
        initialErrorMax = 0;
        compute_error_stats(
            numberOfMarkerErrors, userData,
            initialErrorAvg,
            initialErrorMin,
            initialErrorMax);
    }

    if (printStatsDeviation == true) {
        SolverResult solveResult;

        solveResult.success = true;
        solveResult.reason_number = 0;
        solveResult.reason = "";
        solveResult.iterations = 0;
        solveResult.functionEvals = 0;
        solveResult.jacobianEvals = 0;
        solveResult.errorFinal = 0.0;
        solveResult.errorAvg = initialErrorAvg;
        solveResult.errorMin = initialErrorMin;
        solveResult.errorMax = initialErrorMax;

        logResultsSolveDetails(
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
        // There is no more printing to do, we must solve now if we
        // want to solve.
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
    VRB("Get Initial parameters...");
    get_initial_parameters(numberOfParameters,
                           paramList,
                           paramToAttrList,
                           usedAttrList,
                           frameList,
                           outResult);

    VRB("Initial Parameters: ");
    for (int i = 0; i < numberOfParameters; ++i) {
        // Copy parameter values into the 'previous' parameter list.
        previousParamList[i] = paramList[i];
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
                solveResult);

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
                solveResult);

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

    // Solve Finished, re-calculate error, and only set parameters if
    // the average error is lower.
    bool errorIsBetter = true;
    double errorAvg = 0;
    double errorMin = 0;
    double errorMax = 0;
    compute_error_stats(
        numberOfMarkerErrors, userData,
        errorAvg, errorMin, errorMax);
    solveResult.errorAvg = errorAvg;
    solveResult.errorMin = errorMin;
    solveResult.errorMax = errorMax;
    if (solverOptions.acceptOnlyBetter) {
        errorIsBetter = errorAvg <= initialErrorAvg;
    }

    // Set the solved parameters
    VRB("Setting Parameters...");
    if (errorIsBetter) {
        set_maya_attribute_values(
            numberOfParameters,
            paramToAttrList,
            usedAttrList,
            paramList,
            frameList,
            dgmod,
            curveChange);
    } else {
        // Set the initial parameter values.
        set_maya_attribute_values(
            numberOfParameters,
            paramToAttrList,
            usedAttrList,
            previousParamList,
            frameList,
            dgmod,
            curveChange);
    }
    VRB("Solved Parameters:");
    for (int i = 0; i < numberOfParameters; ++i) {
        VRB("-> " << paramList[i]);
    }

    logResultsSolveDetails(
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
