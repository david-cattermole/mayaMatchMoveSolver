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

#include "HudRender.h"

#include <maya/MImage.h>
#include <maya/MPoint.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MTextureManager.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/render/data/constants.h"

namespace mmsolver {
namespace render {

HudRender::HudRender()
    : m_targets(nullptr), m_target_index(0), m_target_count(0) {}

HudRender::~HudRender() { m_targets = nullptr; }

// Called by Maya.
MHWRender::MRenderTarget *const *HudRender::targetOverrideList(
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
