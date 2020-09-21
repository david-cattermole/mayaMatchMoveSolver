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
class TestSolver2(solverUtils.SolverTestCase):

    def do_solve(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        group_tfm = maya.cmds.createNode('transform', name='group_tfm')
        bundle1_tfm = maya.cmds.createNode('transform', name='bundle1_tfm', parent=group_tfm)
        bundle1_shp = maya.cmds.createNode('locator', name='bundle1_shp', parent=bundle1_tfm)
        bundle2_tfm = maya.cmds.createNode('transform', name='bundle2_tfm', parent=group_tfm)
        bundle2_shp = maya.cmds.createNode('locator', name='bundle2_shp', parent=bundle2_tfm)
        maya.cmds.setAttr(bundle1_tfm + '.tx', 10.0)
        maya.cmds.setAttr(bundle2_tfm + '.tx', -10.0)
        maya.cmds.setAttr(group_tfm + '.ry', 45.0)
        maya.cmds.setAttr(group_tfm + '.tz', -35.0)

        marker1_tfm = maya.cmds.createNode('transform', name='marker1_tfm', parent=cam_tfm)
        marker1_shp = maya.cmds.createNode('locator', name='marker1_shp', parent=marker1_tfm)
        maya.cmds.setAttr(marker1_tfm + '.tx', -2.5)
        maya.cmds.setAttr(marker1_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker1_tfm + '.tz', -10)

        marker2_tfm = maya.cmds.createNode('transform', name='marker2_tfm', parent=cam_tfm)
        marker2_shp = maya.cmds.createNode('locator', name='marker2_shp', parent=marker2_tfm)
        maya.cmds.setAttr(marker2_tfm + '.tx', 2.5)
        maya.cmds.setAttr(marker2_tfm + '.ty', -0.8)
        maya.cmds.setAttr(marker2_tfm + '.tz', -6.0)

        cameras = (
            (cam_tfm, cam_shp),
        )
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
        path = self.get_data_path('solver_test2_before.ma')
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
            verbose=True,
            **kwargs
        )
        e = time.time()
        print 'total time:', e - s
        self.assertEqual(result[0], 'success=0')

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
        result = maya.cmds.mmSolver(
            iterations=1000,
            verbose=True,
            **kwargs
        )
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = self.get_data_path('solver_test2_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        
        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')

    def test_init_levmar(self):
        self.do_solve('levmar', 0)

    def test_init_cminpack_lmdif(self):
        self.do_solve('cminpack_lmdif', 1)

    def test_init_cminpack_lmder(self):
        self.do_solve('cminpack_lmder', 2)

if __name__ == '__main__':
    prog = unittest.main()
