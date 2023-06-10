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

#include "test_once_3de_classic.h"

#include <mmlens/mmlens.h>

#include <algorithm>
#include <iostream>
#include <vector>

#include "common.h"

int test_once_3de_classic() {
    const auto test_name = "test_once_3de_classic";
    const auto identity_prefix = "test_once_3de_classic: start";
    const auto undistort_prefix = "test_once_3de_classic: undistort";
    const auto undistort_compare = " -> ";
    const auto redistort_prefix = "test_once_3de_classic: redistort";
    const auto redistort_compare = " -> ";
    const auto print_prefix = "test_once_3de_classic: output";
    const auto print_compare = " == ";
    const bool do_print = true;

    const size_t width = 8;
    const size_t height = 8;
    const size_t stride = 2;  // 2D data

    const bool print_identity = false;
    std::vector<double> in_data_vec =
        generate_st_map_identity<kCoordinateSystemNDC, double, print_identity>(
            identity_prefix, width, height, stride);
    std::vector<double> temp_data_vec(width * height * stride);
    std::vector<double> out_data_vec(width * height * stride);

    double* in_data = &in_data_vec[0];
    double* temp_data = &temp_data_vec[0];
    double* out_data = &out_data_vec[0];
    const size_t in_data_size = width * height * stride;
    const size_t temp_data_size = width * height * stride;
    const size_t out_data_size = width * height * stride;

    double focal_length_cm = 3.5;
    double film_back_width_cm = 3.6;
    double film_back_height_cm = 2.4;
    double pixel_aspect = 1.0;
    double lens_center_offset_x_cm = 0.0;
    double lens_center_offset_y_cm = 0.0;

    double distortion = 0.1;
    double anamorphic_squeeze = 1.0;
    double curvature_x = 0.0;
    double curvature_y = 0.0;
    double quartic_distortion = 0.1;

    auto lens = mmlens::LensModel3deClassic();
    lens.setFocalLength(focal_length_cm);
    lens.setFilmBackWidth(film_back_width_cm);
    lens.setFilmBackHeight(film_back_height_cm);
    lens.setPixelAspect(pixel_aspect);
    lens.setLensCenterOffsetX(lens_center_offset_x_cm);
    lens.setLensCenterOffsetY(lens_center_offset_y_cm);

    lens.setDistortion(distortion);
    lens.setAnamorphicSqueeze(anamorphic_squeeze);
    lens.setCurvatureX(curvature_x);
    lens.setCurvatureY(curvature_y);
    lens.setQuarticDistortion(quartic_distortion);

    if (do_print) {
        std::cout << test_name << " hash : " << lens.hashValue() << std::endl;
    }

    // Undistort input data.
    apply_distortion_loop<double, double, mmlens::LensModel3deClassic,
                          kDirectionUndistort>(width, height, stride, stride,
                                               in_data, temp_data, lens);
    if (do_print) {
        print_data_2d_compare(undistort_prefix, undistort_compare, width,
                              height, stride, stride, in_data, temp_data);
    }

    // Redistort input data.
    apply_distortion_loop<double, double, mmlens::LensModel3deClassic,
                          kDirectionRedistort>(width, height, stride, stride,
                                               temp_data, out_data, lens);
    if (do_print) {
        print_data_2d_compare(redistort_prefix, redistort_compare, width,
                              height, stride, stride, temp_data, out_data);
    }

    print_data_2d_compare<double, double>(print_prefix, print_compare, width,
                                          height, stride, stride, in_data,
                                          out_data);

    return 0;
}
