/*
 * Copyright (C) 2022 David Cattermole.
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
 * Header for mmReadImage Maya command.
 */

#ifndef MAYA_MM_READ_IMAGE_CMD_H
#define MAYA_MM_READ_IMAGE_CMD_H

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPxCommand.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>
#include <maya/MSyntax.h>

namespace mmsolver {

class MMReadImageCmd : public MPxCommand {
public:
    MMReadImageCmd() : m_file_path(){};

    virtual ~MMReadImageCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs(const MArgList &args);

    MString m_file_path;
    bool m_query_width_height;
    bool m_query_data_header;
    bool m_query_resolve_file_path;
};

}  // namespace mmsolver

#endif  // MAYA_MM_READ_IMAGE_CMD_H
