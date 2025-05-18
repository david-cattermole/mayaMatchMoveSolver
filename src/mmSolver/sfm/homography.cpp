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

#include "homography.h"

// STL
#include <algorithm>
#include <array>
#include <cmath>
#include <fstream>
#include <iostream>
#include <iterator>
#include <limits>
#include <list>
#include <map>
#include <memory>
#include <string>
#include <thread>
#include <vector>

// OpenMVG
#ifdef MMSOLVER_USE_OPENMVG

#include <openMVG/numeric/numeric.h>

#include <openMVG/multiview/solver_homography_kernel.hpp>
#include <openMVG/numeric/eigen_alias_definition.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansac.hpp>
#include <openMVG/robust_estimation/robust_estimator_ACRansacKernelAdaptator.hpp>
#include <openMVG/types.hpp>

#endif  // MMSOLVER_USE_OPENMVG

#include "mmSolver/sfm/sfm_utils.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/number_utils.h"

namespace mmsolver {
namespace sfm {

using KernelType = openMVG::robust::ACKernelAdaptor<
    openMVG::homography::kernel::FourPointSolver,
    openMVG::homography::kernel::AsymmetricError, openMVG::UnnormalizerI,
    openMVG::Mat3>;

bool robust_homography(const openMVG::Mat &x1, const openMVG::Mat &x2,
                       openMVG::Mat3 &homography_matrix,
                       const std::pair<uint32_t, uint32_t> &size_ima1,
                       const std::pair<uint32_t, uint32_t> &size_ima2,
                       const uint32_t max_iteration_count) {
    // Enable to print out 'MMSOLVER_MAYA_VRB' results.
    const bool verbose = false;

    // Upper bound pixel tolerance for residual errors.
    const double error_max = std::numeric_limits<double>::infinity();

    // The amount of pixel error that is computed.
    double out_error_max = std::numeric_limits<double>::infinity();

    MMSOLVER_MAYA_VRB("robust_homography: x1: " << x1);
    MMSOLVER_MAYA_VRB("robust_homography: x2: " << x2);
    MMSOLVER_MAYA_VRB("robust_homography: size_ima1: "
                      << size_ima1.first << ", " << size_ima1.second);
    MMSOLVER_MAYA_VRB("robust_homography: size_ima2: "
                      << size_ima2.first << ", " << size_ima2.second);
    MMSOLVER_MAYA_VRB(
        "robust_homography: max_iteration_count: " << max_iteration_count);

    double error_upper_bound = std::numeric_limits<double>::infinity();
    if (error_max != std::numeric_limits<double>::infinity()) {
        error_upper_bound = (error_max * error_max);
    }

    // point to point error model.
    auto point_to_line = false;

    KernelType kernel(x1, size_ima1.first, size_ima1.second, x2,
                      size_ima2.first, size_ima2.second, point_to_line);

    // Robustly estimate the Homography matrix with A Contrario (AC)
    // RANSAC.
    std::vector<uint32_t> vec_inliers;
    const auto ac_ransac_output = openMVG::robust::ACRANSAC(
        kernel, vec_inliers, max_iteration_count, &homography_matrix,
        error_upper_bound, verbose);
    out_error_max = ac_ransac_output.first;

    auto minimum_samples = KernelType::Solver::MINIMUM_SAMPLES;
    MMSOLVER_MAYA_VRB(
        "robust_homography: minimum_samples: " << minimum_samples);
    MMSOLVER_MAYA_VRB("robust_homography: samples: " << vec_inliers.size());
    if (vec_inliers.size() < minimum_samples) {
        // no sufficient coverage (not enough 2D points given that
        // match)
        return false;
    }

    // Change the translation to be in the range 0.0 to (-/+) 1.0.
    //
    // TODO: Confirm this works correctly. Ideally this matrix should
    // be image independent, and so we want to remove the image
    // resolution from the matrix.
    homography_matrix.row(0)[2] = homography_matrix.row(0)[2] / size_ima2.first;
    homography_matrix.row(1)[2] =
        homography_matrix.row(0)[2] / size_ima2.second;

    MMSOLVER_MAYA_VRB("Found a Homography matrix:");
    MMSOLVER_MAYA_VRB("- matrix: " << homography_matrix);
    MMSOLVER_MAYA_VRB("- error: " << out_error_max << " pixels");

    MMSOLVER_MAYA_VRB("- #matches: " << x1.size());
    for (auto i = 0; i < x1.size(); i++) {
        auto coord_x_a = x1.col(i)[0];
        auto coord_y_a = x1.col(i)[1];
        auto coord_x_b = x2.col(i)[0];
        auto coord_y_b = x2.col(i)[1];
        MMSOLVER_MAYA_VRB("  - #match: " << i << " = " << coord_x_a << ","
                                         << coord_y_a << " <-> " << coord_x_b
                                         << "," << coord_y_b);
    }
    MMSOLVER_MAYA_VRB("- #inliers: " << vec_inliers.size());

    return true;
}

bool compute_homography(
    const int32_t image_width_a, const int32_t image_width_b,
    const int32_t image_height_a, const int32_t image_height_b,
    const std::vector<std::pair<double, double>> &marker_coords_a,
    const std::vector<std::pair<double, double>> &marker_coords_b,
    openMVG::Mat3 &homography_matrix) {
    openMVG::Mat marker_coords_matrix_a =
        convert_marker_coords_to_matrix(marker_coords_a);
    openMVG::Mat marker_coords_matrix_b =
        convert_marker_coords_to_matrix(marker_coords_b);

    const std::pair<uint32_t, uint32_t> image_size_a(
        static_cast<uint32_t>(image_width_a),
        static_cast<uint32_t>(image_height_a));
    const std::pair<uint32_t, uint32_t> image_size_b(
        static_cast<uint32_t>(image_width_b),
        static_cast<uint32_t>(image_height_b));

    const auto num_max_iter = 4096;
    bool robust_pose_ok = robust_homography(
        marker_coords_matrix_a, marker_coords_matrix_b, homography_matrix,
        image_size_a, image_size_b, num_max_iter);
    if (!robust_pose_ok) {
        MMSOLVER_MAYA_ERR("Robust homography estimation failure.");
        return false;
    }
    return true;
}

}  // namespace sfm
}  // namespace mmsolver
