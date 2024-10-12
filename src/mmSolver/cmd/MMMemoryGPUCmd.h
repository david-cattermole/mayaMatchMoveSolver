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
 * 'mmMemoryGPU' Command is responsible for querying details about
 * the operating systems's memory.
 *
 * MEL:
 *     // Return the number of used memory by the image cache.
 *     mmMemoryGPU -query -total -asMegaBytes;
 *     mmMemoryGPU -query -free -asMegaBytes;
 *     mmMemoryGPU -query -used -asMegaBytes;
 *
 */

#ifndef MAYA_MM_MEMORY_GPU_CMD_H
#define MAYA_MM_MEMORY_GPU_CMD_H

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

class MMMemoryGPUCmd : public MPxCommand {
public:
    MMMemoryGPUCmd()
        : m_memory_total(false)
        , m_memory_free(false)
        , m_memory_used(false)
        , m_memory_unit(mmmemory::MemoryUnit::kBytes){};

    virtual ~MMMemoryGPUCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    bool m_memory_total;
    bool m_memory_free;
    bool m_memory_used;
    mmmemory::MemoryUnit m_memory_unit;
};

}  // namespace mmsolver

#endif  // MAYA_MM_MEMORY_GPU_CMD_H
