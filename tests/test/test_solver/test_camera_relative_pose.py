# Copyright (C) 2022 David Cattermole.
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
Calculate the camera and bundle poses from 2D marker positions only
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import unittest

try:
    import maya.standalone

    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import test.test_solver.solverutils as solverUtils


def deconstruct_result(command_kwargs, result):
    # TODO: Deconstruct the result values and set node attribute
    # values.
    if len(result) == 0:
        print('Solve did not complete.')
        return

    print('command_kwargs:', command_kwargs)
    print('result:', result)

    mkr_bnd_list = command_kwargs['markerBundle']

    cam_matrix_a = result[0:16]
    cam_matrix_b = result[16:32]
    print('cam_matrix_a:', cam_matrix_a)
    print('cam_matrix_b:', cam_matrix_b)

    bnd_results = result[32:]
    assert (len(bnd_results) % 4) == 0
    bnd_result_num = len(bnd_results) // 4
    for i in range(bnd_result_num):
        result_index = i * 4
        index = int(bnd_results[result_index])
        bnd_node = mkr_bnd_list[index][2]
        tx = bnd_results[result_index + 1]
        ty = bnd_results[result_index + 2]
        tz = bnd_results[result_index + 3]
        print('bnd:', bnd_node, 'pos:', tx, ty, tz)
    return


