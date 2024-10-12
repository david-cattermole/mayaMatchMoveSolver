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
 * A marker should display as a red-coloured cross shape, with a dot
 * in the middle.
 *
 * The Marker should draw on-top of all nodes, without depth-culling,
 * and should always be at a phyisical depth of near clip-plane +
 * epsilon.
 *
 */

#include "MarkerShapeNode.h"

// Maya
#include <maya/MColor.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MDistance.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MPlug.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MVector.h>

#if MAYA_API_VERSION >= 20190000
#include <assert.h>
#include <maya/MEvaluationNode.h>
#include <maya/MViewport2Renderer.h>
#endif

// MM Solver
#include "MarkerConstants.h"
#include "MarkerDrawOverride.h"
#include "mmSolver/nodeTypeIds.h"

namespace mmsolver {

MTypeId MarkerShapeNode::m_id(MM_MARKER_SHAPE_TYPE_ID);
MString MarkerShapeNode::m_draw_db_classification(MM_MARKER_DRAW_CLASSIFY);
MString MarkerShapeNode::m_draw_registrant_id(MM_MARKER_DRAW_REGISTRANT_ID);
MString MarkerShapeNode::m_selection_type_name(
    MM_MARKER_SHAPE_SELECTION_TYPE_NAME);
MString MarkerShapeNode::m_display_filter_name(
    MM_MARKER_SHAPE_DISPLAY_FILTER_NAME);
MString MarkerShapeNode::m_display_filter_label(
    MM_MARKER_SHAPE_DISPLAY_FILTER_LABEL);

// Attributes
MObject MarkerShapeNode::m_color;
MObject MarkerShapeNode::m_alpha;
MObject MarkerShapeNode::m_line_width;
MObject MarkerShapeNode::m_point_size;
MObject MarkerShapeNode::m_icon_size;
MObject MarkerShapeNode::m_draw_name;
MObject MarkerShapeNode::m_show_in_camera_only;

MarkerShapeNode::MarkerShapeNode() {}

MarkerShapeNode::~MarkerShapeNode() {}

MString MarkerShapeNode::nodeName() {
    return MString(MM_MARKER_SHAPE_TYPE_NAME);
}

MStatus MarkerShapeNode::compute(const MPlug & /*plug*/,
                                 MDataBlock & /*dataBlock*/) {
    return MS::kUnknownParameter;
    ;
}

bool MarkerShapeNode::isBounded() const { return true; }

MBoundingBox MarkerShapeNode::boundingBox() const {
    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);

    double icon_size = 0.0;
    MObject thisNode = thisMObject();
    MPlug plug(thisNode, m_icon_size);
    plug.getValue(icon_size);

    corner1 = corner1 * icon_size;
    corner2 = corner2 * icon_size;
    return MBoundingBox(corner1, corner2);
}

bool MarkerShapeNode::excludeAsLocator() const {
    // Returning 'false' here means that when the user toggles
    // locators on/off with the (per-viewport) "Show" menu, this shape
    // node will not be affected.
    return false;
}

// Called before this node is evaluated by Evaluation Manager
//
#if MAYA_API_VERSION >= 20190000
MStatus MarkerShapeNode::preEvaluation(const MDGContext &context,
                                       const MEvaluationNode &evaluationNode) {
    if (context.isNormal()) {
        MStatus status;
        if (evaluationNode.dirtyPlugExists(m_icon_size, &status) && status) {
            MHWRender::MRenderer::setGeometryDrawDirty(thisMObject());
        }
    }

    return MStatus::kSuccess;
}
#endif

#if MAYA_API_VERSION >= 20200000
void MarkerShapeNode::getCacheSetup(const MEvaluationNode &evalNode,
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

void *MarkerShapeNode::creator() { return new MarkerShapeNode(); }

MStatus MarkerShapeNode::initialize() {
    MStatus status;
    MFnUnitAttribute uAttr;
    MFnNumericAttribute nAttr;

    // Color
    m_color = nAttr.createColor("color", "clr");
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setDefault(1.0f, 0.0f, 0.0f));

    // Alpha
    auto alpha_min = 0.0;
    auto alpha_max = 1.0;
    auto alpha_default = 1.0;
    m_alpha =
        nAttr.create("alpha", "alp", MFnNumericData::kDouble, alpha_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(alpha_min));
    CHECK_MSTATUS(nAttr.setMax(alpha_max));

    // Line Width
    auto line_width_min = 0.01;
    auto line_width_soft_min = 0.1;
    auto line_width_soft_max = 10.0;
    m_line_width =
        nAttr.create("lineWidth", "lnwd", MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(line_width_min));
    CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    // Point size
    auto point_size_min = 0.0;
    auto point_size_soft_min = 0.5;
    auto point_size_soft_max = 10.0;
    m_point_size =
        nAttr.create("pointSize", "ptsz", MFnNumericData::kDouble, 4.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(point_size_min));
    CHECK_MSTATUS(nAttr.setSoftMin(point_size_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(point_size_soft_max));

    // icon size
    auto icon_size_min = 0.0;
    m_icon_size =
        nAttr.create("iconSize", "icnsz", MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(icon_size_min));

    // Draw Name
    m_draw_name =
        nAttr.create("drawName", "drwnm", MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    // Show In Camera Only
    m_show_in_camera_only = nAttr.create("showInCameraOnly", "shwcamony",
                                         MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    // Add attributes
    CHECK_MSTATUS(addAttribute(m_icon_size));
    CHECK_MSTATUS(addAttribute(m_draw_name));
    CHECK_MSTATUS(addAttribute(m_color));
    CHECK_MSTATUS(addAttribute(m_alpha));
    CHECK_MSTATUS(addAttribute(m_line_width));
    CHECK_MSTATUS(addAttribute(m_point_size));
    CHECK_MSTATUS(addAttribute(m_show_in_camera_only));

    return MS::kSuccess;
}

}  // namespace mmsolver
