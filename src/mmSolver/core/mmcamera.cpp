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
 */

#include "mmcamera.h"

// STL
#include <cmath>

// MM Solver
#include "mmSolver/utilities/debug_utils.h"

namespace mmcamera {

double angleOfViewFromFocalLengthFactor(double focalLengthFactor) {
    return 2.0 * std::atan(1.0 / focalLengthFactor);
}

double focalLengthFromAngleOfView(const double angleOfView_radians,
                                  const double filmBack_mm) {
    return (0.5 * filmBack_mm) / std::tan(angleOfView_radians * 0.5);
}

}  // namespace mmcamera
