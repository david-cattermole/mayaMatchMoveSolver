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
 * Set the parameters for the Maya DAG or MM Scene Graph to have an
 * effect.
 */

#ifndef MM_SOLVER_CORE_BUNDLE_ADJUST_SET_PARAMETERS_H
#define MM_SOLVER_CORE_BUNDLE_ADJUST_SET_PARAMETERS_H

#include "adjust_data.h"

namespace mmsolver {

MStatus setParameters(const int numberOfParameters, const double *parameters,
                      SolverData *userData);

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_BUNDLE_ADJUST_SET_PARAMETERS_H
