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
 * mmSolver Renderer command.
 *
 * This command is used to query and edit values for the mmSolver
 * Renderer.
 *
 * Create a 'mmRenderer' node used to store the attributes for the
 * renderer in the scene.
 */

#ifndef MAYA_MM_SOLVER_MM_RENDERER_CMD_H
#define MAYA_MM_SOLVER_MM_RENDERER_CMD_H

#include <maya/MPxCommand.h>

namespace mmsolver {
namespace renderer {

/*
 * Command arguments and command name
 */
#define MM_RENDERER_SWIRL_FLAG        "-s"
#define MM_RENDERER_SWIRL_FLAG_LONG    "-swirl"

#define MM_RENDERER_FISH_EYE_FLAG        "-fe"
#define MM_RENDERER_FISH_EYE_FLAG_LONG    "-fishEye"

#define MM_RENDERER_EDGE_DETECT_FLAG        "-ed"
#define MM_RENDERER_EDGE_DETECT_FLAG_LONG    "-edgeDetect"

#define MM_RENDERER_BLEND_FLAG        "-bl"
#define MM_RENDERER_BLEND_FLAG_LONG    "-blend"

/*
 * MM Renderer command.
 */
class MMRendererCmd : public MPxCommand {
public:
    MMRendererCmd();

    ~MMRendererCmd() override;

    MStatus doIt(const MArgList &args) override;

    static MSyntax newSyntax();

    static void *creator();

    static MString cmdName();

private:
    bool m_fishEye;
    bool m_swirl;
    bool m_edgeDetect;
    double m_blend;
};

} // namespace renderer
} // namespace mmsolver

#endif //MAYA_MM_SOLVER_MM_RENDERER_CMD_H
