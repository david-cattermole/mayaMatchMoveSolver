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
Solving only a 'all frames' solver step across multiple frames.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.api as mmapi
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolveAllFrameStrategySolve(test_api_utils.APITestCase):
    def do_solve(self, solver_name, solver_type_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        # Open the Maya file
        file_name = 'mmSolverBasicSolveA_badSolve02.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)

        # Collection
        col = mmapi.Collection(node='collection1')
        mkr_list = col.get_marker_list()

        # Frames
        #
        # Root Frames are automatically calculated from the markers.
        root_frm_list = []
        not_root_frm_list = []
        start_frame, end_frame = time_utils.get_maya_timeline_range_inner()
        min_frames_per_marker = 3
        frame_nums = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start_frame, end_frame
        )
        frame_nums = mmapi.root_frames_list_combine(
            frame_nums, [start_frame, end_frame]
        )
        max_frame_span = 5
        frame_nums = mmapi.root_frames_subdivide(frame_nums, max_frame_span)
        for f in frame_nums:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        for f in range(0, 41):
            frm = mmapi.Frame(f)
            not_root_frm_list.append(frm)

        # Define Solver
        sol_list = []
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(not_root_frm_list)
        sol.set_only_root_frames(False)
        sol.set_global_solve(False)
        sol.set_single_frame(False)
        sol.set_root_frame_strategy(mmapi.ROOT_FRAME_STRATEGY_GLOBAL_VALUE)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol_list.append(sol)
        col.set_solver_list(sol_list)

        # Run solver!
        s = time.time()
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Ensure the values are correct
        for solres in solres_list:
            success = solres.get_success()
            err = solres.get_final_error()
            print('err', err, 'success', success)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        file_name = 'test_solve_allFrameStrategySolve_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(
            solres_list, allow_max_avg_error=0.7, allow_max_error=1.1
        )
        return

    # # NOTE: This solve is too slow and inaccurate - there doesn't seem
    # # to be a point in running it.
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

    # # NOTE: This solve is too slow and inaccurate - there doesn't seem
    # # to be a point in running it.
    # def test_ceres_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'ceres_lmdif',
    #         mmapi.SOLVER_TYPE_CERES_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # # NOTE: Commented out because the results aren't good enough.
    # def test_ceres_lmdif_mmscenegraph(self):
    #     self.do_solve(
    #         'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF, mmapi.SCENE_GRAPH_MODE_AUTO
    #     )

    # # NOTE: This solve is too slow and inaccurate - there doesn't seem
    # # to be a point in running it.
    # def test_cminpack_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # # NOTE: Commented out because the results aren't good enough.
    # def test_cminpack_lmdif_mmscenegraph(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_AUTO,
    #     )

    # # NOTE: This solve is too slow and inaccurate - there doesn't seem
    # # to be a point in running it.
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
