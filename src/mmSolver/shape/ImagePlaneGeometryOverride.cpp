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

#include "ImagePlaneGeometryOverride.h"

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>

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
#include <maya/MSharedPtr.h>
#include <maya/MUserData.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/shape/constant_texture_data.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {

const MString renderItemName_imagePlaneWireframe =
    MString("imagePlaneWireframe");
const MString renderItemName_imagePlaneShaded = MString("imagePlaneShaded");

ImagePlaneGeometryOverride::ImagePlaneGeometryOverride(const MObject &obj)
    : MHWRender::MPxGeometryOverride(obj)
    , m_this_node(obj)
    , m_visible(true)
    , m_draw_hud(false)
    , m_draw_image_size(false)
    , m_draw_camera_size(false)
    , m_geometry_node_type(MFn::kInvalid)
    , m_use_shader_node(true)
    , m_use_image_read(false)
    , m_use_color_bars(false)
    , m_image_display_channel(ImageDisplayChannel::kAll)
    , m_color_gain(1.0f)
    , m_alpha_gain(1.0f)
    , m_ignore_alpha(false)
    , m_flip(false)
    , m_flop(false)
    , m_is_transparent(false)
    , m_file_path()
    , m_shader(nullptr)
    , m_color_texture(nullptr)
    , m_texture_sampler(nullptr) {
    m_model_editor_changed_callback_id = MEventMessage::addEventCallback(
        "modelEditorChanged",
        ImagePlaneGeometryOverride::on_model_editor_changed_func, this);
#if MAYA_API_VERSION >= 20200000
    m_shader_link_lost_user_data_ptr =
        ShaderLinkLostUserDataPtr(new ShaderLinkLostUserData());
#elif
    m_shader_link_lost_user_data = ShaderLinkLostUserData();
#endif
}

ImagePlaneGeometryOverride::~ImagePlaneGeometryOverride() {
    if (m_model_editor_changed_callback_id != 0) {
        MMessage::removeCallback(m_model_editor_changed_callback_id);
        m_model_editor_changed_callback_id = 0;
    }

    if (m_color_texture) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        MHWRender::MTextureManager *textureMgr =
            renderer ? renderer->getTextureManager() : nullptr;
        if (textureMgr) {
            textureMgr->releaseTexture(m_color_texture);
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

void ImagePlaneGeometryOverride::on_model_editor_changed_func(
    void *clientData) {
    // Mark the node as being dirty so that it can update on display
    // appearance switch among wireframe and shaded.
    ImagePlaneGeometryOverride *ovr =
        static_cast<ImagePlaneGeometryOverride *>(clientData);
    if (ovr && !ovr->m_this_node.isNull()) {
        MHWRender::MRenderer::setGeometryDrawDirty(ovr->m_this_node);
    }
}

void ImagePlaneGeometryOverride::shader_link_lost_func(
    ShaderLinkLostUserData *userData) {
    // TODO: What should this function do? Does it need to do anything?
    MMSOLVER_MAYA_DBG(
        "mmImagePlaneShape: shader_link_lost_func: link_lost_count="
        << (*userData).link_lost_count
        << " set_shader_count=" << (*userData).set_shader_count);
    (*userData).link_lost_count += 1;
}

MHWRender::DrawAPI ImagePlaneGeometryOverride::supportedDrawAPIs() const {
    return (MHWRender::kOpenGL | MHWRender::kDirectX11 |
            MHWRender::kOpenGLCoreProfile);
}

bool getUpstreamNodeFromConnection(const MObject &this_node,
                                   const MString &attr_name,
                                   MPlugArray &out_connections) {
    MStatus status;
    MFnDependencyNode mfn_depend_node(this_node);

    bool wantNetworkedPlug = true;
    MPlug plug =
        mfn_depend_node.findPlug(attr_name, wantNetworkedPlug, &status);
    if (status != MStatus::kSuccess) {
        CHECK_MSTATUS(status);
        return false;
    }
    if (plug.isNull()) {
        MMSOLVER_MAYA_WRN("Could not get plug for \""
                          << mfn_depend_node.name().asChar() << "."
                          << attr_name.asChar() << "\" node.");
        return false;
    }

    bool as_destination = true;
    bool as_source = false;
    // Ask for plugs connecting to this node's ".shaderNode"
    // attribute.
    plug.connectedTo(out_connections, as_destination, as_source, &status);
    if (status != MStatus::kSuccess) {
        CHECK_MSTATUS(status);
        return false;
    }
    if (out_connections.length() == 0) {
        MMSOLVER_MAYA_WRN("No connections to the \""
                          << mfn_depend_node.name().asChar() << "."
                          << attr_name.asChar() << "\" attribute.");
        return false;
    }
    return true;
}

void calculate_node_image_size_string(MDagPath &objPath,
                                      const uint32_t int_precision,
                                      const uint32_t double_precision,
                                      bool &out_draw_image_size,
                                      MString &out_image_size) {
    MStatus status = MS::kSuccess;

    double width = 1.0;
    double height = 1.0;
    double pixel_aspect = 1.0;

    status = getNodeAttr(objPath, ImagePlaneShapeNode::m_draw_image_size,
                         out_draw_image_size);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShapeNode::m_image_width, width);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShapeNode::m_image_height, height);
    CHECK_MSTATUS(status);

    status = getNodeAttr(objPath, ImagePlaneShapeNode::m_image_pixel_aspect,
                         pixel_aspect);
    CHECK_MSTATUS(status);

    double aspect = (width * pixel_aspect) / height;

    MString width_string;
    MString height_string;
    MString pixel_aspect_string;
    MString aspect_string;

    width_string.set(width, int_precision);
    height_string.set(height, int_precision);
    pixel_aspect_string.set(pixel_aspect, double_precision);
    aspect_string.set(aspect, double_precision);

    out_image_size = MString("Image: ") + width_string + MString(" x ") +
                     height_string + MString(" | PAR ") + pixel_aspect_string +
                     MString(" | ") + aspect_string;
    return;
}

