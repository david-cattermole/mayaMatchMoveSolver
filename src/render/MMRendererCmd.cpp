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

#include <maya/MSyntax.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MArgDatabase.h>
#include <maya/MGlobal.h>
#include <maya/M3dView.h>

#include "MMRendererCmd.h"
#include "RenderOverride.h"

namespace mmsolver {
namespace render {

MMRendererCmd::MMRendererCmd() :
        m_fishEye(true), m_swirl(false), m_edgeDetect(true) {
}

MMRendererCmd::~MMRendererCmd() {
}

void *MMRendererCmd::creator() {
    return (void *) (new MMRendererCmd);
}

MString MMRendererCmd::cmdName() {
    return MString("mmRenderer");
}

MSyntax MMRendererCmd::newSyntax() {
    MSyntax syntax;
    syntax.addFlag(
        MM_RENDERER_SWIRL_FLAG,
        MM_RENDERER_SWIRL_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(
        MM_RENDERER_FISH_EYE_FLAG,
        MM_RENDERER_FISH_EYE_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(
        MM_RENDERER_EDGE_DETECT_FLAG,
        MM_RENDERER_EDGE_DETECT_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(
        MM_RENDERER_WIREFRAME_ALPHA_FLAG,
        MM_RENDERER_WIREFRAME_ALPHA_FLAG_LONG, MSyntax::kDouble);
    syntax.enableQuery(true);
    return syntax;
}


MStatus MMRendererCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kFailure;

    MHWRender::MRenderer *renderer = MHWRender::MRenderer::theRenderer();
    if (!renderer) {
        MGlobal::displayError("VP2 renderer not initialized.");
        return status;
    }

    RenderOverride *override_ptr =
        (RenderOverride *) renderer->findRenderOverride(
            "mmRenderer");
    if (override_ptr == nullptr) {
        MGlobal::displayError("mmRenderer is not registered.");
        return status;
    }

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool isQuery = argData.isQuery();

    // // Swirl
    // if (argData.isFlagSet(MM_RENDERER_SWIRL_FLAG)) {
    //     int index = override_ptr->mOperations.indexOf(
    //             RenderOverride::kSwirlPassName);
    //     if (isQuery) {
    //         MPxCommand::setResult(
    //                 override_ptr->mOperations[index]->enabled());
    //     } else {
    //         argData.getFlagArgument(MM_RENDERER_SWIRL_FLAG, 0, m_swirl);
    //         override_ptr->mOperations[index]->setEnabled(m_swirl);
    //     }
    // }

    // // Fish-Eye
    // if (argData.isFlagSet(MM_RENDERER_FISH_EYE_FLAG)) {
    //     int index = override_ptr->mOperations.indexOf(
    //             RenderOverride::kFishEyePassName);
    //     if (isQuery)
    //         MPxCommand::setResult(
    //                 override_ptr->mOperations[index]->enabled());
    //     else {
    //         argData.getFlagArgument(MM_RENDERER_FISH_EYE_FLAG, 0, m_fishEye);
    //         override_ptr->mOperations[index]->setEnabled(m_fishEye);
    //     }
    // }

    // // Edge Detect.
    // if (argData.isFlagSet(MM_RENDERER_EDGE_DETECT_FLAG)) {
    //     int index = override_ptr->mOperations.indexOf(
    //             RenderOverride::kEdgeDetectPassName);
    //     if (isQuery)
    //         MPxCommand::setResult(
    //                 override_ptr->mOperations[index]->enabled());
    //     else {
    //         argData.getFlagArgument(MM_RENDERER_EDGE_DETECT_FLAG, 0,
    //                                 m_edgeDetect);
    //         override_ptr->mOperations[index]->setEnabled(m_edgeDetect);
    //     }
    // }

    // Blend
    if (argData.isFlagSet(MM_RENDERER_WIREFRAME_ALPHA_FLAG)) {
        if (isQuery) {
            m_wireframe_alpha = override_ptr->wireframeAlpha();
            MPxCommand::setResult(m_wireframe_alpha);
        } else {
            argData.getFlagArgument(MM_RENDERER_WIREFRAME_ALPHA_FLAG, 0, m_wireframe_alpha);
            override_ptr->setWireframeAlpha(m_wireframe_alpha);
        }
    }

    M3dView view = M3dView::active3dView(&status);
    if (!status) {
        MGlobal::displayWarning("Failed to find an active 3d view.");
        return status;
    }

    view.refresh(false, true);

    return MStatus::kSuccess;
}

} // namespace render
} // namespace mmsolver
