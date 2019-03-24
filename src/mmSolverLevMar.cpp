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

#include <mmSolverLevMar.h>

#ifdef USE_SOLVER_LEVMAR

// // Lev-Mar
// #include <levmar.h>  // dlevmar_dif

#include <mmSolverFunc.h>  // solveFunc

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
void solveFunc_levmar(double *p,
                      double *x,
                      int m,
                      int n,
                      void *data) {
    int ret = solveFunc(m, n, p, x, data);
    if (ret == SOLVE_FUNC_FAILURE) {
        for (int i = 0; i < n; ++i) {
          x[i] = std::numeric_limits<double>::quiet_NaN();
        }
    }
    return;
}


#endif USE_SOLVER_LEVMAR
