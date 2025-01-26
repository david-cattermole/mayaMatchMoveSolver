# Copyright (C) 2023 David Cattermole.
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
A test solve for the tutorial "Solve Robot Arm Rig Hierarchy with
mmSolver":
https://www.youtube.com/watch?v=y9U2QZT-VxA

This test intends to reproduce the issue #248:
https://github.com/david-cattermole/mayaMatchMoveSolver/issues/248
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.lib.mayareadfile as marker_read
import mmSolver.tools.createlens.lib as createlens_lib
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolveRobotArm(test_api_utils.APITestCase):
    def do_solve(self, solver_name, solver_type_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        # Open the scene file.
        scene_file_path = self.get_data_path('scenes', 'robotArm_v001.ma')
        maya.cmds.file(scene_file_path, open=True, force=True, ignoreVersion=True)

        # Time Range
        start = 1087  # 1001
        end = 1089  # 1387
        maya.cmds.playbackOptions(
            animationStartTime=start, minTime=start, animationEndTime=end, maxTime=end
        )

        # Camera
        cam_tfm = '|camera_GRP|trackCamera'
        cam_shp = '|camera_GRP|trackCamera|trackCameraShape'
        cam = mmapi.Camera(shape=cam_shp)

        # Marker Group
        mkr_grp = mmapi.MarkerGroup(node='|camera_GRP|trackCamera|markerGroup1')

        # Markers
        mkr_nodes = maya.cmds.ls('*_MKR', long=True)
        mkr_list = []
        for mkr_node in mkr_nodes:
            mkr = mmapi.Marker(node=mkr_node)
            mkr_list.append(mkr)

        # Root frames
        root_frm_list = []
        min_frames_per_marker = 3
        frame_nums = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, start, end
        )
        frame_nums = mmapi.root_frames_list_combine(frame_nums, [start, end])
        max_frame_span = 5
        frame_nums = mmapi.root_frames_subdivide(frame_nums, max_frame_span)
        for f in frame_nums:
            frm = mmapi.Frame(f)
            root_frm_list.append(frm)

        # Frames
        frm_list = []
        for f in range(start, end + 1):
            frm = mmapi.Frame(f)
            frm_list.append(frm)

        # Solver.
        #
        # We could use a 'mmapi.SolverStandard()' instead and get a
        # proper solve.
        use_standard_solver = True
        sol_list = []
        if use_standard_solver is True:
            sol = mmapi.SolverStandard()
            sol.set_root_frame_list(root_frm_list)
        else:
            sol = mmapi.SolverBasic()
        sol.set_frame_list(frm_list)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)
        sol_list.append(sol)

        # Collection
        col = mmapi.Collection(node='collection1')
        col.add_solver_list(sol_list)

        # Add markers
        col.add_marker_list(mkr_list)

        # save the output
        file_name = 'test_solve_robotArm_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Ensure the values are correct
        for res in results:
            success = res.get_success()
            err = res.get_final_error()
            print('err', err, 'success', success)

        # Set Deviation
        mmapi.update_deviation_on_markers(mkr_list, results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        file_name = 'test_solve_robotArm_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.checkSolveResults(results, allow_max_avg_error=6.14, allow_max_error=6.51)
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
