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

#include <nodeTypeIds.h>
#include "SkyDomeShapeNode.h"

#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MVector.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnNumericData.h>

#if MAYA_API_VERSION >= 20190000
#include <maya/MEvaluationNode.h>
#include <assert.h>
#endif

namespace mmsolver {

MTypeId SkyDomeShapeNode::m_id(MM_SKY_DOME_SHAPE_TYPE_ID);
MString SkyDomeShapeNode::m_draw_db_classification(MM_SKY_DOME_DRAW_CLASSIFY);
MString SkyDomeShapeNode::m_draw_registrant_id(MM_SKY_DOME_DRAW_REGISTRANT_ID);

// Attributes
// TODO: Add Colours.
MObject SkyDomeShapeNode::m_global_enable;
MObject SkyDomeShapeNode::m_global_line_width;
MObject SkyDomeShapeNode::m_resolution;
MObject SkyDomeShapeNode::m_draw_on_top;
MObject SkyDomeShapeNode::m_radius;
MObject SkyDomeShapeNode::m_latitude_enable;
MObject SkyDomeShapeNode::m_longitude_enable;
MObject SkyDomeShapeNode::m_latitude_line_width;
MObject SkyDomeShapeNode::m_longitude_line_width;
MObject SkyDomeShapeNode::m_latitude_divisions;
MObject SkyDomeShapeNode::m_longitude_divisions;
MObject SkyDomeShapeNode::m_x_axis_enable;
MObject SkyDomeShapeNode::m_y_axis_enable;
MObject SkyDomeShapeNode::m_z_axis_enable;
MObject SkyDomeShapeNode::m_x_axis_line_width;
MObject SkyDomeShapeNode::m_y_axis_line_width;
MObject SkyDomeShapeNode::m_z_axis_line_width;


SkyDomeShapeNode::SkyDomeShapeNode() {}

SkyDomeShapeNode::~SkyDomeShapeNode() {}

MString SkyDomeShapeNode::nodeName() {
    return MString(MM_SKY_DOME_SHAPE_TYPE_NAME);
}

MStatus
SkyDomeShapeNode::compute(const MPlug &/*plug*/, MDataBlock &/*dataBlock*/) {
    return MS::kUnknownParameter;;
}

bool SkyDomeShapeNode::isBounded() const {
    return false;
}

MBoundingBox SkyDomeShapeNode::boundingBox() const {
    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);
    return MBoundingBox(corner1, corner2);
}

// Called before this node is evaluated by Evaluation Manager.
#if MAYA_API_VERSION >= 20190000
MStatus SkyDome::preEvaluation(
        const MDGContext &context,
        const MEvaluationNode &evaluationNode) {
    if (context.isNormal()) {
        MStatus status;
        if (evaluationNode.dirtyPlugExists(m_size, &status) && status) {
            MHWRender::MRenderer::setGeometryDrawDirty(thisMObject());
        }
    }

    return MStatus::kSuccess;
}
#endif

