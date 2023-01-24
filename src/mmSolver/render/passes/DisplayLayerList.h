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

#ifndef MM_SOLVER_RENDER_PASSES_DISPLAY_LAYER_LIST_H
#define MM_SOLVER_RENDER_PASSES_DISPLAY_LAYER_LIST_H

// STL
#include <algorithm>
#include <vector>

// Maya
#include <maya/MBoundingBox.h>
#include <maya/MDagMessage.h>
#include <maya/MObjectHandle.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MUiMessage.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "DisplayLayer.h"
#include "mmSolver/render/RenderGlobalsNode.h"
#include "mmSolver/render/data/EdgeDetectMode.h"
#include "mmSolver/render/data/RenderColorFormat.h"
#include "mmSolver/render/data/RenderMode.h"
#include "mmSolver/render/data/constants.h"

namespace mmsolver {
namespace render {

class DisplayLayerList {
public:
    DisplayLayerList();
    ~DisplayLayerList();

    bool startOperationIterator();
    MHWRender::MRenderOperation* renderOperation();
    bool nextRenderOperation();

    MStatus updateRenderOperations();
    MStatus updateRenderTargets(MHWRender::MRenderTarget** targets);
    MStatus setPanelNames(const MString& name);

    DisplayLayer* getDisplayLayer(const size_t index) {
        return &m_layers[index];
    }
    void pushDisplayLayer(DisplayLayer&& item) { m_layers.push_back(item); }
    void clearDisplayLayers() {
        m_current_op = -1;
        m_current_layer = -1;
        m_layers.clear();
    }
    void sortDisplayLayers() {
        std::sort(m_layers.begin(), m_layers.end(), &compareDisplayLayer);
    }

private:
    // The current state of the display layer operations, as we iterate over
    // them.
    size_t m_current_op;
    size_t m_current_layer;

    std::vector<DisplayLayer> m_layers;
};

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_PASSES_DISPLAY_LAYER_LIST_H
