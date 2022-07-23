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
import mmSolver.tools.triangulatebundle.lib as lib_triangulate
import mmSolver.utils.animcurve as animcurve_utils


TRANSLATE_ATTRS = ['tx', 'ty', 'tz']


def _calculate_marker_frame_score(cam_tfm, mkr_nodes, frame, position_marker_nodes):
    """
    Calculate the score of the frame.

    Uses the paper "Structure-from-Motion Revisited", by Johannes
    L. Schonberger, Jan-Michael Frahm, published in 2016, section
    "4.2. Next Best View Selection".
    """
    score = 0

    min_pos = -0.5
    max_pos = 0.5
    levels = 3
    for level in range(levels):
        total_num = pow(2, level)
        weight = total_num

        bins = set()
        positions = []
        for mkr_node in mkr_nodes:
            pos = position_marker_nodes[frame][mkr_node]
            positions.append(pos)

        for pos_x, pos_y in positions:
            if pos_x < min_pos or pos_x > max_pos or pos_y < min_pos or pos_y > max_pos:
                continue

            for y in range(-total_num, total_num):
                for x in range(-total_num, total_num):
                    min_x_f = -min_pos * (x / total_num)
                    max_x_f = max_pos * ((x + 1) / total_num)
                    min_y_f = -min_pos * (y / total_num)
                    max_y_f = max_pos * ((y + 1) / total_num)
                    if (
                        pos_x > min_x_f
                        and pos_x <= max_x_f
                        and pos_y > min_y_f
                        and pos_y <= max_y_f
                    ):
                        bins.add((x, y))
        score += len(bins) * weight

    # Unlike the paper (see above), the score is multipied with the
    # number of enabled markers. This means that if two frames have
    # exactly the same number of markers, but different "uniformity
    # score" (calculated below), then a more uniformly distributed
    # number of frames produces a higher overall score.
    score *= len(mkr_nodes)
    return score


def _compute_enabled_marker_nodes(mkr_list, frame):
    """Given a frame, return the valid marker nodes on that frame."""
    mkr_nodes = set()
    for mkr in mkr_list:
        enable = mkr.get_enable(time=frame)
        if enable > 0:
            mkr_node = mkr.get_node()
            mkr_nodes.add(mkr_node)
    return mkr_nodes


def _marker_maximum_frame_score(
    cam, mkr_list, frames, enabled_marker_nodes, position_marker_nodes
):
    score_max = 0
    frame_max = None
    mkr_nodes_max = set()
    for frame in frames:
        score = _calculate_marker_frame_score(
            cam, mkr_list, frame, position_marker_nodes
        )
        if score >= score_max:
            score_max = score
            frame_max = frame
            mkr_nodes = enabled_marker_nodes[frame]
            assert isinstance(mkr_nodes, set)
            mkr_nodes_max = mkr_nodes
    # print('frame_max:', frame_max, 'score_max:', score_max)
    return frame_max, mkr_nodes_max


def _compute_connected_frame_scores(
    cam,
    mkr_list,
    root_frame_a,
    possible_frames,
    enabled_marker_nodes,
    position_marker_nodes,
):
    mkr_nodes_a = enabled_marker_nodes[root_frame_a]
    assert isinstance(mkr_nodes_a, set)

    scores = []
    for frame in possible_frames:
        mkr_nodes_b = enabled_marker_nodes[frame]
        assert isinstance(mkr_nodes_b, set)

        score = 0
        mkr_nodes = mkr_nodes_a & mkr_nodes_b
        if len(mkr_nodes) < 6:
            # Not enough points, we need at least 6 points to solve
            # two frames of a camera pose and bundles.
            pass
        else:
            score = _calculate_marker_frame_score(
                cam, mkr_nodes, frame, position_marker_nodes
            )
        scores.append(score)
    return scores


