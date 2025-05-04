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
Semi-Complex hierarchy and object-space utilising solve.
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
class TestSolver2(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index, scene_graph_mode):
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

        group_tfm = maya.cmds.createNode('transform', name='group_tfm')
        bundle1_tfm, bundle1_shp = self.create_bundle('bundle1', parent=group_tfm)
        bundle2_tfm, bundle2_shp = self.create_bundle('bundle2', parent=group_tfm)
        maya.cmds.setAttr(bundle1_tfm + '.tx', 10.0)
        maya.cmds.setAttr(bundle2_tfm + '.tx', -10.0)
        maya.cmds.setAttr(group_tfm + '.ry', 45.0)
        maya.cmds.setAttr(group_tfm + '.tz', -35.0)

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)

        marker1_tfm, marker1_shp = self.create_marker(
            'marker1', mkr_grp, bnd_tfm=bundle1_tfm
        )
        maya.cmds.setAttr(marker1_tfm + '.tx', -0.243056042)
        maya.cmds.setAttr(marker1_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker1_tfm + '.tz', -1.0)

        marker2_tfm, marker2_shp = self.create_marker(
            'marker2', mkr_grp, bnd_tfm=bundle2_tfm
        )
        maya.cmds.setAttr(marker2_tfm + '.tx', 0.405093403)
        maya.cmds.setAttr(marker2_tfm + '.ty', -0.194444833)
        maya.cmds.setAttr(marker2_tfm + '.tz', -1.0)

        cameras = ((cam_tfm, cam_shp),)
        markers = (
            (marker1_tfm, cam_shp, bundle1_tfm),
            (marker2_tfm, cam_shp, bundle2_tfm),
        )
        node_attrs = [
            (group_tfm + '.tx', 'None', 'None', 'None', 'None'),
            (group_tfm + '.ty', 'None', 'None', 'None', 'None'),
            (group_tfm + '.tz', 'None', 'None', 'None', 'None'),
            (group_tfm + '.sx', 'None', 'None', 'None', 'None'),
            (group_tfm + '.ry', 'None', 'None', 'None', 'None'),
            (group_tfm + '.rz', 'None', 'None', 'None', 'None'),
        ]
        frames = [
            (1),
        ]

        # save the output
        file_name = 'solver_test2_{}_{}_before.ma'.format(solver_name, scene_graph_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
            'frame': frames,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver, with more attributes than markers; We expect an error.
        s = time.time()
        result = maya.cmds.mmSolver(
            iterations=1000,
            solverType=solver_index,
            sceneGraphMode=scene_graph_mode,
            **kwargs
        )
        e = time.time()
        print('total time:', e - s)
        self.assertEqual(result[0], 'success=0')
        tx = maya.cmds.getAttr(group_tfm + '.tx')
        ty = maya.cmds.getAttr(group_tfm + '.ty')
        tz = maya.cmds.getAttr(group_tfm + '.tz')
        sx = maya.cmds.getAttr(group_tfm + '.sx')
        ry = maya.cmds.getAttr(group_tfm + '.ry')
        rz = maya.cmds.getAttr(group_tfm + '.rz')
        print('tx:', tx)
        print('ty:', ty)
        print('tz:', tz)
        print('sx:', sx)
        print('ry:', ry)
        print('rz:', rz)

        # Run solver! (with less attributes)
        node_attrs = [
            (group_tfm + '.tx', 'None', 'None', 'None', 'None'),
            (group_tfm + '.ty', 'None', 'None', 'None', 'None'),
            (group_tfm + '.sx', 'None', 'None', 'None', 'None'),
            (group_tfm + '.rz', 'None', 'None', 'None', 'None'),
        ]

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
            'frame': frames,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        s = time.time()
        result = maya.cmds.mmSolver(iterations=1000, solverType=solver_index, **kwargs)
        e = time.time()
        print('total time:', e - s)

        tx = maya.cmds.getAttr(group_tfm + '.tx')
        ty = maya.cmds.getAttr(group_tfm + '.ty')
        sx = maya.cmds.getAttr(group_tfm + '.sx')
        rz = maya.cmds.getAttr(group_tfm + '.rz')
        print('tx:', tx)
        print('ty:', ty)
        print('sx:', sx)
        print('rz:', rz)

        # save the output
        file_name = 'solver_test2_{}_{}_after.ma'.format(solver_name, scene_graph_name)
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
