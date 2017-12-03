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
        y = bundle.Bundle().create_node(name='myBundle1')
        y_node = y.get_node()
        self.assertTrue(maya.cmds.objExists(y_node))
        self.assertEqual(y_node, '|myBundle1')

        z = bundle.Bundle(node=y_node)
        z_node = z.get_node()
        self.assertEqual(z_node, y_node)
        self.assertEqual(z_node, '|myBundle1')

    # def test_get_node(self):
    #     pass
    #
    # def test_set_node(self):
    #     pass
    #
    # def test_create_node(self):
    #     pass
    #
    # def test_delete_node(self):
    #     pass
    #
    # def test_get_node_colour(self):
    #     pass
    #
    # def test_set_node_colour(self):
    #     pass

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