def _find_best_connected_frame(
    cam,
    mkr_list,
    root_frame_a,
    possible_frames,
    enabled_marker_nodes,
    position_marker_nodes,
):
    frame = 0

    mkr_nodes_a = enabled_marker_nodes[root_frame_a]
    assert isinstance(mkr_nodes_a, set)

    scores = _compute_connected_frame_scores(
        cam,
        mkr_list,
        root_frame_a,
        possible_frames,
        enabled_marker_nodes,
        position_marker_nodes,
    )
    sorted_frame_scores = reversed(
        sorted(zip(possible_frames, scores), key=lambda x: x[1])
    )

    sorted_frames = [x[0] for x in sorted_frame_scores if x[1] != 0]
    # print('best_connected_frames for ', root_frame_a, ' :', sorted_frames)

    best_frame = None
    if len(sorted_frames) > 0:
        best_frame = sorted_frames[0]
    max_score = max(scores)
    if best_frame is not None and max_score > 0:
        print(
            'Best connected frame pair found:',
            root_frame_a,
            'to',
            best_frame,
            'with score:',
            max(scores),
        )
    return best_frame


def _bundle_adjust(
    cam_tfm,
    cam_shp,
    mkr_nodes,
    frames,
    adjust_camera_translate=None,
    adjust_camera_rotate=None,
    adjust_bundle_positions=None,
    adjust_focal_length=None,
    iteration_num=None,
    per_frame_solve=None,
):
    if adjust_camera_translate is None:
        adjust_camera_translate = False
    if adjust_camera_rotate is None:
        adjust_camera_rotate = False
    if adjust_bundle_positions is None:
        adjust_bundle_positions = False
    if adjust_focal_length is None:
        adjust_focal_length = False
    if iteration_num is None:
        iteration_num = 100
    if per_frame_solve is None:
        per_frame_solve = False
    assert isinstance(adjust_camera_translate, bool)
    assert isinstance(adjust_camera_rotate, bool)
    assert isinstance(adjust_bundle_positions, bool)
    assert isinstance(adjust_focal_length, bool)

    frame_solve_mode = mmapi.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE
    if per_frame_solve is True:
        frame_solve_mode = mmapi.FRAME_SOLVE_MODE_PER_FRAME

    solver_index = mmapi.SOLVER_TYPE_CMINPACK_LMDER
    scene_graph_mode = mmapi.SCENE_GRAPH_MODE_MM_SCENE_GRAPH
    # scene_graph_name = mmapi.SCENE_GRAPH_MODE_NAME_LIST[scene_graph_mode]
    # scene_graph_label = mmapi.SCENE_GRAPH_MODE_LABEL_LIST[scene_graph_mode]
    # print('Scene Graph:', scene_graph_label)

    cameras = ((cam_tfm, cam_shp),)

    node_attrs = []
    if adjust_camera_translate is True:
        node_attrs.append((cam_tfm + '.tx', 'None', 'None', 'None', 'None'))
        node_attrs.append((cam_tfm + '.ty', 'None', 'None', 'None', 'None'))
        node_attrs.append((cam_tfm + '.tz', 'None', 'None', 'None', 'None'))

    if adjust_camera_rotate is True:
        node_attrs.append((cam_tfm + '.rx', 'None', 'None', 'None', 'None'))
        node_attrs.append((cam_tfm + '.ry', 'None', 'None', 'None', 'None'))
        node_attrs.append((cam_tfm + '.rz', 'None', 'None', 'None', 'None'))

    if adjust_focal_length is True:
        value = (cam_shp + '.focalLength', 'None', 'None', 'None', 'None')
        node_attrs.append(value)

    markers = []
    new_mkr_bnd_list = []
    mkr_list = [mmapi.Marker(node=n) for n in mkr_nodes]
    for mkr in mkr_list:
        bnd = mkr.get_bundle()
        assert bnd is not None
        # print('mkr:', mkr, 'bnd:', bnd)
        mkr_node = mkr.get_node()
        bnd_node = bnd.get_node()
        mkr_bnd = (mkr_node, cam_shp, bnd_node)
        markers.append(mkr_bnd)

        if adjust_bundle_positions is True:
            for attr in TRANSLATE_ATTRS:
                solve_node_attr = (
                    '{}.{}'.format(bnd_node, attr),
                    'None',
                    'None',
                    'None',
                    'None',
                )
                node_attrs.append(solve_node_attr)

    # Per-frame solves must only solve with animated attributes.
    if per_frame_solve is True:
        tmp_node_attrs = list(node_attrs)
        node_attrs = []
        for node_attr in tmp_node_attrs:
            attr = node_attr[0]
            key_count = maya.cmds.keyframe(attr, query=True, keyframeCount=True)
            is_animated = key_count > 0
            if is_animated is True:
                node_attrs.append(node_attr)

    kwargs = {
        'camera': cameras,
        'marker': markers,
        'attr': node_attrs,
    }
    # print(pprint.pformat(kwargs))

    # affects_mode = 'addAttrsToMarkers'
    # result = maya.cmds.mmSolverAffects(mode=affects_mode, **kwargs)
    # # print('result:', result)

    # After each pose is added to the camera solve, we must do a
    # mmSolver refinement with 'MM Scene Graph', solving the
    # camera position, rotation and bundle positions.
    result = maya.cmds.mmSolver(
        frame=frames,
        solverType=solver_index,
        sceneGraphMode=scene_graph_mode,
        iterations=iteration_num,
        frameSolveMode=frame_solve_mode,
        **kwargs,
    )
    # print('result:', result)
    assert result[0] == 'success=1'
    return


