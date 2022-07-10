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
import pprint

try:
    import maya.standalone

    maya.standalone.initialize()
except RuntimeError:
    pass
import maya.cmds

import test.test_solver.solverutils as solverUtils

import mmSolver.api as mmapi
import mmSolver.tools.loadmarker.lib.mayareadfile as marker_read
import mmSolver.tools.loadmarker.lib.utils as lib_utils


TRANSLATE_ATTRS = ['tx', 'ty', 'tz']


def _compute_enabled_marker_nodes(mkr_list, frame):
    """Given a frame, return the valid marker nodes on that frame."""
    mkr_nodes = set()
    for mkr in mkr_list:
        enable = mkr.get_enable(time=frame)
        if enable > 0:
            mkr_node = mkr.get_node()
            mkr_nodes.add(mkr_node)
    return mkr_nodes


def _marker_maximum_frame_count(cam, mkr_list, frames):
    count_max = 0
    frame_max = None
    mkr_nodes_max = set()
    for frame in frames:
        mkr_nodes = _compute_enabled_marker_nodes(mkr_list, frame)
        count = len(mkr_nodes)
        if count >= count_max:
            count_max = count
            frame_max = frame
            mkr_nodes_max = set(mkr_nodes)
    return frame_max, mkr_nodes_max


def _sort_root_frames(cam, mkr_list, frames):
    """Sort the frames by using frames with common shared points."""
    sorted_frames = []

    prev_frame = None
    prev_mkr_nodes = set()
    frame_stack = frames
    while len(frame_stack) > 0:
        frame, mkr_nodes = _marker_maximum_frame_count(cam, mkr_list, frame_stack)
        if prev_frame is None:
            count = len(mkr_nodes)
        else:
            count = len(set(prev_mkr_nodes) & mkr_nodes)

        # Only solves with 6 points or more will work. In theory only
        # 5 points are needed, but OpenMVG seems to be broken perhaps.
        if count < 6:
            frame_stack.remove(frame)
            continue

        if frame is None or len(mkr_nodes) == 0:
            # Cannot find a good frame next, so the last choice is to
            # exit.
            break

        frame_stack.remove(frame)
        sorted_frames.append(frame)
        prev_frame = frame
        prev_mkr_nodes |= mkr_nodes

    return sorted_frames


def camera_solve(cam, mkr_list, start_frame, end_frame, root_frames):
    print('cam:', cam)
    print('mkr_list:', mkr_list)
    print('start_frame:', start_frame)
    print('end_frame:', end_frame)
    print('root_frames:', root_frames)
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()

    sorted_frames = _sort_root_frames(cam, mkr_list, root_frames)

    accumulated_mkr_nodes = set()
    solved_frames = set()
    frame_index = 0
    frame_stack = sorted_frames
    next_frame = frame_stack[0]
    while len(frame_stack) > 1:

        root_frame_a = next_frame  # frame_stack[frame_index]

        possible_frames = list(frame_stack)
        possible_frames.remove(root_frame_a)

        new_possible_frames = []
        root_frame_b = possible_frames[0]
        for possible_frame in possible_frames:
            mkr_nodes_a = _compute_enabled_marker_nodes(mkr_list, root_frame_a)
            mkr_nodes_b = _compute_enabled_marker_nodes(mkr_list, possible_frame)
            mkr_nodes = set(mkr_nodes_a) & set(mkr_nodes_b)
            common_mkr_list = [mmapi.Marker(node=n) for n in mkr_nodes]

            new_mkr_bnd_list = []
            for mkr in common_mkr_list:
                bnd = mkr.get_bundle()
                if bnd is None:
                    bnd = mmapi.Bundle.create_node()
                    mkr.set_bundle(bnd)
                mkr_node = mkr.get_node()
                bnd_node = bnd.get_node()
                mkr_bnd = (mkr_node, mkr_node, bnd_node)
                new_mkr_bnd_list.append(mkr_bnd)

            kwargs = {
                'frameA': root_frame_a,
                'frameB': possible_frame,
                'cameraA': cam_tfm,
                'cameraB': cam_tfm,
                'markerBundle': new_mkr_bnd_list,
                'useCameraTransform': True,
                'setValues': True,
            }
            result = maya.cmds.mmCameraRelativePose(**kwargs) or []
            success = len(result) > 0
            if success is False:
                continue

            solved_frames.add(root_frame_a)
            solved_frames.add(possible_frame)

            accumulated_mkr_nodes |= mkr_nodes

        frame_stack.remove(root_frame_a)
        sorted_frames = _sort_root_frames(cam, mkr_list, frame_stack)
        next_frame = sorted_frames[0]

        if len(solved_frames) < 3:
            # Skip bundle adjusting the first pose to ensure we have
            # enough data to solve the bundle adjustment.
            continue

        solver_index = mmapi.SOLVER_TYPE_CMINPACK_LMDER
        scene_graph_mode = mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH

        solver_cameras = ((cam_tfm, cam_shp),)

        solver_node_attrs = [
            (cam_tfm + '.tx', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.ty', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.tz', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.rx', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.ry', 'None', 'None', 'None', 'None'),
            (cam_tfm + '.rz', 'None', 'None', 'None', 'None'),
            (cam_shp + '.focalLength', 'None', 'None', 'None', 'None'),
        ]

        solver_markers = []
        new_mkr_bnd_list = []
        accumulated_mkr_list = [mmapi.Marker(node=n) for n in mkr_nodes]
        for mkr in accumulated_mkr_list:
            bnd = mkr.get_bundle()
            assert bnd is not None
            mkr_node = mkr.get_node()
            bnd_node = bnd.get_node()
            mkr_bnd = (mkr_node, cam_shp, bnd_node)
            solver_markers.append(mkr_bnd)

        for mkr in common_mkr_list:
            bnd = mkr.get_bundle()
            assert bnd is not None
            bnd_node = bnd.get_node()
            for attr in TRANSLATE_ATTRS:
                solve_node_attr = (
                    '{}.{}'.format(bnd_node, attr),
                    'None',
                    'None',
                    'None',
                    'None',
                )
                solver_node_attrs.append(solve_node_attr)

        solver_kwargs = {
            'camera': solver_cameras,
            'marker': solver_markers,
            'attr': solver_node_attrs,
        }

        affects_mode = 'addAttrsToMarkers'
        result = maya.cmds.mmSolverAffects(mode=affects_mode, **solver_kwargs)

        # After each pose is added to the camera solve, we must do a
        # mmSolver refinement with 'MM Scene Graph', solving the
        # camera position, rotation and bundle positions.
        result = maya.cmds.mmSolver(
            frame=list(sorted(solved_frames)),
            solverType=solver_index,
            sceneGraphMode=scene_graph_mode,
            **solver_kwargs,
        )
        assert result[0] == 'success=1'

    return


