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
Solving with the scene file 'mmSolverBasicSolveB_before.ma', was
reported to solve as static values, the same as the initial
values. The DG did not evaluate some how and the solve was therefore
useless.

GitHub Issue #53.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolveIssue53(test_api_utils.APITestCase):

    # @unittest.skip
    def do_solve(self, solver_name, solver_type_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        s = time.time()
        # Open the Maya file
        file_name = 'mmSolverBasicSolveB_before.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)

        # NOTE: We leave these nodes alone, since these are already in
        # the 'correct' position, we are treating these as surveyed.
        # When we have less than 3 points as survey the solve goes
        # crazy.
        dont_touch_these_nodes = [
            '|bundle_12_BND',
            '|bundle_13_BND',
            '|bundle_14_BND',
        ]

        nodes = sorted(maya.cmds.ls(type='transform') or [])
        bnd_nodes = mmapi.filter_bundle_nodes(nodes)
        bnd_list = [mmapi.Bundle(node=n) for n in bnd_nodes]
        for bnd in bnd_list:
            bnd_node = bnd.get_node()
            if bnd_node in dont_touch_these_nodes:
                continue
            attrs = ['translateX', 'translateY', 'translateZ']
            for attr_name in attrs:
                plug = bnd_node + '.' + attr_name
                maya.cmds.setAttr(plug, lock=False)
                maya.cmds.setAttr(plug, 0.0)

        # Get Bundle attributes to compute.
        bnd_attr_list = []
        for bnd in bnd_list:
            node = bnd.get_node()
            attrs = ['translateX', 'translateY', 'translateZ']
            for attr_name in attrs:
                attr = mmapi.Attribute(node=node, attr=attr_name)
                bnd_attr_list.append(attr)

        # Camera attributes
        cam_tfm = 'stA_1_1'
        cam = mmapi.Camera(cam_tfm)
        cam_shp = cam.get_shape_node()
        maya.cmds.setAttr('{}.filmFit'.format(cam_shp), 1)  # 1 = Horizontal
        cam_attr_list = []
        attrs = [
            'translateX',
            'translateY',
            'translateZ',
            'rotateX',
            'rotateY',
            'rotateZ',
        ]
        for attr_name in attrs:
            attr = mmapi.Attribute(node=cam_tfm, attr=attr_name)
            cam_attr_list.append(attr)
        attr = mmapi.Attribute(node=cam_shp, attr='focalLength')
        cam_attr_list.append(attr)

        # Get Markers
        col = mmapi.Collection(node='collection1')
        mkr_list = col.get_marker_list()
        mkr_list = sorted(mkr_list, key=lambda mkr: mkr.get_node())

        # Frames
        #
        # Root Frames are automatically calculated from the markers.
        root_frm_list = []
        not_root_frm_list = []
        start_frame = 0
        end_frame = 94
        min_frames_per_marker = 2
        f_list = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame
        )
        f_list = mmapi.root_frames_list_combine(f_list, [start_frame, end_frame])
        max_frame_span = 5
        f_list = mmapi.root_frames_subdivide(f_list, max_frame_span)
        for f in f_list:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        for f in range(start_frame, end_frame + 1):
            frm = mmapi.Frame(f)
            not_root_frm_list.append(frm)

        # Run solver!
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(not_root_frm_list)
        sol.set_only_root_frames(False)
        sol.set_global_solve(False)
        sol.set_single_frame(False)
        sol.set_triangulate_bundles(False)
        sol.set_use_attr_blocks(False)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)

        attr_list = cam_attr_list + bnd_attr_list
        col.set_attribute_list(attr_list)
        col.set_solver_list([sol])
        e = time.time()
        print('pre-solve time:', e - s)

        # save the output, before.
        file_name = 'test_solve_issue53_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
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
        file_name = 'test_solve_issue53_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure all frames have been keyed (and therefore we assume
        # it's been solved).
        attrs = [
            'translateX',
            'translateY',
            'translateZ',
            'rotateX',
            'rotateY',
            'rotateZ',
        ]
        total_frame_count = (end_frame - start_frame) + 1
        for attr in attrs:
            node_attr = '{}.{}'.format(cam_tfm, attr)
            print('Check Camera Attr:', repr(node_attr))
            key_count = maya.cmds.keyframe(node_attr, query=True, keyframeCount=True)
            self.assertEqual(key_count, total_frame_count)

        self.checkSolveResults(
            solres_list, allow_max_avg_error=0.7, allow_max_error=0.94
        )
        return

    # def test_ceres_lmder_maya_dag(self):
    #     self.do_solve(
    #         'ceres_lmder',
    #         mmapi.SOLVER_TYPE_CERES_LMDER,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    def test_ceres_lmder_mmscenegraph(self):
        self.do_solve(
            'ceres_lmder', mmapi.SOLVER_TYPE_CERES_LMDER, mmapi.SCENE_GRAPH_MODE_AUTO
        )

    # def test_ceres_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'ceres_lmdif',
    #         mmapi.SOLVER_TYPE_CERES_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # def test_ceres_lmdif_mmscenegraph(self):
    #     self.do_solve(
    #         'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF, mmapi.SCENE_GRAPH_MODE_AUTO
    #     )

    # def test_cminpack_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # def test_cminpack_lmdif_mmscenegraph(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_AUTO,
    #     )

    # def test_cminpack_lmder_maya_dag(self):
    #     self.do_solve(
    #         'cminpack_lmder',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDER,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    def test_cminpack_lmder_mmscenegraph(self):
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_AUTO,
        )


if __name__ == '__main__':
    prog = unittest.main()
