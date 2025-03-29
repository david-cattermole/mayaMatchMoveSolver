/*
 * Copyright (C) 2018, 2019, 2025 David Cattermole.
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

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_CERES_LMDER_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_CERES_LMDER_H

// STL
#include <vector>

// MM Solver
#include "adjust_base.h"
#include "adjust_results.h"
#include "adjust_solveFunc.h"

namespace mmsolver {

bool solve_3d_ceres_lmder(SolverOptions &solverOptions, int numberOfParameters,
                          int numberOfErrors, std::vector<double> &paramList,
                          std::vector<double> &errorList,
                          std::vector<double> &paramWeightList,
                          SolverData &userData, SolverResult &solveResult);

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_CERES_LMDER_H
