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

#ifndef MM_LENS_DISTORTION_PROCESS_H
#define MM_LENS_DISTORTION_PROCESS_H

#include <mmcore/mmdata.h>

#include <cmath>
#include <memory>
#include <string>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"

namespace mmlens {

struct ImageDimensions;
struct CameraParameters;
struct Parameters3deClassic;
struct Parameters3deRadialStdDeg4;
struct Parameters3deAnamorphicStdDeg4;
struct Parameters3deAnamorphicStdDeg4Rescaled;
struct Parameters3deAnamorphicStdDeg6;
struct Parameters3deAnamorphicStdDeg6Rescaled;
enum class DistortionDirection : uint8_t;

//////////////////////////////////////////////////////////////////////
// 3DE Classic

MMLENS_API_EXPORT
void apply_identity_to_f64(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deClassic lens_parameters);

MMLENS_API_EXPORT
void apply_identity_to_f32(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deClassic lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f64(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deClassic lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f32(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deClassic lens_parameters);

//////////////////////////////////////////////////////////////////////
// 3DE Radial Decentered Degree 4 Cylindric

MMLENS_API_EXPORT
void apply_identity_to_f64(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deRadialStdDeg4 lens_parameters);

MMLENS_API_EXPORT
void apply_identity_to_f32(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deRadialStdDeg4 lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f64(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deRadialStdDeg4 lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f32(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deRadialStdDeg4 lens_parameters);

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 4 Rotate Squeeze XY

MMLENS_API_EXPORT
void apply_identity_to_f64(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg4 lens_parameters);

MMLENS_API_EXPORT
void apply_identity_to_f32(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg4 lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f64(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg4 lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f32(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg4 lens_parameters);

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 4 Rotate Squeeze XY Rescaled

MMLENS_API_EXPORT
void apply_identity_to_f64(
    const DistortionDirection direction,
    const ImageDimensions image_dimensions, double* out_data_ptr,
    const size_t out_data_size, const size_t out_data_stride,
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters);

MMLENS_API_EXPORT
void apply_identity_to_f32(
    const DistortionDirection direction,
    const ImageDimensions image_dimensions, float* out_data_ptr,
    const size_t out_data_size, const size_t out_data_stride,
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg4Rescaled lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f64(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg4Rescaled lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f32(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg4Rescaled lens_parameters);

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 6 Rotate Squeeze XY

MMLENS_API_EXPORT
void apply_identity_to_f64(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,
                           double* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg6 lens_parameters);

MMLENS_API_EXPORT
void apply_identity_to_f32(const DistortionDirection direction,
                           const ImageDimensions image_dimensions,
                           float* out_data_ptr, const size_t out_data_size,
                           const size_t out_data_stride,
                           const CameraParameters camera_parameters,
                           const double film_back_radius_cm,
                           Parameters3deAnamorphicStdDeg6 lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f64(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg6 lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f32(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg6 lens_parameters);

//////////////////////////////////////////////////////////////////////
// 3DE Anamorphic Degree 6 Rotate Squeeze XY Rescaled

MMLENS_API_EXPORT
void apply_identity_to_f64(
    const DistortionDirection direction,
    const ImageDimensions image_dimensions, double* out_data_ptr,
    const size_t out_data_size, const size_t out_data_stride,
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg6Rescaled lens_parameters);

MMLENS_API_EXPORT
void apply_identity_to_f32(
    const DistortionDirection direction,
    const ImageDimensions image_dimensions, float* out_data_ptr,
    const size_t out_data_size, const size_t out_data_stride,
    const CameraParameters camera_parameters, const double film_back_radius_cm,
    Parameters3deAnamorphicStdDeg6Rescaled lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f64(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      double* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg6Rescaled lens_parameters);

MMLENS_API_EXPORT
void apply_f64_to_f32(const DistortionDirection direction,
                      const size_t data_chunk_start,
                      const size_t data_chunk_end, const double* in_data_ptr,
                      const size_t in_data_size, const size_t in_data_stride,
                      float* out_data_ptr, const size_t out_data_size,
                      const size_t out_data_stride,
                      const CameraParameters camera_parameters,
                      const double film_back_radius_cm,
                      Parameters3deAnamorphicStdDeg6Rescaled lens_parameters);

}  // namespace mmlens

#endif  // MM_LENS_DISTORTION_PROCESS_H
