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

#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MEventMessage.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MPoint.h>

// Viewport 2.0
#include <maya/MPxDrawOverride.h>
#include <maya/MUserData.h>
#include <maya/MDrawContext.h>

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>


namespace mmsolver {

SkyDomeDrawOverride::SkyDomeDrawOverride(const MObject &obj)
        : MHWRender::MPxDrawOverride(obj,
                                     /*callback=*/ nullptr,
                                     /*isAlwaysDirty=*/ true) {
        m_model_editor_changed_callback_id = MEventMessage::addEventCallback(
                "modelEditorChanged", on_model_editor_changed_func, this);

    MStatus status;
    MFnDependencyNode node(obj, &status);
        m_node = status ? dynamic_cast<SkyDomeShapeNode *>(node.userNode()) : nullptr;
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
        MHWRender::MRenderer::setGeometryDrawDirty(
                ovr->m_node->thisMObject());
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


bool SkyDomeDrawOverride::isBounded(const MDagPath & /*objPath*/,
                                    const MDagPath & /*cameraPath*/) const {
    return false;
}

MBoundingBox SkyDomeDrawOverride::boundingBox(
        const MDagPath &/*objPath*/,
        const MDagPath &/*cameraPath*/) const {
    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);
    return MBoundingBox(corner1, corner2);
}

// Called by Maya each time the object needs to be drawn.
MUserData *SkyDomeDrawOverride::prepareForDraw(
        const MDagPath &objPath,
        const MDagPath &/*cameraPath*/,
        const MHWRender::MFrameContext &/*frameContext*/,
        MUserData *oldData) {
    MStatus status;

    SkyDomeDrawData *data = dynamic_cast<SkyDomeDrawData *>(oldData);
    if (!data) {
        data = new SkyDomeDrawData();
    }

    // Global settings
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_global_enable, data->m_global_enable);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_transform_mode, data->m_transform_mode);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_global_line_width, data->m_global_line_width);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_resolution, data->m_resolution);
    CHECK_MSTATUS(status);

    // Depth and display settings.
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_draw_mode, data->m_draw_mode);
    CHECK_MSTATUS(status);

    MDistance radius_distance(1.0);
    status = get_node_attr(objPath, SkyDomeShapeNode::m_radius, radius_distance);
    CHECK_MSTATUS(status);
    if (status) {
        data->m_radius = static_cast<float>(radius_distance.asCentimeters());
    }

    // Enabled status
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_latitude_enable, data->m_latitude_enable);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_longitude_enable, data->m_longitude_enable);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_x_axis_enable, data->m_x_axis_enable);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_y_axis_enable, data->m_y_axis_enable);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_z_axis_enable, data->m_z_axis_enable);
    CHECK_MSTATUS(status);

    // Line width
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_latitude_line_width, data->m_latitude_line_width);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_longitude_line_width, data->m_longitude_line_width);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_x_axis_line_width, data->m_x_axis_line_width);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_y_axis_line_width, data->m_y_axis_line_width);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_z_axis_line_width, data->m_z_axis_line_width);
    CHECK_MSTATUS(status);

    // Lat-long divisions
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_latitude_divisions, data->m_latitude_divisions);
    CHECK_MSTATUS(status);
    status = get_node_attr(
        objPath, SkyDomeShapeNode::m_longitude_divisions, data->m_longitude_divisions);
    CHECK_MSTATUS(status);

    // Default depth priority.
    data->m_depth_priority = MHWRender::MRenderItem::sDormantFilledDepthPriority;

    return data;
}

