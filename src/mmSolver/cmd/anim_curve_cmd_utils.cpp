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
 *
 */

#include "anim_curve_cmd_utils.h"

// STL
#include <cmath>
#include <cstring>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MAnimUtil.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MGlobal.h>
#include <maya/MTime.h>

// MM Solver Libs
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

// MM Solver
#include "mmSolver/utilities/debug_utils.h"

// MM Scene Graph
#include "mmscenegraph/mmscenegraph.h"

namespace mmsg = mmscenegraph;

namespace mmsolver {

MStatus evaluate_curve(const FrameNumber start_frame,
                       const FrameNumber end_frame,
                       const MTime::Unit &time_unit,
                       MFnAnimCurve &anim_curve_fn,
                       rust::Vec<mmsg::Real> &out_values_x,
                       rust::Vec<mmsg::Real> &out_values_y) {
    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    MStatus status = MStatus::kSuccess;

    auto frame_count = static_cast<size_t>(end_frame - start_frame) + 1;
    out_values_x.clear();
    out_values_y.clear();
    out_values_x.reserve(frame_count);
    out_values_y.reserve(frame_count);

    for (auto frame = start_frame; frame <= end_frame; frame += 1.0) {
        auto time = MTime(frame, time_unit);
        auto value = anim_curve_fn.evaluate(time, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        MMSOLVER_MAYA_VRB("anim_curve_cmd_utils::evaluate_curve: f="
                          << frame << " v=" << value);

        out_values_x.push_back(frame);
        out_values_y.push_back(value);
    }

    return status;
}

const MStatus set_anim_curve_keys(rust::Slice<const mmsg::Real> &values_x,
                                  rust::Slice<const mmsg::Real> &values_y,
                                  const MTime::Unit &time_unit,
                                  MFnAnimCurve &anim_curve_fn,
                                  MAnimCurveChange &curve_change) {
    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    MStatus status = MStatus::kSuccess;

    // Clear all keys from the anim curve.
    //
    // TODO: Only keyframes between (and including) the start frame
    // and end frame should be removed.
    auto num_keys = anim_curve_fn.numKeys();
    MMSOLVER_MAYA_VRB(
        "anim_curve_cmd_utils::set_anim_curve_keys: "
        "num_keys="
        << num_keys);
    for (auto i = 0; i < num_keys; i++) {
        anim_curve_fn.remove(0, &curve_change);
    }

    MMSOLVER_MAYA_VRB(
        "anim_curve_cmd_utils::set_anim_curve_keys: "
        "curve data size: "
        << values_x.size() << " | " << values_y.size());
    const auto tangent_in_type = MFnAnimCurve::TangentType::kTangentGlobal;
    const auto tangent_out_type = MFnAnimCurve::TangentType::kTangentGlobal;
    for (auto i = 0; i < values_x.size(); i++) {
        const auto frame = values_x[i];
        const auto value = values_y[i];
        MMSOLVER_MAYA_VRB(
            "anim_curve_cmd_utils::set_anim_curve_keys:"
            " f="
            << frame << " v=" << value);

        const auto time = MTime(frame, time_unit);

        uint32_t key_index = 0;
        const bool found = anim_curve_fn.find(time, key_index, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (found) {
            status = anim_curve_fn.setValue(key_index, value, &curve_change);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        } else {
            // TODO: This should use the 'MFnAnimCurve::addKeys()'
            // method, for performance.
            key_index =
                anim_curve_fn.addKey(time, value, tangent_in_type,
                                     tangent_out_type, &curve_change, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }

    return status;
}

}  // namespace mmsolver
