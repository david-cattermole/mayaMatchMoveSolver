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
 * TODO: Add a "input curves" flag, that will allow the command to
 *       operate on the given animCurve nodes, but output to the
 *       "selection list" objects given. This will allows us to sample
 *       one curve, and output to another.
 *
 *       Example usage (Python):
 *       maya.cmds.mmAnimCurveSimplify(
 *           "outputAnimCurve",
 *           inputCurves="inputAnimCurve",
 *           controlPointCount=5,
 *           distribution="uniform",
 *           interpolation="linear",
 *       )
 *
 */

#include "MMAnimCurveSimplifyCmd.h"

// STL
#include <limits>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MDoubleArray.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MSyntax.h>
#include <maya/MTime.h>
#include <maya/MTypes.h>

// MM Solver Libs
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

// MM Solver
#include "mmSolver/cmd/anim_curve_cmd_utils.h"
#include "mmSolver/core/frame.h"
#include "mmSolver/core/types.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"

#define START_FRAME_FLAG_SHORT "-sf"
#define START_FRAME_FLAG_LONG "-startFrame"

#define END_FRAME_FLAG_SHORT "-ef"
#define END_FRAME_FLAG_LONG "-endFrame"

// How many points to use for the simplified animation curve?
#define CONTROL_POINT_COUNT_FLAG_SHORT "-cpc"
#define CONTROL_POINT_COUNT_FLAG_LONG "-controlPointCount"

// The type of distribution of control points that is used for the
// simplification.
#define DISTRIBUTION_FLAG_SHORT "-dtr"
#define DISTRIBUTION_FLAG_LONG "-distribution"

// Possible values for the 'distribution' flag.
#define CONTROL_POINT_DISTRIBUTION_VALUE_UNIFORM "uniform"
#define CONTROL_POINT_DISTRIBUTION_VALUE_AUTO_KEYPOINTS "auto_keypoints"

// The type of interpolation that is used for the simplification.
#define INTERPOLATION_FLAG_SHORT "-int"
#define INTERPOLATION_FLAG_LONG "-interpolation"

// Possible values for the 'interpolation' flag.
#define INTERPOLATION_VALUE_LINEAR "linear"
#define INTERPOLATION_VALUE_QUADRATIC_NUBS "quadratic_nubs"
#define INTERPOLATION_VALUE_CUBIC_NUBS "cubic_nubs"
#define INTERPOLATION_VALUE_CUBIC_SPLINE "cubic_spline"

