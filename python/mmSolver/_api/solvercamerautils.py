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
The camera solver - allows solving static and animated attributes.

The way an incremental solver should work is by starting with 2 root
frames and then incrementally adding frames. Each additional frame
must be adding attributes to solve and then locking them. Do not allow
re-solving attributes that have been solved before.

TODO: We may also try an approach such as:

1a) Start by calculating a relative camera pose from 2 root frames.

1b) Triangulate all bundles that are shared between both root frames.

2a) Find all camera frames that share at least 3 bundles that were
    correctly triangulated.

2b) Use PnP algorithm to estimate camera poses.

2c) Run bundle-adjustment with all cameras and frames.

3a) Find all camera frames that are not calculated.

3b) Use camera relative pose estimation (using known 3D points) to add
    a new camera frame.

3) Repeat step 2 to 3, until all frames are estimated.

4) Run bundle-adjustment with all cameras and frames.

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import math
import collections
# import pprint

import maya.cmds
import maya.api.OpenMaya as OpenMaya2

import mmSolver.logger

import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.animcurve as animcurve_utils
import mmSolver.utils.transform as tfm_utils
import mmSolver.utils.node as node_utils
import mmSolver._api.constant as const
import mmSolver._api.marker as marker
import mmSolver._api.bundle as bundle
import mmSolver._api.camera as camera
import mmSolver._api.triangulatebundle as triangulatebundle
import mmSolver._api.solveraffects as solveraffects


LOG = mmSolver.logger.get_logger()
TRANSLATE_ATTRS = ['tx', 'ty', 'tz']
MIN_NUM_ITERATIONS = 3
BUNDLE_VALUE_MIN = -1e5
BUNDLE_VALUE_MAX = 1e5


def _calculate_marker_frame_score(mkr_nodes, frame, position_marker_nodes):
    """
    Calculate the score of the frame.

    Uses the paper "Structure-from-Motion Revisited", by Johannes
    L. Schonberger, Jan-Michael Frahm, published in 2016, section
    "4.2. Next Best View Selection".
    """
    score = 0

    # This algorithm tries to score how well distributed a set of
    # points between -0.5 and 0.5. Point distributions that are more
    # uniform and cover the full frame lead to a higher score.
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
    # score" (calculated above), then a more uniformly distributed
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
    mkr_list, frames, enabled_marker_nodes, position_marker_nodes
):
    score_max = 0
    frame_max = None
    mkr_nodes_max = set()
    for frame in frames:
        score = _calculate_marker_frame_score(mkr_list, frame, position_marker_nodes)
        if score >= score_max:
            score_max = score
            frame_max = frame
            mkr_nodes = enabled_marker_nodes[frame]
            assert isinstance(mkr_nodes, set)
            mkr_nodes_max = mkr_nodes
    LOG.debug('frame_max: %s score_max: %s', frame_max, score_max)
    return frame_max, mkr_nodes_max


def _compute_connected_frame_scores(
    root_frame_a,
    possible_frames,
    enabled_marker_nodes,
    position_marker_nodes,
):
    mkr_nodes_a = enabled_marker_nodes[root_frame_a]
    assert isinstance(mkr_nodes_a, set)

    # TODO: This is a hard-coded logic, so we do not select another
    # frame that is closer than max_frame_distance away from the
    # current root_frame_a.
    #
    # If the future we should use more sophisticated logic to avoid
    # picking the frames closest, such as using homography similarity.
    max_frame_distance = 5

    scores = []
    for frame in possible_frames:
        mkr_nodes_b = enabled_marker_nodes[frame]
        assert isinstance(mkr_nodes_b, set)

        distance = abs(root_frame_a - frame)
        if distance < max_frame_distance:
            continue

        score = 0
        mkr_nodes = mkr_nodes_a & mkr_nodes_b
        if len(mkr_nodes) < 6:
            # Not enough points, we need at least 6 points to solve
            # two frames of a camera pose and bundles.
            pass
        else:
            score = _calculate_marker_frame_score(
                mkr_nodes, frame, position_marker_nodes
            )
        scores.append(score)
    return scores


def _bundle_node_is_solved_well(bnd_node, value_min, value_max):
    assert isinstance(value_min, float)
    assert isinstance(value_max, float)
    tx = maya.cmds.getAttr(bnd_node + '.translateX')
    ty = maya.cmds.getAttr(bnd_node + '.translateY')
    tz = maya.cmds.getAttr(bnd_node + '.translateZ')
    bnd_is_good = all(
        [
            tx > BUNDLE_VALUE_MIN,
            ty > BUNDLE_VALUE_MIN,
            tz > BUNDLE_VALUE_MIN,
            tx < BUNDLE_VALUE_MAX,
            ty < BUNDLE_VALUE_MAX,
            tz < BUNDLE_VALUE_MAX,
            tx != 0.0 and ty != 0.0 and tz != 0.0,
        ]
    )
    return bnd_is_good


def _filter_badly_solved_markers(mkr_nodes, value_min, value_max):
    assert isinstance(mkr_nodes, set)
    assert isinstance(value_min, float)
    assert isinstance(value_max, float)

    good_mkr_nodes = set()
    good_bnd_nodes = set()
    mkr_nodes = list(sorted(mkr_nodes))
    mkr_list = [marker.Marker(node=n) for n in mkr_nodes]
    for mkr, mkr_node in zip(mkr_list, mkr_nodes):
        bnd = mkr.get_bundle()
        assert bnd is not None
        bnd_node = bnd.get_node()

        bnd_is_good = _bundle_node_is_solved_well(bnd_node, value_min, value_max)
        if bnd_is_good:
            good_mkr_nodes.add(mkr_node)
            good_bnd_nodes.add(bnd_node)
        else:
            maya.cmds.setAttr(bnd_node + '.translateX', 0.0)
            maya.cmds.setAttr(bnd_node + '.translateY', 0.0)
            maya.cmds.setAttr(bnd_node + '.translateZ', 0.0)

    return good_mkr_nodes, good_bnd_nodes


