"""
Test functions for loadmarker tool module.
"""

import sys
import os
import unittest

import maya.cmds
import maya.OpenMaya as OpenMaya

import test.test_tools.toolsutils as test_tools_utils
import mmSolver.tools.loadmarker.readfile as marker_read


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


if __name__ == '__main__':
    prog = unittest.main()