void calculate_node_camera_size_string(MDagPath &objPath,
                                       const uint32_t double_precision,
                                       bool &out_draw_camera_size,
                                       MString &out_camera_size) {
    MStatus status = MS::kSuccess;

    double width = 0.0;
    double height = 0.0;

    status = getNodeAttr(objPath, ImagePlaneShapeNode::m_draw_camera_size,
                         out_draw_camera_size);
    CHECK_MSTATUS(status);

    status =
        getNodeAttr(objPath, ImagePlaneShapeNode::m_camera_width_inch, width);
    CHECK_MSTATUS(status);

    status =
        getNodeAttr(objPath, ImagePlaneShapeNode::m_camera_height_inch, height);
    CHECK_MSTATUS(status);

    double aspect = width / height;

    MString width_string;
    MString height_string;
    MString aspect_string;

    width_string.set(width * INCH_TO_MM, double_precision);
    height_string.set(height * INCH_TO_MM, double_precision);
    aspect_string.set(aspect, double_precision);

    out_camera_size = MString("Camera: ") + width_string + MString("mm x ") +
                      height_string + MString("mm | ") + aspect_string;
}

void ImagePlaneGeometryOverride::query_node_attributes(
    MObject &node, MDagPath &out_camera_node_path, bool &out_visible,
    bool &out_visible_to_camera_only, bool &out_is_under_camera,
    bool &out_draw_hud, bool &out_draw_image_size, MString &out_image_size,
    bool &out_draw_camera_size, MString &out_camera_size,
    bool &out_use_shader_node, bool &out_use_image_read,
    bool &out_use_color_bars, ImageDisplayChannel &out_image_display_channel,
    float &out_color_gain, float &out_alpha_gain, bool &out_ignore_alpha,
    bool &out_flip, bool &out_flop, bool &out_is_transparent,
    MString &out_file_path, MPlug &out_color_plug) {
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

    status = getNodeAttr(objPath, ImagePlaneShapeNode::m_visible_to_camera_only,
                         out_visible_to_camera_only);
    CHECK_MSTATUS(status);

    status =
        getNodeAttr(objPath, ImagePlaneShapeNode::m_draw_hud, out_draw_hud);
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
    calculate_node_image_size_string(objPath, int_precision, double_precision,
                                     out_draw_image_size, out_image_size);
    calculate_node_camera_size_string(objPath, double_precision,
                                      out_draw_camera_size, out_camera_size);

    // "use" attributes.
    {
        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_use_shader_node,
                             out_use_shader_node);
        CHECK_MSTATUS(status);

        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_use_image_read,
                             out_use_image_read);
        CHECK_MSTATUS(status);

        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_use_color_bars,
                             out_use_color_bars);
        CHECK_MSTATUS(status);
    }

    // Shader attributes.
    {
        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_color_gain,
                             out_color_gain);
        CHECK_MSTATUS(status);

        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_alpha_gain,
                             out_alpha_gain);
        CHECK_MSTATUS(status);

        short image_display_channel_value = 0;
        status =
            getNodeAttr(objPath, ImagePlaneShapeNode::m_image_display_channel,
                        image_display_channel_value);
        CHECK_MSTATUS(status);
        out_image_display_channel =
            static_cast<ImageDisplayChannel>(image_display_channel_value);

        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_ignore_alpha,
                             out_ignore_alpha);
        CHECK_MSTATUS(status);

        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_flip, out_flip);
        CHECK_MSTATUS(status);

        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_flop, out_flop);
        CHECK_MSTATUS(status);

        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_is_transparent,
                             out_is_transparent);
        CHECK_MSTATUS(status);

        status = getNodeAttr(objPath, ImagePlaneShapeNode::m_file_path,
                             out_file_path);
        CHECK_MSTATUS(status);

        status = getNodeAttrPlug(objPath, ImagePlaneShapeNode::m_color,
                                 out_color_plug);
        CHECK_MSTATUS(status);
    }
}

