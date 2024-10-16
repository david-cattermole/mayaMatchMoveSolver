/*
 * Copyright (C) 2024 David Cattermole.
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

#include "MMMemorySystemCmd.h"

// STD
#include <cassert>
#include <string>
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MFileObject.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MImage.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// MM Solver
#include <mmcolorio/lib.h>

#include "mmSolver/mayahelper/maya_string_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/memory_system_utils.h"
#include "mmSolver/utilities/memory_utils.h"
#include "mmSolver/utilities/path_utils.h"
#include "mmSolver/utilities/string_utils.h"

// Command arguments and command name:
#define SYSTEM_PHYSICAL_MEMORY_TOTAL_FLAG "-tot"
#define SYSTEM_PHYSICAL_MEMORY_TOTAL_FLAG_LONG "-systemPhysicalMemoryTotal"

#define SYSTEM_PHYSICAL_MEMORY_FREE_FLAG "-fre"
#define SYSTEM_PHYSICAL_MEMORY_FREE_FLAG_LONG "-systemPhysicalMemoryFree"

#define SYSTEM_PHYSICAL_MEMORY_USED_FLAG "-usd"
#define SYSTEM_PHYSICAL_MEMORY_USED_FLAG_LONG "-systemPhysicalMemoryUsed"

#define PROCESS_MEMORY_USED_FLAG "-pud"
#define PROCESS_MEMORY_USED_FLAG_LONG "-processMemoryUsed"

#define MEMORY_AS_KILOBYTES_FLAG "-kb"
#define MEMORY_AS_KILOBYTES_FLAG_LONG "-asKiloBytes"

#define MEMORY_AS_MEGABYTES_FLAG "-mb"
#define MEMORY_AS_MEGABYTES_FLAG_LONG "-asMegaBytes"

#define MEMORY_AS_GIGABYTES_FLAG "-gb"
#define MEMORY_AS_GIGABYTES_FLAG_LONG "-asGigaBytes"

namespace mmsolver {

MMMemorySystemCmd::~MMMemorySystemCmd() {}

void *MMMemorySystemCmd::creator() { return new MMMemorySystemCmd(); }

MString MMMemorySystemCmd::cmdName() { return MString("mmMemorySystem"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMMemorySystemCmd::hasSyntax() const { return true; }

bool MMMemorySystemCmd::isUndoable() const { return false; }

/*
 * Add flags to the command syntax
 */
MSyntax MMMemorySystemCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(true);
    syntax.enableEdit(false);

    syntax.addFlag(SYSTEM_PHYSICAL_MEMORY_TOTAL_FLAG,
                   SYSTEM_PHYSICAL_MEMORY_TOTAL_FLAG_LONG);
    syntax.addFlag(SYSTEM_PHYSICAL_MEMORY_FREE_FLAG,
                   SYSTEM_PHYSICAL_MEMORY_FREE_FLAG_LONG);
    syntax.addFlag(SYSTEM_PHYSICAL_MEMORY_USED_FLAG,
                   SYSTEM_PHYSICAL_MEMORY_USED_FLAG_LONG);

    syntax.addFlag(PROCESS_MEMORY_USED_FLAG, PROCESS_MEMORY_USED_FLAG_LONG);

    syntax.addFlag(MEMORY_AS_KILOBYTES_FLAG, MEMORY_AS_KILOBYTES_FLAG_LONG);
    syntax.addFlag(MEMORY_AS_MEGABYTES_FLAG, MEMORY_AS_MEGABYTES_FLAG_LONG);
    syntax.addFlag(MEMORY_AS_GIGABYTES_FLAG, MEMORY_AS_GIGABYTES_FLAG_LONG);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMMemorySystemCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (!argData.isQuery()) {
        status = MStatus::kFailure;
        MMSOLVER_MAYA_ERR(
            "mmsolver::MMMemorySystemCmd::parseArgs: "
            "Command must be in query mode!");
        return status;
    }

    m_system_physical_memory_total =
        argData.isFlagSet(SYSTEM_PHYSICAL_MEMORY_TOTAL_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_system_physical_memory_free =
        argData.isFlagSet(SYSTEM_PHYSICAL_MEMORY_FREE_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_system_physical_memory_used =
        argData.isFlagSet(SYSTEM_PHYSICAL_MEMORY_USED_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_process_memory_used =
        argData.isFlagSet(PROCESS_MEMORY_USED_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    const bool as_kilobytes =
        argData.isFlagSet(MEMORY_AS_KILOBYTES_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    const bool as_megabytes =
        argData.isFlagSet(MEMORY_AS_MEGABYTES_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    const bool as_gigabytes =
        argData.isFlagSet(MEMORY_AS_GIGABYTES_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_memory_unit = mmmemory::MemoryUnit::kBytes;
    if (as_kilobytes) {
        m_memory_unit = mmmemory::MemoryUnit::kKiloBytes;
    } else if (as_megabytes) {
        m_memory_unit = mmmemory::MemoryUnit::kMegaBytes;
    } else if (as_gigabytes) {
        m_memory_unit = mmmemory::MemoryUnit::kGigaBytes;
    }

    return status;
}

MStatus MMMemorySystemCmd::doIt(const MArgList &args) {
    const bool verbose = false;

    // Read all the flag arguments.
    MStatus status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    size_t bytes_value = 0;
    if (m_system_physical_memory_total) {
        bytes_value = mmmemorysystem::system_physical_memory_total();
    } else if (m_system_physical_memory_free) {
        bytes_value = mmmemorysystem::system_physical_memory_free();
    } else if (m_system_physical_memory_used) {
        bytes_value = mmmemorysystem::system_physical_memory_used();
    } else if (m_process_memory_used) {
        size_t peak_resident_set_size = 0;
        size_t current_resident_set_size = 0;
        mmmemorysystem::process_memory_usage(peak_resident_set_size,
                                             current_resident_set_size);
        bytes_value = current_resident_set_size;
    } else {
        MMSOLVER_MAYA_ERR(
            "mmsolver::MMMemorySystemCmd::doIt: "
            "Give a flag to the command!");
        return MStatus::kFailure;
    }

    if (m_memory_unit == mmmemory::MemoryUnit::kBytes) {
        // It is only possible to return a maximum of "unsigned int"
        // (unsigned 32-bit number) from a Maya command, but our
        // maximum may exceed that size, so we must return the full
        // number converted to a string, then have the Python (or
        // MEL?) code convert that to an integer.
        MString number_mstring = mmmayastring::numberToMString(bytes_value);
        MMMemorySystemCmd::setResult(number_mstring);
    } else {
        double outResult =
            mmmemory::bytes_as_double(bytes_value, m_memory_unit);
        MMMemorySystemCmd::setResult(outResult);
    }
    return status;
}

}  // namespace mmsolver
