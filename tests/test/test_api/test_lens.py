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
Test functions for lens module.
"""

import sys
import os
import unittest

import maya.cmds


import test.test_api.apiutils as test_api_utils
import mmSolver.utils.node as node_utils
import mmSolver._api.lens as mod


# @unittest.skip
class TestLens(test_api_utils.APITestCase):
    def test_init(self):
        x = mod.Lens()
        x_node = x.get_node()
        self.assertEqual(x_node, None)

        # Create nodes
        lens_node = maya.cmds.createNode('mmLensBasic', name='myLens1')

        y = mod.Lens(node=lens_node)
        y_node = y.get_node()
        self.assertTrue(maya.cmds.objExists(y_node))
        self.assertEqual(y_node, lens_node)

        z1 = mod.Lens(node=lens_node)
        z1_node = z1.get_node()
        self.assertEqual(z1_node, lens_node)

    # def test_create_node(self):
    #     pass

    # def test_change_node_type(self):
    #     pass

    # def test_set_camera(self):
    #     pass

    # def test_set_input_lens(self):
    #     pass


if __name__ == '__main__':
    prog = unittest.main()
