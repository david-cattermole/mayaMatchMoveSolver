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
 */

#include "arg_flags_solve_log.h"

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MArgParser.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// Internal Objects
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

void createSolveLogSyntax_v1(MSyntax &syntax) {
    syntax.addFlag(LOG_LEVEL_FLAG, LOG_LEVEL_FLAG_LONG, MSyntax::kUnsigned);
    syntax.addFlag(VERBOSE_FLAG, VERBOSE_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(PRINT_STATS_FLAG, PRINT_STATS_FLAG_LONG, MSyntax::kString);
    syntax.makeFlagMultiUse(PRINT_STATS_FLAG);
}

void createSolveLogSyntax_v2(MSyntax &syntax) {
    syntax.addFlag(LOG_LEVEL_FLAG, LOG_LEVEL_FLAG_LONG, MSyntax::kUnsigned);
    syntax.addFlag(PRINT_STATS_FLAG, PRINT_STATS_FLAG_LONG, MSyntax::kString);
    syntax.makeFlagMultiUse(PRINT_STATS_FLAG);
    syntax.addFlag(RESULTS_NODE_FLAG, RESULTS_NODE_FLAG_LONG, MSyntax::kString);
    syntax.addFlag(SET_MARKER_DEVIATION_ATTRS_FLAG,
                   SET_MARKER_DEVIATION_ATTRS_FLAG_LONG, MSyntax::kBoolean);
}

MStatus parseSolveLogArguments_logLevel(const MArgDatabase &argData,
                                        LogLevel &out_logLevel) {
    MStatus status = MStatus::kSuccess;
    if (argData.isFlagSet(LOG_LEVEL_FLAG)) {
        int logLevelNum = static_cast<int>(LOG_LEVEL_DEFAULT_VALUE);
        status = argData.getFlagArgument(LOG_LEVEL_FLAG, 0, logLevelNum);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        out_logLevel = static_cast<LogLevel>(logLevelNum);
    }
    return status;
}

MStatus parseSolveLogArguments_printStats(const MArgDatabase &argData,
                                          MStringArray &out_printStatsList) {
    MStatus status = MStatus::kSuccess;
    unsigned int printStatsNum = argData.numberOfFlagUses(PRINT_STATS_FLAG);
    out_printStatsList.clear();
    for (auto i = 0; i < printStatsNum; ++i) {
        MArgList printStatsArgs;
        status =
            argData.getFlagArgumentList(PRINT_STATS_FLAG, i, printStatsArgs);
        if (status == MStatus::kSuccess) {
            MString printStatsArg = "";
            for (auto j = 0; j < printStatsArgs.length(); ++j) {
                printStatsArg = printStatsArgs.asString(j, &status);
                MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
                out_printStatsList.append(printStatsArg);
            }
        }
    }
    return status;
}

MStatus parseSolveLogArguments_v1(const MArgDatabase &argData,
                                  MStringArray &out_printStatsList,
                                  LogLevel &out_logLevel) {
    // 'Log Level' can be overwritten by the (deprecated) verbose
    // flag.
    out_logLevel = LOG_LEVEL_DEFAULT_VALUE;

    // Get 'Verbose' flag. This is deprecated, but kept for backwards
    // compatibility.
    MStatus status = MS::kSuccess;
    if (argData.isFlagSet(VERBOSE_FLAG)) {
        bool verbose = VERBOSE_DEFAULT_VALUE;
        status = argData.getFlagArgument(VERBOSE_FLAG, 0, verbose);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        if (verbose) {
            out_logLevel = LogLevel::kVerbose;
        } else {
            out_logLevel = LogLevel::kInfo;
        }
    }

    // Get 'Log Level'
    status = parseSolveLogArguments_logLevel(argData, out_logLevel);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get 'Print Statistics'
    status = parseSolveLogArguments_printStats(argData, out_printStatsList);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

MStatus parseSolveLogArguments_v2(const MArgDatabase &argData,
                                  MStringArray &out_printStatsList,
                                  LogLevel &out_logLevel,
                                  MObject &out_resultsNodeObject,
                                  bool &out_setMarkerDeviationAttrs) {
    // Get 'Results Node'
    MStatus status = MS::kSuccess;
    if (argData.isFlagSet(RESULTS_NODE_FLAG)) {
        MString node_name;
        status = argData.getFlagArgument(RESULTS_NODE_FLAG, 0, node_name);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
        status = getAsObject(node_name, out_resultsNodeObject);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Set Marker Deviation Attrs' flag.
    out_setMarkerDeviationAttrs = SET_MARKER_DEVIATION_ATTRS_DEFAULT_VALUE;
    if (argData.isFlagSet(SET_MARKER_DEVIATION_ATTRS_FLAG)) {
        status = argData.getFlagArgument(SET_MARKER_DEVIATION_ATTRS_FLAG, 0,
                                         out_setMarkerDeviationAttrs);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Log Level'
    out_logLevel = LOG_LEVEL_DEFAULT_VALUE;
    status = parseSolveLogArguments_logLevel(argData, out_logLevel);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get 'Print Statistics'
    status = parseSolveLogArguments_printStats(argData, out_printStatsList);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

}  // namespace mmsolver
