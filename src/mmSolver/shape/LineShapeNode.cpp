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
 * A line between 2 points, with the points and the extended line area
 * shown.
 *
 * The Line should draw on-top of all nodes, without depth-culling.
 *
 */

#include "LineShapeNode.h"

// Maya
#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MVector.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMatrixAttribute.h>
#include <maya/MFnNumericData.h>

#if MAYA_API_VERSION >= 20190000
#include <maya/MViewport2Renderer.h>
#include <maya/MEvaluationNode.h>
#include <assert.h>
#endif

// MM Solver
#include "mmSolver/nodeTypeIds.h"
#include "LineDrawOverride.h"

namespace mmsolver {

MTypeId LineShapeNode::m_id(MM_LINE_SHAPE_TYPE_ID);
MString LineShapeNode::m_draw_db_classification(MM_LINE_DRAW_CLASSIFY);
MString LineShapeNode::m_draw_registrant_id(MM_LINE_DRAW_REGISTRANT_ID);
MString LineShapeNode::m_selection_type_name(MM_LINE_SHAPE_SELECTION_TYPE_NAME);
MString LineShapeNode::m_display_filter_name(MM_LINE_SHAPE_DISPLAY_FILTER_NAME);
MString LineShapeNode::m_display_filter_label(MM_LINE_SHAPE_DISPLAY_FILTER_LABEL);

// Attributes
MObject LineShapeNode::m_draw_name;
MObject LineShapeNode::m_text_color;
MObject LineShapeNode::m_point_color;
MObject LineShapeNode::m_inner_color;
MObject LineShapeNode::m_outer_color;
MObject LineShapeNode::m_text_alpha;
MObject LineShapeNode::m_point_alpha;
MObject LineShapeNode::m_inner_alpha;
MObject LineShapeNode::m_outer_alpha;
MObject LineShapeNode::m_inner_line_width;
MObject LineShapeNode::m_outer_line_width;
MObject LineShapeNode::m_outer_scale;
MObject LineShapeNode::m_point_size;
MObject LineShapeNode::m_matrix_array;

LineShapeNode::LineShapeNode() {}

LineShapeNode::~LineShapeNode() {}

MString LineShapeNode::nodeName() {
    return MString(MM_LINE_SHAPE_TYPE_NAME);
}

MStatus
LineShapeNode::compute(const MPlug &/*plug*/,
                         MDataBlock &/*dataBlock*/) {
    return MS::kUnknownParameter;
}

bool LineShapeNode::isBounded() const {
    return true;
}

MBoundingBox LineShapeNode::boundingBox() const
{
    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);

    double scale = 0.0;
    MObject thisNode = thisMObject();
    MPlug plug(thisNode, m_outer_scale);
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
MStatus LineShapeNode::preEvaluation(
        const MDGContext &context,
        const MEvaluationNode &evaluationNode) {
    if (context.isNormal()) {
        MStatus status;
        bool ok = evaluationNode.dirtyPlugExists(m_matrix_array, &status);
        CHECK_MSTATUS_AND_RETURN_IT(status);
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
    assert(!disablingInfo.getCacheDisabled());
    cacheSetupInfo.setPreference(MNodeCacheSetupInfo::kWantToCacheByDefault,
                                 true);
}
#endif

void *LineShapeNode::creator() {
    return new LineShapeNode();
}

MStatus LineShapeNode::initialize() {
    MStatus status;
    MFnUnitAttribute uAttr;
    MFnNumericAttribute nAttr;
    MFnEnumAttribute eAttr;
    MFnMatrixAttribute matrixAttr;

    // Draw Name
    m_draw_name = nAttr.create(
            "drawName", "drwnm",
            MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    // Color
    m_text_color = nAttr.createColor(
            "textColor", "txtclr");
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setDefault(1.0f, 0.0f, 1.0f));

    m_point_color = nAttr.createColor(
            "pointColor", "pntclr");
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setDefault(1.0f, 0.0f, 1.0f));

    m_inner_color = nAttr.createColor(
            "innerColor", "inrclr");
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setDefault(1.0f, 0.0f, 1.0f));