void find_geometry_node_path(MObject &node, MString &attr_name,
                             MDagPath &out_geometry_node_path,
                             MFn::Type &out_geometry_node_type) {
    const auto verbose = false;

    MPlugArray connections;
    bool ok = getUpstreamNodeFromConnection(node, attr_name, connections);

    if (ok) {
        for (uint32_t i = 0; i < connections.length(); ++i) {
            MObject node = connections[i].node();

            if (node.hasFn(MFn::kMesh)) {
                MDagPath path;
                MDagPath::getAPathTo(node, path);
                out_geometry_node_path = path;
                out_geometry_node_type = path.apiType();
                MMSOLVER_MAYA_VRB(
                    "Validated geometry node: "
                    << " path="
                    << out_geometry_node_path.fullPathName().asChar()
                    << " type=" << node.apiTypeStr());
                break;
            } else {
                MMSOLVER_MAYA_WRN(
                    "Geometry node is not correct type:"
                    << " path="
                    << out_geometry_node_path.fullPathName().asChar()
                    << " type=" << node.apiTypeStr());
            }
        }
    }
}

void find_shader_node(MObject &node, MString &attr_name,
                      MObject &out_shader_node,
                      MFn::Type &out_shader_node_type) {
    const auto verbose = false;

    MPlugArray connections;
    bool ok = getUpstreamNodeFromConnection(node, attr_name, connections);

    if (ok) {
        for (uint32_t i = 0; i < connections.length(); ++i) {
            MObject node = connections[i].node();

            MFnDependencyNode mfn_depend_node(node);
            if (node.hasFn(MFn::kSurfaceShader) ||
                node.hasFn(MFn::kHwShaderNode) ||
                node.hasFn(MFn::kPluginHardwareShader) ||
                node.hasFn(MFn::kPluginHwShaderNode)) {
                out_shader_node = node;
                out_shader_node_type = node.apiType();
                MMSOLVER_MAYA_VRB("Validated shader node:"
                                  << " name=" << mfn_depend_node.name().asChar()
                                  << " type=" << node.apiTypeStr());
                break;
            } else {
                MMSOLVER_MAYA_WRN("Shader node is not correct type: "
                                  << " name=" << mfn_depend_node.name().asChar()
                                  << " type=" << node.apiTypeStr());
            }
        }
    }
}

void find_camera_node_path(MObject &node, MString &attr_name,
                           MDagPath &out_camera_node_path,
                           MFn::Type &out_camera_node_type) {
    const auto verbose = false;

    MPlugArray connections;
    bool ok = getUpstreamNodeFromConnection(node, attr_name, connections);

    if (ok) {
        for (uint32_t i = 0; i < connections.length(); ++i) {
            MObject node = connections[i].node();

            if (node.hasFn(MFn::kCamera)) {
                MDagPath path;
                MDagPath::getAPathTo(node, path);
                out_camera_node_path = path;
                out_camera_node_type = path.apiType();
                MMSOLVER_MAYA_VRB(
                    "Validated camera node: "
                    << " path=" << out_camera_node_path.fullPathName().asChar()
                    << " type=" << node.apiTypeStr());
                break;
            } else {
                MMSOLVER_MAYA_WRN(
                    "Camera node is not correct type:"
                    << " path=" << out_camera_node_path.fullPathName().asChar()
                    << " type=" << node.apiTypeStr());
            }
        }
    }
}

