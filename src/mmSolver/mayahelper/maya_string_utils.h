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
 * Generic string helper functions for Maya.
 */

#ifndef MAYA_STRING_UTILS_H
#define MAYA_STRING_UTILS_H

// STL
#include <cmath>  // fabs
#include <iostream>
#include <sstream>  // stringstream
#include <string>

// MM Solver
#include "mmSolver/utilities/string_utils.h"

// Maya
#include <maya/MString.h>

namespace mmmayastring {

/*! Convert a number to a Maya MString
 *
 * Convert 42 to "42".
 */
template <typename NUM_TYPE>
MString numberToMString(NUM_TYPE num) {
    std::string string = mmstring::numberToString<NUM_TYPE>(num);
    MString mstring(string.c_str());
    return mstring;
}

/*! Convert a Maya MString to a number.
 *
 * Convert "3.14" to 3.14.
 */
template <typename NUM_TYPE>
NUM_TYPE mstringToNumber(const MString &text) {
    std::string text_string = text.asChar();
    return mmstring::stringToNumber<NUM_TYPE>(text_string);
}

}  // namespace mmmayastring

#endif  // MAYA_STRING_UTILS_H
