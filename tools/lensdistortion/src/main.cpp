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

#include <mmSolver/buildConstant.h>
#include <mmimage/mmimage.h>
#include <mmlens/mmlens.h>

#include <algorithm>
#include <cassert>
#include <chrono>
#include <cstring>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

const char* TOOL_EXECUTABLE_NAME = "mmsolver-lensdistortion";
const char* TOOL_DESCRIPTION = "Create lens distortion ST-Maps.";
const char* EXR_METADATA_SOFTWARE_NAME = "mayaMatchMoveSolver (mmSolver)";

// The coordinates around the edges of an image bounding box. These
// coordinates are used to sample the lens distortion at the edges to
// find the maximum/minimum extent of the distorted bounding box.
const size_t BOUNDING_BOX_COORD_COUNT = 32;
const double BOUNDING_BOX_IDENTITY_COORDS[BOUNDING_BOX_COORD_COUNT * 2] = {
    // Bottom Edge
    -0.5, -0.5,    //
    -0.375, -0.5,  //
    -0.25, -0.5,   //
    -0.125, -0.5,  //
    0.0, -0.5,     //
    0.125, -0.5,   //
    0.25, -0.5,    //
    0.375, -0.5,   //
    0.5, -0.5,     //

    // Left Edge
    -0.5, -0.375,  //
    -0.5, -0.25,   //
    -0.5, -0.125,  //
    -0.5, 0.0,     //
    -0.5, 0.125,   //
    -0.5, 0.25,    //
    -0.5, 0.375,   //
    -0.5, 0.5,     //

    // Right Edge
    -0.375, 0.5,  //
    -0.25, 0.5,   //
    -0.125, 0.5,  //
    0.0, 0.5,     //
    0.125, 0.5,   //
    0.25, 0.5,    //
    0.375, 0.5,   //

    // Top Edge   //
    0.5, -0.375,  //
    0.5, -0.25,   //
    0.5, -0.125,  //
    0.5, 0.0,     //
    0.5, 0.125,   //
    0.5, 0.25,    //
    0.5, 0.375,   //
    0.5, 0.5,     //
};

enum class ExrCompressionMode : ::std::uint8_t {
    kUncompressed = 0,
    kRLE = 1,
    kZIP1 = 2,
    kZIP16 = 3,
    kPIZ = 4,
};

mmimage::ExrCompression convert_exr_compression(ExrCompressionMode value) {
    if (value == ExrCompressionMode::kZIP1) {
        return mmimage::ExrCompression::kZIP1;
    } else if (value == ExrCompressionMode::kZIP16) {
        return mmimage::ExrCompression::kZIP16;
    } else if (value == ExrCompressionMode::kRLE) {
        return mmimage::ExrCompression::kRLE;
    } else if (value == ExrCompressionMode::kPIZ) {
        return mmimage::ExrCompression::kPIZ;
    } else {
        // Other compression methods are not currently considered
        // important for this tool. B44 may be added to this list.
        return mmimage::ExrCompression::kZIP16;
    }
}

enum class Direction : ::std::uint8_t {
    kUndistort = 0,
    kRedistort = 1,
    kBoth = 2,
};

mmlens::DistortionDirection convert_distortion_direction(Direction value) {
    if (value == Direction::kUndistort) {
        return mmlens::DistortionDirection::kUndistort;
    } else if (value == Direction::kRedistort) {
        return mmlens::DistortionDirection::kRedistort;
    } else {
        return mmlens::DistortionDirection::kUndistortAndRedistort;
    }
}

std::string query_software_name() {
    std::stringstream software_name_join;
    software_name_join << EXR_METADATA_SOFTWARE_NAME << " v" << PROJECT_VERSION;
    return software_name_join.str();
}

struct Arguments {
    std::string lens_file_path;
    std::string input_file_path;
    std::string output_file_path;
    mmlens::FrameNumber start_frame;
    mmlens::FrameNumber end_frame;
    ExrCompressionMode exr_compression;
    Direction direction;
    int32_t num_threads;
    bool verbose;
};

