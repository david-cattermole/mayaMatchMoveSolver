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

#ifndef MM_SOLVER_RENDER_QUAD_RENDER_BASE_H
#define MM_SOLVER_RENDER_QUAD_RENDER_BASE_H

#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

namespace mmsolver {
namespace render {

class QuadRenderBase : public MHWRender::MQuadRender {
public:
    QuadRenderBase(const MString &name);
    ~QuadRenderBase() override;

    MHWRender::MClearOperation &clearOperation() override;

    void setRenderTargets(MHWRender::MRenderTarget **targets,
                          const uint32_t index, const uint32_t count) {
        m_targets = targets;
        m_target_index = index;
        m_target_count = count;
    }

    const MFloatPoint &viewRectangle() const { return m_view_rectangle; }
    void setViewRectangle(const MFloatPoint &rect) { m_view_rectangle = rect; }

    uint32_t clearMask() { return m_clear_mask; }
    void setClearMask(const uint32_t clear_mask) { m_clear_mask = clear_mask; }

protected:
    // Targets used as input parameters to mShaderInstance;
    MHWRender::MRenderTarget **m_targets;

    // The index (and count) into the m_targets list of pointers. We
    // are able to give the exact targets.
    uint32_t m_target_index;
    uint32_t m_target_count;

    // View rectangle
    MFloatPoint m_view_rectangle;

    // How the clear operation works?
    uint32_t m_clear_mask;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_QUAD_RENDER_BASE_H
