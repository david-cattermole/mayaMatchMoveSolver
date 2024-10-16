/*
 * Copyright (C) 2023 David Cattermole.
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
 * Explicitly clear render targets.
 */

#ifndef MM_SOLVER_RENDER_OPS_CLEAR_OPERATION_H
#define MM_SOLVER_RENDER_OPS_CLEAR_OPERATION_H

#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

namespace mmsolver {
namespace render {

class ClearOperation : public MHWRender::MClearOperation {
public:
    explicit ClearOperation(const MString &name);
    ~ClearOperation() override;

    void setRenderTargets(MHWRender::MRenderTarget **targets,
                          const uint32_t index, const uint32_t count) {
        m_targets = targets;
        m_target_index = index;
        m_target_count = count;
    }

    const MFloatPoint &viewRectangle() const { return m_view_rectangle; }
    void setViewRectangle(const MFloatPoint &rect) { m_view_rectangle = rect; }

    MHWRender::MRenderTarget *const *targetOverrideList(
        unsigned int &listSize) override;

protected:
    // Targets used as input parameters to mShaderInstance;
    MHWRender::MRenderTarget **m_targets;

    // The index (and count) into the m_targets list of pointers. We
    // are able to give the exact targets.
    uint32_t m_target_index;
    uint32_t m_target_count;

    // View rectangle
    MFloatPoint m_view_rectangle;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_OPS_CLEAR_OPERATION_H
