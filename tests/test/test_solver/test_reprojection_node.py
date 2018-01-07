"""
Test the mmReprojection node for correctness.
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
import mmSolver._api.utils as api_utils


# @unittest.skip
class TestMarkerScaleNode(solverUtils.SolverTestCase):

    @staticmethod
    def create_camera(name):
        cam_tfm = maya.cmds.createNode('transform', name=name)
        cam_tfm = api_utils.get_long_name(cam_tfm)
        cam_shp = maya.cmds.createNode('camera', name=name+'Shape',
                                       parent=cam_tfm)
        cam_shp = api_utils.get_long_name(cam_shp)
        return cam_tfm, cam_shp

    @staticmethod
    def print_node(node):
        outCoord = maya.cmds.getAttr(node + '.outCoord')
        outNormCoord = maya.cmds.getAttr(node + '.outNormCoord')
        outPixel = maya.cmds.getAttr(node + '.outPixel')
        outInsideFrustum = maya.cmds.getAttr(node + '.outInsideFrustum')
        outPoint = maya.cmds.getAttr(node + '.outPoint')
        outWorldPoint = maya.cmds.getAttr(node + '.outWorldPoint')
        outMatrix = maya.cmds.getAttr(node + '.outMatrix')
        outWorldMatrix = maya.cmds.getAttr(node + '.outWorldMatrix')
        outCameraProjectionMatrix = maya.cmds.getAttr(node + '.outCameraProjectionMatrix')
        outInverseCameraProjectionMatrix = maya.cmds.getAttr(node + '.outInverseCameraProjectionMatrix')
        outWorldCameraProjectionMatrix = maya.cmds.getAttr(node + '.outWorldCameraProjectionMatrix')
        outWorldInverseCameraProjectionMatrix = maya.cmds.getAttr(node + '.outWorldInverseCameraProjectionMatrix')
        outPan = maya.cmds.getAttr(node + '.outPan')
        print 'outCoord', outCoord
        print 'outNormCoord', outNormCoord
        print 'outPixel', outPixel
        print 'outInsideFrustum', outInsideFrustum
        print '-' * 5
        print 'outPoint', outPoint
        print 'outWorldPoint', outWorldPoint
        print 'outMatrix', outMatrix
        print 'outWorldMatrix', outWorldMatrix
        print '-' * 5
        print 'outCameraProjectionMatrix', outCameraProjectionMatrix
        print 'outInverseCameraProjectionMatrix', outInverseCameraProjectionMatrix
        print 'outWorldCameraProjectionMatrix', outWorldCameraProjectionMatrix
        print 'outWorldInverseCameraProjectionMatrix', outWorldInverseCameraProjectionMatrix
        print '-' * 5
        print 'outPan', outPan
        print '-' * 40

    def test_reprojection_node(self):
        maya.cmds.loadPlugin('matrixNodes')  # for decomposeMatrix node.

        # Reprojection node
        node = maya.cmds.createNode('mmReprojection')

        # Camera
        cam_tfm, cam_shp = self.create_camera('camera')
        # FIXME: Moving the camera makes the calculations incorrect, this must be fixed inside the node.
        # maya.cmds.setAttr(cam_tfm + '.translateX', -2.0)
        # maya.cmds.setAttr(cam_tfm + '.translateY', 2.0)
        # maya.cmds.setAttr(cam_tfm + '.translateZ', 5)
        # maya.cmds.setAttr(cam_tfm + '.rotateX', 10.0)

        # Input transform
        in_tfm = maya.cmds.createNode('transform', name='INPUT')
        in_shp = maya.cmds.createNode('locator', parent=in_tfm)

        maya.cmds.setAttr(in_tfm + '.translateX', -0.5)
        maya.cmds.setAttr(in_tfm + '.translateY', -0.27)
        maya.cmds.setAttr(in_tfm + '.translateZ', -1.0)

        # Connect transform
        maya.cmds.connectAttr(in_tfm + '.worldMatrix', node + '.transformWorldMatrix')

        # Connect camera attributes
        maya.cmds.connectAttr(cam_tfm + '.worldMatrix', node + '.cameraWorldMatrix')
        maya.cmds.connectAttr(cam_shp + '.focalLength', node + '.focalLength')
        maya.cmds.connectAttr(cam_shp + '.cameraAperture', node + '.cameraAperture')
        maya.cmds.connectAttr(cam_shp + '.filmOffset', node + '.filmOffset')
        maya.cmds.connectAttr(cam_shp + '.filmFit', node + '.filmFit')
        maya.cmds.connectAttr(cam_shp + '.nearClipPlane', node + '.nearClipPlane')
        maya.cmds.connectAttr(cam_shp + '.farClipPlane', node + '.farClipPlane')
        maya.cmds.connectAttr(cam_shp + '.cameraScale', node + '.cameraScale')

        # Connect render settings attributes
        maya.cmds.connectAttr('defaultResolution.width', node + '.imageWidth')
        maya.cmds.connectAttr('defaultResolution.height', node + '.imageHeight')

        # Output Pan
        # Connect Pan to camera.pan
        maya.cmds.connectAttr(node + '.outPan', cam_shp + '.pan')

        # Output Coordinates
        out_coord_tfm = maya.cmds.createNode('transform',
                                               name='outputCoord',
                                               parent=cam_tfm)
        out_coord_shp = maya.cmds.createNode('locator',
                                               parent=out_coord_tfm)
        maya.cmds.connectAttr(node + '.outCoordX', out_coord_tfm + '.translateX')
        maya.cmds.connectAttr(node + '.outCoordY', out_coord_tfm + '.translateY')
        maya.cmds.connectAttr(node + '.outInsideFrustum', out_coord_tfm + '.visibility')
        maya.cmds.setAttr(out_coord_tfm + '.translateZ', -1.0)

        # Output Normalised Coordinates
        out_norm_coord_tfm = maya.cmds.createNode('transform',
                                                  name='outputNormCoord',
                                                  parent=cam_tfm)
        out_norm_coord_shp = maya.cmds.createNode('locator',
                                                  parent=out_norm_coord_tfm)
        maya.cmds.connectAttr(node + '.outNormCoordX', out_norm_coord_tfm + '.translateX')
        maya.cmds.connectAttr(node + '.outNormCoordY', out_norm_coord_tfm + '.translateY')
        maya.cmds.connectAttr(node + '.outInsideFrustum', out_norm_coord_tfm + '.visibility')
        maya.cmds.setAttr(out_norm_coord_tfm + '.translateZ', -1.0)

        # Output Pixel
        out_pixel_tfm = maya.cmds.createNode('transform',
                                             name='outputPixel',
                                             parent=cam_tfm)
        out_pixel_shp = maya.cmds.createNode('locator',
                                             parent=out_pixel_tfm)
        maya.cmds.connectAttr(node + '.outPixelX', out_pixel_tfm + '.translateX')
        maya.cmds.connectAttr(node + '.outPixelY', out_pixel_tfm + '.translateY')
        maya.cmds.connectAttr(node + '.outInsideFrustum', out_pixel_tfm + '.visibility')
        maya.cmds.setAttr(out_pixel_tfm + '.translateZ', -2000.0)

        # Output camera-space transform
        out_cam_matrix_tfm = maya.cmds.createNode('transform', 
                                                  name='outputTransform_inCameraSpace', 
                                                  parent=cam_tfm)
        out_cam_matrix_shp = maya.cmds.createNode('locator', 
                                                  parent=out_cam_matrix_tfm)
        decompose = maya.cmds.createNode('decomposeMatrix')
        maya.cmds.connectAttr(node + '.outMatrix', decompose + '.inputMatrix')
        maya.cmds.connectAttr(decompose + '.outputTranslate', out_cam_matrix_tfm + '.translate')
        maya.cmds.connectAttr(decompose + '.outputRotate', out_cam_matrix_tfm + '.rotate')
        maya.cmds.connectAttr(decompose + '.outputScale', out_cam_matrix_tfm + '.scale')
        maya.cmds.connectAttr(decompose + '.outputShear', out_cam_matrix_tfm + '.shear')

        # Output world-space transform
        out_world_matrix_tfm = maya.cmds.createNode('transform', 
                                                  name='outputTransform_inWorldSpace')
        out_world_matrix_shp = maya.cmds.createNode('locator', 
                                                  parent=out_world_matrix_tfm)
        decompose = maya.cmds.createNode('decomposeMatrix')
        maya.cmds.connectAttr(node + '.outWorldMatrix', decompose + '.inputMatrix')
        maya.cmds.connectAttr(decompose + '.outputTranslate', out_world_matrix_tfm + '.translate')
        maya.cmds.connectAttr(decompose + '.outputRotate', out_world_matrix_tfm + '.rotate')
        maya.cmds.connectAttr(decompose + '.outputScale', out_world_matrix_tfm + '.scale')
        maya.cmds.connectAttr(decompose + '.outputShear', out_world_matrix_tfm + '.shear')

        # Output camera-space point
        out_cam_pnt_tfm = maya.cmds.createNode('transform',
                                               name='outputPoint_inCameraSpace',
                                               parent=cam_tfm)
        out_cam_pnt_shp = maya.cmds.createNode('locator',
                                               parent=out_cam_pnt_tfm)
        maya.cmds.connectAttr(node + '.outPoint', out_cam_pnt_tfm + '.translate')

        # Output world-space point
        out_world_pnt_tfm = maya.cmds.createNode('transform',
                                                 name='outputPoint_inWorldSpace')
        out_world_pnt_shp = maya.cmds.createNode('locator',
                                                 parent=out_world_pnt_tfm)
        maya.cmds.connectAttr(node + '.outPoint', out_world_pnt_tfm + '.translate')

        # Query output
        self.print_node(node)

        # Change Depth Scale and query again.
        maya.cmds.setAttr(node + '.depthScale', 10.0)
        self.print_node(node)

        # save the output
        path = self.get_data_path('reprojection_node_test.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
