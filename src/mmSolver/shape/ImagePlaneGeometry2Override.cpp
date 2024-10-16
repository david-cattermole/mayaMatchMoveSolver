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

#include "ImagePlaneGeometry2Override.h"

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>

// STL
#include <algorithm>
#include <cstring>
#include <string>

// Maya
#include <maya/MColor.h>
#include <maya/MDistance.h>
#include <maya/MEventMessage.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MImage.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MPoint.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>
#include <maya/MGeometryExtractor.h>
#include <maya/MPxGeometryOverride.h>
#include <maya/MShaderManager.h>
#include <maya/MUserData.h>

// MM Solver
#include <mmcolorio/lib.h>
#include <mmcore/lib.h>

#include "ImagePlaneShape2Node.h"
#include "ImagePlaneUtils.h"
#include "mmSolver/image/ImageCache.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/shape/constant_texture_data.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

const MString renderItemName_imagePlaneWireframe =
    MString("imagePlaneWireframe");
const MString renderItemName_imagePlaneShaded = MString("imagePlaneShaded");

ImagePlaneGeometry2Override::ImagePlaneGeometry2Override(const MObject &obj)
    : MHWRender::MPxGeometryOverride(obj)
    , m_this_node(obj)
    , m_visible(true)
    , m_draw_hud(false)
    , m_draw_image_size(false)
    , m_draw_camera_size(false)
    , m_geometry_node_type(MFn::kInvalid)
    , m_image_display_channel(ImageDisplayChannel::kRGBA)
    , m_color_gain(1.0, 1.0, 1.0, 1.0)
    , m_color_exposure(0.0f)
    , m_color_gamma(1.0f)
    , m_color_saturation(1.0f)
    , m_color_soft_clip(0.0f)
    , m_alpha_gain(1.0f)
    , m_default_color(0.3, 0.0, 0.0, 1.0)
    , m_ignore_alpha(false)
    , m_flip(false)
    , m_flop(false)
    , m_is_transparent(false)
    , m_frame(0)
    , m_file_path()
    , m_input_color_space_name()
    , m_output_color_space_name()
    , m_shader(nullptr)
    , m_update_shader(false)
    , m_color_texture(nullptr)
    , m_texture_sampler(nullptr) {
    m_model_editor_changed_callback_id = MEventMessage::addEventCallback(
        "modelEditorChanged",
        ImagePlaneGeometry2Override::on_model_editor_changed_func, this);
#if MAYA_API_VERSION >= 20220000
    m_shader_link_lost_user_data_ptr =
        ShaderLinkLostUserData2Ptr(new ShaderLinkLostUserData2());
#else
    m_shader_link_lost_user_data = ShaderLinkLostUserData2();
#endif
}

ImagePlaneGeometry2Override::~ImagePlaneGeometry2Override() {
    if (m_model_editor_changed_callback_id != 0) {
        MMessage::removeCallback(m_model_editor_changed_callback_id);
        m_model_editor_changed_callback_id = 0;
    }

    if (m_color_texture) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        MHWRender::MTextureManager *texture_manager =
            renderer ? renderer->getTextureManager() : nullptr;
        if (texture_manager) {
            texture_manager->releaseTexture(m_color_texture);
            m_color_texture = nullptr;
        }
    }

    if (m_texture_sampler) {
        MHWRender::MStateManager::releaseSamplerState(m_texture_sampler);
        m_texture_sampler = nullptr;
    }

    if (m_shader) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        const MHWRender::MShaderManager *shaderManager =
            renderer ? renderer->getShaderManager() : nullptr;
        if (shaderManager) {
            shaderManager->releaseShader(m_shader);
        }
    }
}

void ImagePlaneGeometry2Override::on_model_editor_changed_func(
    void *clientData) {
    // Mark the node as being dirty so that it can update on display
    // appearance switch among wireframe and shaded.
    ImagePlaneGeometry2Override *ovr =
        static_cast<ImagePlaneGeometry2Override *>(clientData);
    if (ovr && !ovr->m_this_node.isNull()) {
        MHWRender::MRenderer::setGeometryDrawDirty(ovr->m_this_node);
    }
}

