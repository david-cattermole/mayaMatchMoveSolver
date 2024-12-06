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
#include <mmlens/lib.h>

#include <iostream>
#include <type_traits>

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
            distorted_point_dn = lens.eval_inv(in_point_dn, guess_point_dn);
        } else {
            distorted_point_dn = lens.eval_inv(in_point_dn);
        }

        const mmdata::Vector2D distorted_point_unit =
            diagonal_normalized_to_unit(camera_parameters, film_back_radius_cm,
                                        distorted_point_dn);

        out_x = static_cast<OUT_TYPE>(distorted_point_unit.x_);
        out_y = static_cast<OUT_TYPE>(distorted_point_unit.y_);
    }

    return std::make_pair(out_x, out_y);
}

// Apply lens distortion to a pixel.
template <DistortionDirection DIRECTION, size_t OUT_DATA_STRIDE, class IN_TYPE,
          class OUT_TYPE, class LENS_TYPE>
void apply_lens_distortion_to_pixel(const IN_TYPE in_x, const IN_TYPE in_y,
                                    OUT_TYPE* out_pixel,
                                    const CameraParameters camera_parameters,
                                    const double film_back_radius_cm,
                                    LENS_TYPE lens) {
    // TODO: See if we can improve performance by calculating 2, 4 or
    // 8 points at once? Try to use SIMD.
    if (DIRECTION == DistortionDirection::kUndistort ||
        DIRECTION == DistortionDirection::kRedistort) {
        const auto out_xy =
            apply_lens_distortion_once<DIRECTION, IN_TYPE, OUT_TYPE, LENS_TYPE>(
                in_x, in_y, camera_parameters, film_back_radius_cm, lens);

        // Convert back to -0.5 to 0.5 coordinate space.
        OUT_TYPE out_x = static_cast<OUT_TYPE>(out_xy.first - 0.5);
        OUT_TYPE out_y = static_cast<OUT_TYPE>(out_xy.second - 0.5);
        if (std::is_same<OUT_TYPE, float>::value) {
            // Converting to -0.5 to 0.5 coordinate space is not
            // important if we are writing to a 'float' data type,
            // since we can assume that f32 data will be the output
            // and will not be processed further.
            out_x = static_cast<OUT_TYPE>(out_xy.first);
            out_y = static_cast<OUT_TYPE>(out_xy.second);
        }

        out_pixel[0] = out_x;
        out_pixel[1] = out_y;
    } else {
        // It is a logical error if trying to calculate both
        // undistortion and redistortion and trying to output to less
        // than 4 values.
        assert(OUT_DATA_STRIDE >= 4);

        // Calculate both directions, and pack into the output data.
        const auto out_undistort_xy =
            apply_lens_distortion_once<DistortionDirection::kUndistort, IN_TYPE,
                                       OUT_TYPE, LENS_TYPE>(
                in_x, in_y, camera_parameters, film_back_radius_cm, lens);
        const auto out_redistort_xy =
            apply_lens_distortion_once<DistortionDirection::kRedistort, IN_TYPE,
                                       OUT_TYPE, LENS_TYPE>(
                in_x, in_y, camera_parameters, film_back_radius_cm, lens);

        // Convert back to -0.5 to 0.5 coordinate space.
        auto out_undistort_x =
            static_cast<OUT_TYPE>(out_undistort_xy.first - 0.5);
        auto out_undistort_y =
            static_cast<OUT_TYPE>(out_undistort_xy.second - 0.5);
        auto out_redistort_x =
            static_cast<OUT_TYPE>(out_redistort_xy.first - 0.5);
        auto out_redistort_y =
            static_cast<OUT_TYPE>(out_redistort_xy.second - 0.5);
        if (std::is_same<OUT_TYPE, float>::value) {
            // Converting to -0.5 to 0.5 coordinate space is not
            // important if we are writing to a 'float' data type,
            // since we can assume that f32 data will be the output
            // and will not be processed further.
            out_undistort_x = static_cast<OUT_TYPE>(out_undistort_xy.first);
            out_undistort_y = static_cast<OUT_TYPE>(out_undistort_xy.second);
            out_redistort_x = static_cast<OUT_TYPE>(out_redistort_xy.first);
            out_redistort_y = static_cast<OUT_TYPE>(out_redistort_xy.second);
        }

        if (DIRECTION == DistortionDirection::kUndistortAndRedistort) {
            out_pixel[0] = out_undistort_x;
            out_pixel[1] = out_undistort_y;
            out_pixel[2] = out_redistort_x;
            out_pixel[3] = out_redistort_y;
        } else if (DIRECTION == DistortionDirection::kRedistortAndUndistort) {
            out_pixel[0] = out_redistort_x;
            out_pixel[1] = out_redistort_y;
            out_pixel[2] = out_undistort_x;
            out_pixel[3] = out_undistort_y;
        }
    }
    return;
}

