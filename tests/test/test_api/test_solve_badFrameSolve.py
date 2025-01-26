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
This file solves wildly, with each frame good, then next bad. The
animCurves created are very spikey, but we expect to solve a smooth
curve.

When opening the scene file manually using the GUI, and running the
solver, the undo-ing the (bad) result, the timeline is traversed
slowly. This shows issue #45.
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
class TestSolveBadPerFrameSolve(test_api_utils.APITestCase):
    def do_solve(self, solver_name, solver_type_index, scene_graph_mode):
        """
        The same test as 'test_badPerFrameSolve', but using the SolverStandard class.

        NOTE: Using the 'MM Scene Graph' scene graph doesn't correctly
        solve this test because it's using an object solve that has a
        non-zero pivot point.
        """
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        s = time.time()

        # Open the Maya file
        file_name = 'mmSolverBasicSolveA_badSolve01.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)
        print('File opened:', path)

        # MM Scene Graph does not support filmFit values other than
        # 'horizontal'.
        filmFit = 1  # 1 = Horizontal
        maya.cmds.setAttr('cameraShape1.filmFit', filmFit)

        # Frames
        start_frame = 1
        end_frame = 120
        root_frames = [1, 30, 60, 90, 120]
        root_frm_list = []
        for f in root_frames:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)
        # print('root frames:', root_frm_list)

        frm_list = []
        for f in range(start_frame, end_frame):
            frm = mmapi.Frame(f)
            frm_list.append(frm)
        # print('frames:', frm_list)

        # Solver
        sol = mmapi.SolverStandard()
        sol.set_root_frame_list(root_frm_list)
        sol.set_frame_list(frm_list)
        sol.set_use_single_frame(False)
        sol.set_global_solve(False)
        sol.set_only_root_frames(False)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol_list = [sol]
        # print('Solver:', sol)
        e = time.time()
        print('pre-solve time:', e - s)

        # Run solver!
        s = time.time()
        col = mmapi.Collection(node='collection1')
        col.set_solver_list(sol_list)
        solres_list = mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # Set Deviation
        mkr_list = col.get_marker_list()
        mmapi.update_deviation_on_markers(mkr_list, solres_list)
        mmapi.update_deviation_on_collection(col, solres_list)

        # save the output
        file_name = 'test_solve_badPerFrameSolve_solverstandard_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(
            solres_list, allow_max_avg_error=0.01, allow_max_error=0.03
        )
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

    def test_ceres_lmdif_maya_dag(self):
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_ceres_lmdif_mmscenegraph(self):
        self.do_solve(
            'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF, mmapi.SCENE_GRAPH_MODE_AUTO
        )

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
