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

#include "test_lens_file_load.h"

#include <mmlens/mmlens.h>

#include <algorithm>
#include <iostream>
#include <vector>

#include "common.h"

int test_lens_file_load(const char* dir_path, const char* file_name) {
    const auto test_name = "test_lens_file_load";
    std::cout << "Running... " << test_name << std::endl;

    // Read lens file path (eg. .nk file)
    //
    // - Give file path to Rust function.
    //
    // - Rust function will try to parse and deserialize the file.
    //
    // - A 'lens file' object will be returned, with functions that
    //   can access the underlying data structure and return
    //   CameraParameters and LensParameter objects.

    mmlens::DistortionLayers distortion_layers;

    const uint8_t layer_count = distortion_layers.get_layer_count();
    std::cout << test_name << ": layer_count: " << static_cast<int>(layer_count)
              << std::endl;

    const uint8_t layer_num = 0;
    const int32_t frame = 0;
    mmlens::LensModelType lens_model_type =
        distortion_layers.layer_lens_model_type(layer_num);
    std::cout << test_name
              << ": lens_model_type: " << static_cast<int>(lens_model_type)
              << std::endl;

    mmlens::OptionParameters3deClassic option_lens_parameters =
        distortion_layers.layer_parameters_3de_classic(layer_num, frame);

    if (option_lens_parameters.exists) {
        const mmlens::Parameters3deClassic lens_parameters =
            option_lens_parameters.value;
        // TODO: Do something with the lens parameters.
    }

    rust::String debug_string = distortion_layers.as_string();
    std::cout << test_name << " debug_string: " << debug_string.c_str()
              << std::endl;

    rust::Str file_path = join_path(dir_path, file_name);
    std::cout << test_name << " reading: " << file_path << std::endl;
    distortion_layers = mmlens::read_lens_file(file_path);
    std::cout << test_name << " " << file_name << ": "
              << distortion_layers.as_string().c_str() << std::endl;

    return 0;
}
