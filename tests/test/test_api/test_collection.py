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
Test functions for collection module, and especially for the Collection class.

Note, Collection.execute() is tested separately in 'test.test_api.test_solve'
module.
"""

import sys
import os
import unittest

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver._api.utils as api_utils
import mmSolver._api.solverstep as solver
import mmSolver._api.frame as frame
import mmSolver._api.camera as camera
import mmSolver._api.marker as marker
import mmSolver._api.bundle as bundle
import mmSolver._api.attribute as attribute
import mmSolver._api.collection as collection
import mmSolver._api.excep as excep


# @unittest.skip
class TestCollection(test_api_utils.APITestCase):
    def test_init(self):
        x = collection.Collection()
        x.create_node('mySolve')
        y = collection.Collection('mySolve')
        z = collection.Collection(node='mySolve')
        self.assertTrue(maya.cmds.objExists(x.get_node()))
        self.assertTrue(maya.cmds.objExists(y.get_node()))
        self.assertTrue(maya.cmds.objExists(z.get_node()))
        self.assertEqual(x.get_node(), y.get_node())
        self.assertEqual(x.get_node(), z.get_node())

        self.assertRaises(TypeError, collection.Collection, ['mySolve'])

    def test_create(self):
        x = collection.Collection()
        x.create_node('mySolve')
        self.assertTrue(maya.cmds.objExists(x.get_node()))

    def test_get_node(self):
        x = collection.Collection()
        x.create_node('mySolve')
        node = x.get_node()
        self.assertIsInstance(node, (str, unicode))
        self.assertGreater(len(node), 0)
        self.assertTrue(maya.cmds.objExists(node))

    def test_set_node(self):
        x = collection.Collection()
        x.create_node('mySolve')

        y = collection.Collection()
        y.create_node('myOtherSolve')

        z = collection.Collection()
        z.set_node(x.get_node())
        self.assertEqual(x.get_node(), z.get_node())

        z.set_node(y.get_node())
        self.assertEqual(y.get_node(), z.get_node())

    def test_get_solver_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        sol1 = solver.Solver()
        x.add_solver(sol1)

        sol_list = x.get_solver_list()
        self.assertIsInstance(sol_list, list)
        self.assertEqual(sol1.get_data(), sol_list[0].get_data())

        # Re-create the collection asset from the original node and ensure
        # everything still matches.
        x_node = x.get_node()
        y = collection.Collection(node=x_node)
        sol_list = y.get_solver_list()
        self.assertIsInstance(sol_list, list)
        self.assertEqual(len(sol_list), 1)
        self.assertEqual(sol1.get_data(), sol_list[0].get_data())

    def test_add_solver(self):
        x = collection.Collection()
        x.create_node('mySolve')

        sol1 = solver.Solver()
        x.add_solver(sol1)
        sol_list1 = x.get_solver_list()
        self.assertEqual(len(sol_list1), 1)
        self.assertIn(sol1, sol_list1)
        self.assertIsInstance(sol_list1, list)

        sol3 = solver.Solver()
        x.add_solver(sol3)
        sol_list2 = x.get_solver_list()
        self.assertEqual(len(sol_list2), 2)
        self.assertEqual(sol3.get_data(), sol_list2[1].get_data())
        self.assertIsInstance(sol_list2, list)

        # Start from a new class.
        x_node = x.get_node()
        y = collection.Collection(node=x_node)
        sol4 = solver.Solver()
        y.add_solver(sol4)
        sol_list3 = y.get_solver_list()
        self.assertEqual(len(sol_list3), 3)

    def test_add_solver_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        sol_list0 = []
        for i in range(10):
            sol = solver.Solver()
            sol_list0.append(sol)
        x.add_solver_list(sol_list0)
        sol_list1 = x.get_solver_list()
        self.assertEqual(len(sol_list1), 10)
        self.assertIsInstance(sol_list1, list)

        x.add_solver_list([
            solver.Solver(),
            solver.Solver(),
            solver.Solver()
        ])
        sol_list2 = x.get_solver_list()
        self.assertEqual(len(sol_list2), 13)
        self.assertIsInstance(sol_list2, list)

    def test_remove_solver(self):
        x = collection.Collection()
        x.create_node('mySolve')

        sol_list1 = []
        for i in range(10):
            sol = solver.Solver()
            sol_list1.append(sol)
        x.set_solver_list(sol_list1)
        self.assertEqual(x.get_solver_list_length(), 10)

        for i in range(0, 10, 2):
            x.remove_solver(sol_list1[i])
        self.assertEqual(x.get_solver_list_length(), 5)

    def test_remove_solver_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        sol_list1 = []
        for i in range(10):
            sol = solver.Solver()
            sol_list1.append(sol)
        x.set_solver_list(sol_list1)
        self.assertEqual(x.get_solver_list_length(), 10)

        x.remove_solver_list(sol_list1)
        self.assertEqual(x.get_solver_list_length(), 0)

    def test_set_solver_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        sol_list1 = []
        for i in range(10):
            sol = solver.Solver()
            sol_list1.append(sol)
        x.set_solver_list(sol_list1)
        self.assertEqual(x.get_solver_list_length(), 10)

        # first half of list
        sol_list2 = sol_list1[:5]
        x.set_solver_list(sol_list2)
        self.assertEqual(x.get_solver_list_length(), 5)

    def test_get_marker_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        self.assertEqual(x.get_marker_list_length(), 0)

        node = maya.cmds.createNode('transform')
        mkr1 = marker.Marker().create_node()
        mkr2 = marker.Marker().create_node()
        attr1 = attribute.Attribute(node=node, attr='translateX')
        attr2 = attribute.Attribute(node=node, attr='translateY')
        attr3 = attribute.Attribute(node=node, attr='translateZ')
        attr4 = attribute.Attribute(node=node, attr='rotateX')
        attr5 = attribute.Attribute(node=node, attr='rotateY')
        attr6 = attribute.Attribute(node=node, attr='rotateZ')
        x.add_marker(mkr1)
        x.add_marker(mkr2)
        x.add_attribute(attr1)
        x.add_attribute(attr2)
        x.add_attribute(attr3)
        x.add_attribute(attr4)
        x.add_attribute(attr5)
        x.add_attribute(attr6)

        self.assertEqual(x.get_marker_list_length(), 2)

    def test_get_marker_list_length(self):
        x = collection.Collection()
        x.create_node('mySolve')
        self.assertEqual(x.get_marker_list_length(), 0)

        mkr = marker.Marker().create_node()
        x.add_marker(mkr)
        self.assertEqual(x.get_marker_list_length(), 1)

    def test_add_marker(self):
        x = collection.Collection()
        x.create_node('mySolve')

        name = 'myMarker1'
        mkr = marker.Marker().create_node(name=name)
        x.add_marker(mkr)

        mkr_list = x.get_marker_list()
        n2 = len(mkr_list)
        self.assertEqual(n2, 1)
        self.assertIsInstance(mkr_list[0], marker.Marker)
        self.assertIsNot(mkr, mkr_list[0])  # objects are not the same memory.
        self.assertIn(name, mkr.get_node())
        self.assertEqual(mkr.get_node(), mkr_list[0].get_node())  # same node

    def test_add_marker_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        x.add_marker_list([])

        name = 'myMarker1'
        mkr_list = []
        for i in range(10):
            mkr = marker.Marker().create_node(name=name)
            mkr_list.append(mkr)
        x.add_marker_list(mkr_list)

        mkr_list2 = x.get_marker_list()
        self.assertEqual(len(mkr_list2), 10)

        node_list = []
        for mkr in mkr_list:
            node_list.append(mkr.get_node())
        for mkr in mkr_list2:
            node = mkr.get_node()
            self.assertIn(node, node_list)

    def test_remove_marker(self):
        x = collection.Collection()
        x.create_node('mySolve')

        name = 'myMarker1'
        mkr = marker.Marker().create_node(name=name)
        x.add_marker(mkr)

        mkr_list = x.get_marker_list()
        n1 = len(mkr_list)
        self.assertEqual(n1, 1)
        self.assertIsInstance(mkr_list[0], marker.Marker)
        self.assertIn(name, mkr.get_node())
        self.assertEqual(mkr.get_node(), mkr_list[0].get_node())

        x.remove_marker(mkr)
        mkr_list = x.get_marker_list()
        n2 = len(mkr_list)
        self.assertEqual(n2, 0)

    def test_remove_marker_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        name = 'myMarker1'
        mkr_list = []
        for i in range(10):
            mkr = marker.Marker().create_node(name=name)
            mkr_list.append(mkr)
        x.add_marker_list(mkr_list)

        self.assertEqual(x.get_marker_list_length(), 10)

        # remove the first half
        x.remove_marker_list(mkr_list[:5])

        self.assertEqual(x.get_marker_list_length(), 5)

        # remove the second half
        x.remove_marker_list(mkr_list[4:])

        self.assertEqual(x.get_marker_list_length(), 0)

    def test_set_marker_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        attr_list = []
        mkr_list = []
        mkr1 = marker.Marker().create_node()
        mkr_list.append(mkr1)
        for i in range(10):
            mkr = marker.Marker().create_node()
            mkr_list.append(mkr)

            node = maya.cmds.createNode('transform')
            attr = attribute.Attribute(node=node, attr='translateZ')
            attr_list.append(attr)

        x.set_marker_list(mkr_list)
        x.set_attribute_list(mkr_list)
        self.assertEqual(x.get_marker_list_length(), 11)

        mkr_list = [mkr1]
        x.set_marker_list(mkr_list)
        self.assertEqual(x.get_marker_list_length(), 1)

        mkr_list = x.get_marker_list()
        self.assertEqual(mkr1.get_node(), mkr_list[0].get_node())

    def test_clear_marker_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        attr_list = []
        mkr_list = []
        for i in range(10):
            mkr = marker.Marker().create_node()
            mkr_list.append(mkr)

            node = maya.cmds.createNode('transform')
            attr = attribute.Attribute(node=node, attr='translateZ')
            attr_list.append(attr)

        x.set_marker_list(mkr_list)
        x.set_attribute_list(attr_list)
        self.assertEqual(x.get_marker_list_length(), 10)

        x.clear_marker_list()
        self.assertEqual(x.get_marker_list_length(), 0)

    def test_get_attribute_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        self.assertEqual(x.get_attribute_list_length(), 0)

        attr_list2 = []
        for i in range(10):
            node = maya.cmds.createNode('transform')
            attr = attribute.Attribute(node=node, attr='translateX')
            attr_list2.append(attr)
        x.set_attribute_list(attr_list2)

        attr_list3 = x.get_attribute_list()
        n2 = len(attr_list3)
        self.assertEqual(n2, 10)
        name_list = []
        for attr in attr_list3:
            name = attr.get_name()
            name_list.append(name)
        for attr in attr_list2:
            name = attr.get_name()
            self.assertIn(name, name_list)

    def test_get_attribute_list_length(self):
        x = collection.Collection()
        x.create_node('mySolve')
        self.assertEqual(x.get_attribute_list_length(), 0)

        node = maya.cmds.createNode('transform')
        attr = attribute.Attribute(node=node, attr='translateX')
        x.add_attribute(attr)
        self.assertEqual(x.get_attribute_list_length(), 1)

    def test_add_attribute(self):
        x = collection.Collection()
        x.create_node('mySolve')

        node = maya.cmds.createNode('transform')
        attr = attribute.Attribute(node=node, attr='translateX')
        x.add_attribute(attr)

        attr_list = x.get_attribute_list()
        self.assertEqual(len(attr_list), 1)
        self.assertIsInstance(attr_list[0], attribute.Attribute)
        self.assertIsNot(attr, attr_list[0])  # objects are not the same memory.

        self.assertEqual(attr.get_node(), attr_list[0].get_node())  # same node
        self.assertEqual(attr.get_attr(), attr_list[0].get_attr())  # same attr
        self.assertEqual(attr_list[0].get_name(), attr.get_name())  # same name

    def test_add_attribute_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        attr_list = []
        for i in range(10):
            node = maya.cmds.createNode('transform')
            attr = attribute.Attribute(node=node, attr='rotateX')
            attr_list.append(attr)
        x.add_attribute_list(attr_list)

        attr_list2 = x.get_attribute_list()
        self.assertEqual(len(attr_list2), 10)
        self.assertIsInstance(attr_list2[0], attribute.Attribute)

        node_list = []
        for attr in attr_list:
            node_list.append(attr.get_node())
        for attr in attr_list2:
            node = attr.get_node()
            self.assertIn(node, node_list)

    def test_remove_attribute(self):
        x = collection.Collection()
        x.create_node('mySolve')

        node = maya.cmds.createNode('transform')
        attr = attribute.Attribute(node=node, attr='translateX')
        x.add_attribute(attr)

        self.assertEqual(x.get_attribute_list_length(), 1)
        x.remove_attribute(attr)
        self.assertEqual(x.get_attribute_list_length(), 0)

    def test_remove_attribute_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        attr_list = []
        for i in range(10):
            node = maya.cmds.createNode('transform')
            attr = attribute.Attribute(node=node, attr='rotateY')
            attr_list.append(attr)
        x.add_attribute_list(attr_list)

        self.assertEqual(x.get_attribute_list_length(), 10)

        # Remove the first half
        x.remove_attribute_list(attr_list[:5])

        self.assertEqual(x.get_attribute_list_length(), 5)

        # Remove the other half
        x.remove_attribute_list(attr_list[4:])

        self.assertEqual(x.get_attribute_list_length(), 0)

    def test_set_attribute_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        attr_list = []
        for i in range(10):
            node = maya.cmds.createNode('transform')
            attr = attribute.Attribute(node=node, attr='translateX')
            attr_list.append(attr)
        x.set_attribute_list(attr_list)

        attr_list2 = x.get_attribute_list()
        self.assertEqual(len(attr_list2), 10)
        name_list = []
        for attr in attr_list2:
            name = attr.get_name()
            name_list.append(name)
        for attr in attr_list:
            name = attr.get_name()
            self.assertIn(name, name_list)

    def test_clear_attribute_list(self):
        x = collection.Collection()
        x.create_node('mySolve')

        attr_list = []
        for i in range(10):
            node = maya.cmds.createNode('transform')
            attr = attribute.Attribute(node=node, attr='translateX')
            attr_list.append(attr)
        x.set_attribute_list(attr_list)

        self.assertEqual(x.get_attribute_list_length(), 10)
        x.clear_attribute_list()
        self.assertEqual(x.get_attribute_list_length(), 0)

    def test_is_valid(self):
        """
        Collection validation.
        Once all pieces are connected, the collection is valid.
        """
        x = collection.Collection()
        x.create_node('myCollection')
        self.assertFalse(x.is_valid())

        # Solver
        sol = solver.Solver()
        x.add_solver(sol)
        self.assertFalse(x.is_valid())

        # Solver (with frame)
        f = frame.Frame(1)
        sol.add_frame(f)
        self.assertFalse(x.is_valid())

        # Marker / Bundle
        cam_tfm = maya.cmds.createNode('transform', name='camera1')
        cam_shp = maya.cmds.createNode('camera', name='cameraShape1')
        cam = camera.Camera(shape=cam_shp)
        bnd = bundle.Bundle().create_node()
        mkr = marker.Marker().create_node(cam=cam, bnd=bnd)
        x.add_marker(mkr)
        self.assertFalse(x.is_valid())

        # Attribute
        node = bnd.get_node()
        attr = attribute.Attribute(node=node, attr='translateX')
        x.add_attribute(attr)
        self.assertTrue(x.is_valid())


if __name__ == '__main__':
    prog = unittest.main()
