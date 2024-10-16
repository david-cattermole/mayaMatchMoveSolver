/*
 * Copyright (C) 2021 David Cattermole.
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
 */

#include "SkyDomeDrawOverride.h"

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>

// Maya
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MEventMessage.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MPlug.h>
#include <maya/MPoint.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>
#include <maya/MPxDrawOverride.h>
#include <maya/MUserData.h>

// MM Solver
#include <mmcore/mmmath.h>

namespace mmsolver {

SkyDomeDrawOverride::SkyDomeDrawOverride(const MObject &obj)
    : MHWRender::MPxDrawOverride(obj,
                                 /*callback=*/nullptr,
                                 /*isAlwaysDirty=*/true) {
    m_model_editor_changed_callback_id = MEventMessage::addEventCallback(
        "modelEditorChanged", on_model_editor_changed_func, this);

    MStatus status;
    MFnDependencyNode node(obj, &status);
    m_node =
        status ? dynamic_cast<SkyDomeShapeNode *>(node.userNode()) : nullptr;
}

SkyDomeDrawOverride::~SkyDomeDrawOverride() {
    m_node = nullptr;

    if (m_model_editor_changed_callback_id != 0) {
        MMessage::removeCallback(m_model_editor_changed_callback_id);
        m_model_editor_changed_callback_id = 0;
    }
}

void SkyDomeDrawOverride::on_model_editor_changed_func(void *clientData) {
    // Mark the node as being dirty so that it can update when the
    // display appearance switches between wireframe and shaded.
    SkyDomeDrawOverride *ovr = static_cast<SkyDomeDrawOverride *>(clientData);
    if (ovr && ovr->m_node) {
        MHWRender::MRenderer::setGeometryDrawDirty(ovr->m_node->thisMObject());
    }
}

MHWRender::DrawAPI SkyDomeDrawOverride::supportedDrawAPIs() const {
    return (MHWRender::kOpenGL | MHWRender::kDirectX11 |
            MHWRender::kOpenGLCoreProfile);
}

MStatus SkyDomeDrawOverride::get_node_attr(const MDagPath &objPath,
                                           const MObject &attr,
                                           MDistance &value) const {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            status = plug.getValue(value);
            return status;
        }
    }
    return status;
}

MStatus SkyDomeDrawOverride::get_node_attr(const MDagPath &objPath,
                                           const MObject &attr,
                                           bool &value) const {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asBool();
            return status;
        }
    }
    return status;
}

MStatus SkyDomeDrawOverride::get_node_attr(const MDagPath &objPath,
                                           const MObject &attr,
                                           int32_t &value) const {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asInt();
            return status;
        }
    }
    return status;
}

MStatus SkyDomeDrawOverride::get_node_attr(const MDagPath &objPath,
                                           const MObject &attr,
                                           uint32_t &value) const {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = static_cast<uint32_t>(plug.asInt());
            return status;
        }
    }
    return status;
}

MStatus SkyDomeDrawOverride::get_node_attr(const MDagPath &objPath,
                                           const MObject &attr,
                                           short &value) const {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asShort();
            return status;
        }
    }
    return status;
}

MStatus SkyDomeDrawOverride::get_node_attr(const MDagPath &objPath,
                                           const MObject &attr,
                                           float &value) const {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asFloat();
            return status;
        }
    }
    return status;
}

MStatus SkyDomeDrawOverride::get_node_attr(const MDagPath &objPath,
                                           const MObject &attr,
                                           double &value) const {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            value = plug.asDouble();
            return status;
        }
    }
    return status;
}

MStatus SkyDomeDrawOverride::get_node_attr(const MDagPath &objPath,
                                           const MObject &attr,
                                           MColor &value) const {
    MStatus status;
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, attr);
        if (!plug.isNull()) {
            MDataHandle data_handle = plug.asMDataHandle(&status);
            CHECK_MSTATUS_AND_RETURN_IT(status);
            auto data = data_handle.asFloat3();
            value.r = data[0];
            value.g = data[1];
            value.b = data[2];
            return status;
        }
    }
    return status;
}