#if MAYA_API_VERSION >= 20190000
void SkyDome::getCacheSetup(const MEvaluationNode &evalNode,
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

void *SkyDomeShapeNode::creator() {
    return new SkyDomeShapeNode();
}

MStatus SkyDomeShapeNode::initialize() {
    MFnUnitAttribute uAttr;
    MFnNumericAttribute nAttr;

    // Resolution
    auto resolution_default = 64;
    auto resolution_min = 3;
    auto resolution_soft_min = 4;
    auto resolution_soft_max = 256;
    m_resolution = nAttr.create(
        "resolution", "res",
        MFnNumericData::kInt, resolution_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(resolution_min));
    CHECK_MSTATUS(nAttr.setSoftMin(resolution_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(resolution_soft_max));

    // Draw on top?
    //
    // TODO: Replace this attribute with a 'draw depth' enum, with the
    // following values;
    //
    // - Draw on top.
    // - Draw behind.
    // - Custom Depth
    //
    m_draw_on_top = nAttr.create(
        "drawOnTop", "dot",
        MFnNumericData::kBoolean, 0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    // TODO: Add 'enum' attribute to allow users using the camera
    // position or not.

    // Radius / Depth
    m_radius = uAttr.create("radius", "rd", MFnUnitAttribute::kDistance);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(uAttr.setDefault(1.0));

    // Axis Enable
    m_global_enable = nAttr.create(
        "enable", "enb",
        MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    m_latitude_enable = nAttr.create(
        "latitudeEnableX", "lte",
        MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    m_longitude_enable = nAttr.create(
        "longitudeEnableX", "lge",
        MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    m_x_axis_enable = nAttr.create(
        "axisEnableX", "aex",
        MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    m_y_axis_enable = nAttr.create(
        "axisEnableY", "aey",
        MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    m_z_axis_enable = nAttr.create(
        "axisEnableZ", "aez",
        MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));

    // Axis Line Width
    auto line_width_min = 0.01;
    auto line_width_soft_min = 1.0f;
    auto line_width_soft_max = 10.0f;
    m_global_line_width = nAttr.create(
        "lineWidth", "lnwd",
        MFnNumericData::kFloat, 1.0f);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(line_width_min));
    CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    m_latitude_line_width = nAttr.create(
        "latitudeLineWidth", "ltlw",
        MFnNumericData::kFloat, 1.0f);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(line_width_min));
    CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    m_longitude_line_width = nAttr.create(
        "longitudeLineWidth", "lglw",
        MFnNumericData::kFloat, 1.0f);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(line_width_min));
    CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    m_x_axis_line_width = nAttr.create(
        "axisLineWidthX", "alwx",
        MFnNumericData::kFloat, 2.0f);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(line_width_min));
    CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    m_y_axis_line_width = nAttr.create(
        "axisLineWidthY", "alwy",
        MFnNumericData::kFloat, 2.0f);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(line_width_min));
    CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    m_z_axis_line_width = nAttr.create(
        "axisLineWidthZ", "alwz",
        MFnNumericData::kFloat, 2.0f);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(line_width_min));
    CHECK_MSTATUS(nAttr.setSoftMin(line_width_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(line_width_soft_max));

    // Lat-Long Divisions
    auto divisions_default = 6;
    auto divisions_min = 2;
    auto divisions_soft_min = 2;
    auto divisions_soft_max = 10;
    m_latitude_divisions = nAttr.create(
        "latitudeDivisions", "ltdv",
        MFnNumericData::kInt, divisions_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(divisions_min));
    CHECK_MSTATUS(nAttr.setSoftMin(divisions_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(divisions_soft_max));

    m_longitude_divisions = nAttr.create(
        "longitudeDivisions", "lgdv",
        MFnNumericData::kInt, divisions_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(divisions_min));
    CHECK_MSTATUS(nAttr.setSoftMin(divisions_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(divisions_soft_max));

    // Colors
    //
    // Add colours for axis lines and lat-long lines.
    //
    // // aColor = nAttr.createColor( "color", "c" );
    // // CHECK_MSTATUS(nAttr.setStorable(true));
    // // CHECK_MSTATUS(nAttr.setKeyable(true));
    // // MAKE_INPUT(nAttr);
    // // CHECK_MSTATUS( nAttr.setDefault(0.0f, 0.58824f, 0.644f) );

    // Add attributes
    CHECK_MSTATUS(addAttribute(m_global_enable));
    CHECK_MSTATUS(addAttribute(m_global_line_width));
    CHECK_MSTATUS(addAttribute(m_resolution));
    CHECK_MSTATUS(addAttribute(m_draw_on_top));
    CHECK_MSTATUS(addAttribute(m_radius));
    CHECK_MSTATUS(addAttribute(m_latitude_enable));
    CHECK_MSTATUS(addAttribute(m_longitude_enable));
    CHECK_MSTATUS(addAttribute(m_latitude_line_width));
    CHECK_MSTATUS(addAttribute(m_longitude_line_width));
    CHECK_MSTATUS(addAttribute(m_latitude_divisions));
    CHECK_MSTATUS(addAttribute(m_longitude_divisions));
    CHECK_MSTATUS(addAttribute(m_x_axis_enable));
    CHECK_MSTATUS(addAttribute(m_x_axis_line_width));
    CHECK_MSTATUS(addAttribute(m_y_axis_enable));
    CHECK_MSTATUS(addAttribute(m_y_axis_line_width));
    CHECK_MSTATUS(addAttribute(m_z_axis_enable));
    CHECK_MSTATUS(addAttribute(m_z_axis_line_width));


    return MS::kSuccess;
}

} // namespace mmsolver
