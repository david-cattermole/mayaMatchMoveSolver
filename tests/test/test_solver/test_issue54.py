"""
Test a rotation solve where the correct solve value is 0.0.

Relates to GitHub issue #54.
"""

import os
import math
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
class TestSolverIssue54(solverUtils.SolverTestCase):

    def setup_scene(self,
                    cam_translate,
                    cam_rotate,
                    cam_rotate_offset,
                    bnd_translate):
        """
        Create a scene file ready for solving.
        """
        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp',
                                       parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', cam_translate[0])
        maya.cmds.setAttr(cam_tfm + '.ty', cam_translate[1])
        maya.cmds.setAttr(cam_tfm + '.tz', cam_translate[2])

        bundle_tfm = maya.cmds.createNode('transform',
                                          name='bundle_tfm')
        bundle_shp = maya.cmds.createNode('locator',
                                          name='bundle_shp',
                                          parent=bundle_tfm)
        maya.cmds.setAttr(bundle_tfm + '.tx', bnd_translate[0])
        maya.cmds.setAttr(bundle_tfm + '.ty', bnd_translate[1])
        maya.cmds.setAttr(bundle_tfm + '.tz', bnd_translate[2])

        marker_tfm = maya.cmds.createNode('transform',
                                          name='marker_tfm',
                                          parent=cam_tfm)
        marker_shp = maya.cmds.createNode('locator',
                                          name='marker_shp',
                                          parent=marker_tfm)
        maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)
        maya.cmds.setAttr(marker_tfm + '.tz', -10)

        maya.cmds.setAttr(cam_tfm + '.rx', cam_rotate[0])
        maya.cmds.setAttr(cam_tfm + '.ry', cam_rotate[1])
        maya.cmds.setAttr(cam_tfm + '.rz', cam_rotate[2])

        cameras = (
            (cam_tfm, cam_shp),
        )
        markers = (
            (marker_tfm, cam_shp, bundle_tfm),
        )
        node_attrs = [
            (cam_tfm + '.rx', 'None', 'None', cam_rotate_offset[0], 'None'),
            (cam_tfm + '.ry', 'None', 'None', cam_rotate_offset[1], 'None'),
        ]
        frames = [
            (1),
        ]
        return cameras, markers, node_attrs, frames

    def do_solve_with_initial_value_zero(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        cam_translate = [-2.0, 2.0, -5.0]
        cam_rotate = [0.0, 0.0, 0.0]
        cam_rotate_offset = ['360', '360', 'None']
        bnd_translate = [-1.0, 1.0, -25.0]
        cameras, markers, node_attrs, frames = self.setup_scene(
            cam_translate,
            cam_rotate,
            cam_rotate_offset,
            bnd_translate)
        cam_tfm, cam_shp = cameras[0]

        # save the output
        path = 'solver_test_issue54_initial_value_zero_%s_before.ma'
        path = self.get_data_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            iterations=10,
            solverType=solver_index,
            frame=frames,
            verbose=True,
        )
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = 'solver_test_issue54_initial_value_zero_%s_after.ma'
        path = self.get_data_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        rx = maya.cmds.getAttr(cam_tfm + '.rx')
        ry = maya.cmds.getAttr(cam_tfm + '.ry')
        print 'rx', rx
        print 'ry', ry
        assert self.approx_equal(rx, -2.85, eps=0.1)
        assert self.approx_equal(ry, -2.86, eps=0.1)

    def do_solve_with_initial_value_twenty(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        cam_translate = [-1.0, 1.0, -5.0]
        cam_rotate = [20.0, 20.0, 20.0]
        cam_rotate_offset = ['360', '360', 'None']
        bnd_translate = [-1.0, 1.0, -25.0]
        cameras, markers, node_attrs, frames = self.setup_scene(
            cam_translate,
            cam_rotate,
            cam_rotate_offset,
            bnd_translate)
        cam_tfm, cam_shp = cameras[0]

        # save the output
        path = 'solver_test_issue54_initial_value_twenty_%s_before.ma'
        path = self.get_data_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            iterations=10,
            solverType=solver_index,
            frame=frames,
            verbose=True,
        )
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = 'solver_test_issue54_initial_value_twenty_%s_after.ma'
        path = self.get_data_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        rx = maya.cmds.getAttr(cam_tfm + '.rx')
        ry = maya.cmds.getAttr(cam_tfm + '.ry')
        print 'rx', rx
        print 'ry', ry
        assert self.approx_equal(rx, 0.0, eps=0.01)
        assert self.approx_equal(ry, 0.0, eps=0.01)

    def do_solve_with_initial_value_threeSixty(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        cam_translate = [-1.0, 1.0, -5.0]
        cam_rotate = [360.0, 360.0, 360.0]
        cam_rotate_offset = ['360', '360', 'None']
        bnd_translate = [-1.0, 1.0, -25.0]
        cameras, markers, node_attrs, frames = self.setup_scene(
            cam_translate,
            cam_rotate,
            cam_rotate_offset,
            bnd_translate)
        cam_tfm, cam_shp = cameras[0]

        # save the output
        path = 'solver_test_issue54_initial_value_threeSixty_%s_before.ma'
        path = self.get_data_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            iterations=10,
            solverType=solver_index,
            frame=frames,
            verbose=True,
        )
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = 'solver_test_issue54_initial_value_threeSixty_%s_after.ma'
        path = self.get_data_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        rx = maya.cmds.getAttr(cam_tfm + '.rx')
        ry = maya.cmds.getAttr(cam_tfm + '.ry')
        print 'rx', rx
        print 'ry', ry
        assert self.approx_equal(rx, 360.0, eps=0.01)
        assert self.approx_equal(ry, 360.0, eps=0.01)

    def test_init_levmar(self):
        """
        Solve nodal camera on a single frame, using levmar.
        """
        self.do_solve_with_initial_value_zero('levmar', 0)
        self.do_solve_with_initial_value_twenty('levmar', 0)
        self.do_solve_with_initial_value_threeSixty('levmar', 0)

    def test_init_cminpack_lmdif(self):
        """
        Solve nodal camera on a single frame, using cminpack_lm
        """
        self.do_solve_with_initial_value_zero('cminpack_lm', 1)
        self.do_solve_with_initial_value_twenty('cminpack_lm', 1)
        self.do_solve_with_initial_value_threeSixty('cminpack_lm', 1)

    def test_init_cminpack_lmder(self):
        """
        Solve nodal camera on a single frame, using cminpack_lm
        """
        self.do_solve_with_initial_value_zero('cminpack_lmder', 2)
        self.do_solve_with_initial_value_twenty('cminpack_lmder', 2)
        self.do_solve_with_initial_value_threeSixty('cminpack_lmder', 2)



if __name__ == '__main__':
    prog = unittest.main()
