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
Solve a single non-animated bundle to the screen-space location of a bundle.

This test is the same as 'test.test_solver.test1' except this test uses the
Python API. It's a basic example of how to use the API.
"""

import time
import pprint
import math
import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.animcurve as anim_utils
import mmSolver.api as mmapi
import mmSolver._api.rootframe as mod
import mmSolver.tools.loadmarker.lib.mayareadfile as marker_read

import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestRootFrame(test_api_utils.APITestCase):

    def test_get_root_frames_from_markers_1(self):
        # Time Range
        start = 1001
        end = 1101
        maya.cmds.playbackOptions(
            animationStartTime=start, minTime=start,
            animationEndTime=end, maxTime=end)

        # Create Camera and Marker Group
        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        cam = mmapi.Camera(shape=cam_shp)
        mkr_grp = mmapi.MarkerGroup().create_node(cam=cam)

        # Marker A
        mkr_a = mmapi.Marker().create_node()
        mkr_a_node = mkr_a.get_node()
        times = [1000, 1001, 1101, 1102]
        values = [0, 1, 1, 0]
        anim_utils.create_anim_curve_node_apione(
            times, values, mkr_a_node + '.enable')

        # Calculate Root Frames
        min_frames_per_marker = 2
        mkr_list = [mkr_a]
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        frame_nums = mod.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame)
        print 'frames:', frame_nums
        return

    def test_get_root_frames_from_markers_2(self):
        # Time Range
        start = 1001
        end = 1101
        maya.cmds.playbackOptions(
            animationStartTime=start, minTime=start,
            animationEndTime=end, maxTime=end)

        # Create Camera and Marker Group
        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        cam = mmapi.Camera(shape=cam_shp)
        mkr_grp = mmapi.MarkerGroup().create_node(cam=cam)

        # Marker A
        mkr_a = mmapi.Marker().create_node()
        mkr_a_node = mkr_a.get_node()
        times = [1000, 1001, 1101, 1102]
        values = [0, 1, 1, 0]
        anim_utils.create_anim_curve_node_apione(
            times, values, mkr_a_node + '.enable')

        # Marker B
        mkr_b = mmapi.Marker().create_node()
        mkr_b_node = mkr_b.get_node()
        times = [1000, 1001, 1051, 1052]
        values = [0, 1, 1, 0]
        anim_utils.create_anim_curve_node_apione(
            times, values, mkr_b_node + '.enable')

        # Marker C
        mkr_c = mmapi.Marker().create_node()
        mkr_c_node = mkr_c.get_node()
        times = [1050, 1051, 1101, 1102]
        values = [0, 1, 1, 0]
        anim_utils.create_anim_curve_node_apione(
            times, values, mkr_c_node + '.enable')

        # Calculate Root Frames
        min_frames_per_marker = 2
        mkr_list = [mkr_a, mkr_b, mkr_c]
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        frame_nums = mod.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame)
        print 'frames:', frame_nums
        return

    def test_get_root_frames_from_markers_3(self):
        # Time Range
        start = 0
        end = 41
        maya.cmds.playbackOptions(
            animationStartTime=start, minTime=start,
            animationEndTime=end, maxTime=end)

        # Create Camera
        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        cam = mmapi.Camera(shape=cam_shp)

        # Create image plane
        path = self.get_data_path('operahouse', 'frame00.jpg')
        imgpl = maya.cmds.imagePlane(
            camera=cam_shp,
            fileName=path
        )
        maya.cmds.setAttr(imgpl[1] + '.useFrameExtension', 1)

        # Load Marker Data
        path = self.get_data_path('match_mover', 'loadmarker.rz2')
        _, mkr_data_list = marker_read.read(path)

        # Create Markers
        mkr_grp = mmapi.MarkerGroup().create_node(cam=cam)
        mkr_list = marker_read.create_nodes(
            mkr_data_list,
            cam=cam,
            mkr_grp=mkr_grp
        )

        # Calculate Root Frames
        min_frames_per_marker = 3
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        frame_nums = mod.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame)
        print 'frames:', frame_nums
        return

if __name__ == '__main__':
    prog = unittest.main()
