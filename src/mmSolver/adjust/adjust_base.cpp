/*
 * Copyright (C) 2018, 2019, 2022, 2025 David Cattermole.
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
#include <cmath>
#include <cstdlib>
#include <limits>
#include <map>
#include <sstream>
#include <string>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MFloatMatrix.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnCamera.h>
#include <maya/MGlobal.h>
#include <maya/MItDependencyGraph.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

#ifdef MAYA_PROFILE
#include <maya/MProfiler.h>
#endif

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "adjust_ceres_lmder.h"
#include "adjust_ceres_lmdif.h"
#include "adjust_cminpack_lmder.h"
#include "adjust_cminpack_lmdif.h"
#include "adjust_consoleLogging.h"
#include "adjust_measureErrors.h"
#include "adjust_relationships.h"
#include "adjust_results.h"
#include "adjust_solveFunc.h"
#include "mmSolver/core/frame_list.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_attr_list.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_frame_utils.h"
#include "mmSolver/mayahelper/maya_lens_model_utils.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_marker_list.h"
#include "mmSolver/mayahelper/maya_scene_graph.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"
#include "mmscenegraph/mmscenegraph.h"

namespace mmsg = mmscenegraph;

namespace mmsolver {
// Get a list of all available solver types (index and name).
//
// This list may change in different plug-ins, as the compiled
// dependencies may differ.
std::vector<SolverTypePair> getSolverTypes() {
    std::vector<std::pair<int, std::string>> solverTypes;
    std::pair<int, std::string> solverType;

    solverType.first = SOLVER_TYPE_CMINPACK_LMDIF;
    solverType.second = SOLVER_TYPE_CMINPACK_LMDIF_NAME;
    solverTypes.push_back(solverType);

    solverType.first = SOLVER_TYPE_CMINPACK_LMDER;
    solverType.second = SOLVER_TYPE_CMINPACK_LMDER_NAME;
    solverTypes.push_back(solverType);

    solverType.first = SOLVER_TYPE_CERES_LMDIF;
    solverType.second = SOLVER_TYPE_CERES_LMDIF_NAME;
    solverTypes.push_back(solverType);

    solverType.first = SOLVER_TYPE_CERES_LMDER;
    solverType.second = SOLVER_TYPE_CERES_LMDER_NAME;
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
            std::string name = cit->second;

            if (defaultSolver == name) {
                solverTypeIndex = cit->first;
                solverTypeName = name;
            }
        }
        if (solverTypeName.empty()) {
            MMSOLVER_MAYA_ERR(
                "MMSOLVER_DEFAULT_SOLVER environment variable is invalid. "
                << "Value may be "
                << "\"" << SOLVER_TYPE_CMINPACK_LMDIF_NAME << "\", "
                << "\"" << SOLVER_TYPE_CMINPACK_LMDER_NAME << "\", "
                << "\"" << SOLVER_TYPE_CERES_LMDIF_NAME << "\", "
                << "or \"" << SOLVER_TYPE_CERES_LMDER_NAME << "\"; "
                << "; value=" << defaultSolver);
        }
    }
    SolverTypePair solverType(solverTypeIndex, solverTypeName);
    return solverType;
}

void lossFunctionTrivial(const double z, double &rho0, double &rho1,
                         double &rho2) {
    // Trivial - 'no op' loss function.
    rho0 = z;
    rho1 = 1.0;
    rho2 = 0.0;
}

void lossFunctionSoftL1(const double z, double &rho0, double &rho1,
                        double &rho2) {
    // Soft L1
    double t = 1.0 + z;
    rho0 = 2.0 * (std::pow(t, 0.5 - 1.0));
    rho1 = std::pow(t, -0.5);
    rho2 = -0.5 * std::pow(t, -1.5);
}

void lossFunctionCauchy(const double z, double &rho0, double &rho1,
                        double &rho2) {
    // Cauchy
    rho0 = std::log1p(z);
    double t = 1.0 + z;
    rho1 = 1.0 / t;
    rho2 = -1.0 / std::pow(t, 2.0);
}

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
            MMSOLVER_MAYA_DBG(
                "Invalid Robust Loss Type given; value=" << loss_type);
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
    const AttrList &attrList, const FrameList &frameList,
    const bool solverSupportsParameterBounds, SolverResult &out_solverResult) {
    const bool verbose = false;

    MMSOLVER_MAYA_VRB(
        "get_initial_parameters numberOfParameters=" << numberOfParameters);
    MMSOLVER_MAYA_VRB("get_initial_parameters solverSupportsParameterBounds="
                      << solverSupportsParameterBounds);

    MStatus status = MS::kSuccess;

    const auto ui_unit = MTime::uiUnit();
    const int timeEvalMode = TIME_EVAL_MODE_DG_CONTEXT;
    MTime currentFrame = MAnimControl::currentTime();
    for (int i = 0; i < numberOfParameters; ++i) {
        const IndexPair attrPair = paramToAttrList[i];
        AttrIndex attrIndex = attrPair.first;
        AttrPtr attr = attrList.get_attr(attrIndex);

        // Get frame time
        MTime frame = currentFrame;
        if (attrPair.second != -1) {
            const FrameNumber frameNumber =
                frameList.get_frame(attrPair.second);
            frame = convert_to_time(frameNumber, ui_unit);
        }

        double value = 0.0;
        status = attr->getValue(value, frame, timeEvalMode);
        CHECK_MSTATUS(status);
        if (status != MS::kSuccess) {
            out_solverResult.success = false;
            return false;
        }

        if (solverSupportsParameterBounds) {
            const double xoffset = attr->getOffsetValue();
            const double xscale = attr->getScaleValue();
            const double xmin = attr->getMinimumValue();
            const double xmax = attr->getMaximumValue();

            value = parameterBoundFromExternalToInternal(value, xmin, xmax,
                                                         xoffset, xscale);
        }

        paramList[i] = value;
    }
    return true;
}

bool set_maya_attribute_values(
    const int numberOfParameters,
    const std::vector<std::pair<int, int>> &paramToAttrList,
    const AttrList &attrList, const std::vector<double> &paramList,
    const FrameList &frameList, MDGModifier &dgmod,
    MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;

    const auto ui_unit = MTime::uiUnit();
    MTime currentFrame = MAnimControl::currentTime();
    for (int i = 0; i < numberOfParameters; ++i) {
        IndexPair attrPair = paramToAttrList[i];
        AttrIndex attrIndex = attrPair.first;
        AttrPtr attr = attrList.get_attr(attrIndex);

        const double offset = attr->getOffsetValue();
        const double scale = attr->getScaleValue();
        const double xmin = attr->getMinimumValue();
        const double xmax = attr->getMaximumValue();
        const double solver_value = paramList[i];
        const double real_value = parameterBoundFromInternalToExternal(
            solver_value, xmin, xmax, offset, scale);

        // Get frame time
        MTime frame = currentFrame;
        FrameNumber frameNumber =
            convert_to_frame_number(currentFrame, ui_unit);
        if (attrPair.second != -1) {
            frameNumber = frameList.get_frame(attrPair.second);
            frame = convert_to_time(frameNumber);
        }

        status = attr->setValue(real_value, frame, dgmod, curveChange);
        CHECK_MSTATUS(status);

        if (status != MS::kSuccess) {
            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            MMSOLVER_MAYA_ERR(
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
    const auto marker_error_count = numberOfMarkerErrors / ERRORS_PER_MARKER;
    for (int i = 0; i < marker_error_count; ++i) {
        const double err = errorDistanceList[i];
        if (!std::isfinite(err)) {
            MMSOLVER_MAYA_ERR(
                "Error distance value is invalid, skipping: " << err);
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
    MMSOLVER_ASSERT(numberOfMarkerErrors > 0,
                    "If we have zero, something bad has happened somewhere. We "
                    "cannot divide by zero.");
    out_errorAvg /= marker_error_count;
    return true;
}

void logResultsTimer(const SolverTimer &timer, TimerResult &outTimerResult) {
    outTimerResult.fill(timer);
}

void logResultsSolveValues(const int numberOfParameters,
                           const int numberOfErrors,
                           const std::vector<double> &paramList,
                           const std::vector<double> &errorList,
                           SolveValuesResult &outSolveValuesResult) {
    outSolveValuesResult.fill(numberOfParameters, numberOfErrors, paramList,
                              errorList);
}

void logResultsErrorMetrics(const int numberOfMarkerErrors,
                            const MarkerList &markerList,
                            const FrameList &frameList,
                            const std::vector<IndexPair> &errorToMarkerList,
                            const std::vector<double> &errorDistanceList,
                            ErrorMetricsResult &outErrorMetricsResult) {
    outErrorMetricsResult.fill(numberOfMarkerErrors, markerList, frameList,
                               errorToMarkerList, errorDistanceList);
}

void printSolveDetails(const SolverResult &solverResult, SolverData &userData,
                       SolverTimer &timer, const int numberOfParameters,
                       const int numberOfMarkerErrors,
                       const int numberOfAttrStiffnessErrors,
                       const int numberOfAttrSmoothnessErrors,
                       const LogLevel &logLevel,
                       const std::vector<double> &paramList) {
    const bool verbose = logLevel >= LOG_LEVEL_PRINT_VERBOSE;

    MMSOLVER_MAYA_VRB("Results:");
    if (solverResult.success) {
        MMSOLVER_MAYA_VRB("Solver returned SUCCESS in "
                          << solverResult.iterations << " iterations");
    } else {
        MMSOLVER_MAYA_VRB("Solver returned FAILURE in "
                          << solverResult.iterations << " iterations");
    }

    MMSOLVER_MAYA_VRB("Reason: " << solverResult.reason);
    MMSOLVER_MAYA_VRB("Reason number: " << solverResult.reason_number);

    MMSOLVER_MAYA_VRB(std::endl << "Solve Information:");
    MMSOLVER_MAYA_VRB("Maximum Error: " << solverResult.errorMax);
    MMSOLVER_MAYA_VRB("Average Error: " << solverResult.errorAvg);
    MMSOLVER_MAYA_VRB("Minimum Error: " << solverResult.errorMin);

    MMSOLVER_MAYA_VRB("Iterations: " << solverResult.iterations);
    MMSOLVER_MAYA_VRB("Function Evaluations: " << solverResult.functionEvals);
    MMSOLVER_MAYA_VRB("Jacobian Evaluations: " << solverResult.jacobianEvals);

    if (logLevel >= LOG_LEVEL_PRINT_SOLVER_RESULTS) {
        console_log_solver_results(solverResult, timer);
    }

    if (logLevel >= LOG_LEVEL_PRINT_SOLVER_TIMING) {
        const uint32_t total_num = userData.iterNum + userData.jacIterNum;
        MMSOLVER_ASSERT(total_num > 0, "There must have been some iterations.");
        console_log_solver_timer(timer, total_num);
    }
}

MStatus logResultsObjectCounts(const int numberOfParameters,
                               const int numberOfErrors,
                               const int numberOfMarkerErrors,
                               const int numberOfAttrStiffnessErrors,
                               const int numberOfAttrSmoothnessErrors,
                               SolverObjectCountResult &out_result) {
    const bool verbose = false;
    MStatus status = MStatus::kSuccess;

    MMSOLVER_MAYA_VRB(
        "logResultsObjectCounts numberOfParameters=" << numberOfParameters);
    MMSOLVER_MAYA_VRB(
        "logResultsObjectCounts numberOfErrors=" << numberOfErrors);
    MMSOLVER_MAYA_VRB(
        "logResultsObjectCounts numberOfMarkerErrors=" << numberOfMarkerErrors);
    MMSOLVER_MAYA_VRB("logResultsObjectCounts numberOfAttrStiffnessErrors="
                      << numberOfAttrStiffnessErrors);
    MMSOLVER_MAYA_VRB("logResultsObjectCounts numberOfAttrSmoothnessErrors="
                      << numberOfAttrSmoothnessErrors);

    out_result.fill(numberOfParameters, numberOfErrors, numberOfMarkerErrors,
                    numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors);
    return status;
}

/*
 * Print out the marker-to-attribute 'affects' relationship.
 *
 * The markerList and attrList are expected to have the
 * enabled/disabled state set for each marker/attr that is enabled or
 * disabled.
 */
