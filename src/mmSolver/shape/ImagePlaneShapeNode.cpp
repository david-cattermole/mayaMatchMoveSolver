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

// STL
#include <assert.h>

// Maya
#include <maya/MColor.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MDistance.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMessageAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MPlug.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MVector.h>
#include <maya/MViewport2Renderer.h>

#if MAYA_API_VERSION >= 20190000
#include <maya/MEvaluationNode.h>
#endif

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"

namespace mmsolver {

MTypeId ImagePlaneShapeNode::m_id(MM_IMAGE_PLANE_SHAPE_TYPE_ID);
MString ImagePlaneShapeNode::m_draw_db_classification(
    MM_IMAGE_PLANE_SHAPE_DRAW_CLASSIFY);
MString ImagePlaneShapeNode::m_draw_registrant_id(
    MM_IMAGE_PLANE_SHAPE_DRAW_REGISTRANT_ID);
MString ImagePlaneShapeNode::m_selection_type_name(
    MM_IMAGE_PLANE_SHAPE_SELECTION_TYPE_NAME);
MString ImagePlaneShapeNode::m_display_filter_draw_db_classification(
    MM_IMAGE_PLANE_SHAPE_DISPLAY_FILTER_DRAW_DB_CLASSIFICATION);
MString ImagePlaneShapeNode::m_display_filter_name(
    MM_IMAGE_PLANE_SHAPE_DISPLAY_FILTER_NAME);
MString ImagePlaneShapeNode::m_display_filter_label(
    MM_IMAGE_PLANE_SHAPE_DISPLAY_FILTER_LABEL);

// Attributes
MObject ImagePlaneShapeNode::m_visible_to_camera_only;
MObject ImagePlaneShapeNode::m_draw_hud;
MObject ImagePlaneShapeNode::m_draw_image_size;
MObject ImagePlaneShapeNode::m_draw_camera_size;
MObject ImagePlaneShapeNode::m_image_width;
MObject ImagePlaneShapeNode::m_image_height;
MObject ImagePlaneShapeNode::m_image_pixel_aspect;
MObject ImagePlaneShapeNode::m_camera_width_inch;
MObject ImagePlaneShapeNode::m_camera_height_inch;
MObject ImagePlaneShapeNode::m_lens_hash_current;
MObject ImagePlaneShapeNode::m_lens_hash_previous;
MObject ImagePlaneShapeNode::m_geometry_node;
MObject ImagePlaneShapeNode::m_shader_node;
MObject ImagePlaneShapeNode::m_camera_node;

ImagePlaneShapeNode::ImagePlaneShapeNode() {}

ImagePlaneShapeNode::~ImagePlaneShapeNode() {}

MString ImagePlaneShapeNode::nodeName() {
    return MString(MM_IMAGE_PLANE_SHAPE_TYPE_NAME);
}

MStatus ImagePlaneShapeNode::compute(const MPlug & /*plug*/,
                                     MDataBlock & /*dataBlock*/
) {
    return MS::kUnknownParameter;
}

bool ImagePlaneShapeNode::isBounded() const { return true; }

MBoundingBox ImagePlaneShapeNode::boundingBox() const {
    MObject this_node = thisMObject();

    MPlug current_plug(this_node, m_lens_hash_current);
    int64_t current_hash = current_plug.asInt64();

    MPlug previous_plug(this_node, m_lens_hash_previous);
    int64_t previous_hash = previous_plug.asInt64();

    // Limit the number of calls to
    // 'setGeometryDrawDirty', because this causes the viewport update
    // to run constantly, running up CPU for no reason.
    if (current_hash != previous_hash) {
        MHWRender::MRenderer::setGeometryDrawDirty(this_node);
        previous_plug.setInt64(current_hash);
    }

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
    const MDGContext &context, const MEvaluationNode &evaluationNode) {
    if (context.isNormal()) {
        MHWRender::MRenderer::setGeometryDrawDirty(thisMObject());
    }

    return MStatus::kSuccess;
}
#endif

#if MAYA_API_VERSION >= 20200000
void ImagePlaneShapeNode::getCacheSetup(
    const MEvaluationNode &evalNode, MNodeCacheDisablingInfo &disablingInfo,
    MNodeCacheSetupInfo &cacheSetupInfo,
    MObjectArray &monitoredAttributes) const {
    MPxLocatorNode::getCacheSetup(evalNode, disablingInfo, cacheSetupInfo,
                                  monitoredAttributes);
    assert(!disablingInfo.getCacheDisabled());
    cacheSetupInfo.setPreference(MNodeCacheSetupInfo::kWantToCacheByDefault,
                                 true);
}
#endif

void *ImagePlaneShapeNode::creator() { return new ImagePlaneShapeNode(); }

MStatus ImagePlaneShapeNode::initialize() {
    MStatus status;
    MFnNumericAttribute nAttr;
    MFnMessageAttribute msgAttr;

    m_visible_to_camera_only = nAttr.create("visibleToCameraOnly", "viscamony",
                                            MFnNumericData::kBoolean, 0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(m_visible_to_camera_only));

    m_draw_hud = nAttr.create("drawHud", "enbhud", MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(m_draw_hud));

    m_draw_image_size =
        nAttr.create("drawImageSize", "enbimgsz", MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(m_draw_image_size));

    m_draw_camera_size =
        nAttr.create("drawCameraSize", "enbcamsz", MFnNumericData::kBoolean, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(m_draw_camera_size));

    m_image_width =
        nAttr.create("imageWidth", "imgwdth", MFnNumericData::kInt, 1920);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(1));
    CHECK_MSTATUS(addAttribute(m_image_width));

