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

// Maya
#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "DisplayLayer.h"
#include "mmSolver/render/data/constants.h"
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
            DisplayLayer* layer =
                DisplayLayerList::getDisplayLayer(m_current_layer);
            for (; (m_current_layer < layer_count) &&
                   (layer->visibility() == false);
                 m_current_layer++) {
                layer = DisplayLayerList::getDisplayLayer(m_current_layer);
            }
        }
    }

    return m_current_op >= 0 && m_current_layer >= 0;
}

MStatus DisplayLayerList::updateRenderOperations() {
    const bool verbose = false;
    MMSOLVER_VRB("DisplayLayerList::updateRenderOperations: ");

    for (auto i = 0; i < m_layers.size(); ++i) {
        m_layers[i].updateRenderOperations();
    }

    return MS::kSuccess;
}

MStatus DisplayLayerList::updateRenderTargets(
    MHWRender::MRenderTarget** targets) {
    MStatus status = MS::kSuccess;

    const bool verbose = false;
    MMSOLVER_VRB("DisplayLayerList::updateRenderTargets");

    for (auto i = 0; i < m_layers.size(); ++i) {
        m_layers[i].updateRenderTargets(targets);
    }

    return status;
}

MStatus DisplayLayerList::setPanelNames(const MString& name) {
    const bool verbose = false;
    MMSOLVER_VRB("DisplayLayerList::setPanelNames: " << name.asChar());

    for (auto i = 0; i < m_layers.size(); ++i) {
        m_layers[i].setPanelNames(name);
    }

    return MS::kSuccess;
}

}  // namespace render
}  // namespace mmsolver
