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

#ifndef MM_SOLVER_LENS_DISTORTION_ARGUMENTS_H
#define MM_SOLVER_LENS_DISTORTION_ARGUMENTS_H

#include <mmimage/mmimage.h>
#include <mmlens/mmlens.h>
#include <mmsolverlibs/assert.h>
#include <mmsolverlibs/buildConstant.h>

#include <cstddef>
#include <cstdint>
#include <cstring>
#include <sstream>
#include <string>

#include "constants.h"

enum class ExrCompressionMode : uint8_t {
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
    const auto project_version = ::mmsolverlibs::build_info::project_version();
    std::stringstream software_name_join;
    software_name_join << EXR_METADATA_SOFTWARE_NAME << " v" << project_version;
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

void print_version() {
    const auto project_version = ::mmsolverlibs::build_info::project_version();
    std::cout << TOOL_EXECUTABLE_NAME << " v" << project_version << std::endl;
}

void print_description(const char* this_executable_file) {
    const auto project_name = ::mmsolverlibs::build_info::project_name();
    const auto project_copyright =
        ::mmsolverlibs::build_info::project_copyright();
    const auto project_homepage_url =
        ::mmsolverlibs::build_info::project_homepage_url();
    std::cout << this_executable_file << '\n'
              << TOOL_DESCRIPTION << '\n'
              << '\n'
              << "This tool is part of " << project_name << ".\n"
              << project_name << " is copyright " << project_copyright << '\n'
              << project_homepage_url << '\n'
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
    MMSOLVER_CORE_ASSERT(
        argc > 0, "Not enough arguments available. This should never happen.");
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

#endif  // MM_SOLVER_LENS_DISTORTION_ARGUMENTS_H
