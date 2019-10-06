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
Test functions for createcontroller tool.
"""

import unittest

import maya.cmds
import maya.debug.closeness as closeness

import test.test_tools.toolsutils as test_tools_utils
import mmSolver.tools.createcontroller.lib as lib


# @unittest.skip
class TestCreateController(test_tools_utils.ToolsTestCase):

    def create_no_keyframe_scene(self):
        tfm = maya.cmds.createNode('transform')
        maya.cmds.setAttr(tfm + '.translateX', 10.0)
        maya.cmds.setAttr(tfm + '.translateY', 20.0)
        maya.cmds.setAttr(tfm + '.translateZ', 30.0)
        return tfm

    def create_no_keyframe_scene_with_pivot(self):
        tfm = maya.cmds.createNode('transform')
        maya.cmds.setAttr(tfm + '.translateX', 10.0)
        maya.cmds.setAttr(tfm + '.translateY', 20.0)
        maya.cmds.setAttr(tfm + '.translateZ', 30.0)

        pivot = (-10.0, -20.0, -30.0)
        maya.cmds.setAttr(tfm + '.rotatePivotX', pivot[0])
        maya.cmds.setAttr(tfm + '.rotatePivotY', pivot[1])
        maya.cmds.setAttr(tfm + '.rotatePivotZ', pivot[2])
        maya.cmds.setAttr(tfm + '.scalePivotX', pivot[0])
        maya.cmds.setAttr(tfm + '.scalePivotY', pivot[1])
        maya.cmds.setAttr(tfm + '.scalePivotZ', pivot[2])
        return tfm

    def test_create_one(self):
        """
        Transform node with no keyframes.
        """
        tfm = self.create_no_keyframe_scene()
        ctrls = lib.create([tfm])
        ctrl = ctrls[0]

        maya.cmds.setAttr(ctrl + '.ty', 42.0)

        # save the output
        name = 'controller_create_no_keyframes_after.ma'
        path = self.get_data_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateX'), 10.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateY'), 42.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateZ'), 30.0)
        return

    def test_create_one_with_pivot(self):
        """
        Transform node with no keyframes, with pivot point changed.
        """
        tfm = self.create_no_keyframe_scene_with_pivot()
        ctrls = lib.create([tfm])
        ctrl = ctrls[0]

        maya.cmds.setAttr(ctrl + '.ty', 42.0)

        # save the output
        name = 'controller_create_no_keyframes_with_pivot_after.ma'
        path = self.get_data_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateX'), 0.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateY'), 42.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateZ'), 00.0)
        return

    def test_remove_one(self):
        """
        Transform node with no keyframes.
        """
        tfm = self.create_no_keyframe_scene()
        ctrls = lib.create([tfm])
        ctrl = ctrls[0]

        maya.cmds.setAttr(ctrl + '.ty', 42.0)

        nodes = lib.remove(ctrls)

        # save the output
        path = self.get_data_path('controller_remove_no_keyframes_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        node = nodes[0]
        self.assertEqual(maya.cmds.getAttr(node + '.translateX'), 10.0)
        self.assertEqual(maya.cmds.getAttr(node + '.translateY'), 42.0)
        self.assertEqual(maya.cmds.getAttr(node + '.translateZ'), 30.0)
        return

    def test_remove_one_with_pivot(self):
        """
        Transform node with no keyframes, with pivot point changed.
        """
        tfm = self.create_no_keyframe_scene_with_pivot()
        ctrls = lib.create([tfm])
        ctrl = ctrls[0]

        maya.cmds.setAttr(ctrl + '.ty', 42.0)

        nodes = lib.remove(ctrls)

        # save the output
        path = self.get_data_path('controller_remove_no_keyframes_with_pivot_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        node = nodes[0]
        self.assertEqual(maya.cmds.getAttr(node + '.translateX'), 0.0)
        self.assertEqual(maya.cmds.getAttr(node + '.translateY'), 42.0)
        self.assertEqual(maya.cmds.getAttr(node + '.translateZ'), 0.0)
        return

    def test_create_hierarchy_with_pivot(self):
        name = 'controller_hierarchy_with_pivot_point_changed.ma'
        path = self.get_data_path('scenes', name)
        maya.cmds.file(path, open=True, force=True)

        base_node = 'group'
        node = 'node'
        ctrls = lib.create([node])
        ctrl = ctrls[0]

        maya.cmds.setAttr(ctrl + '.rz', 45.0)

        # save the output
        name = 'controller_create_hierarchy_with_pivot_point_changed_after.ma'
        path = self.get_data_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        tx = maya.cmds.getAttr(ctrl + '.translateX')
        ty = maya.cmds.getAttr(ctrl + '.translateY')
        tz = maya.cmds.getAttr(ctrl + '.translateZ')
        self.assertTrue(self.approx_equal(tx, 15.67139279))
        self.assertTrue(self.approx_equal(ty, 143.5280034))
        self.assertTrue(self.approx_equal(tz, 0.43112753))

        rx = maya.cmds.getAttr(ctrl + '.rotateX')
        ry = maya.cmds.getAttr(ctrl + '.rotateY')
        rz = maya.cmds.getAttr(ctrl + '.rotateZ')
        self.assertTrue(self.approx_equal(rx, 0.0))
        self.assertTrue(self.approx_equal(ry, 0.0))
        self.assertTrue(self.approx_equal(rz, 45.0))
        return

    def test_remove_hierarchy_with_pivot(self):
        name = 'controller_hierarchy_with_pivot_point_changed.ma'
        path = self.get_data_path('scenes', name)
        maya.cmds.file(path, open=True, force=True)

        base_node = 'group'
        node = 'node'
        ctrls = lib.create([node])
        ctrl = ctrls[0]

        maya.cmds.setAttr(ctrl + '.rz', 45.0)

        nodes = lib.remove(ctrls)

        # save the output
        name = 'controller_remove_hierarchy_with_pivot_point_changed_after.ma'
        path = self.get_data_path(name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        node = nodes[0]
        tx = maya.cmds.getAttr(node + '.translateX')
        ty = maya.cmds.getAttr(node + '.translateY')
        tz = maya.cmds.getAttr(node + '.translateZ')
        self.assertTrue(self.approx_equal(tx, 0))
        self.assertTrue(self.approx_equal(ty, 0))
        self.assertTrue(self.approx_equal(tz, 0))

        rx = maya.cmds.getAttr(node + '.rotateX')
        ry = maya.cmds.getAttr(node + '.rotateY')
        rz = maya.cmds.getAttr(node + '.rotateZ')
        print('rz: %r' % rz)
        self.assertTrue(self.approx_equal(rx, 0.0))
        self.assertTrue(self.approx_equal(ry, 0.0))
        self.assertTrue(self.approx_equal(rz, 45.0))
        return

    def create_one_keyframe_scene(self):
        tfm = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm, attribute='translateX', value=10.0)
        maya.cmds.setKeyframe(tfm, attribute='translateY', value=20.0)
        maya.cmds.setKeyframe(tfm, attribute='translateZ', value=30.0)
        return tfm

    def test_create_two(self):
        """
        Transform node with a single keyframe.
        """
        tfm = self.create_one_keyframe_scene()
        ctrls = lib.create([tfm])
        ctrl = ctrls[0]

        # save the output
        path = self.get_data_path('controller_create_one_keyframe_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateX'), 10.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateY'), 20.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateZ'), 30.0)
        return

    def test_remove_two(self):
        """
        Transform node with a single keyframe.
        """
        tfm = self.create_one_keyframe_scene()
        ctrls = lib.create([tfm])
        ctrl = ctrls[0]

        maya.cmds.setKeyframe(ctrl, attribute='translateY', value=42.0)

        nodes = lib.remove(ctrls)

        # save the output
        path = self.get_data_path('controller_remove_one_keyframe_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        node = nodes[0]
        self.assertEqual(maya.cmds.getAttr(node + '.translateY'), 42.0)
        return

    def create_multi_keyframe_scene(self, start, mid, end):
        maya.cmds.playbackOptions(edit=True, minTime=start)
        maya.cmds.playbackOptions(edit=True, animationStartTime=start)
        maya.cmds.playbackOptions(edit=True, animationEndTime=end)
        maya.cmds.playbackOptions(edit=True, maxTime=end)

        tfm = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm, attribute='translateX', value=10.0, time=start)
        maya.cmds.setKeyframe(tfm, attribute='translateY', value=20.0, time=start)
        maya.cmds.setKeyframe(tfm, attribute='translateZ', value=30.0, time=start)
        maya.cmds.setKeyframe(tfm, attribute='rotateY', value=45.0, time=start)

        maya.cmds.setKeyframe(tfm, attribute='translateX', value=20.0, time=mid)
        maya.cmds.setKeyframe(tfm, attribute='translateY', value=30.0, time=mid)
        maya.cmds.setKeyframe(tfm, attribute='translateZ', value=10.0, time=mid)

        maya.cmds.setKeyframe(tfm, attribute='translateX', value=30.0, time=end)
        maya.cmds.setKeyframe(tfm, attribute='translateY', value=10.0, time=end)
        maya.cmds.setKeyframe(tfm, attribute='translateZ', value=20.0, time=end)
        maya.cmds.setKeyframe(tfm, attribute='rotateY', value=-60.0, time=end)
        return tfm

    def test_create_three(self):
        """
        Transform node with three keyframes.
        """
        start = 1
        mid = 25
        end = 100
        tfm = self.create_multi_keyframe_scene(start, mid, end)

        ctrls = lib.create([tfm])
        ctrl = ctrls[0]

        # save the output
        path = self.get_data_path('controller_create_three_keyframes_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        self.assertEqual(maya.cmds.getAttr(tfm + '.translateX', time=mid), 20.0)
        self.assertEqual(maya.cmds.getAttr(tfm + '.translateY', time=mid), 30.0)
        self.assertEqual(maya.cmds.getAttr(tfm + '.translateZ', time=mid), 10.0)

        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateX', time=mid), 20.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateY', time=mid), 30.0)
        self.assertEqual(maya.cmds.getAttr(ctrl + '.translateZ', time=mid), 10.0)
        self.approx_equal(maya.cmds.getAttr(ctrl + '.rotateY', time=mid), 19.545454545454547)
        return

    def create_hierachy_scene(self, start, end):
        maya.cmds.playbackOptions(edit=True, minTime=start)
        maya.cmds.playbackOptions(edit=True, animationStartTime=start)
        maya.cmds.playbackOptions(edit=True, animationEndTime=end)
        maya.cmds.playbackOptions(edit=True, maxTime=end)

        tfm_a = maya.cmds.createNode('transform')
        maya.cmds.setKeyframe(tfm_a, attribute='translateY', value=20.0, time=start)
        maya.cmds.setKeyframe(tfm_a, attribute='rotateY', value=345.0, time=start)

        maya.cmds.setKeyframe(tfm_a, attribute='translateY', value=10.0, time=end)
        maya.cmds.setKeyframe(tfm_a, attribute='rotateY', value=-360.0, time=end)

        tfm_b = maya.cmds.createNode('transform', parent=tfm_a)
        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=10.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=20.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=30.0, time=start)
        maya.cmds.setKeyframe(tfm_b, attribute='rotateY', value=45.0, time=start)

        maya.cmds.setKeyframe(tfm_b, attribute='translateX', value=30.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='translateY', value=10.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='translateZ', value=20.0, time=end)
        maya.cmds.setKeyframe(tfm_b, attribute='rotateY', value=-60.0, time=end)

        child_a = maya.cmds.createNode('transform', parent=tfm_a)
        child_b = maya.cmds.createNode('transform', parent=tfm_b)
        return tfm_a, tfm_b

    def test_create_four(self):
        """
        Transform node in a hierarchy.
        """
        start = 1
        end = 100
        tfm_a, tfm_b = self.create_hierachy_scene(start, end)

        ctrls = lib.create([tfm_a, tfm_b])
        ctrl_a, ctrl_b = ctrls

        child_a = maya.cmds.createNode('transform', parent=ctrl_a)
        child_b = maya.cmds.createNode('transform', parent=ctrl_b)

        # save the output
        path = self.get_data_path('controller_create_hierarchy_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # self.assertEqual(maya.cmds.getAttr(ctrl + '.translateX', time=start), 20.0)
        # self.assertEqual(maya.cmds.getAttr(ctrl + '.translateY', time=start), 30.0)
        # self.assertEqual(maya.cmds.getAttr(ctrl + '.translateZ', time=start), 10.0)
        return

    def test_remove_four(self):
        """
        Transform node in a hierarchy.
        """
        start = 1
        end = 100
        tfm_a, tfm_b = self.create_hierachy_scene(start, end)

        ctrls = lib.create([tfm_a, tfm_b])
        ctrl_a, ctrl_b = ctrls

        child_a = maya.cmds.createNode('transform', parent=ctrl_a)
        child_b = maya.cmds.createNode('transform', parent=ctrl_b)

        lib.remove(ctrls)

        # save the output
        path = self.get_data_path('controller_remove_hierarchy_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # self.assertEqual(maya.cmds.getAttr(ctrl + '.translateX', time=start), 20.0)
        # self.assertEqual(maya.cmds.getAttr(ctrl + '.translateY', time=start), 30.0)
        # self.assertEqual(maya.cmds.getAttr(ctrl + '.translateZ', time=start), 10.0)
        return

    def test_remove_five(self):
        """
        Open a rigged character and create a controller.
        """
        path = self.get_data_path('scenes', 'rigHierachy.ma')
        maya.cmds.file(path, open=True, force=True)

        tfm_a = 'rig:FKShoulder_L'
        tfm_b = 'rig:FKElbow_L'

        ctrls = lib.create([tfm_a, tfm_b])
        ctrl_a, ctrl_b = ctrls

        child_a = maya.cmds.createNode('transform', parent=ctrl_a, name='childA')
        child_b = maya.cmds.createNode('transform', parent=ctrl_b, name='childB')

        # save the output
        path = self.get_data_path('controller_remove_riggedCharacter_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        lib.remove(ctrls)

        # save the output
        path = self.get_data_path('controller_remove_riggedCharacter_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Make sure child objects are parented under the original rig
        # controls
        self.assertEqual(maya.cmds.objExists('childA'), True)
        self.assertEqual(maya.cmds.objExists('childB'), True)
        self.assertEqual(maya.cmds.objExists('|childA'), False)
        self.assertEqual(maya.cmds.objExists('|childB'), False)
        self.assertIn('childA', maya.cmds.listRelatives(tfm_a))
        self.assertIn('childB', maya.cmds.listRelatives(tfm_b))

        # Test shoulder control matrix.
        real_matrix = maya.cmds.xform(tfm_a, query=True, matrix=True, worldSpace=True)
        test_matrix = [
            -0.16512703574001636, 0.9851022889880628, 0.04802647497156621, 0.0,
            0.15842071164425758, 0.07455484524495984, -0.9845529204530482, 0.0,
            -0.9734659419773467, -0.1549679169408274, -0.1683716262592317, 0.0,
            14.328976267123226, 128.14777525332602, -4.969046642854377, 1.0
        ]
        self.assertGreater(
            closeness.compare_floats(real_matrix, test_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS
        )

        # Test elbow control matrix.
        real_matrix = maya.cmds.xform(tfm_b, query=True, matrix=True, worldSpace=True)
        test_matrix = [
            -0.08499154235006842, 0.9280069723575602, -0.3627388826479886, 0.0,
            0.21246293215315154, -0.3388037838849731, -0.9165541437831752, 0.0,
            -0.9734659419773467, -0.1549679169408281, -0.16837162625923255, 0.0,
            19.05322384980939, 99.96421895926306, -6.34307335672691, 1.0
        ]
        self.assertGreater(
            closeness.compare_floats(real_matrix, test_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS
        )
        return

    def test_remove_six(self):
        """
        Open a rigged character and create a controller, set some values
        and remove the controller.
        """
        path = self.get_data_path('scenes', 'rigHierachy.ma')
        maya.cmds.file(path, open=True, force=True)
        
        tfm_a = 'rig:FKShoulder_L'
        tfm_b = 'rig:FKElbow_L'

        ctrls = lib.create([tfm_a])
        ctrl_a = ctrls[0]

        plug = ctrl_a + '.rotateY'
        maya.cmds.setAttr(plug, 0.0)

        # save the output
        path = self.get_data_path('controller_remove_riggedCharacterArmModify_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        real_matrix = maya.cmds.xform(tfm_a, query=True, matrix=True, worldSpace=True)
        test_matrix = [
            -0.7216083162924442, 0.5093866470512706, -0.46883545265204635, 0.0,
            0.6923015512459766, 0.53095019079326, -0.48868236825060146, 0.0,
            4.163336342344337e-16, -0.677212772105242, -0.7357872391510578, 0.0,
            14.328976267123226, 128.14777525332602, -4.9690466428543845, 1.0
        ]
        self.assertGreater(
            closeness.compare_floats(real_matrix, test_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS
        )

        lib.remove(ctrls)

        # save the output
        path = self.get_data_path('controller_remove_riggedCharacterArmModify_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Should be the exact same matrix as before.
        real_matrix = maya.cmds.xform(tfm_a, query=True, matrix=True, worldSpace=True)
        self.assertGreater(
            closeness.compare_floats(real_matrix, test_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS
        )

        # Test elbow control matrix.
        real_matrix = maya.cmds.xform(tfm_b, query=True, matrix=True, worldSpace=True)
        test_matrix = [
            -0.37141467173729487, 0.6831542385392256, -0.6287697734339405, 0.0,
            0.928467092372303, 0.27328217589778103, -0.25152675944777053, 0.0,
            1.5091078635869547e-15, -0.6772127721052421, -0.7357872391510579, 0.0,
            34.97402889955959, 113.57433714126877, 8.444230861601302, 1.0
        ]
        self.assertGreater(
            closeness.compare_floats(real_matrix, test_matrix),
            closeness.DEFAULT_SIGNIFICANT_DIGITS
        )
        return

    def test_remove_seven(self):
        """
        Create and destroy controllers on a hierarchy of transforms.
        """
        path = self.get_data_path('scenes', 'objectHierachy.ma')
        maya.cmds.file(path, open=True, force=True)

        tfm_a = 'group1'
        tfm_b = 'pSphere1'
        tfm_c = 'pSphere2'

        ctrls = lib.create([tfm_a, tfm_b, tfm_c])
        ctrl_a, ctrl_b, ctrl_c = ctrls

        # save the output
        path = self.get_data_path('controller_remove_hierachyOfControls_before.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the hierarchy is correct.
        ctrl_a_children = maya.cmds.listRelatives(
            ctrl_a,
            children=True,
            fullPath=True,
            type='transform') or []
        ctrl_b_children = maya.cmds.listRelatives(
            ctrl_b,
            children=True,
            fullPath=True,
            type='transform') or []
        self.assertIn(ctrl_b, ctrl_a_children)
        self.assertIn(ctrl_c, ctrl_b_children)

        lib.remove([ctrl_a, ctrl_b, ctrl_c])

        # save the output
        path = self.get_data_path('controller_remove_hierachyOfControls_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
