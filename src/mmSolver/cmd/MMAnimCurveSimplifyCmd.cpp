/*
 * Copyright (C) 2024, 2025 David Cattermole.
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
 * Command for simplifying animation curves.
 *
 * TODO: Add a "return result" flag, that will not modify the actual
 *       animation curves, but will instead output the computed result
 *       in the command's return value. This allows us to analyse the
 *       anim curve but process the output in Python.
 *
 *       Example usage (Python):
 *       result = maya.cmds.mmAnimCurveSimplify(
 *           "outputAnimCurve",
 *           returnResult=True,
 *           controlPointCount=5,
 *           distribution="uniform",
 *           interpolation="linear",
 *       ) or []
 *       keyframe_count = len(result) / 2
 *
 *       # Get X axis values from result.
 *       values_x = []
 *       for i in range(keyframe_count + 1):
 *           values_x.append(result[i])
 *
 *       # Get Y axis values from result.
 *       values_y = []
 *       for i in range(keyframe_count + 1):
 *           index = keyframe_count + i
 *           values_y.append(result[index])
 */

#include "MMAnimCurveSimplifyCmd.h"

// STL
#include <algorithm>
#include <array>
#include <cassert>
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <list>
#include <map>
#include <memory>
#include <string>
#include <thread>
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MEulerRotation.h>
#include <maya/MFnDagNode.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MItSelectionList.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTimeArray.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MTypes.h>

// MM Solver Libs
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

// MM Solver
#include "mmSolver/cmd/anim_curve_cmd_utils.h"
#include "mmSolver/utilities/debug_utils.h"

#define START_FRAME_FLAG_SHORT "-sf"
#define START_FRAME_FLAG_LONG "-startFrame"

#define END_FRAME_FLAG_SHORT "-ef"
#define END_FRAME_FLAG_LONG "-endFrame"

// How many points to use for the simplified animation curve?
#define CONTROL_POINT_COUNT_SHORT_FLAG "-cpc"
#define CONTROL_POINT_COUNT_LONG_FLAG "-controlPointCount"

// The type of distribution of control points that is used for the
// simplification.
#define DISTRIBUTION_SHORT_FLAG "-dtr"
#define DISTRIBUTION_LONG_FLAG "-distribution"

// Possible values for the 'distribution' flag.
#define CONTROL_POINT_DISTRIBUTION_VALUE_UNIFORM "uniform"
#define CONTROL_POINT_DISTRIBUTION_VALUE_AUTO_KEYPOINTS "auto_keypoints"

// The type of interpolation that is used for the simplification.
#define INTERPOLATION_SHORT_FLAG "-int"
#define INTERPOLATION_LONG_FLAG "-interpolation"

// Possible values for the 'interpolation' flag.
#define INTERPOLATION_VALUE_LINEAR "linear"
#define INTERPOLATION_VALUE_CUBIC_NUBS "cubic_nubs"
#define INTERPOLATION_VALUE_CUBIC_SPLINE "cubic_spline"

#define CMD_NAME "mmAnimCurveSimplify"

namespace mmsg = mmscenegraph;

