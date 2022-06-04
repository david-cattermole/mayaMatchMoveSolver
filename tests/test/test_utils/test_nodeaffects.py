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
Test functions for 'nodeaffects' utilities module.

The 'nodeaffects' module is responsible for the internals of the
'maya.cmds.mmSolverAffects' plug-in command.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import unittest
import pprint

import maya.cmds

import test.test_utils.utilsutils as test_utils
import mmSolver.utils.node as node_utils
import mmSolver.utils.nodeaffects as nodeaffects
import mmSolver.utils.python_compat as pycompat


# @unittest.skip
class TestNodeAffects(test_utils.UtilsTestCase):
    """
    Test nodeaffects module.
    """

    # Attribute names that can affect a transform matrix.
    TRANSFORM_ATTRS = [
        'rotateAxisX',
        'rotateAxisY',
        'rotateAxisZ',
        'rotatePivotTranslateX',
        'rotatePivotTranslateY',
        'rotatePivotTranslateZ',
        'rotatePivotX',
        'rotatePivotY',
        'rotatePivotZ',
        'rotateX',
        'rotateY',
        'rotateZ',
        'scalePivotTranslateX',
        'scalePivotTranslateY',
        'scalePivotTranslateZ',
        'scalePivotX',
        'scalePivotY',
        'scalePivotZ',
        'scaleX',
        'scaleY',
        'scaleZ',
        'shearXY',
        'shearXZ',
        'shearYZ',
        'translateX',
        'translateY',
        'translateZ',
    ]

    @staticmethod
    def create_camera(name, tfm_node_type=None):
        assert isinstance(name, pycompat.TEXT_TYPE)
        if tfm_node_type is None:
            tfm_node_type = 'transform'
        cam_tfm = maya.cmds.createNode(tfm_node_type, name=name)
        cam_tfm = node_utils.get_long_name(cam_tfm)
        shp_name = name + 'Shape'
        cam_shp = maya.cmds.createNode('camera', name=shp_name, parent=cam_tfm)
        cam_shp = node_utils.get_long_name(cam_shp)
        return cam_tfm, cam_shp

    @staticmethod
    def get_node_names_from_plugs(plugs):
        nodes = [p.partition('.')[0] for p in plugs]
        nodes = list(set(nodes))
        return sorted(nodes)

    def test_find_plugs_affecting_transform_hierachy(self):
        """
        Simple transform hierachy test.
        """
        cam_tfm, cam_shp = self.create_camera('myCamera')

        top_node = maya.cmds.createNode('transform', name='top_node')
        top_node = node_utils.get_long_name(top_node)

        bot_node = maya.cmds.createNode(
            'transform', name='bottom_node', parent=top_node
        )
        bot_node = node_utils.get_long_name(bot_node)

        # Plugs should only be the 'top' node.
        top_plugs = nodeaffects.find_plugs_affecting_transform(top_node, None)
        nodes = self.get_node_names_from_plugs(top_plugs)
        self.assertIn(top_node, nodes)
        self.assertEqual(len(nodes), 1)

        # Plugs should contain both the 'bottom' and 'top' nodes,
        # because 'bottom' has a parent node.
        bot_plugs = nodeaffects.find_plugs_affecting_transform(bot_node, None)
        nodes = self.get_node_names_from_plugs(bot_plugs)
        self.assertIn(top_node, nodes)
        self.assertIn(bot_node, nodes)
        self.assertEqual(len(nodes), 2)

        # The same as 'bottom' nodes, but will contain the camera
        # hierachy too.
        with_cam_plugs = nodeaffects.find_plugs_affecting_transform(bot_node, cam_tfm)
        nodes = self.get_node_names_from_plugs(with_cam_plugs)
        self.assertIn(top_node, nodes)
        self.assertIn(bot_node, nodes)
        self.assertIn(cam_tfm, nodes)
        self.assertIn(cam_shp, nodes)
        self.assertEqual(len(nodes), 4)
        return

    def test_find_plugs_affecting_transform_constrained(self):
        """
        A transform node parented under a transform that is controlled by
        a constraint.
        """
        # Open File Path
        scenePath = self.get_data_path(
            'scenes', 'mmSolver_nodeaffects_constrained_transforms.ma'
        )
        maya.cmds.file(
            scenePath,
            open=True,
            force=True,
            typ='mayaAscii',
            ignoreVersion=True,
            options='v=0',
        )
        tfm_node = 'null1'
        plugs = nodeaffects.find_plugs_affecting_transform(tfm_node, None)
        return

    def test_find_plugs_affecting_transform_simple_rivet(self):
        """
        A transform node parented under a rivet.mel rivet.
        """
        # Open File Path
        scenePath = self.get_data_path('scenes', 'mmSolver_nodeaffects_simple_rivet.ma')
        maya.cmds.file(
            scenePath,
            open=True,
            force=True,
            typ='mayaAscii',
            ignoreVersion=True,
            options='v=0',
        )

        tfm_node = 'rivet1'
        plugs = nodeaffects.find_plugs_affecting_transform(tfm_node, None)
        return

    def test_find_plugs_affecting_transform_rig_rivet(self):
        """
        A transform node parented under a 'rivet.mel' rivet.

        GitHub Issue 176.
        """
        # Open File Path
        scenePath = self.get_data_path('scenes', 'mmSolver_nodeaffects_rig_rivet.ma')
        maya.cmds.file(
            scenePath,
            open=True,
            force=True,
            typ='mayaAscii',
            ignoreVersion=True,
            options='v=0',
        )

        tfm_node = 'Avg_Point_03_BND'
        must_have_plugs = [
            '|woman_rig2:Group|woman_rig2:Main|woman_rig2:DeformationSystem|woman_rig2:Root_M.translateX',
            '|woman_rig2:Group|woman_rig2:Main|woman_rig2:MotionSystem|woman_rig2:IKSystem|woman_rig2:IKHandle|woman_rig2:IKScalerRoot_M.translateX',
            '|woman_rig2:Group|woman_rig2:Main|woman_rig2:MotionSystem|woman_rig2:IKSystem|woman_rig2:IKHandle|woman_rig2:IKRootConstraint|woman_rig2:IKOffsetSpine1_M|woman_rig2:IKExtraSpine1_M|woman_rig2:IKSpine1_M.translateX',
        ]

        s = time.time()
        plugs = nodeaffects.find_plugs_affecting_transform(tfm_node, None)
        e = time.time()
        print('Compute time:', e - s)

        self.assertGreater(len(plugs), 0)
        for plug in must_have_plugs:
            self.assertIn(plug, plugs)
        return


if __name__ == '__main__':
    prog = unittest.main()
