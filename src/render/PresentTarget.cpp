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
#include "PresentTarget.h"

#include <maya/MStreamUtils.h>
#include <maya/MShaderManager.h>

namespace mmsolver {
namespace render {

// Custom present target operation
//
// There is not much in this operation except to override which
// targets will be presented.
//
// This differs from scene and quad operations which generally use
// targets as the place to render into.
//
PresentTarget::PresentTarget(const MString &name)
        : MPresentTarget(name),
          m_targets(nullptr),
          m_target_index(0),
          m_target_count(0) {
}

PresentTarget::~PresentTarget() {
    m_targets = nullptr;
}

// Called by Maya.
MHWRender::MRenderTarget *const *
PresentTarget::targetOverrideList(unsigned int &listSize) {
    if (m_targets && (m_target_count > 0)) {
        listSize = m_target_count;
        return &m_targets[m_target_index];
    }
    listSize = 0;
    return nullptr;
}

} // namespace render
} // namespace mmsolver
