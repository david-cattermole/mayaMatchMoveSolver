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

#ifndef MM_SOLVER_LENS_DISTORTION_APPLY_H
#define MM_SOLVER_LENS_DISTORTION_APPLY_H

// STL
#include <cstdint>
#include <iostream>
#include <limits>
#include <sstream>  // stringstream

// MM Solver Libs
#include <mmimage/mmimage.h>
#include <mmlens/mmlens.h>
#include <mmsolverlibs/assert.h>

#include "buffer.h"

bool lens_layers_frame_is_valid(const mmlens::DistortionLayers& lens_layers,
                                const mmlens::FrameNumber frame) {
    bool result = true;
    const mmlens::LayerSize layer_count = lens_layers.layer_count();
    for (mmlens::LayerIndex layer_num = 0; layer_num < layer_count;
         layer_num++) {
        mmlens::LensModelType lens_model_type =
            lens_layers.layer_lens_model_type(layer_num);
        if (lens_model_type == mmlens::LensModelType::kUninitialized) {
            std::cerr << "Warning: Invalid lens model type on " << frame << '.'
                      << std::endl;
            result = false;
            break;
        }

        mmlens::OptionParameters3deClassic option_classic =
            lens_layers.layer_lens_parameters_3de_classic(layer_num, frame);
        if (option_classic.exists) {
            continue;
        }

        mmlens::OptionParameters3deRadialStdDeg4 option_radial =
            lens_layers.layer_lens_parameters_3de_radial_std_deg4(layer_num,
                                                                  frame);
        if (option_radial.exists) {
            continue;
        }

        mmlens::OptionParameters3deAnamorphicStdDeg4 option_anamorphic =
            lens_layers.layer_lens_parameters_3de_anamorphic_std_deg4(layer_num,
                                                                      frame);
        if (option_anamorphic.exists) {
            continue;
        }

        mmlens::OptionParameters3deAnamorphicStdDeg4Rescaled
            option_anamorphic_rescaled =
                lens_layers
                    .layer_lens_parameters_3de_anamorphic_std_deg4_rescaled(
                        layer_num, frame);
        if (option_anamorphic_rescaled.exists) {
            continue;
        }

        result = false;
        break;
    }
    return result;
}

enum class InputMode : uint8_t {
    kIdentity = 0,
    kF64x2 = 1,
    kF64x4 = 2,
};

enum class OutputMode : uint8_t {
    kF32x4 = 0,
    kF64x2 = 1,
    kF64x4 = 2,
};

