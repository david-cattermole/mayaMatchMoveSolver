/*
 * Copyright (C) 2023 Patcha Saheb Binginapalli.
 * Copyright (C) 2023, 2024 David Cattermole.
 *
 * Patcha Saheb Binginapalli Python code was ported to C++ by David
 * Cattermole (2023-09-13 YYYY-MM-DD).
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

#ifndef MM_SOLVER_RENDER_OPS_SILHOUETTE_RENDER_H
#define MM_SOLVER_RENDER_OPS_SILHOUETTE_RENDER_H

// Maya
#include <maya/M3dView.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>

// Maya Viewport 1.0
#include <maya/MGL.h>
#include <maya/MGLFunctionTable.h>

// Maya Viewport 2.0
#include <maya/MRenderTargetManager.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/render/data/CullFace.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/ops/scene_utils.h"

namespace mmsolver {
namespace render {

class SilhouetteRender : public MHWRender::MUserRenderOperation {
public:
    SilhouetteRender(const MString &name);
    ~SilhouetteRender() override;

    MStatus execute(const MHWRender::MDrawContext &drawContext) override;

    bool requiresLightData() const override { return true; }
    void setLightList(MSelectionList *val) { mLightList = val; }

    MHWRender::MRenderTarget *const *targetOverrideList(
        unsigned int &listSize) override;

    void setRenderTargets(MHWRender::MRenderTarget **targets) {
        m_output_targets = targets;
    }

    void setPanelName(MString value) { m_panel_name = value; }
    void setSilhouetteEnable(const bool value) { m_silhouette_enable = value; }
    void setSilhouetteOverrideColor(const bool value) { m_silhouette_override_color = value; }
    void setSilhouetteDepthOffset(const float value) {
        m_silhouette_depth_offset = value;
    }
    void setSilhouetteWidth(const float value) { m_silhouette_width = value; }
    void setSilhouetteColor(const float r, const float g, const float b) {
        m_silhouette_color[0] = r;
        m_silhouette_color[1] = g;
        m_silhouette_color[2] = b;
    }
    void setSilhouetteAlpha(const float value) { m_silhouette_alpha = value; }
    void setSilhouetteCullFace(const CullFace value) {
        if (value == CullFace::kBack) {
            m_silhouette_cull_face = GL_BACK;

        } else if (value == CullFace::kFront) {
            m_silhouette_cull_face = GL_FRONT;

        } else if (value == CullFace::kFrontAndBack) {
            m_silhouette_cull_face = GL_FRONT_AND_BACK;
        } else {
            MMSOLVER_MAYA_ERR("MM Renderer SilhouetteRender: "
                              << "setSilhouetteCullFace failed, CullFace enum "
                                 "value is invalid: "
                              << static_cast<int>(value));
            // Error.
        }
    }

protected:
    MSelectionList *mLightList;
    MHWRender::MRenderTarget **m_output_targets;
    MString m_panel_name;
    GLuint m_shader_program;
    MGLFunctionTable *gGLFT;

    bool m_silhouette_enable;
    bool m_silhouette_override_color;
    float m_silhouette_depth_offset;
    float m_silhouette_width;
    float m_silhouette_color[3];
    float m_silhouette_alpha;
    GLenum m_silhouette_cull_face;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_OPS_SILHOUETTE_RENDER_H
