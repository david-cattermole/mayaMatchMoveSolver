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
 * Header for mmSolver Maya command.
 */

#ifndef MM_SOLVER_CMD_H
#define MM_SOLVER_CMD_H

// STL
#include <cmath>
#include <vector>

// Maya
#include <maya/MAnimCurveChange.h>
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MComputation.h>
#include <maya/MDGModifier.h>
#include <maya/MDagModifier.h>
#include <maya/MDagPath.h>
#include <maya/MDoubleArray.h>
#include <maya/MFnDagNode.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MMatrix.h>
#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MPoint.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MVector.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/mayahelper/maya_attr.h"
#include "mmSolver/mayahelper/maya_bundle.h"
#include "mmSolver/mayahelper/maya_camera.h"
#include "mmSolver/mayahelper/maya_marker.h"

// Command arguments

// Type of Solver to use.
//
// The Type of Solver backend to use for refinement and
// guessing of parameter values.
#define SOLVER_TYPE_FLAG "-st"
#define SOLVER_TYPE_FLAG_LONG "-solverType"

// Time Evaluation Mode
//
// How should the solver evaluate time? Should we use DG Context, or
// just changing the scene's current time?
//
// TIME_EVAL_MODE_DG_CONTEXT = 'DG Context'
// TIME_EVAL_MODE_SET_TIME = 'Set Time' - change the scene time value.
//
#define TIME_EVAL_MODE_FLAG "-tem"
#define TIME_EVAL_MODE_FLAG_LONG "-timeEvalMode"
#define TIME_EVAL_MODE_DEFAULT_VALUE TIME_EVAL_MODE_DG_CONTEXT

// Frame solve mode.
#define FRAME_SOLVE_MODE_FLAG "-fsm"
#define FRAME_SOLVE_MODE_FLAG_LONG "-frameSolveMode"

// Maximum number of iterations
//
// This option does not directly control the number of evaluations the
// solver may run, but instead controls how many attempts the solver
// will try before giving up.
#define ITERATIONS_FLAG "-it"
#define ITERATIONS_FLAG_LONG "-iterations"

// Initial Damping Factor.
//
// Larger values should be used when the initial unknown parameters
// have high error. This forces the LevMar algorithm to use
// steepest-decent, rather than gauss-newton.
//
// "The algorithm is not very sensitive to the choice of 'tau', but as
// a rule of thumb, one should use a small value, eg 'tau = 10-6', if
// 'the initial parameters' are believed to be a good approximation to
// the 'final parameter values'. Otherwise, use 'tau = 10-3' or even
// 'tau = 1.0'."
//
// Reference:
//   'METHODS FOR NON-LINEAR LEAST SQUARES PROBLEMS'
//   Page 25, Figure 3.14,
//   http://www2.imm.dtu.dk/pubdb/views/edoc_download.php/3215/pdf/imm3215.pdf
#define TAU_FLAG "-t"
#define TAU_FLAG_LONG "-tauFactor"

// Acceptable Gradient Change.
//
// At the beginning of an solver iteration, if the solver has not
// decreased the gradient by at least this value, the solver gives up
// trying to reduce the error any more.
#define EPSILON1_FLAG "-e1"
#define EPSILON1_FLAG_LONG "-epsilon1"

// Acceptable Parameter Change.
//
// At the beginning of an solver iteration, if the guessed parameters
// do not change by at least this value, the solver gives up trying to
// reduce the error any more.
#define EPSILON2_FLAG "-e2"
#define EPSILON2_FLAG_LONG "-epsilon2"

// Acceptable Error
//
// At the beginning of an solver iteration, if the error level is
// below this value, the solver considers the error to be low enough
// for the user's needs and stops trying to reduce the error.
#define EPSILON3_FLAG "-e3"
#define EPSILON3_FLAG_LONG "-epsilon3"

// Change to the guessed parameters each iteration
//
// Each time the solver guesses an unknown parameter value, it adds or
// subtracts the 'delta' value to the unknown parameter value. This
// changes the magnitude of the parameter values in each guess. If
// this value is too small, the change in error level may not be
// detected, if this value is too large the solver will over-estimate
// and will likely lead to poor convergence.
#define DELTA_FLAG "-dt"
#define DELTA_FLAG_LONG "-delta"

// Auto-Differencing Type
//
// 0 = 'forward' (fast but not accurate)
// 1 = 'central' (more accurate but 1/3rd slower to compute initially)
#define AUTO_DIFF_TYPE_FLAG "-adt"
#define AUTO_DIFF_TYPE_FLAG_LONG "-autoDiffType"

// Auto-Scaling Parameters Type
//
// 0 = 'off'
// 1 = 'on'
#define AUTO_PARAM_SCALE_FLAG "-aps"
#define AUTO_PARAM_SCALE_FLAG_LONG "-autoParamScaling"

// Robust Loss Function Type
//
// 0 = 'trivial'
// 1 = 'soft_l1'
// 2 = 'cauchy'
#define ROBUST_LOSS_TYPE_FLAG "-rlt"
#define ROBUST_LOSS_TYPE_FLAG_LONG "-robustLossType"

