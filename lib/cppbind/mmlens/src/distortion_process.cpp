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

//////////////////////////////////////////////////////////////////////
// 3DE Classic

inline Distortion3deClassic create_distortion_3de_classic(
    Parameters3deClassic lens_parameters) {
    auto distortion = Distortion3deClassic();
    distortion.set_parameter(0, lens_parameters.distortion);
    distortion.set_parameter(1, lens_parameters.anamorphic_squeeze);
    distortion.set_parameter(2, lens_parameters.curvature_x);
    distortion.set_parameter(3, lens_parameters.curvature_y);
    distortion.set_parameter(4, lens_parameters.quartic_distortion);
    return distortion;
}

void apply_identity_to_f64(const DistortionDirection direction,

                           // Image size
                           const size_t image_width, const size_t image_height,

                           // Image sub-window
                           const size_t start_image_width,
                           const size_t start_image_height,
                           const size_t end_image_width,
                           const size_t end_image_height,

                           // Output buffer
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deClassic lens_parameters) {
    auto distortion = create_distortion_3de_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, double, Distortion3deClassic>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, double, Distortion3deClassic>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, double,
            Distortion3deClassic>(image_width, image_height, start_image_width,
                                  start_image_height, end_image_width,
                                  end_image_height, out_data_ptr, out_data_size,
                                  out_data_stride, camera_parameters,
                                  film_back_radius_cm, distortion);
    }

    return;
}

