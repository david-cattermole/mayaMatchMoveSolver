/*
 * Copyright (C) 2024 David Cattermole.
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
 * 'mmAnimCurveFilterPops' Maya command.
 *
 */

#include "MMAnimCurveFilterPopsCmd.h"

// STL
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

#define THRESHOLD_FLAG_SHORT "-th"
#define THRESHOLD_FLAG_LONG "-threshold"

// When true, don't modify the animCurve, just return the results.
#define RETURN_RESULT_ONLY_FLAG_SHORT "-rro"
#define RETURN_RESULT_ONLY_FLAG_LONG "-returnResultOnly"

#define CMD_NAME "mmAnimCurveFilterPops"

namespace mmsg = mmscenegraph;

namespace mmsolver {

MMAnimCurveFilterPopsCmd::~MMAnimCurveFilterPopsCmd() {}

void *MMAnimCurveFilterPopsCmd::creator() {
    return new MMAnimCurveFilterPopsCmd();
}

MString MMAnimCurveFilterPopsCmd::cmdName() { return MString(CMD_NAME); }

bool MMAnimCurveFilterPopsCmd::hasSyntax() const { return true; }

bool MMAnimCurveFilterPopsCmd::isUndoable() const { return true; }

MSyntax MMAnimCurveFilterPopsCmd::newSyntax() {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(CMD_NAME << ": newSyntax");

    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(START_FRAME_FLAG_SHORT, START_FRAME_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(END_FRAME_FLAG_SHORT, END_FRAME_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(THRESHOLD_FLAG_SHORT, THRESHOLD_FLAG_LONG, MSyntax::kDouble);
    // TODO: Add an option to 'infill' the pops.

    MMSOLVER_CHECK_MSTATUS(syntax.addFlag(RETURN_RESULT_ONLY_FLAG_SHORT,
                                          RETURN_RESULT_ONLY_FLAG_LONG,
                                          MSyntax::kBoolean));

    // Add object argument for animation curve
    const unsigned int min_curves = 1;
    syntax.setObjectType(MSyntax::kSelectionList, min_curves);
    syntax.useSelectionAsDefault(true);

    return syntax;
}

MStatus MMAnimCurveFilterPopsCmd::parseArgs(const MArgList &args) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(CMD_NAME << ": parseArgs");

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

    if (argData.isFlagSet(RETURN_RESULT_ONLY_FLAG_SHORT)) {
        bool value = false;
        status =
            argData.getFlagArgument(RETURN_RESULT_ONLY_FLAG_SHORT, 0, value);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        m_returnResultOnly = value;
    }

    // Parse optional arguments
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

    if (argData.isFlagSet(THRESHOLD_FLAG_SHORT)) {
        status = argData.getFlagArgument(THRESHOLD_FLAG_SHORT, 0, m_threshold);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_startFrame=" << m_startFrame);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_endFrame=" << m_endFrame);
    MMSOLVER_MAYA_VRB(CMD_NAME << ": m_threshold=" << m_threshold);

    if (m_threshold < 0.0) {
        MGlobal::displayError(CMD_NAME ": Threshold value is less than 0.0.");
        return MS::kFailure;
    }

    return status;
}

MStatus MMAnimCurveFilterPopsCmd::doIt(const MArgList &args) {
    const bool verbose = false;

    MStatus status = parseArgs(args);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Don't store each individual edit, just store the combination.
    m_curveChange.setInteractive(true);

    const auto count = static_cast<size_t>(m_endFrame - m_startFrame) + 1;
    MMSOLVER_MAYA_VRB(CMD_NAME << ": count=" << count);

    rust::Vec<mmsg::Real> values_x;
    rust::Vec<mmsg::Real> values_y;
    values_x.reserve(count);
    values_y.reserve(count);

    rust::Vec<mmsg::Real> out_values_x;
    rust::Vec<mmsg::Real> out_values_y;
    MDoubleArray result;

    auto time_unit = MTime::uiUnit();
    uint32_t success_count = 0;
    uint32_t failure_count = 0;
    for (auto i = 0; i < m_selection.length(); i++) {
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
                                    ": failed to validate animation curve.");
            failure_count++;
            continue;
        }

        status = evaluate_curve(start_frame, end_frame, time_unit,
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

        // TODO: Can we 'calc_signal_to_noise_ratio', so we can determine
        // if a pop-detection is actually needed?

        MMSOLVER_MAYA_VRB(CMD_NAME << ": m_threshold=" << m_threshold);
        rust::Slice<const mmsg::Real> values_slice_x{values_x.data(),
                                                     values_x.size()};
        rust::Slice<const mmsg::Real> values_slice_y{values_y.data(),
                                                     values_y.size()};
        success =
            mmsg::filter_curve_pops(values_slice_x, values_slice_y, m_threshold,
                                    out_values_x, out_values_y);
        if (!success) {
            MGlobal::displayWarning(CMD_NAME ": failed to detect curve pops.");
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
                    CMD_NAME ": failed to set animation curve keyframes.");
                failure_count++;
                continue;
            }
        }

        success_count++;
    }

    MMSOLVER_MAYA_VRB(CMD_NAME << ": failure_count="
                               << static_cast<int32_t>(failure_count));
    MMSOLVER_MAYA_VRB(CMD_NAME << ": success_count="
                               << static_cast<int32_t>(success_count));
    if (failure_count > 0) {
        MGlobal::displayError(CMD_NAME
                              ": failed to filter pops on animation curves.");
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

MStatus MMAnimCurveFilterPopsCmd::redoIt() {
    MStatus status = MS::kSuccess;
    if (!m_returnResultOnly) {
        status = m_dgmod.doIt();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        status = m_curveChange.redoIt();
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    return status;
}

MStatus MMAnimCurveFilterPopsCmd::undoIt() {
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
