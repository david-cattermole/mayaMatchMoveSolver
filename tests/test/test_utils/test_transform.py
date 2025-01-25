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
Test functions for transform utilities module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import test.test_utils.utilsutils as test_utils

import maya.cmds
import maya.api.OpenMaya as OpenMaya2
import maya.debug.closeness as closeness

import mmSolver.utils.node as node_utils
import mmSolver.utils.transform as mod


# @unittest.skip
class TestTransform(test_utils.UtilsTestCase):
    """
    Test transform module.
    """

    def test_create_dg_context_apitwo(self):
        times = [1.0, 2, -1.0, -1, 42, 9999, -9999]
        for time in times:
            ctx = mod.create_dg_context_apitwo(time)
            assert isinstance(ctx, OpenMaya2.MDGContext)
        return

    def test_get_matrix_from_plug_apitwo(self):
        start_frame = 1001
        end_frame = 1101
        node = maya.cmds.createNode('transform')
        attr_names = [
            'matrix',
            'worldMatrix[0]',
            'parentMatrix[0]',
        ]
        for attr_name in attr_names:
            plug_name = '{}.{}'.format(node, attr_name)
            plug = node_utils.get_as_plug_apitwo(plug_name)
            times = [1.0, 2, -1.0, -1, 42, 9999, -9999]
            times += list(range(start_frame, end_frame))
            for time in times:
                ctx = mod.create_dg_context_apitwo(time)
                matrix = mod.get_matrix_from_plug_apitwo(plug, ctx)
                assert isinstance(matrix, OpenMaya2.MMatrix)
        return

    def test_get_double_from_plug_apitwo(self):
        start_frame = 1001
        end_frame = 1101
        node = maya.cmds.createNode('transform')
        attr_names = [
            'translateX',
            'rotateY',
            'scaleZ',
        ]
        for attr_name in attr_names:
            plug_name = '{}.{}'.format(node, attr_name)
            plug = node_utils.get_as_plug_apitwo(plug_name)
            times = [1.0, 2, -1.0, -1, 42, 9999, -9999]
            times += list(range(start_frame, end_frame))
            for time in times:
                ctx = mod.create_dg_context_apitwo(time)
                value = mod.get_double_from_plug_apitwo(plug, ctx)
                assert isinstance(value, float)
        return

    def test_get_parent_inverse_matrix_apitwo(self):
        start_frame = 1001
        end_frame = 1101
        node = maya.cmds.createNode('transform')
        times = [1.0, 2, -1.0, -1, 42, 9999, -9999]
        times += list(range(start_frame, end_frame))
        for time in times:
            ctx = mod.create_dg_context_apitwo(time)
            value = mod.get_parent_inverse_matrix_apitwo(node, ctx)
            assert isinstance(value, OpenMaya2.MMatrix)
        return

    def test_get_world_matrix_apitwo(self):
        start_frame = 1001
        end_frame = 1101
        node = maya.cmds.createNode('transform')
        times = [1.0, 2, -1.0, -1, 42, 9999, -9999]
        times += list(range(start_frame, end_frame))
        for time in times:
            ctx = mod.create_dg_context_apitwo(time)
            value = mod.get_world_matrix_apitwo(node, ctx)
            assert isinstance(value, OpenMaya2.MMatrix)
        return

    def test_detect_rotate_pivot_non_zero(self):
        tfm_node = maya.cmds.createNode('transform')
        tfm = mod.TransformNode(tfm_node)
        self.assertFalse(mod.detect_rotate_pivot_non_zero(tfm))

        path = self.get_data_path('scenes', 'bookHierarchy.ma')
        maya.cmds.file(path, open=True, force=True)

        book_node = 'book_GRP'
        spine_node = 'spine_GRP'
        cover_node = 'front_cover_GRP'
        book_tfm = mod.TransformNode(book_node)
        spine_tfm = mod.TransformNode(spine_node)
        cover_tfm = mod.TransformNode(cover_node)

        self.assertFalse(mod.detect_rotate_pivot_non_zero(book_tfm))
        self.assertTrue(mod.detect_rotate_pivot_non_zero(spine_tfm))
        self.assertTrue(mod.detect_rotate_pivot_non_zero(cover_tfm))
        return

    def test_get_transform_matrix_list_90degrees(self):
        path = self.get_data_path('scenes', 'bookHierarchy.ma')
        maya.cmds.file(path, open=True, force=True)

        book_node = 'book_GRP'
        spine_node = 'spine_GRP'
        cover_node = 'front_cover_GRP'
        latch_node = 'latch_GRP'

        maya.cmds.setAttr(book_node + '.ty', 10.0)
        maya.cmds.setAttr(book_node + '.rz', 90.0)  # <<< 90 degrees
        maya.cmds.setAttr(spine_node + '.rz', 90.0)
        maya.cmds.setAttr(cover_node + '.rz', 90.0)

        book_tfm = mod.TransformNode(book_node)
        spine_tfm = mod.TransformNode(spine_node)
        cover_tfm = mod.TransformNode(cover_node)
        latch_tfm = mod.TransformNode(latch_node)
        tfm_nodes = [book_tfm, spine_tfm, cover_tfm, latch_tfm]

        current_frame = maya.cmds.currentTime(query=True)
        frame_range = [current_frame]

        # Query the transform matrix for the nodes
        cache = mod.TransformMatrixCache()
        for tfm_node in tfm_nodes:
            cache.add_node(tfm_node, frame_range)
        cache.process()

        book_world_matrix_list = mod.get_transform_matrix_list(
            cache, frame_range, book_tfm
        )
        self.assertEqual(len(book_world_matrix_list), 1)
        book_world_matrix = list(book_world_matrix_list[0].asMatrix())

        spine_world_matrix_list = mod.get_transform_matrix_list(
            cache, frame_range, spine_tfm
        )
        self.assertEqual(len(spine_world_matrix_list), 1)
        spine_world_matrix = list(spine_world_matrix_list[0].asMatrix())

        cover_world_matrix_list = mod.get_transform_matrix_list(
            cache, frame_range, cover_tfm
        )
        self.assertEqual(len(cover_world_matrix_list), 1)
        cover_world_matrix = list(cover_world_matrix_list[0].asMatrix())

        latch_world_matrix_list = mod.get_transform_matrix_list(
            cache, frame_range, latch_tfm
        )
        self.assertEqual(len(latch_world_matrix_list), 1)
        latch_world_matrix = list(latch_world_matrix_list[0].asMatrix())

        # Expected Matrices
        expected_book_matrix = [
            0.0,
            1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            10.0,
            0.0,
            1.0,
        ]
        expected_spine_matrix = [
            -1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.3518918752670288,
            8.476484298706055,
            0.0029969215393066406,
            1.0,
        ]
        expected_cover_matrix = [
            0.0,
            -1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.3488234877586365,
            7.9185943603515625,
            0.0029969215393066406,
            1.0,
        ]
        expected_latch_matrix = [
            0.0,
            1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.3430972993373871,
            11.661497116088867,
            0.0001980811357498169,
            1.0,
        ]

        # Confirm matrix values in the cache are correct
        self.assertGreater(
            closeness.compare_floats(book_world_matrix, expected_book_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )

        self.assertGreater(
            closeness.compare_floats(spine_world_matrix, expected_spine_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )

        self.assertGreater(
            closeness.compare_floats(cover_world_matrix, expected_cover_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )

        self.assertGreater(
            closeness.compare_floats(latch_world_matrix, expected_latch_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )
        return

    def test_get_transform_matrix_list_45degrees(self):
        path = self.get_data_path('scenes', 'bookHierarchy.ma')
        maya.cmds.file(path, open=True, force=True)

        book_node = 'book_GRP'
        spine_node = 'spine_GRP'
        cover_node = 'front_cover_GRP'
        latch_node = 'latch_GRP'

        maya.cmds.setAttr(book_node + '.ty', 10.0)
        maya.cmds.setAttr(book_node + '.rz', 45.0)  # <<< 45 degrees
        maya.cmds.setAttr(spine_node + '.rz', 90.0)
        maya.cmds.setAttr(cover_node + '.rz', 90.0)

        book_tfm = mod.TransformNode(book_node)
        spine_tfm = mod.TransformNode(spine_node)
        cover_tfm = mod.TransformNode(cover_node)
        latch_tfm = mod.TransformNode(latch_node)
        tfm_nodes = [book_tfm, spine_tfm, cover_tfm, latch_tfm]

        current_frame = maya.cmds.currentTime(query=True)
        frame_range = [current_frame]

        # Query the transform matrix for the nodes
        cache = mod.TransformMatrixCache()
        for tfm_node in tfm_nodes:
            cache.add_node(tfm_node, frame_range)
        cache.process()

        book_world_matrix_list = mod.get_transform_matrix_list(
            cache, frame_range, book_tfm
        )
        self.assertEqual(len(book_world_matrix_list), 1)
        book_world_matrix = list(book_world_matrix_list[0].asMatrix())

        spine_world_matrix_list = mod.get_transform_matrix_list(
            cache, frame_range, spine_tfm
        )
        self.assertEqual(len(spine_world_matrix_list), 1)
        spine_world_matrix = list(spine_world_matrix_list[0].asMatrix())

        cover_world_matrix_list = mod.get_transform_matrix_list(
            cache, frame_range, cover_tfm
        )
        self.assertEqual(len(cover_world_matrix_list), 1)
        cover_world_matrix = list(cover_world_matrix_list[0].asMatrix())

        latch_world_matrix_list = mod.get_transform_matrix_list(
            cache, frame_range, latch_tfm
        )
        self.assertEqual(len(latch_world_matrix_list), 1)
        latch_world_matrix = list(latch_world_matrix_list[0].asMatrix())

        # Expected Matrices
        expected_book_matrix = [
            0.7071067811865475,
            0.7071067811865476,
            0.0,
            0.0,
            -0.7071067811865476,
            0.7071067811865475,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            10.0,
            0.0,
            1.0,
        ]
        expected_spine_matrix = [
            -0.7071067811865475,
            0.7071067811865477,
            0.0,
            0.0,
            -0.7071067811865477,
            -0.7071067811865475,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            -0.8284631523833599,
            8.673886585125107,
            0.0029969215393066406,
            1.0,
        ]
        expected_cover_matrix = [
            -0.7071067811865479,
            -0.7071067811865474,
            0.0,
            0.0,
            0.7071067811865474,
            -0.7071067811865479,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            -1.2251205885640575,
            8.281568504173393,
            0.0029969215393066406,
            1.0,
        ]
        expected_latch_matrix = [
            0.7071067811865475,
            0.7071067811865476,
            0.0,
            0.0,
            -0.7071067811865476,
            0.7071067811865475,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            1.417462229728698,
            10.932249069213867,
            0.0001980811357498169,
            1.0,
        ]

        # Confirm matrix values in the cache are correct
        self.assertGreater(
            closeness.compare_floats(book_world_matrix, expected_book_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )

        tol = 0.000001
        mat_a = OpenMaya2.MMatrix(book_world_matrix)
        mat_b = OpenMaya2.MMatrix(expected_book_matrix)
        self.assertTrue(mat_a.isEquivalent(mat_b, tol))

        self.assertGreater(
            closeness.compare_floats(spine_world_matrix, expected_spine_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )
        mat_a = OpenMaya2.MMatrix(spine_world_matrix)
        mat_b = OpenMaya2.MMatrix(expected_spine_matrix)
        self.assertTrue(mat_a.isEquivalent(mat_b, tol))

        self.assertGreater(
            closeness.compare_floats(cover_world_matrix, expected_cover_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )
        mat_a = OpenMaya2.MMatrix(cover_world_matrix)
        mat_b = OpenMaya2.MMatrix(expected_cover_matrix)
        self.assertTrue(mat_a.isEquivalent(mat_b, tol))

        self.assertGreater(
            closeness.compare_floats(latch_world_matrix, expected_latch_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )
        mat_a = OpenMaya2.MMatrix(latch_world_matrix)
        mat_b = OpenMaya2.MMatrix(expected_latch_matrix)
        self.assertTrue(mat_a.isEquivalent(mat_b, tol))
        return

    def test_decompose_matrix(self):
        prv_rot = (0.0, 0.0, 0.0)

        # Identity Transform.
        tfm_matrix = OpenMaya2.MTransformationMatrix()
        tfm_components = mod.decompose_matrix(tfm_matrix, prv_rot)
        tx, ty, tz, rx, ry, rz, sx, sy, sz = tfm_components
        self.assertAlmostEqual(tx, 0.0)
        self.assertAlmostEqual(ty, 0.0)
        self.assertAlmostEqual(tz, 0.0)
        self.assertAlmostEqual(rx, 0.0)
        self.assertAlmostEqual(ry, 0.0)
        self.assertAlmostEqual(rz, 0.0)
        self.assertAlmostEqual(sx, 1.0)
        self.assertAlmostEqual(sy, 1.0)
        self.assertAlmostEqual(sz, 1.0)

        # TODO: Create other matrices with values.
        return

    def test_set_transform_values(self):
        start_frame = 1001
        end_frame = 1101
        node = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(
            node, attribute='translateX', time=start_frame, value=-100.0
        )
        maya.cmds.setKeyframe(node, attribute='translateX', time=end_frame, value=100.0)
        maya.cmds.setKeyframe(
            node, attribute='translateY', time=start_frame, value=-10.0
        )
        maya.cmds.setKeyframe(node, attribute='translateY', time=end_frame, value=10.0)
        maya.cmds.setKeyframe(node, attribute='rotateY', time=start_frame, value=90.0)
        maya.cmds.setKeyframe(node, attribute='rotateY', time=end_frame, value=-90.0)
        frame_range = list(range(start_frame, end_frame + 1))

        tfm_node = mod.TransformNode(node=node)

        tfm_cache = mod.TransformMatrixCache()
        tfm_cache.add_node_attr(tfm_node, 'worldMatrix[0]', frame_range)
        tfm_cache.process()

        dst_node = maya.cmds.createNode('transform')
        dst_tfm_node = mod.TransformNode(node=dst_node)

        mod.set_transform_values(
            tfm_cache,
            frame_range,
            tfm_node,
            dst_tfm_node,
            delete_static_anim_curves=True,
        )

        # save the output scene file
        path = 'test_transform_after.ma'
        path = self.get_data_path(path)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return

    def test_set_transform_values_with_rotate_pivot(self):
        path = self.get_data_path('scenes', 'bookHierarchy.ma')
        maya.cmds.file(path, open=True, force=True)

        book_node = 'book_GRP'
        spine_node = 'spine_GRP'
        cover_node = 'front_cover_GRP'

        maya.cmds.setAttr(book_node + '.ty', 10.0)
        maya.cmds.setAttr(book_node + '.rz', 90.0)
        maya.cmds.setAttr(spine_node + '.rz', 90.0)
        maya.cmds.setAttr(cover_node + '.rz', 90.0)

        book_tfm = mod.TransformNode(book_node)
        spine_tfm = mod.TransformNode(spine_node)
        cover_tfm = mod.TransformNode(cover_node)
        tfm_nodes = [book_tfm, spine_tfm, cover_tfm]

        current_frame = maya.cmds.currentTime(query=True)
        frame_range = [current_frame]

        # Query the transform matrix for the nodes
        cache = mod.TransformMatrixCache()
        for tfm_node in tfm_nodes:
            cache.add_node(tfm_node, frame_range)
        cache.process()

        book_dst_node = maya.cmds.createNode('transform', name='book_CTRL')
        book_dst_tfm_node = mod.TransformNode(node=book_dst_node)
        mod.set_transform_values(
            cache,
            frame_range,
            book_tfm,
            book_dst_tfm_node,
            delete_static_anim_curves=False,
        )

        spine_dst_node = maya.cmds.createNode('transform', name='spine_CTRL')
        spine_dst_tfm_node = mod.TransformNode(node=spine_dst_node)
        mod.set_transform_values(
            cache,
            frame_range,
            spine_tfm,
            spine_dst_tfm_node,
            delete_static_anim_curves=False,
        )

        cover_dst_node = maya.cmds.createNode('transform', name='cover_CTRL')
        cover_dst_tfm_node = mod.TransformNode(node=cover_dst_node)
        mod.set_transform_values(
            cache,
            frame_range,
            cover_tfm,
            cover_dst_tfm_node,
            delete_static_anim_curves=False,
        )

        # save the output scene file
        path = 'test_transform_set_transforms_with_rotate_pivot_after.ma'
        path = self.get_data_path(path)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Expected Matrices
        expected_book_matrix = [
            0.0,
            1.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            10.0,
            0.0,
            1.0,
        ]
        expected_spine_matrix = [
            -1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.3518918752670288,
            8.476484298706055,
            0.0029969215393066406,
            1.0,
        ]
        expected_cover_matrix = [
            0.0,
            -1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.3488234877586365,
            7.9185943603515625,
            0.0029969215393066406,
            1.0,
        ]
        expected_spine_par_inv_matrix = [
            0.0,
            -1.0,
            0.0,
            0.0,
            1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            -10.0,
            0.0,
            0.0,
            1.0,
        ]
        expected_front_cover_par_inv_matrix = [
            -1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            -1.0,
            0.0,
            0.0,
            0.0,
            0.0,
            1.0,
            0.0,
            -1.1716232898755894,
            8.124592860140336,
            0.0,
            1.0,
        ]

        # Confirm attributes in the cache are correct
        book_attrs = cache.get_attrs_for_node(book_tfm)
        self.assertEqual(list(book_attrs), ["worldMatrix[0]"])

        attr_names_with_pivot = list(
            sorted(
                [
                    "worldMatrix[0]",
                    "matrix",
                    "parentInverseMatrix[0]",
                    "rotatePivotX",
                    "rotatePivotY",
                    "rotatePivotZ",
                ]
            )
        )
        spine_attrs = cache.get_attrs_for_node(spine_tfm)
        self.assertEqual(list(sorted(spine_attrs)), attr_names_with_pivot)

        cover_attrs = cache.get_attrs_for_node(cover_tfm)
        self.assertEqual(list(sorted(cover_attrs)), attr_names_with_pivot)

        # Confirm matrix values in the cache are correct
        book_world_matrix = list(
            cache.get_node_attr(book_tfm, "worldMatrix[0]", frame_range)[0]
        )
        self.assertGreater(
            closeness.compare_floats(book_world_matrix, expected_book_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )

        spine_par_inv_matrix = list(
            cache.get_node_attr(spine_tfm, "parentInverseMatrix[0]", frame_range)[0]
        )
        self.assertGreater(
            closeness.compare_floats(
                spine_par_inv_matrix, expected_spine_par_inv_matrix
            ),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )

        cover_par_inv_matrix = list(
            cache.get_node_attr(cover_tfm, "parentInverseMatrix[0]", frame_range)[0]
        )
        self.assertGreater(
            closeness.compare_floats(
                cover_par_inv_matrix, expected_front_cover_par_inv_matrix
            ),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )

        # Compare destination node matrices with the original
        book_matrix = maya.cmds.xform(
            book_dst_node, query=True, matrix=True, worldSpace=True
        )
        self.assertGreater(
            closeness.compare_floats(book_matrix, expected_book_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )

        spine_matrix = maya.cmds.xform(
            spine_dst_node, query=True, matrix=True, worldSpace=True
        )
        self.assertGreater(
            closeness.compare_floats(spine_matrix, expected_spine_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )

        cover_matrix = maya.cmds.xform(
            cover_dst_node, query=True, matrix=True, worldSpace=True
        )
        self.assertGreater(
            closeness.compare_floats(cover_matrix, expected_cover_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS,
        )
        return

    def test_TransformNode_usage(self):
        start_frame = 1001
        end_frame = 1101
        maya_node = maya.cmds.createNode('transform', name='myNode')
        tfm_node = mod.TransformNode(node=maya_node)
        node = tfm_node.get_node()
        node_uuid = tfm_node.get_node_uuid()
        tfm_node_parents = tfm_node.get_parents()
        tfm_node_b = mod.TransformNode()
        tfm_node_b.set_node('myNode')
        return

    def test_TransformMatrixCache_init(self):
        start_frame = 1001
        end_frame = 1101
        node = maya.cmds.createNode('transform')
        mod.TransformNode(node=node)
        mod.TransformMatrixCache()
        return

    def test_TransformMatrixCache_usage(self):
        start_frame = 1001
        end_frame = 1101
        times = list(range(start_frame, end_frame))
        node = maya.cmds.createNode('transform')
        tfm_node = mod.TransformNode(node=node)
        tfm_matrix_cache = mod.TransformMatrixCache()
        tfm_matrix_cache.add_node(tfm_node, times)
        tfm_matrix_cache.process()
        attr_name = 'translateX'
        tfm_matrix_cache.get_node_attr_matrix(tfm_node, attr_name, times)
        return


if __name__ == '__main__':
    prog = unittest.main()
