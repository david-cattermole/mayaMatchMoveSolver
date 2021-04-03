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

#include "MMRendererConstants.h"
#include "MMRendererQuadRender.h"

#include <maya/MShaderManager.h>

// Render a full-screen quad, with a preset shader applied.
MMRendererQuadRender::MMRendererQuadRender(const MString &name, const MString &id,
                                           const MString &technique)
        : MQuadRender(name),
          m_targets(nullptr),
          m_target_index(0),
          m_target_count(0),
          m_shader_instance(nullptr),
          m_effect_id(id),
          m_effect_id_technique(technique),
          m_clear_mask(MHWRender::MClearOperation::kClearNone) {
}

MMRendererQuadRender::~MMRendererQuadRender() {
    m_targets = nullptr;
    if (m_shader_instance) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        if (renderer) {
            const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
            if (shaderMgr) {
                shaderMgr->releaseShader(m_shader_instance);
            }
        }
        m_shader_instance = nullptr;
    }
}

// Return the appropriate shader instance based on the what we want
// the quad operation to perform.
const MHWRender::MShaderInstance *
MMRendererQuadRender::shader() {
    // Create shader for quad render.
    if ((m_shader_instance == nullptr)
        && (m_effect_id.length() > 0)) {

        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        if (!renderer) {
            return nullptr;
        }
        const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
        if (!shaderMgr) {
            return nullptr;
        }

        // Load shader
        m_shader_instance = shaderMgr->getEffectsFileShader(
            m_effect_id.asChar(), m_effect_id_technique.asChar());
    }
    return m_shader_instance;
}

// Called by Maya.
MHWRender::MRenderTarget *const *
MMRendererQuadRender::targetOverrideList(unsigned int &listSize) {
    if (m_targets) {
        listSize = m_target_count;
        return &m_targets[m_target_index];
    }
    listSize = 0;
    return nullptr;
}

MHWRender::MClearOperation &
MMRendererQuadRender::clearOperation() {
    mClearOperation.setClearGradient(false);
    mClearOperation.setMask(m_clear_mask);
    return mClearOperation;
}