void ImagePlaneGeometry2Override::shader_link_lost_func(
    ShaderLinkLostUserData2 *userData) {
    // TODO: What should this function do? Does it need to do anything?
    MMSOLVER_MAYA_DBG(
        "mmImagePlaneGeometry2Override: "
        "shader_link_lost_func: "
        "link_lost_count="
        << (*userData).link_lost_count
        << " set_shader_count=" << (*userData).set_shader_count);
    (*userData).link_lost_count += 1;
}

MHWRender::DrawAPI ImagePlaneGeometry2Override::supportedDrawAPIs() const {
    // TODO: We cannot support DirectX, unless we also write another
    // mmImagePlane for DirectX. Legacy OpenGL is also unsupported.
    return MHWRender::kOpenGLCoreProfile;
}

void ImagePlaneGeometry2Override::query_node_attributes(
    MObject &node, MDagPath &out_camera_node_path, bool &out_visible,
    bool &out_visible_to_camera_only, bool &out_is_under_camera,
    bool &out_draw_hud, bool &out_draw_image_size, MString &out_image_size,
    bool &out_draw_camera_size, MString &out_camera_size,
    ImageDisplayChannel &out_image_display_channel, MColor &out_color_gain,
    float &out_color_exposure, float &out_color_gamma,
    float &out_color_saturation, float &out_color_soft_clip,
    float &out_alpha_gain, MColor &out_default_color, bool &out_ignore_alpha,
    bool &out_flip, bool &out_flop, bool &out_is_transparent,
    mmcore::FrameValue &out_frame, MString &out_file_path,
    MString &out_input_color_space_name, MString &out_output_color_space_name) {
    const bool verbose = false;

    MDagPath objPath;
    MDagPath::getAPathTo(node, objPath);

    if (!objPath.isValid()) {
        return;
    }
    MStatus status;

    auto frame_context = MPxGeometryOverride::getFrameContext();
    MDagPath camera_node_path = frame_context->getCurrentCameraPath(&status);
    CHECK_MSTATUS(status);

    // By default the draw is visible, unless overridden by
    // out_visible_to_camera_only or out_is_under_camera.
    out_visible = true;

    status =
        getNodeAttr(objPath, ImagePlaneShape2Node::m_visible_to_camera_only,
                    out_visible_to_camera_only);
    CHECK_MSTATUS(status);

    status =
        getNodeAttr(objPath, ImagePlaneShape2Node::m_draw_hud, out_draw_hud);
    CHECK_MSTATUS(status);

    out_is_under_camera = true;
    if (camera_node_path.isValid() && out_camera_node_path.isValid()) {
        // Using an explicit camera node path to compare
        // against ensures that if a rouge camera is parented
        // under the attached camera, the node will be
        // invisible.
        out_is_under_camera = out_camera_node_path == camera_node_path;
    }

    if (!out_is_under_camera) {
        if (out_visible_to_camera_only) {
            out_visible = false;
        }
        // Do not draw the HUD if we are not under the camera,
        // the HUD must only be visible from the point of view
        // of the intended camera, otherwise it will look
        // wrong.
        out_draw_hud = false;
    }

    const auto int_precision = 0;
    const auto double_precision = 3;
    calculate_node_image_size_string(
        objPath, ImagePlaneShape2Node::m_draw_image_size,
        ImagePlaneShape2Node::m_image_width,
        ImagePlaneShape2Node::m_image_height,
        ImagePlaneShape2Node::m_image_pixel_aspect, int_precision,
        double_precision, out_draw_image_size, out_image_size);
    calculate_node_camera_size_string(
        objPath, ImagePlaneShape2Node::m_draw_camera_size,
        ImagePlaneShape2Node::m_camera_width_inch,
        ImagePlaneShape2Node::m_camera_height_inch, double_precision,
        out_draw_camera_size, out_camera_size);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_color_gain,
                         out_color_gain);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_color_exposure,
                         out_color_exposure);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_color_gamma,
                         out_color_gamma);
    CHECK_MSTATUS(status);

    status =
        getNodeAttr(objPath, ImagePlaneShape2Node::m_image_color_saturation,
                    out_color_saturation);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_color_soft_clip,
                         out_color_soft_clip);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_alpha_gain,
                         out_alpha_gain);
    CHECK_MSTATUS(status);

    short image_display_channel_value = 0;
    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_display_channel,
                         image_display_channel_value);
    CHECK_MSTATUS(status);
    out_image_display_channel =
        static_cast<ImageDisplayChannel>(image_display_channel_value);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_ignore_alpha,
                         out_ignore_alpha);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_flip, out_flip);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_flop, out_flop);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_shader_is_transparent,
                         out_is_transparent);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_frame_number,
                         out_frame);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShape2Node::m_image_file_path,
                         out_file_path);
    CHECK_MSTATUS(status);

    status =
        getNodeAttr(objPath, ImagePlaneShape2Node::m_image_input_color_space,
                    out_input_color_space_name);
    CHECK_MSTATUS(status);

    status =
        getNodeAttr(objPath, ImagePlaneShape2Node::m_image_output_color_space,
                    out_output_color_space_name);
    CHECK_MSTATUS(status);

    // Find the input/output file color spaces.
    //
    // TODO: Do not re-calculate this each update. Compute once and
    // cache the results.
    const char *file_color_space_name =
        mmcolorio::guess_color_space_name_from_file_path(
            out_file_path.asChar());
    MMSOLVER_MAYA_VRB(
        "mmImagePlaneGeometry2Override: "
        "query_node_attributes:"
        << " file_color_space_name=\"" << file_color_space_name << "\".");

    const char *output_color_space_name = mmcolorio::get_role_color_space_name(
        mmcolorio::ColorSpaceRole::kSceneLinear);
    out_output_color_space_name = MString(output_color_space_name);
    MMSOLVER_MAYA_VRB(
        "mmImagePlaneGeometry2Override: "
        "query_node_attributes:"
        << " out_output_color_space_name=\""
        << out_output_color_space_name.asChar() << "\".");
}

