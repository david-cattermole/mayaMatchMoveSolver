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

#ifndef MAYA_MM_SOLVER_MM_RENDERER_SCENE_RENDER_H
#define MAYA_MM_SOLVER_MM_RENDERER_SCENE_RENDER_H

#include "MMRendererConstants.h"

#include <maya/MString.h>
#include <maya/MDrawTraversal.h>
#include <maya/MSelectionList.h>
#include <maya/M3dView.h>
#include <maya/MDrawContext.h>
#include <maya/MFrameContext.h>
#include <maya/MMessage.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MRenderTargetManager.h>


class MMRendererSceneRender : public MHWRender::MSceneRender {
public:
    MMRendererSceneRender(const MString &name);

    ~MMRendererSceneRender() override;

    MHWRender::MRenderTarget *const *
    targetOverrideList(uint32_t &listSize) override;

    MHWRender::MSceneRender::MSceneFilterOption renderFilterOverride() override;
    MHWRender::MSceneRender::MDisplayMode displayModeOverride() override;
    const MSelectionList *objectSetOverride() override;

    MUint64 getObjectTypeExclusions() override;
    MHWRender::MClearOperation &clearOperation() override;

    void setRenderTargets(MHWRender::MRenderTarget **targets,
                          const uint32_t index,
                          const uint32_t count) {
        m_targets = targets;
        m_target_index = index;
        m_target_count = count;
    }

    const MString &panelName() const {
        return m_panel_name;
    }

    void setPanelName(const MString &name) {
        m_panel_name.set(name.asChar());
    }

    const MFloatPoint &viewRectangle() const {
        return m_view_rectangle;
    }

    void setViewRectangle(const MFloatPoint &rect) {
        m_view_rectangle = rect;
    }

    MHWRender::MRenderTarget *colorTarget() const {
        if (m_targets) {
            return m_targets[kMyColorTarget];
        }
        return nullptr;
    }

    MHWRender::MRenderTarget *depthTarget() const {
        if (m_targets) {
            return m_targets[kMyDepthTarget];
        }
        return nullptr;
    }

    const MHWRender::MSceneRender::MSceneFilterOption sceneFilter() const {
        return m_scene_filter;
    }

    void setSceneFilter(const MHWRender::MSceneRender::MSceneFilterOption value) {
        m_scene_filter = value;
    }

    const uint32_t clearMask() const {
        return m_clear_mask;
    }

    void setClearMask(const uint32_t value) {
        m_clear_mask = value;
    }

    const MUint64 excludeTypes() const {
        return m_exclude_types;
    }

    void setExcludeTypes(const MUint64 value) {
        m_exclude_types = value;
    }

    const MHWRender::MSceneRender::MDisplayMode
    displayModeOverride() const {
        return m_display_mode_override;
    }

    void setDisplayModeOverride(const MHWRender::MSceneRender::MDisplayMode value) {
        m_display_mode_override = value;
    }

    const bool doSelectable() const {
        return m_do_selectable;
    }

    void setDoSelectable(const bool value) {
        m_do_selectable = value;
    }

    const bool doBackground() const {
        return m_do_background;
    }

    void setDoBackground(const bool value) {
        m_do_background = value;
    }

protected:
    MSelectionList mSelectionList;

    // 3D viewport panel name, if available
    MString m_panel_name;

    // Camera override
    MHWRender::MCameraOverride m_camera_override;

    // Viewport rectangle override
    MFloatPoint m_view_rectangle;

    // Render targets
    MHWRender::MRenderTarget **m_targets;

    // The index (and count) into the m_targets list of pointers. We
    // are able to give the exact targets.
    uint32_t m_target_index;
    uint32_t m_target_count;

    // Shader override for surfaces
    MHWRender::MShaderInstance *m_shader_override;

    // Scene draw filter override
    MHWRender::MSceneRender::MSceneFilterOption m_scene_filter;

    // Mask for clear override
    uint32_t m_clear_mask;

    // The node types to be excluded from drawing.
    MUint64 m_exclude_types;

    // Override the display mode (wireframe, shaded, etc)
    MHWRender::MSceneRender::MDisplayMode m_display_mode_override;

    // Specific values to control the objects to be drawn.
    bool m_do_selectable;
    bool m_do_background;

    M3dView::DisplayStyle m_prev_display_style;
};


#endif //MAYA_MM_SOLVER_MM_RENDERER_SCENE_RENDER_H
