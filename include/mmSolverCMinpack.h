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
 */


#ifndef MAYA_MM_SOLVER_CMINPACK_H
#define MAYA_MM_SOLVER_CMINPACK_H

// STL
#include <string>
#include <vector>

// Maya
#include <maya/MPoint.h>
#include <maya/MStringArray.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MDGModifier.h>
#include <maya/MComputation.h>

// Internal Objects
#include <Camera.h>
#include <Marker.h>
#include <Bundle.h>
#include <Attr.h>

#include <mmSolverFunc.h>
#include <mmSolver.h>


// CMinpack 'lmdif' Termination Reasons:
//
// info is an integer output variable. If the user has terminated
// execution, info is set to the (negative) value of iflag. See
// description of fcn. Otherwise, info is set as follows.
//
const std::string cminpackReasons[9] = {
        // reason 0
        "Improper input parameters",

        // reason 1
        "Both actual and predicted relative reductions in the sum of squares are at most ftol.",

        // reason 2
        "Relative error between two consecutive iterates is at most xtol.",

        // reason 3
        "Conditions for info = 1 and info = 2 both hold.",

        // reason 4
        "The cosine of the angle between fvec and any column of the Jacobian is at most gtol in absolute value.",

        // reason 5
        "Number of calls to fcn has reached or exceeded maxfev.",

        // reason 6
        "\'ftol\' is too small. No further reduction in the sum of squares is possible.",

        // reason 7
        "\'xtol\' is too small. No further improvement in the approximate solution x is possible.",

        // reason 8
        "\'gtol\' is too small. fvec is orthogonal to the columns of the Jacobian to machine precision.",
};


bool solve_3d_cminpack_lmdif(SolverOptions &solverOptions,
                             int numberOfParameters,
                             int numberOfErrors,
                             std::vector<double> &paramList,
                             std::vector<double> &errorList,
                             std::vector<double> &paramLowerBoundList,
                             std::vector<double> &paramUpperBoundList,
                             std::vector<double> &paramWeightList,
                             SolverData &userData,
                             SolverResult &solveResult,
                             MStringArray &outResult);


int solveFunc_cminpack_lm(void *data,
                          int n,
                          int m,
                          const double *p,
                          double *x,
                          int iflag);

#endif // MAYA_MM_SOLVER_CMINPACK_H