void ImagePlaneGeometryOverride::updateDG() {
    if (!m_geometry_node_path.isValid()) {
        MString attr_name = "geometryNode";
        find_geometry_node_path(m_this_node, attr_name, m_geometry_node_path,
                                m_geometry_node_type);
    }

    if (m_shader_node.isNull()) {
        MString attr_name = "shaderNode";
        find_shader_node(m_this_node, attr_name, m_shader_node,
                         m_shader_node_type);
    }

    if (!m_camera_node_path.isValid()) {
        MString attr_name = "cameraNode";
        find_camera_node_path(m_this_node, attr_name, m_camera_node_path,
                              m_camera_node_type);
    }

    // Query Attributes from the base node.
    ImagePlaneGeometryOverride::query_node_attributes(
        m_this_node, m_camera_node_path, m_visible, m_visible_to_camera_only,
        m_is_under_camera, m_draw_hud, m_draw_image_size, m_image_size,
        m_draw_camera_size, m_camera_size, m_use_shader_node, m_use_image_read,
        m_use_color_bars, m_image_display_channel, m_color_gain, m_alpha_gain,
        m_ignore_alpha, m_flip, m_flop, m_is_transparent, m_file_path,
        m_color_plug);
}

MTexture *create_color_bars_texture(
    MHWRender::MTextureManager *textureManager) {
    MHWRender::MTextureDescription texture_desc;
    texture_desc.setToDefault2DTexture();
    texture_desc.fWidth = COLOR_BARS_F32_4X4_PIXEL_WIDTH;
    texture_desc.fHeight = COLOR_BARS_F32_4X4_PIXEL_HEIGHT;
    texture_desc.fDepth = 1;
    texture_desc.fBytesPerSlice =
        COLOR_BARS_F32_4X4_PIXEL_COUNT * COLOR_BARS_F32_4X4_PIXEL_BYTE_COUNT;
    texture_desc.fBytesPerRow =
        COLOR_BARS_F32_4X4_PIXEL_WIDTH * COLOR_BARS_F32_4X4_PIXEL_BYTE_COUNT;
    texture_desc.fMipmaps = 1;
    texture_desc.fArraySlices = 1;
    texture_desc.fTextureType = MHWRender::kImage2D;
    texture_desc.fFormat = MHWRender::kR32G32B32A32_FLOAT;

    const bool generate_mip_maps = false;
    return textureManager->acquireTexture(
        "", texture_desc, &(COLOR_BARS_F32_4X4[0]), generate_mip_maps);
}

MTexture *create_plug_texture(MHWRender::MTextureManager *textureManager,
                              MPlug &texture_plug) {
    MObject texture_node;
    MStatus status = get_connected_node(texture_plug, texture_node);
    CHECK_MSTATUS(status);
    if (status != MS::kSuccess) {
        return nullptr;
    }

    if (texture_node.isNull()) {
        // For when the plug is just a color value, but doesn't have
        // any input texture.
        const bool generate_mip_maps = false;
        const int width = 2;
        const int height = 2;
        return textureManager->acquireTexture("", texture_plug, width, height,
                                              generate_mip_maps);
    }

    const bool allowBackgroundLoad = false;
    return textureManager->acquireTexture(texture_node, allowBackgroundLoad);
}

void *get_image_pixel_data(const MImage &image,
                           const MImage::MPixelType pixel_type,
                           const uint8_t number_of_channels,
                           uint8_t &out_bytes_per_channel,
                           MHWRender::MRasterFormat &out_texture_format) {
    const bool verbose = false;

    const uint32_t print_num_pixels = 8;
    void *pixel_data = nullptr;
    if (pixel_type == MImage::MPixelType::kByte) {
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: get_image_pixel_data:"
                          << " pixel_type=MImage::MPixelType::kByte");

        // 8-bit unsigned integers use 1 byte.
        out_bytes_per_channel = 1;

        const bool is_rgba = image.isRGBA();
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: get_image_pixel_data:"
                          << " is_rgba=" << is_rgba);
        if (is_rgba) {
            out_texture_format = MHWRender::kR8G8B8A8_UNORM;
        } else {
            out_texture_format = MHWRender::kB8G8R8A8;
        }

        unsigned char *pixels = image.pixels();

        for (uint32_t row = 0; row <= print_num_pixels; row++) {
            const uint32_t index = row * number_of_channels;
            const uint32_t r = static_cast<uint32_t>(pixels[index + 0]);
            const uint32_t g = static_cast<uint32_t>(pixels[index + 1]);
            const uint32_t b = static_cast<uint32_t>(pixels[index + 2]);
            const uint32_t a = static_cast<uint32_t>(pixels[index + 3]);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: get_image_pixel_data:"
                              << " row=" << row << " pixel=" << r << ", " << g
                              << ", " << b << ", " << a);
        }

        pixel_data = static_cast<void *>(pixels);
    } else if (pixel_type == MImage::MPixelType::kFloat) {
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: get_image_pixel_data:"
                          << " pixel_type=MImage::MPixelType::kFloat");

        // 32-bit floats use 4 bytes.
        out_bytes_per_channel = 4;

        out_texture_format = MHWRender::kR32G32B32A32_FLOAT;

        float *floatPixels = image.floatPixels();

        for (uint32_t row = 0; row <= print_num_pixels; row++) {
            const uint32_t index = row * number_of_channels;
            const float r = floatPixels[index + 0];
            const float g = floatPixels[index + 1];
            const float b = floatPixels[index + 2];
            const float a = floatPixels[index + 3];
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: get_image_pixel_data:"
                              << " row=" << row << " pixel=" << r << ", " << g
                              << ", " << b << ", " << a);
        }

        pixel_data = static_cast<void *>(floatPixels);
    } else {
        MMSOLVER_MAYA_ERR("mmImagePlaneShape: get_image_pixel_data: "
                          << "Invalid pixel type is "
                          << static_cast<int>(pixel_type));
        return nullptr;
    }

    return pixel_data;
}

