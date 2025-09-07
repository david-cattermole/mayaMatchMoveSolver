# Copyright (C) 2019 David Cattermole.
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
Test a rotation solve where the correct solve value is 0.0.

Relates to GitHub issue #54.
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

import test.test_solver.solverutils as solverUtils
import mmSolver.api as mmapi


# @unittest.skip
class TestSolverIssue54(solverUtils.SolverTestCase):
    def setup_scene(self, cam_translate, cam_rotate, cam_rotate_offset, bnd_translate):
        """
        Create a scene file ready for solving.
        """
        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', cam_translate[0])
        maya.cmds.setAttr(cam_tfm + '.ty', cam_translate[1])
        maya.cmds.setAttr(cam_tfm + '.tz', cam_translate[2])

        bundle_tfm, bundle_shp = self.create_bundle('bundle')
        maya.cmds.setAttr(bundle_tfm + '.tx', bnd_translate[0])
        maya.cmds.setAttr(bundle_tfm + '.ty', bnd_translate[1])
        maya.cmds.setAttr(bundle_tfm + '.tz', bnd_translate[2])

        mkr_grp = self.create_marker_group('marker_group', cam_tfm)
        marker_tfm, marker_shp = self.create_marker(
            'marker', mkr_grp, bnd_tfm=bundle_tfm
        )
        maya.cmds.setAttr(marker_tfm + '.tx', 0.0)
        maya.cmds.setAttr(marker_tfm + '.ty', 0.0)
        maya.cmds.setAttr(marker_tfm + '.tz', -1.0)

        maya.cmds.setAttr(cam_tfm + '.rx', cam_rotate[0])
        maya.cmds.setAttr(cam_tfm + '.ry', cam_rotate[1])
        maya.cmds.setAttr(cam_tfm + '.rz', cam_rotate[2])

        cameras = ((cam_tfm, cam_shp),)
        markers = ((marker_tfm, cam_shp, bundle_tfm),)
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
            cam_translate, cam_rotate, cam_rotate_offset, bnd_translate
        )
        cam_tfm, cam_shp = cameras[0]

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
            'frame': frames,
        }

        # save the output
        path = 'solver_test_issue54_initial_value_zero_%s_before.ma'
        path = self.get_output_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            iterations=10, solverType=solver_index, verbose=True, **kwargs
        )
        e = time.time()
        print('total time:', e - s)

        # save the output
        path = 'solver_test_issue54_initial_value_zero_%s_after.ma'
        path = self.get_output_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        rx = maya.cmds.getAttr(cam_tfm + '.rx')
        ry = maya.cmds.getAttr(cam_tfm + '.ry')
        print('rx', rx)
        print('ry', ry)
        self.assertApproxEqual(rx, -2.85, eps=0.1)
        self.assertApproxEqual(ry, -2.86, eps=0.1)

    def do_solve_with_initial_value_twenty(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        cam_translate = [-1.0, 1.0, -5.0]
        cam_rotate = [20.0, 20.0, 20.0]
        cam_rotate_offset = ['360', '360', 'None']
        bnd_translate = [-1.0, 1.0, -25.0]
        cameras, markers, node_attrs, frames = self.setup_scene(
            cam_translate, cam_rotate, cam_rotate_offset, bnd_translate
        )
        cam_tfm, cam_shp = cameras[0]

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
            'frame': frames,
        }

        # save the output
        path = 'solver_test_issue54_initial_value_twenty_%s_before.ma'
        path = self.get_output_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            iterations=10, solverType=solver_index, verbose=True, **kwargs
        )
        e = time.time()
        print('total time:', e - s)

        # save the output
        path = 'solver_test_issue54_initial_value_twenty_%s_after.ma'
        path = self.get_output_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        rx = maya.cmds.getAttr(cam_tfm + '.rx')
        ry = maya.cmds.getAttr(cam_tfm + '.ry')
        print('rx', rx)
        print('ry', ry)
        self.assertApproxEqual(rx, 0.0, eps=0.01)
        self.assertApproxEqual(ry, 0.0, eps=0.01)

    def do_solve_with_initial_value_threeSixty(self, solver_name, solver_index):
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        cam_translate = [-1.0, 1.0, -5.0]
        cam_rotate = [360.0, 360.0, 360.0]
        cam_rotate_offset = ['360', '360', 'None']
        bnd_translate = [-1.0, 1.0, -25.0]
        cameras, markers, node_attrs, frames = self.setup_scene(
            cam_translate, cam_rotate, cam_rotate_offset, bnd_translate
        )
        cam_tfm, cam_shp = cameras[0]

        kwargs = {
            'camera': cameras,
            'marker': markers,
            'attr': node_attrs,
            'frame': frames,
        }

        # save the output
        path = 'solver_test_issue54_initial_value_threeSixty_%s_before.ma'
        path = self.get_output_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        affects_mode = 'addAttrsToMarkers'
        self.runSolverAffects(affects_mode, **kwargs)

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            iterations=10, solverType=solver_index, verbose=True, **kwargs
        )
        e = time.time()
        print('total time:', e - s)

        # save the output
        path = 'solver_test_issue54_initial_value_threeSixty_%s_after.ma'
        path = self.get_output_path(path % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        rx = maya.cmds.getAttr(cam_tfm + '.rx')
        ry = maya.cmds.getAttr(cam_tfm + '.ry')
        print('rx', rx)
        print('ry', ry)
        self.assertApproxEqual(rx, 360.0, eps=0.01)
        self.assertApproxEqual(ry, 360.0, eps=0.01)

    def test_init_ceres_line_search_lbfgs_der(self):
        """
        Solve nodal camera on a single frame, using ceres.
        """
        self.do_solve_with_initial_value_zero(
            'ceres_line_search_lbfgs_der', mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER
        )
        self.do_solve_with_initial_value_twenty(
            'ceres_line_search_lbfgs_der',
            mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER,
        )
        self.do_solve_with_initial_value_threeSixty(
            'ceres_line_search_lbfgs_der',
            mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER,
        )

    def test_init_ceres_lmder(self):
        """
        Solve nodal camera on a single frame, using ceres.
        """
        self.do_solve_with_initial_value_zero(
            'ceres_lmder', mmapi.SOLVER_TYPE_CERES_LMDER
        )
        self.do_solve_with_initial_value_twenty(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
        )
        self.do_solve_with_initial_value_threeSixty(
            'ceres_lmder',
            mmapi.SOLVER_TYPE_CERES_LMDER,
        )

    def test_init_ceres_lmdif(self):
        """
        Solve nodal camera on a single frame, using ceres.
        """
        self.do_solve_with_initial_value_zero(
            'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF
        )
        self.do_solve_with_initial_value_twenty(
            'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF
        )
        self.do_solve_with_initial_value_threeSixty(
            'ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF
        )

    def test_init_cminpack_lmdif(self):
        """
        Solve nodal camera on a single frame, using cminpack_lm
        """
        self.do_solve_with_initial_value_zero(
            'cminpack_lmdif', mmapi.SOLVER_TYPE_CMINPACK_LMDIF
        )
        self.do_solve_with_initial_value_twenty(
            'cminpack_lmdif', mmapi.SOLVER_TYPE_CMINPACK_LMDIF
        )
        self.do_solve_with_initial_value_threeSixty(
            'cminpack_lmdif', mmapi.SOLVER_TYPE_CMINPACK_LMDIF
        )

    def test_init_cminpack_lmder(self):
        """
        Solve nodal camera on a single frame, using cminpack_lm
        """
        self.do_solve_with_initial_value_zero(
            'cminpack_lmder', mmapi.SOLVER_TYPE_CMINPACK_LMDER
        )
        self.do_solve_with_initial_value_twenty(
            'cminpack_lmder', mmapi.SOLVER_TYPE_CMINPACK_LMDER
        )
        self.do_solve_with_initial_value_threeSixty(
            'cminpack_lmder', mmapi.SOLVER_TYPE_CMINPACK_LMDER
        )


if __name__ == '__main__':
    prog = unittest.main()
