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
Solve a camera focal length to optimise rotateX, rotateY and focal length.
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
class TestSolver10(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', 0.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        # Marker Group
        mkr_grp = self.create_marker_group('marker_group', cam_tfm)

        # Bundle 1
        bundle1_tfm, bundle1_shp = self.create_bundle('bundle1')
        maya.cmds.setAttr(bundle1_tfm + '.tx', -2.0)
        maya.cmds.setAttr(bundle1_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle1_tfm + '.tz', -25.0)

        # Bundle 2
        bundle2_tfm, bundle2_shp = self.create_bundle('bundle2')
        maya.cmds.setAttr(bundle2_tfm + '.tx', 0.0)
        maya.cmds.setAttr(bundle2_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle2_tfm + '.tz', -25.0)

        # Marker 1
        marker1_tfm, marker1_shp = self.create_marker(
            'marker1', mkr_grp, bnd_tfm=bundle1_tfm
        )
        maya.cmds.setAttr(marker1_tfm + '.tx', -0.2)
        maya.cmds.setAttr(marker1_tfm + '.ty', 0.13)
        maya.cmds.setAttr(marker1_tfm + '.tz', -1.0)

        # Marker 2
        marker2_tfm, marker2_shp = self.create_marker(
            'marker2', mkr_grp, bnd_tfm=bundle2_tfm
        )
        maya.cmds.setAttr(marker2_tfm + '.tx', 0.2)
        maya.cmds.setAttr(marker2_tfm + '.ty', 0.13)
        maya.cmds.setAttr(marker2_tfm + '.tz', -1.0)

        # save the output
        path = self.get_data_path('solver_test10_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        cameras = ((cam_tfm, cam_shp),)
        markers = (
            (marker1_tfm, cam_shp, bundle1_tfm),
            (marker2_tfm, cam_shp, bundle2_tfm),
        )
        node_attrs = [
            (cam_tfm + '.rx', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.ry', 'None', 'None', 'None', 'None'),
            # (cam_tfm + '.rz', 'None', 'None', 'None', 'None'),
            (cam_shp + '.focalLength', 'None', 'None', 'None', 'None'),
        ]
        frames = [
            (1),
        ]

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
            'frame': frames,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            iterations=1000,
            solverType=solver_index,
            sceneGraphMode=scene_graph_mode,
            verbose=True,
            **kwargs
        )
        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = 'solver_test10_{}_{}_after.ma'.format(solver_name, scene_graph_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')

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

    def test_init_ceres_lmdif_maya_dag(self):
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_init_ceres_lmdif_mmscenegraph(self):
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )

    def test_init_cminpack_lmdif_maya_dag(self):
        self.do_solve(
            'cminpack_lmdif',
            mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_init_cminpack_lmdif_mmscenegraph(self):
        self.do_solve(
            'cminpack_lmdif',
            mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )

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
