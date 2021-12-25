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
 * Command for running mmSolver.
 */

// Internal
#include <MMSolverCmd.h>
#include <core/bundleAdjust_defines.h>
#include <core/bundleAdjust_data.h>
#include <mayaUtils.h>
#include <mmscenegraph/mmscenegraph.h>

// STL
#include <cmath>
#include <cassert>
#include <cstdlib>
#include <algorithm>

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MStreamUtils.h>

// Internal Objects
#include <commonArgFlags.h>
#include <Attr.h>
#include <Marker.h>
#include <Bundle.h>
#include <Camera.h>


MMSolverCmd::~MMSolverCmd() {}

void *MMSolverCmd::creator() {
    return new MMSolverCmd();
}

MString MMSolverCmd::cmdName() {
    return MString("mmSolver");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMSolverCmd::hasSyntax() const {
    return true;
}

bool MMSolverCmd::isUndoable() const {
    return true;
}


void createSolveLogSyntax(MSyntax &syntax) {
    // TODO: Deprecate 'verbose' flag, replace with 'log level' flag.
    syntax.addFlag(VERBOSE_FLAG, VERBOSE_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(DEBUG_FILE_FLAG, DEBUG_FILE_FLAG_LONG,
                   MSyntax::kString);
    syntax.addFlag(PRINT_STATS_FLAG, PRINT_STATS_FLAG_LONG,
                   MSyntax::kString);
    syntax.makeFlagMultiUse(PRINT_STATS_FLAG);
}


void createSolveInfoSyntax(MSyntax &syntax) {
    syntax.addFlag(TAU_FLAG, TAU_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(EPSILON1_FLAG, EPSILON1_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(EPSILON2_FLAG, EPSILON2_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(EPSILON3_FLAG, EPSILON3_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(DELTA_FLAG, DELTA_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(AUTO_DIFF_TYPE_FLAG, AUTO_DIFF_TYPE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(AUTO_PARAM_SCALE_FLAG, AUTO_PARAM_SCALE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ROBUST_LOSS_TYPE_FLAG, ROBUST_LOSS_TYPE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ROBUST_LOSS_SCALE_FLAG, ROBUST_LOSS_SCALE_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(SOLVER_TYPE_FLAG, SOLVER_TYPE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ITERATIONS_FLAG, ITERATIONS_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ACCEPT_ONLY_BETTER_FLAG, ACCEPT_ONLY_BETTER_FLAG_LONG,
                   MSyntax::kBoolean);

    syntax.addFlag(REMOVE_UNUSED_MARKERS_FLAG, REMOVE_UNUSED_MARKERS_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(REMOVE_UNUSED_ATTRIBUTES_FLAG, REMOVE_UNUSED_ATTRIBUTES_FLAG_LONG,
                   MSyntax::kBoolean);

    syntax.addFlag(TIME_EVAL_MODE_FLAG, TIME_EVAL_MODE_FLAG_LONG,
                   MSyntax::kUnsigned);
}

/*
 * Add flags to the command syntax
 */
MSyntax MMSolverCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    createSolveObjectSyntax(syntax);
    createAttributeDetailsSyntax(syntax);
    createSolveFramesSyntax(syntax);
    createSolveInfoSyntax(syntax);
    createSolveLogSyntax(syntax);

    return syntax;
}

MStatus parseSolveLogArguments(const MArgDatabase &argData,
                               MString &out_debugFile,
                               MStringArray &out_printStatsList,
                               bool &out_verbose) {
    MStatus status = MStatus::kSuccess;

    // Get 'Verbose'
    // TODO: Deprecate 'verbose' flag, replace with 'log level' flag.
    out_verbose = VERBOSE_DEFAULT_VALUE;
    if (argData.isFlagSet(VERBOSE_FLAG)) {
        status = argData.getFlagArgument(VERBOSE_FLAG, 0, out_verbose);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Debug File'
    out_debugFile = DEBUG_FILE_DEFAULT_VALUE;
    if (argData.isFlagSet(DEBUG_FILE_FLAG)) {
        status = argData.getFlagArgument(DEBUG_FILE_FLAG, 0, out_debugFile);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Print Statistics'
    unsigned int printStatsNum = argData.numberOfFlagUses(PRINT_STATS_FLAG);
    out_printStatsList.clear();
    for (unsigned int i = 0; i < printStatsNum; ++i) {
        MArgList printStatsArgs;
        status = argData.getFlagArgumentList(PRINT_STATS_FLAG, i, printStatsArgs);
        if (status == MStatus::kSuccess) {
            MString printStatsArg = "";
            for (unsigned j = 0; j < printStatsArgs.length(); ++j) {
                printStatsArg = printStatsArgs.asString(j, &status);
                CHECK_MSTATUS_AND_RETURN_IT(status);
                out_printStatsList.append(printStatsArg);
            }
        }
    }

    return status;
}


MStatus parseSolveInfoArguments(const MArgDatabase &argData,
                                unsigned int &out_iterations,
                                double &out_tau,
                                double &out_epsilon1,
                                double &out_epsilon2,
                                double &out_epsilon3,
                                double &out_delta,
                                int &out_autoDiffType,
                                int &out_autoParamScale,
                                int &out_robustLossType,
                                double &out_robustLossScale,
                                int &out_solverType,
                                int &out_timeEvalMode,
                                bool &out_acceptOnlyBetter,
                                bool &out_supportAutoDiffForward,
                                bool &out_supportAutoDiffCentral,
                                bool &out_supportParameterBounds,
                                bool &out_supportRobustLoss,
                                bool &out_removeUnusedMarkers,
                                bool &out_removeUnusedAttributes) {
    MStatus status = MStatus::kSuccess;

    // Get 'Accept Only Better'
    out_acceptOnlyBetter = ACCEPT_ONLY_BETTER_DEFAULT_VALUE;
    if (argData.isFlagSet(ACCEPT_ONLY_BETTER_FLAG)) {
        status = argData.getFlagArgument(ACCEPT_ONLY_BETTER_FLAG, 0, out_acceptOnlyBetter);
        CHECK_MSTATUS(status);
    }

    // Get 'Solver Type'
    SolverTypePair solverType = getSolverTypeDefault();
    out_solverType = solverType.first;
    if (argData.isFlagSet(SOLVER_TYPE_FLAG)) {
        status = argData.getFlagArgument(SOLVER_TYPE_FLAG, 0, out_solverType);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Time Evaluation Mode'
    out_timeEvalMode = TIME_EVAL_MODE_DEFAULT_VALUE;
    if (argData.isFlagSet(TIME_EVAL_MODE_FLAG)) {
        status = argData.getFlagArgument(TIME_EVAL_MODE_FLAG, 0, out_timeEvalMode);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Set defaults based on solver type chosen.
    if (out_solverType == SOLVER_TYPE_CMINPACK_LMDIF) {
        out_iterations = CMINPACK_LMDIF_ITERATIONS_DEFAULT_VALUE;
        out_tau = CMINPACK_LMDIF_TAU_DEFAULT_VALUE;
        out_epsilon1 = CMINPACK_LMDIF_EPSILON1_DEFAULT_VALUE;
        out_epsilon2 = CMINPACK_LMDIF_EPSILON2_DEFAULT_VALUE;
        out_epsilon3 = CMINPACK_LMDIF_EPSILON3_DEFAULT_VALUE;
        out_delta = CMINPACK_LMDIF_DELTA_DEFAULT_VALUE;
        out_autoDiffType = CMINPACK_LMDIF_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        out_autoParamScale = CMINPACK_LMDIF_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        out_robustLossType = CMINPACK_LMDIF_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        out_robustLossScale = CMINPACK_LMDIF_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        out_supportAutoDiffForward = CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        out_supportAutoDiffCentral = CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        out_supportParameterBounds = CMINPACK_LMDIF_SUPPORT_PARAMETER_BOUNDS_VALUE;
        out_supportRobustLoss = CMINPACK_LMDIF_SUPPORT_ROBUST_LOSS_VALUE;
    } else if (out_solverType == SOLVER_TYPE_CMINPACK_LMDER) {
        out_iterations = CMINPACK_LMDER_ITERATIONS_DEFAULT_VALUE;
        out_tau = CMINPACK_LMDER_TAU_DEFAULT_VALUE;
        out_epsilon1 = CMINPACK_LMDER_EPSILON1_DEFAULT_VALUE;
        out_epsilon2 = CMINPACK_LMDER_EPSILON2_DEFAULT_VALUE;
        out_epsilon3 = CMINPACK_LMDER_EPSILON3_DEFAULT_VALUE;
        out_delta = CMINPACK_LMDER_DELTA_DEFAULT_VALUE;
        out_autoDiffType = CMINPACK_LMDER_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        out_autoParamScale = CMINPACK_LMDER_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        out_robustLossType = CMINPACK_LMDER_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        out_robustLossScale = CMINPACK_LMDER_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        out_supportAutoDiffForward = CMINPACK_LMDER_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        out_supportAutoDiffCentral = CMINPACK_LMDER_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        out_supportParameterBounds = CMINPACK_LMDER_SUPPORT_PARAMETER_BOUNDS_VALUE;
        out_supportRobustLoss = CMINPACK_LMDER_SUPPORT_ROBUST_LOSS_VALUE;
    } else if (out_solverType == SOLVER_TYPE_LEVMAR) {
        out_iterations = LEVMAR_ITERATIONS_DEFAULT_VALUE;
        out_tau = LEVMAR_TAU_DEFAULT_VALUE;
        out_epsilon1 = LEVMAR_EPSILON1_DEFAULT_VALUE;
        out_epsilon2 = LEVMAR_EPSILON2_DEFAULT_VALUE;
        out_epsilon3 = LEVMAR_EPSILON3_DEFAULT_VALUE;
        out_delta = LEVMAR_DELTA_DEFAULT_VALUE;
        out_autoDiffType = LEVMAR_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        out_autoParamScale = LEVMAR_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        out_robustLossType = LEVMAR_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        out_robustLossScale = LEVMAR_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        out_supportAutoDiffForward = LEVMAR_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        out_supportAutoDiffCentral = LEVMAR_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        out_supportParameterBounds = LEVMAR_SUPPORT_PARAMETER_BOUNDS_VALUE;
        out_supportRobustLoss = LEVMAR_SUPPORT_ROBUST_LOSS_VALUE;
    } else {
        ERR("Solver Type is invalid. "
            << "Value may be 0 or 1 (0 == levmar, 1 == cminpack_lm);"
            << "value=" << out_solverType);
        status = MS::kFailure;
        status.perror("Solver Type is invalid. Value may be 0 or 1 (0 == levmar, 1 == cminpack_lm).");
        return status;
    }

    // Get 'Iterations'
    if (argData.isFlagSet(ITERATIONS_FLAG)) {
        status = argData.getFlagArgument(ITERATIONS_FLAG, 0, out_iterations);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Tau'
    if (argData.isFlagSet(TAU_FLAG)) {
        status = argData.getFlagArgument(TAU_FLAG, 0, out_tau);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    out_tau = std::max(0.0, out_tau);
    out_tau = std::min(out_tau, 1.0);
    assert((out_tau >= 0.0) && (out_tau <= 1.0));

    // Get 'Epsilon1'
    if (argData.isFlagSet(EPSILON1_FLAG)) {
        status = argData.getFlagArgument(EPSILON1_FLAG, 0, out_epsilon1);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Epsilon2'
    if (argData.isFlagSet(EPSILON2_FLAG)) {
        status = argData.getFlagArgument(EPSILON2_FLAG, 0, out_epsilon2);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Epsilon3'
    if (argData.isFlagSet(EPSILON3_FLAG)) {
        status = argData.getFlagArgument(EPSILON3_FLAG, 0, out_epsilon3);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Delta'
    if (argData.isFlagSet(DELTA_FLAG)) {
        status = argData.getFlagArgument(DELTA_FLAG, 0, out_delta);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Auto Differencing Type'
    if (argData.isFlagSet(AUTO_DIFF_TYPE_FLAG)) {
        status = argData.getFlagArgument(AUTO_DIFF_TYPE_FLAG, 0, out_autoDiffType);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Auto Parameter Scaling'
    if (argData.isFlagSet(AUTO_PARAM_SCALE_FLAG)) {
        status = argData.getFlagArgument(AUTO_PARAM_SCALE_FLAG, 0, out_autoParamScale);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Robust Loss Type'
    if (argData.isFlagSet(ROBUST_LOSS_TYPE_FLAG)) {
        status = argData.getFlagArgument(ROBUST_LOSS_TYPE_FLAG, 0, out_robustLossType);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Robust Loss Scale'
    if (argData.isFlagSet(ROBUST_LOSS_SCALE_FLAG)) {
        status = argData.getFlagArgument(ROBUST_LOSS_SCALE_FLAG, 0, out_robustLossScale);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Remove Unused Markers'
    out_removeUnusedMarkers = REMOVE_UNUSED_MARKERS_DEFAULT_VALUE;
    if (argData.isFlagSet(REMOVE_UNUSED_MARKERS_FLAG)) {
        status = argData.getFlagArgument(REMOVE_UNUSED_MARKERS_FLAG, 0, out_removeUnusedMarkers);
        CHECK_MSTATUS(status);
    }

    // Get 'Remove Unused Attributes'
    out_removeUnusedAttributes = REMOVE_UNUSED_ATTRIBUTES_DEFAULT_VALUE;
    if (argData.isFlagSet(REMOVE_UNUSED_ATTRIBUTES_FLAG)) {
        status = argData.getFlagArgument(REMOVE_UNUSED_ATTRIBUTES_FLAG, 0, out_removeUnusedAttributes);
        CHECK_MSTATUS(status);
    }

    return status;
}

/*
 * Parse command line arguments
 */
MStatus MMSolverCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveObjectArguments(
        argData,
        m_cameraList,
        m_markerList,
        m_bundleList,
        m_attrList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseAttributeDetailsArguments(
        argData,
        m_attrList,
        m_stiffAttrsList,
        m_smoothAttrsList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveFramesArguments(
        argData,
        m_frameList);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveInfoArguments(
        argData,
        m_iterations,
        m_tau,
        m_epsilon1,
        m_epsilon2,
        m_epsilon3,
        m_delta,
        m_autoDiffType,
        m_autoParamScale,
        m_robustLossType,
        m_robustLossScale,
        m_solverType,
        m_timeEvalMode,
        m_acceptOnlyBetter,
        m_supportAutoDiffForward,
        m_supportAutoDiffCentral,
        m_supportParameterBounds,
        m_supportRobustLoss,
        m_removeUnusedMarkers,
        m_removeUnusedAttributes);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveLogArguments(
        argData,
        m_debugFile,
        m_printStatsList,
        m_verbose);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}


MStatus MMSolverCmd::doIt(const MArgList &args) {
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

    mmscenegraph::foo(1);
    mmscenegraph::foo(2);
    mmscenegraph::foo(3);
    mmscenegraph::foo(42);
    auto cpp_string_1 = mmscenegraph::foobar(1);
    auto cpp_string_2 = mmscenegraph::foobar(2);
    auto cpp_string_3 = mmscenegraph::foobar(3);
    auto cpp_string_42 = mmscenegraph::foobar(42);
    MStreamUtils::stdErrorStream()
        << "mmSolver: Rust result: "
        << cpp_string_1
        << '\n';
    MStreamUtils::stdErrorStream()
        << "mmSolver: Rust result: "
        << cpp_string_2
        << '\n';
    MStreamUtils::stdErrorStream()
        << "mmSolver: Rust result: "
        << cpp_string_3
        << '\n';
    MStreamUtils::stdErrorStream()
        << "mmSolver: Rust result: "
        << cpp_string_42
        << '\n';

    auto cam = mmscenegraph::make_camera(24.0, 35.0);
    MStreamUtils::stdErrorStream()
        << "MM camera:"
        << " width=" << cam.sensor_width_mm
        << " focal=" << cam.focal_length_mm
        << '\n';

    // Mouse cursor spinning...
    // MGlobal::executeCommand("waitCursor -state on;");

    // Read all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    assert(m_frameList.length() > 0);

    // Don't store each individual edits, just store the combination
    // of edits.
    m_curveChange.setInteractive(true);

    SolverOptions solverOptions;
    solverOptions.iterMax = m_iterations;
    solverOptions.tau = m_tau;
    solverOptions.eps1 = m_epsilon1;
    solverOptions.eps2 = m_epsilon2;
    solverOptions.eps3 = m_epsilon3;
    solverOptions.delta = m_delta;
    solverOptions.autoDiffType = m_autoDiffType;
    solverOptions.autoParamScale = m_autoParamScale;
    solverOptions.robustLossType = m_robustLossType;
    solverOptions.robustLossScale = m_robustLossScale;
    solverOptions.solverType = m_solverType;
    solverOptions.timeEvalMode = m_timeEvalMode;
    solverOptions.acceptOnlyBetter = m_acceptOnlyBetter;
    solverOptions.solverSupportsAutoDiffForward = m_supportAutoDiffForward;
    solverOptions.solverSupportsAutoDiffCentral = m_supportAutoDiffCentral;
    solverOptions.solverSupportsParameterBounds = m_supportParameterBounds;
    solverOptions.solverSupportsRobustLoss = m_supportRobustLoss;
    solverOptions.removeUnusedMarkers = m_removeUnusedMarkers;
    solverOptions.removeUnusedAttributes = m_removeUnusedAttributes;

    MStringArray outResult;
    bool ret = solve(
            solverOptions,
            m_cameraList,
            m_markerList,
            m_bundleList,
            m_attrList,
            m_frameList,
            m_stiffAttrsList,
            m_smoothAttrsList,
            m_dgmod,
            m_curveChange,
            m_computation,
            m_debugFile,
            m_printStatsList,
            m_verbose,
            outResult
    );

    MMSolverCmd::setResult(outResult);
    if (ret == false) {
        MStreamUtils::stdErrorStream()
            << "WARNING: mmSolver: Solver returned false!"
            << '\n';
    }

    // Mouse cursor back to normal.
    // MGlobal::executeCommand("waitCursor -state off;");
    return status;
}

MStatus MMSolverCmd::redoIt() {
//
//  Description:
//    Implements redo for the MEL mmSolver command.
//
//    This method is called when the user has undone a command of this type
//    and then redoes it.  No arguments are passed in as all of the necessary
//    information is cached by the doIt method.
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

MStatus MMSolverCmd::undoIt() {
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
