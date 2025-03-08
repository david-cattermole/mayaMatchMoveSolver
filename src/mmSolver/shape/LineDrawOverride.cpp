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
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MEventMessage.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MFnMatrixData.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MPoint.h>
#include <maya/MPointArray.h>
#include <maya/MString.h>
#include <maya/MTransformationMatrix.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>
#include <maya/MHWGeometryUtilities.h>
#include <maya/MPxDrawOverride.h>
#include <maya/MUserData.h>

// MM Solver Libs
#include <mmcore/mmdata.h>

// MM Solver
#include "LineConstants.h"
#include "ShapeConstants.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/node/node_line_utils.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/number_utils.h"

// MM SceneGraph
#include <mmscenegraph/mmscenegraph.h>

namespace mmsg = mmscenegraph;

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
                                 /*callback=*/nullptr,
                                 /*isAlwaysDirty=*/true) {
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
        MHWRender::MRenderer::setGeometryDrawDirty(ovr->m_node->thisMObject());
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
    const MDagPath &objPath, const MDagPath & /*cameraPath*/) const {
    MStatus status;

    MPoint corner1;
    MPoint corner2;

    MObject node = objPath.node(&status);
    if (status) {
        MPlug plug(node, LineShapeNode::m_objects);
        if (!plug.isNull()) {
            double x = 0.0;
            double y = 0.0;
            double z = 0.0;

            uint32_t numElements = plug.evaluateNumElements();
            for (uint32_t i = 0; i < numElements; ++i) {
                MPlug plugElement = plug.elementByPhysicalIndex(i, &status);
                CHECK_MSTATUS(status);
                if (!plugElement.isNull()) {
                    status =
                        get_position_from_connected_node(plugElement, x, y, z);
                    CHECK_MSTATUS(status);

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
    const MDagPath &objPath, const MDagPath & /*cameraPath*/,
    const MHWRender::MFrameContext & /*frameContext*/, MUserData *oldData) {
    LineDrawData *data = dynamic_cast<LineDrawData *>(oldData);
    if (!data) {
        data = new LineDrawData();
    }
    MStatus status;

    // When 'true', verbose will print out additional details for
    // debugging.
    bool verbose = false;

    MDagPath transformPath(objPath);
    CHECK_MSTATUS(transformPath.pop(1));
    MObject transformObj = transformPath.node();
    MFnDependencyNode dependNodeFn(transformObj);
    data->m_name = dependNodeFn.name();

    // The object's transform matrix
    MMatrix matrix_inverse = objPath.exclusiveMatrixInverse(&status);
    CHECK_MSTATUS(status);
    MMatrix obj_matrix = matrix_inverse;

    status = getNodeAttr(objPath, LineShapeNode::m_middle_scale,
                         data->m_middle_scale);
    CHECK_MSTATUS(status);

    // Color
    MColor color1(0.0f, 0.0f, 0.0f, 1.0f);
    status = getNodeAttr(objPath, LineShapeNode::m_color, color1);
    CHECK_MSTATUS(status);

    // Alpha
    status = getNodeAttr(objPath, LineShapeNode::m_alpha, color1[3]);
    CHECK_MSTATUS(status);

    // Line Width
    status = getNodeAttr(objPath, LineShapeNode::m_inner_line_width,
                         data->m_inner_line_width);
    CHECK_MSTATUS(status);

    // Point Size
    status =
        getNodeAttr(objPath, LineShapeNode::m_point_size, data->m_point_size);
    CHECK_MSTATUS(status);

    // Draw Name
    status =
        getNodeAttr(objPath, LineShapeNode::m_draw_name, data->m_draw_name);
    CHECK_MSTATUS(status);

    // Draw Middle
    status =
        getNodeAttr(objPath, LineShapeNode::m_draw_middle, data->m_draw_middle);
    CHECK_MSTATUS(status);

    // Create secondary color.
    MColor color2(0.0f, 0.0f, 0.0f, 1.0f);
    float hue = 0.0;
    float sat = 0.0;
    float val = 0.0;
    float alpha = 0.0;
    color1.get(MColor::kHSV, hue, sat, val, alpha);
    sat *= color_secondary_saturation_factor;
    alpha *= color_secondary_alpha_factor;
    color2.set(MColor::kHSV, hue, sat, val, alpha);

    // Adjust colors due to state.
    auto display_status = MHWRender::MGeometryUtilities::displayStatus(objPath);
    if ((display_status == MHWRender::kLead) ||
        (display_status == MHWRender::kActive) ||
        (display_status == MHWRender::kHilite) ||
        (display_status == MHWRender::kActiveComponent)) {
        // The line is selected/active.
        data->m_active = true;
        data->m_depth_priority =
            MHWRender::MRenderItem::sActiveWireDepthPriority;

        // Primary Color
        color1.get(MColor::kHSV, hue, sat, val, alpha);
        sat *= selection_saturation_factor;
        val *= selection_value_factor;
        color1.set(MColor::kHSV, hue, sat, val, alpha);

        // Secondary Color
        color2.get(MColor::kHSV, hue, sat, val, alpha);
        sat *= selection_saturation_factor;
        val *= selection_value_factor;
        color2.set(MColor::kHSV, hue, sat, val, alpha);
    } else {
        // The line is not selected.
        data->m_active = false;
        data->m_depth_priority =
            MHWRender::MRenderItem::sDormantFilledDepthPriority;
    }
    data->m_color1 = color1;
    data->m_color2 = color2;

    // The positions of the lines.
    data->m_point_data_x.clear();
    data->m_point_data_y.clear();
    data->m_point_list.clear();
    MObject node = objPath.node(&status);
    if (status == MStatus::kSuccess) {
        MPoint point;

        MPlug plug(node, LineShapeNode::m_objects);
        if (!plug.isNull()) {
            uint32_t numElements = plug.evaluateNumElements();
            for (uint32_t i = 0; i < numElements; ++i) {
                MPlug plugElement = plug.elementByPhysicalIndex(i, &status);
                CHECK_MSTATUS(status);
                if (!plugElement.isNull()) {
                    double x = 0.0;
                    double y = 0.0;
                    double z = 0.0;
                    status =
                        get_position_from_connected_node(plugElement, x, y, z);
                    CHECK_MSTATUS(status);

                    point = MPoint(x, y, z);
                    point = point * obj_matrix;
                    data->m_point_list.append(point);
                    data->m_point_data_x.push_back(point.x);
                    data->m_point_data_y.push_back(point.y);

                    MMSOLVER_MAYA_VRB("Point X: " << data->m_point_data_x.size()
                                                  << " : " << point.x);
                    MMSOLVER_MAYA_VRB("Point Y: " << data->m_point_data_y.size()
                                                  << " : " << point.y);
                }
            }
        }
    }
    MMSOLVER_MAYA_VRB(
        "data->m_point_data_x.size(): " << data->m_point_data_x.size());
    MMSOLVER_MAYA_VRB(
        "data->m_point_data_y.size(): " << data->m_point_data_y.size());

    auto numberOfPoints = data->m_point_list.length();
    if (numberOfPoints == 0) {
        return data;
    }

    // Middle line point data.
    {
        auto line_length = data->m_middle_scale;
        auto line_center = mmdata::Point2D();
        auto line_slope = 0.0;
        auto line_angle = 0.0;
        auto line_dir = mmdata::Vector2D();
        auto line_point_a = mmdata::Point2D();
        auto line_point_b = mmdata::Point2D();

        status = fit_line_to_points(line_length, data->m_point_data_x,
                                    data->m_point_data_y, line_center,
                                    line_slope, line_angle, line_dir,
                                    line_point_a, line_point_b, verbose);
        if (status == MS::kSuccess) {
            // Convert line center point and slope to 2 points to make
            // up a line we can draw between.
            data->m_middle_point_a.x = line_point_a.x_;
            data->m_middle_point_a.y = line_point_a.y_;
            data->m_middle_point_a.z = -1.0;

            data->m_middle_point_b.x = line_point_b.x_;
            data->m_middle_point_b.y = line_point_b.y_;
            data->m_middle_point_b.z = -1.0;
        }
    }

    return data;
}

void LineDrawOverride::addUIDrawables(
    const MDagPath & /*objPath*/, MHWRender::MUIDrawManager &drawManager,
    const MHWRender::MFrameContext & /*frameContext*/,
    const MUserData *userData) {
    MStatus status;
    LineDrawData *data = (LineDrawData *)userData;
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

    MPointArray inner_line_list(num_of_points);
    for (uint32_t i = 0; i < (num_of_points - 1); i++) {
        auto index_a = i + 0;
        auto index_b = i + 1;
        MPoint pnt_a = data->m_point_list[index_a];
        MPoint pnt_b = data->m_point_list[index_b];
        inner_line_list.set(pnt_a, index_a);
        inner_line_list.set(pnt_b, index_b);
    }

    MPointArray mid_line_list(2);
    mid_line_list.set(data->m_middle_point_a, 0);
    mid_line_list.set(data->m_middle_point_b, 1);

    // Draw middle line.
    //
    // The "best-fit" straight line between points. This is drawn
    // first, so that subsequent draw calls will render over the top
    // of this middle line.
    if (data->m_draw_middle) {
        // X-Ray mode disregards depth testing and will always draw
        // on-top.
        drawManager.beginDrawable(MHWRender::MUIDrawManager::kSelectable);
        drawManager.setColor(data->m_color2);
        drawManager.setLineWidth(static_cast<float>(data->m_middle_line_width));
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.beginDrawInXray();
        drawManager.setColor(data->m_color2);
        drawManager.setLineWidth(static_cast<float>(data->m_middle_line_width));
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.mesh(MHWRender::MUIDrawManager::kLines, mid_line_list);

        drawManager.endDrawInXray();
        drawManager.endDrawable();
    }

    // Draw inner line
    {
        // X-Ray mode disregards depth testing and will always draw
        // on-top.
        drawManager.beginDrawable(MHWRender::MUIDrawManager::kSelectable);
        drawManager.setColor(data->m_color1);
        drawManager.setLineWidth(static_cast<float>(data->m_inner_line_width));
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.beginDrawInXray();
        drawManager.setColor(data->m_color1);
        drawManager.setLineWidth(static_cast<float>(data->m_inner_line_width));
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.mesh(MHWRender::MUIDrawManager::kLineStrip,
                         inner_line_list);

        drawManager.endDrawInXray();
        drawManager.endDrawable();
    }

    // Draw point directly in the center of the object transform.
    {
        // X-Ray mode disregards depth testing and will always draw
        // on-top.
        drawManager.beginDrawable(MHWRender::MUIDrawManager::kSelectable);
        drawManager.setColor(data->m_color1);
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setPointSize(static_cast<float>(data->m_point_size));
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.beginDrawInXray();
        drawManager.setColor(data->m_color1);
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setPointSize(static_cast<float>(data->m_point_size));
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.mesh(MHWRender::MUIDrawManager::kPoints,
                         data->m_point_list);

        drawManager.endDrawInXray();
        drawManager.endDrawable();
    }

    // Draw text
    {
        // X-Ray mode disregards depth testing and will always draw
        // on-top.
        drawManager.beginDrawable(MHWRender::MUIDrawManager::kSelectable);
        drawManager.setColor(data->m_color1);
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        drawManager.beginDrawInXray();
        drawManager.setColor(data->m_color1);
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setDepthPriority(data->m_depth_priority);

        // TODO:
        // - Draw 'weight'.
        // - Draw 'frame deviation'.
        // - Draw 'average deviation'.
        // - Draw 'max deviation'.
        if (data->m_draw_name && data->m_active) {
            // TODO: Add attribute to multiply the font size.
            drawManager.setFontSize(
                MHWRender::MUIDrawManager::kDefaultFontSize);
            drawManager.text(middle_point, data->m_name,
                             MHWRender::MUIDrawManager::kLeft);
        }

        drawManager.endDrawInXray();
        drawManager.endDrawable();
    }
}

}  // namespace mmsolver