    m_outer_color = nAttr.createColor(
            "outerColor", "otrclr");
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setDefault(1.0f, 0.5f, 1.0f));

    // Alpha
    auto alpha_min = 0.0;
    auto alpha_max = 1.0;
    auto alpha_default = 1.0;
    m_text_alpha = nAttr.create(
            "textAlpha", "txtalp",
            MFnNumericData::kDouble, alpha_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(alpha_min));
    CHECK_MSTATUS(nAttr.setMax(alpha_max));

    m_point_alpha = nAttr.create(
        "pointAlpha", "pntalp",
        MFnNumericData::kDouble, alpha_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(alpha_min));
    CHECK_MSTATUS(nAttr.setMax(alpha_max));

    m_inner_alpha = nAttr.create(
            "innerAlpha", "inralp",
            MFnNumericData::kDouble, alpha_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(alpha_min));
    CHECK_MSTATUS(nAttr.setMax(alpha_max));

    m_outer_alpha = nAttr.create(
            "outerAlpha", "otralp",
            MFnNumericData::kDouble, alpha_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(alpha_min));
    CHECK_MSTATUS(nAttr.setMax(alpha_max));

    // Line Width
    auto line_width_min = 0.01;
    auto line_width_soft_min = 0.1;
    auto line_width_soft_max = 10.0;
    m_inner_line_width = nAttr.create(
            "innerLineWidth", "inrlnwd",
            MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(line_width_min));
    CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    m_outer_line_width = nAttr.create(
            "outerLineWidth", "otrlnwd",
            MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(line_width_min));
    CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    // Scale
    auto scale_min = 0.0;
    m_outer_scale = nAttr.create(
        "outerScale", "otrscl",
        MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(scale_min));

    // Point size
    auto point_size_min = 0.0;
    auto point_size_soft_min = 0.5;
    auto point_size_soft_max = 10.0;
    m_point_size = nAttr.create(
            "pointSize", "ptsz",
            MFnNumericData::kDouble, 4.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(point_size_min));
    CHECK_MSTATUS(nAttr.setSoftMin(point_size_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(point_size_soft_max));

    // Matrix
    m_matrix_array = matrixAttr.create(
        "matrixArray", "mtxarry",
        MFnMatrixAttribute::kDouble, &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(matrixAttr.setStorable(true));
    CHECK_MSTATUS(matrixAttr.setConnectable(true));
    CHECK_MSTATUS(matrixAttr.setArray(true));
    CHECK_MSTATUS(matrixAttr.setReadable(false));
    CHECK_MSTATUS(matrixAttr.setWritable(true));
    CHECK_MSTATUS(matrixAttr.setIndexMatters(false));
    CHECK_MSTATUS(matrixAttr.setDisconnectBehavior(
                      MFnAttribute::DisconnectBehavior::kDelete));

    // Add attributes
    CHECK_MSTATUS(addAttribute(m_draw_name));
    CHECK_MSTATUS(addAttribute(m_text_color));
    CHECK_MSTATUS(addAttribute(m_point_color));
    CHECK_MSTATUS(addAttribute(m_inner_color));
    CHECK_MSTATUS(addAttribute(m_outer_color));
    CHECK_MSTATUS(addAttribute(m_text_alpha));
    CHECK_MSTATUS(addAttribute(m_point_alpha));
    CHECK_MSTATUS(addAttribute(m_inner_alpha));
    CHECK_MSTATUS(addAttribute(m_outer_alpha));
    CHECK_MSTATUS(addAttribute(m_point_size));
    CHECK_MSTATUS(addAttribute(m_outer_scale));
    CHECK_MSTATUS(addAttribute(m_inner_line_width));
    CHECK_MSTATUS(addAttribute(m_outer_line_width));
    CHECK_MSTATUS(addAttribute(m_matrix_array));

    return MS::kSuccess;
}

} // namespace mmsolver