bool SkyDomeDrawOverride::isBounded(const MDagPath & /*objPath*/,
                                    const MDagPath & /*cameraPath*/) const {
    return false;
}

MBoundingBox SkyDomeDrawOverride::boundingBox(
    const MDagPath & /*objPath*/, const MDagPath & /*cameraPath*/) const {
    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);
    return MBoundingBox(corner1, corner2);
}

// Called by Maya each time the object needs to be drawn.
MUserData *SkyDomeDrawOverride::prepareForDraw(
    const MDagPath &objPath, const MDagPath & /*cameraPath*/,
    const MHWRender::MFrameContext & /*frameContext*/, MUserData *oldData) {
    MStatus status;

    SkyDomeDrawData *data = dynamic_cast<SkyDomeDrawData *>(oldData);
    if (!data) {
        data = new SkyDomeDrawData();
    }

    // Global settings
    status = get_node_attr(objPath, SkyDomeShapeNode::m_enable, data->m_enable);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_transform_mode,
                           data->m_transform_mode);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_line_width,
                           data->m_line_width);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_resolution,
                           data->m_resolution);
    CHECK_MSTATUS(status);

    // Depth and display settings.
    status = get_node_attr(objPath, SkyDomeShapeNode::m_draw_mode,
                           data->m_draw_mode);
    CHECK_MSTATUS(status);

    MDistance radius_distance(1.0);
    status =
        get_node_attr(objPath, SkyDomeShapeNode::m_radius, radius_distance);
    CHECK_MSTATUS(status);
    if (status) {
        data->m_radius = radius_distance.asCentimeters();
    }

    // Enabled status
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_x_enable,
                           data->m_axis_x_enable);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_y_enable,
                           data->m_axis_y_enable);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_z_enable,
                           data->m_axis_z_enable);
    CHECK_MSTATUS(status);

    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_x_enable_top,
                           data->m_axis_x_enable_top);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_z_enable_top,
                           data->m_axis_z_enable_top);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_x_enable_bottom,
                           data->m_axis_x_enable_bottom);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_z_enable_bottom,
                           data->m_axis_z_enable_bottom);
    CHECK_MSTATUS(status);

    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_lat_enable,
                           data->m_grid_lat_enable);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_long_enable,
                           data->m_grid_long_enable);
    CHECK_MSTATUS(status);

    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_lat_enable_top,
                           data->m_grid_lat_enable_top);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_long_enable_top,
                           data->m_grid_long_enable_top);
    CHECK_MSTATUS(status);

    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_lat_enable_bottom,
                           data->m_grid_lat_enable_bottom);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_long_enable_bottom,
                           data->m_grid_long_enable_bottom);
    CHECK_MSTATUS(status);

    // Color
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_x_color,
                           data->m_axis_x_color);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_y_color,
                           data->m_axis_y_color);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_z_color,
                           data->m_axis_z_color);
    CHECK_MSTATUS(status);

    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_lat_color,
                           data->m_grid_lat_color);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_long_color,
                           data->m_grid_long_color);
    CHECK_MSTATUS(status);

    // Alpha
    status = get_node_attr(objPath, SkyDomeShapeNode::m_alpha, data->m_alpha);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_x_alpha,
                           data->m_axis_x_color[3]);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_y_alpha,
                           data->m_axis_y_color[3]);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_z_alpha,
                           data->m_axis_z_color[3]);
    CHECK_MSTATUS(status);

    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_lat_alpha,
                           data->m_grid_lat_color[3]);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_long_alpha,
                           data->m_grid_long_color[3]);
    CHECK_MSTATUS(status);

    // Apply global alpha as a multiplier.
    data->m_axis_x_color[3] *= static_cast<float>(data->m_alpha);
    data->m_axis_y_color[3] *= static_cast<float>(data->m_alpha);
    data->m_axis_z_color[3] *= static_cast<float>(data->m_alpha);
    data->m_grid_lat_color[3] *= static_cast<float>(data->m_alpha);
    data->m_grid_long_color[3] *= static_cast<float>(data->m_alpha);

    // Line width
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_x_line_width,
                           data->m_axis_x_line_width);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_y_line_width,
                           data->m_axis_y_line_width);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_axis_z_line_width,
                           data->m_axis_z_line_width);
    CHECK_MSTATUS(status);

    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_lat_line_width,
                           data->m_grid_lat_line_width);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_long_line_width,
                           data->m_grid_long_line_width);
    CHECK_MSTATUS(status);

    // Lat-long divisions
    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_lat_divisions,
                           data->m_grid_lat_divisions);
    CHECK_MSTATUS(status);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_grid_long_divisions,
                           data->m_grid_long_divisions);
    CHECK_MSTATUS(status);

    // Default depth priority.
    data->m_depth_priority =
        MHWRender::MRenderItem::sDormantFilledDepthPriority;

    return data;
}

