"""
Solve a single non-animated bundle to the screen-space location of a bundle.

This test is the same as 'test.test_solver.test1' except this test uses the
Python API. It's a basic example of how to use the API.
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

import mmSolver.api as api
import test.test_api.apiutils as test_api_utils


@unittest.skip
class TestSolve(test_api_utils.APITestCase):

    def test_init(self):
        # Camera
        cam_tfm = maya.cmds.createNode('transform',
                                       name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera',
                                       name='cam_shp',
                                       parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        # Bundle
        bundle_tfm = maya.cmds.createNode('transform',
                                          name='bundle_tfm')
        bundle_shp = maya.cmds.createNode('locator',
                                          name='bundle_shp',
                                          parent=bundle_tfm)
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)
        bnd = api.Bundle(bundle_tfm)

        # Marker
        marker_tfm = maya.cmds.createNode('transform',
                                          name='marker_tfm',
                                          parent=cam_tfm)
        marker_shp = maya.cmds.createNode('locator',
                                          name='marker_shp',
                                          parent=marker_tfm)
        maya.cmds.setAttr(marker_tfm + '.tx', -2.5)
        maya.cmds.setAttr(marker_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker_tfm + '.tz', -10)
        mkr = api.Marker(marker_tfm)
        mkr.set_bundle(bnd)

        # Attributes
        attr_tx = api.Attribute(bundle_tfm + '.tx')
        attr_ty = api.Attribute(bundle_tfm + '.ty')

        # Solver
        sol = api.Solver()
        sol.set_max_iterations(1000)
        sol.set_solver_type(api.SOLVER_TYPE_LEVMAR)
        sol.set_verbose(True)
        sol.add_frame(1)
        sol.set_frame_list([1])

        # Collection
        col = api.Collection()
        col.create('mySolveCollection')
        col.add_solver(sol)
        col.add_marker(mkr)
        col.add_attribute(attr_tx)
        col.add_attribute(attr_ty)

        # Run solver!
        s = time.time()
        results = col.execute()
        e = time.time()
        print 'total time:', e - s

        # Ensure the values are correct
        for res in results:
            err = res.get_error()
            assert self.approx_equal(err, 0.0, eps=0.001)
        assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.tx'), -6.0)
        assert self.approx_equal(maya.cmds.getAttr(bundle_tfm+'.ty'), 3.6)


if __name__ == '__main__':
    prog = unittest.main()
