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

#include "MMRendererQuadRender.h"

#include <maya/MShaderManager.h>

// Render a full-screen quad, with a preset shader applied.
//
// Reads from 'auxiliary' Target, and writes to 'main' Target.
//
MMRendererQuadRender::MMRendererQuadRender(const MString &name, const MString &id,
                                           const MString &technique)
        : MQuadRender(name), m_shader_instance(nullptr), m_effect_id(id),
          m_effect_id_technique(technique) {
    // Input targets.
    //
    // Auxiliary targets first, then main target second.
    mInputTargetNames.clear();
    mInputTargetNames.append(kAuxiliaryTargetName);
    mInputTargetNames.append(kAuxiliaryDepthTargetName);
    mInputTargetNames.append(kColorTargetName);
    mInputTargetNames.append(kDepthTargetName);

    // Output targets.
    //
    // Main target first, then auxiliary targets second. This is the
    // reverse order from the input targets.
    mOutputTargetNames.clear();
    mOutputTargetNames.append(kColorTargetName);
    mOutputTargetNames.append(kDepthTargetName);
    mOutputTargetNames.append(kAuxiliaryTargetName);
    mOutputTargetNames.append(kAuxiliaryDepthTargetName);
}

MMRendererQuadRender::~MMRendererQuadRender() {
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

/*
 * Return the appropriate shader instance based on the what we want
 * the quad operation to perform
*/
const MHWRender::MShaderInstance *
MMRendererQuadRender::shader() {
    // Create shader for quad render.
    if (m_shader_instance == nullptr) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        if (renderer) {
            const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
            if (shaderMgr) {
                m_shader_instance = shaderMgr->getEffectsFileShader(
                        m_effect_id.asChar(), m_effect_id_technique.asChar());
            }
        }
    }

    if (m_shader_instance) {
        // Set shader input texture as our 'kColourTargetName'.
        MHWRender::MRenderTargetAssignment assignment;
        assignment.target = getInputTarget(kColorTargetName);
        MStatus status = m_shader_instance->setParameter("gInputTex", assignment);
        CHECK_MSTATUS_AND_RETURN(status, nullptr)

        // Set general shader values for edge detecting.
        const MString edgeDetect("FilterEdgeDetect");
        if (m_effect_id == edgeDetect) {
            CHECK_MSTATUS(m_shader_instance->setParameter("gThickness", 0.5f));
            CHECK_MSTATUS(m_shader_instance->setParameter("gThreshold", 0.1f));
        }
    }

    return m_shader_instance;
}

bool MMRendererQuadRender::getInputTargetDescription(const MString &name,
                                                     MHWRender::MRenderTargetDescription &description) {
    // We do not provide a target description for the auxiliary target
    // because we expect that target to be set as an output.  We copy
    // the descriptions from the auxiliary targets so the MSAA
    // properties and size match.
    if (name == kColorTargetName) {
        MHWRender::MRenderTarget *outTarget =
            getInputTarget(kAuxiliaryTargetName);
        if (outTarget) {
            outTarget->targetDescription(description);
        }
        description.setName("_post_target_1");
        return true;
    } else if (name == kDepthTargetName) {
        MHWRender::MRenderTarget *outTarget =
            getInputTarget(kAuxiliaryDepthTargetName);
        if (outTarget) {
            outTarget->targetDescription(description);
        }
        description.setName("_post_target_depth");
        return true;
    }

    return false;
}

int MMRendererQuadRender::writableTargets(unsigned int &count) {
    count = 2;
    return 0;
}

MHWRender::MClearOperation &
MMRendererQuadRender::clearOperation() {
    mClearOperation.setClearGradient(false);
    mClearOperation.setMask(
            (unsigned int) MHWRender::MClearOperation::kClearNone);
    return mClearOperation;
}
