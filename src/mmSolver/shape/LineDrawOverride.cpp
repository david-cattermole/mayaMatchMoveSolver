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

#include "LineDrawOverride.h"

// STL
#include <algorithm>

// Maya
#include <maya/MString.h>
#include <maya/MPlug.h>
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MEventMessage.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MPoint.h>
#include <maya/MTransformationMatrix.h>
#include <maya/MPointArray.h>

// Maya Viewport 2.0
#include <maya/MPxDrawOverride.h>
#include <maya/MUserData.h>
#include <maya/MDrawContext.h>
#include <maya/MHWGeometryUtilities.h>

#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {

// By setting isAlwaysDirty to false in MPxDrawOverride constructor,
// the draw override will be updated (via prepareForDraw()) only when
// the node is marked dirty via DG evaluation or dirty
// propagation. Additional callback is also added to explicitly mark
// the node as being dirty (via MRenderer::setGeometryDrawDirty()) for
// certain circumstances. Note that the draw callback in
// MPxDrawOverride constructor is set to nullptr in order to achieve
// better performance.
LineDrawOverride::LineDrawOverride(const MObject &obj)
        : MHWRender::MPxDrawOverride(obj,
                                     /*callback=*/ nullptr,
                                     /*isAlwaysDirty=*/ true) {
        m_model_editor_changed_callback_id = MEventMessage::addEventCallback(
                "modelEditorChanged", on_model_editor_changed_func, this);

    MStatus status;
    MFnDependencyNode node(obj, &status);
        m_node = status ? dynamic_cast<LineShapeNode *>(node.userNode()) : nullptr;
}

LineDrawOverride::~LineDrawOverride() {
    m_node = nullptr;

    if (m_model_editor_changed_callback_id != 0) {
        MMessage::removeCallback(m_model_editor_changed_callback_id);
        m_model_editor_changed_callback_id = 0;
    }
}

void LineDrawOverride::on_model_editor_changed_func(void *clientData) {
    // Mark the node as being dirty so that it can update on display appearance
    // switch among wireframe and shaded.
    LineDrawOverride *ovr = static_cast<LineDrawOverride *>(clientData);
    if (ovr && ovr->m_node) {
        MHWRender::MRenderer::setGeometryDrawDirty(
                ovr->m_node->thisMObject());
    }
}

MHWRender::DrawAPI LineDrawOverride::supportedDrawAPIs() const {
    return (MHWRender::kOpenGL | MHWRender::kDirectX11 |
            MHWRender::kOpenGLCoreProfile);
}

bool LineDrawOverride::isBounded(const MDagPath & /*objPath*/,
                                   const MDagPath & /*cameraPath*/) const {
    return true;
}

MBoundingBox LineDrawOverride::boundingBox(
        const MDagPath &objPath,
        const MDagPath &/*cameraPath*/) const
{
    MStatus status;

    MPoint corner1;
    MPoint corner2;

    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, LineShapeNode::m_matrix_array);
        if (!plug.isNull()) {
            uint32_t numElements = plug.evaluateNumElements();
            for (uint32_t i = 0; i < numElements; ++i) {
                MPlug plugElement = plug.elementByPhysicalIndex(i, &status);
                CHECK_MSTATUS(status);
                if (!plugElement.isNull()) {
                    MDataHandle dataHandle = plugElement.asMDataHandle(&status);
                    CHECK_MSTATUS(status);
                    MMatrix matrix = dataHandle.asMatrix();

                    double x = matrix[3][0];
                    double y = matrix[3][1];
                    double z = matrix[3][2];
                    corner1[0] = std::min(corner1[0], x);
                    corner1[1] = std::min(corner1[1], y);
                    corner1[2] = std::min(corner1[2], z);

                    corner2[0] = std::max(corner2[0], x);
                    corner2[1] = std::max(corner2[1], y);
                    corner2[2] = std::max(corner2[2], z);
                }
            }
        }
    }

    return MBoundingBox(corner1, corner2);
}

