# Copyright (C) 2020 David Cattermole.
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
Test functions for copypastecamera tool.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import unittest

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils
import mmSolver.tools.copypastecamera.lib as lib


def get_path_start():
    path_start = os.sep
    if os.name == 'nt':
        path_start = 'C:\\'
    return path_start


# @unittest.skip
class TestCopyPasteCamera(test_tools_utils.ToolsTestCase):
    def test_get_image_path_tokens(self):
        path_start = get_path_start()

        # Single file path, without a frame extension.
        path = os.path.join(path_start, 'path', 'to', 'file.jpg')
        data = lib.get_image_path_tokens(path)
        self.assertEqual(data, None)

        # Multi-file path, with a frame extension.
        path = os.path.join(path_start, 'path', 'to', 'file.1001.jpg')
        data = lib.get_image_path_tokens(path)
        self.assertNotEqual(data, None)
        self.assertIn('name', data)
        self.assertIn('frame', data)
        self.assertIn('ext', data)
        self.assertEqual(data['name'], 'file')
        self.assertEqual(data['frame'], '1001')
        self.assertEqual(data['ext'], 'jpg')
        return

    def test_get_image_path_pattern(self):
        path_start = get_path_start()

        # Single file path, without a frame extension.
        path = os.path.join(path_start, 'path', 'to', 'file.jpg')

        # No frame extension, but with use_frame_ext=True.
        use_frame_ext = True
        image_file_path, multi_frame = lib.get_image_path_pattern(
            path, use_frame_ext, test_disk=False
        )
        self.assertEqual(image_file_path, path)
        self.assertEqual(multi_frame, False)

        # No frame extension, but with use_frame_ext=False. Same
        # result as above.
        use_frame_ext = False
        image_file_path, multi_frame = lib.get_image_path_pattern(
            path, use_frame_ext, test_disk=False
        )
        self.assertEqual(image_file_path, path)
        self.assertEqual(multi_frame, False)

        # With frame extension - padded with variable number of digits.
        use_frame_ext = True
        frame_num = 9
        padding = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 20]
        frame_sep_chars = ['.', '_']  # 'file.1001.jpg' and 'file_1001.jpg'.
        for frame_sep_char in frame_sep_chars:
            for pad_length in padding:
                # Construct file name.
                file_name_format = 'file' + frame_sep_char
                file_name_format += '{0:0' + str(pad_length) + 'd}'
                file_name_format += '.jpg'
                file_name = file_name_format.format(frame_num)

                # Construct expected file name.
                pad_string = '#' * pad_length
                expected_file_name = 'file{0}{1}.jpg'.format(frame_sep_char, pad_string)

                # Test the function
                path = os.path.join(path_start, 'path', 'to', file_name)
                image_file_path, multi_frame = lib.get_image_path_pattern(
                    path, use_frame_ext, test_disk=False
                )
                expected_path = os.path.join(
                    path_start, 'path', 'to', expected_file_name
                )
                self.assertEqual(image_file_path, expected_path)
                self.assertEqual(multi_frame, True)
        return

    def test_get_image_path_pattern_issue161(self):
        """
        Test image paths with '#', '?' or '*' characters in them.

        GitHub issue #161.
        """
        path_start = get_path_start()

        paths = [
            (
                os.path.join(path_start, 'path', 'to', 'file.1001.jpg'),
                os.path.join(path_start, 'path', 'to', 'file.####.jpg'),
            ),
            (
                os.path.join(path_start, 'path', 'to', 'file.####.jpg'),
                os.path.join(path_start, 'path', 'to', 'file.####.jpg'),
            ),
            (
                os.path.join(path_start, 'path', 't#o', 'file.####.jpg'),
                os.path.join(path_start, 'path', 't#o', 'file.####.jpg'),
            ),
            (
                os.path.join(path_start, 'path', 'to', 'file?.####.jpg'),
                os.path.join(path_start, 'path', 'to', 'file?.####.jpg'),
            ),
            (
                os.path.join(path_start, 'path', 'to', 'file*.####.jpg'),
                os.path.join(path_start, 'path', 'to', 'file*.####.jpg'),
            ),
        ]
        use_frame_ext = True
        for path, expected_path in paths:
            image_file_path, multi_frame = lib.get_image_path_pattern(
                path, use_frame_ext, test_disk=False
            )
            self.assertEqual(image_file_path, expected_path)
            self.assertEqual(multi_frame, True)
        return


if __name__ == '__main__':
    prog = unittest.main()
