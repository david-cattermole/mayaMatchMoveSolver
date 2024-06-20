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

#include <mmcore/mmdata.h>
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
#include "steps.h"

bool run_frame(mmlens::FrameNumber frame,
               const mmlens::DistortionDirection distortion_direction,
               const size_t image_width, const size_t image_height,
               const size_t num_channels,
               const mmlens::CameraParameters camera_parameters,
               const double film_back_radius_cm,

               const uint8_t layer_count, mmlens::DistortionLayers& lens_layers,

               const ExrCompressionMode exr_compression_mode,
               std::string output_file_path_string, int32_t num_threads,
               const bool verbose) {
    auto bbox_in_data_ptr = &BOUNDING_BOX_IDENTITY_COORDS[0];
    const size_t bbox_in_data_stride = 2;
    const size_t bbox_out_data_stride = 4;
    const size_t bbox_in_data_size =
        BOUNDING_BOX_COORD_COUNT * bbox_in_data_stride;
    const size_t bbox_out_data_size =
        BOUNDING_BOX_COORD_COUNT * bbox_out_data_stride;

    for (uint8_t layer_num = 0; layer_num < layer_count; layer_num++) {
        std::cout << "layer_num: " << static_cast<int>(layer_num) << std::endl;
        const auto lens_model_type =
            lens_layers.layer_lens_model_type(layer_num);

        std::chrono::duration<float> bbox_duration;
        const mmimage::Box2F32 box_region =
            calculate_lens_distortion_bbox_region(
                layer_num, frame, lens_model_type, camera_parameters,
                film_back_radius_cm, lens_layers, bbox_duration, verbose);

        auto display_window =
            mmimage::ImageRegionRectangle{0, 0, image_width, image_height};
        auto layer_position = mmimage::Vec2I32{0, 0};

        std::chrono::duration<float> create_duration;
        std::chrono::duration<float> process_duration;
        auto pixel_buffer = mmimage::ImagePixelBuffer();
        calculate_image(distortion_direction, layer_num, frame, lens_model_type,
                        camera_parameters, film_back_radius_cm, lens_layers,
                        //
                        image_width, image_height, num_channels, pixel_buffer,
                        num_threads,
                        //
                        create_duration, process_duration);

        const std::string output_file_path_string =
            compute_output_file_path(output_file_path_string, frame, verbose);
        const rust::Str output_file_path(output_file_path_string.c_str());

        auto meta_data = mmimage::ImageMetaData();
        std::chrono::duration<float> write_duration;
        bool save_result = save_exr_image(
            display_window, layer_position, exr_compression_mode, pixel_buffer,
            meta_data, output_file_path, write_duration, verbose);

        // Controls if the image will be double checked by reading the
        // saved image file just after being written. This is a validation
        // test that is not needed for anything other than testing.
        const bool reread_image = false;

        auto reread_duration = std::chrono::duration<float>::zero();
        bool reread_result = true;
        if (reread_image) {
            auto reread_start = std::chrono::high_resolution_clock::now();
            reread_result = mmimage::image_read_pixels_exr_f32x4(
                output_file_path, meta_data, pixel_buffer);
            auto reread_end = std::chrono::high_resolution_clock::now();
            reread_duration = reread_end - reread_start;
            std::cout << "Re-read image file path: " << output_file_path << '\n'
                      << "        image read result: "
                      << static_cast<uint32_t>(reread_result) << '\n'
                      << "        image width x height: "
                      << pixel_buffer.image_width() << 'x'
                      << pixel_buffer.image_height() << std::endl;
        }

        if (verbose) {
            std::cout << std::fixed << std::setprecision(3)
                      << "Create time: " << create_duration.count()
                      << " seconds\n"
                      << "BBox time: " << bbox_duration.count() << " seconds\n"
                      << "Process time: " << process_duration.count()
                      << " seconds\n"
                      << "Write time: " << write_duration.count()
                      << " seconds\n"
                      << "Re-Read time: " << reread_duration.count()
                      << " seconds" << std::endl;
        }

        if (!save_result) {
            std::cerr << "Failed to write image." << output_file_path
                      << std::endl;
            return false;
        }

        if (!reread_result) {
            std::cerr << "Failed to re-read image: " << output_file_path
                      << std::endl;
            return false;
        }
    }
    return true;
}

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

    // Read input image dimensions.
    //
    // ... or fall back to the given resolution (via command line arguments)
    //
    // TODO: Update resolution based on the input file contents.
    const size_t image_width = 3600;
    const size_t image_height = 2400;
    const size_t num_channels = 4;  // 4 channels - RGBA
    const rust::Str input_file_path(args.input_file_path.c_str());

    // Read input lens distortion file.
    //
    // From the file we can tell if the lens distortion is animated,
    // or not. We can re-use lens distortion values across frames if
    // they are not animated. This also includes when some frames
    // share lens distortion, but others do not; such as frames 1 to
    // 10 are the same and frames 11 to 20 are animated.
    const rust::Str lens_file_path(args.lens_file_path.c_str());
    mmlens::DistortionLayers lens_layers =
        mmlens::read_lens_file(lens_file_path);
    std::cout << "read_lens_file: " << lens_layers.as_string().c_str()
              << std::endl;

    const uint8_t layer_count = lens_layers.layer_count();
    std::cout << "layer_count: " << static_cast<int>(layer_count) << std::endl;
    MMSOLVER_ASSERT(layer_count == 1,
                    "Error: Only 1 layer is supported currently.");

    const mmlens::CameraParameters camera_parameters =
        lens_layers.camera_parameters();
    const double film_back_radius_cm =
        mmlens::compute_diagonal_normalized_camera_factor(camera_parameters);
    std::cout << "film_back_radius_cm: " << film_back_radius_cm << std::endl;

    const mmlens::DistortionDirection distortion_direction =
        convert_distortion_direction(args.direction);

    mmlens::HashValue64 last_frame_hash = 0;
    const mmlens::FrameNumber start_frame = args.start_frame;
    const mmlens::FrameNumber end_frame = args.end_frame;
    for (mmlens::FrameNumber frame = start_frame; frame <= end_frame; frame++) {
        std::cout << "frame: " << frame << std::endl;

        const mmlens::HashValue64 frame_hash = lens_layers.frame_hash(frame);
        std::cout << "frame_hash: " << frame_hash << std::endl;

        if (last_frame_hash == frame_hash) {
            // TODO: Re-use the computed values from last frame if so.
        } else {
            last_frame_hash = frame_hash;
        }

        bool frame_valid = lens_layers_frame_is_valid(lens_layers, frame);
        if (!frame_valid) {
            std::cerr << "Warning: Skipping frame. Frame " << frame
                      << " is invalid." << std::endl;
            continue;
        }

        const bool result =
            run_frame(frame, distortion_direction, image_width, image_height,
                      num_channels, camera_parameters, film_back_radius_cm,

                      // Layers
                      layer_count, lens_layers,

                      // Out to write out data.
                      args.exr_compression, args.output_file_path,
                      args.num_threads, args.verbose);

        if (!result) {
            return result;
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

    bool process_succeeded = false;
    std::chrono::duration<float> duration;
    {
        auto start = std::chrono::high_resolution_clock::now();
        process_succeeded = run(args);
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

    if (!process_succeeded) {
        return 1;
    }
    return 0;
}
