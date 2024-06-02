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

#include "ImageCache.h"

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
#include <mmcolorio/lib.h>
#include <mmcore/lib.h>

#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/shape/constant_texture_data.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/path_utils.h"

namespace mmsolver {

void *get_mimage_pixel_data(const MImage &image,
                            const CachePixelDataType pixel_data_type,
                            const uint32_t width, const uint32_t height,
                            const uint8_t number_of_channels,
                            uint8_t &out_bytes_per_channel,
                            MHWRender::MRasterFormat &out_texture_format) {
    const bool verbose = false;

    const uint32_t print_num_pixels = 8;
    void *pixel_data = nullptr;
    if (pixel_data_type == CachePixelDataType::kU8) {
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                          << " pixel_data_type=CachePixelDataType::kU8");

        // 8-bit unsigned integers use 1 byte.
        out_bytes_per_channel = 1;

        const bool is_rgba = image.isRGBA();
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                          << " is_rgba=" << is_rgba);
        if (is_rgba) {
            out_texture_format = MHWRender::kR8G8B8A8_UNORM;
        } else {
            out_texture_format = MHWRender::kB8G8R8A8;
        }

        unsigned char *pixels = image.pixels();

        if (verbose) {
            for (uint32_t row = 0; row <= print_num_pixels; row++) {
                const uint32_t index = row * number_of_channels;
                const uint32_t r = static_cast<uint32_t>(pixels[index + 0]);
                const uint32_t g = static_cast<uint32_t>(pixels[index + 1]);
                const uint32_t b = static_cast<uint32_t>(pixels[index + 2]);
                const uint32_t a = static_cast<uint32_t>(pixels[index + 3]);
                MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                                  << " row=" << row << " pixel=" << r << ", "
                                  << g << ", " << b << ", " << a);
            }
        }

        // TODO: Allow giving the explicit input and output color
        // space names.
        //
        // TODO: Allow outputting 32-bit/16-bit float pixel data, to
        // ensure the plate doesn't get quantize.
        //
        // mmcolorio::image_convert_srgb_to_linear_srgb_u8(pixels, width,
        // height,
        //                                                 number_of_channels);

        // mmcolorio::test_opencolorio(pixels, width, height,
        // number_of_channels);

        pixel_data = static_cast<void *>(pixels);
    } else if (pixel_data_type == CachePixelDataType::kF32) {
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                          << " pixel_data_type=CachePixelDataType::kF32");

        // 32-bit floats use 4 bytes.
        out_bytes_per_channel = 4;

        out_texture_format = MHWRender::kR32G32B32A32_FLOAT;

        float *floatPixels = image.floatPixels();

        if (verbose) {
            for (uint32_t row = 0; row <= print_num_pixels; row++) {
                const uint32_t index = row * number_of_channels;
                const float r = floatPixels[index + 0];
                const float g = floatPixels[index + 1];
                const float b = floatPixels[index + 2];
                const float a = floatPixels[index + 3];
                MMSOLVER_MAYA_VRB("mmsolver::ImageCache: get_mimage_pixel_data:"
                                  << " row=" << row << " pixel=" << r << ", "
                                  << g << ", " << b << ", " << a);
            }
        }

        // mmcolorio::image_convert_srgb_to_linear_srgb_f32(
        //     floatPixels, width, height, number_of_channels);

        pixel_data = static_cast<void *>(floatPixels);
    } else {
        MMSOLVER_MAYA_ERR("mmsolver::ImageCache: get_mimage_pixel_data: "
                          << "Invalid pixel type is "
                          << static_cast<int>(pixel_data_type));
        return nullptr;
    }

    return pixel_data;
}

CachePixelDataType convert_mpixel_type_to_pixel_data_type(
    MImage::MPixelType pixel_type) {
    CachePixelDataType pixel_data_type = CachePixelDataType::kUnknown;
    if (pixel_type == MImage::MPixelType::kByte) {
        pixel_data_type = CachePixelDataType::kU8;
    } else if (pixel_type == MImage::MPixelType::kFloat) {
        pixel_data_type = CachePixelDataType::kF32;
    } else {
        MMSOLVER_MAYA_WRN(
            "mmsolver::ImageCache: convert_mpixel_type_to_pixel_data_type: "
            "Invalid MImage::MPixelType value.");
    }
    return pixel_data_type;
}

MStatus read_with_mimage(MImage &image, MString &file_path,
                         const MImage::MPixelType pixel_type,
                         uint32_t &out_width, uint32_t &out_height,
                         uint8_t &out_number_of_channels,
                         uint8_t &out_bytes_per_channel,
                         MHWRender::MRasterFormat &out_texture_format,
                         CachePixelDataType &out_pixel_data_type,
                         void *&out_pixel_data) {
    const bool verbose = false;

    MStatus status = MStatus::kSuccess;

    // TODO: This code can be changed to whatever reading function
    // that reads the input file path.
    status = image.readFromFile(file_path, pixel_type);
    CHECK_MSTATUS(status);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_WRN("mmsolver::ImageCache: read_with_mimage:"
                          << " failed to read image \"" << file_path.asChar()
                          << "\".");
        return status;
    }

    image.getSize(out_width, out_height);
    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_with_mimage:"
                      << " width=" << out_width << " height=" << out_height);

    out_pixel_data_type = convert_mpixel_type_to_pixel_data_type(pixel_type);

    out_pixel_data = get_mimage_pixel_data(
        image, out_pixel_data_type, out_width, out_height,
        out_number_of_channels, out_bytes_per_channel, out_texture_format);

    return status;
}

