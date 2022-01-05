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

#include "constants.h"
#include "QuadRenderBase.h"

#include <maya/MShaderManager.h>

namespace mmsolver {
namespace render {

// Render a full-screen quad, with a preset shader applied.
//
// Reads from 'auxiliary' Target, and writes to 'main' Target.
//
QuadRenderBase::QuadRenderBase(const MString &name)
        : MQuadRender(name),
          m_targets(nullptr),
          m_target_index(0),
          m_target_count(0),
          m_clear_mask(MHWRender::MClearOperation::kClearNone) {
}

QuadRenderBase::~QuadRenderBase() {
    m_targets = nullptr;
}

MHWRender::MClearOperation &
QuadRenderBase::clearOperation() {
    mClearOperation.setClearGradient(false);
    mClearOperation.setMask(m_clear_mask);
    return mClearOperation;
}

} // namespace render
} // namespace mmsolver