    m_image_height =
        nAttr.create("imageHeight", "imghght", MFnNumericData::kInt, 1080);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(1));
    CHECK_MSTATUS(addAttribute(m_image_height));

    m_image_pixel_aspect = nAttr.create("imagePixelAspect", "imgpxasp",
                                        MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(0.1));
    CHECK_MSTATUS(nAttr.setMax(4.0));
    CHECK_MSTATUS(addAttribute(m_image_pixel_aspect));

    m_camera_width_inch = nAttr.create("cameraWidthInch", "camwdthin",
                                       MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setConnectable(true));
    CHECK_MSTATUS(nAttr.setKeyable(false));
    CHECK_MSTATUS(nAttr.setMin(0));
    CHECK_MSTATUS(nAttr.setNiceNameOverride(MString("Camera Width (inches)")));
    CHECK_MSTATUS(addAttribute(m_camera_width_inch));

    m_camera_height_inch = nAttr.create("cameraHeightInch", "camhghtin",
                                        MFnNumericData::kDouble, 1.0);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setConnectable(true));
    CHECK_MSTATUS(nAttr.setKeyable(false));
    CHECK_MSTATUS(nAttr.setMin(0));
    CHECK_MSTATUS(nAttr.setNiceNameOverride(MString("Camera Height (inches)")));
    CHECK_MSTATUS(addAttribute(m_camera_height_inch));

    m_lens_hash_current =
        nAttr.create("lensHashCurrent", "lnshshcur", MFnNumericData::kInt64, 0);
    CHECK_MSTATUS(nAttr.setStorable(false));
    CHECK_MSTATUS(nAttr.setConnectable(true));
    CHECK_MSTATUS(nAttr.setKeyable(false));
    CHECK_MSTATUS(nAttr.setHidden(true));
    CHECK_MSTATUS(addAttribute(m_lens_hash_current));

    m_lens_hash_previous = nAttr.create("lensHashPrevious", "lnshshprv",
                                        MFnNumericData::kInt64, 0);
    CHECK_MSTATUS(nAttr.setStorable(false));
    CHECK_MSTATUS(nAttr.setConnectable(false));
    CHECK_MSTATUS(nAttr.setKeyable(false));
    CHECK_MSTATUS(nAttr.setHidden(true));
    CHECK_MSTATUS(addAttribute(m_lens_hash_previous));

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

    m_camera_node = msgAttr.create("cameraNode", "camnd", &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(msgAttr.setStorable(true));
    CHECK_MSTATUS(msgAttr.setConnectable(true));
    CHECK_MSTATUS(msgAttr.setKeyable(false));
    CHECK_MSTATUS(addAttribute(m_camera_node));

    return MS::kSuccess;
}

}  // namespace mmsolver
