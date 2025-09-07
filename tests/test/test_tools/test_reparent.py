# Copyright (C) 2019 David Cattermole.
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
Test functions for reparent tool.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.tools.reparent.lib as lib


# @unittest.skip
class TestReparent(test_tools_utils.ToolsTestCase):
    def create_scene_a(self):
        """
        Simple scene, two transforms, both without any keyframes.

        - A
        - B
        """
        tfm_a = maya.cmds.createNode('transform')
        maya.cmds.setAttr(tfm_a + '.translateX', 10.0)
        maya.cmds.setAttr(tfm_a + '.translateY', 20.0)
        maya.cmds.setAttr(tfm_a + '.translateZ', 30.0)
        tfm_node_a = tfm_utils.TransformNode(node=tfm_a)

        tfm_b = maya.cmds.createNode('transform')
        maya.cmds.setAttr(tfm_b + '.translateX', -10.0)
        maya.cmds.setAttr(tfm_b + '.translateY', -20.0)
        maya.cmds.setAttr(tfm_b + '.translateZ', -30.0)
        tfm_node_b = tfm_utils.TransformNode(node=tfm_b)
        return tfm_node_a, tfm_node_b

    def test_reparent_no_keyframes(self):
        """
        Transform node with no keyframes.
        """
        tfm_node_a, tfm_node_b = self.create_scene_a()
        tfm_nodes = lib.reparent(
            [tfm_node_a], tfm_node_b, sparse=True, delete_static_anim_curves=True
        )

        # save the output
        name = 'reparent_no_keyframes_after.ma'
        path = self.get_output_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(len(tfm_nodes), 1)
        new_tfm_node = tfm_nodes[0]
        new_parent = new_tfm_node.get_parent()
        self.assertEqual(tfm_node_b.get_node(), new_parent.get_node())
        return

    def create_scene_b(self):
        """
        Three transforms, 2 children under 1 parent.
        No keyframes.

        - A
          - B
          - C
        """
        tfm_a = maya.cmds.createNode('transform')
        maya.cmds.setAttr(tfm_a + '.translateX', 10.0)
        maya.cmds.setAttr(tfm_a + '.translateY', 20.0)
        maya.cmds.setAttr(tfm_a + '.translateZ', 30.0)
        tfm_node_a = tfm_utils.TransformNode(node=tfm_a)

        tfm_b = maya.cmds.createNode('transform', parent=tfm_a)
        maya.cmds.setAttr(tfm_b + '.translateX', -10.0)
        maya.cmds.setAttr(tfm_b + '.translateY', -20.0)
        maya.cmds.setAttr(tfm_b + '.translateZ', -30.0)
        tfm_node_b = tfm_utils.TransformNode(node=tfm_b)

        tfm_c = maya.cmds.createNode('transform', parent=tfm_a)
        maya.cmds.setAttr(tfm_b + '.translateX', -12.0)
        maya.cmds.setAttr(tfm_b + '.translateY', -22.0)
        maya.cmds.setAttr(tfm_b + '.translateZ', -32.0)
        tfm_node_c = tfm_utils.TransformNode(node=tfm_c)
        return tfm_node_a, tfm_node_b, tfm_node_c

    def test_unparent_no_keyframes(self):
        """
        Unparent to world, with no keyframes.
        """
        tfm_node_a, tfm_node_b, tfm_node_c = self.create_scene_b()
        tfm_nodes = lib.reparent(
            [tfm_node_b, tfm_node_c], None, sparse=True, delete_static_anim_curves=True
        )

        # save the output
        name = 'reparent_to_world_no_keyframes_after.ma'
        path = self.get_output_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(len(tfm_nodes), 2)
        for tfm_node in tfm_nodes:
            new_parent = tfm_node.get_parent()
            self.assertIs(new_parent, None)
        return

    def create_scene_c(self, start, end):
        """
        Simple scene, two transforms, both with keyframes.

        - A
        - B
        """
        maya.cmds.playbackOptions(edit=True, minTime=start)
        maya.cmds.playbackOptions(edit=True, animationStartTime=start)
        maya.cmds.playbackOptions(edit=True, animationEndTime=end)
        maya.cmds.playbackOptions(edit=True, maxTime=end)

        tfm_a = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm_a, attribute='translateX', value=10.0, time=start)
        maya.cmds.setKeyframe(tfm_a, attribute='translateY', value=20.0, time=start)
        maya.cmds.setKeyframe(tfm_a, attribute='translateZ', value=30.0, time=start)
        maya.cmds.setKeyframe(tfm_a, attribute='translateX', value=-10.0, time=end)
        maya.cmds.setKeyframe(tfm_a, attribute='translateY', value=-20.0, time=end)
        maya.cmds.setKeyframe(tfm_a, attribute='translateZ', value=-30.0, time=end)
        tfm_node_a = tfm_utils.TransformNode(node=tfm_a)

        tfm_b = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=-10.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=-20.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=-30.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=10.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=20.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=30.0, time=end)
        tfm_node_b = tfm_utils.TransformNode(node=tfm_b)
        return tfm_node_a, tfm_node_b

    def test_reparent_with_keyframes(self):
        """
        Transform node with keyframes.
        """
        start = 1001
        end = 1101
        tfm_node_a, tfm_node_b = self.create_scene_c(start, end)
        tfm_nodes = lib.reparent(
            [tfm_node_a], tfm_node_b, sparse=True, delete_static_anim_curves=True
        )

        # save the output
        name = 'reparent_with_keyframes_after.ma'
        path = self.get_output_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(len(tfm_nodes), 1)
        new_tfm_node = tfm_nodes[0]
        new_parent = new_tfm_node.get_parent()
        self.assertEqual(tfm_node_b.get_node(), new_parent.get_node())
        return

    def create_scene_d(self, start, end):
        """
        Three transforms, 2 transforms parented 1 parent.
        With keyframes.

        - A
          - B
          - C
        """
        tfm_a = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm_a, attribute='translateX', value=10.0, time=start)
        maya.cmds.setKeyframe(tfm_a, attribute='translateY', value=20.0, time=start)
        maya.cmds.setKeyframe(tfm_a, attribute='translateZ', value=30.0, time=start)
        maya.cmds.setKeyframe(tfm_a, attribute='translateX', value=-10.0, time=end)
        maya.cmds.setKeyframe(tfm_a, attribute='translateY', value=-20.0, time=end)
        maya.cmds.setKeyframe(tfm_a, attribute='translateZ', value=-30.0, time=end)
        tfm_node_a = tfm_utils.TransformNode(node=tfm_a)

        tfm_b = maya.cmds.createNode('transform', parent=tfm_a)
        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=30.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=20.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=10.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=-30.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=-20.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=-10.0, time=end)
        tfm_node_b = tfm_utils.TransformNode(node=tfm_b)

        tfm_c = maya.cmds.createNode('transform', parent=tfm_a)
        maya.cmds.setKeyframe(tfm_c, attribute='translateX', value=-32.0, time=start)
        maya.cmds.setKeyframe(tfm_c, attribute='translateY', value=-22.0, time=start)
        maya.cmds.setKeyframe(tfm_c, attribute='translateZ', value=-12.0, time=start)
        maya.cmds.setKeyframe(tfm_c, attribute='translateX', value=32.0, time=end)
        maya.cmds.setKeyframe(tfm_c, attribute='translateY', value=22.0, time=end)
        maya.cmds.setKeyframe(tfm_c, attribute='translateZ', value=12.0, time=end)
        tfm_node_c = tfm_utils.TransformNode(node=tfm_c)
        return tfm_node_a, tfm_node_b, tfm_node_c

    def test_unparent_to_world_with_keyframes(self):
        """
        Transform node with keyframes.
        """
        start = 1001
        end = 1101
        tfm_node_a, tfm_node_b, tfm_node_c = self.create_scene_d(start, end)
        tfm_nodes = lib.reparent(
            [tfm_node_b, tfm_node_c], None, sparse=True, delete_static_anim_curves=True
        )

        # save the output
        name = 'reparent_to_world_with_keyframes_after.ma'
        path = self.get_output_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(len(tfm_nodes), 2)
        for tfm_node in tfm_nodes:
            new_parent = tfm_node.get_parent()
            self.assertIs(new_parent, None)
        return

    def test_reparent_unparent_with_sparse_keyframes(self):
        name = 'reparent_sparse_keyframes.ma'
        path = self.get_data_path('scenes', name)
        maya.cmds.file(path, open=True, force=True)

        tfm_a = 'pSphere1'
        tfm_b = 'pCube1'
        tfm_node_a = tfm_utils.TransformNode(node=tfm_a)
        tfm_node_b = tfm_utils.TransformNode(node=tfm_b)

        # Parent sphere under cube.
        tfm_nodes = lib.reparent(
            [tfm_node_a], tfm_node_b, sparse=True, delete_static_anim_curves=True
        )
        tfm_node_c = tfm_nodes[0]

        node = tfm_node_c.get_node()
        plug = node + '.translateX'
        times = maya.cmds.keyframe(plug, query=True, timeChange=True)
        self.assertEqual(len(times), 5)
        self.assertEqual(sorted(times), sorted([1, 16, 61, 98, 120]))
        self.assertEqual(len(tfm_nodes), 1)
        new_parent = tfm_node_a.get_parent()
        self.assertEqual(new_parent, tfm_node_b)

        # Unparent sphere to world
        tfm_nodes = lib.reparent(
            [tfm_node_c], None, sparse=True, delete_static_anim_curves=True
        )
        tfm_node_d = tfm_nodes[0]

        # save the output
        name = 'reparent_unparent_sparse_with_keyframes_after.ma'
        path = self.get_output_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        node = tfm_node_d.get_node()
        plug = node + '.translateX'
        times = maya.cmds.keyframe(plug, query=True, timeChange=True)
        self.assertEqual(len(times), 5)
        self.assertEqual(sorted(times), sorted([1, 16, 61, 98, 120]))
        self.assertEqual(len(tfm_nodes), 1)
        new_parent = tfm_node_a.get_parent()
        self.assertIs(new_parent, None)


if __name__ == '__main__':
    prog = unittest.main()
