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
 * Uses Non-Linear Least Squares algorithm to calculate attribute
 * values based on 2D-to-3D error measurements through a pinhole
 * camera.
 */

#ifdef MMSOLVER_USE_CMINPACK

#include "adjust_cminpack_lmder.h"

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
#include <maya/MFnAnimCurve.h>
#include <maya/MMatrix.h>
#include <maya/MObject.h>
#include <maya/MPoint.h>
#include <maya/MProfiler.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

// CMinpack
#include <cminpack.h>

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Solver
#include "adjust_cminpack_base.h"
#include "adjust_solveFunc.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

// Forward declare.
int solveFunc_cminpack_lmder(void *data, int m, int n, const double *x,
                             double *fvec, double *fjac, int ldfjac, int iflag);

bool solve_3d_cminpack_lmder(SolverOptions &solverOptions,
                             int numberOfParameters, int numberOfErrors,
                             std::vector<double> &paramList,
                             std::vector<double> &errorList,
                             std::vector<double> &paramWeightList,
                             SolverData &userData, SolverResult &solveResult) {
    const int solverType = SOLVER_TYPE_CMINPACK_LMDER;
    int ret = 0;
    int iterMax = solverOptions.iterMax;
    userData.solverType = solverType;

    std::vector<double> jacobianList(1);
    jacobianList.resize((unsigned long)numberOfParameters * numberOfErrors, 0);

    std::vector<int> ipvtList(1);
    ipvtList.resize((unsigned long)numberOfParameters, 0);

    std::vector<double> qtfList(1);
    qtfList.resize((unsigned long)numberOfParameters, 0);

    std::vector<double> wa1List(1);
    std::vector<double> wa2List(1);
    std::vector<double> wa3List(1);
    std::vector<double> wa4List(1);
    wa1List.resize((unsigned long)numberOfParameters, 0);
    wa2List.resize((unsigned long)numberOfParameters, 0);
    wa3List.resize((unsigned long)numberOfParameters, 0);
    wa4List.resize((unsigned long)numberOfErrors, 0);

    int ldfjac = numberOfErrors;
    if (numberOfParameters >= numberOfErrors) {
        ldfjac = numberOfParameters;
    }

    double ftol = solverOptions.function_tolerance;
    double xtol = solverOptions.parameter_tolerance;
    double gtol = solverOptions.gradient_tolerance;

    int mode = 2;  // Off
    if (solverOptions.autoParamScale == 1) {
        mode = 1;  // On
    }

    // cminpack uses a 'tau' value of between 0.0 to 100.0;
    double factor = solverOptions.tau * 100.0;
    int nprint = 0;  // 0 == don't print anything.
    int calls = 0;
    int njev = 0;
    double error_norm_value = 0.0;
    int info = __cminpack_func__(lmder)(
        // Function to call
        solveFunc_cminpack_lmder,

        // Input user data.
        (void *)&userData,

        // Number of errors.
        numberOfErrors,

        // Number of parameters.
        numberOfParameters,

        // Parameters
        &paramList[0],

        // Errors
        &errorList[0],

        // Jacobian (of length numberOfErrors * numberOfParameters)
        //
        // 'fjac' is an output numberOfParameters by n
        // array. The upper n by n submatrix of fjac contains
        // an upper triangular matrix r with diagonal elements
        // of nonincreasing magnitude.
        &jacobianList[0],

        // Longest Dimension of Jacobian Matrix
        ldfjac,

        // Tolerance to stop solving.
        ftol, xtol, gtol,

        // Iteration maximum
        iterMax,

        // Weight list (diagonal scaling)
        &paramWeightList[0],

        // Auto-parameter-scaling mode
        mode,

        // Tau factor (scale factor for initialTransform mu)
        factor,

        // Should we print at each iteration?
        nprint,

        // 'nfev' is an integer output variable set to the
        // number of calls to 'fcn'.
        &calls,

        // Number of Jacobian calls.
        &njev,

        // 'ipvt' is an integer output array of length n. ipvt
        // defines a permutation matrix p such that jac*p =
        // q*r, where jac is the final calculated Jacobian, q
        // is orthogonal (not stored), and r is upper
        // triangular with diagonal elements of non-increasing
        // magnitude. Column j of p is column ipvt(j) of the
        // identity matrix
        &ipvtList[0],

        // 'qtf' is an output array of length n which contains
        // the first n elements of the vector `(q transpose) *
        // fvec`.
        &qtfList[0],

        // Working memory arrays
        &wa1List[0], &wa2List[0], &wa3List[0], &wa4List[0]);
    error_norm_value = __cminpack_func__(enorm)(numberOfErrors, &errorList[0]);
    ret = userData.iterNum;

    const int reason_number = info;
    const std::string &reason = cminpackReasons[reason_number];
    solveResult.success = ret > 0;
    solveResult.reason_number = reason_number;
    solveResult.reason = reason;
    solveResult.iterations = calls;
    solveResult.functionEvals = userData.iterNum;
    solveResult.jacobianEvals = userData.jacIterNum;
    solveResult.errorFinal = error_norm_value;
    return true;
}

// Run the cminpack 'lmder' solve function.
//
// 'data' is a pointer to a user data that was passed to 'lmdif'.
//
// 'm' is a positive integer input variable set to the number of
// functions.
//
// 'n' is a positive integer input variable set to the number of
// variables. n must not exceed m.
//
// 'x' is an array of length n. On input x must contain an initial
// estimate of the solution vector. On output x contains the final
// estimate of the solution vector.
//
// 'fvec' is an output array of length m which contains the functions
// evaluated at the output x.
//
// 'fjac' is an output array of length m*n containing the
// jacobian matrix (at end of solve).
//
// 'ldfjac' is a positive integer of the highest dimension of the
// fjac array (m or n).
//
// 'iflag' tells us what type of call this function is expected to perform.
int solveFunc_cminpack_lmder(void *data, int m, int n, const double *x,
                             double *fvec, double *fjac, int ldfjac,
                             int iflag) {
    MMSOLVER_ASSERT(ldfjac == n ? m <= n : m,
                    "'ldfjac' is the highest dimension of the array.");
    MMSOLVER_CORE_UNUSED(ldfjac);

    SolverData *ud = static_cast<SolverData *>(data);
    ud->isPrintCall = iflag == 0;
    ud->isNormalCall = iflag == 1;
    ud->isJacobianCall = iflag == 2;
    ud->doCalcJacobian = iflag == 2;

    int ret = solveFunc(n, m, x, fvec, fjac, data);

    int info = -1;
    if (ret == SOLVE_FUNC_SUCCESS) {
        info = 0;
    } else if (ret == SOLVE_FUNC_FAILURE) {
        info = -1;
    }
    return info;
}

}  // namespace mmsolver

#endif  // MMSOLVER_USE_CMINPACK