def _solve_relative_poses(
    cam_tfm,
    cam_shp,
    mkr_nodes_a,
    root_frame_a,
    possible_frames,
    solved_frames,
    accumulated_mkr_nodes,
    accumulated_bnd_nodes,
    enabled_marker_nodes,
):
    assert isinstance(solved_frames, set)
    assert isinstance(accumulated_mkr_nodes, set)
    assert isinstance(accumulated_bnd_nodes, set)
    failed_frames = set()

    new_possible_frames = []
    tmp_possible_frames = list(possible_frames)
    while len(tmp_possible_frames) > 0:
        if root_frame_a in tmp_possible_frames:
            tmp_possible_frames.remove(root_frame_a)

        # The closest frame number ot the root frame, so we move
        # incrementally outwards from the root frame.
        possible_frame = min(tmp_possible_frames, key=lambda x: abs(x - root_frame_a))
        tmp_possible_frames.remove(possible_frame)

        if possible_frame in solved_frames:
            # Already solved, no need to solve it again.
            continue
        if possible_frame in failed_frames:
            # Already failed to solve, no need to try again.
            continue

        mkr_nodes_b = enabled_marker_nodes[possible_frame]
        mkr_nodes = set(mkr_nodes_a) & set(mkr_nodes_b)
        common_mkr_list = [mmapi.Marker(node=n) for n in mkr_nodes]

        bnd_nodes = set()
        new_mkr_bnd_list = []
        for mkr in common_mkr_list:
            bnd = mkr.get_bundle()
            if bnd is None:
                bnd = mmapi.Bundle.create_node()
                mkr.set_bundle(bnd)
            # print('mkr:', mkr, 'bnd:', bnd)
            mkr_node = mkr.get_node()
            bnd_node = bnd.get_node()
            mkr_bnd = (mkr_node, mkr_node, bnd_node)
            new_mkr_bnd_list.append(mkr_bnd)
            bnd_nodes.add(bnd_node)

        kwargs = {
            'frameA': root_frame_a,
            'frameB': possible_frame,
            'cameraA': cam_tfm,
            'cameraB': cam_tfm,
            'markerBundle': new_mkr_bnd_list,
            'useCameraTransform': True,
            'setValues': True,
        }
        result = maya.cmds.mmCameraRelativePose(**kwargs)
        if result is None:
            print('Failed Camera Pose:', root_frame_a, 'to', possible_frame)
            failed_frames.add(possible_frame)
            continue

        print('Solved Camera Pose:', root_frame_a, 'to', possible_frame)
        solved_frames.add(root_frame_a)
        solved_frames.add(possible_frame)
        accumulated_mkr_nodes = accumulated_mkr_nodes | mkr_nodes
        accumulated_bnd_nodes = accumulated_bnd_nodes | bnd_nodes

        # Refine the solve.
        solved_frames_count = len(solved_frames)
        solve_every_n_poses = 10
        if (solved_frames_count % solve_every_n_poses) == 0:
            animcurve_utils.euler_filter_plug(cam_tfm, 'rotateX')
            animcurve_utils.euler_filter_plug(cam_tfm, 'rotateY')
            animcurve_utils.euler_filter_plug(cam_tfm, 'rotateZ')

            frames = list(sorted(solved_frames))
            _bundle_adjust(
                cam_tfm,
                cam_shp,
                accumulated_mkr_nodes,
                frames,
                adjust_camera_translate=True,
                adjust_camera_rotate=True,
                adjust_bundle_positions=True,
                adjust_focal_length=True,
                iteration_num=25,
            )

    return accumulated_mkr_nodes, accumulated_bnd_nodes, solved_frames, failed_frames


