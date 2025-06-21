# Copyright (C) 2025 David Cattermole.
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
Test functions for mmAnimCurveSimplify command.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils

DISTRIBUTION_UNIFORM = 'uniform'
DISTRIBUTION_AUTO_KEYPOINTS = 'auto_keypoints'
DISTRIBUTIONS = [
    DISTRIBUTION_UNIFORM,
    DISTRIBUTION_AUTO_KEYPOINTS,
]

INTERPOLATION_LINEAR = 'linear'
INTERPOLATION_CUBIC_NUBS = 'cubic_nubs'
INTERPOLATION_CUBIC_SPLINE = 'cubic_spline'
INTERPOLATIONS = [
    INTERPOLATION_LINEAR,
    INTERPOLATION_CUBIC_NUBS,
    INTERPOLATION_CUBIC_SPLINE,
]


# @unittest.skip
class TestAnimCurveSimplify(test_tools_utils.ToolsTestCase):
    def _create_scene(self):
        name = 'anim_curves1.ma'
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        tfm = 'transform1'
        tfm_attr_tx = '{}.translateX'.format(tfm)
        tfm_attr_ty = '{}.translateY'.format(tfm)
        tfm_attr_tz = '{}.translateZ'.format(tfm)
        # print('tfm_attr_tx:', repr(tfm_attr_tx))
        # print('tfm_attr_ty:', repr(tfm_attr_ty))
        # print('tfm_attr_tz:', repr(tfm_attr_tz))
        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type='animCurve')[0]
        animCurve_ty = maya.cmds.listConnections(tfm_attr_ty, type='animCurve')[0]
        animCurve_tz = maya.cmds.listConnections(tfm_attr_tz, type='animCurve')[0]

        # print('animCurve_tx:', repr(animCurve_tx))
        # print('animCurve_ty:', repr(animCurve_ty))
        # print('animCurve_ty:', repr(animCurve_ty))
        return (animCurve_tx, animCurve_ty, animCurve_tz)
        # return [animCurve_tx]

    def _save_scene(self, name):
        name = 'animcurve_{}_after.ma'.format(name)
        path = self.get_data_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

    def test_simplify_uniform_linear_control_points2(self):
        interpolation = INTERPOLATION_LINEAR
        distribution = DISTRIBUTION_UNIFORM
        animCurves = self._create_scene()
        maya.cmds.mmAnimCurveSimplify(
            animCurves,
            controlPointCount=2,
            distribution=distribution,
            interpolation=interpolation,
            startFrame=1,
            endFrame=200,
        )
        self._save_scene(
            'simplify_control_points2_{}_{}'.format(distribution, interpolation)
        )
        return

    def test_simplify_control_points3(self):
        for distribution in DISTRIBUTIONS:
            for interpolation in INTERPOLATIONS:
                animCurves = self._create_scene()
                maya.cmds.mmAnimCurveSimplify(
                    animCurves,
                    controlPointCount=3,
                    distribution=distribution,
                    interpolation=interpolation,
                    startFrame=1,
                    endFrame=200,
                )
                self._save_scene(
                    'simplify_control_points3_{}_{}'.format(distribution, interpolation)
                )
        return

    def test_simplify_control_points4(self):
        for distribution in DISTRIBUTIONS:
            for interpolation in INTERPOLATIONS:
                animCurves = self._create_scene()
                maya.cmds.mmAnimCurveSimplify(
                    animCurves,
                    controlPointCount=4,
                    distribution=distribution,
                    interpolation=interpolation,
                    startFrame=1,
                    endFrame=200,
                )
                self._save_scene(
                    'simplify_control_points4_{}_{}'.format(distribution, interpolation)
                )
        return

    def test_simplify_control_points5(self):
        for distribution in DISTRIBUTIONS:
            for interpolation in INTERPOLATIONS:
                animCurves = self._create_scene()
                maya.cmds.mmAnimCurveSimplify(
                    animCurves,
                    controlPointCount=5,
                    distribution=distribution,
                    interpolation=interpolation,
                    startFrame=1,
                    endFrame=200,
                )
                self._save_scene(
                    'simplify_control_points5_{}_{}'.format(distribution, interpolation)
                )
        return

    def test_simplify_control_points16(self):
        for distribution in DISTRIBUTIONS:
            for interpolation in INTERPOLATIONS:
                animCurves = self._create_scene()
                maya.cmds.mmAnimCurveSimplify(
                    animCurves,
                    controlPointCount=16,
                    distribution=distribution,
                    interpolation=interpolation,
                    startFrame=1,
                    endFrame=200,
                )
                self._save_scene(
                    'simplify_control_points16_{}_{}'.format(
                        distribution, interpolation
                    )
                )
        return


if __name__ == '__main__':
    prog = unittest.main()
