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
#include "QuadRenderEdgeDetect.h"

#include <maya/MStreamUtils.h>
#include <maya/MShaderManager.h>

namespace mmsolver {
namespace renderer {

QuadRenderEdgeDetect::QuadRenderEdgeDetect(const MString &name)
        : QuadRenderBase(name)
        , m_shader_instance(nullptr)
        , m_target_index_input(0) {
}

QuadRenderEdgeDetect::~QuadRenderEdgeDetect() {
    // Release all shaders.
    if (m_shader_instance) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        if (!renderer) {
            return;
        }
        const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
        if (!shaderMgr) {
            return;
        }
        shaderMgr->releaseShader(m_shader_instance);
        m_shader_instance = nullptr;
    }
    return;
}

// Determine the targets to be used.
//
// Called by Maya.
MHWRender::MRenderTarget *const *
QuadRenderEdgeDetect::targetOverrideList(unsigned int &listSize) {
    if (m_targets && (m_target_count > 0)) {
        listSize = m_target_count;
        return &m_targets[m_target_index];
    }
    listSize = 0;
    return nullptr;
}

// Maya calls this method to know what shader should be used for this
// quad render operation.
const MHWRender::MShaderInstance *
QuadRenderEdgeDetect::shader() {
    auto simple_shader = false;
    if (simple_shader) {
        // Compile shader
        if (!m_shader_instance) {
            MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
            if (!renderer) {
                return nullptr;
            }
            const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
            if (!shaderMgr) {
                return nullptr;
            }

            MStreamUtils::stdOutStream()
                << "QuardRenderEdgeDetect: Compile shader...\n";
            m_shader_instance = shaderMgr->getStockShader(
                MHWRender::MShaderManager::k3dSolidShader);
        }

        // Set default parameters
        if (m_shader_instance) {
            MStreamUtils::stdOutStream()
                << "QuardRenderEdgeDetect: Assign shader parameters...\n";
            const float color[] = {0.0f, 0.0f, 1.0f, 1.0f};
            CHECK_MSTATUS(m_shader_instance->setParameter("solidColor", color));
        }

    } else {
        // Compile shader
        if (!m_shader_instance) {
            MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
            if (!renderer) {
                return nullptr;
            }
            const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
            if (!shaderMgr) {
                return nullptr;
            }

            MStreamUtils::stdOutStream()
                << "QuardRenderEdgeDetect: Compile shader...\n";
            MString file_name = "FilterEdgeDetect";
            MString shader_technique = "";
            m_shader_instance = shaderMgr->getEffectsFileShader(
                file_name.asChar(),
                shader_technique.asChar());
        }

        // Set default parameters
        if (m_shader_instance) {
            MStreamUtils::stdOutStream()
                << "QuardRenderEdgeDetect: Assign shader parameters...\n";

            if (m_targets) {
                MHWRender::MRenderTargetAssignment assignment;
                MHWRender::MRenderTarget *target = m_targets[m_target_index_input];
                if (target) {
                    MStreamUtils::stdOutStream()
                        << "QuardRenderEdgeDetect: Assign texture to shader...\n";
                    assignment.target = target;
                    CHECK_MSTATUS(m_shader_instance->setParameter(
                                      "gInputTex", assignment));
                }
            }

            // The edge thickness. default = 1.5f.
            //
            // TODO: Allow the user to change the thickness.
            CHECK_MSTATUS(m_shader_instance->setParameter("gThickness", 0.5f));

            // The edge detection threshold. default = 0.2f.
            //
            // TODO: Allow the user to change the threshold.
            CHECK_MSTATUS(m_shader_instance->setParameter("gThreshold", 0.1f));
        }
    }
    return m_shader_instance;
}

} // namespace renderer
} // namespace mmsolver
