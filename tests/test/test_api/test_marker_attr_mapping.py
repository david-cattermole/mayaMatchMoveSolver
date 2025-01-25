"""
Test querying DG relationship information between Markers and
Attributes.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import time

import maya.cmds

import test.test_api.apiutils as apiUtils
import mmSolver.api as mmapi
import mmSolver.utils.nodeaffects as affects_utils
import mmSolver.tools.solver.lib.collectionstate as collectionstate
import mmSolver.tools.solver.constant as solver_const


# @unittest.skip
class TestMarkerAttrMapping(apiUtils.APITestCase):
    def test_find_marker_attr_mapping(self):
        # top level transform
        root = maya.cmds.createNode('transform', name='top1')

        # Camera A, don't parent under the root.
        cam_tfm_a = maya.cmds.createNode('transform', name='camA_tfm')
        cam_shp_a = maya.cmds.createNode('camera', name='camA_shp', parent=cam_tfm_a)
        maya.cmds.setAttr(cam_tfm_a + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm_a + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm_a + '.tz', -5.0)
        cam_a = mmapi.Camera(shape=cam_shp_a)

        # Camera B, parent under the root
        cam_tfm_b = maya.cmds.createNode('transform', name='camB_tfm', parent=root)
        cam_shp_b = maya.cmds.createNode('camera', name='camB_shp', parent=cam_tfm_b)
        maya.cmds.setAttr(cam_tfm_b + '.tx', 1.0)
        maya.cmds.setAttr(cam_tfm_b + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm_b + '.tz', -5.0)
        cam_b = mmapi.Camera(shape=cam_shp_b)

        # Hierarchy structure
        dummy = maya.cmds.createNode('transform', name='dummy')
        dummy = maya.cmds.ls(dummy, long=True)[0]
        nothing = maya.cmds.createNode('transform', name='nothing')
        nothing = maya.cmds.ls(nothing, long=True)[0]
        top = maya.cmds.createNode('transform', name='top2')
        top = maya.cmds.ls(top, long=True)[0]
        multDivide = maya.cmds.createNode('multiplyDivide', name='multDiv')
        multDivide2 = maya.cmds.createNode('multiplyDivide', name='multDiv2')
        child1 = maya.cmds.createNode('transform', name='child1', parent=top)
        child2 = maya.cmds.createNode('transform', name='child2', parent=child1)
        child1 = maya.cmds.ls(child1, long=True)[0]
        child2 = maya.cmds.ls(child2, long=True)[0]

        # Set up animation and connections
        maya.cmds.setKeyframe(dummy, at='tx', t=1, v=1)
        maya.cmds.setKeyframe(dummy, at='tx', t=10, v=10)
        maya.cmds.connectAttr(dummy + '.tx', child2 + '.ty')
        maya.cmds.connectAttr(dummy + '.tx', child1 + '.tz')
        maya.cmds.connectAttr(dummy + '.ty', top + '.tx')
        maya.cmds.connectAttr(dummy + '.ry', child2 + '.ry')

        maya.cmds.connectAttr(multDivide + '.outputX', dummy + '.ty')
        maya.cmds.connectAttr(multDivide2 + '.outputX', dummy + '.tz')

        maya.cmds.setKeyframe(child2, at='tz', t=1, v=1)
        maya.cmds.setKeyframe(child2, at='tz', t=10, v=10)

        maya.cmds.setKeyframe(top, at='ty', t=1, v=1)
        maya.cmds.setKeyframe(top, at='ty', t=10, v=10)

        maya.cmds.setKeyframe(top, at='tz', t=1, v=1)
        maya.cmds.setKeyframe(top, at='tz', t=10, v=10)

        maya.cmds.setKeyframe(top, at='ry', t=1, v=-90)
        maya.cmds.setKeyframe(top, at='ry', t=10, v=45)

        # Bundle
        bnd = mmapi.Bundle().create_node()
        bundle_tfm = bnd.get_node()
        maya.cmds.setKeyframe(bundle_tfm, at='tx', t=1, v=-1)
        maya.cmds.setKeyframe(bundle_tfm, at='tx', t=10, v=1)
        maya.cmds.parent(bundle_tfm, child2)
        bundle_tfm = bnd.get_node()
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)

        # Marker A
        mkr_a = mmapi.Marker().create_node(cam=cam_a, bnd=bnd)
        marker_tfm = mkr_a.get_node()
        maya.cmds.setAttr(marker_tfm + '.tx', 0.0)

        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        # Marker B
        mkr_b = mmapi.Marker().create_node(cam=cam_b, bnd=bnd)
        marker_tfm = mkr_b.get_node()
        maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

        mkr_list = [mkr_a, mkr_b]

        # Attributes
        attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
        attr_ty = mmapi.Attribute(bundle_tfm + '.ty')
        attr_top_tz = mmapi.Attribute(top + '.tz')

        attr_top_rx = mmapi.Attribute(top + '.rx')
        attr_child1_ty = mmapi.Attribute(child1 + '.ty')
        attr_child1_rx = mmapi.Attribute(child1 + '.rx')

        attr_root_ty = mmapi.Attribute(root + '.ty')
        attr_cam_a_ty = mmapi.Attribute(cam_tfm_a + '.ty')
        attr_cam_a_focal = mmapi.Attribute(cam_shp_a + '.focalLength')

        attr_nothing_tx = mmapi.Attribute(nothing + '.tx')

        attr_list = [
            attr_tx,
            attr_ty,
            attr_top_tz,
            attr_top_rx,
            attr_child1_ty,
            attr_child1_rx,
            attr_root_ty,
            attr_cam_a_ty,
            attr_cam_a_focal,
            attr_nothing_tx,
        ]

        # Test getting affected plugs from a base transform node.
        bnd_node = bnd.get_node()
        ret = affects_utils.find_plugs_affecting_transform(bnd_node, None)
        assert (multDivide + '.input1X') in ret
        assert (dummy + '.translateX') in ret
        assert (dummy + '.rotateY') in ret
        assert (dummy + '.translateY') not in ret
        for r in ret:
            assert nothing not in r
        print('len(ret):', len(ret))
        assert len(ret) == 128

        # Test getting the affect mapping between markers and attrs.
        ret = mmapi.find_marker_attr_mapping(mkr_list, attr_list)
        expected = [
            [True, True, True, True, True, True, False, True, True, False],
            [True, True, True, True, True, True, True, False, False, False],
        ]
        assert ret == expected

        # Save the output
        path = self.get_data_path('find_marker_attr_mapping_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return

    # @unittest.skip
    def test_static_attr_correctness_solver_basic(self):
        s = time.time()
        # Open the Maya file
        file_name = 'solverAffectsCorrectnessSolverBasic.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)

        col = mmapi.Collection(node='myCollection')
        collectionstate.set_solver_type_on_collection(
            col, solver_const.SOLVER_TYPE_CMINPACK_LMDER
        )

        e = time.time()
        print('pre-solve time:', e - s)

        # save the output, before.
        path = self.get_data_path(
            'test_marker_attr_mapping_correctness_solver_basic_before.ma'
        )
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        s = time.time()
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        path = self.get_data_path(
            'test_marker_attr_mapping_correctness_solver_basic_after.ma'
        )
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(
            solres_list, allow_max_avg_error=0.1, allow_max_error=0.1
        )
        return

    # @unittest.skip
    def test_static_attr_correctness_solver_standard(self):
        s = time.time()
        # Open the Maya file
        file_name = 'solverAffectsCorrectnessSolverStandard.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)

        col = mmapi.Collection(node='myCollection')
        collectionstate.set_solver_type_on_collection(
            col, solver_const.SOLVER_TYPE_CMINPACK_LMDER
        )

        e = time.time()
        print('pre-solve time:', e - s)

        # save the output, before.
        path = self.get_data_path(
            'test_marker_attr_mapping_correctness_solver_standard_before.ma'
        )
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        s = time.time()
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        path = self.get_data_path(
            'test_marker_attr_mapping_correctness_solver_standard_after.ma'
        )
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(
            solres_list, allow_max_avg_error=0.1, allow_max_error=0.1
        )
        return


if __name__ == '__main__':
    prog = unittest.main()
