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

#include "SceneDepthRender.h"

// Maya
#include <maya/MShaderManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/ops/scene_utils.h"
#include "mmSolver/render/shader/shader_utils.h"

namespace mmsolver {
namespace render {

const char kPARAMETER_DEPTH_OFFSET[] = "gDepthOffset";

SceneDepthRender::SceneDepthRender(const MString &name)
    : SceneRenderBase(name)
    , m_shader_override(nullptr)
    , m_depth_priority(0.0) {}

SceneDepthRender::~SceneDepthRender() {
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

const MHWRender::MShaderInstance *SceneDepthRender::shaderOverride() {
    const bool verbose = false;

    if (!m_shader_override) {
        MMSOLVER_VRB("SceneDepthRender: Compile Depth Main shader...");
        const MString file_name = "mmDepth";
        const MString main_technique = "Main";
        m_shader_override = compile_shader_file(file_name, main_technique);
    }

    if (m_shader_override) {
        MMSOLVER_VRB("SceneDepthRender: Assign Depth shader parameters...");

        // We assume the depth buffer has at least 24 bits for the depth
        // value.
        //
        // Smaller Z-Depth values are nearer the camera, and larger values
        // are farther away.
        const float depth_value_range = 1048576.0f;  // (2 ^ 24) / 16
        const float depth_value_step = 1.0f / depth_value_range;
        const float depth_offset = depth_value_step * m_depth_priority;

        CHECK_MSTATUS(m_shader_override->setParameter(kPARAMETER_DEPTH_OFFSET,
                                                      depth_offset));
    }

    return m_shader_override;
}

}  // namespace render
}  // namespace mmsolver
