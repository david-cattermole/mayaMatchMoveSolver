/*
 * Uses Non-Linear Least Squares algorithm from levmar library to calculate attribute values based on 2D-to-3D error measurements through a pinhole camera.
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

//
#include <mmSolver.h>


// Sparse LM or Lev-Mar Termination Reasons:
const std::string reasons[8] = {
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


// The user data given to levmar.
struct LevMarSolverData {
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
 #if USE_EXPERIMENTAL_SOLVER == 1
    BoolList2D errorToParamMapping;
 #endif

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


void levmarSolveFunc(double *p, double *x, int m, int n, void *data);

void levmarSolveJacFunc(double *p, double *x, int m, int n, void *data);

void levmarSolveOptimiseFunc(double *p, double *x, int m, int n, void *data);

void levmarSolveJacOptimiseFunc(double *p, double *x, int m, int n, void *data);

#endif // MAYA_MM_SOLVER_LEVMAR_H
