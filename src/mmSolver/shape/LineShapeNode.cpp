/*
 * Copyright (C) 2021-2022 David Cattermole.
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
 * A line between 2 points, with the points and the extended line area
 * shown.
 *
 * The Line should draw on-top of all nodes, without depth-culling.
 *
 */

#include "LineShapeNode.h"

// Maya
#include <maya/MColor.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MDistance.h>
#include <maya/MFnCompoundAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnMatrixData.h>
#include <maya/MFnMessageAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MPlug.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MVector.h>

#if MAYA_API_VERSION >= 20190000
#include <maya/MEvaluationNode.h>
#include <maya/MViewport2Renderer.h>
#endif

// MM Solver
#include <mmcore/mmdata.h>
#include <mmcore/mmmath.h>

#include "LineDrawOverride.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/node/node_line_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

// MM SceneGraph
#include <mmscenegraph/mmscenegraph.h>

namespace mmsg = mmscenegraph;

namespace mmsolver {

MTypeId LineShapeNode::m_id(MM_LINE_SHAPE_TYPE_ID);
MString LineShapeNode::m_draw_db_classification(MM_LINE_DRAW_CLASSIFY);
MString LineShapeNode::m_draw_registrant_id(MM_LINE_DRAW_REGISTRANT_ID);
MString LineShapeNode::m_selection_type_name(MM_LINE_SHAPE_SELECTION_TYPE_NAME);
MString LineShapeNode::m_display_filter_name(MM_LINE_SHAPE_DISPLAY_FILTER_NAME);
MString LineShapeNode::m_display_filter_label(
    MM_LINE_SHAPE_DISPLAY_FILTER_LABEL);

// Display Attributes
MObject LineShapeNode::m_draw_name;
MObject LineShapeNode::m_draw_middle;
MObject LineShapeNode::m_color;
MObject LineShapeNode::m_alpha;
MObject LineShapeNode::m_inner_line_width;
MObject LineShapeNode::m_middle_line_width;
MObject LineShapeNode::m_point_size;

// Input Attributes
MObject LineShapeNode::m_objects;
MObject LineShapeNode::m_transform_matrix;
MObject LineShapeNode::m_parent_inverse_matrix;
MObject LineShapeNode::m_middle_scale;

// Output Attributes
MObject LineShapeNode::m_out_line_point_a;
MObject LineShapeNode::m_out_line_point_ax;
MObject LineShapeNode::m_out_line_point_ay;

MObject LineShapeNode::m_out_line_point_b;
MObject LineShapeNode::m_out_line_point_bx;
MObject LineShapeNode::m_out_line_point_by;

MObject LineShapeNode::m_out_line;
MObject LineShapeNode::m_out_line_center_x;
MObject LineShapeNode::m_out_line_center_y;
MObject LineShapeNode::m_out_line_dir_x;
MObject LineShapeNode::m_out_line_dir_y;
MObject LineShapeNode::m_out_line_slope;
MObject LineShapeNode::m_out_line_angle;

LineShapeNode::LineShapeNode() {}

LineShapeNode::~LineShapeNode() {}

MString LineShapeNode::nodeName() { return MString(MM_LINE_SHAPE_TYPE_NAME); }

MStatus LineShapeNode::compute(const MPlug &plug, MDataBlock &data) {
    MStatus status = MS::kUnknownParameter;

    // When 'true', verbose will print out additional details for
    // debugging.
    bool verbose = false;

    if ((plug == m_out_line_point_a) || (plug == m_out_line_point_ax) ||
        (plug == m_out_line_point_ay) || (plug == m_out_line_point_b) ||
        (plug == m_out_line_point_bx) || (plug == m_out_line_point_by) ||
        (plug == m_out_line) || (plug == m_out_line_center_x) ||
        (plug == m_out_line_center_y) || (plug == m_out_line_slope) ||
        (plug == m_out_line_angle)) {
        MObject this_node = MPxNode::thisMObject();

        // Get Parent Inverse Matrix
        MDagPath dag_path;
        MDagPath::getAPathTo(this_node, dag_path);
        MMatrix parentInverseMatrix = dag_path.exclusiveMatrixInverse();
        MMSOLVER_MAYA_VRB("parentInverseMatrix: " << parentInverseMatrix);

        MArrayDataHandle transformArrayHandle =
            data.inputArrayValue(m_transform_matrix, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        // Get Transform Positions
        status =
            query_line_point_data(parentInverseMatrix, transformArrayHandle,
                                  m_point_data_x, m_point_data_y, verbose);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        MDataHandle middleLineScaleHandle =
            data.inputValue(m_middle_scale, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        auto line_length = middleLineScaleHandle.asDouble();

        auto line_center = mmdata::Point2D();
        auto line_slope = 0.0;
        auto line_angle = 0.0;
        auto line_dir = mmdata::Vector2D(0.0, 1.0);
        auto line_point_a = mmdata::Point2D(-1.0, -1.0);
        auto line_point_b = mmdata::Point2D(1.0, 1.0);

        status =
            fit_line_to_points(line_length, m_point_data_x, m_point_data_y,
                               line_center, line_slope, line_angle, line_dir,
                               line_point_a, line_point_b, verbose);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

        // Output Points
        MDataHandle outLinePointAXHandle =
            data.outputValue(m_out_line_point_ax);
        MDataHandle outLinePointAYHandle =
            data.outputValue(m_out_line_point_ay);
        outLinePointAXHandle.setDouble(line_point_a.x_);
        outLinePointAYHandle.setDouble(line_point_a.y_);
        outLinePointAXHandle.setClean();
        outLinePointAYHandle.setClean();

        MDataHandle outLinePointBXHandle =
            data.outputValue(m_out_line_point_bx);
        MDataHandle outLinePointBYHandle =
            data.outputValue(m_out_line_point_by);
        outLinePointBXHandle.setDouble(line_point_b.x_);
        outLinePointBYHandle.setDouble(line_point_b.y_);
        outLinePointBXHandle.setClean();
        outLinePointBYHandle.setClean();

        // Output Line
        MDataHandle outLineCenterXHandle =
            data.outputValue(m_out_line_center_x);
        MDataHandle outLineCenterYHandle =
            data.outputValue(m_out_line_center_y);
        MDataHandle outLineDirXHandle = data.outputValue(m_out_line_dir_x);
        MDataHandle outLineDirYHandle = data.outputValue(m_out_line_dir_y);
        MDataHandle outLineSlopeHandle = data.outputValue(m_out_line_slope);
        MDataHandle outLineAngleHandle = data.outputValue(m_out_line_angle);
        outLineCenterXHandle.setDouble(line_center.x_);
        outLineCenterYHandle.setDouble(line_center.y_);
        outLineDirXHandle.setDouble(line_dir.x_);
        outLineDirYHandle.setDouble(line_dir.y_);
        outLineSlopeHandle.setDouble(line_slope);
        outLineAngleHandle.setDouble(line_angle);
        outLineCenterXHandle.setClean();
        outLineCenterYHandle.setClean();
        outLineDirXHandle.setClean();
        outLineDirYHandle.setClean();
        outLineSlopeHandle.setClean();
        outLineAngleHandle.setClean();
    }

    return status;
}

bool LineShapeNode::isBounded() const { return true; }

MBoundingBox LineShapeNode::boundingBox() const {
    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);

    double scale = 0.0;
    MObject thisNode = thisMObject();
    MPlug plug(thisNode, m_middle_scale);
    plug.getValue(scale);

    corner1 = corner1 * scale;
    corner2 = corner2 * scale;
    return MBoundingBox(corner1, corner2);
}

bool LineShapeNode::excludeAsLocator() const {
    // Returning 'false' here means that when the user toggles
    // locators on/off with the (per-viewport) "Show" menu, this shape
    // node will not be affected.
    return false;
}

// Called before this node is evaluated by Evaluation Manager
//
#if MAYA_API_VERSION >= 20190000
MStatus LineShapeNode::preEvaluation(const MDGContext &context,
                                     const MEvaluationNode &evaluationNode) {
    if (context.isNormal()) {
        MStatus status;
        bool ok = evaluationNode.dirtyPlugExists(m_objects, &status);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        if (ok) {
            MHWRender::MRenderer::setGeometryDrawDirty(thisMObject());
        }
    }

    return MStatus::kSuccess;
}
#endif

#if MAYA_API_VERSION >= 20200000
void LineShapeNode::getCacheSetup(const MEvaluationNode &evalNode,
                                  MNodeCacheDisablingInfo &disablingInfo,
                                  MNodeCacheSetupInfo &cacheSetupInfo,
                                  MObjectArray &monitoredAttributes) const {
    MPxLocatorNode::getCacheSetup(evalNode, disablingInfo, cacheSetupInfo,
                                  monitoredAttributes);
    MMSOLVER_ASSERT(!disablingInfo.getCacheDisabled(),
                    "Setting up the cache cannot be disabled.");
    cacheSetupInfo.setPreference(MNodeCacheSetupInfo::kWantToCacheByDefault,
                                 true);
}
#endif

void *LineShapeNode::creator() { return new LineShapeNode(); }

MStatus LineShapeNode::initialize() {
    MStatus status;
    MFnUnitAttribute uAttr;
    MFnNumericAttribute nAttr;
    MFnMessageAttribute msgAttr;
    MFnCompoundAttribute compoundAttr;
    MFnMatrixAttribute matrixAttr;

    // Draw Toggles.
    {
        m_draw_name =
            nAttr.create("drawName", "drwnm", MFnNumericData::kBoolean, 1);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

        m_draw_middle =
            nAttr.create("drawMiddle", "drwmid", MFnNumericData::kBoolean, 0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

        MMSOLVER_CHECK_MSTATUS(addAttribute(m_draw_name));
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_draw_middle));
    }

    // Color
    {
        m_color = nAttr.createColor("color", "clr");
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setDefault(1.0f, 0.0f, 1.0f));

        MMSOLVER_CHECK_MSTATUS(addAttribute(m_color));
    }

