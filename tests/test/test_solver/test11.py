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
Test solving an existing solved camera with (almost) all
attributes unlocked.
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
class TestSolver11(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index, scene_graph_mode):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)
        scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
        scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
        print('Scene Graph:', scene_graph_label)

        # Open File Path
        scenePath = self.get_data_path('scenes', 'stA_v002.ma')
        maya.cmds.file(
            scenePath,
            open=True,
            force=True,
            typ='mayaAscii',
            ignoreVersion=True,
            options='v=0',
        )

        # Get cameras
        camTfm = '|Scene|stA_1_1'
        camShape = '|Scene|stA_1_1|stA_1_1Shape1'
        film_fit = 1  # 3=Overscan, 1=Horizontal
        maya.cmds.setAttr(camShape + '.filmFit', film_fit)
        print('camera nodes', (camTfm, camShape))

        maya.cmds.setAttr('defaultResolution.width', 1920)
        maya.cmds.setAttr('defaultResolution.height', 1280)

        # Get Attrs
        node_attrs = [
            (camTfm + '.tx', 'None', 'None', 'None', 'None'),
            (camTfm + '.ty', 'None', 'None', 'None', 'None'),
            (camTfm + '.tz', 'None', 'None', 'None', 'None'),
            (camTfm + '.rx', 'None', 'None', 'None', 'None'),
            (camTfm + '.ry', 'None', 'None', 'None', 'None'),
            (camTfm + '.rz', 'None', 'None', 'None', 'None'),
        ]

        # Get Markers and Bundles
        markers = []
        firstBundle = None
        nodes = maya.cmds.ls('*_MKR', type='transform', long=True) or []
        for node in nodes:
            markerTfm = node

            mkrGrp = maya.cmds.listRelatives(
                markerTfm, parent=True, type='mmMarkerGroupTransform', fullPath=True
            )[0]

            name = markerTfm.rpartition('|')[-1]
            bundleName = '|' + name.replace('marker', 'bundle').replace('MKR', 'BND')
            bundleTfm = maya.cmds.ls(bundleName, type='transform', long=True)[0]

            markers.append((markerTfm, camShape, bundleTfm))

            # Do not solve one of the bundles, this gives the
            # solver an anchor.
            if firstBundle is None:
                firstBundle = bundleTfm
                continue

            # node_attr_tx = bundleTfm + '.tx'
            # node_attr_ty = bundleTfm + '.ty'
            # node_attr_tz = bundleTfm + '.tz'
            # node_attrs.append((node_attr_tx, 'None', 'None', 'None', 'None'))
            # node_attrs.append((node_attr_ty, 'None', 'None', 'None', 'None'))
            # node_attrs.append((node_attr_tz, 'None', 'None', 'None', 'None'))

        # frames = list(range(1, 95 + 1))
        frames = list(range(1, 1 + 1))

        kwargs = {'camera': [(camTfm, camShape)], 'marker': markers, 'attr': node_attrs}

        # save the output
        file_name = 'solver_test11_{}_{}_before.ma'.format(
            solver_name, scene_graph_name
        )
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            frame=frames,
            iterations=1000,
            solverType=solver_index,
            sceneGraphMode=scene_graph_mode,
            verbose=True,
            **kwargs
        )
        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = 'solver_test11_{}_{}_after.ma'.format(solver_name, scene_graph_name)
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        results = [mmapi.SolveResult(result)]
        self.checkSolveResults(results, allow_max_avg_error=3.5, allow_max_error=3.5)

    def test_ceres_lmder_maya_dag(self):
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_ceres_lmder_mmscenegraph(self):
        self.do_solve(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )

    def test_ceres_lmdif_maya_dag(self):
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_ceres_lmdif_mmscenegraph(self):
        self.do_solve(
            'ceres_lmdif',
            mmapi.SOLVER_TYPE_CERES_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )

    def test_cminpack_lmdif_maya_dag(self):
        self.do_solve(
            'cminpack_lmdif',
            mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MAYA_DAG,
        )

    def test_cminpack_lmdif_mmscenegraph(self):
        self.do_solve(
            'cminpack_lmdif',
            mmapi.SOLVER_TYPE_CMINPACK_LMDIF,
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )

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
            mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH,
        )


if __name__ == '__main__':
    prog = unittest.main()
