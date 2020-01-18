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

import unittest

import test.test_utils.utilsutils as test_utils

import maya.cmds
import maya.api.OpenMaya as OpenMaya2
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
        plug_name = '{}.{}'.format(node, 'matrix')
        plug = node_utils.get_as_plug_apitwo(plug_name)
        times = [1.0, 2, -1.0, -1, 42, 9999, -9999]
        for time in times:
            ctx = mod.create_dg_context_apitwo(time)
            matrix = mod.get_matrix_from_plug_apitwo(plug, ctx)
            assert isinstance(matrix, OpenMaya2.MMatrix)
        return

    # def test_get_double_from_plug_apitwo(self):
    #     # mod.get_double_from_plug_apitwo(plug, ctx)
    #     pass

    # def test_get_parent_inverse_matrix_apitwo(self):
    #     # mod.get_parent_inverse_matrix_apitwo(node, ctx)
    #     pass

    # def test_get_world_matrix_apitwo(self):
    #     # mod.get_world_matrix_apitwo(node, ctx)
    #     pass

    # def test_detect_rotate_pivot_non_zero(self):
    #     # mod.detect_rotate_pivot_non_zero(tfm_node)
    #     pass

    # def test_get_transform_matrix_list(self):
    #     # mod.get_transform_matrix_list()
    #     pass

    # def test_decompose_matrix(self):
    #     # mod.decompose_matrix()
    #     pass

    def test_set_transform_values(self):
        start_frame = 1001
        end_frame = 1101
        node = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(node, attribute='translateX', time=start_frame, value=-100.0)
        maya.cmds.setKeyframe(node, attribute='translateX', time=end_frame, value=100.0)
        maya.cmds.setKeyframe(node, attribute='translateY', time=start_frame, value=-10.0)
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

        mod.set_transform_values(tfm_cache, frame_range,
            tfm_node, dst_tfm_node,
            delete_static_anim_curves=True,
        )

        # save the output scene file
        path = 'test_transform.ma'
        path = self.get_data_path(path)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return

    def test_TransformNode_usage(self):
        start_frame = 1001
        end_frame = 1101
        times = list(range(start_frame, end_frame))
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
        times = list(range(start_frame, end_frame))
        node = maya.cmds.createNode('transform')
        tfm_node = mod.TransformNode(node=node)
        tfm_matrix_cache = mod.TransformMatrixCache()
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
        tfm_matrix_cache.get_node_attr_matrix(
            tfm_node,
            attr_name,
            times
        )
        return


if __name__ == '__main__':
    prog = unittest.main()
