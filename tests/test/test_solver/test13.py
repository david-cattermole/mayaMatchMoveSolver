# Copyright (C) 2018, 2019, 2025 David Cattermole.
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
Testing a single point nodal camera solve on a single frame.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import unittest

try:
    import maya.standalone

    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import mmSolver.api as mmapi

import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestSolver13(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index, scene_graph_mode):
        """
        Solve nodal camera on a frames. Some of the frames do not
        have enough markers for the number of parameters being
        solved. As a result, this test is intended to test the valid
        frames approach.
        """
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        bundle1_tfm, bundle1_shp = self.create_bundle('bundle1')
        maya.cmds.setAttr(bundle1_tfm + '.tx', -5.5)
        maya.cmds.setAttr(bundle1_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle1_tfm + '.tz', -25.0)

        bundle2_tfm, bundle2_shp = self.create_bundle('bundle2')
        maya.cmds.setAttr(bundle2_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle2_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle2_tfm + '.tz', -25.0)

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)

        marker_01_tfm, marker_01_shp = self.create_marker('marker1', mkr_grp)
        maya.cmds.setAttr(marker_01_tfm + '.tx', -0.253056042)
        maya.cmds.setAttr(marker_01_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker_01_tfm + '.tz', -1.0)

        marker_02_tfm, marker_02_shp = self.create_marker('marker2', mkr_grp)
        maya.cmds.setAttr(marker_02_tfm + '.tx', 0.253056042)
        maya.cmds.setAttr(marker_02_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker_02_tfm + '.tz', -1.0)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='enable', time=1, value=1)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='enable', time=2, value=0)

        cameras = ((cam_tfm, cam_shp),)
        markers = (
            (marker_01_tfm, cam_shp, bundle1_tfm),
            (marker_02_tfm, cam_shp, bundle2_tfm),
        )
        node_attrs = [
            (cam_tfm + '.rx', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.ry', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.rz', 'None', 'None', 'None', 'None'),
        ]
        frames = [
            1,
            2,
        ]

        # save the output
        file_name = 'solver_test13_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(
            affects_mode,
            frame=frames,
            **kwargs
        )

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            frame=frames,
            solverType=solver_index,
            sceneGraphMode=scene_graph_mode,
            delta=0.00001,
            verbose=True,
            **kwargs
        )
        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = 'solver_test13_{}_{}_after.ma'.format(solver_name, scene_graph_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        rx = maya.cmds.getAttr(cam_tfm + '.rx')
        ry = maya.cmds.getAttr(cam_tfm + '.ry')
        rz = maya.cmds.getAttr(cam_tfm + '.rz')
        print('rx =', rx)
        print('ry =', ry)
        print('rz =', rz)
        self.assertApproxEqual(rx, 7.72, eps=0.01)
        self.assertApproxEqual(ry, -2.377, eps=0.01)
        self.assertApproxEqual(rz, -0.636, eps=0.001)

    def test_init_ceres_lmder_maya_dag(self):
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_init_ceres_lmder_mmscenegraph(self):
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )

    # # NOTE: This solver and scene graph combination fails to solve for
    # # some reason.
    # def test_init_ceres_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'ceres_lmdif',
    #         mmapi.SOLVER_TYPE_CERES_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # def test_init_ceres_lmdif_mmscenegraph(self):
    #     self.do_solve(
    #         'ceres_lmdif',
    #         mmapi.SOLVER_TYPE_CERES_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
    #     )

    # def test_init_cminpack_lmdif_maya_dag(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
    #     )

    # def test_init_cminpack_lmdif_mmscenegraph(self):
    #     self.do_solve(
    #         'cminpack_lmdif',
    #         mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
    #         mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
    #     )

    def test_init_cminpack_lmder_maya_dag(self):
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_init_cminpack_lmder_mmscenegraph(self):
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )


if __name__ == '__main__':
    prog = unittest.main()
