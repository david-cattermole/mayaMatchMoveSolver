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

namespace mmsolver {

// 3D Cross
const float cross_shape_points[][3] = {
    // -X Axis
    {-0.20f, 0.0f, 0.0f},
    {-1.0f, 0.0f, 0.0f},

    // +X Axis
    {0.20f, 0.0f, 0.0f},
    {1.0f, 0.0f, 0.0f},

    // -Y Axis
    {0.0f, -0.20f, 0.0f},
    {0.0f, -1.0f, 0.0f},

    // +Y Axis
    {0.0f, +0.20f, 0.0f},
    {0.0f, +1.0f, 0.0f},

    // -Z Axis
    {0.0f, 0.0f, -0.20f},
    {0.0f, 0.0f, -1.0f},

    // +Z Axis
    {0.0f, 0.0f, 0.20f},
    {0.0f, 0.0f, 1.0f},
};
const int cross_shape_points_count = 2 * 6;

const unsigned int cross_shape_line_indexes[][2] = {
    {0, 1},
    {2, 3},
    {4, 5},
    {6, 7},
    {8, 9},
    {10, 11},
};
const int cross_shape_line_indexes_count = 6;

} // namespace mmsolver
