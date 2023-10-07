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
 * Create a 'mmSilhouetteRenderer' node used to store the attributes for the
 * renderer in the scene.
 */

#ifndef MM_SOLVER_RENDER_MM_SILHOUETTE_RENDERER_CMD_H
#define MM_SOLVER_RENDER_MM_SILHOUETTE_RENDERER_CMD_H

#include <maya/MPxCommand.h>

namespace mmsolver {
namespace render {

/*
 * MM Silhouette Renderer command.
 */
class MMRendererSilhouetteCmd : public MPxCommand {
public:
    MMRendererSilhouetteCmd();

    ~MMRendererSilhouetteCmd() override;

    MStatus doIt(const MArgList &args) override;

    static MSyntax newSyntax();

    static void *creator();

    static MString cmdName();
};

}  // namespace render
}  // namespace mmsolver

#endif  // MAYA_MM_SOLVER_RENDER_MM_SILHOUETTE_RENDERER_CMD_H
