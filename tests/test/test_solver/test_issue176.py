# Copyright (C) 2020 David Cattermole.
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
"""Solve a rig control driven by a rivet.

.. note: Solving rivets appear to only work with Maya 2018 and above.
    The same code fails to work in Maya 2017 and below. The cause is
    unknown.

.. note: The example scene loaded in this test throws warnings that
    the DG contains cycles. Cycles in the DG graph can produce
    undefined results and it is bad to depend on the behaviour in that
    case. That being said, unfortunately people will rely on the
    undefined results.

GitHub Issue #176
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


@unittest.skip
class TestSolverIssue176(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        # Open File Path
        scenePath = self.get_data_path('scenes', 'mmSolver_nodeaffects_rig_rivet.ma')
        maya.cmds.file(
            scenePath,
            open=True,
            force=True,
            typ='mayaAscii',
            ignoreVersion=True,
            options='v=0',
        )

        cam_tfm = '|mainCamera'
        cam_shp = '|mainCamera|mainCameraShape'
        marker_tfm = 'Avg_Point_03_MKR'
        bundle_tfm = 'Avg_Point_03_BND'
        plug_x = 'woman_rig2:IKSpine1_M.translateX'
        plug_y = 'woman_rig2:IKSpine1_M.translateY'

        cameras = ((cam_tfm, cam_shp),)
        markers = ((marker_tfm, cam_shp, bundle_tfm),)
        node_attrs = [
            (plug_x, 'None', 'None', 'None', 'None'),
            (plug_y, 'None', 'None', 'None', 'None'),
        ]
        frames = []
        for f in range(1, 75):  # frames 1-74
            frames.append(f)

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver!
        assert 'mmSolver' in dir(maya.cmds)
        s = time.time()
        results = []
        for f in frames:
            result = maya.cmds.mmSolver(
                frame=f,
                solverType=solver_index,
                timeEvalMode=1,  # 1 = 'set time' eval mode.
                iterations=10,
                verbose=True,
                **kwargs
            )
            results.append(result)
        e = time.time()
        print('total time:', e - s)

        # save the output
        path = self.get_output_path('solver_test_issue176_%s_after.ma' % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        successes = [result[0] != 'success=1' for result in results]
        self.assertEqual(any(successes), False)

    def test_init_ceres_line_search_lbfgs_der(self):
        self.do_solve(
            'ceres_line_search_lbfgs_der', mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER
        )

    def test_init_ceres_lmder(self):
        self.do_solve('ceres_lmder', mmapi.SOLVER_TYPE_CERES_LMDER)

    def test_init_ceres_lmdif(self):
        self.do_solve('ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF)

    def test_init_cminpack_lmdif(self):
        self.do_solve('cminpack_lmdif', mmapi.SOLVER_TYPE_CMINPACK_LMDIF)

    def test_init_cminpack_lmder(self):
        self.do_solve('cminpack_lmder', mmapi.SOLVER_TYPE_CMINPACK_LMDER)


if __name__ == '__main__':
    prog = unittest.main()
