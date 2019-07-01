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
Test functions for createcontroller tool.
"""

import unittest

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils
import mmSolver.tools.createcontroller.lib as lib


# @unittest.skip
class TestCreateController(test_tools_utils.ToolsTestCase):
    def test_create_one(self):
        """
        Transform node with no keyframes.
        """
        tfm = maya.cmds.createNode('transform')
        maya.cmds.setAttr(tfm + '.translateX', 10.0)
        maya.cmds.setAttr(tfm + '.translateY', 20.0)
        maya.cmds.setAttr(tfm + '.translateZ', 30.0)
        ctrls = lib.create([tfm])
        ctrl = ctrls[0]

        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateX'), 10.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateY'), 20.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateZ'), 30.0)
        return

    def test_create_two(self):
        """
        Transform node with a single keyframe.
        """
        tfm = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm, attribute='translateX', value=10.0)
        maya.cmds.setKeyframe(tfm, attribute='translateY', value=20.0)
        maya.cmds.setKeyframe(tfm, attribute='translateZ', value=30.0)
        ctrls = lib.create([tfm])
        ctrl = ctrls[0]

        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateX'), 10.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateY'), 20.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateZ'), 30.0)
        return


if __name__ == '__main__':
    prog = unittest.main()
