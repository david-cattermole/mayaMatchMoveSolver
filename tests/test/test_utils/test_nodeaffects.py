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

import unittest

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
    def create_marker(name, cam_tfm, bnd_tfm=None):
        tfm_name = name + '_tfm'
        shp_name = name + '_shp'

        tfm = maya.cmds.createNode('transform', name=tfm_name, parent=cam_tfm)
        tfm = node_utils.get_long_name(tfm)

        shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)
        shp = node_utils.get_long_name(shp)

        maya.cmds.addAttr(
            tfm,
            longName='enable',
            at='short',
            minValue=0,
            maxValue=1,
            defaultValue=True,
        )
        maya.cmds.addAttr(
            tfm, longName='weight', at='double', minValue=0.0, defaultValue=1.0
        )
        maya.cmds.setAttr(tfm + '.enable', keyable=True, channelBox=True)
        maya.cmds.setAttr(tfm + '.weight', keyable=True, channelBox=True)

        maya.cmds.addAttr(tfm, longName='bundle', at='message')

        if bnd_tfm is not None:
            src = bnd_tfm + '.message'
            dst = tfm + '.bundle'
            if not maya.cmds.isConnected(src, dst):
                maya.cmds.connectAttr(src, dst)
        return tfm, shp

    @staticmethod
    def create_bundle(name, parent=None):
        tfm_name = name + '_tfm'
        shp_name = name + '_shp'

        tfm = maya.cmds.createNode('transform', name=tfm_name, parent=parent)
        shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)

        tfm = node_utils.get_long_name(tfm)
        shp = node_utils.get_long_name(shp)
        return tfm, shp

    @staticmethod
    def get_node_names_from_plugs(plugs):
        nodes = [p.partition('.')[0] for p in plugs]
        nodes = list(set(nodes))
        return sorted(nodes)

    @staticmethod
    def parse_plugs_into_components(plugs):
        components_list = []
        for plug in plugs:
            node = plug.partition('.')[0]
            attr_and_frames = plug.split('.')[-1]
            attr = attr_and_frames.split('#')[0]
            frames = attr_and_frames.split('#')[-1]
            components_list.append(
                {
                    'node': node,
                    'attr': attr,
                    'frames': frames,
                }
            )
        return components_list

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
        nodeaffects.find_plugs_affecting_transform(tfm_node, None)
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
        nodeaffects.find_plugs_affecting_transform(tfm_node, None)
        return

    def setup_scene_marker_multiple_frames(self):
        """
        Setup test scene with multiple frames.

        The scene should replicate the following:
        - marker_a is enabled on frames 1 and 2.
        - marker_b is enabled on frames 3 and 4.
        - bundle_a is connected to marker_a.
        - bundle_b is connected to marker_b.
        """
        cam_tfm, cam_shp = self.create_camera('myCamera')

        bnd_a_tfm, bnd_a_shp = self.create_bundle('myBundle_A')
        mkr_a_tfm, mkr_a_shp = self.create_marker(
            'myMarker_A', cam_tfm, bnd_tfm=bnd_a_tfm
        )

        bnd_b_tfm, bnd_b_shp = self.create_bundle('myBundle_B')
        mkr_b_tfm, mkr_b_shp = self.create_marker(
            'myMarker_B', cam_tfm, bnd_tfm=bnd_b_tfm
        )

        # Note: Frame 3 is disabled by 'weight' value.
        maya.cmds.setKeyframe(mkr_a_tfm, attribute='enable', time=1, value=1)
        maya.cmds.setKeyframe(mkr_a_tfm, attribute='enable', time=2, value=1)
        maya.cmds.setKeyframe(mkr_a_tfm, attribute='enable', time=3, value=1)
        maya.cmds.setKeyframe(mkr_a_tfm, attribute='enable', time=4, value=0)

        maya.cmds.setKeyframe(mkr_a_tfm, attribute='weight', time=1, value=1)
        maya.cmds.setKeyframe(mkr_a_tfm, attribute='weight', time=2, value=1)
        maya.cmds.setKeyframe(mkr_a_tfm, attribute='weight', time=3, value=0)
        maya.cmds.setKeyframe(mkr_a_tfm, attribute='weight', time=4, value=0)

        # Note: Frame 2 is disabled by 'weight' value.
        maya.cmds.setKeyframe(mkr_b_tfm, attribute='enable', time=1, value=0)
        maya.cmds.setKeyframe(mkr_b_tfm, attribute='enable', time=2, value=1)
        maya.cmds.setKeyframe(mkr_b_tfm, attribute='enable', time=3, value=1)
        maya.cmds.setKeyframe(mkr_b_tfm, attribute='enable', time=4, value=1)

        maya.cmds.setKeyframe(mkr_b_tfm, attribute='weight', time=1, value=0)
        maya.cmds.setKeyframe(mkr_b_tfm, attribute='weight', time=2, value=0)
        maya.cmds.setKeyframe(mkr_b_tfm, attribute='weight', time=3, value=1)
        maya.cmds.setKeyframe(mkr_b_tfm, attribute='weight', time=4, value=1)

        return cam_tfm, cam_shp, [mkr_a_tfm, bnd_a_tfm], [mkr_b_tfm, bnd_b_tfm]

    def test_marker_multiple_frames_1(self):
        """
        Test affects with multiple frames.

        Run 'node affects' on frames 1, 2, 3 and 4 with marker_a and marker_b.

        Result: Both bundle_a and bundle_b should be affected.
        """
        (
            cam_tfm,
            cam_shp,
            mkr_bnd_a_tfm,
            mkr_bnd_b_tfm,
        ) = self.setup_scene_marker_multiple_frames()
        mkr_a_tfm, bnd_a_tfm = mkr_bnd_a_tfm
        mkr_b_tfm, bnd_b_tfm = mkr_bnd_b_tfm

        all_frames = [1, 2, 3, 4]

        cam_tfms = [cam_tfm]
        mkr_a_plugs = nodeaffects.find_plugs_affected_by_marker(
            mkr_a_tfm, cam_tfm, frames=all_frames
        )
        mkr_b_plugs = nodeaffects.find_plugs_affected_by_marker(
            mkr_b_tfm, cam_tfm, frames=all_frames
        )

        cam_tfms = None
        bnd_a_plugs = nodeaffects.find_plugs_affecting_bundle(
            bnd_a_tfm, mkr_a_tfm, cam_tfms, frames=all_frames
        )
        bnd_a_nodes = self.get_node_names_from_plugs(bnd_a_plugs)
        self.assertEqual(len(bnd_a_nodes), 1)

        bnd_b_plugs = nodeaffects.find_plugs_affecting_bundle(
            bnd_b_tfm, mkr_b_tfm, cam_tfms, frames=all_frames
        )
        bnd_b_nodes = self.get_node_names_from_plugs(bnd_b_plugs)
        self.assertEqual(len(bnd_b_nodes), 1)

        all_plugs = set()
        all_plugs |= set(mkr_a_plugs)
        all_plugs |= set(mkr_b_plugs)
        all_plugs |= set(bnd_a_plugs)
        all_plugs |= set(bnd_b_plugs)
        all_plugs = list(sorted(all_plugs))

        all_nodes = self.get_node_names_from_plugs(all_plugs)
        self.assertIn(mkr_a_tfm, all_nodes)
        self.assertIn(bnd_a_tfm, all_nodes)
        self.assertIn(mkr_b_tfm, all_nodes)
        self.assertIn(bnd_b_tfm, all_nodes)
        self.assertIn(cam_tfm, all_nodes)
        self.assertIn(cam_shp, all_nodes)
        self.assertEqual(len(all_nodes), 6)

    def test_marker_multiple_frames_2(self):
        """
        Test affects with multiple frames.

        Run 'node affects' on frames 1 and 2 with marker_a and marker_b.

        Result: Only bundle_a should be affected.
        """
        (
            cam_tfm,
            cam_shp,
            mkr_bnd_a_tfm,
            mkr_bnd_b_tfm,
        ) = self.setup_scene_marker_multiple_frames()
        mkr_a_tfm, bnd_a_tfm = mkr_bnd_a_tfm
        mkr_b_tfm, bnd_b_tfm = mkr_bnd_b_tfm

        all_frames = [1, 2]

        cam_tfms = [cam_tfm]
        mkr_a_plugs = nodeaffects.find_plugs_affected_by_marker(
            mkr_a_tfm, cam_tfm, frames=all_frames
        )
        mkr_b_plugs = nodeaffects.find_plugs_affected_by_marker(
            mkr_b_tfm, cam_tfm, frames=all_frames
        )

        cam_tfms = None
        bnd_a_plugs = nodeaffects.find_plugs_affecting_bundle(
            bnd_a_tfm, mkr_a_tfm, cam_tfms, frames=all_frames
        )
        bnd_a_nodes = self.get_node_names_from_plugs(bnd_a_plugs)
        self.assertEqual(len(bnd_a_nodes), 1)

        bnd_b_plugs = nodeaffects.find_plugs_affecting_bundle(
            bnd_b_tfm, mkr_b_tfm, cam_tfms, frames=all_frames
        )
        bnd_b_nodes = self.get_node_names_from_plugs(bnd_b_plugs)
        self.assertEqual(len(bnd_b_nodes), 0)

        all_plugs = set()
        all_plugs |= set(mkr_a_plugs)
        all_plugs |= set(mkr_b_plugs)
        all_plugs |= set(bnd_a_plugs)
        all_plugs |= set(bnd_b_plugs)
        all_plugs = list(sorted(all_plugs))

        all_nodes = self.get_node_names_from_plugs(all_plugs)
        self.assertIn(mkr_a_tfm, all_nodes)
        self.assertIn(bnd_a_tfm, all_nodes)
        self.assertIn(cam_tfm, all_nodes)
        self.assertIn(cam_shp, all_nodes)
        self.assertEqual(len(all_nodes), 4)
        return

    def test_marker_multiple_frames_3(self):
        """
        Test affects with multiple frames.

        Run 'node affects' on frames 3 and 4 with marker_a and marker_b.

        Result: Only bundle_b should be affected.
        """
        (
            cam_tfm,
            cam_shp,
            mkr_bnd_a_tfm,
            mkr_bnd_b_tfm,
        ) = self.setup_scene_marker_multiple_frames()
        mkr_a_tfm, bnd_a_tfm = mkr_bnd_a_tfm
        mkr_b_tfm, bnd_b_tfm = mkr_bnd_b_tfm

        all_frames = [3, 4]

        cam_tfms = [cam_tfm]
        mkr_a_plugs = nodeaffects.find_plugs_affected_by_marker(
            mkr_a_tfm, cam_tfm, frames=all_frames
        )
        mkr_b_plugs = nodeaffects.find_plugs_affected_by_marker(
            mkr_b_tfm, cam_tfm, frames=all_frames
        )

        cam_tfms = None
        bnd_a_plugs = nodeaffects.find_plugs_affecting_bundle(
            bnd_a_tfm, mkr_a_tfm, cam_tfms, frames=all_frames
        )
        bnd_a_nodes = self.get_node_names_from_plugs(bnd_a_plugs)
        self.assertEqual(len(bnd_a_nodes), 0)

        bnd_b_plugs = nodeaffects.find_plugs_affecting_bundle(
            bnd_b_tfm, mkr_b_tfm, cam_tfms, frames=all_frames
        )
        bnd_b_nodes = self.get_node_names_from_plugs(bnd_b_plugs)
        self.assertEqual(len(bnd_b_nodes), 1)

        all_plugs = set()
        all_plugs |= set(mkr_a_plugs)
        all_plugs |= set(mkr_b_plugs)
        all_plugs |= set(bnd_a_plugs)
        all_plugs |= set(bnd_b_plugs)
        all_plugs = list(sorted(all_plugs))

        all_nodes = self.get_node_names_from_plugs(all_plugs)
        self.assertIn(mkr_b_tfm, all_nodes)
        self.assertIn(bnd_b_tfm, all_nodes)
        self.assertIn(cam_tfm, all_nodes)
        self.assertIn(cam_shp, all_nodes)
        self.assertEqual(len(all_nodes), 4)
        return

    def test_unused_nodes(self):
        cam_tfm, cam_shp = self.create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        bundle_tfm, bundle_shp = self.create_bundle('bundle')
        maya.cmds.setAttr(bundle_tfm + '.tx', 5.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 6.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -25.0)

        # This bundle is not affected by any marker.
        bundleUnused_tfm, bundleUnused_shp = self.create_bundle('bundleUnused')

        marker_tfm, marker_shp = self.create_marker(
            'marker', cam_tfm, bnd_tfm=bundle_tfm
        )
        maya.cmds.setAttr(marker_tfm + '.tx', -2.5)
        maya.cmds.setAttr(marker_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker_tfm + '.tz', -10)

        # This marker does not affect the bundle - they are not connected
        markerUnused_tfm, markerUnused_shp = self.create_marker(
            'markerUnused', cam_tfm, bnd_tfm=None
        )
        maya.cmds.setAttr(markerUnused_tfm + '.tx', 0.0)
        maya.cmds.setAttr(markerUnused_tfm + '.ty', 0.0)
        maya.cmds.setAttr(markerUnused_tfm + '.tz', -10)

        all_frames = [1]

        cam_tfms = [cam_tfm]
        marker_plugs = nodeaffects.find_plugs_affected_by_marker(
            marker_tfm, cam_tfm, frames=all_frames
        )
        marker_nodes = self.get_node_names_from_plugs(marker_plugs)
        self.assertEqual(len(marker_nodes), 4)
        self.assertIn(marker_tfm, marker_nodes)
        self.assertIn(bundle_tfm, marker_nodes)
        self.assertIn(cam_tfm, marker_nodes)
        self.assertIn(cam_shp, marker_nodes)

        markerUnused_plugs = nodeaffects.find_plugs_affected_by_marker(
            markerUnused_tfm, cam_tfm, frames=all_frames
        )
        markerUnused_nodes = self.get_node_names_from_plugs(markerUnused_plugs)
        self.assertEqual(len(markerUnused_nodes), 3)
        self.assertIn(markerUnused_tfm, markerUnused_nodes)
        self.assertIn(cam_tfm, markerUnused_nodes)
        self.assertIn(cam_shp, markerUnused_nodes)

        cam_tfms = None
        bundle_plugs = nodeaffects.find_plugs_affecting_bundle(
            bundle_tfm, marker_tfm, cam_tfms, frames=all_frames
        )
        bundle_nodes = self.get_node_names_from_plugs(bundle_plugs)
        self.assertEqual(len(bundle_nodes), 1)

        bundleUnused_plugs = nodeaffects.find_plugs_affecting_bundle(
            bundleUnused_tfm, markerUnused_tfm, cam_tfms, frames=all_frames
        )
        bundleUnused_nodes = self.get_node_names_from_plugs(bundleUnused_plugs)
        self.assertEqual(len(bundleUnused_nodes), 1)

        all_plugs = set()
        all_plugs |= set(marker_plugs)
        all_plugs |= set(bundle_plugs)
        all_plugs |= set(markerUnused_plugs)
        all_plugs |= set(bundleUnused_plugs)
        all_plugs = list(sorted(all_plugs))
        self.assertEqual(len(all_plugs), 145)

        all_nodes = self.get_node_names_from_plugs(all_plugs)
        self.assertIn(marker_tfm, all_nodes)
        self.assertIn(bundle_tfm, all_nodes)
        self.assertIn(markerUnused_tfm, all_nodes)
        self.assertIn(bundleUnused_tfm, all_nodes)
        self.assertIn(cam_tfm, all_nodes)
        self.assertIn(cam_shp, all_nodes)
        self.assertEqual(len(all_nodes), 6)

    # def test_find_plugs_affecting_transform_rig_rivet(self):
    #     """
    #     A transform node parented under a 'rivet.mel' rivet.

    #     GitHub Issue 176.
    #     """
    #     # Open File Path
    #     scenePath = self.get_data_path('scenes', 'mmSolver_nodeaffects_rig_rivet.ma')
    #     maya.cmds.file(
    #         scenePath,
    #         open=True,
    #         force=True,
    #         typ='mayaAscii',
    #         ignoreVersion=True,
    #         options='v=0',
    #     )

    #     tfm_node = 'Avg_Point_03_BND'
    #     must_have_plugs = [
    #         '|woman_rig2:Group|woman_rig2:Main|woman_rig2:DeformationSystem|woman_rig2:Root_M.translateX',
    #         '|woman_rig2:Group|woman_rig2:Main|woman_rig2:MotionSystem|woman_rig2:IKSystem|woman_rig2:IKHandle|woman_rig2:IKScalerRoot_M.translateX',
    #         '|woman_rig2:Group|woman_rig2:Main|woman_rig2:MotionSystem|woman_rig2:IKSystem|woman_rig2:IKHandle|woman_rig2:IKRootConstraint|woman_rig2:IKOffsetSpine1_M|woman_rig2:IKExtraSpine1_M|woman_rig2:IKSpine1_M.translateX',
    #     ]

    #     s = time.time()
    #     plugs = nodeaffects.find_plugs_affecting_transform(tfm_node, None)
    #     e = time.time()
    #     print('Compute time:', e - s)

    #     self.assertGreater(len(plugs), 0)
    #     for plug in must_have_plugs:
    #         self.assertIn(plug, plugs)
    #     return


if __name__ == '__main__':
    prog = unittest.main()
