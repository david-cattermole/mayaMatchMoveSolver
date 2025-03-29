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
 * Sets solve data onto Maya nodes.
 */

#include "adjust_results_setSolveData.h"

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MDGModifier.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnStringData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>

// MM Solver
#include "adjust_data.h"
#include "adjust_results.h"
#include "adjust_results_helpers.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

MStatus createResultAttr_boolean(const char *attr_name, MObject &node,
                                 MDGModifier &dgmod) {
    MFnNumericAttribute numeric_attr;
    MStatus status = create_numeric_attr(attr_name, node, dgmod, numeric_attr,
                                         MFnNumericData::kBoolean);
    numeric_attr.setKeyable(true);
    numeric_attr.setDefault(true);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus createResultAttr_success(const char *attr_name, MObject &node,
                                 MDGModifier &dgmod) {
    return createResultAttr_boolean(attr_name, node, dgmod);
}

MStatus createResultAttr_reasonNum(const char *attr_name, MObject &node,
                                   MDGModifier &dgmod) {
    MFnNumericAttribute numeric_attr;
    MStatus status = create_numeric_attr(attr_name, node, dgmod, numeric_attr,
                                         MFnNumericData::kLong);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    numeric_attr.setMin(0);
    numeric_attr.setDefault(0);

    return status;
}

MStatus createResultAttr_reasonString(const char *attr_name, MObject &node,
                                      MDGModifier &dgmod) {
    MFnTypedAttribute typedAttr;

    MFnStringData string_data_fn;
    MObject string_default_object = string_data_fn.create("");

    MStatus status =
        create_typed_attr(attr_name, node, dgmod, typedAttr, MFnData::kString);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    typedAttr.setReadable(true);
    typedAttr.setWritable(true);

    return status;
}

MStatus createResultAttr_userInterrupted(const char *attr_name, MObject &node,
                                         MDGModifier &dgmod) {
    return createResultAttr_boolean(attr_name, node, dgmod);
}

MStatus createResultAttr_deviation(const char *attr_name, MObject &node,
                                   MDGModifier &dgmod) {
    MFnNumericAttribute numeric_attr;
    MStatus status = create_numeric_attr(attr_name, node, dgmod, numeric_attr,
                                         MFnNumericData::kDouble);
    numeric_attr.setKeyable(true);
    numeric_attr.setMin(-1.0);
    numeric_attr.setDefault(-1.0);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus createResultAttr_averageDeviation(const char *attr_name, MObject &node,
                                          MDGModifier &dgmod) {
    return createResultAttr_deviation(attr_name, node, dgmod);
}

MStatus createResultAttr_maximumDeviation(const char *attr_name, MObject &node,
                                          MDGModifier &dgmod) {
    return createResultAttr_deviation(attr_name, node, dgmod);
}

MStatus createResultAttr_minimumDeviation(const char *attr_name, MObject &node,
                                          MDGModifier &dgmod) {
    return createResultAttr_deviation(attr_name, node, dgmod);
}

MStatus createResultAttr_maxDeviationFrame(const char *attr_name, MObject &node,
                                           MDGModifier &dgmod) {
    MFnNumericAttribute numeric_attr;
    MStatus status = create_numeric_attr(attr_name, node, dgmod, numeric_attr,
                                         MFnNumericData::kLong);
    numeric_attr.setKeyable(true);
    numeric_attr.setMin(-1);
    numeric_attr.setDefault(-1);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus createResultAttr_objectCount(const char *attr_name, MObject &node,
                                     MDGModifier &dgmod) {
    MFnNumericAttribute numeric_attr;
    MStatus status = create_numeric_attr(attr_name, node, dgmod, numeric_attr,
                                         MFnNumericData::kLong);
    numeric_attr.setMin(0);
    numeric_attr.setDefault(0);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus createResultAttr_iterationNum(const char *attr_name, MObject &node,
                                      MDGModifier &dgmod) {
    return createResultAttr_objectCount(attr_name, node, dgmod);
}

MStatus createResultAttr_iterationFunctionNum(const char *attr_name,
                                              MObject &node,
                                              MDGModifier &dgmod) {
    return createResultAttr_objectCount(attr_name, node, dgmod);
}

MStatus createResultAttr_iterationJacobianNum(const char *attr_name,
                                              MObject &node,
                                              MDGModifier &dgmod) {
    return createResultAttr_objectCount(attr_name, node, dgmod);
}

MStatus setSolverResultDataOnNode(SolverResult &results, MObject &node,
                                  MDGModifier &dgmod,
                                  MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;

    MFnDependencyNode dg_node_fn(node, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    const char *success_attr_name = "success";
    const char *reason_num_attr_name = "reason_num";
    const char *reason_string_attr_name = "reason_string";
    const char *error_final_attr_name = "error_final";
    const char *error_final_avg_attr_name = "error_final_average";
    const char *error_final_max_attr_name = "error_final_maximum";
    const char *error_final_min_attr_name = "error_final_minimum";
    const char *iteration_num_attr_name = "iteration_num";
    const char *iteration_function_num_attr_name = "iteration_function_num";
    const char *iteration_jacobian_num_attr_name = "iteration_jacobian_num";
    const char *user_interrupted_attr_name = "user_interrupted";

    MPlug success_plug;
    MPlug reason_num_plug;
    MPlug reason_string_plug;
    MPlug error_final_plug;
    MPlug error_final_avg_plug;
    MPlug error_final_max_plug;
    MPlug error_final_min_plug;
    MPlug iteration_num_plug;
    MPlug iteration_function_num_plug;
    MPlug iteration_jacobian_num_plug;
    MPlug user_interrupted_plug;

    status = find_plug(success_attr_name, dg_node_fn, success_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(reason_num_attr_name, dg_node_fn, reason_num_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(reason_string_attr_name, dg_node_fn, reason_string_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(error_final_attr_name, dg_node_fn, error_final_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status =
        find_plug(error_final_avg_attr_name, dg_node_fn, error_final_avg_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status =
        find_plug(error_final_max_attr_name, dg_node_fn, error_final_max_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status =
        find_plug(error_final_min_attr_name, dg_node_fn, error_final_min_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(iteration_num_attr_name, dg_node_fn, iteration_num_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(iteration_function_num_attr_name, dg_node_fn,
                       iteration_function_num_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(iteration_jacobian_num_attr_name, dg_node_fn,
                       iteration_jacobian_num_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(user_interrupted_attr_name, dg_node_fn,
                       user_interrupted_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool success_exists = !success_plug.isNull();
    bool reason_num_exists = !reason_num_plug.isNull();
    bool reason_string_exists = !reason_string_plug.isNull();
    bool error_final_exists = !error_final_plug.isNull();
    bool error_final_avg_exists = !error_final_avg_plug.isNull();
    bool error_final_max_exists = !error_final_max_plug.isNull();
    bool error_final_min_exists = !error_final_min_plug.isNull();
    bool iteration_num_exists = !iteration_num_plug.isNull();
    bool iteration_function_num_exists = !iteration_function_num_plug.isNull();
    bool iteration_jacobian_num_exists = !iteration_jacobian_num_plug.isNull();
    bool user_interrupted_exists = !user_interrupted_plug.isNull();

    int created_attrs_count = 0;
    if (!success_exists) {
        status = createResultAttr_success(success_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!reason_num_exists) {
        status = createResultAttr_reasonNum(reason_num_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!reason_string_exists) {
        status =
            createResultAttr_reasonString(reason_string_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!error_final_exists) {
        status = createResultAttr_deviation(error_final_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!error_final_avg_exists) {
        status = createResultAttr_averageDeviation(error_final_avg_attr_name,
                                                   node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!error_final_max_exists) {
        status = createResultAttr_maximumDeviation(error_final_max_attr_name,
                                                   node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!error_final_min_exists) {
        status = createResultAttr_minimumDeviation(error_final_min_attr_name,
                                                   node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!iteration_num_exists) {
        status =
            createResultAttr_iterationNum(iteration_num_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!iteration_function_num_exists) {
        status = createResultAttr_iterationFunctionNum(
            iteration_function_num_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!iteration_jacobian_num_exists) {
        status = createResultAttr_iterationJacobianNum(
            iteration_jacobian_num_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!user_interrupted_exists) {
        status = createResultAttr_userInterrupted(user_interrupted_attr_name,
                                                  node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    // Any non-created attributes need to be created before
    // proceeding.
    if (created_attrs_count > 0) {
        dgmod.doIt();

        if (!success_exists) {
            status = find_plug(success_attr_name, dg_node_fn, success_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            success_exists = !success_plug.isNull();
        }

        if (!reason_num_exists) {
            status =
                find_plug(reason_num_attr_name, dg_node_fn, reason_num_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            reason_num_exists = !reason_num_plug.isNull();
        }

        if (!reason_string_exists) {
            status = find_plug(reason_string_attr_name, dg_node_fn,
                               reason_string_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            reason_string_exists = !reason_string_plug.isNull();
        }

        if (!error_final_exists) {
            status =
                find_plug(error_final_attr_name, dg_node_fn, error_final_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            error_final_exists = !error_final_plug.isNull();
        }

        if (!error_final_avg_exists) {
            status = find_plug(error_final_avg_attr_name, dg_node_fn,
                               error_final_avg_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            error_final_avg_exists = !error_final_avg_plug.isNull();
        }

        if (!error_final_max_exists) {
            status = find_plug(error_final_max_attr_name, dg_node_fn,
                               error_final_max_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            error_final_max_exists = !error_final_max_plug.isNull();
        }

        if (!error_final_min_exists) {
            status = find_plug(error_final_min_attr_name, dg_node_fn,
                               error_final_min_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            error_final_min_exists = !error_final_min_plug.isNull();
        }

        if (!iteration_num_exists) {
            status = find_plug(iteration_num_attr_name, dg_node_fn,
                               iteration_num_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            iteration_num_exists = !iteration_num_plug.isNull();
        }

        if (!iteration_function_num_exists) {
            status = find_plug(iteration_function_num_attr_name, dg_node_fn,
                               iteration_function_num_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            iteration_function_num_exists =
                !iteration_function_num_plug.isNull();
        }

        if (!iteration_jacobian_num_exists) {
            status = find_plug(iteration_jacobian_num_attr_name, dg_node_fn,
                               iteration_jacobian_num_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            iteration_jacobian_num_exists =
                !iteration_jacobian_num_plug.isNull();
        }

        if (!user_interrupted_exists) {
            status = find_plug(user_interrupted_attr_name, dg_node_fn,
                               user_interrupted_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            user_interrupted_exists = !user_interrupted_plug.isNull();
        }
    }

    MMSOLVER_ASSERT(success_exists, "Success flag must be given.");
    MMSOLVER_ASSERT(reason_num_exists, "Reason number flag must be given.");
    MMSOLVER_ASSERT(reason_string_exists, "Reason string flag must be given.");
    MMSOLVER_ASSERT(error_final_exists, "Error final flag must be given.");
    MMSOLVER_ASSERT(error_final_avg_exists,
                    "Error average flag must be given.");
    MMSOLVER_ASSERT(error_final_max_exists,
                    "Error maximum flag must be given.");
    MMSOLVER_ASSERT(error_final_min_exists,
                    "Error minimum flag must be given.");
    MMSOLVER_ASSERT(iteration_num_exists,
                    "Iteration count flag must be given.");
    MMSOLVER_ASSERT(iteration_function_num_exists,
                    "Iteration function count flag must be given.");
    MMSOLVER_ASSERT(iteration_jacobian_num_exists,
                    "Iteration jacobian count flag must be given.");
    MMSOLVER_ASSERT(user_interrupted_exists,
                    "User interrupted flag must be given.");

    dgmod.newPlugValueBool(success_plug, results.success);
    dgmod.newPlugValueInt(reason_num_plug, results.reason_number);
    dgmod.newPlugValueString(reason_string_plug,
                             MString(results.reason.c_str()));
    dgmod.newPlugValueDouble(error_final_plug, results.errorFinal);
    dgmod.newPlugValueDouble(error_final_avg_plug, results.errorAvg);
    dgmod.newPlugValueDouble(error_final_max_plug, results.errorMax);
    dgmod.newPlugValueDouble(error_final_min_plug, results.errorMin);
    dgmod.newPlugValueInt(iteration_num_plug, results.iterations);
    dgmod.newPlugValueInt(iteration_function_num_plug, results.functionEvals);
    dgmod.newPlugValueInt(iteration_jacobian_num_plug, results.jacobianEvals);
    dgmod.newPlugValueBool(user_interrupted_plug, results.user_interrupted);
    dgmod.doIt();

    return status;
}

MStatus setTimerResultDataOnNode(TimerResult &results, MObject &node,
                                 MDGModifier &dgmod,
                                 MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;

    // TODO: Write this.

    return status;
}

MStatus setSolveValuesResultDataOnNode(SolveValuesResult &results,
                                       MObject &node, MDGModifier &dgmod,
                                       MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;

    // TODO: Write this.

    return status;
}

std::string get_short_node_name(const std::string &in_string) {
    const auto start = in_string.rfind('|');
    if (start == -1) {
        return std::string(in_string);
    }
    const auto end = in_string.size();
    return std::string(in_string.substr(start + 1, end));
}

MStatus setErrorMetricsResultDataOnNode(ErrorMetricsResult &results,
                                        MObject &node, MDGModifier &dgmod,
                                        MAnimCurveChange &curveChange) {
    const char *deviation_attr_name = "deviation";
    const char *deviation_avg_attr_name = "average_deviation";
    const char *deviation_max_attr_name = "maximum_deviation";
    const char *deviation_max_frame_attr_name = "maximum_deviation_frame";

    MStatus status = create_deviation_attrs_on_node(
        node, results.error_per_frame, deviation_attr_name,
        deviation_avg_attr_name, deviation_max_attr_name,
        deviation_max_frame_attr_name, dgmod, curveChange);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Set deviation attributes for each for each marker, on the given
    // `node`.
    const char *prefix = "mkr___";
    for (const auto &kv : results.error_per_marker_per_frame) {
        const auto marker_name = get_short_node_name(kv.first);
        const auto map = kv.second;

        // MMSOLVER_MAYA_WRN("results marker name: " << marker_name);
        std::stringstream deviation_ss;
        std::stringstream deviation_avg_ss;
        std::stringstream deviation_max_ss;
        std::stringstream deviation_max_frame_ss;

        deviation_ss << prefix << marker_name << "___" << deviation_attr_name;
        const std::string marker_deviation_attr_name = deviation_ss.str();

        deviation_avg_ss << prefix << marker_name << "___"
                         << deviation_avg_attr_name;
        const std::string marker_deviation_avg_attr_name =
            deviation_avg_ss.str();

        deviation_max_ss << prefix << marker_name << "___"
                         << deviation_max_attr_name;
        const std::string marker_deviation_max_attr_name =
            deviation_max_ss.str();

        deviation_max_frame_ss << prefix << marker_name << "___"
                               << deviation_max_frame_attr_name;
        const std::string marker_deviation_max_frame_attr_name =
            deviation_max_frame_ss.str();

        status = create_deviation_attrs_on_node(
            node, map, marker_deviation_attr_name.c_str(),
            marker_deviation_avg_attr_name.c_str(),
            marker_deviation_max_attr_name.c_str(),
            marker_deviation_max_frame_attr_name.c_str(), dgmod, curveChange);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

MStatus setAffectsResultDataOnNode(AffectsResult &results, MObject &node,
                                   MDGModifier &dgmod,
                                   MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;

    // TODO: Write this.

    return status;
}

MStatus setSolverObjectUsageResultDataOnNode(SolverObjectUsageResult &results,
                                             MObject &node, MDGModifier &dgmod,
                                             MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;

    // TODO: Write this.

    return status;
}

MStatus setSolverObjectCountResultDataOnNode(SolverObjectCountResult &results,
                                             MObject &node, MDGModifier &dgmod,
                                             MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;

    MFnDependencyNode dg_node_fn(node, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    const char *parameters_num_attr_name = "numberOfParameters";
    const char *errors_num_attr_name = "numberOfErrors";
    const char *marker_errors_num_attr_name = "numberOfMarkerErrors";
    const char *stiff_errors_num_attr_name = "numberOfAttrStiffnessErrors";
    const char *smooth_errors_num_attr_name = "numberOfAttrSmoothnessErrors";

    MPlug parameters_num_plug;
    MPlug errors_num_plug;
    MPlug marker_errors_num_plug;
    MPlug stiff_errors_num_plug;
    MPlug smooth_errors_num_plug;

    status =
        find_plug(parameters_num_attr_name, dg_node_fn, parameters_num_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(errors_num_attr_name, dg_node_fn, errors_num_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(marker_errors_num_attr_name, dg_node_fn,
                       marker_errors_num_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(stiff_errors_num_attr_name, dg_node_fn,
                       stiff_errors_num_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = find_plug(smooth_errors_num_attr_name, dg_node_fn,
                       smooth_errors_num_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool parameters_num_exists = !parameters_num_plug.isNull();
    bool errors_num_exists = !errors_num_plug.isNull();
    bool marker_errors_num_exists = !marker_errors_num_plug.isNull();
    bool stiff_errors_num_exists = !stiff_errors_num_plug.isNull();
    bool smooth_errors_num_exists = !smooth_errors_num_plug.isNull();

    int created_attrs_count = 0;
    if (!parameters_num_exists) {
        status =
            createResultAttr_objectCount(parameters_num_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!errors_num_exists) {
        status =
            createResultAttr_objectCount(errors_num_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!marker_errors_num_exists) {
        status = createResultAttr_objectCount(marker_errors_num_attr_name, node,
                                              dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!stiff_errors_num_exists) {
        status = createResultAttr_objectCount(stiff_errors_num_attr_name, node,
                                              dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!smooth_errors_num_exists) {
        status = createResultAttr_objectCount(smooth_errors_num_attr_name, node,
                                              dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    // Any non-created attributes need to be created before
    // proceeding.
    if (created_attrs_count > 0) {
        dgmod.doIt();

        if (!parameters_num_exists) {
            status = find_plug(parameters_num_attr_name, dg_node_fn,
                               parameters_num_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            parameters_num_exists = !parameters_num_plug.isNull();
        }

        if (!errors_num_exists) {
            status =
                find_plug(errors_num_attr_name, dg_node_fn, errors_num_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            errors_num_exists = !errors_num_plug.isNull();
        }

        if (!marker_errors_num_exists) {
            status = find_plug(marker_errors_num_attr_name, dg_node_fn,
                               marker_errors_num_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            marker_errors_num_exists = !marker_errors_num_plug.isNull();
        }

        if (!stiff_errors_num_exists) {
            status = find_plug(stiff_errors_num_attr_name, dg_node_fn,
                               stiff_errors_num_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            stiff_errors_num_exists = !stiff_errors_num_plug.isNull();
        }

        if (!smooth_errors_num_exists) {
            status = find_plug(smooth_errors_num_attr_name, dg_node_fn,
                               smooth_errors_num_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            smooth_errors_num_exists = !smooth_errors_num_plug.isNull();
        }
    }

    MMSOLVER_ASSERT(parameters_num_exists,
                    "parameter count attribute must exist.");
    MMSOLVER_ASSERT(errors_num_exists, "errors count attribute must exist.");
    MMSOLVER_ASSERT(marker_errors_num_exists,
                    "marker errors count attribute must exist.");
    MMSOLVER_ASSERT(stiff_errors_num_exists,
                    "stiff errors count attribute must exist.");
    MMSOLVER_ASSERT(smooth_errors_num_exists,
                    "smooth errors count attribute must exist.");

    dgmod.newPlugValueInt(parameters_num_plug, results.parameter_count);
    dgmod.newPlugValueInt(errors_num_plug, results.error_count);
    dgmod.newPlugValueInt(marker_errors_num_plug, results.marker_error_count);
    dgmod.newPlugValueInt(stiff_errors_num_plug,
                          results.attr_stiffness_error_count);
    dgmod.newPlugValueInt(smooth_errors_num_plug,
                          results.attr_smoothness_error_count);
    dgmod.doIt();

    return status;
}

MStatus setCommandResultDataOnNode(CommandResult &results,
                                   const PrintStatOptions &printStats,
                                   MObject &node, MDGModifier &dgmod,
                                   MAnimCurveChange &curveChange) {
    if (node.isNull()) {
        return MS::kFailure;
    }

    MStatus status = MS::kSuccess;
    if (printStats.input) {
        status = setSolverObjectCountResultDataOnNode(
            results.solverObjectCountResult, node, dgmod, curveChange);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (printStats.usedSolveObjects) {
        status = setSolverObjectUsageResultDataOnNode(
            results.solverObjectUsageResult, node, dgmod, curveChange);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (printStats.affects) {
        status = setAffectsResultDataOnNode(results.affectsResult, node, dgmod,
                                            curveChange);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    status = setSolverResultDataOnNode(results.solverResult, node, dgmod,
                                       curveChange);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status =
        setTimerResultDataOnNode(results.timerResult, node, dgmod, curveChange);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = setErrorMetricsResultDataOnNode(results.errorMetricsResult, node,
                                             dgmod, curveChange);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = setSolveValuesResultDataOnNode(results.solveValuesResult, node,
                                            dgmod, curveChange);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // TODO: Add "Solver Frames" attributes.

    return status;
}

}  // namespace mmsolver
