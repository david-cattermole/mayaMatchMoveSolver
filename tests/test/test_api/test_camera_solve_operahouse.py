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
Solve the camera trajectory using 2D marker positions only.
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

import test.test_api.apiutils as test_api_utils

import mmSolver.api as mmapi
import mmSolver._api.solvercamerautils as solvercamerautils
import mmSolver.tools.loadmarker.lib.mayareadfile as marker_read
import mmSolver.tools.loadmarker.lib.utils as lib_utils
import mmSolver.tools.createlens.lib as createlens_lib


# @unittest.skip
class TestCameraSolveOperahouse(test_api_utils.APITestCase):
    def create_scene_operahouse(self, frame_a, frame_b):
        maya.cmds.playbackOptions(edit=True, minTime=frame_a)
        maya.cmds.playbackOptions(edit=True, maxTime=frame_b)

        cam = lib_utils.create_new_camera()
        mkr_grp = lib_utils.create_new_marker_group(cam)

        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()
        fb_width = 5.4187 / 25.4
        fb_height = 4.0640 / 25.4
        focal_length = 14.0
        maya.cmds.setAttr(cam_tfm + '.rotateOrder', 2)  # 2 = ZXY
        maya.cmds.setAttr(cam_shp + '.horizontalFilmAperture', fb_width)
        maya.cmds.setAttr(cam_shp + '.verticalFilmAperture', fb_height)
        maya.cmds.setAttr(cam_shp + '.focalLength', focal_length)
        maya.cmds.setAttr(cam_shp + '.displayCameraFrustum', 1)
        maya.cmds.setAttr(cam_shp + '.displayFilmGate', 1)
        maya.cmds.setAttr(cam_shp + '.overscan', 1.5)
        cam = mmapi.Camera(shape=cam_shp)

        # Create lens
        lens = createlens_lib.create_lens_on_camera(cam, force_create_new=None)
        lens_node = lens.get_node()
        maya.cmds.setAttr(lens_node + '.lensModel', 2)  # 2 = 3DE Classic

        attrs = [
            'translateX',
            'translateY',
            'translateZ',
            'rotateX',
            'rotateY',
            'rotateZ',
        ]
        for attr in attrs:
            maya.cmds.setKeyframe(cam_tfm, attribute=attr, time=frame_a, value=0.0)
        maya.cmds.setKeyframe(
            cam_shp, attribute='focalLength', time=frame_a, value=focal_length
        )

        marker_file_path = self.get_data_path('match_mover', 'loadmarker.rz2')
        _, mkr_data_list = marker_read.read(marker_file_path)
        mkr_list = marker_read.create_nodes(mkr_data_list, cam=cam, mkr_grp=mkr_grp)

        mkr_bnd_list = []
        for mkr in mkr_list:

            bnd = mkr.get_bundle()
            if bnd is None:
                print('mkr (%r) could not get bundle.')
                assert False
            mkr_node = mkr.get_node()
            bnd_node = bnd.get_node()
            assert mkr_node is not None
            assert bnd_node is not None
            mkr_bnd = (mkr_node, bnd_node)
            mkr_bnd_list.append(mkr_bnd)

        scene_data = {
            'cam': cam,
            'lens': lens,
            'mkr_list': mkr_list,
            'mkr_bnd_list': mkr_bnd_list,
        }
        return scene_data

    def solve_operahouse(
        self,
        name,
        cam,
        lens,
        mkr_list,
        mkr_bnd_list,
        frame_a,
        frame_b,
        scene_scale,
        origin_frame,
        root_frame_a=None,
        root_frame_b=None,
        min_frames_per_marker=None,
        max_frame_span=None,
    ):
        assert isinstance(cam, mmapi.Camera)
        assert lens is None or isinstance(lens, mmapi.Lens)
        assert isinstance(mkr_list, list)
        assert isinstance(mkr_bnd_list, list)
        assert isinstance(frame_a, int)
        assert isinstance(frame_b, int)
        assert isinstance(scene_scale, float)
        assert isinstance(origin_frame, int)
        assert root_frame_a is None or isinstance(root_frame_a, int)
        assert root_frame_b is None or isinstance(root_frame_b, int)
        assert min_frames_per_marker is None or isinstance(min_frames_per_marker, int)
        assert max_frame_span is None or isinstance(max_frame_span, int)

        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()
        lens_node = None
        if lens is not None:
            lens_node = lens.get_node()

        # Frames start to end to solve.
        frame_list = []
        for f in range(frame_a, frame_b + 1):
            frm = mmapi.Frame(f)
            frame_list.append(frm)

        # Root Frames
        root_frames = []
        if min_frames_per_marker is not None:
            root_frames = mmapi.get_root_frames_from_markers(
                mkr_list, min_frames_per_marker, frame_a, frame_b
            )
        if root_frame_a is not None and root_frame_b is not None:
            root_frames = mmapi.root_frames_list_combine(
                root_frames, [root_frame_a, root_frame_b]
            )
        if max_frame_span is not None:
            root_frames = mmapi.root_frames_subdivide(root_frames, max_frame_span)
        root_frame_list = [mmapi.Frame(f) for f in root_frames]

        sol_list = []
        sol = mmapi.SolverCamera()
        sol.set_root_frame_list(root_frame_list)
        sol.set_frame_list(frame_list)
        sol.set_origin_frame(origin_frame)
        sol.set_scene_scale(scene_scale)
        sol.set_triangulate_bundles(True)
        sol_list.append(sol)

        col = mmapi.Collection()
        col.create_node('mySolverCollection')
        col.add_solver_list(sol_list)
        col.add_marker_list(mkr_list)

        # Attributes
        attr_cam_tx = mmapi.Attribute(cam_tfm + '.tx')
        attr_cam_ty = mmapi.Attribute(cam_tfm + '.ty')
        attr_cam_tz = mmapi.Attribute(cam_tfm + '.tz')
        attr_cam_rx = mmapi.Attribute(cam_tfm + '.rx')
        attr_cam_ry = mmapi.Attribute(cam_tfm + '.ry')
        attr_cam_rz = mmapi.Attribute(cam_tfm + '.rz')
        attr_cam_focal = mmapi.Attribute(cam_shp + '.focalLength')
        col.add_attribute(attr_cam_tx)
        col.add_attribute(attr_cam_ty)
        col.add_attribute(attr_cam_tz)
        col.add_attribute(attr_cam_rx)
        col.add_attribute(attr_cam_ry)
        col.add_attribute(attr_cam_rz)
        col.add_attribute(attr_cam_focal)

        if lens_node is not None:
            attr_lens_k1 = mmapi.Attribute(lens_node + '.tdeClassic_distortion')
            attr_lens_k2 = mmapi.Attribute(lens_node + '.tdeClassic_quarticDistortion')
            col.add_attribute(attr_lens_k1)
            col.add_attribute(attr_lens_k2)

        for mkr in mkr_list:
            bnd = mkr.get_bundle()
            bnd_node = bnd.get_node()
            attr_tx = mmapi.Attribute(bnd_node + '.tx')
            attr_ty = mmapi.Attribute(bnd_node + '.ty')
            attr_tz = mmapi.Attribute(bnd_node + '.tz')
            col.add_attribute(attr_tx)
            col.add_attribute(attr_ty)
            col.add_attribute(attr_tz)

        # save the output
        file_name = '{}_before.ma'.format(name)
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        assert 'mmSolver' in dir(maya.cmds)
        s = time.time()
        mmapi.execute(col)
        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = '{}_after.ma'.format(name)
        path = self.get_output_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return

    def test_camera_solve2_operahouse(self):
        frame_a = 0
        frame_b = 41
        scene_scale = 10.0
        origin_frame = frame_a
        root_frame_a = frame_a
        root_frame_b = frame_b
        min_frames_per_marker = 3
        max_frame_span = 5

        scene_data = self.create_scene_operahouse(frame_a, frame_b)

        name = 'solver_camera_solve2_operahouse'
        self.solve_operahouse(
            name,
            scene_data['cam'],
            scene_data['lens'],
            scene_data['mkr_list'],
            scene_data['mkr_bnd_list'],
            frame_a,
            frame_b,
            scene_scale,
            origin_frame,
            root_frame_a=root_frame_a,
            root_frame_b=root_frame_b,
            min_frames_per_marker=min_frames_per_marker,
            max_frame_span=max_frame_span,
        )

    def test_camera_solve4_operahouse_marker_score(self):
        # Tests the Marker score calculation.
        frame_a = 0
        frame_b = 41

        scene_data = self.create_scene_operahouse(frame_a, frame_b)
        mkr_list = scene_data['mkr_list']

        # Root Frames
        min_frames_per_marker = 2
        max_frame_span = 5
        root_frame_a = frame_a
        root_frame_b = frame_b
        root_frames = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, frame_a, frame_b
        )
        root_frames = mmapi.root_frames_list_combine(
            root_frames, [root_frame_a, root_frame_b]
        )
        root_frames = mmapi.root_frames_subdivide(root_frames, max_frame_span)

        s = time.time()
        enabled_marker_nodes = solvercamerautils._cache_enabled_marker_nodes(
            mkr_list, root_frames
        )
        position_marker_nodes = solvercamerautils._cache_position_marker_nodes(
            root_frames, enabled_marker_nodes
        )

        expected_values = {
            0: 1092,
            1: 1110,
            2: 1110,
            3: 1020,
            7: 1088,
            12: 1088,
            13: 1184,
            14: 930,
            17: 990,
            20: 952,
            23: 1326,
            28: 1558,
            33: 1932,
            37: 1722,
            40: 1600,
            41: 1360,
        }

        for frame in root_frames:
            mkr_nodes = enabled_marker_nodes[frame]
            score = solvercamerautils._calculate_marker_frame_score(
                mkr_nodes, frame, position_marker_nodes
            )
            print('frame:', frame, 'score:', score)
            expected_value = expected_values.get(frame)
            assert expected_value is not None
            assert expected_value == score

        e = time.time()
        print('total time:', e - s)


if __name__ == '__main__':
    prog = unittest.main()