// Called by Maya each time the object needs to be drawn.
MUserData *LineDrawOverride::prepareForDraw(
        const MDagPath &objPath,
        const MDagPath &/*cameraPath*/,
        const MHWRender::MFrameContext &/*frameContext*/,
        MUserData *oldData) {
    LineDrawData *data = dynamic_cast<LineDrawData *>(oldData);
    if (!data) {
        data = new LineDrawData();
    }
    MStatus status;

    MDagPath transformPath(objPath);
    CHECK_MSTATUS(transformPath.pop(1));
    MObject transformObj = transformPath.node();
    MFnDependencyNode dependNodeFn(transformObj);
    data->m_name = dependNodeFn.name();

    // The object's transform matrix
    MMatrix matrix_inverse = objPath.exclusiveMatrixInverse(&status);
    CHECK_MSTATUS(status);
    MMatrix obj_matrix = matrix_inverse;

    // CHECK_MSTATUS(status);
    status = getNodeAttr(objPath, LineShapeNode::m_outer_scale, data->m_outer_scale);
    CHECK_MSTATUS(status);

    // Color
    MColor text_color(0.0f, 0.0f, 0.0f, 1.0f);
    MColor point_color(0.0f, 0.0f, 0.0f, 1.0f);
    MColor inner_color(0.0f, 0.0f, 0.0f, 1.0f);
    MColor outer_color(0.0f, 0.0f, 0.0f, 1.0f);
    status = getNodeAttr(
        objPath, LineShapeNode::m_text_color, text_color);
    CHECK_MSTATUS(status);
    status = getNodeAttr(
        objPath, LineShapeNode::m_point_color, point_color);
    CHECK_MSTATUS(status);
    status = getNodeAttr(
        objPath, LineShapeNode::m_inner_color, inner_color);
    CHECK_MSTATUS(status);
    status = getNodeAttr(
        objPath, LineShapeNode::m_outer_color, outer_color);
    CHECK_MSTATUS(status);

    // Alpha
    status = getNodeAttr(
        objPath, LineShapeNode::m_text_alpha, text_color[3]);
    CHECK_MSTATUS(status);
    status = getNodeAttr(
        objPath, LineShapeNode::m_point_alpha, point_color[3]);
    CHECK_MSTATUS(status);
    status = getNodeAttr(
        objPath, LineShapeNode::m_inner_alpha, inner_color[3]);
    CHECK_MSTATUS(status);
    status = getNodeAttr(
        objPath, LineShapeNode::m_outer_alpha, outer_color[3]);
    CHECK_MSTATUS(status);

    // Line Width
    status = getNodeAttr(
        objPath, LineShapeNode::m_inner_line_width, data->m_inner_line_width);
    CHECK_MSTATUS(status);
    status = getNodeAttr(
        objPath, LineShapeNode::m_outer_line_width, data->m_outer_line_width);
    CHECK_MSTATUS(status);

    // Point Size
    status = getNodeAttr(
        objPath, LineShapeNode::m_point_size, data->m_point_size);
    CHECK_MSTATUS(status);

    // Draw Name
    status = getNodeAttr(
        objPath, LineShapeNode::m_draw_name, data->m_draw_name);
    CHECK_MSTATUS(status);

    // Colors
    float hue = 0.0;
    float sat = 0.0;
    float val = 0.0;
    float alpha = 0.0;
    auto display_status = MHWRender::MGeometryUtilities::displayStatus(objPath);
    if ((display_status == MHWRender::kLead)
        || (display_status == MHWRender::kLead)
        || (display_status == MHWRender::kActive)
        || (display_status == MHWRender::kHilite)
        || (display_status == MHWRender::kActiveComponent)) {
        // The line is selected/active.
        data->m_active = true;
        data->m_depth_priority = MHWRender::MRenderItem::sActiveWireDepthPriority;

        // Text
        text_color.get(MColor::kHSV, hue, sat, val, alpha);
        sat *= 0.95f;
        val *= 1.05f;
        text_color.set(MColor::kHSV, hue, sat, val, alpha);

        // Point
        point_color.get(MColor::kHSV, hue, sat, val, alpha);
        sat *= 0.95f;
        val *= 1.05f;
        point_color.set(MColor::kHSV, hue, sat, val, alpha);

        // Inner
        inner_color.get(MColor::kHSV, hue, sat, val, alpha);
        sat *= 0.95f;
        val *= 1.05f;
        inner_color.set(MColor::kHSV, hue, sat, val, alpha);

        // Outer
        outer_color.get(MColor::kHSV, hue, sat, val, alpha);
        sat *= 0.95f;
        val *= 1.05f;
        outer_color.set(MColor::kHSV, hue, sat, val, alpha);
    } else {
        // The line is not selected.
        data->m_active = false;
        data->m_depth_priority = MHWRender::MRenderItem::sDormantFilledDepthPriority;
    }
    data->m_text_color = text_color;
    data->m_point_color = point_color;
    data->m_inner_color = inner_color;
    data->m_outer_color = outer_color;

    // The positions of the lines.
    data->m_point_list.clear();
    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, LineShapeNode::m_matrix_array);
        if (!plug.isNull()) {
            uint32_t numElements = plug.evaluateNumElements();
            for (uint32_t i = 0; i < numElements; ++i) {
                MPlug plugElement = plug.elementByPhysicalIndex(i, &status);
                CHECK_MSTATUS(status);
                if (!plugElement.isNull()) {
                    MDataHandle dataHandle = plugElement.asMDataHandle(&status);
                    CHECK_MSTATUS(status);
                    MMatrix matrix = dataHandle.asMatrix();
                    MPoint point(matrix(3, 0), matrix(3, 1), matrix(3, 2));
                    data->m_point_list.append(point * obj_matrix);
                }
            }
        }
    }
    auto numberOfPoints = data->m_point_list.length();
    if (numberOfPoints == 0) {
        return data;
    }

    auto lastPointNum = numberOfPoints - 1;
    MPoint start_point = data->m_point_list[0];
    MPoint end_point = data->m_point_list[lastPointNum];

    return data;
}

