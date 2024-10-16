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

#ifndef MM_SOLVER_RENDER_OPS_SCENE_RENDER_BASE_H
#define MM_SOLVER_RENDER_OPS_SCENE_RENDER_BASE_H

// Maya
#include <maya/M3dView.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/ops/scene_utils.h"

namespace mmsolver {
namespace render {

class SceneRenderBase : public MHWRender::MSceneRender {
public:
    explicit SceneRenderBase(const MString &name);
    ~SceneRenderBase() override;

    MHWRender::MRenderTarget *const *targetOverrideList(
        unsigned int &listSize) override;

    MHWRender::MSceneRender::MSceneFilterOption renderFilterOverride() override;
    MHWRender::MSceneRender::MDisplayMode displayModeOverride() override;
    const MSelectionList *objectSetOverride() override;
    void setObjectSetOverride(const MSelectionList *selection_list) {
        m_object_set_override = selection_list;
    }

    MUint64 getObjectTypeExclusions() override;
    MHWRender::MClearOperation &clearOperation() override;

    MHWRender::MSceneRender::MPostEffectsOverride postEffectsOverride()
        override;
    void setPostEffectsOverride(
        const MHWRender::MSceneRender::MPostEffectsOverride value) {
        m_post_effects_override = value;
    }

    MHWRender::MSceneRender::MCullingOption cullingOverride() override;
    void setCullingOverride(
        const MHWRender::MSceneRender::MCullingOption value) {
        m_culling_override = value;
    }

    void setRenderTargets(MHWRender::MRenderTarget **targets,
                          const uint32_t index, const uint32_t count) {
        m_targets = targets;
        m_target_index = index;
        m_target_count = count;
    }

    const MString &panelName() const { return m_panel_name; }
    void setPanelName(const MString &name) { m_panel_name.set(name.asChar()); }

    const MFloatPoint &viewRectangle() const { return m_view_rectangle; }
    void setViewRectangle(const MFloatPoint &rect) { m_view_rectangle = rect; }

    const MHWRender::MSceneRender::MSceneFilterOption sceneFilter() const {
        return m_scene_filter;
    }
    void setSceneFilter(
        const MHWRender::MSceneRender::MSceneFilterOption value) {
        m_scene_filter = value;
    }

    // "Background Style" is the color/alpha of the pixels that get
    // cleared (by the "clear operation"), which also uses the
    // "clearMask" to know which parts of the buffer are cleared (with
    // the requested color).
    const BackgroundStyle backgroundStyle() const { return m_background_style; }
    void setBackgroundStyle(const BackgroundStyle value) {
        m_background_style = value;
    }

    const uint32_t clearMask() const { return m_clear_mask; }
    void setClearMask(const uint32_t value) { m_clear_mask = value; }

    const MUint64 excludeTypes() const { return m_exclude_types; }
    void setExcludeTypes(const MUint64 value) { m_exclude_types = value; }

    const MHWRender::MSceneRender::MDisplayMode displayModeOverride() const {
        return m_display_mode_override;
    }
    void setDisplayModeOverride(
        const MHWRender::MSceneRender::MDisplayMode value) {
        m_display_mode_override = value;
    }

protected:
    // Objects Set override. Override which objects are drawn.
    const MSelectionList *m_object_set_override;

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

    // Scene draw filter override
    MHWRender::MSceneRender::MSceneFilterOption m_scene_filter;

    // Mask for clear override
    uint32_t m_clear_mask;

    BackgroundStyle m_background_style;

    MHWRender::MSceneRender::MPostEffectsOverride m_post_effects_override;
    MHWRender::MSceneRender::MCullingOption m_culling_override;

    // The node types to be excluded from drawing.
    MUint64 m_exclude_types;

    // Override the display mode (wireframe, shaded, etc)
    MHWRender::MSceneRender::MDisplayMode m_display_mode_override;

    M3dView::DisplayStyle m_prev_display_style;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_OPS_SCENE_RENDER_BASE_H
