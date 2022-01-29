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

// Cross
const float shape_a_points[][3] = {
    // Center Left
    {-0.20f, 0.0f, 0.0f},
    {-1.0f, 0.0f, 0.0f},

    // Center Right
    {0.20f, 0.0f, 0.0f},
    {1.0f, 0.0f, 0.0f},

    // Center Top
    {0.0f, 0.20f, 0.0f},
    {0.0f, 1.0f, 0.0f},

    // Center Bottom
    {0.0f, -0.20f, 0.0f},
    {0.0f, -1.0f, 0.0f},
};
const int shape_a_points_count = 2 * 4;

const unsigned int shape_a_line_indexes[][2] = {
    // Center Left
    {0, 1},
    // Center Right
    {2, 3},
    // Center Top
    {4, 5},
    // Center Bottom
    {6, 7},
};
const int shape_a_line_indexes_count = 4;

// Box shape.
const float shape_b_points[][3] = {
    // Top left
    {-0.50f, 1.00f, 0.0f},
    {-1.00f, 1.00f, 0.0f},
    {-1.00f, 0.50f, 0.0f},

    // Top right
    {0.50f, 1.00f, 0.0f},
    {1.00f, 1.00f, 0.0f},
    {1.00f, 0.50f, 0.0f},

    // Bottom left
    {-0.50f, -1.00f, 0.0f},
    {-1.00f, -1.00f, 0.0f},
    {-1.00f, -0.50f, 0.0f},

    // Bottom right
    {0.50f, -1.00f, 0.0f},
    {1.00f, -1.00f, 0.0f},
    {1.00f, -0.50f, 0.0f}
};

const unsigned int shape_b_line_indexes[][2] = {
    // Top left
    {0, 1},
    {1, 2},
    // Top right
    {3, 4},
    {4, 5},
    // Bottom left
    {6, 7},
    {7, 8},
    // Bottom right
    {9, 10},
    {10, 11},
};

const int shape_b_points_count = 3 * 4;
const int shape_b_line_indexes_count = 2 * 4;

} // namespace mmsolver
