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
 * Uses Non-Linear Least Squares algorithm to calculate attribute
 * values based on 2D-to-3D error measurements through a pinhole
 * camera.
 */

#ifdef MMSOLVER_USE_CERES

#include "adjust_ceres_lmdif.h"

// STL
#include <math.h>

#include <cassert>
#include <cmath>
#include <ctime>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

// Ceres
#include <ceres/ceres.h>
#include <ceres/numeric_diff_cost_function.h>
#include <ceres/problem.h>
#include <ceres/solver.h>
#include <ceres/types.h>

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "adjust_solveFunc.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace {

struct ResidualFunctor {
    ResidualFunctor(const int num_parameters, const int num_residuals,
                    SolverData* user_data)
        : numberOfParameters(num_parameters)
        , numberOfResiduals(num_residuals)
        , userData(user_data) {}

    bool operator()(double const* const* parameters, double* residuals) const {
        // Jacobian matrices are not calculated by this functor at
        // all.
        double* jacobians = nullptr;  // No Jacobians
        userData->isPrintCall = false;
        userData->isNormalCall = true;
        userData->isJacobianCall = false;
        userData->doCalcJacobian = false;

        const int ret =
            solveFunc(numberOfParameters, numberOfResiduals, parameters[0],
                      residuals, jacobians, userData);

        return ret == SOLVE_FUNC_SUCCESS;
    }

    const int numberOfParameters;
    const int numberOfResiduals;
    SolverData* userData;
};

}  // namespace

bool solve_3d_ceres_lmdif(SolverOptions& solverOptions,
                          const int numberOfParameters,
                          const int numberOfErrors,
                          std::vector<double>& paramList,
                          std::vector<double>& errorList,
                          std::vector<double>& paramWeightList,
                          SolverData& userData, SolverResult& solveResult) {
    const bool verbose = false;

    ::ceres::Problem::Options problemOptions;
    problemOptions.enable_fast_removal = true;
    // // For debug turn this to 'false'.
    // problemOptions.apply_loss_function = false;
    ::ceres::Problem problem(problemOptions);

    auto cost_functor =
        new ResidualFunctor(numberOfParameters, numberOfErrors, &userData);

    ::ceres::NumericDiffOptions numericDiffOptions;
    numericDiffOptions.relative_step_size = solverOptions.delta;
    auto cost_function = new ::ceres::DynamicNumericDiffCostFunction<
        ResidualFunctor, ::ceres::FORWARD>(
        cost_functor,
        ::ceres::DO_NOT_TAKE_OWNERSHIP,  // Don't let Ceres delete our functor
        numericDiffOptions);
    cost_function->AddParameterBlock(numberOfParameters);
    cost_function->SetNumResiduals(numberOfErrors);

    // We only have a single parameter block.
    double* param_ptr = paramList.data();
    problem.AddResidualBlock(cost_function, nullptr, param_ptr);

    ::ceres::Solver::Options options;
    options.minimizer_type = ::ceres::TRUST_REGION;
    options.trust_region_strategy_type = ::ceres::LEVENBERG_MARQUARDT;
    options.linear_solver_type = ::ceres::DENSE_QR;

    // Allow solve to get worse before it gets better. The parameters
    // with the lowest error is always picked at the end of the solve.
    options.use_nonmonotonic_steps = true;
    options.max_num_consecutive_invalid_steps = 5;  // Allow some invalid steps.

    options.max_num_iterations = solverOptions.iterMax;
    options.function_tolerance = solverOptions.eps1;
    options.parameter_tolerance = solverOptions.eps2;
    options.gradient_tolerance = solverOptions.eps3;
    options.initial_trust_region_radius = solverOptions.tau;
    options.jacobi_scaling = true;
    options.num_threads = 1;

    options.minimizer_progress_to_stdout = verbose;
    options.logging_type = ::ceres::SILENT;
    if (verbose) {
        options.logging_type = ::ceres::PER_MINIMIZER_ITERATION;
    }

    // // TODO: Add parameter bounds.
    // for (int i = 0; i < numberOfParameters; i++) {
    //     if (paramWeightList[i] < 1.0) {
    //         // TODO: Set parameter bounds.
    //         problem.SetParameterLowerBound(param_ptr, i, -1e8);
    //         problem.SetParameterUpperBound(param_ptr, i, 1e8);
    //     }
    // }

    ::ceres::Solver::Summary summary;
    ::ceres::Solve(options, &problem, &summary);

    if (verbose) {
        MMSOLVER_MAYA_VRB(
            "Ceres Solver Success: " << summary.IsSolutionUsable());
        MMSOLVER_MAYA_VRB(summary.BriefReport());
        MMSOLVER_MAYA_VRB(summary.FullReport());
    }

    solveResult.success = summary.IsSolutionUsable();
    solveResult.iterations =
        summary.num_successful_steps + summary.num_unsuccessful_steps;
    solveResult.functionEvals = summary.num_residual_evaluations;
    solveResult.jacobianEvals = summary.num_jacobian_evaluations;
    solveResult.reason = summary.message;
    solveResult.reason_number = static_cast<int>(summary.termination_type);
    solveResult.errorFinal = summary.final_cost;

    if (solveResult.success) {
        // NOTE: Parameters are updated in-place.
        errorList.resize(numberOfErrors);
        cost_function->Evaluate(&param_ptr, errorList.data(), nullptr);
    }

    return true;
}

#endif  // MMSOLVER_USE_CERES
