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
Test functions for mmAnimCurveFilterPops command.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import unittest

import maya.cmds

import test.test_tools.toolsutils as test_tools_utils


# @unittest.skip
class TestAnimCurveFilterPops(test_tools_utils.ToolsTestCase):
    def test_filter_pops1(self):
        name = 'anim_curves1.ma'
        path = self.get_data_path("anim_curves", name)
        maya.cmds.file(path, open=True, force=True)

        startFrame = 1.0
        endFrame = 200.0

        tfm = 'transform1'
        tfm_attr_tx = '{}.translateX'.format(tfm)
        tfm_attr_ty = '{}.translateY'.format(tfm)
        tfm_attr_tz = '{}.translateZ'.format(tfm)
        print('tfm_attr_tx:', repr(tfm_attr_tx))
        print('tfm_attr_ty:', repr(tfm_attr_ty))
        print('tfm_attr_tz:', repr(tfm_attr_tz))
        animCurve_tx = maya.cmds.listConnections(tfm_attr_tx, type='animCurve')[0]
        animCurve_ty = maya.cmds.listConnections(tfm_attr_ty, type='animCurve')[0]
        animCurve_tz = maya.cmds.listConnections(tfm_attr_tz, type='animCurve')[0]

        print('animCurve_tx:', repr(animCurve_tx))
        print('animCurve_ty:', repr(animCurve_ty))
        print('animCurve_ty:', repr(animCurve_ty))

        maya.cmds.mmAnimCurveFilterPops(
            animCurve_tx, threshold=1.0, startFrame=startFrame, endFrame=endFrame
        )
        maya.cmds.mmAnimCurveFilterPops(
            animCurve_ty, threshold=1.0, startFrame=startFrame, endFrame=endFrame
        )
        maya.cmds.mmAnimCurveFilterPops(
            animCurve_tz, threshold=0.1, startFrame=startFrame, endFrame=endFrame
        )

        # save the output
        name = 'animcurve_filter_pops1_after.ma'
        path = self.get_output_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)


if __name__ == '__main__':
    prog = unittest.main()
