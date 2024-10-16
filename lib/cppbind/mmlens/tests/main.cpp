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

#include <mmlens/mmlens.h>

#include <cstring>
#include <iostream>
#include <string>
#include <utility>

#include "test_batch_3de_anamorphic_std_deg4.h"
#include "test_batch_3de_anamorphic_std_deg4_rescaled.h"
#include "test_batch_3de_classic.h"
#include "test_batch_3de_radial_std_deg4.h"
#include "test_both_3de_anamorphic_std_deg4.h"
#include "test_both_3de_anamorphic_std_deg4_rescaled.h"
#include "test_both_3de_classic.h"
#include "test_both_3de_radial_std_deg4.h"
#include "test_lens_file_load.h"
#include "test_once_3de_anamorphic_std_deg4.h"
#include "test_once_3de_anamorphic_std_deg4_rescaled.h"
#include "test_once_3de_classic.h"
#include "test_once_3de_radial_std_deg4.h"

void print_help(const char* exec_file) {
    std::cout
        << "Executable: " << exec_file << '\n'
        << '\n'
        << "Help:\n"
        << "This command is used to test the mmlens component of mmSolver.\n"
        << '\n'
        << "Run this executable file with the first argument as the directory"
        << " to the test files.\n"
        << '\n'
        << "Like this on Linux:\n"
        << "$ mmlens_tests /path/to/project_root/lib/cppbind/mmlens/tests/\n"
        << "...or on Windows: \n"
        << "> mmlens_tests.exe "
        << "C:\\path\\to\\project_root\\lib\\cppbind\\mmlens\\tests\\"
        << std::endl;
}

int main(int argc, char* argv[]) {
    for (int i = 0; i < argc; i++) {
        const char* arg = argv[i];
        const bool is_help_flag = (std::strcmp(arg, "-h") == 0) ||
                                  (std::strcmp(arg, "-help") == 0) ||
                                  (std::strcmp(arg, "--help") == 0);
        if (is_help_flag) {
            print_help(argv[0]);
            return 0;
        }
    }

    if (argc <= 1) {
        print_help(argv[0]);
        return 0;
    }
    const char* dir_path = argv[1];

    // Verbosity level;
    // - 0 == Minimal info is printed.
    // - 1 == Standard info is printed.
    // - 2 == All info is printed.
    const int verbosity = 0;

    // 0 == logical CPU count, -1 == Physical CPU count, numbers
    // greater than 0 mean an explicit number of threads.
    const auto num_threads = 0;
    mmlens::initialize_global_thread_pool(num_threads);

    // The sizes of pseudo "images" to test with.
    std::vector<std::pair<size_t, size_t>> test_image_sizes;
    test_image_sizes.push_back(std::make_pair(8, 8));
    test_image_sizes.push_back(std::make_pair(80, 80));
    test_image_sizes.push_back(std::make_pair(73, 3));

    // Loop over all values in a buffer, evaluating all values in the
    // buffer at once, in batch.
    bool multithread = false;
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        multithread = false;
        test_batch_3de_classic(image_width, image_height, multithread,
                               verbosity);
        multithread = true;
        test_batch_3de_classic(image_width, image_height, multithread,
                               verbosity);
    }
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        multithread = false;
        test_batch_3de_radial_std_deg4(image_width, image_height, multithread,
                                       verbosity);
        multithread = true;
        test_batch_3de_radial_std_deg4(image_width, image_height, multithread,
                                       verbosity);
    }
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        multithread = false;
        test_batch_3de_anamorphic_std_deg4(image_width, image_height,
                                           multithread, verbosity);
        multithread = true;
        test_batch_3de_anamorphic_std_deg4(image_width, image_height,
                                           multithread, verbosity);
    }
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        multithread = false;
        test_batch_3de_anamorphic_std_deg4_rescaled(image_width, image_height,
                                                    multithread, verbosity);
        multithread = true;
        test_batch_3de_anamorphic_std_deg4_rescaled(image_width, image_height,
                                                    multithread, verbosity);
    }

    // Loop over each coordinate and call the evaluation of each
    // once. This achieves the same result as the "batch" approach but
    // could be slower due to the number of (virtual?) function calls.
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        test_once_3de_classic(image_width, image_height, verbosity);
    }
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        test_once_3de_radial_std_deg4(image_width, image_height, verbosity);
    }
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        test_once_3de_anamorphic_std_deg4(image_width, image_height, verbosity);
    }
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        test_once_3de_anamorphic_std_deg4_rescaled(image_width, image_height,
                                                   verbosity);
    }

    // Calculates both undistortion and redistortion in the same loop.
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        multithread = false;
        test_both_3de_classic(image_width, image_height, multithread,
                              verbosity);
        multithread = true;
        test_both_3de_classic(image_width, image_height, multithread,
                              verbosity);
    }
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        multithread = false;
        test_both_3de_radial_std_deg4(image_width, image_height, multithread,
                                      verbosity);
        multithread = true;
        test_both_3de_radial_std_deg4(image_width, image_height, multithread,
                                      verbosity);
    }
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        multithread = false;
        test_both_3de_anamorphic_std_deg4(image_width, image_height,
                                          multithread, verbosity);
        multithread = true;
        test_both_3de_anamorphic_std_deg4(image_width, image_height,
                                          multithread, verbosity);
    }
    for (const auto& test_size : test_image_sizes) {
        size_t image_width = test_size.first;
        size_t image_height = test_size.second;
        multithread = false;
        test_both_3de_anamorphic_std_deg4_rescaled(image_width, image_height,
                                                   multithread, verbosity);
        multithread = true;
        test_both_3de_anamorphic_std_deg4_rescaled(image_width, image_height,
                                                   multithread, verbosity);
    }

    // Load Lens files.
    test_lens_file_load(dir_path, "test_file_3de_classic_1.nk");
    test_lens_file_load(dir_path, "test_file_3de_radial_std_deg4_1.nk");
    test_lens_file_load(dir_path, "test_file_3de_anamorphic_std_deg4_1.nk");
    test_lens_file_load(dir_path,
                        "test_file_3de_anamorphic_std_deg4_rescaled_1.nk");
    test_lens_file_load(dir_path, "test_file_3de_classic_2.nk");
    test_lens_file_load(dir_path, "test_file_3de_radial_std_deg4_2.nk");
    test_lens_file_load(dir_path, "test_file_3de_anamorphic_std_deg4_2.nk");
    test_lens_file_load(dir_path,
                        "test_file_3de_anamorphic_std_deg4_rescaled_2.nk");
    test_lens_file_load(dir_path, "test_file_3de_classic_3.nk");
    test_lens_file_load(dir_path, "test_file_3de_radial_std_deg4_3.nk");
    test_lens_file_load(dir_path, "test_file_3de_anamorphic_std_deg4_3.nk");
    test_lens_file_load(dir_path,
                        "test_file_3de_anamorphic_std_deg4_rescaled_3.nk");
    return 0;
}
