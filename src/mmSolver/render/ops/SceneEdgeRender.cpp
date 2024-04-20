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

#include "SceneEdgeRender.h"

// Maya
#include <maya/MShaderManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/ops/scene_utils.h"
#include "mmSolver/render/shader/shader_utils.h"

namespace mmsolver {
namespace render {

const char kPARAMETER_EDGE_COLOR[] = "gEdgeColor";
const char kPARAMETER_EDGE_ALPHA[] = "gEdgeAlpha";
const char kPARAMETER_EDGE_THICKNESS[] = "gEdgeThickness";

SceneEdgeRender::SceneEdgeRender(const MString &name)
    : SceneRenderBase(name)
    , m_shader_override(nullptr)
    , m_edge_color(kEdgeColorDefault)
    , m_edge_alpha(kEdgeAlphaDefault)
    , m_edge_thickness(kEdgeThicknessDefault) {}

SceneEdgeRender::~SceneEdgeRender() {
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

const MHWRender::MShaderInstance *SceneEdgeRender::shaderOverride() {
    const bool verbose = false;

    if (!m_shader_override) {
        MMSOLVER_MAYA_VRB("SceneEdgeRender: Compile Edge Main shader...");
        const MString file_name = "mmEdge";
        const MString main_technique = "Main";
        m_shader_override = compile_shader_file(file_name, main_technique);
    }

    if (m_shader_override) {
        MMSOLVER_MAYA_VRB("SceneEdgeRender: Assign Edge shader parameters...");

        // This value is intended to bring an m_edge_thickness of 1.0
        // into an acceptable look for the edge rendering.
        //
        // This value is arbitrary and is picked from rough
        // experimentation.
        const float adjust_thickness = 0.01f;

        // Edge Thickness.
        CHECK_MSTATUS(m_shader_override->setParameter(
            kPARAMETER_EDGE_THICKNESS, m_edge_thickness * adjust_thickness));

        // Edge Color and Alpha
        const float alpha = m_edge_alpha;
        const float color[] = {m_edge_color.r, m_edge_color.g, m_edge_color.b,
                               1.0};
        CHECK_MSTATUS(
            m_shader_override->setParameter(kPARAMETER_EDGE_COLOR, color));
        CHECK_MSTATUS(
            m_shader_override->setParameter(kPARAMETER_EDGE_ALPHA, alpha));
    }

    return m_shader_override;
}

}  // namespace render
}  // namespace mmsolver