void ImagePlaneGeometry2Override::updateDG() {
    if (!m_geometry_node_path.isValid()) {
        MString attr_name = "geometryNode";
        find_geometry_node_path(m_this_node, attr_name, m_geometry_node_path,
                                m_geometry_node_type);
    }

    if (!m_camera_node_path.isValid()) {
        MString attr_name = "cameraNode";
        find_camera_node_path(m_this_node, attr_name, m_camera_node_path,
                              m_camera_node_type);
    }

    // Query Attributes from the base node.
    MString temp_input_color_space_name = "";
    MString temp_output_color_space_name = "";
    ImagePlaneGeometry2Override::query_node_attributes(
        m_this_node, m_camera_node_path, m_visible, m_visible_to_camera_only,
        m_is_under_camera, m_draw_hud, m_draw_image_size, m_image_size,
        m_draw_camera_size, m_camera_size, m_image_display_channel,
        m_color_gain, m_color_exposure, m_color_gamma, m_color_saturation,
        m_color_soft_clip, m_alpha_gain, m_default_color, m_ignore_alpha,
        m_flip, m_flop, m_is_transparent, m_frame, m_file_path,
        temp_input_color_space_name, temp_output_color_space_name);

    if ((m_input_color_space_name.asChar() !=
         temp_input_color_space_name.asChar()) ||
        (m_input_color_space_name.asChar() !=
         temp_input_color_space_name.asChar())) {
        m_input_color_space_name = temp_input_color_space_name;
        m_output_color_space_name = temp_output_color_space_name;
        m_update_shader = true;
    }
}

