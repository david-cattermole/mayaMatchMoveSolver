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

#ifndef MAYA_MM_SOLVER_MM_RENDERER_MAIN_OVERRIDE_H
#define MAYA_MM_SOLVER_MM_RENDERER_MAIN_OVERRIDE_H

#include "constants.h"

#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MRenderTargetManager.h>

namespace mmsolver {
namespace renderer {

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
        // Draw the Maya background colour using the Maya preferences,
        // and draw imagePlanes.
        //
        // The render targets used for this pass is only the colour,
        // so the depth is ignored.
        kSceneBackgroundPass,

        // --------------------------------------------------------------------
        // Selection pass.
        //
        // Draw manipulators and excluded objects (but image planes
        // are draw here).
        kSceneSelectionPass,

        // --------------------------------------------------------------------
        // Wireframe pass.
        //
        // Draw the scene as wireframe, but it will be cut out from
        // the depth pass.
        kSceneWireframePass,

        // Post ops on target 1
        kEdgeDetectOp,

        // --------------------------------------------------------------------
        // Blend pass.
        //
        // Blend target 1 and 2 back to target 1
        kBlendOp,

        // Post ops on target 1
        kInvertOp,

        // --------------------------------------------------------------------
        // HUD pass. Draw 2D heads-up-display elements.
        kHudPass,

        // --------------------------------------------------------------------
        // Present pass. Present the drawn texture to the screen.
        kPresentOp,

        // Holds the total number of entries (must be last field).
        kNumberOfOps
    };

    RenderOverride(const MString &name);

    ~RenderOverride() override;

    MHWRender::DrawAPI supportedDrawAPIs() const override;

    bool startOperationIterator() override;

    MHWRender::MRenderOperation *renderOperation() override;

    bool nextRenderOperation() override;

    // Basic setup and cleanup
    MStatus setup(const MString &destination) override;
    MStatus cleanup() override;

    // Called by Maya to determine the name in the "Renderers" menu.
    MString uiName() const override {
        return m_ui_name;
    }

    // The Maya panel name this override is locked to.
    const MString &panelName() const {
        return m_panel_name;
    }

    // The blend value between edge detect and non-edge detect.
    double blend() const {
        return m_blend;
    }

    // The blend value between edge detect and non-edge detect.
    void setBlend(const double value) {
        m_blend = value;
    }

protected:
    MStatus updateRenderOperations();
    MStatus updateRenderTargets();
    MStatus setPanelNames(const MString &name);

    // Operation lists
    MHWRender::MRenderOperation *m_ops[kNumberOfOps];
    MString m_op_names[kNumberOfOps];
    int32_t m_current_op;

    // Shared render target list
    MString m_target_override_names[kTargetCount];
    MHWRender::MRenderTargetDescription *m_target_descs[kTargetCount];
    MHWRender::MRenderTarget *m_targets[kTargetCount];
    bool m_target_supports_sRGB_write[kTargetCount];

    // UI name
    MString m_ui_name;

    friend class MMRendererCmd;

private:
    // Override is for this panel
    MString m_panel_name;

    double m_blend;
};

} // namespace renderer
} // namespace mmsolver

#endif //MAYA_MM_SOLVER_MM_RENDERER_MAIN_OVERRIDE_H
