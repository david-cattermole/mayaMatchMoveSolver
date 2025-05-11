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
"""
Solve using the attribute smoothness feature.
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
class TestSolverSmoothness(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        start = 1
        end = 10

        # TODO: Make sure to set tangents to auto, in case the Maya
        #  user contains preferences to change this behaviour.
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

        marker_tfm, marker_shp = self.create_marker(
            'marker', cam_tfm, bnd_tfm=bundle_tfm
        )
        maya.cmds.setAttr(marker_tfm + '.tz', -10)
        maya.cmds.setKeyframe(
            marker_tfm, attribute='translateX', time=start, value=-2.5
        )
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=end, value=3.0)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateY', time=start, value=1.5)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateY', time=end, value=1.3)

        # Add dynamic attributes for attribute smoothness flags.
        maya.cmds.addAttr(cam_tfm, longName='weightValue')
        maya.cmds.addAttr(cam_tfm, longName='varianceValue')
        maya.cmds.addAttr(cam_tfm, longName='smoothValue')
        maya.cmds.setAttr(cam_tfm + '.weightValue', 1.0)
        maya.cmds.setAttr(cam_tfm + '.varianceValue', 0.5)
        maya.cmds.setAttr(cam_tfm + '.smoothValue', 10.0)

        cameras = ((cam_tfm, cam_shp),)
        markers = ((marker_tfm, cam_shp, bundle_tfm),)
        # NOTE: All animated attributes must have a keyframe before
        # starting to solve.
        node_attrs = [
            (cam_tfm + '.rx', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.ry', 'None', 'None', 'None', 'None'),
        ]
        frames = []
        for f in range(start, end + 1):
            frames.append(f)

        smooth_flags = [
            (
                cam_tfm + '.rx',
                cam_tfm + '.weightValue',
                cam_tfm + '.varianceValue',
                cam_tfm + '.smoothValue',
            )
        ]

        # save the output
        path = self.get_data_path('solver_smoothness_%s_before.ma' % solver_name)
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
        s = time.time()
        result = maya.cmds.mmSolver(
            attrSmoothness=smooth_flags,
            solverType=solver_index,
            iterations=10,
            verbose=True,
            **kwargs
        )
        e = time.time()
        print('total time:', e - s)

        # save the output
        path = self.get_data_path('solver_smoothness_%s_after.ma' % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')

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
