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

#include "MMSolverTypeCmd.h"

// STL
#include <cassert>
#include <cmath>
#include <cstdlib>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MStatus.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>

// MM Solver
#include "mmSolver/adjust/adjust_base.h"
#include "mmSolver/mayahelper/maya_string_utils.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {

MMSolverTypeCmd::~MMSolverTypeCmd() {}

void *MMSolverTypeCmd::creator() { return new MMSolverTypeCmd(); }

MString MMSolverTypeCmd::cmdName() { return MString("mmSolverType"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMSolverTypeCmd::hasSyntax() const { return true; }

bool MMSolverTypeCmd::isUndoable() const { return false; }

/*
 * Add flags to the command syntax
 */
MSyntax MMSolverTypeCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(true);
    syntax.enableEdit(false);

    // Flags
    syntax.addFlag(MM_SOLVER_TYPE_DEFAULT_FLAG,
                   MM_SOLVER_TYPE_DEFAULT_FLAG_LONG, MSyntax::kBoolean);
    syntax.addFlag(MM_SOLVER_TYPE_LIST_FLAG, MM_SOLVER_TYPE_LIST_FLAG_LONG,
                   MSyntax::kBoolean);
    syntax.addFlag(MM_SOLVER_TYPE_NAME_FLAG, MM_SOLVER_TYPE_NAME_FLAG_LONG,
                   MSyntax::kString);
    syntax.addFlag(MM_SOLVER_TYPE_INDEX_FLAG, MM_SOLVER_TYPE_INDEX_FLAG_LONG,
                   MSyntax::kUnsigned);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMSolverTypeCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    const bool query = argData.isQuery(&status);
    CHECK_MSTATUS(status);
    if (status != MStatus::kSuccess) {
        status.perror("mmSolverType Could not get the query flag");
        return status;
    }
    if (!query) {
        status = MStatus::kFailure;
        status.perror("mmSolverType must query using the 'query' flag");
        return status;
    }

    // Get 'default'
    m_default = false;
    if (argData.isFlagSet(MM_SOLVER_TYPE_DEFAULT_FLAG)) {
        status =
            argData.getFlagArgument(MM_SOLVER_TYPE_DEFAULT_FLAG, 0, m_default);
        if (status != MStatus::kSuccess) {
            status.perror("mmSolverType could not get 'default' flag value");
            return status;
        }
    }

    // Get 'list'
    m_list = false;
    if (argData.isFlagSet(MM_SOLVER_TYPE_LIST_FLAG)) {
        status = argData.getFlagArgument(MM_SOLVER_TYPE_LIST_FLAG, 0, m_list);
        if (status != MStatus::kSuccess) {
            status.perror("mmSolverType could not get 'list' flag value");
            return status;
        }
    }

    if ((m_list && m_default) || (!m_list && !m_default)) {
        status = MStatus::kFailure;
        status.perror(
            "mmSolverType; must give 'list' or 'default' flag, not both flags "
            "at once");
        return status;
    }

    // Default switches
    m_name = false;
    m_index = false;
    if (m_list || m_default) {
        m_name = true;
        m_index = true;
    }

    // Get 'name'
    if (argData.isFlagSet(MM_SOLVER_TYPE_NAME_FLAG)) {
        status = argData.getFlagArgument(MM_SOLVER_TYPE_NAME_FLAG, 0, m_name);
        if (status != MStatus::kSuccess) {
            status.perror("mmSolverType could not get 'name' flag value");
            return status;
        }
    }

    // Get 'index'
    if (argData.isFlagSet(MM_SOLVER_TYPE_INDEX_FLAG)) {
        status = argData.getFlagArgument(MM_SOLVER_TYPE_INDEX_FLAG, 0, m_index);
        if (status != MStatus::kSuccess) {
            status.perror("mmSolverType could not get 'index' flag value");
            return status;
        }
    }

    // Must have 'name' or 'index' flag, otherwise we don't print anything.
    if (!m_name && !m_index) {
        status = MStatus::kFailure;
        status.perror("mmSolverType must have 'name' or 'index' flags");
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
    //    MStatus::kFailure - command failed (returning this value will cause
    //    the
    //                     MEL script that is being run to terminate unless the
    //                     error is caught using a "catch" statement.
    //

    // Read all the flag arguments.
    MStatus status = parseArgs(args);
    if (status != MStatus::kSuccess) {
        return status;
    }

    if (m_list) {
        // Get List of Solver Types
        std::vector<SolverTypePair> solverTypes = getSolverTypes();
        std::vector<SolverTypePair>::const_iterator cit;

        if (m_name) {
            MStringArray outResult;

            for (cit = solverTypes.cbegin(); cit != solverTypes.cend(); ++cit) {
                const std::string name = cit->second;

                MString item = "";
                if (m_index) {
                    int index = cit->first;
                    MString index_mstring =
                        mmmayastring::numberToMString<int>(index);
                    item += index_mstring;
                    item += "=";
                }
                item += name.c_str();
                outResult.append(item);
            }

            MMSolverTypeCmd::setResult(outResult);
        } else if (m_index) {
            MIntArray outResult;

            for (cit = solverTypes.cbegin(); cit != solverTypes.cend(); ++cit) {
                int index = cit->first;
                outResult.append(index);
            }

            MMSolverTypeCmd::setResult(outResult);
        }
    } else if (m_default) {
        // Get Default Solver Type
        SolverTypePair solverType = getSolverTypeDefault();

        if (m_name) {
            MString outResult = "";
            const std::string name = solverType.second;

            if (m_index) {
                const int index = solverType.first;
                MString index_mstring =
                    mmmayastring::numberToMString<int>(index);
                outResult += index_mstring;
                outResult += "=";
            }
            outResult += name.c_str();

            MMSolverTypeCmd::setResult(outResult);
        } else if (m_index) {
            int outResult = solverType.first;
            MMSolverTypeCmd::setResult(outResult);
        } else {
            status = MStatus::kFailure;
            status.perror("mmSolverType must have 'name' or 'index' flags");
            return status;
        }
    }

    return status;
}

}  // namespace mmsolver
