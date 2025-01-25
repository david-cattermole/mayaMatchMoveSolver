/*
 * Copyright (C) 2018, 2019, 2020, 2025 David Cattermole.
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
 * Calculates the graph relationships between Errors (Markers) and
 * Parameters (Attributes).
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_DEFINES_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_DEFINES_H

// The number of errors that are measured per-marker.
// There are two measurements per-marker, X and Y.
//
// 3 measurements were used in the past with
// success, but tests now prove 2 to reduce error with less
// iterations, and is significantly faster overall.
//
// Do not change this definition.
#define ERRORS_PER_MARKER (2)

// The different solver types to choose from:

// Dense LM solver using 'levmar',
#define SOLVER_TYPE_LEVMAR (0)
#define SOLVER_TYPE_LEVMAR_NAME "levmar"

// Dense LM solver using 'cminpack' library.
#define SOLVER_TYPE_CMINPACK_LMDIF (1)
#define SOLVER_TYPE_CMINPACK_LMDIF_NAME "cminpack_lmdif"

// Dense LM solver, with custom jacobian, using 'cminpack' library.
#define SOLVER_TYPE_CMINPACK_LMDER (2)
#define SOLVER_TYPE_CMINPACK_LMDER_NAME "cminpack_lmder"

// Dense LM solver using 'ceres' using a trust-region
// Levenberg-Marquardt algorithm.
#define SOLVER_TYPE_CERES_LMDIF (3)
#define SOLVER_TYPE_CERES_LMDIF_NAME "ceres_lmdif"

// The default solver to use, if all solvers are available.
#define SOLVER_TYPE_DEFAULT_VALUE SOLVER_TYPE_CMINPACK_LMDER

// // Enable the Maya profiling data collection.
// #define MAYA_PROFILE 1

// Text character used to split up a single result string.
#define CMD_RESULT_SPLIT_CHAR "#"

// How to evaluate values at different times?
//
// These are the possible values:
#define TIME_EVAL_MODE_DG_CONTEXT (0)
#define TIME_EVAL_MODE_SET_TIME (1)

// What Scene Graph should we use for evaluation?
//
// These are the possible values:
#define SCENE_GRAPH_MODE_MAYA_DAG (1)
#define SCENE_GRAPH_MODE_MM_SCENE_GRAPH (2)
// The default value
#define SCENE_GRAPH_MODE_DEFAULT_VALUE SCENE_GRAPH_MODE_MAYA_DAG

// How the list of frames is solved.
//
// These are the possible values:
#define FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE (0)
#define FRAME_SOLVE_MODE_PER_FRAME (1)
// The default value
#define FRAME_SOLVE_MODE_DEFAULT_VALUE FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE

// Print Statistics for mmSolver command.
//
// These are the possible values:
#define PRINT_STATS_MODE_INPUTS "inputs"
#define PRINT_STATS_MODE_AFFECTS "affects"
#define PRINT_STATS_MODE_USED_SOLVE_OBJECTS "usedSolveObjects"
#define PRINT_STATS_MODE_DEVIATION "deviation"
// #define PRINT_STATS_MODE_SOLVE_FRAMES "solveFrames"

// Robust Loss Function Types.
//
#define ROBUST_LOSS_TYPE_TRIVIAL (0)
#define ROBUST_LOSS_TYPE_SOFT_L_ONE (1)
#define ROBUST_LOSS_TYPE_CAUCHY (2)

// CMinpack-specific values for recognising forward or central differencing.
//
#define AUTO_DIFF_TYPE_FORWARD (0)
#define AUTO_DIFF_TYPE_CENTRAL (1)

// CMinpack lmdif Solver default flag values
//
#define CMINPACK_LMDIF_ITERATIONS_DEFAULT_VALUE (100)
#define CMINPACK_LMDIF_TAU_DEFAULT_VALUE (1.0)
#define CMINPACK_LMDIF_EPSILON1_DEFAULT_VALUE (1E-6)  // ftol
#define CMINPACK_LMDIF_EPSILON2_DEFAULT_VALUE (1E-6)  // xtol
#define CMINPACK_LMDIF_EPSILON3_DEFAULT_VALUE (1E-6)  // gtol
#define CMINPACK_LMDIF_DELTA_DEFAULT_VALUE (1E-04)
// cminpack lmdif only supports forward '0=forward' differentiation.
#define CMINPACK_LMDIF_AUTO_DIFF_TYPE_DEFAULT_VALUE (AUTO_DIFF_TYPE_FORWARD)
#define CMINPACK_LMDIF_AUTO_PARAM_SCALE_DEFAULT_VALUE \
    (1)  // default is 'on=1 (mode=1)'
#define CMINPACK_LMDIF_ROBUST_LOSS_TYPE_DEFAULT_VALUE (ROBUST_LOSS_TYPE_TRIVIAL)
#define CMINPACK_LMDIF_ROBUST_LOSS_SCALE_DEFAULT_VALUE (1.0)
// TODO: Technically this is actually for finite-differentiation, not
// auto-differentiation
#define CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_FORWARD_VALUE true
#define CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_CENTRAL_VALUE false
#define CMINPACK_LMDIF_SUPPORT_PARAMETER_BOUNDS_VALUE true
#define CMINPACK_LMDIF_SUPPORT_ROBUST_LOSS_VALUE false

// CMinpack lmder Solver default flag values
//
#define CMINPACK_LMDER_ITERATIONS_DEFAULT_VALUE (100)
#define CMINPACK_LMDER_TAU_DEFAULT_VALUE (1.0)
#define CMINPACK_LMDER_EPSILON1_DEFAULT_VALUE (1E-6)  // ftol
#define CMINPACK_LMDER_EPSILON2_DEFAULT_VALUE (1E-6)  // xtol
#define CMINPACK_LMDER_EPSILON3_DEFAULT_VALUE (1E-6)  // gtol
#define CMINPACK_LMDER_DELTA_DEFAULT_VALUE (1E-04)
// cminpack lmder supports both forward '0=forward' and 'central' auto-diff'ing.
#define CMINPACK_LMDER_AUTO_DIFF_TYPE_DEFAULT_VALUE (AUTO_DIFF_TYPE_FORWARD)
#define CMINPACK_LMDER_AUTO_PARAM_SCALE_DEFAULT_VALUE \
    (1)  // default is 'on=1 (mode=1)'
#define CMINPACK_LMDER_ROBUST_LOSS_TYPE_DEFAULT_VALUE (ROBUST_LOSS_TYPE_TRIVIAL)
#define CMINPACK_LMDER_ROBUST_LOSS_SCALE_DEFAULT_VALUE (1.0)
// TODO: Technically this is actually for finite-differentiation, not
// auto-differentiation
#define CMINPACK_LMDER_SUPPORT_AUTO_DIFF_FORWARD_VALUE true
#define CMINPACK_LMDER_SUPPORT_AUTO_DIFF_CENTRAL_VALUE true
#define CMINPACK_LMDER_SUPPORT_PARAMETER_BOUNDS_VALUE true
#define CMINPACK_LMDER_SUPPORT_ROBUST_LOSS_VALUE false

// Ceres Levenberg-Marquardt Solver default flag values.
//
#define CERES_LMDIF_ITERATIONS_DEFAULT_VALUE (100)
#define CERES_LMDIF_TAU_DEFAULT_VALUE (1E4)
#define CERES_LMDIF_EPSILON1_DEFAULT_VALUE (1E-6)   // function_tolerance
#define CERES_LMDIF_EPSILON2_DEFAULT_VALUE (1E-10)  // parameter_tolerance
#define CERES_LMDIF_EPSILON3_DEFAULT_VALUE (1E-8)   // gradient_tolerance
#define CERES_LMDIF_DELTA_DEFAULT_VALUE (1E-04)
// cminpack lmder supports both forward '0=forward' and 'central' auto-diff'ing.
#define CERES_LMDIF_AUTO_DIFF_TYPE_DEFAULT_VALUE (AUTO_DIFF_TYPE_FORWARD)
#define CERES_LMDIF_AUTO_PARAM_SCALE_DEFAULT_VALUE \
    (1)  // default is 'on=1 (mode=1)'
#define CERES_LMDIF_ROBUST_LOSS_TYPE_DEFAULT_VALUE (ROBUST_LOSS_TYPE_TRIVIAL)
#define CERES_LMDIF_ROBUST_LOSS_SCALE_DEFAULT_VALUE (1.0)
// TODO: Technically this is actually for finite-differentiation, not
// auto-differentiation
#define CERES_LMDIF_SUPPORT_AUTO_DIFF_FORWARD_VALUE false
#define CERES_LMDIF_SUPPORT_AUTO_DIFF_CENTRAL_VALUE false
#define CERES_LMDIF_SUPPORT_PARAMETER_BOUNDS_VALUE false
#define CERES_LMDIF_SUPPORT_ROBUST_LOSS_VALUE false

// Levmar Solver default flag values
//
#define LEVMAR_ITERATIONS_DEFAULT_VALUE (100)
#define LEVMAR_TAU_DEFAULT_VALUE (1.0)
#define LEVMAR_EPSILON1_DEFAULT_VALUE (1E-6)
#define LEVMAR_EPSILON2_DEFAULT_VALUE (1E-6)
#define LEVMAR_EPSILON3_DEFAULT_VALUE (1E-6)
#define LEVMAR_DELTA_DEFAULT_VALUE (1E-04)
#define LEVMAR_AUTO_DIFF_TYPE_DEFAULT_VALUE (AUTO_DIFF_TYPE_FORWARD)
// LevMar does not have auto-parameter scaling.
#define LEVMAR_AUTO_PARAM_SCALE_DEFAULT_VALUE (0)
#define LEVMAR_ROBUST_LOSS_TYPE_DEFAULT_VALUE (ROBUST_LOSS_TYPE_TRIVIAL)
#define LEVMAR_ROBUST_LOSS_SCALE_DEFAULT_VALUE (1.0)
// TODO: Technically this is actually for finite-differentiation, not
// auto-differentiation
#define LEVMAR_SUPPORT_AUTO_DIFF_FORWARD_VALUE true
#define LEVMAR_SUPPORT_AUTO_DIFF_CENTRAL_VALUE true
#define LEVMAR_SUPPORT_PARAMETER_BOUNDS_VALUE true
#define LEVMAR_SUPPORT_ROBUST_LOSS_VALUE false

// Allow mmSolver to compute lens distortion during the solve. These
// are compile time flags for debugging.
//
// Note: If 'MMSOLVER_LENS_DISTORTION' is disabled both
// 'MMSOLVER_LENS_DISTORTION_MAYA_DAG' and
// 'MMSOLVER_LENS_DISTORTION_MM_SCENE_GRAPH' should be considered
// disabled too.
#define MMSOLVER_LENS_DISTORTION (1)
#define MMSOLVER_LENS_DISTORTION_MAYA_DAG (1)
#define MMSOLVER_LENS_DISTORTION_MM_SCENE_GRAPH (1)

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_DEFINES_H
