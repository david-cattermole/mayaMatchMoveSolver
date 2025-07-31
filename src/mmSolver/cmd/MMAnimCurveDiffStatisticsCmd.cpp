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
 * 'mmAnimCurveDiffStatistics' Maya command.
 *
 * This command calculates statistical differences between two animation curves.
 */

#include "MMAnimCurveDiffStatisticsCmd.h"

// STL
#include <algorithm>
#include <cmath>
#include <cstring>
#include <vector>

// Maya
#include <maya/MAnimUtil.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
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
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"

// MM Scene Graph
#include "mmscenegraph/mmscenegraph.h"

// Command arguments:
#define START_FRAME_FLAG_SHORT "-sf"
#define START_FRAME_FLAG_LONG "-startFrame"

#define END_FRAME_FLAG_SHORT "-ef"
#define END_FRAME_FLAG_LONG "-endFrame"

#define MEAN_ABSOLUTE_DIFF_FLAG_SHORT "-mad"
#define MEAN_ABSOLUTE_DIFF_FLAG_LONG "-meanAbsoluteDifference"

#define RMS_DIFF_FLAG_SHORT "-rms"
#define RMS_DIFF_FLAG_LONG "-rootMeanSquareDifference"

#define MEAN_DIFF_FLAG_SHORT "-md"
#define MEAN_DIFF_FLAG_LONG "-meanDifference"

#define MEDIAN_DIFF_FLAG_SHORT "-mdd"
#define MEDIAN_DIFF_FLAG_LONG "-medianDifference"

#define VARIANCE_FLAG_SHORT "-var"
#define VARIANCE_FLAG_LONG "-variance"

#define STANDARD_DEVIATION_FLAG_SHORT "-sd"
#define STANDARD_DEVIATION_FLAG_LONG "-standardDeviation"

#define PEAK_TO_PEAK_FLAG_SHORT "-ptp"
#define PEAK_TO_PEAK_FLAG_LONG "-peakToPeak"

#define SIGNAL_TO_NOISE_RATIO_FLAG_SHORT "-snr"
#define SIGNAL_TO_NOISE_RATIO_FLAG_LONG "-signalToNoiseRatio"

#define CMD_NAME "mmAnimCurveDiffStatistics"

// Statistic type identifiers for output
#define STAT_TYPE_MEAN_ABSOLUTE_DIFF 0.0
#define STAT_TYPE_RMS_DIFF 1.0
#define STAT_TYPE_POPULATION_STD_DEV 2.0
#define STAT_TYPE_PEAK_TO_PEAK_DIFF 3.0
#define STAT_TYPE_SIGNAL_TO_NOISE_RATIO 4.0
#define STAT_TYPE_POPULATION_VARIANCE 5.0
#define STAT_TYPE_MEAN_DIFF 6.0
#define STAT_TYPE_MEDIAN_DIFF 7.0

namespace mmsg = mmscenegraph;

