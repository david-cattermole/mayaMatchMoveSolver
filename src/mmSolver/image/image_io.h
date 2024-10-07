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

#ifndef MM_SOLVER_IMAGE_IMAGE_IO_H
#define MM_SOLVER_IMAGE_IMAGE_IO_H

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
#include <mmimage/lib.h>

#include "PixelDataType.h"
#include "mmSolver/utilities/debug_utils.h"

namespace mmsolver {
namespace image {

MStatus read_image_file(MImage &maya_mimage,
                        mmimage::ImagePixelBuffer &pixel_buffer,
                        mmimage::ImageMetaData &meta_data,
                        const MString &file_path, uint32_t &out_width,
                        uint32_t &out_height, uint8_t &out_num_channels,
                        uint8_t &out_bytes_per_channel,
                        MHWRender::MRasterFormat &out_texture_format,
                        PixelDataType &out_pixel_data_type,
                        void *&out_pixel_data);

}  // namespace image
}  // namespace mmsolver

#endif  // MM_SOLVER_IMAGE_IMAGE_IO_H
