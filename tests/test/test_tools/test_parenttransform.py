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
Test functions for parenttransform tool.
"""

import unittest

import maya.cmds
import maya.debug.closeness as closeness

import test.test_tools.toolsutils as test_tools_utils
import mmSolver.tools.parenttransform.lib as lib


# @unittest.skip
class TestParentTransform(test_tools_utils.ToolsTestCase):

    def create_zero_keyframe_scene(self):
        tfm_a = maya.cmds.createNode('transform', name='tfm_a')
        tfm_b = maya.cmds.createNode('transform', name='tfm_b', parent=tfm_a)
        maya.cmds.setAttr(tfm_b + '.translateX', 10.0)
        maya.cmds.setAttr(tfm_b + '.translateY', 20.0)
        maya.cmds.setAttr(tfm_b + '.translateZ', 30.0)
        tfm_c = maya.cmds.createNode('transform', name='tfm_c')
        return tfm_a, tfm_b, tfm_c

    def create_one_keyframe_scene(self):
        tfm_a = maya.cmds.createNode('transform', name='tfm_a')
        tfm_b = maya.cmds.createNode('transform', name='tfm_b', parent=tfm_a)
        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=10.0)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=20.0)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=30.0)
        tfm_c = maya.cmds.createNode('transform', name='tfm_c')
        return tfm_a, tfm_b, tfm_c

    def create_two_keyframe_scene(self, startFrame, endFrame):
        tfm_a = maya.cmds.createNode('transform', name='tfm_a')
        tfm_b = maya.cmds.createNode('transform', name='tfm_b', parent=tfm_a)
        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=10.0, time=startFrame)
        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=20.0, time=endFrame)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=20.0, time=startFrame)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=30.0, time=endFrame)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=30.0, time=startFrame)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=10.0, time=endFrame)
        tfm_c = maya.cmds.createNode('transform', name='tfm_c')
        return tfm_a, tfm_b, tfm_c

    def test_one(self):
        """
        Create a hierarchy with no keyframes set, and parent then unparent.
        """
        tfm_a, tfm_b, tfm_c = self.create_zero_keyframe_scene()
        ctrls = lib.parent([tfm_b, tfm_a], tfm_c)
        ctrl_b, ctrl_a = ctrls
        # print 'ctrl_a', ctrl_a
        # print 'ctrl_b', ctrl_b

        maya.cmds.setKeyframe(ctrl_b, attribute='translateY', value=42.0)

        # save the output
        path = self.get_data_path('parenttransform_one_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        node_a, node_b = lib.unparent([ctrl_a, ctrl_b])
        # print 'node_a', node_a
        # print 'node_b', node_b

        # save the output
        path = self.get_data_path('parenttransform_one_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(maya.cmds.getAttr(node_b + '.translateX'), 10.0)
        self.assertEqual(maya.cmds.getAttr(node_b + '.translateY'), 42.0)
        self.assertEqual(maya.cmds.getAttr(node_b + '.translateZ'), 30.0)
        return

    def test_two(self):
        """
        Create a hierarchy with one keyframes set, and parent then unparent.
        """
        tfm_a, tfm_b, tfm_c = self.create_one_keyframe_scene()
        ctrls = lib.parent([tfm_b, tfm_a], tfm_c)
        ctrl_b, ctrl_a = ctrls
        # print 'ctrl_a', ctrl_a
        # print 'ctrl_b', ctrl_b

        maya.cmds.setKeyframe(ctrl_b, attribute='translateY', value=42.0)

        # save the output
        path = self.get_data_path('parenttransform_two_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        node_a, node_b = lib.unparent([ctrl_a, ctrl_b])
        # print 'node_a', node_a
        # print 'node_b', node_b

        # save the output
        path = self.get_data_path('parenttransform_two_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(maya.cmds.getAttr(node_b + '.translateX'), 10.0)
        self.assertEqual(maya.cmds.getAttr(node_b + '.translateY'), 42.0)
        self.assertEqual(maya.cmds.getAttr(node_b + '.translateZ'), 30.0)
        return

    def test_three(self):
        """
        Create a hierarchy with one keyframes set, and parent then unparent.
        """
        startFrame = 1
        endFrame = 24
        tfm_a, tfm_b, tfm_c = self.create_two_keyframe_scene(startFrame, endFrame)
        # print 'tfm_a', tfm_a
        # print 'tfm_b', tfm_b
        # print 'tfm_c', tfm_c

        ctrls = lib.parent([tfm_a, tfm_b], tfm_c)
        ctrl_a, ctrl_b = ctrls
        # print 'ctrl_a', ctrl_a
        # print 'ctrl_b', ctrl_b

        maya.cmds.setKeyframe(ctrl_b, attribute='translateY', value=42.0, time=endFrame)

        # save the output
        path = self.get_data_path('parenttransform_three_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        node_a, node_b = lib.unparent([ctrl_a, ctrl_b])
        # print 'node_a', node_a
        # print 'node_b', node_b

        # save the output
        path = self.get_data_path('parenttransform_three_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        maya.cmds.currentTime(endFrame, update=True)
        self.assertEqual(maya.cmds.getAttr(node_b + '.translateX'), 20.0)
        self.assertEqual(maya.cmds.getAttr(node_b + '.translateY'), 42.0)
        self.assertEqual(maya.cmds.getAttr(node_b + '.translateZ'), 10.0)
        return


if __name__ == '__main__':
    prog = unittest.main()
