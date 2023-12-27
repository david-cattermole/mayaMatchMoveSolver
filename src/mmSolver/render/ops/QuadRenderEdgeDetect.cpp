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

#include "QuadRenderEdgeDetect.h"

#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>

// MM Solver
#include "mmSolver/render/data/constants.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

const char kPARAMETER_COLOR_TEX[] = "gColorTex";
const char kPARAMETER_DEPTH_TEX[] = "gDepthTex";
const char kPARAMETER_EDGE_COLOR[] = "gEdgeColor";
const char kPARAMETER_EDGE_ALPHA[] = "gEdgeAlpha";
const char kPARAMETER_THICKNESS[] = "gThickness";
const char kPARAMETER_THRESHOLD_COLOR[] = "gThresholdColor";
const char kPARAMETER_THRESHOLD_ALPHA[] = "gThresholdAlpha";
const char kPARAMETER_THRESHOLD_DEPTH[] = "gThresholdDepth";

QuadRenderEdgeDetect::QuadRenderEdgeDetect(const MString &name)
    : QuadRenderBase(name)
    , m_shader_instance_sobel(nullptr)
    , m_shader_instance_frei_chen(nullptr)
    , m_target_index_depth(0)
    , m_target_index_color(0)
    , m_edge_detect_mode(kEdgeDetectModeDefault)
    , m_edge_color(kEdgeColorDefault)
    , m_edge_alpha(kEdgeAlphaDefault)
    , m_thickness(kEdgeThicknessDefault)
    , m_threshold_color(kEdgeThresholdColorDefault)
    , m_threshold_alpha(kEdgeThresholdAlphaDefault)
    , m_threshold_depth(kEdgeThresholdDepthDefault) {}

QuadRenderEdgeDetect::~QuadRenderEdgeDetect() {
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        return;
    }
    const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
    if (!shaderMgr) {
        return;
    }

    // Release Sobel shader.
    if (m_shader_instance_sobel) {
        shaderMgr->releaseShader(m_shader_instance_sobel);
        m_shader_instance_sobel = nullptr;
    }

    // Release Frei-Chen shader.
    if (m_shader_instance_frei_chen) {
        shaderMgr->releaseShader(m_shader_instance_frei_chen);
        m_shader_instance_frei_chen = nullptr;
    }
}

// Determine the targets to be used.
//
// Called by Maya.
MHWRender::MRenderTarget *const *QuadRenderEdgeDetect::targetOverrideList(
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
const MHWRender::MShaderInstance *QuadRenderEdgeDetect::shader() {
    const bool verbose = false;

    if (m_edge_detect_mode == EdgeDetectMode::k3dSilhouette) {
        return nullptr;
    }

    const MString file_name = "mmSilhouette";
    const MString sobel_technique = "Sobel";
    const MString frei_chen_technique = "FreiChen";

    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        return nullptr;
    }
    const MHWRender::MShaderManager *shader_manager =
        renderer->getShaderManager();
    if (!shader_manager) {
        return nullptr;
    }

    // Compile Sobel shader
    if (!m_shader_instance_sobel) {
        MMSOLVER_MAYA_VRB("QuardRenderEdgeDetect: Compile Sobel shader...");
        m_shader_instance_sobel = shader_manager->getEffectsFileShader(
            file_name.asChar(), sobel_technique.asChar());
    }

    // Compile Frei-Chen shader
    if (!m_shader_instance_frei_chen) {
        MMSOLVER_MAYA_VRB("QuardRenderEdgeDetect: Compile Frei-Chen shader...");
        m_shader_instance_frei_chen = shader_manager->getEffectsFileShader(
            file_name.asChar(), frei_chen_technique.asChar());
    }

    // Set default parameters
    if (m_shader_instance_sobel && m_shader_instance_frei_chen) {
        MMSOLVER_MAYA_VRB("QuardRenderEdgeDetect: Assign shader parameters...");

        if (m_targets) {
            MHWRender::MRenderTarget *depth_target =
                m_targets[m_target_index_depth];
            MHWRender::MRenderTarget *color_target =
                m_targets[m_target_index_color];
            if (depth_target) {
                MMSOLVER_MAYA_VRB(
                    "QuardRenderEdgeDetect: Assign depth texture to shader...");
                MHWRender::MRenderTargetAssignment assignment;
                assignment.target = depth_target;
                CHECK_MSTATUS(m_shader_instance_sobel->setParameter(
                    kPARAMETER_DEPTH_TEX, assignment));
                CHECK_MSTATUS(m_shader_instance_frei_chen->setParameter(
                    kPARAMETER_DEPTH_TEX, assignment));
            }
            if (color_target) {
                MMSOLVER_MAYA_VRB(
                    "QuardRenderEdgeDetect: Assign color texture to shader...");
                MHWRender::MRenderTargetAssignment assignment;
                assignment.target = color_target;
                CHECK_MSTATUS(m_shader_instance_sobel->setParameter(
                    kPARAMETER_COLOR_TEX, assignment));
                CHECK_MSTATUS(m_shader_instance_frei_chen->setParameter(
                    kPARAMETER_COLOR_TEX, assignment));
            }
        }

        // The edge thickness.
        CHECK_MSTATUS(m_shader_instance_sobel->setParameter(
            kPARAMETER_THICKNESS, m_thickness));
        CHECK_MSTATUS(m_shader_instance_frei_chen->setParameter(
            kPARAMETER_THICKNESS, m_thickness));

        // The edge threshold.
        CHECK_MSTATUS(m_shader_instance_sobel->setParameter(
            kPARAMETER_THRESHOLD_COLOR, m_threshold_color));
        CHECK_MSTATUS(m_shader_instance_sobel->setParameter(
            kPARAMETER_THRESHOLD_ALPHA, m_threshold_alpha));
        CHECK_MSTATUS(m_shader_instance_sobel->setParameter(
            kPARAMETER_THRESHOLD_DEPTH, m_threshold_depth));
        CHECK_MSTATUS(m_shader_instance_frei_chen->setParameter(
            kPARAMETER_THRESHOLD_COLOR, m_threshold_color));
        CHECK_MSTATUS(m_shader_instance_frei_chen->setParameter(
            kPARAMETER_THRESHOLD_ALPHA, m_threshold_alpha));
        CHECK_MSTATUS(m_shader_instance_frei_chen->setParameter(
            kPARAMETER_THRESHOLD_DEPTH, m_threshold_depth));

        // Edge Color and Alpha
        const float alpha = m_edge_alpha;
        const float color[] = {m_edge_color.r, m_edge_color.g, m_edge_color.b,
                               1.0};
        CHECK_MSTATUS(m_shader_instance_sobel->setParameter(
            kPARAMETER_EDGE_COLOR, color));
        CHECK_MSTATUS(m_shader_instance_frei_chen->setParameter(
            kPARAMETER_EDGE_COLOR, color));
        CHECK_MSTATUS(m_shader_instance_sobel->setParameter(
            kPARAMETER_EDGE_ALPHA, alpha));
        CHECK_MSTATUS(m_shader_instance_frei_chen->setParameter(
            kPARAMETER_EDGE_ALPHA, alpha));
    }

    if (m_edge_detect_mode == EdgeDetectMode::kSobel) {
        return m_shader_instance_sobel;
    } else if (m_edge_detect_mode == EdgeDetectMode::kFreiChen) {
        return m_shader_instance_frei_chen;
    }
    return nullptr;
}

}  // namespace render
}  // namespace mmsolver
