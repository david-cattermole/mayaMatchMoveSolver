/*
 * 
 */


#ifndef MAYA_MM_SOLVER_CMINPACK_H
#define MAYA_MM_SOLVER_CMINPACK_H

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

//
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


// The user data given to cminpack.
/*
struct CMinpackSolverData {
    // Solver Objects.
    CameraPtrList cameraList;
    MarkerPtrList markerList;
    BundlePtrList bundleList;
    AttrPtrList attrList;
    MTimeArray frameList;  // Times to solve

    // Relational mapping indexes.
    std::vector<std::pair<int, int> > paramToAttrList;
    std::vector<std::pair<int, int> > errorToMarkerList;
    std::vector<MPoint> markerPosList;
    std::vector<double> markerWeightList;

    // Internal Solver Data.
    std::vector<double> errorList;
    std::vector<double> errorDistanceList;
    int iterNum;
    int jacIterNum;
    int iterMax;
    int solverType;
    bool isJacobianCalculation;
    double imageWidth;

    // Error Thresholds.
    double tau;
    double eps1;
    double eps2;
    double eps3;
    double delta;

    // Benchmarks
    debug::TimestampBenchmark *jacBenchTimer;
    debug::TimestampBenchmark *funcBenchTimer;
    debug::TimestampBenchmark *errorBenchTimer;
    debug::TimestampBenchmark *paramBenchTimer;
    debug::CPUBenchmark *jacBenchTicks;
    debug::CPUBenchmark *funcBenchTicks;
    debug::CPUBenchmark *errorBenchTicks;
    debug::CPUBenchmark *paramBenchTicks;

    // Storing changes for undo/redo.
    MDGModifier *dgmod;
    MAnimCurveChange *curveChange;

    // Allow user to cancel the solve.
    MComputation *computation;

    // Verbosity.
    bool verbose;
};
*/

int solveFunc_cminpack_lm(void *data,
                          int n,
                          int m,
                          const double *p,
                          double *x,
                          int iflag);

#endif // MAYA_MM_SOLVER_CMINPACK_H
