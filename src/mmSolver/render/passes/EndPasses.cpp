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

#include "EndPasses.h"

// Maya
#include <maya/MObject.h>
#include <maya/MShaderManager.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/data/constants.h"
#include "mmSolver/render/ops/HudRender.h"
#include "mmSolver/render/ops/PresentTarget.h"
#include "mmSolver/render/ops/SceneRender.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace render {

// Set up operations
EndPasses::EndPasses() : m_current_op(-1) {
    // Initialise the operations for this override.
    for (auto i = 0; i < EndPass::kEndPassCount; ++i) {
        m_ops[i] = nullptr;
    }
}

EndPasses::~EndPasses() {
    // Delete all the operations. This will release any references to
    // other resources user per operation.
    for (auto i = 0; i < EndPass::kEndPassCount; ++i) {
        delete m_ops[i];
        m_ops[i] = nullptr;
    }
}

bool EndPasses::startOperationIterator() {
    m_current_op = 0;
    return true;
}

MHWRender::MRenderOperation *EndPasses::getOperationFromList(
    size_t &current_op, MRenderOperation **ops, const size_t count) {
    if (current_op >= 0 && current_op < count) {
        while (!ops[current_op] || !ops[current_op]->enabled()) {
            current_op++;
            if (current_op >= count) {
                return nullptr;
            }
        }
        if (ops[current_op]) {
            return ops[current_op];
        }
    }
    return nullptr;
}

MHWRender::MRenderOperation *EndPasses::renderOperation() {
    const auto count = EndPass::kEndPassCount;
    auto op = EndPasses::getOperationFromList(m_current_op, m_ops, count);
    if (op != nullptr) {
        return op;
    } else {
        m_current_op = -1;
    }
    return nullptr;
}

bool EndPasses::nextRenderOperation() {
    m_current_op++;

    const auto count = EndPass::kEndPassCount;
    if (m_current_op >= count) {
        m_current_op = -1;
    }

    return m_current_op >= 0;
}

MStatus EndPasses::updateRenderOperations() {
    const bool verbose = false;
    MMSOLVER_VRB("EndPasses::updateRenderOperations: ");

    if (m_ops[EndPass::kPresentOp] != nullptr) {
        // render operations are already up-to-date.
        return MS::kSuccess;
    }

    // Clear Masks
    const auto clear_mask_none =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearNone);
    const auto clear_mask_all =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearAll);
    const auto clear_mask_depth =
        static_cast<uint32_t>(MHWRender::MClearOperation::kClearDepth);

    // Draw these objects for transparency.
    const auto wire_draw_object_types =
        ~(MHWRender::MFrameContext::kExcludeMeshes |
          MHWRender::MFrameContext::kExcludeNurbsCurves |
          MHWRender::MFrameContext::kExcludeNurbsSurfaces |
          MHWRender::MFrameContext::kExcludeSubdivSurfaces);

    // Draw all non-geometry normally.
    const auto non_wire_draw_object_types =
        ((~wire_draw_object_types) |
         MHWRender::MFrameContext::kExcludeImagePlane |
         MHWRender::MFrameContext::kExcludePluginShapes);

    // Manipulators pass.
    auto *sceneOp = new SceneRender(kSceneManipulatorPassName);
    sceneOp->setBackgroundStyle(BackgroundStyle::kTransparentBlack);
    sceneOp->setClearMask(clear_mask_none);
    sceneOp->setSceneFilter(MHWRender::MSceneRender::kRenderPostSceneUIItems);
    sceneOp->setExcludeTypes(non_wire_draw_object_types);
    sceneOp->setDrawObjects(DrawObjects::kNoOverride);
    m_ops[EndPass::kSceneManipulatorPass] = sceneOp;

    // A preset 2D HUD render operation
    auto hudOp = new HudRender();
    m_ops[EndPass::kHudPass] = hudOp;

    // "Present" operation which will display the target for
    // viewports.  Operation is a no-op for batch rendering as
    // there is no on-screen buffer to send the result to.
    auto presentOp = new PresentTarget(kPresentOpName);
    m_ops[EndPass::kPresentOp] = presentOp;
    return MS::kSuccess;
}

// Update the render targets that are required for the entire
// override.  References to these targets are set on the individual
// operations as required so that they will send their output to the
// appropriate location.
MStatus EndPasses::updateRenderTargets(MHWRender::MRenderTarget **targets) {
    MStatus status = MS::kSuccess;
    const bool verbose = false;
    MMSOLVER_VRB("EndPasses::updateRenderTargets");

    // Update the render targets on the individual operations.
    //
    // This section will determine the outputs of each operation.  The
    // input of each operation is assumed to be the Maya provided
    // color and depth targets, but shaders may internally reference
    // specific render targets.

    auto manipulatorPassOp =
        dynamic_cast<SceneRender *>(m_ops[EndPass::kSceneManipulatorPass]);
    auto hudOp = dynamic_cast<HudRender *>(m_ops[EndPass::kHudPass]);
    auto presentOp = dynamic_cast<PresentTarget *>(m_ops[EndPass::kPresentOp]);

    if (!manipulatorPassOp || !hudOp || !presentOp) {
        return MS::kFailure;
    }

    manipulatorPassOp->setEnabled(true);
    manipulatorPassOp->setRenderTargets(targets, kMainColorTarget, 2);

    hudOp->setEnabled(false);
    hudOp->setRenderTargets(targets, kMainColorTarget, 2);

    presentOp->setEnabled(true);
    presentOp->setRenderTargets(targets, kMainColorTarget, 2);

    return status;
}

MStatus EndPasses::setPanelNames(const MString &name) {
    const bool verbose = false;
    MMSOLVER_VRB("EndPasses::setPanelNames: " << name.asChar());

    // Set the name of the panel on operations which may use the panel
    // name to find out the associated M3dView.
    if (m_ops[EndPass::kSceneManipulatorPass]) {
        auto op =
            dynamic_cast<SceneRender *>(m_ops[EndPass::kSceneManipulatorPass]);
        op->setPanelName(name);
    }

    return MS::kSuccess;
}

}  // namespace render
}  // namespace mmsolver
