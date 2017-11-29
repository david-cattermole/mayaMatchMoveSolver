"""
Test multi-camera solving on a single frame.
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
class TestSolver7(solverUtils.SolverTestBase):

    def test_init(self):
        head, tail = os.path.split(__file__)
        name, ext = os.path.splitext(tail)
        scenePath = os.path.join(head, name + '.ma')

        # Open File Path
        maya.cmds.file(new=True, force=True)
        maya.cmds.unloadPlugin('mmSolver')
        maya.cmds.file(scenePath,
                       open=True,
                       force=True,
                       typ='mayaAscii',
                       ignoreVersion=True,
                       options='v=0')
        maya.cmds.loadPlugin('mmSolver')

        # Get cameras
        cameras = []
        nodes = maya.cmds.ls('|cam_tfm*',
                             type='transform',
                             long=True)
        for node in nodes:
            print "camera node:", node
            camTfm = node
            camShape = maya.cmds.listRelatives(node,
                                               children=True,
                                               type='camera',
                                               fullPath=True)[0]
            print 'nodes', (camTfm, camShape)
            cameras.append((camTfm, camShape))

        # Get Markers
        markers = []
        nodes = maya.cmds.ls('|cam_tfm*|marker_tfm*',
                             type='transform', long=True)
        for node in nodes:
            markerTfm = node
            camTfm = maya.cmds.listRelatives(node,
                                             parent=True,
                                             type='transform',
                                             fullPath=True)[0]
            camShape = maya.cmds.listRelatives(camTfm, children=True,
                                               type='camera',
                                               fullPath=True)[0]
            bundleName = markerTfm.rpartition('|')[-1]
            bundleName = bundleName.replace('marker', 'bundle')
            bundleTfm = maya.cmds.ls(bundleName, type='transform')[0]
            markers.append((markerTfm, camShape, bundleTfm))

        # Get Attrs
        node_attrs = [
            (cameras[0][0] + '.tx', 0),
            (cameras[0][0] + '.ty', 0),
            (cameras[0][0] + '.tz', 0),
            (cameras[0][0] + '.rx', 0),
            (cameras[0][0] + '.ry', 0),
            (cameras[0][0] + '.rz', 0),

            (cameras[1][0] + '.tx', 0),
            (cameras[1][0] + '.ty', 0),
            (cameras[1][0] + '.tz', 0),
            (cameras[1][0] + '.rx', 0),
            (cameras[1][0] + '.ry', 0),
            (cameras[1][0] + '.rz', 0),
        ]
        frames = [1]

        # Run solver!
        s = time.time()
        err = maya.cmds.mmSolver(
        camera=cameras,
            marker=markers,
            attr=node_attrs,
            frame=frames,
            solverType=0,
            iterations=1000,
            verbose=True,
        )
        e = time.time()
        print 'total time:', e - s

        # Ensure the values are correct
        print 'Error:', err
        assert err < 0.001


if __name__ == '__main__':
    prog = unittest.main()
