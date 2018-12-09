/*
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
#define SOLVER_TYPE_DEFAULT_VALUE  0  // levmar

// Maximum number of iterations
//
// This option does not directly control the number of evaluations the
// solver may run, but instead controls how many attempts the solver
// will try before giving up.
#define ITERATIONS_FLAG           "-it"
#define ITERATIONS_FLAG_LONG      "-iterations"
#define ITERATIONS_DEFAULT_VALUE  20

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
#define TAU_DEFAULT_VALUE  1E-03 // LevMar default is  1E-3

// Acceptable Gradient Change.
//
// At the beginning of an solver iteration, if the solver has not
// decreased the gradient by at least this value, the solver gives up
// trying to reduce the error any more.
#define EPSILON1_FLAG           "-e1"
#define EPSILON1_FLAG_LONG      "-epsilon1"
#define EPSILON1_DEFAULT_VALUE  1E-6 // LevMar default is 1E-12

// Acceptable Parameter Change.
//
// At the beginning of an solver iteration, if the guessed parameters
// do not change by at least this value, the solver gives up trying to
// reduce the error any more.
#define EPSILON2_FLAG           "-e2"
#define EPSILON2_FLAG_LONG      "-epsilon2"
#define EPSILON2_DEFAULT_VALUE  1E-6 // LevMar default is 1E-12

// Acceptable Error
//
// At the beginning of an solver iteration, if the error level is
// below this value, the solver considers the error to be low enough
// for the user's needs and stops trying to reduce the error.
#define EPSILON3_FLAG           "-e3"
#define EPSILON3_FLAG_LONG      "-epsilon3"
#define EPSILON3_DEFAULT_VALUE  1E-6 // LevMar default is 1E-12

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
#define DELTA_DEFAULT_VALUE  (1E-04) // LevMar default is 1E-06

// Auto-Differencing Type
//
// 0 = 'forward' (fast but not accurate)
// 1 = 'central' (more accurate but 1/3rd slower to compute initially)
#define AUTO_DIFF_TYPE_FLAG      "-adt"
#define AUTO_DIFF_TYPE_FLAG_LONG "-autoDiffType"
#define AUTO_DIFF_TYPE_DEFAULT_VALUE  1 // LevMar default is 'forward'

// Should the solver print out verbose information while solving?
#define VERBOSE_FLAG           "-v"
#define VERBOSE_FLAG_LONG      "-verbose"
#define VERBOSE_DEFAULT_VALUE  false


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
    double m_epsilon1;  // Stopping threshold for ||J^T e||_inf
    double m_epsilon2;  // Stopping threshold for ||Dp||_2
    double m_epsilon3;  // Stopping threshold for ||e||_2
    double m_delta;     // Step used in difference approximation to the Jacobian
    int m_autoDiffType; // Auto Differencing type to use; 0=forward, 1=central.
    int m_solverType;   // Solver type to use; 0=levmar.
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
