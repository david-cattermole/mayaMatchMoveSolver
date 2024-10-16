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

#ifndef MM_IMAGE_PLANE_GEOMETRY_2_OVERRIDE_H
#define MM_IMAGE_PLANE_GEOMETRY_2_OVERRIDE_H

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

#if MAYA_API_VERSION >= 20220000
#include <maya/MSharedPtr.h>
#endif

// MM Solver
#include <mmcore/lib.h>
#include <mmimage/lib.h>

#include "ImagePlaneShape2Node.h"
#include "ImagePlaneUtils.h"
#include "mmSolver/image/ImageCache.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

class ShaderLinkLostUserData2 : public MUserData {
public:
    ShaderLinkLostUserData2()
#if MAYA_API_VERSION >= 20220000
        : MUserData()
#else
        // MUserData(bool) constructor is deprecated in Maya 2022+
        // because 'deleteAfterUse' is no longer needed.
        : MUserData(/*deleteAfterUse=*/true)  // let Maya clean up
#endif
        , link_lost_count(0)
        , set_shader_count(0) {
    }

    // Keep track of the number of times stuff happens, just for
    // interest sake (maybe to help debugging?) - doesn't really mean
    // or do anything special.
    uint32_t link_lost_count;
    uint32_t set_shader_count;
};

#if MAYA_API_VERSION >= 20220000
using ShaderLinkLostUserData2Ptr = MSharedPtr<ShaderLinkLostUserData2>;
#endif

class ImagePlaneGeometry2Override : public MPxGeometryOverride {
public:
    static MPxGeometryOverride *Creator(const MObject &obj) {
        return new ImagePlaneGeometry2Override(obj);
    }

    ~ImagePlaneGeometry2Override() override;

    MHWRender::DrawAPI supportedDrawAPIs() const override;

    bool hasUIDrawables() const override;
    void addUIDrawables(const MDagPath &path, MUIDrawManager &drawManager,
                        const MFrameContext &frameContext) override;

    void updateDG() override;
    void updateRenderItems(const MDagPath &path,
                           MRenderItemList &list) override;
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
        MGlobal::displayInfo("ImagePlaneGeometry2Override: " + message);
        MMSOLVER_MAYA_INFO("ImagePlaneGeometry2Override: " << message.asChar());
    }

protected:
    explicit ImagePlaneGeometry2Override(const MObject &obj);

    static void on_model_editor_changed_func(void *clientData);
    static void shader_link_lost_func(ShaderLinkLostUserData2 *userData);

    void query_node_attributes(
        MObject &node, MDagPath &out_camera_node_path, bool &out_visible,
        bool &out_visible_to_camera_only, bool &out_is_under_camera,
        bool &out_draw_hud, bool &out_draw_image_size, MString &out_image_size,
        bool &out_draw_camera_size, MString &out_camera_size,
        ImageDisplayChannel &out_image_display_channel, MColor &out_color_gain,
        float &out_color_exposure, float &out_color_gamma,
        float &out_color_saturation, float &out_color_soft_clip,
        float &out_alpha_gain, MColor &out_default_color,
        bool &out_ignore_alpha, bool &out_flip, bool &out_flop,
        bool &out_is_transparent, mmcore::FrameValue &out_frame,
        MString &out_file_path, MString &out_input_color_space_name,
        MString &out_output_color_space_name);

    void set_shader_instance_parameters(
        MShaderInstance *shader, MHWRender::MTextureManager *textureManager,
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
        const MHWRender::MSamplerState *out_texture_sampler);

    MObject m_this_node;
    MDagPath m_geometry_node_path;
    MDagPath m_camera_node_path;
    MFn::Type m_geometry_node_type;
    MFn::Type m_camera_node_type;

    bool m_visible;
    bool m_visible_to_camera_only;
    bool m_is_under_camera;
    bool m_draw_hud;
    bool m_draw_image_size;
    bool m_draw_camera_size;
    bool m_update_shader;
    MString m_image_size;
    MString m_camera_size;
    MCallbackId m_model_editor_changed_callback_id;

    // Shader attributes.
    MShaderInstance *m_shader;
    ImageDisplayChannel m_image_display_channel;
    MColor m_color_gain;
    float m_alpha_gain;
    float m_color_exposure;
    float m_color_gamma;
    float m_color_saturation;
    float m_color_soft_clip;
    MColor m_default_color;
    bool m_ignore_alpha;
    bool m_flip;
    bool m_flop;
    bool m_is_transparent;
    mmcore::FrameValue m_frame;
    MString m_file_path;
    MString m_input_color_space_name;
    MString m_output_color_space_name;

    // Texture caching
    MImage m_temp_image;
    mmimage::ImagePixelBuffer m_temp_pixel_buffer;
    mmimage::ImageMetaData m_temp_meta_data;
    MHWRender::MTexture *m_color_texture;
    const MHWRender::MSamplerState *m_texture_sampler;

#if MAYA_API_VERSION >= 20220000
    ShaderLinkLostUserData2Ptr m_shader_link_lost_user_data_ptr;
#else
    ShaderLinkLostUserData2 m_shader_link_lost_user_data;
#endif
};

}  // namespace mmsolver

#endif  // MM_IMAGE_PLANE_GEOMETRY_2_OVERRIDE_H