namespace mmsolver {

MMAnimCurveSimplifyCmd::~MMAnimCurveSimplifyCmd() {}

void *MMAnimCurveSimplifyCmd::creator() { return new MMAnimCurveSimplifyCmd(); }

MString MMAnimCurveSimplifyCmd::cmdName() { return MString(CMD_NAME); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMAnimCurveSimplifyCmd::hasSyntax() const { return true; }

bool MMAnimCurveSimplifyCmd::isUndoable() const { return true; }

/*
 * Add flags to the command syntax
 */
MSyntax MMAnimCurveSimplifyCmd::newSyntax() {
    MStatus status = MStatus::kSuccess;

    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    const uint32_t min_object_count = 1;
    syntax.setObjectType(MSyntax::kSelectionList, min_object_count);

    CHECK_MSTATUS(syntax.addFlag(START_FRAME_FLAG_SHORT, START_FRAME_FLAG_LONG,
                                 MSyntax::kUnsigned));
    CHECK_MSTATUS(syntax.addFlag(END_FRAME_FLAG_SHORT, END_FRAME_FLAG_LONG,
                                 MSyntax::kUnsigned));

    CHECK_MSTATUS(syntax.addFlag(CONTROL_POINT_COUNT_SHORT_FLAG,
                                 CONTROL_POINT_COUNT_LONG_FLAG,
                                 MSyntax::kUnsigned));

    CHECK_MSTATUS(syntax.addFlag(DISTRIBUTION_SHORT_FLAG,
                                 DISTRIBUTION_LONG_FLAG, MSyntax::kString));

    CHECK_MSTATUS(syntax.addFlag(INTERPOLATION_SHORT_FLAG,
                                 INTERPOLATION_LONG_FLAG, MSyntax::kString));

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMAnimCurveSimplifyCmd::parseArgs(const MArgList &args) {
    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    MStatus status = MStatus::kSuccess;
    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get animation curve from selection.
    status = argData.getObjects(m_selection);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (m_selection.length() == 0) {
        MGlobal::displayError(CMD_NAME
                              ": Please select at least one animation curve.");
        return MS::kFailure;
    }

    // To make sure that if any node is invalid, we catch it here, and
    // not during 'doIt'.
    for (auto i = 0; i < m_selection.length(); i++) {
        status = m_selection.getDependNode(i, m_animCurveObj);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    m_startFrame = std::numeric_limits<uint32_t>::max();
    m_endFrame = std::numeric_limits<uint32_t>::max();
    if (argData.isFlagSet(START_FRAME_FLAG_SHORT)) {
        status =
            argData.getFlagArgument(START_FRAME_FLAG_SHORT, 0, m_startFrame);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    if (argData.isFlagSet(END_FRAME_FLAG_SHORT)) {
        status = argData.getFlagArgument(END_FRAME_FLAG_SHORT, 0, m_endFrame);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (argData.isFlagSet(CONTROL_POINT_COUNT_SHORT_FLAG)) {
        uint32_t value = 0;
        status =
            argData.getFlagArgument(CONTROL_POINT_COUNT_SHORT_FLAG, 0, value);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Largest number of keypoints that can be used.
        const uint32_t keypoint_count_max = 255;

        if (value > keypoint_count_max) {
            MMSOLVER_MAYA_WRN(CMD_NAME
                              << ": " << CONTROL_POINT_COUNT_LONG_FLAG << "("
                              << CONTROL_POINT_COUNT_SHORT_FLAG
                              << ") flag value is too high, clamping value to "
                              << keypoint_count_max << "; value=" << value);
            value = keypoint_count_max;
        }
        m_controlPointCount = static_cast<uint8_t>(value);
    } else {
        MMSOLVER_MAYA_ERR(CMD_NAME << ": " << CONTROL_POINT_COUNT_LONG_FLAG
                                   << "(" << CONTROL_POINT_COUNT_SHORT_FLAG
                                   << ") flag must be given.");
        status = MS::kFailure;
    }

    m_interpolation = mmsg::InterpolationMethod::kUnknown;
    if (argData.isFlagSet(INTERPOLATION_SHORT_FLAG)) {
        MString value = "";
        status = argData.getFlagArgument(INTERPOLATION_SHORT_FLAG, 0, value);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (value == INTERPOLATION_VALUE_LINEAR) {
            m_interpolation = mmsg::InterpolationMethod::kLinear;
        } else if (value == INTERPOLATION_VALUE_CUBIC_NUBS) {
            m_interpolation = mmsg::InterpolationMethod::kCubicNUBS;
        } else if (value == INTERPOLATION_VALUE_CUBIC_SPLINE) {
            m_interpolation = mmsg::InterpolationMethod::kCubicSpline;
        } else {
            MMSOLVER_MAYA_ERR(CMD_NAME << ": Method value is invalid: "
                                       << "method=" << value.asChar());
            status = MS::kFailure;
        }
    } else {
        MMSOLVER_MAYA_ERR(CMD_NAME << ": " << INTERPOLATION_LONG_FLAG << "("
                                   << INTERPOLATION_SHORT_FLAG
                                   << ") flag must be given.");
        return MS::kFailure;
    }

    if (m_interpolation == mmsg::InterpolationMethod::kLinear) {
        if (m_controlPointCount < 2) {
            MMSOLVER_MAYA_ERR(CMD_NAME
                              << ": keypoint count is below minimum (2)"
                                 " for Linear interpolation method.");
            return MS::kFailure;
        }
    } else if (m_interpolation == mmsg::InterpolationMethod::kCubicNUBS) {
        if (m_controlPointCount < 3) {
            MMSOLVER_MAYA_ERR(CMD_NAME
                              << ": keypoint count is below minimum (3)"
                                 " for Cubic NURB interpolation method.");
            return MS::kFailure;
        }
    } else if (m_interpolation == mmsg::InterpolationMethod::kCubicSpline) {
        if (m_controlPointCount < 3) {
            MMSOLVER_MAYA_ERR(CMD_NAME
                              << ": keypoint count is below minimum (3)"
                                 " for Cubic Spline interpolation method.");
            return MS::kFailure;
        }
    }

    m_distribution = mmsg::ControlPointDistribution::kUniform;
    if (argData.isFlagSet(DISTRIBUTION_SHORT_FLAG)) {
        MString value = "";
        status = argData.getFlagArgument(DISTRIBUTION_SHORT_FLAG, 0, value);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (value == CONTROL_POINT_DISTRIBUTION_VALUE_UNIFORM) {
            m_distribution = mmsg::ControlPointDistribution::kUniform;
        } else if (value == CONTROL_POINT_DISTRIBUTION_VALUE_AUTO_KEYPOINTS) {
            m_distribution = mmsg::ControlPointDistribution::kAutoKeypoints;
        } else {
            MMSOLVER_MAYA_ERR(CMD_NAME << ": Distribution value is invalid: "
                                       << "distribution=" << value.asChar());
            status = MS::kFailure;
        }
    }

    if ((m_startFrame == std::numeric_limits<uint32_t>::max()) &&
        (m_endFrame == std::numeric_limits<uint32_t>::max())) {
        auto uiUnit = MTime::uiUnit();
        m_startTime = MTime(static_cast<double>(m_startFrame), uiUnit);
        m_endTime = MTime(static_cast<double>(m_endFrame), uiUnit);
    }

    return status;
}

MStatus MMAnimCurveSimplifyCmd::doIt(const MArgList &args) {
    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    // Read all the flag arguments.
    MStatus status = parseArgs(args);
    if (status == MStatus::kFailure) {
        return status;
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_startFrame=" << m_startFrame);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_endFrame=" << m_endFrame);
    auto frame_count = static_cast<size_t>(m_endFrame - m_startFrame) + 1;
    MMSOLVER_MAYA_VRB(CMD_NAME << ": frame_count=" << frame_count);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_selection.length()="
                               << m_selection.length());

    rust::Vec<mmsg::Real> values_x;
    rust::Vec<mmsg::Real> values_y;
    values_x.reserve(frame_count);
    values_y.reserve(frame_count);

    rust::Vec<mmsg::Real> out_values_x;
    rust::Vec<mmsg::Real> out_values_y;

    const auto time_unit = MTime::uiUnit();
    uint32_t success_count = 0;
    uint32_t failure_count = 0;
    for (auto i = 0; i < m_selection.length(); i++) {
        MMSOLVER_MAYA_VRB(CMD_NAME << ": i=" << i);

        status = m_selection.getDependNode(i, m_animCurveObj);
        if (status != MS::kSuccess) {
            MGlobal::displayError(
                CMD_NAME ": Selected object is not an animation curve.");
            return status;
        }

        status = m_animCurveFn.setObject(m_animCurveObj);
        if (status != MS::kSuccess) {
            MGlobal::displayError(
                CMD_NAME ": Selected object is not an animation curve.");
            return status;
        }

        status = evaluate_curve(m_startFrame, m_endFrame, time_unit,
                                m_animCurveFn, values_x, values_y);
        if (status != MS::kSuccess) {
            MGlobal::displayWarning(
                CMD_NAME ": failed to set animation curve keyframes.");
            failure_count++;
            continue;
        }

        MMSOLVER_MAYA_VRB(CMD_NAME << ": Input curve size:"
                                      " x="
                                   << values_x.size()
                                   << " y=" << values_y.size());

        auto actual_count = values_x.size();
        MMSOLVER_MAYA_VRB(CMD_NAME << ": actual_count=" << actual_count);
        out_values_x.reserve(actual_count);
        out_values_y.reserve(actual_count);
        out_values_x.clear();
        out_values_y.clear();

        MMSOLVER_MAYA_VRB(CMD_NAME
                          << ": m_controlPointCount="
                          << static_cast<int32_t>(m_controlPointCount));

        rust::Slice<const mmsg::Real> values_slice_x{values_x.data(),
                                                     values_x.size()};
        rust::Slice<const mmsg::Real> values_slice_y{values_y.data(),
                                                     values_y.size()};
        const bool success = mmsg::curve_simplify(
            values_slice_x, values_slice_y, m_controlPointCount, m_distribution,
            m_interpolation, out_values_x, out_values_y);
        if (!success) {
            MGlobal::displayWarning(CMD_NAME
                                    ": curve simplification failed to solve.");
            failure_count++;
            continue;
        }

        rust::Slice<const mmsg::Real> out_values_slice_x{out_values_x.data(),
                                                         out_values_x.size()};
        rust::Slice<const mmsg::Real> out_values_slice_y{out_values_y.data(),
                                                         out_values_y.size()};
        status = set_anim_curve_keys(out_values_slice_x, out_values_slice_y,
                                     time_unit, m_animCurveFn, m_curveChange);
        if (status != MS::kSuccess) {
            MGlobal::displayWarning(
                CMD_NAME ": failed to set animation curve keyframes.");
            failure_count++;
            continue;
        }

        success_count++;
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": failure_count="
                               << static_cast<int32_t>(failure_count));
    MMSOLVER_MAYA_VRB(CMD_NAME << ": success_count="
                               << static_cast<int32_t>(success_count));

    m_dgmod.doIt();
    return status;
}

MStatus MMAnimCurveSimplifyCmd::redoIt() {
    MStatus status;
    m_dgmod.doIt();
    m_curveChange.redoIt();
    return status;
}

MStatus MMAnimCurveSimplifyCmd::undoIt() {
    MStatus status;
    m_curveChange.undoIt();
    m_dgmod.undoIt();
    return status;
}

}  // namespace mmsolver
