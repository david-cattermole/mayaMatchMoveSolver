"""
Solve a single non-animated bundle to the screen-space location of a bundle.
"""

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
class TestSolver1(solverUtils.SolverTestCase):

    def test_init(self):
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
            (bundle_tfm + '.tx'),
            (bundle_tfm + '.ty'),
        ]
        frames = [
            (1),
        ]

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            iterations=1000,
            solverType=0,
            frame=frames,
            verbose=True,
        )
        e = time.time()
        print 'total time:', e - s

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)


if __name__ == '__main__':
    prog = unittest.main()
