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
 * Common functions used to set result data structures.
 */

#include "adjust_results_helpers.h"

// Maya
#include <maya/MAnimUtil.h>
#include <maya/MDGModifier.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MFnAttribute.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>

// MM Solver
#include "adjust_data.h"
#include "mmSolver/utilities/debug_utils.h"

MStatus create_attr_deviation(const char *attr_name, MObject &node,
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

MStatus create_attr_averageDeviation(const char *attr_name, MObject &node,
                                     MDGModifier &dgmod) {
    return create_attr_deviation(attr_name, node, dgmod);
}

MStatus create_attr_maximumDeviation(const char *attr_name, MObject &node,
                                     MDGModifier &dgmod) {
    return create_attr_deviation(attr_name, node, dgmod);
}

MStatus create_attr_maxDeviationFrame(const char *attr_name, MObject &node,
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

typedef std::unordered_multimap<double, double> MultiMapDoubleDouble;

MStatus create_deviation_attrs_on_node(
    MObject &node, const MultiMapDoubleDouble &map,
    const char *deviation_attr_name, const char *deviation_avg_attr_name,
    const char *deviation_max_attr_name,
    const char *deviation_max_frame_attr_name, MDGModifier &dgmod,
    MAnimCurveChange &curveChange) {
    MStatus status = MS::kSuccess;

    // How to create the animation curve.
    const auto anim_curve_type = MFnAnimCurve::kAnimCurveTU;
    const auto anim_curve_infinity_type = MFnAnimCurve::kConstant;
    const auto anim_curve_tangent_in_type = MFnAnimCurve::kTangentGlobal;
    const auto anim_curve_tangent_out_type = MFnAnimCurve::kTangentGlobal;

    MTime::Unit ui_unit = MTime::uiUnit();

    MFnDependencyNode dg_node_fn(node, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    int created_attrs_count = 0;
    bool deviation_has_anim_curve = false;

    MPlug deviation_plug;
    MPlug deviation_avg_plug;
    MPlug deviation_max_plug;
    MPlug deviation_max_frame_plug;

    MObject deviation_anim_curve_obj;

    status = find_plug(deviation_attr_name, dg_node_fn, deviation_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = find_plug(deviation_avg_attr_name, dg_node_fn, deviation_avg_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = find_plug(deviation_max_attr_name, dg_node_fn, deviation_max_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = find_plug(deviation_max_frame_attr_name, dg_node_fn,
                       deviation_max_frame_plug);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool deviation_exists = !deviation_plug.isNull();
    bool deviation_avg_exists = !deviation_avg_plug.isNull();
    bool deviation_max_exists = !deviation_max_plug.isNull();
    bool deviation_max_frame_exists = !deviation_max_frame_plug.isNull();

    if (!deviation_exists) {
        status = create_attr_deviation(deviation_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!deviation_avg_exists) {
        status =
            create_attr_averageDeviation(deviation_avg_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!deviation_max_exists) {
        status =
            create_attr_maximumDeviation(deviation_max_attr_name, node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (!deviation_max_frame_exists) {
        status = create_attr_maxDeviationFrame(deviation_max_frame_attr_name,
                                               node, dgmod);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        ++created_attrs_count;
    }

    if (created_attrs_count > 0) {
        dgmod.doIt();

        if (!deviation_exists) {
            status = find_plug(deviation_attr_name, dg_node_fn, deviation_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            deviation_exists = !deviation_plug.isNull();
            MFnAnimCurve anim_curve_fn;
            deviation_anim_curve_obj = anim_curve_fn.create(
                deviation_plug, anim_curve_type, &dgmod, &status);
            dgmod.doIt();
            deviation_has_anim_curve = true;
        }

        if (!deviation_avg_exists) {
            status = find_plug(deviation_avg_attr_name, dg_node_fn,
                               deviation_avg_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            deviation_avg_exists = !deviation_avg_plug.isNull();
        }

        if (!deviation_max_exists) {
            status = find_plug(deviation_max_attr_name, dg_node_fn,
                               deviation_max_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            deviation_max_exists = !deviation_max_plug.isNull();
        }

        if (!deviation_max_frame_exists) {
            status = find_plug(deviation_max_frame_attr_name, dg_node_fn,
                               deviation_max_frame_plug);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            deviation_max_frame_exists = !deviation_max_frame_plug.isNull();
        }
    }

    // Make sure we get the deviation animation curve.
    if (!deviation_has_anim_curve) {
        MObjectArray objects;
        const bool find =
            MAnimUtil::findAnimation(deviation_plug, objects, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        if (find && (objects.length() > 0)) {
            deviation_anim_curve_obj = objects[0];
        } else {
            MFnAnimCurve anim_curve_fn;
            deviation_anim_curve_obj = anim_curve_fn.create(
                deviation_plug, anim_curve_type, &dgmod, &status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            dgmod.doIt();
        }
        deviation_has_anim_curve = true;
    }

    assert(deviation_has_anim_curve);
    assert(deviation_exists);
    assert(deviation_avg_exists);
    assert(deviation_max_exists);
    assert(deviation_max_frame_exists);

    int value_count = 0;
    double value_avg = 0.0;
    double value_max = -0.0;
    MTime frame_max_deviation(-1.0, ui_unit);
    MTime frame_min(99999.0, ui_unit);
    MTime frame_max(-1.0, ui_unit);

    MTimeArray times;
    MDoubleArray values;
    const bool keep_existing_keys = false;
    for (const auto &kv : map) {
        const auto frame_value = kv.first;
        const auto error_value = kv.second;

        MTime time(frame_value, ui_unit);
        times.append(time);
        values.append(error_value);

        value_avg += error_value;

        ++value_count;

        if (error_value > value_max) {
            value_max = error_value;
            frame_max_deviation.setValue(frame_value);
        }

        if (time < frame_min) {
            frame_min = time;
        }
        if (time > frame_max) {
            frame_max = time;
        }
    }

    // Ensure the frames before the last and first frames have values
    // of -1.0, otherwise the values outside the solved range will be
    // the last deviation value, and we want there to be no deviation,
    // so that tools do not recognise the Marker on those frames.
    frame_min -= MTime(1.0, ui_unit);
    frame_max += MTime(1.0, ui_unit);
    times.append(frame_min);
    times.append(frame_max);
    values.append(-1.0);
    values.append(-1.0);

    if (value_count > 0) {
        value_avg = value_avg / static_cast<double>(value_count);
    }

    const auto frame_max_deviation_num =
        static_cast<int>(frame_max_deviation.asUnits(ui_unit));

    dgmod.newPlugValueDouble(deviation_avg_plug, value_avg);
    dgmod.newPlugValueDouble(deviation_max_plug, value_max);
    dgmod.newPlugValueInt(deviation_max_frame_plug, frame_max_deviation_num);
    dgmod.doIt();

    MFnDependencyNode depend_fn(deviation_anim_curve_obj, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    const MString node_name = depend_fn.name();
    const MString node_type = depend_fn.typeName();

    MFnAnimCurve deviation_anim_curve_fn(deviation_anim_curve_obj);
    status = deviation_anim_curve_fn.addKeys(
        &times, &values, anim_curve_tangent_in_type,
        anim_curve_tangent_out_type, keep_existing_keys, &curveChange);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = deviation_anim_curve_fn.setPreInfinityType(
        anim_curve_infinity_type, &curveChange);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = deviation_anim_curve_fn.setPostInfinityType(
        anim_curve_infinity_type, &curveChange);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}
