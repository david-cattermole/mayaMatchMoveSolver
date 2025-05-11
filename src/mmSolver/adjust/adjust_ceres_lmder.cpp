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

#include "adjust_ceres_lmder.h"

// STL
#include <math.h>

#include <cmath>
#include <ctime>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

// Ceres
#include <ceres/ceres.h>
#include <ceres/dynamic_cost_function.h>
#include <ceres/numeric_diff_cost_function.h>
#include <ceres/problem.h>
#include <ceres/solver.h>
#include <ceres/types.h>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MDGModifier.h>
#include <maya/MPoint.h>
#include <maya/MStringArray.h>

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "adjust_ceres_base.h"
#include "adjust_solveFunc.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

namespace {

// Cost function adapter for Ceres that wraps the existing solve
// function "solveFunc".
class ResidualAndJacobianFunction : public ::ceres::DynamicCostFunction {
public:
    ResidualAndJacobianFunction(const int numberOfParameters,
                                const int numberOfResiduals,
                                SolverData* userData)
        : m_jacobians_temp(numberOfParameters * numberOfResiduals, 0.0)
        , m_userData(userData) {
        // Set the number of residuals and parameter block sizes.
        ::ceres::CostFunction::set_num_residuals(numberOfResiduals);
        ::ceres::CostFunction::mutable_parameter_block_sizes()->push_back(
            numberOfParameters);
    }

    bool Evaluate(double const* const* parameters, double* residuals,
                  double** jacobians) const override {
        const bool verbose = false;
        MMSOLVER_MAYA_VRB(
            "adjust_ceres_lmder ResidualAndJacobianFunction::Evaluate");

        const int numberOfParameters = parameter_block_sizes()[0];
        const int numberOfResiduals = num_residuals();
        const int numberOfJacobians = numberOfParameters * numberOfResiduals;
        MMSOLVER_MAYA_VRB(
            "adjust_ceres_lmder ResidualAndJacobianFunction::Evaluate "
            "numberOfParameters: "
            << numberOfParameters);
        MMSOLVER_MAYA_VRB(
            "adjust_ceres_lmder ResidualAndJacobianFunction::Evaluate "
            "numberOfResiduals: "
            << numberOfResiduals);
        MMSOLVER_MAYA_VRB(
            "adjust_ceres_lmder ResidualAndJacobianFunction::Evaluate "
            "numberOfJacobians: "
            << numberOfJacobians);

        if (verbose) {
            for (auto i = 0; i < numberOfParameters; i++) {
                MMSOLVER_MAYA_VRB(
                    "adjust_ceres_lmder ResidualAndJacobianFunction::Evaluate "
                    "parameters[0]["
                    << i << "] = " << parameters[0][i]);
            }
        }

        const bool do_jacobians = jacobians && jacobians[0];
        MMSOLVER_MAYA_VRB(
            "adjust_ceres_lmder ResidualAndJacobianFunction::Evaluate "
            "do_jacobians: "
            << do_jacobians);
        double* jacobians_block = nullptr;
        if (do_jacobians) {
            jacobians_block = jacobians[0];

            m_userData->isPrintCall = false;
            m_userData->isNormalCall = false;
            m_userData->isJacobianCall = true;
        } else {
            m_userData->isPrintCall = false;
            m_userData->isNormalCall = true;
            m_userData->isJacobianCall = false;
        }

        m_userData->doCalcJacobian = false;
        int ret = solveFunc(numberOfParameters, numberOfResiduals,
                            parameters[0], residuals, nullptr, m_userData);

        if (do_jacobians) {
            m_userData->doCalcJacobian = true;
            ret =
                solveFunc(numberOfParameters, numberOfResiduals, parameters[0],
                          residuals, jacobians_block, m_userData);
        }

        // We need to transpose the matrix from column-major to
        // row-major.
        //
        // CMinpack uses Jacobian matrices that are stored in
        // column-major order, but Ceres uses row-major.
        if (do_jacobians) {
            memcpy((void*)m_jacobians_temp.data(), jacobians[0],
                   sizeof(double) * numberOfParameters * numberOfResiduals);

            for (uint32_t i = 0; i < numberOfResiduals; ++i) {
                for (uint32_t j = 0; j < numberOfParameters; ++j) {
                    auto row_major_index = i * numberOfParameters + j;
                    auto column_major_index = j * numberOfResiduals + i;
                    jacobians[0][row_major_index] =
                        m_jacobians_temp[column_major_index];
                }
            }
        }

        if (verbose) {
            for (auto i = 0; i < numberOfResiduals; i++) {
                MMSOLVER_MAYA_VRB(
                    "adjust_ceres_lmder ResidualAndJacobianFunction::Evaluate "
                    "residuals["
                    << i << "] = " << residuals[i]);
            }

            if (do_jacobians) {
                for (auto i = 0; i < numberOfJacobians; i++) {
                    MMSOLVER_MAYA_VRB(
                        "adjust_ceres_lmder "
                        "ResidualAndJacobianFunction::Evaluate "
                        "jacobians[0]["
                        << i << "] = " << jacobians[0][i]);
                }
            }
        }

        return ret == SOLVE_FUNC_SUCCESS;
    }

private:
    SolverData* m_userData;
    std::vector<double> m_jacobians_temp;
};

}  // namespace

