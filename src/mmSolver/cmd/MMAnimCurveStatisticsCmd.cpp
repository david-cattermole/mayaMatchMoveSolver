/*
 * Copyright (C) 2025 David Cattermole.
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
 * 'mmAnimCurveStatistics' Maya command.
 *
 */

#include "MMAnimCurveStatisticsCmd.h"

// STL
#include <algorithm>
#include <cmath>
#include <cstring>
#include <vector>

// Maya
#include <maya/MAnimUtil.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MGlobal.h>
#include <maya/MStreamUtils.h>
#include <maya/MSyntax.h>

// MM Solver Libs
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

// MM Solver
#include "mmSolver/cmd/anim_curve_cmd_utils.h"
#include "mmSolver/core/types.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"

// MM Scene Graph
#include "mmscenegraph/mmscenegraph.h"

// Command arguments:
#define START_FRAME_FLAG_SHORT "-sf"
#define START_FRAME_FLAG_LONG "-startFrame"

#define END_FRAME_FLAG_SHORT "-ef"
#define END_FRAME_FLAG_LONG "-endFrame"

#define MEAN_FLAG_SHORT "-m"
#define MEAN_FLAG_LONG "-mean"

#define MEDIAN_FLAG_SHORT "-md"
#define MEDIAN_FLAG_LONG "-median"

#define POPULATION_VARIANCE_FLAG_SHORT "-pvr"
#define POPULATION_VARIANCE_FLAG_LONG "-populationVariance"

#define POPULATION_STANDARD_DEVIATION_FLAG_SHORT "-psd"
#define POPULATION_STANDARD_DEVIATION_FLAG_LONG "-populationStandardDeviation"

#define SIGNAL_TO_NOISE_RATIO_FLAG_SHORT "-snr"
#define SIGNAL_TO_NOISE_RATIO_FLAG_LONG "-signalToNoiseRatio"

#define X_VALUES_FLAG_SHORT "-xv"
#define X_VALUES_FLAG_LONG "-xValues"

#define Y_VALUES_FLAG_SHORT "-yv"
#define Y_VALUES_FLAG_LONG "-yValues"

#define CMD_NAME "mmAnimCurveStatistics"

// Statistic type identifiers for output.
#define STAT_TYPE_MEAN 0.0
#define STAT_TYPE_MEDIAN 1.0
#define STAT_TYPE_POPULATION_VARIANCE 2.0
#define STAT_TYPE_POPULATION_STD_DEV 3.0
#define STAT_TYPE_SIGNAL_TO_NOISE_RATIO 4.0

namespace mmsg = mmscenegraph;