MStatus logResultsMarkerAffectsAttribute(const MarkerList &markerList,
                                         const AttrList &attrList,
                                         AffectsResult &out_result) {
    out_result.fill(markerList, attrList);
    return MStatus::kSuccess;
}

/*
 * Print out the frame numbers that are valid or invalid in the solve.
 */
MStatus logResultsSolverFrames(const size_t total_frame_count,
                               const FrameList &frameList,
                               SolverFramesResult &out_result) {
    const bool verbose = false;

    std::unordered_set<int32_t> valid_frames;
    std::unordered_set<int32_t> invalid_frames;
    valid_frames.reserve(frameList.count_enabled());
    invalid_frames.reserve(frameList.count_disabled());

    for (FrameIndex frameIndex = 0; frameIndex < frameList.size();
         ++frameIndex) {
        const FrameNumber frameNumber = frameList.get_frame(frameIndex);
        const bool frameEnabled = frameList.get_enabled(frameIndex);
        if (frameEnabled) {
            valid_frames.insert(frameNumber);
        } else {
            invalid_frames.insert(frameNumber);
        }
    }

    MMSOLVER_MAYA_VRB(
        "logResultsSolverFrames "
        "total_frame_count="
        << total_frame_count);

    const std::string valid_frames_str =
        create_string_sorted_set_numbers(valid_frames);
    MMSOLVER_MAYA_VRB(
        "logResultsSolverFrames "
        "valid_frames.size()="
        << valid_frames.size());
    MMSOLVER_MAYA_VRB(
        "logResultsSolverFrames "
        "valid_frames_str=\""
        << valid_frames_str << "\"");

    const std::string invalid_frames_str =
        create_string_sorted_set_numbers(invalid_frames);
    MMSOLVER_MAYA_VRB(
        "logResultsSolverFrames "
        "invalid_frames.size()="
        << invalid_frames.size());
    MMSOLVER_MAYA_VRB(
        "logResultsSolverFrames "
        "invalid_frames_str=\""
        << invalid_frames_str << "\"");

    out_result.fill(total_frame_count, std::move(valid_frames),
                    std::move(invalid_frames));
    return MStatus::kSuccess;
}

/*
 * Print out if objects added to the solve (such as markers and
 * attributes) are being used, or are unused.
 */
MStatus logResultsSolveObjectUsage(const MarkerList &validMarkerList,
                                   const AttrList &validAttrList,
                                   SolverObjectUsageResult &out_result) {
    const bool verbose = false;

    MStatus status = MStatus::kSuccess;

    MMSOLVER_MAYA_VRB(
        "logResultsSolveObjectUsage"
        " validMarkerList.size()="
        << validMarkerList.size());
    MMSOLVER_MAYA_VRB(
        "logResultsSolveObjectUsage"
        " validMarkerList.size()="
        << validMarkerList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "logResultsSolveObjectUsage"
        " validMarkerList.size()="
        << validMarkerList.count_disabled());

    MMSOLVER_MAYA_VRB(
        "logResultsSolveObjectUsage"
        " validAttrList.size()="
        << validAttrList.size());
    MMSOLVER_MAYA_VRB(
        "logResultsSolveObjectUsage"
        " validAttrList.size()="
        << validAttrList.count_enabled());
    MMSOLVER_MAYA_VRB(
        "logResultsSolveObjectUsage"
        " validAttrList.size()="
        << validAttrList.count_disabled());

    out_result.fill(validMarkerList, validAttrList);
    return status;
}

PrintStatOptions constructPrintStats(const MStringArray &printStatsList) {
    auto printStats = PrintStatOptions();
    printStats.doNotSolve = false;
    printStats.input = false;
    printStats.affects = false;
    printStats.usedSolveObjects = false;
    printStats.deviation = false;

    if (printStatsList.length() == 0) {
        return printStats;
    }

    for (uint32_t i = 0; i < printStatsList.length(); ++i) {
        if (printStatsList[i] == PRINT_STATS_MODE_INPUTS) {
            printStats.doNotSolve = true;
            printStats.input = true;
        } else if (printStatsList[i] == PRINT_STATS_MODE_AFFECTS) {
            printStats.doNotSolve = true;
            printStats.affects = true;
        } else if (printStatsList[i] == PRINT_STATS_MODE_USED_SOLVE_OBJECTS) {
            printStats.doNotSolve = true;
            printStats.usedSolveObjects = true;
        } else if (printStatsList[i] == PRINT_STATS_MODE_DEVIATION) {
            printStats.doNotSolve = true;
            printStats.deviation = true;
        }
    }
    return printStats;
}

