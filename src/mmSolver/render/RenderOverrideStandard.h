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
 * mmSolver viewport 2.0 renderer override.
 *
 */

#ifndef MM_SOLVER_RENDER_STANDARD_RENDER_OVERRIDE_H
#define MM_SOLVER_RENDER_STANDARD_RENDER_OVERRIDE_H

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
#include "RenderGlobalsStandardNode.h"
#include "mmSolver/render/data/RenderMode.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/ops/SceneRender.h"
#include "mmSolver/render/ops/SilhouetteRender.h"

namespace mmsolver {
namespace render {

class RenderOverrideStandard : public MHWRender::MRenderOverride {
public:
    RenderOverrideStandard(const MString& name);
    ~RenderOverrideStandard() override;

    MHWRender::DrawAPI supportedDrawAPIs() const override;

    MStatus setup(const MString& destination) override;
    MStatus cleanup() override;

    // Called by Maya to determine the name in the "Renderers" menu.
    MString uiName() const override { return m_ui_name; }

protected:
    // UI name
    MString m_ui_name;

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

    // A handle to the 'mmRenderGlobalsStandard' node.
    MObjectHandle m_globals_node;

    MSelectionList m_image_plane_nodes;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_STANDARD_RENDER_OVERRIDE_H
