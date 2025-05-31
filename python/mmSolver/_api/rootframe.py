# Copyright (C) 2020 David Cattermole.
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
Root Frame calculation logic.
"""

# TODO: Create a list of markers specially for root frames.  Loop over
#  all given markers, determine which markers have 2 or more root
#  frames, only use those markers for root frame computation. Overall,
#  we must filter out all markers that cannot/should not be used for
#  different solves.
#
# TODO: We must make sure to allow the solver to detect that not
#  enough markers are being used, and warn the user.
#
# TODO: All markers that do not have enough root frames to solve
#  correctly, but the Bundle is still in the solver, then it should be
#  triangulated after the initial root frame solve is performed.
#
# TODO: Run the solver multiple times for a hierarchy. First, solve
#  DAG level 0 nodes, then add DAG level 1, then level 2, etc. This
#  will allow us to incrementally add solving of hierarchy, without
#  getting the optimiser confused which attributes to solve first to
#  get a stable solve.

# TODO: Root frame ordering can be determined by the count of markers
#  available at each frame. After we have an ordering of these frames,
#  we can solve the frames incrementally, starting with the first
#  highest, then add the next highest, etc. This should ensure
#  stability of the solver is maximum.

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections

import mmSolver.logger
import mmSolver._api.constant as const
import mmSolver._api.attribute as attribute


LOG = mmSolver.logger.get_logger()
BUNDLE_ATTR_NAMES = ['translateX', 'translateY', 'translateZ']


def generate_increment_frame_forward(int_list):
    """Convert a list of integers into multiple lists of the same
    integers, increasing the number of elements by 3 each time.

    Example:

       >>> x = [1, 2]
       >>> generate_increment_frame_forward(x)
       [[1, 2]]
       >>> x = [1, 2, 3, 4, 5]
       >>> generate_increment_frame_forward(x)
       [[1, 2, 3], [1, 2, 3, 4, 5]]
       >>> x = [1, 2, 3, 4, 5, 6, 7, 8, 9]
       >>> generate_increment_frame_forward(x)
       [[1, 2, 3], [1, 2, 3, 4, 5, 6], [1, 2, 3, 4, 5, 6, 7, 8, 9]]

    """
    if len(int_list) < 3:
        batch_list = [int_list]
        return batch_list
    end = len(int_list) - 1
    batch_list = []
    for i in range(1, end):
        s = 0
        e = i + pow(2, i)
        frm_list = int_list[s:e]
        batch_list.append(frm_list)
        if len(frm_list) >= len(int_list):
            break
    return batch_list


def _get_minimum_number_of_root_frames_for_marker(mkr):
    min_frames_count = 0

    bnd = mkr.get_bundle()
    if bnd is None:
        return min_frames_count
    bnd_node = bnd.get_node()
    if bnd_node is None:
        return min_frames_count

    locked_count = 0
    animated_count = 0
    static_count = 0
    for attr_name in BUNDLE_ATTR_NAMES:
        attr = attribute.Attribute(node=bnd_node, attr=attr_name)
        attr_state = attr.get_state()
        locked_count += int(attr_state == const.ATTR_STATE_LOCKED)
        static_count += int(attr_state == const.ATTR_STATE_STATIC)
        animated_count += int(attr_state == const.ATTR_STATE_ANIMATED)

    if static_count > 0:
        min_frames_count = 2
    elif (animated_count == 3) or (locked_count == 3):
        min_frames_count = 1
    return min_frames_count


def _default_to_regular(d):
    """Convert defaultdict to a regular dict. This function works
    recursively.
    """
    if isinstance(d, collections.defaultdict):
        d = {k: _default_to_regular(v) for k, v in d.items()}
    return d


def _markers_to_data_lists(mkr_list, start_frame, end_frame, min_frames_per_marker):
    assert isinstance(mkr_list, (list, set))
    assert isinstance(min_frames_per_marker, int)
    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)

    mkr_node_list = []
    mkr_enabled_frames = {}
    mkr_min_frames_count = {}

    for mkr in mkr_list:
        mkr_node = mkr.get_node()
        mkr_node_list.append(mkr_node)
        enabled_frames = mkr.get_enabled_frames(
            frame_range_start=start_frame, frame_range_end=end_frame
        )

        min_frames_count = _get_minimum_number_of_root_frames_for_marker(mkr)
        min_frames_count = max(min_frames_per_marker, min_frames_count)

        mkr_enabled_frames[mkr_node] = enabled_frames
        mkr_min_frames_count[mkr_node] = min_frames_count

    return mkr_node_list, mkr_enabled_frames, mkr_min_frames_count


def get_root_frames_from_markers(
    mkr_list, min_frames_per_marker, start_frame, end_frame
):
    """
    Get root frames numbers from the markers.

    :param mkr_list:
        List of Markers to compute root frames from.
    :type mkr_list: [Marker, ..]

    :param min_frames_per_marker:
        The number of frames that are required for each marker.
    :type min_frames_per_marker: int

    :param start_frame:
        The first frame to consider as a root frame.
    :type start_frame: int

    :param end_frame:
        The last frame to consider as a root frame.
    :type end_frame: int

    :returns: List of frame numbers.
    :rtype: [int, ..]
    """
    assert isinstance(mkr_list, (list, set))
    assert isinstance(min_frames_per_marker, int)
    assert isinstance(start_frame, int)
    assert isinstance(end_frame, int)
    # In future, this paper has a very promising "key-frame selection
    # criterion", which could be used to increase quality and speed of
    # bundle-adjustment.
    #
    # Optimal key-frame selection for video-based structure-from-motion
    #
    # Park,M.-G. et al.
    # Electronics Letters(2011),47(25):1367
    # http://dx.doi.org/10.1049/el.2011.2674
    #
    # https://www.researchgate.net/publication/260616120_Optimal_key-frame_selection_for_video-based_structure-from-motion
    #
    all_frames = range(start_frame, end_frame + 1)
    root_frames = list()
    mkr_root_frames = collections.defaultdict(set)
    root_frame_mkr_list = collections.defaultdict(set)

    # Convert Markers to data lists.
    mkr_node_list, mkr_enabled_frames, mkr_min_frames_count = _markers_to_data_lists(
        mkr_list, start_frame, end_frame, min_frames_per_marker
    )

    # Create maps for frames and markers.
    for mkr_node in mkr_node_list:
        enabled_frames = mkr_enabled_frames[mkr_node]
        for f in all_frames:
            if f in enabled_frames:
                mkr_root_frames[mkr_node].add(f)
                root_frame_mkr_list[f].add(mkr_node)

    common_nodes = collections.defaultdict(
        lambda: collections.defaultdict(lambda: collections.defaultdict(set))
    )
    for mkr_node in sorted(mkr_node_list):
        min_frames_count = mkr_min_frames_count[mkr_node] - 1
        enabled_frames = mkr_enabled_frames[mkr_node]

        for f in enabled_frames:
            nodes = set(root_frame_mkr_list[f])
            nodes.discard(mkr_node)

            mkr_counts = len(nodes)
            if mkr_counts >= min_frames_count:
                common_nodes[mkr_node][mkr_counts][f] = nodes

    # Controls how close a frame is before it's considered too close
    # to use. If we choose key-frames that are too close, there will
    # not be enough paralax in the solve and therefore a bad solve may
    # occur.
    close_num = 2

    mkr_frames = collections.defaultdict(set)
    for mkr_node in sorted(mkr_node_list):
        min_frames_count = mkr_min_frames_count[mkr_node]

        mkr_counts = common_nodes[mkr_node].keys()
        mkr_counts = reversed(sorted(mkr_counts))
        for mkr_count in mkr_counts:
            if len(mkr_frames[mkr_node]) >= min_frames_count:
                break

            frame_map = common_nodes[mkr_node][mkr_count]
            frame_keys = list(sorted(frame_map.keys()))
            i = 0
            while len(frame_keys) > 0:
                if len(mkr_frames[mkr_node]) >= min_frames_count:
                    break
                even = (i % 2) == 0
                if even is True:
                    f = frame_keys.pop(0)
                else:
                    f = frame_keys.pop(-1)

                if len(frame_keys) > 0:
                    # Only test if a frame is too near if we have a
                    # choice of more frames.
                    too_near = False
                    near_frames = range(f - close_num, f + close_num + 1)
                    for near_frame in near_frames:
                        if near_frame in root_frames:
                            too_near = True
                    if too_near is True:
                        # Skip this frame, because it's too close to
                        # another (already selected) root frame.
                        continue

                mkr_frames[mkr_node].add(f)
                if f not in root_frames:
                    root_frames.append(f)
                i += 1

    return list(sorted(set(root_frames)))


def _frame_list_max_frame_distance(frame_list):
    assert isinstance(frame_list, (list, set))
    frame_list = list(sorted(set(frame_list)))

    max_frame_distance = 0
    result_frame_a = 0
    result_frame_b = 0
    for i in range(len(frame_list) - 1):
        frame_a = frame_list[i]
        frame_b = frame_list[i + 1]
        assert frame_a < frame_b

        frame_distance = frame_b - frame_a
        if frame_distance > max_frame_distance:
            max_frame_distance = frame_distance
            result_frame_a = frame_a
            result_frame_b = frame_b

    assert isinstance(max_frame_distance, int)
    assert isinstance(result_frame_a, int)
    assert isinstance(result_frame_b, int)
    assert result_frame_a < result_frame_b
    return max_frame_distance, result_frame_a, result_frame_b


def root_frames_subdivide(root_frames, max_frame_span):
    """
    Get root frames numbers from the markers.

    :param max_frame_span:
        The maximum number of frames between a frame pair the list of
        root frames.
    :type max_frame_span: int

    :returns: List of frame numbers.
    :rtype: [int, ..]
    """
    assert isinstance(max_frame_span, int)
    assert max_frame_span > 0
    if len(root_frames) == 0:
        return list(sorted(set(root_frames)))

    if max_frame_span == 1:
        # Special case where each frame will be a root frame.
        root_frames = list(sorted(set(root_frames)))
        start_frame = root_frames[0]
        end_frame = root_frames[-1]
        all_frames = range(start_frame, end_frame + 1)
        return list(all_frames)

    # Make the largest distance between two frames 'max_frame_span' or
    # less.
    max_frame_distance, frame_a, frame_b = _frame_list_max_frame_distance(root_frames)
    while max_frame_distance > max_frame_span:
        frame_mid = frame_a + int(round((frame_b - frame_a) * 0.5))
        if frame_mid not in root_frames:
            root_frames.append(frame_mid)
        max_frame_distance, frame_a, frame_b = _frame_list_max_frame_distance(
            root_frames
        )

    return list(sorted(set(root_frames)))


def root_frames_list_combine(frame_list_a, frame_list_b):
    """
    Get root frames numbers from the markers.

    :param frame_list_a:
        List of Frames that will be added to the root frames.
    :type frame_list_a: [int, ..]

    :param frame_list_b:
        List of Frames that will be added to the root frames.
    :type frame_list_b: [int, ..]

    :returns: List of frame numbers.
    :rtype: [int, ..]
    """
    assert isinstance(frame_list_a, (list, set))
    assert isinstance(frame_list_b, (list, set))
    frame_list = set(frame_list_a) | set(frame_list_b)
    return list(sorted(frame_list))
