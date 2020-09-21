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
Solve a single non-animated bundle to the screen-space location of a bundle.
"""

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
class TestSolver1(solverUtils.SolverTestCase):

    def do_solve(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        bundle_tfm = maya.cmds.createNode('transform', name='bundle_tfm')
        bundle_shp = maya.cmds.createNode('locator', name='bundle_shp', parent=bundle_tfm)
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)

        marker_tfm = maya.cmds.createNode('transform', name='marker_tfm', parent=cam_tfm)
        marker_shp = maya.cmds.createNode('locator', name='marker_shp', parent=marker_tfm)
        maya.cmds.addAttr(marker_tfm, longName='enable', at='byte',
                          minValue=0, maxValue=1, defaultValue=True)
        maya.cmds.addAttr(marker_tfm, longName='weight', at='double',
                          minValue=0.0, defaultValue=1.0)
        maya.cmds.setAttr(marker_tfm + '.tx', -2.5)
        maya.cmds.setAttr(marker_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker_tfm + '.tz', -10)

        cameras = (
            (cam_tfm, cam_shp),
        )
        markers = (
            (marker_tfm, cam_shp, bundle_tfm),
        )
        node_attrs = [
            (bundle_tfm + '.tx', 'None', 'None', 'None', 'None'),
            (bundle_tfm + '.ty', 'None', 'None', 'None', 'None'),
        ]
        frames = [
            (1),
        ]

        # save the output
        path = self.get_data_path('solver_test1_%s_before.ma' % solver_name)
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
            iterations=1000,
            verbose=True,
            **kwargs)
        e = time.time()
        print 'total time:', e - s
        
        # save the output
        path = self.get_data_path('solver_test1_%s_after.ma' % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)

    def test_init_levmar(self):
        self.do_solve('levmar', 0)

    def test_init_cminpack_lmdif(self):
        self.do_solve('cminpack_lmdif', 1)

    def test_init_cminpack_lmder(self):
        self.do_solve('cminpack_lmder', 2)


if __name__ == '__main__':
    prog = unittest.main()
