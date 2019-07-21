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
#include <core/bundleAdjust_base.h>
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
    syntax.addFlag(DEFAULT_FLAG, DEFAULT_FLAG_LONG, MSyntax::kBoolean);
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
    if (status == MStatus::kFailure) {
        return status;
    }
    if (query == false) {
        status = MStatus::kFailure;
        return status;
    }

    // Get 'default'
    m_default = false;
    if (argData.isFlagSet(DEFAULT_FLAG)) {
        status = argData.getFlagArgument(DEFAULT_FLAG, 0, m_default);
        if (status == MStatus::kFailure) {
            return status;
        }
    }

    // Get 'list'
    m_list = false;
    if (argData.isFlagSet(LIST_FLAG)) {
        status = argData.getFlagArgument(LIST_FLAG, 0, m_list);
        if (status == MStatus::kFailure) {
            return status;
        }
    }

    if ((m_list == true && m_default == true)
       || (m_list == false && m_default == false)) {
        status = MStatus::kFailure;
        return status;
    }

    // Default switches
    m_name = false;
    m_index = false;
    if (m_list == true || m_default == true) {
        m_name = true;
        m_index = true;
    }

    // Get 'name'
    if (argData.isFlagSet(NAME_FLAG)) {
        status = argData.getFlagArgument(NAME_FLAG, 0, m_name);
        if (status == MStatus::kFailure) {
            return status;
        }
    }

    // Get 'index'
    if (argData.isFlagSet(INDEX_FLAG)) {
        status = argData.getFlagArgument(INDEX_FLAG, 0, m_index);
        if (status == MStatus::kFailure) {
            return status;
        }
    }

    // Must have 'name' or 'index' flag, otherwise we don't print anything.
    if (m_name == false && m_index == false) {
        status = MStatus::kFailure;
        return status;
    }
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
//    MStatus::kSuccess - command succeeded
//    MStatus::kFailure - command failed (returning this value will cause the
//                     MEL script that is being run to terminate unless the
//                     error is caught using a "catch" statement.
//
    MStatus status = MStatus::kSuccess;

    // Read all the flag arguments.
    status = parseArgs(args);
    if (status == MStatus::kFailure) {
        return status;
    }

    if (m_list == true) {
        // Get List of Solver Types
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
    } else if (m_default == true) {
        // Get Default Solver Type
        SolverTypePair solverType = getSolverTypeDefault();

        if (m_name == true) {
            MString outResult = "";
            int index = solverType.first;
            std::string name = solverType.second;

            if (m_index == true) {
                std::string index_string = string::numberToString<int>(index);
                outResult += MString(index_string.c_str());
                outResult += "=";
            }
            outResult += name.c_str();

            MMSolverTypeCmd::setResult(outResult);
        } else if (m_name == false && m_index == true) {
            int outResult = solverType.first;
            MMSolverTypeCmd::setResult(outResult);
        }
    }

    return status;
}
