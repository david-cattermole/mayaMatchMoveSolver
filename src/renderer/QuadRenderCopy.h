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

#ifndef MAYA_MM_SOLVER_RENDERER_QUAD_RENDER_COPY_H
#define MAYA_MM_SOLVER_RENDERER_QUAD_RENDER_COPY_H

#include "QuadRenderBase.h"

#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MRenderTargetManager.h>


namespace mmsolver {
namespace renderer {

class QuadRenderCopy : public QuadRenderBase {
public:
    QuadRenderCopy(const MString &name);
    ~QuadRenderCopy() override;

    const MHWRender::MShaderInstance *shader() override;

    MHWRender::MRenderTarget* const* targetOverrideList(unsigned int &listSize) override;

    void
    setInputTarget(const uint32_t index) {
        m_target_index_input = index;
    }

protected:
    // Shader to use for the quad render
    MHWRender::MShaderInstance *m_shader_instance;

    uint32_t m_target_index_input;
};

} // namespace renderer
} // namespace mmsolver

#endif // MAYA_MM_SOLVER_RENDERER_QUAD_RENDER_COPY_H
