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

#include "SkyDomeShapeNode.h"

// Maya
#include <maya/MColor.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MDistance.h>
#include <maya/MFnEnumAttribute.h>
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
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

MTypeId SkyDomeShapeNode::m_id(MM_SKY_DOME_SHAPE_TYPE_ID);
MString SkyDomeShapeNode::m_draw_db_classification(MM_SKY_DOME_DRAW_CLASSIFY);
MString SkyDomeShapeNode::m_draw_registrant_id(MM_SKY_DOME_DRAW_REGISTRANT_ID);
MString SkyDomeShapeNode::m_selection_type_name(
    MM_SKY_DOME_SHAPE_SELECTION_TYPE_NAME);
MString SkyDomeShapeNode::m_display_filter_name(
    MM_SKY_DOME_SHAPE_DISPLAY_FILTER_NAME);
MString SkyDomeShapeNode::m_display_filter_label(
    MM_SKY_DOME_SHAPE_DISPLAY_FILTER_LABEL);

// Attributes
MObject SkyDomeShapeNode::m_enable;
MObject SkyDomeShapeNode::m_transform_mode;
MObject SkyDomeShapeNode::m_alpha;
MObject SkyDomeShapeNode::m_line_width;
MObject SkyDomeShapeNode::m_resolution;
MObject SkyDomeShapeNode::m_draw_mode;
MObject SkyDomeShapeNode::m_radius;

MObject SkyDomeShapeNode::m_axis_x_enable;
MObject SkyDomeShapeNode::m_axis_y_enable;
MObject SkyDomeShapeNode::m_axis_z_enable;
MObject SkyDomeShapeNode::m_axis_x_enable_top;
MObject SkyDomeShapeNode::m_axis_z_enable_top;
MObject SkyDomeShapeNode::m_axis_x_enable_bottom;
MObject SkyDomeShapeNode::m_axis_z_enable_bottom;
MObject SkyDomeShapeNode::m_axis_x_color;
MObject SkyDomeShapeNode::m_axis_y_color;
MObject SkyDomeShapeNode::m_axis_z_color;
MObject SkyDomeShapeNode::m_axis_x_alpha;
MObject SkyDomeShapeNode::m_axis_y_alpha;
MObject SkyDomeShapeNode::m_axis_z_alpha;
MObject SkyDomeShapeNode::m_axis_x_line_width;
MObject SkyDomeShapeNode::m_axis_y_line_width;
MObject SkyDomeShapeNode::m_axis_z_line_width;

MObject SkyDomeShapeNode::m_grid_lat_enable;
MObject SkyDomeShapeNode::m_grid_long_enable;
MObject SkyDomeShapeNode::m_grid_lat_enable_top;
MObject SkyDomeShapeNode::m_grid_long_enable_top;
MObject SkyDomeShapeNode::m_grid_lat_enable_bottom;
MObject SkyDomeShapeNode::m_grid_long_enable_bottom;
MObject SkyDomeShapeNode::m_grid_lat_color;
MObject SkyDomeShapeNode::m_grid_long_color;
MObject SkyDomeShapeNode::m_grid_lat_alpha;
MObject SkyDomeShapeNode::m_grid_long_alpha;
MObject SkyDomeShapeNode::m_grid_lat_line_width;
MObject SkyDomeShapeNode::m_grid_long_line_width;
MObject SkyDomeShapeNode::m_grid_lat_divisions;
MObject SkyDomeShapeNode::m_grid_long_divisions;

SkyDomeShapeNode::SkyDomeShapeNode() {}

SkyDomeShapeNode::~SkyDomeShapeNode() {}

MString SkyDomeShapeNode::nodeName() {
    return MString(MM_SKY_DOME_SHAPE_TYPE_NAME);
}

MStatus SkyDomeShapeNode::compute(const MPlug & /*plug*/,
                                  MDataBlock & /*dataBlock*/) {
    return MS::kUnknownParameter;
}

bool SkyDomeShapeNode::isBounded() const { return false; }

MBoundingBox SkyDomeShapeNode::boundingBox() const {
    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);
    return MBoundingBox(corner1, corner2);
}

bool SkyDomeShapeNode::excludeAsLocator() const {
    // Returning 'false' here means that when the user toggles
    // locators on/off with the (per-viewport) "Show" menu, this shape
    // node will not be affected.
    return false;
}

// Called before this node is evaluated by Evaluation Manager.
#if MAYA_API_VERSION >= 20190000
MStatus SkyDomeShapeNode::preEvaluation(const MDGContext &context,
                                        const MEvaluationNode &evaluationNode) {
    if (context.isNormal()) {
        MStatus status;
        if (evaluationNode.dirtyPlugExists(m_radius, &status) && status) {
            MHWRender::MRenderer::setGeometryDrawDirty(thisMObject());
        }
    }

    return MStatus::kSuccess;
}
#endif

