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
 * Logging functions for the solver.
 */

#include "adjust_solveFunc.h"

// Maya
#include <maya/MStreamUtils.h>

// MM Solver
#include "adjust_data.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

void log_solver_iteration_pre_solve(const LogLevel log_level,
                                    const bool is_normal_call,
                                    const bool is_jacobian_call,
                                    const bool do_calc_jacobian,
                                    const int32_t iter_num,
                                    const int32_t func_eval_num,
                                    const int32_t jac_iter_num) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_logging log_solver_iteration_pre_solve");

    if (is_normal_call) {
        if (log_level >= LOG_LEVEL_PRINT_NORMAL_ITERATIONS) {
            MStreamUtils::stdErrorStream() << "Iteration ";
            MStreamUtils::stdErrorStream()
                << std::right << std::setfill('0') << std::setw(4) << iter_num;
            MStreamUtils::stdErrorStream() << " | Eval ";
            MStreamUtils::stdErrorStream() << std::right << std::setfill('0')
                                           << std::setw(4) << func_eval_num;
        }
    } else if (is_jacobian_call && !do_calc_jacobian) {
        if (log_level >= LOG_LEVEL_PRINT_JACOBIAN_ITERATIONS) {
            MStreamUtils::stdErrorStream() << "Jacobian  ";
            MStreamUtils::stdErrorStream() << std::right << std::setfill('0')
                                           << std::setw(4) << jac_iter_num;
            MStreamUtils::stdErrorStream() << " | Eval ";
            MStreamUtils::stdErrorStream() << std::right << std::setfill('0')
                                           << std::setw(4) << func_eval_num;
            if (do_calc_jacobian) {
                MStreamUtils::stdErrorStream() << "\n";
            }
        }
    }
}

void log_solver_iteration_post_solve(
    const LogLevel log_level, const bool is_normal_call,
    const bool is_jacobian_call, const bool do_calc_jacobian,
    const double error_avg, const double error_min, const double error_max) {
    const bool verbose = false;
    MMSOLVER_MAYA_VRB("adjust_logging log_solver_iteration_post_solve");

    if (is_normal_call) {
        if (log_level >= LOG_LEVEL_PRINT_NORMAL_ITERATIONS) {
            char formatBuffer[128];
            sprintf(formatBuffer, " | error avg %8.4f   min %8.4f   max %8.4f",
                    error_avg, error_min, error_max);
            MStreamUtils::stdErrorStream() << std::string(formatBuffer) << "\n";
        }
    } else {
        if (log_level >= LOG_LEVEL_PRINT_JACOBIAN_ITERATIONS) {
            if (!do_calc_jacobian) {
                MStreamUtils::stdErrorStream() << "\n";
            }
        }
    }
}

}  // namespace mmsolver
