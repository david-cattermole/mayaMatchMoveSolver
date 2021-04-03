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

#include "MMRendererConstants.h"
#include "MMRendererSceneRender.h"

#include <maya/MIOStream.h>
#include <maya/MGlobal.h>
#include <maya/MString.h>
#include <maya/MSelectionList.h>
#include <maya/MItSelectionList.h>
#include <maya/MItDag.h>
#include <maya/M3dView.h>
#include <maya/MPoint.h>
#include <maya/MImage.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MStateManager.h>
#include <maya/MShaderManager.h>
#include <maya/MTextureManager.h>
#include <maya/MDrawContext.h>
#include <maya/MShaderManager.h>

namespace mmsolver {
namespace renderer {

MMRendererSceneRender::MMRendererSceneRender(const MString &name)
        : MSceneRender(name),
          m_do_background(false),
          m_do_selectable(false),
          m_exclude_types(kExcludeNone),
          m_prev_display_style(M3dView::kGouraudShaded),
          m_scene_filter(MHWRender::MSceneRender::kNoSceneFilterOverride),
          m_clear_mask(MHWRender::MClearOperation::kClearNone),
          m_display_mode_override(MHWRender::MSceneRender::kNoDisplayModeOverride),
          m_targets(nullptr),
          m_target_index(0),
          m_target_count(0),
          m_shader_override(nullptr) {
    m_view_rectangle[0] = 0.0f;
    m_view_rectangle[1] = 0.0f;
    m_view_rectangle[2] = 1.0f;
    m_view_rectangle[3] = 1.0f;
}

MMRendererSceneRender::~MMRendererSceneRender() {
    m_targets = nullptr;

    if (m_shader_override) {
        MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
        if (!renderer) {
            return;
        }
        const MHWRender::MShaderManager *shaderMgr = renderer->getShaderManager();
        if (!shaderMgr) {
            return;
        }
        shaderMgr->releaseShader(m_shader_override);
        m_shader_override = nullptr;
    }
}

MHWRender::MRenderTarget *const *
MMRendererSceneRender::targetOverrideList(unsigned int &listSize) {
    if (m_targets) {
        listSize = m_target_count;
        return &m_targets[m_target_index];
    }
    listSize = 0;
    return nullptr;
}

MHWRender::MSceneRender::MSceneFilterOption
MMRendererSceneRender::renderFilterOverride() {
    return m_scene_filter;
}

MHWRender::MSceneRender::MDisplayMode
MMRendererSceneRender::displayModeOverride() {
    return m_display_mode_override;
}

MUint64
MMRendererSceneRender::getObjectTypeExclusions() {
    return m_exclude_types;
}

MHWRender::MClearOperation &
MMRendererSceneRender::clearOperation() {
    // Background color override. We get the current colors from the
    // renderer and use them.
    MHWRender::MRenderer* renderer = MHWRender::MRenderer::theRenderer();
    bool gradient = renderer->useGradient();
    MColor color1 = renderer->clearColor();
    MColor color2 = renderer->clearColor2();
    float val1[4] = { color1[0], color1[1], color1[2], 1.0f };
    float val2[4] = { color2[0], color2[1], color2[2], 1.0f };

    mClearOperation.setClearColor(val1);
    mClearOperation.setClearColor2(val2);
    mClearOperation.setClearGradient(gradient);

    mClearOperation.setMask(m_clear_mask);

    return mClearOperation;
}

const MSelectionList *
MMRendererSceneRender::objectSetOverride() {
    mSelectionList.clear();
    if (m_do_selectable) {
        MItDag it;
        it.traverseUnderWorld(m_do_background);

        for (it.reset(); !it.isDone(); it.next()) {
            auto item = it.currentItem();
            if (item.hasFn(MFn::kImagePlane)) {
                MDagPath path;
                it.getPath(path);
                if (m_do_background && (path.pathCount() < 2)) {

                } else {
                    mSelectionList.add(path);
                }
            }
        }
        return &mSelectionList;
    }
    return nullptr;
}

} // namespace renderer
} // namespace mmsolver
