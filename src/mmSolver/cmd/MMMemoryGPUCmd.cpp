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

#include "MMMemoryGPUCmd.h"

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
#include "mmSolver/utilities/memory_gpu_utils.h"
#include "mmSolver/utilities/path_utils.h"
#include "mmSolver/utilities/string_utils.h"

// Command arguments and command name:
#define MEMORY_TOTAL_FLAG "-tot"
#define MEMORY_TOTAL_FLAG_LONG "-total"

#define MEMORY_FREE_FLAG "-fre"
#define MEMORY_FREE_FLAG_LONG "-free"

#define MEMORY_USED_FLAG "-usd"
#define MEMORY_USED_FLAG_LONG "-used"

#define MEMORY_AS_KILOBYTES_FLAG "-kb"
#define MEMORY_AS_KILOBYTES_FLAG_LONG "-asKiloBytes"

#define MEMORY_AS_MEGABYTES_FLAG "-mb"
#define MEMORY_AS_MEGABYTES_FLAG_LONG "-asMegaBytes"

#define MEMORY_AS_GIGABYTES_FLAG "-gb"
#define MEMORY_AS_GIGABYTES_FLAG_LONG "-asGigaBytes"

namespace mmsolver {

MMMemoryGPUCmd::~MMMemoryGPUCmd() {}

void *MMMemoryGPUCmd::creator() { return new MMMemoryGPUCmd(); }

MString MMMemoryGPUCmd::cmdName() { return MString("mmMemoryGPU"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMMemoryGPUCmd::hasSyntax() const { return true; }

bool MMMemoryGPUCmd::isUndoable() const { return false; }

/*
 * Add flags to the command syntax
 */
MSyntax MMMemoryGPUCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(true);
    syntax.enableEdit(false);

    syntax.addFlag(MEMORY_TOTAL_FLAG, MEMORY_TOTAL_FLAG_LONG);
    syntax.addFlag(MEMORY_FREE_FLAG, MEMORY_FREE_FLAG_LONG);
    syntax.addFlag(MEMORY_USED_FLAG, MEMORY_USED_FLAG_LONG);

    syntax.addFlag(MEMORY_AS_KILOBYTES_FLAG, MEMORY_AS_KILOBYTES_FLAG_LONG);
    syntax.addFlag(MEMORY_AS_MEGABYTES_FLAG, MEMORY_AS_MEGABYTES_FLAG_LONG);
    syntax.addFlag(MEMORY_AS_GIGABYTES_FLAG, MEMORY_AS_GIGABYTES_FLAG_LONG);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMMemoryGPUCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (!argData.isQuery()) {
        status = MStatus::kFailure;
        MMSOLVER_MAYA_ERR(
            "mmsolver::MMMemoryGPUCmd::parseArgs: "
            "Command must be in query mode!");
        return status;
    }

    m_memory_total = argData.isFlagSet(MEMORY_TOTAL_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_memory_free = argData.isFlagSet(MEMORY_FREE_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_memory_used = argData.isFlagSet(MEMORY_USED_FLAG, &status);
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

MStatus MMMemoryGPUCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kSuccess;
    const bool verbose = false;

    // Read all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    size_t bytes_value = 0;
    if (m_memory_total) {
        status = mmmemorygpu::memory_total_size_in_bytes(bytes_value);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    } else if (m_memory_free) {
        status = mmmemorygpu::memory_free_size_in_bytes(bytes_value);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    } else if (m_memory_used) {
        status = mmmemorygpu::memory_used_size_in_bytes(bytes_value);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        MMSOLVER_MAYA_ERR(
            "mmsolver::MMMemoryGPUCmd::doIt: "
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
        MMMemoryGPUCmd::setResult(number_mstring);
    } else {
        double outResult =
            mmmemory::bytes_as_double(bytes_value, m_memory_unit);
        MMMemoryGPUCmd::setResult(outResult);
    }

    return status;
}

}  // namespace mmsolver
