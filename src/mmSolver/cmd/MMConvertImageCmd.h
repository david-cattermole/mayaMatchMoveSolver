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
 * Header for mmConvertImage Maya command.
 */

#ifndef MAYA_MM_CONVERT_IMAGE_CMD_H
#define MAYA_MM_CONVERT_IMAGE_CMD_H

// Maya
#include <maya/MArgDatabase.h>
#include <maya/MArgList.h>
#include <maya/MGlobal.h>
#include <maya/MIOStream.h>
#include <maya/MPxCommand.h>
#include <maya/MSyntax.h>
#include <maya/MSelectionList.h>
#include <maya/MString.h>


// Command arguments and command name:
#define SRC_FILE_PATH_FLAG       "-src"
#define SRC_FILE_PATH_FLAG_LONG  "-source"

#define SRC_FRAME_START_FLAG       "-sfs"
#define SRC_FRAME_START_FLAG_LONG  "-sourceFrameStart"

#define SRC_FRAME_END_FLAG       "-sfe"
#define SRC_FRAME_END_FLAG_LONG  "-sourceFrameEnd"

#define SRC_FRAME_PADDING_FLAG       "-sfp"
#define SRC_FRAME_PADDING_FLAG_LONG  "-sourceFramePadding"

#define DST_FILE_PATH_FLAG       "-dst"
#define DST_FILE_PATH_FLAG_LONG  "-destination"

#define DST_OUTPUT_FORMAT_FLAG       "-dof"
#define DST_OUTPUT_FORMAT_FLAG_LONG  "-destinationOutputFormat"

#define DST_FRAME_START_FLAG       "-dfs"
#define DST_FRAME_START_FLAG_LONG  "-destinationFrameStart"

#define DST_FRAME_PADDING_FLAG       "-dfp"
#define DST_FRAME_PADDING_FLAG_LONG  "-destinationFramePadding"

#define RESIZE_SCALE_FLAG      "-rzs"
#define RESIZE_SCALE_FLAG_LONG  "-resizeScale"


namespace mmsolver {

class MMConvertImageCmd : public MPxCommand {
public:

    MMConvertImageCmd()
            : m_src_file_path()
            , m_dst_file_path()
            , m_dst_output_format(MString("iff"))
            , m_src_frame_start(1)
            , m_src_frame_end(1)
            , m_dst_frame_start(1)
            , m_src_frame_padding(1)
            , m_dst_frame_padding(1)
            , m_resize_scale(1.0F)
        {};

    virtual ~MMConvertImageCmd();

    virtual bool hasSyntax() const;
    static MSyntax newSyntax();

    virtual MStatus doIt(const MArgList &args);

    virtual bool isUndoable() const;

    static void *creator();

    static MString cmdName();

private:
    MStatus parseArgs( const MArgList& args );

    MString m_src_file_path;
    MString m_dst_file_path;

    MString m_dst_output_format;

    uint32_t m_src_frame_start;
    uint32_t m_src_frame_end;
    uint32_t m_dst_frame_start;

    uint32_t m_src_frame_padding;
    uint32_t m_dst_frame_padding;

    double m_resize_scale;
};

} // namespace mmsolver

#endif // MAYA_MM_CONVERT_IMAGE_CMD_H
