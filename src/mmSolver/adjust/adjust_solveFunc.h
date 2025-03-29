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
 * Universal solver functions, to be used by any library.
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_SOLVE_FUNC_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_SOLVE_FUNC_H

#include "adjust_data.h"

// success / failure constants.
#define SOLVE_FUNC_SUCCESS (0)
#define SOLVE_FUNC_FAILURE (-1)

namespace mmsolver {

int solveFunc(const int numberOfParameters, const int numberOfErrors,
              const double *parameters, double *errors, double *jacobian,
              void *userData);

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_SOLVE_FUNC_H
