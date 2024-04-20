/*
 * Copyright (C) 2021, 2023 David Cattermole.
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

#include "SceneRender.h"

// Maya
#include <maya/MShaderManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/ops/scene_utils.h"

namespace mmsolver {
namespace render {

SceneRender::SceneRender(const MString &name)
    : SceneRenderBase(name), m_shader_override(nullptr) {}

SceneRender::~SceneRender() {
    m_targets = nullptr;

    if (m_shader_override) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        if (!renderer) {
            return;
        }
        const MHWRender::MShaderManager *shaderMgr =
            renderer->getShaderManager();
        if (!shaderMgr) {
            return;
        }
        shaderMgr->releaseShader(m_shader_override);
        m_shader_override = nullptr;
    }
}

const MHWRender::MShaderInstance *SceneRender::shaderOverride() {
    return m_shader_override;
}

}  // namespace render
}  // namespace mmsolver
