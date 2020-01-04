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
Test functions for bundle module.
"""

import sys
import os
import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver._api.utils as api_utils
import mmSolver._api.bundle as bundle
import mmSolver._api.marker as marker


# @unittest.skip
class TestBundle(test_api_utils.APITestCase):
    def test_init(self):
        x = bundle.Bundle()
        x_node = x.get_node()
        self.assertEqual(x_node, None)

        # Create nodes
        y = bundle.Bundle().create_node()
        y_node = y.get_node()
        self.assertTrue(maya.cmds.objExists(y_node))
        self.assertEqual(y_node, '|bundle1')

        # Create nodes (again, with explicit node name)
        y = bundle.Bundle().create_node(name='myBundle1')
        y_node = y.get_node()
        self.assertTrue(maya.cmds.objExists(y_node))
        self.assertEqual(y_node, '|myBundle1')

        # Set Node via __init__
        z = bundle.Bundle(node=y_node)
        z_node = z.get_node()
        self.assertEqual(z_node, y_node)
        self.assertEqual(z_node, '|myBundle1')

        # Set Node via set_node
        x.set_node(y_node)
        x_node = x.get_node()
        self.assertEqual(x_node, y_node)

    def test_set_colour_rgb(self):
        """
        Set wireframe colour of the bundle.
        """
        green = (0.0, 1.0, 0.0)
        blue = (0.0, 0.0, 1.0)

        x = bundle.Bundle()
        x_rgb = x.get_colour_rgb()
        self.assertEqual(x_rgb, None)

        # Create nodes
        y = bundle.Bundle().create_node(name='myBundle1')
        y_rgb = y.get_colour_rgb()
        self.assertEqual(y_rgb, green)

        y.set_colour_rgb(blue)
        y_rgb = y.get_colour_rgb()
        self.assertEqual(y_rgb, blue)
        return

    def test_get_marker_list(self):
        x = bundle.Bundle().create_node(name='myBundle1')
        mkr_list1 = x.get_marker_list()
        self.assertEqual(len(mkr_list1), 0)

        for i in xrange(10):
            mkr = marker.Marker().create_node()
            mkr.set_bundle(x)
        mkr_list2 = x.get_marker_list()
        self.assertEqual(len(mkr_list2), 10)


if __name__ == '__main__':
    prog = unittest.main()
