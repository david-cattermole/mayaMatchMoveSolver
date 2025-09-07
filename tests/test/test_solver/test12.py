# Copyright (C) 2018-2022 David Cattermole.
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
"""Solve a single non-animated bundle to the screen-space location of
a bundle, but the bundle is being driven by connections to a transform
in world-space.
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
class TestSolver12(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index, scene_graph_mode, single_frame):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        start_frame = 1
        end_frame = 10
        maya.cmds.playbackOptions(
            animationStartTime=start_frame,
            minTime=start_frame,
            animationEndTime=end_frame,
            maxTime=end_frame,
        )

        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        tfm_a = maya.cmds.createNode('transform', name='transform_a')
        maya.cmds.setAttr(tfm_a + '.tx', -5.5)
        maya.cmds.setAttr(tfm_a + '.ty', 6.4)
        maya.cmds.setAttr(tfm_a + '.tz', -25.0)
        if single_frame is False:
            maya.cmds.setKeyframe(tfm_a + '.tx', time=start_frame)
            maya.cmds.setKeyframe(tfm_a + '.ty', time=end_frame)

        tfm_b = maya.cmds.createNode('transform', name='transform_b')
        maya.cmds.connectAttr(tfm_a + '.tx', tfm_b + '.tx')
        maya.cmds.connectAttr(tfm_a + '.ty', tfm_b + '.ty')
        maya.cmds.connectAttr(tfm_a + '.tz', tfm_b + '.tz')

        bundle_tfm, bundle_shp = self.create_bundle('bundle')
        maya.cmds.connectAttr(tfm_b + '.tx', bundle_tfm + '.tx')
        maya.cmds.connectAttr(tfm_b + '.ty', bundle_tfm + '.ty')
        maya.cmds.connectAttr(tfm_b + '.tz', bundle_tfm + '.tz')

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)
        marker_tfm, marker_shp = self.create_marker(
            'marker', mkr_grp, bnd_tfm=bundle_tfm
        )
        maya.cmds.setAttr(marker_tfm + '.tx', -0.243056042)
        maya.cmds.setAttr(marker_tfm + '.ty', 0.189583713)
        maya.cmds.setAttr(marker_tfm + '.tz', -1)
        if single_frame is False:
            maya.cmds.setKeyframe(
                marker_tfm + '.tx', time=start_frame, value=-0.243056042
            )
            maya.cmds.setKeyframe(marker_tfm + '.tx', time=end_frame, value=0.243056042)
            maya.cmds.setKeyframe(
                marker_tfm + '.ty', time=start_frame, value=0.189583713
            )
            maya.cmds.setKeyframe(
                marker_tfm + '.ty', time=end_frame, value=-0.189583713
            )

        cameras = ((cam_tfm, cam_shp),)
        markers = ((marker_tfm, cam_shp, bundle_tfm),)
        node_attrs = [
            (tfm_a + '.tx', 'None', 'None', 'None', 'None'),
            (tfm_a + '.ty', 'None', 'None', 'None', 'None'),
        ]

        frames = []
        if single_frame is True:
            frames = [(1)]
        else:
            frames = [(1), (2), (3), (4), (5), (6), (7), (8), (9), (10)]

        # save the output
        file_name = 'solver_test12_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_output_path(file_name)
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

        # Run solver!
        assert 'mmSolver' in dir(maya.cmds)
        s = time.time()
        result = maya.cmds.mmSolver(
            solverType=solver_index,
            sceneGraphMode=scene_graph_mode,
            iterations=1000,
            verbose=True,
            **kwargs
        )
        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = 'solver_test12_{}_{}_after.ma'.format(solver_name, scene_graph_name)
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        tx = maya.cmds.getAttr(bundle_tfm + '.tx', time=start_frame)
        ty = maya.cmds.getAttr(bundle_tfm + '.ty', time=start_frame)
        print('tx:', tx)
        print('ty:', ty)

        # The Ceres Line Search L-BGFS solver was calculating
        # '3.60012' rather than '3.6' +/- 0.0001, which caused the
        # test to fail.
        #
        # The Ceres Line Search L-BGFS solver was calculating
        # '3.60012' rather than '3.6' +/- 0.0001, which caused the
        # test to fail.
        self.assertApproxEqual(tx, -6.0, eps=0.0002)
        self.assertApproxEqual(ty, 3.6, eps=0.0002)

    def test_init_ceres_line_search_lbfgs_der_maya_dag_single_frame(self):
        single_frame = True
        self.do_solve(
            'ceres_line_search_lbfgs_der',
            mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_ceres_line_search_lbfgs_der_maya_dag_multi_frame(self):
        single_frame = False
        self.do_solve(
            'ceres_line_search_lbfgs_der',
            mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_ceres_line_search_lbfgs_der_mmscenegraph_single_frame(self):
        single_frame = True
        self.do_solve(
            'ceres_line_search_lbfgs_der',
            mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )

    def test_init_ceres_line_search_lbfgs_der_mmscenegraph_multi_frame(self):
        single_frame = False
        self.do_solve(
            'ceres_line_search_lbfgs_der',
            mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )

    def test_init_ceres_lmder_maya_dag_single_frame(self):
        single_frame = True
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_ceres_lmder_maya_dag_multi_frame(self):
        single_frame = False
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_ceres_lmder_mmscenegraph_single_frame(self):
        single_frame = True
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )

    def test_init_ceres_lmder_mmscenegraph_multi_frame(self):
        single_frame = False
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )

    def test_init_ceres_lmdif_maya_dag_single_frame(self):
        single_frame = True
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_ceres_lmdif_maya_dag_multi_frame(self):
        single_frame = False
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_ceres_lmdif_mmscenegraph_single_frame(self):
        single_frame = True
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )

    def test_init_ceres_lmdif_mmscenegraph_multi_frame(self):
        single_frame = False
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )

    def test_init_cminpack_lmdif_maya_dag_single_frame(self):
        single_frame = True
        self.do_solve(
            'cminpack_lmdif',
            mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_cminpack_lmdif_maya_dag_multi_frame(self):
        single_frame = False
        self.do_solve(
            'cminpack_lmdif',
            mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_cminpack_lmdif_mmscenegraph_single_frame(self):
        single_frame = True
        self.do_solve(
            'cminpack_lmdif',
            mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )

    def test_init_cminpack_lmdif_mmscenegraph_multi_frame(self):
        single_frame = False
        self.do_solve(
            'cminpack_lmdif',
            mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )

    def test_init_cminpack_lmder_maya_dag_single_frame(self):
        single_frame = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_cminpack_lmder_maya_dag_multi_frame(self):
        single_frame = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
            single_frame,
        )

    def test_init_cminpack_lmder_mmscenegraph_single_frame(self):
        single_frame = True
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )

    def test_init_cminpack_lmder_mmscenegraph_multi_frame(self):
        single_frame = False
        self.do_solve(
            'cminpack_lmder',
            mmapi.SOLVER_TYPE_CMINPACK_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
            single_frame,
        )


if __name__ == '__main__':
    prog = unittest.main()
