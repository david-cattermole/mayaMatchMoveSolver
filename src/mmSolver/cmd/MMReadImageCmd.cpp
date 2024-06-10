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
 * Command for running mmReadImage.
 */

#include "MMReadImageCmd.h"

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MDagPath.h>
#include <maya/MFileObject.h>
#include <maya/MImage.h>
#include <maya/MObject.h>
#include <maya/MString.h>
#include <maya/MStringArray.h>
#include <maya/MSyntax.h>

// MM Solver
#include "mmSolver/image/ImagePixelData.h"
#include "mmSolver/image/PixelDataType.h"
#include "mmSolver/image/image_io.h"
#include "mmSolver/utilities/debug_utils.h"
#include "mmSolver/utilities/string_utils.h"

// Command arguments and command name:
#define FILE_PATH_FLAG "-fp"
#define FILE_PATH_FLAG_LONG "-filePath"

#define WIDTH_HEIGHT_FLAG "-wh"
#define WIDTH_HEIGHT_FLAG_LONG "-widthHeight"

#define DATA_HEADER_FLAG "-dhr"
#define DATA_HEADER_FLAG_LONG "-dataHeader"

namespace mmsolver {

MMReadImageCmd::~MMReadImageCmd() {}

void *MMReadImageCmd::creator() { return new MMReadImageCmd(); }

MString MMReadImageCmd::cmdName() { return MString("mmReadImage"); }

/*
 * Tell Maya we have a syntax function.
 */
bool MMReadImageCmd::hasSyntax() const { return true; }

bool MMReadImageCmd::isUndoable() const { return false; }

/*
 * Add flags to the command syntax
 */
MSyntax MMReadImageCmd::newSyntax() {
    MSyntax syntax;
    syntax.enableQuery(true);
    syntax.enableEdit(false);

    auto minNumObjects = 1;
    auto maxNumObjects = 1;
    syntax.setObjectType(MSyntax::kStringObjects, minNumObjects, maxNumObjects);

    syntax.addFlag(WIDTH_HEIGHT_FLAG, WIDTH_HEIGHT_FLAG_LONG);
    syntax.addFlag(DATA_HEADER_FLAG, DATA_HEADER_FLAG_LONG);

    return syntax;
}

/*
 * Parse command line arguments
 */
MStatus MMReadImageCmd::parseArgs(const MArgList &args) {
    MStatus status = MStatus::kSuccess;

    MArgDatabase argData(syntax(), args, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    // Query Flag
    const bool query = argData.isQuery(&status);
    CHECK_MSTATUS(status);
    if (status != MStatus::kSuccess) {
        status.perror("mmReadImage: Could not get the query flag");
        return status;
    }

    if (!query) {
        status = MStatus::kFailure;
        status.perror("mmReadImage command must query using the 'query' flag");
        return status;
    }

    // Get the file path.
    MStringArray objects;
    argData.getObjects(objects);
    if (objects.length() == 0) {
        status = MStatus::kFailure;
        status.perror(
            "mmReadImage: No file path was was not given, but is required!");
        return status;
    }
    if (objects.length() > 1) {
        status = MStatus::kFailure;
        status.perror(
            "mmReadImage: "
            "More than one file path was was not given,"
            " only one file path should be given.");
        return status;
    }
    m_file_path = objects[0];

    m_query_width_height = argData.isFlagSet(WIDTH_HEIGHT_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    m_query_data_header = argData.isFlagSet(DATA_HEADER_FLAG, &status);
    CHECK_MSTATUS_AND_RETURN_IT(status);
    return status;
}

MStatus read_image_header(const MString &file_path, uint32_t &out_image_width,
                          uint32_t &out_image_height, uint8_t &out_num_channels,
                          uint8_t &out_bytes_per_channel,
                          MHWRender::MRasterFormat &out_texture_format,
                          image::PixelDataType &out_pixel_data_type) {
    MStatus status = MStatus::kSuccess;
    MImage image;

    out_image_width = 0;
    out_image_height = 0;
    out_num_channels = 0;
    out_bytes_per_channel = 0;

    // We won't use the image data anyway.
    void *pixel_data = nullptr;

    // TODO: Can we read just the file header to get the image size?
    // This would remove the need to read the entire image for this
    // command's usage.
    status = image::read_image_file(image, file_path, out_image_width,
                                    out_image_height, out_num_channels,
                                    out_bytes_per_channel, out_texture_format,
                                    out_pixel_data_type, pixel_data);
    if (status != MS::kSuccess) {
        MMSOLVER_MAYA_WRN("mmReadImage: "
                          << "Image file path could not be read: "
                          << file_path.asChar());
    }

    return status;
}

MStatus MMReadImageCmd::doIt(const MArgList &args) {
    const bool verbose = false;
    MStatus status = MStatus::kSuccess;

    // Read all the flag arguments.
    status = parseArgs(args);
    CHECK_MSTATUS_AND_RETURN_IT(status);

    auto file_object = MFileObject();
    file_object.setRawFullName(m_file_path);
    file_object.setResolveMethod(MFileObject::kInputFile);

    bool path_exists = file_object.exists();
    if (!path_exists) {
        MString resolved_file_path = file_object.resolvedFullName();
        status = MS::kFailure;
        MMSOLVER_MAYA_WRN("mmReadImage: Could not find file path "
                          << "\"" << m_file_path.asChar()
                          << "\", resolved path "
                          << "\"" << resolved_file_path.asChar() << "\".");
        return status;
    }

    MString resolved_file_path = file_object.resolvedFullName();
    if (resolved_file_path.length() > 0) {
        MMSOLVER_MAYA_VRB("mmReadImage: resolved file path "
                          << "\"" << resolved_file_path.asChar() << "\".");
        m_file_path = file_object.resolvedFullName();
    }

    if (m_query_width_height) {
        uint32_t image_width = 0;
        uint32_t image_height = 0;
        uint8_t num_channels = 0;
        uint8_t bytes_per_channel = 0;
        MHWRender::MRasterFormat texture_format;
        image::PixelDataType pixel_data_type;

        status = read_image_header(m_file_path, image_width, image_height,
                                   num_channels, bytes_per_channel,
                                   texture_format, pixel_data_type);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        MIntArray outResult;
        outResult.append(image_width);
        outResult.append(image_height);
        MMReadImageCmd::setResult(outResult);
    } else if (m_query_data_header) {
        // NOTE: We do not want to have to call mmReadImage multiple
        // times. We want to get as much data as possible in a single
        // call, because subsequent calls will need to re-read the
        // image.

        uint32_t image_width = 0;
        uint32_t image_height = 0;
        uint8_t num_channels = 0;
        uint8_t bytes_per_channel = 0;
        MHWRender::MRasterFormat texture_format;
        image::PixelDataType pixel_data_type;

        status = read_image_header(m_file_path, image_width, image_height,
                                   num_channels, bytes_per_channel,
                                   texture_format, pixel_data_type);
        CHECK_MSTATUS_AND_RETURN_IT(status);

        void *pixel_data = nullptr;
        image::ImagePixelData image_pixel_data(pixel_data, image_width,
                                               image_height, num_channels,
                                               pixel_data_type);
        size_t byte_count = image_pixel_data.byte_count();

        // Some of the numbers may be more than 'int' can hold, so we
        // must return as a MString.
        std::string width_string = mmstring::numberToString(image_width);
        std::string height_string = mmstring::numberToString(image_height);
        std::string num_channels_string =
            mmstring::numberToString(static_cast<uint32_t>(num_channels));
        std::string bytes_per_channel_string =
            mmstring::numberToString(static_cast<uint32_t>(bytes_per_channel));
        std::string byte_count_string = mmstring::numberToString(byte_count);

        MString width_mstring(width_string.c_str());
        MString height_mstring(height_string.c_str());
        MString num_channels_mstring(num_channels_string.c_str());
        MString bytes_per_channel_mstring(bytes_per_channel_string.c_str());
        MString byte_count_mstring(byte_count_string.c_str());

        MStringArray outResult;
        outResult.append(width_mstring);
        outResult.append(height_mstring);
        outResult.append(num_channels_mstring);
        outResult.append(bytes_per_channel_mstring);
        outResult.append(byte_count_mstring);
        MMReadImageCmd::setResult(outResult);
    }

    return status;
}

}  // namespace mmsolver
