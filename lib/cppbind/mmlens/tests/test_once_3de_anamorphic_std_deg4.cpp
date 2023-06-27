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

#include "test_once_3de_anamorphic_std_deg4.h"

#include <mmlens/mmlens.h>

#include <algorithm>
#include <iostream>
#include <vector>

#include "common.h"

int test_once_3de_anamorphic_std_deg4(const size_t width, const size_t height,
                                      const int verbosity) {
    const auto test_name = "test_once_3de_anamorphic_std_deg4";
    const auto identity_prefix = "test_once_3de_anamorphic_std_deg4: start";
    const auto undistort_prefix =
        "test_once_3de_anamorphic_std_deg4: undistort";
    const auto redistort_prefix =
        "test_once_3de_anamorphic_std_deg4: redistort";
    const auto print_prefix = "test_once_3de_anamorphic_std_deg4: output";

    const size_t data_stride = 2;  // 2D data

    const bool print_identity = false;
    std::vector<double> in_data_vec =
        generate_st_map_identity<kCoordinateSystemNDC, double, print_identity>(
            identity_prefix, width, height, data_stride);
    std::vector<double> temp_data_vec(width * height * data_stride);
    std::vector<double> out_data_vec(width * height * data_stride);

    const double focal_length_cm = 3.5;
    const double film_back_width_cm = 3.6;
    const double film_back_height_cm = 2.4;
    const double pixel_aspect = 1.0;
    const double lens_center_offset_x_cm = 0.0;
    const double lens_center_offset_y_cm = 0.0;

    const double degree2_cx02 = 0.05;
    const double degree2_cy02 = 0.05;
    const double degree2_cx22 = -0.05;
    const double degree2_cy22 = -0.05;
    const double degree4_cx04 = 0.05;
    const double degree4_cy04 = 0.05;
    const double degree4_cx24 = -0.05;
    const double degree4_cy24 = -0.05;
    const double degree4_cx44 = 0.15;
    const double degree4_cy44 = 0.15;
    const double lens_rotation = 45.0;
    const double squeeze_x = 1.1;
    const double squeeze_y = 1.0;

    auto lens = mmlens::LensModel3deAnamorphicDeg4RotateSqueezeXY();
    lens.setFocalLength(focal_length_cm);
    lens.setFilmBackWidth(film_back_width_cm);
    lens.setFilmBackHeight(film_back_height_cm);
    lens.setPixelAspect(pixel_aspect);
    lens.setLensCenterOffsetX(lens_center_offset_x_cm);
    lens.setLensCenterOffsetY(lens_center_offset_y_cm);

    lens.setDegree2Cx02(degree2_cx02);
    lens.setDegree2Cy02(degree2_cy02);
    lens.setDegree2Cx22(degree2_cx22);
    lens.setDegree2Cy22(degree2_cy22);
    lens.setDegree4Cx04(degree4_cx04);
    lens.setDegree4Cy04(degree4_cy04);
    lens.setDegree4Cx24(degree4_cx24);
    lens.setDegree4Cy24(degree4_cy24);
    lens.setDegree4Cx44(degree4_cx44);
    lens.setDegree4Cy44(degree4_cy44);
    lens.setSqueezeX(squeeze_x);
    lens.setSqueezeY(squeeze_y);

    test_once<double, mmlens::LensModel3deAnamorphicDeg4RotateSqueezeXY,
              data_stride>(test_name, undistort_prefix, redistort_prefix,
                           print_prefix, width, height, in_data_vec,
                           temp_data_vec, out_data_vec, lens, verbosity);

    return 0;
}
