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
 * mmSolver viewport 2.0 renderer.
 *
 * TODO:
 *
 * - Add 'MSceneRender' override.
 *
 * - Add 'MHUDRender' override.
 *
 * - Add 'MPresent' override.
 *
 * - Allow user's background color to be used. The farmilar 'Alt+B'
 *   should work as expected.
 *
 * - Add blend between wireframe on shaded or not.
 *
 * - Add edge silhouette draw mode for specific objects.
 *
 */

#include "MMRendererMainOverride.h"
#include "MMRendererQuadRender.h"
#include "MMRendererSceneRender.h"
#include "MMRendererHudRender.h"
#include "MMRendererPresentTarget.h"
#include <maya/MShaderManager.h>

const MString MMRendererMainOverride::kSwirlPassName = "mmRenderer_Swirl";
const MString MMRendererMainOverride::kFishEyePassName = "mmRenderer_FishEye";
const MString MMRendererMainOverride::kEdgeDetectPassName = "mmRenderer_EdgeDetect";

// Set up operations
MMRendererMainOverride::MMRendererMainOverride(const MString &name)
        : MRenderOverride(name), m_ui_name("mmSolver Renderer") {
    MHWRender::MRenderer *theRenderer = MHWRender::MRenderer::theRenderer();
    if (!theRenderer)
        return;

    // These are all the Maya operations needed to render the scene.
    MHWRender::MRenderer::theRenderer()->getStandardViewportOperations(
        mOperations);

    MMRendererQuadRender *swirlOp =
        new MMRendererQuadRender(kSwirlPassName, "FilterSwirl", "");
    MMRendererQuadRender *fishEyeOp =
        new MMRendererQuadRender(kFishEyePassName, "FilterFishEye", "");
    MMRendererQuadRender *edgeDetectOp =
        new MMRendererQuadRender(kEdgeDetectPassName, "FilterEdgeDetect", "");

    swirlOp->setEnabled(false); // swirl is disabled by default

    mOperations.insertAfter(
        MHWRender::MRenderOperation::kStandardSceneName, swirlOp);
    mOperations.insertAfter(kSwirlPassName, fishEyeOp);
    mOperations.insertAfter(kFishEyePassName, edgeDetectOp);
}


MMRendererMainOverride::~MMRendererMainOverride() {
}

// What type of Draw APIs are supported? All of them; OpenGL DirectX,
// etc.
MHWRender::DrawAPI MMRendererMainOverride::supportedDrawAPIs() const {
    return MHWRender::kAllDevices;
}

MStatus MMRendererMainOverride::setup(const MString &destination) {
    return MRenderOverride::setup(destination);
}

MStatus MMRendererMainOverride::cleanup() {
    return MRenderOverride::cleanup();
}