bool solve_3d_ceres_lmder(SolverOptions& solverOptions,
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

    auto* cost_function = new ResidualAndJacobianFunction(
        numberOfParameters, numberOfErrors, &userData);

    // We only have a single parameter block.
    double* param_ptr = paramList.data();
    problem.AddResidualBlock(cost_function, nullptr, param_ptr);

    ::ceres::Solver::Options options;

    options.minimizer_type = ::ceres::TRUST_REGION;
    options.trust_region_strategy_type = ::ceres::LEVENBERG_MARQUARDT;

    // See "How do I choose the right linear solver?";
    // http://ceres-solver.org/solving_faqs.html#solving
    options.linear_solver_type = ::ceres::DENSE_QR;

    // Allow solve to get worse before it gets better. The parameters
    // with the lowest error is always picked at the end of the solve.
    //
    // NOTE: This only affects Trust Region algorithms.
    const uint8_t max_invalid_steps = 0;  // or 5?
    options.use_nonmonotonic_steps = max_invalid_steps > 0;
    options.max_num_consecutive_invalid_steps = max_invalid_steps;

    // TODO: Should we bound the solver time?
    options.max_solver_time_in_seconds = 1e9;

    options.max_num_iterations = solverOptions.iterMax;
    options.function_tolerance = solverOptions.function_tolerance;
    options.parameter_tolerance = solverOptions.parameter_tolerance;
    options.gradient_tolerance = solverOptions.gradient_tolerance;
    options.initial_trust_region_radius = solverOptions.tau;
    options.jacobi_scaling = true;
    options.num_threads = 1;

    options.minimizer_progress_to_stdout = false;
    options.logging_type = ::ceres::SILENT;
    if (verbose) {
        options.minimizer_progress_to_stdout = true;
        options.logging_type = ::ceres::PER_MINIMIZER_ITERATION;
    }

    ::ceres::Solver::Summary summary;
    ::ceres::Solve(options, &problem, &summary);

    if (verbose) {
        MMSOLVER_MAYA_VRB("Ceres Solver Success: " << summary.IsSolutionUsable());
        MMSOLVER_MAYA_VRB(summary.BriefReport());
        MMSOLVER_MAYA_VRB(summary.FullReport());
    }

    solveResult.success = summary.IsSolutionUsable();
    solveResult.iterations =
        summary.num_successful_steps + summary.num_unsuccessful_steps;
    solveResult.functionEvals = summary.num_residual_evaluations;
    solveResult.jacobianEvals = summary.num_jacobian_evaluations;

    const size_t reason_number = static_cast<int>(summary.termination_type);
    const std::string& reason = CERES_REASONS[reason_number];
    solveResult.reason_number = reason_number;
    solveResult.reason = reason + " (" + summary.message + ")";
    solveResult.errorFinal = summary.final_cost;

    // solveResult.iterationAttempts = (int) levmar_info[9];
    // solveResult.errorInitial = summary.initial_cost;
    // solveResult.errorJt = levmar_info[2];
    // solveResult.errorDp = levmar_info[3];
    // solveResult.errorMaximum = levmar_info[4];

    if (solveResult.success) {
        // NOTE: Parameters are updated in-place.
        errorList.resize(numberOfErrors);
        cost_function->SetNumResiduals(errorList.size());
        cost_function->Evaluate(&param_ptr, errorList.data(), nullptr);
    }

    return true;
}

}  // namespace mmsolver

#endif  // MMSOLVER_USE_CERES
