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

//////////////////////////////////////////////////////////////////////
// 3DE Classic

inline Distortion3deClassic create_distortion_tde_classic(
    Parameters3deClassic lens_parameters) {
    auto distortion = Distortion3deClassic();
    distortion.set_parameter(0, lens_parameters.distortion);
    distortion.set_parameter(1, lens_parameters.anamorphic_squeeze);
    distortion.set_parameter(2, lens_parameters.curvature_x);
    distortion.set_parameter(3, lens_parameters.curvature_y);
    distortion.set_parameter(4, lens_parameters.quartic_distortion);
    return distortion;
}

void apply_undistort_3de_classic_identity_to_f64_2d(
    const size_t image_width, const size_t image_height, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, Parameters3deClassic lens_parameters) {
    // The output buffer is expected to have 2D coordinates only.
    const size_t data_stride = 2;

    auto distortion = create_distortion_tde_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_from_identity<direction, data_stride, double,
                                        Distortion3deClassic>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_classic_identity_to_f64_2d(
    const size_t image_width, const size_t image_height, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, Parameters3deClassic lens_parameters) {
    // The output buffer is expected to have 2D coordinates only.
    const size_t data_stride = 2;

    auto distortion = create_distortion_tde_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, double,
                                        Distortion3deClassic>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_classic_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, Parameters3deClassic lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion = create_distortion_tde_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deClassic>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_classic_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, Parameters3deClassic lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion = create_distortion_tde_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deClassic>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_and_redistort_3de_classic_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, Parameters3deClassic lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion = create_distortion_tde_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistortAndRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deClassic>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_classic_f64_2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, Parameters3deClassic lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    auto distortion = create_distortion_tde_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double, Distortion3deClassic>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_classic_f64_2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, Parameters3deClassic lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    auto distortion = create_distortion_tde_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double, Distortion3deClassic>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_classic_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, Parameters3deClassic lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    auto distortion = create_distortion_tde_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float, Distortion3deClassic>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_classic_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm, Parameters3deClassic lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    auto distortion = create_distortion_tde_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float, Distortion3deClassic>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

//////////////////////////////////////////////////////////////////////
// 3DE Radial Decentered Degree 4 Cylindric

inline Distortion3deRadialStdDeg4 create_distortion_3de_radial_std_deg4(
    Parameters3deRadialStdDeg4 lens_parameters) {
    auto distortion = Distortion3deRadialStdDeg4();
    distortion.set_parameter(0, lens_parameters.degree2_distortion);
    distortion.set_parameter(1, lens_parameters.degree2_u);
    distortion.set_parameter(2, lens_parameters.degree2_v);
    distortion.set_parameter(3, lens_parameters.degree4_distortion);
    distortion.set_parameter(4, lens_parameters.degree4_u);
    distortion.set_parameter(5, lens_parameters.degree4_v);
    distortion.set_parameter(6, lens_parameters.cylindric_direction);
    distortion.set_parameter(7, lens_parameters.cylindric_bending);
    return distortion;
}

void apply_undistort_3de_radial_std_deg4_identity_to_f64_2d(
    const size_t image_width, const size_t image_height, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deRadialStdDeg4 lens_parameters) {
    // The output buffer is expected to have 2D coordinates only.
    const size_t data_stride = 2;

    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_from_identity<direction, data_stride, double,
                                        Distortion3deRadialStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_radial_std_deg4_identity_to_f64_2d(
    const size_t image_width, const size_t image_height, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deRadialStdDeg4 lens_parameters) {
    // The output buffer is expected to have 2D coordinates only.
    const size_t data_stride = 2;

    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, double,
                                        Distortion3deRadialStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_radial_std_deg4_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deRadialStdDeg4 lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deRadialStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_radial_std_deg4_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deRadialStdDeg4 lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deRadialStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_and_redistort_3de_radial_std_deg4_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deRadialStdDeg4 lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistortAndRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deRadialStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_radial_std_deg4_f64_2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deRadialStdDeg4 lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double, Distortion3deRadialStdDeg4>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_radial_std_deg4_f64_2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deRadialStdDeg4 lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double, Distortion3deRadialStdDeg4>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_radial_std_deg4_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deRadialStdDeg4 lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float, Distortion3deRadialStdDeg4>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_radial_std_deg4_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deRadialStdDeg4 lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float, Distortion3deRadialStdDeg4>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 4 Rotate Squeeze XY

inline Distortion3deAnamorphicStdDeg4 create_distortion_3de_anamorphic_std_deg4(
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    auto distortion = Distortion3deAnamorphicStdDeg4();
    distortion.set_parameter(0, lens_parameters.degree2_cx02);
    distortion.set_parameter(1, lens_parameters.degree2_cy02);
    distortion.set_parameter(2, lens_parameters.degree2_cx22);
    distortion.set_parameter(3, lens_parameters.degree2_cy22);
    distortion.set_parameter(4, lens_parameters.degree4_cx04);
    distortion.set_parameter(5, lens_parameters.degree4_cy04);
    distortion.set_parameter(6, lens_parameters.degree4_cx24);
    distortion.set_parameter(7, lens_parameters.degree4_cy24);
    distortion.set_parameter(8, lens_parameters.degree4_cx44);
    distortion.set_parameter(9, lens_parameters.degree4_cy44);
    distortion.set_parameter(10, lens_parameters.lens_rotation);
    distortion.set_parameter(11, lens_parameters.squeeze_x);
    distortion.set_parameter(12, lens_parameters.squeeze_y);
    return distortion;
}

void apply_undistort_3de_anamorphic_std_deg4_identity_to_f64_2d(
    const size_t image_width, const size_t image_height, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    // The output buffer is expected to have 2D coordinates only.
    const size_t data_stride = 2;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_from_identity<direction, data_stride, double,
                                        Distortion3deAnamorphicStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_anamorphic_std_deg4_identity_to_f64_2d(
    const size_t image_width, const size_t image_height, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    // The output buffer is expected to have 2D coordinates only.
    const size_t data_stride = 2;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, double,
                                        Distortion3deAnamorphicStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_anamorphic_std_deg4_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deAnamorphicStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_anamorphic_std_deg4_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deAnamorphicStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_and_redistort_3de_anamorphic_std_deg4_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistortAndRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deAnamorphicStdDeg4>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_anamorphic_std_deg4_f64_2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double, Distortion3deAnamorphicStdDeg4>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_anamorphic_std_deg4_f64_2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double, Distortion3deAnamorphicStdDeg4>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_anamorphic_std_deg4_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float,
                                    Distortion3deAnamorphicStdDeg4>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_anamorphic_std_deg4_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4 lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float,
                                    Distortion3deAnamorphicStdDeg4>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 4 Rotate Squeeze XY Rescaled

inline Distortion3deAnamorphicStdDeg4Rescaled
create_distortion_3de_anamorphic_std_deg4_rescaled(
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    auto distortion = Distortion3deAnamorphicStdDeg4Rescaled();
    distortion.set_parameter(0, lens_parameters.degree2_cx02);
    distortion.set_parameter(1, lens_parameters.degree2_cy02);
    distortion.set_parameter(2, lens_parameters.degree2_cx22);
    distortion.set_parameter(3, lens_parameters.degree2_cy22);
    distortion.set_parameter(4, lens_parameters.degree4_cx04);
    distortion.set_parameter(5, lens_parameters.degree4_cy04);
    distortion.set_parameter(6, lens_parameters.degree4_cx24);
    distortion.set_parameter(7, lens_parameters.degree4_cy24);
    distortion.set_parameter(8, lens_parameters.degree4_cx44);
    distortion.set_parameter(9, lens_parameters.degree4_cy44);
    distortion.set_parameter(10, lens_parameters.lens_rotation);
    distortion.set_parameter(11, lens_parameters.squeeze_x);
    distortion.set_parameter(12, lens_parameters.squeeze_y);
    distortion.set_parameter(13, lens_parameters.rescale);
    return distortion;
}

void apply_undistort_3de_anamorphic_std_deg4_rescaled_identity_to_f64_2d(
    const size_t image_width, const size_t image_height, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    // The output buffer is expected to have 2D coordinates only.
    const size_t data_stride = 2;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_from_identity<direction, data_stride, double,
                                        Distortion3deAnamorphicStdDeg4Rescaled>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_anamorphic_std_deg4_rescaled_identity_to_f64_2d(
    const size_t image_width, const size_t image_height, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    // The output buffer is expected to have 2D coordinates only.
    const size_t data_stride = 2;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, double,
                                        Distortion3deAnamorphicStdDeg4Rescaled>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_anamorphic_std_deg4_rescaled_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deAnamorphicStdDeg4Rescaled>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_anamorphic_std_deg4_rescaled_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deAnamorphicStdDeg4Rescaled>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_and_redistort_3de_anamorphic_std_deg4_rescaled_identity_to_f32_4d(
    const size_t image_width, const size_t image_height, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    // The output buffer is expected to have 4 values; RGBA.
    const size_t data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistortAndRedistort;
    apply_lens_distortion_from_identity<direction, data_stride, float,
                                        Distortion3deAnamorphicStdDeg4Rescaled>(
        image_width, image_height, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_anamorphic_std_deg4_rescaled_f64_2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double,
                                    Distortion3deAnamorphicStdDeg4Rescaled>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_anamorphic_std_deg4_rescaled_f64_2d_to_f64_2d(
    const double* in_data, const size_t in_data_size, double* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    // Input and output buffers are both expected to have 2D
    // coordinates only.
    const size_t data_stride = 2;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_to_buffer<direction, data_stride, data_stride, double,
                                    double,
                                    Distortion3deAnamorphicStdDeg4Rescaled>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_undistort_3de_anamorphic_std_deg4_rescaled_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kUndistort;
    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float,
                                    Distortion3deAnamorphicStdDeg4Rescaled>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

void apply_redistort_3de_anamorphic_std_deg4_rescaled_f64_2d_to_f32_4d(
    const double* in_data, const size_t in_data_size, float* out_data,
    const size_t out_data_size, const CameraParameters camera_parameters,
    const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    // Input Buffer is expected to have 2D coordinates only.
    const size_t in_data_stride = 2;

    // RGBA has 4 channels.
    const size_t out_data_stride = 4;

    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    const auto direction = DistortionDirection::kRedistort;
    apply_lens_distortion_to_buffer<direction, in_data_stride, out_data_stride,
                                    double, float,
                                    Distortion3deAnamorphicStdDeg4Rescaled>(
        in_data, in_data_size, out_data, out_data_size, camera_parameters,
        film_back_radius_cm, distortion);
    return;
}

}  // namespace mmlens
