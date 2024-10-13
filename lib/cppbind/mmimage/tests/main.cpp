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

#include <cstring>
#include <iostream>
#include <sstream>
#include <string>

#include "test_a.h"
#include "test_b.h"
#include "test_c.h"
#include "test_d.h"

void print_help(const char *exec_file) {
    std::cout
        << "Executable: " << exec_file << '\n'
        << '\n'
        << "Help:\n"
        << "This command is used to test the mmimage component of mmSolver.\n"
        << '\n'
        << "Download the test images from "
        << "https://github.com/AcademySoftwareFoundation/openexr-images\n"
        << "Then run this executable file with the first argument as the path "
        << "to the \"openexr-images\" directory.\n"
        << '\n'
        << "Like this on Linux:\n"
        << "$ mmimage_tests /path/to/openexr-images/\n"
        << "...or on Windows: \n"
        << "> mmimage_tests.exe C:\\path\\to\\openexr-images\\" << std::endl;
}

int main(int argc, char *argv[]) {
    for (int i = 0; i < argc; i++) {
        const char *arg = argv[i];
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
    const char *dir_path = argv[1];

    if (!test_a("mmimage_test_a:", dir_path)) {
        return 1;
    }
    if (!test_b("mmimage_test_b:", dir_path)) {
        return 1;
    }
    if (!test_c("mmimage_test_c:", dir_path)) {
        return 1;
    }
    if (!test_d("mmimage_test_d:", dir_path)) {
        return 1;
    }
    return 0;
}
