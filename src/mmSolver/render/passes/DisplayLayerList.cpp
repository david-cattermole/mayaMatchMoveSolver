/*
 * Copyright (C) 2023 David Cattermole.
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

#include "DisplayLayerList.h"

// STL
#include <cassert>

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MFnSet.h>
#include <maya/MItDag.h>
#include <maya/MItDependencyNodes.h>
#include <maya/MIteratorType.h>
#include <maya/MSelectionList.h>
#include <maya/MShaderManager.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "DisplayLayer.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/ops/scene_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

DisplayLayerList::DisplayLayerList() : m_current_op(-1), m_current_layer(-1) {}

DisplayLayerList::~DisplayLayerList() {}

bool DisplayLayerList::startOperationIterator() {
    m_current_op = 0;
    m_current_layer = 0;
    return true;
}

MHWRender::MRenderOperation* DisplayLayerList::renderOperation() {
    const auto count = m_layers.size();
    if (m_current_layer >= 0 && m_current_layer < count) {
        DisplayLayer* layer =
            DisplayLayerList::getDisplayLayer(m_current_layer);
        if (!layer) {
            // If the layer is in the vector, it should always be
            // allocated and should therefore this branch should never
            // happen.
            return nullptr;
        }
        auto op = layer->getOperation(m_current_op);
        if (op != nullptr) {
            return op;
        } else {
            m_current_op = -1;
        }
    }
    return nullptr;
}

bool DisplayLayerList::nextRenderOperation() {
    m_current_op++;

    const auto pass_count = DisplayLayerPasses::kLayerPassesCount;
    if (m_current_op >= pass_count) {
        m_current_layer++;
        m_current_op = 0;

        const auto layer_count = m_layers.size();
        if (m_current_layer >= layer_count) {
            m_current_layer = -1;
            m_current_op = -1;
        } else {
            // Get next layer index that is visible.
            do {
                DisplayLayer* layer =
                    DisplayLayerList::getDisplayLayer(m_current_layer);
                if (layer->visibility()) {
                    break;
                } else {
                    m_current_layer += 1;
                }
                if (m_current_layer >= layer_count) {
                    m_current_layer = -1;
                    m_current_op = -1;
                    break;
                }
            } while (m_current_layer < layer_count);
        }
    }

    return m_current_op >= 0 && m_current_layer >= 0;
}

MStatus DisplayLayerList::updateRenderOperations() {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("DisplayLayerList::updateRenderOperations: ");

    for (auto i = 0; i < m_layers.size(); ++i) {
        const MSelectionList* drawable_nodes = &m_layer_children_nodes[i];
        m_layers[i].updateRenderOperations(drawable_nodes);
    }

    return MS::kSuccess;
}

MStatus DisplayLayerList::updateRenderTargets(
    MHWRender::MRenderTarget** targets) {
    MStatus status = MS::kSuccess;

    const bool verbose = false;
    MMSOLVER_MAYA_VRB("DisplayLayerList::updateRenderTargets");

    for (auto i = 0; i < m_layers.size(); ++i) {
        m_layers[i].updateRenderTargets(targets);
    }

    return status;
}

MStatus DisplayLayerList::updateNodes() {
    const bool verbose = false;
    MStatus status = MS::kSuccess;

    m_layer_children_nodes.clear();
    for (int i = 0; i < m_layers.size(); i++) {
        const DisplayLayer display_layer = m_layers[i];

        MObject object_set_node = display_layer.objectSetNode();
        MSelectionList selection_list;
        if (object_set_node.isNull()) {
            MMSOLVER_MAYA_WRN(
                "DisplayLayerList::updateNodes: "
                "ObjectSet node is not valid."
                " i="
                << i << " displayLayer name=" << display_layer.name().asChar());
            m_layer_children_nodes.emplace_back(selection_list);
            continue;
        }

        MFnSet mfn_object_set(object_set_node, &status);
        CHECK_MSTATUS(status);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_WRN(
                "DisplayLayerList::updateNodes: "
                "Failed to construct a MFnSet object."
                " i="
                << i << " displayLayer name=" << display_layer.name().asChar());
            continue;
        }

        MMSOLVER_MAYA_VRB("DisplayLayerList::updateNodes: ObjectSet name: "
                          << mfn_object_set.name().asChar());

        // We do not expect to have any sets in our set.
        const bool flatten = false;
        status = mfn_object_set.getMembers(selection_list, flatten);
        CHECK_MSTATUS(status);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_WRN(
                "DisplayLayerList::updateNodes: "
                "Failed to get members from a MFnSet object."
                " i="
                << i << " displayLayer name=" << display_layer.name().asChar()
                << " ObjectSet node=" << mfn_object_set.name().asChar());
            continue;
        }

        MMSOLVER_MAYA_VRB(
            "DisplayLayerList::updateNodes: Number of ObjectSet Members: "
            << selection_list.length());

        m_layer_children_nodes.emplace_back(selection_list);
    }

    return status;
}

MStatus DisplayLayerList::setPanelNames(const MString& name) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("DisplayLayerList::setPanelNames: " << name.asChar());

    for (auto i = 0; i < m_layers.size(); ++i) {
        m_layers[i].setPanelNames(name);
    }

    return MS::kSuccess;
}

}  // namespace render
}  // namespace mmsolver
