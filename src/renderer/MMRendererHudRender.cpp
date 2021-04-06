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
#include "MMRendererHudRender.h"

#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MPoint.h>
#include <maya/MImage.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MRenderTargetManager.h>
#include <maya/MShaderManager.h>
#include <maya/MTextureManager.h>

namespace mmsolver {
namespace renderer {

MMRendererHudRender::MMRendererHudRender()
        : m_targets(nullptr),
          m_target_index(0),
          m_target_count(0) {
}

MMRendererHudRender::~MMRendererHudRender() {
    m_targets = nullptr;
}

// Called by Maya.
MHWRender::MRenderTarget *const *
MMRendererHudRender::targetOverrideList(unsigned int &listSize) {
    if (m_targets && (m_target_count > 0)) {
        listSize = m_target_count;
        return &m_targets[m_target_index];
    }
    listSize = 0;
    return nullptr;
}

bool
MMRendererHudRender::hasUIDrawables() const /*override*/ {
    return true;
}

void
MMRendererHudRender::addUIDrawables(MHWRender::MUIDrawManager &drawManager2D,
                                    const MHWRender::MFrameContext &frameContext) {
    // Start draw UI
    drawManager2D.beginDrawable();
    // Set font color
    drawManager2D.setColor(MColor(1.0f, 0.0f, 0.0f));
    // Set font size
    drawManager2D.setFontSize(MHWRender::MUIDrawManager::kDefaultFontSize);

    // Draw renderer name
    int x = 0, y = 0, w = 0, h = 0;
    frameContext.getViewportDimensions(x, y, w, h);
    drawManager2D.text(MPoint(w * 0.5f, h * 0.91f),
                       MString("mmRenderer"),
                       MHWRender::MUIDrawManager::kCenter);

    // Draw viewport information
    MString viewportInfoText("Viewport information: x= ");
    viewportInfoText += x;
    viewportInfoText += ", y= ";
    viewportInfoText += y;
    viewportInfoText += ", w= ";
    viewportInfoText += w;
    viewportInfoText += ", h= ";
    viewportInfoText += h;
    drawManager2D.text(MPoint(w * 0.5f, h * 0.885f), viewportInfoText,
                       MHWRender::MUIDrawManager::kCenter);

    // End draw UI
    drawManager2D.endDrawable();
}

} // namespace renderer
} // namespace mmsolver
