/*
 * Command for running mmSolverType.
 *
 * mmSolverType allows the user to:
 * - Query the available solvers.
 * - Query the default solver.
 * - Query the solver name, from an index.
 * - Query the solver index from a name.
 */

// Internal
#include <MMSolverTypeCmd.h>
#include <mmSolver.h>
#include <mayaUtils.h>

// STL
#include <cmath>
#include <cassert>
#include <cstdlib>  // getenv

// Utils
#include <utilities/debugUtils.h>
#include <utilities/stringUtils.h>

// Maya
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MFnDependencyNode.h>

//// Internal Objects
//#include <Marker.h>
//#include <Bundle.h>
//#include <Camera.h>


MMSolverTypeCmd::~MMSolverTypeCmd() {}

void *MMSolverTypeCmd::creator() {
    return new MMSolverTypeCmd();
}

MString MMSolverTypeCmd::cmdName() {
    return MString("mmSolverType");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMSolverTypeCmd::hasSyntax() const {
    return true;
}

bool MMSolverTypeCmd::isUndoable() const {
    return false;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMSolverTypeCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(true);
    syntax.enableEdit(false);

    // Flags
    syntax.addFlag(LIST_FLAG, LIST_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(NAME_FLAG, NAME_FLAG_LONG, MSyntax::kString);
    syntax.addFlag(INDEX_FLAG, INDEX_FLAG_LONG, MSyntax::kUnsigned);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMSolverTypeCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool query = argData.isQuery(&status);
    CHECK_MSTATUS(status);
    if (query == false) {
        status = MS::kFailure;
        return status;
    }

    // Get 'list'
    m_list = false;
    if (argData.isFlagSet(LIST_FLAG)) {
        status = argData.getFlagArgument(LIST_FLAG, 0, m_list);
        CHECK_MSTATUS(status);
    }

    // Default switches based on 'list' flag.
    m_name = false;
    m_index = false;
    if (m_list == true) {
        m_name = true;
        m_index = true;
    }

    // Get 'name'
    if (argData.isFlagSet(NAME_FLAG)) {
        status = argData.getFlagArgument(NAME_FLAG, 0, m_name);
        CHECK_MSTATUS(status);
    }

    // Get 'index'
    if (argData.isFlagSet(INDEX_FLAG)) {
        status = argData.getFlagArgument(INDEX_FLAG, 0, m_index);
        CHECK_MSTATUS(status);
    }

    // Must have 'name' or 'index' flag, otherwise we don't print anything.
    if (m_list == true && m_name == false && m_index == false) {
        status = MS::kFailure;
        return status;
    }

    // // Get 'Verbose'
    // m_verbose = VERBOSE_DEFAULT_VALUE;
    // if (argData.isFlagSet(VERBOSE_FLAG)) {
    //     status = argData.getFlagArgument(VERBOSE_FLAG, 0, m_verbose);
    //     CHECK_MSTATUS(status);
    // }


    // // Get 'Solver Type'
    // if (argData.isFlagSet(SOLVER_TYPE_FLAG)) {
    //     status = argData.getFlagArgument(SOLVER_TYPE_FLAG, 0, m_solverType);
    //     CHECK_MSTATUS(status);
    // }
    return status;
}


MStatus MMSolverTypeCmd::doIt(const MArgList &args) {
//
//  Description:
//    implements the MEL mmSolver command.
//
//  Arguments:
//    argList - the argument list that was passes to the command from MEL
//
//  Return Value:
//    MS::kSuccess - command succeeded
//    MS::kFailure - command failed (returning this value will cause the
//                     MEL script that is being run to terminate unless the
//                     error is caught using a "catch" statement.
//
    MStatus status = MStatus::kSuccess;

    // Read all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (m_list == true) {
        std::vector<SolverTypePair> solverTypes = getSolverTypes();
        std::vector<SolverTypePair>::const_iterator cit;

        if (m_name == true) {
            MStringArray outResult;

            for (cit = solverTypes.cbegin(); cit != solverTypes.cend(); ++cit){
                int index = cit->first;
                std::string name = cit->second;

                MString item = "";
                if (m_index == true) {
                    std::string index_string = string::numberToString<int>(index);
                    item += MString(index_string.c_str());
                    item += "=";
                }
                item += name.c_str();
                outResult.append(item);
            }

            MMSolverTypeCmd::setResult(outResult);
        } else if (m_name == false && m_index == true) {
            MIntArray outResult;

            for (cit = solverTypes.cbegin(); cit != solverTypes.cend(); ++cit){
                int index = cit->first;
                outResult.append(index);
            }

            MMSolverTypeCmd::setResult(outResult);
        }
    }


    return status;
}
