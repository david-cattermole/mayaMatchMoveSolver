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
 * A full-screen quad render, with a shader applied.
 */

#ifndef MM_SOLVER_RENDER_OPS_QUAD_RENDER_EDGE_DETECT_H
#define MM_SOLVER_RENDER_OPS_QUAD_RENDER_EDGE_DETECT_H

#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "QuadRenderBase.h"
#include "mmSolver/render/data/EdgeDetectMode.h"

namespace mmsolver {
namespace render {

class QuadRenderEdgeDetect : public QuadRenderBase {
public:
    QuadRenderEdgeDetect(const MString &name);
    ~QuadRenderEdgeDetect() override;

    const MHWRender::MShaderInstance *shader() override;

    MHWRender::MRenderTarget *const *targetOverrideList(
        unsigned int &listSize) override;

    void setInputDepthTarget(const uint32_t index) {
        m_target_index_depth = index;
    }
    void setInputColorTarget(const uint32_t index) {
        m_target_index_color = index;
    }

    void setEdgeDetectMode(const EdgeDetectMode value) {
        m_edge_detect_mode = value;
    }
    void setEdgeColor(const float r, const float g, const float b) {
        m_edge_color.r = r;
        m_edge_color.g = g;
        m_edge_color.b = b;
    }
    void setEdgeAlpha(const float value) { m_edge_alpha = value; }
    void setThickness(const float value) { m_thickness = value; }
    void setThreshold(const float value) { m_threshold = value; }

protected:
    // Shader to use for the quad render
    MHWRender::MShaderInstance *m_shader_instance_sobel;
    MHWRender::MShaderInstance *m_shader_instance_frei_chen;

    uint32_t m_target_index_depth;
    uint32_t m_target_index_color;

    EdgeDetectMode m_edge_detect_mode;
    MColor m_edge_color;
    float m_edge_alpha;
    float m_thickness;
    float m_threshold;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_OPS_QUAD_RENDER_EDGE_DETECT_H
