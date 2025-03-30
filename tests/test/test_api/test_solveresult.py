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
Test functions for API utils module.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import pprint
import unittest
import time

import maya.cmds

import test.test_api.apiutils as test_api_utils
import mmSolver._api.solveresult as solveresult  # used indirectly.
import mmSolver.api as mmapi


def create_example_solve_scene():
    """
    Very basic single frame solver set up.

    This function does not execute the solve, execution must be done manually.

    :return: API Collection object.
    """
    # Camera
    cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
    cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
    maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
    maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
    maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
    cam = mmapi.Camera(shape=cam_shp)

    # Bundle
    bnd = mmapi.Bundle().create_node()
    bundle_tfm = bnd.get_node()
    maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
    maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
    maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
    assert mmapi.get_object_type(bundle_tfm) == 'bundle'

    # Marker
    mkr = mmapi.Marker().create_node(cam=cam, bnd=bnd)
    marker_tfm = mkr.get_node()
    assert mmapi.get_object_type(marker_tfm) == 'marker'
    maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
    maya.cmds.setAttr(marker_tfm + '.ty', 0.0)

    # Attributes
    attr_tx = mmapi.Attribute(bundle_tfm + '.tx')
    attr_ty = mmapi.Attribute(bundle_tfm + '.ty')

    # Frames
    frm_list = [mmapi.Frame(1, primary=True)]

    # Solver
    sol = mmapi.Solver()
    sol.set_max_iterations(10)
    sol.set_verbose(True)
    sol.set_frame_list(frm_list)

    # Collection
    col = mmapi.Collection()
    col.create_node('mySolveCollection')
    col.add_solver(sol)
    col.add_marker(mkr)
    col.add_attribute(attr_tx)
    col.add_attribute(attr_ty)
    return col


# @unittest.skip
class TestSolveResult(test_api_utils.APITestCase):
    def test_init(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        print('error stats: ' + pprint.pformat(results[0].get_error_stats()))
        print('timer stats: ' + pprint.pformat(results[0].get_timer_stats()))
        print('solver stats: ' + pprint.pformat(results[0].get_solver_stats()))
        print(
            'frame error list: '
            + pprint.pformat(dict(results[0].get_frame_error_list()))
        )
        print(
            'marker error list: '
            + pprint.pformat(dict(results[0].get_marker_error_list()))
        )

    def test_combine_timer_stats(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        timer_stats = mmapi.combine_timer_stats(results)
        assert isinstance(timer_stats, dict)
        for k, v in timer_stats.items():
            assert v >= 0

    def test_merge_frame_error_list(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_error_list = mmapi.merge_frame_error_list(results)
        assert isinstance(frame_error_list, dict)

    def test_merge_frame_list(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_list = mmapi.merge_frame_list(results)
        assert isinstance(frame_list, list)
        assert len(frame_list) > 0

    def test_get_average_frame_error_list(self):
        frame_error_list = {1: 0, 2: 0.5, 3: 1.0}
        v = mmapi.get_average_frame_error_list(frame_error_list)
        self.assertApproxEqual(v, 0.5)

        frame_error_list = {1: 1.0}
        v = mmapi.get_average_frame_error_list(frame_error_list)
        self.assertApproxEqual(v, 1.0)

        frame_error_list = {}
        v = mmapi.get_average_frame_error_list(frame_error_list)
        self.assertApproxEqual(v, 0.0)

        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_error_list = dict(results[0].get_frame_error_list())

        v = mmapi.get_average_frame_error_list(frame_error_list)
        assert isinstance(v, float)

    def test_get_max_frame_error(self):
        frame_error_list = {1: 0, 2: 0.5, 3: 1.0}
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert isinstance(frm, int)
        self.assertApproxEqual(frm, 3)
        self.assertApproxEqual(val, 1.0)

        frame_error_list = {1: 1.0}
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert isinstance(frm, int)
        self.assertApproxEqual(frm, 1)
        self.assertApproxEqual(val, 1.0)

        frame_error_list = {}
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert frm is None
        self.assertApproxEqual(val, -0.0)

        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        frame_error_list = dict(results[0].get_frame_error_list())
        frm, val = mmapi.get_max_frame_error(frame_error_list)
        assert frm is None or isinstance(frm, float) or isinstance(frm, int)
        assert isinstance(val, float)

    def test_merge_marker_error_list(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        marker_error_list = mmapi.merge_marker_error_list(results)
        assert isinstance(marker_error_list, dict)
        assert len(marker_error_list) > 0

    def test_merge_marker_node_list(self):
        col = create_example_solve_scene()
        results = col.execute()
        success = results[0].get_success()
        err = results[0].get_final_error()
        self.assertTrue(isinstance(success, bool))
        self.assertTrue(isinstance(err, float))

        nodes = mmapi.merge_marker_node_list(results)
        assert isinstance(nodes, list)
        assert len(nodes) > 0

    def do_solve(self, solver_name, solver_type_index, scene_graph_mode):
        """
        Open a file and trigger a solve to get perfect results.
        Make sure solver results doesn't fail in this case.
        """
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        start_frame = 1
        end_frame = 120

        # Open the Maya file
        file_name = 'mmSolverBasicSolveA_triggerMaxFrameErrorTraceback.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True)

        # Collection.
        col = mmapi.Collection(node='collection1')

        # Frames
        root_frm_list = [
            mmapi.Frame(1),
            mmapi.Frame(30),
            mmapi.Frame(60),
            mmapi.Frame(90),
            mmapi.Frame(120),
        ]
        not_root_frm_list = []
        for f in range(start_frame, end_frame + 1):
            frm = mmapi.Frame(f)
            not_root_frm_list.append(frm)

        # Solvers
        sol_list = []
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(not_root_frm_list)
        sol.set_only_root_frames(False)
        sol.set_global_solve(False)
        sol.set_use_single_frame(False)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol_list.append(sol)
        col.set_solver_list(sol_list)

        # save the output
        file_name = 'solveresult_testPerfectSolve_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        s = time.time()
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = 'solveresult_testPerfectSolve_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        solres = solres_list[0]
        success = solres.get_success()
        err = solres.get_final_error()
        frame_error_list = mmapi.merge_frame_error_list([solres])
        avg_error = mmapi.get_average_frame_error_list(frame_error_list)
        max_frame_error = mmapi.get_max_frame_error(frame_error_list)
        solver_valid_frames = solres.get_solver_valid_frame_list()
        solver_invalid_frames = solres.get_solver_invalid_frame_list()
        print('solver_frames_stats:', pprint.pformat(solres.get_solver_frames_stats()))
        print('solver_valid_frames:', solver_valid_frames)
        print('solver_invalid_frames:', solver_invalid_frames)
        # self.assertEqual(max_frame_error[0], 120)
        self.assertIsInstance(max_frame_error[0], int)
        self.assertIsInstance(max_frame_error[1], float)
        self.assertTrue(success)
        self.assertLess(avg_error, 1.0)
        self.assertGreater(err, 0.0)
        return

    def test_ceres_lmder_maya_dag(self):
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

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

    def test_cminpack_lmder_maya_dag(self):
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_cminpack_lmder_mmscenegraph(self):
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_AUTO,
        )


if __name__ == '__main__':
    prog = unittest.main()