# @unittest.skip
class TestCameraSolve(solverUtils.SolverTestCase):
    def test_camera_solve1_stA(self):
        frame_a = 0
        frame_b = 94
        root_frame_a = frame_a
        root_frame_b = frame_b
        maya.cmds.playbackOptions(edit=True, minTime=frame_a)
        maya.cmds.playbackOptions(edit=True, maxTime=frame_b)

        cam = lib_utils.create_new_camera()
        mkr_grp = lib_utils.create_new_marker_group(cam)

        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()
        fb_width = 36.0 / 25.4
        fb_height = 24.0 / 25.4
        # Note: 35 mm is not the correct focal length for the shot,
        # but despite this we leave it as the wrong value, as a task
        # for the solver to refine.
        focal_length = 35.0
        maya.cmds.setAttr(cam_tfm + '.rotateOrder', 2)  # 2 = ZXY
        maya.cmds.setAttr(cam_shp + '.horizontalFilmAperture', fb_width)
        maya.cmds.setAttr(cam_shp + '.verticalFilmAperture', fb_height)
        maya.cmds.setAttr(cam_shp + '.focalLength', focal_length)
        maya.cmds.setAttr(cam_shp + '.displayCameraFrustum', 1)
        maya.cmds.setAttr(cam_shp + '.displayFilmGate', 1)
        maya.cmds.setAttr(cam_shp + '.overscan', 1.5)

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

        marker_file_path = self.get_data_path('uvtrack', 'stA.uv')
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

        # Root Frames
        min_frames_per_marker = 3
        max_frame_span = 5
        root_frames = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, frame_a, frame_b
        )
        root_frames = mmapi.root_frames_list_combine(root_frames, [frame_a, frame_b])
        root_frames = mmapi.root_frames_subdivide(root_frames, max_frame_span)

        # save the output
        file_name = 'solver_camera_solve1_stA_before.ma'
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        assert 'mmSolver' in dir(maya.cmds)
        s = time.time()
        camera_solve(cam, mkr_list, frame_a, frame_b, root_frames)
        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = 'solver_camera_solve1_stA_after.ma'
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

    def test_camera_solve2_operahouse(self):
        frame_a = 0
        frame_b = 41
        root_frame_a = frame_a
        root_frame_b = frame_b
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

        # Root Frames
        min_frames_per_marker = 2
        max_frame_span = 5
        root_frames = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, frame_a, frame_b
        )
        root_frames = mmapi.root_frames_list_combine(root_frames, [frame_a, frame_b])
        root_frames = mmapi.root_frames_subdivide(root_frames, max_frame_span)
        # print('root_frames:', root_frames)

        # save the output
        file_name = 'solver_camera_solve2_operahouse_before.ma'
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)

        # Run solver!
        assert 'mmSolver' in dir(maya.cmds)
        s = time.time()
        camera_solve(cam, mkr_list, frame_a, frame_b, root_frames)
        e = time.time()
        print('total time:', e - s)

        # save the output
        file_name = 'solver_camera_solve2_operahouse_after.ma'
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)


if __name__ == '__main__':
    prog = unittest.main()