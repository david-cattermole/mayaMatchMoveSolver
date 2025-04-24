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
 * Logging functions.
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_CONSOLE_LOGGING_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_CONSOLE_LOGGING_H

#include "adjust_data.h"
#include "adjust_results.h"

namespace mmsolver {

void console_log_solver_iteration_pre_solve(const LogLevel log_level,
                                            const bool is_normal_call,
                                            const bool is_jacobian_call,
                                            const bool do_calc_jacobian,
                                            const int32_t iter_num,
                                            const int32_t func_eval_num,
                                            const int32_t jac_iter_num);

void console_log_solver_iteration_post_solve(
    const LogLevel log_level, const bool is_normal_call,
    const bool is_jacobian_call, const bool do_calc_jacobian,
    const double error_avg, const double error_min, const double error_max);

void console_log_solver_results(const SolverResult &solverResult,
                                const SolverTimer &timer);

void console_log_solver_timer(const SolverTimer &timer,
                              const uint32_t total_iteration_count);

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_CONSOLE_LOGGING_H