// Apply lens distortion to 'identity' coordinate data.
template <DistortionDirection DIRECTION, size_t OUT_DATA_STRIDE, class OUT_TYPE,
          class LENS_TYPE>
void apply_lens_distortion_from_identity(
    const size_t image_width, const size_t image_height,
    const size_t start_image_width, const size_t start_image_height,
    const size_t end_image_width, const size_t end_image_height,
    OUT_TYPE* out_data_ptr, const size_t out_data_size,
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    LENS_TYPE lens) {
    for (auto row = start_image_height; row < end_image_height; row++) {
        for (auto column = start_image_width; column < end_image_width;
             column++) {
            const size_t row_offset = row - start_image_height;
            const size_t column_offset = column - start_image_width;
            const size_t index = (row_offset * image_width) + column_offset;

            // TODO: This assumes that the x/y coordinate matches up
            // with the display window coordinate. In reality the
            // image_width/height may have a larger size and position
            // offset compared to the display window. This must be
            // taken into account for accurate re-creation of ST-Maps,
            // as generated by Natron (our reference).
            //
            // TODO: The Y coordinates must be flipped compared to the
            // Natron lens distortion node output. (0.0, 0.0) origin
            // is bottom screen-left, and (1.0, 1.0) is the upper
            // screen-right.
            const double in_x = static_cast<double>(column) /
                                static_cast<double>(image_width - 1);
            const double in_y = (static_cast<double>(row) /
                                 static_cast<double>(image_height - 1) * -1.0) +
                                1.0;

            const size_t out_index = index * OUT_DATA_STRIDE;
            OUT_TYPE* out_pixel = out_data_ptr + out_index;

            apply_lens_distortion_to_pixel<DIRECTION, OUT_DATA_STRIDE, double,
                                           OUT_TYPE, LENS_TYPE>(
                in_x, in_y, out_pixel, camera_parameters, film_back_radius_cm,
                lens);
        }
    }
    return;
}

template <DistortionDirection DIRECTION, class OUT_TYPE, class LENS_TYPE>
void apply_lens_distortion_from_identity_with_stride(
    const size_t image_width, const size_t image_height,
    const size_t start_image_width, const size_t start_image_height,
    const size_t end_image_width, const size_t end_image_height,
    OUT_TYPE* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride, const CameraParameters camera_parameters,
    const double film_back_radius_cm, LENS_TYPE lens) {
    if (out_data_stride == 2) {
        // The output buffer is expected to have 2D coordinates only.
        const size_t output_buffer_data_stride = 2;

        apply_lens_distortion_from_identity<
            DIRECTION, output_buffer_data_stride, OUT_TYPE, LENS_TYPE>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            camera_parameters, film_back_radius_cm, lens);

    } else if (out_data_stride == 4) {
        // The output buffer is expected to have 4 values; RGBA.
        const size_t output_buffer_data_stride = 4;

        apply_lens_distortion_from_identity<
            DIRECTION, output_buffer_data_stride, OUT_TYPE, LENS_TYPE>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            camera_parameters, film_back_radius_cm, lens);
    } else {
        std::cerr << "apply_lens_distortion_from_identity_with_stride: "
                  << "Invalid out data stride value: " << out_data_stride
                  << std::endl;
    }
    return;
}

