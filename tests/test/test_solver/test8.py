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
Test multi-camera solving on a single frame.
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
class TestSolver8(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        # Open File Path
        scenePath = self.get_data_path('scenes', 'solver_test8.ma')
        maya.cmds.file(
            scenePath,
            open=True,
            force=True,
            typ='mayaAscii',
            ignoreVersion=True,
            options='v=0',
        )

        # Get cameras
        cameras = []
        nodes = maya.cmds.ls('|cam_tfm*', type='transform', long=True)
        for node in nodes:
            print('camera node:', node)
            camTfm = node
            camShape = maya.cmds.listRelatives(
                node, children=True, type='camera', fullPath=True
            )[0]
            print('nodes', (camTfm, camShape))
            cameras.append((camTfm, camShape))

        # Get Markers
        markers = []
        for camTfm, camShape in cameras:
            nodes = maya.cmds.ls(
                camTfm + '|marker_group|marker_tfm*', type='transform', long=True
            )
            for node in nodes:
                markerTfm = node
                maya.cmds.addAttr(
                    markerTfm,
                    longName='enable',
                    at='byte',
                    minValue=0,
                    maxValue=1,
                    defaultValue=True,
                )
                maya.cmds.addAttr(
                    markerTfm,
                    longName='weight',
                    at='double',
                    minValue=0.0,
                    defaultValue=1.0,
                )
                maya.cmds.addAttr(markerTfm, longName='bundle', at='message')

                mkrGrp = maya.cmds.listRelatives(
                    markerTfm, parent=True, type='transform', fullPath=True
                )[0]

                camTfm = maya.cmds.listRelatives(
                    mkrGrp, parent=True, type='transform', fullPath=True
                )[0]
                camShape = maya.cmds.listRelatives(
                    camTfm, children=True, type='camera', fullPath=True
                )[0]

                name = markerTfm.rpartition('|')[-1]
                bundleName = '|cam_bundles|' + name.replace('marker_tfm', 'bundle_tfm')
                bundleTfm = maya.cmds.ls(bundleName, type='transform')[0]

                src = bundleTfm + '.message'
                dst = markerTfm + '.bundle'
                if not maya.cmds.isConnected(src, dst):
                    maya.cmds.connectAttr(src, dst)

                markers.append((markerTfm, camShape, bundleTfm))

        # Get Attrs
        node_attrs = [
            (cameras[0][0] + '.tx', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.ty', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.tz', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.rx', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.ry', 'None', 'None', 'None', 'None'),
            (cameras[0][0] + '.rz', 'None', 'None', 'None', 'None'),
            (cameras[1][0] + '.tx', 'None', 'None', 'None', 'None'),
            (cameras[1][0] + '.ty', 'None', 'None', 'None', 'None'),
            (cameras[1][0] + '.tz', 'None', 'None', 'None', 'None'),
            (cameras[1][0] + '.rx', 'None', 'None', 'None', 'None'),
            (cameras[1][0] + '.ry', 'None', 'None', 'None', 'None'),
            (cameras[1][0] + '.rz', 'None', 'None', 'None', 'None'),
        ]
        frames = [1]

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
            'frame': frames,
        }

        # save the output
        path = self.get_output_path('solver_test8_%s_before.ma' % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

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
        file_name = 'solver_test8_{}_{}_after.ma'.format(solver_name, scene_graph_name)
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')

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
