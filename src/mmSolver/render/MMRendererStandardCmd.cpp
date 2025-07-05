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

#include "MMRendererStandardCmd.h"

// Maya
#include <maya/M3dView.h>
#include <maya/MArgDatabase.h>
#include <maya/MGlobal.h>
#include <maya/MSyntax.h>
#include <maya/MViewport2Renderer.h>

// MM Solver
#include "RenderOverrideStandard.h"

namespace mmsolver {
namespace render {

MMRendererStandardCmd::MMRendererStandardCmd() {}

MMRendererStandardCmd::~MMRendererStandardCmd() {}

void *MMRendererStandardCmd::creator() {
    return (void *)(new MMRendererStandardCmd);
}

MString MMRendererStandardCmd::cmdName() { return kRendererStandardCmdName; }

MSyntax MMRendererStandardCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(true);
    return syntax;
}

MStatus MMRendererStandardCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kFailure;

    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MGlobal::displayError("VP2 renderer not initialized.");
        return status;
    }

    const RenderOverrideStandard *override_ptr =
        (RenderOverrideStandard *)renderer->findRenderOverride(
            kRendererStandardName);
    if (override_ptr == nullptr) {
        MGlobal::displayError(kRendererStandardCmdName + " is not registered.");
        return status;
    }

    MArgDatabase argData(syntax(), args, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    M3dView view = M3dView::active3dView(&status);
    if (!status) {
        MGlobal::displayWarning("Failed to find an active 3d view.");
        return status;
    }

    const bool all_views = false;
    const bool force_refresh = true;
    view.refresh(all_views, force_refresh);

    return MStatus::kSuccess;
}

}  // namespace render
}  // namespace mmsolver
