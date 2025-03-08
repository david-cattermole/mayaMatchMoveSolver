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

#ifndef MM_SOLVER_IMAGE_TEXTURE_DATA_H
#define MM_SOLVER_IMAGE_TEXTURE_DATA_H

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

// MM Solver Libs
#include <mmcore/lib.h>

// MM Solver
#include "PixelDataType.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace image {

struct TextureData {
    TextureData()
        : m_texture(nullptr)
        , m_width(0)
        , m_height(0)
        , m_num_channels(0)
        , m_pixel_data_type(PixelDataType::kUnknown){};

    TextureData(MTexture *texture, const uint32_t width, const uint32_t height,
                const uint8_t num_channels, const PixelDataType pixel_data_type)
        : m_texture(texture)
        , m_width(width)
        , m_height(height)
        , m_num_channels(num_channels)
        , m_pixel_data_type(pixel_data_type){};

    ~TextureData() = default;

    bool allocate_texture(MHWRender::MTextureManager *texture_manager,
                          void *pixel_data, const uint32_t width,
                          const uint32_t height, const uint8_t num_channels,
                          const PixelDataType pixel_data_type);
    void deallocate_texture(MHWRender::MTextureManager *texture_manager);

    bool is_valid() const {
        return (m_texture != nullptr) && (m_width != 0) && (m_height != 0) &&
               (m_num_channels != 0) &&
               (m_pixel_data_type != PixelDataType::kUnknown);
    };

    MTexture *texture() const { return m_texture; };
    uint32_t width() const { return m_width; }
    uint32_t height() const { return m_height; }
    uint8_t num_channels() const { return m_num_channels; }
    PixelDataType pixel_data_type() const { return m_pixel_data_type; }

    size_t byte_count() const {
        const uint8_t bytes_per_channel =
            convert_pixel_data_type_to_bytes_per_channel(m_pixel_data_type);
        return m_width * m_height * m_num_channels *
               static_cast<size_t>(bytes_per_channel);
    }

private:
    MTexture *m_texture;
    uint32_t m_width;
    uint32_t m_height;
    uint8_t m_num_channels;
    PixelDataType m_pixel_data_type;
};

}  // namespace image
}  // namespace mmsolver

#endif  // MM_SOLVER_IMAGE_TEXTURE_DATA_H
