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
#include <mmlens/_cxxbridge.h>

namespace mmlens {

// Apply lens distortion to a single 2D coordinate.
template <DistortionDirection DIRECTION, class IN_TYPE, class OUT_TYPE,
          class LENS_TYPE>
std::pair<OUT_TYPE, OUT_TYPE> apply_lens_distortion_once(
    const IN_TYPE in_x, const IN_TYPE in_y,
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    LENS_TYPE lens) {
    auto out_x = static_cast<OUT_TYPE>(0);
    auto out_y = static_cast<OUT_TYPE>(0);

    if (DIRECTION == DistortionDirection::kUndistort) {
        // Undistort
        const auto in_point_unit = mmdata::Vector2D(in_x, in_y);
        const mmdata::Vector2D in_point_dn = unit_to_diagonal_normalized(
            camera_parameters, film_back_radius_cm, in_point_unit);

        const mmdata::Vector2D undistorted_point_dn = lens.eval(in_point_dn);

        const mmdata::Vector2D undistorted_point_unit =
            diagonal_normalized_to_unit(camera_parameters, film_back_radius_cm,
                                        undistorted_point_dn);

        out_x = static_cast<OUT_TYPE>(undistorted_point_unit.x_);
        out_y = static_cast<OUT_TYPE>(undistorted_point_unit.y_);
    } else {
        // Distort
        //
        // This operation requires iteration to calculate the correct
        // 2D coordinate, which is a lot slower than the undistortion
        // operation.

        // TODO: Look up an initial value from a thread-safe
        // structure that holds a grid of values at vertices which
        // we can interpolate as an initial guess.
        const auto use_guess = false;
        auto guess_point_x = in_x;
        auto guess_point_y = in_y;
        const auto guess_point_unit =
            mmdata::Vector2D(guess_point_x, guess_point_y);
        const mmdata::Vector2D guess_point_dn = unit_to_diagonal_normalized(
            camera_parameters, film_back_radius_cm, guess_point_unit);

        const auto in_point_unit = mmdata::Vector2D(in_x, in_y);
        const mmdata::Vector2D in_point_dn = unit_to_diagonal_normalized(
            camera_parameters, film_back_radius_cm, in_point_unit);

        mmdata::Vector2D distorted_point_dn;
        if (use_guess) {
            // A guess can be used to reduce the number of
            // iterations required to get a good result,
            // increasing performance.
            distorted_point_dn = lens.map_inverse(in_point_dn, guess_point_dn);
        } else {
            distorted_point_dn = lens.map_inverse(in_point_dn);
        }

        const mmdata::Vector2D distorted_point_unit =
            diagonal_normalized_to_unit(camera_parameters, film_back_radius_cm,
                                        distorted_point_dn);

        out_x = static_cast<OUT_TYPE>(distorted_point_unit.x_);
        out_y = static_cast<OUT_TYPE>(distorted_point_unit.y_);
    }

    return std::make_pair(out_x, out_y);
}

// Apply lens distortion to a buffer of data.
//
// This is assumed to be called by multiple threads at once.
template <DistortionDirection DIRECTION, size_t IN_DATA_STRIDE,
          size_t OUT_DATA_STRIDE, class IN_TYPE, class OUT_TYPE,
          class LENS_TYPE>
void apply_lens_distortion_to_buffer(
    const IN_TYPE* in_data, const size_t in_data_size, OUT_TYPE* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, LENS_TYPE lens) {
    const size_t input_data_num_total = in_data_size / IN_DATA_STRIDE;
    for (size_t i = 0; i < input_data_num_total; i++) {
        size_t in_index = i * IN_DATA_STRIDE;

        // The lens distortion operation expects values 0.0 to 1.0,
        // but our inputs are -0.5 to 0.5, therefore we must convert.
        const auto in_x = static_cast<double>(in_data[in_index + 0]) + 0.5;
        const auto in_y = static_cast<double>(in_data[in_index + 1]) + 0.5;

        // TODO: See if we can improve performance by calculating 2, 4 or
        // 8 points at once? Try to use SIMD.
        auto out_xy =
            apply_lens_distortion_once<DIRECTION, IN_TYPE, OUT_TYPE, LENS_TYPE>(
                in_x, in_y, camera_parameters, film_back_radius_cm, lens);

        // Convert back to -0.5 to 0.5 coordinate space.
        auto out_x = out_xy.first - 0.5;
        auto out_y = out_xy.second - 0.5;

        size_t out_index = i * OUT_DATA_STRIDE;
        out_data[out_index + 0] = static_cast<OUT_TYPE>(out_x);
        out_data[out_index + 1] = static_cast<OUT_TYPE>(out_y);
    }
    return;
}

}  // namespace mmlens