MStatus update_texture(MHWRender::MTextureManager *textureManager,
                       MImage &image, const MImage::MPixelType pixel_type,
                       MTexture *texture, const bool generate_mip_maps,
                       const uint8_t number_of_channels) {
    const bool verbose = false;

    MHWRender::MRasterFormat texture_format;
    uint8_t bytes_per_channel = 0;
    const void *pixel_data =
        get_image_pixel_data(image, pixel_type, number_of_channels,
                             bytes_per_channel, texture_format);

    // The default value of this argument is 0. This means to use
    // the texture's width * the number of bytes per pixel.
    unsigned int rowPitch = 0;

    MHWRender::MTextureUpdateRegion *region = nullptr;

    MMSOLVER_MAYA_VRB("mmImagePlaneShape: update_texture: update");
    MStatus status =
        texture->update(pixel_data, generate_mip_maps, rowPitch, region);

    return status;
}

MTexture *acquire_texture(MHWRender::MTextureManager *textureManager,
                          MImage &image, const MString &file_path,
                          const MImage::MPixelType pixel_type,
                          const bool generate_mip_maps,
                          const uint8_t number_of_channels) {
    const bool verbose = false;

    unsigned int width = 0;
    unsigned int height = 0;
    image.getSize(width, height);
    MMSOLVER_MAYA_VRB("mmImagePlaneShape: acquire_texture:"
                      << " width=" << width << " height=" << height);

    MHWRender::MTextureDescription texture_desc;
    texture_desc.setToDefault2DTexture();
    texture_desc.fWidth = width;
    texture_desc.fHeight = height;
    texture_desc.fDepth = 1;

    texture_desc.fMipmaps = 1;
    texture_desc.fArraySlices = 1;
    texture_desc.fTextureType = MHWRender::kImage2D;

    uint8_t bytes_per_channel = 0;
    const void *pixel_data =
        get_image_pixel_data(image, pixel_type, number_of_channels,
                             bytes_per_channel, texture_desc.fFormat);

    MMSOLVER_MAYA_VRB("mmImagePlaneShape: acquire_texture: "
                      << "pixel_data=" << pixel_data);
    if (!pixel_data) {
        MMSOLVER_MAYA_ERR("mmImagePlaneShape: acquire_texture: "
                          << "Invalid pixel data! ");
        return nullptr;
    }

    // MImage seems to always convert images into 4 channels.
    texture_desc.fBytesPerRow = number_of_channels * bytes_per_channel * width;
    texture_desc.fBytesPerSlice = texture_desc.fBytesPerRow * height;

    MMSOLVER_MAYA_VRB(
        "mmImagePlaneShape: acquire_texture:"
        << " number_of_channels=" << static_cast<int>(number_of_channels)
        << " bytes_per_channel=" << static_cast<int>(bytes_per_channel));

    MMSOLVER_MAYA_VRB("mmImagePlaneShape: acquire_texture:"
                      << " fBytesPerRow=" << texture_desc.fBytesPerRow
                      << " fBytesPerSlice=" << texture_desc.fBytesPerSlice);

    MMSOLVER_MAYA_VRB("mmImagePlaneShape: acquire_texture: acquireTexture");
    return textureManager->acquireTexture(file_path, texture_desc, pixel_data,
                                          generate_mip_maps);
}

