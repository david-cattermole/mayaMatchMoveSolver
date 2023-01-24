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

#ifndef MM_SOLVER_RENDER_QUAD_RENDER_LAYER_MERGE_H
#define MM_SOLVER_RENDER_QUAD_RENDER_LAYER_MERGE_H

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

    const MHWRender::MShaderInstance *shader() override;

    void setColorTargetA(const uint32_t index) {
        m_target_index_color_a = index;
    }
    void setDepthTargetA(const uint32_t index) {
        m_target_index_depth_a = index;
    }
    void setColorTargetB(const uint32_t index) {
        m_target_index_color_b = index;
    }
    void setDepthTargetB(const uint32_t index) {
        m_target_index_depth_b = index;
    }

    void setLayerMode(const LayerMode value) { m_layer_mode = value; }
    void setLayerMix(const float value) { m_layer_mix = value; }

    void setDebug(const bool value) { m_debug = value; }

protected:
    // Shader to use for the quad render
    MHWRender::MShaderInstance *m_shader_instance;

    // The target indexes for render targets used to blend between.
    uint32_t m_target_index_color_a;
    uint32_t m_target_index_depth_a;
    uint32_t m_target_index_color_b;
    uint32_t m_target_index_depth_b;

    LayerMode m_layer_mode;
    float m_layer_mix;
    bool m_debug;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_QUAD_RENDER_LAYER_MERGE_H
