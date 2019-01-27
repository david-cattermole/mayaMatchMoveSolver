/*
 * Uses Non-Linear Least Squares algorithm from levmar library to
 * calculate attribute values based on 2D-to-3D error measurements
 * through a pinhole camera.
 */


#ifndef MAYA_MM_SOLVER_LEVMAR_H
#define MAYA_MM_SOLVER_LEVMAR_H

// STL
#include <string>  // string
#include <vector>  // vector

// Utils
#include <utilities/debugUtils.h>

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

void solveFunc_levmar(double *p,
                      double *x,
                      int m,
                      int n,
                      void *data);

#endif // MAYA_MM_SOLVER_LEVMAR_H