template <typename LENS_TYPE>
void function(const InputMode input_mode, const OutputMode output_mode,
              const mmlens::DistortionDirection distortion_direction,
              const size_t image_width, const size_t image_height,
              BufferSlice& in_buffer, BufferSlice& out_buffer,
              const mmlens::CameraParameters camera_parameters,
              const double film_back_radius_cm, const LENS_TYPE lens_parameters,
              const int32_t num_threads) {
    const size_t pixel_count = image_width * image_height;
    const size_t in_data_size = in_buffer.element_count();
    const size_t in_pixel_count = in_buffer.pixel_count();
    const size_t out_data_size = out_buffer.element_count();
    const size_t out_pixel_count = out_buffer.pixel_count();

    auto image_dimensions = mmlens::ImageDimensions{
        image_width, image_height, 0, 0, image_width, image_height};

    if ((input_mode == InputMode::kIdentity) &&
        (output_mode == OutputMode::kF32x4)) {
        const size_t out_data_stride = 4;  // RGBA.
        float* out_data_ptr = static_cast<float*>(out_buffer.data_mut());
        MMSOLVER_CORE_ASSERT(
            pixel_count == out_pixel_count,
            "pixel counts of output buffer must match image width/height.");

        if (num_threads == 1) {
            mmlens::apply_identity_to_f32(
                distortion_direction, image_dimensions, out_data_ptr,
                out_data_size, out_data_stride, camera_parameters,
                film_back_radius_cm, lens_parameters);
        } else {
            mmlens::apply_identity_to_f32_multithread(
                distortion_direction, image_width, image_height, out_data_ptr,
                out_data_size, out_data_stride, camera_parameters,
                film_back_radius_cm, lens_parameters);
        }

    } else if ((input_mode == InputMode::kIdentity) &&
               (output_mode == OutputMode::kF64x2)) {
        const size_t out_data_stride = 2;
        double* out_data_ptr = static_cast<double*>(out_buffer.data_mut());
        MMSOLVER_CORE_ASSERT(
            pixel_count == out_pixel_count,
            "pixel counts of output buffer must match image width/height.");

        if (num_threads == 1) {
            mmlens::apply_identity_to_f64(
                distortion_direction, image_dimensions, out_data_ptr,
                out_data_size, out_data_stride, camera_parameters,
                film_back_radius_cm, lens_parameters);
        } else {
            mmlens::apply_identity_to_f64_multithread(
                distortion_direction, image_width, image_height, out_data_ptr,
                out_data_size, out_data_stride, camera_parameters,
                film_back_radius_cm, lens_parameters);
        }

    } else if ((input_mode == InputMode::kIdentity) &&
               (output_mode == OutputMode::kF64x4)) {
        const size_t out_data_stride = 4;
        double* out_data_ptr = static_cast<double*>(out_buffer.data_mut());
        MMSOLVER_CORE_ASSERT(
            pixel_count == out_pixel_count,
            "pixel counts of output buffer must match image width/height.");

        if (num_threads == 1) {
            mmlens::apply_identity_to_f64(
                distortion_direction, image_dimensions, out_data_ptr,
                out_data_size, out_data_stride, camera_parameters,
                film_back_radius_cm, lens_parameters);
        } else {
            mmlens::apply_identity_to_f64_multithread(
                distortion_direction, image_width, image_height, out_data_ptr,
                out_data_size, out_data_stride, camera_parameters,
                film_back_radius_cm, lens_parameters);
        }

    } else if ((input_mode == InputMode::kF64x2) &&
               (output_mode == OutputMode::kF64x2)) {
        const size_t in_data_stride = 2;
        const size_t out_data_stride = 2;
        const double* in_data_ptr =
            static_cast<const double*>(in_buffer.data());
        double* out_data_ptr = static_cast<double*>(out_buffer.data_mut());
        MMSOLVER_CORE_ASSERT(
            pixel_count == in_pixel_count == out_pixel_count,
            "pixel counts of input and output buffers must match.");

        if (num_threads == 1) {
            mmlens::apply_f64_to_f64(
                distortion_direction, 0, pixel_count, in_data_ptr, in_data_size,
                in_data_stride, out_data_ptr, out_data_size, out_data_stride,
                camera_parameters, film_back_radius_cm, lens_parameters);
        } else {
            mmlens::apply_f64_to_f64_multithread(
                distortion_direction, in_data_ptr, in_data_size, in_data_stride,
                out_data_ptr, out_data_size, out_data_stride, camera_parameters,
                film_back_radius_cm, lens_parameters);
        }
    }
}

