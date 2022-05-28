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
#include <vector>
#include <algorithm>

// Maya
#include <maya/MArgList.h>
#include <maya/MArgDatabase.h>
#include <maya/MDagPath.h>
#include <maya/MFileObject.h>
#include <maya/MFnDependencyNode.h>
#include <maya/MMatrix.h>
#include <maya/MMatrixArray.h>
#include <maya/MObject.h>
#include <maya/MPlug.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>
#include <maya/MImage.h>

// MM Solver
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

// For an image sequence the 'file_path' should contain at least one
// character '#', which will be replaced with the 'frame_number', with
// a padding width of 'frame_padding'.
MStatus expandFilePathWithFrameNumber(const MString &file_path,
                                      uint32_t frame_padding,
                                      uint32_t frame_number,
                                      MString &out_file_path) {
    MStatus status = MStatus::kSuccess;

    auto first_char = file_path.index('#');
    if (first_char == -1) {
        return status;
    }

    auto last_char = file_path.rindex('#');
    if (last_char == -1) {
        return status;
    }

    MString start = file_path.substring(0, first_char - 1);
    MString end = file_path.substring(last_char + 1, file_path.length() - 1);

    std::string number_as_string = mmstring::numberToString(frame_number);

    int extra_zeros = std::max(
        0, static_cast<int>(frame_padding) - static_cast<int>(number_as_string.size()));
    if (extra_zeros > 0) {
        // Fill the start of the string with zeros, to pad the string
        // to at least frame_padding characters.
        number_as_string.insert(0, extra_zeros, '0');
    }
    MString number_padded(number_as_string.c_str());

    out_file_path = start + number_padded + end;

    return status;
}

MStatus find_file_path(MFileObject &file_object,
                       MString &out_file_path) {
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
        MMSOLVER_WRN(
            "mmConvertImage: Could not find file path "
            << "\"" << in_file_path.asChar() << "\", resolved path "
            << "\"" << resolved_file_path.asChar() << "\".");
        return status;
    }

    status = find_file_path(file_object, out_file_path);
    return status;
}

// https://martin.ankerl.com/2007/10/04/optimized-pow-approximation-for-java-and-c-c/
double fast_pow(double a, double b) {
    union {
        double d;
        int x[2];
    } u = { a };
    u.x[1] = static_cast<int>(b * (u.x[1] - 1072632447) + 1072632447);
    u.x[0] = 0;
    return u.d;
}

// https://martin.ankerl.com/2007/10/04/optimized-pow-approximation-for-java-and-c-c/
float fast_pow(float a, float b) {
    union {
        float f;
        int i;
    } u = { a };
    u.i = static_cast<int>(b * (u.i - 1065307417) + 1065307417);
    return u.f;
}

MStatus convert_image(const MString &src_file_path,
                      const MString &dst_file_path,
                      // Common output formats include: als, bmp, cin,
                      // gif, jpg, rla, sgi, tga, tif, iff.  "iff" is
                      // default.
                      const MString &dst_output_format,
                      const double resize_scale,
                      // Temporary memory used to hold floating point
                      // pixels and reused for each call to this
                      // function.
                      std::vector<float> &inout_temp_float_pixels) {
    MStatus status = MStatus::kSuccess;

    auto image = MImage();
    // kUnknown attempts to load the native pixel type.
    auto pixel_type = MImage::kUnknown;
    status = image.readFromFile(
        src_file_path,
        pixel_type  // The desired pixel format is unknown.
    );
    if (status != MS::kSuccess) {
        MMSOLVER_ERR(
            "mmConvertImage: "
            << "Image file path could not be read: "
            << src_file_path.asChar());
        return status;
    }

    uint32_t src_width = 2;
    uint32_t src_height = 2;
    image.getSize(src_width, src_height);

    const auto preserve_aspect_ratio = true;
    auto dst_width_float = static_cast<double>(src_width) * resize_scale;
    auto dst_height_float = static_cast<double>(src_height) * resize_scale;
    auto dst_width = static_cast<uint32_t>(dst_width_float);
    auto dst_height = static_cast<uint32_t>(dst_height_float);
    // TODO: Replace this with a hand-written resize function. The
    // MImage.resize() method appears to have a bug whereby the
    // resized image is offset by +1 pixel in X and Y.
    image.resize(dst_width, dst_height, preserve_aspect_ratio);

    // TODO: Use the destination output format to work out if we are
    // converting to/from a linear floating point image, then apply
    // color management and convert to the desired file format. Only
    // EXR is supported as a floating-point image file format.
    if (image.pixelType() == MImage::kFloat) {
        // Apply hard-coded gamma to the floating point image, so the
        // image looks better than a default linear color space.
        //
        // Maya always stores 4 channels (according to the
        // documentation).
        auto channels = 4;
        float * data_ptr = image.floatPixels();
        if (data_ptr == nullptr) {
            // The data pointer should be valid because we have
            // already read and operated on the pixels, so it seems
            // very wrong that the data wouldn't be valid.
            status = MS::kFailure;
            MMSOLVER_ERR(
                "mmConvertImage: "
                << "Failed to get floating point pixel data: "
                << src_file_path.asChar());
            return status;
        }

        // TODO: Use the Autodesk 'synColor' library to change the color
        // space for an 8-bit file format.
        //
        // https://forums.autodesk.com/t5/maya-programming/how-to-export-colors-with-correct-color-management/td-p/10515406

        // Apply (hard-coded) gamma.
        auto data_size = dst_width * dst_height * channels;
        inout_temp_float_pixels.resize(data_size);

        const float gamma = 2.2F;
        const float inv_gamma = 1.0 / gamma;
        for (auto y = 0; y < dst_height; ++y) {
            for (auto x = 0; x < dst_width; ++x) {
                auto index = (y * dst_height) + dst_width;
                inout_temp_float_pixels[index + 0] = fast_pow(data_ptr[index + 0], gamma);
                inout_temp_float_pixels[index + 1] = fast_pow(data_ptr[index + 1], gamma);
                inout_temp_float_pixels[index + 2] = fast_pow(data_ptr[index + 2], gamma);
                // Alpha (4th channel) is not gamma corrected.
                inout_temp_float_pixels[index + 3] = data_ptr[index + 3];
            }
        }
        image.setFloatPixels(
            &inout_temp_float_pixels[0],
            dst_width, dst_height, channels);

        // TODO: Convert the image into a pixel format needed as the
        // output.
        const auto to_pixel_format = MImage::kByte;
        // A scale of 0 will automatically rescale based on the
        // minimum and maximum values in the image.
        const auto pixel_range_scale = 0.0;
        const auto pixel_range_offset = 0.0;
        image.convertPixelFormat(
            to_pixel_format,
            pixel_range_scale,
            pixel_range_offset);
    }

    status = image.writeToFile(dst_file_path, dst_output_format);
    if (status != MS::kSuccess) {
        MMSOLVER_ERR(
            "mmConvertImage: "
            << "Failed to write image file: "
            << dst_file_path.asChar());
        return status;
    }
}


