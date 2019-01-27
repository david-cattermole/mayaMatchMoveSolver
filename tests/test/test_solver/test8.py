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


import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestSolver8(solverUtils.SolverTestCase):

    def test_init(self):
        # Open File Path
        scenePath = self.get_data_path('solver_test8.ma')
        maya.cmds.file(scenePath,
                       open=True,
                       force=True,
                       typ='mayaAscii',
                       ignoreVersion=True,
                       options='v=0')

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

        for camTfm, camShape in cameras:
            nodes = maya.cmds.ls(camTfm + '|marker_tfm*',
                                 type='transform', long=True)
            for node in nodes:
                markerTfm = node
                name = markerTfm.rpartition('|')[-1]
                bundleName = '|cam_bundles|' + name.replace('marker_tfm', 'bundle_tfm')
                bundleTfm = maya.cmds.ls(bundleName, type='transform')[0]
                markers.append((markerTfm, camShape, bundleTfm))

        # Get Attrs
        node_attrs = [
            (cameras[0][0] + '.tx', 'None', 'None'),
            (cameras[0][0] + '.ty', 'None', 'None'),
            (cameras[0][0] + '.tz', 'None', 'None'),
            (cameras[0][0] + '.rx', 'None', 'None'),
            (cameras[0][0] + '.ry', 'None', 'None'),
            (cameras[0][0] + '.rz', 'None', 'None'),

            (cameras[1][0] + '.tx', 'None', 'None'),
            (cameras[1][0] + '.ty', 'None', 'None'),
            (cameras[1][0] + '.tz', 'None', 'None'),
            (cameras[1][0] + '.rx', 'None', 'None'),
            (cameras[1][0] + '.ry', 'None', 'None'),
            (cameras[1][0] + '.rz', 'None', 'None'),
        ]
        frames = [1]

        # Run solver!
        s = time.time()
        result = maya.cmds.mmSolver(
        camera=cameras,
            marker=markers,
            attr=node_attrs,
            frame=frames,
            iterations=1000,
            verbose=True,
        )
        e = time.time()
        print 'total time:', e - s

        # save the output
        path = self.get_data_path('solver_test8_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        
        # Ensure the values are correct
        self.assertEqual(result[0], 'success=1')


if __name__ == '__main__':
    prog = unittest.main()
