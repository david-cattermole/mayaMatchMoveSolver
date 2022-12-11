# Copyright (C) 2018 David Cattermole.
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
The .txt format from the 3DEqualizer 2D Points exporter.

The position coordinate (0.0, 0.0) is the lower-left.
The position coordinate (width, height) is the upper-right.

This format is resolution dependent!

The file format looks like this::

    int     # Number of track points in the file
    string  # Name of point
    int     # Color of the point
    int     # Number of frames
    int float float  # Frame, X position, Y position

Simple file with 1 2D track and 1 frame of data::

    1
    My Point Name
    0
    1
    1 1920.0 1080.0

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.logger

import mmSolver.utils.loadfile.excep as excep
import mmSolver.utils.loadfile.loader as loader
import mmSolver.utils.loadmarker.markerdata as markerdata
import mmSolver.utils.loadmarker.fileinfo as fileinfo
import mmSolver.utils.loadmarker.formatmanager as fmtmgr

LOG = mmSolver.logger.get_logger()


def _parse_int_or_none(value):
    try:
        return int(value)
    except ValueError:
        return None


def _parse_float_or_none(value):
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


class Loader3DETXT(loader.LoaderBase):

    name = '3DEqualizer Track Points (*.txt)'
    file_exts = ['.txt']
    args = [
        ('image_width', None),
        ('image_height', None),
    ]

    def parse(self, file_path, **kwargs):
        """
        Parse the file path as a 3DEqualizer .txt file.

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

        f = open(file_path, 'r')
        lines = f.readlines()
        f.close()
        if len(lines) == 0:
            raise OSError('No contents in the file: %s' % file_path)
        mkr_data_list = []

        lines = _remove_comments_from_lines(lines)

        line = lines[0]
        line = line.strip()
        num_points = _parse_int_or_none(line)
        if num_points is None:
            raise excep.ParserError('Invalid file format.')
        if num_points < 1:
            raise excep.ParserError('No points exist.')

        idx = 1  # Skip the first line
        for i in range(num_points):
            line = lines[idx]
            mkr_name = line.strip()

            # Create marker
            mkr_data = markerdata.MarkerData()
            mkr_data.set_name(mkr_name)

            # Get point color
            idx += 1
            line = lines[idx]
            line = line.strip()
            mkr_color = _parse_int_or_none(line)
            if mkr_color is None:
                raise excep.ParserError('Invalid file format.')
            mkr_data.set_color(mkr_color)

            idx += 1
            line = lines[idx]
            line = line.strip()
            num_frames = _parse_int_or_none(line)
            if num_frames is None:
                raise excep.ParserError('Invalid file format.')
            if num_frames <= 0:
                idx += 1
                msg = 'point has no data: %r'
                LOG.warning(msg, mkr_name)
                continue

            # Frame data parsing
            frames = []
            j = num_frames
            while j > 0:
                idx += 1
                line = lines[idx]
                line = line.strip()
                if len(line) == 0:
                    # Have we reached the end of the file?
                    break
                j = j - 1
                split = line.split()
                if len(split) != 3:
                    # We should not get here
                    msg = 'File invalid, there must be 3 numbers in line: %r'
                    raise excep.ParserError(msg % line)
                frame = _parse_int_or_none(split[0])
                pos_x = _parse_float_or_none(split[1])
                pos_y = _parse_float_or_none(split[2])
                if frame is None or pos_x is None or pos_y is None:
                    raise excep.ParserError('Invalid file format.')
                mkr_u = pos_x * inv_image_width
                mkr_v = pos_y * inv_image_height
                mkr_weight = 1.0

                mkr_data.weight.set_value(frame, mkr_weight)
                mkr_data.x.set_value(frame, mkr_u)
                mkr_data.y.set_value(frame, mkr_v)
                frames.append(frame)

            # Fill in occluded point frames
            all_frames = list(range(min(frames), max(frames) + 1))
            for frame in all_frames:
                mkr_enable = bool(frame in frames)
                mkr_data.enable.set_value(frame, int(mkr_enable))
                if mkr_enable is False:
                    mkr_data.weight.set_value(frame, 0.0)

            mkr_data_list.append(mkr_data)
            idx += 1

        file_info = fileinfo.create_file_info()
        return file_info, mkr_data_list


# Register the File Format
mgr = fmtmgr.get_format_manager()
mgr.register_format(Loader3DETXT)
