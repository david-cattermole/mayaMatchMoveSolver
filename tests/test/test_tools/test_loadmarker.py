# Copyright (C) 2018, 2019 David Cattermole.
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
Test functions for loadmarker tool module.
"""

import unittest

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils
import mmSolver.tools.loadmarker.lib.mayareadfile as marker_read


# @unittest.skip
class TestLoadMarker(test_tools_utils.ToolsTestCase):
    def test_loadmarker_rz2_format(self):
        mkr_data_list = []
        paths = [
            self.get_data_path('match_mover', 'loadmarker.rz2'),
            self.get_data_path('match_mover', 'loadmarker_corners.rz2'),
            # self.get_data_path('match_mover', '2dtracks.rz2'),
            # self.get_data_path('match_mover', 'cha_171_1020_atb_v001.rz2'),
            # self.get_data_path('match_mover', 'EP_1000_head_trackers_v002.rz2'),
            # self.get_data_path('match_mover', 'kipPointsMatchmover.rz2'),
            # self.get_data_path('match_mover', 'NonSequentialMatchmoverPoints.rz2'),
        ]
        for path in paths:
            tmp_list = marker_read.read(path)
            mkr_data_list += tmp_list

        # create the markers
        num_nodes1 = len(maya.cmds.ls())
        marker_read.create_nodes(mkr_data_list)
        num_nodes2 = len(maya.cmds.ls())
        self.assertGreater(num_nodes2, num_nodes1)

        self.assertTrue(maya.cmds.objExists('TopLeft_MKR'))
        self.assertEqual(maya.cmds.getAttr('TopLeft_MKR.translateX'), -0.5)
        self.assertEqual(maya.cmds.getAttr('TopLeft_MKR.translateY'), 0.5)

        self.assertTrue(maya.cmds.objExists('TopRight_MKR'))
        self.assertEqual(maya.cmds.getAttr('TopRight_MKR.translateX'), 0.5)
        self.assertEqual(maya.cmds.getAttr('TopRight_MKR.translateY'), 0.5)

        self.assertTrue(maya.cmds.objExists('BottomLeft_MKR'))
        self.assertEqual(maya.cmds.getAttr('BottomLeft_MKR.translateX'), -0.5)
        self.assertEqual(maya.cmds.getAttr('BottomLeft_MKR.translateY'), -0.5)

        self.assertTrue(maya.cmds.objExists('BottomRight_MKR'))
        self.assertEqual(maya.cmds.getAttr('BottomRight_MKR.translateX'), 0.5)
        self.assertEqual(maya.cmds.getAttr('BottomRight_MKR.translateY'), -0.5)

    def test_loadmarker_uvtrack_format(self):
        """
        Test loading markers using the '.uv' format.
        """
        mkr_data_list = []
        paths = [
            self.get_data_path('uvtrack', 'test_v1.uv'),
            self.get_data_path('uvtrack', 'loadmarker_corners.uv'),
            self.get_data_path('uvtrack', 'cameraTrackRnD.uv'),
            self.get_data_path('uvtrack', 'stA.uv'),
            self.get_data_path('uvtrack', 'stA_with_emptyMarker.uv'),
            self.get_data_path('uvtrack', 'eye_fmt1_v001.uv'),
            self.get_data_path('uvtrack', 'eye_fmt2_v001.uv'),
        ]
        for path in paths:
            print('Reading... %r' % path)
            tmp_list = marker_read.read(path)
            self.assertNotEqual(tmp_list, None)
            mkr_data_list += tmp_list

        # Create the markers
        num_nodes1 = len(maya.cmds.ls())
        marker_read.create_nodes(mkr_data_list)
        num_nodes2 = len(maya.cmds.ls())
        self.assertGreater(num_nodes2, num_nodes1)

        self.assertTrue(maya.cmds.objExists('TopLeft_MKR'))
        self.assertEqual(maya.cmds.getAttr('TopLeft_MKR.translateX'), -0.5)
        self.assertEqual(maya.cmds.getAttr('TopLeft_MKR.translateY'), 0.5)

        self.assertTrue(maya.cmds.objExists('TopRight_MKR'))
        self.assertEqual(maya.cmds.getAttr('TopRight_MKR.translateX'), 0.5)
        self.assertEqual(maya.cmds.getAttr('TopRight_MKR.translateY'), 0.5)

        self.assertTrue(maya.cmds.objExists('BottomLeft_MKR'))
        self.assertEqual(maya.cmds.getAttr('BottomLeft_MKR.translateX'), -0.5)
        self.assertEqual(maya.cmds.getAttr('BottomLeft_MKR.translateY'), -0.5)

        self.assertTrue(maya.cmds.objExists('BottomRight_MKR'))
        self.assertEqual(maya.cmds.getAttr('BottomRight_MKR.translateX'), 0.5)
        self.assertEqual(maya.cmds.getAttr('BottomRight_MKR.translateY'), -0.5)

    def test_loadmarker_tdetxt_format(self):
        """
        Test loading markers using the '.uv' format.
        """
        mkr_data_list = []
        paths = [
            (self.get_data_path('3de_v4', 'loadmarker_corners.txt'), (1920.0, 1080.0)),
            # (self.get_data_path('3de_v4', '3de_export_cube.txt'), (1920.0, 1080.0)),
            # (self.get_data_path('3de_v4', 'FB1880_man_v05.txt'), (1920.0, 1080.0)),
        ]
        for path, res in paths:
            print('Reading... %r' % path)
            tmp_list = marker_read.read(
                path,
                image_width=res[0],
                image_height=res[1]
            )
            self.assertNotEqual(tmp_list, None)
            mkr_data_list += tmp_list

        # Create the markers
        num_nodes1 = len(maya.cmds.ls())
        marker_read.create_nodes(mkr_data_list)
        num_nodes2 = len(maya.cmds.ls())
        self.assertGreater(num_nodes2, num_nodes1)

        self.assertTrue(maya.cmds.objExists('TopLeft_MKR'))
        self.assertEqual(maya.cmds.getAttr('TopLeft_MKR.translateX'), -0.5)
        self.assertEqual(maya.cmds.getAttr('TopLeft_MKR.translateY'), 0.5)

        self.assertTrue(maya.cmds.objExists('TopRight_MKR'))
        self.assertEqual(maya.cmds.getAttr('TopRight_MKR.translateX'), 0.5)
        self.assertEqual(maya.cmds.getAttr('TopRight_MKR.translateY'), 0.5)

        self.assertTrue(maya.cmds.objExists('BottomLeft_MKR'))
        self.assertEqual(maya.cmds.getAttr('BottomLeft_MKR.translateX'), -0.5)
        self.assertEqual(maya.cmds.getAttr('BottomLeft_MKR.translateY'), -0.5)

        self.assertTrue(maya.cmds.objExists('BottomRight_MKR'))
        self.assertEqual(maya.cmds.getAttr('BottomRight_MKR.translateX'), 0.5)
        self.assertEqual(maya.cmds.getAttr('BottomRight_MKR.translateY'), -0.5)


if __name__ == '__main__':
    prog = unittest.main()
