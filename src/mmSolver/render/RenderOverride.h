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

#ifndef MM_SOLVER_RENDER_MAIN_OVERRIDE_H
#define MM_SOLVER_RENDER_MAIN_OVERRIDE_H

#include <maya/MBoundingBox.h>
#include <maya/MDagMessage.h>
#include <maya/MObjectHandle.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MUiMessage.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "RenderColorFormat.h"
#include "RenderGlobalsNode.h"
#include "RenderMode.h"
#include "constants.h"

namespace mmsolver {
namespace render {

class RenderOverride : public MHWRender::MRenderOverride {
public:
    // Enumerations to identify an operation within
    // a list of operations.
    enum {
        // --------------------------------------------------------------------
        // Depth pass.
        //
        // Draw the scene (except image planes), but only write to the
        // depth channel.
        kSceneDepthPass = 0,

        // --------------------------------------------------------------------
        // Background pass.
        //
        // Draw the Maya background color using the Maya preferences,
        // and draw imagePlanes.
        //
        // The render targets used for this pass is only the colour,
        // so the depth is ignored.
        kSceneBackgroundPass,

        // --------------------------------------------------------------------
        // Selection pass.
        //
        // Draw manipulators and excluded objects (but image planes
        // are drawn here).
        kSceneSelectionPass,

        // Post ops on target 1
        kEdgeDetectOp,

        // Copy target 1 to target 2.
        kCopyOp,

        // --------------------------------------------------------------------
        // Wireframe pass.
        //
        // Draw the scene as wireframe, but it will be cut out from
        // the depth pass.
        kSceneWireframePass,

        // --------------------------------------------------------------------
        // Blend pass.
        //
        // Blend target 1 and 2 back to target 1
        kWireframeBlendOp,

        // Post ops on target 1
        kInvertOp,

        // --------------------------------------------------------------------
        // Manipulator pass.
        //
        // Draw only manipulators.
        kSceneManipulatorPass,

        // --------------------------------------------------------------------
        // HUD pass. Draw 2D heads-up-display elements.
        kHudPass,

        // --------------------------------------------------------------------
        // Present pass. Present the drawn texture to the screen.
        kPresentOp,

        // Holds the total number of entries (must be last field).
        kNumberOfOps
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

    // The blend value between wireframe and non-wireframe.
    double wireframeAlpha() const { return m_wireframe_alpha; }
    void setWireframeAlpha(const double value) { m_wireframe_alpha = value; }

    double edgeThickness() const { return m_edge_thickness; }
    void setEdgeThickness(const double value) { m_edge_thickness = value; }

    double edgeThreshold() const { return m_edge_threshold; }
    void setEdgeThreshold(const double value) { m_edge_threshold = value; }

protected:
    MStatus updateParameters();
    MStatus updateRenderOperations();
    MStatus updateRenderTargets();
    MStatus setPanelNames(const MString& name);

    // Operation lists
    MHWRender::MRenderOperation* m_ops[kNumberOfOps];
    MString m_op_names[kNumberOfOps];
    int32_t m_current_op;

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
    // Override is for this panel
    MString m_panel_name;

    // A handle to the 'mmRenderGlobals' node.
    MObjectHandle m_globals_node;

    // A handle to the 'hardwareRenderingGlobals' node.
    MObjectHandle m_maya_hardware_globals_node;

    // Query update parameters from the mmRenderGlobals node.
    bool m_pull_updates;

    // Renderer settings
    RenderMode m_render_mode;
    RenderColorFormat m_render_color_format;
    bool m_multi_sample_enable;
    int32_t m_multi_sample_count;
    double m_wireframe_alpha;
    double m_edge_thickness;
    double m_edge_threshold;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_MAIN_OVERRIDE_H
