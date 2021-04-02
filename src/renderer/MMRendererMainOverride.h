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
 * mmSolver Viewport Renderer override.
 *
 */

#ifndef MAYA_MM_SOLVER_MM_RENDERER_MAIN_OVERRIDE_H
#define MAYA_MM_SOLVER_MM_RENDERER_MAIN_OVERRIDE_H

#include <maya/MString.h>
#include <maya/MViewport2Renderer.h>
#include <maya/MRenderTargetManager.h>


class MMRendererMainOverride : public MHWRender::MRenderOverride {
public:
    // operation names
    static const MString kSwirlPassName;
    static const MString kFishEyePassName;
    static const MString kEdgeDetectPassName;

    MMRendererMainOverride(const MString &name);

    ~MMRendererMainOverride() override;

    MHWRender::DrawAPI supportedDrawAPIs() const override;

    // Basic setup and cleanup
    MStatus setup(const MString &destination) override;

    MStatus cleanup() override;

    // Called by Maya to determine the name in the "Renderers" menu.
    MString uiName() const override {
        return m_ui_name;
    }

protected:

    // UI name
    MString m_ui_name;

    friend class MMRendererCmd;
};

#endif //MAYA_MM_SOLVER_MM_RENDERER_MAIN_OVERRIDE_H
