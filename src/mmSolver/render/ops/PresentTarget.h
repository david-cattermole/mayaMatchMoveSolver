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
 */

#ifndef MM_SOLVER_RENDER_OPS_PRESENT_TARGET_H
#define MM_SOLVER_RENDER_OPS_PRESENT_TARGET_H

#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

namespace mmsolver {
namespace render {

class PresentTarget : public MHWRender::MPresentTarget {
public:
    explicit PresentTarget(const MString &name);

    ~PresentTarget() override;

    MHWRender::MRenderTarget *const *targetOverrideList(
        unsigned int &listSize) override;

    void setRenderTargets(MHWRender::MRenderTarget **targets,
                          const uint32_t index, const uint32_t count) {
        m_targets = targets;
        m_target_index = index;
        m_target_count = count;
    }

protected:
    // Targets to be used for operation
    MHWRender::MRenderTarget **m_targets;

    // The index (and count) into the m_targets list of pointers. We
    // are able to give the exact targets.
    uint32_t m_target_index;
    uint32_t m_target_count;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_OPS_PRESENT_TARGET_H
