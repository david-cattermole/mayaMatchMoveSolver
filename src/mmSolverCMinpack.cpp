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

#ifdef USE_SOLVER_CMINPACK

// CMinpack
#include <cminpack.h>

// STL
#include <ctime>     // time
#include <cmath>     // exp
#include <iostream>  // cout, cerr, endl
#include <string>    // string
#include <vector>    // vector
#include <cassert>   // assert
#include <limits>    // double max value, NaN
#include <math.h>

// Utils
#include <utilities/debugUtils.h>
#include <utilities/stringUtils.h>

// Maya
#include <maya/MPoint.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MFnAnimCurve.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MMatrix.h>
#include <maya/MComputation.h>
#include <maya/MProfiler.h>

// Utilities
#include <mayaUtils.h>

#include <mmSolverFunc.h>  // solveFunc, SolverData
#include <mmSolverCMinpack.h>


bool solve_3d_cminpack_lmdif(
        SolverOptions &solverOptions,
        int numberOfParameters,
        int numberOfErrors,
        std::vector<double> &paramList,
        std::vector<double> &errorList,
        std::vector<double> &paramLowerBoundList,
        std::vector<double> &paramUpperBoundList,
        std::vector<double> &paramWeightList,
        SolverData &userData,
        SolverResult &solveResult,
        MStringArray &outResult){
    int solverType = SOLVER_TYPE_CMINPACK_LM;
    int ret = 0;
    std::string resultStr;
    int iterMax = solverOptions.iterMax;
    userData.solverType = solverType;

    std::vector<double> jacobianList(1);
    jacobianList.resize((unsigned long) numberOfParameters * numberOfErrors, 0);

    int cminpack_info = 0;

    std::vector<int> ipvtList(1);
    ipvtList.resize((unsigned long) numberOfParameters, 0);

    std::vector<double> qtfList(1);
    qtfList.resize((unsigned long) numberOfParameters, 0);

    std::vector<double> wa1List(1);
    std::vector<double> wa2List(1);
    std::vector<double> wa3List(1);
    std::vector<double> wa4List(1);
    wa1List.resize((unsigned long) numberOfParameters, 0);
    wa2List.resize((unsigned long) numberOfParameters, 0);
    wa3List.resize((unsigned long) numberOfParameters, 0);
    wa4List.resize((unsigned long) numberOfErrors, 0);

    int ldfjac = numberOfErrors;
    if (numberOfParameters >= numberOfErrors) {
        ldfjac = numberOfParameters;
    }

    double cminpack_ftol = solverOptions.eps1;
    double cminpack_xtol = solverOptions.eps2;
    double cminpack_gtol = solverOptions.eps3;

    // Change the sign of the delta
    double cminpack_epsfcn = std::abs(solverOptions.delta);
    if (solverOptions.autoDiffType == 1) {
        // Central Differencing
        //
        // To use forward differing the delta must be a positive
        // number, so we make 'delta_factor' negative.
        cminpack_epsfcn *= -1;
    }

    int cminpack_mode = 2; // Off
    if (solverOptions.autoParamScale == 1) {
        cminpack_mode = 1; // On
    }

    double cminpack_factor = solverOptions.tau;
    int cminpack_nprint = 0;  // 0 == don't print anything.
    int cminpack_calls = 0;
    double cminpack_fnorm = 0.0;

    cminpack_info = __cminpack_func__(lmdif)(
            // Function to call
            solveFunc_cminpack_lm,

            // Input user data.
            (void *) &userData,

            // Number of errors.
            numberOfErrors,

            // Number of parameters.
            numberOfParameters,

            // parameters
            &paramList[0],

            // errors
            &errorList[0],

            // Tolerance to stop solving.
            cminpack_ftol, cminpack_xtol, cminpack_gtol,

            // Iteration maximum
            iterMax,

            // Delta (how much to shift parameters when calculating
            // jacobian).
            cminpack_epsfcn,

            // Weight list (diagonal scaling)
            &paramWeightList[0],

            // Auto-parameter scaling mode
            cminpack_mode,

            // Tau factor (scale factor for initialTransform mu)
            cminpack_factor,

            // Should we print at each iteration?
            cminpack_nprint,

            // 'nfev' is an integer output variable set to the
            // number of calls to 'fcn'.
            &cminpack_calls,

            // 'fjac' is an output numberOfParameters by n
            // array. The upper n by n submatrix of fjac contains
            // an upper triangular matrix r with diagonal elements
            // of nonincreasing magnitude.
            &jacobianList[0],

            // 'ldfjac' is a positive integer input variable not
            // less than numberOfParameters which specifies the
            // leading dimension of the array fjac.
            ldfjac,

            // 'ipvt' is an integer output array of length n. ipvt
            // defines a permutation matrix p such that jac*p =
            // q*r, where jac is the final calculated Jacobian, q
            // is orthogonal (not stored), and r is upper
            // triangular with diagonal elements of nonincreasing
            // magnitude. Column j of p is column ipvt(j) of the
            // identity matrix
            &ipvtList[0],

            // 'qtf' is an output array of length n which contains
            // the first n elements of the vector `(q transpose) *
            // fvec`.
            &qtfList[0],

            // Working memory arrays
            &wa1List[0],
            &wa2List[0],
            &wa3List[0],
            &wa4List[0]);
    cminpack_fnorm = __cminpack_func__(enorm)(numberOfErrors, &errorList[0]);
    ret = userData.iterNum;

    int reason_number = cminpack_info;
    const std::string &reason = cminpackReasons[reason_number];
    solveResult.success = ret > 0;
    solveResult.reason_number = reason_number;
    solveResult.reason = reason;
    solveResult.iterations = cminpack_calls;
    solveResult.functionEvals = userData.iterNum;
    solveResult.jacobianEvals = userData.jacIterNum;
    solveResult.errorFinal = cminpack_fnorm;
    return true;
}


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
int solveFunc_cminpack_lm(void *data,
                          int m,
                          int n,
                          const double *x,
                          double *fvec,
                          int iflag) {
    SolverData *ud = static_cast<SolverData *>(data);
    ud->isPrintCall = iflag == 0;
    ud->isNormalCall = iflag == 1;
    ud->isJacobianCall = iflag == 2;

    int ret = solveFunc(n, m, x, fvec, data);

    int info = -1;
    if (ret == SOLVE_FUNC_SUCCESS) {
        info = 0;
    } else if (ret == SOLVE_FUNC_FAILURE) {
        info = -1;
    }
    return info;
}


#endif // USE_SOLVER_CMINPACK
