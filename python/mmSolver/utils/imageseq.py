# Copyright (C) 2022 David Cattermole.
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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import glob
import os

import mmSolver.logger
import mmSolver.utils.constant as const

LOG = mmSolver.logger.get_logger()


def _get_string_numbers_at_end(string_value):
    numbers = []
    for i in range(1, len(string_value) + 1):
        char = string_value[-i]
        if char.isdigit():
            numbers.insert(0, char)
        else:
            break
    if len(string_value) == len(numbers):
        # If the file name is only image numbers, it's not considered a valid
        # image sequence.
        return ''
    return ''.join(numbers)


def _split_image_sequence_path(file_path):
    head, tail = os.path.split(file_path)
    file_name, file_extension = os.path.splitext(tail)

    seq_num_int = 0
    seq_num_str = _get_string_numbers_at_end(file_name)
    if len(seq_num_str) > 0:
        file_name = file_name[: -len(seq_num_str)]
        seq_num_int = int(seq_num_str)
    return head, file_name, seq_num_int, seq_num_str, file_extension


def _get_image_sequence_start_end_frames(base_dir, file_name, file_extension):
    join_file_name = '{}*{}'.format(file_name, file_extension)
    glob_path = os.path.join(base_dir, join_file_name)
    # TODO: Only do this once and cache the results.
    all_paths = glob.iglob(glob_path)

    padding_num = 99
    start_frame = 9999999
    end_frame = 0
    count = 0
    for path in all_paths:
        (
            path_base_dir,
            path_file_name,
            path_seq_num_int,
            path_seq_num_str,
            path_file_extension,
        ) = _split_image_sequence_path(path)
        start_frame = min(path_seq_num_int, start_frame)
        end_frame = max(path_seq_num_int, end_frame)
        padding_num = min(padding_num, len(path_seq_num_str))
        count = count + 1

    if count <= 1:
        start_frame = 0
        end_frame = 0
        padding_num = 0

    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)
    assert isinstance(padding_num, int)
    return start_frame, end_frame, padding_num


def expand_image_sequence_path(image_sequence_path, format_style, exact_frame=None):
    """
    Expand a given image sequence path into tokens.

    Converts 'file.1001.png' into 'file.####.png', when format_style
    is IMAGE_SEQ_FORMAT_STYLE_HASH_PADDED.

    :param image_sequence_path: An existing file path.
    :type image_sequence_path: str

    :param format_style: What style this function should expand into?
    :type format_style: One of mmSolver.utils.constant.IMAGE_SEQ_FORMAT_STYLE_VALUES

    :param exact_frame: The frame number that will be expanded to when
        format_style IMAGE_SEQ_FORMAT_STYLE_EXACT_FRAME is used.
    :type exact_frame: None or int

    The tokens are:
      - file_pattern: str, the pattern of the file path.
      - start_frame: int, first frame of the image sequence.
      - end_frame: int, last frame of the image sequence.
      - padding_num: int, number of padding digits for the frame number.
      - is_seq: bool, is this a sequence? Otherwise it's a single frame.

    :returns:
        Tuple of (file_pattern, start_frame, end_frame, padding_num, is_seq)
    """
    assert os.path.isfile(image_sequence_path)
    assert format_style in const.IMAGE_SEQ_FORMAT_STYLE_VALUES
    assert exact_frame is None or isinstance(exact_frame, int)
    image_sequence_path = os.path.abspath(image_sequence_path)

    (
        base_dir,
        file_name,
        seq_num_int,
        seq_num_str,
        file_extension,
    ) = _split_image_sequence_path(image_sequence_path)

    start_frame, end_frame, padding_num = _get_image_sequence_start_end_frames(
        base_dir, file_name, file_extension
    )

    is_seq = start_frame != end_frame and padding_num > 0
    if is_seq is False:
        file_pattern = image_sequence_path
    else:
        image_seq_num = ''
        if format_style == const.IMAGE_SEQ_FORMAT_STYLE_MAYA:
            # file.<f>.png
            if padding_num > 0:
                image_seq_num = '<f>'
        elif format_style == const.IMAGE_SEQ_FORMAT_STYLE_HASH_PADDED:
            # file.####.png
            image_seq_num = '#' * padding_num
        elif format_style == const.IMAGE_SEQ_FORMAT_STYLE_PRINTF:
            # file.%04d.png
            if padding_num > 0:
                image_seq_num = '%0{}d'.format(padding_num)
        elif format_style == const.IMAGE_SEQ_FORMAT_STYLE_FIRST_FRAME:
            # file.1001.png
            image_seq_num = str(start_frame).zfill(padding_num)
        elif format_style == const.IMAGE_SEQ_FORMAT_STYLE_EXACT_FRAME:
            # file.0042.png (exact_frame == 42)
            #
            # Same as 'IMAGE_SEQ_FORMAT_STYLE_FIRST_FRAME', but allows
            # the user to give the frame value that will be used.
            frame = start_frame
            if exact_frame is not None:
                frame = exact_frame
            image_seq_num = str(frame).zfill(padding_num)
        else:
            raise NotImplementedError
        file_pattern = '{}{}{}'.format(file_name, image_seq_num, file_extension)
        file_pattern = os.path.join(base_dir, file_pattern)

    return file_pattern, start_frame, end_frame, padding_num, is_seq


