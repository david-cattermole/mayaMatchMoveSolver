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
 * Uses Non-Linear Least Squares algorithm from levmar library to
 * calculate attribute values based on 2D-to-3D error measurements
 * through a pinhole camera.
 */


#ifndef MAYA_MM_SOLVER_LEVMAR_H
#define MAYA_MM_SOLVER_LEVMAR_H

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


// Sparse LM or Lev-Mar Termination Reasons:
const std::string levmarReasons[8] = {
        // reason 0
        "No reason, should not get here!",

        // reason 1
        "Stopped by small gradient J^T e",

        // reason 2
        "Stopped by small Dp",

        // reason 3
        "Stopped by reaching maximum iterations",

        // reason 4
        "Singular matrix. Restart from current parameters with increased \'Tau Factor\'",

        // reason 5
        "Too many failed attempts to increase damping. Restart with increased \'Tau Factor\'",

        // reason 6
        "Stopped by small error",

        // reason 7
        // "stopped by invalid (i.e. NaN or Inf) \"func\" refPoints (user error)",
        "User canceled",
};


bool solve_3d_levmar_dif(
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
        MStringArray &outResult);

void solveFunc_levmar(double *p,
                      double *x,
                      int m,
                      int n,
                      void *data);

#endif // MAYA_MM_SOLVER_LEVMAR_H
