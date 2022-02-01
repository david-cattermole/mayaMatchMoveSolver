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

import os
import time
import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds


import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestSolver10(solverUtils.SolverTestCase):

    def do_solve(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', 0.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        # Marker Group
        mkr_grp = maya.cmds.createNode('transform',
                                       name='markerGroup',
                                       parent=cam_tfm)
        mkr_scl = maya.cmds.createNode('mmMarkerScale')
        maya.cmds.connectAttr(cam_shp + '.focalLength', mkr_scl + '.focalLength')
        maya.cmds.connectAttr(cam_shp + '.cameraAperture', mkr_scl + '.cameraAperture')
        maya.cmds.connectAttr(cam_shp + '.filmOffset', mkr_scl + '.filmOffset')
        maya.cmds.connectAttr(mkr_scl + '.outScale', mkr_grp + '.scale')

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
            'marker1', mkr_grp, bnd_tfm=bundle1_tfm)
        maya.cmds.setAttr(marker1_tfm + '.tx', -2.0)
        maya.cmds.setAttr(marker1_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker1_tfm + '.tz', -10)

        # Marker 2
        marker2_tfm, marker2_shp = self.create_marker(
            'marker2', mkr_grp, bnd_tfm=bundle2_tfm)
        maya.cmds.setAttr(marker2_tfm + '.tx', 2.0)
        maya.cmds.setAttr(marker2_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker2_tfm + '.tz', -10)

        # save the output
        path = self.get_data_path('solver_test10_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        cameras = (
            (cam_tfm, cam_shp),
        )
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
        }

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            frame=frames,
            iterations=1000,
            solverType=solver_index,
            verbose=True,
            **kwargs
        )
        e = time.time()
        print('total time:', e - s)

        # save the output
        path = self.get_data_path('solver_test10_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        
        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')

    def test_init_ceres(self):
        self.do_solve('ceres', 0)

    def test_init_cminpack_lmdif(self):
        self.do_solve('cminpack_lmdif', 1)

    def test_init_cminpack_lmder(self):
        self.do_solve('cminpack_lmder', 2)


if __name__ == '__main__':
    prog = unittest.main()
