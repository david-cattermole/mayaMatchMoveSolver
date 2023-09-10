# Copyright (C) 2019, 2020, 2022 David Cattermole.
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
Test functions for createcontroller2 tool.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils
import mmSolver.tools.createcontroller2.lib as lib
import mmSolver.tools.createcontroller2.constant as const


# @unittest.skip
class TestCreateController2(test_tools_utils.ToolsTestCase):
    def create_no_keyframe_scene(self):
        tfm = maya.cmds.createNode('transform')
        maya.cmds.setAttr(tfm + '.translateX', 10.0)
        maya.cmds.setAttr(tfm + '.translateY', 20.0)
        maya.cmds.setAttr(tfm + '.translateZ', 30.0)
        return tfm

    def create_no_keyframe_scene_with_pivot(self):
        tfm = maya.cmds.createNode('transform')
        maya.cmds.setAttr(tfm + '.translateX', 10.0)
        maya.cmds.setAttr(tfm + '.translateY', 20.0)
        maya.cmds.setAttr(tfm + '.translateZ', 30.0)

        pivot = (-10.0, -20.0, -30.0)
        maya.cmds.setAttr(tfm + '.rotatePivotX', pivot[0])
        maya.cmds.setAttr(tfm + '.rotatePivotY', pivot[1])
        maya.cmds.setAttr(tfm + '.rotatePivotZ', pivot[2])
        maya.cmds.setAttr(tfm + '.scalePivotX', pivot[0])
        maya.cmds.setAttr(tfm + '.scalePivotY', pivot[1])
        maya.cmds.setAttr(tfm + '.scalePivotZ', pivot[2])
        return tfm

    def create_one_keyframe_scene(self):
        tfm = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm, attribute='translateX', value=10.0)
        maya.cmds.setKeyframe(tfm, attribute='translateY', value=20.0)
        maya.cmds.setKeyframe(tfm, attribute='translateZ', value=30.0)
        return tfm

    def create_multi_keyframe_scene(self, start, mid, end):
        maya.cmds.playbackOptions(edit=True, minTime=start)
        maya.cmds.playbackOptions(edit=True, animationStartTime=start)
        maya.cmds.playbackOptions(edit=True, animationEndTime=end)
        maya.cmds.playbackOptions(edit=True, maxTime=end)

        tfm = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm, attribute='translateX', value=10.0, time=start)
        maya.cmds.setKeyframe(tfm, attribute='translateY', value=20.0, time=start)
        maya.cmds.setKeyframe(tfm, attribute='translateZ', value=30.0, time=start)
        maya.cmds.setKeyframe(tfm, attribute='rotateY', value=45.0, time=start)

        maya.cmds.setKeyframe(tfm, attribute='translateX', value=20.0, time=mid)
        maya.cmds.setKeyframe(tfm, attribute='translateY', value=30.0, time=mid)
        maya.cmds.setKeyframe(tfm, attribute='translateZ', value=10.0, time=mid)

        maya.cmds.setKeyframe(tfm, attribute='translateX', value=30.0, time=end)
        maya.cmds.setKeyframe(tfm, attribute='translateY', value=10.0, time=end)
        maya.cmds.setKeyframe(tfm, attribute='translateZ', value=20.0, time=end)
        maya.cmds.setKeyframe(tfm, attribute='rotateY', value=-60.0, time=end)
        return tfm

    def create_hierarchy_scene(self, start, end):
        maya.cmds.playbackOptions(edit=True, minTime=start)
        maya.cmds.playbackOptions(edit=True, animationStartTime=start)
        maya.cmds.playbackOptions(edit=True, animationEndTime=end)
        maya.cmds.playbackOptions(edit=True, maxTime=end)

        tfm_a = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm_a, attribute='translateY', value=20.0, time=start)
        maya.cmds.setKeyframe(tfm_a, attribute='rotateY', value=345.0, time=start)

        maya.cmds.setKeyframe(tfm_a, attribute='translateY', value=10.0, time=end)
        maya.cmds.setKeyframe(tfm_a, attribute='rotateY', value=-360.0, time=end)

        tfm_b = maya.cmds.createNode('transform', parent=tfm_a)
        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=10.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=20.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=30.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='rotateY', value=45.0, time=start)

        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=30.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=10.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=20.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='rotateY', value=-60.0, time=end)

        maya.cmds.createNode('transform', parent=tfm_a)
        maya.cmds.createNode('transform', parent=tfm_b)
        return tfm_a, tfm_b

    def run_tool(
        self, name, pivot_node, main_node, camera_tfm_node, start_frame, end_frame
    ):
        """
        Runs the given nodes with all The combination of options
        that the tool can take.
        """
        smart_bakes = [False, True]
        dynamic_pivots = [False, True]
        controller_spaces = const.CONTROLLER_SPACE_LIST
        for smart_bake in smart_bakes:
            for dynamic_pivot in dynamic_pivots:
                for controller_space in controller_spaces:
                    loc_grp_nodes = maya.cmds.spaceLocator(name=name)
                    ctrls = lib.create_controller(
                        name,
                        pivot_node,
                        main_node,
                        loc_grp_nodes,
                        start_frame,
                        end_frame,
                        controller_space,
                        smart_bake=smart_bake,
                        camera=camera_tfm_node,
                        dynamic_pivot=dynamic_pivot,
                    )
                    lib.remove_controller(ctrls[0], start_frame, end_frame)

    def test_no_keyframe(self):
        """
        Create/Remove Controller node with no keyframes.
        """
        tfm = self.create_no_keyframe_scene()

        name = 'controller'
        camera_tfm_node = '|persp'
        start_frame = 1
        end_frame = 100
        self.run_tool(name, tfm, tfm, camera_tfm_node, start_frame, end_frame)
        return

    def test_one_keyframe(self):
        """
        Create/Remove Controller node with a single keyframe.
        """
        tfm = self.create_one_keyframe_scene()

        name = 'controller'
        camera_tfm_node = '|persp'
        start_frame = 1
        end_frame = 100
        self.run_tool(name, tfm, tfm, camera_tfm_node, start_frame, end_frame)
        return

    def test_three_keyframes(self):
        """
        Create/Remove Controller node with three keyframes.
        """
        start = 1
        mid = 25
        end = 100
        tfm = self.create_multi_keyframe_scene(start, mid, end)

        name = 'controller'
        camera_tfm_node = '|persp'
        start_frame = 1
        end_frame = 100
        self.run_tool(name, tfm, tfm, camera_tfm_node, start_frame, end_frame)
        return

    def test_hierarchy(self):
        """
        Create/Remove Controller node in a hierarchy.
        """
        start = 1
        end = 100
        tfm_a, tfm_b = self.create_hierarchy_scene(start, end)

        name = 'controller'
        camera_tfm_node = '|persp'
        start_frame = 1
        end_frame = 100
        self.run_tool(name, tfm_a, tfm_a, camera_tfm_node, start_frame, end_frame)
        self.run_tool(name, tfm_b, tfm_b, camera_tfm_node, start_frame, end_frame)
        return

    def test_object_hierarchy(self):
        """
        Create and destroy controllers on a hierarchy of transforms.
        """
        path = self.get_data_path('scenes', 'objectHierarchy.ma')
        maya.cmds.file(path, open=True, force=True)

        tfm_a = 'group1'
        tfm_b = 'pSphere1'
        tfm_c = 'pSphere2'

        name = 'controller'
        camera_tfm_node = '|persp'
        start_frame = 1
        end_frame = 100
        self.run_tool(name, tfm_a, tfm_a, camera_tfm_node, start_frame, end_frame)
        self.run_tool(name, tfm_b, tfm_b, camera_tfm_node, start_frame, end_frame)
        self.run_tool(name, tfm_c, tfm_c, camera_tfm_node, start_frame, end_frame)
        return


if __name__ == '__main__':
    prog = unittest.main()
