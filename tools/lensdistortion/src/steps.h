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
 * This tool is used to generate lens distortion ST-Maps.
 */

// MM Solver Libs
#include <mmcore/mmdata.h>
#include <mmimage/mmimage.h>
#include <mmsolverlibs/assert.h>
#include <mmsolverlibs/debug.h>

// STL
#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>  // stringstream

#include "apply.h"
#include "arguments.h"
#include "buffer.h"
#include "constants.h"

// Compute the bounding box of the lens distortion values, so we can
// work out how many pixels to generate outside the Display Window.
//
// To calculate the bounding box we sample the un-distortion and
// re-distortion at 32 positions along the outer edge of the image,
// then we get the minimum and maximum values. Finally we add a small
// offset number, for padding, to ensure we definitely have *just*
// enough pixels.
//
// TODO: It would be handy to pre-compute the bounding box for all
// frames. This would allow us find the frame with the largest
// required pixel count and then pre-allocate the maximum amount of
// memory required for the largest image and therefore always be sure
// that we are not exceeding the memory.
template <typename LENS_TYPE>
mmimage::Box2F32 calculate_lens_distortion_bbox_region_function(
    const mmlens::FrameNumber frame,
    const mmlens::CameraParameters camera_parameters,
    const double film_back_radius_cm, const LENS_TYPE lens_parameters,
    std::chrono::duration<float>& bbox_duration, const bool verbose) {
    auto bbox_start = std::chrono::high_resolution_clock::now();

    const size_t in_data_stride = 2;   // X and Y coordinates.
    const size_t out_data_stride = 4;  // Undistort XY and Distort XY.
    const size_t in_data_size = BOUNDING_BOX_COORD_COUNT * in_data_stride;
    const size_t out_data_size = BOUNDING_BOX_COORD_COUNT * out_data_stride;

    std::vector<mmimage::PixelF32x4> bbox_out_coords(BOUNDING_BOX_COORD_COUNT);
    auto in_data_ptr = &BOUNDING_BOX_IDENTITY_COORDS[0];
    auto out_data_ptr = reinterpret_cast<float*>(bbox_out_coords.data());

    const size_t in_pixel_count = in_data_size / in_data_stride;
    const size_t out_pixel_count = out_data_size / out_data_stride;
    MMSOLVER_CORE_ASSERT(in_pixel_count == out_pixel_count,
                         "Pixel count must match between input and output.");

    // TODO: Use 'calculate_lens_layers_distortion' function to
    // support multiple lens layers.
    mmlens::apply_f64_to_f32(
        mmlens::DistortionDirection::kUndistortAndRedistort, 0, in_pixel_count,
        in_data_ptr, in_data_size, in_data_stride, out_data_ptr, out_data_size,
        out_data_stride, camera_parameters, film_back_radius_cm,
        lens_parameters);

    auto point_min = mmimage::Vec2F32{std::numeric_limits<float>::max(),
                                      std::numeric_limits<float>::max()};
    auto point_max = mmimage::Vec2F32{std::numeric_limits<float>::lowest(),
                                      std::numeric_limits<float>::lowest()};
    for (size_t i = 0; i < bbox_out_coords.size(); i++) {
        mmimage::PixelF32x4 rgba_pixel = bbox_out_coords[i];
        point_min.x = std::min<float>(point_min.x, rgba_pixel.r);
        point_min.y = std::min<float>(point_min.y, rgba_pixel.g);
        point_min.x = std::min<float>(point_min.x, rgba_pixel.b);
        point_min.y = std::min<float>(point_min.y, rgba_pixel.a);

        point_max.x = std::max<float>(point_max.x, rgba_pixel.r);
        point_max.y = std::max<float>(point_max.y, rgba_pixel.g);
        point_max.x = std::max<float>(point_max.x, rgba_pixel.b);
        point_max.y = std::max<float>(point_max.y, rgba_pixel.a);
    }

    if (verbose) {
        std::cout << "BBox Min: " << point_min.x << ", " << point_min.y
                  << " Max: " << point_max.y << ", " << point_max.y
                  << std::endl;
    }

    // TODO: Check for invalid min/max values. Infinite or NaN values
    // may be returned and we must gracefully error in that case.
    if (!std::isfinite(point_min.x) || !std::isfinite(point_min.y) ||
        !std::isfinite(point_max.x) || !std::isfinite(point_max.y)) {
        MMSOLVER_CORE_ERR(
            std::cerr, "Bounding box must have a finite size, skipping frame "
                           << frame << ".");
        MMSOLVER_CORE_PANIC("Bounding box must have a finite size, got "
                            << "min: " << point_min.x << ", " << point_min.y
                            << " max: " << point_max.y << ", " << point_max.y);
        return mmimage::Box2F32{0.0, 0.0, 0.0, 0.0};
    }

    return mmimage::Box2F32{point_min.x, point_min.y, point_max.x, point_max.y};
}

