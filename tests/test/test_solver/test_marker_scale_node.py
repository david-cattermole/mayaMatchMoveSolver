"""
Test the mmMarkerScale node for correctness.
"""

import os
import time
import unittest

try:
    import maya.standalone
    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds


import test.test_solver.solverutils as solverUtils


@unittest.skip
class TestMarkerScaleNode(solverUtils.SolverTestCase):

    @staticmethod
    def create_camera(name):
        cam_tfm = maya.cmds.createNode('transform', name=name)
        cam_tfm = api_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name=name+'Shape',
                                       parent=cam_tfm)
        cam_shp = api_utils.get_long_name(cam_shp)
        return cam_tfm, cam_shp

    def test_marker_scale_node(self):
        # Reprojection node
        node = maya.cmds.createNode('mmMarkerScale')

        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()

        mkr_grp = maya.cmds.createNode('mmMarkerGroupTransform',
                                       name=name, parent=cam_tfm)
        mkr_scl = maya.cmds.createNode('mmMarkerScale')
        self.set_node(mkr_grp)

        # Add attr and connect depth
        maya.cmds.addAttr(mkr_grp, longName='depth', at='double', minValue=0.0,
                          defaultValue=1.0)
        maya.cmds.setAttr(mkr_grp + '.depth', keyable=True)
        maya.cmds.connectAttr(mkr_grp + '.depth', mkr_scl + '.depth')

        # Connect camera attributes
        maya.cmds.connectAttr(cam_shp + '.focalLength', mkr_scl + '.focalLength')
        maya.cmds.connectAttr(cam_shp + '.cameraAperture', mkr_scl + '.cameraAperture')
        maya.cmds.connectAttr(cam_shp + '.filmOffset', mkr_scl + '.filmOffset')

        # Connect marker scale to marker group
        maya.cmds.connectAttr(mkr_scl + '.outScale', mkr_grp + '.scale')
        maya.cmds.connectAttr(mkr_scl + '.outTranslate', mkr_grp + '.translate')

        # save the output
        path = self.get_data_path('reprojection_node_test.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
