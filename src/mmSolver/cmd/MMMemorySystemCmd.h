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
 * 'mmMemorySystem' Command is responsible for querying details about
 * the operating systems's memory.
 *
 * MEL:
 *     // Return the number of used memory by the image cache.
 *     mmMemorySystem -query -systemPhysicalMemoryTotal -asMegaBytes;
 *     mmMemorySystem -query -systemPhysicalMemoryFree -asMegaBytes;
 *     mmMemorySystem -query -systemPhysicalMemoryUsed -asMegaBytes;
 *
 *     // Return the amount of memory used by the current process.
 *     mmMemorySystem -query -processMemoryUsed -asMegaBytes;
 *
 */

#ifndef MAYA_MM_MEMORY_SYSTEM_CMD_H
#define MAYA_MM_MEMORY_SYSTEM_CMD_H

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MSyntax.h>

// MM Solver
#include "mmSolver/utilities/memory_utils.h"

namespace mmsolver {

class MMMemorySystemCmd : public MPxCommand {
public:
    MMMemorySystemCmd()
        : m_system_physical_memory_total(false)
        , m_system_physical_memory_free(false)
        , m_system_physical_memory_used(false)
        , m_process_memory_used(false)
        , m_memory_unit(mmmemory::MemoryUnit::kBytes){};

    virtual ~MMMemorySystemCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    bool m_system_physical_memory_total;
    bool m_system_physical_memory_free;
    bool m_system_physical_memory_used;
    bool m_process_memory_used;
    mmmemory::MemoryUnit m_memory_unit;
};

}  // namespace mmsolver

#endif  // MAYA_MM_MEMORY_SYSTEM_CMD_H