// Process lens distortion bounding box, and calculate the maximum
// bbox region required for undistortion and redistortion.
mmimage::Box2F32 calculate_lens_distortion_bbox_region(
    const uint8_t layer_num, const mmlens::FrameNumber frame,
    const mmlens::LensModelType lens_model_type,
    const mmlens::CameraParameters camera_parameters,
    const double film_back_radius_cm,
    const mmlens::DistortionLayers& lens_layers,
    std::chrono::duration<float>& bbox_duration, const bool verbose) {
    auto bbox_start = std::chrono::high_resolution_clock::now();

    // TODO: Generate a hash for the lens parameters. If the
    // hash has not changed since the last frame we can re-use
    // the results from last frame.

    mmimage::Box2F32 box_region = mmimage::Box2F32{0.0, 0.0, 0.0, 0.0};

    if (lens_model_type == mmlens::LensModelType::k3deClassic) {
        const auto option =
            lens_layers.layer_lens_parameters_3de_classic(layer_num, frame);
        MMSOLVER_CORE_ASSERT(
            option.exists,
            "LensParameters are expected to exist for matching LensModelType.");

        const auto lens_parameters = option.value;
        box_region = calculate_lens_distortion_bbox_region_function(
            frame, camera_parameters, film_back_radius_cm, lens_parameters,
            bbox_duration, verbose);

    } else if (lens_model_type == mmlens::LensModelType::k3deRadialStdDeg4) {
        const auto option =
            lens_layers.layer_lens_parameters_3de_radial_std_deg4(layer_num,
                                                                  frame);
        MMSOLVER_CORE_ASSERT(
            option.exists,
            "LensParameters are expected to exist for matching LensModelType.");

        const auto lens_parameters = option.value;
        box_region = calculate_lens_distortion_bbox_region_function(
            frame, camera_parameters, film_back_radius_cm, lens_parameters,
            bbox_duration, verbose);
    } else if (lens_model_type ==
               mmlens::LensModelType::k3deAnamorphicStdDeg4) {
        const auto option =
            lens_layers.layer_lens_parameters_3de_anamorphic_std_deg4(layer_num,
                                                                      frame);
        MMSOLVER_CORE_ASSERT(
            option.exists,
            "LensParameters are expected to exist for matching LensModelType.");

        const auto lens_parameters = option.value;
        box_region = calculate_lens_distortion_bbox_region_function(
            frame, camera_parameters, film_back_radius_cm, lens_parameters,
            bbox_duration, verbose);
    } else if (lens_model_type ==
               mmlens::LensModelType::k3deAnamorphicStdDeg4Rescaled) {
        const auto option =
            lens_layers.layer_lens_parameters_3de_anamorphic_std_deg4_rescaled(
                layer_num, frame);
        MMSOLVER_CORE_ASSERT(
            option.exists,
            "LensParameters are expected to exist for matching LensModelType.");

        const auto lens_parameters = option.value;
        box_region = calculate_lens_distortion_bbox_region_function(
            frame, camera_parameters, film_back_radius_cm, lens_parameters,
            bbox_duration, verbose);

    } else if (lens_model_type ==
               mmlens::LensModelType::k3deAnamorphicStdDeg6) {
        const auto option =
            lens_layers.layer_lens_parameters_3de_anamorphic_std_deg6(layer_num,
                                                                      frame);
        MMSOLVER_CORE_ASSERT(
            option.exists,
            "LensParameters are expected to exist for matching LensModelType.");

        const auto lens_parameters = option.value;
        box_region = calculate_lens_distortion_bbox_region_function(
            frame, camera_parameters, film_back_radius_cm, lens_parameters,
            bbox_duration, verbose);
    } else if (lens_model_type ==
               mmlens::LensModelType::k3deAnamorphicStdDeg6Rescaled) {
        const auto option =
            lens_layers.layer_lens_parameters_3de_anamorphic_std_deg6_rescaled(
                layer_num, frame);
        MMSOLVER_CORE_ASSERT(
            option.exists,
            "LensParameters are expected to exist for matching LensModelType.");

        const auto lens_parameters = option.value;
        box_region = calculate_lens_distortion_bbox_region_function(
            frame, camera_parameters, film_back_radius_cm, lens_parameters,
            bbox_duration, verbose);

    } else {
        std::stringstream message;
        message << "calculate_lens_distortion_bbox_region: Unsupported "
                   "lens_model_type: "
                << static_cast<int>(lens_model_type);
        MMSOLVER_CORE_TODO(message.str().c_str());
    }

    auto bbox_end = std::chrono::high_resolution_clock::now();
    bbox_duration = bbox_end - bbox_start;

    return box_region;
}