MStatus validateSolveFrames(
    CameraPtrList &cameraList, BundlePtrList &bundleList,
    const FrameList &frameList, const MarkerList &markerList,
    const AttrList &attrList, const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList,
    const MatrixBool3D &markerToAttrToFrameMatrix,
    const FrameSolveMode frameSolveMode, SolverOptions &solverOptions,
    //
    std::vector<double> &out_jacobianList, IndexPairList &out_paramToAttrList,
    IndexPairList &out_errorToMarkerList,
    std::vector<MPoint> &out_markerPosList,
    std::vector<double> &out_markerWeightList,
    std::vector<double> &out_errorList, std::vector<double> &out_paramList,
    std::vector<double> &out_previousParamList,
    //
    uint32_t &out_numberOfParameters, uint32_t &out_numberOfErrors,
    uint32_t &out_numberOfMarkerErrors,
    uint32_t &out_numberOfAttrStiffnessErrors,
    uint32_t &out_numberOfAttrSmoothnessErrors, FrameCount &out_validFrameCount,
    FrameCount &out_invalidFrameCount,
    //
    FrameList &out_validFrameList, MatrixBool2D &out_errorToParamMatrix,
    MatrixBool2D &out_paramToFrameMatrix,
    std::vector<double> &out_paramWeightList,
    //
    const LogLevel &logLevel, const bool verbose, bool &out_solve_is_valid,
    CommandResult &out_cmdResult) {
    MStatus status = MS::kSuccess;

    MMSOLVER_MAYA_VRB("validateSolveFrames");

    out_solve_is_valid = false;
    out_cmdResult.solverResult.success = true;

    out_paramToAttrList.clear();
    out_errorToMarkerList.clear();
    out_markerPosList.clear();
    out_markerWeightList.clear();
    out_errorList.clear();
    out_paramList.clear();
    out_previousParamList.clear();
    out_jacobianList.clear();

    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: frameList.size()=" << frameList.size());
    MMSOLVER_MAYA_VRB("validateSolveFrames: frameList.count_enabled()="
                      << frameList.count_enabled());
    if (verbose) {
        for (FrameIndex frameIndex = 0; frameIndex < frameList.size();
             frameIndex++) {
            const FrameNumber frameNumber = frameList.get_frame(frameIndex);
            MMSOLVER_MAYA_VRB("validateSolveFrames: frameList["
                              << frameIndex << "]=" << frameNumber);
        }
    }

    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: markerList.size()=" << markerList.size());
    MMSOLVER_MAYA_VRB("validateSolveFrames: markerList.count_enabled()="
                      << markerList.count_enabled());

    out_numberOfMarkerErrors = 0;
    out_numberOfAttrStiffnessErrors = 0;
    out_numberOfAttrSmoothnessErrors = 0;
    out_numberOfErrors = countUpNumberOfErrors(
        markerList, stiffAttrsList, smoothAttrsList, frameList,

        // Outputs
        out_markerPosList, out_markerWeightList, out_errorToMarkerList,
        out_numberOfMarkerErrors, out_numberOfAttrStiffnessErrors,
        out_numberOfAttrSmoothnessErrors, status);
    if ((out_numberOfErrors == 0) || (status != MS::kSuccess)) {
        MMSOLVER_MAYA_VRB(
            "validateSolveFrames: countUpNumberOfErrors "
            "failed; out_numberOfErrors="
            << out_numberOfErrors);
        out_solve_is_valid = false;
        CHECK_MSTATUS(status);
        return status;
    }
    MMSOLVER_ASSERT(out_numberOfErrors == (out_numberOfMarkerErrors +
                                           out_numberOfAttrStiffnessErrors +
                                           out_numberOfAttrSmoothnessErrors),
                    "Our error count calculation must be wrong.");

    auto camStaticAttrList = AttrList();
    auto camAnimAttrList = AttrList();
    auto staticAttrList = AttrList();
    auto animAttrList = AttrList();
    auto paramLowerBoundList = std::vector<double>();
    auto paramUpperBoundList = std::vector<double>();
    out_numberOfParameters = countUpNumberOfUnknownParameters(
        attrList, frameList,

        // Outputs
        camStaticAttrList, camAnimAttrList, staticAttrList, animAttrList,
        paramLowerBoundList, paramUpperBoundList, out_paramWeightList,
        out_paramToAttrList, out_paramToFrameMatrix, status);
    if ((out_numberOfParameters == 0) || (status != MS::kSuccess)) {
        MMSOLVER_MAYA_VRB(
            "validateSolveFrames: countUpNumberOfUnknownParameters failed; "
            "out_numberOfParameters="
            << out_numberOfParameters);
        out_solve_is_valid = false;
        CHECK_MSTATUS(status);
        return status;
    }

    MMSOLVER_ASSERT(
        paramLowerBoundList.size() ==
            static_cast<size_t>(out_numberOfParameters),
        "Each parameter must have a lower bounds entry; "
            << "paramLowerBoundList.size()=" << paramLowerBoundList.size()
            << " static_cast<size_t>(out_numberOfParameters)="
            << static_cast<size_t>(out_numberOfParameters));
    MMSOLVER_ASSERT(
        paramUpperBoundList.size() ==
            static_cast<size_t>(out_numberOfParameters),
        "Each parameter must have a upper bounds entry; "
            << "paramUpperBoundList.size()=" << paramUpperBoundList.size()
            << " static_cast<size_t>(out_numberOfParameters)="
            << static_cast<size_t>(out_numberOfParameters));
    MMSOLVER_ASSERT(
        out_paramWeightList.size() ==
            static_cast<size_t>(out_numberOfParameters),
        "Each parameter must have a weights entry; "
            << "out_paramWeightList.size()=" << out_paramWeightList.size()
            << " static_cast<size_t>(out_numberOfParameters)="
            << static_cast<size_t>(out_numberOfParameters));
    MMSOLVER_ASSERT(
        static_cast<size_t>(out_numberOfParameters) >= attrList.count_enabled(),
        "We cannot have more attributes than parameters; "
            << "static_cast<size_t>(out_numberOfParameters)="
            << static_cast<size_t>(out_numberOfParameters)
            << " attrList.count_enabled()=" << attrList.count_enabled());

    // Expand the 'Marker to Attribute to Frame' relationship into
    // errors and parameter relationships.
    mapErrorsToParameters(markerList, attrList, frameList,

                          out_numberOfParameters, out_numberOfMarkerErrors,
                          out_paramToAttrList, out_errorToMarkerList,
                          markerToAttrToFrameMatrix,

                          // Outputs
                          out_errorToParamMatrix, status);

    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_VRB("validateSolveFrames: mapErrorsToParameters failed.");
        out_solve_is_valid = false;
        CHECK_MSTATUS(status);
        return status;
    }

    if (out_cmdResult.printStats.input) {
        MMSOLVER_ASSERT(
            out_cmdResult.printStats.doNotSolve,
            "We are not expected to solve when only printing stats.");
        status = logResultsObjectCounts(
            out_numberOfParameters, out_numberOfErrors,
            out_numberOfMarkerErrors, out_numberOfAttrStiffnessErrors,
            out_numberOfAttrSmoothnessErrors,
            out_cmdResult.solverObjectCountResult);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_VRB(
                "validateSolveFrames: logResultsObjectCounts failed.");
            out_solve_is_valid = false;
            CHECK_MSTATUS(status);
            return status;
        }
    }

    if (out_cmdResult.printStats.usedSolveObjects) {
        MMSOLVER_ASSERT(
            out_cmdResult.printStats.doNotSolve,
            "We are not expected to solve when only printing stats.");
        status = logResultsSolveObjectUsage(
            markerList, attrList, out_cmdResult.solverObjectUsageResult);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_VRB(
                "validateSolveFrames: logResultsSolveObjectUsage failed.");
            out_solve_is_valid = false;
            CHECK_MSTATUS(status);
            return status;
        }
    }

    if (out_cmdResult.printStats.affects) {
        MMSOLVER_ASSERT(
            out_cmdResult.printStats.doNotSolve,
            "We are not expected to solve when only printing stats.");
        status = logResultsMarkerAffectsAttribute(markerList, attrList,
                                                  out_cmdResult.affectsResult);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_VRB(
                "validateSolveFrames: logResultsMarkerAffectsAttribute "
                "failed.");
            out_solve_is_valid = false;
            CHECK_MSTATUS(status);
            return status;
        }
    }

    MMSOLVER_ASSERT(markerToAttrToFrameMatrix.width() == markerList.size(),
                    "markerToAttrToFrameMatrix.width() must represent the "
                    "markerList.size().");
    MMSOLVER_ASSERT(markerToAttrToFrameMatrix.height() == attrList.size(),
                    "markerToAttrToFrameMatrix.height() must represent the "
                    "attrList.size().");
    MMSOLVER_ASSERT(markerToAttrToFrameMatrix.depth() == frameList.size(),
                    "markerToAttrToFrameMatrix.depth() must represent the "
                    "frameList.size().");

    const FrameCount frameListEnabledCount = frameList.count_enabled();
    const size_t frameCount = frameList.size();
    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: "
        "FrameList count: "
        << frameList.size());
    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: "
        "FrameList enabled count: "
        << frameListEnabledCount);

    calculateMarkerAndParameterCount(
        markerList, attrList, frameList, out_numberOfParameters,
        out_numberOfMarkerErrors, out_paramToAttrList, out_errorToMarkerList,
        markerToAttrToFrameMatrix, frameSolveMode,

        // Outputs
        out_validFrameList, status);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_VRB(
            "validateSolveFrames: calculateMarkerAndParameterCount failed.");
        CHECK_MSTATUS(status);
        out_solve_is_valid = false;
        return status;
    }

    out_validFrameCount = out_validFrameList.count_enabled();
    out_invalidFrameCount = out_validFrameList.count_disabled();

    status = logResultsSolverFrames(frameCount, out_validFrameList,
                                    out_cmdResult.solverFramesResult);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_VRB(
            "validateSolveFrames: logResultsSolverFrames failed.");
        out_solve_is_valid = false;
        CHECK_MSTATUS(status);
        return status;
    }

    if (logLevel >= LOG_LEVEL_PRINT_SOLVER_OBJECT_COUNTS) {
        MMSOLVER_MAYA_INFO("Number of Markers; used="
                           << markerList.count_enabled()
                           << " | unused=" << markerList.count_disabled());
        MMSOLVER_MAYA_INFO("Number of Attributes; used="
                           << attrList.count_enabled()
                           << " | unused=" << attrList.count_disabled());
        MMSOLVER_MAYA_INFO("Number of Parameters; " << out_numberOfParameters);
        MMSOLVER_MAYA_INFO("Number of Frames; " << frameCount);
        MMSOLVER_MAYA_INFO("Number of Valid Frames; " << out_validFrameCount);
        MMSOLVER_MAYA_INFO("Number of Invalid Frames; "
                           << out_invalidFrameCount);
        MMSOLVER_MAYA_INFO("Number of Marker Errors; "
                           << out_numberOfMarkerErrors);
        MMSOLVER_MAYA_INFO("Number of Attribute Stiffness Errors; "
                           << out_numberOfAttrStiffnessErrors);
        MMSOLVER_MAYA_INFO("Number of Attribute Smoothness Errors; "
                           << out_numberOfAttrSmoothnessErrors);
        MMSOLVER_MAYA_INFO("Number of Total Errors; " << out_numberOfErrors);
    }

    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: "
        "out_validFrameCount: "
        << out_validFrameCount);
    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: "
        "out_numberOfParameters: "
        << out_numberOfParameters);
    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: "
        "out_numberOfErrors: "
        << out_numberOfErrors);
    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: "
        "usedMarkerList.size(): "
        << markerList.size());
    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: "
        "usedAttrList.size(): "
        << attrList.size());

    // Bail out of solve if we don't have enough frames to solve.
    if (out_validFrameCount == 0) {
        const std::string invalidFrameStr =
            create_string_sorted_frame_numbers_disabled(out_validFrameList);

        if (out_cmdResult.printStats.doNotSolve) {
            // If the user is asking to print statistics, then we have
            // successfully achieved that goal and we cannot continue
            // to generate statistics, because not enough frames are valid.
            MMSOLVER_MAYA_VRB(
                "validateSolveFrames: "
                "No frames are valid to solve, invalid frames: "
                << invalidFrameStr);
            out_solve_is_valid = false;
            out_cmdResult.solverResult.success = true;
            return status;
        }
        MMSOLVER_MAYA_ERR(
            "Solver failure; No frames are valid to solve, invalid frames: "
            << invalidFrameStr);
        out_solve_is_valid = false;
        out_cmdResult.solverResult.success = false;
        return status;
    }

    // Bail out of solve if we don't have enough used markers or
    // attributes.
    const Count32 enabledMarkerCount = markerList.count_enabled();
    const Count32 enabledAttrCount = attrList.count_enabled();
    if ((enabledMarkerCount == 0) || (enabledAttrCount == 0)) {
        if (out_cmdResult.printStats.doNotSolve) {
            // If the user is asking to print statistics, then we have
            // successfully achieved that goal and we cannot continue
            // to generate statistics, because not enough markers or
            // attributes were used.
            MMSOLVER_MAYA_VRB(
                "validateSolveFrames: "
                "Not enough markers or attributes are used by solver; "
                << "used_markers=" << enabledMarkerCount << " "
                << "used_attributes=" << enabledAttrCount);
            out_solve_is_valid = false;
            out_cmdResult.solverResult.success = true;
            return status;
        }
        MMSOLVER_MAYA_ERR(
            "Solver failure; Not enough markers or attributes are used by "
            "solver; "
            << "used_markers=" << enabledMarkerCount << " "
            << "used_attributes=" << enabledAttrCount);
        out_solve_is_valid = false;
        out_cmdResult.solverResult.success = false;
        return status;
    }

    if ((out_numberOfParameters > out_numberOfErrors) ||
        (out_numberOfParameters == 0) || (out_numberOfErrors == 0)) {
        if (out_cmdResult.printStats.doNotSolve) {
            // If the user is asking to print statistics, then we have
            // successfully achieved that goal and we cannot continue
            // to generate statistics, because of an invalid number of
            // parameters/errors.
            MMSOLVER_MAYA_VRB(
                "validateSolveFrames: "
                "Cannot solve for more attributes (\"parameters\") "
                << "than number of markers (\"errors\"); "
                << "parameters=" << out_numberOfParameters << " "
                << "errors=" << out_numberOfErrors);
            out_solve_is_valid = false;
            out_cmdResult.solverResult.success = true;
            return status;
        }
        MMSOLVER_MAYA_ERR(
            "Solver failure; Cannot solve for more attributes (\"parameters\") "
            << "than number of markers (\"errors\"); "
            << "parameters=" << out_numberOfParameters << " "
            << "errors=" << out_numberOfErrors);
        out_solve_is_valid = false;
        out_cmdResult.solverResult.success = false;
        return status;
    }

    out_solve_is_valid = true;
    MMSOLVER_MAYA_VRB(
        "validateSolveFrames: "
        "out_solve_is_valid: "
        << out_solve_is_valid);
    return status;
}