void calculate_lens_layer_distortion(
    const InputMode input_mode, const OutputMode output_mode,
    const mmlens::DistortionDirection distortion_direction,
    const mmlens::DistortionLayers& lens_layers,
    const mmlens::LayerIndex layer_num, const mmlens::FrameNumber frame,
    const size_t image_width, const size_t image_height, BufferSlice& in_buffer,
    BufferSlice& out_buffer, const mmlens::CameraParameters camera_parameters,
    const double film_back_radius_cm, const int32_t num_threads) {
    mmlens::LensModelType lens_model_type =
        lens_layers.layer_lens_model_type(layer_num);

    if (lens_model_type == mmlens::LensModelType::k3deClassic) {
        mmlens::OptionParameters3deClassic option_lens_parameters =
            lens_layers.layer_lens_parameters_3de_classic(layer_num, frame);
        if (!option_lens_parameters.exists) {
            return;
        }
        const mmlens::Parameters3deClassic lens_parameters =
            option_lens_parameters.value;
        function<mmlens::Parameters3deClassic>(
            input_mode, output_mode, distortion_direction, image_width,
            image_height, in_buffer, out_buffer, camera_parameters,
            film_back_radius_cm, lens_parameters, num_threads);

    } else if (lens_model_type == mmlens::LensModelType::k3deRadialStdDeg4) {
        mmlens::OptionParameters3deRadialStdDeg4 option_lens_parameters =
            lens_layers.layer_lens_parameters_3de_radial_std_deg4(layer_num,
                                                                  frame);
        if (!option_lens_parameters.exists) {
            return;
        }
        const mmlens::Parameters3deRadialStdDeg4 lens_parameters =
            option_lens_parameters.value;
        function<mmlens::Parameters3deRadialStdDeg4>(
            input_mode, output_mode, distortion_direction, image_width,
            image_height, in_buffer, out_buffer, camera_parameters,
            film_back_radius_cm, lens_parameters, num_threads);

    } else if (lens_model_type ==
               mmlens::LensModelType::k3deAnamorphicStdDeg4) {
        mmlens::OptionParameters3deAnamorphicStdDeg4 option_lens_parameters =
            lens_layers.layer_lens_parameters_3de_anamorphic_std_deg4(layer_num,
                                                                      frame);
        if (!option_lens_parameters.exists) {
            return;
        }
        const mmlens::Parameters3deAnamorphicStdDeg4 lens_parameters =
            option_lens_parameters.value;
        function<mmlens::Parameters3deAnamorphicStdDeg4>(
            input_mode, output_mode, distortion_direction, image_width,
            image_height, in_buffer, out_buffer, camera_parameters,
            film_back_radius_cm, lens_parameters, num_threads);

    } else if (lens_model_type ==
               mmlens::LensModelType::k3deAnamorphicStdDeg4Rescaled) {
        mmlens::OptionParameters3deAnamorphicStdDeg4Rescaled
            option_lens_parameters =
                lens_layers
                    .layer_lens_parameters_3de_anamorphic_std_deg4_rescaled(
                        layer_num, frame);
        if (!option_lens_parameters.exists) {
            return;
        }
        const mmlens::Parameters3deAnamorphicStdDeg4Rescaled lens_parameters =
            option_lens_parameters.value;
        function<mmlens::Parameters3deAnamorphicStdDeg4Rescaled>(
            input_mode, output_mode, distortion_direction, image_width,
            image_height, in_buffer, out_buffer, camera_parameters,
            film_back_radius_cm, lens_parameters, num_threads);

    } else {
        MMSOLVER_CORE_TODO("Unsupported lens_model_type: "
                           << static_cast<int>(lens_model_type));
    }
}

enum class CompareModeSize : uint8_t {
    kInputLargerThanOutput = 0,
    kInputSmallerThanOutput = 1,
    kInputAndOutputSame = 2,
    kUnspecified = 255,
};

// Compares the byte sizes of InputMode and OutputMode, to show the
// equality of the number of bytes used for different modes.
//
// Returns kInputLargerThanOutput if input is larger than output.
// Returns kInputAndOutputSame if input is the same size as output.
// Returns kInputSmallerThanOutput if the input smaller than output.
//
// If an error happens, kUnspesifided is returned.
CompareModeSize compare_input_output_mode_size(const InputMode input_mode,
                                               const OutputMode output_mode) {
    if (input_mode == InputMode::kIdentity) {
        // Identity is 0 bytes, so output is always larger.
        return CompareModeSize::kInputSmallerThanOutput;
    } else if (input_mode == InputMode::kF64x2) {
        // Input is 16 bytes per-pixel.
        if (output_mode == OutputMode::kF32x4) {
            // Output is 16 bytes per-pixel.
            return CompareModeSize::kInputAndOutputSame;
        } else if (output_mode == OutputMode::kF64x2) {
            // Output is 16 bytes per-pixel.
            return CompareModeSize::kInputAndOutputSame;
        } else if (output_mode == OutputMode::kF64x4) {
            // Output is 32 bytes per-pixel.
            return CompareModeSize::kInputSmallerThanOutput;
        }
    } else if (input_mode == InputMode::kF64x4) {
        // Input is 32 bytes per-pixel.
        if (output_mode == OutputMode::kF32x4) {
            // Output is 16 bytes per-pixel.
            return CompareModeSize::kInputLargerThanOutput;
        } else if (output_mode == OutputMode::kF64x2) {
            // Output is 16 bytes per-pixel.
            return CompareModeSize::kInputLargerThanOutput;
        } else if (output_mode == OutputMode::kF64x4) {
            // Output is 32 bytes per-pixel.
            return CompareModeSize::kInputAndOutputSame;
        }
    }
    return CompareModeSize::kUnspecified;
}