void calculate_image(const mmlens::DistortionDirection distortion_direction,
                     const uint8_t layer_num, const mmlens::FrameNumber frame,
                     const mmlens::LensModelType lens_model_type,
                     const mmlens::CameraParameters camera_parameters,
                     const double film_back_radius_cm,
                     const mmlens::DistortionLayers& lens_layers,

                     // Image dimensions.
                     const size_t image_width, const size_t image_height,
                     const size_t num_channels,
                     mmimage::ImagePixelBuffer& out_pixel_buffer,

                     const int num_threads,
                     std::chrono::duration<float>& create_duration,
                     std::chrono::duration<float>& process_duration) {
    auto intermediate_buffer = mmimage::ImagePixelBuffer();

    const InputMode image_input_mode = InputMode::kIdentity;
    const OutputMode image_output_mode = OutputMode::kF32x4;

    // A switch to use the old or new code.
    const bool use_new_code = true;

    // Create image pixel data.
    //
    // TODO: Save processing time by re-using the last frame's
    // result if the lens distortion has not changed between
    // runs.
    {
        auto create_start = std::chrono::high_resolution_clock::now();

        if (use_new_code) {
            const size_t pixel_count = image_width * image_height;
            const uint8_t layer_count = lens_layers.layer_count();
            allocate_buffer_memory(distortion_direction, layer_count,
                                   image_width, image_height, image_input_mode,
                                   image_output_mode, intermediate_buffer,
                                   out_pixel_buffer);
        } else {
            const size_t num_channels = 4;
            out_pixel_buffer.resize(mmimage::BufferDataType::kF32, image_width,
                                    image_height, num_channels);
        }

        auto create_end = std::chrono::high_resolution_clock::now();
        create_duration = create_end - create_start;
    }

    // Compute the lens distortion on the image.
    {
        auto process_start = std::chrono::high_resolution_clock::now();

        if (use_new_code) {
            // The input buffer is empty of all data, because the input
            // coordinates will be identity.
            auto in_buffer_slice = BufferSlice();

            BufferSlice intermediate_buffer_slice =
                BufferSlice(intermediate_buffer.data_type(),
                            intermediate_buffer.image_width(),
                            intermediate_buffer.image_height(),
                            intermediate_buffer.num_channels(),
                            intermediate_buffer.as_slice_f32x4_mut().data());
            BufferSlice out_pixel_buffer_slice = BufferSlice(
                out_pixel_buffer.data_type(), out_pixel_buffer.image_width(),
                out_pixel_buffer.image_height(),
                out_pixel_buffer.num_channels(),
                out_pixel_buffer.as_slice_f32x4_mut().data());

            calculate_lens_layers_distortion(
                distortion_direction, lens_layers, frame, image_width,
                image_height, image_input_mode, image_output_mode,
                in_buffer_slice, intermediate_buffer_slice,
                out_pixel_buffer_slice, camera_parameters, film_back_radius_cm,
                num_threads);
        } else {
            rust::Slice<mmimage::PixelF32x4> data_slice_mut =
                out_pixel_buffer.as_slice_f32x4_mut();
            const size_t data_size = image_width * image_height * num_channels;
            float* data_ptr = reinterpret_cast<float*>(data_slice_mut.data());

            const size_t data_stride = 4;  // RGBA.
            if (lens_model_type == mmlens::LensModelType::k3deClassic) {
                mmlens::OptionParameters3deClassic option =
                    lens_layers.layer_lens_parameters_3de_classic(layer_num,
                                                                  frame);
                std::cout << "calculate_image: option.exists: "
                          << static_cast<int>(option.exists) << std::endl;
                if (option.exists) {
                    const mmlens::Parameters3deClassic lens_parameters =
                        option.value;
                    if (num_threads == 1) {
                        auto image_dimensions = mmlens::ImageDimensions{
                            image_width, image_height, 0,
                            0,           image_width,  image_height};

                        mmlens::apply_identity_to_f32(
                            distortion_direction, image_dimensions, data_ptr,
                            data_size, data_stride, camera_parameters,
                            film_back_radius_cm, lens_parameters);
                    } else {
                        mmlens::apply_identity_to_f32_multithread(
                            distortion_direction, image_width, image_height,
                            data_ptr, data_size, data_stride, camera_parameters,
                            film_back_radius_cm, lens_parameters);
                    }
                }
            } else {
                MMSOLVER_CORE_TODO(
                    "calculate_image: Unsupported lens_model_type: "
                    << static_cast<int>(lens_model_type));
            }
        }

        auto process_end = std::chrono::high_resolution_clock::now();
        process_duration = process_end - process_start;
    }
}