void SkyDomeDrawOverride::addUIDrawables(
        const MDagPath &/*objPath*/,
        MHWRender::MUIDrawManager &drawManager,
        const MHWRender::MFrameContext &frameContext,
        const MUserData *userData) {
    MStatus status;
    SkyDomeDrawData *data = (SkyDomeDrawData *) userData;
    if (!data) {
        return;
    }
    if (!data->m_global_enable) {
        return;
    }

    // TODO: Allow users to optionally use the 'view position' or not.
    float pos_x = 0.0f;
    float pos_y = 0.0f;
    float pos_z = 0.0f;
    if (data->m_transform_mode == static_cast<short>(TransformMode::kCenterOfCamera)) {
        // Use the camera position.
        MDoubleArray view_pos = frameContext.getTuple(
            MFrameContext::kViewPosition, &status);
        CHECK_MSTATUS(status);
        pos_x = static_cast<float>(view_pos[0]);
        pos_y = static_cast<float>(view_pos[1]);
        pos_z = static_cast<float>(view_pos[2]);
    }

    const uint32_t res = data->m_resolution;
    const float radius = data->m_radius;
    const uint32_t interval_latitude =
        static_cast<uint32_t>(std::powf(2, data->m_latitude_divisions));
    const uint32_t interval_longitude =
        static_cast<uint32_t>(std::powf(2, data->m_longitude_divisions));

    auto initial_size_x = res * 2 * data->m_x_axis_enable;
    auto initial_size_y = res * 2 * data->m_y_axis_enable;
    auto initial_size_z = res * 2 * data->m_z_axis_enable;
    const uint32_t initial_size_latitude =
            res * 2 * interval_latitude * data->m_latitude_enable;
    const uint32_t initial_size_longitude =
            res * 2 * interval_longitude * data->m_longitude_enable;
    MFloatPointArray lines_x(initial_size_x);
    MFloatPointArray lines_y(initial_size_y);
    MFloatPointArray lines_z(initial_size_z);
    MFloatPointArray lines_latitude(initial_size_latitude);
    MFloatPointArray lines_longitude(initial_size_longitude);

    auto index = 0;
    const float pi = static_cast<float>(M_PI);

    // X Axis
    //
    // TODO: Allow skipping only top or bottom.
    if (data->m_x_axis_enable) {
        index = 0;
        for (uint32_t i = 0; i < res; i++) {
            const float ratio1 = static_cast<float>(i) / static_cast<float>(res);
            const float ratio2 = static_cast<float>(i + 1) / static_cast<float>(res);
            const float angle1 = 2.0f * pi * ratio1;
            const float angle2 = 2.0f * pi * ratio2;
            const float x1 = radius * std::cosf(angle1);
            const float x2 = radius * std::cosf(angle2);
            const float y1 = radius * std::sinf(angle1);
            const float y2 = radius * std::sinf(angle2);
            lines_x.set(
                index,
                pos_x,
                pos_y + x1,
                pos_z + y1);
            lines_x.set(
                index + 1,
                pos_x,
                pos_y + x2,
                pos_z + y2);
            index += 2;
        }
    }

    // Y Axis
    //
    // TODO: Allow skipping only top or bottom.
    if (data->m_y_axis_enable) {
        index = 0;
        for (uint32_t i = 0; i < res; i++) {
            const float ratio1 = static_cast<float>(i) / static_cast<float>(res);
            const float ratio2 = static_cast<float>(i + 1) / static_cast<float>(res);
            const float angle1 = 2.0f * pi * ratio1;
            const float angle2 = 2.0f * pi * ratio2;
            const float x1 = radius * std::cosf(angle1);
            const float x2 = radius * std::cosf(angle2);
            const float y1 = radius * std::sinf(angle1);
            const float y2 = radius * std::sinf(angle2);
            lines_y.set(
                index,
                pos_x + x1,
                pos_y,
                pos_z + y1);
            lines_y.set(
                index + 1,
                pos_x + x2,
                pos_y,
                pos_z + y2);
            index += 2;
        }
    }

    // Z Axis
    //
    // TODO: Allow skipping only top or bottom.
    if (data->m_z_axis_enable) {
        index = 0;
        for (uint32_t i = 0; i < res; i++) {
            const float ratio1 = static_cast<float>(i) / static_cast<float>(res);
            const float ratio2 = static_cast<float>(i + 1) / static_cast<float>(res);
            const float angle1 = 2.0f * pi * ratio1;
            const float angle2 = 2.0f * pi * ratio2;
            const float x1 = radius * std::cosf(angle1);
            const float x2 = radius * std::cosf(angle2);
            const float y1 = radius * std::sinf(angle1);
            const float y2 = radius * std::sinf(angle2);
            lines_z.set(
                index,
                pos_x + x1,
                pos_y + y1,
                pos_z);
            lines_z.set(
                index + 1,
                pos_x + x2,
                pos_y + y2,
                pos_z);
            index += 2;
        }
    }

    // Latitude
    //
    // TODO: Add little crosses, and/or dots at selected intervals.
    //
    // TODO: Allow skipping only top or bottom.
    if (data->m_latitude_enable) {
        index = 0;
        for (uint32_t i = 0; i < interval_latitude; i++) {
            const float outer_ratio =
                    static_cast<float>(i) / static_cast<float>(interval_latitude);
            const float outer_angle = 2.0f * pi * outer_ratio;
            const float x = std::cosf(outer_angle);
            const float y = std::sinf(outer_angle);

            for (uint32_t j = 0; j < res; j++) {
                const float inner_ratio1 =
                    static_cast<float>(j) / static_cast<float>(res);
                const float inner_ratio2 =
                    static_cast<float>(j + 1) / static_cast<float>(res);
                const float inner_angle1 = 2.0f * pi * inner_ratio1;
                const float inner_angle2 = 2.0f * pi * inner_ratio2;
                const float xy1 = radius * std::cosf(inner_angle1);
                const float xy2 = radius * std::cosf(inner_angle2);
                const float z1 = radius * std::sinf(inner_angle1);
                const float z2 = radius * std::sinf(inner_angle2);

                lines_latitude.set(
                    index,
                    pos_x + (z1 * x),
                    pos_y + xy1,
                    pos_z + (z1 * y));
                lines_latitude.set(
                    index + 1,
                    pos_x + (z2 * x),
                    pos_y + xy2,
                    pos_z + (z2 * y));
                index += 2;
            }
        }
    }

    // Longitude
    if (data->m_longitude_enable) {
        index = 0;
        for (uint32_t j = 0; j < interval_longitude; j++) {
            const float outer_ratio =
                static_cast<float>(j) / static_cast<float>(interval_longitude);
            const float outer_angle = 2.0f * pi * outer_ratio;
            const float xy = radius * std::cosf(outer_angle);
            const float z = radius * std::sinf(outer_angle);
            for (uint32_t i = 0; i < res; i++) {
                const float ratio1 = static_cast<float>(i) / static_cast<float>(res);
                const float ratio2 = static_cast<float>(i + 1) / static_cast<float>(res);
                const float angle1 = 2.0f * pi * ratio1;
                const float angle2 = 2.0f * pi * ratio2;
                const float x1 = xy * std::cosf(angle1);
                const float x2 = xy * std::cosf(angle2);
                const float y1 = xy * std::sinf(angle1);
                const float y2 = xy * std::sinf(angle2);
                lines_longitude.set(
                    index,
                    pos_x + x1,
                    pos_y + z,
                    pos_z + y1);
                lines_longitude.set(
                    index + 1,
                    pos_x + x2,
                    pos_y + z,
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
        if (data->m_latitude_enable) {
            drawManager.setLineWidth(
                data->m_global_line_width * data->m_latitude_line_width);
            drawManager.setColor(data->m_color_latitude);
            drawManager.mesh(
                MHWRender::MUIDrawManager::kLines,
                lines_latitude);
        }

        // Longitude
        if (data->m_longitude_enable) {
            drawManager.setLineWidth(
                data->m_global_line_width * data->m_longitude_line_width);
            drawManager.setColor(data->m_color_longitude);
            drawManager.mesh(
                MHWRender::MUIDrawManager::kLines,
                lines_longitude);
        }

        // X Axis
        if (data->m_x_axis_enable) {
            drawManager.setLineWidth(
                data->m_global_line_width * data->m_x_axis_line_width);
            drawManager.setColor(data->m_color_x);
            drawManager.mesh(
                MHWRender::MUIDrawManager::kLines,
                lines_x);
        }

        // Y Axis
        if (data->m_y_axis_enable) {
            drawManager.setLineWidth(
                data->m_global_line_width * data->m_y_axis_line_width);
            drawManager.setColor(data->m_color_y);
            drawManager.mesh(
                MHWRender::MUIDrawManager::kLines,
                lines_y);
        }

        // Z Axis
        if (data->m_z_axis_enable) {
            drawManager.setLineWidth(
                data->m_global_line_width * data->m_z_axis_line_width);
            drawManager.setColor(data->m_color_z);
            drawManager.mesh(
                MHWRender::MUIDrawManager::kLines,
                lines_z);
        }

        drawManager.endDrawable();
    }
}

} // namespace mmsolver
