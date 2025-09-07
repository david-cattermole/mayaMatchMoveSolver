# Copyright (C) 2018, 2019 David Cattermole.
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
Test the mmReprojection node for correctness.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import unittest

import maya.cmds

import test.test_solver.solverutils as solverUtils


# @unittest.skip
class TestReprojectionNode(solverUtils.SolverTestCase):
    @staticmethod
    def query_output_attrs(node):
        data = {}
        attrs = [
            'outCoord',
            'outNormCoord',
            'outPixel',
            'outInsideFrustum',
            'outPoint',
            'outWorldPoint',
            'outMatrix',
            'outWorldMatrix',
            'outCameraProjectionMatrix',
            'outInverseCameraProjectionMatrix',
            'outWorldCameraProjectionMatrix',
            'outWorldInverseCameraProjectionMatrix',
            'outPan',
            'outCameraDirectionRatio',
        ]
        for attr in attrs:
            plug = '{0}.{1}'.format(node, attr)
            value = maya.cmds.getAttr(plug)
            data[attr] = value
        return data

    @staticmethod
    def print_node(data):
        outCoord = data.get('outCoord')
        outNormCoord = data.get('outNormCoord')
        outPixel = data.get('outPixel')
        outInsideFrustum = data.get('outInsideFrustum')
        outPoint = data.get('outPoint')
        outWorldPoint = data.get('outWorldPoint')
        outMatrix = data.get('outMatrix')
        outWorldMatrix = data.get('outWorldMatrix')
        outCameraProjectionMatrix = data.get('outCameraProjectionMatrix')
        outInverseCameraProjectionMatrix = data.get('outInverseCameraProjectionMatrix')
        outWorldCameraProjectionMatrix = data.get('outWorldCameraProjectionMatrix')
        outWorldInverseCameraProjectionMatrix = data.get(
            'outWorldInverseCameraProjectionMatrix'
        )
        outPan = data.get('outPan')
        outCameraDirectionRatio = data.get('outCameraDirectionRatio')
        print('=== Printing Node ===')
        print('outCoord', outCoord)
        print('outNormCoord', outNormCoord)
        print('outPixel', outPixel)
        print('outInsideFrustum', outInsideFrustum)
        print('-' * 5)
        print('outPoint', outPoint)
        print('outWorldPoint', outWorldPoint)
        print('outMatrix', outMatrix)
        print('outWorldMatrix', outWorldMatrix)
        print('-' * 5)
        print('outCameraProjectionMatrix', outCameraProjectionMatrix)
        print('outInverseCameraProjectionMatrix', outInverseCameraProjectionMatrix)
        print('outWorldCameraProjectionMatrix', outWorldCameraProjectionMatrix)
        print(
            'outWorldInverseCameraProjectionMatrix',
            outWorldInverseCameraProjectionMatrix,
        )
        print('-' * 5)
        print('outPan', outPan)
        print('-' * 5)
        print('outCameraDirectionRatio', outCameraDirectionRatio)
        print('-' * 40)

    def check_values(self, data):
        print('=== Testing Node Values ===')
        for key, value in data.items():
            print('attr', repr(key), 'value', repr(value))
            if isinstance(value, (list, tuple)):
                for v1 in value:
                    if isinstance(v1, (list, tuple)):
                        for v2 in v1:
                            self.assertFalse(math.isnan(v2))
                    else:
                        self.assertFalse(math.isnan(v1))
            else:
                self.assertFalse(math.isnan(value))
        return

    def test_reprojection_node(self):
        maya.cmds.loadPlugin('matrixNodes')  # for decomposeMatrix node.

        # Reprojection node
        node = maya.cmds.createNode('mmReprojection')

        # Camera
        cam_tfm, cam_shp = self.create_camera('camera')
        maya.cmds.setAttr(cam_tfm + '.translateX', -2.0)
        maya.cmds.setAttr(cam_tfm + '.translateY', 2.0)
        maya.cmds.setAttr(cam_tfm + '.translateZ', 5)
        maya.cmds.setAttr(cam_tfm + '.rotateX', 10.0)

        # Input transform
        in_tfm = maya.cmds.createNode('transform', name='INPUT')
        maya.cmds.createNode('locator', parent=in_tfm)

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
        out_coord_tfm = maya.cmds.createNode(
            'transform', name='outputCoord', parent=cam_tfm
        )
        maya.cmds.createNode('locator', parent=out_coord_tfm)
        maya.cmds.connectAttr(node + '.outCoordX', out_coord_tfm + '.translateX')
        maya.cmds.connectAttr(node + '.outCoordY', out_coord_tfm + '.translateY')
        maya.cmds.connectAttr(node + '.outInsideFrustum', out_coord_tfm + '.visibility')
        maya.cmds.setAttr(out_coord_tfm + '.translateZ', -1.0)

        # Output Normalised Coordinates
        out_norm_coord_tfm = maya.cmds.createNode(
            'transform', name='outputNormCoord', parent=cam_tfm
        )
        maya.cmds.createNode('locator', parent=out_norm_coord_tfm)
        maya.cmds.connectAttr(
            node + '.outNormCoordX', out_norm_coord_tfm + '.translateX'
        )
        maya.cmds.connectAttr(
            node + '.outNormCoordY', out_norm_coord_tfm + '.translateY'
        )
        maya.cmds.connectAttr(
            node + '.outInsideFrustum', out_norm_coord_tfm + '.visibility'
        )
        maya.cmds.setAttr(out_norm_coord_tfm + '.translateZ', -1.0)

        # Output Pixel
        out_pixel_tfm = maya.cmds.createNode(
            'transform', name='outputPixel', parent=cam_tfm
        )
        maya.cmds.createNode('locator', parent=out_pixel_tfm)
        maya.cmds.connectAttr(node + '.outPixelX', out_pixel_tfm + '.translateX')
        maya.cmds.connectAttr(node + '.outPixelY', out_pixel_tfm + '.translateY')
        maya.cmds.connectAttr(node + '.outInsideFrustum', out_pixel_tfm + '.visibility')
        maya.cmds.setAttr(out_pixel_tfm + '.translateZ', -2000.0)

        # Output camera-space transform
        out_cam_matrix_tfm = maya.cmds.createNode(
            'transform', name='outputTransform_inCameraSpace', parent=cam_tfm
        )
        maya.cmds.createNode('locator', parent=out_cam_matrix_tfm)
        decompose = maya.cmds.createNode('decomposeMatrix')
        maya.cmds.connectAttr(node + '.outMatrix', decompose + '.inputMatrix')
        maya.cmds.connectAttr(
            decompose + '.outputTranslate', out_cam_matrix_tfm + '.translate'
        )
        maya.cmds.connectAttr(
            decompose + '.outputRotate', out_cam_matrix_tfm + '.rotate'
        )
        maya.cmds.connectAttr(decompose + '.outputScale', out_cam_matrix_tfm + '.scale')
        maya.cmds.connectAttr(decompose + '.outputShear', out_cam_matrix_tfm + '.shear')

        # Output world-space transform
        out_world_matrix_tfm = maya.cmds.createNode(
            'transform', name='outputTransform_inWorldSpace'
        )
        maya.cmds.createNode('locator', parent=out_world_matrix_tfm)
        decompose = maya.cmds.createNode('decomposeMatrix')
        maya.cmds.connectAttr(node + '.outWorldMatrix', decompose + '.inputMatrix')
        maya.cmds.connectAttr(
            decompose + '.outputTranslate', out_world_matrix_tfm + '.translate'
        )
        maya.cmds.connectAttr(
            decompose + '.outputRotate', out_world_matrix_tfm + '.rotate'
        )
        maya.cmds.connectAttr(
            decompose + '.outputScale', out_world_matrix_tfm + '.scale'
        )
        maya.cmds.connectAttr(
            decompose + '.outputShear', out_world_matrix_tfm + '.shear'
        )

        # Output camera-space point
        out_cam_pnt_tfm = maya.cmds.createNode(
            'transform', name='outputPoint_inCameraSpace', parent=cam_tfm
        )
        maya.cmds.createNode('locator', parent=out_cam_pnt_tfm)
        maya.cmds.connectAttr(node + '.outPoint', out_cam_pnt_tfm + '.translate')

        # Output world-space point
        out_world_pnt_tfm = maya.cmds.createNode(
            'transform', name='outputPoint_inWorldSpace'
        )
        maya.cmds.createNode('locator', parent=out_world_pnt_tfm)
        maya.cmds.connectAttr(node + '.outPoint', out_world_pnt_tfm + '.translate')

        # Query output
        data = self.query_output_attrs(node)
        self.check_values(data)
        self.print_node(data)

        # Change Depth Scale and query again.
        #
        # NOTE: If depthScale is set to a value other than 1.0, the
        # outWorldPoint is incorrectly scaled.
        maya.cmds.setAttr(node + '.depthScale', 1.0)
        data = self.query_output_attrs(node)
        self.print_node(data)

        # save the output
        path = self.get_output_path('reprojection_node_test_after.ma')
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return


if __name__ == '__main__':
    prog = unittest.main()