void apply_identity_to_f32(const DistortionDirection direction,

                           // Image size
                           const size_t image_width, const size_t image_height,

                           // Image sub-window
                           const size_t start_image_width,
                           const size_t start_image_height,
                           const size_t end_image_width,
                           const size_t end_image_height,

                           // Output buffer
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deClassic lens_parameters) {
    auto distortion = create_distortion_3de_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, float, Distortion3deClassic>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, float, Distortion3deClassic>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, float,
            Distortion3deClassic>(image_width, image_height, start_image_width,
                                  start_image_height, end_image_width,
                                  end_image_height, out_data_ptr, out_data_size,
                                  out_data_stride, camera_parameters,
                                  film_back_radius_cm, distortion);
    }

    return;
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
    auto distortion = create_distortion_3de_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, double,
            Distortion3deClassic>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, double,
            Distortion3deClassic>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, double,
            Distortion3deClassic>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

    return;
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
    auto distortion = create_distortion_3de_classic(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, float,
            Distortion3deClassic>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, float,
            Distortion3deClassic>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, float,
            Distortion3deClassic>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

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

void apply_identity_to_f64(const DistortionDirection direction,

                           // Image size
                           const size_t image_width, const size_t image_height,

                           // Image sub-window
                           const size_t start_image_width,
                           const size_t start_image_height,
                           const size_t end_image_width,
                           const size_t end_image_height,

                           // Output buffer
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deRadialStdDeg4 lens_parameters) {
    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, double,
            Distortion3deRadialStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, double,
            Distortion3deRadialStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, double,
            Distortion3deRadialStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
}

void apply_identity_to_f32(const DistortionDirection direction,

                           // Image size
                           const size_t image_width, const size_t image_height,

                           // Image sub-window
                           const size_t start_image_width,
                           const size_t start_image_height,
                           const size_t end_image_width,
                           const size_t end_image_height,

                           // Output buffer
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deRadialStdDeg4 lens_parameters) {
    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, float, Distortion3deRadialStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, float, Distortion3deRadialStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, float,
            Distortion3deRadialStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
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
    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, double,
            Distortion3deRadialStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, double,
            Distortion3deRadialStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, double,
            Distortion3deRadialStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

    return;
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
    auto distortion = create_distortion_3de_radial_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, float,
            Distortion3deRadialStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, float,
            Distortion3deRadialStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, float,
            Distortion3deRadialStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

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

void apply_identity_to_f64(const DistortionDirection direction,

                           // Image size
                           const size_t image_width, const size_t image_height,

                           // Image sub-window
                           const size_t start_image_width,
                           const size_t start_image_height,
                           const size_t end_image_width,
                           const size_t end_image_height,

                           // Output buffer
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg4 lens_parameters) {
    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, double,
            Distortion3deAnamorphicStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, double,
            Distortion3deAnamorphicStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, double,
            Distortion3deAnamorphicStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
}

void apply_identity_to_f32(const DistortionDirection direction,

                           // Image size
                           const size_t image_width, const size_t image_height,

                           // Image sub-window
                           const size_t start_image_width,
                           const size_t start_image_height,
                           const size_t end_image_width,
                           const size_t end_image_height,

                           // Output buffer
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg4 lens_parameters) {
    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, float,
            Distortion3deAnamorphicStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, float,
            Distortion3deAnamorphicStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, float,
            Distortion3deAnamorphicStdDeg4>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
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
    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, double,
            Distortion3deAnamorphicStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, double,
            Distortion3deAnamorphicStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, double,
            Distortion3deAnamorphicStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

    return;
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
    auto distortion =
        create_distortion_3de_anamorphic_std_deg4(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, float,
            Distortion3deAnamorphicStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, float,
            Distortion3deAnamorphicStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, float,
            Distortion3deAnamorphicStdDeg4>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

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

void apply_identity_to_f64(
    const DistortionDirection direction,

    // Image size
    const size_t image_width, const size_t image_height,

    // Image sub-window
    const size_t start_image_width, const size_t start_image_height,
    const size_t end_image_width, const size_t end_image_height,

    // Output buffer
    double* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride,

    // Camera and lens parameters
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, double,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, double,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, double,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
}

void apply_identity_to_f32(
    const DistortionDirection direction,

    // Image size
    const size_t image_width, const size_t image_height,

    // Image sub-window
    const size_t start_image_width, const size_t start_image_height,
    const size_t end_image_width, const size_t end_image_height,

    // Output buffer
    float* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride,

    // Camera and lens parameters
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters) {
    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, float,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, float,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, float,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
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
    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, double,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, double,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, double,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

    return;
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
    auto distortion =
        create_distortion_3de_anamorphic_std_deg4_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, float,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, float,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, float,
            Distortion3deAnamorphicStdDeg4Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

    return;
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 6 Rotate Squeeze XY

inline Distortion3deAnamorphicStdDeg6 create_distortion_3de_anamorphic_std_deg6(
    Parameters3deAnamorphicStdDeg6 lens_parameters) {
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

                           // Image size
                           const size_t image_width, const size_t image_height,

                           // Image sub-window
                           const size_t start_image_width,
                           const size_t start_image_height,
                           const size_t end_image_width,
                           const size_t end_image_height,

                           // Output buffer
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg6 lens_parameters) {
    auto distortion =
        create_distortion_3de_anamorphic_std_deg6(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, double,
            Distortion3deAnamorphicStdDeg6>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, double,
            Distortion3deAnamorphicStdDeg6>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, double,
            Distortion3deAnamorphicStdDeg6>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
}

void apply_identity_to_f32(const DistortionDirection direction,

                           // Image size
                           const size_t image_width, const size_t image_height,

                           // Image sub-window
                           const size_t start_image_width,
                           const size_t start_image_height,
                           const size_t end_image_width,
                           const size_t end_image_height,

                           // Output buffer
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,

                           // Camera and lens parameters
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg6 lens_parameters) {
    auto distortion =
        create_distortion_3de_anamorphic_std_deg6(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, float,
            Distortion3deAnamorphicStdDeg6>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, float,
            Distortion3deAnamorphicStdDeg6>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, float,
            Distortion3deAnamorphicStdDeg6>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
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
    auto distortion =
        create_distortion_3de_anamorphic_std_deg6(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, double,
            Distortion3deAnamorphicStdDeg6>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, double,
            Distortion3deAnamorphicStdDeg6>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, double,
            Distortion3deAnamorphicStdDeg6>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

    return;
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
    auto distortion =
        create_distortion_3de_anamorphic_std_deg6(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, float,
            Distortion3deAnamorphicStdDeg6>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, float,
            Distortion3deAnamorphicStdDeg6>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, float,
            Distortion3deAnamorphicStdDeg6>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

    return;
}

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 6 Rotate Squeeze XY Rescaled

inline Distortion3deAnamorphicStdDeg6Rescaled
create_distortion_3de_anamorphic_std_deg6_rescaled(
    Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) {
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

    // Image size
    const size_t image_width, const size_t image_height,

    // Image sub-window
    const size_t start_image_width, const size_t start_image_height,
    const size_t end_image_width, const size_t end_image_height,

    // Output buffer
    double* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride,

    // Camera and lens parameters
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) {
    auto distortion =
        create_distortion_3de_anamorphic_std_deg6_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, double,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, double,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, double,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
}

void apply_identity_to_f32(
    const DistortionDirection direction,

    // Image size
    const size_t image_width, const size_t image_height,

    // Image sub-window
    const size_t start_image_width, const size_t start_image_height,
    const size_t end_image_width, const size_t end_image_height,

    // Output buffer
    float* out_data_ptr, const size_t out_data_size,
    const size_t out_data_stride,

    // Camera and lens parameters
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg6Rescaled lens_parameters) {
    auto distortion =
        create_distortion_3de_anamorphic_std_deg6_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistort, float,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kRedistort, float,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_identity_with_stride<
            DistortionDirection::kUndistortAndRedistort, float,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            image_width, image_height, start_image_width, start_image_height,
            end_image_width, end_image_height, out_data_ptr, out_data_size,
            out_data_stride, camera_parameters, film_back_radius_cm,
            distortion);
    }

    return;
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
    auto distortion =
        create_distortion_3de_anamorphic_std_deg6_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, double,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, double,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, double,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

    return;
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
    auto distortion =
        create_distortion_3de_anamorphic_std_deg6_rescaled(lens_parameters);
    distortion.initialize_parameters(camera_parameters);

    if (direction == DistortionDirection::kUndistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistort, double, float,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kRedistort, double, float,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);

    } else if (direction == DistortionDirection::kUndistortAndRedistort) {
        apply_lens_distortion_from_buffer_with_stride<
            DistortionDirection::kUndistortAndRedistort, double, float,
            Distortion3deAnamorphicStdDeg6Rescaled>(
            data_chunk_start, data_chunk_end, in_data_ptr, in_data_size,
            in_data_stride, out_data_ptr, out_data_size, out_data_stride,
            camera_parameters, film_back_radius_cm, distortion);
    }

    return;
}

}  // namespace mmlens
