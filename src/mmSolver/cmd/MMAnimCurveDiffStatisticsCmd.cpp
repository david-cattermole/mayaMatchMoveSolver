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

#define MEAN_ABSOLUTE_DIFF_FLAG_SHORT "-mad"
#define MEAN_ABSOLUTE_DIFF_FLAG_LONG "-meanAbsoluteDifference"

#define RMS_DIFF_FLAG_SHORT "-rsd"
#define RMS_DIFF_FLAG_LONG "-rootMeanSquareDifference"

#define MEAN_DIFF_FLAG_SHORT "-mnf"
#define MEAN_DIFF_FLAG_LONG "-meanDifference"

#define MEDIAN_DIFF_FLAG_SHORT "-mdf"
#define MEDIAN_DIFF_FLAG_LONG "-medianDifference"

#define POPULATION_VARIANCE_FLAG_SHORT "-pvr"
#define POPULATION_VARIANCE_FLAG_LONG "-populationVariance"

#define POPULATION_STANDARD_DEVIATION_FLAG_SHORT "-psd"
#define POPULATION_STANDARD_DEVIATION_FLAG_LONG "-populationStandardDeviation"

#define PEAK_TO_PEAK_FLAG_SHORT "-ptp"
#define PEAK_TO_PEAK_FLAG_LONG "-peakToPeak"

#define SIGNAL_TO_NOISE_RATIO_FLAG_SHORT "-snr"
#define SIGNAL_TO_NOISE_RATIO_FLAG_LONG "-signalToNoiseRatio"

#define MEAN_ABSOLUTE_ERROR_FLAG_SHORT "-mae"
#define MEAN_ABSOLUTE_ERROR_FLAG_LONG "-meanAbsoluteError"

#define ROOT_MEAN_SQUARE_ERROR_FLAG_SHORT "-rme"
#define ROOT_MEAN_SQUARE_ERROR_FLAG_LONG "-rootMeanSquareError"

#define NORMALIZED_RMSE_FLAG_SHORT "-nse"
#define NORMALIZED_RMSE_FLAG_LONG "-normalizedRootMeanSquareError"

#define R_SQUARED_FLAG_SHORT "-r2"
#define R_SQUARED_FLAG_LONG "-rSquared"

#define X_VALUES_FLAG_SHORT "-xv"
#define X_VALUES_FLAG_LONG "-xValues"

#define Y_VALUES_A_FLAG_SHORT "-yva"
#define Y_VALUES_A_FLAG_LONG "-yValuesA"

