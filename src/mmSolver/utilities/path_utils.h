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
 * Generic path helper functions.
 */

#ifndef PATH_UTILS_H
#define PATH_UTILS_H

// STL
#include <cmath>  // fabs
#include <iostream>
#include <sstream>  // stringstream
#include <string>

// Maya
#include <maya/MStatus.h>
#include <maya/MString.h>

namespace mmpath {

MStatus resolve_input_file_path(MString &file_path);

}  // namespace mmpath

#endif  // PATH_UTILS_H