namespace mmsolver {

MMAnimCurveDiffStatisticsCmd::~MMAnimCurveDiffStatisticsCmd() {}

void *MMAnimCurveDiffStatisticsCmd::creator() {
    return new MMAnimCurveDiffStatisticsCmd();
}

MString MMAnimCurveDiffStatisticsCmd::cmdName() { return MString(CMD_NAME); }

bool MMAnimCurveDiffStatisticsCmd::hasSyntax() const { return true; }

bool MMAnimCurveDiffStatisticsCmd::isUndoable() const { return false; }

MSyntax MMAnimCurveDiffStatisticsCmd::newSyntax() {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(CMD_NAME << ": newSyntax");

    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(START_FRAME_FLAG_SHORT, START_FRAME_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(END_FRAME_FLAG_SHORT, END_FRAME_FLAG_LONG,
                   MSyntax::kUnsigned);

    // Statistics flags
    syntax.addFlag(MEAN_ABSOLUTE_DIFF_FLAG_SHORT, MEAN_ABSOLUTE_DIFF_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(RMS_DIFF_FLAG_SHORT, RMS_DIFF_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(MEAN_DIFF_FLAG_SHORT, MEAN_DIFF_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(MEDIAN_DIFF_FLAG_SHORT, MEDIAN_DIFF_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(VARIANCE_FLAG_SHORT, VARIANCE_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(STANDARD_DEVIATION_FLAG_SHORT, STANDARD_DEVIATION_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(PEAK_TO_PEAK_FLAG_SHORT, PEAK_TO_PEAK_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(SIGNAL_TO_NOISE_RATIO_FLAG_SHORT,
                   SIGNAL_TO_NOISE_RATIO_FLAG_LONG, MSyntax::kBoolean);

    // Require exactly 2 animation curves
    const unsigned int min_curves = 2;
    const unsigned int max_curves = 2;
    syntax.setObjectType(MSyntax::kSelectionList, min_curves, max_curves);
    syntax.useSelectionAsDefault(true);

    return syntax;
}

MStatus MMAnimCurveDiffStatisticsCmd::parseArgs(const MArgList &args) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(CMD_NAME << ": parseArgs");

    MStatus status = MStatus::kSuccess;
    MArgDatabase argData(syntax(), args, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get animation curves from selection.
    status = argData.getObjects(m_selection);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    if (m_selection.length() != 2) {
        MGlobal::displayError(CMD_NAME
                              ": Please select exactly two animation curves.");
        return MS::kFailure;
    }

    // Validate both curves.
    status = m_selection.getDependNode(0, m_animCurveObj1);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    status = m_selection.getDependNode(1, m_animCurveObj2);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

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
    m_calculateMeanAbsDiff = false;
    m_calculateRmsDiff = false;
    m_calculateMeanDiff = false;
    m_calculateMedianDiff = false;
    m_calculateVariance = false;
    m_calculateStdDev = false;
    m_calculatePeakToPeak = false;
    m_calculateSNR = false;

    if (argData.isFlagSet(MEAN_ABSOLUTE_DIFF_FLAG_SHORT)) {
        status = argData.getFlagArgument(MEAN_ABSOLUTE_DIFF_FLAG_SHORT, 0,
                                         m_calculateMeanAbsDiff);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(RMS_DIFF_FLAG_SHORT)) {
        status =
            argData.getFlagArgument(RMS_DIFF_FLAG_SHORT, 0, m_calculateRmsDiff);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(MEAN_DIFF_FLAG_SHORT)) {
        status = argData.getFlagArgument(MEAN_DIFF_FLAG_SHORT, 0,
                                         m_calculateMeanDiff);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(MEDIAN_DIFF_FLAG_SHORT)) {
        status = argData.getFlagArgument(MEDIAN_DIFF_FLAG_SHORT, 0,
                                         m_calculateMedianDiff);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(VARIANCE_FLAG_SHORT)) {
        status = argData.getFlagArgument(VARIANCE_FLAG_SHORT, 0,
                                         m_calculateVariance);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(STANDARD_DEVIATION_FLAG_SHORT)) {
        status = argData.getFlagArgument(STANDARD_DEVIATION_FLAG_SHORT, 0,
                                         m_calculateStdDev);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(PEAK_TO_PEAK_FLAG_SHORT)) {
        status = argData.getFlagArgument(PEAK_TO_PEAK_FLAG_SHORT, 0,
                                         m_calculatePeakToPeak);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(SIGNAL_TO_NOISE_RATIO_FLAG_SHORT)) {
        status = argData.getFlagArgument(SIGNAL_TO_NOISE_RATIO_FLAG_SHORT, 0,
                                         m_calculateSNR);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // If no flags are set, calculate all statistics by default
    if (!m_calculateMeanAbsDiff && !m_calculateRmsDiff &&
        !m_calculateMeanDiff && !m_calculateMedianDiff &&
        !m_calculateVariance && !m_calculateStdDev && !m_calculatePeakToPeak &&
        !m_calculateSNR) {
        MGlobal::displayError(CMD_NAME
                              ": At least one statistic must be enabled.");
        return MS::kFailure;
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_startFrame=" << m_startFrame);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_endFrame=" << m_endFrame);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateMeanAbsDiff="
                               << m_calculateMeanAbsDiff);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateRmsDiff="
                               << m_calculateRmsDiff);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateMeanDiff="
                               << m_calculateMeanDiff);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateMedianDiff="
                               << m_calculateMedianDiff);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateVariance="
                               << m_calculateVariance);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateStdDev=" << m_calculateStdDev);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculatePeakToPeak="
                               << m_calculatePeakToPeak);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateSNR=" << m_calculateSNR);

    return status;
}

MStatus MMAnimCurveDiffStatisticsCmd::doIt(const MArgList &args) {
    const bool verbose = false;

    MStatus status = parseArgs(args);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Set up the animation curve function objects.
    status = m_animCurveFn1.setObject(m_animCurveObj1);
    if (status != MS::kSuccess) {
        MGlobal::displayError(
            CMD_NAME ": First selected object is not an animation curve.");
        return status;
    }

    status = m_animCurveFn2.setObject(m_animCurveObj2);
    if (status != MS::kSuccess) {
        MGlobal::displayError(
            CMD_NAME ": Second selected object is not an animation curve.");
        return status;
    }

    // Validate both curves and determine frame ranges.
    FrameNumber start_frame1 = 0;
    FrameNumber end_frame1 = 0;
    FrameNumber start_frame2 = 0;
    FrameNumber end_frame2 = 0;
    const FrameCount min_keyframe_count = 2;
    const FrameCount min_frame_count = 2;
    const char *cmd_name = CMD_NAME;

    bool success1 = validate_anim_curve(
        cmd_name, m_startFrame, m_endFrame, min_keyframe_count, min_frame_count,
        m_animCurveFn1, start_frame1, end_frame1);
    if (!success1) {
        MGlobal::displayError(CMD_NAME
                              ": Failed to validate first animation curve.");
        return MS::kFailure;
    }

    bool success2 = validate_anim_curve(
        cmd_name, m_startFrame, m_endFrame, min_keyframe_count, min_frame_count,
        m_animCurveFn2, start_frame2, end_frame2);
    if (!success2) {
        MGlobal::displayError(CMD_NAME
                              ": Failed to validate second animation curve.");
        return MS::kFailure;
    }

    // Use the intersection of both frame ranges.
    FrameNumber start_frame = std::max(start_frame1, start_frame2);
    FrameNumber end_frame = std::min(end_frame1, end_frame2);
    if (start_frame > end_frame) {
        MGlobal::displayError(
            CMD_NAME ": Animation curves have no overlapping frame range.");
        return MS::kFailure;
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": start_frame=" << start_frame);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": end_frame=" << end_frame);

    auto time_unit = MTime::uiUnit();
    auto frame_count = static_cast<size_t>(end_frame - start_frame) + 1;

    // Evaluate both curves.
    rust::Vec<mmsg::Real> values_x1, values_y1;
    rust::Vec<mmsg::Real> values_x2, values_y2;
    values_x1.reserve(frame_count);
    values_y1.reserve(frame_count);
    values_x2.reserve(frame_count);
    values_y2.reserve(frame_count);

    status = evaluate_curve(start_frame, end_frame, time_unit, m_animCurveFn1,
                            values_x1, values_y1);
    if (status != MS::kSuccess) {
        MGlobal::displayError(CMD_NAME
                              ": Failed to evaluate first animation curve.");
        return status;
    }

    status = evaluate_curve(start_frame, end_frame, time_unit, m_animCurveFn2,
                            values_x2, values_y2);
    if (status != MS::kSuccess) {
        MGlobal::displayError(CMD_NAME
                              ": Failed to evaluate second animation curve.");
        return status;
    }

    // Verify we have the same number of values.
    if (values_y1.size() != values_y2.size()) {
        MGlobal::displayError(
            CMD_NAME ": Curves have different number of evaluated points.");
        return MS::kFailure;
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": Evaluated points=" << values_y1.size());

    // Calculate differences between the curves.
    rust::Vec<mmsg::Real> differences;
    rust::Vec<mmsg::Real> absolute_differences;
    differences.reserve(values_y1.size());
    absolute_differences.reserve(values_y1.size());

    // Validate data and compute differences.
    for (size_t i = 0; i < values_y1.size(); ++i) {
        mmsg::Real diff = values_y1[i] - values_y2[i];
        differences.push_back(diff);
        absolute_differences.push_back(std::abs(diff));
    }

    // Create data slices for statistical calculations.
    rust::Slice<const mmsg::Real> diff_slice{differences.data(),
                                             differences.size()};
    rust::Slice<const mmsg::Real> abs_diff_slice{absolute_differences.data(),
                                                 absolute_differences.size()};

    // Output format:
    // [stat_count, statType1, statValue1, statType2, statValue2, ...]
    MDoubleArray result;
    std::vector<std::pair<double, double>> statsResults;

    // Variables to store calculated values that might be reused
    mmsg::Real mean_diff = 0.0;
    mmsg::Real variance_diff = 0.0;
    bool meanCalculated = false;
    bool varianceCalculated = false;

    // Calculate mean absolute difference.
    if (m_calculateMeanAbsDiff) {
        mmsg::Real mean_abs_diff = 0.0;
        mmsg::Real mad = 0.0;
        if (mmsg::calc_mean_absolute_deviation(abs_diff_slice, mean_abs_diff,
                                               mad)) {
            statsResults.push_back(
                {STAT_TYPE_MEAN_ABSOLUTE_DIFF, mean_abs_diff});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": mean_absolute_diff="
                                       << mean_abs_diff);
        } else {
            MGlobal::displayWarning(
                CMD_NAME ": Failed to calculate mean absolute difference.");
        }
    }

    // Calculate mean and variance if needed (they come together)
    if (m_calculateMeanDiff || m_calculateVariance) {
        if (mmsg::calc_population_variance(diff_slice, mean_diff,
                                           variance_diff)) {
            meanCalculated = true;
            varianceCalculated = true;

            if (m_calculateMeanDiff) {
                statsResults.push_back({STAT_TYPE_MEAN_DIFF, mean_diff});
                MMSOLVER_MAYA_VRB(CMD_NAME << ": mean_diff=" << mean_diff);
            }
            if (m_calculateVariance) {
                statsResults.push_back(
                    {STAT_TYPE_POPULATION_VARIANCE, variance_diff});
                MMSOLVER_MAYA_VRB(CMD_NAME << ": population_variance="
                                           << variance_diff);
            }
        } else {
            MGlobal::displayWarning(
                CMD_NAME
                ": Failed to calculate mean and variance of differences.");
        }
    }

    // Calculate population standard deviation.
    if (m_calculateStdDev) {
        if (varianceCalculated) {
            // We already have variance, just calculate std dev from it
            mmsg::Real std_dev_diff = std::sqrt(variance_diff);
            statsResults.push_back(
                {STAT_TYPE_POPULATION_STD_DEV, std_dev_diff});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": population_std_dev="
                                       << std_dev_diff);
        } else {
            // Calculate std dev directly
            mmsg::Real std_dev_diff = 0.0;
            mmsg::Real mean_for_std = 0.0;
            if (mmsg::calc_population_standard_deviation(
                    diff_slice, mean_for_std, std_dev_diff)) {
                statsResults.push_back(
                    {STAT_TYPE_POPULATION_STD_DEV, std_dev_diff});
                MMSOLVER_MAYA_VRB(CMD_NAME << ": population_std_dev="
                                           << std_dev_diff);
                if (!meanCalculated) {
                    mean_diff = mean_for_std;
                    meanCalculated = true;
                }
            } else {
                MGlobal::displayWarning(
                    CMD_NAME
                    ": Failed to calculate population standard deviation.");
            }
        }
    }

    // Calculate Root Mean Square (RMS) of differences.
    if (m_calculateRmsDiff) {
        mmsg::Real rms_diff = 0.0;
        rust::Vec<mmsg::Real> squared_differences;
        squared_differences.reserve(differences.size());
        for (const auto &diff : differences) {
            squared_differences.push_back(diff * diff);
        }
        rust::Slice<const mmsg::Real> squared_diff_slice{
            squared_differences.data(), squared_differences.size()};
        mmsg::Real mean_squared = 0.0;
        mmsg::Real variance_squared = 0.0;
        if (mmsg::calc_population_variance(squared_diff_slice, mean_squared,
                                           variance_squared)) {
            rms_diff = std::sqrt(mean_squared);
            statsResults.push_back({STAT_TYPE_RMS_DIFF, rms_diff});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": rms_diff=" << rms_diff);
        } else {
            MGlobal::displayWarning(CMD_NAME
                                    ": Failed to calculate RMS difference.");
        }
    }

