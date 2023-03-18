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
 */

#include "ClearOperation.h"

#include <maya/MShaderManager.h>

namespace mmsolver {
namespace render {

// Render a full-screen quad, with a preset shader applied.
ClearOperation::ClearOperation(const MString &name)
    : MClearOperation(name)
    , m_targets(nullptr)
    , m_target_index(0)
    , m_target_count(0) {
    // Set inherited values from the base class 'MClearOperation'.
    MClearOperation::setMask(MHWRender::MClearOperation::kClearNone);
    float default_color[4] = {0.0f, 0.0f, 0.0f, 0.0f};
    MClearOperation::setClearColor(default_color);
    MClearOperation::setClearColor2(default_color);
    MClearOperation::setClearGradient(false);
    MClearOperation::setClearStencil(0);
    // A depth value of 1.0f represents the 'most distant' object. As
    // objects draw, they draw darker pixels on top of this background
    // color.
    MClearOperation::setClearDepth(1.0f);

    ClearOperation::m_view_rectangle[0] = 0.0f;
    ClearOperation::m_view_rectangle[1] = 0.0f;
    ClearOperation::m_view_rectangle[2] = 1.0f;
    ClearOperation::m_view_rectangle[3] = 1.0f;
}

ClearOperation::~ClearOperation() { m_targets = nullptr; }

// Determine the targets to be used.
//
// Called by Maya.
MHWRender::MRenderTarget *const *ClearOperation::targetOverrideList(
    unsigned int &listSize) {
    if (m_targets && (m_target_count > 0)) {
        listSize = m_target_count;
        return &m_targets[m_target_index];
    }
    listSize = 0;
    return nullptr;
}

}  // namespace render
}  // namespace mmsolver
