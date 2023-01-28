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

#ifndef MM_SOLVER_RENDER_RENDER_OVERRIDE_H
#define MM_SOLVER_RENDER_RENDER_OVERRIDE_H

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
#include "RenderGlobalsNode.h"
#include "mmSolver/render/data/EdgeDetectMode.h"
#include "mmSolver/render/data/RenderColorFormat.h"
#include "mmSolver/render/data/RenderMode.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/passes/BeginPasses.h"
#include "mmSolver/render/passes/DisplayLayerList.h"
#include "mmSolver/render/passes/EndPasses.h"

namespace mmsolver {
namespace render {

class RenderOverride : public MHWRender::MRenderOverride {
public:
    // Enumerations to identify the different operation stage.
    enum Pass {
        kUninitialized = 0,
        kBegin,
        kLayers,
        kEnd,

        // Holds the total number of entries (must be last field).
        kPassCount
    };

    RenderOverride(const MString& name);
    ~RenderOverride() override;

    MHWRender::DrawAPI supportedDrawAPIs() const override;

    bool startOperationIterator() override;
    MHWRender::MRenderOperation* renderOperation() override;
    bool nextRenderOperation() override;

    // Basic setup and cleanup
    MStatus setup(const MString& destination) override;
    MStatus cleanup() override;

    // Called by Maya to determine the name in the "Renderers" menu.
    MString uiName() const override { return m_ui_name; }

    // The Maya panel name this override is locked to.
    const MString& panelName() const { return m_panel_name; }

protected:
    MStatus updateParameters();
    MStatus updateDisplayLayers();
    MStatus updateRenderOperations();
    MStatus updateRenderTargets();
    MStatus setPanelNames(const MString& name);

    // Shared render target list
    MString m_target_override_names[kTargetCount];
    MHWRender::MRenderTargetDescription* m_target_descs[kTargetCount];
    MHWRender::MRenderTarget* m_targets[kTargetCount];
    bool m_target_supports_sRGB_write[kTargetCount];

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
    static MStatus getDisplayLayerFromNode(MFnDependencyNode& depends_node,
                                           unsigned int viewport_display_style,
                                           DisplayLayer& out_display_layer);

    // Override is for this panel
    MString m_panel_name;

    // A handle to the 'mmRenderGlobals' node.
    MObjectHandle m_globals_node;

    // A handle to the 'hardwareRenderingGlobals' node.
    MObjectHandle m_maya_hardware_globals_node;

    // Display layer node object handles.
    std::vector<MObjectHandle> m_display_layer_nodes;

    // Query update parameters from the mmRenderGlobals node.
    bool m_pull_updates;

    // Keep track of the current state of the render operation layers.
    Pass m_current_pass;

    // Renderer settings
    RenderColorFormat m_render_color_format;
    bool m_multi_sample_enable;
    int32_t m_multi_sample_count;
    unsigned int m_viewport_display_style;
    bool m_viewport_draw_textures;

    // Passes and Layers.
    BeginPasses m_begin_passes;
    EndPasses m_end_passes;
    DisplayLayerList m_display_layers;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_RENDER_OVERRIDE_H