inline MFloatMatrix create_saturation_matrix(const float saturation) {
    // Luminance weights
    //
    // From Mozilla:
    // https://developer.mozilla.org/en-US/docs/Web/Accessibility/Understanding_Colors_and_Luminance
    const float kLuminanceRed = 0.2126f;
    const float kLuminanceGreen = 0.7152f;
    const float kLuminanceBlue = 0.0722f;

    const float r_weight = kLuminanceRed;
    const float g_weight = kLuminanceGreen;
    const float b_weight = kLuminanceBlue;

    const float r1 = (1.0 - saturation) * r_weight + saturation;
    const float r2 = (1.0 - saturation) * r_weight;
    const float r3 = (1.0 - saturation) * r_weight;

    const float g1 = (1.0 - saturation) * g_weight;
    const float g2 = (1.0 - saturation) * g_weight + saturation;
    const float g3 = (1.0 - saturation) * g_weight;

    const float b1 = (1.0 - saturation) * b_weight;
    const float b2 = (1.0 - saturation) * b_weight;
    const float b3 = (1.0 - saturation) * b_weight + saturation;

    const float saturation_matrix_values[4][4] = {
        // Column 0
        {r1, g1, b1, 0.0},
        // Column 1
        {r2, g2, b2, 0.0},
        // Column 2
        {r3, g3, b3, 0.0},
        // Column 3
        {0.0, 0.0, 0.0, 1.0},
    };

    return MFloatMatrix(saturation_matrix_values);
}

void ImagePlaneGeometry2Override::set_shader_instance_parameters(
    MShaderInstance *shader, MHWRender::MTextureManager *texture_manager,
    const MColor &color_gain, const float color_exposure,
    const float color_gamma, const float color_saturation,
    const float color_soft_clip, const float alpha_gain,
    const MColor &default_color, const bool ignore_alpha, const bool flip,
    const bool flop, const bool is_transparent,
    const ImageDisplayChannel image_display_channel,
    const mmcore::FrameValue frame, const MString &file_path,
    const MString &input_color_space_name,
    const MString &output_color_space_name,
    MHWRender::MTexture *out_color_texture,
    const MHWRender::MSamplerState *out_texture_sampler) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(
        "mmImagePlaneGeometry2Override: set_shader_instance_parameters.");

    const float color[] = {color_gain[0], color_gain[1], color_gain[2], 1.0f};
    MStatus status = shader->setParameter("gColorGain", color);
    CHECK_MSTATUS(status);

    status = shader->setParameter("gColorExposure", color_exposure);
    CHECK_MSTATUS(status);

    status = shader->setParameter("gColorGamma", color_gamma);
    CHECK_MSTATUS(status);

    MFloatMatrix saturation_matrix = create_saturation_matrix(color_saturation);
    status = shader->setParameter("gColorSaturationMatrix", saturation_matrix);
    CHECK_MSTATUS(status);

    status = shader->setParameter("gColorSoftClip", color_soft_clip);
    CHECK_MSTATUS(status);

    status = shader->setParameter("gAlphaGain", alpha_gain);
    CHECK_MSTATUS(status);

    const float temp_default_color[] = {default_color[0], default_color[1],
                                        default_color[2], 1.0f};
    status = shader->setParameter("gFallbackColor", temp_default_color);
    CHECK_MSTATUS(status);

    status = shader->setParameter("gFlip", flip);
    CHECK_MSTATUS(status);

    status = shader->setParameter("gFlop", flop);
    CHECK_MSTATUS(status);

    status = shader->setParameter("gIgnoreAlpha", m_ignore_alpha);
    CHECK_MSTATUS(status);

    status = shader->setParameter("gDisplayChannel",
                                  static_cast<int32_t>(image_display_channel));
    CHECK_MSTATUS(status);

    status = shader->setIsTransparent(is_transparent);
    MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: shader->isTransparent()="
                      << shader->isTransparent());
    CHECK_MSTATUS(status);

    MMSOLVER_MAYA_VRB(
        "mmImagePlaneGeometry2Override: file_path=" << file_path.asChar());

    rust::Str file_path_rust_str = rust::Str(file_path.asChar());
    rust::String expanded_file_path_rust_string =
        mmcore::expand_file_path_string(file_path_rust_str, frame);
    MString expanded_file_path(expanded_file_path_rust_string.data(),
                               expanded_file_path_rust_string.length());
    MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: expanded_file_path="
                      << expanded_file_path.asChar());

    MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: start out_color_texture="
                      << out_color_texture);

    if (!out_color_texture) {
        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: use image read");

        const bool do_texture_update = false;
        image::ImageCache &image_cache = image::ImageCache::getInstance();
        out_color_texture = image::read_texture_image_file(
            texture_manager, image_cache, m_temp_image, m_temp_pixel_buffer,
            m_temp_meta_data, file_path, expanded_file_path, do_texture_update);

        if (out_color_texture) {
            MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: texture->name()="
                              << out_color_texture->name().asChar());
            const void *resource_handle = out_color_texture->resourceHandle();
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture->resourceHandle()="
                << resource_handle);
            if (resource_handle) {
                MMSOLVER_MAYA_VRB(
                    "mmImagePlaneGeometry2Override: *texture->resourceHandle()="
                    << *(uint32_t *)resource_handle);
            }

            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture->hasAlpha()="
                << out_color_texture->hasAlpha());
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture->hasZeroAlpha()="
                << out_color_texture->hasZeroAlpha());
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture->hasTransparentAlpha()="
                << out_color_texture->hasTransparentAlpha());
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture->bytesPerPixel()="
                << out_color_texture->bytesPerPixel());

            MTextureDescription texture_desc;
            out_color_texture->textureDescription(texture_desc);

            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fWidth="
                << texture_desc.fWidth);
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fHeight="
                << texture_desc.fHeight);
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fDepth="
                << texture_desc.fDepth);
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fBytesPerRow="
                << texture_desc.fBytesPerRow);
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fBytesPerSlice="
                << texture_desc.fBytesPerSlice);
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fMipmaps="
                << texture_desc.fMipmaps);
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fArraySlices="
                << texture_desc.fArraySlices);
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fFormat="
                << texture_desc.fFormat);
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fTextureType="
                << texture_desc.fTextureType);
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: texture_desc.fEnvMapType="
                << texture_desc.fEnvMapType);
        }
    }

    if (!out_texture_sampler) {
        MHWRender::MSamplerStateDesc sampler_desc;
        sampler_desc.addressU = MHWRender::MSamplerState::kTexWrap;
        sampler_desc.addressV = MHWRender::MSamplerState::kTexWrap;
        sampler_desc.addressW = MHWRender::MSamplerState::kTexWrap;
        // kMinMagMipPoint is "nearest pixel" filtering.
        sampler_desc.filter = MHWRender::MSamplerState::kMinMagMipPoint;
        out_texture_sampler =
            MHWRender::MStateManager::acquireSamplerState(sampler_desc);
    }

    if (out_texture_sampler) {
        status =
            shader->setParameter("gImageTextureSampler", *out_texture_sampler);
        CHECK_MSTATUS(status);
    } else {
        MMSOLVER_MAYA_WRN(
            "mmImagePlaneGeometry2Override: "
            "Could not get texture sampler."
            << " out_texture_sampler=" << out_texture_sampler);
    }

    if (out_color_texture) {
        MHWRender::MTextureAssignment texture_assignment;
        texture_assignment.texture = out_color_texture;
        status = shader->setParameter("gImageTexture", texture_assignment);
        CHECK_MSTATUS(status);

        out_color_texture = nullptr;
    } else {
        MMSOLVER_MAYA_VRB(
            "mmImagePlaneGeometry2Override: "
            "Could not get color texture; did not assign texture."
            << " out_color_texture=" << out_color_texture);
    }

    return;
}