#define Y_VALUES_B_FLAG_SHORT "-yvb"
#define Y_VALUES_B_FLAG_LONG "-yValuesB"

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
#define STAT_TYPE_MEAN_ABSOLUTE_ERROR 8.0
#define STAT_TYPE_ROOT_MEAN_SQUARE_ERROR 9.0
#define STAT_TYPE_NORMALIZED_RMSE 10.0
#define STAT_TYPE_R_SQUARED 11.0

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
    syntax.addFlag(POPULATION_VARIANCE_FLAG_SHORT,
                   POPULATION_VARIANCE_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(POPULATION_STANDARD_DEVIATION_FLAG_SHORT,
                   POPULATION_STANDARD_DEVIATION_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(PEAK_TO_PEAK_FLAG_SHORT, PEAK_TO_PEAK_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(SIGNAL_TO_NOISE_RATIO_FLAG_SHORT,
                   SIGNAL_TO_NOISE_RATIO_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(MEAN_ABSOLUTE_ERROR_FLAG_SHORT,
                   MEAN_ABSOLUTE_ERROR_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(ROOT_MEAN_SQUARE_ERROR_FLAG_SHORT,
                   ROOT_MEAN_SQUARE_ERROR_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(NORMALIZED_RMSE_FLAG_SHORT, NORMALIZED_RMSE_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(R_SQUARED_FLAG_SHORT, R_SQUARED_FLAG_LONG,
                   MSyntax::kBoolean);

    // List input flags
    syntax.addFlag(X_VALUES_FLAG_SHORT, X_VALUES_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(Y_VALUES_A_FLAG_SHORT, Y_VALUES_A_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(Y_VALUES_B_FLAG_SHORT, Y_VALUES_B_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.makeFlagMultiUse(X_VALUES_FLAG_SHORT);
    syntax.makeFlagMultiUse(Y_VALUES_A_FLAG_SHORT);
    syntax.makeFlagMultiUse(Y_VALUES_B_FLAG_SHORT);

    // Require 0 to 2 animation curves (0 when using list inputs)
    const unsigned int min_curves = 0;
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

    // Check if list inputs are provided
    bool hasSomeListInputs = argData.isFlagSet(X_VALUES_FLAG_SHORT) ||
                             argData.isFlagSet(Y_VALUES_A_FLAG_SHORT) ||
                             argData.isFlagSet(Y_VALUES_B_FLAG_SHORT);
    bool hasAllListInputs = argData.isFlagSet(X_VALUES_FLAG_SHORT) &&
                            argData.isFlagSet(Y_VALUES_A_FLAG_SHORT) &&
                            argData.isFlagSet(Y_VALUES_B_FLAG_SHORT);

    // All four list flags must be provided, or none at all.
    if (hasSomeListInputs && !hasAllListInputs) {
        MGlobal::displayError(
            CMD_NAME
            ": All list value flags (xValues, yValuesA, yValuesB) must be "
            "provided together, or none at all.");
        return MS::kFailure;
    }

    m_useListInput = false;
    if (hasAllListInputs) {
        m_useListInput = true;

        Count32 xCount = argData.numberOfFlagUses(X_VALUES_FLAG_SHORT);
        Count32 yCount1 = argData.numberOfFlagUses(Y_VALUES_A_FLAG_SHORT);
        Count32 yCount2 = argData.numberOfFlagUses(Y_VALUES_B_FLAG_SHORT);

        // Validate list lengths
        if (xCount != yCount1) {
            MGlobal::displayError(
                CMD_NAME
                ": X and Y value lists for curve 1 must have the same length.");
            return MS::kFailure;
        }

        if (xCount != yCount2) {
            MGlobal::displayError(
                CMD_NAME
                ": X and Y value lists for curve 2 must have the same length.");
            return MS::kFailure;
        }

        if (xCount < 2) {
            MGlobal::displayError(
                CMD_NAME ": Value lists must contain at least 2 values.");
            return MS::kFailure;
        }

        m_xValues.clear();
        m_yValuesA.clear();
        m_yValuesB.clear();

        for (Count32 i = 0; i < xCount; ++i) {
            MArgList xArgList;
            status =
                argData.getFlagArgumentList(X_VALUES_FLAG_SHORT, i, xArgList);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            const double value = xArgList.asDouble(0, &status);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            m_xValues.push_back(value);
        }

        for (Count32 i = 0; i < xCount; ++i) {
            MArgList yArgList1;
            status = argData.getFlagArgumentList(Y_VALUES_A_FLAG_SHORT, i,
                                                 yArgList1);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            const double value = yArgList1.asDouble(0, &status);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            m_yValuesA.push_back(value);
        }

        for (Count32 i = 0; i < xCount; ++i) {
            MArgList yArgList2;
            status = argData.getFlagArgumentList(Y_VALUES_B_FLAG_SHORT, i,
                                                 yArgList2);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            const double value = yArgList2.asDouble(0, &status);
            MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
            m_yValuesB.push_back(value);
        }

    } else {
        // Get animation curves from selection.
        status = argData.getObjects(m_selection);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        if (m_selection.length() != 2) {
            MGlobal::displayError(CMD_NAME
                                  ": Please select exactly two animation "
                                  "curves or provide list values.");
            return MS::kFailure;
        }

        // Validate both curves.
        status = m_selection.getDependNode(0, m_animCurveObj1);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        status = m_selection.getDependNode(1, m_animCurveObj2);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
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
    m_calculateMeanAbsDiff = false;
    m_calculateRmsDiff = false;
    m_calculateMeanDiff = false;
    m_calculateMedianDiff = false;
    m_calculatePopVariance = false;
    m_calculatePopStdDev = false;
    m_calculatePeakToPeak = false;
    m_calculateSNR = false;
    m_calculateMAE = false;
    m_calculateRMSE = false;
    m_calculateNRMSE = false;
    m_calculateR2 = false;

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
    if (argData.isFlagSet(MEAN_ABSOLUTE_ERROR_FLAG_SHORT)) {
        status = argData.getFlagArgument(MEAN_ABSOLUTE_ERROR_FLAG_SHORT, 0,
                                         m_calculateMAE);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(ROOT_MEAN_SQUARE_ERROR_FLAG_SHORT)) {
        status = argData.getFlagArgument(ROOT_MEAN_SQUARE_ERROR_FLAG_SHORT, 0,
                                         m_calculateRMSE);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(NORMALIZED_RMSE_FLAG_SHORT)) {
        status = argData.getFlagArgument(NORMALIZED_RMSE_FLAG_SHORT, 0,
                                         m_calculateNRMSE);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(R_SQUARED_FLAG_SHORT)) {
        status =
            argData.getFlagArgument(R_SQUARED_FLAG_SHORT, 0, m_calculateR2);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // If no flags are set, calculate all statistics by default
    if (!m_calculateMeanAbsDiff && !m_calculateRmsDiff &&
        !m_calculateMeanDiff && !m_calculateMedianDiff &&
        !m_calculatePopVariance && !m_calculatePopStdDev &&
        !m_calculatePeakToPeak && !m_calculateSNR && !m_calculateMAE &&
        !m_calculateRMSE && !m_calculateNRMSE && !m_calculateR2) {
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
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculatePopVariance="
                               << m_calculatePopVariance);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculatePopStdDev="
                               << m_calculatePopStdDev);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculatePeakToPeak="
                               << m_calculatePeakToPeak);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateSNR=" << m_calculateSNR);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateMAE=" << m_calculateMAE);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateRMSE=" << m_calculateRMSE);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateNRMSE=" << m_calculateNRMSE);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_calculateR2=" << m_calculateR2);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_useListInput=" << m_useListInput);

    return status;
}

MStatus MMAnimCurveDiffStatisticsCmd::doIt(const MArgList &args) {
    const bool verbose = false;

    MStatus status = parseArgs(args);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Evaluate both curves.
    rust::Vec<mmsg::Real> values_x1;
    rust::Vec<mmsg::Real> values_y1;
    rust::Vec<mmsg::Real> values_x2;
    rust::Vec<mmsg::Real> values_y2;

    if (m_useListInput) {
        // Use provided list values with interpolation for matching X
        // values.
        values_x1.reserve(m_xValues.size());
        values_y1.reserve(m_xValues.size());
        values_x2.reserve(m_xValues.size());
        values_y2.reserve(m_xValues.size());

        for (auto i = 0; i < m_xValues.size(); i++) {
            values_x1.push_back(m_xValues[i]);
        }

        for (auto i = 0; i < m_yValuesA.size(); i++) {
            values_y1.push_back(m_yValuesA[i]);
        }

        for (auto i = 0; i < m_xValues.size(); i++) {
            values_x2.push_back(m_xValues[i]);
        }

        for (auto i = 0; i < m_yValuesB.size(); i++) {
            values_y2.push_back(m_yValuesB[i]);
        }

    } else {
        // Use animation curves

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
            cmd_name, m_startFrame, m_endFrame, min_keyframe_count,
            min_frame_count, m_animCurveFn1, start_frame1, end_frame1);
        if (!success1) {
            MGlobal::displayError(
                CMD_NAME ": Failed to validate first animation curve.");
            return MS::kFailure;
        }

        bool success2 = validate_anim_curve(
            cmd_name, m_startFrame, m_endFrame, min_keyframe_count,
            min_frame_count, m_animCurveFn2, start_frame2, end_frame2);
        if (!success2) {
            MGlobal::displayError(
                CMD_NAME ": Failed to validate second animation curve.");
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

        values_x1.reserve(frame_count);
        values_y1.reserve(frame_count);
        values_x2.reserve(frame_count);
        values_y2.reserve(frame_count);

        status = evaluate_curve(start_frame, end_frame, time_unit,
                                m_animCurveFn1, values_x1, values_y1);
        if (status != MS::kSuccess) {
            MGlobal::displayError(
                CMD_NAME ": Failed to evaluate first animation curve.");
            return status;
        }

        status = evaluate_curve(start_frame, end_frame, time_unit,
                                m_animCurveFn2, values_x2, values_y2);
        if (status != MS::kSuccess) {
            MGlobal::displayError(
                CMD_NAME ": Failed to evaluate second animation curve.");
            return status;
        }
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
    rust::Slice<const mmsg::Real> values_y1_slice{values_y1.data(),
                                                  values_y1.size()};
    rust::Slice<const mmsg::Real> values_y2_slice{values_y2.data(),
                                                  values_y2.size()};

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
    if (m_calculateMeanDiff || m_calculatePopVariance) {
        if (mmsg::calc_population_variance(diff_slice, mean_diff,
                                           variance_diff)) {
            meanCalculated = true;
            varianceCalculated = true;

            if (m_calculateMeanDiff) {
                statsResults.push_back({STAT_TYPE_MEAN_DIFF, mean_diff});
                MMSOLVER_MAYA_VRB(CMD_NAME << ": mean_diff=" << mean_diff);
            }
            if (m_calculatePopVariance) {
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
    if (m_calculatePopStdDev) {
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

    // Calculate Mean Absolute Error (MAE).
    if (m_calculateMAE) {
        mmsg::Real mae = 0.0;
        if (mmsg::calc_mean_absolute_error(values_y2_slice, values_y1_slice,
                                           mae)) {
            statsResults.push_back({STAT_TYPE_MEAN_ABSOLUTE_ERROR, mae});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": mean_absolute_error=" << mae);
        } else {
            MGlobal::displayWarning(
                CMD_NAME ": Failed to calculate mean absolute error.");
        }
    }

    // Calculate Root Mean Square Error (RMSE).
    if (m_calculateRMSE) {
        mmsg::Real rmse = 0.0;
        if (mmsg::calc_root_mean_square_error(values_y2_slice, values_y1_slice,
                                              rmse)) {
            statsResults.push_back({STAT_TYPE_ROOT_MEAN_SQUARE_ERROR, rmse});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": root_mean_square_error=" << rmse);
        } else {
            MGlobal::displayWarning(
                CMD_NAME ": Failed to calculate root mean square error.");
        }
    }

    // Calculate Normalized Root Mean Square Error (NRMSE).
    if (m_calculateNRMSE) {
        mmsg::Real nrmse = 0.0;
        if (mmsg::calc_normalized_root_mean_square_error(
                values_y2_slice, values_y1_slice, nrmse)) {
            statsResults.push_back({STAT_TYPE_NORMALIZED_RMSE, nrmse});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": normalized_root_mean_square_error="
                                       << nrmse);
        } else {
            MGlobal::displayWarning(
                CMD_NAME
                ": Failed to calculate normalized root mean square error.");
        }
    }

    // Calculate Coefficient of Determination (R^2 also known as "R-squared").
    if (m_calculateR2) {
        mmsg::Real r_squared = 0.0;
        // Note: For R^2, we treat the first curve as "actual" and
        // second as "predicted".
        if (mmsg::calc_coefficient_of_determination(
                values_y1_slice, values_y2_slice, r_squared)) {
            statsResults.push_back({STAT_TYPE_R_SQUARED, r_squared});
            MMSOLVER_MAYA_VRB(CMD_NAME << ": r_squared=" << r_squared);
        } else {
            MGlobal::displayWarning(
                CMD_NAME ": Failed to calculate coefficient of determination.");
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