MStatus validateSolve(
    CameraPtrList &cameraList, BundlePtrList &bundleList,
    const FrameList &frameList, const MarkerList &markerList,
    const AttrList &attrList, const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList,
    const MatrixBool3D &markerToAttrToFrameMatrix, SolverOptions &solverOptions,
    const FrameSolveMode frameSolveMode,
    //
    const MGlobal::MMayaState &mayaSessionState, MDGModifier &out_dgmod,
    MAnimCurveChange &out_curveChange, MComputation &out_computation,
    //
    std::vector<double> &out_jacobianList, IndexPairList &out_paramToAttrList,
    IndexPairList &out_errorToMarkerList,
    std::vector<MPoint> &out_markerPosList,
    std::vector<double> &out_markerWeightList,
    std::vector<double> &out_errorList, std::vector<double> &out_paramList,
    std::vector<double> &out_previousParamList,
    //
    uint32_t &out_numberOfParameters, uint32_t &out_numberOfErrors,
    uint32_t &out_numberOfMarkerErrors,
    uint32_t &out_numberOfAttrStiffnessErrors,
    uint32_t &out_numberOfAttrSmoothnessErrors, FrameCount &out_validFrameCount,
    FrameCount &out_invalidFrameCount,
    //
    FrameList &out_validFrameList, MatrixBool2D &out_errorToParamMatrix,
    MatrixBool2D &out_paramToFrameMatrix,
    std::vector<double> &out_paramWeightList,
    //
    const LogLevel &logLevel, const bool verbose, bool &out_solve_is_valid,
    CommandResult &out_cmdResult) {
    MMSOLVER_MAYA_VRB("validateSolve");

    MMSOLVER_MAYA_VRB("validateSolve: A");

    mmsolver::debug::Timestamp validateStartTimestamp =
        mmsolver::debug::get_timestamp();
    mmsolver::debug::TimestampBenchmark benchTimer;
    mmsolver::debug::CPUBenchmark benchTicks;
    benchTimer.start();
    benchTicks.start();

    const Count32 markerEnabledCount = markerList.count_enabled();
    const Count32 frameEnabledCount = frameList.count_enabled();
    if ((markerEnabledCount == 0) || (frameEnabledCount == 0)) {
        if (!out_cmdResult.printStats.doNotSolve) {
            if (markerEnabledCount == 0) {
                console_log_warn_no_valid_markers(markerList);
            }
            if (frameEnabledCount == 0) {
                console_log_warn_no_valid_frames(frameList);
            }
        }
        return MS::kSuccess;
    }

    // Get valid frames to solve with.
    bool solve_is_valid = false;
    MStatus status = validateSolveFrames(
        cameraList, bundleList, frameList, markerList, attrList, stiffAttrsList,
        smoothAttrsList, markerToAttrToFrameMatrix, frameSolveMode,
        solverOptions,
        //
        out_jacobianList, out_paramToAttrList, out_errorToMarkerList,
        out_markerPosList, out_markerWeightList, out_errorList, out_paramList,
        out_previousParamList,
        //
        out_numberOfParameters, out_numberOfErrors, out_numberOfMarkerErrors,
        out_numberOfAttrStiffnessErrors, out_numberOfAttrSmoothnessErrors,
        out_validFrameCount, out_invalidFrameCount,
        //
        out_validFrameList, out_errorToParamMatrix, out_paramToFrameMatrix,
        out_paramWeightList,
        //
        logLevel, verbose, solve_is_valid, out_cmdResult);
    MMSOLVER_MAYA_VRB("validateSolve: A solve_is_valid=" << solve_is_valid);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_VRB("validateSolve: A change solve_is_valid.");
        solve_is_valid = false;
    }
    if (!solve_is_valid) {
        out_solve_is_valid = false;
        return status;
    }

    MMSOLVER_MAYA_VRB("validateSolve: C");

    MMSOLVER_ASSERT(
        (out_validFrameCount + out_invalidFrameCount) == frameList.size(),
        "Frames can only be valid or invalid. "
        "All frames must be accountable as either of these states.");

    if (verbose) {
        benchTimer.stop();
        benchTicks.stop();

        const uint32_t total_frame_count = frameList.size();
        MMSOLVER_MAYA_VRB(
            "validateSolve: total_frame_count: " << total_frame_count);

        static std::ostream &stream = MStreamUtils::stdErrorStream();

        double validate_seconds = mmsolver::debug::timestamp_as_seconds(
            mmsolver::debug::get_timestamp() - validateStartTimestamp);
        validate_seconds = std::max(1e-9, validate_seconds);
        MMSOLVER_MAYA_VRB(
            "validateSolve: validate_seconds: " << validate_seconds);

        auto frames_per_sec = static_cast<size_t>(
            static_cast<double>(total_frame_count) / validate_seconds);
        std::string frames_per_sec_string =
            mmstring::numberToStringWithCommas(frames_per_sec);
        MMSOLVER_MAYA_VRB(
            "validateSolve: frames per-second: " << frames_per_sec_string);

        benchTimer.print(stream, "validateSolve: Validate Time", 1);
        benchTimer.print(stream, "validateSolve: Validate Time",
                         total_frame_count);
        benchTicks.print(stream, "validateSolve: Validate Ticks", 1);
        benchTicks.print(stream, "validateSolve: Validate Ticks",
                         total_frame_count);
    }

    out_solve_is_valid = true;
    return status;
}

