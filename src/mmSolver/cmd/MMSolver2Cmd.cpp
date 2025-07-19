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
 * 'mmSolver_v2' is the second iteration of the 'mmSolver' solving
 * command, with a cleaner syntax.
 */

#include "MMSolver2Cmd.h"

// Maya
#include <maya/MStreamUtils.h>
#include <maya/MString.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/adjust/adjust_results_setMarkerData.h"
#include "mmSolver/adjust/adjust_results_setSolveData.h"
#include "mmSolver/cmd/common_arg_flags.h"
#include "mmSolver/core/frame_list.h"
#include "mmSolver/utilities/assert_utils.h"

namespace mmsolver {

MMSolver2Cmd::~MMSolver2Cmd() {}

void *MMSolver2Cmd::creator() { return new MMSolver2Cmd(); }

MString MMSolver2Cmd::cmdName() { return MString("mmSolver_v2"); }

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
    createSolveInfoSyntax_v2(syntax);
    createSolveLogSyntax_v2(syntax);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMSolver2Cmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveObjectArguments(argData, m_cameraList, m_markerList,
                                       m_bundleList, m_attrList);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveFramesArguments(argData, m_frameList);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveInfoArguments_v2(
        argData, m_solverOptions.iterMax, m_solverOptions.tau,
        m_solverOptions.function_tolerance, m_solverOptions.parameter_tolerance,
        m_solverOptions.gradient_tolerance, m_solverOptions.delta,
        m_solverOptions.autoDiffType, m_solverOptions.autoParamScale,
        m_solverOptions.robustLossType, m_solverOptions.robustLossScale,
        m_solverOptions.solverType, m_solverOptions.sceneGraphMode,
        m_solverOptions.timeEvalMode, m_solverOptions.acceptOnlyBetter,
        m_solverOptions.frameSolveMode,
        m_solverOptions.solverSupportsAutoDiffForward,
        m_solverOptions.solverSupportsAutoDiffCentral,
        m_solverOptions.solverSupportsParameterBounds,
        m_solverOptions.solverSupportsRobustLoss, m_solverOptions.imageWidth);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveLogArguments_v2(argData, m_printStatsList, m_logLevel,
                                       m_resultsNodeObject,
                                       m_setMarkerDeviationAttrs);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus MMSolver2Cmd::doIt(const MArgList &args) {
    //
    //  Description:
    //    implements the MEL mmSolver_v2 command.
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

    // Mouse cursor spinning...
    // MGlobal::executeCommand("waitCursor -state on;");

    // Read all the flag arguments.
    MStatus status = parseArgs(args);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    MMSOLVER_ASSERT(
        !m_frameList.is_empty(),
        "We must solve at least one frame, otherwise there's no point.");

    // Don't store each individual edits, just store the combination
    // of edits.
    m_curveChange.setInteractive(true);

    const bool ret =
        solve_v2(m_solverOptions, m_cameraList, m_markerList, m_bundleList,
                 m_attrList, m_frameList, m_dgmod, m_curveChange, m_computation,
                 m_printStatsList, m_logLevel, m_cmdResult);

    // Set the solve results, using m_dgmod and m_curveChange, so that
    // the values can be reverted if the user undoes a 'mmSolver_v2'
    // command.
    if (!m_resultsNodeObject.isNull()) {
        status = setCommandResultDataOnNode(m_cmdResult, m_cmdResult.printStats,
                                            m_resultsNodeObject, m_dgmod,
                                            m_curveChange);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (m_setMarkerDeviationAttrs) {
        status = setErrorMetricsResultDataOnMarkers(
            m_cmdResult.errorMetricsResult, m_markerList, m_dgmod,
            m_curveChange);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    MMSolver2Cmd::setResult(ret);
    if (!ret) {
        MStreamUtils::stdErrorStream()
            << "WARNING: mmSolver_v2: Solver returned false!\n";
    }
    if (status != MS::kSuccess) {
        MStreamUtils::stdErrorStream()
            << "WARNING: mmSolver_v2: Solver status is not success!\n";
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
    MStatus status = MS::kSuccess;
    m_dgmod.doIt();
    m_curveChange.redoIt();
    return status;
}

MStatus MMSolver2Cmd::undoIt() {
    //
    //  Description:
    //    implements undo for the MEL mmSolver_v2 command.
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
    MStatus status = MS::kSuccess;
    m_curveChange.undoIt();
    m_dgmod.undoIt();
    return status;
}

}  // namespace mmsolver