void ImagePlaneGeometry2Override::updateRenderItems(const MDagPath &path,
                                                    MRenderItemList &list) {
    const bool verbose = false;
    if (!m_geometry_node_path.isValid()) {
        MMSOLVER_MAYA_VRB(
            "mmImagePlaneGeometry2Override: "
            "Geometry node DAG path is not valid.");
        return;
    }

    MHWRender::MRenderer *renderer = MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_WRN(
            "mmImagePlaneGeometry2Override: "
            "Could not get MRenderer.");
        return;
    }

    const MHWRender::MShaderManager *shaderManager =
        renderer->getShaderManager();
    if (!shaderManager) {
        MMSOLVER_MAYA_WRN(
            "mmImagePlaneGeometry2Override: "
            "Could not get MShaderManager.");
        return;
    }

    if (m_geometry_node_type != MFn::kMesh) {
        MMSOLVER_MAYA_WRN("mmImagePlaneGeometry2Override: "
                          << "Only Meshes are supported, geometry node "
                             "given is not a mesh.");
        return;
    }

    MRenderItem *wireframeItem = nullptr;
    const bool draw_wireframe = false;  // for debugging.
    if (draw_wireframe) {
        // Add render item for drawing wireframe on the mesh
        int index = list.indexOf(renderItemName_imagePlaneWireframe);
        if (index >= 0) {
            wireframeItem = list.itemAt(index);
        } else {
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: "
                "Generate wireframe MRenderItem...");
            wireframeItem = MRenderItem::Create(
                renderItemName_imagePlaneWireframe, MRenderItem::DecorationItem,
                MGeometry::kLines);

            auto draw_mode = MGeometry::kAll;  // Draw in all visible modes.
            auto depth_priority = MRenderItem::sActiveWireDepthPriority;

            wireframeItem->setDrawMode(draw_mode);
            wireframeItem->depthPriority(depth_priority);

            list.append(wireframeItem);
        }
    }

    // Add render item for drawing shaded on the mesh
    MRenderItem *shadedItem = nullptr;
    int index = list.indexOf(renderItemName_imagePlaneShaded);
    if (index >= 0) {
        shadedItem = list.itemAt(index);
    } else {
        MMSOLVER_MAYA_VRB(
            "mmImagePlaneGeometry2Override: "
            "Generate shaded MRenderItem...");
        shadedItem = MRenderItem::Create(renderItemName_imagePlaneShaded,
                                         MRenderItem::NonMaterialSceneItem,
                                         MGeometry::kTriangles);

        auto draw_mode = MGeometry::kAll;  // Draw in all visible modes.
        auto depth_priority = MRenderItem::sDormantWireDepthPriority;

        shadedItem->setDrawMode(draw_mode);
        shadedItem->depthPriority(depth_priority);

        list.append(shadedItem);
    }

    if (wireframeItem) {
        wireframeItem->enable(m_visible);

        MShaderInstance *shader =
            shaderManager->getStockShader(MShaderManager::k3dSolidShader);
        if (shader) {
            static const float color[] = {1.0f, 0.0f, 0.0f, 1.0f};
            MStatus status = shader->setParameter("solidColor", color);
            CHECK_MSTATUS(status);
            wireframeItem->setShader(shader);
            shaderManager->releaseShader(shader);
        }
    }

    if (shadedItem) {
        shadedItem->enable(m_visible);

        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: "
                          << "shadedItem->isEnabled()="
                          << shadedItem->isEnabled());
        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: "
                          << "shadedItem->isShaderFromNode()="
                          << shadedItem->isShaderFromNode());
        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: "
                          << "shadedItem->isMultiDraw()="
                          << shadedItem->isMultiDraw());
        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: "
                          << "shadedItem->isConsolidated()="
                          << shadedItem->isConsolidated());
        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: "
                          << "shadedItem->wantConsolidation()="
                          << shadedItem->wantConsolidation());
        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: "
                          << "shadedItem->castsShadows()="
                          << shadedItem->castsShadows());
        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: "
                          << "shadedItem->receivesShadows()="
                          << shadedItem->receivesShadows());
        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: "
                          << "shadedItem->excludedFromPostEffects()="
                          << shadedItem->excludedFromPostEffects());
        MMSOLVER_MAYA_VRB("mmImagePlaneGeometry2Override: "
                          << "shadedItem->supportsAdvancedTransparency()="
                          << shadedItem->supportsAdvancedTransparency());

        if (!m_shader || m_update_shader) {
            if (m_shader) {
                shaderManager->releaseShader(m_shader);
            }

            const MString shader_file_path =
                mmsolver::render::find_shader_file_path("mmImagePlane.ogsfx");
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneGeometry2Override: "
                "found shader_file_path=\""
                << shader_file_path << "\"");

            if (shader_file_path.length() > 0) {
                MString shader_text =
                    mmsolver::render::read_shader_file(shader_file_path);

                std::string ocio_shader_text;
                mmcolorio::generate_shader_text(
                    m_input_color_space_name.asChar(),
                    m_output_color_space_name.asChar(), ocio_shader_text);
                MMSOLVER_MAYA_VRB(
                    "mmImagePlaneGeometry2Override: "
                    "ocio_shader_text=\""
                    << ocio_shader_text << "\"");
                if (ocio_shader_text.size() > 0) {
                    const MString ocio_function_declare_text = MString(
                        "vec4 OCIODisplay(vec4 passthrough) { return "
                        "passthrough; "
                        "}");
                    MStatus status = shader_text.substitute(
                        ocio_function_declare_text,
                        MString(ocio_shader_text.c_str()));
                    CHECK_MSTATUS(status);
                }

                m_shader =
                    mmsolver::render::compile_shader_text(shader_text, "Main");
            }

            if (m_shader) {
                m_update_shader = false;
            }
        }

        if (m_shader) {
            MHWRender::MTextureManager *texture_manager =
                renderer->getTextureManager();
            if (!texture_manager) {
                MMSOLVER_MAYA_WRN(
                    "mmImagePlaneGeometry2Override: "
                    "Could not get MTextureManager.");
                return;
            }

            set_shader_instance_parameters(
                m_shader, texture_manager, m_color_gain, m_color_exposure,
                m_color_gamma, m_color_saturation, m_color_soft_clip,
                m_alpha_gain, m_default_color, m_ignore_alpha, m_flip, m_flop,
                m_is_transparent, m_image_display_channel, m_frame, m_file_path,
                m_input_color_space_name, m_output_color_space_name,
                m_color_texture, m_texture_sampler);

            shadedItem->setShader(m_shader);
        }
    }
}

