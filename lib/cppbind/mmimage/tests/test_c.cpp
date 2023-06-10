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

#include "test_c.h"

#include <mmimage/mmimage.h>

#include <algorithm>
#include <iostream>

#include "common.h"

namespace mmimg = mmimage;

bool test_c_image_write(const char *test_name, rust::Str input_file_path,
                        rust::Str output_file_path) {
    auto meta_data = mmimg::ImageMetaData();
    auto pixel_data = mmimg::ImagePixelDataRgbaF32();
    auto exr_encoder = mmimg::ImageExrEncoder{
        mmimg::ExrCompression::kZIP1,
        mmimg::ExrPixelLayout{mmimg::ExrPixelLayoutMode::kScanLines, 0, 0},
        mmimg::ExrLineOrder::kIncreasing,
    };

    // TODO: Get the EXR Encoding when reading the file.
    bool result = mmimg::image_read_pixels_exr_rgba_f32(input_file_path,
                                                        meta_data, pixel_data);
    std::cout << test_name << " image file path: " << input_file_path
              << " image read result: " << static_cast<uint32_t>(result)
              << std::endl
              << test_name << " image width: " << pixel_data.width()
              << " image height: " << pixel_data.height() << std::endl;
    if (!result) {
        return result;
    }

    rust::String debug_string = meta_data.as_string();
    std::cout << test_name << " debug_string: " << debug_string.c_str()
              << std::endl;

    rust::Slice<mmimg::PixelRgbaF32> raw_data_mut = pixel_data.data_mut();
    const rust::Slice<const mmimg::PixelRgbaF32> raw_data = pixel_data.data();
    for (int32_t row = 0; row < pixel_data.height(); row++) {
        for (int32_t column = 0; column < pixel_data.width(); column++) {
            size_t index = (row * pixel_data.width()) + column;

            mmimg::PixelRgbaF32 pixel = raw_data[index];
            pixel.r *= 2.0f;
            pixel.g *= 2.0f;
            pixel.b *= 2.0f;
            pixel.a *= 2.0f;
            raw_data_mut[index] = pixel;

            pixel = raw_data[index];
        }
    }

    std::cout << test_name << " output file path: " << output_file_path
              << std::endl;
    result = mmimg::image_write_pixels_exr_rgba_f32(
        output_file_path, exr_encoder, meta_data, pixel_data);

    bool reread_result = mmimg::image_read_pixels_exr_rgba_f32(
        output_file_path, meta_data, pixel_data);
    std::cout << test_name << " image file path: " << output_file_path
              << " image read result: " << static_cast<uint32_t>(reread_result)
              << std::endl
              << test_name << " image width: " << pixel_data.width()
              << " image height: " << pixel_data.height() << std::endl;

    test_print_metadata_named_attributes(test_name, meta_data);
    test_print_metadata_fields(test_name, meta_data);

    rust::String reread_debug_string = meta_data.as_string();
    std::cout << test_name << " debug_string: " << reread_debug_string.c_str()
              << std::endl;

    return result;
}

int test_c(const char *dir_path) {
    const auto test_name = "test_c:";

    auto path_string1 =
        join_path(dir_path, "/Beachball/singlepart.0001", ".exr");
    auto path_string2 = join_path(dir_path, "/ScanLines/Tree", ".exr");
    auto path_out_string1 =
        join_path(dir_path, "/Beachball/singlepart.0001", ".out.exr");
    auto path_out_string2 = join_path(dir_path, "/ScanLines/Tree", ".out.exr");
    const auto file_path1 = rust::Str(path_string1);
    const auto file_path2 = rust::Str(path_string2);
    const auto file_path_out1 = rust::Str(path_out_string1);
    const auto file_path_out2 = rust::Str(path_out_string2);

    bool ok = false;
    ok = test_c_image_write(test_name, file_path1, file_path_out1);
    if (!ok) {
        return 1;
    }

    ok = test_c_image_write(test_name, file_path2, file_path_out2);
    if (!ok) {
        return 1;
    }

    return 0;
}
