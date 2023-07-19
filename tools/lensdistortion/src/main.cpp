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

#include <mmimage/mmimage.h>
#include <mmsolverlibs/assert.h>
#include <mmsolverlibs/debug.h>

#include <chrono>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>

#include "apply.h"
#include "arguments.h"
#include "buffer.h"
#include "constants.h"

bool run(const Arguments& args) {
    if (args.verbose) {
        std::cout
            << "Running... \n"
            << "Lens           : " << args.lens_file_path.c_str() << '\n'
            << "Input          : " << args.input_file_path.c_str() << '\n'
            << "Output         : " << args.output_file_path.c_str() << '\n'
            << "Start Frame    : " << static_cast<int>(args.start_frame) << '\n'
            << "End Frame      : " << static_cast<int>(args.end_frame) << '\n'
            << "Direction      : " << static_cast<int>(args.direction) << '\n'
            << "ExrCompression : " << static_cast<int>(args.exr_compression)
            << '\n'
            << "NumThreads     : " << static_cast<int>(args.num_threads) << '\n'
            << "Verbose        : " << static_cast<int>(args.verbose) << '\n'
            << std::endl;
    }

    auto thread_count = mmlens::initialize_global_thread_pool(args.num_threads);
    if (args.verbose) {
        std::cout << "Initialized " << thread_count << " threads." << std::endl;
    }

    // 1) Read input image dimensions.
    //
    // ... or fall back to the given resolution (via command line arguments)
    const size_t image_width = 3600;
    const size_t image_height = 2400;
    const size_t num_channels = 4;  // 4 channels - RGBA
    const auto input_file_path = rust::Str(args.input_file_path);

    // 2) Read input lens distortion file.
    //
    // From the file we can tell if the lens distortion is animated,
    // or not. We can re-use lens distortion values across frames if
    // they are not animated. This also includes when some frames
    // share lens distortion, but others do not; such as frames 1 to
    // 10 are the same and frames 11 to 20 are animated.
    const auto lens_file_path = rust::Str(args.lens_file_path);
    mmlens::DistortionLayers lens_layers =
        mmlens::read_lens_file(lens_file_path);
    std::cout << "read_lens_file: " << lens_layers.as_string().c_str()
              << std::endl;

    const uint8_t layer_count = lens_layers.layer_count();
    std::cout << "layer_count: " << static_cast<int>(layer_count) << std::endl;

    const mmlens::CameraParameters camera_parameters =
        lens_layers.camera_parameters();
    const double film_back_radius_cm =
        mmlens::compute_diagonal_normalized_camera_factor(camera_parameters);
    std::cout << "film_back_radius_cm: " << film_back_radius_cm << std::endl;

    const mmlens::DistortionDirection distortion_direction =
        convert_distortion_direction(args.direction);

    const size_t pixel_count = image_width * image_height;
    auto intermediate_buffer = mmimage::ImagePixelBuffer();
    auto out_buffer = mmimage::ImagePixelBuffer();

    const InputMode image_input_mode = InputMode::kIdentity;
    const OutputMode image_output_mode = OutputMode::kF32x4;
    allocate_buffer_memory(distortion_direction, layer_count, image_width,
                           image_height, image_input_mode, image_output_mode,
                           intermediate_buffer, out_buffer);

    // The input buffer is purposefully empty of all data, because the
    // input coordinates will be identity, and therefore it's not
    // needed.
    auto in_buffer_slice = BufferSlice();

    BufferSlice intermediate_buffer_slice = BufferSlice(
        intermediate_buffer.data_type(), intermediate_buffer.image_width(),
        intermediate_buffer.image_height(), intermediate_buffer.num_channels(),
        intermediate_buffer.as_slice_f32x4_mut().data());
    BufferSlice out_buffer_slice =
        BufferSlice(out_buffer.data_type(), out_buffer.image_width(),
                    out_buffer.image_height(), out_buffer.num_channels(),
                    out_buffer.as_slice_f32x4_mut().data());

    mmlens::HashValue64 last_frame_hash = 0;
    const mmlens::FrameNumber start_frame = args.start_frame;
    const mmlens::FrameNumber end_frame = args.end_frame;
    for (mmlens::FrameNumber frame = start_frame; frame <= end_frame; frame++) {
        std::cout << "frame: " << frame << std::endl;

        const mmlens::HashValue64 frame_hash = lens_layers.frame_hash(frame);
        std::cout << "frame_hash: " << frame_hash << std::endl;
        // TODO: Check if the last frame's hash is the same and re-use
        // the computed values from last frame if so.
        last_frame_hash = frame_hash;

        bool frame_valid = lens_layers_frame_is_valid(lens_layers, frame);
        if (!frame_valid) {
            std::cerr << "Warning: Skipping frame. Frame " << frame
                      << " is invalid." << std::endl;
            continue;
        }

        calculate_lens_layers_distortion(
            distortion_direction, lens_layers, frame, image_width, image_height,
            image_input_mode, image_output_mode, in_buffer_slice,
            intermediate_buffer_slice, out_buffer_slice, camera_parameters,
            film_back_radius_cm, args.num_threads);

        for (uint8_t layer_num = 0; layer_num < layer_count; layer_num++) {
            std::cout << "layer_num: " << static_cast<int>(layer_num)
                      << std::endl;

            mmlens::OptionParameters3deClassic option =
                lens_layers.layer_lens_parameters_3de_classic(layer_num, frame);
            std::cout << "option.exists: " << static_cast<int>(option.exists)
                      << std::endl;

            // TODO: Generate a hash for the lens parameters. If the
            // hash has not changed since the last frame we can re-use
            // the results from last frame.
            const mmlens::Parameters3deClassic lens_parameters = option.value;

            // 3) Process lens distortion and write images.

            // TODO: Compute the bounding box of the lens distortion values,
            // so we can work out how many pixels to generate outside the
            // Display Window.
            //
            // To calculate the bounding box we sample the un-distortion and
            // re-distortion at 32 positions along the outer edge of the
            // image, then we get the minimum and maximum values. Finally we
            // add a small offset number, for padding, to ensure we
            // definitely have *just* enough pixels.
            //
            // TODO: It would be handy to pre-compute the bounding box
            // for all frames. This would allow us find the frame with
            // the largest required pixel count and then pre-allocate
            // the maximum amount of memory required for the largest
            // image and therefore always be sure that we are not
            // exceeding the memory.
            std::chrono::duration<float> bbox_duration;
            auto point_min =
                mmimage::Vec2F32{std::numeric_limits<float>::max(),
                                 std::numeric_limits<float>::max()};
            auto point_max =
                mmimage::Vec2F32{std::numeric_limits<float>::lowest(),
                                 std::numeric_limits<float>::lowest()};
            {
                auto bbox_start = std::chrono::high_resolution_clock::now();

                std::vector<mmimage::PixelF32x4> out_bounding_coords(
                    BOUNDING_BOX_COORD_COUNT);

                const size_t in_data_stride = 2;
                const size_t out_data_stride = 4;
                const size_t in_data_size =
                    BOUNDING_BOX_COORD_COUNT * in_data_stride;
                const size_t out_data_size =
                    BOUNDING_BOX_COORD_COUNT * out_data_stride;
                auto in_data_ptr = &BOUNDING_BOX_IDENTITY_COORDS[0];
                auto out_data_ptr =
                    reinterpret_cast<float*>(out_bounding_coords.data());

                const auto pixel_count = in_data_size / in_data_stride;
                mmlens::apply_f64_to_f32(
                    distortion_direction, 0, pixel_count, in_data_ptr,
                    in_data_size, in_data_stride, out_data_ptr, out_data_size,
                    out_data_stride, camera_parameters, film_back_radius_cm,
                    lens_parameters);

                for (int i = 0; i < out_bounding_coords.size(); i++) {
                    mmimage::PixelF32x4 rgba_pixel = out_bounding_coords[i];
                    point_min.x = std::min<float>(point_min.x, rgba_pixel.r);
                    point_min.y = std::min<float>(point_min.y, rgba_pixel.g);
                    point_min.x = std::min<float>(point_min.x, rgba_pixel.b);
                    point_min.y = std::min<float>(point_min.y, rgba_pixel.a);

                    point_max.x = std::max<float>(point_max.x, rgba_pixel.r);
                    point_max.y = std::max<float>(point_max.y, rgba_pixel.g);
                    point_max.x = std::max<float>(point_max.x, rgba_pixel.b);
                    point_max.y = std::max<float>(point_max.y, rgba_pixel.a);
                }

                auto bbox_end = std::chrono::high_resolution_clock::now();
                bbox_duration = bbox_end - bbox_start;
            }
            if (args.verbose) {
                std::cout << "BBox Min: " << point_min.x << ", " << point_min.y
                          << " Max: " << point_max.y << ", " << point_max.y
                          << std::endl;
            }
            // TODO: Use calculated BBox to allocate the required image data
            // as the "data window".
            //
            // TODO: Check for invalid min/max values. Infinite or NaN
            // values may be returned and we must gracefully error in
            // that case.
            if (!std::isfinite(point_min.x) || !std::isfinite(point_min.y) ||
                !std::isfinite(point_max.x) || !std::isfinite(point_max.y)) {
                MMSOLVER_CORE_ERR(
                    std::cerr,
                    "Bounding box must have a finite size, skipping frame "
                        << frame << ".");
                MMSOLVER_PANIC("Bounding box must have a finite size, got "
                               << "min: " << point_min.x << ", " << point_min.y
                               << " max: " << point_max.y << ", "
                               << point_max.y);
                continue;
            }

            auto display_window =
                mmimage::ImageRegionRectangle{0, 0, image_width, image_height};
            auto layer_position = mmimage::Vec2I32{0, 0};

            // Create image pixel data.
            //
            // TODO: Save processing time by re-using the last frame's
            // result if the lens distortion has not changed between
            // runs.
            std::chrono::duration<float> create_duration;
            auto meta_data = mmimage::ImageMetaData();
            auto pixel_buffer = mmimage::ImagePixelBuffer();
            {
                auto create_start = std::chrono::high_resolution_clock::now();
                const size_t num_channels = 4;
                pixel_buffer.resize(mmimage::BufferDataType::kF32, image_width,
                                    image_height, num_channels);
                auto create_end = std::chrono::high_resolution_clock::now();
                create_duration = create_end - create_start;
            }
            rust::Slice<mmimage::PixelF32x4> data_slice_mut =
                pixel_buffer.as_slice_f32x4_mut();
            const size_t data_size = image_width * image_height * num_channels;
            float* data_ptr = reinterpret_cast<float*>(data_slice_mut.data());

            // Compute the lens distortion.
            std::chrono::duration<float> process_duration;
            {
                auto process_start = std::chrono::high_resolution_clock::now();

                const size_t data_stride = 4;  // RGBA.
                if (args.num_threads == 1) {
                    mmlens::apply_identity_to_f32(
                        distortion_direction, image_width, image_height, 0, 0,
                        image_width, image_height, data_ptr, data_size,
                        data_stride, camera_parameters, film_back_radius_cm,
                        lens_parameters);
                } else {
                    mmlens::apply_identity_to_f32_multithread(
                        distortion_direction, image_width, image_height,
                        data_ptr, data_size, data_stride, camera_parameters,
                        film_back_radius_cm, lens_parameters);
                }
                auto process_end = std::chrono::high_resolution_clock::now();
                process_duration = process_end - process_start;
            }

            // Save the OpenEXR image.
            //
            // TODO: Properly format the output path given with the
            // frame number embedded into it, taking into account file
            // path rules such as "####" converting to "0001".
            std::stringstream output_file_path_join;
            output_file_path_join << args.output_file_path << '.' << frame
                                  << ".exr";
            std::string output_file_path_string = output_file_path_join.str();
            const auto output_file_path = rust::Str(output_file_path_string);
            // TODO: file_path = mmfileseq::construct_file_path(file_path,
            // frame);
            if (args.verbose) {
                std::cout << "Output file path: " << output_file_path
                          << std::endl;
            }

            auto exr_compression =
                convert_exr_compression(args.exr_compression);
            auto exr_encoder = mmimage::ImageExrEncoder{
                exr_compression,
                mmimage::ExrPixelLayout{mmimage::ExrPixelLayoutMode::kScanLines,
                                        0, 0},
                mmimage::ExrLineOrder::kIncreasing,
            };

            meta_data.set_display_window(display_window);
            meta_data.set_layer_name("rgba");
            meta_data.set_layer_position(layer_position);

            std::string software_name = query_software_name();
            meta_data.set_software_name(software_name);
            if (args.verbose) {
                std::cout << "Output image metadata: " << meta_data.as_string()
                          << std::endl;
            }

            std::chrono::duration<float> write_duration;
            bool result = false;
            {
                auto write_start = std::chrono::high_resolution_clock::now();
                result = mmimage::image_write_pixels_exr_f32x4(
                    output_file_path, exr_encoder, meta_data, pixel_buffer);
                auto write_end = std::chrono::high_resolution_clock::now();
                write_duration = write_end - write_start;
            }
            if (!result) {
                if (result) {
                    std::cerr
                        << "ERROR: Failed to write image: " << output_file_path
                        << std::endl;
                }
            } else if (args.verbose && result) {
                std::cout << "Successfully wrote: " << output_file_path
                          << std::endl;
            }

            // Controls if the image will be double checked by reading the
            // saved image file just after being written. This is a validation
            // test that is not needed for anything other than testing.
            const bool reread_image = false;

            // Re-read the file can be used for debugging only, but
            // not on by default.
            bool reread_result = true;
            std::chrono::duration<float> reread_duration;
            if (reread_image) {
                auto reread_start = std::chrono::high_resolution_clock::now();
                reread_result = mmimage::image_read_pixels_exr_f32x4(
                    output_file_path, meta_data, pixel_buffer);
                auto reread_end = std::chrono::high_resolution_clock::now();
                reread_duration = reread_end - reread_start;
                std::cout << "Re-read image file path: " << output_file_path
                          << '\n'
                          << "        image read result: "
                          << static_cast<uint32_t>(reread_result) << '\n'
                          << "        image width x height: "
                          << pixel_buffer.image_width() << 'x'
                          << pixel_buffer.image_height() << std::endl;
            }

            if (args.verbose) {
                std::cout << std::fixed << std::setprecision(3)
                          << "Create time: " << create_duration.count()
                          << " seconds\n"
                          << "BBox time: " << bbox_duration.count()
                          << " seconds\n"
                          << "Process time: " << process_duration.count()
                          << " seconds\n"
                          << "Write time: " << write_duration.count()
                          << " seconds\n"
                          << "Re-Read time: " << reread_duration.count()
                          << " seconds" << std::endl;
            }

            if (!result) {
                return false;
            }
        }
    }

    return true;
}

