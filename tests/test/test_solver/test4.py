"""
Testing a single point nodal camera solve across time.
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


import test.test_solver.utils as solverUtils


@unittest.skip
class TestSolver4(solverUtils.SolverTestBase):

    def test_init(self):
        start = 1
        end = 100

        maya.cmds.file(new=True, force=True)
        maya.cmds.unloadPlugin('mmSolver')
        maya.cmds.loadPlugin('mmSolver')

        # Start the Profiler
        profilerOutPath = None
        if '__file__' in dir():
            profilerOutPath = os.path.join(os.path.dirname(__file__), 'test4.txt')
        maya.cmds.profiler(addCategory='mmSolver')
        maya.cmds.profiler(bufferSize=250)
        maya.cmds.profiler(sampling=True)

        cam_tfm = maya.cmds.createNode('transform', name='cam_tfm')
        cam_shp = maya.cmds.createNode('camera', name='cam_shp', parent=cam_tfm)
        maya.cmds.setAttr(cam_tfm + '.tx', -1.0)
        maya.cmds.setAttr(cam_tfm + '.ty',  1.0)
        maya.cmds.setAttr(cam_tfm + '.tz', -5.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=start, value=-2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=end, value=2.0)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=start, value=-2.5)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=end, value=2.5)

        bundle_tfm = maya.cmds.createNode('transform', name='bundle_tfm')
        bundle_shp = maya.cmds.createNode('locator', name='bundle_shp', parent=bundle_tfm)
        maya.cmds.setAttr(bundle_tfm + '.tx', -2.5)
        maya.cmds.setAttr(bundle_tfm + '.ty', 2.4)
        maya.cmds.setAttr(bundle_tfm + '.tz', -15.0)

        marker_tfm = maya.cmds.createNode('transform', name='marker_tfm', parent=cam_tfm)
        marker_shp = maya.cmds.createNode('locator', name='marker_shp', parent=marker_tfm)
        maya.cmds.setAttr(marker_tfm + '.tz', -10)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=start, value=-2.5)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateX', time=end, value=3.0)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateY', time=start, value=1.5)
        maya.cmds.setKeyframe(marker_tfm, attribute='translateY', time=end, value=1.3)

        cameras = (
            (cam_tfm, cam_shp),
        )
        markers = (
            (marker_tfm, cam_shp, bundle_tfm),
        )
        # NOTE: All dynamic attributes must have a keyframe before starting to solve.
        node_attrs = [
            (cam_tfm + '.rx', 1),
            (cam_tfm + '.ry', 1),
        ]
        frames = []
        for f in range(start, end+1):
            frames.append(f)

        # Run solver!
        s = time.time()
        err = maya.cmds.mmSolver(
            camera=cameras,
            marker=markers,
            attr=node_attrs,
            frame=frames,
            solverType=1,
            iterations=100,
            verbose=True,
        )
        e = time.time()
        print 'total time:', e - s

        # Stop the Profiler
        maya.cmds.profiler(sampling=False)
        if profilerOutPath is not None:
            maya.cmds.profiler(output=profilerOutPath)

        # Ensure the values are correct
        print 'Error:', err
        assert self.approxEqual(err, 0.0, eps=0.001)


if __name__ == '__main__':
    prog = unittest.main()