#if MAYA_API_VERSION >= 20200000
void SkyDomeShapeNode::getCacheSetup(const MEvaluationNode &evalNode,
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

void *SkyDomeShapeNode::creator() { return new SkyDomeShapeNode(); }

MStatus SkyDomeShapeNode::initialize() {
    MStatus status;
    MFnUnitAttribute uAttr;
    MFnNumericAttribute nAttr;
    MFnEnumAttribute eAttr;

    // Resolution
    auto resolution_default = 64;
    auto resolution_min = 3;
    auto resolution_soft_min = 4;
    auto resolution_soft_max = 256;
    m_resolution = nAttr.create("resolution", "res", MFnNumericData::kInt,
                                resolution_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(resolution_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(resolution_soft_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(resolution_soft_max));

    // The 'mode' of the Sky Dome.
    m_draw_mode = eAttr.create(
        "drawMode", "drmd", static_cast<short>(DrawMode::kDrawOnTop), &status);
    MMSOLVER_CHECK_MSTATUS(status);
    MMSOLVER_CHECK_MSTATUS(eAttr.addField(
        "Use Custom Depth", static_cast<short>(DrawMode::kUseCustomDepth)));
    MMSOLVER_CHECK_MSTATUS(eAttr.addField(
        "Draw On Top", static_cast<short>(DrawMode::kDrawOnTop)));
    // MMSOLVER_CHECK_MSTATUS(eAttr.addField("Draw Behind",
    //                              static_cast<short>(DrawMode::kDrawBehind)));
    MMSOLVER_CHECK_MSTATUS(eAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(eAttr.setKeyable(true));

    // The 'transform mode' of the Sky Dome, how are transforms
    // applied?
    m_transform_mode = eAttr.create(
        "transformMode", "tfmd",
        static_cast<short>(TransformMode::kCenterOfCamera), &status);
    MMSOLVER_CHECK_MSTATUS(status);
    MMSOLVER_CHECK_MSTATUS(eAttr.addField(
        "No Offset", static_cast<short>(TransformMode::kNoOffset)));
    MMSOLVER_CHECK_MSTATUS(
        eAttr.addField("Center of Camera",
                       static_cast<short>(TransformMode::kCenterOfCamera)));
    MMSOLVER_CHECK_MSTATUS(eAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(eAttr.setKeyable(true));

    // Radius / Depth
    m_radius = uAttr.create("radius", "rd", MFnUnitAttribute::kDistance);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(uAttr.setDefault(1.0));

    // Axis Enable
    m_enable = nAttr.create("enable", "enb", MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    m_axis_x_enable =
        nAttr.create("axisEnableX", "aex", MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    m_axis_y_enable =
        nAttr.create("axisEnableY", "aey", MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    m_axis_z_enable =
        nAttr.create("axisEnableZ", "aez", MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    // Axis Enable Top
    m_axis_x_enable_top =
        nAttr.create("axisEnableTopX", "aetx", MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    m_axis_z_enable_top =
        nAttr.create("axisEnableTopZ", "aetz", MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    // Axis Enable Bottom
    m_axis_x_enable_bottom =
        nAttr.create("axisEnableBottomX", "aebx", MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    m_axis_z_enable_bottom =
        nAttr.create("axisEnableBottomZ", "aebz", MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    // Grid Lat/Long Enable
    m_grid_lat_enable = nAttr.create("gridLatitudeEnable", "grlte",
                                     MFnNumericData::kBoolean, 0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    m_grid_long_enable = nAttr.create("gridLongitudeEnable", "grlge",
                                      MFnNumericData::kBoolean, 0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    // Grid Lat/Long Enable Top
    m_grid_lat_enable_top = nAttr.create("gridLatitudeEnableTop", "grltet",
                                         MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    m_grid_long_enable_top = nAttr.create("gridLongitudeEnableTop", "grlget",
                                          MFnNumericData::kBoolean, 1);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    // Grid Enable Bottom
    m_grid_lat_enable_bottom = nAttr.create(
        "gridLatitudeEnableBottom", "grlteb", MFnNumericData::kBoolean, 0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    m_grid_long_enable_bottom = nAttr.create(
        "gridLongitudeEnableBottom", "grlgeb", MFnNumericData::kBoolean, 0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));

    // Line Width multiplier
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

    line_width_min = 0.01;
    line_width_soft_min = 1.0;
    line_width_soft_max = 10.0;

    // Axis Line Widths
    m_axis_x_line_width =
        nAttr.create("axisLineWidthX", "alwx", MFnNumericData::kDouble, 2.0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(line_width_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    m_axis_y_line_width =
        nAttr.create("axisLineWidthY", "alwy", MFnNumericData::kDouble, 2.0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(line_width_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    m_axis_z_line_width =
        nAttr.create("axisLineWidthZ", "alwz", MFnNumericData::kDouble, 2.0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(line_width_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    // Grid Lat/Long Line Widths
    m_grid_lat_line_width = nAttr.create("gridLatitudeLineWidth", "grltlw",
                                         MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(line_width_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    m_grid_long_line_width = nAttr.create("gridLongitudeLineWidth", "grlglw",
                                          MFnNumericData::kDouble, 1.0);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(line_width_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    // Colors - Add colours for axis lines and lat-long lines.
    m_axis_x_color = nAttr.createColor("axisColorX", "aclx");
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setDefault(1.0f, 0.0f, 0.0f));

    m_axis_y_color = nAttr.createColor("axisColorY", "acly");
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setDefault(0.0f, 1.0f, 0.0f));

    m_axis_z_color = nAttr.createColor("axisColorZ", "aclz");
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setDefault(0.0f, 0.0f, 1.0f));

    m_grid_lat_color = nAttr.createColor("gridLatitudeColor", "grltcl");
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setDefault(1.0f, 0.0f, 1.0f));

    m_grid_long_color = nAttr.createColor("gridLongitudeColor", "grlgcl");
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setDefault(0.0f, 1.0f, 1.0f));

    // Alpha multiplier
    auto alpha_min = 0.0;
    auto alpha_max = 1.0;
    auto alpha_soft_max = 1.0;
    auto alpha_default = 1.0;
    m_alpha =
        nAttr.create("alpha", "alp", MFnNumericData::kDouble, alpha_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(alpha_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(alpha_soft_max));

    // Axis Alphas
    alpha_default = 1.0;
    m_axis_x_alpha = nAttr.create("axisAlphaX", "aaplx",
                                  MFnNumericData::kDouble, alpha_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(alpha_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMax(alpha_max));

    m_axis_y_alpha = nAttr.create("axisAlphaY", "aaply",
                                  MFnNumericData::kDouble, alpha_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(alpha_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMax(alpha_max));

    m_axis_z_alpha = nAttr.create("axisAlphaZ", "aalpz",
                                  MFnNumericData::kDouble, alpha_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(alpha_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMax(alpha_max));

    // Grid Lat/Long Alphas
    alpha_default = 0.5;
    m_grid_lat_alpha = nAttr.create("gridLatitudeAlpha", "grltalp",
                                    MFnNumericData::kDouble, alpha_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(alpha_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMax(alpha_max));

    m_grid_long_alpha = nAttr.create("gridLongitudeAlpha", "grlgalp",
                                     MFnNumericData::kDouble, alpha_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(alpha_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMax(alpha_max));

    // Lat-Long Divisions
    auto divisions_default = 6;
    auto divisions_min = 3;
    auto divisions_soft_min = 3;
    auto divisions_soft_max = 10;
    m_grid_lat_divisions =
        nAttr.create("gridLatitudeDivisions", "grltdv", MFnNumericData::kInt,
                     divisions_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(divisions_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(divisions_soft_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(divisions_soft_max));

    m_grid_long_divisions =
        nAttr.create("gridLongitudeDivisions", "grlgdv", MFnNumericData::kInt,
                     divisions_default);
    MMSOLVER_CHECK_MSTATUS(nAttr.setStorable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setKeyable(true));
    MMSOLVER_CHECK_MSTATUS(nAttr.setMin(divisions_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMin(divisions_soft_min));
    MMSOLVER_CHECK_MSTATUS(nAttr.setSoftMax(divisions_soft_max));

    // Add attributes
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_enable));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_transform_mode));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_alpha));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_line_width));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_resolution));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_draw_mode));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_radius));
    // Axis X
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_x_enable));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_x_enable_top));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_x_enable_bottom));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_x_color));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_x_alpha));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_x_line_width));
    // Axis Y
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_y_enable));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_y_color));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_y_alpha));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_y_line_width));
    // Axis Z
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_z_enable));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_z_enable_top));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_z_enable_bottom));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_z_color));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_z_alpha));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_axis_z_line_width));
    // Grid Latitude
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_lat_enable));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_lat_enable_top));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_lat_enable_bottom));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_lat_color));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_lat_alpha));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_lat_line_width));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_lat_divisions));
    // Grid Longitude
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_long_enable));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_long_enable_top));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_long_enable_bottom));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_long_color));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_long_alpha));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_long_line_width));
    MMSOLVER_CHECK_MSTATUS(addAttribute(m_grid_long_divisions));

    return MS::kSuccess;
}

}  // namespace mmsolver
