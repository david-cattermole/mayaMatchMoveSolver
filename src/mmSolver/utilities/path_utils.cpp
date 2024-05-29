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

#include "path_utils.h"

// Maya
#include <maya/MFileObject.h>
#include <maya/MStatus.h>
#include <maya/MString.h>

// MM Solver
#include "debug_utils.h"

namespace mmpath {

// This changes the given 'file_path' directly to a resolve file path,
// or returns a non-MStatus::kSuccess status.
MStatus resolve_input_file_path(MString &file_path) {
    MStatus status = MStatus::kSuccess;
    const bool verbose = false;

    auto file_object = MFileObject();
    file_object.setRawFullName(file_path);
    file_object.setResolveMethod(MFileObject::kInputFile);

    bool path_exists = file_object.exists();
    if (!path_exists) {
        MString resolved_file_path = file_object.resolvedFullName();
        status = MStatus::kFailure;
        MMSOLVER_MAYA_VRB(
            "mmpath::resolve_input_file_path: Could not find file path "
            << "\"" << file_path.asChar() << "\", resolved path "
            << "\"" << resolved_file_path.asChar() << "\".");
        return status;
    }

    MString resolved_file_path = file_object.resolvedFullName();
    status = MStatus::kFailure;
    if (resolved_file_path.length() > 0) {
        MMSOLVER_MAYA_VRB("mmpath::resolve_input_file_path: resolved file path "
                          << "\"" << resolved_file_path.asChar() << "\".");
        file_path = file_object.resolvedFullName();
        status = MStatus::kSuccess;
    }
    return status;
}

}  // namespace mmpath
