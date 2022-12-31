/*
 * Copyright (C) 2022 David Cattermole.
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

#ifndef MM_SOLVER_RENDER_RENDER_MODE_H
#define MM_SOLVER_RENDER_RENDER_MODE_H

namespace mmsolver {
namespace render {

enum class RenderMode : short {
    kZero = 0,
    kOne = 1,
    kTwo = 2,
    kThree = 3,
    kFour = 4,
    kRenderModeCount,
};

}  // namespace render
}  // namespace mmsolver

#endif  // MM_SOLVER_RENDER_RENDER_MODE_H
