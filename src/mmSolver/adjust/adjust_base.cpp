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
 * Sets up the Bundle Adjustment data and sends it off to the bundling
 * algorithm.
 *
 */

#include "adjust_base.h"

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
#include <maya/MDagPath.h>
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
#include <maya/MVector.h>

// MM Solver
#include "adjust_cminpack_base.h"
#include "adjust_cminpack_lmder.h"
#include "adjust_cminpack_lmdif.h"
#include "adjust_lensModel.h"
#include "adjust_measureErrors.h"
#include "adjust_relationships.h"
#include "adjust_solveFunc.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_scene_graph.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/string_utils.h"
#include "mmscenegraph/mmscenegraph.h"

namespace mmsg = mmscenegraph;

// Get a list of all available solver types (index and name).
//
// This list may change in different plug-ins, as the compiled
// dependencies may differ.
std::vector<SolverTypePair> getSolverTypes() {
    std::vector<std::pair<int, std::string>> solverTypes;
    std::pair<int, std::string> solverType;

    solverType.first = SOLVER_TYPE_CMINPACK_LMDIF;
    solverType.second = SOLVER_TYPE_CMINPACK_LM_DIF_NAME;
    solverTypes.push_back(solverType);

    solverType.first = SOLVER_TYPE_CMINPACK_LMDER;
    solverType.second = SOLVER_TYPE_CMINPACK_LM_DER_NAME;
    solverTypes.push_back(solverType);

    return solverTypes;
}

// Determine the default solver.
SolverTypePair getSolverTypeDefault() {
    int solverTypeIndex = SOLVER_TYPE_DEFAULT_VALUE;
    std::string solverTypeName = "";

    std::vector<SolverTypePair> solverTypes = getSolverTypes();

    const char *defaultSolver_ptr = std::getenv("MMSOLVER_DEFAULT_SOLVER");
    if (defaultSolver_ptr != nullptr) {
        // The memory may change under our feet, we copy the data into a
        // string for save keeping.
        std::string defaultSolver(defaultSolver_ptr);

        std::vector<SolverTypePair>::const_iterator cit;
        for (cit = solverTypes.cbegin(); cit != solverTypes.cend(); ++cit) {
            int index = cit->first;
            std::string name = cit->second;

            if (defaultSolver == name) {
                solverTypeIndex = index;
                solverTypeName = name;
            }
        }
        if (solverTypeName == "") {
            MMSOLVER_ERR(
                "MMSOLVER_DEFAULT_SOLVER environment variable is invalid. "
                << "Value may be "
                << "\"cminpack_lm\", "
                << "\"cminpack_lmder\", "
                << "or \"ceres\"; "
                << "; value=" << defaultSolver);
        }
    }
    SolverTypePair solverType(solverTypeIndex, solverTypeName);
    return solverType;
};

void lossFunctionTrivial(const double z, double &rho0, double &rho1,
                         double &rho2) {
    // Trivial - 'no op' loss function.
    rho0 = z;
    rho1 = 1.0;
    rho2 = 0.0;
};

void lossFunctionSoftL1(const double z, double &rho0, double &rho1,
                        double &rho2) {
    // Soft L1
    double t = 1.0 + z;
    rho0 = 2.0 * (std::pow(t, 0.5 - 1.0));
    rho1 = std::pow(t, -0.5);
    rho2 = -0.5 * std::pow(t, -1.5);
};

void lossFunctionCauchy(const double z, double &rho0, double &rho1,
                        double &rho2) {
    // Cauchy
    rho0 = std::log1p(z);
    double t = 1.0 + z;
    rho1 = 1.0 / t;
    rho2 = -1.0 / std::pow(t, 2.0);
};

void applyLossFunctionToErrors(const int numberOfErrors, double *f,
                               const int loss_type, const double loss_scale) {
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
            MMSOLVER_DBG("Invalid Robust Loss Type given; value=" << loss_type);
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
double parameterBoundFromInternalToExternal(double value, const double xmin,
                                            const double xmax,
                                            const double offset,
                                            const double scale) {
    const double float_max = std::numeric_limits<float>::max();
    if ((xmin <= -float_max) && (xmax >= float_max)) {
        // No bounds!
        value = (value / scale) - offset;
        value = std::max<double>(value, xmin);
        value = std::min<double>(value, xmax);
        return value;
    } else if (xmax >= float_max) {
        // Lower bound only.
        value = xmin - (1.0 + std::sqrt(value * value + 1.0));
    } else if (xmin <= -float_max) {
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
double parameterBoundFromExternalToInternal(double value, double xmin,
                                            double xmax, const double offset,
                                            const double scale) {
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
            value, initial_xmin, initial_xmax, offset, scale);
        return value;
    } else if (xmax >= float_max) {
        // Lower bound only.
        value = std::sqrt(std::pow(((value - xmin) + 1.0), 2.0) - 1.0);
    } else if (xmin <= -float_max) {
        // Upper bound only.
        value = std::sqrt(std::pow((xmax - value) + 1.0, 2.0) - 1.0);
    } else {
        // Both lower and upper bounds.
        value = std::asin((2.0 * (value - xmin) / (xmax - xmin)) - 1.0);
    }

    reconvert_value = parameterBoundFromInternalToExternal(
        value, initial_xmin, initial_xmax, offset, scale);
    return value;
}

bool get_initial_parameters(
    const int numberOfParameters, std::vector<double> &paramList,
    const std::vector<std::pair<int, int>> &paramToAttrList,
    AttrPtrList &attrList, const MTimeArray &frameList,
    MStringArray &outResult) {
    std::string resultStr;
    MStatus status = MS::kSuccess;
    const int timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
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
        status = attr->getValue(value, frame, timeEvalMode);
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
        value = parameterBoundFromExternalToInternal(value, xmin, xmax, xoffset,
                                                     xscale);
        paramList[i] = value;
    }
    return true;
}