namespace mmsolver {

MMAnimCurveStatisticsCmd::~MMAnimCurveStatisticsCmd() {}

void *MMAnimCurveStatisticsCmd::creator() {
    return new MMAnimCurveStatisticsCmd();
}

MString MMAnimCurveStatisticsCmd::cmdName() { return MString(CMD_NAME); }

bool MMAnimCurveStatisticsCmd::hasSyntax() const { return true; }

bool MMAnimCurveStatisticsCmd::isUndoable() const { return false; }

MSyntax MMAnimCurveStatisticsCmd::newSyntax() {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(CMD_NAME << ": newSyntax");

    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(START_FRAME_FLAG_SHORT, START_FRAME_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(END_FRAME_FLAG_SHORT, END_FRAME_FLAG_LONG,
                   MSyntax::kUnsigned);

    // Statistics flags.
    syntax.addFlag(MEAN_FLAG_SHORT, MEAN_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(MEDIAN_FLAG_SHORT, MEDIAN_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(POPULATION_VARIANCE_FLAG_SHORT,
                   POPULATION_VARIANCE_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(POPULATION_STANDARD_DEVIATION_FLAG_SHORT,
                   POPULATION_STANDARD_DEVIATION_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(SIGNAL_TO_NOISE_RATIO_FLAG_SHORT,
                   SIGNAL_TO_NOISE_RATIO_FLAG_LONG, MSyntax::kBoolean);

    // List input flags.
    syntax.addFlag(X_VALUES_FLAG_SHORT, X_VALUES_FLAG_LONG, MSyntax::kDouble);
    syntax.makeFlagMultiUse(X_VALUES_FLAG_SHORT);
    syntax.addFlag(Y_VALUES_FLAG_SHORT, Y_VALUES_FLAG_LONG, MSyntax::kDouble);
    syntax.makeFlagMultiUse(Y_VALUES_FLAG_SHORT);

    // Add object argument for animation curve.
    const Count32 min_curves = 0;
    syntax.setObjectType(MSyntax::kSelectionList, min_curves);
    syntax.useSelectionAsDefault(true);

    return syntax;
}

MStatus MMAnimCurveStatisticsCmd::parseArgs(const MArgList &args) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(CMD_NAME << ": parseArgs");

    MStatus status = MStatus::kSuccess;
    MArgDatabase argData(syntax(), args, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Check if list inputs are provided.
    m_useListInput = false;
    if (argData.isFlagSet(X_VALUES_FLAG_SHORT) ||
        argData.isFlagSet(Y_VALUES_FLAG_SHORT)) {
        m_useListInput = true;

        // Both X and Y values must be provided together.
        if (!argData.isFlagSet(X_VALUES_FLAG_SHORT) ||
            !argData.isFlagSet(Y_VALUES_FLAG_SHORT)) {
            MGlobal::displayError(
                CMD_NAME
                ": Both xValues and yValues must be provided together.");
            return MS::kFailure;
        }

        Count32 xCount = argData.numberOfFlagUses(X_VALUES_FLAG_SHORT);
        Count32 yCount = argData.numberOfFlagUses(Y_VALUES_FLAG_SHORT);

        if (xCount < 2) {
            MGlobal::displayError(CMD_NAME
                                  ": xValues must have 2 or more values.");
            return MS::kFailure;
        }

        if (yCount < 2) {
            MGlobal::displayError(CMD_NAME
                                  ": yValues must have 2 or more values.");
            return MS::kFailure;
        }

        if (xCount != yCount) {
            MGlobal::displayError(
                CMD_NAME ": Number of xValues must match number of yValues.");
            return MS::kFailure;
        }

        // Parse the list values for each curve.
        m_xValues.clear();
        m_yValues.clear();

        for (Count32 i = 0; i < xCount; ++i) {
            MArgList args;
            status = argData.getFlagArgumentList(X_VALUES_FLAG_SHORT, i, args);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            const double value = args.asDouble(0, &status);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            m_xValues.push_back(value);
        }

        for (Count32 i = 0; i < xCount; ++i) {
            MArgList args;
            status = argData.getFlagArgumentList(Y_VALUES_FLAG_SHORT, i, args);
            const double value = args.asDouble(0, &status);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            m_yValues.push_back(value);
        }

    } else {
        // Get animation curve from selection.
        status = argData.getObjects(m_selection);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        if (m_selection.length() == 0) {
            MGlobal::displayError(CMD_NAME
                                  ": Please select at least one animation "
                                  "curve or provide list values.");
            return MS::kFailure;
        }

        // To make sure that if any node is invalid, we catch it here, and
        // not during 'doIt'.
        for (auto i = 0; i < m_selection.length(); i++) {
            status = m_selection.getDependNode(i, m_animCurveObj);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }

    // Parse optional frame range arguments.
    m_startFrame = std::numeric_limits<FrameNumber>::max();
    m_endFrame = std::numeric_limits<FrameNumber>::max();
    if (argData.isFlagSet(START_FRAME_FLAG_SHORT)) {
        status =
            argData.getFlagArgument(START_FRAME_FLAG_SHORT, 0, m_startFrame);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(END_FRAME_FLAG_SHORT)) {
        status = argData.getFlagArgument(END_FRAME_FLAG_SHORT, 0, m_endFrame);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Parse statistics flags with default values.
    m_calculateMean = false;
    m_calculateMedian = false;
    m_calculatePopVariance = false;
    m_calculatePopStdDev = false;
    m_calculateSignalToNoiseRatio = false;

    if (argData.isFlagSet(MEAN_FLAG_SHORT)) {
        status = argData.getFlagArgument(MEAN_FLAG_SHORT, 0, m_calculateMean);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(MEDIAN_FLAG_SHORT)) {
        status =
            argData.getFlagArgument(MEDIAN_FLAG_SHORT, 0, m_calculateMedian);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(POPULATION_VARIANCE_FLAG_SHORT)) {
        status = argData.getFlagArgument(POPULATION_VARIANCE_FLAG_SHORT, 0,
                                         m_calculatePopVariance);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(POPULATION_STANDARD_DEVIATION_FLAG_SHORT)) {
        status = argData.getFlagArgument(
            POPULATION_STANDARD_DEVIATION_FLAG_SHORT, 0, m_calculatePopStdDev);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(SIGNAL_TO_NOISE_RATIO_FLAG_SHORT)) {
        status = argData.getFlagArgument(SIGNAL_TO_NOISE_RATIO_FLAG_SHORT, 0,
                                         m_calculateSignalToNoiseRatio);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Check that at least one statistic is enabled.
    if (!m_calculateMean && !m_calculateMedian && !m_calculatePopVariance &&
        !m_calculatePopStdDev && !m_calculateSignalToNoiseRatio) {
        MGlobal::displayError(CMD_NAME
                              ": At least one statistic must be enabled.");
        return MS::kFailure;
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_startFrame=" << m_startFrame);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_endFrame=" << m_endFrame);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateMean=" << m_calculateMean);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateMedian=" << m_calculateMedian);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculatePopVariance="
                               << m_calculatePopVariance);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculatePopStdDev="
                               << m_calculatePopStdDev);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateSignalToNoiseRatio="
                               << m_calculateSignalToNoiseRatio);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_useListInput=" << m_useListInput);

    return status;
}

MStatus MMAnimCurveStatisticsCmd::doIt(const MArgList &args) {
    const bool verbose = false;

    MStatus status = parseArgs(args);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    MDoubleArray result;

    // Output format:
    //
    // For each curve:
    // [curveIndex, numStats, stat1Type, stat1Value, stat2Type, stat2Value, ...]
    //
    // Where statType: 0=mean, 1=median, 2=variance, 3=stdDev, 4=SNR

    auto time_unit = MTime::uiUnit();
    Count32 success_count = 0;
    Count32 failure_count = 0;

    // Determine the number of curves to process.
    Count32 numCurves = m_selection.length();
    if (m_useListInput) {
        numCurves = 1;
    }

    rust::Vec<mmsg::Real> values_x;
    rust::Vec<mmsg::Real> values_y;
    for (auto i = 0; i < numCurves; i++) {
        values_x.clear();
        values_y.clear();

        if (m_useListInput) {
            const auto count = m_xValues.size();
            values_x.reserve(count);
            values_y.reserve(count);

            for (Count32 j = 0; j < count; ++j) {
                const double x = m_xValues[j];
                values_x.push_back(x);
            }

            for (Count32 j = 0; j < count; ++j) {
                const double y = m_yValues[j];
                values_y.push_back(y);
            }

        } else {
            // Use animation curve.
            status = m_selection.getDependNode(i, m_animCurveObj);
            if (status != MS::kSuccess) {
                MGlobal::displayWarning(CMD_NAME
                                        ": Selected object is not DG node.");
                failure_count++;
                continue;
            }

            status = m_animCurveFn.setObject(m_animCurveObj);
            if (status != MS::kSuccess) {
                MGlobal::displayWarning(
                    CMD_NAME ": Failed to set animation curve function set.");
                failure_count++;
                continue;
            }

            FrameNumber start_frame = 0;
            FrameNumber end_frame = 0;
            const FrameCount min_keyframe_count = 2;
            const FrameCount min_frame_count = 2;
            const char *cmd_name = CMD_NAME;
            bool success = validate_anim_curve(
                cmd_name, m_startFrame, m_endFrame, min_keyframe_count,
                min_frame_count, m_animCurveFn, start_frame, end_frame);
            if (!success) {
                MGlobal::displayWarning(
                    CMD_NAME ": Failed to validate animation curve.");
                failure_count++;
                continue;
            }

            auto frame_count = static_cast<size_t>(end_frame - start_frame) + 1;
            values_x.reserve(frame_count);
            values_y.reserve(frame_count);
            status = evaluate_curve(start_frame, end_frame, time_unit,
                                    m_animCurveFn, values_x, values_y);
            if (status != MS::kSuccess) {
                MGlobal::displayWarning(
                    CMD_NAME ": Failed to evaluate animation curve.");
                failure_count++;
                continue;
            }
        }

        MMSOLVER_MAYA_VRB(CMD_NAME << ": Input curve size:"
                                      " x="
                                   << values_x.size()
                                   << " y=" << values_y.size());

        // Create data slice for statistics calculations.
        rust::Slice<const mmsg::Real> values_slice_y{values_y.data(),
                                                     values_y.size()};

        // Count statistics and prepare result array.
        std::vector<std::pair<double, double>> statsResults;

        // Variables to store calculated values.
        mmsg::Real mean = 0.0;
        mmsg::Real pop_variance = 0.0;
        mmsg::Real pop_std_dev = 0.0;
        mmsg::Real snr = 0.0;
        bool meanCalculated = false;

        // Calculate variance first, because it gives us the mean as well.
        if (m_calculatePopVariance) {
            if (mmsg::calc_population_variance(values_slice_y, mean,
                                               pop_variance)) {
                statsResults.push_back(
                    {STAT_TYPE_POPULATION_VARIANCE, pop_variance});
                meanCalculated = true;
                MMSOLVER_MAYA_VRB(CMD_NAME << ": pop_variance="
                                           << pop_variance);
            } else {
                MGlobal::displayWarning(
                    CMD_NAME ": Failed to calculate population variance.");
            }
        }

        if (m_calculatePopStdDev && !m_calculatePopVariance) {
            if (mmsg::calc_population_standard_deviation(values_slice_y, mean,
                                                         pop_std_dev)) {
                statsResults.push_back(
                    {STAT_TYPE_POPULATION_STD_DEV, pop_std_dev});
                meanCalculated = true;
                MMSOLVER_MAYA_VRB(CMD_NAME << ": standard deviation="
                                           << pop_std_dev);
            } else {
                MGlobal::displayWarning(
                    CMD_NAME ": Failed to calculate standard deviation.");
            }
        } else if (m_calculatePopStdDev && m_calculatePopVariance) {
            // We already have population variance, just calculate population
            // std dev from it.
            pop_std_dev = std::sqrt(pop_variance);
            statsResults.push_back({STAT_TYPE_POPULATION_STD_DEV, pop_std_dev});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": standard deviation="
                                       << pop_std_dev);
        }

        // Calculate SNR if needed.
        if (m_calculateSignalToNoiseRatio) {
            mmsg::Real signal_to_noise_ratio_mean = 0.0;
            if (mmsg::calc_signal_to_noise_ratio(
                    values_slice_y, signal_to_noise_ratio_mean, snr)) {
                statsResults.push_back({STAT_TYPE_SIGNAL_TO_NOISE_RATIO, snr});
                if (!meanCalculated) {
                    mean = signal_to_noise_ratio_mean;
                    meanCalculated = true;
                }
                MMSOLVER_MAYA_VRB(CMD_NAME << ": SNR=" << snr);
            } else {
                MGlobal::displayWarning(
                    CMD_NAME ": Failed to calculate signal-to-noise ratio.");
            }
        }

        // If mean is requested and we have it, add it.
        if (m_calculateMean && meanCalculated) {
            // Insert mean at the beginning (it should come first in output).
            statsResults.insert(statsResults.begin(), {STAT_TYPE_MEAN, mean});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": mean=" << mean);
        } else if (m_calculateMean && !meanCalculated) {
            // Need to calculate mean separately - use variance function.
            mmsg::Real dummy_variance = 0.0;
            if (mmsg::calc_population_variance(values_slice_y, mean,
                                               dummy_variance)) {
                statsResults.insert(statsResults.begin(),
                                    {STAT_TYPE_MEAN, mean});
                MMSOLVER_MAYA_VRB(CMD_NAME << ": mean=" << mean);
            } else {
                MGlobal::displayWarning(CMD_NAME ": Failed to calculate mean.");
            }
        }

        // Calculate median if needed (requires sorted data).
        if (m_calculateMedian) {
            // Create sorted copy of the data.
            rust::Vec<mmsg::Real> sorted_values_y = values_y;
            std::sort(sorted_values_y.begin(), sorted_values_y.end());

            rust::Slice<const mmsg::Real> sorted_slice_y{
                sorted_values_y.data(), sorted_values_y.size()};

            // Calculate median using quartiles function.
            mmsg::Real q1 = 0.0, q2 = 0.0, q3 = 0.0;
            if (mmsg::calc_quartiles(sorted_slice_y, q1, q2, q3)) {
                // Insert median after mean (if mean exists).
                auto insertPos = statsResults.begin();
                if (m_calculateMean && !statsResults.empty() &&
                    statsResults[0].first == STAT_TYPE_MEAN) {
                    insertPos++;
                }
                statsResults.insert(insertPos, {STAT_TYPE_MEDIAN, q2});
                MMSOLVER_MAYA_VRB(CMD_NAME << ": median=" << q2);
            } else {
                MGlobal::displayWarning(CMD_NAME
                                        ": Failed to calculate median.");
            }
        }

        // Build result array for this curve.
        const auto curve_index = static_cast<double>(i);
        const auto statistics_count = static_cast<double>(statsResults.size());
        result.append(curve_index);
        result.append(statistics_count);

        for (const auto &stat : statsResults) {
            result.append(stat.first);   // stat type
            result.append(stat.second);  // stat value
        }

        success_count++;
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": failure_count="
                               << static_cast<int32_t>(failure_count));
    MMSOLVER_MAYA_VRB(CMD_NAME << ": success_count="
                               << static_cast<int32_t>(success_count));

    if (failure_count > 0) {
        MGlobal::displayWarning(
            CMD_NAME ": Failed to calculate statistics for some curves.");
    }
    if (success_count == 0) {
        MGlobal::displayError(
            CMD_NAME ": Failed to calculate statistics for all curves.");
        return MS::kFailure;
    }

    // Return calculated statistics from the command.
    MPxCommand::setResult(result);

    return MS::kSuccess;
}

}  // namespace mmsolver
