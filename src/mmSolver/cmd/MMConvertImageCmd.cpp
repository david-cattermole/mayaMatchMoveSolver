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
#include <maya/MFileObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// MM Solver Libs
#include <mmcore/mmmath.h>

// MM Solver
#include "mmSolver/image/image_convert.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

namespace mmsolver {

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
    bool path_exists = file_object.exists();
    if (!path_exists) {
        MString resolved_file_path = file_object.resolvedFullName();
        MMSOLVER_MAYA_WRN("mmConvertImage: Could not find file path "
                          << "\"" << in_file_path.asChar()
                          << "\", resolved path "
                          << "\"" << resolved_file_path.asChar() << "\".");
        return MS::kFailure;
    }

    MStatus status = find_file_path(file_object, out_file_path);
    CHECK_MSTATUS(status);
    return status;
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
        MMSOLVER_MAYA_ERR("Required source file path argument (\""
                          << SRC_FILE_PATH_FLAG_LONG << "\" flag) is missing.");
        return status;
    }

    status = argData.getFlagArgument(DST_FILE_PATH_FLAG, 0, m_dst_file_path);
    if (status != MStatus::kSuccess) {
        MMSOLVER_MAYA_ERR("Required destination file path argument (\""
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
            MMSOLVER_MAYA_WRN(
                "Destination output format argument (\""
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
    // Convert all the flag arguments.
    MStatus status = parseArgs(args);
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
            MMSOLVER_MAYA_WRN("mmConvertImage: "
                              << "Failed to resolve source file path: "
                              << "\"" << src_file_path.asChar() << "\"");
            fail_count += 1;
            continue;
        }

        dst_file_object.setRawFullName(dst_file_path);
        dst_file_object.setResolveMethod(MFileObject::kNone);
        status = find_file_path(dst_file_object, dst_file_path);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_WRN("mmConvertImage: "
                              << "Failed to resolve destination file path: "
                              << "\"" << dst_file_path.asChar() << "\"");
            fail_count += 1;
            continue;
        }

        if ((src_file_path.length() == 0) || (dst_file_path.length() == 0)) {
            MMSOLVER_MAYA_WRN("mmConvertImage: Failed to resolve file paths "
                              << "\"" << src_file_path.asChar() << "\" to \""
                              << dst_file_path.asChar() << "\".");
            fail_count += 1;
            continue;
        }

        status = image::convert_image(src_file_path, dst_file_path,
                                      m_dst_output_format, m_resize_scale);
        if (status != MS::kSuccess) {
            MMSOLVER_MAYA_WRN("mmConvertImage: "
                              << "Failed to convert image: "
                              << "\"" << src_file_path.asChar() << "\" to \""
                              << dst_file_path.asChar() << "\".");
            fail_count += 1;
            continue;
        }

        MMSOLVER_MAYA_INFO("mmConvertImage: "
                           << "Converted "
                           << "\"" << src_file_path.asChar() << "\" to \""
                           << dst_file_path.asChar() << "\".");
        succeeded_count += 1;
    }

    status = MS::kSuccess;
    if ((total_count == fail_count) && (succeeded_count == 0)) {
        // All of the tasks failed.
        MMConvertImageCmd::setResult(false);
        MMSOLVER_MAYA_ERR("mmConvertImage: "
                          << "All images failed to convert image:"
                          << " failed=" << fail_count);
    } else if (fail_count > 0) {
        // Some of the tasks failed.
        MMConvertImageCmd::setResult(false);
        MMSOLVER_MAYA_WRN("mmConvertImage: "
                          << "Some images failed to convert image:"
                          << " total=" << total_count << " succeeded="
                          << succeeded_count << " failed=" << fail_count);
    }

    return status;
}

}  // namespace mmsolver