std::string compute_output_file_path(const std::string& input_output_file_path,
                                     const mmlens::FrameNumber frame,
                                     const bool verbose) {
    std::stringstream output_file_path_join;
    output_file_path_join << input_output_file_path << '.' << frame << ".exr";
    std::string output_file_path_string = output_file_path_join.str();

    // TODO: Properly format the output path given with the frame number
    // embedded into it, taking into account file path rules such as
    // "####" converting to "0001".
    //
    // // file_path = mmfileseq::construct_file_path(file_path, frame);
    if (verbose) {
        std::cout << "Output file path: " << output_file_path_string
                  << std::endl;
    }
    return output_file_path_string;
}

bool save_exr_image(const mmimage::ImageRegionRectangle display_window,
                    const mmimage::Vec2I32 layer_position,
                    const ExrCompressionMode exr_compression_mode,
                    mmimage::ImagePixelBuffer& pixel_buffer,
                    mmimage::ImageMetaData& meta_data,
                    const rust::Str& output_file_path,
                    std::chrono::duration<float>& write_duration,
                    const bool verbose) {
    auto exr_compression = convert_exr_compression(exr_compression_mode);
    auto exr_encoder = mmimage::ImageExrEncoder{
        exr_compression,
        mmimage::ExrPixelLayout{mmimage::ExrPixelLayoutMode::kScanLines, 0, 0},
        mmimage::ExrLineOrder::kIncreasing,
    };

    meta_data.set_display_window(display_window);
    meta_data.set_layer_name("rgba");
    meta_data.set_layer_position(layer_position);

    std::string software_name = query_software_name();
    meta_data.set_software_name(software_name);
    if (verbose) {
        std::cout << "Output image metadata: " << meta_data.as_string()
                  << std::endl;
    }

    bool save_result = false;
    {
        auto write_start = std::chrono::high_resolution_clock::now();
        save_result = mmimage::image_write_pixels_exr_f32x4(
            output_file_path, exr_encoder, meta_data, pixel_buffer);
        auto write_end = std::chrono::high_resolution_clock::now();
        write_duration = write_end - write_start;
    }
    if (!save_result) {
        std::cerr << "ERROR: Failed to write image: " << output_file_path
                  << std::endl;
    } else if (verbose && save_result) {
        std::cout << "Successfully wrote: " << output_file_path << std::endl;
    }

    return save_result;
}
