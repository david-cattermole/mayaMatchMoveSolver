# Copyright (C) 2018, 2019, 2022 David Cattermole.
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
Solve lens distortion with 2D Lines.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest
import time

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolve(test_api_utils.APITestCase):
    def do_solve(self, solver_name, solver_type_index, scene_graph_mode):
        """
        Single Frame solve, using the standard solver
        """
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        s = time.time()
        # Open the Maya file
        file_name = 'lens_distortion_lines_v002.ma'
        path = self.get_data_path('scenes', file_name)
        maya.cmds.file(path, open=True, force=True, ignoreVersion=True)

        # Get Markers
        col = mmapi.Collection(node='collection1')
        mkr_list = col.get_marker_list()
        mkr_list = sorted(mkr_list, key=lambda mkr: mkr.get_node())

        # Lens
        lens = mmapi.Lens(node='lens1')
        lens_node = lens.get_node()
        lens_attr_a = lens_node + '.tdeRadialStdDeg4_degree2_distortion'
        lens_attr_b = lens_node + '.tdeRadialStdDeg4_degree4_distortion'
        attr_a = mmapi.Attribute(lens_attr_a)
        attr_b = mmapi.Attribute(lens_attr_b)
        attr_list = [attr_a, attr_b]

        # Frames
        frm_list = [mmapi.Frame(1, primary=True)]

        # Run solver!
        sol_list = []
        sol = mmapi.SolverStandard()
        sol.set_use_single_frame(True)
        sol.set_single_frame(frm_list[0])
        sol.set_only_root_frames(False)
        sol.set_global_solve(False)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol_list.append(sol)

        # Collection
        col.set_marker_list(mkr_list)
        col.set_attribute_list(attr_list)
        col.set_solver_list(sol_list)
        e = time.time()
        print('pre-solve time:', e - s)

        # save the output
        file_name = 'test_solve_line_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Set Deviation
        mmapi.update_deviation_on_markers(mkr_list, results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        file_name = 'test_solve_line_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.checkSolveResults(results, allow_max_avg_error=4.0, allow_max_error=4.0)
        return

    def test_line_ceres_lmdif_maya_dag(self):
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_line_ceres_lmdif_mmscenegraph(self):
        self.do_solve(
            'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF, mmapi.SCENE_GRAPH_MODE_AUTO
        )

    # def test_line_cminpack_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # def test_line_cminpack_lmdif_mmscenegraph(self):
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