void LineDrawOverride::addUIDrawables(
        const MDagPath &/*objPath*/,
        MHWRender::MUIDrawManager &drawManager,
        const MHWRender::MFrameContext &/*frameContext*/,
        const MUserData *userData) {
    MStatus status;
    LineDrawData *data = (LineDrawData *) userData;
    if (!data) {
        return;
    }
    const auto num_of_points = data->m_point_list.length();
    if (num_of_points == 0) {
        return;
    }

    const auto inverse_num_of_points = 1.0 / data->m_point_list.length();
    auto middle_point = MPoint();
    for (uint32_t i = 0; i < data->m_point_list.length(); i++) {
        MPoint pnt = data->m_point_list[i];
        middle_point += pnt * inverse_num_of_points;
    }

    const auto num_inner_points = num_of_points;
    const auto num_outer_points = 4;  // 2 lines with 2 points each.

    MPointArray inner_line_list(num_inner_points);
    for (uint32_t i = 0; i < (num_of_points - 1); i++) {
        auto index_a = i + 0;
        auto index_b = i + 1;
        MPoint pnt_a = data->m_point_list[index_a];
        MPoint pnt_b = data->m_point_list[index_b];
        inner_line_list.set(pnt_a, index_a);
        inner_line_list.set(pnt_b, index_b);
    }

    MPointArray outer_line_list(num_outer_points);
    auto first_point_index = 0;
    auto last_point_index = num_inner_points - 1;
    auto dir = MVector(data->m_point_list[first_point_index] - data->m_point_list[last_point_index]);
    dir.normalize();
    dir *= data->m_outer_scale;

    auto temp0 = data->m_point_list[first_point_index];
    auto temp1 = data->m_point_list[last_point_index];
    MPoint vertex0 = MPoint(
        temp0.x + dir.x,
        temp0.y + dir.y,
        temp0.z + dir.z);
    MPoint vertex1 = data->m_point_list[first_point_index];
    MPoint vertex2 = data->m_point_list[last_point_index];
    MPoint vertex3 = MPoint(
        temp1.x + (dir.x * -1.0),
        temp1.y + (dir.y * -1.0),
        temp1.z + (dir.z * -1.0));

    outer_line_list.set(vertex0, 0);
    outer_line_list.set(vertex1, 1);
    outer_line_list.set(vertex2, 2);
    outer_line_list.set(vertex3, 3);

    // Draw inner line
    {
        // X-Ray mode disregards depth testing and will always draw
        // on-top.
        drawManager.beginDrawable(MHWRender::MUIDrawManager::kSelectable);
        drawManager.setColor(data->m_inner_color);
        drawManager.setLineWidth(static_cast<float>(data->m_inner_line_width));
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.beginDrawInXray();
        drawManager.setColor(data->m_inner_color);
        drawManager.setLineWidth(static_cast<float>(data->m_inner_line_width));
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.mesh(
            MHWRender::MUIDrawManager::kLineStrip,
            inner_line_list);

        drawManager.endDrawInXray();
        drawManager.endDrawable();
    }

    // Draw outer line.
    {
        // X-Ray mode disregards depth testing and will always draw
        // on-top.
        drawManager.beginDrawable(MHWRender::MUIDrawManager::kSelectable);
        drawManager.setColor(data->m_outer_color);
        drawManager.setLineWidth(static_cast<float>(data->m_outer_line_width));
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.beginDrawInXray();
        drawManager.setColor(data->m_outer_color);
        drawManager.setLineWidth(static_cast<float>(data->m_outer_line_width));
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.mesh(
            MHWRender::MUIDrawManager::kLines,
            outer_line_list);

        drawManager.endDrawInXray();
        drawManager.endDrawable();
    }

    // Draw point directly in the center of the object transform.
    {
        // X-Ray mode disregards depth testing and will always draw
        // on-top.
        drawManager.beginDrawable(MHWRender::MUIDrawManager::kSelectable);
        drawManager.setColor(data->m_point_color);
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setPointSize(static_cast<float>(data->m_point_size));
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.beginDrawInXray();
        drawManager.setColor(data->m_point_color);
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setPointSize(static_cast<float>(data->m_point_size));
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.mesh(
            MHWRender::MUIDrawManager::kPoints,
            data->m_point_list);

        drawManager.endDrawInXray();
        drawManager.endDrawable();
    }

    // Draw text
    {
        // X-Ray mode disregards depth testing and will always draw
        // on-top.
        drawManager.beginDrawable(MHWRender::MUIDrawManager::kSelectable);
        drawManager.setColor(data->m_text_color);
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.beginDrawInXray();
        drawManager.setColor(data->m_text_color);
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        // TODO:
        // - Draw 'weight'.
        // - Draw 'frame deviation'.
        // - Draw 'average deviation'.
        // - Draw 'max deviation'.
        if (data->m_draw_name && data->m_active) {
            // TODO: Add attribute to multiply the font size.
            drawManager.setFontSize(MHWRender::MUIDrawManager::kDefaultFontSize);
            drawManager.text(middle_point, data->m_name, MHWRender::MUIDrawManager::kLeft);
        }

        drawManager.endDrawInXray();
        drawManager.endDrawable();
    }
}

} // namespace mmsolver