bool set_maya_attribute_values(
    const int numberOfParameters,
    const std::vector<std::pair<int, int>> &paramToAttrList,
    AttrPtrList &attrList, const std::vector<double> &paramList,
    const MTimeArray &frameList, MDGModifier &dgmod,
    MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;
    MTime currentFrame = MAnimControl::currentTime();
    for (int i = 0; i < numberOfParameters; ++i) {
        IndexPair attrPair = paramToAttrList[i];
        AttrPtr attr = attrList[attrPair.first];

        const double offset = attr->getOffsetValue();
        const double scale = attr->getScaleValue();
        const double xmin = attr->getMinimumValue();
        const double xmax = attr->getMaximumValue();
        const double solver_value = paramList[i];
        const double real_value = parameterBoundFromInternalToExternal(
            solver_value, xmin, xmax, offset, scale);

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1) {
            frame = frameList[attrPair.second];
        }

        status = attr->setValue(real_value, frame, dgmod, curveChange);
        CHECK_MSTATUS(status);

        if (status != MS::kSuccess) {
            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            MMSOLVER_ERR(
                "set_maya_attribute_values was given an invalid value to set:"
                << " frame=" << frame << " attr name=" << attr_name_char
                << " solver value=" << solver_value
                << " bound value=" << real_value << " offset=" << offset
                << " scale=" << scale << " min=" << xmin << " max=" << xmax);

            break;
        }
    }
    dgmod.doIt();  // Commit changed data into Maya
    return status == MS::kSuccess;
}

// Compute the average error based on the error values
// the solve function last computed.
bool compute_error_stats(const int numberOfMarkerErrors,
                         const std::vector<double> &errorDistanceList,
                         double &out_errorAvg, double &out_errorMin,
                         double &out_errorMax) {
    out_errorAvg = 0;
    out_errorMin = std::numeric_limits<double>::max();
    out_errorMax = -0.0;
    for (int i = 0; i < (numberOfMarkerErrors / ERRORS_PER_MARKER); ++i) {
        const double err = errorDistanceList[i];
        if (!std::isfinite(err)) {
            MMSOLVER_ERR("Error distance value is invalid, skipping: " << err);
            continue;
        }
        out_errorAvg += err;
        if (err < out_errorMin) {
            out_errorMin = err;
        }
        if (err > out_errorMax) {
            out_errorMax = err;
        }
    }
    assert(numberOfMarkerErrors > 0);
    out_errorAvg /= (double)(numberOfMarkerErrors / ERRORS_PER_MARKER);
    return true;
}

void logResultsSolveDetails(SolverResult &solverResult, SolverData &userData,
                            SolverTimer &timer, const int numberOfParameters,
                            const int numberOfMarkerErrors,
                            const int numberOfAttrStiffnessErrors,
                            const int numberOfAttrSmoothnessErrors,
                            const bool verbose, std::vector<double> &paramList,
                            MStringArray &outResult) {
    int numberOfErrors = numberOfMarkerErrors;
    numberOfErrors += numberOfAttrStiffnessErrors;
    numberOfErrors += numberOfAttrSmoothnessErrors;

    MMSOLVER_VRB("Results:");
    if (solverResult.success) {
        MMSOLVER_VRB("Solver returned SUCCESS in " << solverResult.iterations
                                                   << " iterations");
    } else {
        MMSOLVER_VRB("Solver returned FAILURE in " << solverResult.iterations
                                                   << " iterations");
    }

    int reasonNum = solverResult.reason_number;
    MMSOLVER_VRB("Reason: " << solverResult.reason);
    MMSOLVER_VRB("Reason number: " << solverResult.reason_number);

    MMSOLVER_VRB(std::endl << "Solve Information:");
    MMSOLVER_VRB("Maximum Error: " << solverResult.errorMax);
    MMSOLVER_VRB("Average Error: " << solverResult.errorAvg);
    MMSOLVER_VRB("Minimum Error: " << solverResult.errorMin);

    MMSOLVER_VRB("Iterations: " << solverResult.iterations);
    MMSOLVER_VRB("Function Evaluations: " << solverResult.functionEvals);
    MMSOLVER_VRB("Jacobian Evaluations: " << solverResult.jacobianEvals);

    if (verbose == false) {
        if (solverResult.success) {
            MStreamUtils::stdErrorStream() << "Solver returned SUCCESS    | ";
        } else {
            MStreamUtils::stdErrorStream() << "Solver returned FAILURE    | ";
        }

        const size_t buffer_size = 128;
        char formatBuffer[buffer_size];
        std::snprintf(
            formatBuffer, buffer_size,
            "error avg %8.4f   min %8.4f   max %8.4f  iterations %03u",
            solverResult.errorAvg, solverResult.errorMin, solverResult.errorMax,
            solverResult.iterations);
        // Note: We use std::endl to flush the stream, and ensure an
        //  update for the user.
        MMSOLVER_INFO(std::string(formatBuffer));
    }

    // Add all the data into the output string from the Maya command.
    std::string resultStr;
    std::string value = mmstring::numberToString<int>(solverResult.success);
    resultStr = "success=" + value;
    outResult.append(MString(resultStr.c_str()));

    // resultStr = "reason_string=" + levmarReasons[reasonNum];
    // outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<int>(reasonNum);
    resultStr = "reason_num=" + value;
    outResult.append(MString(resultStr.c_str()));

    //    value = mmstring::numberToString<double>(solverResult.errorInitial);
    //    resultStr = "error_initial=" + value;
    //    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<double>(solverResult.errorFinal);
    resultStr = "error_final=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<double>(solverResult.errorAvg);
    resultStr = "error_final_average=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<double>(solverResult.errorMax);
    resultStr = "error_final_maximum=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<double>(solverResult.errorMin);
    resultStr = "error_final_minimum=" + value;
    outResult.append(MString(resultStr.c_str()));

    //    value = mmstring::numberToString<double>(solverResult.errorJt);
    //    resultStr = "error_jt=" + value;
    //    outResult.append(MString(resultStr.c_str()));

    //    value = mmstring::numberToString<double>(solverResult.errorDp);
    //    resultStr = "error_dp=" + value;
    //    outResult.append(MString(resultStr.c_str()));

    //    value = mmstring::numberToString<double>(solverResult.errorMaximum);
    //    resultStr = "error_maximum=" + value;
    //    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<int>(solverResult.iterations);
    resultStr = "iteration_num=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<int>(solverResult.functionEvals);
    resultStr = "iteration_function_num=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<int>(solverResult.jacobianEvals);
    resultStr = "iteration_jacobian_num=" + value;
    outResult.append(MString(resultStr.c_str()));

    //    value = mmstring::numberToString<int>(solverResult.iterationAttempts);
    //    resultStr = "iteration_attempt_num=" + value;
    //    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<int>((bool)userData.userInterrupted);
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

    value =
        mmstring::numberToString<double>(timer.solveBenchTimer.get_seconds());
    resultStr = "timer_solve=" + value;
    outResult.append(MString(resultStr.c_str()));

    value =
        mmstring::numberToString<double>(timer.funcBenchTimer.get_seconds());
    resultStr = "timer_function=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<double>(timer.jacBenchTimer.get_seconds());
    resultStr = "timer_jacobian=" + value;
    outResult.append(MString(resultStr.c_str()));

    value =
        mmstring::numberToString<double>(timer.paramBenchTimer.get_seconds());
    resultStr = "timer_parameter=" + value;
    outResult.append(MString(resultStr.c_str()));

    value =
        mmstring::numberToString<double>(timer.paramBenchTimer.get_seconds());
    resultStr = "timer_error=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<debug::Ticks>(
        timer.solveBenchTicks.get_ticks());
    resultStr = "ticks_solve=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<debug::Ticks>(
        timer.funcBenchTicks.get_ticks());
    resultStr = "ticks_function=" + value;
    outResult.append(MString(resultStr.c_str()));

    value =
        mmstring::numberToString<debug::Ticks>(timer.jacBenchTicks.get_ticks());
    resultStr = "ticks_jacobian=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<debug::Ticks>(
        timer.paramBenchTicks.get_ticks());
    resultStr = "ticks_parameter=" + value;
    outResult.append(MString(resultStr.c_str()));

    value = mmstring::numberToString<debug::Ticks>(
        timer.paramBenchTicks.get_ticks());
    resultStr = "ticks_error=" + value;
    outResult.append(MString(resultStr.c_str()));

    resultStr = "solve_parameter_list=";
    for (int i = 0; i < numberOfParameters; ++i) {
        resultStr += mmstring::numberToString<double>(paramList[i]);
        resultStr += CMD_RESULT_SPLIT_CHAR;
    }
    outResult.append(MString(resultStr.c_str()));

    resultStr = "solve_error_list=";
    for (int i = 0; i < numberOfErrors; ++i) {
        double err = userData.errorList[i];
        resultStr += mmstring::numberToString<double>(err);
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
        const double d = userData.errorDistanceList[i];

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
        frameErrorMapping.insert(
            std::pair<int, ErrorPair>(markerPair.second, pair));

        resultStr = "error_per_marker_per_frame=";
        resultStr += markerName;
        resultStr += CMD_RESULT_SPLIT_CHAR;
        resultStr +=
            mmstring::numberToString<double>(frame.asUnits(MTime::uiUnit()));
        resultStr += CMD_RESULT_SPLIT_CHAR;
        resultStr += mmstring::numberToString<double>(d);
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
        resultStr +=
            mmstring::numberToString<double>(frame.asUnits(MTime::uiUnit()));
        resultStr += CMD_RESULT_SPLIT_CHAR;
        resultStr += mmstring::numberToString<double>(d / num);
        outResult.append(MString(resultStr.c_str()));
    }
};

