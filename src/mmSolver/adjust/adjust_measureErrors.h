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
 * Measure the deviation/error distances between Markers and Bundles.
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_MEASURE_ERRORS_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_MEASURE_ERRORS_H

// STL
#include <vector>

// Maya
#include <maya/MStatus.h>

// MM Solver
#include "adjust_data.h"

namespace mmsolver {

void measureErrors(const int numberOfErrors, const int numberOfMarkerErrors,
                   const int numberOfAttrStiffnessErrors,
                   const int numberOfAttrSmoothnessErrors,
                   const std::vector<bool> &frameIndexEnable,
                   const std::vector<bool> &errorMeasurements,
                   const double imageWidth, double *errors, SolverData *ud,
                   double &error_avg, double &error_max, double &error_min,
                   MStatus &status);

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_MEASURE_ERRORS_H
