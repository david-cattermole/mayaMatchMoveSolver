/*
 * Copyright (C) 2022 David Cattermole.
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
 * Command for running mmConvertImage.
 *
 * This tool should be able to convert an image sequence with one
 * image format to another.
 *
 * Mostly this tool is intended to convert non-native image formats to
 * Maya IFF for increased speed.
 *
 * Along the way, we could offer the option to down-res or resize the
 * image down, to generate a fast reading, low-memory representation
 * of the image sequence.
 *
 * # Example Python code:
 * src = 'sourceimages/stA/stA.#.jpg'
 * dst = 'sourceimages/stA_CONVERT.#.iff'
 * maya.cmds.mmConvertImage(
 *     source=src,
 *     destination=dst,
 *     sourceFrameStart=0,
 *     sourceFrameEnd=94,
 *     sourceFramePadding=4,
 *     destinationOutputFormat='iff',
 *     destinationFrameStart=0,
 *     destinationFramePadding=4,
 *     resizeScale=1.0)
 *
 */

#include "MMConvertImageCmd.h"

// STL
#include <algorithm>
#include <vector>

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MFileObject.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MImage.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// MM Solver
#include "mmSolver/core/mmmath.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

using mmmath::clamp;
using mmmath::fast_pow;

// For an image sequence the 'file_path' should contain at least one
// character '#', which will be replaced with the 'frame_number', with
// a padding width of 'frame_padding'.
MStatus expand_file_path_with_frame_number(const MString &file_path,
                                           uint32_t frame_padding,
                                           uint32_t frame_number,
                                           MString &out_file_path) {
    MStatus status = MStatus::kSuccess;

    auto first_char = file_path.index('#');
    if (first_char == -1) {
        // Not an image sequence.
        out_file_path = file_path;
        return status;
    }

    auto last_char = file_path.rindex('#');
    if (last_char == -1) {
        // Not an image sequence.
        out_file_path = file_path;
        return status;
    }

    MString start = file_path.substring(0, first_char - 1);
    MString end = file_path.substring(last_char + 1, file_path.length() - 1);

    std::string number_as_string = mmstring::numberToString(frame_number);

    int extra_zeros =
        std::max(0, static_cast<int>(frame_padding) -
                        static_cast<int>(number_as_string.size()));
    if (extra_zeros > 0) {
        // Fill the start of the string with zeros, to pad the string
        // to at least frame_padding characters.
        number_as_string.insert(0, extra_zeros, '0');
    }
    MString number_padded(number_as_string.c_str());

    out_file_path = start + number_padded + end;

    return status;
}

MStatus find_file_path(MFileObject &file_object, MString &out_file_path) {
    MStatus status = MStatus::kSuccess;

    MString resolved_file_path = file_object.resolvedFullName();
    if (resolved_file_path.length() > 0) {
        out_file_path = file_object.resolvedFullName();
    }

    return status;
}

MStatus find_existing_file_path(MFileObject &file_object,
                                const MString &in_file_path,
                                MString &out_file_path) {
    MStatus status = MStatus::kSuccess;

    bool path_exists = file_object.exists();
    if (!path_exists) {
        MString resolved_file_path = file_object.resolvedFullName();
        status = MS::kFailure;
        MMSOLVER_WRN("mmConvertImage: Could not find file path "
                     << "\"" << in_file_path.asChar() << "\", resolved path "
                     << "\"" << resolved_file_path.asChar() << "\".");
        return status;
    }

    status = find_file_path(file_object, out_file_path);
    return status;
}

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
    MStatus status = MStatus::kSuccess;

    MImage::MPixelType pixel_type = image.pixelType();
    if (pixel_type != MImage::kByte) {
        MMSOLVER_WRN(
            "mmConvertImage: "
            << "Maya does not support resizing floating-point pixels.");
    }

    uint32_t src_width = 2;
    uint32_t src_height = 2;
    status = image.getSize(src_width, src_height);
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

