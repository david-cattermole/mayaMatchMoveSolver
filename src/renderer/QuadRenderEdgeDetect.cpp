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
        , m_target_index_input(0)
        , m_thickness(1.5f)
        , m_threshold(0.2f) {
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
        MString file_name = "mmSilhouette";
        MString shader_technique = "Sobel";
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
                                  "gDepthTex", assignment));
            }
        }

        // The edge thickness.
        CHECK_MSTATUS(m_shader_instance->setParameter("gThickness", m_thickness));

        // The edge detection threshold.
        CHECK_MSTATUS(m_shader_instance->setParameter("gThreshold", m_threshold));

        // Colors
        CHECK_MSTATUS(m_shader_instance->setParameter("gLineColor", kEdgeColorDefault));
        CHECK_MSTATUS(m_shader_instance->setParameter("gBackgroundColor", kTransparentBlackColor));
    }
    // }
    return m_shader_instance;
}

} // namespace renderer
} // namespace mmsolver
