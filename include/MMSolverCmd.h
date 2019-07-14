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

#ifndef MAYA_MM_SOLVER_CMD_H
#define MAYA_MM_SOLVER_CMD_H


// STL
#include <cmath>
#include <vector>

// Maya
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>

#include <maya/MPxCommand.h>
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MSyntax.h>

#include <maya/MSelectionList.h>
#include <maya/MDagPath.h>
#include <maya/MDGModifier.h>
#include <maya/MDagModifier.h>
#include <maya/MFnDagNode.h>

#include <maya/MPlug.h>
#include <maya/MPlugArray.h>
#include <maya/MAnimCurveChange.h>
#include <maya/MComputation.h>

#include <maya/MPoint.h>
#include <maya/MVector.h>
#include <maya/MMatrix.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MDoubleArray.h>

// Internal Objects
#include <Camera.h>
#include <Marker.h>
#include <Bundle.h>
#include <Attr.h>

// Define solvers
#include <mmSolver.h>


// Command arguments and command name
#define CAMERA_FLAG       "-c"
#define CAMERA_FLAG_LONG  "-camera"

#define MARKER_FLAG       "-m"
#define MARKER_FLAG_LONG  "-marker"

#define ATTR_FLAG       "-a"
#define ATTR_FLAG_LONG  "-attr"

#define FRAME_FLAG       "-f"
#define FRAME_FLAG_LONG  "-frame"

#define SOLVER_TYPE_FLAG           "-st"
#define SOLVER_TYPE_FLAG_LONG      "-solverType"

// Maximum number of iterations
//
// This option does not directly control the number of evaluations the
// solver may run, but instead controls how many attempts the solver
// will try before giving up.
#define ITERATIONS_FLAG           "-it"
#define ITERATIONS_FLAG_LONG      "-iterations"

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
#define TAU_FLAG           "-t"
#define TAU_FLAG_LONG      "-tauFactor"

// Acceptable Gradient Change.
//
// At the beginning of an solver iteration, if the solver has not
// decreased the gradient by at least this value, the solver gives up
// trying to reduce the error any more.
#define EPSILON1_FLAG           "-e1"
#define EPSILON1_FLAG_LONG      "-epsilon1"

// Acceptable Parameter Change.
//
// At the beginning of an solver iteration, if the guessed parameters
// do not change by at least this value, the solver gives up trying to
// reduce the error any more.
#define EPSILON2_FLAG           "-e2"
#define EPSILON2_FLAG_LONG      "-epsilon2"

// Acceptable Error
//
// At the beginning of an solver iteration, if the error level is
// below this value, the solver considers the error to be low enough
// for the user's needs and stops trying to reduce the error.
#define EPSILON3_FLAG           "-e3"
#define EPSILON3_FLAG_LONG      "-epsilon3"

// Change to the guessed parameters each iteration
//
// Each time the solver guesses an unknown parameter value, it adds or
// subtracts the 'delta' value to the unknown parameter value. This
// changes the magnitude of the parameter values in each guess. If
// this value is too small, the change in error level may not be
// detected, if this value is too large the solver will over-estimate
// and will likely lead to poor convergence.
#define DELTA_FLAG           "-dt"
#define DELTA_FLAG_LONG      "-delta"

// Auto-Differencing Type
//
// 0 = 'forward' (fast but not accurate)
// 1 = 'central' (more accurate but 1/3rd slower to compute initially)
#define AUTO_DIFF_TYPE_FLAG      "-adt"
#define AUTO_DIFF_TYPE_FLAG_LONG "-autoDiffType"

// Auto-Scaling Parameters Type
//
// 0 = 'off'
// 1 = 'on'
#define AUTO_PARAM_SCALE_FLAG      "-aps"
#define AUTO_PARAM_SCALE_FLAG_LONG "-autoParamScaling"

// Should the solver print out verbose information while solving?
#define VERBOSE_FLAG           "-v"
#define VERBOSE_FLAG_LONG      "-verbose"
#define VERBOSE_DEFAULT_VALUE  false

// Write a debug file somewhere
#define DEBUG_FILE_FLAG           "-df"
#define DEBUG_FILE_FLAG_LONG      "-debugFile"
#define DEBUG_FILE_DEFAULT_VALUE  ""

// Print Statistics from the solver inputs.
#define PRINT_STATS_FLAG           "-pst"
#define PRINT_STATS_FLAG_LONG      "-printStatistics"

// Default Values for solver option flags
#define CMINPACK_LM_ITERATIONS_DEFAULT_VALUE  20
#define CMINPACK_LM_TAU_DEFAULT_VALUE  100.0 // default is 100.0
#define CMINPACK_LM_EPSILON1_DEFAULT_VALUE  1E-6 // default is 1E-15 (ftol)
#define CMINPACK_LM_EPSILON2_DEFAULT_VALUE  1E-6 // default is 1E-15 (xtol)
#define CMINPACK_LM_EPSILON3_DEFAULT_VALUE  1E-6 // default is 0.0 (gtol)
#define CMINPACK_LM_DELTA_DEFAULT_VALUE  1E-03 // default is 0.0
// cminpack only supports forward '0=forward' auto-diff'ing.
#define CMINPACK_LM_AUTO_DIFF_TYPE_DEFAULT_VALUE  0
#define CMINPACK_LM_AUTO_PARAM_SCALE_DEFAULT_VALUE  1  // default is 'on=1 (mode=1)'

#define LEVMAR_ITERATIONS_DEFAULT_VALUE  20
#define LEVMAR_TAU_DEFAULT_VALUE  1E-03 // LevMar default is 1E-3
#define LEVMAR_EPSILON1_DEFAULT_VALUE  1E-6 // LevMar default is 1E-12
#define LEVMAR_EPSILON2_DEFAULT_VALUE  1E-6 // LevMar default is 1E-12
#define LEVMAR_EPSILON3_DEFAULT_VALUE  1E-6 // LevMar default is 1E-12
#define LEVMAR_DELTA_DEFAULT_VALUE  (1E-04) // LevMar default is 1E-06
#define LEVMAR_AUTO_DIFF_TYPE_DEFAULT_VALUE  1 // LevMar default is '0=forward'
// LevMar does not have auto-parameter scaling.
#define LEVMAR_AUTO_PARAM_SCALE_DEFAULT_VALUE  0


class MMSolverCmd : public MPxCommand {
public:

    MMSolverCmd() {};

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
    MStatus parseArgs( const MArgList& args );

    // Solver Information.
    unsigned int m_iterations;
    double m_tau;       // Scale factor for initial transform mu
    double m_epsilon1;  // Stopping threshold for ||J^T e||_inf  (ftol)
    double m_epsilon2;  // Stopping threshold for ||Dp||_2       (xtol)
    double m_epsilon3;  // Stopping threshold for ||e||_2        (gtol)
    double m_delta;     // Step used in difference approximation to the Jacobian
    int m_autoDiffType; // Auto Differencing type to use; 0=forward, 1=central.
    int m_autoParamScale; // Auto Parameter Scaling; 0=OFF, 1=ON.
    int m_solverType;   // Solver type to use; 0=levmar, 1=cminpack_lm.

    // Solver printing.
    MString m_debugFile;
    MStringArray m_printStatsList;
    bool m_verbose;

    // Objects
    CameraPtrList m_cameraList;
    MarkerPtrList m_markerList;
    BundlePtrList m_bundleList;
    AttrPtrList   m_attrList;
    MTimeArray m_frameList;

    // Undo/Redo
    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
    MComputation m_computation;
};

#endif // MAYA_MM_SOLVER_CMD_H
