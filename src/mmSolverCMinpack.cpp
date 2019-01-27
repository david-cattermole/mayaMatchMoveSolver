/*
 * Uses Non-Linear Least Squares algorithm to calculate attribute
 * values based on 2D-to-3D error measurements through a pinhole
 * camera.
 */

#ifdef USE_SOLVER_CMINPACK

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
#include <mmSolverCminpack.h>


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
