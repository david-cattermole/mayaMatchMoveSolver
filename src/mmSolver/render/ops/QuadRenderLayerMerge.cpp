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
    , m_target_index_color_current_layer(0)
    , m_target_index_depth_current_layer(0)
    , m_target_index_color_previous_layer(0)
    , m_target_index_depth_previous_layer(0)
    , m_target_index_color_edges(0)
    , m_target_index_depth_edges(0)
    , m_target_index_color_background(0)
    , m_target_index_depth_background(0)
    , m_use_color_target_edges(false)
    , m_alpha_current_layout(1.0f)
    , m_alpha_previous_layer(1.0f)
    , m_alpha_edges(1.0f)
    , m_alpha_background(1.0f)
    , m_hold_out(false) {}

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
            MHWRender::MRenderTarget *target_color_current_layer =
                m_targets[m_target_index_color_current_layer];
            MHWRender::MRenderTarget *target_color_previous_layer =
                m_targets[m_target_index_color_previous_layer];
            MHWRender::MRenderTarget *target_color_d =
                m_targets[m_target_index_color_background];
            MHWRender::MRenderTarget *target_depth_current_layer =
                m_targets[m_target_index_depth_current_layer];
            MHWRender::MRenderTarget *target_depth_previous_layer =
                m_targets[m_target_index_depth_previous_layer];
            MHWRender::MRenderTarget *target_depth_d =
                m_targets[m_target_index_depth_background];

            if (target_color_current_layer) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: "
                    "Assign Current Layer Color to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_color_current_layer;
                CHECK_MSTATUS(m_shader_instance->setParameter(
                    "gColorTexCurrentLayer", assignment));
            }

            if (target_depth_current_layer) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: "
                    "Assign Current Layer Depth to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_depth_current_layer;
                CHECK_MSTATUS(m_shader_instance->setParameter(
                    "gDepthTexCurrentLayer", assignment));
            }

            if (target_color_previous_layer) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: "
                    "Assign Previous Layer Color to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_color_previous_layer;
                CHECK_MSTATUS(m_shader_instance->setParameter(
                    "gColorTexPreviousLayer", assignment));
            }

            if (target_depth_previous_layer) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: "
                    "Assign Previous Layer Depth to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_depth_previous_layer;
                CHECK_MSTATUS(m_shader_instance->setParameter(
                    "gDepthTexPreviousLayer", assignment));
            }

            if (m_use_color_target_edges) {
                MHWRender::MRenderTarget *target_color_edges =
                    m_targets[m_target_index_color_edges];
                MHWRender::MRenderTarget *target_depth_edges =
                    m_targets[m_target_index_depth_edges];

                if (target_color_edges) {
                    MMSOLVER_VRB(
                        "QuadRenderLayerMerge: "
                        "Assign Edges Color to shader...");
                    MHWRender::MRenderTargetAssignment assignment{};
                    assignment.target = target_color_edges;
                    CHECK_MSTATUS(m_shader_instance->setParameter(
                        "gColorTexEdges", assignment));
                }

                if (target_depth_edges) {
                    MMSOLVER_VRB(
                        "QuadRenderLayerMerge: "
                        "Assign Edges Depth to shader...");
                    MHWRender::MRenderTargetAssignment assignment{};
                    assignment.target = target_depth_edges;
                    CHECK_MSTATUS(m_shader_instance->setParameter(
                        "gDepthTexEdges", assignment));
                }
            }

            if (target_color_d) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: "
                    "Assign Color Background to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_color_d;
                CHECK_MSTATUS(m_shader_instance->setParameter(
                    "gColorTexBackground", assignment));
            }

            if (target_depth_d) {
                MMSOLVER_VRB(
                    "QuadRenderLayerMerge: "
                    "Assign Depth Background to shader...");
                MHWRender::MRenderTargetAssignment assignment{};
                assignment.target = target_depth_d;
                CHECK_MSTATUS(m_shader_instance->setParameter(
                    "gDepthTexBackground", assignment));
            }
        }

        CHECK_MSTATUS(m_shader_instance->setParameter("gAlphaCurrentLayer",
                                                      m_alpha_current_layout));
        CHECK_MSTATUS(m_shader_instance->setParameter("gAlphaPreviousLayer",
                                                      m_alpha_previous_layer));
        CHECK_MSTATUS(
            m_shader_instance->setParameter("gAlphaEdges", m_alpha_edges));
        CHECK_MSTATUS(m_shader_instance->setParameter("gAlphaBackground",
                                                      m_alpha_background));
        CHECK_MSTATUS(m_shader_instance->setParameter(
            "gUseColorEdges", static_cast<int32_t>(m_use_color_target_edges)));
        CHECK_MSTATUS(m_shader_instance->setParameter(
            "gHoldOut", static_cast<int32_t>(m_hold_out)));
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
