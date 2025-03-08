/*
 * Copyright (C) 2022, 2024 David Cattermole.
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

#include "ImagePlaneShape2Node.h"

// Maya
#include <maya/MColor.h>
#include <maya/MDataBlock.h>
#include <maya/MDataHandle.h>
#include <maya/MDistance.h>
#include <maya/MFnEnumAttribute.h>
#include <maya/MFnMessageAttribute.h>
#include <maya/MFnNumericAttribute.h>
#include <maya/MFnNumericData.h>
#include <maya/MFnStringData.h>
#include <maya/MFnTypedAttribute.h>
#include <maya/MFnUnitAttribute.h>
#include <maya/MPlug.h>
#include <maya/MPxLocatorNode.h>
#include <maya/MString.h>
#include <maya/MTypeId.h>
#include <maya/MVector.h>

#if MAYA_API_VERSION >= 20190000
#include <maya/MEvaluationNode.h>
#endif

// Maya Viewport 2.0
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "ImagePlaneUtils.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/nodeTypeIds.h"
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

MTypeId ImagePlaneShape2Node::m_id(MM_IMAGE_PLANE_SHAPE_2_TYPE_ID);
MString ImagePlaneShape2Node::m_draw_db_classification(
    MM_IMAGE_PLANE_SHAPE_2_DRAW_CLASSIFY);
MString ImagePlaneShape2Node::m_draw_registrant_id(
    MM_IMAGE_PLANE_SHAPE_2_DRAW_REGISTRANT_ID);
MString ImagePlaneShape2Node::m_selection_type_name(
    MM_IMAGE_PLANE_SHAPE_2_SELECTION_TYPE_NAME);
MString ImagePlaneShape2Node::m_display_filter_draw_db_classification(
    MM_IMAGE_PLANE_SHAPE_2_DISPLAY_FILTER_DRAW_DB_CLASSIFICATION);
MString ImagePlaneShape2Node::m_display_filter_name(
    MM_IMAGE_PLANE_SHAPE_2_DISPLAY_FILTER_NAME);
MString ImagePlaneShape2Node::m_display_filter_label(
    MM_IMAGE_PLANE_SHAPE_2_DISPLAY_FILTER_LABEL);

// Attributes
MObject ImagePlaneShape2Node::m_visible_to_camera_only;
MObject ImagePlaneShape2Node::m_draw_hud;
MObject ImagePlaneShape2Node::m_draw_image_size;
MObject ImagePlaneShape2Node::m_draw_camera_size;
MObject ImagePlaneShape2Node::m_image_width;
MObject ImagePlaneShape2Node::m_image_height;
MObject ImagePlaneShape2Node::m_image_num_channels;
MObject ImagePlaneShape2Node::m_image_bytes_per_channel;
MObject ImagePlaneShape2Node::m_image_size_bytes;
MObject ImagePlaneShape2Node::m_image_pixel_aspect;
MObject ImagePlaneShape2Node::m_camera_width_inch;
MObject ImagePlaneShape2Node::m_camera_height_inch;
MObject ImagePlaneShape2Node::m_lens_hash_current;
MObject ImagePlaneShape2Node::m_lens_hash_previous;
MObject ImagePlaneShape2Node::m_geometry_node;
MObject ImagePlaneShape2Node::m_camera_node;

// Image Attributes
MObject ImagePlaneShape2Node::m_image_display_channel;
MObject ImagePlaneShape2Node::m_image_color_gain;
MObject ImagePlaneShape2Node::m_image_color_exposure;
MObject ImagePlaneShape2Node::m_image_color_gamma;
MObject ImagePlaneShape2Node::m_image_color_saturation;
MObject ImagePlaneShape2Node::m_image_color_soft_clip;
MObject ImagePlaneShape2Node::m_image_alpha_gain;
MObject ImagePlaneShape2Node::m_image_default_color;
MObject ImagePlaneShape2Node::m_image_ignore_alpha;
MObject ImagePlaneShape2Node::m_image_flip;
MObject ImagePlaneShape2Node::m_image_flop;
MObject ImagePlaneShape2Node::m_image_frame_number;
MObject ImagePlaneShape2Node::m_image_file_path;
MObject ImagePlaneShape2Node::m_image_input_color_space;
MObject ImagePlaneShape2Node::m_image_output_color_space;
MObject ImagePlaneShape2Node::m_shader_is_transparent;

ImagePlaneShape2Node::ImagePlaneShape2Node() {}

ImagePlaneShape2Node::~ImagePlaneShape2Node() {}

MString ImagePlaneShape2Node::nodeName() {
    return MString(MM_IMAGE_PLANE_SHAPE_2_TYPE_NAME);
}

MStatus ImagePlaneShape2Node::compute(const MPlug & /*plug*/,
                                      MDataBlock & /*dataBlock*/
) {
    return MS::kUnknownParameter;
}