void ImagePlaneGeometry2Override::populateGeometry(
    const MGeometryRequirements &requirements,
    const MRenderItemList &renderItems, MGeometry &data) {
    const bool verbose = false;
    if (!m_geometry_node_path.isValid()) {
        MMSOLVER_MAYA_VRB(
            "mmImagePlaneGeometry2Override: "
            "Geometry node DAG path is not valid.");
        return;
    }

    MStatus status;

    // kPolyGeom_Normal = Normal Indicates the polygon performs the
    // default geometry.
    //
    // kPolyGeom_NotSharing = NotSharing Indicates if you don't want
    // vertex sharing to be computed by the extractor. Vertex buffer
    // size will not be reduced if sharing can be performed.
    //
    // kPolyGeom_BaseMesh = BaseMesh Indicates if you want the base
    // geometry in smoothCage mode. The geometry in extractor is
    // always the base geometry in normal mode.
    MHWRender::MPolyGeomOptions polygon_geometry_options =
        MHWRender::kPolyGeom_Normal | MHWRender::kPolyGeom_BaseMesh;

    MGeometryExtractor extractor(requirements, m_geometry_node_path,
                                 polygon_geometry_options, &status);
    if (status == MS::kFailure) {
        CHECK_MSTATUS(status);
        return;
    }

    const MVertexBufferDescriptorList &descList =
        requirements.vertexRequirements();
    for (int reqNum = 0; reqNum < descList.length(); ++reqNum) {
        MVertexBufferDescriptor desc;
        if (!descList.getDescriptor(reqNum, desc)) {
            continue;
        }

        auto desc_semantic = desc.semantic();
        if ((desc_semantic == MGeometry::kPosition) ||
            (desc_semantic == MGeometry::kNormal) ||
            (desc_semantic == MGeometry::kTexture) ||
            (desc_semantic == MGeometry::kTangent) ||
            (desc_semantic == MGeometry::kBitangent) ||
            (desc_semantic == MGeometry::kColor)) {
            MVertexBuffer *vertexBuffer = data.createVertexBuffer(desc);
            if (vertexBuffer) {
                uint32_t vertexCount = extractor.vertexCount();
                bool writeOnly =
                    true;  // We don't need the current buffer values.
                float *data = static_cast<float *>(
                    vertexBuffer->acquire(vertexCount, writeOnly));
                if (data) {
                    status =
                        extractor.populateVertexBuffer(data, vertexCount, desc);
                    if (status == MS::kFailure) return;
                    vertexBuffer->commit(data);
                }
            }
        }
    }

    for (int i = 0; i < renderItems.length(); ++i) {
        const MRenderItem *item = renderItems.itemAt(i);
        if (!item) {
            continue;
        }

        MIndexBuffer *indexBuffer =
            data.createIndexBuffer(MGeometry::kUnsignedInt32);
        if (!indexBuffer) {
            continue;
        }

        if (item->primitive() == MGeometry::kTriangles) {
            MIndexBufferDescriptor triangleDesc(
                MIndexBufferDescriptor::kTriangle, MString(),
                MGeometry::kTriangles, 3);
            uint32_t numTriangles = extractor.primitiveCount(triangleDesc);
            bool writeOnly = true;  // We don't need the current buffer values.
            uint32_t *indices = static_cast<uint32_t *>(
                indexBuffer->acquire(3 * numTriangles, writeOnly));

            status = extractor.populateIndexBuffer(indices, numTriangles,
                                                   triangleDesc);
            if (status == MS::kFailure) {
                return;
            }
            indexBuffer->commit(indices);
        } else if (item->primitive() == MGeometry::kLines) {
            MIndexBufferDescriptor edgeDesc(MIndexBufferDescriptor::kEdgeLine,
                                            MString(), MGeometry::kLines, 2);
            uint32_t numEdges = extractor.primitiveCount(edgeDesc);
            bool writeOnly = true;  // We don't need the current buffer values.
            uint32_t *indices = static_cast<uint32_t *>(
                indexBuffer->acquire(2 * numEdges, writeOnly));

            status = extractor.populateIndexBuffer(indices, numEdges, edgeDesc);
            if (status == MS::kFailure) {
                return;
            }
            indexBuffer->commit(indices);
        }

        item->associateWithIndexBuffer(indexBuffer);
    }
}

