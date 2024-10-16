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

#include "TextureData.h"

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>

// STL
#include <cassert>
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

#include "ImagePixelData.h"
#include "PixelDataType.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/shape/constant_texture_data.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/path_utils.h"

namespace mmsolver {
namespace image {

bool TextureData::allocate_texture(MHWRender::MTextureManager *texture_manager,
                                   void *pixel_data, const uint32_t width,
                                   const uint32_t height,
                                   const uint8_t num_channels,
                                   const PixelDataType pixel_data_type) {
    assert(texture_manager != nullptr);

    m_width = width;
    m_height = height;
    m_num_channels = num_channels;
    m_pixel_data_type = pixel_data_type;

    const uint8_t bytes_per_channel =
        convert_pixel_data_type_to_bytes_per_channel(pixel_data_type);
    const size_t pixel_data_byte_count = TextureData::byte_count();

    if (pixel_data_byte_count == 0) {
        MMSOLVER_MAYA_ERR("mmsolver::TextureData:allocate_pixels: "
                          << "Invalid image size for allocating pixel data!"
                          << " width=" << m_width << " height=" << m_height
                          << " num_channels=" << m_num_channels
                          << " pixel_data_type="
                          << static_cast<int>(m_pixel_data_type));
        return false;
    }

    bool ok = false;

    MHWRender::MTextureDescription texture_desc;
    texture_desc.setToDefault2DTexture();
    texture_desc.fWidth = m_width;
    texture_desc.fHeight = m_height;
    texture_desc.fDepth = 1;

    texture_desc.fMipmaps = 1;
    texture_desc.fArraySlices = 1;
    texture_desc.fTextureType = MHWRender::kImage2D;
    texture_desc.fFormat =
        convert_pixel_data_type_to_texture_format(m_pixel_data_type);

    texture_desc.fBytesPerRow = m_num_channels * bytes_per_channel * m_width;
    texture_desc.fBytesPerSlice = texture_desc.fBytesPerRow * m_height;

    // No need for MIP-maps.
    const bool generate_mip_maps = false;

    // If the texture name provided is an empty string then the
    // texture will not be cached as part of the internal texture
    // caching system. Thus each such call to this method will
    // create a new texture.

    // Pre-allocated empty string to be re-used inside the class, to
    // avoid reallocations.
    const MString g_empty_string;

    MTexture *new_texture = texture_manager->acquireTexture(
        g_empty_string, texture_desc, pixel_data, generate_mip_maps);
    if (new_texture) {
        m_texture = new_texture;
        ok = true;
    } else {
        ok = false;
        MMSOLVER_MAYA_ERR("mmsolver::TextureData:allocate_texture: "
                          << "Could not acquire texture!"
                          << " requested=" << pixel_data_byte_count << "B"
                          << " requested="
                          << (static_cast<float>(pixel_data_byte_count) * 1e-6)
                          << "MB");
    }

    return ok;
}

void TextureData::deallocate_texture(
    MHWRender::MTextureManager *texture_manager) {
    assert(texture_manager != nullptr);
    texture_manager->releaseTexture(m_texture);
}

}  // namespace image
}  // namespace mmsolver
