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

#include <Camera.h>
#include <Marker.h>
#include <Bundle.h>
#include <Attr.h>

// Command arguments and command name
#define kCameraFlag        "-c"
#define kCameraFlagLong    "-camera"

#define kMarkerFlag          "-m"
#define kMarkerFlagLong      "-marker"

#define kAttrFlag          "-a"
#define kAttrFlagLong      "-attr"

#define kStartFrameFlag          "-sf"
#define kStartFrameFlagLong      "-startFrame"
#define kStartFrameDefaultValue  1

#define kEndFrameFlag            "-ef"
#define kEndFrameFlagLong        "-endFrame"
#define kEndFrameDefaultValue    1

#define kIterationsFlag          "-it"
#define kIterationsFlagLong      "-iterations"
#define kIterationsDefaultValue  1000


#define kVerboseFlag          "-v"
#define kVerboseFlagLong      "-verbose"
#define kVerboseDefaultValue  false

#define kCommandName "mmSolver"


class mmSolverCmd : public MPxCommand {
public:

    mmSolverCmd() {};

    virtual ~mmSolverCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    virtual MStatus undoIt();

    virtual MStatus redoIt();

    static void *creator();

private:
    MStatus parseArgs( const MArgList& args );

    int m_startFrame;
    int m_endFrame;
    unsigned int m_iterations;
    bool m_verbose;

    std::vector< std::shared_ptr<Camera> > m_cameraList;
    std::vector< std::shared_ptr<Marker> > m_markerList;
    std::vector< std::shared_ptr<Bundle> > m_bundleList;
    std::vector< std::shared_ptr<Attr> > m_attrList;
    MTimeArray m_frameList;

    MDGModifier m_dgmod;
    MAnimCurveChange m_curveChange;
    MComputation m_computation;
};

#endif // MAYA_MM_SOLVER_CMD_H
