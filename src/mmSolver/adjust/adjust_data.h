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

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_DATA_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_DATA_H

// STL
#include <fstream>
#include <iostream>
#include <memory>
#include <string>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>
#include <maya/MDGModifier.h>
#include <maya/MGlobal.h>
#include <maya/MPoint.h>
#include <maya/MStringArray.h>

// MM Solver Libs
#include <mmsolverlibs/debug.h>

// MM Scene Graph
#include <mmscenegraph/mmscenegraph.h>

// MM Solver
#include <mmlens/lens_model.h>

#include "adjust_defines.h"
#include "mmSolver/core/matrix_bool_2d.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"
#include "mmSolver/utilities/debug_utils.h"

// Group all the benchmark timers together.
struct SolverTimer {
    mmsolver::debug::Timestamp startTimestamp;

    mmsolver::debug::TimestampBenchmark solveBenchTimer;
    mmsolver::debug::TimestampBenchmark jacBenchTimer;
    mmsolver::debug::TimestampBenchmark funcBenchTimer;
    mmsolver::debug::TimestampBenchmark errorBenchTimer;
    mmsolver::debug::TimestampBenchmark paramBenchTimer;

    mmsolver::debug::CPUBenchmark solveBenchTicks;
    mmsolver::debug::CPUBenchmark jacBenchTicks;
    mmsolver::debug::CPUBenchmark funcBenchTicks;
    mmsolver::debug::CPUBenchmark errorBenchTicks;
    mmsolver::debug::CPUBenchmark paramBenchTicks;
};

enum class FrameSolveMode {
    kPerFrame = FRAME_SOLVE_MODE_PER_FRAME,
    kAllFrameAtOnce = FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE,
    kNumFrameSolveMode,
};

enum class SceneGraphMode {
    kMayaDag = SCENE_GRAPH_MODE_MAYA_DAG,
    kMMSceneGraph = SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
    kNumSceneGraphModes,
};

// Logging level for mmSolver command.
//
// Each entry is treated as a number with higher numbers being more verbose.
//
// NOTE: These values must match the values in the Python
// LOG_LEVEL_NAME_TO_VALUE_MAP dictionary, see
// ./python/mmSolver/_api/constant.py
enum class LogLevel {
    kError = 0,
    kWarning,
    kInfo,
    kVerbose,
    kDebug,
    kNumLogLevels,
};

struct PrintStatOptions {
    // Do not actually solve anything, just stop after preparing to
    // solve, because we have already calculated all the data needed
    // to print statistics.
    bool doNotSolve;

    // Prints details about how many object counts are used; number of
    // paramters, number of errors, number of marker errors, and
    // smoothness/stiffness error counts.
    bool input;

    // Prints a 2D matrix of Markers and Attributes, which markers
    // affect which attributes?
    bool affects;

    // If true, prints solve object usage. For example, which markers
    // are used or unused, and which attributes are used or unused.
    bool usedSolveObjects;

    // Print deviation details; the individual error values reported
    // from the solver, per-frame and per-marker-per-frame.
    bool deviation;

    PrintStatOptions()
        : doNotSolve(false)
        , input(false)
        , affects(false)
        , usedSolveObjects(false)
        , deviation(false) {}
};

struct SolverOptions {
    int iterMax;
    double tau;
    double function_tolerance;
    double parameter_tolerance;
    double gradient_tolerance;
    double delta;
    int autoDiffType;
    int autoParamScale;
    int robustLossType;
    double robustLossScale;
    SceneGraphMode sceneGraphMode;
    int solverType;
    int timeEvalMode;
    bool acceptOnlyBetter;
    double imageWidth;
    FrameSolveMode frameSolveMode;

    // Auto-adjust the input solve objects before solving?
    bool removeUnusedMarkers;
    bool removeUnusedAttributes;

    // All the different supported features by the currently active
    // solver type.
    bool solverSupportsAutoDiffForward;
    bool solverSupportsAutoDiffCentral;
    bool solverSupportsParameterBounds;
    bool solverSupportsRobustLoss;

    SolverOptions()
        : iterMax(0)
        , tau(0.0)
        , function_tolerance(0.0)
        , parameter_tolerance(0.0)
        , gradient_tolerance(0.0)
        , delta(0.0)
        , autoDiffType(AUTO_DIFF_TYPE_FORWARD)
        , autoParamScale(0)
        , robustLossType(ROBUST_LOSS_TYPE_TRIVIAL)
        , robustLossScale(1.0)
        , sceneGraphMode(SceneGraphMode::kMayaDag)
        , solverType(SOLVER_TYPE_DEFAULT_VALUE)
        , timeEvalMode(TIME_EVAL_MODE_DG_CONTEXT)
        , acceptOnlyBetter(false)
        , imageWidth(1.0)
        , frameSolveMode(FrameSolveMode::kAllFrameAtOnce)
        , removeUnusedMarkers(false)
        , removeUnusedAttributes(false)
        , solverSupportsAutoDiffForward(false)
        , solverSupportsAutoDiffCentral(false)
        , solverSupportsParameterBounds(false)
        , solverSupportsRobustLoss(false) {}
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

    // Lens Distortion
    std::vector<std::shared_ptr<mmlens::LensModel>> markerFrameToLensModelList;
    std::vector<std::shared_ptr<mmlens::LensModel>> attrFrameToLensModelList;
    std::vector<std::shared_ptr<mmlens::LensModel>> lensModelList;

    // MM Scene Graph
    mmscenegraph::SceneGraph mmsgSceneGraph;
    mmscenegraph::AttrDataBlock mmsgAttrDataBlock;
    std::vector<mmscenegraph::FrameValue> mmsgFrameList;
    mmscenegraph::FlatScene mmsgFlatScene;
    std::vector<mmscenegraph::CameraNode> mmsgCameraNodes;
    std::vector<mmscenegraph::BundleNode> mmsgBundleNodes;
    std::vector<mmscenegraph::MarkerNode> mmsgMarkerNodes;
    std::vector<mmscenegraph::AttrId> mmsgAttrIdList;

    // Relational mapping indexes.
    std::vector<std::pair<int, int>> paramToAttrList;
    std::vector<std::pair<int, int>> errorToMarkerList;
    std::vector<MPoint> markerPosList;
    std::vector<double> markerWeightList;
    mmsolver::MatrixBool2D paramFrameList;
    mmsolver::MatrixBool2D errorToParamList;

    // Internal Solver Data.
    std::vector<double> paramList;
    std::vector<double> errorList;
    std::vector<double> errorDistanceList;
    std::vector<double> jacobianList;
    std::vector<double> previousParamList;
    int funcEvalNum;
    int iterNum;
    int jacIterNum;
    int solverType;
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

    LogLevel logLevel;

    SolverData()
        : funcEvalNum(0)
        , iterNum(0)
        , jacIterNum(0)
        , solverType(SOLVER_TYPE_DEFAULT_VALUE)
        , numberOfMarkerErrors(0)
        , numberOfAttrStiffnessErrors(0)
        , numberOfAttrSmoothnessErrors(0)
        , isNormalCall(false)
        , isJacobianCall(false)
        , isPrintCall(false)
        , doCalcJacobian(false)
        , solverOptions(nullptr)
        , timer()
        , dgmod(nullptr)
        , curveChange(nullptr)
        , computation(nullptr)
        , userInterrupted(false)
        , logLevel(LogLevel::kInfo){};
};

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_DATA_H
