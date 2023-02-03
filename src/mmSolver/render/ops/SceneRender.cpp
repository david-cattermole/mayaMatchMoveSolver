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
#include <maya/MFnDependencyNode.h>
#include <maya/MItDag.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MSelectionList.h>
#include <maya/MShaderManager.h>
#include <maya/MStateManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"

namespace mmsolver {
namespace render {

SceneRender::SceneRender(const MString &name)
    : MSceneRender(name)
    , m_background_style(kBackgroundStyleDefault)
    , m_draw_objects(DrawObjects::kNoOverride)
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
    if (m_background_style == BackgroundStyle::kTransparentBlack) {
        float val[4] = {0.0f, 0.0f, 0.0f, 0.0f};
        mClearOperation.setClearColor(val);
        mClearOperation.setClearColor2(val);
        mClearOperation.setClearGradient(false);
        mClearOperation.setClearStencil(0);
        // A depth value of 1.0f represents the 'most distant'
        // object. As objects draw, they draw darker pixels on top of
        // this background color.
        mClearOperation.setClearDepth(1.0f);
    } else if (m_background_style == BackgroundStyle::kMayaDefault) {
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
        mClearOperation.setClearStencil(0);
        mClearOperation.setClearDepth(1.0f);
    } else {
        MMSOLVER_ERR(
            "SceneRender::clearOperation: Background style is invalid: "
            << static_cast<short>(m_background_style));
    }

    mClearOperation.setMask(m_clear_mask);

    return mClearOperation;
}

const MHWRender::MShaderInstance *SceneRender::shaderOverride() {
    return m_shader_override;
}

MHWRender::MSceneRender::MPostEffectsOverride
SceneRender::postEffectsOverride() {
    return m_post_effects_override;
}

const MSelectionList *SceneRender::objectSetOverride() {
    const bool verbose = false;

    // If m_do_selectable is false and m_do_background is false: do
    // not override.
    m_selection_list.clear();

    if (m_draw_objects == DrawObjects::kOnlyNamedLayerObjects) {
        // Get the objects from the given display layer node.
        MObject layer_node;
        MStatus status = getAsObject(m_layer_name, layer_node);
        CHECK_MSTATUS(status);
        if ((status != MS::kSuccess) || layer_node.isNull()) {
            return nullptr;
        }

        MFnDependencyNode layer_depends_fn(layer_node, &status);
        CHECK_MSTATUS(status);
        MMSOLVER_VRB("SceneRender::objectSetOverride::layer: "
                     << layer_depends_fn.name().asChar());

        const bool want_networked_plug = true;

        // Get connection from layer to objects;
        // 'DisplayLater.drawInfo' -> 'Transform.drawOverrides'.
        MPlug draw_info_plug =
            layer_depends_fn.findPlug("drawInfo", want_networked_plug, &status);
        CHECK_MSTATUS(status);
        if (status == MStatus::kSuccess && !draw_info_plug.isNull()) {
            MPlugArray destination_plugs;
            draw_info_plug.destinations(destination_plugs, &status);
            MMSOLVER_VRB("SceneRender::objectSetOverride::count: "
                         << destination_plugs.length());

            for (auto i = 0; i < destination_plugs.length(); ++i) {
                if (destination_plugs[i].isNull()) {
                    continue;
                }
                MObject destination_node = destination_plugs[i].node();

                MDagPath dag_path;
                status = MDagPath::getAPathTo(destination_node, dag_path);
                if (status == MStatus::kSuccess) {
                    if ((dag_path.apiType() == MFn::kShape) ||
                        (dag_path.apiType() == MFn::kPluginLocatorNode) ||
                        (dag_path.apiType() == MFn::kPluginShape)) {
                        MMSOLVER_VRB(
                            "SceneRender::objectSetOverride::node: i = "
                            << i << " - " << dag_path.fullPathName().asChar());
                        m_selection_list.add(dag_path);
                    }

                    unsigned int shape_count = 0;
                    status = dag_path.numberOfShapesDirectlyBelow(shape_count);
                    for (auto j = 0; j < shape_count; ++j) {
                        MDagPath shape_path(dag_path);
                        shape_path.extendToShapeDirectlyBelow(j);

                        MMSOLVER_VRB(
                            "SceneRender::objectSetOverride::shape_node: i="
                            << i << " j=" << j << " - "
                            << shape_path.fullPathName().asChar());

                        m_selection_list.add(shape_path);
                    }
                }
            }
        }

        return &m_selection_list;
    } else if (m_draw_objects == DrawObjects::kNoOverride) {
        return nullptr;
    } else if (m_draw_objects ==
               DrawObjects::kOnlyCameraBackgroundImagePlanes) {
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
            } else if ((item.apiType() == MFn::kPluginLocatorNode) ||
                       (item.apiType() == MFn::kPluginShape)) {
                MDagPath path;
                it.getPath(path);
                m_selection_list.add(path);
            }
        }
        return &m_selection_list;
    } else if (m_draw_objects == DrawObjects::kAllImagePlanes) {
        // override drawn objects to all image planes not under cameras.
        MItDag it;
        it.traverseUnderWorld(false);
        for (it.reset(); !it.isDone(); it.next()) {
            auto item = it.currentItem();
            if (item.hasFn(MFn::kImagePlane) ||
                (item.apiType() == MFn::kPluginLocatorNode) ||
                (item.apiType() == MFn::kPluginShape)) {
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
