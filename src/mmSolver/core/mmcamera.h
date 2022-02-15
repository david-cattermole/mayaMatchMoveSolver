/*
 * Copyright (C) 2021 David Cattermole.
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
 * Camera geometry related functions.
 */

#ifndef MM_SOLVER_CORE_MM_CAMERA_H
#define MM_SOLVER_CORE_MM_CAMERA_H

// Internal
#include "mmdata.h"

namespace mmcamera {

// Returns the angle of view (in degrees) from a relative focal length factor.
double
angleOfViewFromFocalLengthFactor(
    double focalLengthFactor);

// Returns the focal length (in millimeters), from the field of view (in radians) and the film back (in millimeters).
double
focalLengthFromAngleOfView(
    const double angleOfView_radians,
    const double filmBack_mm);

} // namespace mmcamera

#endif // MM_SOLVER_CORE_MM_CAMERA_H