MTexture *read_image_file(MHWRender::MTextureManager *texture_manager,
                          ImageCache &image_cache, MImage &temp_image,
                          const MString &file_path,
                          const MImage::MPixelType pixel_type,
                          const bool do_texture_update) {
    assert(texture_manager != nullptr);

    const bool verbose = false;
    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file:"
                      << " file_path=" << file_path.asChar());

    MString resolved_file_path = file_path;
    MStatus status = mmpath::resolve_input_file_path(resolved_file_path);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file:"
                          << " file does not exist \""
                          << resolved_file_path.asChar() << "\".");
        return nullptr;
    }

    std::string key = std::string(resolved_file_path.asChar());
    MTexture *texture = image_cache.gpu_find(key);

    MMSOLVER_MAYA_VRB(
        "mmsolver::ImageCache: read_image_file: findTexture: " << texture);
    MMSOLVER_MAYA_VRB(
        "mmsolver::ImageCache: read_image_file: do_texture_update="
        << do_texture_update);
    if (texture && (do_texture_update == false)) {
        MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file DONE1:"
                          << " texture=" << texture);
        return texture;
    }

    // TODO: We should test if the file exists, then cache
    // result. This avoids us having to check the disk each time we
    // hit a frame that is outside the frame range of the image
    // sequence. This would mean that we would then need to be able to
    // flush that cached result - for example if the image sequence
    // changes. Alternatively, we could could pre-cache the file path
    // existence as soon as the user changes the file path. Another
    // approach would be to expose a Maya command that would allow
    // Python user code to add the list of valid images into the
    // cache.

    CacheImagePixelData image_pixel_data = image_cache.cpu_find(key);

    uint32_t width = 0;
    uint32_t height = 0;
    uint8_t number_of_channels = 4;
    uint8_t bytes_per_channel = 0;
    MHWRender::MRasterFormat texture_format;
    CachePixelDataType pixel_data_type = CachePixelDataType::kUnknown;
    void *maya_owned_pixel_data = nullptr;

    const bool image_pixel_data_valid = image_pixel_data.is_valid();
    if (image_pixel_data_valid) {
        maya_owned_pixel_data = image_pixel_data.pixel_data();
        width = image_pixel_data.width();
        height = image_pixel_data.height();
        number_of_channels = image_pixel_data.num_channels();
        pixel_data_type = image_pixel_data.pixel_data_type();
        bytes_per_channel =
            convert_pixel_data_type_to_bytes_per_channel(pixel_data_type);

        if (pixel_data_type == CachePixelDataType::kU8) {
            // Assumes the 8-bit data is "RGBA".
            texture_format = MHWRender::kR8G8B8A8_UNORM;
        } else if (pixel_data_type == CachePixelDataType::kF32) {
            texture_format = MHWRender::kR32G32B32A32_FLOAT;
        }

    } else {
        // TODO: This code can be changed to whatever reading function
        // that reads the input file path.

        status = read_with_mimage(temp_image, resolved_file_path, pixel_type,
                                  width, height, number_of_channels,
                                  bytes_per_channel, texture_format,
                                  pixel_data_type, maya_owned_pixel_data);
        if (status != MS::kSuccess) {
            return nullptr;
        }

        // TODO: any image manipulations required can be done here.
        // TODO: Apply colour correction via OIIO.
        // // image.verticalFlip();
    }

    if (!maya_owned_pixel_data) {
        MMSOLVER_MAYA_ERR("mmsolver::ImageCache: read_image_file: "
                          << "Invalid pixel data!");
        return nullptr;
    }

    CacheImagePixelData gpu_image_pixel_data =
        CacheImagePixelData(static_cast<void *>(maya_owned_pixel_data), width,
                            height, number_of_channels, pixel_data_type);

    texture =
        image_cache.gpu_insert(texture_manager, key, gpu_image_pixel_data);
    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file: "
                      << "gpu_inserted=" << texture);

    // Duplicate the Maya-owned pixel data for our image cache.
    const size_t pixel_data_byte_count =
        width * height * number_of_channels * bytes_per_channel;
    image_pixel_data = CacheImagePixelData();
    const bool allocated_ok = image_pixel_data.allocate_pixels(
        width, height, number_of_channels, pixel_data_type);
    if (allocated_ok == false) {
        MMSOLVER_MAYA_ERR("mmsolver::ImageCache: read_image_file: "
                          << "Could not allocate pixel data!");
        return nullptr;
    }
    assert(image_pixel_data.is_valid() == true);
    assert(image_pixel_data.byte_count() == pixel_data_byte_count);
    std::memcpy(image_pixel_data.pixel_data(), maya_owned_pixel_data,
                pixel_data_byte_count);

    const bool cpu_inserted = image_cache.cpu_insert(key, image_pixel_data);
    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file: "
                      << "cpu_inserted=" << cpu_inserted);

    MMSOLVER_MAYA_VRB("mmsolver::ImageCache: read_image_file DONE2:"
                      << " texture=" << texture);

    return texture;
}

}  // namespace mmsolver