void SkyDomeDrawOverride::addUIDrawables(
    const MDagPath &objPath, MHWRender::MUIDrawManager &drawManager,
    const MHWRender::MFrameContext &frameContext, const MUserData *userData) {
    MStatus status;
    SkyDomeDrawData *data = (SkyDomeDrawData *)userData;
    if (!data) {
        return;
    }
    if (!data->m_enable) {
        return;
    }

    double pos_x = 0.0;
    double pos_y = 0.0;
    double pos_z = 0.0;
    if (data->m_transform_mode ==
        static_cast<short>(TransformMode::kCenterOfCamera)) {
        // Use the camera position.
        MDoubleArray view_pos =
            frameContext.getTuple(MFrameContext::kViewPosition, &status);
        CHECK_MSTATUS(status);
        MPoint view_point(view_pos[0], view_pos[1], view_pos[2]);

        // Remove the sky dome's transform.
        MMatrix matrix_inverse = objPath.inclusiveMatrixInverse(&status);
        CHECK_MSTATUS(status);
        view_point *= matrix_inverse;

        pos_x = static_cast<double>(view_point[0]);
        pos_y = static_cast<double>(view_point[1]);
        pos_z = static_cast<double>(view_point[2]);
    }

    const uint32_t res = data->m_resolution;
    const double radius = data->m_radius;
    const uint32_t interval_latitude =
        static_cast<uint32_t>(std::pow(2, data->m_grid_lat_divisions));
    const uint32_t interval_longitude =
        static_cast<uint32_t>(std::pow(2, data->m_grid_long_divisions));

    // Allow skipping only top or bottom.
    auto axis_x_top = data->m_axis_x_enable_top;
    auto axis_z_top = data->m_axis_z_enable_top;
    auto axis_x_bot = data->m_axis_x_enable_bottom;
    auto axis_z_bot = data->m_axis_z_enable_bottom;

    auto grid_lat_top = data->m_grid_lat_enable_top;
    auto grid_long_top = data->m_grid_long_enable_top;
    auto grid_lat_bot = data->m_grid_lat_enable_bottom;
    auto grid_long_bot = data->m_grid_long_enable_bottom;

    auto initial_size_x = res * 2 * data->m_axis_x_enable;
    auto initial_size_y = res * 2 * data->m_axis_y_enable;
    auto initial_size_z = res * 2 * data->m_axis_z_enable;
    const uint32_t initial_size_latitude =
        res * 2 * interval_latitude * data->m_grid_lat_enable;
    const uint32_t initial_size_longitude =
        res * 2 * interval_longitude * data->m_grid_long_enable;
    MPointArray lines_x(initial_size_x);
    MPointArray lines_y(initial_size_y);
    MPointArray lines_z(initial_size_z);
    MPointArray lines_latitude(initial_size_latitude);
    MPointArray lines_longitude(initial_size_longitude);

    // Calculate the start/end angle that each component will rotate.
    const double pi = static_cast<double>(M_PI);
    const double half_pi = static_cast<double>(M_PI / 2);
    const double angle_offset_x = pi * 0.5;
    const double angle_offset_z = pi;
    const double angle_offset_lat = pi / 2.0;
    double angle_start_x = angle_offset_x + (-pi * axis_x_top);
    double angle_start_z = angle_offset_z + (-pi * axis_z_top);
    double angle_start_lat = angle_offset_lat + (-half_pi * grid_lat_top);
    double angle_end_x = angle_offset_x + (pi * axis_x_bot);
    double angle_end_z = angle_offset_z + (pi * axis_z_bot);
    double angle_end_lat = angle_offset_lat + (half_pi * grid_lat_bot);

    // X Axis
    if (data->m_axis_x_enable && (axis_x_top || axis_x_bot)) {
        auto index = 0;
        for (uint32_t i = 0; i < res; i++) {
            const double ratio1 =
                static_cast<double>(i) / static_cast<double>(res);
            const double ratio2 =
                static_cast<double>(i + 1) / static_cast<double>(res);
            const double angle1 =
                mmmath::lerp(angle_start_x, angle_end_x, ratio1);
            const double angle2 =
                mmmath::lerp(angle_start_x, angle_end_x, ratio2);
            const double x1 = radius * std::cos(angle1);
            const double x2 = radius * std::cos(angle2);
            const double y1 = radius * std::sin(angle1);
            const double y2 = radius * std::sin(angle2);

            lines_x.set(index, pos_x, pos_y + x1, pos_z + y1);
            lines_x.set(index + 1, pos_x, pos_y + x2, pos_z + y2);
            index += 2;
        }
    }

    // Y Axis
    if (data->m_axis_y_enable) {
        auto index = 0;
        for (uint32_t i = 0; i < res; i++) {
            const double ratio1 =
                static_cast<double>(i) / static_cast<double>(res);
            const double ratio2 =
                static_cast<double>(i + 1) / static_cast<double>(res);
            const double angle1 = 2.0f * pi * ratio1;
            const double angle2 = 2.0f * pi * ratio2;
            const double x1 = radius * std::cos(angle1);
            const double x2 = radius * std::cos(angle2);
            const double y1 = radius * std::sin(angle1);
            const double y2 = radius * std::sin(angle2);
            lines_y.set(index, pos_x + x1, pos_y, pos_z + y1);
            lines_y.set(index + 1, pos_x + x2, pos_y, pos_z + y2);
            index += 2;
        }
    }

    // Z Axis
    if (data->m_axis_z_enable && (axis_z_top || axis_z_bot)) {
        auto index = 0;
        for (uint32_t i = 0; i < res; i++) {
            const double ratio1 =
                static_cast<double>(i) / static_cast<double>(res);
            const double ratio2 =
                static_cast<double>(i + 1) / static_cast<double>(res);
            const double angle1 =
                mmmath::lerp(angle_start_z, angle_end_z, ratio1);
            const double angle2 =
                mmmath::lerp(angle_start_z, angle_end_z, ratio2);
            const double x1 = radius * std::cos(angle1);
            const double x2 = radius * std::cos(angle2);
            const double y1 = radius * std::sin(angle1);
            const double y2 = radius * std::sin(angle2);

            lines_z.set(index, pos_x + x1, pos_y + y1, pos_z);
            lines_z.set(index + 1, pos_x + x2, pos_y + y2, pos_z);
            index += 2;
        }
    }

    // Latitude
    //
    // TODO: Add little crosses, and/or dots at selected intervals.
    if (data->m_grid_lat_enable && (grid_lat_top || grid_lat_bot)) {
        auto index = 0;
        for (uint32_t i = 0; i < interval_latitude; i++) {
            const double outer_ratio =
                static_cast<double>(i) / static_cast<double>(interval_latitude);
            const double outer_angle = 2.0f * pi * outer_ratio;
            const double x = std::cos(outer_angle);
            const double y = std::sin(outer_angle);

            for (uint32_t j = 0; j < res; j++) {
                const double inner_ratio1 =
                    static_cast<double>(j) / static_cast<double>(res);
                const double inner_ratio2 =
                    static_cast<double>(j + 1) / static_cast<double>(res);
                const double inner_angle1 =
                    mmmath::lerp(angle_start_lat, angle_end_lat, inner_ratio1);
                const double inner_angle2 =
                    mmmath::lerp(angle_start_lat, angle_end_lat, inner_ratio2);
                const double xy1 = radius * std::cos(inner_angle1);
                const double xy2 = radius * std::cos(inner_angle2);
                const double z1 = radius * std::sin(inner_angle1);
                const double z2 = radius * std::sin(inner_angle2);

                lines_latitude.set(index, pos_x + (z1 * x), pos_y + xy1,
                                   pos_z + (z1 * y));
                lines_latitude.set(index + 1, pos_x + (z2 * x), pos_y + xy2,
                                   pos_z + (z2 * y));
                index += 2;
            }
        }
    }

    // Longitude
    if (data->m_grid_long_enable && (grid_long_top || grid_long_bot)) {
        auto index = 0;
        for (uint32_t j = 0; j < interval_longitude; j++) {
            const double outer_ratio = static_cast<double>(j) /
                                       static_cast<double>(interval_longitude);
            const double outer_angle = 2.0f * pi * outer_ratio;
            const double xy = radius * std::cos(outer_angle);
            const double z = radius * std::sin(outer_angle);

            if (!grid_long_top && (z > 0.0f)) {
                continue;
            }
            if (!grid_long_bot && (z < 0.0f)) {
                continue;
            }

            for (uint32_t i = 0; i < res; i++) {
                const double ratio1 =
                    static_cast<double>(i) / static_cast<double>(res);
                const double ratio2 =
                    static_cast<double>(i + 1) / static_cast<double>(res);
                const double angle1 = 2.0f * pi * ratio1;
                const double angle2 = 2.0f * pi * ratio2;
                const double x1 = xy * std::cos(angle1);
                const double x2 = xy * std::cos(angle2);
                const double y1 = xy * std::sin(angle1);
                const double y2 = xy * std::sin(angle2);

                lines_longitude.set(index, pos_x + x1, pos_y + z, pos_z + y1);
                lines_longitude.set(index + 1, pos_x + x2, pos_y + z,
                                    pos_z + y2);
                index += 2;
            }
        }
    }

    // Add drawable
    {
        if (data->m_draw_mode == static_cast<short>(DrawMode::kDrawOnTop)) {
            // No depth testing while drawing.
            drawManager.beginDrawInXray();
        } else {
            drawManager.beginDrawable();
            drawManager.setDepthPriority(data->m_depth_priority);
        }

        // Latitude
        if (data->m_grid_lat_enable) {
            drawManager.setLineWidth(static_cast<float>(
                data->m_line_width * data->m_grid_lat_line_width));
            drawManager.setColor(data->m_grid_lat_color);
            drawManager.mesh(MHWRender::MUIDrawManager::kLines, lines_latitude);
        }

        // Longitude
        if (data->m_grid_long_enable) {
            drawManager.setLineWidth(static_cast<float>(
                data->m_line_width * data->m_grid_long_line_width));
            drawManager.setColor(data->m_grid_long_color);
            drawManager.mesh(MHWRender::MUIDrawManager::kLines,
                             lines_longitude);
        }

        // X Axis
        if (data->m_axis_x_enable) {
            drawManager.setLineWidth(static_cast<float>(
                data->m_line_width * data->m_axis_x_line_width));
            drawManager.setColor(data->m_axis_x_color);
            drawManager.mesh(MHWRender::MUIDrawManager::kLines, lines_x);
        }

        // Y Axis
        if (data->m_axis_y_enable) {
            drawManager.setLineWidth(static_cast<float>(
                data->m_line_width * data->m_axis_y_line_width));
            drawManager.setColor(data->m_axis_y_color);
            drawManager.mesh(MHWRender::MUIDrawManager::kLines, lines_y);
        }

        // Z Axis
        if (data->m_axis_z_enable) {
            drawManager.setLineWidth(static_cast<float>(
                data->m_line_width * data->m_axis_z_line_width));
            drawManager.setColor(data->m_axis_z_color);
            drawManager.mesh(MHWRender::MUIDrawManager::kLines, lines_z);
        }

        drawManager.endDrawable();
    }
}

}  // namespace mmsolver
