/*
 * Header for mmSolverType Maya command.
 */

#ifndef MAYA_MM_SOLVER_TYPE_CMD_H
#define MAYA_MM_SOLVER_TYPE_CMD_H


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


// Command arguments and command name:

// List of Solver Types
#define LIST_FLAG           "-ls"
#define LIST_FLAG_LONG      "-list"

// Solver Type Name
#define NAME_FLAG           "-n"
#define NAME_FLAG_LONG      "-name"

// Solver Type Index
#define INDEX_FLAG           "-i"
#define INDEX_FLAG_LONG      "-index"

// Solver Type Default
#define DEFAULT_FLAG           "-df"
#define DEFAULT_FLAG_LONG      "-default"


class MMSolverTypeCmd : public MPxCommand {
public:

    MMSolverTypeCmd() {
        m_default = false;
        m_list = false;
        m_name = false;
        m_index = false;
    };

    virtual ~MMSolverTypeCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs( const MArgList& args );

    bool  m_default;
    bool  m_list;
    bool  m_name;
    bool  m_index;
};

#endif // MAYA_MM_SOLVER_TYPE_CMD_H
