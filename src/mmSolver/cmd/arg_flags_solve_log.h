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

#ifndef MM_SOLVER_ARG_FLAGS_SOLVE_LOG_H
#define MM_SOLVER_ARG_FLAGS_SOLVE_LOG_H

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// Internal Objects
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/utilities/debug_utils.h"

// Should the solver print out verbose information while solving?
// Deprecated. Use the 'log level' flag instead.
#define VERBOSE_FLAG "-v"
#define VERBOSE_FLAG_LONG "-verbose"
#define VERBOSE_DEFAULT_VALUE false

// How much detail does the mmSolver command print?
#define LOG_LEVEL_FLAG "-lgl"
#define LOG_LEVEL_FLAG_LONG "-logLevel"
#define LOG_LEVEL_DEFAULT_VALUE LogLevel::kInfo

// Print Statistics from the solver inputs.
#define PRINT_STATS_FLAG "-pst"
#define PRINT_STATS_FLAG_LONG "-printStatistics"

namespace mmsolver {

// Add flags for solver logging to the command syntax.
void createSolveLogSyntax(MSyntax &syntax);

// Parse arguments into solver logging.
MStatus parseSolveLogArguments(const MArgDatabase &argData,
                               MStringArray &out_printStatsList,
                               LogLevel &out_logLevel);

}  // namespace mmsolver

#endif  // MM_SOLVER_ARG_FLAGS_SOLVE_LOG_H
