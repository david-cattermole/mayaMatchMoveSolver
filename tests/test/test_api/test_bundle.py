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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver._api.utils as api_utils
import mmSolver._api.bundle as bundle
import mmSolver._api.marker as marker
import mmSolver._api.constant as const


# @unittest.skip
class TestBundle(test_api_utils.APITestCase):
    def test_init(self):
        x = bundle.Bundle()
        x_node = x.get_node()
        self.assertEqual(x_node, None)

        # Create nodes
        y = bundle.Bundle().create_node()
        y_node = y.get_node()
        y_obj_type = api_utils.get_object_type(y_node)
        self.assertTrue(maya.cmds.objExists(y_node))
        self.assertEqual(y_node, '|bundle1')
        self.assertEqual(y_obj_type, const.OBJECT_TYPE_BUNDLE)

        # Create nodes (again, with explicit node name)
        y = bundle.Bundle().create_node(name='myBundle1')
        y_node = y.get_node()
        y_obj_type = api_utils.get_object_type(y_node)
        self.assertTrue(maya.cmds.objExists(y_node))
        self.assertEqual(y_node, '|myBundle1')
        self.assertEqual(y_obj_type, const.OBJECT_TYPE_BUNDLE)

        # Set Node via __init__
        z = bundle.Bundle(node=y_node)
        z_node = z.get_node()
        z_obj_type = api_utils.get_object_type(z_node)
        self.assertEqual(z_node, y_node)
        self.assertEqual(z_node, '|myBundle1')
        self.assertEqual(z_obj_type, const.OBJECT_TYPE_BUNDLE)

        # Set Node via set_node
        x.set_node(y_node)
        x_node = x.get_node()
        x_obj_type = api_utils.get_object_type(x_node)
        self.assertEqual(x_node, y_node)
        self.assertEqual(x_obj_type, const.OBJECT_TYPE_BUNDLE)

    def test_set_colour_rgb(self):
        """
        Set colour of the bundle.
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

    def test_set_colour_rgba(self):
        """
        Set colour of the bundle.
        """
        green = (0.0, 1.0, 0.0, 1.0)
        blue = (0.0, 0.0, 1.0, 0.5)

        x = bundle.Bundle()
        x_rgba = x.get_colour_rgba()
        self.assertEqual(x_rgba, None)

        # Create nodes
        y = bundle.Bundle().create_node(name='myBundle1')
        y_rgba = y.get_colour_rgba()
        self.assertEqual(y_rgba, green)

        y.set_colour_rgba(blue)
        y_rgba = y.get_colour_rgba()
        self.assertEqual(y_rgba, blue)
        return

    def test_get_marker_list(self):
        x = bundle.Bundle().create_node(name='myBundle1')
        mkr_list1 = x.get_marker_list()
        self.assertEqual(len(mkr_list1), 0)

        for i in range(10):
            mkr = marker.Marker().create_node()
            mkr.set_bundle(x)
        mkr_list2 = x.get_marker_list()
        self.assertEqual(len(mkr_list2), 10)


if __name__ == '__main__':
    prog = unittest.main()