    // Calculate peak-to-peak difference.
    if (m_calculatePeakToPeak) {
        mmsg::Real peak_to_peak_diff = 0.0;
        if (mmsg::calc_peak_to_peak(diff_slice, peak_to_peak_diff)) {
            statsResults.push_back(
                {STAT_TYPE_PEAK_TO_PEAK_DIFF, peak_to_peak_diff});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": peak_to_peak_diff="
                                       << peak_to_peak_diff);
        } else {
            MGlobal::displayWarning(
                CMD_NAME ": Failed to calculate peak-to-peak difference.");
        }
    }

    // Calculate signal-to-noise ratio of differences.
    if (m_calculateSNR) {
        mmsg::Real snr_mean = 0.0;
        mmsg::Real snr = 0.0;
        if (mmsg::calc_signal_to_noise_ratio(diff_slice, snr_mean, snr)) {
            statsResults.push_back({STAT_TYPE_SIGNAL_TO_NOISE_RATIO, snr});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": signal_to_noise_ratio=" << snr);
        } else {
            MGlobal::displayWarning(
                CMD_NAME ": Failed to calculate signal-to-noise ratio.");
        }
    }

    // Calculate median difference (requires sorted data).
    if (m_calculateMedianDiff) {
        rust::Vec<mmsg::Real> sorted_differences = differences;
        std::sort(sorted_differences.begin(), sorted_differences.end());
        rust::Slice<const mmsg::Real> sorted_diff_slice{
            sorted_differences.data(), sorted_differences.size()};
        mmsg::Real q1 = 0.0, q2 = 0.0, q3 = 0.0;
        if (mmsg::calc_quartiles(sorted_diff_slice, q1, q2, q3)) {
            statsResults.push_back({STAT_TYPE_MEDIAN_DIFF, q2});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": median_diff=" << q2);
        } else {
            MGlobal::displayWarning(CMD_NAME
                                    ": Failed to calculate median difference.");
        }
    }

    // Build result array.
    const auto statistics_count = static_cast<double>(statsResults.size());
    result.append(static_cast<double>(statistics_count));

    for (const auto &stat : statsResults) {
        result.append(stat.first);   // stat type
        result.append(stat.second);  // stat value
    }

    MPxCommand::setResult(result);

    return MS::kSuccess;
}

}  // namespace mmsolver
