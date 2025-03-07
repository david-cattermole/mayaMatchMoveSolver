/*
 * Copyright (C) 2025 David Cattermole.
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

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_CERES_BASE_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_CERES_BASE_H

// STL
#include <string>

namespace mmsolver {

// Ceres Summary Termination Types:
const std::string ceresReasons[5] = {

    // reason 0
    "Ceres CONVERGENCE",
    // Minimizer terminated because one of the convergence criterion set
    // by the user was satisfied.
    //
    // 1.  (new_cost - old_cost) < function_tolerance * old_cost;
    // 2.  max_i |gradient_i| < gradient_tolerance
    // 3.  |step|_2 <= parameter_tolerance * ( |x|_2 + parameter_tolerance)
    //
    // The user's parameter blocks will be updated with the solution.

    // reason 1
    "Ceres NO_CONVERGENCE",
    // The solver ran for maximum number of iterations or maximum amount
    // of time specified by the user, but none of the convergence
    // criterion specified by the user were met. The user's parameter
    // blocks will be updated with the solution found so far.

    // reason 2
    "Ceres FAILURE",
    // The minimizer terminated because of an error.  The user's
    // parameter blocks will not be updated.

    // reason 3
    "Ceres USER_SUCCESS",
    // Using an IterationCallback object, user code can control the
    // minimizer. The following enums indicate that the user code was
    // responsible for termination.
    //
    // Minimizer terminated successfully because a user
    // IterationCallback returned SOLVER_TERMINATE_SUCCESSFULLY.
    //
    // The user's parameter blocks will be updated with the solution.

    // reason 4
    "Ceres USER_FAILURE",
    // Minimizer terminated because because a user IterationCallback
    // returned SOLVER_ABORT.
    //
    // The user's parameter blocks will not be updated.
};

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_CERES_BASE_H
