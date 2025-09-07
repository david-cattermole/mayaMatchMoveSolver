# Copyright (C) 2018, 2019, 2020 David Cattermole.
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
Solve lens distortion using a line of points.
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
class TestLens3(solverUtils.SolverTestCase):
    def do_solve(self, solver_name, solver_index):
        """
        Solve nodal camera on a single frame
        """
        if self.haveSolverType(name=solver_name) is False:
            msg = '%r solver is not available!' % solver_name
            raise unittest.SkipTest(msg)

        lens_node = maya.cmds.createNode('mmLensModel3de')
        maya.cmds.setAttr(lens_node + '.lensModel', 2)  # 2 == k3deClassic
        maya.cmds.setAttr(lens_node + '.tdeClassic_distortion', 0.0)
        maya.cmds.setAttr(lens_node + '.tdeClassic_quarticDistortion', 0.0)

        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        # maya.cmds.setAttr(cam_tfm + '.ry', -10.0)

        grp_tfm = maya.cmds.createNode('transform', name='grp_tfm')
        maya.cmds.setAttr(grp_tfm + '.tx', 0.0)
        maya.cmds.setAttr(grp_tfm + '.ty', 0.0)
        maya.cmds.setAttr(grp_tfm + '.tz', -25.0)

        # Create marker group first (like all other working tests)
        mkr_grp = self.create_marker_group('marker_group', cam_tfm)

        # Lens model is connected to markers via mmLensEvaluate nodes
        # below.
        node_attrs = []
        markers = []
        x_amount_list = [
            -1.1231859675317912,
            -1.1871395352225662,
            -1.1109997312441933,
            -1.1428886155934697,
            -1.1278301401493243,
            -1.1706081159505088,
            -1.026174880111348,
            -1.0396101080616948,
            -1.007821380899889,
            -1.0505157687955868,
        ]  # [random.uniform(-1.0, -1.2) for x in range(10)]
        num = len(x_amount_list)
        for i, x_amount in enumerate(x_amount_list):
            y_amount = -3.0 + ((float(i) / num) * 6.0)

            bundle_tfm, bundle_shp = self.create_bundle('bundle', parent=grp_tfm)
            maya.cmds.setAttr(bundle_tfm + '.tx', 0.0)
            maya.cmds.setAttr(bundle_tfm + '.ty', 0.0)
            maya.cmds.setAttr(bundle_tfm + '.tz', 0.0)
            node_attrs.append(
                (bundle_tfm + '.ty', 'None', 'None', 'None', 'None'),
            )

            marker_tfm, marker_shp = self.create_marker(
                'marker', mkr_grp, bnd_tfm=bundle_tfm
            )
            maya.cmds.setAttr(marker_tfm + '.tz', -10)

            eval_node = maya.cmds.createNode('mmLensEvaluate')
            maya.cmds.setAttr(eval_node + '.inX', x_amount * 3.0)
            maya.cmds.setAttr(eval_node + '.inY', y_amount)

            src = lens_node + '.outLens'
            dst = eval_node + '.inLens'
            maya.cmds.connectAttr(src, dst)

            src = eval_node + '.outX'
            dst = marker_tfm + '.tx'
            maya.cmds.connectAttr(src, dst)

            src = eval_node + '.outY'
            dst = marker_tfm + '.ty'
            maya.cmds.connectAttr(src, dst)

            markers.append((marker_tfm, cam_shp, bundle_tfm))

        node_attrs.append(
            (grp_tfm + '.tx', 'None', 'None', 'None', 'None'),
        )
        node_attrs.append(
            (lens_node + '.tdeClassic_distortion', 'None', 'None', 'None', 'None'),
        )
        node_attrs.append(
            (
                lens_node + '.tdeClassic_quarticDistortion',
                'None',
                'None',
                'None',
                'None',
            ),
        )
        cameras = ((cam_tfm, cam_shp),)
        frames = [
            (1),
        ]

        # Get initial lens distortion values
        initial_distortion = maya.cmds.getAttr(lens_node + '.tdeClassic_distortion')
        initial_quartic = maya.cmds.getAttr(lens_node + '.tdeClassic_quarticDistortion')
        print(f'Initial lens distortion: {initial_distortion}')
        print(f'Initial quartic distortion: {initial_quartic}')

        # save the output
        path = self.get_output_path('lens3_%s_before.ma' % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run SolverAffects to create relationship attributes on markers
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
        maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            solverType=solver_index,
            # delta=0.00001,
            frame=frames,
            verbose=True,
        )
        e = time.time()
        print('total time:', e - s)

        # Get final lens distortion values.
        final_distortion = maya.cmds.getAttr(lens_node + '.tdeClassic_distortion')
        final_quartic = maya.cmds.getAttr(lens_node + '.tdeClassic_quarticDistortion')
        print(f'Final lens distortion: {final_distortion}')
        print(f'Final quartic distortion: {final_quartic}')

        # Calculate changes.
        distortion_change = abs(final_distortion - initial_distortion)
        quartic_change = abs(final_quartic - initial_quartic)
        print(f'Distortion change: {distortion_change}')
        print(f'Quartic change: {quartic_change}')

        # Lens distortion parameters should change during solving, if
        # they don't change, it means the solver is not working on
        # lens distortion.
        min_expected_change = 1e-6
        lens_params_changed = (distortion_change > min_expected_change) or (
            quartic_change > min_expected_change
        )

        # This assertion will fail if lens distortion is not being
        # solved.
        self.assertTrue(
            lens_params_changed,
            (
                "Lens distortion not being solved! "
                "Expected parameter changes > {min_expected_change}, "
                "but got distortion_change={distortion_change}, quartic_change={quartic_change}"
            ).format(
                min_expected_change=min_expected_change,
                distortion_change=distortion_change,
                quartic_change=quartic_change,
            ),
        )

        # save the output
        path = self.get_output_path('lens3_%s_after.ma' % solver_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

    def test_init_ceres_line_search_lbfgs_der(self):
        """
        Solve lens distortion on a single frame, using ceres.
        """
        self.do_solve(
            'ceres_line_search_lbfgs_der', mmapi.SOLVER_TYPE_CERES_LINE_SEARCH_LBFGS_DER
        )

    def test_init_ceres_lmder(self):
        """
        Solve lens distortion on a single frame, using ceres.
        """
        self.do_solve('ceres_lmder', mmapi.SOLVER_TYPE_CERES_LMDER)

    def test_init_ceres_lmdif(self):
        """
        Solve lens distortion on a single frame, using ceres.
        """
        self.do_solve('ceres_lmdif', mmapi.SOLVER_TYPE_CERES_LMDIF)

    def test_init_cminpack_lmdif(self):
        """
        Solve lens distortion on a single frame, using cminpack_lmdif
        """
        self.do_solve('cminpack_lmdif', mmapi.SOLVER_TYPE_CMINPACK_LMDIF)

    def test_init_cminpack_lmder(self):
        """
        Solve lens distortion on a single frame, using cminpack_lmder
        """
        self.do_solve('cminpack_lmder', mmapi.SOLVER_TYPE_CMINPACK_LMDER)


if __name__ == '__main__':
    prog = unittest.main()
