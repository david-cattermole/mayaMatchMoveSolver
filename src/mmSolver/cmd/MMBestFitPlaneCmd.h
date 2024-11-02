/*
 * Copyright (C) 2024 David Cattermole.
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
 * Header for 'mmBestFitPlane' Maya command.
 */

#ifndef MM_SOLVER_MM_BEST_FIT_PLANE_CMD_H
#define MM_SOLVER_MM_BEST_FIT_PLANE_CMD_H

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MPointArray.h>
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>

// MM SceneGraph
#include <mmscenegraph/mmscenegraph.h>

namespace mmsolver {

class MMBestFitPlaneCmd : public MPxCommand {
public:
    MMBestFitPlaneCmd(){};
    virtual ~MMBestFitPlaneCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);
    virtual bool isUndoable() const;

    static void *creator();
    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    rust::Vec<mmscenegraph::Real> m_points_xyz;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_MM_BEST_FIT_PLANE_CMD_H
