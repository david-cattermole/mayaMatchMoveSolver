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
 * A bundle should display as a red-coloured cross shape, with a dot
 * in the middle.
 *
 * The Bundle should draw on-top of all nodes, without depth-culling,
 * and should always be at a phyisical depth of near clip-plane +
 * epsilon.
 *
 */

#include "BundleShapeNode.h"

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
#include <maya/MEvaluationNode.h>
#endif

#include "BundleConstants.h"
#include "BundleDrawOverride.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

MTypeId BundleShapeNode::m_id(MM_BUNDLE_SHAPE_TYPE_ID);
MString BundleShapeNode::m_draw_db_classification(MM_BUNDLE_DRAW_CLASSIFY);
MString BundleShapeNode::m_draw_registrant_id(MM_BUNDLE_DRAW_REGISTRANT_ID);
MString BundleShapeNode::m_selection_type_name(
    MM_BUNDLE_SHAPE_SELECTION_TYPE_NAME);
MString BundleShapeNode::m_display_filter_name(
    MM_BUNDLE_SHAPE_DISPLAY_FILTER_NAME);
MString BundleShapeNode::m_display_filter_label(
    MM_BUNDLE_SHAPE_DISPLAY_FILTER_LABEL);

// Attributes
MObject BundleShapeNode::m_color;
MObject BundleShapeNode::m_alpha;
MObject BundleShapeNode::m_line_width;
MObject BundleShapeNode::m_point_size;
MObject BundleShapeNode::m_icon_size;
MObject BundleShapeNode::m_draw_name;
MObject BundleShapeNode::m_draw_on_top;

BundleShapeNode::BundleShapeNode() {}

BundleShapeNode::~BundleShapeNode() {}

MString BundleShapeNode::nodeName() {
    return MString(MM_BUNDLE_SHAPE_TYPE_NAME);
}

MStatus BundleShapeNode::compute(const MPlug & /*plug*/,
                                 MDataBlock & /*dataBlock*/) {
    return MS::kUnknownParameter;
}

bool BundleShapeNode::isBounded() const { return true; }

MBoundingBox BundleShapeNode::boundingBox() const {
    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);
    return MBoundingBox(corner1, corner2);
}

bool BundleShapeNode::excludeAsLocator() const {
    // Returning 'false' here means that when the user toggles
    // locators on/off with the (per-viewport) "Show" menu, this shape
    // node will not be affected.
    return false;
}

// Called before this node is evaluated by Evaluation Manager
//
#if MAYA_API_VERSION >= 20190000
MStatus BundleShapeNode::preEvaluation(const MDGContext &context,
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
void BundleShapeNode::getCacheSetup(const MEvaluationNode &evalNode,
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

void *BundleShapeNode::creator() { return new BundleShapeNode(); }

MStatus BundleShapeNode::initialize() {
    MStatus status;
    MFnUnitAttribute uAttr;
    MFnNumericAttribute nAttr;

    // Color
    m_color = nAttr.createColor("color", "clr");
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setDefault(0.0f, 1.0f, 0.0f));

    // Alpha
    auto alpha_min = 0.0;
    auto alpha_max = 1.0;
    auto alpha_default = 1.0;
    m_alpha =
        nAttr.create("alpha", "alp", MFnNumericData::kDouble, alpha_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(alpha_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMax(alpha_max));

    // Line Width
    auto line_width_min = 0.01;
    auto line_width_soft_min = 0.1;
    auto line_width_soft_max = 10.0;
    m_line_width =
        nAttr.create("lineWidth", "lnwd", MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(line_width_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    // Point size
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

    // Icon Size
    auto icon_size_min = 0.0;
    m_icon_size =
        nAttr.create("iconSize", "icnsz", MFnNumericData::kDouble, 10.0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(icon_size_min));

    // Draw Name
    m_draw_name =
        nAttr.create("drawName", "drwnm", MFnNumericData::kBoolean, 0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    // Draw on Top
    m_draw_on_top =
        nAttr.create("drawOnTop", "drwtp", MFnNumericData::kBoolean, 0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    MMSOLVER_CHECK_MSTATUS(addAttribute(m_icon_size));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_draw_on_top));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_draw_name));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_color));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_alpha));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_line_width));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_point_size));

    return MS::kSuccess;
}

}  // namespace mmsolver
