/*
 * Copyright (C) 2019 David Cattermole.
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
 * Common data structures for all bundle adjustment algorithms.
 */


#ifndef MAYA_MM_SOLVER_CORE_BUNDLE_ADJUST_DATA_H
#define MAYA_MM_SOLVER_CORE_BUNDLE_ADJUST_DATA_H

// STL
#include <string>
#include <vector> 
#include <iostream>
#include <fstream>

// Utils
#include <utilities/debugUtils.h>

// Maya
#include <maya/MGlobal.h>
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


// Group all the benchmark timers together.
struct SolverTimer {
    debug::TimestampBenchmark solveBenchTimer;
    debug::TimestampBenchmark jacBenchTimer;
    debug::TimestampBenchmark funcBenchTimer;
    debug::TimestampBenchmark errorBenchTimer;
    debug::TimestampBenchmark paramBenchTimer;

    debug::CPUBenchmark solveBenchTicks;
    debug::CPUBenchmark jacBenchTicks;
    debug::CPUBenchmark funcBenchTicks;
    debug::CPUBenchmark errorBenchTicks;
    debug::CPUBenchmark paramBenchTicks;
};


struct SolverOptions {
    int iterMax;
    double tau;
    double eps1;
    double eps2;
    double eps3;
    double delta;
    int autoDiffType;
    int autoParamScale;
    int robustLossType;
    double robustLossScale;
    int solverType;
    bool acceptOnlyBetter;

    // All the different supported features by the currently active
    // solver type.
    bool solverSupportsAutoDiffForward;
    bool solverSupportsAutoDiffCentral;
    bool solverSupportsParameterBounds;
    bool solverSupportsRobustLoss;
};


// The user data given to the solve function.
struct SolverData {
    // Solver Objects.
    CameraPtrList cameraList;
    MarkerPtrList markerList;
    BundlePtrList bundleList;
    AttrPtrList attrList;
    MTimeArray frameList;  // Times to solve
    SmoothAttrsPtrList smoothAttrsList;
    StiffAttrsPtrList stiffAttrsList;

    // Relational mapping indexes.
    std::vector<std::pair<int, int> > paramToAttrList;
    std::vector<std::pair<int, int> > errorToMarkerList;
    std::vector<MPoint> markerPosList;
    std::vector<double> markerWeightList;

    // Internal Solver Data.
    std::vector<double> paramList;
    std::vector<double> errorList;
    std::vector<double> errorDistanceList;
    std::vector<double> jacobianList;
    int funcEvalNum;
    int iterNum;
    int jacIterNum;
    int solverType;
    double imageWidth;
    int numberOfMarkerErrors;
    int numberOfAttrStiffnessErrors;
    int numberOfAttrSmoothnessErrors;

    // Type of solve function call.
    bool isNormalCall;
    bool isJacobianCall;
    bool isPrintCall;
    bool doCalcJacobian;

    // Solver Options
    SolverOptions *solverOptions;

    // Benchmarks
    SolverTimer timer;

    // Storing changes for undo/redo.
    MDGModifier *dgmod;
    MAnimCurveChange *curveChange;

    // Allow user to cancel the solve.
    MComputation *computation;
    bool userInterrupted;

    // Maya is running as an interactive or batch?
    MGlobal::MMayaState mayaSessionState;

    // Verbosity.
    bool verbose;
    MString debugFileName;
};


struct SolverResult {
    bool success;
    double errorAvg;
    double errorMin;
    double errorMax;
    int reason_number;
    std::string reason;
    int iterations;
    int functionEvals;
    int jacobianEvals;
    double errorFinal;
};

#endif // MAYA_MM_SOLVER_CORE_BUNDLE_ADJUST_DATA_H
