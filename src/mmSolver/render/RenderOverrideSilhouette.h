/*
 * Copyright (C) 2021, 2023, 2024 David Cattermole.
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
 * mmSolver viewport 2.0 renderer override.
 *
 */

#ifndef MM_SOLVER_RENDER_RENDER_OVERRIDE_SILHOUETTE_H
#define MM_SOLVER_RENDER_RENDER_OVERRIDE_SILHOUETTE_H

// STL
#include <vector>

// Maya
#include <maya/MBoundingBox.h>
#include <maya/MDagMessage.h>
#include <maya/MObjectHandle.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MUiMessage.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "RenderGlobalsBasicNode.h"
#include "mmSolver/render/data/RenderMode.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/ops/ClearOperation.h"
#include "mmSolver/render/ops/HudRender.h"
#include "mmSolver/render/ops/PresentTarget.h"
#include "mmSolver/render/ops/SceneRender.h"
#include "mmSolver/render/ops/SilhouetteRender.h"

namespace mmsolver {
namespace render {

// Helper to enumerate the target indexing
enum SilhouetteTargetId {
    kColorTarget = 0,
    kDepthTarget = 1,

    // Last item contains the number of enum entries.
    kTargetCount
};

class RenderOverrideSilhouette : public MHWRender::MRenderOverride {
public:
    RenderOverrideSilhouette(const MString& name);
    ~RenderOverrideSilhouette() override;

    MHWRender::DrawAPI supportedDrawAPIs() const override;

    MStatus setup(const MString& destination) override;
    MStatus cleanup() override;

    // Called by Maya to determine the name in the "Renderers" menu.
    MString uiName() const override { return m_ui_name; }

protected:
    // UI name
    MString m_ui_name;

    // Shared render target list
    MString m_target_override_names[SilhouetteTargetId::kTargetCount];
    MHWRender::MRenderTargetDescription*
        m_target_descriptions[SilhouetteTargetId::kTargetCount];
    MHWRender::MRenderTarget* m_targets[SilhouetteTargetId::kTargetCount];

    // Callback IDs for tracking viewport changes
    MCallbackId m_renderer_change_callback;
    MCallbackId m_render_override_change_callback;
    static void renderer_change_func(const MString& panel_name,
                                     const MString& old_renderer,
                                     const MString& new_renderer,
                                     void* client_data);
    static void render_override_change_func(const MString& panel_name,
                                            const MString& old_renderer,
                                            const MString& new_renderer,
                                            void* client_data);

    // Allow the command to access this class.
    friend class MMRendererCmd;

private:
    SceneRender* m_backgroundOp;
    SceneRender* m_sceneOp;
    SceneRender* m_selectOp;
    SilhouetteRender* m_silhouetteOp;
    SceneRender* m_wireframeOp;
    HudRender* m_hudOp;
    PresentTarget* m_presentOp;

    // A handle to the 'mmRenderGlobals' node.
    MObjectHandle m_globals_node;

    MSelectionList m_image_plane_nodes;

    bool m_enable;
    bool m_override_color;
    float m_depth_offset;
    float m_width;
    float m_color[3];
    float m_alpha;
    CullFace m_cull_face;
    uint8_t m_operation_num;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_RENDER_OVERRIDE_SILHOUETTE_H
