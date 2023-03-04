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

#include "QuadRenderLayerMerge.h"

#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>

// MM Solver
#include "mmSolver/render/data/constants.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

// Render a full-screen quad, with a preset shader applied.
QuadRenderLayerMerge::QuadRenderLayerMerge(const MString &name)
    : QuadRenderBase(name)
    , m_shader_instance(nullptr)
    , m_depth_stencil_state(nullptr)
    , m_target_index_color_a(0)
    , m_target_index_depth_a(0)
    , m_target_index_color_b(0)
    , m_target_index_depth_b(0)
    , m_target_index_color_c(0)
    , m_use_color_target_c(false)
    , m_layer_mode(kLayerModeDefault)
    , m_layer_mix(0.5f)
    , m_alpha_a(1.0f)
    , m_alpha_b(1.0f)
    , m_alpha_c(1.0f) {}

QuadRenderLayerMerge::~QuadRenderLayerMerge() {
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
MHWRender::MRenderTarget *const *QuadRenderLayerMerge::targetOverrideList(
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
const MHWRender::MShaderInstance *QuadRenderLayerMerge::shader() {
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

        MMSOLVER_VRB("QuadRenderLayerMerge: Compile shader...");
        MString file_name = "mmLayerMerge";
        MString shader_technique = "Main";
        m_shader_instance = shaderMgr->getEffectsFileShader(
            file_name.asChar(), shader_technique.asChar());
    }

    // Set default parameters
    if (m_shader_instance) {
        MMSOLVER_VRB("QuadRenderLayerMerge: Assign shader parameters...");
        if (m_targets) {
            MHWRender::MRenderTarget *target_color_a =
                m_targets[m_target_index_color_a];
            MHWRender::MRenderTarget *target_color_b =
                m_targets[m_target_index_color_b];
            MHWRender::MRenderTarget *target_depth_a =
                m_targets[m_target_index_depth_a];
            MHWRender::MRenderTarget *target_depth_b =
                m_targets[m_target_index_depth_b];

            if (target_color_a) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: Assign Color A to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_color_a;
                CHECK_MSTATUS(
                    m_shader_instance->setParameter("gColorTexA", assignment));
            }

            if (target_depth_a) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: Assign Depth A to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_depth_a;
                CHECK_MSTATUS(
                    m_shader_instance->setParameter("gDepthTexA", assignment));
            }

            if (target_color_b) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: Assign Color B to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_color_b;
                CHECK_MSTATUS(
                    m_shader_instance->setParameter("gColorTexB", assignment));
            }

            if (target_depth_b) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: Assign Depth B to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_depth_b;
                CHECK_MSTATUS(
                    m_shader_instance->setParameter("gDepthTexB", assignment));
            }

            if (m_use_color_target_c) {
                MHWRender::MRenderTarget *target_color_c =
                    m_targets[m_target_index_color_c];

                if (target_color_c) {
                    MMSOLVER_VRB(
                        "QuadRenderLayerMerge: Assign Color C to shader...");
                    MHWRender::MRenderTargetAssignment assignment{};
                    assignment.target = target_color_c;
                    CHECK_MSTATUS(m_shader_instance->setParameter("gColorTexC",
                                                                  assignment));
                }
            }
        }

        CHECK_MSTATUS(m_shader_instance->setParameter(
            "gLayerMode", static_cast<int32_t>(m_layer_mode)));
        CHECK_MSTATUS(
            m_shader_instance->setParameter("gLayerMix", m_layer_mix));
        CHECK_MSTATUS(m_shader_instance->setParameter("gAlphaA", m_alpha_a));
        CHECK_MSTATUS(m_shader_instance->setParameter("gAlphaB", m_alpha_b));
        CHECK_MSTATUS(m_shader_instance->setParameter("gAlphaC", m_alpha_c));
        CHECK_MSTATUS(m_shader_instance->setParameter(
            "gUseColorC", static_cast<int32_t>(m_use_color_target_c)));
        CHECK_MSTATUS(m_shader_instance->setParameter(
            "gDebugMode", static_cast<int32_t>(m_debug)));
    }
    return m_shader_instance;
}

const MDepthStencilState *QuadRenderLayerMerge::depthStencilStateOverride() {
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