def _triangulate_bundles(
    mkr_list, mkr_nodes, bnd_nodes, solver_frames, marker_nodes_enabled
):
    assert isinstance(solver_frames, set)
    assert isinstance(marker_nodes_enabled, dict)
    triangulated_count = 0
    for mkr in mkr_list:
        bnd = mkr.get_bundle()
        if bnd is None:
            continue

        mkr_node = mkr.get_node()
        bnd_node = bnd.get_node()

        start_solved_frame = min(solver_frames)
        end_solved_frame = max(solver_frames)
        enabled_frames = marker_nodes_enabled[mkr_node]
        assert isinstance(enabled_frames, set)
        overlapping_frames = solver_frames & enabled_frames
        if len(overlapping_frames) < 2:
            continue

        if bnd_node not in bnd_nodes:
            ok = lib_triangulate.triangulate_bundle(bnd, direction_tolerance=2.0)
            if ok is True:
                print('Triangulated Bundle:', bnd_node)
                mkr_nodes.add(mkr_node)
                bnd_nodes.add(bnd_node)
                triangulated_count += 1
            else:
                print('Failed to triangulated Bundle:', bnd_node)
    return triangulated_count, mkr_nodes, bnd_nodes


def camera_solve(cam, mkr_list, start_frame, end_frame, root_frames):
    # TODO: Categorize the marker/bundle nodes that are given to this
    # function and output the categories. This will allow the caller
    # to organise the nodes for the user to see diagnostic
    # information.
    print('cam:', cam)
    print('mkr_list:', pprint.pformat(mkr_list))
    print('start_frame:', start_frame)
    print('end_frame:', end_frame)
    print('root_frame count:', len(root_frames))
    print('root_frames:', root_frames)
    cam_tfm = cam.get_transform_node()
    cam_shp = cam.get_shape_node()

    # Create cache for re-use in _compute_enabled_marker_nodes().
    enabled_marker_nodes = {}
    for frame in root_frames:
        mkr_nodes = _compute_enabled_marker_nodes(mkr_list, frame)
        enabled_marker_nodes[frame] = mkr_nodes

    marker_nodes_enabled = {}
    for mkr in mkr_list:
        mkr_node = mkr.get_node()
        enabled_frames = mkr.get_enabled_frames(
            frame_range_start=start_frame, frame_range_end=end_frame
        )
        marker_nodes_enabled[mkr_node] = set(enabled_frames)

    # Create cache for re-use in _marker_maximum_frame_score().
    position_marker_nodes = {}
    for frame in root_frames:
        position_marker_nodes[frame] = {}
        mkr_positions = {}
        mkr_nodes = enabled_marker_nodes[frame]
        for mkr_node in mkr_nodes:
            attr_tx = mkr_node + '.translateX'
            attr_ty = mkr_node + '.translateY'
            pos_x = maya.cmds.getAttr(attr_tx, time=frame)
            pos_y = maya.cmds.getAttr(attr_ty, time=frame)
            mkr_position = (pos_x, pos_y)
            position_marker_nodes[frame][mkr_node] = mkr_position

    # Pre-compute the connected frame statistics, to help guess the
    # best frames for solving camera pairs.
    frame_scores_map = {}
    frame_scores_stats_map = {}
    frame_best_frame_map = {}
    for frame in root_frames:
        scores = _compute_connected_frame_scores(
            cam,
            mkr_list,
            frame,
            root_frames,
            enabled_marker_nodes,
            position_marker_nodes,
        )
        frame_scores = zip(root_frames, scores)
        frame_scores_map[frame] = list(frame_scores)

        best_frame = None
        best_score = -1
        for frame_score in frame_scores:
            if frame_score[1] >= best_score:
                best_frame = frame_score[0]
                best_score = frame_score[1]
        frame_best_frame_map[frame] = (best_frame, best_score)

        max_score = max(scores)
        avg_score = sum(scores) / len(scores)
        frame_scores_stats_map[frame] = (avg_score, max_score)

    # Find the frame with the best connectivity to all other root
    # frames. This is not the frame that gives the most solved frames,
    # but rather the highest quality solve overall.
    #
    # For simple camera solves with plenty of 2D marker data the best
    # frame should have connectivity to all other root frames.
    best_frame = None
    best_score = -1
    for frame in reversed(root_frames):
        frames_scores = frame_scores_map[frame]
        frame_score_stats = frame_scores_stats_map[frame]
        avg_score, max_score = frame_score_stats
        if avg_score >= best_score:
            best_score = avg_score
            best_frame = frame

    # print('best_frame:', best_frame)
    # print('best_score:', best_score)

    frame_stack = list(root_frames)
    next_frame = best_frame
    root_frame_a = best_frame
    mkr_nodes_a = enabled_marker_nodes[root_frame_a]

    possible_frames = list(frame_stack)
    if root_frame_a in possible_frames:
        possible_frames.remove(root_frame_a)

    solved_frames = set()
    accumulated_mkr_nodes = set()
    accumulated_bnd_nodes = set()
    before_count = 0
    while len(possible_frames) > 0:
        print('root_frame_a:', root_frame_a)

        # Only solves the frame that are possible to be solved from the root frame.
        relative_pose_frames = []
        pose_frame_scores = frame_scores_map[root_frame_a]
        for frame, score in pose_frame_scores:
            if score > 0 and frame not in solved_frames:
                relative_pose_frames.append(frame)

        (
            accumulated_mkr_nodes,
            accumulated_bnd_nodes,
            solved_frames,
            failed_frames,
        ) = _solve_relative_poses(
            cam_tfm,
            cam_shp,
            mkr_nodes_a,
            root_frame_a,
            relative_pose_frames,
            solved_frames,
            accumulated_mkr_nodes,
            accumulated_bnd_nodes,
            enabled_marker_nodes,
        )

        for frame in solved_frames:
            if frame in possible_frames:
                possible_frames.remove(frame)

        after_count = len(solved_frames)
        if before_count == after_count:
            # No progress made.
            break

        if len(possible_frames) == 0:
            break

        possible_frame = min(possible_frames)
        # Closest value to 'possible_frame' frame.
        root_frame_a = min(solved_frames, key=lambda x: abs(x - possible_frame))
        before_count = after_count

    if len(solved_frames) > 2:
        # Only bundle adjust after the first pose to ensure we have
        # enough data to solve the bundle adjustment.

        # Refine the solve.
        frames = list(sorted(solved_frames))
        for mkr_node in accumulated_mkr_nodes:
            start_solved_frame = min(frames)
            end_solved_frame = max(frames)
            enabled_frames = marker_nodes_enabled[mkr_node]
            assert isinstance(enabled_frames, set)
            overlapping_frames = set(frames) & enabled_frames
            if len(overlapping_frames) < 2:
                continue
            overlapping_frames = list(sorted(overlapping_frames))

            _bundle_adjust(
                cam_tfm,
                cam_shp,
                [mkr_node],
                overlapping_frames,
                adjust_camera_translate=False,
                adjust_camera_rotate=False,
                adjust_bundle_positions=True,
                adjust_focal_length=False,
                iteration_num=5,
            )

        adjust_mkr_nodes = set()
        for mkr_node in accumulated_mkr_nodes:
            enabled_frames = marker_nodes_enabled[mkr_node]
            assert isinstance(enabled_frames, set)
            overlapping_frames = set(frames) & set(enabled_frames)
            if len(overlapping_frames) > 2:
                adjust_mkr_nodes.add(mkr_node)
        adjust_mkr_nodes = list(sorted(adjust_mkr_nodes))

        _bundle_adjust(
            cam_tfm,
            cam_shp,
            adjust_mkr_nodes,
            frames,
            adjust_camera_translate=True,
            adjust_camera_rotate=True,
            adjust_bundle_positions=True,
            adjust_focal_length=True,
            iteration_num=100,
        )

    # Triangulate Bundles that were not solved with camera relative
    # poses.
    (
        triangulated_count,
        accumulated_mkr_nodes,
        accumulated_bnd_nodes,
    ) = _triangulate_bundles(
        mkr_list,
        accumulated_mkr_nodes,
        accumulated_bnd_nodes,
        solved_frames,
        marker_nodes_enabled,
    )

    if len(solved_frames) > 2 and triangulated_count > 0:
        # Only bundle adjust after the first pose to ensure we have
        # enough data to solve the bundle adjustment.

        # Refine the solve.
        frames = list(sorted(solved_frames))
        for mkr_node in accumulated_mkr_nodes:
            mkr = mmapi.Marker(node=mkr_node)
            start_solved_frame = min(frames)
            end_solved_frame = max(frames)
            enabled_frames = mkr.get_enabled_frames(
                frame_range_start=start_solved_frame, frame_range_end=end_solved_frame
            )
            overlapping_frames = set(frames) & set(enabled_frames)
            if len(overlapping_frames) < 2:
                continue
            overlapping_frames = list(sorted(overlapping_frames))

            _bundle_adjust(
                cam_tfm,
                cam_shp,
                [mkr_node],
                overlapping_frames,
                adjust_camera_translate=False,
                adjust_camera_rotate=False,
                adjust_bundle_positions=True,
                adjust_focal_length=False,
                iteration_num=5,
            )

        adjust_mkr_nodes = set()
        for mkr_node in accumulated_mkr_nodes:
            enabled_frames = marker_nodes_enabled[mkr_node]
            assert isinstance(enabled_frames, set)
            overlapping_frames = set(frames) & set(enabled_frames)
            if len(overlapping_frames) > 2:
                adjust_mkr_nodes.add(mkr_node)
        adjust_mkr_nodes = list(sorted(adjust_mkr_nodes))

        _bundle_adjust(
            cam_tfm,
            cam_shp,
            adjust_mkr_nodes,
            frames,
            adjust_camera_translate=True,
            adjust_camera_rotate=True,
            adjust_bundle_positions=True,
            adjust_focal_length=True,
            iteration_num=100,
        )

    # Solve per-frame. Only animated attributes are solved - bundles
    # and (static) focal lengths are ignored.
    start_frame = min(frames)
    end_frame = max(frames)
    frames = list(range(start_frame, end_frame + 1))

    adjust_mkr_nodes = set()
    for mkr_node in accumulated_mkr_nodes:
        enabled_frames = marker_nodes_enabled[mkr_node]
        assert isinstance(enabled_frames, set)
        overlapping_frames = set(frames) & enabled_frames
        if len(overlapping_frames) > 2:
            adjust_mkr_nodes.add(mkr_node)
    adjust_mkr_nodes = list(sorted(adjust_mkr_nodes))

    _bundle_adjust(
        cam_tfm,
        cam_shp,
        adjust_mkr_nodes,
        frames,
        adjust_camera_translate=True,
        adjust_camera_rotate=True,
        adjust_bundle_positions=False,
        adjust_focal_length=True,
        per_frame_solve=True,
    )

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
        # print('root_frames:', root_frames)

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
        return

    def test_camera_solve3_garage(self):
        frame_a = 0
        # frame_b = 2706
        frame_b = 600
        root_frame_a = frame_a
        root_frame_b = frame_b
        maya.cmds.playbackOptions(edit=True, minTime=frame_a)
        maya.cmds.playbackOptions(edit=True, maxTime=frame_b)

        cam = lib_utils.create_new_camera()
        mkr_grp = lib_utils.create_new_marker_group(cam)

        cam_tfm = cam.get_transform_node()
        cam_shp = cam.get_shape_node()
        fb_width = 36.0 / 25.4
        fb_height = 20.25 / 25.4
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

        marker_file_path = self.get_data_path('pftrack', 'pftrack5_garage.2dt')
        _, mkr_data_list = marker_read.read(
            marker_file_path, image_width=960, image_height=540
        )
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
        max_frame_span = 20
        root_frames = mmapi.get_root_frames_from_markers(
            mkr_list, min_frames_per_marker, frame_a, frame_b
        )
        root_frames = mmapi.root_frames_list_combine(root_frames, [frame_a, frame_b])
        root_frames = mmapi.root_frames_subdivide(root_frames, max_frame_span)

        # save the output
        file_name = 'solver_camera_solve3_garage_before.ma'
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
        file_name = 'solver_camera_solve3_garage_after.ma'
        path = self.get_data_path(file_name)
        maya.cmds.file(rename=path)
        maya.cmds.file(save=True, type='mayaAscii', force=True)
        return

    def test_camera_solve4_operahouse_marker_score(self):
        # Tests the Marker score calculation.
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

        s = time.time()

        # Create cache for re-use in _compute_enabled_marker_nodes().
        enabled_marker_nodes = {}
        for frame in root_frames:
            mkr_nodes = _compute_enabled_marker_nodes(mkr_list, frame)
            enabled_marker_nodes[frame] = mkr_nodes

        # Create cache for re-use in _marker_maximum_frame_score().
        position_marker_nodes = {}
        for frame in root_frames:
            position_marker_nodes[frame] = {}
            mkr_positions = {}
            mkr_nodes = enabled_marker_nodes[frame]
            for mkr_node in mkr_nodes:
                attr_tx = mkr_node + '.translateX'
                attr_ty = mkr_node + '.translateY'
                pos_x = maya.cmds.getAttr(attr_tx, time=frame)
                pos_y = maya.cmds.getAttr(attr_ty, time=frame)
                mkr_position = (pos_x, pos_y)
                position_marker_nodes[frame][mkr_node] = mkr_position

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
            score = _calculate_marker_frame_score(
                cam, mkr_nodes, frame, position_marker_nodes
            )
            print('frame:', frame, 'score:', score)
            expected_value = expected_values.get(frame)
            assert expected_value is not None
            assert expected_value == score

        e = time.time()
        print('total time:', e - s)


if __name__ == '__main__':
    prog = unittest.main()
