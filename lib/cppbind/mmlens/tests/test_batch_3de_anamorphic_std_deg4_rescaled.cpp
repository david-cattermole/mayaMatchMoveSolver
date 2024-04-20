/*
 * Copyright (C) 2023 David Cattermole.
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

#include "test_batch_3de_anamorphic_std_deg4_rescaled.h"

#include <mmlens/mmlens.h>

#include <algorithm>
#include <iostream>
#include <vector>

#include "common.h"

int test_batch_3de_anamorphic_std_deg4_rescaled(const size_t width,
                                                const size_t height,
                                                const bool multithread,
                                                const int verbosity) {
    const auto test_name = "test_batch_3de_anamorphic_std_deg4_rescaled";
    const auto undistort_prefix =
        "test_batch_3de_anamorphic_std_deg4_rescaled: undistort";
    const auto redistort_prefix =
        "test_batch_3de_anamorphic_std_deg4_rescaled: redistort";
    const auto print_prefix =
        "test_batch_3de_anamorphic_std_deg4_rescaled: output";

    const size_t in_data_stride = 2;   // 2D data
    const size_t out_data_stride = 4;  // 4 channels - RGBA
    std::vector<double> in_data_vec(width * height * in_data_stride);
    std::vector<float> out_data_vec(width * height * out_data_stride);

    const double focal_length_cm = 3.5;
    const double film_back_width_cm = 3.6;
    const double film_back_height_cm = 2.4;
    const double pixel_aspect = 1.0;
    const double lens_center_offset_x_cm = 0.0;
    const double lens_center_offset_y_cm = 0.0;
    const mmlens::CameraParameters camera_parameters{
        focal_length_cm, film_back_width_cm,      film_back_height_cm,
        pixel_aspect,    lens_center_offset_x_cm, lens_center_offset_y_cm};

    auto lens = mmlens::Parameters3deAnamorphicStdDeg4Rescaled();
    lens.degree2_cx02 = 0.05;
    lens.degree2_cy02 = 0.05;
    lens.degree2_cx22 = -0.05;
    lens.degree2_cy22 = -0.05;
    lens.degree4_cx04 = 0.05;
    lens.degree4_cy04 = 0.05;
    lens.degree4_cx24 = -0.05;
    lens.degree4_cy24 = -0.05;
    lens.degree4_cx44 = 0.15;
    lens.degree4_cy44 = 0.15;
    lens.lens_rotation = 45.0;
    lens.squeeze_x = 1.1;
    lens.squeeze_y = 1.0;
    lens.rescale = 2.0;

    test_batch<double, float, mmlens::Parameters3deAnamorphicStdDeg4Rescaled>(
        test_name, undistort_prefix, redistort_prefix, print_prefix, width,
        height, in_data_vec, in_data_stride, out_data_vec, out_data_stride,
        camera_parameters, lens, multithread, verbosity);

    return 0;
}
