"""
Testing marker 'enabled' attribute.
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


def _create_camera(name):
    tfm_name = name + '_tfm'
    shp_name = name + '_shp'
    tfm = maya.cmds.createNode('transform', name=tfm_name)
    shp = maya.cmds.createNode('camera', name=shp_name, parent=tfm)
    return tfm, shp


def _create_bundle(name, parent=None):
    tfm_name = name + '_tfm'
    shp_name = name + '_shp'
    tfm = maya.cmds.createNode('transform', name=tfm_name, parent=parent)
    shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)
    return tfm, shp


def _create_marker(name, cam_tfm):
    tfm_name = name + '_tfm'
    shp_name = name + '_shp'
    tfm = maya.cmds.createNode('transform', name=tfm_name, parent=cam_tfm)
    shp = maya.cmds.createNode('locator', name=shp_name, parent=tfm)
    maya.cmds.addAttr(
        tfm,
        longName='enable',
        at='short',
        minValue=0,
        maxValue=1,
        defaultValue=True
    )
    maya.cmds.addAttr(
        tfm,
        longName='weight',
        at='double',
        minValue=0.0,
        defaultValue=1.0)
    maya.cmds.setAttr(tfm + '.enable', keyable=True, channelBox=True)
    maya.cmds.setAttr(tfm + '.weight', keyable=True, channelBox=True)
    return tfm, shp


# @unittest.skip
class TestSolverMarkerEnabled(solverUtils.SolverTestCase):

    def test_single_frame(self):
        """
        Test 2 markers, one enabled, one disabled; only the "enabled"
        marker should be "used" by the solver.
        """
        cam_tfm, cam_shp = _create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)

        # Create a group, and add both bundles underneath.
        grp = maya.cmds.createNode('transform', name='group1')
        bundle_01_tfm, bundle_01_shp = _create_bundle('bundle_01', parent=grp)
        bundle_02_tfm, bundle_02_shp = _create_bundle('bundle_02', parent=grp)
        maya.cmds.setAttr(grp + '.tz', -10)

        marker_01_tfm, marker_01_shp = _create_marker('marker_01', cam_tfm)
        maya.cmds.setAttr(marker_01_tfm + '.tx', -2.5)
        maya.cmds.setAttr(marker_01_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker_01_tfm + '.tz', -10)

        # disable this marker
        marker_02_tfm, marker_02_shp = _create_marker('marker_02', cam_tfm)
        maya.cmds.setAttr(marker_02_tfm + '.tx', 2.5)
        maya.cmds.setAttr(marker_02_tfm + '.ty', 1.3)
        maya.cmds.setAttr(marker_02_tfm + '.tz', -10)
        maya.cmds.setAttr(marker_02_tfm + '.enable', 0)

        cameras = (
            (cam_tfm, cam_shp),
        )
        markers = (
            (marker_01_tfm, cam_shp, bundle_01_tfm),
            (marker_02_tfm, cam_shp, bundle_02_tfm),
        )
        node_attrs = [
            (grp + '.tx', 'None', 'None', 'None', 'None'),
            (grp + '.ty', 'None', 'None', 'None', 'None'),
        ]
        frames = [
            (1),
        ]

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            frame=frames,
            verbose=True,
        )
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = self.get_data_path('solver_marker_enabled_staticframe_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')
        assert self.approx_equal(maya.cmds.getAttr(grp + '.tx'), -2.24999755)
        assert self.approx_equal(maya.cmds.getAttr(grp + '.ty'), 1.65000644)

    def test_multi_frame(self):
        """
        Solve with different marker enabled values, animated across time.
        """
        start = 1
        mid = 5
        end = 10

        cam_tfm, cam_shp = _create_camera('cam')
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty', 1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=start, value=-5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=end, value=5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-5.5)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=5.5)

        # Create a group, and add both bundles underneath.
        grp = maya.cmds.createNode('transform', name='group1')
        bundle_01_tfm, bundle_01_shp = _create_bundle('bundle_01', parent=grp)
        bundle_02_tfm, bundle_02_shp = _create_bundle('bundle_02', parent=grp)
        maya.cmds.setAttr(grp + '.tz', -10)
        # TODO: Make sure to set tangents to auto, in case the Maya
        #  user contains preferences to change this behaviour.
        maya.cmds.setKeyframe(grp, attribute='translateX', time=start, value=0)
        maya.cmds.setKeyframe(grp, attribute='translateY', time=start, value=0)

        marker_01_tfm, marker_01_shp = _create_marker('marker_01', cam_tfm)
        maya.cmds.setAttr(marker_01_tfm + '.tz', -10)
        maya.cmds.setKeyframe(marker_01_tfm, attribute='translateX', time=start, value=-2.5)
        maya.cmds.setKeyframe(marker_01_tfm, attribute='translateX', time=end, value=-3.0)
        maya.cmds.setKeyframe(marker_01_tfm, attribute='translateY', time=start, value=1.5)
        maya.cmds.setKeyframe(marker_01_tfm, attribute='translateY', time=end, value=1.3)

        # disable this marker
        marker_02_tfm, marker_02_shp = _create_marker('marker_02', cam_tfm)
        maya.cmds.setAttr(marker_02_tfm + '.tz', -10)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='translateX', time=start, value=2.5)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='translateX', time=end, value=3.0)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='translateY', time=start, value=1.5)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='translateY', time=end, value=1.3)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='enable', time=start, value=1)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='enable', time=mid, value=0)
        maya.cmds.setKeyframe(marker_02_tfm, attribute='enable', time=end, value=1)

        maya.cmds.keyTangent(marker_02_tfm,
                             attribute='enable',
                             inTangentType='linear',
                             outTangentType='step')


        cameras = (
            (cam_tfm, cam_shp),
        )
        markers = (
            (marker_01_tfm, cam_shp, bundle_01_tfm),
            (marker_02_tfm, cam_shp, bundle_02_tfm),
        )
        # NOTE: All dynamic attributes must have a keyframe before starting to solve.
        node_attrs = [
            (grp + '.tx', 'None', 'None', 'None', 'None'),
            (grp + '.ty', 'None', 'None', 'None', 'None'),
        ]

        # Run solver, over each frame!
        #
        # Note: the start and end frames will take longer to solve,
        # because the error cannot be constrained. This is normal for
        # the test set up.
        results = []
        s = time.time()
        for f in range(start, end+1):
            frames = [(f)]
            result = maya.cmds.mmSolver(
                camera=cameras,
                marker=markers,
                attr=node_attrs,
                frame=frames,
                verbose=True,
            )
            results.append(result)
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = self.get_data_path('solver_marker_enabled_multiframe_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Ensure the values are correct
        for result in results:
            self.assertEqual(result[0], 'success=1')
        tx_start = maya.cmds.getAttr(grp + '.tx', time=start)
        tx_mid = maya.cmds.getAttr(grp + '.tx', time=mid)
        tx_end = maya.cmds.getAttr(grp + '.tx', time=end)
        ty_start = maya.cmds.getAttr(grp + '.ty', time=start)
        ty_mid = maya.cmds.getAttr(grp + '.ty', time=mid)
        ty_end = maya.cmds.getAttr(grp + '.ty', time=end)
        assert self.approx_equal(tx_start, -0.51855463, eps=0.001)
        assert self.approx_equal(tx_mid, -2.30711317518, eps=0.001)
        assert self.approx_equal(tx_end, -1.48144697, eps=0.001)
        assert self.approx_equal(ty_start, 1.30993172, eps=0.001)
        assert self.approx_equal(ty_mid, 1.65458758547, eps=0.001)
        assert self.approx_equal(ty_end, 2.10503952, eps=0.001)


if __name__ == '__main__':
    prog = unittest.main()