// Robust Loss Function Scale
//
// The scale factor to remap '1.0' of the robust loss function to.
#define ROBUST_LOSS_SCALE_FLAG "-rls"
#define ROBUST_LOSS_SCALE_FLAG_LONG "-robustLossScale"

// Only set the solve values if the quality is better that it was when
// we started the solve.
#define ACCEPT_ONLY_BETTER_FLAG "-aob"
#define ACCEPT_ONLY_BETTER_FLAG_LONG "-acceptOnlyBetter"
#define ACCEPT_ONLY_BETTER_DEFAULT_VALUE true

// If unused Markers are detected, should they automatically be removed?
#define REMOVE_UNUSED_MARKERS_FLAG "-rum"
#define REMOVE_UNUSED_MARKERS_FLAG_LONG "-removeUnusedMarkers"
#define REMOVE_UNUSED_MARKERS_DEFAULT_VALUE true

// If unused Attributes are detected, should they automatically be removed?
#define REMOVE_UNUSED_ATTRIBUTES_FLAG "-rua"
#define REMOVE_UNUSED_ATTRIBUTES_FLAG_LONG "-removeUnusedAttributes"
#define REMOVE_UNUSED_ATTRIBUTES_DEFAULT_VALUE true

// Should the solver print out verbose information while solving?
// Deprecated. Use the 'log level' flag instead.
#define VERBOSE_FLAG "-v"
#define VERBOSE_FLAG_LONG "-verbose"
#define VERBOSE_DEFAULT_VALUE false

// How much detail does the mmSolver command print?
#define LOG_LEVEL_FLAG "-lgl"
#define LOG_LEVEL_FLAG_LONG "-logLevel"
#define LOG_LEVEL_DEFAULT_VALUE LogLevel::kInfo

// Print Statistics from the solver inputs.
#define PRINT_STATS_FLAG "-pst"
#define PRINT_STATS_FLAG_LONG "-printStatistics"

// What is the width of the image we are matchmoving? This value is
// used to while calculating per-pixel deviation/error levels.
//
// The value will not change the solve, but will only change the
// per-pixel numbers displayed to the user.
#define IMAGE_WIDTH_FLAG "-imw"
#define IMAGE_WIDTH_FLAG_LONG "-imageWidth"
#define IMAGE_WIDTH_DEFAULT_VALUE 2048.0

namespace mmsolver {

class MMSolverCmd : public MPxCommand {
public:
    MMSolverCmd(){};

    virtual ~MMSolverCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    virtual MStatus undoIt();

    virtual MStatus redoIt();

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    // Solver Information.
    unsigned int m_iterations;
    double m_tau;       // Scale factor for initial transform mu
    double m_epsilon1;  // Stopping threshold for ||J^T e||_inf  (ftol)
    double m_epsilon2;  // Stopping threshold for ||Dp||_2       (xtol)
    double m_epsilon3;  // Stopping threshold for ||e||_2        (gtol)
    double m_delta;     // Step used in difference approximation to the Jacobian
    int m_autoDiffType;  // Auto Differencing type to use; 0=forward, 1=central.
    int m_autoParamScale;      // Auto Parameter Scaling; 0=OFF, 1=ON.
    int m_robustLossType;      // Robust Loss function type; 0=trivial,
                               //                            1=soft_l1,
                               //                            2=cauchy.
    double m_robustLossScale;  // Factor to scale robust loss function by.
    int m_solverType;          // Solver type to use; 0=levmar,
                               //                     1=cminpack_lmdif,
                               //                     2=cmpinpack_lmder.
    int m_timeEvalMode;        // How to evaluate values at different times?
    SceneGraphMode m_sceneGraphMode;
    bool m_acceptOnlyBetter;  // Do not accept solved parameter values if
                              // the average devation is higher than at start.
    bool m_removeUnusedMarkers;     // Remove unused Markers from solve?
    bool m_removeUnusedAttributes;  // Remove unused Attributes from solve?
    double m_imageWidth;            // Defines pixel size in camera space.
    FrameSolveMode m_frameSolveMode;

    // What type of features does the given solver type support?
    bool m_supportAutoDiffForward;
    bool m_supportAutoDiffCentral;
    bool m_supportParameterBounds;
    bool m_supportRobustLoss;

    // Solver printing.
    MStringArray m_printStatsList;
    LogLevel m_logLevel;

    // Solver Objects
    CameraPtrList m_cameraList;
    MarkerPtrList m_markerList;
    BundlePtrList m_bundleList;
    AttrPtrList m_attrList;
    MTimeArray m_frameList;
    StiffAttrsPtrList m_stiffAttrsList;
    SmoothAttrsPtrList m_smoothAttrsList;

    // Undo/Redo
    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
    MComputation m_computation;
};

}  // namespace mmsolver

#endif  // MM_SOLVER_CMD_H
