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

#ifndef MM_SOLVER_RENDER_OPS_QUAD_RENDER_COPY_H
#define MM_SOLVER_RENDER_OPS_QUAD_RENDER_COPY_H

#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

#include "QuadRenderBase.h"

namespace mmsolver {
namespace render {

class QuadRenderCopy : public QuadRenderBase {
public:
    QuadRenderCopy(const MString &name);
    ~QuadRenderCopy() override;

    const MHWRender::MShaderInstance *shader() override;

    const MDepthStencilState *depthStencilStateOverride() override;

    MHWRender::MRenderTarget *const *targetOverrideList(
        unsigned int &listSize) override;

    void setUseColorTarget(const bool value) { m_use_color_target = value; }
    void setUseDepthTarget(const bool value) { m_use_depth_target = value; }

    void setColorTarget(const uint32_t index) {
        m_target_index_color_input = index;
    }
    void setDepthTarget(const uint32_t index) {
        m_target_index_depth_input = index;
    }

protected:
    // Shaders to use for the quad render
    MHWRender::MShaderInstance *m_shader_color_and_depth;
    MHWRender::MShaderInstance *m_shader_color_only;
    MHWRender::MShaderInstance *m_shader_depth_only;

    bool m_use_color_target;
    bool m_use_depth_target;

    uint32_t m_target_index_color_input;
    uint32_t m_target_index_depth_input;

private:
    const MDepthStencilState *m_depth_stencil_state;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_OPS_QUAD_RENDER_COPY_H
