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

#include <mmcore/mmdata.h>
#include <mmlens/lib.h>

#include "distortion_operations.h"
#include "distortion_structs.h"

namespace mmlens {

// This is assumed to be called by multiple threads at once.
void apply_undistort_3de_classic_f64__2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, TdeClassicParameters lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    const auto direction = DistortionDirection::kUndistort;

    auto lens = Distortion3deClassic();
    lens.set_parameter(0, lens_parameters.distortion);
    lens.set_parameter(1, lens_parameters.anamorphic_squeeze);
    lens.set_parameter(2, lens_parameters.curvature_x);
    lens.set_parameter(3, lens_parameters.curvature_y);
    lens.set_parameter(4, lens_parameters.quartic_distortion);

    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double, Distortion3deClassic>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, lens);
    return;
}

// This is assumed to be called by multiple threads at once.
void apply_redistort_3de_classic_f64__2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, TdeClassicParameters lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    const auto direction = DistortionDirection::kRedistort;

    auto lens = Distortion3deClassic();
    lens.set_parameter(0, lens_parameters.distortion);
    lens.set_parameter(1, lens_parameters.anamorphic_squeeze);
    lens.set_parameter(2, lens_parameters.curvature_x);
    lens.set_parameter(3, lens_parameters.curvature_y);
    lens.set_parameter(4, lens_parameters.quartic_distortion);

    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double, Distortion3deClassic>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, lens);
    return;
}

// This is assumed to be called by multiple threads at once.
void apply_undistort_3de_classic_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, TdeClassicParameters lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    const auto direction = DistortionDirection::kUndistort;

    auto lens = Distortion3deClassic();
    lens.set_parameter(0, lens_parameters.distortion);
    lens.set_parameter(1, lens_parameters.anamorphic_squeeze);
    lens.set_parameter(2, lens_parameters.curvature_x);
    lens.set_parameter(3, lens_parameters.curvature_y);
    lens.set_parameter(4, lens_parameters.quartic_distortion);

    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float, Distortion3deClassic>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, lens);
    return;
}

// This is assumed to be called by multiple threads at once.
void apply_redistort_3de_classic_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, TdeClassicParameters lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    const auto direction = DistortionDirection::kRedistort;

    auto lens = Distortion3deClassic();
    lens.set_parameter(0, lens_parameters.distortion);
    lens.set_parameter(1, lens_parameters.anamorphic_squeeze);
    lens.set_parameter(2, lens_parameters.curvature_x);
    lens.set_parameter(3, lens_parameters.curvature_y);
    lens.set_parameter(4, lens_parameters.quartic_distortion);

    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float, Distortion3deClassic>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, lens);
    return;
}

}  // namespace mmlens
