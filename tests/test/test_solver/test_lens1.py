# Copyright (C) 2020 David Cattermole.
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
Create a basic lens distortion evaluation set up.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

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
class TestLens1(solverUtils.SolverTestCase):
    """
    Test the mmLensEvaluate node.
    """

    def test_create_lens_evaluate(self):
        tfm_a = maya.cmds.createNode('transform')
        shp_a = maya.cmds.createNode('locator', parent=tfm_a)
        tfm_b = maya.cmds.createNode('transform')
        shp_b = maya.cmds.createNode('locator', parent=tfm_b)
        lens_node = maya.cmds.createNode('mmLensBasic')
        eval_node = maya.cmds.createNode('mmLensEvaluate')

        plug = lens_node + '.k1'
        maya.cmds.setAttr(plug, 0.2)

        plug = lens_node + '.k2'
        maya.cmds.setAttr(plug, 0.1)

        src = lens_node + '.outLens'
        dst = eval_node + '.inLens'
        maya.cmds.connectAttr(src, dst)

        for axis in ['X', 'Y']:
            plug = tfm_a + '.translate' + axis
            maya.cmds.setAttr(plug, 0.5)

            src = tfm_a + '.translate' + axis
            dst = eval_node + '.in' + axis
            maya.cmds.connectAttr(src, dst)

            src = eval_node + '.out' + axis
            dst = tfm_b + '.translate' + axis
            maya.cmds.connectAttr(src, dst)

        # save the scene
        path = self.get_data_path('lens1_test_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Compute the DG
        for axis in ['X', 'Y']:
            plug = tfm_b + '.translate' + axis
            print('trigger:', plug)
            value = maya.cmds.getAttr(plug)
            print('value:', axis, value)
        return

    def test_layered_lens_distortion_evaluation(self):
        tfm_a = maya.cmds.createNode('transform')
        shp_a = maya.cmds.createNode('locator', parent=tfm_a)
        tfm_b = maya.cmds.createNode('transform')
        shp_b = maya.cmds.createNode('locator', parent=tfm_b)
        lens_a_node = maya.cmds.createNode('mmLensBasic')
        lens_b_node = maya.cmds.createNode('mmLensBasic')
        eval_node = maya.cmds.createNode('mmLensEvaluate')

        plug = lens_a_node + '.k1'
        maya.cmds.setAttr(plug, 0.2)

        plug = lens_b_node + '.k2'
        maya.cmds.setAttr(plug, 0.1)

        src = lens_a_node + '.outLens'
        dst = lens_b_node + '.inLens'
        maya.cmds.connectAttr(src, dst)

        src = lens_b_node + '.outLens'
        dst = eval_node + '.inLens'
        maya.cmds.connectAttr(src, dst)

        for axis in ['X', 'Y']:
            plug = tfm_a + '.translate' + axis
            maya.cmds.setAttr(plug, 0.5)

            src = tfm_a + '.translate' + axis
            dst = eval_node + '.in' + axis
            maya.cmds.connectAttr(src, dst)

            src = eval_node + '.out' + axis
            dst = tfm_b + '.translate' + axis
            maya.cmds.connectAttr(src, dst)

        # save the scene
        path = self.get_data_path('lens1_test_layered_lenses_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Compute the DG
        for axis in ['X', 'Y']:
            plug = tfm_b + '.translate' + axis
            print('trigger:', plug)
            value = maya.cmds.getAttr(plug)
            print('value:', axis, value)
        return


if __name__ == '__main__':
    prog = unittest.main()
