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

#include "SceneRenderBase.h"

// Maya
#include <maya/M3dView.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MSelectionList.h>
#include <maya/MShaderManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/ops/scene_utils.h"

namespace mmsolver {
namespace render {

SceneRenderBase::SceneRenderBase(const MString &name)
    : MSceneRender(name)
    , m_background_style(kBackgroundStyleDefault)
    , m_draw_objects(DrawObjects::kNoOverride)
    , m_exclude_types(kExcludeNone)
    , m_prev_display_style(M3dView::kGouraudShaded)
    , m_scene_filter(MHWRender::MSceneRender::kNoSceneFilterOverride)
    , m_clear_mask(MHWRender::MClearOperation::kClearNone)
    , m_display_mode_override(MHWRender::MSceneRender::kNoDisplayModeOverride)
    , m_post_effects_override(MHWRender::MSceneRender::kPostEffectDisableAll)
    , m_culling_override(MHWRender::MSceneRender::kNoCullingOverride)
    , m_targets(nullptr)
    , m_target_index(0)
    , m_target_count(0) {
    m_view_rectangle[0] = 0.0f;
    m_view_rectangle[1] = 0.0f;
    m_view_rectangle[2] = 1.0f;
    m_view_rectangle[3] = 1.0f;
}

SceneRenderBase::~SceneRenderBase() { m_targets = nullptr; }

MHWRender::MRenderTarget *const *SceneRenderBase::targetOverrideList(
    unsigned int &listSize) {
    if (m_targets && (m_target_count > 0)) {
        listSize = m_target_count;
        return &m_targets[m_target_index];
    }
    listSize = 0;
    return nullptr;
}

MHWRender::MSceneRender::MSceneFilterOption
SceneRenderBase::renderFilterOverride() {
    return m_scene_filter;
}

MHWRender::MSceneRender::MDisplayMode SceneRenderBase::displayModeOverride() {
    return m_display_mode_override;
}

MUint64 SceneRenderBase::getObjectTypeExclusions() { return m_exclude_types; }

MHWRender::MClearOperation &SceneRenderBase::clearOperation() {
    set_background_clear_operation(m_background_style, m_clear_mask,
                                   mClearOperation);
    return mClearOperation;
}

MHWRender::MSceneRender::MPostEffectsOverride
SceneRenderBase::postEffectsOverride() {
    return m_post_effects_override;
}

MHWRender::MSceneRender::MCullingOption SceneRenderBase::cullingOverride() {
    return m_culling_override;
}

const MSelectionList *SceneRenderBase::objectSetOverride() {
    return find_draw_objects(m_draw_objects, m_layer_name, m_selection_list);
}

}  // namespace render
}  // namespace mmsolver