bool ImagePlaneShape2Node::isBounded() const { return true; }

MBoundingBox ImagePlaneShape2Node::boundingBox() const {
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

bool ImagePlaneShape2Node::excludeAsLocator() const {
    // Returning 'false' here means that when the user toggles
    // locators on/off with the (per-viewport) "Show" menu, this shape
    // node will not be affected.
    return false;
}

// Called before this node is evaluated by Evaluation Manager.
#if MAYA_API_VERSION >= 20190000
MStatus ImagePlaneShape2Node::preEvaluation(
    const MDGContext &context, const MEvaluationNode &evaluationNode) {
    if (context.isNormal()) {
        MHWRender::MRenderer::setGeometryDrawDirty(thisMObject());
    }

    return MStatus::kSuccess;
}
#endif

#if MAYA_API_VERSION >= 20200000
void ImagePlaneShape2Node::getCacheSetup(
    const MEvaluationNode &evalNode, MNodeCacheDisablingInfo &disablingInfo,
    MNodeCacheSetupInfo &cacheSetupInfo,
    MObjectArray &monitoredAttributes) const {
    MPxLocatorNode::getCacheSetup(evalNode, disablingInfo, cacheSetupInfo,
                                  monitoredAttributes);
    MMSOLVER_ASSERT(!disablingInfo.getCacheDisabled(),
                    "Setting up the cache cannot be disabled.");
    cacheSetupInfo.setPreference(MNodeCacheSetupInfo::kWantToCacheByDefault,
                                 false);
}
#endif

void *ImagePlaneShape2Node::creator() { return new ImagePlaneShape2Node(); }

MStatus ImagePlaneShape2Node::initialize() {
    MStatus status;
    MFnNumericAttribute nAttr;
    MFnTypedAttribute tAttr;
    MFnEnumAttribute eAttr;
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

    m_image_num_channels =
        nAttr.create("imageNumChannels", "imgnchan", MFnNumericData::kInt, 4);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(0));
    CHECK_MSTATUS(addAttribute(m_image_num_channels));

    m_image_bytes_per_channel = nAttr.create(
        "imageBytesPerChannel", "imgbtyprchan", MFnNumericData::kInt, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(0));
    CHECK_MSTATUS(addAttribute(m_image_bytes_per_channel));

    // Create empty string data to be used as attribute default
    // (string) value.
    MFnStringData zero_string_data;
    MObject zero_string_data_obj = zero_string_data.create("0");

    m_image_size_bytes = tAttr.create("imageSizeBytes", "imgszbyt",
                                      MFnData::kString, zero_string_data_obj);
    CHECK_MSTATUS(tAttr.setStorable(true));
    CHECK_MSTATUS(tAttr.setUsedAsFilename(false));
    CHECK_MSTATUS(addAttribute(m_image_size_bytes));

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

    m_camera_node = msgAttr.create("cameraNode", "camnd", &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(msgAttr.setStorable(true));
    CHECK_MSTATUS(msgAttr.setConnectable(true));
    CHECK_MSTATUS(msgAttr.setKeyable(false));
    CHECK_MSTATUS(addAttribute(m_camera_node));

    m_image_color_gain = nAttr.createColor("colorGain", "colgn");
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setReadable(true));
    CHECK_MSTATUS(nAttr.setWritable(true));
    CHECK_MSTATUS(nAttr.setDefault(1.0f, 1.0f, 1.0f));
    CHECK_MSTATUS(nAttr.setNiceNameOverride(MString("Gain")));
    CHECK_MSTATUS(addAttribute(m_image_color_gain));

    const float exposure_soft_min = -9.0f;
    const float exposure_soft_max = +9.0f;
    const float exposure_default = 0.0f;
    m_image_color_exposure = nAttr.create(
        "colorExposure", "colexpsr", MFnNumericData::kFloat, exposure_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setSoftMin(exposure_soft_min));
    CHECK_MSTATUS(nAttr.setSoftMax(exposure_soft_max));
    CHECK_MSTATUS(nAttr.setNiceNameOverride(MString("Exposure")));
    CHECK_MSTATUS(addAttribute(m_image_color_exposure));

    const float gamma_min = 0.0f;
    const float gamma_soft_max = +2.0f;
    const float gamma_default = 1.0f;
    m_image_color_gamma = nAttr.create("colorGamma", "colgmma",
                                       MFnNumericData::kFloat, gamma_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(gamma_min));
    CHECK_MSTATUS(nAttr.setSoftMax(gamma_soft_max));
    CHECK_MSTATUS(nAttr.setNiceNameOverride(MString("Gamma")));
    CHECK_MSTATUS(addAttribute(m_image_color_gamma));

    const float saturation_min = 0.0f;
    const float saturation_soft_max = 2.0f;
    const float saturation_default = 1.0f;
    m_image_color_saturation =
        nAttr.create("colorSaturation", "colstrtn", MFnNumericData::kFloat,
                     saturation_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(saturation_min));
    CHECK_MSTATUS(nAttr.setSoftMax(saturation_soft_max));
    CHECK_MSTATUS(nAttr.setNiceNameOverride(MString("Saturation")));
    CHECK_MSTATUS(addAttribute(m_image_color_saturation));

    const float soft_clip_min = 0.0f;
    const float soft_clip_max = 1.0f;
    const float soft_clip_default = 0.0f;
    m_image_color_soft_clip =
        nAttr.create("colorSoftClip", "colsftclp", MFnNumericData::kFloat,
                     soft_clip_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(soft_clip_min));
    CHECK_MSTATUS(nAttr.setMax(soft_clip_max));
    CHECK_MSTATUS(nAttr.setNiceNameOverride(MString("SoftClip")));
    CHECK_MSTATUS(addAttribute(m_image_color_soft_clip));

    const double alpha_min = 0.0;
    const double alpha_max = 1.0;
    const double alpha_default = 1.0;
    m_image_alpha_gain = nAttr.create("alphaGain", "alpgn",
                                      MFnNumericData::kDouble, alpha_default);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setConnectable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setMin(alpha_min));
    CHECK_MSTATUS(nAttr.setMax(alpha_max));
    CHECK_MSTATUS(addAttribute(m_image_alpha_gain));

    // Which channel of the image should be displayed?
    const short value_rgba = static_cast<short>(ImageDisplayChannel::kRGBA);
    const short value_rgb = static_cast<short>(ImageDisplayChannel::kRGB);
    const short value_red = static_cast<short>(ImageDisplayChannel::kRed);
    const short value_green = static_cast<short>(ImageDisplayChannel::kGreen);
    const short value_blue = static_cast<short>(ImageDisplayChannel::kBlue);
    const short value_alpha = static_cast<short>(ImageDisplayChannel::kAlpha);
    const short value_luminance =
        static_cast<short>(ImageDisplayChannel::kLuminance);
    m_image_display_channel =
        eAttr.create("displayChannel", "dspchan", value_rgba, &status);
    CHECK_MSTATUS(status);
    CHECK_MSTATUS(eAttr.addField("RGBA", value_rgba));
    CHECK_MSTATUS(eAttr.addField("RGB", value_rgb));
    CHECK_MSTATUS(eAttr.addField("Red", value_red));
    CHECK_MSTATUS(eAttr.addField("Green", value_green));
    CHECK_MSTATUS(eAttr.addField("Blue", value_blue));
    CHECK_MSTATUS(eAttr.addField("Alpha", value_alpha));
    CHECK_MSTATUS(eAttr.addField("Luminance", value_luminance));
    CHECK_MSTATUS(eAttr.setStorable(true));
    CHECK_MSTATUS(eAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(m_image_display_channel));

    m_image_ignore_alpha = nAttr.create("imageIgnoreAlpha", "imgignalp",
                                        MFnNumericData::kBoolean, false);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setConnectable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(m_image_ignore_alpha));

    m_image_flip =
        nAttr.create("imageFlip", "imgflip", MFnNumericData::kBoolean, false);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setConnectable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(nAttr.setNiceNameOverride(MString("Image Flip (Vertical)")));
    CHECK_MSTATUS(addAttribute(m_image_flip));

    m_image_flop =
        nAttr.create("imageFlop", "imgflop", MFnNumericData::kBoolean, false);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setConnectable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(
        nAttr.setNiceNameOverride(MString("Image Flop (Horizontal)")));
    CHECK_MSTATUS(addAttribute(m_image_flop));

    m_shader_is_transparent = nAttr.create("shaderIsTransparent", "shdistrnsp",
                                           MFnNumericData::kBoolean, false);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setConnectable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(
        nAttr.setNiceNameOverride(MString("Shader Is Transparent (Debug)")));
    CHECK_MSTATUS(addAttribute(m_shader_is_transparent));

    m_image_frame_number =
        nAttr.create("imageFrameNumber", "imgfrmnmb", MFnNumericData::kInt, 1);
    CHECK_MSTATUS(nAttr.setStorable(true));
    CHECK_MSTATUS(nAttr.setKeyable(true));
    CHECK_MSTATUS(addAttribute(m_image_frame_number));

    // // Pixel Data Type
    // m_cache_pixel_data_type = eAttr.create(
    //     "cachePixelDataType", "cchpxldtyp",
    //     kDataTypeUnknown);
    // CHECK_MSTATUS(eAttr.addField("auto", kDataTypeUnknown));
    // CHECK_MSTATUS(eAttr.addField("uint8", kDataTypeUInt8));
    // CHECK_MSTATUS(eAttr.addField("uint16", kDataTypeUInt16));
    // CHECK_MSTATUS(eAttr.addField("half16", kDataTypeHalf16));
    // CHECK_MSTATUS(eAttr.addField("float32", kDataTypeFloat32));
    // CHECK_MSTATUS(eAttr.setStorable(true));

    // Create empty string data to be used as attribute default
    // (string) value.
    MFnStringData empty_string_data;
    MObject empty_string_data_obj = empty_string_data.create("");

    m_image_file_path = tAttr.create("imageFilePath", "imgflpth",
                                     MFnData::kString, empty_string_data_obj);
    CHECK_MSTATUS(tAttr.setStorable(true));
    CHECK_MSTATUS(tAttr.setUsedAsFilename(true));
    CHECK_MSTATUS(addAttribute(m_image_file_path));

    m_image_input_color_space = tAttr.create(
        "inputColorSpace", "incolspc", MFnData::kString, empty_string_data_obj);
    CHECK_MSTATUS(tAttr.setStorable(true));
    CHECK_MSTATUS(tAttr.setUsedAsFilename(false));
    CHECK_MSTATUS(addAttribute(m_image_input_color_space));

    m_image_output_color_space =
        tAttr.create("outputColorSpace", "outcolspc", MFnData::kString,
                     empty_string_data_obj);
    CHECK_MSTATUS(tAttr.setStorable(true));
    CHECK_MSTATUS(tAttr.setUsedAsFilename(false));
    CHECK_MSTATUS(addAttribute(m_image_output_color_space));

    return MS::kSuccess;
}

}  // namespace mmsolver
