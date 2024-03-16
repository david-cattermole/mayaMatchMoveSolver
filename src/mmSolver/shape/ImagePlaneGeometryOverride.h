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

#ifndef MM_IMAGE_PLANE_GEOMETRY_OVERRIDE_H
#define MM_IMAGE_PLANE_GEOMETRY_OVERRIDE_H

// Maya
#include <maya/MColor.h>
#include <maya/MEventMessage.h>
#include <maya/MGlobal.h>
#include <maya/MImage.h>
#include <maya/MPointArray.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MDrawContext.h>
#include <maya/MDrawRegistry.h>
#include <maya/MHWGeometryUtilities.h>
#include <maya/MPxGeometryOverride.h>
#include <maya/MUserData.h>

// MM Solver
#include "ImagePlaneShapeNode.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

class ShaderLinkLostUserData : public MUserData {
public:
    ShaderLinkLostUserData()
        : MUserData(), link_lost_count(0), set_shader_count(0) {}

    // Keep track of the number of times stuff happens, just for
    // interest sake (maybe to help debugging?) - doesn't really mean
    // or do anything special.
    uint32_t link_lost_count;
    uint32_t set_shader_count;
};

using ShaderLinkLostUserDataPtr = MSharedPtr<ShaderLinkLostUserData>;

class ImagePlaneGeometryOverride : public MPxGeometryOverride {
public:
    static MPxGeometryOverride *Creator(const MObject &obj) {
        return new ImagePlaneGeometryOverride(obj);
    }

    ~ImagePlaneGeometryOverride() override;

    MHWRender::DrawAPI supportedDrawAPIs() const override;

    bool hasUIDrawables() const override;

    void updateDG() override;

    void updateRenderItems(const MDagPath &path,
                           MRenderItemList &list) override;

    void addUIDrawables(const MDagPath &path, MUIDrawManager &drawManager,
                        const MFrameContext &frameContext) override;

    void populateGeometry(const MGeometryRequirements &requirements,
                          const MRenderItemList &renderItems,
                          MGeometry &data) override;

    void cleanUp() override;

#if MAYA_API_VERSION >= 20190000
    bool requiresGeometryUpdate() const override;
    bool requiresUpdateRenderItems(const MDagPath &path) const;
#endif

    bool traceCallSequence() const override {
        // Return true if internal tracing is desired.
        return false;
    }

    void handleTraceMessage(const MString &message) const override {
        MGlobal::displayInfo("ImagePlaneGeometryOverride: " + message);
        MMSOLVER_MAYA_INFO("ImagePlaneGeometryOverride: " << message.asChar());
    }

protected:
    ImagePlaneGeometryOverride(const MObject &obj);

    static void on_model_editor_changed_func(void *clientData);
    static void shader_link_lost_func(ShaderLinkLostUserData *userData);

    void query_node_attributes(
        MObject &node, MDagPath &out_camera_node_path, bool &out_visible,
        bool &out_visible_to_camera_only, bool &out_is_under_camera,
        bool &out_draw_hud, bool &out_draw_image_size, MString &out_image_size,
        bool &out_draw_camera_size, MString &out_camera_size,
        bool &out_use_shader_node, bool &out_use_image_read,
        bool &out_use_color_bars,
        ImageDisplayChannel &out_image_display_channel, float &out_color_gain,
        float &out_alpha_gain, bool &out_ignore_alpha, bool &out_flip,
        bool &out_flop, bool &out_is_transparent, MString &out_file_path,
        MPlug &out_color_plug);

    void set_shader_instance_parameters(
        MShaderInstance *shader, MHWRender::MTextureManager *textureManager,
        const float color_gain, const float alpha_gain, const bool ignore_alpha,
        const bool flip, const bool flop, const bool is_transparent,
        const ImageDisplayChannel image_display_channel,
        const MString file_path, MHWRender::MTexture *out_color_texture,
        const MHWRender::MSamplerState *out_texture_sampler,
        MPlug &out_color_plug);

    MObject m_this_node;
    MDagPath m_geometry_node_path;
    MDagPath m_camera_node_path;
    MFn::Type m_geometry_node_type;
    MFn::Type m_shader_node_type;
    MFn::Type m_camera_node_type;
    MObject m_shader_node;

    bool m_visible;
    bool m_visible_to_camera_only;
    bool m_is_under_camera;
    bool m_draw_hud;
    bool m_draw_image_size;
    bool m_draw_camera_size;
    MString m_image_size;
    MString m_camera_size;
    MCallbackId m_model_editor_changed_callback_id;

    bool m_use_shader_node;
    bool m_use_image_read;
    bool m_use_color_bars;

    // Shader attributes.
    MShaderInstance *m_shader;
    ImageDisplayChannel m_image_display_channel;
    float m_color_gain;
    float m_alpha_gain;
    bool m_ignore_alpha;
    bool m_flip;
    bool m_flop;
    bool m_is_transparent;
    MString m_file_path;
    MPlug m_color_plug;

    // Texture caching
    MImage m_image;
    MHWRender::MTexture *m_color_texture;
    const MHWRender::MSamplerState *m_texture_sampler;

#if MAYA_API_VERSION >= 20200000
    ShaderLinkLostUserDataPtr m_shader_link_lost_user_data_ptr;
#elif
    ShaderLinkLostUserData m_shader_link_lost_user_data;
#endif
};

}  // namespace mmsolver

#endif  // MM_IMAGE_PLANE_GEOMETRY_OVERRIDE_H