MTexture *read_image_file(MHWRender::MTextureManager *textureManager,
                          MImage &image, const MString &file_path,
                          const MImage::MPixelType pixel_type,
                          const bool do_texture_update) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("mmImagePlaneShape: read_image_file:"
                      << " file_path=" << file_path.asChar());

    MTexture *texture = textureManager->findTexture(file_path);
    MMSOLVER_MAYA_VRB(
        "mmImagePlaneShape: read_image_file: findTexture: " << texture);
    if (texture && !do_texture_update) {
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: read_image_file:"
                          << " texture=" << texture);
        return texture;
    }

    // TODO: Should we test to see if the file exists first, before
    // attempting to read, or just catch the failure?
    MStatus status = image.readFromFile(file_path, pixel_type);
    CHECK_MSTATUS(status);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_WRN("mmImagePlaneShape: read_image_file:"
                          << " failed to read image \"" << file_path.asChar()
                          << "\".");
        return nullptr;
    }

    image.verticalFlip();

    // TODO: Apply colour correction via OCIO.

    const bool generate_mip_maps = false;
    const uint8_t number_of_channels = 4;
    if (texture) {
        status = update_texture(textureManager, image, pixel_type, texture,
                                generate_mip_maps, number_of_channels);
        CHECK_MSTATUS(status);
        if (status == MS::kSuccess) {
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: read_image_file:"
                              << " texture updated!");
        }
    } else {
        texture = acquire_texture(textureManager, image, file_path, pixel_type,
                                  generate_mip_maps, number_of_channels);
    }

    MMSOLVER_MAYA_VRB("mmImagePlaneShape: read_image_file:"
                      << " texture=" << texture);

    return texture;
}

void ImagePlaneGeometryOverride::set_shader_instance_parameters(
    MShaderInstance *shader, MHWRender::MTextureManager *textureManager,
    const float color_gain, const float alpha_gain, const bool ignore_alpha,
    const bool flip, const bool flop, const bool is_transparent,
    const ImageDisplayChannel image_display_channel, const MString file_path,
    MHWRender::MTexture *out_color_texture,
    const MHWRender::MSamplerState *out_texture_sampler,
    MPlug &out_color_plug) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("mmImagePlaneShape: set_shader_instance_parameters.");

    static const float color[] = {1.0f, 1.0f, 1.0f, 1.0f};
    shader->setParameter("gSolidColor", color);
    shader->setParameter("gColorGain", color_gain);
    shader->setParameter("gAlphaGain", alpha_gain);
    shader->setParameter("gFlip", flip);
    shader->setParameter("gFlop", flop);
    shader->setParameter("gIgnoreAlpha", m_ignore_alpha);
    shader->setParameter("gShowChannelRed",
                         image_display_channel == ImageDisplayChannel::kRed);
    shader->setParameter("gShowChannelGreen",
                         image_display_channel == ImageDisplayChannel::kGreen);
    shader->setParameter("gShowChannelBlue",
                         image_display_channel == ImageDisplayChannel::kBlue);
    shader->setParameter("gShowChannelAlpha",
                         image_display_channel == ImageDisplayChannel::kAlpha);

    shader->setIsTransparent(is_transparent);
    MMSOLVER_MAYA_VRB("mmImagePlaneShape: shader->isTransparent()="
                      << shader->isTransparent());

    MMSOLVER_MAYA_VRB("mmImagePlaneShape: file_path=" << file_path.asChar());
    MMSOLVER_MAYA_VRB(
        "mmImagePlaneShape: start out_color_texture=" << out_color_texture);

    if (!out_color_texture) {
        if (m_use_color_bars) {
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: use color bars");
            out_color_texture = create_color_bars_texture(textureManager);
        } else if (m_use_image_read) {
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: use image read");
            const MImage::MPixelType pixel_type = MImage::MPixelType::kByte;

            // // TODO: using kFloat crashes.
            // const MImage::MPixelType pixel_type = MImage::MPixelType::kFloat;

            const bool do_texture_update = false;
            out_color_texture =
                read_image_file(textureManager, m_image, file_path, pixel_type,
                                do_texture_update);
        } else if (!out_color_plug.isNull()) {
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: use color plug texture");
            out_color_texture =
                create_plug_texture(textureManager, out_color_plug);
        } else {
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: use color bars");
            out_color_texture = create_color_bars_texture(textureManager);
        }

        if (out_color_texture) {
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture->name()="
                              << out_color_texture->name().asChar());
            const void *resource_handle = out_color_texture->resourceHandle();
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture->resourceHandle()="
                              << resource_handle);
            if (resource_handle) {
                MMSOLVER_MAYA_VRB(
                    "mmImagePlaneShape: *texture->resourceHandle()="
                    << *(uint32_t *)resource_handle);
            }

            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture->hasAlpha()="
                              << out_color_texture->hasAlpha());
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture->hasZeroAlpha()="
                              << out_color_texture->hasZeroAlpha());
            MMSOLVER_MAYA_VRB(
                "mmImagePlaneShape: texture->hasTransparentAlpha()="
                << out_color_texture->hasTransparentAlpha());
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture->bytesPerPixel()="
                              << out_color_texture->bytesPerPixel());

            MTextureDescription texture_desc;
            out_color_texture->textureDescription(texture_desc);

            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fWidth="
                              << texture_desc.fWidth);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fHeight="
                              << texture_desc.fHeight);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fDepth="
                              << texture_desc.fDepth);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fBytesPerRow="
                              << texture_desc.fBytesPerRow);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fBytesPerSlice="
                              << texture_desc.fBytesPerSlice);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fMipmaps="
                              << texture_desc.fMipmaps);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fArraySlices="
                              << texture_desc.fArraySlices);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fFormat="
                              << texture_desc.fFormat);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fTextureType="
                              << texture_desc.fTextureType);
            MMSOLVER_MAYA_VRB("mmImagePlaneShape: texture_desc.fEnvMapType="
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
        shader->setParameter("gImageTextureSampler", *out_texture_sampler);
    } else {
        MMSOLVER_MAYA_WRN("mmImagePlaneShape: Could not get texture sampler."
                          << " out_texture_sampler=" << out_texture_sampler);
    }

    if (out_color_texture) {
        MHWRender::MTextureAssignment texture_assignment;
        texture_assignment.texture = out_color_texture;
        shader->setParameter("gImageTexture", texture_assignment);

        textureManager->releaseTexture(out_color_texture);
        out_color_texture = nullptr;
    } else {
        MMSOLVER_MAYA_WRN(
            "mmImagePlaneShape: Could not get color texture; "
            "did not assign texture."
            << " out_color_texture=" << out_color_texture);
    }

    return;
}