void ImagePlaneGeometry2Override::cleanUp() {}

#if MAYA_API_VERSION >= 20190000
bool ImagePlaneGeometry2Override::requiresGeometryUpdate() const {
    const bool verbose = false;
    if (m_geometry_node_path.isValid()) {
        MMSOLVER_MAYA_VRB(
            "ImagePlaneGeometry2Override::requiresGeometryUpdate: false");
        return false;
    }
    MMSOLVER_MAYA_VRB(
        "ImagePlaneGeometry2Override::requiresGeometryUpdate: true");
    return true;
}

bool ImagePlaneGeometry2Override::requiresUpdateRenderItems(
    const MDagPath &path) const {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(
        "ImagePlaneGeometry2Override::requiresUpdateRenderItems: true: "
        << path.fullPathName().asChar());
    return true;  // Always update the render items.
}
#endif

bool ImagePlaneGeometry2Override::hasUIDrawables() const { return true; }

void ImagePlaneGeometry2Override::addUIDrawables(
    const MDagPath &path, MUIDrawManager &drawManager,
    const MFrameContext &frameContext) {
    if (!m_draw_hud) {
        return;
    }

    const float pos_coord_x = 0.48f;
    const float pos_coord_y = 0.52f;
    const MColor text_color = MColor(1.0f, 0.0f, 0.0f);
    const uint32_t font_size = 12;
    const int *background_size = nullptr;
    const MColor *background_color = nullptr;
    auto dynamic = false;

    if (m_draw_image_size) {
        auto text_position = MPoint(pos_coord_x, pos_coord_y, 0.0);
        auto font_alignment = MUIDrawManager::kRight;

        drawManager.beginDrawable();
        drawManager.setColor(text_color);
        drawManager.setFontSize(font_size);
        drawManager.text(text_position, m_image_size, font_alignment,
                         background_size, background_color, dynamic);
        drawManager.endDrawable();
    }

    if (m_draw_camera_size) {
        auto text_position = MPoint(-pos_coord_x, pos_coord_y, 0.0);
        auto font_alignment = MUIDrawManager::kLeft;

        drawManager.beginDrawable();
        drawManager.setColor(text_color);
        drawManager.setFontSize(font_size);
        drawManager.text(text_position, m_camera_size, font_alignment,
                         background_size, background_color, dynamic);
        drawManager.endDrawable();
    }
}

}  // namespace mmsolver
