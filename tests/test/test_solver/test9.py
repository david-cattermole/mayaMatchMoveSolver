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
Test a multi-frame bundle solve, with the bundle very, very far away from the camera.
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
class TestSolver9(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index, scene_graph_mode):
        """
        Solve an animated bundle across time.
        """
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        start = 1
        end = 2

        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=start, value=-2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=end, value=2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-2.5)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=2.5)

        # Bundle is created very, very far away from camera.
        bundle_tfm, bundle_shp = self.create_bundle('bundle')

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)
        marker_tfm, marker_shp = self.create_marker(
            'marker', mkr_grp, bnd_tfm=bundle_tfm
        )
        maya.cmds.setAttr(marker_tfm + '.tx', 0)
        maya.cmds.setAttr(marker_tfm + '.ty', 0)
        maya.cmds.setAttr(marker_tfm + '.tz', -1)

        depth_list = [
            # These depths solve correctly.
            0.0,
            -10.0,
            -100.0,
            -1000.0,
            -10000.0,
            # These depths produce errors.
            -100000.0,
            -1000000.0,
            -10000000.0,
            -100000000.0,
        ]
        for d in depth_list:
            print('Solve Depth: %r' % d)
            maya.cmds.cutKey(bundle_tfm, cl=True, t=(), f=(), at='tx')
            maya.cmds.cutKey(bundle_tfm, cl=True, t=(), f=(), at='ty')
            maya.cmds.setAttr(bundle_tfm + '.tx', -2.5)
            maya.cmds.setAttr(bundle_tfm + '.ty', 2.4)
            maya.cmds.setAttr(bundle_tfm + '.tz', d)

            # Ensure the far-clip-plane is large enough to see the bundle.
            if d > 0:
                maya.cmds.setAttr(cam_shp + '.farClipPlane', d * 1.1)

            cameras = ((cam_tfm, cam_shp),)
            markers = ((marker_tfm, cam_shp, bundle_tfm),)
            # NOTE: All dynamic attributes must have a keyframe before
            # starting to solve.
            node_attrs = [
                (bundle_tfm + '.tx', 'None', 'None', 'None', 'None'),
                (bundle_tfm + '.ty', 'None', 'None', 'None', 'None'),
            ]

            frames = list(range(start, end + 1))

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
            frames = []
            for f in frames:
                # Default values for the solver should get us a good solve.
                result = maya.cmds.mmSolver(
                    frame=[f], solverType=solver_index, verbose=True, **kwargs
                )
                # Ensure the values are correct
                self.assertEqual(result[0], 'success=1')
                # # Stopped by low error
                # self.assertEqual(result[2], 'reason_num=6')
            e = time.time()
            print('total time:', e - s)

        # save the output
        file_name = 'solver_test9_{}_{}_after.ma'.format(solver_name, scene_graph_name)
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

    def test_init_ceres_line_search_lbfgs_der_maya_dag(self):
        self.do_solve(
            'ceres_line_search_lbfgs_der',
            mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_init_ceres_line_search_lbfgs_der_mmscenegraph(self):
        self.do_solve(
            'ceres_line_search_lbfgs_der',
            mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )

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
