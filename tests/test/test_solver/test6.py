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
Testing a single point nodal camera solve across time.

This script calls the solver multiple times in different ways, the aim
is to reduce the slowness while maintaining static value solving.
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
class TestSolver6(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        start = 1
        end = 100
        mid = start + ((end - start) / 2)

        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=start, value=-2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=end, value=2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-2.5)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=2.5)

        bundle_tfm, bundle_shp = self.create_bundle('bundle')
        maya.cmds.setAttr(bundle_tfm + '.tx', -2.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 2.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -15.0)

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)

        marker_tfm, marker_shp = self.create_marker(
            'marker', mkr_grp, bnd_tfm=bundle_tfm
        )
        maya.cmds.setAttr(marker_tfm + '.tz', -1)
        maya.cmds.setKeyframe(
            marker_tfm, attribute='translateX', time=start, value=-0.243056042
        )
        maya.cmds.setKeyframe(
            marker_tfm, attribute='translateX', time=end, value=0.29166725
        )
        maya.cmds.setKeyframe(
            marker_tfm, attribute='translateY', time=start, value=0.218750438
        )
        maya.cmds.setKeyframe(
            marker_tfm, attribute='translateY', time=end, value=0.189583713
        )

        # save the output
        file_name = 'solver_test6_{}_{}_before.ma'.format(solver_name, scene_graph_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        cameras = ((cam_tfm, cam_shp),)
        markers = ((marker_tfm, cam_shp, bundle_tfm),)
        # NOTE: All dynamic attributes must have a keyframe before starting to solve.
        node_attrs = [
            (cam_tfm + '.rx', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.ry', 'None', 'None', 'None', 'None'),
        ]

        framesList = [
            [(start), (mid), (end)],
            [(start), (25), (mid), (75), (end)],
            [(start), (12), (25), (37), (mid), (62), (75), (87), (end)],
        ]
        print('framesList:', framesList)
        allFrames = []
        for f in range(start, end + 1):
            allFrames.append(f)
        print('allFrames:', allFrames)

        # Run solver!
        results = []
        s = time.time()

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, frame=allFrames, **kwargs)

        # Solve primary frames (first, middle and last), and sub-divide.
        for frames in framesList:
            result = maya.cmds.mmSolver(
                frame=frames,
                iterations=10,
                solverType=solver_index,
                sceneGraphMode=scene_graph_mode,
                verbose=True,
                **kwargs
            )
            results.append(result)

        # # Solve between primary frames
        # for frames in framesList:
        #     for i in range(len(frames)-1):
        #         betweenFrames = []
        #         for j in range(frames[i]+1, frames[i+1]):
        #             result = maya.cmds.mmSolver(
        #                 camera=cameras,
        #                 marker=markers,
        #                 attr=node_attrs,
        #                 iterations=10,
        #                 solverType=solver_index,
        #                 sceneGraphMode=scene_graph_mode,
        #                 frame=[j],
        #                 verbose=True,
        #             )
        #             results.append(result)
        #         # betweenFrames = []
        #         # for j in range(frames[i]+1, frames[i+1]):
        #         #     betweenFrames.append(j)
        #         # result = maya.cmds.mmSolver(
        #         #     camera=cameras,
        #         #     marker=markers,
        #         #     attr=node_attrs,
        #         #     iterations=10,
        #         #     solverType=solver_index,
        #         #     sceneGraphMode=scene_graph_mode,
        #         #     frame=betweenFrames,
        #         #     verbose=True,
        #         # )
        #         # results.append(result)

        # # Global Solve
        # result = maya.cmds.mmSolver(
        #     camera=cameras,
        #     marker=markers,
        #     attr=node_attrs,
        #     iterations=10,
        #     solverType=solver_index,
        #     sceneGraphMode=scene_graph_mode,
        #     frame=allFrames,
        #     verbose=True,
        # )
        # results.append(result)

        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = 'solver_test6_{}_{}_after.ma'.format(solver_name, scene_graph_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        for i, result in enumerate(results):
            print('i', i, result[0])
        for result in results:
            print(result[0])
            self.assertEqual(result[0], 'success=1')
        return

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
