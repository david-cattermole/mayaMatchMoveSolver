/*
 * Copyright (C) 2024 David Cattermole.
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

#ifndef MM_SOLVER_IMAGE_PIXEL_DATA_TYPE_H
#define MM_SOLVER_IMAGE_PIXEL_DATA_TYPE_H

// STL
#include <algorithm>
#include <list>
#include <string>
#include <unordered_map>

// Maya
#include <maya/MImage.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MTextureManager.h>

// MM Solver
#include <mmcore/lib.h>

#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace image {

enum class PixelDataType : uint8_t {
    kU8 = 0,
    kF32,

    // Always the second to last, so it's equal to the number of
    // options.
    kCount,

    // When the pixel data type is not initialized or invalid.
    kUnknown = 255,
};

static uint8_t convert_pixel_data_type_to_bytes_per_channel(
    PixelDataType pixel_data_type) {
    uint8_t bytes_per_channel = 0;
    if (pixel_data_type == PixelDataType::kU8) {
        // 8-bit unsigned integers use 1 byte.
        bytes_per_channel = 1;
    } else if (pixel_data_type == PixelDataType::kF32) {
        // 32-bit floats use 4 bytes.
        bytes_per_channel = 4;
    } else {
        bytes_per_channel = 0;
        MMSOLVER_MAYA_ERR(
            "mmsolver::image::convert_pixel_data_type_to_bytes_per_channel: "
            << "Invalid pixel type is " << static_cast<int>(pixel_data_type));
    }
    return bytes_per_channel;
}

static MHWRender::MRasterFormat convert_pixel_data_type_to_texture_format(
    const PixelDataType pixel_data_type) {
    if (pixel_data_type == PixelDataType::kU8) {
        // Assumes the 8-bit data is "RGBA".
        return MHWRender::kR8G8B8A8_UNORM;
    } else if (pixel_data_type == PixelDataType::kF32) {
        return MHWRender::kR32G32B32A32_FLOAT;
    }

    return MHWRender::MRasterFormat();
}

}  // namespace image
}  // namespace mmsolver

#endif  // MM_SOLVER_IMAGE_PIXEL_DATA_TYPE_H
