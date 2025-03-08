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

#include "ImagePixelData.h"

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>

// STL
#include <cstdlib>
#include <cstring>
#include <string>

// Maya
#include <maya/MImage.h>
#include <maya/MString.h>

// Maya Viewport 2.0
#include <maya/MTextureManager.h>

// MM Solver
#include <mmcore/lib.h>

#include "PixelDataType.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/shape/constant_texture_data.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/path_utils.h"

namespace mmsolver {
namespace image {

bool ImagePixelData::allocate_pixels(const uint32_t width,
                                     const uint32_t height,
                                     const uint8_t num_channels,
                                     const PixelDataType pixel_data_type) {
    m_width = width;
    m_height = height;
    m_num_channels = num_channels;
    m_pixel_data_type = pixel_data_type;

    const size_t pixel_data_byte_count = ImagePixelData::byte_count();

    if (pixel_data_byte_count == 0) {
        MMSOLVER_MAYA_ERR("mmsolver::ImagePixelData:allocate_pixels: "
                          << "Invalid image size for allocating pixel data!"
                          << " width=" << m_width << " height=" << m_height
                          << " num_channels=" << m_num_channels
                          << " pixel_data_type="
                          << static_cast<int>(m_pixel_data_type));
        return false;
    }

    bool ok = false;
    void *data = std::malloc(pixel_data_byte_count);
    if (data) {
        m_pixel_data = data;
        ok = true;
    } else {
        ok = false;
        MMSOLVER_MAYA_ERR("mmsolver::ImagePixelData:allocate_pixels: "
                          << "Could not allocate pixel data!"
                          << " requested=" << pixel_data_byte_count << "B"
                          << " requested="
                          << (static_cast<float>(pixel_data_byte_count) * 1e-6)
                          << "MB");
    }

    return ok;
}

void ImagePixelData::deallocate_pixels() { std::free(m_pixel_data); }

}  // namespace image
}  // namespace mmsolver
