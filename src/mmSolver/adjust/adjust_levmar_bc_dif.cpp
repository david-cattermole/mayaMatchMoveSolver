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
 * Bundle Adjustment functions to launch a solve using the levmar library.
 */

#ifdef MMSOLVER_USE_LEVMAR

// STL
#include <math.h>

#include <cmath>
#include <ctime>
#include <iostream>
#include <limits>
#include <string>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MDGModifier.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MProfiler.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

// Lev-Mar
#include <levmar.h>

// MM Solver
#include "adjust_levmar_bc_dif.h"
#include "adjust_solveFunc.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

// Forward declare.
void solveFunc_levmar_bc_dif(double *p, double *x, int m, int n, void *data);

bool solve_3d_levmar_bc_dif(SolverOptions &solverOptions,
                            int numberOfParameters, int numberOfErrors,
                            std::vector<double> &paramList,
                            std::vector<double> &errorList,
                            std::vector<double> &paramLowerBoundList,
                            std::vector<double> &paramUpperBoundList,
                            std::vector<double> &paramWeightList,
                            SolverData &userData, SolverResult &solveResult,
                            MStringArray &outResult) {
    int solverType = SOLVER_TYPE_LEVMAR;
    std::string resultStr;

    const unsigned int levmar_optsSize = LM_OPTS_SZ;
    const unsigned int levmar_infoSize = LM_INFO_SZ;
    double levmar_opts[levmar_optsSize];
    double levmar_info[levmar_infoSize];

    // Change the sign of the delta
    double delta_factor = std::abs(solverOptions.delta);
    if (solverOptions.autoDiffType == LEVMAR_AUTO_DIFF_TYPE_CENTRAL) {
        // Central Differencing
        //
        // To use forward differing the delta must be a positive
        // number, so we make 'delta_factor' negative.
        delta_factor *= -1;
    }

    levmar_opts[0] = solverOptions.tau;
    levmar_opts[1] = solverOptions.function_tolerance;
    levmar_opts[2] = solverOptions.parameter_tolerance;
    levmar_opts[3] = solverOptions.gradient_tolerance;
    levmar_opts[4] = delta_factor;
    userData.solverType = solverType;

    // Allocate a memory block for both 'work' and 'covar', so that
    // the block is close together in physical memory.
    double *work, *covar;
    work =
        (double *)malloc((LM_BC_DIF_WORKSZ(numberOfParameters, numberOfErrors) +
                          numberOfParameters * numberOfParameters) *
                         sizeof(double));
    if (!work) {
        MMSOLVER_MAYA_ERR("Memory allocation request failed.");
        resultStr = "success=0";
        outResult.append(MString(resultStr.c_str()));
        return false;
    }
    covar = work + LM_BC_DIF_WORKSZ(numberOfParameters, numberOfErrors);

    // Solve!
    int ret = dlevmar_bc_dif(
        // Function to call (input only)
        // Function must be of the structure:
        //   func(double *params, double *x, int numberOfParameters, int
        //   numberOfErrors, void *data)
        solveFunc_levmar_bc_dif,

        // Parameters (input and output)
        // Should be filled with initial estimate, will be filled
        // with output parameters
        &paramList[0],

        // Measurement Vector (input only)
        // nullptr implies a zero vector
        &errorList[0],

        // Parameter Vector Dimension (input only)
        // (i.e. #unknowns)
        numberOfParameters,

        // Measurement Vector Dimension (input only)
        numberOfErrors,

        // vector of lower bounds. If nullptr, no lower bounds apply
        &paramLowerBoundList[0],

        // vector of upper bounds. If nullptr, no upper bounds apply (input
        // only)
        &paramUpperBoundList[0],

        // diagonal scaling constants. nullptr implies no scaling (input only)
        &paramWeightList[0],

        // Maximum Number of Iterations (input only)
        solverOptions.iterMax,

        // Minimisation options (input only)
        // opts[0] = tau      (scale factor for initialTransform mu)
        // opts[1] = function_tolerance (stopping threshold for ||J^T e||_inf)
        // opts[2] = parameter_tolerance (stopping threshold for ||Dp||_2)
        // opts[3] = gradient_tolerance (stopping threshold for ||e||_2)
        // opts[4] = delta    (step used in difference approximation to the
        // Jacobian)
        //
        // If \delta<0, the Jacobian is approximated with central differences
        // which are more accurate (but slower!) compared to the forward
        // differences employed by default.
        // Set to nullptr for defaults to be used.
        levmar_opts,

        // Output Information (output only)
        // information regarding the minimization.
        // info[0] = ||e||_2 at initialTransform params.
        // info[1-4] = (all computed at estimated params)
        //  [
        //   ||e||_2,
        //   ||J^T e||_inf,
        //   ||Dp||_2,
        //   \mu/max[J^T J]_ii
        //  ]
        // info[5] = number of iterations,
        // info[6] = reason for terminating:
        //   1 - stopped by small gradient J^T e
        //   2 - stopped by small Dp
        //   3 - stopped by iterMax
        //   4 - singular matrix. Restart from current params with increased \mu
        //   5 - no further error reduction is possible. Restart with increased
        //   mu 6 - stopped by small ||e||_2 7 - stopped by invalid (i.e. NaN or
        //   Inf) "func" refPoints; a user error
        // info[7] = number of function evaluations
        // info[8] = number of Jacobian evaluations
        // info[9] = number linear systems solved (number of attempts for
        // reducing error)
        //
        // Set to nullptr if don't care
        levmar_info,

        // Working Data (input only)
        // working memory, allocated internally if nullptr. If !=nullptr, it is
        // assumed to point to a memory chunk at least
        // LM_DIF_WORKSZ(numberOfParameters, numberOfErrors)*sizeof(double)
        // bytes long
        work,

        // Covariance matrix (output only)
        // Covariance matrix corresponding to LS solution; Assumed to point to a
        // mxm matrix. Set to nullptr if not needed.
        covar,

        // Custom Data for 'func' (input only)
        // pointer to possibly needed additional data, passed uninterpreted to
        // func. Set to nullptr if not needed
        (void *)&userData);

    free(work);

    int reason_number = (int)levmar_info[6];
    const std::string &reason = levmarReasons[reason_number];
    solveResult.success = ret > 0;
    solveResult.reason_number = reason_number;
    solveResult.reason = reason;
    solveResult.iterations = (int)levmar_info[5];
    ;
    solveResult.functionEvals = (int)levmar_info[7];
    solveResult.jacobianEvals = (int)levmar_info[8];
    // solveResult.iterationAttempts = (int) levmar_info[9];
    // solveResult.errorInitial = levmar_info[0];
    solveResult.errorFinal = levmar_info[1];
    // solveResult.errorJt = levmar_info[2];
    // solveResult.errorDp = levmar_info[3];
    // solveResult.errorMaximum = levmar_info[4];
    return true;
}

// Function run by lev-mar algorithm to test the input parameters, p,
// and compute the output errors, x.
//
// 'p' are the parameters to be solved with.
//
// 'x' are the errors to be computed in the solve function.
//
// 'm' is the number of parameters (the length of 'p').
//
// 'n' is the number of errors (the length of 'x')
//
// 'data' is the user data passed to the solving function.
void solveFunc_levmar_bc_dif(double *p, double *x, int m, int n, void *data) {
    // We will not compute a jacobian in 'levmar'
    SolverData *ud = static_cast<SolverData *>(data);
    ud->doCalcJacobian = false;
    double *fjac = nullptr;

    // int ret = solveFunc(m, n, p, x, data);
    int ret = solveFunc(m, n, p, x, fjac, data);
    if (ret == SOLVE_FUNC_FAILURE) {
        for (int i = 0; i < n; ++i) {
            x[i] = std::numeric_limits<double>::quiet_NaN();
        }
    }
    return;
}

}  // namespace mmsolver

#endif  // MMSOLVER_USE_LEVMAR
