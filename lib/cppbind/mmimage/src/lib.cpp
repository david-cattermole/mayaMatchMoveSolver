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

#include <mmimage/lib.h>

#include <iostream>

std::ostream& operator<<(std::ostream& os,
                         const mmimage::OptionF32& option_f32) {
    os << option_f32.exists << '|' << option_f32.value;
    return os;
}

namespace mmimage {

bool image_read_metadata_exr(const rust::Str& file_path,
                             ImageMetaData& out_meta_data) {
    auto meta_data = out_meta_data.get_inner();

    bool result = shim_image_read_metadata_exr(file_path, meta_data);

    out_meta_data.set_inner(meta_data);
    return result;
}

bool image_read_pixels_exr_f32x4(const rust::Str& file_path,
                                 const bool vertical_flip,
                                 ImageMetaData& out_meta_data,
                                 ImagePixelBuffer& out_pixel_data) {
    auto pixel_data = out_pixel_data.get_inner();
    auto meta_data = out_meta_data.get_inner();

    bool result = shim_image_read_pixels_exr_f32x4(file_path, vertical_flip,
                                                   meta_data, pixel_data);

    out_pixel_data.set_inner(pixel_data);
    out_meta_data.set_inner(meta_data);
    return result;
}

bool image_write_pixels_exr_f32x4(const rust::Str& file_path,
                                  ImageExrEncoder exr_encoder,
                                  ImageMetaData& in_meta_data,
                                  ImagePixelBuffer& in_pixel_data) {
    auto inner_pixel_data = in_pixel_data.get_inner();
    auto inner_meta_data = in_meta_data.get_inner();

    bool result = shim_image_write_pixels_exr_f32x4(
        file_path, exr_encoder, inner_meta_data, inner_pixel_data);

    in_pixel_data.set_inner(inner_pixel_data);
    in_meta_data.set_inner(inner_meta_data);
    return result;
}

}  // namespace mmimage
