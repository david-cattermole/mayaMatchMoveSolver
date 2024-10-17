/*
 * Copyright (C) 2018, 2019, 2022 David Cattermole.
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
 * Header for mmSolver2 Maya command.
 */

#ifndef MM_SOLVER2_CMD_H
#define MM_SOLVER2_CMD_H

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
#include "mmSolver/adjust/adjust_results.h"
#include "mmSolver/cmd/common_arg_flags.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"

namespace mmsolver {

class MMSolver2Cmd : public MPxCommand {
public:
    MMSolver2Cmd() : m_setMarkerDeviationAttrs(false){};

    virtual ~MMSolver2Cmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    virtual MStatus undoIt();

    virtual MStatus redoIt();

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    // Solver Information.
    SolverOptions m_solverOptions;

    // Solver printing.
    MStringArray m_printStatsList;
    LogLevel m_logLevel;
    CommandResult m_cmdResult;
    MObject m_resultsNodeObject;
    bool m_setMarkerDeviationAttrs;

    // Solver Objects
    CameraPtrList m_cameraList;
    MarkerPtrList m_markerList;
    BundlePtrList m_bundleList;
    AttrPtrList m_attrList;
    MTimeArray m_frameList;

    // Undo/Redo
    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
    MComputation m_computation;
};

}  // namespace mmsolver

#endif  // MM_SOLVER2_CMD_H