int main(const int argc, const char* argv[]) {
    Arguments args;
    args.start_frame = 1;
    args.end_frame = 1;
    args.direction = Direction::kBoth;
    args.exr_compression = ExrCompressionMode::kZIP16;
    args.num_threads = 0;
    args.verbose = false;

    const bool parse_succeeded = parse_arguments(argc, argv, args);
    if (!parse_succeeded) {
        return 0;
    }

    std::chrono::duration<float> duration;
    {
        auto start = std::chrono::high_resolution_clock::now();
        const bool process_succeeded = run(args);
        auto end = std::chrono::high_resolution_clock::now();
        duration = end - start;
    }
    if (args.verbose) {
        const mmlens::FrameNumber start_frame = args.start_frame;
        const mmlens::FrameNumber end_frame = args.end_frame;
        const double frame_count =
            static_cast<double>((end_frame - start_frame) + 1);
        const double average_time_per_frame = duration.count() / frame_count;
        const double frames_per_second = 1.0 / average_time_per_frame;
        std::cout << std::fixed << std::setprecision(3)
                  << "Average Frame time: " << average_time_per_frame
                  << " seconds\n"
                  << "Frames per-second: " << frames_per_second << " seconds\n"
                  << "Total time: " << duration.count() << " seconds\n"
                  << std::endl;
    }
    if (!parse_succeeded) {
        return 1;
    }

    return 0;
}
