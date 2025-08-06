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
 * Calculate 2D homography matrix, used to align two sets of 2D
 * points.
 */

#ifndef MM_SOLVER_SFM_HOMOGRAPHY_H
#define MM_SOLVER_SFM_HOMOGRAPHY_H

// STL
#include <cmath>
#include <vector>

// mmsolverlibs
#include <mmsolverlibs/openmvg_wrapper.h>

namespace mmsolver {
namespace sfm {

// 3x3 homography matrix representation
struct HomographyMatrix {
    double data[9];

    HomographyMatrix() {
        for (int i = 0; i < 9; ++i) {
            data[i] = 0.0;
        }
    }

    double &operator()(int row, int col) { return data[row * 3 + col]; }

    const double &operator()(int row, int col) const {
        return data[row * 3 + col];
    }
};

bool robust_homography(const std::vector<std::pair<double, double>> &points1,
                       const std::vector<std::pair<double, double>> &points2,
                       HomographyMatrix &homography_matrix,
                       const std::pair<uint32_t, uint32_t> &size_ima1,
                       const std::pair<uint32_t, uint32_t> &size_ima2,
                       const uint32_t max_iteration_count);

bool compute_homography(
    const int32_t image_width_a, const int32_t image_width_b,
    const int32_t image_height_a, const int32_t image_height_b,
    const std::vector<std::pair<double, double>> &marker_coords_a,
    const std::vector<std::pair<double, double>> &marker_coords_b,
    HomographyMatrix &homography_matrix);

}  // namespace sfm
}  // namespace mmsolver

#endif  // MM_SOLVER_SFM_HOMOGRAPHY_H