void allocate_output_mode_memory(const size_t image_width,
                                 const size_t image_height,
                                 const OutputMode output_mode,
                                 mmimage::ImagePixelBuffer& out_buffer) {
    if (output_mode == OutputMode::kF32x4) {
        // Output is 16 bytes per-pixel.
        const size_t num_channels = 4;
        out_buffer.resize(mmimage::BufferDataType::kF32, image_width,
                          image_height, num_channels);
    } else if (output_mode == OutputMode::kF64x2) {
        // Output is 16 bytes per-pixel.
        const size_t num_channels = 2;
        out_buffer.resize(mmimage::BufferDataType::kF64, image_width,
                          image_height, num_channels);
    } else if (output_mode == OutputMode::kF64x4) {
        // Output is 32 bytes per-pixel.
        const size_t num_channels = 4;
        out_buffer.resize(mmimage::BufferDataType::kF64, image_width,
                          image_height, num_channels);
    }
}

void allocate_input_mode_memory(const size_t image_width,
                                const size_t image_height,
                                const InputMode input_mode,
                                mmimage::ImagePixelBuffer& in_buffer) {
    if (input_mode == InputMode::kIdentity) {
        // Input is 0 bytes per-pixel. No allocation needed.
    } else if (input_mode == InputMode::kF64x2) {
        // Input is 16 bytes per-pixel.
        const size_t num_channels = 2;
        in_buffer.resize(mmimage::BufferDataType::kF64, num_channels,
                         image_width, image_height);
    } else if (input_mode == InputMode::kF64x4) {
        // Input is 32 bytes per-pixel.
        const size_t num_channels = 4;
        in_buffer.resize(mmimage::BufferDataType::kF64, num_channels,
                         image_width, image_height);
    }
}