def resolve_file_pattern_to_file_path(file_pattern, format_style, exact_frame=None):
    """
    Resolve a file pattern into a valid file path.

    Converts 'file.####.png' into 'file.1001.png', when format_style
    is IMAGE_SEQ_FORMAT_STYLE_HASH_PADDED.

    :param file_pattern: The pattern of the file path.
    :type file_pattern: str

    :param format_style: The format style of the input file pattern
    :type format_style: One of mmSolver.utils.constant.IMAGE_SEQ_FORMAT_STYLE_VALUES

    :param exact_frame: The frame number that will be expanded to.
        If None is given, the start_frame of the image sequence is used.
    :type exact_frame: None or int

    :returns: Valid file path or None.
    :rtype: str or None
    """
    assert format_style in const.IMAGE_SEQ_FORMAT_STYLE_VALUES
    assert isinstance(file_pattern, str)

    if os.path.isfile(file_pattern):
        file_pattern = os.path.abspath(file_pattern)
        return file_pattern

    if format_style == const.IMAGE_SEQ_FORMAT_STYLE_MAYA:
        # file.<f>.png
        file_pattern = file_pattern.replace('<f>', '')
    elif format_style == const.IMAGE_SEQ_FORMAT_STYLE_HASH_PADDED:
        # file.####.png
        file_pattern = file_pattern.replace('#', '')
    elif format_style == const.IMAGE_SEQ_FORMAT_STYLE_PRINTF:
        # file.%04d.png
        raise NotImplementedError
    elif format_style in [
        const.IMAGE_SEQ_FORMAT_STYLE_FIRST_FRAME,
        const.IMAGE_SEQ_FORMAT_STYLE_EXACT_FRAME,
    ]:
        # file.1001.png

        # Should have already been picked out as a valid file path, so
        # it must be wrong.
        return None
    else:
        raise NotImplementedError

    (
        base_dir,
        file_name,
        seq_num_int,
        seq_num_str,
        file_extension,
    ) = _split_image_sequence_path(file_pattern)

    start_frame, end_frame, padding_num = _get_image_sequence_start_end_frames(
        base_dir, file_name, file_extension
    )

    image_seq_num = str(start_frame).zfill(padding_num)
    file_pattern = '{}{}{}'.format(file_name, image_seq_num, file_extension)
    file_pattern = os.path.join(base_dir, file_pattern)

    file_path, _, _, _, _ = expand_image_sequence_path(
        file_pattern, const.IMAGE_SEQ_FORMAT_STYLE_EXACT_FRAME, exact_frame=exact_frame
    )
    return file_path
