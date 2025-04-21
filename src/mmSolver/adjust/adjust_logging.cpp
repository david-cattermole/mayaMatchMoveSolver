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
 * Logging functions for the solver to the terminal/Maya Output
 * Window.
 */

#include "adjust_solveFunc.h"

// Maya
#include <maya/MStreamUtils.h>

// MM Solver
#include "adjust_data.h"
#include "adjust_results.h"
#include "mmSolver/utilities/assert_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

const char *const LOG_SOLVER_RETURN_SUCCESS = "Solver returned SUCCESS    | ";
const char *const LOG_SOLVER_RETURN_FAILURE = "Solver returned FAILURE    | ";
const char *const LOG_SOLVER_ITERATION_RESIDUAL_ERROR_FORMAT =
    " | error avg %8.4f   min %8.4f   max %8.4f";
const char *const LOG_SOLVER_END_RESIDUAL_ERROR_FORMAT =
    "error avg %8.4f   min %8.4f   max %8.4f  iterations %03u  (%s evals/sec)";

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
            sprintf(formatBuffer, LOG_SOLVER_ITERATION_RESIDUAL_ERROR_FORMAT,
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

void log_solver_results(const SolverResult &solverResult,
                        const SolverTimer &timer) {
    if (solverResult.success) {
        MStreamUtils::stdErrorStream() << LOG_SOLVER_RETURN_SUCCESS;
    } else {
        MStreamUtils::stdErrorStream() << LOG_SOLVER_RETURN_FAILURE;
    }

    double seconds = mmsolver::debug::timestamp_as_seconds(
        mmsolver::debug::get_timestamp() - timer.startTimestamp);
    seconds = std::max(1e-9, seconds);
    auto evals_per_sec = static_cast<size_t>(
        static_cast<double>(solverResult.functionEvals) / seconds);
    std::string evals_per_sec_string =
        mmstring::numberToStringWithCommas(evals_per_sec);

    const auto solverResult_iterations =
        static_cast<uint32_t>(solverResult.iterations);

    const size_t buffer_size = 128;
    char formatBuffer[buffer_size];
    std::snprintf(formatBuffer, buffer_size,
                  LOG_SOLVER_END_RESIDUAL_ERROR_FORMAT, solverResult.errorAvg,
                  solverResult.errorMin, solverResult.errorMax,
                  solverResult_iterations, &evals_per_sec_string[0]);
    // Note: We use std::endl to flush the stream, and ensure an
    //  update for the user.
    MStreamUtils::stdErrorStream() << formatBuffer << std::endl;
}

void log_solver_timer(const SolverTimer &timer,
                      const uint32_t total_iteration_count) {
    static std::ostream &stream = MStreamUtils::stdErrorStream();
    timer.solveBenchTimer.print(stream, "Solve Time", 1);
    timer.funcBenchTimer.print(stream, "Func Time", 1);
    timer.jacBenchTimer.print(stream, "Jacobian Time", 1);
    timer.paramBenchTimer.print(stream, "Param Time", total_iteration_count);
    timer.errorBenchTimer.print(stream, "Error Time", total_iteration_count);
    timer.funcBenchTimer.print(stream, "Func Time", total_iteration_count);

    timer.solveBenchTicks.print(stream, "Solve Ticks", 1);
    timer.funcBenchTicks.print(stream, "Func Ticks", 1);
    timer.jacBenchTicks.print(stream, "Jacobian Ticks", 1);
    timer.paramBenchTicks.print(stream, "Param Ticks", total_iteration_count);
    timer.errorBenchTicks.print(stream, "Error Ticks", total_iteration_count);
    timer.funcBenchTicks.print(stream, "Func Ticks", total_iteration_count);
}

}  // namespace mmsolver
