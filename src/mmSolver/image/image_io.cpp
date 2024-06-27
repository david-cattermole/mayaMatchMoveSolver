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

#include "image_io.h"

// Get M_PI constant
#define _USE_MATH_DEFINES
#include <cmath>

// STL
#include <cassert>
#include <cstdint>
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
#include <mmimage/lib.h>

#include "PixelDataType.h"
#include "mmSolver/mayahelper/maya_utils.h"
#include "mmSolver/render/shader/shader_utils.h"
#include "mmSolver/shape/constant_texture_data.h"
#include "mmSolver/utilities/number_utils.h"
#include "mmSolver/utilities/path_utils.h"

namespace mmsolver {
namespace image {

void *get_mimage_pixel_data(const MImage &image,
                            const PixelDataType pixel_data_type,
                            const uint32_t width, const uint32_t height,
                            const uint8_t num_channels,
                            uint8_t &out_bytes_per_channel,
                            MHWRender::MRasterFormat &out_texture_format) {
    const bool verbose = false;

    const uint32_t print_num_pixels = 8;
    void *pixel_data = nullptr;
    if (pixel_data_type == PixelDataType::kU8) {
        MMSOLVER_MAYA_VRB("mmsolver::image_io::get_mimage_pixel_data:"
                          << " pixel_data_type=PixelDataType::kU8");

        // 8-bit unsigned integers use 1 byte.
        out_bytes_per_channel = 1;

        const bool is_rgba = image.isRGBA();
        MMSOLVER_MAYA_VRB("mmsolver::image_io::get_mimage_pixel_data:"
                          << " is_rgba=" << is_rgba);
        if (is_rgba) {
            out_texture_format = MHWRender::kR8G8B8A8_UNORM;
        } else {
            out_texture_format = MHWRender::kB8G8R8A8;
        }

        unsigned char *pixels = image.pixels();

        if (verbose) {
            for (uint32_t row = 0; row <= print_num_pixels; row++) {
                const uint32_t index = row * num_channels;
                const uint32_t r = static_cast<uint32_t>(pixels[index + 0]);
                const uint32_t g = static_cast<uint32_t>(pixels[index + 1]);
                const uint32_t b = static_cast<uint32_t>(pixels[index + 2]);
                const uint32_t a = static_cast<uint32_t>(pixels[index + 3]);
                MMSOLVER_MAYA_VRB("mmsolver::image_io::get_mimage_pixel_data:"
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
        //                                                 num_channels);

        // mmcolorio::test_opencolorio(pixels, width, height,
        // num_channels);

        pixel_data = static_cast<void *>(pixels);
    } else if (pixel_data_type == PixelDataType::kF32) {
        MMSOLVER_MAYA_VRB("mmsolver::image_io::get_mimage_pixel_data:"
                          << " pixel_data_type=PixelDataType::kF32");

        // 32-bit floats use 4 bytes.
        out_bytes_per_channel = 4;

        out_texture_format = MHWRender::kR32G32B32A32_FLOAT;

        float *floatPixels = image.floatPixels();

        if (verbose) {
            for (uint32_t row = 0; row <= print_num_pixels; row++) {
                const uint32_t index = row * num_channels;
                const float r = floatPixels[index + 0];
                const float g = floatPixels[index + 1];
                const float b = floatPixels[index + 2];
                const float a = floatPixels[index + 3];
                MMSOLVER_MAYA_VRB("mmsolver::image_io::get_mimage_pixel_data:"
                                  << " row=" << row << " pixel=" << r << ", "
                                  << g << ", " << b << ", " << a);
            }
        }

        // mmcolorio::image_convert_srgb_to_linear_srgb_f32(
        //     floatPixels, width, height, num_channels);

        pixel_data = static_cast<void *>(floatPixels);
    } else {
        MMSOLVER_MAYA_ERR("mmsolver::image_io::get_mimage_pixel_data: "
                          << "Invalid pixel type is "
                          << static_cast<int>(pixel_data_type));
        return nullptr;
    }

    return pixel_data;
}

PixelDataType convert_mpixel_type_to_pixel_data_type(
    const MImage::MPixelType pixel_type) {
    PixelDataType pixel_data_type = PixelDataType::kUnknown;
    if (pixel_type == MImage::MPixelType::kByte) {
        pixel_data_type = PixelDataType::kU8;
    } else if (pixel_type == MImage::MPixelType::kFloat) {
        pixel_data_type = PixelDataType::kF32;
    } else {
        MMSOLVER_MAYA_WRN(
            "mmsolver::image_io::convert_mpixel_type_to_pixel_data_type: "
            "Invalid MImage::MPixelType value. "
            "value="
            << static_cast<int>(pixel_type));
    }
    return pixel_data_type;
}

MStatus read_with_maya_image(MImage &image, const MString &file_path,
                             const MImage::MPixelType pixel_type,
                             uint32_t &out_width, uint32_t &out_height,
                             uint8_t &out_num_channels,
                             uint8_t &out_bytes_per_channel,
                             MHWRender::MRasterFormat &out_texture_format,
                             PixelDataType &out_pixel_data_type,
                             void *&out_pixel_data) {
    const bool verbose = false;

    MStatus status = MStatus::kSuccess;

    status = image.readFromFile(file_path, pixel_type);
    CHECK_MSTATUS(status);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_WRN("mmsolver::image_io::read_with_maya_image:"
                          << " failed to read image \"" << file_path.asChar()
                          << "\".");
        return status;
    }

    image.getSize(out_width, out_height);
    MMSOLVER_MAYA_VRB("mmsolver::image_io::read_with_maya_image:"
                      << " width=" << out_width << " height=" << out_height);

    out_pixel_data_type = convert_mpixel_type_to_pixel_data_type(pixel_type);

    out_pixel_data = get_mimage_pixel_data(
        image, out_pixel_data_type, out_width, out_height, out_num_channels,
        out_bytes_per_channel, out_texture_format);

    return status;
}

MStatus read_exr_with_mmimage(MImage &image, const MString &file_path,
                              uint32_t &out_width, uint32_t &out_height,
                              uint8_t &out_num_channels,
                              uint8_t &out_bytes_per_channel,
                              MHWRender::MRasterFormat &out_texture_format,
                              PixelDataType &out_pixel_data_type,
                              void *&out_pixel_data) {
    const bool verbose = false;

    MStatus status = MStatus::kSuccess;

    auto pixel_buffer = mmimage::ImagePixelBuffer();
    auto meta_data = mmimage::ImageMetaData();

    const std::string input_file_path_string = file_path.asChar();
    const rust::Str input_file_path(input_file_path_string.c_str());

    // TODO: Support 3-channel RGB EXR images.
    bool read_ok = mmimage::image_read_pixels_exr_f32x4(
        input_file_path, meta_data, pixel_buffer);

    if (!read_ok) {
        MMSOLVER_MAYA_WRN("mmsolver::image_io::read_exr_with_mmimage:"
                          << " failed to read image \"" << file_path.asChar()
                          << "\".");
        return MStatus::kFailure;
    }

    size_t num_channels = pixel_buffer.num_channels();
    if ((num_channels != 3) && (num_channels != 4)) {
        MMSOLVER_MAYA_WRN("mmsolver::image_io::read_exr_with_mmimage:"
                          << " image has " << num_channels
                          << " which is supported; \"" << file_path.asChar()
                          << "\".");
        return MStatus::kFailure;
    }

    if (num_channels == 3) {
        out_texture_format = MHWRender::kR32G32B32_FLOAT;
    } else if (num_channels == 4) {
        out_texture_format = MHWRender::kR32G32B32A32_FLOAT;
    } else {
        MMSOLVER_MAYA_ERR("mmsolver::image_io::read_exr_with_mmimage:"
                          << " should never get here; \"" << file_path.asChar()
                          << "\".");
        return MStatus::kFailure;
    }

    out_width = pixel_buffer.image_width();
    out_height = pixel_buffer.image_height();
    out_num_channels = num_channels;

    // Other data types are unsupported right now.
    out_pixel_data_type = PixelDataType::kF32;
    out_bytes_per_channel = 4;  // f32 is 4-bytes per element.

    MMSOLVER_MAYA_VRB(
        "mmsolver::image_io::read_exr_with_mmimage:"
        << " width=" << out_width << " height=" << out_height
        << " num_channels=" << static_cast<int32_t>(out_num_channels)
        << " bytes_per_channel=" << static_cast<int32_t>(out_bytes_per_channel)
        << " pixel_data_type=" << static_cast<int32_t>(out_pixel_data_type)
        << " sizeof(mmimage::PixelF32x4)=" << sizeof(mmimage::PixelF32x4));

    const rust::Slice<const mmimage::PixelF32x4> slice =
        pixel_buffer.as_slice_f32x4();

    // TODO: Why does this need to be multiplied by 2? Shouldn't it be
    // 4?
    size_t pixel_data_byte_count = slice.size() * 2 * out_bytes_per_channel;

    MMSOLVER_MAYA_VRB("mmsolver::image_io::read_exr_with_mmimage:"
                      << " pixel_data_byte_count=" << pixel_data_byte_count);

    MMSOLVER_MAYA_VRB("mmsolver::image_io::read_exr_with_mmimage:"
                      << " slice.length()=" << slice.length());

    MMSOLVER_MAYA_VRB("mmsolver::image_io::read_exr_with_mmimage:"
                      << " slice.size()=" << slice.size());

    MMSOLVER_MAYA_VRB("mmsolver::image_io::read_exr_with_mmimage:"
                      << " requesting=" << pixel_data_byte_count << "B"
                      << " requesting="
                      << (static_cast<float>(pixel_data_byte_count) * 1e-6)
                      << "MB");

    bool ok = false;
    void *data = std::malloc(pixel_data_byte_count);
    MMSOLVER_MAYA_VRB("mmsolver::image_io::read_exr_with_mmimage:"
                      << " void *data=" << data);

    if (data) {
        ok = true;

        const bool is_vertically_flipped = true;
        if (is_vertically_flipped) {
            // The underlying EXR data is actually flipped vertically
            // compared to Maya's MImage output. We must flip this to
            // be consistent.
            //
            // TODO: Try to do this somewhere else, perhaps in the
            // shader, because that would probably be faster.
            const int8_t *src_ptr = (int8_t *)slice.data();
            int8_t *dst_ptr = reinterpret_cast<int8_t *>(data);
            const size_t line_count = out_height;  // * out_num_channels;
            const size_t line_byte_count = pixel_data_byte_count / line_count;
            MMSOLVER_MAYA_VRB(
                "mmsolver::image_io::read_exr_with_mmimage:"
                << " std::memcpy"
                << " src_ptr=" << reinterpret_cast<std::uintptr_t>(src_ptr)
                << " dst_ptr=" << reinterpret_cast<std::uintptr_t>(dst_ptr)
                << " line_count=" << line_count
                << " line_byte_count=" << line_byte_count
                << " pixel_data_byte_count=" << pixel_data_byte_count);
            for (size_t i = 0; i < line_count; i++) {
                const size_t reverse_i = (line_count - 1) - i;

                const size_t src_offset = reverse_i * line_byte_count;
                const size_t dst_offset = i * line_byte_count;

                const void *src_ptr_with_offset = src_ptr + src_offset;
                void *dst_ptr_with_offset = dst_ptr + dst_offset;

                std::memcpy(dst_ptr_with_offset, src_ptr_with_offset,
                            line_byte_count);
            }
        } else {
            // Make a copy of the underlying Rust allocated data. This is
            // a little wasteful because we need to allocate and copy new
            // memory, but it's much easier than coercing Rust-owned
            // memory across the FFI barrier.
            void *src_ptr = (void *)slice.data();
            MMSOLVER_MAYA_VRB("mmsolver::image_io::read_exr_with_mmimage:"
                              << " std::memcpy(data=" << data
                              << ", (void *)slice.data()=" << src_ptr
                              << ", pixel_data_byte_count="
                              << pixel_data_byte_count << ");");
            std::memcpy(data, src_ptr, pixel_data_byte_count);
        }

        out_pixel_data = data;
    } else {
        ok = false;
        out_pixel_data = nullptr;
        MMSOLVER_MAYA_ERR("mmsolver::image_io::read_exr_with_mmimage: "
                          << "Could not allocate pixel data!"
                          << " requested=" << pixel_data_byte_count << "B"
                          << " requested="
                          << (static_cast<float>(pixel_data_byte_count) * 1e-6)
                          << "MB");
    }

    MMSOLVER_MAYA_VRB("mmsolver::image_io::read_exr_with_mmimage:"
                      << " out_pixel_data=" << out_pixel_data);

    return status;
}

MStatus read_image_file(MImage &image, const MString &file_path,
                        uint32_t &out_width, uint32_t &out_height,
                        uint8_t &out_num_channels,
                        uint8_t &out_bytes_per_channel,
                        MHWRender::MRasterFormat &out_texture_format,
                        PixelDataType &out_pixel_data_type,
                        void *&out_pixel_data) {
    const bool verbose = false;
    MStatus status = MStatus::kSuccess;

    MMSOLVER_MAYA_VRB("mmsolver::image_io::read_image_file:"
                      << " file_path=" << file_path.asChar());

    // We assume the file extension is standard and common.
    // Non-standard file extensions will fail to use the expected
    // image reader.
    MString file_extension = "";
    int32_t dot_char_index = file_path.rindexW('.');
    if (dot_char_index >= 0) {
        file_extension =
            file_path.substringW(dot_char_index + 1, file_path.length());
        file_extension.toLowerCase();
    }

    MMSOLVER_MAYA_VRB("mmsolver::image_io::read_image_file:"
                      << " file_extension=" << file_extension.asChar());

    // BUG: The EXR reader is leaking memory and we don't know where,
    // so for now, lets disable the reader.
    const bool use_exr_reader = false;

    if ((file_extension == "exr") && use_exr_reader) {
        MMSOLVER_MAYA_VRB("mmsolver::image_io::read_image_file:"
                          << "read_exr_with_mmimage...");
        status = read_exr_with_mmimage(image, file_path, out_width, out_height,
                                       out_num_channels, out_bytes_per_channel,
                                       out_texture_format, out_pixel_data_type,
                                       out_pixel_data);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    } else {
        MMSOLVER_MAYA_VRB("mmsolver::image_io::read_image_file:"
                          << "read_with_maya_image...");

        // Maya always reads images as RGBA.
        out_num_channels = 4;

        // Maya is meant to be able to load pixels as float (kFloat),
        // but in my attempts it just fails, so lets hard-code to 8-bit.
        const MImage::MPixelType pixel_type = MImage::MPixelType::kByte;

        status = read_with_maya_image(image, file_path, pixel_type, out_width,
                                      out_height, out_num_channels,
                                      out_bytes_per_channel, out_texture_format,
                                      out_pixel_data_type, out_pixel_data);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

}  // namespace image
}  // namespace mmsolver
