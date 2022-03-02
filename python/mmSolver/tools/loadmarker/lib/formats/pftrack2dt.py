# Copyright (C) 2018, 2022 David Cattermole.
#
# This file is part of mmSolver.
#
# mmSolver is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# mmSolver is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
#
"""
The .txt format from PFTrack / PFMatchIt.

The position coordinate (-0.5, -0.5) is the lower-left.
The position coordinate (width - 0.5, height - 0.5) is the upper-right.

This format is resolution dependant!

The data block looks like this::

    "trackerName"   # Tracker name.
    int     # Clip number. First number is 1, then 2, etc.
    int     # Number of frames
    int float float float  # Frame, X position, Y position, residual

Or another variation::

    "trackerName"   # Tracker name.
    "cameraName"    # Camera name
    int     # Number of frames
    int float float float float  # Frame, X position, Y position, residual


Each block of data is separated by whitespace (usually a blank line).

Optionally, each line of tracker frame and position may also have a
Z-Depth value, like this::

    "trackerName"   # Tracker name.
    int     # Clip number.
    int     # Number of frames
    int float float float float  # Frame, X position, Y position, residual, z-depth

Simple file with 1 2D track and 1 frame of data::

    "MyFeature1"
    1
    1
    1 1920.000 1080.000 0.000

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger
import mmSolver.tools.loadmarker.lib.interface as interface
import mmSolver.tools.loadmarker.lib.formatmanager as fmtmgr

LOG = mmSolver.logger.get_logger()


def parse_int_or_none(value):
  try:
    return int(value)
  except ValueError:
    return None


def parse_float_or_none(value):
  try:
    return float(value)
  except ValueError:
    return None


def _remove_comments_from_lines(lines):
    clean_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue
        line = line.partition('#')[0]
        clean_lines.append(line)
    return clean_lines


class LoaderPFTrack2DT(interface.LoaderBase):

    name = 'PFTrack 2D Tracks (*.2dt / *.txt)'
    file_exts = ['.2dt', '.txt']
    args = [
        ('image_width', None),
        ('image_height', None),
    ]

    def parse(self, file_path, **kwargs):
        """
        Parse the file path as a PFTrack .2dt/.txt file.

        :param file_path: File path to parse.
        :type file_path: str

        :param kwargs: expected to contain 'image_width' and 'image_height'.

        :return: List of MarkerData.
        """
        # If the image width/height is not given we raise an error immediately.
        image_width = kwargs.get('image_width')
        image_height = kwargs.get('image_height')
        if image_width is None:
            image_width = 1.0
        if image_height is None:
            image_height = 1.0
        inv_image_width = 1.0 / image_width
        inv_image_height = 1.0 / image_height

        lines = []
        with open(file_path, 'r') as f:
            lines = f.readlines()
        if len(lines) == 0:
            raise OSError('No contents in the file: %s' % file_path)
        mkr_data_list = []

        i = 0
        lines = _remove_comments_from_lines(lines)
        while i < len(lines):
            line = lines[i]
            mkr_name = None
            # Tracker Name
            if line.startswith('"') and line.endswith('"'):
                mkr_name = line[1:-1]
                i += 1
            else:
                i += 1
                continue

            # Clip number or Camera name.
            #
            # PFTrack 5 used a camera name, but future versions of
            # PFTrack use clip numbers.
            #
            # Either way, this value is parsed by never used by the
            # importer because I don't know how the clip number or
            # camera name should be used in mmSolver.
            cam_name = None
            line = lines[i]
            clip_number = parse_int_or_none(line)
            if clip_number is not None:
                i += 1
            elif line.startswith('"') and line.endswith('"'):
                cam_name = line[1:-1]
                i += 1
            else:
                msg = (
                    'File invalid, '
                    'expecting a camera name (string) in line: %r'
                )
                raise interface.ParserError(msg % line)

            # Create marker
            mkr_data = interface.MarkerData()
            mkr_data.set_name(mkr_name)

            # Number of frames.
            line = lines[i]
            number_of_frames = parse_int_or_none(line)
            if number_of_frames is None:
                msg = (
                    'File invalid, '
                    'expecting a number of frames (integer) in line: %r'
                )
                raise interface.ParserError(msg % line)
            i += 1

            # Parse per-frame data.
            frames = []
            for frame_index in range(number_of_frames):
                line = lines[i]
                line_split = line.split(' ')
                frame = None
                mkr_u = 0.0
                mkr_v = 0.0
                residual = None
                zdepth = None
                if len(line_split) not in [4, 5]:
                    msg = (
                        'File invalid, '
                        'there must be 4 or 5 numbers in line: %r'
                    )
                    raise interface.ParserError(msg % line)

                frame = parse_int_or_none(line_split[0])
                pos_x = parse_float_or_none(line_split[1])
                pos_y = parse_float_or_none(line_split[2])
                if frame is None or pos_x is None or pos_y is None:
                    raise interface.ParserError('Invalid file format.')

                # PFTrack treats the center of the pixel as "0.0",
                # which is different from other matchmove
                # software.
                mkr_u = (pos_x + 0.5) * inv_image_width
                mkr_v = (pos_y + 0.5) * inv_image_height

                # # There is no need for residual or the Z-depth for now.
                # residual = parse_float_or_none(line_split[3])
                # if len(line_split) == 5:
                #     zdepth = parse_float_or_none(line_split[4])

                mkr_weight = 1.0
                mkr_data.weight.set_value(frame, mkr_weight)
                mkr_data.x.set_value(frame, mkr_u)
                mkr_data.y.set_value(frame, mkr_v)
                frames.append(frame)
                i += 1

            # Fill in occluded frames
            all_frames = list(range(min(frames), max(frames)+1))
            for frame in all_frames:
                mkr_enable = int(frame in frames)
                mkr_data.enable.set_value(frame, mkr_enable)
                if mkr_enable is False:
                    mkr_data.weight.set_value(frame, 0.0)

            mkr_data_list.append(mkr_data)

        file_info = interface.create_file_info()
        return file_info, mkr_data_list


# Register the File Format
mgr = fmtmgr.get_format_manager()
mgr.register_format(LoaderPFTrack2DT)