// Below are logic examples of how much memory is required for
// different numbers of layers in the case of ST-Maps and Bounding-Box
// calculations.
//
// --------------------------------------------------------------------
// 1 layers, kIdentity -> kF32x4 (ST-map - both un/redistort)
//
// - Layer 0: I Identity -> B f32x4
//
// In this example (1 layer, kIdentity -> kF32x4, un/redistort),
// no A buffer needs memory at all, only the output buffer.
//
// --------------------------------------------------------------------
// 2 layers, kIdentity -> kF32x4 (ST-map - both un/redistort)
//
// - Layer 0: I Identity -> A f64x4
// - Layer 1: A f64x4    -> B f32x4
//
// In this example (2 layers, kIdentity -> kF32x4, un/redistort),
// buffer A needs to be double the size of buffer B.
//
// --------------------------------------------------------------------
// 2 layers, kIdentity -> kF32x4 (ST-map - undistort only)
//
// - Layer 0: I Identity -> A f64x2
// - Layer 1: A f64x2    -> B f32x4
//
// In this example (2 layers, kIdentity -> kF32x4, undistort only),
// both buffer A and B need the same amount of memory.
//
// --------------------------------------------------------------------
// 3 layers, kIdentity -> kF32x4 (ST-map - both un/redistort)
//
// - Layer 0: I Identity -> B f64x4
// - Layer 1: B f64x4    -> A f64x4
// - Layer 2: A f64x4    -> B f32x4
//
// In this example (3 layers, kIdentity -> kF32x4, un/redistort), both
// A and B buffers need to store f64x4 at some point during the
// computation. We need at least that amount of memory in 2
// buffers.
//
// --------------------------------------------------------------------
// 3 layers, kIdentity -> kF32x4 (ST-map - undistort only)
//
// - Layer 0: I Identity -> B f64x2
// - Layer 1: B f64x2    -> A f64x2
// - Layer 2: A f64x2    -> B f32x4
//
// In this example (3 layers, kIdentity -> kF32x4, undistort only),
// the maximum amount of memory required is only f64x2 (because f32x4
// fits exactly inside f64x2).
//
// --------------------------------------------------------------------
// 4 layers, kIdentity -> kF32x4 (ST-map - both un/redistort)
//
// - Layer 0: I Identity -> A f64x4
// - Layer 1: A f64x4    -> B f64x4
// - Layer 2: B f64x4    -> A f64x4
// - Layer 3: A f64x4    -> B f32x4
//
// In this example (4 layers, kIdentity -> kF32x4, both un/redistort),
// we require f64x4 memory for both A and B buffers.
//
// --------------------------------------------------------------------
// 5 layers, kIdentity -> kF32x4 (ST-map - both un/redistort)
//
// - Layer 0: I Identity -> B f64x4
// - Layer 1: B f64x4    -> A f64x4
// - Layer 2: A f64x4    -> B f64x4
// - Layer 3: B f64x4    -> A f64x4
// - Layer 3: A f64x4    -> B f32x4
//
// In this example (4 layers, kIdentity -> kF32x4, both un/redistort),
// we require f64x4 memory for both A and B buffers. We require a
// third intermediate memory buffer (A buffer).
//
// --------------------------------------------------------------------
// 2 layers, kF64x2 -> kF32x4 (bbox - both un/redistort)
//
// - Layer 0: I f64x2 -> A f64x4
// - Layer 2: A f64x4 -> B f32x4
//
// In this example (2 layers, kF64x2 -> kF32x4), we require a third
// intermediate memory buffer (A buffer).
//
// --------------------------------------------------------------------
// 3 layers, kF64x2 -> kF32x4 (bbox - both un/redistort)
//
// - Layer 0: I f64x2 -> B f64x4
// - Layer 1: B f64x4 -> A f64x4
// - Layer 2: A f64x4 -> B f32x4
//
// In this example (3 layers, kF64x2 -> kF32x4), we know that B will
// be the output buffer and will require memory for f64x4, even if the
// final result will only need half of that.
//
void allocate_buffer_memory(
    const mmlens::DistortionDirection distortion_direction,
    const mmlens::LayerSize layer_count, const size_t image_width,
    const size_t image_height, const InputMode input_mode,
    const OutputMode output_mode,
    mmimage::ImagePixelBuffer& intermediate_buffer,
    mmimage::ImagePixelBuffer& out_buffer) {
    const bool only_single_layer = layer_count == 1;
    if (layer_count == 0) {
        MMSOLVER_CORE_PANIC("Layer count is zero.");
    }

    if (only_single_layer) {
        allocate_output_mode_memory(image_width, image_height, output_mode,
                                    out_buffer);
        return;
    }

    const bool require_four_intermidate_channels =
        (distortion_direction ==
         mmlens::DistortionDirection::kUndistortAndRedistort) ||
        (distortion_direction ==
         mmlens::DistortionDirection::kRedistortAndUndistort);

    // The "intermediate" buffer is needed to hold values between
    // layers has it's only 'mode'.
    InputMode intermediate_mode = InputMode::kF64x2;
    if (require_four_intermidate_channels) {
        intermediate_mode = InputMode::kF64x4;
    }

    allocate_input_mode_memory(image_width, image_height, intermediate_mode,
                               intermediate_buffer);
    allocate_output_mode_memory(image_width, image_height, output_mode,
                                out_buffer);

    return;
}

