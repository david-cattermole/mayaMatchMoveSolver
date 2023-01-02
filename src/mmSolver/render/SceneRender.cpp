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

#include "SceneRender.h"

// Maya
#include <maya/M3dView.h>
#include <maya/MItDag.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MSelectionList.h>
#include <maya/MShaderManager.h>
#include <maya/MStateManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "constants.h"

namespace mmsolver {
namespace render {

SceneRender::SceneRender(const MString &name)
    : MSceneRender(name)
    , m_do_background(false)
    , m_do_selectable(false)
    , m_exclude_types(kExcludeNone)
    , m_prev_display_style(M3dView::kGouraudShaded)
    , m_scene_filter(MHWRender::MSceneRender::kNoSceneFilterOverride)
    , m_clear_mask(MHWRender::MClearOperation::kClearNone)
    , m_display_mode_override(MHWRender::MSceneRender::kNoDisplayModeOverride)
    , m_post_effects_override(MHWRender::MSceneRender::kPostEffectDisableAll)
    , m_targets(nullptr)
    , m_target_index(0)
    , m_target_count(0)
    , m_shader_override(nullptr) {
    m_view_rectangle[0] = 0.0f;
    m_view_rectangle[1] = 0.0f;
    m_view_rectangle[2] = 1.0f;
    m_view_rectangle[3] = 1.0f;
}

SceneRender::~SceneRender() {
    m_targets = nullptr;

    if (m_shader_override) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        if (!renderer) {
            return;
        }
        const MHWRender::MShaderManager *shaderMgr =
            renderer->getShaderManager();
        if (!shaderMgr) {
            return;
        }
        shaderMgr->releaseShader(m_shader_override);
        m_shader_override = nullptr;
    }
}

MHWRender::MRenderTarget *const *SceneRender::targetOverrideList(
    unsigned int &listSize) {
    if (m_targets && (m_target_count > 0)) {
        listSize = m_target_count;
        return &m_targets[m_target_index];
    }
    listSize = 0;
    return nullptr;
}

MHWRender::MSceneRender::MSceneFilterOption
SceneRender::renderFilterOverride() {
    return m_scene_filter;
}

MHWRender::MSceneRender::MDisplayMode SceneRender::displayModeOverride() {
    return m_display_mode_override;
}

MUint64 SceneRender::getObjectTypeExclusions() { return m_exclude_types; }

MHWRender::MClearOperation &SceneRender::clearOperation() {
    // Background color override. We get the current colors from the
    // renderer and use them.
    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    bool gradient = renderer->useGradient();
    MColor color1 = renderer->clearColor();
    MColor color2 = renderer->clearColor2();
    float val1[4] = {color1[0], color1[1], color1[2], 1.0f};
    float val2[4] = {color2[0], color2[1], color2[2], 1.0f};

    mClearOperation.setClearColor(val1);
    mClearOperation.setClearColor2(val2);
    mClearOperation.setClearGradient(gradient);

    mClearOperation.setMask(m_clear_mask);

    return mClearOperation;
}

MHWRender::MSceneRender::MPostEffectsOverride
SceneRender::postEffectsOverride() {
    return m_post_effects_override;
}

const MSelectionList *SceneRender::objectSetOverride() {
    // If m_do_selectable is false and m_do_background is false: do
    // not override.
    m_selection_list.clear();
    if (!m_do_selectable && !m_do_background) {
        // This is the most common branch, so it is first.
        return nullptr;
    } else if (m_do_selectable && m_do_background) {
        // If m_do_selectable is true and m_do_background is true:
        // override drawn objects to only image planes under cameras.
        MItDag it;
        it.traverseUnderWorld(true);
        for (it.reset(); !it.isDone(); it.next()) {
            auto item = it.currentItem();
            if (item.hasFn(MFn::kImagePlane)) {
                MDagPath path;
                it.getPath(path);
                if (path.pathCount() < 2) {
                    continue;
                }
                m_selection_list.add(path);
            } else if (item.apiType() == MFn::kPluginLocatorNode) {
                MDagPath path;
                it.getPath(path);
                m_selection_list.add(path);
            }
        }
        return &m_selection_list;
    } else if (m_do_selectable && !m_do_background) {
        // If m_do_selectable is true and m_do_background is false:
        // override drawn objects to all image planes not under cameras.
        MItDag it;
        it.traverseUnderWorld(false);
        for (it.reset(); !it.isDone(); it.next()) {
            auto item = it.currentItem();
            if (item.hasFn(MFn::kImagePlane) ||
                (item.apiType() == MFn::kPluginLocatorNode)) {
                MDagPath path;
                it.getPath(path);
                m_selection_list.add(path);
            }
        }
        return &m_selection_list;
    }
    return nullptr;
}

}  // namespace render
}  // namespace mmsolver