# @unittest.skip
class TestCameraRelativePose(solverUtils.SolverTestCase):
    def create_scene(self, frame_a, frame_b, marker_data_list):
        maya.cmds.playbackOptions(edit=True, minTime=frame_a)
        maya.cmds.playbackOptions(edit=True, maxTime=frame_b)

        cam_tfm, cam_shp = self.create_camera('cam')
        mkr_grp = self.create_marker_group('marker_group', cam_tfm)

        fb_width = 36.0 / 25.4
        fb_height = 24.0 / 25.4
        focal_length = 35.0
        maya.cmds.setAttr(cam_tfm + '.rotateOrder', 2)  # 2 = ZXY
        maya.cmds.setAttr(cam_shp + '.horizontalFilmAperture', fb_width)
        maya.cmds.setAttr(cam_shp + '.verticalFilmAperture', fb_height)
        maya.cmds.setAttr(cam_shp + '.focalLength', focal_length)
        maya.cmds.setAttr(cam_shp + '.displayCameraFrustum', 1)
        maya.cmds.setAttr(cam_shp + '.displayFilmGate', 1)
        maya.cmds.setAttr(cam_shp + '.overscan', 1.5)

        # Set some initial values for the camera. As long as the
        # 'useCameraTransform' flag is given to mmCameraRelativePose,
        # then these values should be taken into consideration and the
        # solved camera pose should be relative to the initial camera
        # transform.
        attrs = [
            'translateX',
            'translateY',
            'translateZ',
            'rotateX',
            'rotateY',
            'rotateZ',
        ]
        for frame in [frame_a, frame_b]:
            for attr in attrs:
                maya.cmds.setKeyframe(cam_tfm, attribute=attr, time=frame_a, value=10.0)

        mkr_bnd_list = []
        for marker_data in marker_data_list:
            bundle_tfm, bundle_shp = self.create_bundle('bundle')
            marker_tfm, marker_shp = self.create_marker(
                'marker', mkr_grp, bnd_tfm=bundle_tfm
            )
            mkr_bnd_list.append([marker_tfm, marker_tfm, bundle_tfm])

            maya.cmds.setAttr(marker_shp + '.localScaleX', 0.1)
            maya.cmds.setAttr(marker_shp + '.localScaleY', 0.1)
            maya.cmds.setAttr(marker_shp + '.localScaleZ', 0.1)

            maya.cmds.setAttr(bundle_shp + '.localScaleX', 0.1)
            maya.cmds.setAttr(bundle_shp + '.localScaleY', 0.1)
            maya.cmds.setAttr(bundle_shp + '.localScaleZ', 0.1)

            data_a = marker_data[0]
            data_b = marker_data[1]

            maya.cmds.setAttr(marker_tfm + '.translateZ', -1.0)
            maya.cmds.setKeyframe(
                marker_tfm, attribute='translateX', time=frame_a, value=data_a[0]
            )
            maya.cmds.setKeyframe(
                marker_tfm, attribute='translateY', time=frame_a, value=data_a[1]
            )

            maya.cmds.setKeyframe(
                marker_tfm, attribute='translateX', time=frame_b, value=data_b[0]
            )
            maya.cmds.setKeyframe(
                marker_tfm, attribute='translateY', time=frame_b, value=data_b[1]
            )

        kwargs = {
            'frameA': frame_a,
            'frameB': frame_b,
            'cameraA': cam_tfm,
            'cameraB': cam_tfm,
            'markerBundle': mkr_bnd_list,
        }
        return kwargs

    def test_five_point_pose1(self):
        frame_a = 90
        frame_b = 227

        marker_data_list = [
            # Marker 1
            [
                [-0.22213842759755273, 0.43804316401489374],
                [-0.08642928582293867, 0.3234780288109984],
            ],
            # Marker 2
            [
                [-0.20545909173698554, -0.3558258316920981],
                [-0.04548909780154666, -0.02291302704077903],
            ],
            # Marker 3
            [
                [0.2585297058387899, 0.30999977761054015],
                [0.08112222441275806, 0.2938258761699901],
            ],
            # Marker 4
            [
                [0.2934046808199758, -0.24530417184834036],
                [0.11675535102396956, 0.020217376800687425],
            ],
            # Marker 5
            [
                [0.11827165428402146, 0.42186926257434304],
                [-0.14480696133492332, 0.42321708769438915],
            ],
            # Marker 6
            [
                [-0.04170971192586818, -0.36059376305425983],
                [-0.15328309655861172, -0.18145432634896919],
            ],
        ]
        kwargs = self.create_scene(frame_a, frame_b, marker_data_list)
        kwargs['useCameraTransform'] = True
        kwargs['setValues'] = True

        # save the output
        file_name = 'solver_camera_relative_pose_five_point_pose1_before.ma'
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        assert 'mmSolver' in dir(maya.cmds)
        s = time.time()
        result = maya.cmds.mmCameraRelativePose(**kwargs)
        e = time.time()
        print('total time:', e - s)

        deconstruct_result(kwargs, result)

        # TODO: Test the re-projection deviation between the marker
        # and bundles to ensure they are under a specific minimum.

        # save the output
        file_name = 'solver_camera_relative_pose_five_point_pose1_after.ma'
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

    def test_eight_point_pose1(self):
        frame_a = 90
        frame_b = 227

        marker_data_list = [
            # Marker 1
            [
                [-0.22213842759755273, 0.43804316401489374],
                [-0.08642928582293867, 0.3234780288109984],
            ],
            # Marker 2
            [
                [-0.20545909173698554, -0.3558258316920981],
                [-0.04548909780154666, -0.02291302704077903],
            ],
            # Marker 3
            [
                [0.2585297058387899, 0.30999977761054015],
                [0.08112222441275806, 0.2938258761699901],
            ],
            # Marker 4
            [
                [0.2934046808199758, -0.24530417184834036],
                [0.11675535102396956, 0.020217376800687425],
            ],
            # Marker 5
            [
                [0.11827165428402146, 0.42186926257434304],
                [-0.14480696133492332, 0.42321708769438915],
            ],
            # Marker 6
            [
                [-0.04170971192586818, -0.36059376305425983],
                [-0.15328309655861172, -0.18145432634896919],
            ],
            # Marker 7
            [
                [-0.3174396037950528, 0.018883703844402074],
                [-0.46268515584794695, 0.03510006177623348],
            ],
            # Marker 8
            [
                [-0.3557417274046072, -0.36241117044613047],
                [-0.3943178470132531, -0.24449776807901671],
            ],
            # Marker 9
            [
                [-0.030209309850007183, 0.4380787465980631],
                [-0.3439804204951894, 0.4583753755158096],
            ],
            # Marker 10
            [
                [0.19923110354181264, 0.057848519369854835],
                [0.06719591143730845, 0.16515035978433498],
            ],
        ]
        kwargs = self.create_scene(frame_a, frame_b, marker_data_list)
        kwargs['useCameraTransform'] = True
        kwargs['setValues'] = True

        # save the output
        file_name = 'solver_camera_relative_pose_eight_point_pose1_before.ma'
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        assert 'mmSolver' in dir(maya.cmds)
        s = time.time()
        result = maya.cmds.mmCameraRelativePose(**kwargs)
        e = time.time()
        print('total time:', e - s)

        deconstruct_result(kwargs, result)

        # TODO: Test the re-projection deviation between the marker
        # and bundles to ensure they are under a specific minimum.

        # save the output
        file_name = 'solver_camera_relative_pose_eight_point_pose1_after.ma'
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)


if __name__ == '__main__':
    prog = unittest.main()