MStatus solveFrames(
    CameraPtrList &cameraList, BundlePtrList &bundleList,
    const FrameList &frameList, MarkerList &markerList, AttrList &attrList,
    const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList,
    const MatrixBool3D &markerToAttrToFrameMatrix, SolverOptions &solverOptions,
    //
    const Count32 numberOfParameters, const Count32 numberOfErrors,
    const Count32 numberOfMarkerErrors,
    const Count32 numberOfAttrStiffnessErrors,
    const Count32 numberOfAttrSmoothnessErrors,
    const FrameCount validFrameCount, const FrameCount invalidFrameCount,
    //
    MatrixBool2D &errorToParamMatrix, MatrixBool2D &paramToFrameMatrix,
    std::vector<double> &paramWeightList,
    //
    const MGlobal::MMayaState &mayaSessionState, MDGModifier &out_dgmod,
    MAnimCurveChange &out_curveChange, MComputation &out_computation,
    //
    std::vector<double> &out_jacobianList, IndexPairList &out_paramToAttrList,
    IndexPairList &out_errorToMarkerList,
    std::vector<MPoint> &out_markerPosList,
    std::vector<double> &out_markerWeightList,
    std::vector<double> &out_errorList, std::vector<double> &out_paramList,
    std::vector<double> &out_previousParamList,
    //
    const LogLevel &logLevel, const bool verbose,
    CommandResult &out_cmdResult) {
    MStatus status = MS::kSuccess;
    MMSOLVER_MAYA_VRB("solveFrames");

    MMSOLVER_MAYA_VRB("solveFrames: C");

    MMSOLVER_ASSERT(numberOfErrors > 0,
                    "Valid solves cannot have zero errors.");
    MMSOLVER_ASSERT(numberOfParameters > 0,
                    "Valid solves cannot have zero parameters.");

    MMSOLVER_MAYA_VRB("solveFrames: numberOfErrors=" << numberOfErrors);
    MMSOLVER_MAYA_VRB("solveFrames: numberOfParameters=" << numberOfParameters);

    // Initialize memory for solving.
    out_paramList.resize(static_cast<uint64_t>(numberOfParameters), 0);
    out_previousParamList.resize(static_cast<uint64_t>(numberOfParameters), 0);
    out_errorList.resize(static_cast<uint64_t>(numberOfErrors), 0);
    out_jacobianList.resize(
        static_cast<uint64_t>(numberOfParameters * numberOfErrors), 0);

    std::vector<double> errorDistanceList(
        static_cast<uint64_t>(numberOfMarkerErrors / ERRORS_PER_MARKER), 0);
    MMSOLVER_ASSERT(out_errorToMarkerList.size() == errorDistanceList.size(),
                    "Errors and error distances must match.");

    MMSOLVER_MAYA_VRB("solveFrames: D");

    const auto frameCount = frameList.size();
    MMSOLVER_MAYA_VRB("solveFrames: frameCount=" << frameCount);
    if (logLevel >= LOG_LEVEL_PRINT_SOLVER_HEADER_EXTENDED) {
        console_log_solver_header_extended(markerList, attrList, frameList,
                                           solverOptions);
    } else if (!out_cmdResult.printStats.doNotSolve &&
               (logLevel >= LOG_LEVEL_PRINT_NORMAL_ITERATIONS)) {
        console_log_solver_header_simple(markerList, attrList, frameList);
    }

    // MComputation helper.
    const bool withProgressBar = !out_cmdResult.printStats.doNotSolve &&
                                 (logLevel >= LOG_LEVEL_SOLVER_PROGRESS_BAR) &&
                                 (frameCount > 1);
    if (withProgressBar) {
        const bool showProgressBar = true;
        const bool isInterruptable = true;
        const bool useWaitCursor = true;
        out_computation.setProgressRange(0, solverOptions.iterMax);
        out_computation.beginComputation(showProgressBar, isInterruptable,
                                         useWaitCursor);
    }

    // Start Solving
    SolverTimer timer;
    timer.startTimestamp = mmsolver::debug::get_timestamp();
    if (!out_cmdResult.printStats.doNotSolve) {
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
        MMSOLVER_MAYA_VRB("solveFrames: SceneGraphMode::kMMSceneGraph");
        status = construct_scene_graph(
            cameraList, markerList, bundleList, attrList, frameList,
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
            MMSOLVER_MAYA_ERR(
                "Maya DAG is invalid for use with MM Scene Graph, "
                << "please switch to Maya DAG and solve again.");
            out_cmdResult.solverResult.success = false;
            return status;
        }
    } else if (solverOptions.sceneGraphMode == SceneGraphMode::kMayaDag) {
        MMSOLVER_MAYA_VRB("solveFrames: SceneGraphMode::kMayaDag");
        // Nothing to do.
    } else {
        MMSOLVER_MAYA_ERR("Invalid Scene Graph mode!");
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    }

#if MMSOLVER_LENS_DISTORTION == 1
    MMSOLVER_MAYA_VRB("solveFrames: MMSOLVER_LENS_DISTORTION");
    std::vector<std::shared_ptr<mmlens::LensModel>> markerFrameToLensModelList;
    std::vector<std::shared_ptr<mmlens::LensModel>> attrFrameToLensModelList;
    std::vector<std::shared_ptr<mmlens::LensModel>> lensModelList;

    status = constructLensModelList(cameraList, markerList, attrList, frameList,
                                    markerFrameToLensModelList,
                                    attrFrameToLensModelList, lensModelList);
    CHECK_MSTATUS_AND_RETURN_IT(status);
#endif

    // Solving Objects.
    //
    // This data structure is passed to the solve function, so we can
    // access all this data inside the solver function.
    SolverData userData;
    userData.cameraList = cameraList;
    userData.markerList = markerList;
    userData.bundleList = bundleList;
    userData.attrList = attrList;
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
    userData.paramToFrameMatrix = paramToFrameMatrix;
    userData.errorToParamMatrix = errorToParamMatrix;
    userData.markerToAttrToFrameMatrix = markerToAttrToFrameMatrix;

    userData.paramList = out_paramList;
    userData.previousParamList = out_previousParamList;
    userData.errorList = out_errorList;
    userData.errorDistanceList = errorDistanceList;
    userData.jacobianList = out_jacobianList;
    userData.funcEvalNum = 0;  // number of function evaluations.
    userData.iterNum = 0;
    userData.jacIterNum = 0;
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

    userData.logLevel = logLevel;

    // Calculate initial errors.
    double initialErrorAvg = 0.0;
    double initialErrorMin = std::numeric_limits<double>::max();
    double initialErrorMax = -0.0;
    if (solverOptions.acceptOnlyBetter || out_cmdResult.printStats.deviation) {
        // TODO: Use mmsolver::ArrayMask.
        std::vector<bool> frameIndexEnable(frameList.size(), 1);
        std::vector<bool> skipErrorMeasurements(numberOfErrors, 1);
        measureErrors(numberOfErrors, numberOfMarkerErrors,
                      numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                      frameIndexEnable, skipErrorMeasurements,
                      solverOptions.imageWidth, &out_errorList[0], &userData,
                      initialErrorAvg, initialErrorMax, initialErrorMin,
                      status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        initialErrorAvg = 0;
        initialErrorMin = 0;
        initialErrorMax = 0;
        const bool error_stats_ok = compute_error_stats(
            numberOfMarkerErrors, userData.errorDistanceList, initialErrorAvg,
            initialErrorMin, initialErrorMax);
        if (!error_stats_ok) {
            MMSOLVER_MAYA_ERR("Failed to compute initial error stats.");
            out_cmdResult.solverResult.success = false;
            status = MS::kFailure;
            return status;
        }
    }

    // Fill in default values, with initial error values.
    out_cmdResult.solverResult.success = true;
    out_cmdResult.solverResult.reason_number = 0;
    out_cmdResult.solverResult.reason = "";
    out_cmdResult.solverResult.iterations = 0;
    out_cmdResult.solverResult.functionEvals = 0;
    out_cmdResult.solverResult.jacobianEvals = 0;
    out_cmdResult.solverResult.errorFinal = 0.0;
    out_cmdResult.solverResult.errorAvg = initialErrorAvg;
    out_cmdResult.solverResult.errorMin = initialErrorMin;
    out_cmdResult.solverResult.errorMax = initialErrorMax;

    if (out_cmdResult.printStats.doNotSolve) {
        logResultsErrorMetrics(numberOfMarkerErrors, userData.markerList,
                               userData.frameList, userData.errorToMarkerList,
                               userData.errorDistanceList,
                               out_cmdResult.errorMetricsResult);
        logResultsTimer(timer, out_cmdResult.timerResult);
        out_cmdResult.solverResult.user_interrupted = userData.userInterrupted;
        logResultsSolveValues(
            numberOfParameters,
            numberOfMarkerErrors + numberOfAttrStiffnessErrors +
                numberOfAttrSmoothnessErrors,
            out_paramList, userData.errorList, out_cmdResult.solveValuesResult);

        // There is no more printing to do, we must solve now if we
        // want to solve.
        status = MS::kSuccess;
        out_cmdResult.solverResult.success = true;
        return status;
    }

    // Set Initial parameters
    MMSOLVER_MAYA_VRB("Get Initial parameters...");
    const bool initial_ok = get_initial_parameters(
        numberOfParameters, out_paramList, out_paramToAttrList, attrList,
        frameList, solverOptions.solverSupportsParameterBounds,
        out_cmdResult.solverResult);
    if (!initial_ok) {
        MMSOLVER_MAYA_ERR("Failed to get initial parameters.");
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    }

    MMSOLVER_MAYA_VRB("Initial Parameters: ");
    for (int i = 0; i < numberOfParameters; ++i) {
        // Copy parameter values into the 'previous' parameter list.
        out_previousParamList[i] = out_paramList[i];
    }
    if (logLevel >= LOG_LEVEL_PRINT_SOLVER_PARAMETERS_INITIAL) {
        for (int i = 0; i < numberOfParameters; ++i) {
            IndexPair attrPair = out_paramToAttrList[i];
            const AttrIndex attrIndex = attrPair.first;
            AttrPtr attr = attrList.get_attr(attrIndex);

            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            MMSOLVER_MAYA_VRB("-> " << out_paramList[i] << " | "
                                    << attr_name_char);
        }
    }

    MMSOLVER_MAYA_VRB("Solve...");
    MMSOLVER_MAYA_VRB("Solver Type: " << solverOptions.solverType);
    if (solverOptions.solverType == SOLVER_TYPE_LEVMAR) {
        MMSOLVER_MAYA_ERR(
            "mmSolver: Solver Type is not supported by this compiled plug-in. "
            << "solverType=" << solverOptions.solverType);
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    } else if (solverOptions.solverType == SOLVER_TYPE_CMINPACK_LMDIF) {
        solve_3d_cminpack_lmdif(solverOptions, numberOfParameters,
                                numberOfErrors, out_paramList, out_errorList,
                                paramWeightList, userData,
                                out_cmdResult.solverResult);
    } else if (solverOptions.solverType == SOLVER_TYPE_CMINPACK_LMDER) {
        solve_3d_cminpack_lmder(solverOptions, numberOfParameters,
                                numberOfErrors, out_paramList, out_errorList,
                                paramWeightList, userData,
                                out_cmdResult.solverResult);
    } else if (solverOptions.solverType == SOLVER_TYPE_CERES_LMDIF) {
        solve_3d_ceres_lmdif(solverOptions, numberOfParameters, numberOfErrors,
                             out_paramList, out_errorList, paramWeightList,
                             userData, out_cmdResult.solverResult);
    } else if (solverOptions.solverType == SOLVER_TYPE_CERES_LMDER) {
        solve_3d_ceres_lmder(solverOptions, numberOfParameters, numberOfErrors,
                             out_paramList, out_errorList, paramWeightList,
                             userData, out_cmdResult.solverResult);
    } else {
        MMSOLVER_MAYA_ERR("mmSolver: Solver Type is invalid. solverType="
                          << solverOptions.solverType);
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    }

    if (!out_cmdResult.printStats.doNotSolve) {
        timer.solveBenchTicks.stop();
        timer.solveBenchTimer.stop();
    }
    if (withProgressBar) {
        out_computation.endComputation();
    }

    logResultsErrorMetrics(numberOfMarkerErrors, userData.markerList,
                           userData.frameList, userData.errorToMarkerList,
                           userData.errorDistanceList,
                           out_cmdResult.errorMetricsResult);
    logResultsTimer(timer, out_cmdResult.timerResult);
    out_cmdResult.solverResult.user_interrupted = userData.userInterrupted;

    // Solve Finished, re-calculate error, and only set parameters if
    // the average error is lower.
    bool errorIsBetter = true;
    double errorAvg = 0;
    double errorMin = 0;
    double errorMax = 0;
    const bool error_stats_ok =
        compute_error_stats(numberOfMarkerErrors, userData.errorDistanceList,
                            errorAvg, errorMin, errorMax);
    if (!error_stats_ok) {
        MMSOLVER_MAYA_ERR("Failed to compute error stats.");
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    }

    out_cmdResult.solverResult.errorAvg = errorAvg;
    out_cmdResult.solverResult.errorMin = errorMin;
    out_cmdResult.solverResult.errorMax = errorMax;
    if (solverOptions.acceptOnlyBetter) {
        errorIsBetter = errorAvg <= initialErrorAvg;
    }

    // Set the solved parameters
    bool set_attrs_ok = false;
    if (errorIsBetter) {
        MMSOLVER_MAYA_VRB("Setting Solved Parameters...");
        set_attrs_ok = set_maya_attribute_values(
            numberOfParameters, out_paramToAttrList, attrList, out_paramList,
            frameList, out_dgmod, out_curveChange);
    } else {
        // Set the initial parameter values.
        MMSOLVER_MAYA_VRB("Setting Initial Parameters...");
        set_attrs_ok = set_maya_attribute_values(
            numberOfParameters, out_paramToAttrList, attrList,
            out_previousParamList, frameList, out_dgmod, out_curveChange);
    }
    if (!set_attrs_ok) {
        MMSOLVER_MAYA_ERR("Failed to set solved parameters.");
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    }

    if (logLevel >= LOG_LEVEL_PRINT_SOLVER_PARAMETERS_SOLVED) {
        MMSOLVER_MAYA_VRB("Solved Parameters:");
        for (int i = 0; i < numberOfParameters; ++i) {
            IndexPair attrPair = out_paramToAttrList[i];
            const AttrIndex attrIndex = attrPair.first;
            AttrPtr attr = attrList.get_attr(attrIndex);

            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            const double offset = attr->getOffsetValue();
            const double scale = attr->getScaleValue();
            const double xmin = attr->getMinimumValue();
            const double xmax = attr->getMaximumValue();

            const double solver_value = out_paramList[i];
            const double real_value = parameterBoundFromInternalToExternal(
                solver_value, xmin, xmax, offset, scale);

            MMSOLVER_MAYA_VRB("-> " << real_value << " | " << attr_name_char);
        }
    }

    logResultsSolveValues(numberOfParameters, numberOfErrors, out_paramList,
                          userData.errorList, out_cmdResult.solveValuesResult);
    printSolveDetails(out_cmdResult.solverResult, userData, timer,
                      numberOfParameters, numberOfMarkerErrors,
                      numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                      logLevel, out_paramList);

    CHECK_MSTATUS(status);

    MMSOLVER_MAYA_VRB("solveFrames: Z");

    return status;
}

MStatus generateMarkerAndBundleRelationships(
    CameraPtrList &cameraList, MarkerList &markerList,
    BundlePtrList &bundleList, AttrList &attrList, const FrameList &frameList,
    const bool removeUnusedMarkers, const bool removeUnusedAttributes,
    const bool removeUnusedFrames,

    // Outputs
    Count32 &out_relationshipAttrsExistCount, MarkerList &out_validMarkerList,
    AttrList &out_validAttrList, FrameList &out_validFrameList,
    MatrixBool3D &out_markerToAttrToFrameMatrix) {
    MStatus status = MS::kSuccess;
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("generateMarkerAndBundleRelationships");

    MMSOLVER_MAYA_VRB(
        "generateMarkerAndBundleRelationships: removeUnusedMarkers="
        << removeUnusedMarkers);
    MMSOLVER_MAYA_VRB(
        "generateMarkerAndBundleRelationships: removeUnusedAttributes="
        << removeUnusedAttributes);
    MMSOLVER_MAYA_VRB(
        "generateMarkerAndBundleRelationships: removeUnusedFrames="
        << removeUnusedFrames);

    out_relationshipAttrsExistCount = 0;
    if (!removeUnusedMarkers && !removeUnusedAttributes &&
        !removeUnusedFrames) {
        // All 'object relationships' will be ignored.

        // All Markers, Attributes and Frames are assumed to be used.
        out_validMarkerList = MarkerList(markerList);
        out_validAttrList = AttrList(attrList);
        out_validFrameList = FrameList(frameList);

        // Initialise 'out_markerToAttrToFrameMatrix' to assume all
        // markers affect all attributes. This is the default
        // assumption.
        out_markerToAttrToFrameMatrix.reset(markerList.size(), attrList.size(),
                                            frameList.size(),
                                            /*fill_value=*/true);
    } else {
        // Query the relationship by pre-computed attributes on the
        // Markers. If the attributes do not exist, we assume all markers
        // affect all attributes (and therefore suffer a performance
        // problem).
        readStoredRelationships(markerList, attrList, frameList,

                                // Outputs
                                out_relationshipAttrsExistCount,
                                out_markerToAttrToFrameMatrix, status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Create 'valid' lists.
        generateValidMarkerAttrFrameLists(
            markerList, attrList, frameList, out_markerToAttrToFrameMatrix,

            out_validMarkerList, out_validAttrList, out_validFrameList, status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Print warnings about unused solve objects.
        if ((out_validMarkerList.count_disabled() > 0) && removeUnusedMarkers) {
            console_log_warn_unused_markers(out_validMarkerList);
        }
        if ((out_validAttrList.count_disabled() > 0) &&
            removeUnusedAttributes) {
            console_log_warn_unused_attributes(out_validAttrList);
        }

        // Change the list of Markers and Attributes to filter out unused
        // objects.
        bool usedMarkersChanged = false;
        if (removeUnusedMarkers) {
            MMSOLVER_MAYA_VRB(
                "generateMarkerAndBundleRelationships: "
                "out_validMarkerList.count_enabled()="
                << out_validMarkerList.count_enabled());
            MMSOLVER_MAYA_VRB(
                "generateMarkerAndBundleRelationships: "
                "out_validMarkerList.count_disabled()="
                << out_validMarkerList.count_disabled());

            if (out_validMarkerList.count_enabled() !=
                markerList.count_enabled()) {
                usedMarkersChanged = true;
            }
        } else {
            out_validMarkerList = MarkerList(markerList);
        }
        MMSOLVER_MAYA_VRB(
            "generateMarkerAndBundleRelationships: "
            "usedMarkersChanged="
            << usedMarkersChanged);

        bool usedAttrsChanged = false;
        if (removeUnusedAttributes) {
            MMSOLVER_MAYA_VRB(
                "generateMarkerAndBundleRelationships: "
                "out_validAttrList.count_enabled()="
                << out_validAttrList.count_enabled());
            MMSOLVER_MAYA_VRB(
                "generateMarkerAndBundleRelationships: "
                "out_validAttrList.count_disabled()="
                << out_validAttrList.count_disabled());

            if (out_validAttrList.count_enabled() != attrList.count_enabled()) {
                usedAttrsChanged = true;
            }

        } else {
            out_validAttrList = AttrList(attrList);
        }
        MMSOLVER_MAYA_VRB(
            "generateMarkerAndBundleRelationships: "
            "usedAttrsChanged="
            << usedAttrsChanged);
    }

    MMSOLVER_MAYA_VRB(
        "generateMarkerAndBundleRelationships: "
        "out_relationshipAttrsExistCount="
        << out_relationshipAttrsExistCount);

    return status;
}

// We assume that the per-frame solve will be (relatively)
// fast, and so we don't need as much logging per-frame
// otherwise the solve will slow down due to so much text
// being printed out.
LogLevel chooseLogLevelPerFrame(const LogLevel logLevel) {
    LogLevel perFrameLogLevel = logLevel;
    if (logLevel >= LOG_LEVEL_PRINT_NORMAL_ITERATIONS) {
        const auto logLevelNum = static_cast<int8_t>(logLevel);
        perFrameLogLevel = static_cast<LogLevel>(std::max(0, logLevelNum - 1));
    }
    return perFrameLogLevel;
}

/*! Solve everything!
 *
 * This function is responsible for taking the given cameras, markers,
 * bundles and solver options, and modifying the current Maya scene,
 * saving changes in the 'dgmod' variable, and returning the results
 * in the outResult string.
 */
bool solve_v1(SolverOptions &solverOptions, CameraPtrList &cameraList,
              MarkerList &markerList, BundlePtrList &bundleList,
              AttrList &attrList, const FrameList &frameList,
              StiffAttrsPtrList &stiffAttrsList,
              SmoothAttrsPtrList &smoothAttrsList, MDGModifier &dgmod,
              MAnimCurveChange &curveChange, MComputation &computation,
              const MStringArray &printStatsList, const LogLevel logLevel,
              MStringArray &outResult) {
    MStatus status = MS::kSuccess;

    CommandResult cmdResult;

    bool verbose = logLevel >= LogLevel::kDebug;
    cmdResult.printStats = constructPrintStats(printStatsList);
    if (cmdResult.printStats.doNotSolve) {
        // When printing statistics, turn off verbosity.
        verbose = false;
    }

    MMSOLVER_MAYA_VRB("solve_v1");

#ifdef MAYA_PROFILE
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope profilingScope(profileCategory, MProfiler::kColorC_L3,
                                   "solve");
#endif

    const Count32 markerEnabledCount = markerList.count_enabled();
    const Count32 attrEnabledCount = attrList.count_enabled();
    const Count32 frameEnabledCount = frameList.count_enabled();
    MMSOLVER_MAYA_VRB("solve_v1: markerList enabled=" << markerEnabledCount);
    MMSOLVER_MAYA_VRB("solve_v1: attrList enabled=" << attrEnabledCount);
    MMSOLVER_MAYA_VRB("solve_v1: frameList enabled=" << frameEnabledCount);
    if ((markerEnabledCount == 0) || (attrEnabledCount == 0) ||
        (frameEnabledCount == 0)) {
        if (!cmdResult.printStats.doNotSolve) {
            if (markerEnabledCount == 0) {
                console_log_warn_no_valid_markers(markerList);
            }
            if (attrEnabledCount == 0) {
                console_log_warn_no_valid_attrs(attrList);
            }
            if (frameEnabledCount == 0) {
                console_log_warn_no_valid_frames(frameList);
            }
        }
        return MS::kSuccess;
    }

    MMSOLVER_MAYA_VRB("solve_v1: A");

    // The validated markers and attributes.
    MarkerList validMarkerList;
    AttrList validAttrList;
    FrameList validFrameList;

    // Initialise 'markerToAttrToFrameMatrix' to assume all markers affect
    // all attributes on all frames. This is the default assumption.
    auto markerToAttrToFrameMatrix = MatrixBool3D();

    Count32 relationshipAttrsExistCount = 0;
    status = generateMarkerAndBundleRelationships(
        cameraList, markerList, bundleList, attrList, frameList,
        solverOptions.removeUnusedMarkers, solverOptions.removeUnusedAttributes,
        solverOptions.removeUnusedFrames,

        // Outputs
        relationshipAttrsExistCount, validMarkerList, validAttrList,
        validFrameList, markerToAttrToFrameMatrix);
    CHECK_MSTATUS(status);

    const Count32 validMarkerEnabledCount = validMarkerList.count_enabled();
    const Count32 validAttrEnabledCount = validAttrList.count_enabled();
    const Count32 validFrameEnabledCount = validFrameList.count_enabled();
    MMSOLVER_MAYA_VRB(
        "solve_v1: validMarkerList enabled=" << validMarkerEnabledCount);
    MMSOLVER_MAYA_VRB(
        "solve_v1: validAttrList enabled=" << validAttrEnabledCount);
    MMSOLVER_MAYA_VRB(
        "solve_v1: validFrameList enabled=" << validFrameEnabledCount);
    if ((validMarkerEnabledCount == 0) || (validAttrEnabledCount == 0) ||
        (validFrameEnabledCount == 0)) {
        if (!cmdResult.printStats.doNotSolve) {
            if (validMarkerEnabledCount == 0) {
                console_log_warn_no_valid_markers(validMarkerList);
            }
            if (validAttrEnabledCount == 0) {
                console_log_warn_no_valid_attrs(validAttrList);
            }
            if (validFrameEnabledCount == 0) {
                console_log_warn_no_valid_frames(validFrameList);
            }
        }
        return MS::kSuccess;
    }

    MMSOLVER_MAYA_VRB("solve_v1: B");

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

    auto frameSolveMode = solverOptions.frameSolveMode;
    MMSOLVER_MAYA_VRB(
        "solve_v1: frameSolveMode: " << static_cast<uint32_t>(frameSolveMode));
    if (frameSolveMode == FrameSolveMode::kAllFrameAtOnce) {
        MMSOLVER_MAYA_VRB(
            "solve_v1: frameSolveMode == FrameSolveMode::kAllFrameAtOnce");

        Count32 numberOfParameters = 0;
        Count32 numberOfErrors = 0;
        Count32 numberOfMarkerErrors = 0;
        Count32 numberOfAttrStiffnessErrors = 0;
        Count32 numberOfAttrSmoothnessErrors = 0;
        FrameCount validFrameCount = 0;
        FrameCount invalidFrameCount = 0;

        MatrixBool2D errorToParamMatrix;
        MatrixBool2D paramToFrameMatrix;
        std::vector<double> paramWeightList;

        FrameList validAllFrameList(validFrameList);

        bool solve_is_valid = false;
        status = validateSolve(
            cameraList, bundleList, validFrameList, validMarkerList,
            validAttrList, stiffAttrsList, smoothAttrsList,
            markerToAttrToFrameMatrix, solverOptions, frameSolveMode,
            //
            mayaSessionState, dgmod, curveChange, computation,
            //
            jacobianList, paramToAttrList, errorToMarkerList, markerPosList,
            markerWeightList, errorList, paramList, previousParamList,
            //
            numberOfParameters, numberOfErrors, numberOfMarkerErrors,
            numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
            validFrameCount, invalidFrameCount,
            //
            validAllFrameList, errorToParamMatrix, paramToFrameMatrix,
            paramWeightList,
            //
            logLevel, verbose, solve_is_valid, cmdResult);
        CHECK_MSTATUS(status);

        if (solve_is_valid) {
            status = solveFrames(
                cameraList, bundleList, validAllFrameList, validMarkerList,
                validAttrList, stiffAttrsList, smoothAttrsList,
                markerToAttrToFrameMatrix, solverOptions,
                //
                numberOfParameters, numberOfErrors, numberOfMarkerErrors,
                numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                validFrameCount, invalidFrameCount,
                //
                errorToParamMatrix, paramToFrameMatrix, paramWeightList,
                //
                mayaSessionState, dgmod, curveChange, computation,
                //
                jacobianList, paramToAttrList, errorToMarkerList, markerPosList,
                markerWeightList, errorList, paramList, previousParamList,
                //
                logLevel, verbose, cmdResult);
        } else {
            MMSOLVER_MAYA_VRB("solve_v1: Cannot continue solving.");
        }
    } else if (frameSolveMode == FrameSolveMode::kPerFrame) {
        MMSOLVER_MAYA_VRB(
            "solve_v1: frameSolveMode == FrameSolveMode::kPerFrame");

        Count32 numberOfParameters = 0;
        Count32 numberOfErrors = 0;
        Count32 numberOfMarkerErrors = 0;
        Count32 numberOfAttrStiffnessErrors = 0;
        Count32 numberOfAttrSmoothnessErrors = 0;
        FrameCount validFrameCount = 0;
        FrameCount invalidFrameCount = 0;

        MatrixBool2D errorToParamMatrix;
        MatrixBool2D paramToFrameMatrix;
        std::vector<double> paramWeightList;

        const auto frameCount = frameList.size();
        MMSOLVER_MAYA_VRB("solve_v1: frameCount=" << frameCount);

        const bool withProgressBar =
            !cmdResult.printStats.doNotSolve &&
            (logLevel >= LOG_LEVEL_SOLVER_PROGRESS_BAR);
        if (withProgressBar) {
            const bool showProgressBar = true;
            const bool isInterruptable = true;
            const bool useWaitCursor = true;
            computation.setProgressRange(0, static_cast<int>(frameCount));
            computation.beginComputation(showProgressBar, isInterruptable,
                                         useWaitCursor);
        }

        auto perFrameLogLevel = chooseLogLevelPerFrame(logLevel);

        FrameList validAllFrameList(validFrameList);
        FrameList validPerFrameList(validFrameList);
        for (auto i = 0; i < frameCount; ++i) {
            MMSOLVER_MAYA_VRB("solve_v1: i=" << i);

            if (withProgressBar) {
                computation.setProgress(i);
            }

            const FrameNumber frameNumber = validFrameList.get_frame(i);
            const bool frameEnabled = validFrameList.get_enabled(i);
            MMSOLVER_MAYA_VRB("solve_v1: frameNumber=" << frameNumber);
            MMSOLVER_MAYA_VRB("solve_v1: frameEnabled=" << frameEnabled);

            if (!frameEnabled) {
                MMSOLVER_MAYA_VRB("solve_v1: Skipping solving disabled frame "
                                  << frameNumber << ".");
                continue;
            }

            validPerFrameList.set_all_enabled(false);
            validPerFrameList.set_enabled(i, true);

            validAllFrameList.set_all_enabled(false);
            validAllFrameList.set_enabled(i, true);

            CommandResult perFrameCmdResult;
            perFrameCmdResult.printStats = cmdResult.printStats;

            bool solve_is_valid = false;
            status = validateSolve(
                cameraList, bundleList, validAllFrameList, validMarkerList,
                validAttrList, stiffAttrsList, smoothAttrsList,
                markerToAttrToFrameMatrix, solverOptions, frameSolveMode,
                //
                mayaSessionState, dgmod, curveChange, computation,
                //
                jacobianList, paramToAttrList, errorToMarkerList, markerPosList,
                markerWeightList, errorList, paramList, previousParamList,
                //
                numberOfParameters, numberOfErrors, numberOfMarkerErrors,
                numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                validFrameCount, invalidFrameCount,
                //
                validPerFrameList, errorToParamMatrix, paramToFrameMatrix,
                paramWeightList,
                //
                logLevel, verbose, solve_is_valid, perFrameCmdResult);
            CHECK_MSTATUS(status);

            if (solve_is_valid) {
                status = solveFrames(
                    cameraList, bundleList, validPerFrameList, validMarkerList,
                    validAttrList, stiffAttrsList, smoothAttrsList,
                    markerToAttrToFrameMatrix, solverOptions,
                    //
                    numberOfParameters, numberOfErrors, numberOfMarkerErrors,
                    numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                    validFrameCount, invalidFrameCount,
                    //
                    errorToParamMatrix, paramToFrameMatrix, paramWeightList,
                    //
                    mayaSessionState, dgmod, curveChange, computation,
                    //
                    jacobianList, paramToAttrList, errorToMarkerList,
                    markerPosList, markerWeightList, errorList, paramList,
                    previousParamList,
                    //
                    perFrameLogLevel, verbose, perFrameCmdResult);

                // Combine results from each iteration.
                cmdResult.add(perFrameCmdResult);
            } else {
                MMSOLVER_MAYA_VRB("solve_v1: Cannot continue solving.");
            }

            if (status != MS::kSuccess) {
                MMSOLVER_MAYA_ERR("Failed to solve frame "
                                  << frameNumber << ", stopping solve.");
                break;
            }
        }

        cmdResult.divide();

        computation.endComputation();
    }

    cmdResult.appendToMStringArray(outResult);

    MMSOLVER_MAYA_VRB("solve_v1: cmdResult.solverResult.success="
                      << cmdResult.solverResult.success);
    MMSOLVER_MAYA_VRB("solve_v1: Z");

    return cmdResult.solverResult.success;
}

/*! Solve everything!
 *
 * This function is responsible for taking the given cameras, markers,
 * bundles and solver options, and modifying the current Maya scene,
 * saving changes in the 'dgmod' variable, and returning the results
 * in the outResult string.
 *
 * This is the refactored solve function. It's intended to be shorter
 * and easier to understand while providing exactly the same
 * functionality.
 *
 * As part of this refactor, we can remove older features that are
 * unused or unneeded, such as stiffness and smoothness attributes.
 */
bool solve_v2(SolverOptions &solverOptions, CameraPtrList &cameraList,
              MarkerList &markerList, BundlePtrList &bundleList,
              AttrList &attrList, const FrameList &frameList,
              MDGModifier &dgmod, MAnimCurveChange &curveChange,
              MComputation &computation, const MStringArray &printStatsList,
              const LogLevel logLevel, CommandResult &out_cmdResult) {
    MStatus status = MS::kSuccess;

    bool verbose = logLevel >= LogLevel::kDebug;
    out_cmdResult.printStats = constructPrintStats(printStatsList);
    if (out_cmdResult.printStats.doNotSolve) {
        // When printing statistics, turn off verbosity.
        verbose = false;
    }

    MMSOLVER_MAYA_VRB("solve_v2");

#ifdef MAYA_PROFILE
    int profileCategory = MProfiler::getCategoryIndex("mmSolver");
    MProfilingScope profilingScope(profileCategory, MProfiler::kColorC_L3,
                                   "solve");
#endif

    // TODO: Remove stiffness and smoothness attributes.
    StiffAttrsPtrList stiffAttrsList;
    SmoothAttrsPtrList smoothAttrsList;

    MMSOLVER_MAYA_VRB("solve_v2: A");

    // The validated markers and attributes.
    MarkerList validMarkerList;
    AttrList validAttrList;
    FrameList validFrameList;

    // Initialise 'markerToAttrToFrameMatrix' to assume all markers affect
    // all attributes on all frames. This is the default assumption.
    auto markerToAttrToFrameMatrix = MatrixBool3D();

    Count32 relationshipAttrsExistCount = 0;
    status = generateMarkerAndBundleRelationships(
        cameraList, markerList, bundleList, attrList, frameList,
        solverOptions.removeUnusedMarkers, solverOptions.removeUnusedAttributes,
        solverOptions.removeUnusedFrames,

        // Outputs
        relationshipAttrsExistCount, validMarkerList, validAttrList,
        validFrameList, markerToAttrToFrameMatrix);
    CHECK_MSTATUS(status);

    const Count32 markerEnabledCount = markerList.count_enabled();
    const Count32 frameEnabledCount = frameList.count_enabled();
    if ((markerEnabledCount == 0) || (frameEnabledCount == 0)) {
        if (!out_cmdResult.printStats.doNotSolve) {
            if (markerEnabledCount == 0) {
                console_log_warn_no_valid_markers(markerList);
            }
            if (frameEnabledCount == 0) {
                console_log_warn_no_valid_frames(frameList);
            }
        }
        return MS::kSuccess;
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

    auto frameSolveMode = solverOptions.frameSolveMode;
    MMSOLVER_MAYA_VRB(
        "solve_v2: frameSolveMode: " << static_cast<uint32_t>(frameSolveMode));
    if (frameSolveMode == FrameSolveMode::kAllFrameAtOnce) {
        MMSOLVER_MAYA_VRB(
            "solve_v2: frameSolveMode == FrameSolveMode::kAllFrameAtOnce");

        Count32 numberOfParameters = 0;
        Count32 numberOfErrors = 0;
        Count32 numberOfMarkerErrors = 0;
        Count32 numberOfAttrStiffnessErrors = 0;
        Count32 numberOfAttrSmoothnessErrors = 0;
        FrameCount validFrameCount = 0;
        FrameCount invalidFrameCount = 0;

        MatrixBool2D errorToParamMatrix;
        MatrixBool2D paramToFrameMatrix;
        std::vector<double> paramWeightList;

        FrameList validFrameList(frameList);

        bool solve_is_valid = false;
        status = validateSolve(
            cameraList, bundleList, validFrameList, validMarkerList,
            validAttrList, stiffAttrsList, smoothAttrsList,
            markerToAttrToFrameMatrix, solverOptions, frameSolveMode,
            //
            mayaSessionState, dgmod, curveChange, computation,
            //
            jacobianList, paramToAttrList, errorToMarkerList, markerPosList,
            markerWeightList, errorList, paramList, previousParamList,
            //
            numberOfParameters, numberOfErrors, numberOfMarkerErrors,
            numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
            validFrameCount, invalidFrameCount,
            //
            validFrameList, errorToParamMatrix, paramToFrameMatrix,
            paramWeightList,
            //
            logLevel, verbose, solve_is_valid, out_cmdResult);
        CHECK_MSTATUS(status);

        if (solve_is_valid) {
            status = solveFrames(
                cameraList, bundleList, validFrameList, validMarkerList,
                validAttrList, stiffAttrsList, smoothAttrsList,
                markerToAttrToFrameMatrix, solverOptions,
                //
                numberOfParameters, numberOfErrors, numberOfMarkerErrors,
                numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                validFrameCount, invalidFrameCount,
                //
                errorToParamMatrix, paramToFrameMatrix, paramWeightList,
                //
                mayaSessionState, dgmod, curveChange, computation,
                //
                jacobianList, paramToAttrList, errorToMarkerList, markerPosList,
                markerWeightList, errorList, paramList, previousParamList,
                //
                logLevel, verbose, out_cmdResult);
        } else {
            MMSOLVER_MAYA_VRB("solve_v2: Cannot continue solving.");
        }
    } else if (frameSolveMode == FrameSolveMode::kPerFrame) {
        MMSOLVER_MAYA_VRB(
            "solve_v2: frameSolveMode == FrameSolveMode::kPerFrame");

        Count32 numberOfParameters = 0;
        Count32 numberOfErrors = 0;
        Count32 numberOfMarkerErrors = 0;
        Count32 numberOfAttrStiffnessErrors = 0;
        Count32 numberOfAttrSmoothnessErrors = 0;
        FrameCount validFrameCount = 0;
        FrameCount invalidFrameCount = 0;

        MatrixBool2D errorToParamMatrix;
        MatrixBool2D paramToFrameMatrix;
        std::vector<double> paramWeightList;

        FrameList validPerFrameList(frameList);

        const auto frameCount = frameList.size();
        MMSOLVER_MAYA_VRB("solve_v2: frameCount=" << frameCount);

        const bool withProgressBar =
            (!out_cmdResult.printStats.doNotSolve) &&
            (logLevel >= LOG_LEVEL_SOLVER_PROGRESS_BAR);
        if (withProgressBar) {
            const bool showProgressBar = true;
            const bool isInterruptable = true;
            const bool useWaitCursor = true;
            computation.setProgressRange(0, frameCount);
            computation.beginComputation(showProgressBar, isInterruptable,
                                         useWaitCursor);
        }

        auto perFrameLogLevel = chooseLogLevelPerFrame(logLevel);

        for (auto i = 0; i < frameCount; ++i) {
            MMSOLVER_MAYA_VRB("solve_v2: i=" << i);

            if (withProgressBar) {
                computation.setProgress(i);
            }

            CommandResult perFrameCmdResult;
            perFrameCmdResult.printStats = out_cmdResult.printStats;

            const FrameNumber frameNumber = frameList.get_frame(i);
            const bool frameEnabled = frameList.get_enabled(i);
            MMSOLVER_MAYA_VRB("solve_v2: frameNumber=" << frameNumber);
            MMSOLVER_MAYA_VRB("solve_v2: frameEnabled=" << frameEnabled);

            if (!frameEnabled) {
                MMSOLVER_MAYA_VRB("solve_v2: Skipping solving disabled frame "
                                  << frameNumber << ".");
                continue;
            }

            validPerFrameList.set_all_enabled(false);
            validPerFrameList.set_enabled(i, true);

            bool solve_is_valid = false;
            status = validateSolve(
                cameraList, bundleList, validFrameList, validMarkerList,
                validAttrList, stiffAttrsList, smoothAttrsList,
                markerToAttrToFrameMatrix, solverOptions, frameSolveMode,
                //
                mayaSessionState, dgmod, curveChange, computation,
                //
                jacobianList, paramToAttrList, errorToMarkerList, markerPosList,
                markerWeightList, errorList, paramList, previousParamList,
                //
                numberOfParameters, numberOfErrors, numberOfMarkerErrors,
                numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                validFrameCount, invalidFrameCount,
                //
                validPerFrameList, errorToParamMatrix, paramToFrameMatrix,
                paramWeightList,
                //
                perFrameLogLevel, verbose, solve_is_valid, perFrameCmdResult);
            CHECK_MSTATUS(status);

            if (solve_is_valid) {
                status = solveFrames(
                    cameraList, bundleList, validPerFrameList, validMarkerList,
                    validAttrList, stiffAttrsList, smoothAttrsList,
                    markerToAttrToFrameMatrix, solverOptions,
                    //
                    numberOfParameters, numberOfErrors, numberOfMarkerErrors,
                    numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                    validFrameCount, invalidFrameCount,
                    //
                    errorToParamMatrix, paramToFrameMatrix, paramWeightList,
                    //
                    mayaSessionState, dgmod, curveChange, computation,
                    //
                    jacobianList, paramToAttrList, errorToMarkerList,
                    markerPosList, markerWeightList, errorList, paramList,
                    previousParamList,
                    //
                    perFrameLogLevel, verbose, perFrameCmdResult);
            } else {
                MMSOLVER_MAYA_VRB("solve_v2: Cannot continue solving.");
            }

            // Combine results from each iteration.
            out_cmdResult.add(perFrameCmdResult);

            if (status != MS::kSuccess) {
                MMSOLVER_MAYA_ERR("Failed to solve frame "
                                  << frameNumber << ", stopping solve.");
                break;
            }
        }

        out_cmdResult.divide();

        computation.endComputation();
    }

    MMSOLVER_MAYA_VRB("solve_v2: cmdResult.solverResult.success="
                      << out_cmdResult.solverResult.success);
    MMSOLVER_MAYA_VRB("solve_v2: Z");

    return out_cmdResult.solverResult.success;
}

}  // namespace mmsolver
