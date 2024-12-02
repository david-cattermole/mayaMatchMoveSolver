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
#include <cassert>
#include <cmath>
#include <cstring>
#include <vector>

// Maya
#include <maya/MAnimUtil.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MGlobal.h>
#include <maya/MSelectionList.h>
#include <maya/MStreamUtils.h>
#include <maya/MSyntax.h>

// MM Solver
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

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

namespace mmsg = mmscenegraph;

namespace mmsolver {

MMAnimCurveFilterPopsCmd::~MMAnimCurveFilterPopsCmd() {}

void *MMAnimCurveFilterPopsCmd::creator() {
    return new MMAnimCurveFilterPopsCmd();
}

MString MMAnimCurveFilterPopsCmd::cmdName() {
    return MString("mmAnimCurveFilterPops");
}

bool MMAnimCurveFilterPopsCmd::hasSyntax() const { return true; }

bool MMAnimCurveFilterPopsCmd::isUndoable() const { return true; }

MSyntax MMAnimCurveFilterPopsCmd::newSyntax() {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("MMAnimCurveFilterPopsCmd::newSyntax");

    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(START_FRAME_FLAG_SHORT, START_FRAME_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(END_FRAME_FLAG_SHORT, END_FRAME_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(THRESHOLD_FLAG_SHORT, THRESHOLD_FLAG_LONG, MSyntax::kDouble);
    // TODO: Add an option to 'infill' the pops.

    // Add object argument for animation curve
    syntax.setObjectType(MSyntax::kSelectionList, 1, 1);
    syntax.useSelectionAsDefault(true);

    return syntax;
}

MStatus MMAnimCurveFilterPopsCmd::parseArgs(const MArgList &args) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("MMAnimCurveFilterPopsCmd::parseArgs");

    MStatus status = MStatus::kSuccess;
    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get animation curve from selection
    MSelectionList selection;
    status = argData.getObjects(selection);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (selection.length() == 0) {
        MGlobal::displayError("Please select at least one animation curve.");
        return MS::kFailure;
    }

    status = selection.getDependNode(0, m_animCurveObj);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = m_animCurveFn.setObject(m_animCurveObj);
    if (status != MS::kSuccess) {
        MGlobal::displayError("Selected object is not an animation curve.");
        return status;
    }

    // Parse optional arguments
    if (argData.isFlagSet(START_FRAME_FLAG_SHORT)) {
        status =
            argData.getFlagArgument(START_FRAME_FLAG_SHORT, 0, m_startFrame);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        m_startFrame = m_animCurveFn.time(0).value();
    }

    if (argData.isFlagSet(END_FRAME_FLAG_SHORT)) {
        status = argData.getFlagArgument(END_FRAME_FLAG_SHORT, 0, m_endFrame);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        auto last_key_index = m_animCurveFn.numKeys() - 1;
        m_endFrame = m_animCurveFn.time(last_key_index).value();
    }

    if (argData.isFlagSet(THRESHOLD_FLAG_SHORT)) {
        status = argData.getFlagArgument(THRESHOLD_FLAG_SHORT, 0, m_threshold);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (verbose) {
        MMSOLVER_MAYA_VRB(
            "MMAnimCurveFilterPopsCmd::m_startFrame=" << m_startFrame);
        MMSOLVER_MAYA_VRB(
            "MMAnimCurveFilterPopsCmd::m_endFrame=" << m_endFrame);
        MMSOLVER_MAYA_VRB(
            "MMAnimCurveFilterPopsCmd::m_threshold=" << m_threshold);
    }

    return status;
}

MStatus MMAnimCurveFilterPopsCmd::doIt(const MArgList &args) {
    const bool verbose = false;

    MStatus status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Don't store each individual edit, just store the combination.
    m_curveChange.setInteractive(true);

    auto count = static_cast<size_t>((m_endFrame - m_startFrame) / 1.0);

    rust::Vec<mmsg::Real> x_values;
    rust::Vec<mmsg::Real> y_values;
    x_values.reserve(count);
    y_values.reserve(count);

    auto time_unit = MTime::uiUnit();
    for (auto frame = m_startFrame; frame <= m_endFrame; frame += 1.0) {
        auto time = MTime(frame, time_unit);
        auto value = m_animCurveFn.evaluate(time, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMSOLVER_MAYA_VRB("f=" << frame << " v=" << value);

        x_values.push_back(frame);
        y_values.push_back(value);
    }

    MMSOLVER_MAYA_VRB("In curve: " << x_values.size() << " | "
                                   << y_values.size());

    auto actual_count = x_values.size();
    rust::Vec<mmsg::Real> filtered_x_values;
    rust::Vec<mmsg::Real> filtered_y_values;
    filtered_x_values.reserve(actual_count);
    filtered_y_values.reserve(actual_count);

    MMSOLVER_MAYA_VRB("m_threshold: " << m_threshold);
    rust::Slice<const mmsg::Real> x_values_slice{x_values.data(),
                                                 x_values.size()};
    rust::Slice<const mmsg::Real> y_values_slice{y_values.data(),
                                                 y_values.size()};
    mmsg::filter_curve_pops(x_values_slice, y_values_slice, m_threshold,
                            filtered_x_values, filtered_y_values);

    // Clear all keys from the anim curve.
    //
    // TODO: Only keyframes between (and including) the start frame
    // and end frame should be removed.
    auto num_keys = m_animCurveFn.numKeys();
    MMSOLVER_MAYA_VRB("num_keys=" << num_keys);
    for (auto i = 0; i < num_keys; i++) {
        m_animCurveFn.remove(0, &m_curveChange);
    }

    MMSOLVER_MAYA_VRB("Filtered curve: " << filtered_x_values.size() << " | "
                                         << filtered_y_values.size());
    const auto tangent_in_type = MFnAnimCurve::TangentType::kTangentGlobal;
    const auto tangent_out_type = MFnAnimCurve::TangentType::kTangentGlobal;
    for (auto i = 0; i < filtered_x_values.size(); i++) {
        auto frame = filtered_x_values[i];
        auto value = filtered_y_values[i];
        MMSOLVER_MAYA_VRB("f=" << frame << " v=" << value);

        auto time = MTime(frame, time_unit);

        uint32_t key_index = 0;
        const bool found = m_animCurveFn.find(time, key_index, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (found) {
            status = m_animCurveFn.setValue(key_index, value, &m_curveChange);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        } else {
            key_index =
                m_animCurveFn.addKey(time, value, tangent_in_type,
                                     tangent_out_type, &m_curveChange, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }

    m_dgmod.doIt();
    return status;
}

MStatus MMAnimCurveFilterPopsCmd::redoIt() {
    MStatus status = m_dgmod.doIt();
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = m_curveChange.redoIt();
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus MMAnimCurveFilterPopsCmd::undoIt() {
    MStatus status = m_curveChange.undoIt();
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = m_dgmod.undoIt();
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

}  // namespace mmsolver
