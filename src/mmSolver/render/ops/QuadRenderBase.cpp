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

#include "QuadRenderBase.h"

#include <maya/MShaderManager.h>

namespace mmsolver {
namespace render {

// Render a full-screen quad, with a preset shader applied.
QuadRenderBase::QuadRenderBase(const MString &name)
    : MQuadRender(name)
    , m_targets(nullptr)
    , m_target_index(0)
    , m_target_count(0)
    , m_clear_depth(1.0f)
    , m_clear_mask(MHWRender::MClearOperation::kClearNone) {
    m_view_rectangle[0] = 0.0f;
    m_view_rectangle[1] = 0.0f;
    m_view_rectangle[2] = 1.0f;
    m_view_rectangle[3] = 1.0f;
}

QuadRenderBase::~QuadRenderBase() { m_targets = nullptr; }

MHWRender::MClearOperation &QuadRenderBase::clearOperation() {
    float val[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    mClearOperation.setClearColor(val);
    mClearOperation.setClearColor2(val);
    mClearOperation.setClearGradient(false);
    mClearOperation.setClearStencil(0);
    // A depth value of 1.0f represents the 'most distant'
    // object. As objects draw, they draw darker pixels on top of
    // this background color.
    mClearOperation.setClearDepth(m_clear_depth);
    mClearOperation.setMask(m_clear_mask);
    return mClearOperation;
}

}  // namespace render
}  // namespace mmsolver