// Apply lens distortion to a buffer of data.
//
// The in_data_ptr and out_data_ptr may be the same or different pointers.
//
// It is possible to use in_data_ptr as 2 x f64 and out_data_ptr as 4 x
// f32. This may seem strange but is legal and is memory efficient.
//
// Reusing the same memory is more efficient as we reduce the amount
// of memory used and also increase the CPU cache use per-pixel being
// processed.
template <DistortionDirection DIRECTION, size_t IN_DATA_STRIDE,
          size_t OUT_DATA_STRIDE, class IN_TYPE, class OUT_TYPE,
          class LENS_TYPE>
void apply_lens_distortion_to_buffer(
    // Data chunk sub-window
    const size_t pixel_num_start, const size_t pixel_num_end,

    // Input data buffer
    const IN_TYPE* in_data_ptr, const size_t in_data_size,

    // Output data buffer
    OUT_TYPE* out_data_ptr, const size_t out_data_size,

    // Camera and lens parameters.
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    LENS_TYPE lens) {
    for (size_t i = pixel_num_start; i < pixel_num_end; i++) {
        const size_t in_index = i * IN_DATA_STRIDE;
        assert(in_index < in_data_size);
        const IN_TYPE* in_pixel = in_data_ptr + in_index;

        // The lens distortion operation expects values 0.0 to 1.0,
        // but our inputs are -0.5 to 0.5, therefore we must convert.
        const auto in_x = static_cast<double>(in_pixel[0]) + 0.5;
        const auto in_y = static_cast<double>(in_pixel[1]) + 0.5;

        // The '{}' scope is used to ensure that the in_x/in_y values
        // are read first before we write to the out_data_ptr, because
        // in theory both in_data_ptr and out_data_ptr may point to
        // the same memory, but we are interpreting the memory as
        // different types.
        {
            const size_t out_index = i * OUT_DATA_STRIDE;
            assert(out_index < out_data_size);
            OUT_TYPE* out_pixel = out_data_ptr + out_index;

            apply_lens_distortion_to_pixel<DIRECTION, OUT_DATA_STRIDE, double,
                                           OUT_TYPE, LENS_TYPE>(
                in_x, in_y, out_pixel, camera_parameters, film_back_radius_cm,
                lens);
        }
    }
    return;
}

template <DistortionDirection DIRECTION, class IN_TYPE, class OUT_TYPE,
          class LENS_TYPE>
void apply_lens_distortion_from_buffer_with_stride(
    // Data chunk sub-window
    const size_t data_chunk_start, const size_t data_chunk_end,

    // Input data buffer
    const IN_TYPE* in_data_ptr, const size_t in_data_size,
    const size_t in_data_stride,

    // Output data buffer
    OUT_TYPE* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride,

    // Camera and Lens parameters
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    LENS_TYPE lens) {
    if ((in_data_stride == 2) && (out_data_stride == 2)) {
        // The input buffer will be 2D.
        const size_t input_buffer_data_stride = 2;

        // The output buffer is expected to have 2D coordinates only.
        const size_t output_buffer_data_stride = 2;

        apply_lens_distortion_to_buffer<DIRECTION, input_buffer_data_stride,
                                        output_buffer_data_stride, IN_TYPE,
                                        OUT_TYPE, LENS_TYPE>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            out_data_ptr, out_data_size, camera_parameters, film_back_radius_cm,
            lens);
    } else if ((in_data_stride == 2) && (out_data_stride == 4)) {
        // The input buffer will be 2D.
        const size_t input_buffer_data_stride = 2;

        // The output buffer is expected to have 4 values; RGBA.
        const size_t output_buffer_data_stride = 4;

        apply_lens_distortion_to_buffer<DIRECTION, input_buffer_data_stride,
                                        output_buffer_data_stride, IN_TYPE,
                                        OUT_TYPE, LENS_TYPE>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            out_data_ptr, out_data_size, camera_parameters, film_back_radius_cm,
            lens);
    } else {
        std::cerr << "apply_lens_distortion_from_buffer_with_stride: "
                  << "Invalid in or out data stride value: "
                  << "in_data_stride=" << in_data_stride
                  << " out_data_stride=" << out_data_stride << std::endl;
    }

    return;
}

}  // namespace mmlens