def _filter_badly_solved_bundles(mkr_bnd_nodes, value_min, value_max):
    assert isinstance(mkr_bnd_nodes, set)
    assert isinstance(value_min, float)
    assert isinstance(value_max, float)

    good_mkr_nodes = set()
    good_bnd_nodes = set()
    for mkr_node, bnd_node in mkr_bnd_nodes:
        bnd_is_good = _bundle_node_is_solved_well(bnd_node, value_min, value_max)
        if bnd_is_good:
            good_mkr_nodes.add(mkr_node)
            good_bnd_nodes.add(bnd_node)
        else:
            maya.cmds.setAttr(bnd_node + '.translateX', 0.0)
            maya.cmds.setAttr(bnd_node + '.translateY', 0.0)
            maya.cmds.setAttr(bnd_node + '.translateZ', 0.0)

    return good_mkr_nodes, good_bnd_nodes


def _sub_bundle_adjustment(
    col_node,
    cam_tfm,
    cam_shp,
    mkr_nodes,
    cam_shp_node_attrs,
    lens_node_attrs,
    frames,
    known_bnd_nodes=None,
    adjust_camera_translate=None,
    adjust_camera_rotate=None,
    adjust_bundle_positions=None,
    adjust_camera_intrinsics=None,
    adjust_lens_distortion=None,
    iteration_num=None,
    per_frame_solve=None,
    solver_version=None,
    solver_type=None,
    verbose=None,
):
    LOG.debug('_sub_bundle_adjustment')
    assert isinstance(adjust_camera_translate, bool)
    assert isinstance(adjust_camera_rotate, bool)
    assert isinstance(adjust_bundle_positions, bool)
    assert isinstance(adjust_camera_intrinsics, bool)
    assert isinstance(adjust_lens_distortion, bool)

    if known_bnd_nodes is None:
        known_bnd_nodes = set()

    if solver_version is None:
        solver_version = const.SOLVER_CAM_SOLVER_VERSION_DEFAULT_VALUE
    if solver_type is None:
        solver_type = const.SOLVER_CAM_SOLVER_TYPE_DEFAULT_VALUE
    assert isinstance(solver_version, int)
    assert isinstance(solver_type, int)
    assert solver_version in const.SOLVER_VERSION_LIST
    assert solver_type in const.SOLVER_TYPE_LIST

    if verbose is None:
        verbose = False
    assert isinstance(verbose, bool)

    frame_solve_mode = const.FRAME_SOLVE_MODE_ALL_FRAMES_AT_ONCE
    if per_frame_solve is True:
        frame_solve_mode = const.FRAME_SOLVE_MODE_PER_FRAME

    scene_graph_mode = const.SCENE_GRAPH_MODE_MM_SCENE_GRAPH

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

    if adjust_camera_intrinsics is True:
        for node_attr in cam_shp_node_attrs:
            min_value = 2.5
            max_value = 1000.0
            offset_value = None
            scale_value = None
            value = (
                node_attr,
                str(min_value),
                str(max_value),
                str(offset_value),
                str(scale_value),
            )
            node_attrs.append(value)

    if adjust_lens_distortion is True:
        for node_attr in lens_node_attrs:
            min_value = -1.0
            max_value = 1.0
            offset_value = None
            scale_value = None
            value = (
                node_attr,
                str(min_value),
                str(max_value),
                str(offset_value),
                str(scale_value),
            )
            node_attrs.append(value)

    markers = []
    mkr_list = [marker.Marker(node=n) for n in mkr_nodes]
    for mkr in mkr_list:
        bnd = mkr.get_bundle()
        assert bnd is not None
        mkr_node = mkr.get_node()
        bnd_node = bnd.get_node()
        mkr_bnd = (mkr_node, cam_shp, bnd_node)
        markers.append(mkr_bnd)

        if bnd_node in known_bnd_nodes:
            # Known Bundle are not solved, but they are used in the
            # solve.
            continue

        if adjust_bundle_positions is True:
            for attr in TRANSLATE_ATTRS:
                # TODO: Try to limit the values (eg. -1e4 to 1e4) allowed by bundles, so
                # that we do not have near infinite distances which
                # cause instability in the solver.
                min_value = None
                max_value = None
                offset_value = None
                scale_value = None
                solve_node_attr = (
                    '{}.{}'.format(bnd_node, attr),
                    str(min_value),
                    str(max_value),
                    str(offset_value),
                    str(scale_value),
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

    if len(node_attrs) == 0:
        return

    kwargs = {
        'camera': cameras,
        'marker': markers,
        'attr': node_attrs,
        'frame': frames,
    }
    # LOG.debug('mmSolver kwargs: %s', pprint.pformat(kwargs))

    # After each pose is added to the camera solve, we must do a
    # mmSolver refinement with 'MM Scene Graph', solving the
    # camera position, rotation and bundle positions.
    result = None
    if solver_version == const.SOLVER_VERSION_ONE:
        result = maya.cmds.mmSolver(
            solverType=solver_type,
            sceneGraphMode=scene_graph_mode,
            iterations=iteration_num,
            frameSolveMode=frame_solve_mode,
            verbose=verbose,
            **kwargs
        )
        # LOG.debug('mmSolver result: %s', pprint.pformat(result))
        assert result[0] == 'success=1'
    elif solver_version == const.SOLVER_VERSION_TWO:
        log_level = const.LOG_LEVEL_INFO_VALUE
        if verbose is True:
            log_level = const.LOG_LEVEL_DEBUG_VALUE

        result = maya.cmds.mmSolver_v2(
            solverType=solver_type,
            sceneGraphMode=scene_graph_mode,
            iterations=iteration_num,
            frameSolveMode=frame_solve_mode,
            resultsNode=col_node,
            logLevel=log_level,
            **kwargs
        )
        # LOG.debug('mmSolver_v2 result: %s', pprint.pformat(result))
        assert result is True
    else:
        raise NotImplementedError
    return result


def _bundle_adjust(
    col_node,
    cam_tfm,
    cam_shp,
    mkr_nodes,
    cam_shp_node_attrs,
    lens_node_attrs,
    frames,
    adjust_camera_translate=None,
    adjust_camera_rotate=None,
    adjust_bundle_positions=None,
    adjust_camera_intrinsics=None,
    adjust_lens_distortion=None,
    iteration_num=None,
    per_frame_solve=None,
    solver_version=None,
    solver_type=None,
    verbose=None,
):
    LOG.debug('_bundle_adjust')
    LOG.debug('col_node: %r', col_node)
    LOG.debug('cam_tfm: %r', cam_tfm)
    LOG.debug('cam_shp: %r', cam_shp)
    LOG.debug('mkr_nodes: %r', mkr_nodes)
    LOG.debug('cam_shp_node_attrs: %r', cam_shp_node_attrs)
    LOG.debug('lens_node_attrs: %r', lens_node_attrs)
    LOG.debug('frames: %r', frames)

    if adjust_camera_translate is None:
        adjust_camera_translate = False
    if adjust_camera_rotate is None:
        adjust_camera_rotate = False
    if adjust_bundle_positions is None:
        adjust_bundle_positions = False
    if adjust_camera_intrinsics is None:
        adjust_camera_intrinsics = False
    if adjust_lens_distortion is None:
        adjust_lens_distortion = False
    if iteration_num is None:
        iteration_num = 100
    if per_frame_solve is None:
        per_frame_solve = False
    if solver_version is None:
        solver_version = const.SOLVER_CAM_SOLVER_VERSION_DEFAULT_VALUE
    if solver_type is None:
        solver_type = const.SOLVER_CAM_SOLVER_TYPE_DEFAULT_VALUE
    if verbose is None:
        verbose = False
    assert isinstance(adjust_camera_translate, bool)

    assert isinstance(adjust_camera_rotate, bool)
    assert isinstance(adjust_bundle_positions, bool)
    assert isinstance(adjust_camera_intrinsics, bool)
    assert isinstance(adjust_lens_distortion, bool)
    assert isinstance(solver_version, int)
    assert isinstance(solver_type, int)
    assert isinstance(verbose, bool)
    assert len(mkr_nodes) > 0
    assert solver_version in const.SOLVER_VERSION_LIST
    assert solver_type in const.SOLVER_TYPE_LIST

    result = None
    if adjust_lens_distortion is False:
        result = _sub_bundle_adjustment(
            col_node,
            cam_tfm,
            cam_shp,
            mkr_nodes,
            cam_shp_node_attrs,
            lens_node_attrs,
            frames,
            adjust_camera_translate=adjust_camera_translate,
            adjust_camera_rotate=adjust_camera_rotate,
            adjust_bundle_positions=adjust_bundle_positions,
            adjust_camera_intrinsics=adjust_camera_intrinsics,
            adjust_lens_distortion=adjust_lens_distortion,
            iteration_num=iteration_num,
            per_frame_solve=per_frame_solve,
            solver_version=solver_version,
            solver_type=solver_type,
            verbose=verbose,
        )

    else:
        iteration_num_a = max(MIN_NUM_ITERATIONS, iteration_num * 0.2)
        iteration_num_b = max(MIN_NUM_ITERATIONS, iteration_num * 0.8)
        iteration_num_c = max(MIN_NUM_ITERATIONS, iteration_num * 0.0)
        if adjust_camera_intrinsics or adjust_lens_distortion:
            iteration_num_a = max(MIN_NUM_ITERATIONS, iteration_num * 0.1)
            iteration_num_b = max(MIN_NUM_ITERATIONS, iteration_num * 0.4)
            iteration_num_c = max(MIN_NUM_ITERATIONS, iteration_num * 0.5)

        # Solve camera transform and bundle positions
        _sub_bundle_adjustment(
            col_node,
            cam_tfm,
            cam_shp,
            mkr_nodes,
            cam_shp_node_attrs,
            lens_node_attrs,
            frames,
            adjust_camera_translate=False,
            adjust_camera_rotate=False,
            adjust_bundle_positions=adjust_bundle_positions,
            adjust_camera_intrinsics=False,
            adjust_lens_distortion=False,
            iteration_num=iteration_num_a,
            per_frame_solve=per_frame_solve,
            solver_version=solver_version,
            solver_type=solver_type,
        )

        # Solve camera transform and bundle positions
        _sub_bundle_adjustment(
            col_node,
            cam_tfm,
            cam_shp,
            mkr_nodes,
            cam_shp_node_attrs,
            lens_node_attrs,
            frames,
            adjust_camera_translate=adjust_camera_translate,
            adjust_camera_rotate=adjust_camera_rotate,
            adjust_bundle_positions=adjust_bundle_positions,
            adjust_camera_intrinsics=False,
            adjust_lens_distortion=False,
            iteration_num=iteration_num_b,
            per_frame_solve=per_frame_solve,
            solver_version=solver_version,
            solver_type=solver_type,
        )

        # Solve everything, including camera focal length and lens distortion.
        if adjust_camera_intrinsics or adjust_lens_distortion:
            _sub_bundle_adjustment(
                col_node,
                cam_tfm,
                cam_shp,
                mkr_nodes,
                cam_shp_node_attrs,
                lens_node_attrs,
                frames,
                adjust_camera_translate=adjust_camera_translate,
                adjust_camera_rotate=adjust_camera_rotate,
                adjust_bundle_positions=adjust_bundle_positions,
                adjust_camera_intrinsics=adjust_camera_intrinsics,
                adjust_lens_distortion=adjust_lens_distortion,
                iteration_num=iteration_num_c,
                per_frame_solve=per_frame_solve,
                solver_version=solver_version,
                solver_type=solver_type,
            )

    return result


def _solve_relative_poses(
    col_node,
    cam_tfm,
    cam_shp,
    mkr_nodes_a,
    cam_shp_node_attrs,
    lens_node_attrs,
    root_frame_a,
    possible_frames,
    solved_frames,
    accumulated_mkr_nodes,
    accumulated_bnd_nodes,
    enabled_marker_nodes,
    adjust_every_n_poses,
    verbose
):
    assert isinstance(solved_frames, set)
    assert isinstance(accumulated_mkr_nodes, set)
    assert isinstance(accumulated_bnd_nodes, set)
    assert isinstance(verbose, bool)
    failed_frames = set()

    known_bnd_nodes = set()

    iteration = 0
    tmp_possible_frames = list(possible_frames)
    while len(tmp_possible_frames) > 0:
        iteration += 1

        if root_frame_a in tmp_possible_frames:
            tmp_possible_frames.remove(root_frame_a)

        # The closest frame number to the root frame, so we move
        # incrementally outwards from the root frame.
        possible_frame = min(tmp_possible_frames, key=lambda x: abs(x - root_frame_a))
        tmp_possible_frames.remove(possible_frame)

        if possible_frame in solved_frames:
            # Already solved, no need to solve it again.
            continue
        if possible_frame in failed_frames:
            # Already failed to solve, no need to try again.
            continue

        LOG.debug('iteration: %s', iteration)
        LOG.debug('possible_frame: %s', possible_frame)

        mkr_nodes_b = enabled_marker_nodes[possible_frame]
        mkr_nodes = set(mkr_nodes_a) & set(mkr_nodes_b)
        common_mkr_list = [marker.Marker(node=n) for n in mkr_nodes]

        shared_bnd_nodes = set()
        mkr_bnd_nodes = set()
        new_mkr_bnd_list = []
        for mkr in common_mkr_list:
            bnd = mkr.get_bundle()
            if bnd is None:
                bnd = bundle.Bundle().create_node()
                mkr.set_bundle(bnd)
            mkr_node = mkr.get_node()
            bnd_node = bnd.get_node()

            shared_bnd_nodes.add(bnd_node)

            mkr_bnd = (mkr_node, mkr_node, bnd_node)
            new_mkr_bnd_list.append(mkr_bnd)

            mkr_bnd = (mkr_node, bnd_node)
            mkr_bnd_nodes.add(mkr_bnd)

        # NaN values are a way to signal the Bundle position is
        # unknown, where as non-NaN values are known.
        known_mkr_bnd_nodes = set()
        LOG.debug('len(known_bnd_nodes): %s', len(known_bnd_nodes))
        known_bnd_pos_list = [(float('nan'), float('nan'), float('nan'))] * (
            len(new_mkr_bnd_list)
        )
        known_bnd_count = 0
        for i, (mkr_node_a, mkr_node_b, bnd_node) in enumerate(new_mkr_bnd_list):
            if bnd_node not in known_bnd_nodes:
                continue
            known_bnd_count += 1

            mkr_bnd = (mkr_node_a, bnd_node)
            known_mkr_bnd_nodes.add(mkr_bnd)

            bnd_pos_x = maya.cmds.getAttr(bnd_node + '.translateX')
            bnd_pos_y = maya.cmds.getAttr(bnd_node + '.translateY')
            bnd_pos_z = maya.cmds.getAttr(bnd_node + '.translateZ')
            known_bnd_pos_list[i] = (bnd_pos_x, bnd_pos_y, bnd_pos_z)
        LOG.debug('known_bnd_count: %s', known_bnd_count)

        # Camera relative pose.
        kwargs = {
            'frameA': root_frame_a,
            'frameB': possible_frame,
            'cameraA': cam_tfm,
            'cameraB': cam_tfm,
            'markerBundle': new_mkr_bnd_list,
            'bundlePosition': known_bnd_pos_list,
            'useCameraTransform': True,
            'setValues': True,
        }
        # LOG.debug('mmCameraRelativePose kwargs: %s', pprint.pformat(kwargs))
        result = maya.cmds.mmCameraRelativePose(**kwargs)
        # LOG.debug('mmCameraRelativePose result: %s', pprint.pformat(result))
        if result is None:
            LOG.debug('Failed Camera Pose: %s to %s', root_frame_a, possible_frame)

            # If there are at least 3 or more known bundle positions,
            # we can use a Perspective-N-Points (PnP) algorithm to
            # compute the position of the camera pose, without using
            # camera relative pose estimation.

            if known_bnd_count >= 3:
                # PnP camera pose.
                kwargs = {
                    'setValues': True,
                    'frame': possible_frame,
                    'camera': cam_tfm,
                    'marker': list(sorted(known_mkr_bnd_nodes)),
                }
                # LOG.debug('mmCameraPoseFromPoints kwargs: %s', pprint.pformat(kwargs))
                result = maya.cmds.mmCameraPoseFromPoints(**kwargs)
                # LOG.debug('mmCameraPoseFromPoints result: %s', pprint.pformat(result))
                if result is None:
                    LOG.debug(
                        'Failed Camera Pose (from existing 3D Points): %s',
                        possible_frame,
                    )
                    # If this fails, should we try the camera relative
                    # pose as well?
                    failed_frames.add(possible_frame)
                    continue
            else:
                failed_frames.add(possible_frame)
                continue

        mkr_nodes, bnd_nodes = _filter_badly_solved_bundles(
            mkr_bnd_nodes, BUNDLE_VALUE_MIN, BUNDLE_VALUE_MAX
        )

        LOG.debug('Solved Camera Pose: %s to %s', root_frame_a, possible_frame)
        solved_frames.add(root_frame_a)
        solved_frames.add(possible_frame)
        accumulated_mkr_nodes = accumulated_mkr_nodes | mkr_nodes
        accumulated_bnd_nodes = accumulated_bnd_nodes | bnd_nodes
        known_bnd_nodes = known_bnd_nodes | bnd_nodes

        # Refine the solve.
        solved_frames_count = len(solved_frames)
        if (solved_frames_count % adjust_every_n_poses) == 0:
            animcurve_utils.euler_filter_plug(cam_tfm, 'rotateX')
            animcurve_utils.euler_filter_plug(cam_tfm, 'rotateY')
            animcurve_utils.euler_filter_plug(cam_tfm, 'rotateZ')

            frames = list(sorted(solved_frames))
            _sub_bundle_adjustment(
                col_node,
                cam_tfm,
                cam_shp,
                accumulated_mkr_nodes,
                cam_shp_node_attrs,
                lens_node_attrs,
                frames,
                known_bnd_nodes=known_bnd_nodes,
                adjust_camera_translate=True,
                adjust_camera_rotate=True,
                adjust_bundle_positions=True,
                adjust_camera_intrinsics=True,
                adjust_lens_distortion=False,
                iteration_num=25,
                verbose=verbose,
            )
            accumulated_mkr_nodes, accumulated_bnd_nodes = _filter_badly_solved_markers(
                accumulated_mkr_nodes, BUNDLE_VALUE_MIN, BUNDLE_VALUE_MAX
            )

    accumulated_mkr_nodes, accumulated_bnd_nodes = _filter_badly_solved_markers(
        accumulated_mkr_nodes, BUNDLE_VALUE_MIN, BUNDLE_VALUE_MAX
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

        enabled_frames = marker_nodes_enabled[mkr_node]
        assert isinstance(enabled_frames, set)
        overlapping_frames = solver_frames & enabled_frames
        if len(overlapping_frames) < 2:
            continue

        if bnd_node not in bnd_nodes:
            ok = triangulatebundle.triangulate_bundle(
                bnd, max_distance=1e6, direction_tolerance=1.0
            )
            is_bnd_good = _bundle_node_is_solved_well(
                bnd_node, BUNDLE_VALUE_MIN, BUNDLE_VALUE_MAX
            )
            if ok is True and is_bnd_good is True:
                LOG.debug('Triangulated Bundle: %s', bnd_node)
                mkr_nodes.add(mkr_node)
                bnd_nodes.add(bnd_node)
                triangulated_count += 1
            else:
                LOG.warn('Failed to triangulated Bundle: %s', bnd_node)
                # TODO: Add attribute to define if the bundle has been
                # initialised or is valid?
                maya.cmds.setAttr(bnd_node + '.translateX', 0.0)
                maya.cmds.setAttr(bnd_node + '.translateY', 0.0)
                maya.cmds.setAttr(bnd_node + '.translateZ', 0.0)
    return triangulated_count, mkr_nodes, bnd_nodes


def _set_camera_origin_frame(
    cam_tfm,
    bnd_nodes,
    origin_frame,
    start_frame,
    end_frame,
    scene_scale,
):
    # Camera matrix for use as 'origin frame' offset.
    origin_ctx = tfm_utils.create_dg_context_apitwo(origin_frame)
    node_attr = '{}.matrix'.format(cam_tfm)
    cam_matrix_plug = node_utils.get_as_plug_apitwo(node_attr)
    origin_matrix = tfm_utils.get_matrix_from_plug_apitwo(cam_matrix_plug, origin_ctx)
    origin_matrix_inverse = origin_matrix.inverse()

    # Use the same rotation order that the camera already has.
    rotate_order = maya.cmds.xform(cam_tfm, query=True, rotateOrder=True)
    rotate_order = tfm_utils.ROTATE_ORDER_STR_TO_APITWO_CONSTANT[rotate_order]

    previous_rotation = None
    cam_tfm_values = []
    frames = list(range(start_frame, end_frame + 1))
    for frame in frames:
        ctx = tfm_utils.create_dg_context_apitwo(frame)
        matrix = tfm_utils.get_matrix_from_plug_apitwo(cam_matrix_plug, ctx)
        matrix = matrix * origin_matrix_inverse
        tfm_matrix = OpenMaya2.MTransformationMatrix(matrix)
        tfm_matrix.reorderRotation(rotate_order)
        tfm_values = tfm_utils.decompose_matrix(tfm_matrix, previous_rotation)
        cam_tfm_values.append(tfm_values)

        rx = tfm_values[3]
        ry = tfm_values[4]
        rz = tfm_values[5]
        previous_rotation = (rx, ry, rz)

    # Calculate bounding box for camera positions.
    min_x = 1e9
    min_y = 1e9
    min_z = 1e9
    max_x = -1e9
    max_y = -1e9
    max_z = -1e9
    for tfm_values in cam_tfm_values:
        tx = tfm_values[0]
        ty = tfm_values[1]
        tz = tfm_values[2]
        if tx < min_x:
            min_x = tx
        if tx > max_x:
            max_x = tx
        if ty < min_y:
            min_y = ty
        if ty > max_y:
            max_y = ty
        if tz < min_z:
            min_z = tz
        if tz > max_z:
            max_z = tz
    dx = min_x - max_x
    dy = min_y - max_y
    dz = min_z - max_z
    path_size = math.sqrt(dx * dx + dy * dy + dz * dz)

    for frame, tfm_values in zip(frames, cam_tfm_values):
        tx = (tfm_values[0] / path_size) * scene_scale
        ty = (tfm_values[1] / path_size) * scene_scale
        tz = (tfm_values[2] / path_size) * scene_scale
        maya.cmds.setKeyframe(cam_tfm, attribute='translateX', time=frame, value=tx)
        maya.cmds.setKeyframe(cam_tfm, attribute='translateY', time=frame, value=ty)
        maya.cmds.setKeyframe(cam_tfm, attribute='translateZ', time=frame, value=tz)

        rx = tfm_values[3]
        ry = tfm_values[4]
        rz = tfm_values[5]
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateX', time=frame, value=rx)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateY', time=frame, value=ry)
        maya.cmds.setKeyframe(cam_tfm, attribute='rotateZ', time=frame, value=rz)

    for bnd_node in bnd_nodes:
        tx_attr = '{}.translateX'.format(bnd_node)
        ty_attr = '{}.translateY'.format(bnd_node)
        tz_attr = '{}.translateZ'.format(bnd_node)
        tx = maya.cmds.getAttr(tx_attr)
        ty = maya.cmds.getAttr(ty_attr)
        tz = maya.cmds.getAttr(tz_attr)
        point = OpenMaya2.MPoint(tx, ty, tz) * origin_matrix_inverse
        maya.cmds.setAttr(tx_attr, (point.x / path_size) * scene_scale)
        maya.cmds.setAttr(ty_attr, (point.y / path_size) * scene_scale)
        maya.cmds.setAttr(tz_attr, (point.z / path_size) * scene_scale)
    return


def _remove_keyframes_outside_range(cam_tfm, cam_shp, solved_frames):
    assert isinstance(solved_frames, set)
    key_times = []

    attrs = [
        'translateX',
        'translateY',
        'translateZ',
        'rotateX',
        'rotateY',
        'rotateZ',
        'scaleX',
        'scaleY',
        'scaleZ',
    ]
    for attr in attrs:
        node_attr = '{}.{}'.format(cam_tfm, attr)
        key_count = maya.cmds.keyframe(node_attr, query=True, keyframeCount=True)
        if key_count > 0:
            key_times += maya.cmds.keyframe(node_attr, query=True, timeChange=True)

    node_attr = '{}.focalLength'.format(cam_shp)
    key_count = maya.cmds.keyframe(node_attr, query=True, keyframeCount=True)
    if key_count > 0:
        key_times += maya.cmds.keyframe(node_attr, query=True, timeChange=True)

    outer_frames = set(key_times) - solved_frames
    for frame in outer_frames:
        maya.cmds.cutKey([cam_tfm, cam_shp], time=(frame,))
    return


def _cache_enabled_marker_nodes(mkr_list, root_frames):
    # Create cache for re-use in _compute_enabled_marker_nodes().
    enabled_marker_nodes = {}
    for frame in root_frames:
        mkr_nodes = _compute_enabled_marker_nodes(mkr_list, frame)
        enabled_marker_nodes[frame] = mkr_nodes
    return enabled_marker_nodes


def _cache_position_marker_nodes(root_frames, enabled_marker_nodes):
    # Create cache for re-use in _marker_maximum_frame_score().
    position_marker_nodes = {}
    for frame in root_frames:
        position_marker_nodes[frame] = {}
        mkr_nodes = enabled_marker_nodes[frame]
        for mkr_node in mkr_nodes:
            attr_tx = mkr_node + '.translateX'
            attr_ty = mkr_node + '.translateY'
            pos_x = maya.cmds.getAttr(attr_tx, time=frame)
            pos_y = maya.cmds.getAttr(attr_ty, time=frame)
            mkr_position = (pos_x, pos_y)
            position_marker_nodes[frame][mkr_node] = mkr_position
    return position_marker_nodes


def _cache_marker_nodes_enabled(mkr_list, start_frame, end_frame):
    marker_nodes_enabled = {}
    for mkr in mkr_list:
        mkr_node = mkr.get_node()
        enabled_frames = mkr.get_enabled_frames(
            frame_range_start=start_frame, frame_range_end=end_frame
        )
        marker_nodes_enabled[mkr_node] = set(enabled_frames)
    return marker_nodes_enabled


def _cache_connected_frame_statistics(
    root_frames, enabled_marker_nodes, position_marker_nodes
):
    """
    Pre-compute the connected frame statistics, to help guess the
    best frames for solving camera pairs.
    """
    frame_scores_map = {}
    frame_scores_stats_map = {}
    frame_best_frame_map = {}
    for frame in root_frames:
        scores = _compute_connected_frame_scores(
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

    return frame_scores_map, frame_scores_stats_map, frame_best_frame_map


def _precompute_values(mkr_list, root_frames, start_frame, end_frame):
    LOG.debug('_precompute_values.')
    # LOG.debug('mkr_list: %s', mkr_list)

    enabled_marker_nodes = _cache_enabled_marker_nodes(mkr_list, root_frames)

    position_marker_nodes = _cache_position_marker_nodes(
        root_frames, enabled_marker_nodes
    )

    marker_nodes_enabled = _cache_marker_nodes_enabled(mkr_list, start_frame, end_frame)

    (
        frame_scores_map,
        frame_scores_stats_map,
        frame_best_frame_map,
    ) = _cache_connected_frame_statistics(
        root_frames, enabled_marker_nodes, position_marker_nodes
    )

    return (
        enabled_marker_nodes,
        position_marker_nodes,
        marker_nodes_enabled,
        frame_scores_map,
        frame_scores_stats_map,
        frame_best_frame_map,
    )


def _runSolverAffects(
    col_node,
    cam_tfm,
    cam_shp,
    mkr_list,
    cam_shp_node_attrs,
    lens_node_attrs,
    start_frame,
    end_frame,
):
    all_frames = list(range(start_frame, end_frame + 1))
    cameras = ((cam_tfm, cam_shp),)

    node_attrs = []
    node_attrs.append((cam_tfm + '.tx', 'None', 'None', 'None', 'None'))
    node_attrs.append((cam_tfm + '.ty', 'None', 'None', 'None', 'None'))
    node_attrs.append((cam_tfm + '.tz', 'None', 'None', 'None', 'None'))
    node_attrs.append((cam_tfm + '.rx', 'None', 'None', 'None', 'None'))
    node_attrs.append((cam_tfm + '.ry', 'None', 'None', 'None', 'None'))
    node_attrs.append((cam_tfm + '.rz', 'None', 'None', 'None', 'None'))

    for node_attr in cam_shp_node_attrs:
        min_value = 2.5
        max_value = 1000.0
        offset_value = None
        scale_value = None
        value = (
            node_attr,
            str(min_value),
            str(max_value),
            str(offset_value),
            str(scale_value),
        )
        node_attrs.append(value)

    for node_attr in lens_node_attrs:
        min_value = -1.0
        max_value = 1.0
        offset_value = None
        scale_value = None
        value = (
            node_attr,
            str(min_value),
            str(max_value),
            str(offset_value),
            str(scale_value),
        )
        node_attrs.append(value)

    markers = []
    mkr_nodes = []
    for mkr in mkr_list:
        bnd = mkr.get_bundle()
        assert bnd is not None
        mkr_node = mkr.get_node()
        bnd_node = bnd.get_node()
        mkr_bnd = (mkr_node, cam_shp, bnd_node)
        markers.append(mkr_bnd)
        mkr_nodes.append(mkr_node)

        for attr in TRANSLATE_ATTRS:
            min_value = None
            max_value = None
            offset_value = None
            scale_value = None
            solve_node_attr = (
                '{}.{}'.format(bnd_node, attr),
                str(min_value),
                str(max_value),
                str(offset_value),
                str(scale_value),
            )
            node_attrs.append(solve_node_attr)

    node_attr_plugs = [x[0] for x in node_attrs]
    solveraffects.reset_marker_used_hints(mkr_nodes)
    solveraffects.reset_attr_used_hints(col_node, node_attr_plugs)

    # LOG.debug('maya.cmds.mmSolverAffects camera: %s', pprint.pformat(cameras))
    # LOG.debug('maya.cmds.mmSolverAffects marker: %s', pprint.pformat(markers))
    # LOG.debug('maya.cmds.mmSolverAffects attr: %s', pprint.pformat(node_attrs))
    # LOG.debug('maya.cmds.mmSolverAffects frame: %s', pprint.pformat(all_frames))

    affects_mode = 'addAttrsToMarkers'
    result = maya.cmds.mmSolverAffects(
        mode=affects_mode,
        graphMode=const.AFFECTS_GRAPH_MODE_OBJECT,
        camera=cameras,
        marker=markers,
        attr=node_attrs,
        frame=all_frames,
    )
    return result


# TODO: Make arguments keywords arguments. This will make things
# easier to understand for calling code.
def camera_solve(
    col_node,
    cam_tfm,
    cam_shp,
    mkr_nodes,
    cam_shp_node_attrs,
    lens_node_attrs,
    root_frames,
    start_frame,
    end_frame,
    origin_frame,
    scene_scale,
    bundle_iter_num,
    root_iter_num,
    anim_iter_num,
    adjust_every_n_poses,
    solver_version,
    solver_type,
    verbose,
):
    assert isinstance(col_node, pycompat.TEXT_TYPE)
    assert isinstance(cam_tfm, pycompat.TEXT_TYPE)
    assert isinstance(cam_shp, pycompat.TEXT_TYPE)
    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)
    assert isinstance(origin_frame, int)
    assert isinstance(scene_scale, float)
    assert isinstance(bundle_iter_num, int)
    assert isinstance(root_iter_num, int)
    assert isinstance(anim_iter_num, int)
    assert isinstance(adjust_every_n_poses, int)
    assert isinstance(cam_shp_node_attrs, list)
    assert isinstance(lens_node_attrs, list)
    assert isinstance(solver_version, int)
    assert isinstance(solver_type, int)
    assert isinstance(verbose, bool)
    assert len(mkr_nodes) > 0
    assert solver_version in const.SOLVER_VERSION_LIST
    assert solver_type in const.SOLVER_TYPE_LIST

    # TODO: Categorize the marker/bundle nodes that are given to this
    # function and output the categories. This will allow the caller
    # to organise the nodes for the user to see diagnostic
    # information.

    cam = camera.Camera(shape=cam_shp)
    mkr_list = [marker.Marker(node=x) for x in mkr_nodes]

    LOG.debug('col_node: %s', col_node)
    LOG.debug('cam: %s', cam)
    LOG.debug('mkr_list: %s', mkr_list)
    LOG.debug('cam_shp_node_attrs: %s', cam_shp_node_attrs)
    LOG.debug('lens_node_attrs: %s', lens_node_attrs)
    LOG.debug('start_frame: %s', start_frame)
    LOG.debug('end_frame: %s', end_frame)
    LOG.debug('root_frame count: %s', len(root_frames))
    LOG.debug('root_frames: %s', root_frames)
    LOG.debug('origin_frame: %s', origin_frame)
    LOG.debug('scene_scale: %s', scene_scale)
    LOG.debug('root_iter_num: %s', root_iter_num)
    LOG.debug('bundle_iter_num: %s', bundle_iter_num)
    LOG.debug('anim_iter_num: %s', anim_iter_num)
    LOG.debug('solver_version: %s', solver_version)
    LOG.debug('solver_type: %s', solver_type)
    LOG.debug('verbose: %s', verbose)

    (
        enabled_marker_nodes,
        position_marker_nodes,
        marker_nodes_enabled,
        frame_scores_map,
        frame_scores_stats_map,
        frame_best_frame_map,
    ) = _precompute_values(mkr_list, root_frames, start_frame, end_frame)

    mkr_list = [marker.Marker(node=n) for n in mkr_nodes]

    affectsResult = _runSolverAffects(
        col_node,
        cam_tfm,
        cam_shp,
        mkr_list,
        cam_shp_node_attrs,
        lens_node_attrs,
        start_frame,
        end_frame,
    )
    # LOG.debug('affectsResult: %s', pprint.pformat(affectsResult))

    # Find the frame with the best connectivity to all other root
    # frames. This is not the frame that gives the most solved frames,
    # but rather the highest quality solve overall.
    #
    # For simple camera solves with plenty of 2D marker data the best
    # frame should have connectivity to all other root frames.
    best_frame = None
    best_score = -1
    for frame in reversed(root_frames):
        frame_score_stats = frame_scores_stats_map[frame]
        avg_score, max_score = frame_score_stats
        if avg_score >= best_score:
            best_score = avg_score
            best_frame = frame

    LOG.debug('best_frame: %s', best_frame)
    LOG.debug('best_score: %s', best_score)

    frame_stack = list(root_frames)
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
        LOG.debug('root_frame_a: %s', root_frame_a)

        # Only solves the frame that is possible to be solved from the root frame.
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
            col_node,
            cam_tfm,
            cam_shp,
            mkr_nodes_a,
            cam_shp_node_attrs,
            lens_node_attrs,
            root_frame_a,
            relative_pose_frames,
            solved_frames,
            accumulated_mkr_nodes,
            accumulated_bnd_nodes,
            enabled_marker_nodes,
            adjust_every_n_poses,
            verbose,
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

    accumulated_mkr_nodes, accumulated_bnd_nodes = _filter_badly_solved_markers(
        accumulated_mkr_nodes, BUNDLE_VALUE_MIN, BUNDLE_VALUE_MAX
    )

    _remove_keyframes_outside_range(cam_tfm, cam_shp, solved_frames)

    if len(solved_frames) > 2:
        # Only bundle adjust after the first pose to ensure we have
        # enough data to solve the bundle adjustment.

        # Refine the solve.
        LOG.debug("Refine the solve; solved_frames=%r", solved_frames)
        frames = list(sorted(solved_frames))
        for mkr_node in accumulated_mkr_nodes:
            enabled_frames = marker_nodes_enabled[mkr_node]
            assert isinstance(enabled_frames, set)
            overlapping_frames = set(frames) & enabled_frames
            if len(overlapping_frames) < 2:
                continue
            overlapping_frames = list(sorted(overlapping_frames))

            LOG.debug("Refine the solve; mkr_node=%r", mkr_node)
            _bundle_adjust(
                col_node,
                cam_tfm,
                cam_shp,
                [mkr_node],
                cam_shp_node_attrs,
                lens_node_attrs,
                overlapping_frames,
                adjust_camera_translate=False,
                adjust_camera_rotate=False,
                adjust_bundle_positions=True,
                adjust_camera_intrinsics=False,
                adjust_lens_distortion=False,
                iteration_num=5,
                per_frame_solve=False,
                solver_version=solver_version,
                solver_type=solver_type,
            )

        adjust_mkr_nodes = set()
        for mkr_node in accumulated_mkr_nodes:
            enabled_frames = marker_nodes_enabled[mkr_node]
            assert isinstance(enabled_frames, set)
            overlapping_frames = set(frames) & set(enabled_frames)
            if len(overlapping_frames) > 2:
                adjust_mkr_nodes.add(mkr_node)
        adjust_mkr_nodes = list(sorted(adjust_mkr_nodes))

        LOG.debug("Refine the solve; adjust_mkr_nodes=%r", adjust_mkr_nodes)
        _bundle_adjust(
            col_node,
            cam_tfm,
            cam_shp,
            adjust_mkr_nodes,
            cam_shp_node_attrs,
            lens_node_attrs,
            frames,
            adjust_camera_translate=True,
            adjust_camera_rotate=True,
            adjust_bundle_positions=True,
            adjust_camera_intrinsics=True,
            adjust_lens_distortion=True,
            iteration_num=100,
            per_frame_solve=False,
            solver_version=solver_version,
            solver_type=solver_type,
        )

    # Triangulate Bundles that were not solved with camera relative
    # poses.
    LOG.debug("Triangulate Bundles; accumulated_mkr_nodes=%r", accumulated_mkr_nodes)
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
        LOG.debug("Refine the solve; solved_frames=%r", solved_frames)
        frames = list(sorted(solved_frames))
        for mkr_node in accumulated_mkr_nodes:
            mkr = marker.Marker(node=mkr_node)
            start_solved_frame = min(frames)
            end_solved_frame = max(frames)
            enabled_frames = mkr.get_enabled_frames(
                frame_range_start=start_solved_frame, frame_range_end=end_solved_frame
            )
            overlapping_frames = set(frames) & set(enabled_frames)
            if len(overlapping_frames) < 2:
                continue
            overlapping_frames = list(sorted(overlapping_frames))

            LOG.debug("Refine the solve; mkr_node=%r", mkr_node)
            _bundle_adjust(
                col_node,
                cam_tfm,
                cam_shp,
                [mkr_node],
                cam_shp_node_attrs,
                lens_node_attrs,
                overlapping_frames,
                adjust_camera_translate=False,
                adjust_camera_rotate=False,
                adjust_bundle_positions=True,
                adjust_camera_intrinsics=False,
                adjust_lens_distortion=False,
                per_frame_solve=False,
                iteration_num=5,
                solver_version=solver_version,
                solver_type=solver_type,
            )

        adjust_mkr_nodes = set()
        for mkr_node in accumulated_mkr_nodes:
            enabled_frames = marker_nodes_enabled[mkr_node]
            assert isinstance(enabled_frames, set)
            overlapping_frames = set(frames) & set(enabled_frames)
            if len(overlapping_frames) > 2:
                adjust_mkr_nodes.add(mkr_node)
        adjust_mkr_nodes = list(sorted(adjust_mkr_nodes))

        LOG.debug("Refine the solve; adjust_mkr_nodes=%r", adjust_mkr_nodes)
        _bundle_adjust(
            col_node,
            cam_tfm,
            cam_shp,
            adjust_mkr_nodes,
            cam_shp_node_attrs,
            lens_node_attrs,
            frames,
            adjust_camera_translate=True,
            adjust_camera_rotate=True,
            adjust_bundle_positions=True,
            adjust_camera_intrinsics=True,
            adjust_lens_distortion=True,
            iteration_num=100,
            per_frame_solve=False,
            solver_version=solver_version,
            solver_type=solver_type,
        )

    # Get all valid frames and markers to be solved per-frame.
    original_frames = list(range(start_frame, end_frame + 1))
    frame_counts = collections.defaultdict(int)
    all_frames = set()
    adjust_mkr_nodes = set()
    for mkr_node in accumulated_mkr_nodes:
        enabled_frames = marker_nodes_enabled[mkr_node]
        assert isinstance(enabled_frames, set)
        overlapping_frames = set(original_frames) & enabled_frames
        if len(overlapping_frames) >= 2:
            for frame in overlapping_frames:
                frame_counts[frame] += 1
            all_frames |= enabled_frames
            adjust_mkr_nodes.add(mkr_node)
    adjust_mkr_nodes = list(sorted(adjust_mkr_nodes))

    result = None
    if len(all_frames) > 0 and len(adjust_mkr_nodes) > 0:
        min_markers_num = 4
        all_frames = set(
            [frame for frame in all_frames if frame_counts[frame] >= min_markers_num]
        )

        start_frame = min(all_frames)
        end_frame = max(all_frames)
        frames = list(range(start_frame, end_frame + 1))

        # Solve per-frame. Only animated attributes are solved - bundles
        # and (static) focal lengths are ignored.
        LOG.debug("Solve per-frame; all_frames=%r", all_frames)
        result = _bundle_adjust(
            col_node,
            cam_tfm,
            cam_shp,
            adjust_mkr_nodes,
            cam_shp_node_attrs,
            lens_node_attrs,
            frames,
            adjust_camera_translate=True,
            adjust_camera_rotate=True,
            adjust_bundle_positions=True,
            adjust_camera_intrinsics=True,
            adjust_lens_distortion=True,
            iteration_num=10,
            per_frame_solve=False,
            solver_version=solver_version,
            solver_type=solver_type,
        )

    _set_camera_origin_frame(
        cam_tfm,
        accumulated_bnd_nodes,
        origin_frame,
        start_frame,
        end_frame,
        scene_scale,
    )
    return result
