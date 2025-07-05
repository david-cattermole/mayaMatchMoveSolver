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

#include "BundleDrawOverride.h"

// Maya
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MEventMessage.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MPlug.h>
#include <maya/MPoint.h>
#include <maya/MString.h>
#include <maya/MTransformationMatrix.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>
#include <maya/MHWGeometryUtilities.h>
#include <maya/MPxDrawOverride.h>
#include <maya/MUserData.h>

// MM Solver
#include "BundleConstants.h"
#include "ShapeConstants.h"
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
BundleDrawOverride::BundleDrawOverride(const MObject &obj)
    : MHWRender::MPxDrawOverride(obj,
                                 /*callback=*/nullptr,
                                 /*isAlwaysDirty=*/true) {
    m_model_editor_changed_callback_id = MEventMessage::addEventCallback(
        "modelEditorChanged", on_model_editor_changed_func, this);

    MStatus status;
    MFnDependencyNode node(obj, &status);
    m_node =
        status ? dynamic_cast<BundleShapeNode *>(node.userNode()) : nullptr;
}

BundleDrawOverride::~BundleDrawOverride() {
    m_node = nullptr;

    if (m_model_editor_changed_callback_id != 0) {
        MMessage::removeCallback(m_model_editor_changed_callback_id);
        m_model_editor_changed_callback_id = 0;
    }
}

void BundleDrawOverride::on_model_editor_changed_func(void *clientData) {
    // Mark the node as being dirty so that it can update on display appearance
    // switch among wireframe and shaded.
    BundleDrawOverride *ovr = static_cast<BundleDrawOverride *>(clientData);
    if (ovr && ovr->m_node) {
        MHWRender::MRenderer::setGeometryDrawDirty(ovr->m_node->thisMObject());
    }
}

MHWRender::DrawAPI BundleDrawOverride::supportedDrawAPIs() const {
    return (MHWRender::kOpenGL | MHWRender::kDirectX11 |
            MHWRender::kOpenGLCoreProfile);
}

bool BundleDrawOverride::isBounded(const MDagPath & /*objPath*/,
                                   const MDagPath & /*cameraPath*/) const {
    return true;
}

MBoundingBox BundleDrawOverride::boundingBox(
    const MDagPath &objPath, const MDagPath & /*cameraPath*/) const {
    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);

    double icon_size = 0.0;
    MStatus status =
        getNodeAttr(objPath, BundleShapeNode::m_icon_size, icon_size);

    corner1 = corner1 * icon_size;
    corner2 = corner2 * icon_size;
    return MBoundingBox(corner1, corner2);
}

// Called by Maya each time the object needs to be drawn.
MUserData *BundleDrawOverride::prepareForDraw(
    const MDagPath &objPath, const MDagPath & /*cameraPath*/,
    const MHWRender::MFrameContext &frameContext, MUserData *oldData) {
    BundleDrawData *data = dynamic_cast<BundleDrawData *>(oldData);
    if (!data) {
        data = new BundleDrawData();
    }
    MStatus status;

    MDagPath transformPath(objPath);
    MMSOLVER_CHECK_MSTATUS(transformPath.pop(1));
    MObject transformObj = transformPath.node();
    MFnDependencyNode dependNodeFn(transformObj);
    data->m_name = dependNodeFn.name();

    MDoubleArray pixel_size_array =
        frameContext.getTuple(MFrameContext::kViewportPixelSize, &status);
    MMSOLVER_CHECK_MSTATUS(status);
    double pixel_size_x = 1.0 / pixel_size_array[0];

    double icon_size = 0.0;
    status = getNodeAttr(objPath, BundleShapeNode::m_icon_size, icon_size);
    MMSOLVER_CHECK_MSTATUS(status);
    data->m_icon_size = icon_size * pixel_size_x;

    MColor user_color(0.0f, 0.0f, 0.0f, 0.0f);
    status = getNodeAttr(objPath, BundleShapeNode::m_color, user_color);
    MMSOLVER_CHECK_MSTATUS(status);
    status = getNodeAttr(objPath, BundleShapeNode::m_alpha, user_color[3]);
    MMSOLVER_CHECK_MSTATUS(status);
    status =
        getNodeAttr(objPath, BundleShapeNode::m_line_width, data->m_line_width);
    MMSOLVER_CHECK_MSTATUS(status);
    status =
        getNodeAttr(objPath, BundleShapeNode::m_point_size, data->m_point_size);
    MMSOLVER_CHECK_MSTATUS(status);
    status =
        getNodeAttr(objPath, BundleShapeNode::m_draw_name, data->m_draw_name);
    MMSOLVER_CHECK_MSTATUS(status);
    status = getNodeAttr(objPath, BundleShapeNode::m_draw_on_top,
                         data->m_draw_on_top);
    MMSOLVER_CHECK_MSTATUS(status);

    // The cross icon
    data->m_cross_line_list.clear();
    for (int i = 0; i < cross_shape_points_count; i++) {
        data->m_cross_line_list.append(cross_shape_points[i][0],
                                       cross_shape_points[i][1],
                                       cross_shape_points[i][2]);
    }

    data->m_cross_line_index_list.clear();
    for (int i = 0; i < cross_shape_line_indexes_count; i++) {
        data->m_cross_line_index_list.append(cross_shape_line_indexes[i][0]);
        data->m_cross_line_index_list.append(cross_shape_line_indexes[i][1]);
    }

    auto display_status = MHWRender::MGeometryUtilities::displayStatus(objPath);
    if ((display_status == MHWRender::kLead) ||
        (display_status == MHWRender::kActive) ||
        (display_status == MHWRender::kHilite) ||
        (display_status == MHWRender::kActiveComponent)) {
        // The bundle is selected/active.
        data->m_active = true;
        data->m_depth_priority =
            MHWRender::MRenderItem::sActiveWireDepthPriority;

        float hue = 0.0;
        float sat = 0.0;
        float val = 0.0;
        float alpha = 0.0;
        user_color.get(MColor::kHSV, hue, sat, val, alpha);
        sat *= selection_saturation_factor;
        val *= selection_value_factor;
        user_color.set(MColor::kHSV, hue, sat, val, alpha);
    } else {
        // The bundle is not selected.
        data->m_active = false;
        data->m_depth_priority =
            MHWRender::MRenderItem::sDormantFilledDepthPriority;
    }
    data->m_color = user_color;

    return data;
}

