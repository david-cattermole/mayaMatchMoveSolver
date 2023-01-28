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
 *
 */

#ifndef MM_SOLVER_RENDER_PASSES_END_PASSES_H
#define MM_SOLVER_RENDER_PASSES_END_PASSES_H

// Maya
#include <maya/MBoundingBox.h>
#include <maya/MDagMessage.h>
#include <maya/MObjectHandle.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MString.h>
#include <maya/MUiMessage.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "DisplayLayerList.h"
#include "mmSolver/render/RenderGlobalsNode.h"
#include "mmSolver/render/data/EdgeDetectMode.h"
#include "mmSolver/render/data/RenderColorFormat.h"
#include "mmSolver/render/data/RenderMode.h"
#include "mmSolver/render/data/constants.h"

namespace mmsolver {
namespace render {

class EndPasses {
public:
    // Enumerations to identify an operation within
    // a list of operations, used at the start of the render override.
    enum EndPass {
        kSceneManipulatorPass = 0,  // Draw the scene with 3D manipulators.
        kHudPass,                   // Draw 2D Heads-Up-Display (HUD) elements.
        kPresentOp,                 // Present the drawn texture to the screen.

        // Holds the total number of entries (must be last field).
        kEndPassCount
    };

    EndPasses();
    ~EndPasses();

    bool startOperationIterator();
    MHWRender::MRenderOperation* renderOperation();
    bool nextRenderOperation();

    MStatus updateRenderOperations();
    MStatus updateRenderTargets(MHWRender::MRenderTarget** targets);
    MStatus setPanelNames(const MString& name);

    // Operation lists
    MHWRender::MRenderOperation* m_ops[EndPass::kEndPassCount];

    // Keep track of the current state of the render operation layers.
    size_t m_current_op;

private:
    static MRenderOperation* getOperationFromList(size_t& current_op,
                                                  MRenderOperation** ops,
                                                  const size_t count);
};

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_PASSES_END_PASSES_H
