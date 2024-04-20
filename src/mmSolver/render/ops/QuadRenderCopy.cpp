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

#include "QuadRenderCopy.h"

#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>

// MM Solver
#include "mmSolver/render/data/constants.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

QuadRenderCopy::QuadRenderCopy(const MString &name)
    : QuadRenderBase(name)
    , m_shader_color_and_depth(nullptr)
    , m_shader_color_only(nullptr)
    , m_shader_depth_only(nullptr)
    , m_use_color_target(false)
    , m_use_depth_target(false)
    , m_depth_stencil_state(nullptr)
    , m_target_index_color_input(0)
    , m_target_index_depth_input(0) {}

QuadRenderCopy::~QuadRenderCopy() {
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        return;
    }
    const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
    if (!shaderMgr) {
        return;
    }

    // Release all shaders.
    if (m_shader_color_and_depth) {
        shaderMgr->releaseShader(m_shader_color_and_depth);
        m_shader_color_and_depth = nullptr;
    }
    if (m_shader_color_only) {
        shaderMgr->releaseShader(m_shader_color_only);
        m_shader_color_only = nullptr;
    }
    if (m_shader_depth_only) {
        shaderMgr->releaseShader(m_shader_depth_only);
        m_shader_depth_only = nullptr;
    }

    // Release any state
    if (m_depth_stencil_state) {
        MHWRender::MStateManager::releaseDepthStencilState(
            m_depth_stencil_state);
        m_depth_stencil_state = nullptr;
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

    if (!m_use_color_target && !m_use_depth_target) {
        return nullptr;
    }

    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        return nullptr;
    }
    const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
    if (!shaderMgr) {
        return nullptr;
    }

    // Compile shaders
    const MString file_name = "mmCopy";
    const MString color_and_depth_technique = "Main";
    const MString color_only_technique = "ColorOnly";
    const MString depth_only_technique = "DepthOnly";

    MMSOLVER_MAYA_VRB("QuadRenderCopy: Assign shader parameters...");
    if (m_use_color_target && m_use_depth_target) {
        if (!m_shader_color_and_depth) {
            MMSOLVER_MAYA_VRB(
                "QuadRenderCopy: Compile Color and Depth shader...");
            m_shader_color_and_depth = shaderMgr->getEffectsFileShader(
                file_name.asChar(), color_and_depth_technique.asChar());
        }

        if (m_shader_color_and_depth) {
            if (m_targets) {
                MHWRender::MRenderTarget *color_target =
                    m_targets[m_target_index_color_input];
                MHWRender::MRenderTarget *depth_target =
                    m_targets[m_target_index_depth_input];

                if (color_target) {
                    MMSOLVER_MAYA_VRB(
                        "QuadRenderCopy: Assign Color texture to shader...");
                    MHWRender::MRenderTargetAssignment assignment;
                    assignment.target = color_target;
                    CHECK_MSTATUS(m_shader_color_and_depth->setParameter(
                        "gColorTex", assignment));
                }

                if (depth_target) {
                    MMSOLVER_MAYA_VRB(
                        "QuadRenderCopy: Assign Depth texture to shader...");
                    MHWRender::MRenderTargetAssignment assignment;
                    assignment.target = depth_target;
                    CHECK_MSTATUS(m_shader_color_and_depth->setParameter(
                        "gDepthTex", assignment));
                }
            }
            return m_shader_color_and_depth;
        }
    } else if (m_use_color_target && !m_use_depth_target) {
        if (!m_shader_color_only) {
            MMSOLVER_MAYA_VRB("QuadRenderCopy: Compile Color Only shader...");
            m_shader_color_only = shaderMgr->getEffectsFileShader(
                file_name.asChar(), color_only_technique.asChar());
        }

        if (m_shader_color_only) {
            if (m_targets) {
                MHWRender::MRenderTarget *color_target =
                    m_targets[m_target_index_color_input];
                if (color_target) {
                    MMSOLVER_MAYA_VRB(
                        "QuadRenderCopy: Assign Color texture to shader...");
                    MHWRender::MRenderTargetAssignment assignment;
                    assignment.target = color_target;
                    CHECK_MSTATUS(m_shader_color_only->setParameter(
                        "gColorTex", assignment));
                }
            }
            return m_shader_color_only;
        }
    } else if (!m_use_color_target && m_use_depth_target) {
        if (!m_shader_depth_only) {
            MMSOLVER_MAYA_VRB("QuadRenderCopy: Compile Depth Only shader...");
            m_shader_depth_only = shaderMgr->getEffectsFileShader(
                file_name.asChar(), depth_only_technique.asChar());
        }

        if (m_shader_depth_only) {
            if (m_targets) {
                MHWRender::MRenderTarget *depth_target =
                    m_targets[m_target_index_depth_input];
                if (depth_target) {
                    MMSOLVER_MAYA_VRB(
                        "QuadRenderCopy: Assign Depth texture to shader...");
                    MHWRender::MRenderTargetAssignment assignment;
                    assignment.target = depth_target;
                    CHECK_MSTATUS(m_shader_depth_only->setParameter(
                        "gDepthTex", assignment));
                }
            }
            return m_shader_depth_only;
        }
    }

    return nullptr;
}

const MDepthStencilState *QuadRenderCopy::depthStencilStateOverride() {
    if (!m_use_depth_target) {
        return nullptr;
    }
    if (!m_depth_stencil_state) {
        MHWRender::MDepthStencilStateDesc desc;
        desc.depthEnable = true;
        desc.depthWriteEnable = true;
        desc.depthFunc = MHWRender::MStateManager::kCompareAlways;
        m_depth_stencil_state =
            MHWRender::MStateManager::acquireDepthStencilState(desc);
    }
    return m_depth_stencil_state;
}

}  // namespace render
}  // namespace mmsolver