void BundleDrawOverride::addUIDrawables(
    const MDagPath &objPath, MHWRender::MUIDrawManager &drawManager,
    const MHWRender::MFrameContext &frameContext, const MUserData *userData) {
    MStatus status;
    BundleDrawData *data = (BundleDrawData *)userData;
    if (!data) {
        return;
    }

    // Get the camera position.
    MDoubleArray view_pos =
        frameContext.getTuple(MFrameContext::kViewPosition, &status);
    MMSOLVER_CHECK_MSTATUS(status);
    MPoint camera_pos(view_pos[0], view_pos[1], view_pos[2]);

    // The object's transform matrix
    MMatrix matrix = objPath.inclusiveMatrix(&status);
    MMSOLVER_CHECK_MSTATUS(status);
    MMatrix matrix_inverse = objPath.inclusiveMatrixInverse(&status);
    MMSOLVER_CHECK_MSTATUS(status);

    // Remove scale and shear from marker transform.
    MTransformationMatrix tfm_matrix(matrix);
    const double tfm_shear[] = {0.0, 0.0, 0.0};
    const double tfm_scale[] = {1.0, 1.0, 1.0};
    tfm_matrix.setShear(tfm_shear, MSpace::kObject);
    tfm_matrix.setScale(tfm_scale, MSpace::kObject);
    MMatrix obj_matrix = tfm_matrix.asMatrix() * matrix_inverse;

    // Get distance from camera to transform center.
    MPoint origin(0.0, 0.0, 0.0);
    origin *= matrix;
    double scale = camera_pos.distanceTo(origin) * data->m_icon_size;
    MPointArray cross_line_list(data->m_cross_line_list.length());
    for (uint32_t i = 0; i < data->m_cross_line_list.length(); i++) {
        MPoint orig = data->m_cross_line_list[i];
        MPoint pnt = MPoint(orig.x * scale, orig.y * scale, orig.z * scale);
        cross_line_list.set(pnt * obj_matrix, i);
    }

    drawManager.beginDrawable(MHWRender::MUIDrawManager::kSelectable);
    drawManager.setColor(data->m_color);
    drawManager.setLineWidth(static_cast<float>(data->m_line_width));
    drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
    drawManager.setPointSize(static_cast<float>(data->m_point_size));
    drawManager.setDepthPriority(data->m_depth_priority);

    // X-Ray mode disregards depth testing and will always draw
    // on-top.
    if (data->m_draw_on_top) {
        drawManager.beginDrawInXray();
        drawManager.setColor(data->m_color);
        drawManager.setLineWidth(static_cast<float>(data->m_line_width));
        drawManager.setLineStyle(MHWRender::MUIDrawManager::kSolid);
        drawManager.setPointSize(static_cast<float>(data->m_point_size));
        drawManager.setDepthPriority(data->m_depth_priority);
    }

    // Draw point directly in the center of the object transform.
    MPointArray point_list(1);
    drawManager.mesh(MHWRender::MUIDrawManager::kPoints, point_list);

    // Draw cross
    drawManager.mesh(MHWRender::MUIDrawManager::kLines, cross_line_list,
                     nullptr, nullptr, &data->m_cross_line_index_list);

    if (data->m_draw_on_top) {
        drawManager.endDrawInXray();
    }

    // Draw text
    MPoint pos(1.1 * scale, -1.1 * scale, 0.0);
    pos *= obj_matrix;
    if (data->m_draw_name && data->m_active) {
        // TODO: Add attribute to multiply the font size.
        drawManager.setColor(data->m_color);
        drawManager.setFontSize(MHWRender::MUIDrawManager::kDefaultFontSize);
        drawManager.text(pos, data->m_name, MHWRender::MUIDrawManager::kLeft);
    }

    drawManager.endDrawable();
}

}  // namespace mmsolver
