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

#include "QuadRenderCopy.h"

#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>

// MM Solver
#include "constants.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

QuadRenderCopy::QuadRenderCopy(const MString &name)
    : QuadRenderBase(name)
    , m_shader_instance(nullptr)
    , m_target_index_input(0) {}

QuadRenderCopy::~QuadRenderCopy() {
    // Release all shaders.
    if (m_shader_instance) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        if (!renderer) {
            return;
        }
        const MHWRender::MShaderManager *shaderMgr =
            renderer->getShaderManager();
        if (!shaderMgr) {
            return;
        }
        shaderMgr->releaseShader(m_shader_instance);
        m_shader_instance = nullptr;
    }
}

// Determine the targets to be used.
//
// Called by Maya.
MHWRender::MRenderTarget *const *QuadRenderCopy::targetOverrideList(
    unsigned int &listSize) {
    if (m_targets && (m_target_count > 0)) {
        listSize = m_target_count;
        return &m_targets[m_target_index];
    }
    listSize = 0;
    return nullptr;
}

// Maya calls this method to know what shader should be used for this
// quad render operation.
const MHWRender::MShaderInstance *QuadRenderCopy::shader() {
    const bool verbose = false;

    // Compile shader
    if (!m_shader_instance) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        if (!renderer) {
            return nullptr;
        }
        const MHWRender::MShaderManager *shaderMgr =
            renderer->getShaderManager();
        if (!shaderMgr) {
            return nullptr;
        }

        MMSOLVER_VRB("QuardRenderCopy: Compile shader...");
        MString file_name = "Copy";
        MString shader_technique = "Main";
        m_shader_instance = shaderMgr->getEffectsFileShader(
            file_name.asChar(), shader_technique.asChar());
    }

    // Set default parameters
    if (m_shader_instance) {
        MMSOLVER_VRB("QuardRenderCopy: Assign shader parameters...");

        if (m_targets) {
            MHWRender::MRenderTarget *target = m_targets[m_target_index_input];
            if (target) {
                MMSOLVER_VRB("QuardRenderCopy: Assign texture to shader...");
                MHWRender::MRenderTargetAssignment assignment;
                assignment.target = target;
                CHECK_MSTATUS(
                    m_shader_instance->setParameter("gInputTex", assignment));
            }
        }

        CHECK_MSTATUS(m_shader_instance->setParameter("gVerticalFlip", false));
        CHECK_MSTATUS(m_shader_instance->setParameter("gDisableAlpha", false));
    }
    return m_shader_instance;
}

}  // namespace render
}  // namespace mmsolver
