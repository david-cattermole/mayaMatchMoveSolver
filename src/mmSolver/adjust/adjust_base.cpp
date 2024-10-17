/*
 * Copyright (C) 2018, 2019, 2022 David Cattermole.
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
#include <limits>
#include <map>
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
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

#ifdef MAYA_PROFILE
#include <maya/MProfiler.h>
#endif

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "adjust_cminpack_lmder.h"
#include "adjust_cminpack_lmdif.h"
#include "adjust_measureErrors.h"
#include "adjust_relationships.h"
#include "adjust_results.h"
#include "adjust_solveFunc.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_lens_model_utils.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_scene_graph.h"
#include "mmSolver/utilities/debug_utils.h"
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
                << "\"cminpack_lm\", "
                << "\"cminpack_lmder\", "
                << "or \"ceres\"; "
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
    const AttrPtrList &attrList, const MTimeArray &frameList,
    SolverResult &out_solverResult) {
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
            out_solverResult.success = false;
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
    const AttrPtrList &attrList, const std::vector<double> &paramList,
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
    assert(numberOfMarkerErrors > 0);
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
                            const MarkerPtrList &markerList,
                            const MTimeArray &frameList,
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
    const bool verbose = logLevel >= LogLevel::kDebug;

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

    if (logLevel >= LogLevel::kInfo) {
        if (solverResult.success) {
            MStreamUtils::stdErrorStream() << "Solver returned SUCCESS    | ";
        } else {
            MStreamUtils::stdErrorStream() << "Solver returned FAILURE    | ";
        }

        double seconds = mmsolver::debug::timestamp_as_seconds(
            mmsolver::debug::get_timestamp() - timer.startTimestamp);
        seconds = std::max(1e-9, seconds);
        auto evals_per_sec = static_cast<size_t>(
            static_cast<double>(solverResult.functionEvals) / seconds);
        std::string evals_per_sec_string =
            mmstring::numberToStringWithCommas(evals_per_sec);

        const auto solverResult_iterations =
            static_cast<uint32_t>(solverResult.iterations);

        const size_t buffer_size = 128;
        char formatBuffer[buffer_size];
        std::snprintf(formatBuffer, buffer_size,
                      "error avg %8.4f   min %8.4f   max %8.4f  "
                      "iterations %03u  (%s evals/sec)",
                      solverResult.errorAvg, solverResult.errorMin,
                      solverResult.errorMax, solverResult_iterations,
                      &evals_per_sec_string[0]);
        // Note: We use std::endl to flush the stream, and ensure an
        //  update for the user.
        MMSOLVER_MAYA_INFO(std::string(formatBuffer));
    }

    if (logLevel >= LogLevel::kDebug) {
        unsigned int total_num = userData.iterNum + userData.jacIterNum;
        assert(total_num > 0);
        static std::ostream &stream = MStreamUtils::stdErrorStream();
        timer.solveBenchTimer.print(stream, "Solve Time", 1);
        timer.funcBenchTimer.print(stream, "Func Time", 1);
        timer.jacBenchTimer.print(stream, "Jacobian Time", 1);
        timer.paramBenchTimer.print(stream, "Param Time", total_num);
        timer.errorBenchTimer.print(stream, "Error Time", total_num);
        timer.funcBenchTimer.print(stream, "Func Time", total_num);

        timer.solveBenchTicks.print(stream, "Solve Ticks", 1);
        timer.funcBenchTicks.print(stream, "Func Ticks", 1);
        timer.jacBenchTicks.print(stream, "Jacobian Ticks", 1);
        timer.paramBenchTicks.print(stream, "Param Ticks", total_num);
        timer.errorBenchTicks.print(stream, "Error Ticks", total_num);
        timer.funcBenchTicks.print(stream, "Func Ticks", total_num);
    }
}

MStatus logResultsObjectCounts(const int numberOfParameters,
                               const int numberOfErrors,
                               const int numberOfMarkerErrors,
                               const int numberOfAttrStiffnessErrors,
                               const int numberOfAttrSmoothnessErrors,
                               SolverObjectCountResult &out_result) {
    MStatus status = MStatus::kSuccess;
    out_result.fill(numberOfParameters, numberOfErrors, numberOfMarkerErrors,
                    numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors);
    return status;
}

/*
 * Print out the marker-to-attribute 'affects' relationship.
 *
 * markerToAttrList is expected to be pre-computed from the function
 * 'getMarkerToAttributeRelationship'.
 */
