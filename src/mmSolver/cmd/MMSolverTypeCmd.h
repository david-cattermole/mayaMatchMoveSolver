/*
 * Copyright (C) 2018, 2019 David Cattermole.
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
 * Header for mmSolverType Maya command.
 */

#ifndef MM_SOLVER_TYPE_CMD_H
#define MM_SOLVER_TYPE_CMD_H

// STL
#include <cmath>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MComputation.h>
#include <maya/MDGModifier.h>
#include <maya/MDagModifier.h>
#include <maya/MDagPath.h>
#include <maya/MDoubleArray.h>
#include <maya/MFnDagNode.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MMatrix.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MPoint.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MVector.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"

// Command arguments and command name:

// List of Solver Types
#define MM_SOLVER_TYPE_LIST_FLAG ("-ls")
#define MM_SOLVER_TYPE_LIST_FLAG_LONG ("-list")

// Solver Type Name
#define MM_SOLVER_TYPE_NAME_FLAG ("-n")
#define MM_SOLVER_TYPE_NAME_FLAG_LONG ("-name")

// Solver Type Index
#define MM_SOLVER_TYPE_INDEX_FLAG ("-idx")
#define MM_SOLVER_TYPE_INDEX_FLAG_LONG ("-index")

// Solver Type Default
#define MM_SOLVER_TYPE_DEFAULT_FLAG ("-def")
#define MM_SOLVER_TYPE_DEFAULT_FLAG_LONG ("-default")

namespace mmsolver {

class MMSolverTypeCmd : public MPxCommand {
public:
    MMSolverTypeCmd() {
        m_default = false;
        m_list = false;
        m_name = false;
        m_index = false;
    };

    virtual ~MMSolverTypeCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    bool m_default;
    bool m_list;
    bool m_name;
    bool m_index;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_TYPE_CMD_H
