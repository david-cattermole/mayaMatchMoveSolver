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

#include "test_d.h"

#include <mmimage/mmimage.h>

#include <algorithm>
#include <iostream>

#include "common.h"

namespace mmimg = mmimage;

bool test_d_image_write(const char *test_name, const size_t image_width,
                        const size_t image_height, rust::Str output_file_path) {
    auto meta_data = mmimg::ImageMetaData();
    auto exr_encoder = mmimg::ImageExrEncoder{
        mmimg::ExrCompression::kZIP1,
        mmimg::ExrPixelLayout{mmimg::ExrPixelLayoutMode::kScanLines, 0, 0},
        mmimg::ExrLineOrder::kIncreasing,
    };

    auto pixel_data = mmimg::ImagePixelDataRgbaF32();
    mmimg::create_image_rgba_f32(image_width, image_height, pixel_data);

    rust::Slice<mmimg::PixelRgbaF32> raw_data_mut = pixel_data.data_mut();
    const auto width = pixel_data.width();
    const auto height = pixel_data.height();
    for (auto row = 0; row < height; row++) {
        for (auto column = 0; column < width; column++) {
            const size_t index = (row * width) + column;

            const float x =
                static_cast<float>(column) / static_cast<float>(width - 1);
            const float y =
                static_cast<float>(row) / static_cast<float>(height - 1);

            mmimg::PixelRgbaF32 pixel{x, y, 0.0f, 0.0f};
            raw_data_mut[index] = pixel;
        }
    }

    std::cout << test_name << " output file path: " << output_file_path
              << std::endl;
    bool result = mmimg::image_write_pixels_exr_rgba_f32(
        output_file_path, exr_encoder, meta_data, pixel_data);
    std::cout << test_name << " written result: " << result << std::endl;
    if (!result) {
        return false;
    }

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

int test_d(const char *dir_path) {
    const auto test_name = "test_d:";

    auto out_path = join_path(dir_path, "test_identity_st_map.0001.out.exr");
    const auto out_file_path = rust::Str(out_path);

    size_t image_width = 2048;
    size_t image_height = 1556;
    bool ok =
        test_d_image_write(test_name, image_width, image_height, out_file_path);
    if (!ok) {
        return 1;
    }

    return 0;
}
