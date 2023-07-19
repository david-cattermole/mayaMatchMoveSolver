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
 * Generic string helper functions.
 */

#ifndef MM_SOLVER_LIBS_STRING_H
#define MM_SOLVER_LIBS_STRING_H

#include <cmath>  // fabs
#include <iostream>
#include <sstream>  // stringstream
#include <string>

namespace mmstring {

/*! Convert a number to a string
 *
 * Convert 42 to "42".
 */
template <typename NUM_TYPE>
std::string numberToString(NUM_TYPE num) {
    std::stringstream ss;
    ss << num;
    return ss.str();
}

/*! Convert a number to a string with commas as separators.
 *
 * Convert an integer 10000 to "10,000".
 */
template <typename NUM_TYPE>
std::string numberToStringWithCommas(NUM_TYPE num) {
    auto number_as_string = numberToString(num);

    int n = number_as_string.length() - 3;
    int end = (num >= 0) ? 0 : 1;  // Support for negative numbers
    while (n > end) {
        number_as_string.insert(n, ",");
        n -= 3;
    }

    return number_as_string;
}

/*! Convert a string to a number.
 *
 * Convert "3.14" to 3.14.
 */
template <typename NUM_TYPE>
NUM_TYPE stringToNumber(const std::string &text) {
    std::stringstream ss(text);
    NUM_TYPE result;
    ss >> result;
    if (!result) {
        result = 0;
    }
    return result;
}

}  // namespace mmstring

#endif  // MM_SOLVER_LIBS_STRING_H
