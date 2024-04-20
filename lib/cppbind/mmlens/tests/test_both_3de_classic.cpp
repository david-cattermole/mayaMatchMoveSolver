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

#include "test_both_3de_classic.h"

#include <mmlens/mmlens.h>

#include <algorithm>
#include <iostream>
#include <vector>

#include "common.h"

int test_both_3de_classic(const size_t width, const size_t height,
                          const bool multithread, const int verbosity) {
    const auto test_name = "test_both_3de_classic";
    const auto print_prefix =
        "test_both_3de_classic: undistort/redistort output";

    const size_t out_data_stride = 4;  // 4 channels - RGBA
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

    auto lens = mmlens::Parameters3deClassic();
    lens.distortion = 0.1;
    lens.anamorphic_squeeze = 1.0;
    lens.curvature_x = 0.0;
    lens.curvature_y = 0.0;
    lens.quartic_distortion = 0.1;

    test_both<float, mmlens::Parameters3deClassic>(
        test_name, print_prefix, width, height, out_data_vec, out_data_stride,
        camera_parameters, lens, multithread, verbosity);

    return 0;
}
