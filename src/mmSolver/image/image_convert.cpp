/*
 * Copyright (C) 2022, 2024 David Cattermole.
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

#include "image_convert.h"

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
#include <maya/MStringArray.h>

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

using mmmath::clamp;
using mmmath::fast_pow;

MStatus guess_output_format_pixel_type(const MString &in_output_format,
                                       MImage::MPixelType &out_pixel_type) {
    MStatus status = MStatus::kSuccess;

    MString output_format(in_output_format);
    output_format.toLowerCase();

    if (output_format == MString("exr")) {
        out_pixel_type = MImage::kFloat;
    } else if (output_format == MString("hdr")) {
        out_pixel_type = MImage::kFloat;
    } else {
        out_pixel_type = MImage::kByte;
    }

    return status;
}

MStatus guess_file_path_pixel_type(const MString &in_file_path,
                                   MImage::MPixelType &out_pixel_type) {
    MStatus status = MStatus::kSuccess;

    MString file_path(in_file_path);
    file_path.toLowerCase();

    MStringArray splits;
    file_path.split('.', splits);
    MString file_extension = splits[splits.length() - 1];

    guess_output_format_pixel_type(file_extension, out_pixel_type);

    return status;
}

MStatus resize_image(MImage &image, const double resize_scale) {
    MImage::MPixelType pixel_type = image.pixelType();
    if (pixel_type != MImage::kByte) {
        MMSOLVER_MAYA_WRN(
            "mmConvertImage: "
            << "Maya does not support resizing floating-point pixels.");
    }

    uint32_t src_width = 2;
    uint32_t src_height = 2;
    MStatus status = image.getSize(src_width, src_height);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    auto dst_width_float = static_cast<double>(src_width) * resize_scale;
    auto dst_height_float = static_cast<double>(src_height) * resize_scale;
    auto dst_width = static_cast<uint32_t>(dst_width_float);
    auto dst_height = static_cast<uint32_t>(dst_height_float);
    if ((src_width != dst_width) && (src_height != dst_height)) {
        const auto preserve_aspect_ratio = true;

        // TODO: Replace this with a hand-written resize function. The
        // MImage.resize() method appears to have a bug whereby the
        // resized image is offset by +1 pixel in X and Y.
        //
        // If we can use Rust, then we have these easily available,
        // and they appear to do exactly what we need, very quickly:
        // https://crates.io/crates/fast_image_resize
        // https://crates.io/crates/resize
        //
        // NOTE: MImage.resize() only works on 8-bit images, not
        // floating point.
        status = image.resize(dst_width, dst_height, preserve_aspect_ratio);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

// This tool should be able to convert an image sequence with one
// image format to another.
//
// Mostly this tool is intended to convert non-native image formats to
// Maya IFF for increased speed.
MStatus convert_image(const MString &src_file_path,
                      const MString &dst_file_path,
                      // Common output formats include: als, bmp, cin,
                      // gif, jpg, rla, sgi, tga, tif, iff.  "iff" is
                      // default.
                      const MString &dst_output_format,
                      const double resize_scale) {
    if (src_file_path == dst_file_path) {
        MMSOLVER_MAYA_ERR("mmConvertImage: "
                          << "Cannot have source and destination as same path: "
                          << src_file_path.asChar());
        CHECK_MSTATUS_AND_RETURN_IT(MS::kFailure);
    }

    auto image = MImage();
    // kUnknown attempts to load the native pixel type.
    auto src_pixel_type = MImage::kUnknown;
    MStatus status = image.readFromFile(
        src_file_path,
        src_pixel_type  // The desired pixel format is unknown.
    );
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_ERR("mmConvertImage: "
                          << "Image file path could not be read: "
                          << src_file_path.asChar());
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }
    src_pixel_type = image.pixelType();
    const bool src_is_rgba = image.isRGBA();

    // Maya always stores 4 channels (according to the
    // documentation).
    const auto channels = 4;

    // Guess the Pixel Type for the output image.
    MImage::MPixelType dst_pixel_type;
    MImage::MPixelType format_pixel_type;
    status =
        guess_output_format_pixel_type(dst_output_format, format_pixel_type);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    status = guess_file_path_pixel_type(dst_file_path, dst_pixel_type);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    if (format_pixel_type != dst_pixel_type) {
        MMSOLVER_MAYA_WRN(
            "mmConvertImage: "
            << "The destination file extension and output format seem "
               "to contradict each other. file path: "
            << dst_file_path.asChar() << " output format: \""
            << dst_output_format.asChar() << "\"");
    }

    if (src_pixel_type == dst_pixel_type) {
        // Try to resize. We can only resize kByte - Maya is limited
        // with the pixel types it can resize.
        if (src_pixel_type == MImage::kByte) {
            status = resize_image(image, resize_scale);
            if (status != MS::kSuccess) {
                MMSOLVER_MAYA_ERR("mmConvertImage: "
                                  << "Failed to resize image file: "
                                  << src_file_path.asChar());
                return status;
            }
        }

        // No conversion is needed. We write out the 8-bit image
        // directly.
        status = image.writeToFile(dst_file_path, dst_output_format);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_ERR("mmConvertImage: "
                              << "Failed to write image file: "
                              << dst_file_path.asChar() << " output format: \""
                              << dst_output_format.asChar() << "\"");
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    } else {
        // Convert 32-bit to 8-bit integer. We assume the image
        // has not been resized yet.
        if (image.pixelType() == MImage::kByte) {
            status = MS::kFailure;
            MMSOLVER_MAYA_ERR("mmConvertImage: "
                              << "Failed to write image file: "
                              << dst_file_path.asChar() << " output format: \""
                              << dst_output_format.asChar() << "\"");
            return status;
        }

        // Do gamma correction before converting.
        uint32_t image_width = 2;
        uint32_t image_height = 2;
        status = image.getSize(image_width, image_height);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        // Get exponent based on if we are converting to/from floating
        // point or not. Make (linear color space) pixels brighter.
        const float gamma = 2.2F;
        float exponent = 1.0F / gamma;

        // TODO: Use the OpenColorIO library to change the
        // color space for an 8-bit file format.

        // Make sure we do our color management with floating point
        // numbers, to avoid loss of detail. This does not do anything
        // if the pixel format is already MImage::kFloat.
        const float *float_pixels = image.floatPixels();
        if (float_pixels == nullptr) {
            // The data pointer should be valid because we have
            // already read and operated on the pixels, so it seems
            // very wrong that the data wouldn't be valid.
            status = MS::kFailure;
            MMSOLVER_MAYA_ERR("mmConvertImage: "
                              << "Failed to get floating point pixel data: "
                              << src_file_path.asChar());
            return status;
        }

        MImage out_image;
        out_image.create(image_width, image_height, channels, MImage::kByte);
        unsigned char *pixels = out_image.pixels();

        // Apply gamma correction.
        for (auto y = 0; y < image_height; ++y) {
            for (auto x = 0; x < image_width; ++x) {
                auto index = (y * image_width * channels) + (x * channels);
                auto r =
                    clamp(fast_pow(float_pixels[index + 0], exponent) * 255.0F,
                          0.0, 255.0);
                auto g =
                    clamp(fast_pow(float_pixels[index + 1], exponent) * 255.0F,
                          0.0, 255.0);
                auto b =
                    clamp(fast_pow(float_pixels[index + 2], exponent) * 255.0F,
                          0.0, 255.0);
                auto a = clamp(float_pixels[index + 3] * 255.0F, 0.0, 255.0);
                pixels[index + 0] = static_cast<unsigned char>(r);
                pixels[index + 1] = static_cast<unsigned char>(g);
                pixels[index + 2] = static_cast<unsigned char>(b);
                // Alpha does not need to be gamma corrected.
                pixels[index + 3] = static_cast<unsigned char>(a);
            }
        }
        out_image.setRGBA(true);

        // Try to resize. We can only resize kByte - Maya is
        // limited with the pixel types it can resize.
        status = resize_image(out_image, resize_scale);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_ERR("mmConvertImage: "
                              << "Failed to resize image file: "
                              << src_file_path.asChar());
            return status;
        }

        status = out_image.writeToFile(dst_file_path, dst_output_format);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_ERR("mmConvertImage: "
                              << "Failed to write image file: "
                              << dst_file_path.asChar() << " output format: \""
                              << dst_output_format.asChar() << "\"");
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }
    return status;
}

}  // namespace image
}  // namespace mmsolver
