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

#include "distortion_operations.h"
#include "distortion_structs.h"

namespace mmlens {

// Generic creation of lens parameters.
template <typename DistortionType, typename ParameterType>
inline DistortionType create_distortion(const ParameterType& lens_parameters);

// Applying lens distortion to identity, abstracting the lens
// distortion model away.
template <typename OutType, typename DistortionType, typename ParameterType>
void apply_identity_impl(const DistortionDirection direction,
                         const ImageDimensions image_dimensions,

                         // Output buffer
                         OutType* out_data_ptr, const size_t out_data_size,
                         const size_t out_data_stride,

                         // Parameters
                         const CameraParameters camera_parameters,
                         const double film_back_radius_cm,
                         const ParameterType& lens_parameters) {
    auto distortion = create_distortion<DistortionType>(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, OutType, DistortionType>(
            image_dimensions.width, image_dimensions.height,
            image_dimensions.start_width, image_dimensions.start_height,
            image_dimensions.end_width, image_dimensions.end_height,
            out_data_ptr, out_data_size, out_data_stride, camera_parameters,
            film_back_radius_cm, distortion);
    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, OutType, DistortionType>(
            image_dimensions.width, image_dimensions.height,
            image_dimensions.start_width, image_dimensions.start_height,
            image_dimensions.end_width, image_dimensions.end_height,
            out_data_ptr, out_data_size, out_data_stride, camera_parameters,
            film_back_radius_cm, distortion);
    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, OutType,
            DistortionType>(
            image_dimensions.width, image_dimensions.height,
            image_dimensions.start_width, image_dimensions.start_height,
            image_dimensions.end_width, image_dimensions.end_height,
            out_data_ptr, out_data_size, out_data_stride, camera_parameters,
            film_back_radius_cm, distortion);
    }
}

// Applying lens distortion to an existing buffer, abstracting the
// lens distortion model away.
template <typename InType, typename OutType, typename DistortionType,
          typename ParameterType>
void apply_buffer_impl(const DistortionDirection direction,

                       // Data chunk sub-window
                       const size_t data_chunk_start,
                       const size_t data_chunk_end,

                       // Input data buffer
                       const InType* in_data_ptr, const size_t in_data_size,
                       const size_t in_data_stride,

                       // Output data buffer
                       OutType* out_data_ptr, const size_t out_data_size,
                       const size_t out_data_stride,

                       // Camera and lens parameters
                       const CameraParameters camera_parameters,
                       const double film_back_radius_cm,
                       const ParameterType& lens_parameters) {
    auto distortion = create_distortion<DistortionType>(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, InType, OutType, DistortionType>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, InType, OutType, DistortionType>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, InType, OutType,
            DistortionType>(data_chunk_start, data_chunk_end, in_data_ptr,
                            in_data_size, in_data_stride, out_data_ptr,
                            out_data_size, out_data_stride, camera_parameters,
                            film_back_radius_cm, distortion);
    }
}

//////////////////////////////////////////////////////////////////////
// 3DE Classic

template <>
inline Distortion3deClassic
create_distortion<Distortion3deClassic, Parameters3deClassic>(
    const Parameters3deClassic& lens_parameters) {
    auto distortion = Distortion3deClassic();
    distortion.set_parameter(0, lens_parameters.distortion);
    distortion.set_parameter(1, lens_parameters.anamorphic_squeeze);
    distortion.set_parameter(2, lens_parameters.curvature_x);
    distortion.set_parameter(3, lens_parameters.curvature_y);
    distortion.set_parameter(4, lens_parameters.quartic_distortion);
    return distortion;
}

void apply_identity_to_f64(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,

                           // Output buffer
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deClassic lens_parameters) {
    apply_identity_impl<double, Distortion3deClassic, Parameters3deClassic>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_identity_to_f32(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,

                           // Output buffer
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deClassic lens_parameters) {
    apply_identity_impl<float, Distortion3deClassic, Parameters3deClassic>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_f64_to_f64(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deClassic lens_parameters) {
    apply_buffer_impl<double, double, Distortion3deClassic,
                      Parameters3deClassic>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

void apply_f64_to_f32(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deClassic lens_parameters) {
    apply_buffer_impl<double, float, Distortion3deClassic,
                      Parameters3deClassic>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

//////////////////////////////////////////////////////////////////////
// 3DE Radial Decentered Degree 4 Cylindric

template <>
inline Distortion3deRadialStdDeg4
create_distortion<Distortion3deRadialStdDeg4, Parameters3deRadialStdDeg4>(
    const Parameters3deRadialStdDeg4& lens_parameters) {
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

void apply_identity_to_f64(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,

                           // Output buffer
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deRadialStdDeg4 lens_parameters) {
    apply_identity_impl<double, Distortion3deRadialStdDeg4,
                        Parameters3deRadialStdDeg4>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_identity_to_f32(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,

                           // Output buffer
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deRadialStdDeg4 lens_parameters) {
    apply_identity_impl<float, Distortion3deRadialStdDeg4,
                        Parameters3deRadialStdDeg4>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_f64_to_f64(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deRadialStdDeg4 lens_parameters) {
    apply_buffer_impl<double, double, Distortion3deRadialStdDeg4,
                      Parameters3deRadialStdDeg4>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

void apply_f64_to_f32(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deRadialStdDeg4 lens_parameters) {
    apply_buffer_impl<double, float, Distortion3deRadialStdDeg4,
                      Parameters3deRadialStdDeg4>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 4 Rotate Squeeze XY

template <>
inline Distortion3deAnamorphicStdDeg4 create_distortion<
    Distortion3deAnamorphicStdDeg4, Parameters3deAnamorphicStdDeg4>(
    const Parameters3deAnamorphicStdDeg4& lens_parameters) {
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

void apply_identity_to_f64(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,

                           // Output buffer
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg4 lens_parameters) {
    apply_identity_impl<double, Distortion3deAnamorphicStdDeg4,
                        Parameters3deAnamorphicStdDeg4>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_identity_to_f32(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,

                           // Output buffer
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg4 lens_parameters) {
    apply_identity_impl<float, Distortion3deAnamorphicStdDeg4,
                        Parameters3deAnamorphicStdDeg4>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_f64_to_f64(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg4 lens_parameters) {
    apply_buffer_impl<double, double, Distortion3deAnamorphicStdDeg4,
                      Parameters3deAnamorphicStdDeg4>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

void apply_f64_to_f32(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg4 lens_parameters) {
    apply_buffer_impl<double, float, Distortion3deAnamorphicStdDeg4,
                      Parameters3deAnamorphicStdDeg4>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 4 Rotate Squeeze XY Rescaled

template <>
inline Distortion3deAnamorphicStdDeg4Rescaled
create_distortion<Distortion3deAnamorphicStdDeg4Rescaled,
                  Parameters3deAnamorphicStdDeg4Rescaled>(
    const Parameters3deAnamorphicStdDeg4Rescaled& lens_parameters) {
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

void apply_identity_to_f64(
    const DistortionDirection direction,
    const ImageDimensions image_dimensions,

    // Output buffer
    double* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride,

    // Camera and lens parameters
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    apply_identity_impl<double, Distortion3deAnamorphicStdDeg4Rescaled,
                        Parameters3deAnamorphicStdDeg4Rescaled>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_identity_to_f32(
    const DistortionDirection direction,
    const ImageDimensions image_dimensions,

    // Output buffer
    float* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride,

    // Camera and lens parameters
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    apply_identity_impl<float, Distortion3deAnamorphicStdDeg4Rescaled,
                        Parameters3deAnamorphicStdDeg4Rescaled>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_f64_to_f64(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    apply_buffer_impl<double, double, Distortion3deAnamorphicStdDeg4Rescaled,
                      Parameters3deAnamorphicStdDeg4Rescaled>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

void apply_f64_to_f32(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    apply_buffer_impl<double, float, Distortion3deAnamorphicStdDeg4Rescaled,
                      Parameters3deAnamorphicStdDeg4Rescaled>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 6 Rotate Squeeze XY

template <>
inline Distortion3deAnamorphicStdDeg6 create_distortion<
    Distortion3deAnamorphicStdDeg6, Parameters3deAnamorphicStdDeg6>(
    const Parameters3deAnamorphicStdDeg6& lens_parameters) {
    auto distortion = Distortion3deAnamorphicStdDeg6();
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
    distortion.set_parameter(10, lens_parameters.degree6_cx06);
    distortion.set_parameter(11, lens_parameters.degree6_cy06);
    distortion.set_parameter(12, lens_parameters.degree6_cx26);
    distortion.set_parameter(13, lens_parameters.degree6_cy26);
    distortion.set_parameter(14, lens_parameters.degree6_cx46);
    distortion.set_parameter(15, lens_parameters.degree6_cy46);
    distortion.set_parameter(16, lens_parameters.degree6_cx66);
    distortion.set_parameter(17, lens_parameters.degree6_cy66);
    distortion.set_parameter(18, lens_parameters.lens_rotation);
    distortion.set_parameter(19, lens_parameters.squeeze_x);
    distortion.set_parameter(20, lens_parameters.squeeze_y);
    return distortion;
}

void apply_identity_to_f64(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,

                           // Output buffer
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg6 lens_parameters) {
    apply_identity_impl<double, Distortion3deAnamorphicStdDeg6,
                        Parameters3deAnamorphicStdDeg6>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_identity_to_f32(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,

                           // Output buffer
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg6 lens_parameters) {
    apply_identity_impl<float, Distortion3deAnamorphicStdDeg6,
                        Parameters3deAnamorphicStdDeg6>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_f64_to_f64(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg6 lens_parameters) {
    apply_buffer_impl<double, double, Distortion3deAnamorphicStdDeg6,
                      Parameters3deAnamorphicStdDeg6>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

void apply_f64_to_f32(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg6 lens_parameters) {
    apply_buffer_impl<double, float, Distortion3deAnamorphicStdDeg6,
                      Parameters3deAnamorphicStdDeg6>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 6 Rotate Squeeze XY Rescaled

template <>
inline Distortion3deAnamorphicStdDeg6Rescaled
create_distortion<Distortion3deAnamorphicStdDeg6Rescaled,
                  Parameters3deAnamorphicStdDeg6Rescaled>(
    const Parameters3deAnamorphicStdDeg6Rescaled& lens_parameters) {
    auto distortion = Distortion3deAnamorphicStdDeg6Rescaled();
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
    distortion.set_parameter(10, lens_parameters.degree6_cx06);
    distortion.set_parameter(11, lens_parameters.degree6_cy06);
    distortion.set_parameter(12, lens_parameters.degree6_cx26);
    distortion.set_parameter(13, lens_parameters.degree6_cy26);
    distortion.set_parameter(14, lens_parameters.degree6_cx46);
    distortion.set_parameter(15, lens_parameters.degree6_cy46);
    distortion.set_parameter(16, lens_parameters.degree6_cx66);
    distortion.set_parameter(17, lens_parameters.degree6_cy66);
    distortion.set_parameter(18, lens_parameters.lens_rotation);
    distortion.set_parameter(19, lens_parameters.squeeze_x);
    distortion.set_parameter(20, lens_parameters.squeeze_y);
    distortion.set_parameter(21, lens_parameters.rescale);
    return distortion;
}

void apply_identity_to_f64(
    const DistortionDirection direction,
    const ImageDimensions image_dimensions,

    // Output buffer
    double* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride,

    // Camera and lens parameters
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) {
    apply_identity_impl<double, Distortion3deAnamorphicStdDeg6Rescaled,
                        Parameters3deAnamorphicStdDeg6Rescaled>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_identity_to_f32(
    const DistortionDirection direction,
    const ImageDimensions image_dimensions,

    // Output buffer
    float* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride,

    // Camera and lens parameters
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) {
    apply_identity_impl<float, Distortion3deAnamorphicStdDeg6Rescaled,
                        Parameters3deAnamorphicStdDeg6Rescaled>(
        direction, image_dimensions, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);
}

void apply_f64_to_f64(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) {
    apply_buffer_impl<double, double, Distortion3deAnamorphicStdDeg6Rescaled,
                      Parameters3deAnamorphicStdDeg6Rescaled>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

void apply_f64_to_f32(const DistortionDirection direction,

                      // Data chunk sub-window
                      const size_t data_chunk_start,
                      const size_t data_chunk_end,

                      // Input data buffer
                      const double* in_data_ptr, const size_t in_data_size,
                      const size_t in_data_stride,

                      // Output data buffer
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,

                      // Camera and lens parameters
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) {
    apply_buffer_impl<double, float, Distortion3deAnamorphicStdDeg6Rescaled,
                      Parameters3deAnamorphicStdDeg6Rescaled>(
        direction, data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
        in_data_stride, out_data_ptr, out_data_size, out_data_stride,
        camera_parameters, film_back_radius_cm, lens_parameters);
}

}  // namespace mmlens