bool lens_layers_frame_is_valid(const mmlens::DistortionLayers& lens_layers,
                                const mmlens::FrameNumber frame) {
    bool result = true;
    const mmlens::LayerSize layer_count = lens_layers.get_layer_count();
    for (mmlens::LayerIndex layer_num = 0; layer_num < layer_count;
         layer_num++) {
        std::cout << "layer_num: " << static_cast<int>(layer_num) << std::endl;

        mmlens::LensModelType lens_model_type =
            lens_layers.layer_lens_model_type(layer_num);
        std::cout << "lens_model_type: " << static_cast<int>(lens_model_type)
                  << std::endl;
        if (lens_model_type == mmlens::LensModelType::kUninitialized) {
            std::cerr << "Warning: Invalid lens model type on " << frame << '.'
                      << std::endl;
            result = false;
            break;
        }

        mmlens::OptionParameters3deClassic option =
            lens_layers.layer_parameters_3de_classic(layer_num, frame);
        std::cout << "option.exists: " << static_cast<int>(option.exists)
                  << std::endl;

        if (!option.exists) {
            result = false;
            break;
        }
    }
    return result;
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

    // 1) Read input image dimensions.
    //
    // ... or fall back to the given resolution (via command line arguments)
    const size_t width = 3600;
    const size_t height = 2400;
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

    const uint8_t layer_count = lens_layers.get_layer_count();
    std::cout << "layer_count: " << static_cast<int>(layer_count) << std::endl;

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
        // TODO: Check if the last frame's hash is the same and re-use
        // the computed values from last frame if so.
        last_frame_hash = frame_hash;

        bool frame_valid = lens_layers_frame_is_valid(lens_layers, frame);
        if (!frame_valid) {
            std::cerr << "Warning: Skipping frame. Frame " << frame
                      << " is invalid." << std::endl;
            continue;
        }

        for (uint8_t layer_num = 0; layer_num < layer_count; layer_num++) {
            mmlens::OptionParameters3deClassic option =
                lens_layers.layer_parameters_3de_classic(layer_num, frame);
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
            std::chrono::duration<float> bbox_duration;
            auto point_min =
                mmimage::Vec2F32{std::numeric_limits<float>::max(),
                                 std::numeric_limits<float>::max()};
            auto point_max =
                mmimage::Vec2F32{std::numeric_limits<float>::min(),
                                 std::numeric_limits<float>::min()};
            {
                auto bbox_start = std::chrono::high_resolution_clock::now();

                std::vector<mmimage::PixelRgbaF32> out_bounding_coords(
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
                    mmimage::PixelRgbaF32 rgba_pixel = out_bounding_coords[i];
                    point_min.x = std::min(point_min.x, rgba_pixel.r);
                    point_min.y = std::min(point_min.y, rgba_pixel.g);
                    point_min.x = std::min(point_min.x, rgba_pixel.b);
                    point_min.y = std::min(point_min.y, rgba_pixel.a);

                    point_max.x = std::max(point_max.x, rgba_pixel.r);
                    point_max.y = std::max(point_max.y, rgba_pixel.g);
                    point_max.x = std::max(point_max.x, rgba_pixel.b);
                    point_max.y = std::max(point_max.y, rgba_pixel.a);
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

            auto display_window =
                mmimage::ImageRegionRectangle{0, 0, width, height};
            auto layer_position = mmimage::Vec2I32{0, 0};

            // Create image pixel data.
            //
            // TODO: Save processing time by re-using the last frame's
            // result if the lens distortion has not changed between
            // runs.
            std::chrono::duration<float> create_duration;
            auto meta_data = mmimage::ImageMetaData();
            auto pixel_data = mmimage::ImagePixelDataRgbaF32();
            {
                auto create_start = std::chrono::high_resolution_clock::now();
                mmimage::create_image_rgba_f32(width, height, pixel_data);
                auto create_end = std::chrono::high_resolution_clock::now();
                create_duration = create_end - create_start;
            }
            rust::Slice<mmimage::PixelRgbaF32> data_slice_mut =
                pixel_data.data_mut();
            const size_t data_size = width * height * num_channels;
            float* data_ptr = reinterpret_cast<float*>(data_slice_mut.data());

            // Compute the lens distortion.
            std::chrono::duration<float> process_duration;
            {
                auto process_start = std::chrono::high_resolution_clock::now();

                const size_t data_stride = 4;  // RGBA.
                if (args.num_threads == 1) {
                    mmlens::apply_identity_to_f32(
                        distortion_direction, width, height, 0, 0, width,
                        height, data_ptr, data_size, data_stride,
                        camera_parameters, film_back_radius_cm,
                        lens_parameters);
                } else {
                    mmlens::apply_identity_to_f32_multithread(
                        distortion_direction, width, height, data_ptr,
                        data_size, data_stride, camera_parameters,
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
                result = mmimage::image_write_pixels_exr_rgba_f32(
                    output_file_path, exr_encoder, meta_data, pixel_data);
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

            bool reread_result = true;
            std::chrono::duration<float> reread_duration;

            // bool reread_result = false;
            // std::chrono::duration<float> reread_duration;
            // {
            //     auto reread_start = std::chrono::high_resolution_clock::now();
            //     reread_result = mmimage::image_read_pixels_exr_rgba_f32(
            //         output_file_path, meta_data, pixel_data);
            //     auto reread_end = std::chrono::high_resolution_clock::now();
            //     reread_duration = reread_end - reread_start;
            // }
            // std::cout << "Re-read image file path: " << output_file_path << '\n'
            //           << "        image read result: "
            //           << static_cast<uint32_t>(reread_result) << '\n'
            //           << "        image width x height: " << pixel_data.width()
            //           << 'x' << pixel_data.height() << std::endl;

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

void print_version() {
    std::cout << TOOL_EXECUTABLE_NAME << " v" << PROJECT_VERSION << std::endl;
}

void print_description(const char* this_executable_file) {
    std::cout << this_executable_file << '\n'
              << TOOL_DESCRIPTION << '\n'
              << '\n'
              << "This tool is part of " << PROJECT_NAME << ".\n"
              << PROJECT_NAME << " is copyright " << PROJECT_COPYRIGHT << '\n'
              << PROJECT_HOMEPAGE_URL << '\n'
              << std::endl;
}

void print_flags() {
    std::cout
        << "Flags:\n"
        << "  -h  --help           Print this help message.\n"
        << "  -v  --version        Print the software version.\n"
        << '\n'
        << "  -o  --output         Output file path.\n"
        << "  -i  --input          TODO: Input file path.\n"
        << "      --lens           Lens distortion file path.\n"
        << "      --frame-range    First and last frame to output.\n"
        << "      --stmap          TODO: Generate an ST-Map.\n"
        << "      --padding        TODO: Extra padding added to the ST-Map.\n"
        << "      --direction      The direction of the ST-Map.\n"
        << "                       'undistort', 'redistort', 'both'\n"
        << "                       (default is 'both')\n"
        << "      --exr-compress   OpenEXR compression method;\n"
        << "                       ZIP1, ZIP16, RLE, or PIZ\n"
        << "                       (default is ZIP16)\n"
        << "      --verbose        Print detailed information.\n"
        << "      --num-threads    Number of threads;\n"
        << "                       -1=physical, 0=logical, 1=single\n"
        << "                       (default is 0, logical CPU count).\n"
        << std::endl;
}

void print_help(const char* this_executable_file) {
    print_version();
    print_description(this_executable_file);
    print_flags();
}

// This is a copy of the "stringToNumber" function in
// "./src/mmSolver/utilities/string_utils.h".
//
// TODO: Make "string_utils.h" available in this tool, so we can
// delete this function.
template <typename NUM_TYPE>
NUM_TYPE convert_string_to_number(const std::string& text) {
    std::stringstream ss(text);
    NUM_TYPE result;
    ss >> result;
    if (!result) {
        result = 0;
    }
    return result;
}

bool parse_arguments(const int argc, const char* argv[], Arguments& args) {
    assert(argc > 0);
    if (argc == 1) {
        print_help(argv[0]);
        return false;
    }

    for (int i = 1; i < argc; i++) {
        const char* arg = argv[i];

        const int next_index1 = i + 1;
        const int next_index2 = i + 2;
        std::string next_arg1 = "";
        std::string next_arg2 = "";
        if (next_index1 < argc) {
            next_arg1 = std::string(argv[next_index1]);
        }
        if (next_index2 < argc) {
            next_arg2 = std::string(argv[next_index2]);
        }

        const bool is_help_flag = (std::strcmp(arg, "-h") == 0) ||
                                  (std::strcmp(arg, "-help") == 0) ||
                                  (std::strcmp(arg, "--help") == 0);
        const bool is_version_flag = (std::strcmp(arg, "-v") == 0) ||
                                     (std::strcmp(arg, "--version") == 0);
        const bool is_input_flag =
            (std::strcmp(arg, "-i") == 0) || (std::strcmp(arg, "--input") == 0);
        const bool is_lens_flag = std::strcmp(arg, "--lens") == 0;
        const bool is_output_flag = (std::strcmp(arg, "-o") == 0) ||
                                    (std::strcmp(arg, "--output") == 0);
        const bool is_frame_range_flag = std::strcmp(arg, "--frame-range") == 0;
        const bool is_direction_flag = std::strcmp(arg, "--direction") == 0;
        const bool is_num_threads_flag = std::strcmp(arg, "--num-threads") == 0;
        const bool is_verbose_flag = std::strcmp(arg, "--verbose") == 0;

        if (is_help_flag) {
            print_help(argv[0]);
            return false;
        } else if (is_version_flag) {
            print_version();
            return false;
        } else if (is_verbose_flag) {
            args.verbose = true;
        } else if (is_frame_range_flag) {
            if ((next_arg1.size() == 0) || (next_arg2.size() == 0)) {
                print_help(argv[0]);
                return false;
            }
            args.start_frame = convert_string_to_number<mmlens::FrameNumber>(
                std::string(next_arg1));
            args.end_frame = convert_string_to_number<mmlens::FrameNumber>(
                std::string(next_arg2));
            i += 2;
        } else if (is_direction_flag) {
            if (next_arg1.size() == 0) {
                print_help(argv[0]);
                return false;
            }

            const bool is_undistort =
                std::strcmp(next_arg1.c_str(), "undistort") == 0;
            const bool is_redistort =
                std::strcmp(next_arg1.c_str(), "redistort") == 0;
            const bool is_both = std::strcmp(next_arg1.c_str(), "both") == 0;
            if (is_undistort) {
                args.direction = Direction::kUndistort;
            } else if (is_redistort) {
                args.direction = Direction::kRedistort;
            } else {
                args.direction = Direction::kBoth;
            }

            i++;
        } else if (is_num_threads_flag) {
            if (next_arg1.size() == 0) {
                print_help(argv[0]);
                return false;
            }
            const int32_t given_value =
                convert_string_to_number<int32_t>(std::string(next_arg1));
            // Negative numbers below -1 are technically invalid
            // values and so we force all negative numbers to '-1'
            // logic.
            args.num_threads = std::max(-1, given_value);
            i++;
        } else if (is_input_flag) {
            if (next_arg1.size() == 0) {
                print_help(argv[0]);
                return false;
            }
            args.input_file_path = std::string(next_arg1);
            i++;
        } else if (is_lens_flag) {
            if (next_arg1.size() == 0) {
                print_help(argv[0]);
                return false;
            }
            args.lens_file_path = std::string(next_arg1);
            i++;
        } else if (is_output_flag) {
            if (next_arg1.size() == 0) {
                print_help(argv[0]);
                return false;
            }
            args.output_file_path = std::string(next_arg1);
            i++;
        } else {
            std::cout << "Invalid flag: " << arg << '\n';
            return false;
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
    args.num_threads = false;
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
