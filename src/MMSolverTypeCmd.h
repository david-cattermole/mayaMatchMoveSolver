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

#ifndef MAYA_MM_SOLVER_TYPE_CMD_H
#define MAYA_MM_SOLVER_TYPE_CMD_H


// STL
#include <cmath>
#include <vector>

// Maya
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>

#include <maya/MPxCommand.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MSyntax.h>

#include <maya/MSelectionList.h>
#include <maya/MDagPath.h>
#include <maya/MDGModifier.h>
#include <maya/MDagModifier.h>
#include <maya/MFnDagNode.h>

#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>

#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MMatrix.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MDoubleArray.h>

// Internal Objects
#include <Camera.h>
#include <Marker.h>
#include <Bundle.h>
#include <Attr.h>

// Define solvers
#include <core/bundleAdjust_base.h>


// Command arguments and command name:

// List of Solver Types
#define LIST_FLAG           "-ls"
#define LIST_FLAG_LONG      "-list"

// Solver Type Name
#define NAME_FLAG           "-n"
#define NAME_FLAG_LONG      "-name"

// Solver Type Index
#define INDEX_FLAG           "-i"
#define INDEX_FLAG_LONG      "-index"

// Solver Type Default
#define DEFAULT_FLAG           "-df"
#define DEFAULT_FLAG_LONG      "-default"


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
    MStatus parseArgs( const MArgList& args );

    bool  m_default;
    bool  m_list;
    bool  m_name;
    bool  m_index;
};

#endif // MAYA_MM_SOLVER_TYPE_CMD_H
