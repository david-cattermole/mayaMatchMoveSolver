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
 * Command for running the main solver.
 *
 * 'mmSolver2' is the second iteration of the 'mmSolver' solving
 * command, with a cleaner syntax.
 */

#include "MMSolver2Cmd.h"

// STL
#include <algorithm>
#include <cassert>
#include <cmath>
#include <cstdlib>

// Maya
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MStreamUtils.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/adjust/adjust_defines.h"
#include "mmSolver/cmd/common_arg_flags.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

MMSolver2Cmd::~MMSolver2Cmd() {}

void *MMSolver2Cmd::creator() { return new MMSolver2Cmd(); }

MString MMSolver2Cmd::cmdName() { return MString("mmSolver"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMSolver2Cmd::hasSyntax() const { return true; }

bool MMSolver2Cmd::isUndoable() const { return true; }

/*
 * Add flags to the command syntax
 */
MSyntax MMSolver2Cmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    createSolveObjectSyntax(syntax);
    createSolveFramesSyntax(syntax);
    createSolveInfoSyntax(syntax);
    createSolveLogSyntax(syntax);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMSolver2Cmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveObjectArguments(argData, m_cameraList, m_markerList,
                                       m_bundleList, m_attrList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveFramesArguments(argData, m_frameList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveInfoArguments(
        argData, m_solverOptions.iterMax, m_solverOptions.tau,
        m_solverOptions.eps1, m_solverOptions.eps2, m_solverOptions.eps3,
        m_solverOptions.delta, m_solverOptions.autoDiffType,
        m_solverOptions.autoParamScale, m_solverOptions.robustLossType,
        m_solverOptions.robustLossScale, m_solverOptions.solverType,
        m_solverOptions.sceneGraphMode, m_solverOptions.timeEvalMode,
        m_solverOptions.acceptOnlyBetter, m_solverOptions.frameSolveMode,
        m_solverOptions.solverSupportsAutoDiffForward,
        m_solverOptions.solverSupportsAutoDiffCentral,
        m_solverOptions.solverSupportsParameterBounds,
        m_solverOptions.solverSupportsRobustLoss,
        m_solverOptions.removeUnusedMarkers,
        m_solverOptions.removeUnusedAttributes, m_solverOptions.imageWidth);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveLogArguments(argData, m_printStatsList, m_logLevel);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus MMSolver2Cmd::doIt(const MArgList &args) {
    //
    //  Description:
    //    implements the MEL mmSolver command.
    //
    //  Arguments:
    //    argList - the argument list that was passes to the command from MEL
    //
    //  Return Value:
    //    MS::kSuccess - command succeeded
    //    MS::kFailure - command failed (returning this value will cause the
    //                     MEL script that is being run to terminate unless the
    //                     error is caught using a "catch" statement.
    //
    MStatus status = MStatus::kSuccess;

    // Mouse cursor spinning...
    // MGlobal::executeCommand("waitCursor -state on;");

    // Read all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    assert(m_frameList.length() > 0);

    // Don't store each individual edits, just store the combination
    // of edits.
    m_curveChange.setInteractive(true);

    MStringArray outResult;
    bool ret =
        solve_v2(m_solverOptions, m_cameraList, m_markerList, m_bundleList,
                 m_attrList, m_frameList, m_dgmod, m_curveChange, m_computation,
                 m_printStatsList, m_logLevel, outResult);

    MMSolver2Cmd::setResult(outResult);
    if (ret == false) {
        MStreamUtils::stdErrorStream()
            << "WARNING: mmSolver: Solver returned false!" << '\n';
    }

    return status;
}

MStatus MMSolver2Cmd::redoIt() {
    //
    //  Description:
    //    Implements redo for the MEL mmSolver command.
    //
    //    This method is called when the user has undone a command of this type
    //    and then redoes it.  No arguments are passed in as all of the
    //    necessary information is cached by the doIt method.
    //
    //  Return Value:
    //    MS::kSuccess - command succeeded
    //    MS::kFailure - redoIt failed.  this is a serious problem that will
    //                     likely cause the undo queue to be purged
    //
    MStatus status;
    m_dgmod.doIt();
    m_curveChange.redoIt();
    return status;
}

MStatus MMSolver2Cmd::undoIt() {
    //
    //  Description:
    //    implements undo for the MEL mmSolver command.
    //
    //    This method is called to undo a previous command of this type.  The
    //    system should be returned to the exact state that it was it previous
    //    to this command being executed.  That includes the selection state.
    //
    //  Return Value:
    //    MS::kSuccess - command succeeded
    //    MS::kFailure - redoIt failed.  this is a serious problem that will
    //                     likely cause the undo queue to be purged
    //
    MStatus status;
    m_curveChange.undoIt();
    m_dgmod.undoIt();
    return status;
}

}  // namespace mmsolver
