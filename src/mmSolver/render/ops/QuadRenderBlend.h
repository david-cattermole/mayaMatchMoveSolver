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

#ifndef MM_SOLVER_RENDER_OPS_QUAD_RENDER_BLEND_H
#define MM_SOLVER_RENDER_OPS_QUAD_RENDER_BLEND_H

#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

#include "QuadRenderBase.h"

namespace mmsolver {
namespace render {

class QuadRenderBlend : public QuadRenderBase {
public:
    QuadRenderBlend(const MString &name);
    ~QuadRenderBlend() override;

    MHWRender::MRenderTarget *const *targetOverrideList(
        unsigned int &listSize) override;

    const MHWRender::MShaderInstance *shader() override;

    void setInputTarget1(const uint32_t index) {
        m_target_index_input1 = index;
    }

    void setInputTarget2(const uint32_t index) {
        m_target_index_input2 = index;
    }

    void setBlend(const float value) { m_blend = value; }

protected:
    // Shader to use for the quad render
    MHWRender::MShaderInstance *m_shader_instance;

    // The target indexes for render targets used to blend between.
    uint32_t m_target_index_input1;
    uint32_t m_target_index_input2;

    float m_blend;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_OPS_QUAD_RENDER_BLEND_H
