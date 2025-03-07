/*
 * Copyright (C) 2025 David Cattermole.
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
 * Define a frame.
 */

#ifndef MM_SOLVER_CORE_FRAME_H
#define MM_SOLVER_CORE_FRAME_H

// STL
#include <climits>

namespace mmsolver {

typedef uint32_t FrameCount;
typedef int32_t FrameIndex;
typedef int32_t FrameNumber;

#define FRAME_NUMBER_MAX INT_MAX
#define FRAME_NUMBER_MIN INT_MIN

}  // namespace mmsolver

#endif  // MM_SOLVER_CORE_FRAME_H