// Compute the lens distortion for all layers.
//
// The function arguments are expected to be valid. You must do
// validity checking before calling this function.
//
void calculate_lens_layers_distortion(
    const mmlens::DistortionDirection distortion_direction,
    const mmlens::DistortionLayers& lens_layers,
    const mmlens::FrameNumber frame, const size_t image_width,
    const size_t image_height, const InputMode input_mode,
    const OutputMode output_mode, BufferSlice& in_buffer,
    BufferSlice& intermediate_buffer, BufferSlice& out_buffer,
    const mmlens::CameraParameters camera_parameters,
    const double film_back_radius_cm, const int32_t num_threads) {
    const mmlens::LayerSize layer_count = lens_layers.layer_count();
    const bool layer_count_is_even = (layer_count % 2) == 0;

    // NOTE: All buffers are expected to have enough memory for the
    // possible operations that will be performed.

    // NOTE: As long as there is no operation between a layers that
    // requires less bytes in the destination buffer than the source,
    // then we are able to use the same buffer - reading from and
    // writing to the exact same block of memory. This should not only
    // reduce the operating memory required, but will improve CPU
    // cache usage - the input and output memory can be stored in the
    // same memory.
    for (mmlens::LayerIndex layer_num = 0; layer_num < layer_count;
         layer_num++) {
        const bool is_last_layer = (layer_num + 1) == layer_count;

        if ((layer_num == 0) && is_last_layer) {
            // Use "identity" functions, outputting to f32.
            //
            // If this is the first and only layer, then we should
            // output directly to f32, otherwise we must output to f64
            // as an intermediate data type to store as much precision
            // as possible (f32 is not accurate enough).
            if (input_mode == InputMode::kIdentity) {
                if (output_mode != OutputMode::kF32x4) {
                    MMSOLVER_CORE_TODO("Not supported yet.");
                }
                calculate_lens_layer_distortion(
                    InputMode::kIdentity, OutputMode::kF32x4,
                    distortion_direction, lens_layers, layer_num, frame,
                    image_width, image_height, in_buffer, out_buffer,
                    camera_parameters, film_back_radius_cm, num_threads);
            } else {
                MMSOLVER_CORE_TODO("Not supported yet.");
            }

        } else if ((layer_num == 0) && !is_last_layer) {
            if (input_mode == InputMode::kIdentity) {
                if (output_mode == OutputMode::kF32x4) {
                    calculate_lens_layer_distortion(
                        InputMode::kIdentity, OutputMode::kF32x4,
                        distortion_direction, lens_layers, layer_num, frame,
                        image_width, image_height, in_buffer, out_buffer,
                        camera_parameters, film_back_radius_cm, num_threads);
                } else if (output_mode == OutputMode::kF64x2) {
                    calculate_lens_layer_distortion(
                        InputMode::kIdentity, OutputMode::kF64x2,
                        distortion_direction, lens_layers, layer_num, frame,
                        image_width, image_height, in_buffer, out_buffer,
                        camera_parameters, film_back_radius_cm, num_threads);
                } else if (output_mode == OutputMode::kF64x4) {
                    calculate_lens_layer_distortion(
                        InputMode::kIdentity, OutputMode::kF64x4,
                        distortion_direction, lens_layers, layer_num, frame,
                        image_width, image_height, in_buffer, out_buffer,
                        camera_parameters, film_back_radius_cm, num_threads);
                } else {
                    MMSOLVER_CORE_TODO("Not supported yet.");
                }
            } else {
                MMSOLVER_CORE_TODO("Not supported yet.");
            }

        } else if (is_last_layer) {
            // Use "from buffer" functions, outputting to f32.
            //
            // We want to use the results from the last layer as
            // inputs in this layer.
            calculate_lens_layer_distortion(
                InputMode::kF64x2, OutputMode::kF32x4, distortion_direction,
                lens_layers, layer_num, frame, image_width, image_height,
                in_buffer, out_buffer, camera_parameters, film_back_radius_cm,
                num_threads);

        } else {
            // Use "from buffer" functions, outputting to f64.
            //
            // We want to use the results from the last layer as
            // inputs in this layer.

            MMSOLVER_CORE_TODO("Not supported yet.");
        }
    }
}

#endif  // MM_SOLVER_LENS_DISTORTION_APPLY_H
