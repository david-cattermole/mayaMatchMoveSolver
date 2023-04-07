/*
 * Copyright (C) 2021, 2023 David Cattermole.
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
 * A full-screen quad render, with a shader applied.
 */

#ifndef MM_SOLVER_RENDER_OPS_QUAD_RENDER_LAYER_MERGE_H
#define MM_SOLVER_RENDER_OPS_QUAD_RENDER_LAYER_MERGE_H

#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

#include "QuadRenderBase.h"
#include "mmSolver/render/data/LayerMode.h"

namespace mmsolver {
namespace render {

class QuadRenderLayerMerge : public QuadRenderBase {
public:
    QuadRenderLayerMerge(const MString &name);
    ~QuadRenderLayerMerge() override;

    MHWRender::MRenderTarget *const *targetOverrideList(
        unsigned int &listSize) override;

    const MDepthStencilState *depthStencilStateOverride() override;

    const MHWRender::MShaderInstance *shader() override;

    void setColorTargetCurrentLayer(const uint32_t index) {
        m_target_index_color_current_layer = index;
    }
    void setDepthTargetCurrentLayer(const uint32_t index) {
        m_target_index_depth_current_layer = index;
    }
    void setColorTargetPreviousLayer(const uint32_t index) {
        m_target_index_color_previous_layer = index;
    }
    void setDepthTargetPreviousLayer(const uint32_t index) {
        m_target_index_depth_previous_layer = index;
    }
    void setColorTargetEdges(const uint32_t index) {
        m_target_index_color_edges = index;
    }
    void setDepthTargetEdges(const uint32_t index) {
        m_target_index_depth_edges = index;
    }
    void setColorTargetBackground(const uint32_t index) {
        m_target_index_color_background = index;
    }
    void setDepthTargetBackground(const uint32_t index) {
        m_target_index_depth_background = index;
    }

    void setUseColorTargetEdges(const bool value) {
        m_use_color_target_edges = value;
    }

    void setAlphaCurrentLayer(const float value) {
        m_alpha_current_layout = value;
    }
    void setAlphaPreviousLayer(const float value) {
        m_alpha_previous_layer = value;
    }
    void setAlphaEdges(const float value) { m_alpha_edges = value; }
    void setAlphaBackground(const float value) { m_alpha_background = value; }

    void setHoldOut(const bool value) { m_hold_out = value; }

    void setDebug(const bool value) { m_debug = value; }

protected:
    // Shader to use for the quad render
    MHWRender::MShaderInstance *m_shader_instance;

    // The target indexes for render targets used to blend between.
    uint32_t m_target_index_color_current_layer;
    uint32_t m_target_index_depth_current_layer;
    uint32_t m_target_index_color_previous_layer;
    uint32_t m_target_index_depth_previous_layer;
    uint32_t m_target_index_color_edges;
    uint32_t m_target_index_depth_edges;
    uint32_t m_target_index_color_background;
    uint32_t m_target_index_depth_background;
    bool m_use_color_target_edges;

    float m_alpha_current_layout;
    float m_alpha_previous_layer;
    float m_alpha_edges;
    float m_alpha_background;

    // Is the current layer using a hold out shading mode?
    bool m_hold_out;

    // Toggle to render debug information to the render target.
    bool m_debug;

private:
    const MDepthStencilState *m_depth_stencil_state;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_OPS_QUAD_RENDER_LAYER_MERGE_H
