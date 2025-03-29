/*
 * Copyright (C) 2022 David Cattermole.
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
 * Sets solve data onto Maya nodes.
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_RESULTS_SET_SOLVE_DATA_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_RESULTS_SET_SOLVE_DATA_H

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MDGModifier.h>
#include <maya/MObject.h>

// MM Solver
#include "adjust_data.h"
#include "adjust_results.h"

namespace mmsolver {

MStatus setCommandResultDataOnNode(CommandResult &results,
                                   const PrintStatOptions &printStats,
                                   MObject &node, MDGModifier &dgmod,
                                   MAnimCurveChange &curveChange);

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_RESULTS_SET_SOLVE_DATA_H