MStatus logResultsMarkerAffectsAttribute(const MarkerPtrList &markerList,
                                         const AttrPtrList &attrList,
                                         const BoolList2D &markerToAttrList,
                                         AffectsResult &out_result) {
    MStatus status = MStatus::kSuccess;
    out_result.fill(markerList, attrList, markerToAttrList);
    return status;
}

/*
 * Print out if objects added to the solve (such as markers and
 * attributes) are being used, or are unused.
 */
MStatus logResultsSolveObjectUsage(MarkerPtrList &usedMarkerList,
                                   MarkerPtrList &unusedMarkerList,
                                   AttrPtrList &usedAttrList,
                                   AttrPtrList &unusedAttrList,
                                   SolverObjectUsageResult &out_result) {
    MStatus status = MStatus::kSuccess;
    out_result.fill(usedMarkerList, unusedMarkerList, usedAttrList,
                    unusedAttrList);
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
        if (used) {
            usedList.push_back(object);
        } else {
            unusedList.push_back(object);
        }
    }
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
MStatus splitUsedMarkersAndAttributes(const MarkerPtrList &markerList,
                                      const AttrPtrList &attrList,
                                      const BoolList2D &markerToAttrList,
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

static inline bool addNumberRangeToStringStream(const int &startNum,
                                                const int &endNum,
                                                std::stringstream &ss) {
    if (startNum == endNum) {
        ss << " " << startNum;
    } else if ((endNum - startNum) == 1) {
        ss << " " << startNum << " " << endNum;
    } else {
        ss << " " << startNum << "-" << endNum;
    }
    return true;
}

bool addFrameListToStringStream(const MTimeArray &frameList,
                                std::stringstream &ss) {
    // Display contiguous frame numbers in the format '10-13', rather
    // than '10 11 12 13'.
    //
    // This function is ported from Python, see the function
    // 'intListToString', in ./python/mmSolver/utils/converttypes.py

    int startNum = -1;
    int endNum = -1;
    int prevNum = -1;

    auto frameCount = frameList.length();
    for (auto i = 0; i < frameCount; i++) {
        MTime frame(frameList[i]);
        int frameNum = static_cast<int>(frame.value());

        bool first = i == 0;
        bool last = (i + 1) == frameCount;

        if (first) {
            // Start a new group.
            startNum = frameNum;
            endNum = frameNum;
        }

        if ((prevNum + 1) != frameNum) {
            // End old group.
            endNum = prevNum;
            if (endNum != -1) {
                addNumberRangeToStringStream(startNum, endNum, ss);
            }

            // New group.
            startNum = frameNum;
            endNum = frameNum;
        }

        if (last) {
            // Close off final group.
            endNum = frameNum;
            if (endNum != -1) {
                addNumberRangeToStringStream(startNum, endNum, ss);
            }
        }

        prevNum = frameNum;
    }

    return frameCount > 0;
}

MStatus solveFrames(
    CameraPtrList &cameraList, BundlePtrList &bundleList,
    const MTimeArray &frameList, MarkerPtrList &usedMarkerList,
    MarkerPtrList &unusedMarkerList, AttrPtrList &usedAttrList,
    AttrPtrList &unusedAttrList, const StiffAttrsPtrList &stiffAttrsList,
    const SmoothAttrsPtrList &smoothAttrsList,
    const BoolList2D &markerToAttrList, SolverOptions &solverOptions,
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
    const LogLevel &logLevel, CommandResult &out_cmdResult) {
    MStatus status = MS::kSuccess;
    out_cmdResult.solverResult.success = true;

    const bool verbose = logLevel >= LogLevel::kDebug;

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

    if (out_cmdResult.printStats.input) {
        assert(out_cmdResult.printStats.doNotSolve);
        status = logResultsObjectCounts(
            numberOfParameters, numberOfErrors, numberOfMarkerErrors,
            numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
            out_cmdResult.solverObjectCountResult);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (out_cmdResult.printStats.usedSolveObjects) {
        assert(out_cmdResult.printStats.doNotSolve);
        status = logResultsSolveObjectUsage(
            usedMarkerList, unusedMarkerList, usedAttrList, unusedAttrList,
            out_cmdResult.solverObjectUsageResult);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (out_cmdResult.printStats.affects) {
        assert(out_cmdResult.printStats.doNotSolve);
        status = logResultsMarkerAffectsAttribute(usedMarkerList, usedAttrList,
                                                  markerToAttrList,
                                                  out_cmdResult.affectsResult);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (logLevel >= LogLevel::kDebug) {
        MMSOLVER_MAYA_INFO("Number of Markers; used="
                           << usedMarkerList.size()
                           << " | unused=" << unusedMarkerList.size());
        MMSOLVER_MAYA_INFO("Number of Attributes; used="
                           << usedAttrList.size()
                           << " | unused=" << unusedAttrList.size());
        MMSOLVER_MAYA_INFO("Number of Parameters; " << numberOfParameters);
        MMSOLVER_MAYA_INFO("Number of Frames; " << frameList.length());
        MMSOLVER_MAYA_INFO("Number of Marker Errors; " << numberOfMarkerErrors);
        MMSOLVER_MAYA_INFO("Number of Attribute Stiffness Errors; "
                           << numberOfAttrStiffnessErrors);
        MMSOLVER_MAYA_INFO("Number of Attribute Smoothness Errors; "
                           << numberOfAttrSmoothnessErrors);
        MMSOLVER_MAYA_INFO("Number of Total Errors; " << numberOfErrors);
    }

    // Bail out of solve if we don't have enough used markers or
    // attributes.
    if ((usedMarkerList.empty()) || (usedAttrList.empty())) {
        if (out_cmdResult.printStats.doNotSolve) {
            // If the user is asking to print statistics, then we have
            // successfully achieved that goal and we cannot continue
            // to generate statistics, because not enough markers or
            // attributes were used.
            out_cmdResult.solverResult.success = true;
            status = MS::kSuccess;
            return status;
        }
        MMSOLVER_MAYA_ERR(
            "Solver failure; not enough markers or attributes are not used by "
            "solver "
            << "used markers=" << usedMarkerList.size() << " "
            << "used attributes=" << usedAttrList.size());
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    }

    if (numberOfParameters > numberOfErrors) {
        if (out_cmdResult.printStats.doNotSolve) {
            // If the user is asking to print statistics, then we have
            // successfully achieved that goal and we cannot continue
            // to generate statistics, because of an invalid number of
            // parameters/errors.
            out_cmdResult.solverResult.success = true;
            status = MS::kSuccess;
            return status;
        }
        MMSOLVER_MAYA_ERR(
            "Solver failure; cannot solve for more attributes (\"parameters\") "
            << "than number of markers (\"errors\"). "
            << "parameters=" << numberOfParameters << " "
            << "errors=" << numberOfErrors);
        out_cmdResult.solverResult.success = false;
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

    auto frameCount = frameList.length();
    if (logLevel >= LogLevel::kDebug) {
        MMSOLVER_MAYA_INFO(
            "------------------------------------------------------------------"
            "-------------");
        MMSOLVER_MAYA_INFO("Solving...");
        MMSOLVER_MAYA_INFO("Solver Type=" << solverOptions.solverType);
        MMSOLVER_MAYA_INFO("Maximum Iterations=" << solverOptions.iterMax);
        MMSOLVER_MAYA_INFO("Tau=" << solverOptions.tau);
        MMSOLVER_MAYA_INFO("Epsilon1=" << solverOptions.eps1);
        MMSOLVER_MAYA_INFO("Epsilon2=" << solverOptions.eps2);
        MMSOLVER_MAYA_INFO("Epsilon3=" << solverOptions.eps3);
        MMSOLVER_MAYA_INFO("Delta=" << fabs(solverOptions.delta));
        MMSOLVER_MAYA_INFO(
            "Auto Differencing Type=" << solverOptions.autoDiffType);
        MMSOLVER_MAYA_INFO(
            "Time Evaluation Mode=" << solverOptions.timeEvalMode);
        MMSOLVER_MAYA_INFO("Marker count: " << usedMarkerList.size());
        MMSOLVER_MAYA_INFO("Attribute count: " << usedAttrList.size());
        MMSOLVER_MAYA_INFO("Frame count: " << frameCount);

        std::stringstream ss;
        addFrameListToStringStream(frameList, ss);
        MMSOLVER_MAYA_INFO("Frames:" << ss.str());
    } else if (!out_cmdResult.printStats.doNotSolve &&
               (logLevel >= LogLevel::kVerbose)) {
        MMSOLVER_MAYA_INFO(
            "------------------------------------------------------------------"
            "-------------");
        MMSOLVER_MAYA_INFO("Solving...");
        MMSOLVER_MAYA_INFO("Marker count: " << usedMarkerList.size());
        MMSOLVER_MAYA_INFO("Attribute count: " << usedAttrList.size());
        MMSOLVER_MAYA_INFO("Frame count: " << frameCount);

        std::stringstream ss;
        addFrameListToStringStream(frameList, ss);
        MMSOLVER_MAYA_INFO("Frames:" << ss.str());
    }

    // MComputation helper.
    if (!out_cmdResult.printStats.doNotSolve && (logLevel >= LogLevel::kInfo) &&
        (frameCount > 1)) {
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
            MMSOLVER_MAYA_ERR(
                "Maya DAG is invalid for use with MM Scene Graph, "
                << "please switch to Maya DAG and solve again.");
            out_cmdResult.solverResult.success = false;
            return status;
        }
    } else if (solverOptions.sceneGraphMode == SceneGraphMode::kMayaDag) {
        // Nothing to do.
    } else {
        MMSOLVER_MAYA_ERR("Invalid Scene Graph mode!");
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    }

#if MMSOLVER_LENS_DISTORTION == 1
    std::vector<std::shared_ptr<mmlens::LensModel>> markerFrameToLensModelList;
    std::vector<std::shared_ptr<mmlens::LensModel>> attrFrameToLensModelList;
    std::vector<std::shared_ptr<mmlens::LensModel>> lensModelList;

    status = mmsolver::constructLensModelList(
        cameraList, usedMarkerList, usedAttrList, frameList,
        markerFrameToLensModelList, attrFrameToLensModelList, lensModelList);
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
        std::vector<bool> frameIndexEnable(frameList.length(), 1);
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
        numberOfParameters, out_paramList, out_paramToAttrList, usedAttrList,
        frameList, out_cmdResult.solverResult);
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
    if (logLevel >= LogLevel::kDebug) {
        for (int i = 0; i < numberOfParameters; ++i) {
            IndexPair attrPair = out_paramToAttrList[i];
            AttrPtr attr = usedAttrList[attrPair.first];

            MString attr_name = attr->getName();
            auto attr_name_char = attr_name.asChar();

            MMSOLVER_MAYA_VRB("-> " << out_paramList[i] << " | "
                                    << attr_name_char);
        }
    }

    if (solverOptions.solverType == SOLVER_TYPE_LEVMAR) {
        MMSOLVER_MAYA_ERR(
            "Solver Type is not supported by this compiled plug-in. "
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
    } else {
        MMSOLVER_MAYA_ERR(
            "Solver Type is invalid. solverType=" << solverOptions.solverType);
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    }

    if (!out_cmdResult.printStats.doNotSolve) {
        timer.solveBenchTicks.stop();
        timer.solveBenchTimer.stop();
    }
    if (!out_cmdResult.printStats.doNotSolve && (logLevel >= LogLevel::kInfo) &&
        (frameCount > 1)) {
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
            numberOfParameters, out_paramToAttrList, usedAttrList,
            out_paramList, frameList, out_dgmod, out_curveChange);
    } else {
        // Set the initial parameter values.
        MMSOLVER_MAYA_VRB("Setting Initial Parameters...");
        set_attrs_ok = set_maya_attribute_values(
            numberOfParameters, out_paramToAttrList, usedAttrList,
            out_previousParamList, frameList, out_dgmod, out_curveChange);
    }
    if (!set_attrs_ok) {
        MMSOLVER_MAYA_ERR("Failed to set solved parameters.");
        out_cmdResult.solverResult.success = false;
        status = MS::kFailure;
        return status;
    }

    if (logLevel >= LogLevel::kDebug) {
        MMSOLVER_MAYA_VRB("Solved Parameters:");
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

            MMSOLVER_MAYA_VRB("-> " << real_value << " | " << attr_name_char);
        }
    }

    logResultsSolveValues(numberOfParameters,
                          numberOfMarkerErrors + numberOfAttrStiffnessErrors +
                              numberOfAttrSmoothnessErrors,
                          out_paramList, userData.errorList,
                          out_cmdResult.solveValuesResult);
    printSolveDetails(out_cmdResult.solverResult, userData, timer,
                      numberOfParameters, numberOfMarkerErrors,
                      numberOfAttrStiffnessErrors, numberOfAttrSmoothnessErrors,
                      logLevel, out_paramList);

    CHECK_MSTATUS(status);

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
bool solve_v1(SolverOptions &solverOptions, CameraPtrList &cameraList,
              MarkerPtrList &markerList, BundlePtrList &bundleList,
              AttrPtrList &attrList, const MTimeArray &frameList,
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
        if ((!unusedMarkerList.empty()) &&
            (solverOptions.removeUnusedMarkers)) {
            MMSOLVER_MAYA_WRN("Unused Markers detected and ignored:");
            for (MarkerPtrListCIt mit = unusedMarkerList.cbegin();
                 mit != unusedMarkerList.cend(); ++mit) {
                MarkerPtr marker = *mit;
                const char *markerName = marker->getLongNodeName().asChar();
                MMSOLVER_MAYA_WRN("-> " << markerName);
            }
        }

        if ((!unusedAttrList.empty()) &&
            (solverOptions.removeUnusedAttributes)) {
            MMSOLVER_MAYA_WRN("Unused Attributes detected and ignored:");
            for (AttrPtrListCIt ait = unusedAttrList.cbegin();
                 ait != unusedAttrList.cend(); ++ait) {
                AttrPtr attr = *ait;
                const char *attrName = attr->getLongName().asChar();
                MMSOLVER_MAYA_WRN("-> " << attrName);
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

        if (usedObjectsChanged) {
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

    auto frameSolveMode = solverOptions.frameSolveMode;
    MMSOLVER_MAYA_VRB(
        "frameSolveMode: " << static_cast<uint32_t>(frameSolveMode));
    if (frameSolveMode == FrameSolveMode::kAllFrameAtOnce) {
        status = solveFrames(
            cameraList, bundleList, frameList, usedMarkerList, unusedMarkerList,
            usedAttrList, unusedAttrList, stiffAttrsList, smoothAttrsList,
            markerToAttrList, solverOptions,
            //
            mayaSessionState, dgmod, curveChange, computation,
            //
            jacobianList, paramToAttrList, errorToMarkerList, markerPosList,
            markerWeightList, errorList, paramList, previousParamList,
            //
            logLevel, cmdResult);
    } else if (frameSolveMode == FrameSolveMode::kPerFrame) {
        auto frameCount = frameList.length();

        if (!cmdResult.printStats.doNotSolve) {
            const bool showProgressBar = true;
            const bool isInterruptable = true;
            const bool useWaitCursor = true;
            computation.setProgressRange(0, frameCount);
            computation.beginComputation(showProgressBar, isInterruptable,
                                         useWaitCursor);
        }

        // We assume that the per-frame solve will be (relatively)
        // fast, and so we don't need as much logging per-frame
        // otherwise the solve will slow down due to so much text
        // being printed out.
        auto perFrameLogLevel = logLevel;
        if (logLevel == LogLevel::kVerbose) {
            perFrameLogLevel = LogLevel::kInfo;
        }

        for (auto i = 0; i < frameCount; ++i) {
            computation.setProgress(i);

            CommandResult perFrameCmdResult;
            perFrameCmdResult.printStats = cmdResult.printStats;

            auto frames = MTimeArray(1, frameList[i]);
            status = solveFrames(
                cameraList, bundleList, frames, usedMarkerList,
                unusedMarkerList, usedAttrList, unusedAttrList, stiffAttrsList,
                smoothAttrsList, markerToAttrList, solverOptions,
                //
                mayaSessionState, dgmod, curveChange, computation,
                //
                jacobianList, paramToAttrList, errorToMarkerList, markerPosList,
                markerWeightList, errorList, paramList, previousParamList,
                //
                perFrameLogLevel, perFrameCmdResult);

            // Combine results from each iteration.
            cmdResult.add(perFrameCmdResult);

            if (status != MS::kSuccess) {
                auto frame = frameList[i].asUnits(MTime::uiUnit());
                MMSOLVER_MAYA_ERR("Failed to solve frame "
                                  << frame << ", stopping solve.");
                break;
            }
        }

        cmdResult.divide();

        computation.endComputation();
    }

    cmdResult.appendToMStringArray(outResult);
    return cmdResult.solverResult.success;
}

bool solve_v2(SolverOptions &solverOptions, CameraPtrList &cameraList,
              MarkerPtrList &markerList, BundlePtrList &bundleList,
              AttrPtrList &attrList, const MTimeArray &frameList,
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

    StiffAttrsPtrList stiffAttrsList;
    SmoothAttrsPtrList smoothAttrsList;

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
        if ((!unusedMarkerList.empty()) &&
            (solverOptions.removeUnusedMarkers)) {
            MMSOLVER_MAYA_WRN("Unused Markers detected and ignored:");
            for (MarkerPtrListCIt mit = unusedMarkerList.cbegin();
                 mit != unusedMarkerList.cend(); ++mit) {
                MarkerPtr marker = *mit;
                const char *markerName = marker->getLongNodeName().asChar();
                MMSOLVER_MAYA_WRN("-> " << markerName);
            }
        }

        if ((!unusedAttrList.empty()) &&
            (solverOptions.removeUnusedAttributes)) {
            MMSOLVER_MAYA_WRN("Unused Attributes detected and ignored:");
            for (AttrPtrListCIt ait = unusedAttrList.cbegin();
                 ait != unusedAttrList.cend(); ++ait) {
                AttrPtr attr = *ait;
                const char *attrName = attr->getLongName().asChar();
                MMSOLVER_MAYA_WRN("-> " << attrName);
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

        if (usedObjectsChanged) {
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

    auto frameSolveMode = solverOptions.frameSolveMode;
    MMSOLVER_MAYA_VRB(
        "frameSolveMode: " << static_cast<uint32_t>(frameSolveMode));
    if (frameSolveMode == FrameSolveMode::kAllFrameAtOnce) {
        status = solveFrames(
            cameraList, bundleList, frameList, usedMarkerList, unusedMarkerList,
            usedAttrList, unusedAttrList, stiffAttrsList, smoothAttrsList,
            markerToAttrList, solverOptions,
            //
            mayaSessionState, dgmod, curveChange, computation,
            //
            jacobianList, paramToAttrList, errorToMarkerList, markerPosList,
            markerWeightList, errorList, paramList, previousParamList,
            //
            logLevel, out_cmdResult);
    } else if (frameSolveMode == FrameSolveMode::kPerFrame) {
        auto frameCount = frameList.length();

        if (!out_cmdResult.printStats.doNotSolve) {
            const bool showProgressBar = true;
            const bool isInterruptable = true;
            const bool useWaitCursor = true;
            computation.setProgressRange(0, frameCount);
            computation.beginComputation(showProgressBar, isInterruptable,
                                         useWaitCursor);
        }

        // We assume that the per-frame solve will be (relatively)
        // fast, and so we don't need as much logging per-frame
        // otherwise the solve will slow down due to so much text
        // being printed out.
        auto perFrameLogLevel = logLevel;
        if (logLevel == LogLevel::kVerbose) {
            perFrameLogLevel = LogLevel::kInfo;
        }

        for (auto i = 0; i < frameCount; ++i) {
            computation.setProgress(i);

            CommandResult perFrameCmdResult;
            perFrameCmdResult.printStats = out_cmdResult.printStats;

            auto frames = MTimeArray(1, frameList[i]);
            status = solveFrames(
                cameraList, bundleList, frames, usedMarkerList,
                unusedMarkerList, usedAttrList, unusedAttrList, stiffAttrsList,
                smoothAttrsList, markerToAttrList, solverOptions,
                //
                mayaSessionState, dgmod, curveChange, computation, jacobianList,
                //
                paramToAttrList, errorToMarkerList, markerPosList,
                markerWeightList, errorList, paramList, previousParamList,
                //
                perFrameLogLevel, perFrameCmdResult);

            // Combine results from each iteration.
            out_cmdResult.add(perFrameCmdResult);

            if (status != MS::kSuccess) {
                auto frame = frameList[i].asUnits(MTime::uiUnit());
                MMSOLVER_MAYA_ERR("Failed to solve frame "
                                  << frame << ", stopping solve.");
                break;
            }
        }

        out_cmdResult.divide();

        computation.endComputation();
    }

    return out_cmdResult.solverResult.success;
}
