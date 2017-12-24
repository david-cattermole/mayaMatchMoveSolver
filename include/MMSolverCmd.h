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

#define ITERATIONS_FLAG           "-it"
#define ITERATIONS_FLAG_LONG      "-iterations"
#define ITERATIONS_DEFAULT_VALUE  1000

#define TAU_FLAG           "-t"
#define TAU_FLAG_LONG      "-tauFactor"
#define TAU_DEFAULT_VALUE  1E-03

#define EPSILON1_FLAG           "-e1"
#define EPSILON1_FLAG_LONG      "-epsilon1"
#define EPSILON1_DEFAULT_VALUE  1E-12

#define EPSILON2_FLAG           "-e2"
#define EPSILON2_FLAG_LONG      "-epsilon2"
#define EPSILON2_DEFAULT_VALUE  1E-12

#define EPSILON3_FLAG           "-e3"
#define EPSILON3_FLAG_LONG      "-epsilon3"
#define EPSILON3_DEFAULT_VALUE  1E-12

#define DELTA_FLAG           "-dt"
#define DELTA_FLAG_LONG      "-delta"
#define DELTA_DEFAULT_VALUE  -1E-03  // -1E-06

#define VERBOSE_FLAG           "-v"
#define VERBOSE_FLAG_LONG      "-verbose"
#define VERBOSE_DEFAULT_VALUE  false

#define COMMAND_NAME    "mmSolver"
#define COMMAND_VERSION "1.0"


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

private:
    MStatus parseArgs( const MArgList& args );

    // Solver Information.
    unsigned int m_iterations;
    double m_tau;       // Scale factor for initialTransform mu
    double m_epsilon1;  // Stopping threshold for ||J^T e||_inf
    double m_epsilon2;  // Stopping threshold for ||Dp||_2
    double m_epsilon3;  // Stopping threshold for ||e||_2
    double m_delta;     // Step used in difference approximation to the Jacobian
    int m_solverType;   // Solver type to use; 0=levmar, 1=splm (sparse levmar).
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
