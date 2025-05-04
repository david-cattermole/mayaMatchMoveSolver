/*
 * Copyright (C) 2022 David Cattermole.
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
 * Set data on Marker Maya nodes.
 */

#include "adjust_results_setMarkerData.h"

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MDGModifier.h>
#include <maya/MObject.h>
#include <maya/MString.h>

// MM Solver
#include "adjust_data.h"
#include "adjust_results.h"
#include "adjust_results_helpers.h"
#include "mmSolver/mayahelper/maya_marker_list.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

MStatus setErrorMetricsResultDataOnMarkers(ErrorMetricsResult &results,
                                           MarkerList &markerList,
                                           MDGModifier &dgmod,
                                           MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;

    const char *deviation_attr_name = "deviation";
    const char *deviation_avg_attr_name = "averageDeviation";
    const char *deviation_max_attr_name = "maximumDeviation";
    const char *deviation_max_frame_attr_name = "maximumDeviationFrame";

    for (MarkerIndex markerIndex = 0; markerIndex < markerList.size();
         ++markerIndex) {
        MarkerPtr marker = markerList.get_marker(markerIndex);
        MObject marker_obj = marker->getObject();

        const MString marker_node_name = marker->getNodeName();
        const char *marker_name = marker_node_name.asChar();

        const auto search =
            results.error_per_marker_per_frame.find(marker_name);
        if (search != results.error_per_marker_per_frame.end()) {
            auto map = search->second;

            status = create_deviation_attrs_on_node(
                marker_obj, map, deviation_attr_name, deviation_avg_attr_name,
                deviation_max_attr_name, deviation_max_frame_attr_name, dgmod,
                curveChange);
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }

    return status;
}

}  // namespace mmsolver