MMConvertImageCmd::~MMConvertImageCmd() {}

void *MMConvertImageCmd::creator() {
    return new MMConvertImageCmd();
}

MString MMConvertImageCmd::cmdName() {
    return MString("mmConvertImage");
}

/*
 * Tell Maya we have a syntax function.
 */
bool MMConvertImageCmd::hasSyntax() const {
    return true;
}

bool MMConvertImageCmd::isUndoable() const {
    return false;
}

/*
 * Add flags to the command syntax
 */
MSyntax MMConvertImageCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(false);
    syntax.enableEdit(false);

    syntax.addFlag(
        SRC_FILE_PATH_FLAG,
        SRC_FILE_PATH_FLAG_LONG,
        MSyntax::kString);

    syntax.addFlag(
        SRC_FRAME_START_FLAG,
        SRC_FRAME_START_FLAG_LONG,
        MSyntax::kLong);

    syntax.addFlag(
        SRC_FRAME_END_FLAG,
        SRC_FRAME_END_FLAG_LONG,
        MSyntax::kLong);

    syntax.addFlag(
        SRC_FRAME_PADDING_FLAG,
        SRC_FRAME_PADDING_FLAG_LONG,
        MSyntax::kLong);

    syntax.addFlag(
        DST_FILE_PATH_FLAG,
        DST_FILE_PATH_FLAG_LONG,
        MSyntax::kString);

    syntax.addFlag(
        DST_OUTPUT_FORMAT_FLAG,
        DST_OUTPUT_FORMAT_FLAG_LONG,
        MSyntax::kString);

    syntax.addFlag(
        DST_FRAME_START_FLAG,
        DST_FRAME_START_FLAG_LONG,
        MSyntax::kLong);

    syntax.addFlag(
        DST_FRAME_PADDING_FLAG,
        DST_FRAME_PADDING_FLAG_LONG,
        MSyntax::kLong);

    syntax.addFlag(
        RESIZE_SCALE_FLAG,
        RESIZE_SCALE_FLAG_LONG,
        MSyntax::kDouble);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMConvertImageCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    status = argData.getFlagArgument(
        SRC_FILE_PATH_FLAG, 0, m_src_file_path);
    if (status != MStatus::kSuccess) {
        MMSOLVER_ERR(
            "Required source file path argument (\""
            << SRC_FILE_PATH_FLAG_LONG
            << "\" flag) is missing.");
        return status;
    }

    status = argData.getFlagArgument(
        DST_FILE_PATH_FLAG, 0, m_dst_file_path);
    if (status != MStatus::kSuccess) {
        MMSOLVER_ERR(
            "Required destination file path argument (\""
            << DST_FILE_PATH_FLAG_LONG
            << "\" flag) is missing.");
        return status;
    }

    bool is_set_dst_output_format =
        argData.isFlagSet(DST_OUTPUT_FORMAT_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool is_set_src_frame_start =
        argData.isFlagSet(SRC_FRAME_START_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    bool is_set_src_frame_end =
        argData.isFlagSet(SRC_FRAME_END_FLAG, &status);
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

    bool is_set_resize_scale =
        argData.isFlagSet(RESIZE_SCALE_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    if (is_set_dst_output_format) {
        status = argData.getFlagArgument(
            DST_OUTPUT_FORMAT_FLAG, 0, m_dst_output_format);
        CHECK_MSTATUS_AND_RETURN_IT(status);
        if (m_dst_output_format.length() == 0) {
            MMSOLVER_WRN(
                "Destination output format argument (\""
                << DST_OUTPUT_FORMAT_FLAG_LONG
                << "\" flag) is not valid, defaulting to \"iff\".");
            m_dst_output_format = "iff";
        }
    }

    if (is_set_src_frame_start) {
        status = argData.getFlagArgument(
            SRC_FRAME_START_FLAG, 0, m_src_frame_start);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_src_frame_end) {
        status = argData.getFlagArgument(
            SRC_FRAME_END_FLAG, 0, m_src_frame_end);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_src_frame_padding) {
        status = argData.getFlagArgument(
            SRC_FRAME_PADDING_FLAG, 0, m_src_frame_padding);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_dst_frame_start) {
        status = argData.getFlagArgument(
            DST_FRAME_START_FLAG, 0, m_dst_frame_start);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_dst_frame_padding) {
        status = argData.getFlagArgument(
            DST_FRAME_PADDING_FLAG, 0, m_dst_frame_padding);
        CHECK_MSTATUS_AND_RETURN_IT(status);
    }

    if (is_set_resize_scale) {
        status = argData.getFlagArgument(
            RESIZE_SCALE_FLAG, 0, m_resize_scale);
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

    std::vector<float> reused_temp_memory;
    MString src_file_path;
    MString dst_file_path;

    auto total_count = 0;
    auto succeeded_count = 0;
    auto fail_count = 0;
    for (auto src_frame = m_src_frame_start, dst_frame = m_dst_frame_start;
         src_frame < (m_src_frame_end + 1);
         ++src_frame, ++dst_frame) {
        total_count += 1;

        expandFilePathWithFrameNumber(
            m_src_file_path,
            m_src_frame_padding,
            src_frame,
            src_file_path);

        expandFilePathWithFrameNumber(
            m_dst_file_path,
            m_dst_frame_padding,
            dst_frame,
            dst_file_path);

        src_file_object.setRawFullName(src_file_path);
        src_file_object.setResolveMethod(MFileObject::kInputFile);
        status = find_existing_file_path(src_file_object, src_file_path, src_file_path);
        if (status != MS::kSuccess) {
            MMSOLVER_WRN(
                "mmConvertImage: "
                << "Failed to resolve source file path: "
                << "\"" << src_file_path.asChar()
                << "\"");
            fail_count += 1;
            continue;
        }

        dst_file_object.setRawFullName(dst_file_path);
        dst_file_object.setResolveMethod(MFileObject::kNone);
        status = find_file_path(dst_file_object, dst_file_path);
        if (status != MS::kSuccess) {
            MMSOLVER_WRN(
                "mmConvertImage: "
                << "Failed to resolve destination file path: "
                << "\"" << dst_file_path.asChar()
                << "\"");
            fail_count += 1;
            continue;
        }

        if ((src_file_path.length() == 0) || (dst_file_path.length() == 0)) {
            MMSOLVER_WRN(
                "mmConvertImage: Failed to resolve file paths "
                << "\"" << src_file_path.asChar()
                << "\" to \""
                << dst_file_path.asChar() << "\".");
            fail_count += 1;
            continue;
        }

        status = convert_image(
            src_file_path,
            dst_file_path,
            m_dst_output_format,
            m_resize_scale,
            reused_temp_memory);
        if (status != MS::kSuccess) {
            MMSOLVER_WRN(
                "mmConvertImage: "
                << "Failed to convert image: "
                << "\"" << src_file_path.asChar()
                << "\" to \""
                << dst_file_path.asChar() << "\".");
            fail_count += 1;
            continue;
        }

        MMSOLVER_INFO(
            "mmConvertImage: "
            << "Converted "
            << "\"" << src_file_path.asChar()
            << "\" to \""
            << dst_file_path.asChar() << "\".");
        succeeded_count += 1;
    }

    status = MS::kSuccess;
    if ((total_count == fail_count) && (succeeded_count == 0)) {
        // All of the tasks failed.
        MMConvertImageCmd::setResult(false);
        MMSOLVER_ERR(
            "mmConvertImage: "
            << "All images failed to convert image:"
            << " failed=" << fail_count);
    }
    else if (fail_count > 0) {
        // Some of the tasks failed.
        MMConvertImageCmd::setResult(false);
        MMSOLVER_WRN(
            "mmConvertImage: "
            << "Some images failed to convert image:"
            << " total=" << total_count
            << " succeeded=" << succeeded_count
            << " failed=" << fail_count);
    }

    return status;
}

} // namespace mmsolver