void ImagePlaneGeometryOverride::updateRenderItems(const MDagPath &path,
                                                   MRenderItemList &list) {
    const bool verbose = false;
    if (!m_geometry_node_path.isValid()) {
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "Geometry node DAG path is not valid.");
        return;
    }

    MHWRender::MRenderer *renderer = MRenderer::theRenderer();
    if (!renderer) {
        MMSOLVER_MAYA_WRN("mmImagePlaneShape: Could not get MRenderer.");
        return;
    }

    const MHWRender::MShaderManager *shaderManager =
        renderer->getShaderManager();
    if (!shaderManager) {
        MMSOLVER_MAYA_WRN("mmImagePlaneShape: Could not get MShaderManager.");
        return;
    }

    if (m_geometry_node_type != MFn::kMesh) {
        MMSOLVER_MAYA_WRN("mmImagePlaneShape: "
                          << "Only Meshes are supported, geometry node "
                             "given is not a mesh.");
        return;
    }

    bool draw_wireframe = false;
    int index = 0;

    MRenderItem *wireframeItem = nullptr;
    if (draw_wireframe) {
        // Add render item for drawing wireframe on the mesh
        index = list.indexOf(renderItemName_imagePlaneWireframe);
        if (index >= 0) {
            wireframeItem = list.itemAt(index);
        } else {
            // MMSOLVER_MAYA_INFO("mmImagePlaneShape: Generate wireframe
            // MRenderItem...");
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
    index = list.indexOf(renderItemName_imagePlaneShaded);
    if (index >= 0) {
        shadedItem = list.itemAt(index);
    } else {
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: Generate shaded MRenderItem...");
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
            shader->setParameter("solidColor", color);
            wireframeItem->setShader(shader);
            shaderManager->releaseShader(shader);
        }
    }

    if (shadedItem) {
        shadedItem->enable(m_visible);

        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "shadedItem->isEnabled()="
                          << shadedItem->isEnabled());
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "shadedItem->isShaderFromNode()="
                          << shadedItem->isShaderFromNode());
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "shadedItem->isMultiDraw()="
                          << shadedItem->isMultiDraw());
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "shadedItem->isConsolidated()="
                          << shadedItem->isConsolidated());
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "shadedItem->wantConsolidation()="
                          << shadedItem->wantConsolidation());
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "shadedItem->castsShadows()="
                          << shadedItem->castsShadows());
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "shadedItem->receivesShadows()="
                          << shadedItem->receivesShadows());
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "shadedItem->excludedFromPostEffects()="
                          << shadedItem->excludedFromPostEffects());
        MMSOLVER_MAYA_VRB("mmImagePlaneShape: "
                          << "shadedItem->supportsAdvancedTransparency()="
                          << shadedItem->supportsAdvancedTransparency());

        if (m_use_shader_node) {
            if (!m_shader_node.isNull()) {
                bool nonTextured = false;
                auto linkLostCb = (MHWRender::MRenderItem::LinkLostCallback)
                    ImagePlaneGeometryOverride::shader_link_lost_func;
#if MAYA_API_VERSION >= 20200000
                MMSOLVER_MAYA_DBG(
                    "mmImagePlaneShape: "
                    << "shadedItem->setShaderFromNode2: "
                    << "link_lost_count="
                    << m_shader_link_lost_user_data_ptr->link_lost_count
                    << " set_shader_count="
                    << m_shader_link_lost_user_data_ptr->set_shader_count);
                m_shader_link_lost_user_data_ptr->set_shader_count += 1;

                shadedItem->setShaderFromNode2(
                    m_shader_node, m_geometry_node_path, linkLostCb,
                    m_shader_link_lost_user_data_ptr, nonTextured);
#elif
                MMSOLVER_MAYA_DBG(
                    "mmImagePlaneShape: "
                    << "shadedItem->setShaderFromNode: "
                    << "link_lost_count="
                    << m_shader_link_lost_user_data.link_lost_count
                    << " set_shader_count="
                    << m_shader_link_lost_user_data.set_shader_count);
                m_shader_link_lost_user_data.set_shader_count += 1;

                // NOTE: 'MRenderItem::setShaderFromNode()' is deprecated
                // in Maya 2020 and above.
                shadedItem->setShaderFromNode(
                    m_shader_node, m_geometry_node_path, linkLostCb,
                    &m_shader_link_lost_user_data, nonTextured);
#endif

                shadedItem->setTreatAsTransparent(m_is_transparent);

            } else {
                MMSOLVER_MAYA_WRN("mmImagePlaneShape: "
                                  << "Shader node is not valid, "
                                  << "using fallback blue shader.");
                MShaderInstance *shader = shaderManager->getStockShader(
                    MShaderManager::k3dSolidShader);
                if (shader) {
                    static const float color[] = {0.0f, 0.0f, 1.0f, 1.0f};
                    shader->setParameter("solidColor", color);
                    shadedItem->setShader(shader);
                    shaderManager->releaseShader(shader);
                }
            }
        } else {
            if (!m_shader) {
                m_shader = mmsolver::render::compile_shader_file("mmImagePlane",
                                                                 "Main");
            }

            if (m_shader) {
                MHWRender::MTextureManager *textureManager =
                    renderer->getTextureManager();
                if (!textureManager) {
                    MMSOLVER_MAYA_WRN(
                        "mmImagePlaneShape: Could not get MTextureManager.");
                    return;
                }

                set_shader_instance_parameters(
                    m_shader, textureManager, m_color_gain, m_alpha_gain,
                    m_ignore_alpha, m_flip, m_flop, m_is_transparent,
                    m_image_display_channel, m_file_path, m_color_texture,
                    m_texture_sampler, m_color_plug);

                shadedItem->setShader(m_shader);

                // // Once assigned, no need to hold on to shader instance
                // shaderManager->releaseShader(m_shader);
            }
        }
    }
}