// When true, don't modify the animCurve, just return the
// results. This allows users to analyse the anim curve but process
// the output in Python.
#define RETURN_RESULT_ONLY_FLAG_SHORT "-rro"
#define RETURN_RESULT_ONLY_FLAG_LONG "-returnResultOnly"

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

    MMSOLVER_CHECK_MSTATUS(syntax.addFlag(
        START_FRAME_FLAG_SHORT, START_FRAME_FLAG_LONG, MSyntax::kUnsigned));
    MMSOLVER_CHECK_MSTATUS(syntax.addFlag(
        END_FRAME_FLAG_SHORT, END_FRAME_FLAG_LONG, MSyntax::kUnsigned));

    MMSOLVER_CHECK_MSTATUS(syntax.addFlag(CONTROL_POINT_COUNT_FLAG_SHORT,
                                          CONTROL_POINT_COUNT_FLAG_LONG,
                                          MSyntax::kUnsigned));

    MMSOLVER_CHECK_MSTATUS(syntax.addFlag(
        DISTRIBUTION_FLAG_SHORT, DISTRIBUTION_FLAG_LONG, MSyntax::kString));

    MMSOLVER_CHECK_MSTATUS(syntax.addFlag(
        INTERPOLATION_FLAG_SHORT, INTERPOLATION_FLAG_LONG, MSyntax::kString));

    MMSOLVER_CHECK_MSTATUS(syntax.addFlag(RETURN_RESULT_ONLY_FLAG_SHORT,
                                          RETURN_RESULT_ONLY_FLAG_LONG,
                                          MSyntax::kBoolean));

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
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get animation curve from selection.
    status = argData.getObjects(m_selection);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    if (m_selection.length() == 0) {
        MGlobal::displayError(CMD_NAME
                              ": Please select at least one animation curve.");
        return MS::kFailure;
    }

    // To make sure that if any node is invalid, we catch it here, and
    // not during 'doIt'.
    for (auto i = 0; i < m_selection.length(); i++) {
        status = m_selection.getDependNode(i, m_animCurveObj);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

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

    if (argData.isFlagSet(CONTROL_POINT_COUNT_FLAG_SHORT)) {
        uint32_t value = 0;
        status =
            argData.getFlagArgument(CONTROL_POINT_COUNT_FLAG_SHORT, 0, value);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        // Largest number of keypoints that can be used.
        const uint32_t keypoint_count_max = 255;

        if (value > keypoint_count_max) {
            MMSOLVER_MAYA_WRN(CMD_NAME
                              << ": " << CONTROL_POINT_COUNT_FLAG_LONG << "("
                              << CONTROL_POINT_COUNT_FLAG_SHORT
                              << ") flag value is too high, clamping value to "
                              << keypoint_count_max << "; value=" << value);
            value = keypoint_count_max;
        }
        m_controlPointCount = static_cast<uint8_t>(value);
    } else {
        MMSOLVER_MAYA_ERR(CMD_NAME << ": " << CONTROL_POINT_COUNT_FLAG_LONG
                                   << "(" << CONTROL_POINT_COUNT_FLAG_SHORT
                                   << ") flag must be given.");
        status = MS::kFailure;
    }

    if (argData.isFlagSet(RETURN_RESULT_ONLY_FLAG_SHORT)) {
        bool value = false;
        status =
            argData.getFlagArgument(RETURN_RESULT_ONLY_FLAG_SHORT, 0, value);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        m_returnResultOnly = value;
    }

    m_interpolation = mmsg::Interpolation::kUnknown;
    if (argData.isFlagSet(INTERPOLATION_FLAG_SHORT)) {
        MString value = "";
        status = argData.getFlagArgument(INTERPOLATION_FLAG_SHORT, 0, value);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        if (value == INTERPOLATION_VALUE_LINEAR) {
            m_interpolation = mmsg::Interpolation::kLinear;
        } else if (value == INTERPOLATION_VALUE_QUADRATIC_NUBS) {
            m_interpolation = mmsg::Interpolation::kQuadraticNUBS;
        } else if (value == INTERPOLATION_VALUE_CUBIC_NUBS) {
            m_interpolation = mmsg::Interpolation::kCubicNUBS;
        } else if (value == INTERPOLATION_VALUE_CUBIC_SPLINE) {
            m_interpolation = mmsg::Interpolation::kCubicSpline;
        } else {
            MMSOLVER_MAYA_ERR(CMD_NAME << ": Method value is invalid: "
                                       << "method=" << value.asChar());
            status = MS::kFailure;
        }
    } else {
        MMSOLVER_MAYA_ERR(CMD_NAME << ": " << INTERPOLATION_FLAG_LONG << "("
                                   << INTERPOLATION_FLAG_SHORT
                                   << ") flag must be given.");
        return MS::kFailure;
    }

    if (m_interpolation == mmsg::Interpolation::kLinear) {
        if (m_controlPointCount < 2) {
            MMSOLVER_MAYA_ERR(CMD_NAME
                              << ": keypoint count is below minimum (2)"
                                 " for Linear interpolation method.");
            return MS::kFailure;
        }
    } else if (m_interpolation == mmsg::Interpolation::kQuadraticNUBS) {
        if (m_controlPointCount < 3) {
            MMSOLVER_MAYA_ERR(CMD_NAME
                              << ": keypoint count is below minimum (3)"
                                 " for Quadratic NUBS interpolation method.");
            return MS::kFailure;
        }
    } else if (m_interpolation == mmsg::Interpolation::kCubicNUBS) {
        if (m_controlPointCount < 4) {
            MMSOLVER_MAYA_ERR(CMD_NAME
                              << ": keypoint count is below minimum (4)"
                                 " for Cubic NURB interpolation method.");
            return MS::kFailure;
        }
    } else if (m_interpolation == mmsg::Interpolation::kCubicSpline) {
        if (m_controlPointCount < 3) {
            MMSOLVER_MAYA_ERR(CMD_NAME
                              << ": keypoint count is below minimum (3)"
                                 " for Cubic Spline interpolation method.");
            return MS::kFailure;
        }
    }

    m_distribution = mmsg::ControlPointDistribution::kUniform;
    if (argData.isFlagSet(DISTRIBUTION_FLAG_SHORT)) {
        MString value = "";
        status = argData.getFlagArgument(DISTRIBUTION_FLAG_SHORT, 0, value);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
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
    const auto frame_count = static_cast<size_t>(m_endFrame - m_startFrame) + 1;
    MMSOLVER_MAYA_VRB(CMD_NAME << ": frame_count=" << frame_count);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_selection.length()="
                               << m_selection.length());

    rust::Vec<mmsg::Real> values_x;
    rust::Vec<mmsg::Real> values_y;
    values_x.reserve(frame_count);
    values_y.reserve(frame_count);

    rust::Vec<mmsg::Real> out_values_x;
    rust::Vec<mmsg::Real> out_values_y;
    MDoubleArray result;

    const auto time_unit = MTime::uiUnit();
    Count32 success_count = 0;
    Count32 failure_count = 0;
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

        FrameNumber start_frame = 0;
        FrameNumber end_frame = 0;
        const FrameCount min_keyframe_count = 2;
        const FrameCount min_frame_count = 2;
        const char *cmd_name = CMD_NAME;
        bool success = validate_anim_curve(
            cmd_name, m_startFrame, m_endFrame, min_keyframe_count,
            min_frame_count, m_animCurveFn, start_frame, end_frame);
        if (!success) {
            MGlobal::displayWarning(CMD_NAME
                                    ": Failed to validate animation curve.");
            failure_count++;
            continue;
        }

        status = evaluate_curve(start_frame, end_frame, time_unit,
                                m_animCurveFn, values_x, values_y);
        if (status != MS::kSuccess) {
            MGlobal::displayWarning(
                CMD_NAME ": Failed to set animation curve keyframes.");
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
                          << static_cast<Count32>(m_controlPointCount));

        rust::Slice<const mmsg::Real> values_slice_x{values_x.data(),
                                                     values_x.size()};
        rust::Slice<const mmsg::Real> values_slice_y{values_y.data(),
                                                     values_y.size()};
        success = mmsg::curve_simplify(
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
        if (m_returnResultOnly) {
            append_curve_values_to_command_result(out_values_slice_x,
                                                  out_values_slice_y, result);
        } else {
            // Modify the animation curve.
            const bool preserve_first_last_keys = true;
            status = set_anim_curve_keys(
                cmd_name, out_values_slice_x, out_values_slice_y, time_unit,
                m_animCurveFn, m_curveChange, start_frame, end_frame,
                preserve_first_last_keys);
            if (status != MS::kSuccess) {
                MGlobal::displayWarning(
                    CMD_NAME ": Failed to set animation curve keyframes.");
                failure_count++;
                continue;
            }
        }

        success_count++;
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": failure_count="
                               << static_cast<Count32>(failure_count));
    MMSOLVER_MAYA_VRB(CMD_NAME << ": success_count="
                               << static_cast<Count32>(success_count));
    if (failure_count > 0) {
        MGlobal::displayError(CMD_NAME
                              ": Failed to simplify on animation curves.");
    }
    if (success_count == 0) {
        status = MS::kFailure;
        return status;
    }

    if (m_returnResultOnly) {
        // Return calculated values from the command.
        MPxCommand::setResult(result);
    } else {
        // Modify the animation curve.
        m_dgmod.doIt();
    }
    return status;
}

MStatus MMAnimCurveSimplifyCmd::redoIt() {
    MStatus status = MS::kSuccess;
    if (!m_returnResultOnly) {
        status = m_dgmod.doIt();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        status = m_curveChange.redoIt();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus MMAnimCurveSimplifyCmd::undoIt() {
    MStatus status = MS::kSuccess;
    if (!m_returnResultOnly) {
        status = m_curveChange.undoIt();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        status = m_dgmod.undoIt();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

}  // namespace mmsolver
