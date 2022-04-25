/*
 * Copyright (C) 2022 David Cattermole.
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

#include "ImagePlaneShapeNode.h"

// Maya
#include <maya/MColor.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MDistance.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMessageAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MPlug.h>
#include <maya/MVector.h>
#include <maya/MViewport2Renderer.h>

#if MAYA_API_VERSION >= 20190000
#include <maya/MEvaluationNode.h>
#endif

#include <assert.h>

// MM Solver
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {

MTypeId ImagePlaneShapeNode::m_id(MM_IMAGE_PLANE_SHAPE_TYPE_ID);
MString ImagePlaneShapeNode::m_draw_db_classification(MM_IMAGE_PLANE_SHAPE_DRAW_CLASSIFY);
MString ImagePlaneShapeNode::m_draw_registrant_id(MM_IMAGE_PLANE_SHAPE_DRAW_REGISTRANT_ID);
MString ImagePlaneShapeNode::m_selection_type_name(MM_IMAGE_PLANE_SHAPE_SELECTION_TYPE_NAME);
MString ImagePlaneShapeNode::m_display_filter_name(MM_IMAGE_PLANE_SHAPE_DISPLAY_FILTER_NAME);
MString ImagePlaneShapeNode::m_display_filter_label(MM_IMAGE_PLANE_SHAPE_DISPLAY_FILTER_LABEL);

// Attributes
MObject ImagePlaneShapeNode::m_enable_hud;
MObject ImagePlaneShapeNode::m_enable_image_resolution;
MObject ImagePlaneShapeNode::m_image_width;
MObject ImagePlaneShapeNode::m_image_height;
MObject ImagePlaneShapeNode::m_image_pixel_aspect;
MObject ImagePlaneShapeNode::m_geometry_node;
MObject ImagePlaneShapeNode::m_shader_node;

ImagePlaneShapeNode::ImagePlaneShapeNode() {}

ImagePlaneShapeNode::~ImagePlaneShapeNode() {}

MString ImagePlaneShapeNode::nodeName() {
    return MString(MM_IMAGE_PLANE_SHAPE_TYPE_NAME);
}

MStatus
ImagePlaneShapeNode::compute(
    const MPlug &/*plug*/,
    MDataBlock &/*dataBlock*/
) {
    return MS::kUnknownParameter;;
}

bool ImagePlaneShapeNode::isBounded() const {
    return true;
}

MBoundingBox ImagePlaneShapeNode::boundingBox() const {
    // This forces the image plane to update very often, fast enough
    // to ensure users changing lens distortion sliders will see the
    // node update in real-time.
    MHWRender::MRenderer::setGeometryDrawDirty(thisMObject());

    MPoint corner1(-1.0, -1.0, -1.0);
    MPoint corner2(1.0, 1.0, 1.0);
    return MBoundingBox(corner1, corner2);
}

bool ImagePlaneShapeNode::excludeAsLocator() const {
    // Returning 'false' here means that when the user toggles
    // locators on/off with the (per-viewport) "Show" menu, this shape
    // node will not be affected.
    return false;
}

// Called before this node is evaluated by Evaluation Manager.
#if MAYA_API_VERSION >= 20190000
MStatus ImagePlaneShapeNode::preEvaluation(
    const MDGContext &context,
    const MEvaluationNode &evaluationNode
) {
    if (context.isNormal()) {
        MHWRender::MRenderer::setGeometryDrawDirty(thisMObject());
    }

    return MStatus::kSuccess;
}
#endif

#if MAYA_API_VERSION >= 20200000
void ImagePlaneShapeNode::getCacheSetup(
    const MEvaluationNode &evalNode,
    MNodeCacheDisablingInfo &disablingInfo,
    MNodeCacheSetupInfo &cacheSetupInfo,
    MObjectArray &monitoredAttributes
) const {
    MPxLocatorNode::getCacheSetup(
        evalNode,
        disablingInfo,
        cacheSetupInfo,
        monitoredAttributes);
    assert(!disablingInfo.getCacheDisabled());
    cacheSetupInfo.setPreference(
        MNodeCacheSetupInfo::kWantToCacheByDefault,
        true);
}
#endif

void *ImagePlaneShapeNode::creator() {
    return new ImagePlaneShapeNode();
}

MStatus ImagePlaneShapeNode::initialize() {
    MStatus status;
    MFnNumericAttribute nAttr;
    MFnMessageAttribute msgAttr;

    m_enable_hud = nAttr.create(
        "enableHud", "enbhud",
        MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(m_enable_hud));

    m_enable_image_resolution = nAttr.create(
        "enableImageResolution", "enbimgres",
        MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(m_enable_image_resolution));

    m_image_width = nAttr.create(
        "imageWidth", "imgwdth",
        MFnNumericData::kInt, 1920);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(1));
    CHECK_MSTATUS(addAttribute(m_image_width));

    m_image_height = nAttr.create(
        "imageHeight", "imghght",
        MFnNumericData::kInt, 1080);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(1));
    CHECK_MSTATUS(addAttribute(m_image_height));

    m_image_pixel_aspect = nAttr.create(
        "imagePixelAspect", "imgpxasp",
        MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(0.1));
    CHECK_MSTATUS(nAttr.setMax(4.0));
    CHECK_MSTATUS(addAttribute(m_image_pixel_aspect));

    m_geometry_node = msgAttr.create("geometryNode", "geond", &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(msgAttr.setStorable(true));
    CHECK_MSTATUS(msgAttr.setConnectable(true));
    CHECK_MSTATUS(msgAttr.setKeyable(false));
    CHECK_MSTATUS(addAttribute(m_geometry_node));

    m_shader_node = msgAttr.create("shaderNode", "shdnd", &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(msgAttr.setStorable(true));
    CHECK_MSTATUS(msgAttr.setConnectable(true));
    CHECK_MSTATUS(msgAttr.setKeyable(false));
    CHECK_MSTATUS(addAttribute(m_shader_node));

    return MS::kSuccess;
}

} // namespace mmsolver