MStatus logResultsObjectCounts(const int numberOfParameters,
                               const int numberOfErrors,
                               const int numberOfMarkerErrors,
                               const int numberOfAttrStiffnessErrors,
                               const int numberOfAttrSmoothnessErrors,
                               MStringArray &outResult) {
    MStatus status = MStatus::kSuccess;

    std::string resultStr;
    resultStr = "numberOfParameters=";
    resultStr += mmstring::numberToString<int>(numberOfParameters);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "numberOfErrors=";
    resultStr += mmstring::numberToString<int>(numberOfErrors);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "numberOfMarkerErrors=";
    resultStr += mmstring::numberToString<int>(numberOfMarkerErrors);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "numberOfAttrStiffnessErrors=";
    resultStr += mmstring::numberToString<int>(numberOfAttrStiffnessErrors);
    outResult.append(MString(resultStr.c_str()));

    resultStr = "numberOfAttrSmoothnessErrors=";
    resultStr += mmstring::numberToString<int>(numberOfAttrSmoothnessErrors);
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
MStatus logResultsMarkerAffectsAttribute(const MarkerPtrList markerList,
                                         const AttrPtrList attrList,
                                         const BoolList2D markerToAttrList,
                                         MStringArray &outResult) {
    MStatus status = MStatus::kSuccess;
    std::string resultStr;

    std::vector<bool>::const_iterator cit_inner;
    BoolList2D::const_iterator cit_outer;
    int markerIndex = 0;
    for (cit_outer = markerToAttrList.cbegin();
         cit_outer != markerToAttrList.cend(); ++cit_outer) {
        int attrIndex = 0;
        std::vector<bool> inner = *cit_outer;
        for (cit_inner = inner.cbegin(); cit_inner != inner.cend();
             ++cit_inner) {
            MarkerPtr marker = markerList[markerIndex];
            AttrPtr attr = attrList[attrIndex];

            // Get node names.
            const char *markerName = marker->getNodeName().asChar();

            // Get attribute full path.
            MPlug plug = attr->getPlug();
            MObject attrNode = plug.node();
            MFnDagNode attrFnDagNode(attrNode);
            MString attrNodeName = attrFnDagNode.fullPathName();
            MString attrAttrName =
                plug.partialName(false, true, true, false, false, true);
            MString attrNameString = attrNodeName + "." + attrAttrName;
            const char *attrName = attrNameString.asChar();

            int value = *cit_inner;
            resultStr = "marker_affects_attribute=";
            resultStr += markerName;
            resultStr += CMD_RESULT_SPLIT_CHAR;
            resultStr += attrName;
            resultStr += CMD_RESULT_SPLIT_CHAR;
            resultStr += mmstring::numberToString<int>(value);
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
MStatus logResultsSolveObjectUsage(const MarkerPtrList usedMarkerList,
                                   const MarkerPtrList unusedMarkerList,
                                   const AttrPtrList usedAttrList,
                                   const AttrPtrList unusedAttrList,
                                   MStringArray &outResult) {
    MStatus status = MStatus::kSuccess;

    // Append a string with all the *used* marker names.
    if (usedMarkerList.size() > 0) {
        MString markerUsedStr = "markers_used=";
        for (MarkerPtrListCIt mit = usedMarkerList.cbegin();
             mit != usedMarkerList.cend(); ++mit) {
            MarkerPtr marker = *mit;
            markerUsedStr += marker->getLongNodeName();
            markerUsedStr += CMD_RESULT_SPLIT_CHAR;
        }
        outResult.append(markerUsedStr);
    }

    // Append a string with all the *unused* marker names.
    if (unusedMarkerList.size() > 0) {
        MString markerUnusedStr = "markers_unused=";
        for (MarkerPtrListCIt mit = unusedMarkerList.cbegin();
             mit != unusedMarkerList.cend(); ++mit) {
            MarkerPtr marker = *mit;
            markerUnusedStr += marker->getLongNodeName();
            markerUnusedStr += CMD_RESULT_SPLIT_CHAR;
        }
        outResult.append(markerUnusedStr);
    }

    // Append a string with all the *used* attribute names.
    if (usedAttrList.size() > 0) {
        MString attrUsedStr = "attributes_used=";
        for (AttrPtrListCIt ait = usedAttrList.cbegin();
             ait != usedAttrList.cend(); ++ait) {
            AttrPtr attr = *ait;
            attrUsedStr += attr->getLongName();
            attrUsedStr += CMD_RESULT_SPLIT_CHAR;
        }
        outResult.append(attrUsedStr);
    }

    // Append a string with all the *unused* attribute names.
    if (unusedAttrList.size() > 0) {
        MString attrUnusedStr = "attributes_unused=";
        for (AttrPtrListCIt ait = unusedAttrList.cbegin();
             ait != unusedAttrList.cend(); ++ait) {
            AttrPtr attr = *ait;
            attrUnusedStr += attr->getLongName();
            attrUnusedStr += CMD_RESULT_SPLIT_CHAR;
        }
        outResult.append(attrUnusedStr);
    }

    return status;
}

typedef std::map<size_t, int> IndexCountMap;
typedef IndexCountMap::iterator IndexCountMapIt;

/*
 * Loop over original list contents and add the objects into the
 * respective output list, based on how much it was used (using
 * indexCountMap).
 */
template <class _V, class _T>
void _splitIntoUsedAndUnusedLists(_T inputList, IndexCountMap indexCountMap,
                                  _T &usedList, _T &unusedList) {
    // Reset data structures
    usedList.clear();
    unusedList.clear();

    for (size_t i = 0; i < inputList.size(); ++i) {
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
IndexCountMap _incrementMapIndex(const size_t key,
                                 IndexCountMap &indexCountMap) {
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
    indexCountMap.insert(std::pair<size_t, int>(key, temp));
    return indexCountMap;
}

/*
 * Split the given Markers and Attributes into both used and unused
 * objects.
 */
MStatus splitUsedMarkersAndAttributes(const MarkerPtrList markerList,
                                      const AttrPtrList attrList,
                                      const BoolList2D markerToAttrList,
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
         cit_outer != markerToAttrList.cend(); ++cit_outer) {
        int attrIndex = 0;
        std::vector<bool> inner = *cit_outer;
        for (cit_inner = inner.cbegin(); cit_inner != inner.cend();
             ++cit_inner) {
            MarkerPtr marker = markerList[markerIndex];
            AttrPtr attr = attrList[attrIndex];

            int value = *cit_inner;
            if (value == 1) {
                markerIndexUsedCount =
                    _incrementMapIndex(markerIndex, markerIndexUsedCount);
                attrIndexUsedCount =
                    _incrementMapIndex(attrIndex, attrIndexUsedCount);
            }
            ++attrIndex;
        }
        ++markerIndex;
    }

    _splitIntoUsedAndUnusedLists<MarkerPtr, MarkerPtrList>(
        markerList, markerIndexUsedCount, out_usedMarkerList,
        out_unusedMarkerList);
    _splitIntoUsedAndUnusedLists<AttrPtr, AttrPtrList>(
        attrList, attrIndexUsedCount, out_usedAttrList, out_unusedAttrList);
    return status;
}

PrintStatOptions constructPrintStats(const MStringArray &printStatsList) {
    auto printStats = PrintStatOptions{
        false,  // enable
        false,  // input;
        false,  // affects;
        false,  // usedSolveObjects;
        false   // deviation;
    };
    if (printStatsList.length() == 0) {
        return printStats;
    }
    for (uint32_t i = 0; i < printStatsList.length(); ++i) {
        if (printStatsList[i] == PRINT_STATS_MODE_INPUTS) {
            printStats.enable = true;
            printStats.input = true;
        } else if (printStatsList[i] == PRINT_STATS_MODE_AFFECTS) {
            printStats.enable = true;
            printStats.affects = true;
        } else if (printStatsList[i] == PRINT_STATS_MODE_USED_SOLVE_OBJECTS) {
            printStats.enable = true;
            printStats.usedSolveObjects = true;
        } else if (printStatsList[i] == PRINT_STATS_MODE_DEVIATION) {
            printStats.enable = true;
            printStats.deviation = true;
        }
    }
    return printStats;
}

MStatus solveFrames(
    CameraPtrList &cameraList, BundlePtrList &bundleList,
    const MTimeArray &frameList, MarkerPtrList &usedMarkerList,
    MarkerPtrList &unusedMarkerList, AttrPtrList &usedAttrList,
    AttrPtrList &unusedAttrList, StiffAttrsPtrList &stiffAttrsList,
    SmoothAttrsPtrList &smoothAttrsList, const BoolList2D &markerToAttrList,
    SolverOptions &solverOptions,
    //
    const PrintStatOptions printStats,
    const MGlobal::MMayaState mayaSessionState,
    //
    MDGModifier &out_dgmod, MAnimCurveChange &out_curveChange,
    //
    MComputation &out_computation, const bool verbose,
    //
    IndexPairList &out_paramToAttrList, IndexPairList &out_errorToMarkerList,
    std::vector<MPoint> &out_markerPosList,
    std::vector<double> &out_markerWeightList,
    std::vector<double> &out_errorList, std::vector<double> &out_paramList,
    std::vector<double> &out_previousParamList,
    std::vector<double> &out_jacobianList,
    //
    MStringArray &outResult, SolverResult &out_solveResult) {
    MStatus status = MS::kSuccess;
    std::string resultStr;

    out_paramToAttrList.clear();
    out_errorToMarkerList.clear();
    out_markerPosList.clear();
    out_markerWeightList.clear();
    out_errorList.clear();
    out_paramList.clear();
    out_previousParamList.clear();
    out_jacobianList.clear();

    int numberOfErrors = 0;
    int numberOfMarkerErrors = 0;
    int numberOfAttrStiffnessErrors = 0;
    int numberOfAttrSmoothnessErrors = 0;
    auto validMarkerList = MarkerPtrList();
    numberOfErrors = countUpNumberOfErrors(
        usedMarkerList, stiffAttrsList, smoothAttrsList, frameList,

        // Outputs
        validMarkerList, out_markerPosList, out_markerWeightList,
        out_errorToMarkerList, numberOfMarkerErrors,
        numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors, status);
    CHECK_MSTATUS(status);
    assert(numberOfErrors ==
           (numberOfMarkerErrors + numberOfAttrStiffnessErrors +
            numberOfAttrSmoothnessErrors));

    int numberOfParameters = 0;
    auto camStaticAttrList = AttrPtrList();
    auto camAnimAttrList = AttrPtrList();
    auto staticAttrList = AttrPtrList();
    auto animAttrList = AttrPtrList();
    auto paramLowerBoundList = std::vector<double>();
    auto paramUpperBoundList = std::vector<double>();
    auto paramWeightList = std::vector<double>();
    auto paramFrameList = BoolList2D();
    numberOfParameters = countUpNumberOfUnknownParameters(
        usedAttrList, frameList,

        // Outputs
        camStaticAttrList, camAnimAttrList, staticAttrList, animAttrList,
        paramLowerBoundList, paramUpperBoundList, paramWeightList,
        out_paramToAttrList, paramFrameList, status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    assert(paramLowerBoundList.size() ==
           static_cast<size_t>(numberOfParameters));
    assert(paramUpperBoundList.size() ==
           static_cast<size_t>(numberOfParameters));
    assert(paramWeightList.size() == static_cast<size_t>(numberOfParameters));
    assert(static_cast<size_t>(numberOfParameters) >= usedAttrList.size());

    // Expand the 'Marker to Attribute' relationship into errors and
    // parameter relationships.
    auto errorToParamList = BoolList2D();
    findErrorToParameterRelationship(usedMarkerList, usedAttrList, frameList,

                                     numberOfParameters, numberOfMarkerErrors,
                                     out_paramToAttrList, out_errorToMarkerList,
                                     markerToAttrList,

                                     // Outputs
                                     errorToParamList, status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (printStats.input == true) {
        assert(printStats.enable == true);
        status = logResultsObjectCounts(
            numberOfParameters, numberOfErrors, numberOfMarkerErrors,
            numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
            outResult);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (printStats.usedSolveObjects == true) {
        assert(printStats.enable == true);
        status =
            logResultsSolveObjectUsage(usedMarkerList, unusedMarkerList,
                                       usedAttrList, unusedAttrList, outResult);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (printStats.affects == true) {
        assert(printStats.enable == true);
        status = logResultsMarkerAffectsAttribute(usedMarkerList, usedAttrList,
                                                  markerToAttrList, outResult);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (verbose) {
        MMSOLVER_VRB("Number of Markers; used=" << usedMarkerList.size()
                                                << " | unused="
                                                << unusedMarkerList.size());
        MMSOLVER_VRB("Number of Attributes; used=" << usedAttrList.size()
                                                   << " | unused="
                                                   << unusedAttrList.size());
        MMSOLVER_VRB("Number of Parameters; " << numberOfParameters);
        MMSOLVER_VRB("Number of Frames; " << frameList.length());
        MMSOLVER_VRB("Number of Marker Errors; " << numberOfMarkerErrors);
        MMSOLVER_VRB("Number of Attribute Stiffness Errors; "
                     << numberOfAttrStiffnessErrors);
        MMSOLVER_VRB("Number of Attribute Smoothness Errors; "
                     << numberOfAttrSmoothnessErrors);
        MMSOLVER_VRB("Number of Total Errors; " << numberOfErrors);
    }

    // Bail out of solve if we don't have enough used markers or
    // attributes.
    if ((usedMarkerList.size() == 0) || (usedAttrList.size() == 0)) {
        if (printStats.enable == true) {
            // If the user is asking to print statistics, then we have
            // successfully achieved that goal and we cannot continue
            // to generate statistics, because not enought markers or
            // attributes were used.
            status = MS::kSuccess;
            return status;
        }
        MMSOLVER_ERR(
            "Solver failure; not enough markers or attributes are not used by "
            "solver "
            << "used markers=" << usedMarkerList.size() << " "
            << "used attributes=" << usedAttrList.size());
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        status = MS::kFailure;
        return status;
    }

    if (numberOfParameters > numberOfErrors) {
        if (printStats.enable == true) {
            // If the user is asking to print statistics, then we have
            // successfully achieved that goal and we cannot continue
            // to generate statistics, because of an invalid number of
            // parameters/errors.
            status = MS::kSuccess;
            return status;
        }
        MMSOLVER_ERR(
            "Solver failure; cannot solve for more attributes (\"parameters\") "
            << "than number of markers (\"errors\"). "
            << "parameters=" << numberOfParameters << " "
            << "errors=" << numberOfErrors);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        status = MS::kFailure;
        return status;
    }
    assert(numberOfErrors > 0);
    assert(numberOfParameters > 0);

    out_paramList.resize((uint64_t)numberOfParameters, 0);
    out_previousParamList.resize((uint64_t)numberOfParameters, 0);
    out_errorList.resize((uint64_t)numberOfErrors, 0);
    out_jacobianList.resize((uint64_t)numberOfParameters * numberOfErrors, 0);

    auto errorDistanceList = std::vector<double>();
    errorDistanceList.resize((uint64_t)numberOfMarkerErrors / ERRORS_PER_MARKER,
                             0);
    assert(out_errorToMarkerList.size() == errorDistanceList.size());

    if (verbose) {
        MMSOLVER_VRB("Solving...");
        MMSOLVER_VRB("Solver Type=" << solverOptions.solverType);
        MMSOLVER_VRB("Maximum Iterations=" << solverOptions.iterMax);
        MMSOLVER_VRB("Tau=" << solverOptions.tau);
        MMSOLVER_VRB("Epsilon1=" << solverOptions.eps1);
        MMSOLVER_VRB("Epsilon2=" << solverOptions.eps2);
        MMSOLVER_VRB("Epsilon3=" << solverOptions.eps3);
        MMSOLVER_VRB("Delta=" << fabs(solverOptions.delta));
        MMSOLVER_VRB("Auto Differencing Type=" << solverOptions.autoDiffType);
        MMSOLVER_VRB("Time Evaluation Mode=" << solverOptions.timeEvalMode);
    }

    if ((verbose == false) && (printStats.enable == false)) {
        std::stringstream ss;
        ss << "Solving... frames:";
        for (uint32_t i = 0; i < frameList.length(); i++) {
            MTime frame(frameList[i]);
            ss << " " << frame;
        }
        std::string tmp_string = ss.str();

        size_t num = 100 - tmp_string.size();
        num = std::min<size_t>(0, num);
        std::string pad_chars(num, '=');

        MMSOLVER_INFO(tmp_string << " " << pad_chars);
    }

    // MComputation helper.
    bool showProgressBar = true;
    bool isInterruptable = true;
    bool useWaitCursor = true;
    if (printStats.enable == false) {
        out_computation.setProgressRange(0, solverOptions.iterMax);
        out_computation.beginComputation(showProgressBar, isInterruptable,
                                         useWaitCursor);
    }

    // Start Solving
    SolverTimer timer;
    if (printStats.enable == false) {
        timer.solveBenchTimer.start();
        timer.solveBenchTicks.start();
    }

    auto mmsgFrameList = std::vector<mmsg::FrameValue>();
    auto mmsgSceneGraph = mmsg::SceneGraph();
    auto mmsgAttrDataBlock = mmsg::AttrDataBlock();
    auto mmsgFlatScene = mmsg::FlatScene();
    auto mmsgCameraNodes = std::vector<mmsg::CameraNode>();
    auto mmsgBundleNodes = std::vector<mmsg::BundleNode>();
    auto mmsgMarkerNodes = std::vector<mmsg::MarkerNode>();
    auto mmsgAttrIdList = std::vector<mmsg::AttrId>();
    if (solverOptions.sceneGraphMode == SceneGraphMode::kMMSceneGraph) {
        status = construct_scene_graph(
            cameraList, usedMarkerList, bundleList, usedAttrList, frameList,
            solverOptions.timeEvalMode, mmsgSceneGraph, mmsgAttrDataBlock,
            mmsgFlatScene, mmsgFrameList, mmsgCameraNodes, mmsgBundleNodes,
            mmsgMarkerNodes, mmsgAttrIdList);
        if (status != MS::kSuccess) {
            // Please use the 'mmSolverSceneGraph' command to test construct
            // a scene graph successfully before attempting to use it.
            //
            // If an error constructing the scene is detected,
            // it would be ideal to fall back to the Maya DAG scene
            // graph, and continue without exiting with failure.
            //
            // Unfortunately because mmSolver requires special
            // evaluation to happen when solving with Maya DAG
            // per-frame, it's not possible to easily fall back. See
            // the use of the 'FrameSolveMode' enum type for more
            // details.
            CHECK_MSTATUS(status);
            MMSOLVER_ERR("Maya DAG is invalid for use with MM Scene Graph, "
                         << "please switch to Maya DAG and solve again.");
            return status;
        }
    } else if (solverOptions.sceneGraphMode == SceneGraphMode::kMayaDag) {
    } else {
        MMSOLVER_ERR("Invalid Scene Graph mode!");
        status = MS::kFailure;
        return status;
    }

#if MMSOLVER_LENS_DISTORTION == 1
    std::vector<std::shared_ptr<LensModel>> markerFrameToLensModelList;
    std::vector<std::shared_ptr<LensModel>> attrFrameToLensModelList;
    std::vector<std::shared_ptr<LensModel>> lensModelList;

    status = constructLensModelList(cameraList, usedMarkerList, usedAttrList,
                                    frameList, markerFrameToLensModelList,
                                    attrFrameToLensModelList, lensModelList);
    CHECK_MSTATUS_AND_RETURN_IT(status);
#endif

    // Solving Objects.
    //
    // This data structure is passed to the solve function, so we can
    // access all this data inside the CMinpack solver function.
    SolverData userData;
    userData.cameraList = cameraList;
    userData.markerList = usedMarkerList;
    userData.bundleList = bundleList;
    userData.attrList = usedAttrList;
    userData.frameList = frameList;
    userData.smoothAttrsList = smoothAttrsList;
    userData.stiffAttrsList = stiffAttrsList;

#if MMSOLVER_LENS_DISTORTION == 1
    userData.markerFrameToLensModelList = markerFrameToLensModelList;
    userData.attrFrameToLensModelList = attrFrameToLensModelList;
    userData.lensModelList = lensModelList;
#endif

    userData.mmsgSceneGraph = std::move(mmsgSceneGraph);
    userData.mmsgAttrDataBlock = std::move(mmsgAttrDataBlock);
    userData.mmsgFrameList = std::move(mmsgFrameList);
    userData.mmsgFlatScene = std::move(mmsgFlatScene);
    userData.mmsgCameraNodes = std::move(mmsgCameraNodes);
    userData.mmsgBundleNodes = std::move(mmsgBundleNodes);
    userData.mmsgMarkerNodes = std::move(mmsgMarkerNodes);
    userData.mmsgAttrIdList = std::move(mmsgAttrIdList);

    userData.paramToAttrList = out_paramToAttrList;
    userData.errorToMarkerList = out_errorToMarkerList;
    userData.markerPosList = out_markerPosList;
    userData.markerWeightList = out_markerWeightList;
    userData.paramFrameList = paramFrameList;
    userData.errorToParamList = errorToParamList;

    userData.paramList = out_paramList;
    userData.previousParamList = out_previousParamList;
    userData.errorList = out_errorList;
    userData.errorDistanceList = errorDistanceList;
    userData.jacobianList = out_jacobianList;
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

    userData.dgmod = &out_dgmod;
    userData.curveChange = &out_curveChange;

    // Allow user to exit out of solve.
    userData.computation = &out_computation;
    userData.userInterrupted = false;

    // Maya is running as an interactive or batch?
    userData.mayaSessionState = mayaSessionState;

    // Verbosity
    userData.verbose = verbose;

    // Calculate initial errors.
    double initialErrorAvg = 0;
    double initialErrorMin = 0;
    double initialErrorMax = 0;
    if (solverOptions.acceptOnlyBetter || printStats.deviation) {
        std::vector<bool> frameIndexEnable(frameList.length(), 1);
        std::vector<bool> skipErrorMeasurements(numberOfErrors, 1);
        measureErrors(numberOfErrors, numberOfMarkerErrors,
                      numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                      frameIndexEnable, skipErrorMeasurements,
                      &out_errorList[0], &userData, initialErrorAvg,
                      initialErrorMax, initialErrorMin, status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        initialErrorAvg = 0;
        initialErrorMin = 0;
        initialErrorMax = 0;
        compute_error_stats(numberOfMarkerErrors, userData.errorDistanceList,
                            initialErrorAvg, initialErrorMin, initialErrorMax);
    }

    if (printStats.deviation == true) {
        out_solveResult.success = true;
        out_solveResult.reason_number = 0;
        out_solveResult.reason = "";
        out_solveResult.iterations = 0;
        out_solveResult.functionEvals = 0;
        out_solveResult.jacobianEvals = 0;
        out_solveResult.errorFinal = 0.0;
        out_solveResult.errorAvg = initialErrorAvg;
        out_solveResult.errorMin = initialErrorMin;
        out_solveResult.errorMax = initialErrorMax;

        logResultsSolveDetails(
            out_solveResult, userData, timer, numberOfParameters,
            numberOfMarkerErrors, numberOfAttrStiffnessErrors,
            numberOfAttrSmoothnessErrors, verbose, out_paramList, outResult);
    }
    if (printStats.enable == true) {
        // There is no more printing to do, we must solve now if we
        // want to solve.
        status = MS::kSuccess;
        return status;
    }

    // Set Initial parameters
    MMSOLVER_VRB("Get Initial parameters...");
    get_initial_parameters(numberOfParameters, out_paramList,
                           out_paramToAttrList, usedAttrList, frameList,
                           outResult);

    MMSOLVER_VRB("Initial Parameters: ");
    for (int i = 0; i < numberOfParameters; ++i) {
        // Copy parameter values into the 'previous' parameter list.
        out_previousParamList[i] = out_paramList[i];
    }
    if (verbose) {
        for (int i = 0; i < numberOfParameters; ++i) {
            IndexPair attrPair = out_paramToAttrList[i];
            AttrPtr attr = usedAttrList[attrPair.first];

            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            MMSOLVER_VRB("-> " << out_paramList[i] << " | " << attr_name_char);
        }
    }

    if (solverOptions.solverType == SOLVER_TYPE_LEVMAR) {
        MMSOLVER_ERR("Solver Type is not supported by this compiled plug-in. "
                     << "solverType=" << solverOptions.solverType);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        status = MS::kFailure;
        return status;

    } else if (solverOptions.solverType == SOLVER_TYPE_CMINPACK_LMDIF) {
        solve_3d_cminpack_lmdif(solverOptions, numberOfParameters,
                                numberOfErrors, out_paramList, out_errorList,
                                paramWeightList, userData, out_solveResult);

    } else if (solverOptions.solverType == SOLVER_TYPE_CMINPACK_LMDER) {
        solve_3d_cminpack_lmder(solverOptions, numberOfParameters,
                                numberOfErrors, out_paramList, out_errorList,
                                paramWeightList, userData, out_solveResult);

    } else {
        MMSOLVER_ERR(
            "Solver Type is invalid. solverType=" << solverOptions.solverType);
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        status = MS::kFailure;
        return status;
    }

    timer.solveBenchTicks.stop();
    timer.solveBenchTimer.stop();
    out_computation.endComputation();

    // Solve Finished, re-calculate error, and only set parameters if
    // the average error is lower.
    bool errorIsBetter = true;
    double errorAvg = 0;
    double errorMin = 0;
    double errorMax = 0;
    compute_error_stats(numberOfMarkerErrors, userData.errorDistanceList,
                        errorAvg, errorMin, errorMax);
    out_solveResult.errorAvg = errorAvg;
    out_solveResult.errorMin = errorMin;
    out_solveResult.errorMax = errorMax;
    if (solverOptions.acceptOnlyBetter) {
        errorIsBetter = errorAvg <= initialErrorAvg;
    }

    // Set the solved parameters
    if (errorIsBetter) {
        MMSOLVER_VRB("Setting Solved Parameters...");
        set_maya_attribute_values(numberOfParameters, out_paramToAttrList,
                                  usedAttrList, out_paramList, frameList,
                                  out_dgmod, out_curveChange);
    } else {
        // Set the initial parameter values.
        MMSOLVER_VRB("Setting Initial Parameters...");
        set_maya_attribute_values(numberOfParameters, out_paramToAttrList,
                                  usedAttrList, out_previousParamList,
                                  frameList, out_dgmod, out_curveChange);
    }
    if (verbose) {
        MMSOLVER_VRB("Solved Parameters:");
        for (int i = 0; i < numberOfParameters; ++i) {
            IndexPair attrPair = out_paramToAttrList[i];
            AttrPtr attr = usedAttrList[attrPair.first];

            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            const double offset = attr->getOffsetValue();
            const double scale = attr->getScaleValue();
            const double xmin = attr->getMinimumValue();
            const double xmax = attr->getMaximumValue();

            const double solver_value = out_paramList[i];
            const double real_value = parameterBoundFromInternalToExternal(
                solver_value, xmin, xmax, offset, scale);

            MMSOLVER_VRB("-> " << real_value << " | " << attr_name_char);
        }
    }

    logResultsSolveDetails(out_solveResult, userData, timer, numberOfParameters,
                           numberOfMarkerErrors, numberOfAttrStiffnessErrors,
                           numberOfAttrSmoothnessErrors, verbose, out_paramList,
                           outResult);

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
bool solve(SolverOptions &solverOptions, CameraPtrList &cameraList,
           MarkerPtrList &markerList, BundlePtrList &bundleList,
           AttrPtrList &attrList, const MTimeArray &frameList,
           StiffAttrsPtrList &stiffAttrsList,
           SmoothAttrsPtrList &smoothAttrsList, MDGModifier &dgmod,
           MAnimCurveChange &curveChange, MComputation &computation,
           MStringArray &printStatsList, bool with_verbosity,
           MStringArray &outResult) {
    MStatus status = MS::kSuccess;

    bool verbose = with_verbosity;
    auto printStats = constructPrintStats(printStatsList);
    if (printStats.enable == true) {
        // When printing statistics, turn off verbosity.
        verbose = false;
    }

#ifdef MAYA_PROFILE
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope profilingScope(profileCategory, MProfiler::kColorC_L3,
                                   "solve");
#endif

    // Split the used and unused markers and attributes.
    MarkerPtrList usedMarkerList;
    MarkerPtrList unusedMarkerList;
    AttrPtrList usedAttrList;
    AttrPtrList unusedAttrList;

    auto markerToAttrList = BoolList2D();
    if (!solverOptions.removeUnusedMarkers &&
        !solverOptions.removeUnusedAttributes) {
        // All 'object relationships' will be ignored.

        // All Markers and Attributes are assumed to be used.
        usedMarkerList = markerList;
        usedAttrList = attrList;

        // Initialise 'markerToAttrList' to assume all markers affect
        // all attributes. This is the default assumption.
        markerToAttrList.resize(markerList.size());
        auto defaultValue = true;
        for (size_t i = 0; i < markerList.size(); ++i) {
            markerToAttrList[i].resize(attrList.size(), defaultValue);
        }
    } else {
        // Query the relationship by pre-computed attributes on the
        // Markers. If the attributes do not exist, we assume all markers
        // affect all attributes (and therefore suffer a performance
        // problem).
        getMarkerToAttributeRelationship(markerList, attrList, markerToAttrList,
                                         status);
        CHECK_MSTATUS(status);

        splitUsedMarkersAndAttributes(markerList, attrList, markerToAttrList,
                                      usedMarkerList, unusedMarkerList,
                                      usedAttrList, unusedAttrList);

        // Print warnings about unused solve objects.
        if ((unusedMarkerList.size() > 0) &&
            (solverOptions.removeUnusedMarkers)) {
            MMSOLVER_WRN("Unused Markers detected and ignored:");
            for (MarkerPtrListCIt mit = unusedMarkerList.cbegin();
                 mit != unusedMarkerList.cend(); ++mit) {
                MarkerPtr marker = *mit;
                const char *markerName = marker->getLongNodeName().asChar();
                MMSOLVER_WRN("-> " << markerName);
            }
        }

        if ((unusedAttrList.size() > 0) &&
            (solverOptions.removeUnusedAttributes)) {
            MMSOLVER_WRN("Unused Attributes detected and ignored:");
            for (AttrPtrListCIt ait = unusedAttrList.cbegin();
                 ait != unusedAttrList.cend(); ++ait) {
                AttrPtr attr = *ait;
                const char *attrName = attr->getLongName().asChar();
                MMSOLVER_WRN("-> " << attrName);
            }
        }

        // Change the list of Markers and Attributes to filter out unused
        // objects.
        bool usedObjectsChanged = false;
        if (solverOptions.removeUnusedMarkers) {
            usedObjectsChanged = true;
        } else {
            usedMarkerList = markerList;
        }

        if (solverOptions.removeUnusedAttributes) {
            usedObjectsChanged = true;
        } else {
            usedAttrList = attrList;
        }

        if (usedObjectsChanged == true) {
            getMarkerToAttributeRelationship(usedMarkerList, usedAttrList,
                                             markerToAttrList, status);
            CHECK_MSTATUS(status);
        }
    }

    // Allocate shared memory.
    auto paramToAttrList = IndexPairList();
    auto errorToMarkerList = IndexPairList();
    auto markerPosList = std::vector<MPoint>();
    auto markerWeightList = std::vector<double>();
    auto errorList = std::vector<double>();
    auto paramList = std::vector<double>();
    auto previousParamList = std::vector<double>();
    auto jacobianList = std::vector<double>();

    MGlobal::MMayaState mayaSessionState = MGlobal::mayaState(&status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    SolverResult solveResult;
    auto frameSolveMode = solverOptions.frameSolveMode;
    // MMSOLVER_INFO("frameSolveMode: " <<
    // static_cast<uint32_t>(frameSolveMode));
    if (frameSolveMode == FrameSolveMode::kAllFrameAtOnce) {
        status = solveFrames(
            cameraList, bundleList, frameList, usedMarkerList, unusedMarkerList,
            usedAttrList, unusedAttrList, stiffAttrsList, smoothAttrsList,
            markerToAttrList, solverOptions,
            //
            printStats, mayaSessionState,
            //
            dgmod, curveChange,
            //
            computation, verbose,
            //
            paramToAttrList, errorToMarkerList, markerPosList, markerWeightList,
            errorList, paramList, previousParamList, jacobianList,
            //
            outResult, solveResult);
    } else if (frameSolveMode == FrameSolveMode::kPerFrame) {
        for (uint32_t f = 0; f < frameList.length(); ++f) {
            auto frames = MTimeArray(1, frameList[f]);
            status = solveFrames(cameraList, bundleList, frames, usedMarkerList,
                                 unusedMarkerList, usedAttrList, unusedAttrList,
                                 stiffAttrsList, smoothAttrsList,
                                 markerToAttrList, solverOptions,
                                 //
                                 printStats, mayaSessionState,
                                 //
                                 dgmod, curveChange,
                                 //
                                 computation, verbose,
                                 //
                                 paramToAttrList, errorToMarkerList,
                                 markerPosList, markerWeightList, errorList,
                                 paramList, previousParamList, jacobianList,
                                 //
                                 outResult, solveResult);
            // TODO: Combine solveResult from each iteration.
            if (status != MS::kSuccess) {
                break;
            }
        }
    }

    return solveResult.success;
};