MStatus convert_image(const MString &src_file_path,
                      const MString &dst_file_path,
                      // Common output formats include: als, bmp, cin,
                      // gif, jpg, rla, sgi, tga, tif, iff.  "iff" is
                      // default.
                      const MString &dst_output_format,
                      const double resize_scale) {
    MStatus status = MStatus::kSuccess;

    if (src_file_path == dst_file_path) {
        status = MS::kFailure;
        MMSOLVER_ERR("mmConvertImage: "
                     << "Cannot have source and destination as same path: "
                     << src_file_path.asChar());
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    auto image = MImage();
    // kUnknown attempts to load the native pixel type.
    auto src_pixel_type = MImage::kUnknown;
    status = image.readFromFile(
        src_file_path,
        src_pixel_type  // The desired pixel format is unknown.
    );
    if (status != MS::kSuccess) {
        MMSOLVER_ERR("mmConvertImage: "
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
        MMSOLVER_WRN("mmConvertImage: "
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
                MMSOLVER_ERR("mmConvertImage: "
                             << "Failed to resize image file: "
                             << src_file_path.asChar());
                return status;
            }
        }

        // No conversion is needed. We write out the 8-bit image
        // directly.
        status = image.writeToFile(dst_file_path, dst_output_format);
        if (status != MS::kSuccess) {
            MMSOLVER_ERR("mmConvertImage: "
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
            MMSOLVER_ERR("mmConvertImage: "
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

        // TODO: Use the Autodesk 'synColor' library to change the
        // color space for an 8-bit file format. This library is
        // available in the Maya devkit.
        //
        // https://forums.autodesk.com/t5/maya-programming/how-to-export-colors-with-correct-color-management/td-p/10515406

        // Make sure we do our color management with floating point
        // numbers, to avoid loss of detail. This does not do anything
        // if the pixel format is already MImage::kFloat.
        float *float_pixels = image.floatPixels();
        if (float_pixels == nullptr) {
            // The data pointer should be valid because we have
            // already read and operated on the pixels, so it seems
            // very wrong that the data wouldn't be valid.
            status = MS::kFailure;
            MMSOLVER_ERR("mmConvertImage: "
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
            MMSOLVER_ERR("mmConvertImage: "
                         << "Failed to resize image file: "
                         << src_file_path.asChar());
            return status;
        }

        status = out_image.writeToFile(dst_file_path, dst_output_format);
        if (status != MS::kSuccess) {
            MMSOLVER_ERR("mmConvertImage: "
                         << "Failed to write image file: "
                         << dst_file_path.asChar() << " output format: \""
                         << dst_output_format.asChar() << "\"");
            CHECK_MSTATUS_AND_RETURN_IT(status);
        }
    }
}

MMConvertImageCmd::~MMConvertImageCmd() {}

void *MMConvertImageCmd::creator() { return new MMConvertImageCmd(); }

MString MMConvertImageCmd::cmdName() { return MString("mmConvertImage"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMConvertImageCmd::hasSyntax() const { return true; }

bool MMConvertImageCmd::isUndoable() const { return false; }

/*
 * Add flags to the command syntax
 */
MSyntax MMConvertImageCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(SRC_FILE_PATH_FLAG, SRC_FILE_PATH_FLAG_LONG,
                   MSyntax::kString);

    syntax.addFlag(SRC_FRAME_START_FLAG, SRC_FRAME_START_FLAG_LONG,
                   MSyntax::kLong);

    syntax.addFlag(SRC_FRAME_END_FLAG, SRC_FRAME_END_FLAG_LONG, MSyntax::kLong);

    syntax.addFlag(SRC_FRAME_PADDING_FLAG, SRC_FRAME_PADDING_FLAG_LONG,
                   MSyntax::kLong);

    syntax.addFlag(DST_FILE_PATH_FLAG, DST_FILE_PATH_FLAG_LONG,
                   MSyntax::kString);

    syntax.addFlag(DST_OUTPUT_FORMAT_FLAG, DST_OUTPUT_FORMAT_FLAG_LONG,
                   MSyntax::kString);

    syntax.addFlag(DST_FRAME_START_FLAG, DST_FRAME_START_FLAG_LONG,
                   MSyntax::kLong);

    syntax.addFlag(DST_FRAME_PADDING_FLAG, DST_FRAME_PADDING_FLAG_LONG,
                   MSyntax::kLong);

    syntax.addFlag(RESIZE_SCALE_FLAG, RESIZE_SCALE_FLAG_LONG, MSyntax::kDouble);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMConvertImageCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = argData.getFlagArgument(SRC_FILE_PATH_FLAG, 0, m_src_file_path);
    if (status != MStatus::kSuccess) {
        MMSOLVER_ERR("Required source file path argument (\""
                     << SRC_FILE_PATH_FLAG_LONG << "\" flag) is missing.");
        return status;
    }

    status = argData.getFlagArgument(DST_FILE_PATH_FLAG, 0, m_dst_file_path);
    if (status != MStatus::kSuccess) {
        MMSOLVER_ERR("Required destination file path argument (\""
                     << DST_FILE_PATH_FLAG_LONG << "\" flag) is missing.");
        return status;
    }

    bool is_set_dst_output_format =
        argData.isFlagSet(DST_OUTPUT_FORMAT_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool is_set_src_frame_start =
        argData.isFlagSet(SRC_FRAME_START_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool is_set_src_frame_end = argData.isFlagSet(SRC_FRAME_END_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool is_set_src_frame_padding =
        argData.isFlagSet(SRC_FRAME_PADDING_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool is_set_dst_frame_start =
        argData.isFlagSet(DST_FRAME_START_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool is_set_dst_frame_padding =
        argData.isFlagSet(DST_FRAME_PADDING_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool is_set_resize_scale = argData.isFlagSet(RESIZE_SCALE_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (is_set_dst_output_format) {
        status = argData.getFlagArgument(DST_OUTPUT_FORMAT_FLAG, 0,
                                         m_dst_output_format);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (m_dst_output_format.length() == 0) {
            MMSOLVER_WRN("Destination output format argument (\""
                         << DST_OUTPUT_FORMAT_FLAG_LONG
                         << "\" flag) is not valid, defaulting to \"iff\".");
            m_dst_output_format = "iff";
        }
    }

    if (is_set_src_frame_start) {
        status =
            argData.getFlagArgument(SRC_FRAME_START_FLAG, 0, m_src_frame_start);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_src_frame_end) {
        status =
            argData.getFlagArgument(SRC_FRAME_END_FLAG, 0, m_src_frame_end);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_src_frame_padding) {
        status = argData.getFlagArgument(SRC_FRAME_PADDING_FLAG, 0,
                                         m_src_frame_padding);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_dst_frame_start) {
        status =
            argData.getFlagArgument(DST_FRAME_START_FLAG, 0, m_dst_frame_start);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_dst_frame_padding) {
        status = argData.getFlagArgument(DST_FRAME_PADDING_FLAG, 0,
                                         m_dst_frame_padding);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_resize_scale) {
        status = argData.getFlagArgument(RESIZE_SCALE_FLAG, 0, m_resize_scale);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    return status;
}

MStatus MMConvertImageCmd::doIt(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    // Convert all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    auto src_file_object = MFileObject();
    auto dst_file_object = MFileObject();

    MString src_file_path;
    MString dst_file_path;

    auto total_count = 0;
    auto succeeded_count = 0;
    auto fail_count = 0;
    for (auto src_frame = m_src_frame_start, dst_frame = m_dst_frame_start;
         src_frame < (m_src_frame_end + 1); ++src_frame, ++dst_frame) {
        total_count += 1;

        status = expand_file_path_with_frame_number(
            m_src_file_path, m_src_frame_padding, src_frame, src_file_path);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        status = expand_file_path_with_frame_number(
            m_dst_file_path, m_dst_frame_padding, dst_frame, dst_file_path);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        src_file_object.setRawFullName(src_file_path);
        src_file_object.setResolveMethod(MFileObject::kInputFile);
        status = find_existing_file_path(src_file_object, src_file_path,
                                         src_file_path);
        if (status != MS::kSuccess) {
            MMSOLVER_WRN("mmConvertImage: "
                         << "Failed to resolve source file path: "
                         << "\"" << src_file_path.asChar() << "\"");
            fail_count += 1;
            continue;
        }

        dst_file_object.setRawFullName(dst_file_path);
        dst_file_object.setResolveMethod(MFileObject::kNone);
        status = find_file_path(dst_file_object, dst_file_path);
        if (status != MS::kSuccess) {
            MMSOLVER_WRN("mmConvertImage: "
                         << "Failed to resolve destination file path: "
                         << "\"" << dst_file_path.asChar() << "\"");
            fail_count += 1;
            continue;
        }

        if ((src_file_path.length() == 0) || (dst_file_path.length() == 0)) {
            MMSOLVER_WRN("mmConvertImage: Failed to resolve file paths "
                         << "\"" << src_file_path.asChar() << "\" to \""
                         << dst_file_path.asChar() << "\".");
            fail_count += 1;
            continue;
        }

        status = convert_image(src_file_path, dst_file_path,
                               m_dst_output_format, m_resize_scale);
        if (status != MS::kSuccess) {
            MMSOLVER_WRN("mmConvertImage: "
                         << "Failed to convert image: "
                         << "\"" << src_file_path.asChar() << "\" to \""
                         << dst_file_path.asChar() << "\".");
            fail_count += 1;
            continue;
        }

        MMSOLVER_INFO("mmConvertImage: "
                      << "Converted "
                      << "\"" << src_file_path.asChar() << "\" to \""
                      << dst_file_path.asChar() << "\".");
        succeeded_count += 1;
    }

    status = MS::kSuccess;
    if ((total_count == fail_count) && (succeeded_count == 0)) {
        // All of the tasks failed.
        MMConvertImageCmd::setResult(false);
        MMSOLVER_ERR("mmConvertImage: "
                     << "All images failed to convert image:"
                     << " failed=" << fail_count);
    } else if (fail_count > 0) {
        // Some of the tasks failed.
        MMConvertImageCmd::setResult(false);
        MMSOLVER_WRN("mmConvertImage: "
                     << "Some images failed to convert image:"
                     << " total=" << total_count << " succeeded="
                     << succeeded_count << " failed=" << fail_count);
    }

    return status;
}

}  // namespace mmsolver