    // Alpha
    {
        auto alpha_min = 0.0;
        auto alpha_max = 1.0;
        auto alpha_default = 1.0;
        m_alpha = nAttr.create("alpha", "alp", MFnNumericData::kDouble,
                               alpha_default);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setMin(alpha_min));
        MMSOLVER_CHECK_MSTATUS(nAttr.setMax(alpha_max));

        MMSOLVER_CHECK_MSTATUS(addAttribute(m_alpha));
    }

    // Line Width
    {
        auto line_width_min = 0.01;
        auto line_width_soft_min = 0.1;
        auto line_width_soft_max = 10.0;
        m_inner_line_width = nAttr.create("innerLineWidth", "inrlnwd",
                                          MFnNumericData::kDouble, 1.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setMin(line_width_min));
        MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
        MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

        m_middle_line_width = nAttr.create("middleLineWidth", "midlnwd",
                                           MFnNumericData::kDouble, 1.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setMin(line_width_min));
        MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
        MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

        MMSOLVER_CHECK_MSTATUS(addAttribute(m_inner_line_width));
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_middle_line_width));
    }

    // Scale
    {
        auto scale_min = 0.0;
        m_middle_scale =
            nAttr.create("middleScale", "midscl", MFnNumericData::kDouble, 1.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setMin(scale_min));
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_middle_scale));
    }

    // Point size
    {
        auto point_size_min = 0.0;
        auto point_size_soft_min = 0.5;
        auto point_size_soft_max = 10.0;
        m_point_size =
            nAttr.create("pointSize", "ptsz", MFnNumericData::kDouble, 4.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setMin(point_size_min));
        MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(point_size_soft_min));
        MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(point_size_soft_max));
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_point_size));
    }

    // Objects
    {
        m_objects = msgAttr.create("objects", "objs", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(msgAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(msgAttr.setCached(true));
        MMSOLVER_CHECK_MSTATUS(msgAttr.setConnectable(true));
        MMSOLVER_CHECK_MSTATUS(msgAttr.setArray(true));
        MMSOLVER_CHECK_MSTATUS(msgAttr.setReadable(false));
        MMSOLVER_CHECK_MSTATUS(msgAttr.setWritable(true));
        MMSOLVER_CHECK_MSTATUS(msgAttr.setIndexMatters(false));
        MMSOLVER_CHECK_MSTATUS(msgAttr.setDisconnectBehavior(
            MFnAttribute::DisconnectBehavior::kDelete));
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_objects));
    }

    // (World-space) Transform Matrices.
    {
        m_transform_matrix = matrixAttr.create(
            "transformMatrix", "tfmmtx", MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setConnectable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setArray(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setDisconnectBehavior(
            MFnAttribute::DisconnectBehavior::kDelete));
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_transform_matrix));
    }

    // Parent Inverse Matrix
    //
    // Used to Move the 'm_transform_matrix' world-space matrices into
    // local space.
    {
        m_parent_inverse_matrix =
            matrixAttr.create("transformParentInverseMatrix", "tfmpinvm",
                              MFnMatrixAttribute::kDouble, &status);
        MMSOLVER_CHECK_MSTATUS(status);
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setStorable(true));
        MMSOLVER_CHECK_MSTATUS(matrixAttr.setConnectable(true));
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_parent_inverse_matrix));
    }

    // Out Line Point A
    {
        m_out_line_point_ax = nAttr.create("outLinePointAX", "opax",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));

        m_out_line_point_ay = nAttr.create("outLinePointAY", "opay",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));

        m_out_line_point_a =
            compoundAttr.create("outLinePointA", "opa", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(m_out_line_point_ax);
        compoundAttr.addChild(m_out_line_point_ay);
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_out_line_point_a));
    }

    // Out Line Point B
    {
        m_out_line_point_bx = nAttr.create("outLinePointBX", "opbx",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));

        m_out_line_point_by = nAttr.create("outLinePointBY", "opby",
                                           MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));

        m_out_line_point_b =
            compoundAttr.create("outLinePointB", "opb", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(m_out_line_point_bx);
        compoundAttr.addChild(m_out_line_point_by);
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_out_line_point_b));
    }

    {
        // Out Line Center X
        m_out_line_center_x =
            nAttr.create("outLineX", "olncx", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setWritable(false));

        // Out Line Center Y
        m_out_line_center_y =
            nAttr.create("outLineY", "olncy", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setWritable(false));

        // Out Line Direction X
        m_out_line_dir_x =
            nAttr.create("outLineDirX", "olndrx", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setWritable(false));

        // Out Line Direction Y
        m_out_line_dir_y =
            nAttr.create("outLineDirY", "olndry", MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setWritable(false));

        // Out Line Slope
        m_out_line_slope = nAttr.create("outLineSlope", "olnslp",
                                        MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setWritable(false));

        // Out Line Angle
        m_out_line_angle = nAttr.create("outLineAngle", "olnagl",
                                        MFnNumericData::kDouble, 0.0);
        MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(false));
        MMSOLVER_CHECK_MSTATUS(nAttr.setReadable(true));
        MMSOLVER_CHECK_MSTATUS(nAttr.setWritable(false));

        // Out Coord (parent of outLine* attributes)
        m_out_line = compoundAttr.create("outLine", "oln", &status);
        MMSOLVER_CHECK_MSTATUS(status);
        compoundAttr.addChild(m_out_line_center_x);
        compoundAttr.addChild(m_out_line_center_y);
        compoundAttr.addChild(m_out_line_dir_x);
        compoundAttr.addChild(m_out_line_dir_y);
        compoundAttr.addChild(m_out_line_slope);
        compoundAttr.addChild(m_out_line_angle);
        MMSOLVER_CHECK_MSTATUS(addAttribute(m_out_line));
    }

    // Attribute Affects
    MObjectArray inputAttrs;
    inputAttrs.append(m_objects);
    inputAttrs.append(m_transform_matrix);
    inputAttrs.append(m_parent_inverse_matrix);
    inputAttrs.append(m_middle_scale);

    MObjectArray outputAttrs;
    outputAttrs.append(m_out_line_point_a);
    outputAttrs.append(m_out_line_point_ax);
    outputAttrs.append(m_out_line_point_ay);

    outputAttrs.append(m_out_line_point_b);
    outputAttrs.append(m_out_line_point_bx);
    outputAttrs.append(m_out_line_point_by);

    outputAttrs.append(m_out_line);
    outputAttrs.append(m_out_line_center_x);
    outputAttrs.append(m_out_line_center_y);
    outputAttrs.append(m_out_line_dir_x);
    outputAttrs.append(m_out_line_dir_y);
    outputAttrs.append(m_out_line_slope);
    outputAttrs.append(m_out_line_angle);

    MMSOLVER_CHECK_MSTATUS(
        MMNodeInitUtils::attributeAffectsMulti(inputAttrs, outputAttrs));

    return MS::kSuccess;
}

}  // namespace mmsolver
