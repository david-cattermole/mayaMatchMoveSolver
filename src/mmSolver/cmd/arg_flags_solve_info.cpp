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

#include "arg_flags_solve_info.h"

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// Internal Objects
#include "arg_flags_solve_scene_graph.h"
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/adjust/adjust_data.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

void createSolveInfoSyntax_solverType(MSyntax &syntax) {
    syntax.addFlag(TAU_FLAG, TAU_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(FUNCTION_TOLERANCE_FLAG, FUNCTION_TOLERANCE_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(PARAMETER_TOLERANCE_FLAG, PARAMETER_TOLERANCE_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(GRADIENT_TOLERANCE_FLAG, GRADIENT_TOLERANCE_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(DELTA_FLAG, DELTA_FLAG_LONG, MSyntax::kDouble);
    syntax.addFlag(AUTO_DIFF_TYPE_FLAG, AUTO_DIFF_TYPE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(AUTO_PARAM_SCALE_FLAG, AUTO_PARAM_SCALE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ROBUST_LOSS_TYPE_FLAG, ROBUST_LOSS_TYPE_FLAG_LONG,
                   MSyntax::kUnsigned);
    syntax.addFlag(ROBUST_LOSS_SCALE_FLAG, ROBUST_LOSS_SCALE_FLAG_LONG,
                   MSyntax::kDouble);
    syntax.addFlag(SOLVER_TYPE_FLAG, SOLVER_TYPE_FLAG_LONG, MSyntax::kUnsigned);
    syntax.addFlag(ITERATIONS_FLAG, ITERATIONS_FLAG_LONG, MSyntax::kUnsigned);
}

void createSolveInfoSyntax_other(MSyntax &syntax) {
    syntax.addFlag(ACCEPT_ONLY_BETTER_FLAG, ACCEPT_ONLY_BETTER_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(FRAME_SOLVE_MODE_FLAG, FRAME_SOLVE_MODE_FLAG_LONG,
                   MSyntax::kUnsigned);

    syntax.addFlag(IMAGE_WIDTH_FLAG, IMAGE_WIDTH_FLAG_LONG, MSyntax::kDouble);

    createSolveSceneGraphSyntax(syntax);
    syntax.addFlag(TIME_EVAL_MODE_FLAG, TIME_EVAL_MODE_FLAG_LONG,
                   MSyntax::kUnsigned);
}

void createSolveInfoSyntax_removeUnused(MSyntax &syntax) {
    syntax.addFlag(REMOVE_UNUSED_MARKERS_FLAG, REMOVE_UNUSED_MARKERS_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(REMOVE_UNUSED_ATTRIBUTES_FLAG,
                   REMOVE_UNUSED_ATTRIBUTES_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(REMOVE_UNUSED_FRAMES_FLAG, REMOVE_UNUSED_FRAMES_FLAG_LONG,
                   MSyntax::kBoolean);
}

void createSolveInfoSyntax_v1(MSyntax &syntax) {
    createSolveInfoSyntax_solverType(syntax);
    createSolveInfoSyntax_removeUnused(syntax);
    createSolveInfoSyntax_other(syntax);
}

void createSolveInfoSyntax_v2(MSyntax &syntax) {
    createSolveInfoSyntax_solverType(syntax);
    createSolveInfoSyntax_other(syntax);
}

void createSolveInfoSyntax(MSyntax &syntax, const int command_version = 0) {
    if (command_version == 2) {
        createSolveInfoSyntax_v2(syntax);
    } else {
        createSolveInfoSyntax_v1(syntax);
    }
}

MStatus parseSolveInfoArguments_solverType(
    const MArgDatabase &argData, int &out_iterations, double &out_tau,
    double &out_function_tolerance, double &out_parameter_tolerance,
    double &out_gradient_tolerance, double &out_delta, int &out_autoDiffType,
    int &out_autoParamScale, int &out_robustLossType,
    double &out_robustLossScale, int &out_solverType,
    bool &out_supportAutoDiffForward, bool &out_supportAutoDiffCentral,
    bool &out_supportParameterBounds, bool &out_supportRobustLoss) {
    MStatus status = MStatus::kSuccess;

    // Get 'Solver Type'
    SolverTypePair solverType = getSolverTypeDefault();
    out_solverType = solverType.first;
    if (argData.isFlagSet(SOLVER_TYPE_FLAG)) {
        status = argData.getFlagArgument(SOLVER_TYPE_FLAG, 0, out_solverType);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Tau values represent the range of values that the solver can
    // explore. Larger values take bigger "steps", while smaller
    // values take smaller "steps".
    //
    // Tau value ranges are dependent on the implementation for each
    // solver.
    double tau_min_value = 0.0;
    double tau_max_value = 0.0;

    // Set defaults based on solver type chosen.
    //
    // TODO: Can we set these default values using a struct of some
    // sort? I think we should move these hard-coded values into
    // solver-specific files, especially for the "support*" arguments.
    if (out_solverType == SOLVER_TYPE_CMINPACK_LMDIF) {
        out_iterations = CMINPACK_LMDIF_ITERATIONS_DEFAULT_VALUE;
        out_tau = CMINPACK_LMDIF_TAU_DEFAULT_VALUE;
        out_function_tolerance =
            CMINPACK_LMDIF_FUNCTION_TOLERANCE_DEFAULT_VALUE;
        out_parameter_tolerance =
            CMINPACK_LMDIF_PARAMETER_TOLERANCE_DEFAULT_VALUE;
        out_gradient_tolerance =
            CMINPACK_LMDIF_GRADIENT_TOLERANCE_DEFAULT_VALUE;
        out_delta = CMINPACK_LMDIF_DELTA_DEFAULT_VALUE;
        out_autoDiffType = CMINPACK_LMDIF_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        out_autoParamScale = CMINPACK_LMDIF_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        out_robustLossType = CMINPACK_LMDIF_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        out_robustLossScale = CMINPACK_LMDIF_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        // TODO: Technically this is actually for
        // finite-differentiation, not auto-differentiation
        out_supportAutoDiffForward =
            CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        out_supportAutoDiffCentral =
            CMINPACK_LMDIF_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        out_supportParameterBounds =
            CMINPACK_LMDIF_SUPPORT_PARAMETER_BOUNDS_VALUE;
        out_supportRobustLoss = CMINPACK_LMDIF_SUPPORT_ROBUST_LOSS_VALUE;

        tau_min_value = 0.0;
        tau_max_value = 1.0;
    } else if (out_solverType == SOLVER_TYPE_CMINPACK_LMDER) {
        out_iterations = CMINPACK_LMDER_ITERATIONS_DEFAULT_VALUE;
        out_tau = CMINPACK_LMDER_TAU_DEFAULT_VALUE;
        out_function_tolerance =
            CMINPACK_LMDER_FUNCTION_TOLERANCE_DEFAULT_VALUE;
        out_parameter_tolerance =
            CMINPACK_LMDER_PARAMETER_TOLERANCE_DEFAULT_VALUE;
        out_gradient_tolerance =
            CMINPACK_LMDER_GRADIENT_TOLERANCE_DEFAULT_VALUE;
        out_delta = CMINPACK_LMDER_DELTA_DEFAULT_VALUE;
        out_autoDiffType = CMINPACK_LMDER_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        out_autoParamScale = CMINPACK_LMDER_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        out_robustLossType = CMINPACK_LMDER_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        out_robustLossScale = CMINPACK_LMDER_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        // TODO: Technically this is actually for
        // finite-differentiation, not auto-differentiation
        out_supportAutoDiffForward =
            CMINPACK_LMDER_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        out_supportAutoDiffCentral =
            CMINPACK_LMDER_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        out_supportParameterBounds =
            CMINPACK_LMDER_SUPPORT_PARAMETER_BOUNDS_VALUE;
        out_supportRobustLoss = CMINPACK_LMDER_SUPPORT_ROBUST_LOSS_VALUE;

        tau_min_value = 0.0;
        tau_max_value = 1.0;
    } else if (out_solverType == SOLVER_TYPE_CERES_LMDIF) {
        out_iterations = CERES_LMDIF_ITERATIONS_DEFAULT_VALUE;
        out_tau = CERES_LMDIF_TAU_DEFAULT_VALUE;
        out_function_tolerance = CERES_LMDIF_FUNCTION_TOLERANCE_DEFAULT_VALUE;
        out_parameter_tolerance = CERES_LMDIF_PARAMETER_TOLERANCE_DEFAULT_VALUE;
        out_gradient_tolerance = CERES_LMDIF_GRADIENT_TOLERANCE_DEFAULT_VALUE;
        out_delta = CERES_LMDIF_DELTA_DEFAULT_VALUE;
        out_autoDiffType = CERES_LMDIF_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        out_autoParamScale = CERES_LMDIF_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        out_robustLossType = CERES_LMDIF_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        out_robustLossScale = CERES_LMDIF_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        // TODO: Technically this is actually for
        // finite-differentiation, not auto-differentiation
        out_supportAutoDiffForward =
            CERES_LMDIF_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        out_supportAutoDiffCentral =
            CERES_LMDIF_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        out_supportParameterBounds = CERES_LMDIF_SUPPORT_PARAMETER_BOUNDS_VALUE;
        out_supportRobustLoss = CERES_LMDIF_SUPPORT_ROBUST_LOSS_VALUE;

        // http://ceres-solver.org/nnls_solving.html#_CPPv4N5ceres6Solver7Options23min_trust_region_radiusE
        tau_min_value = 1e-32;

        // http://ceres-solver.org/nnls_solving.html#_CPPv4N5ceres6Solver7Options23max_trust_region_radiusE
        tau_max_value = 1e16;
    } else if (out_solverType == SOLVER_TYPE_CERES_LMDER) {
        out_iterations = CERES_LMDER_ITERATIONS_DEFAULT_VALUE;
        out_tau = CERES_LMDER_TAU_DEFAULT_VALUE;
        out_function_tolerance = CERES_LMDER_FUNCTION_TOLERANCE_DEFAULT_VALUE;
        out_parameter_tolerance = CERES_LMDER_PARAMETER_TOLERANCE_DEFAULT_VALUE;
        out_gradient_tolerance = CERES_LMDER_GRADIENT_TOLERANCE_DEFAULT_VALUE;
        out_delta = CERES_LMDER_DELTA_DEFAULT_VALUE;
        out_autoDiffType = CERES_LMDER_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        out_autoParamScale = CERES_LMDER_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        out_robustLossType = CERES_LMDER_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        out_robustLossScale = CERES_LMDER_ROBUST_LOSS_SCALE_DEFAULT_VALUE;

        // TODO: Technically this is actually for
        // finite-differentiation, not auto-differentiation
        out_supportAutoDiffForward =
            CERES_LMDER_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        out_supportAutoDiffCentral =
            CERES_LMDER_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        out_supportParameterBounds = CERES_LMDER_SUPPORT_PARAMETER_BOUNDS_VALUE;
        out_supportRobustLoss = CERES_LMDER_SUPPORT_ROBUST_LOSS_VALUE;

        // http://ceres-solver.org/nnls_solving.html#_CPPv4N5ceres6Solver7Options23min_trust_region_radiusE
        tau_min_value = 1e-32;

        // http://ceres-solver.org/nnls_solving.html#_CPPv4N5ceres6Solver7Options23max_trust_region_radiusE
        tau_max_value = 1e16;

    } else if (out_solverType == SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER) {
        out_iterations = CERES_LINE_SEARCH_LBFGS_DER_ITERATIONS_DEFAULT_VALUE;
        out_tau = CERES_LINE_SEARCH_LBFGS_DER_TAU_DEFAULT_VALUE;
        out_function_tolerance =
            CERES_LINE_SEARCH_LBFGS_DER_FUNCTION_TOLERANCE_DEFAULT_VALUE;
        out_parameter_tolerance =
            CERES_LINE_SEARCH_LBFGS_DER_PARAMETER_TOLERANCE_DEFAULT_VALUE;
        out_gradient_tolerance =
            CERES_LINE_SEARCH_LBFGS_DER_GRADIENT_TOLERANCE_DEFAULT_VALUE;
        out_delta = CERES_LINE_SEARCH_LBFGS_DER_DELTA_DEFAULT_VALUE;
        out_autoDiffType =
            CERES_LINE_SEARCH_LBFGS_DER_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        out_autoParamScale =
            CERES_LINE_SEARCH_LBFGS_DER_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        out_robustLossType =
            CERES_LINE_SEARCH_LBFGS_DER_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        out_robustLossScale =
            CERES_LINE_SEARCH_LBFGS_DER_ROBUST_LOSS_SCALE_DEFAULT_VALUE;

        // TODO: Technically this is actually for
        // finite-differentiation, not auto-differentiation
        out_supportAutoDiffForward =
            CERES_LINE_SEARCH_LBFGS_DER_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        out_supportAutoDiffCentral =
            CERES_LINE_SEARCH_LBFGS_DER_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        out_supportParameterBounds =
            CERES_LINE_SEARCH_LBFGS_DER_SUPPORT_PARAMETER_BOUNDS_VALUE;
        out_supportRobustLoss =
            CERES_LINE_SEARCH_LBFGS_DER_SUPPORT_ROBUST_LOSS_VALUE;

        // http://ceres-solver.org/nnls_solving.html#_CPPv4N5ceres6Solver7Options23min_trust_region_radiusE
        tau_min_value = 1e-32;

        // http://ceres-solver.org/nnls_solving.html#_CPPv4N5ceres6Solver7Options23max_trust_region_radiusE
        tau_max_value = 1e16;

    } else if (out_solverType == SOLVER_TYPE_LEVMAR) {
        out_iterations = LEVMAR_ITERATIONS_DEFAULT_VALUE;
        out_tau = LEVMAR_TAU_DEFAULT_VALUE;
        out_function_tolerance = LEVMAR_FUNCTION_TOLERANCE_DEFAULT_VALUE;
        out_parameter_tolerance = LEVMAR_PARAMETER_TOLERANCE_DEFAULT_VALUE;
        out_gradient_tolerance = LEVMAR_GRADIENT_TOLERANCE_DEFAULT_VALUE;
        out_delta = LEVMAR_DELTA_DEFAULT_VALUE;
        out_autoDiffType = LEVMAR_AUTO_DIFF_TYPE_DEFAULT_VALUE;
        out_autoParamScale = LEVMAR_AUTO_PARAM_SCALE_DEFAULT_VALUE;
        out_robustLossType = LEVMAR_ROBUST_LOSS_TYPE_DEFAULT_VALUE;
        out_robustLossScale = LEVMAR_ROBUST_LOSS_SCALE_DEFAULT_VALUE;
        // TODO: Technically this is actually for
        // finite-differentiation, not auto-differentiation
        out_supportAutoDiffForward = LEVMAR_SUPPORT_AUTO_DIFF_FORWARD_VALUE;
        out_supportAutoDiffCentral = LEVMAR_SUPPORT_AUTO_DIFF_CENTRAL_VALUE;
        out_supportParameterBounds = LEVMAR_SUPPORT_PARAMETER_BOUNDS_VALUE;
        out_supportRobustLoss = LEVMAR_SUPPORT_ROBUST_LOSS_VALUE;

        tau_min_value = 0.0;
        tau_max_value = 1.0;
    } else {
        MMSOLVER_MAYA_ERR(
            "Solver Type is invalid. "
            "Value may be 0 to 3 "
            "(0 == levmar, "
            "1 == cminpack_lmdif, "
            "2 == cminpack_lmder, "
            "3 == ceres_lmdif, "
            "4 == ceres_lmder, or "
            "5 == ceres_line_search_lbfgs_der); "
            << "value=" << out_solverType);
        status = MS::kFailure;
        status.perror(
            "Solver Type is invalid. "
            "Value may be 0 to 3 "
            "(0 == levmar, "
            "1 == cminpack_lmdif, "
            "2 == cminpack_lmder, "
            "3 == ceres_lmdif, "
            "4 == ceres_lmder, or "
            "5 == ceres_line_search_lbfgs_der).");
        return status;
    }

    // Get 'Iterations'
    if (argData.isFlagSet(ITERATIONS_FLAG)) {
        status = argData.getFlagArgument(ITERATIONS_FLAG, 0, out_iterations);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Tau'
    if (argData.isFlagSet(TAU_FLAG)) {
        status = argData.getFlagArgument(TAU_FLAG, 0, out_tau);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    out_tau = std::max(tau_min_value, out_tau);
    out_tau = std::min(out_tau, tau_max_value);
    MMSOLVER_ASSERT((out_tau >= tau_min_value) && (out_tau <= tau_max_value),
                    "Solver Tau value must not exceed limits.");

    // Get 'Function_Tolerance'
    if (argData.isFlagSet(FUNCTION_TOLERANCE_FLAG)) {
        status = argData.getFlagArgument(FUNCTION_TOLERANCE_FLAG, 0,
                                         out_function_tolerance);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Parameter_Tolerance'
    if (argData.isFlagSet(PARAMETER_TOLERANCE_FLAG)) {
        status = argData.getFlagArgument(PARAMETER_TOLERANCE_FLAG, 0,
                                         out_parameter_tolerance);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Gradient_Tolerance'
    if (argData.isFlagSet(GRADIENT_TOLERANCE_FLAG)) {
        status = argData.getFlagArgument(GRADIENT_TOLERANCE_FLAG, 0,
                                         out_gradient_tolerance);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Delta'
    if (argData.isFlagSet(DELTA_FLAG)) {
        status = argData.getFlagArgument(DELTA_FLAG, 0, out_delta);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Auto Differencing Type'
    if (argData.isFlagSet(AUTO_DIFF_TYPE_FLAG)) {
        status =
            argData.getFlagArgument(AUTO_DIFF_TYPE_FLAG, 0, out_autoDiffType);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Auto Parameter Scaling'
    if (argData.isFlagSet(AUTO_PARAM_SCALE_FLAG)) {
        status = argData.getFlagArgument(AUTO_PARAM_SCALE_FLAG, 0,
                                         out_autoParamScale);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Robust Loss Type'
    if (argData.isFlagSet(ROBUST_LOSS_TYPE_FLAG)) {
        status = argData.getFlagArgument(ROBUST_LOSS_TYPE_FLAG, 0,
                                         out_robustLossType);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Robust Loss Scale'
    if (argData.isFlagSet(ROBUST_LOSS_SCALE_FLAG)) {
        status = argData.getFlagArgument(ROBUST_LOSS_SCALE_FLAG, 0,
                                         out_robustLossScale);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

MStatus parseSolveInfoArguments_removeUnused(const MArgDatabase &argData,
                                             bool &out_removeUnusedMarkers,
                                             bool &out_removeUnusedAttributes,
                                             bool &out_removeUnusedFrames) {
    MStatus status = MStatus::kSuccess;

    // Get 'Remove Unused Markers'
    out_removeUnusedMarkers = REMOVE_UNUSED_MARKERS_DEFAULT_VALUE;
    if (argData.isFlagSet(REMOVE_UNUSED_MARKERS_FLAG)) {
        status = argData.getFlagArgument(REMOVE_UNUSED_MARKERS_FLAG, 0,
                                         out_removeUnusedMarkers);
        MMSOLVER_CHECK_MSTATUS(status);
    }

    // Get 'Remove Unused Attributes'
    out_removeUnusedAttributes = REMOVE_UNUSED_ATTRIBUTES_DEFAULT_VALUE;
    if (argData.isFlagSet(REMOVE_UNUSED_ATTRIBUTES_FLAG)) {
        status = argData.getFlagArgument(REMOVE_UNUSED_ATTRIBUTES_FLAG, 0,
                                         out_removeUnusedAttributes);
        MMSOLVER_CHECK_MSTATUS(status);
    }

    // Get 'Remove Unused Frames'
    out_removeUnusedFrames = REMOVE_UNUSED_FRAMES_DEFAULT_VALUE;
    if (argData.isFlagSet(REMOVE_UNUSED_FRAMES_FLAG)) {
        status = argData.getFlagArgument(REMOVE_UNUSED_FRAMES_FLAG, 0,
                                         out_removeUnusedFrames);
        MMSOLVER_CHECK_MSTATUS(status);
    }

    return status;
}

MStatus parseSolveInfoArguments_other(const MArgDatabase &argData,
                                      SceneGraphMode &out_sceneGraphMode,
                                      int &out_timeEvalMode,
                                      bool &out_acceptOnlyBetter,
                                      FrameSolveMode &out_frameSolveMode,
                                      double &out_imageWidth) {
    // Get 'Scene Graph Mode'
    MStatus status = parseSolveSceneGraphArguments(argData, out_sceneGraphMode);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    // Get 'Time Evaluation Mode'
    out_timeEvalMode = TIME_EVAL_MODE_DEFAULT_VALUE;
    if (argData.isFlagSet(TIME_EVAL_MODE_FLAG)) {
        status =
            argData.getFlagArgument(TIME_EVAL_MODE_FLAG, 0, out_timeEvalMode);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    // Get 'Accept Only Better'
    out_acceptOnlyBetter = ACCEPT_ONLY_BETTER_DEFAULT_VALUE;
    if (argData.isFlagSet(ACCEPT_ONLY_BETTER_FLAG)) {
        status = argData.getFlagArgument(ACCEPT_ONLY_BETTER_FLAG, 0,
                                         out_acceptOnlyBetter);
        MMSOLVER_CHECK_MSTATUS(status);
    }

    // Get 'Frame Solve Mode'
    auto frameSolveMode = FRAME_SOLVE_MODE_DEFAULT_VALUE;
    if (argData.isFlagSet(FRAME_SOLVE_MODE_FLAG)) {
        status =
            argData.getFlagArgument(FRAME_SOLVE_MODE_FLAG, 0, frameSolveMode);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    out_frameSolveMode = static_cast<FrameSolveMode>(frameSolveMode);

    // Get 'Image Width'
    out_imageWidth = IMAGE_WIDTH_DEFAULT_VALUE;
    if (argData.isFlagSet(IMAGE_WIDTH_FLAG)) {
        status = argData.getFlagArgument(IMAGE_WIDTH_FLAG, 0, out_imageWidth);
        MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

MStatus parseSolveInfoArguments_v1(
    const MArgDatabase &argData, int &out_iterations, double &out_tau,
    double &out_function_tolerance, double &out_parameter_tolerance,
    double &out_gradient_tolerance, double &out_delta, int &out_autoDiffType,
    int &out_autoParamScale, int &out_robustLossType,
    double &out_robustLossScale, int &out_solverType,
    SceneGraphMode &out_sceneGraphMode, int &out_timeEvalMode,
    bool &out_acceptOnlyBetter, FrameSolveMode &out_frameSolveMode,
    bool &out_supportAutoDiffForward, bool &out_supportAutoDiffCentral,
    bool &out_supportParameterBounds, bool &out_supportRobustLoss,
    bool &out_removeUnusedMarkers, bool &out_removeUnusedAttributes,
    bool &out_removeUnusedFrames, double &out_imageWidth) {
    MStatus status = parseSolveInfoArguments_solverType(
        argData, out_iterations, out_tau, out_function_tolerance,
        out_parameter_tolerance, out_gradient_tolerance, out_delta,
        out_autoDiffType, out_autoParamScale, out_robustLossType,
        out_robustLossScale, out_solverType, out_supportAutoDiffForward,
        out_supportAutoDiffCentral, out_supportParameterBounds,
        out_supportRobustLoss);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveInfoArguments_other(
        argData, out_sceneGraphMode, out_timeEvalMode, out_acceptOnlyBetter,
        out_frameSolveMode, out_imageWidth);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveInfoArguments_removeUnused(
        argData, out_removeUnusedMarkers, out_removeUnusedAttributes,
        out_removeUnusedFrames);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus parseSolveInfoArguments_v2(
    const MArgDatabase &argData, int &out_iterations, double &out_tau,
    double &out_function_tolerance, double &out_parameter_tolerance,
    double &out_gradient_tolerance, double &out_delta, int &out_autoDiffType,
    int &out_autoParamScale, int &out_robustLossType,
    double &out_robustLossScale, int &out_solverType,
    SceneGraphMode &out_sceneGraphMode, int &out_timeEvalMode,
    bool &out_acceptOnlyBetter, FrameSolveMode &out_frameSolveMode,
    bool &out_supportAutoDiffForward, bool &out_supportAutoDiffCentral,
    bool &out_supportParameterBounds, bool &out_supportRobustLoss,
    double &out_imageWidth) {
    MStatus status = parseSolveInfoArguments_solverType(
        argData, out_iterations, out_tau, out_function_tolerance,
        out_parameter_tolerance, out_gradient_tolerance, out_delta,
        out_autoDiffType, out_autoParamScale, out_robustLossType,
        out_robustLossScale, out_solverType, out_supportAutoDiffForward,
        out_supportAutoDiffCentral, out_supportParameterBounds,
        out_supportRobustLoss);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    status = parseSolveInfoArguments_other(
        argData, out_sceneGraphMode, out_timeEvalMode, out_acceptOnlyBetter,
        out_frameSolveMode, out_imageWidth);
    MMSOLVER_CHECK_MSTATUS_AND_RETURN_IT(status);

    return status;
}

}  // namespace mmsolver
