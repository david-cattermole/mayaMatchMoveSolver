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

#ifndef MM_IMAGE_LIB_H
#define MM_IMAGE_LIB_H

#include <memory>
#include <string>

#include "_cxx.h"
#include "_cxxbridge.h"
#include "_symbol_export.h"
#include "_types.h"
#include "imagemetadata.h"
#include "imagepixelbuffer.h"
#include "imagepixeldata.h"

std::ostream& operator<<(std::ostream& os,
                         const mmimage::OptionF32& option_f32);

namespace mmimage {

bool image_read_metadata_exr(const rust::Str& file_path,
                             ImageMetaData& out_meta_data);

bool image_read_pixels_exr_f32x4(const rust::Str& file_path,
                                 const bool vertical_flip,
                                 ImageMetaData& out_meta_data,
                                 ImagePixelBuffer& out_pixel_data);

bool image_write_pixels_exr_f32x4(const rust::Str& file_path,
                                  ImageExrEncoder exr_encoder,
                                  ImageMetaData& in_meta_data,
                                  ImagePixelBuffer& in_pixel_data);

}  // namespace mmimage

#endif  // MM_IMAGE_LIB_H
