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
Single Frame solve.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import mmSolver.logger
import mmSolver.api as mmapi
import test.test_api.apiutils as test_api_utils


LOG = mmSolver.logger.get_logger()


# @unittest.skip
class TestSolve(test_api_utils.APITestCase):
    def test_init(self):
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
        sol.set_solver_type(mmapi.SOLVER_TYPE_DEFAULT)
        sol.set_verbose(True)
        sol.set_frame_list(frm_list)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolveCollection')
        col.add_solver(sol)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        path = self.get_output_path('test_solve_init_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Set Deviation
        mmapi.update_deviation_on_markers([mkr], results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        path = self.get_output_path('test_solve_init_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.checkSolveResults(results)
        # self.assertApproxEqual(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        # self.assertApproxEqual(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)
        return

    def do_solve_init_solverstandard(
        self, solver_name, solver_type_index, scene_graph_mode
    ):
        """
        Single Frame solve, using the standard solver
        """
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

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
        sol = mmapi.SolverStandard()
        sol.set_verbose(True)
        sol.set_use_single_frame(True)
        sol.set_single_frame(frm_list[0])
        sol.set_global_solve(False)
        sol.set_only_root_frames(False)
        sol.set_solver_type(solver_type_index)
        sol.set_scene_graph_mode(scene_graph_mode)

        # Collection
        col = mmapi.Collection()
        col.create_node('mySolveCollection')
        col.add_solver(sol)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # save the output
        path = self.get_output_path('test_solve_init_solverstandard_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        results = mmapi.execute(col)

        # Set Deviation
        mmapi.update_deviation_on_markers([mkr], results)
        mmapi.update_deviation_on_collection(col, results)

        # save the output
        file_name = 'test_solve_init_solverstandard_{}_{}_after.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.checkSolveResults(
            results, allow_max_avg_error=0.001, allow_max_error=0.001
        )
        # self.assertApproxEqual(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        # self.assertApproxEqual(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)
        return

    def test_init_solverstandard_ceres_lmder_maya_dag(self):
        self.do_solve_init_solverstandard(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_init_solverstandard_ceres_lmder_mmscenegraph(self):
        self.do_solve_init_solverstandard(
            'ceres_lmder', mmapi.SOLVER_TYPE_CERES_LMDER, mmapi.SCENE_GRAPH_MODE_AUTO
        )

    def test_init_solverstandard_ceres_lmdif_maya_dag(self):
        self.do_solve_init_solverstandard(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_init_solverstandard_ceres_lmdif_mmscenegraph(self):
        self.do_solve_init_solverstandard(
            'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF, mmapi.SCENE_GRAPH_MODE_AUTO
        )

    # def test_init_solverstandard_cminpack_lmdif_maya_dag(self):
    #     self.do_solve_init_solverstandard(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # def test_init_solverstandard_cminpack_lmdif_mmscenegraph(self):
    #     self.do_solve_init_solverstandard(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_AUTO,
    #     )

    def test_init_solverstandard_cminpack_lmder_maya_dag(self):
        self.do_solve_init_solverstandard(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_init_solverstandard_cminpack_lmder_mmscenegraph(self):
        self.do_solve_init_solverstandard(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_AUTO,
        )


if __name__ == '__main__':
    prog = unittest.main()
