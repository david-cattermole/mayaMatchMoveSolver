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

#include "test_a.h"

#include <mmimage/mmimage.h>

#include <algorithm>
#include <iostream>

#include "common.h"

namespace mmimg = mmimage;

bool test_a_image_read(const char *test_name, rust::Str file_path) {
    auto meta_data = mmimg::ImageMetaData();
    auto pixel_buffer = mmimg::ImagePixelBuffer();

    bool result =
        mmimg::image_read_pixels_exr_f32x4(file_path, meta_data, pixel_buffer);
    std::cout << test_name << " image file path: " << file_path
              << " image read result: " << static_cast<uint32_t>(result)
              << std::endl
              << test_name << " image width: " << pixel_buffer.image_width()
              << " image height: " << pixel_buffer.image_height() << std::endl;

    rust::Slice<mmimg::PixelF32x4> raw_data_mut =
        pixel_buffer.as_slice_f32x4_mut();
    const rust::Slice<const mmimg::PixelF32x4> raw_data =
        pixel_buffer.as_slice_f32x4();
    const auto max_rows = std::min<size_t>(pixel_buffer.image_height(), 1);
    const auto max_columns = std::min<size_t>(pixel_buffer.image_width(), 8);
    for (int32_t row = 0; row < max_rows; row++) {
        for (int32_t column = 0; column < max_columns; column++) {
            size_t index = (row * pixel_buffer.image_width()) + column;

            mmimg::PixelF32x4 pixel = raw_data[index];
            pixel.r *= 2.0f;
            pixel.g *= 2.0f;
            pixel.b *= 2.0f;
            pixel.a *= 2.0f;
            raw_data_mut[index] = pixel;

            pixel = raw_data[index];
            std::cout << test_name << " " << index << " row: " << row
                      << " column: " << column << " pixel: r=" << pixel.r
                      << ", g=" << pixel.g << ", b=" << pixel.b
                      << ", a=" << pixel.a << std::endl;
        }
    }

    auto attr_name = rust::Str("camera");
    uint8_t type_index = meta_data.get_named_attribute_type_index(attr_name);
    bool has_attr = meta_data.has_named_attribute(attr_name);

    std::cout << test_name << " " << attr_name
              << " exists: " << static_cast<uint32_t>(has_attr)
              << " type index: " << static_cast<uint32_t>(type_index)
              << std::endl;

    test_print_metadata_named_attributes(test_name, meta_data);
    test_print_metadata_fields(test_name, meta_data);

    rust::String debug_string = meta_data.as_string();
    std::cout << test_name << " debug_string: " << debug_string.c_str()
              << std::endl;

    return result;
}

int test_a(const char *test_name, const char *dir_path) {
    const std::string path_string1 =
        join_path(dir_path, "/Beachball/singlepart.0001", ".exr");
    const std::string path_string2 =
        join_path(dir_path, "/ScanLines/Tree", ".exr");
    const rust::Str file_path1(path_string1.c_str());
    const rust::Str file_path2(path_string2.c_str());

    bool ok = test_a_image_read(test_name, file_path1);
    if (!ok) {
        return 1;
    }

    ok = test_a_image_read(test_name, file_path2);
    if (!ok) {
        return 1;
    }

    return 0;
}
