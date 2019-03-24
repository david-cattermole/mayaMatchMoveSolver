/*
 *
 */


#ifndef MAYA_MM_SOLVER_FUNC_H
#define MAYA_MM_SOLVER_FUNC_H

// STL
#include <string>    // string
#include <vector>    // vector
#include <iostream>  // cout, cerr, endl
#include <fstream>   // ofstream

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

// success / failure constants.
#define SOLVE_FUNC_SUCCESS 0
#define SOLVE_FUNC_FAILURE -1


// The user data given to the solve function.
struct SolverData {
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
    double imageWidth;

    // Type of solve function call.
    bool isNormalCall;
    bool isJacobianCall;
    bool isPrintCall;

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
    MString debugFileName;
};

int solveFunc(int numberOfParameters,
              int numberOfErrors,
              const double *parameters,
              double *errors,
              void *userData);

#endif // MAYA_MM_SOLVER_FUNC_H
