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
 * Utilities and definitions related to numbers.
 */

#ifndef NUMBER_UTILS_H
#define NUMBER_UTILS_H

// Radians / Degrees
#define RADIANS_TO_DEGREES 57.295779513082323    // 180.0/M_PI
#define DEGREES_TO_RADIANS 0.017453292519943295  // M_PI/180.0

// Conversion constants
#define MM_TO_INCH 0.03937007874015748  // 0.03937
#define MM_TO_CM 0.1
#define CM_TO_MM 10.0
#define INCH_TO_MM 25.4
#define INCH_TO_CM 2.54

// Memory Conversion
#define BYTES_TO_KILOBYTES 1024         // int(pow(2, 10))
#define BYTES_TO_MEGABYTES 1048576      // int(pow(2, 20))
#define BYTES_TO_GIGABYTES 1073741824   // int(pow(2, 30))
#define KILOBYTES_TO_MEGABYTES 1024     // int(pow(2, 10))
#define KILOBYTES_TO_GIGABYTES 1048576  // int(pow(2, 20))

namespace number {

/*! Compare if two floating point numbers are equal.
 *
 * Deprecated, in favour of 'isApproxEqual'.
 *
 * @param left [in] First number to compare.
 * @param right [in] Second number to compare.
 * @return true or false, based on if the numbers are approximately equal.
 */
bool floatApproxEqual(const float left, const float right);

/*! Compare doubles or float numbers for equality.
 *
 * @tparam T A floating-point number, for example float or double.
 * @param left [in] First number to compare.
 * @param right [in] Second number to compare.
 * @param epsilon [in] Allowed difference between numbers.
 * @return true or false, based on if the numbers are approximately equal.
 */
template <typename T>
inline bool isApproxEqual(const T left, const T right,
                          const T epsilon = 0.0001) {
    return fabs(left - right) < epsilon;
}

}  // namespace number

#endif  // NUMBER_UTILS_H