void ImagePlaneGeometryOverride::populateGeometry(
    const MGeometryRequirements &requirements,
    const MRenderItemList &renderItems, MGeometry &data) {
    const bool verbose = false;
    if (!m_geometry_node_path.isValid()) {
        MMSOLVER_MAYA_VRB(
            "mmImagePlaneShape: Geometry node DAG path is not valid.");
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

void ImagePlaneGeometryOverride::cleanUp() {}

#if MAYA_API_VERSION >= 20190000
bool ImagePlaneGeometryOverride::requiresGeometryUpdate() const {
    const bool verbose = false;
    if (m_geometry_node_path.isValid() && !m_shader_node.isNull()) {
        MMSOLVER_MAYA_VRB(
            "ImagePlaneGeometryOverride::requiresGeometryUpdate: false");
        return false;
    }
    MMSOLVER_MAYA_VRB(
        "ImagePlaneGeometryOverride::requiresGeometryUpdate: true");
    return true;
}

bool ImagePlaneGeometryOverride::requiresUpdateRenderItems(
    const MDagPath &path) const {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB(
        "ImagePlaneGeometryOverride::requiresUpdateRenderItems: true: "
        << path.fullPathName().asChar());
    return true;  // Always update the render items.
}
#endif

bool ImagePlaneGeometryOverride::hasUIDrawables() const { return true; }

void ImagePlaneGeometryOverride::addUIDrawables(
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
