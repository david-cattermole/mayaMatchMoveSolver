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

import collections

import mmSolver.logger
import mmSolver._api.constant as const
import mmSolver._api.attribute as attribute
import mmSolver._api.attributeutils as attributeutils


LOG = mmSolver.logger.get_logger()
BUNDLE_ATTR_NAMES = ['translateX', 'translateY', 'translateZ']


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


def _markers_to_data_lists(mkr_list,
                           start_frame, end_frame,
                           min_frames_per_marker):
    mkr_node_list = []
    mkr_enabled_frames = {}
    mkr_min_frames_count = {}

    for mkr in mkr_list:
        mkr_node = mkr.get_node()
        mkr_node_list.append(mkr_node)
        enabled_frames = mkr.get_enabled_frames(
            frame_range_start=start_frame,
            frame_range_end=end_frame)

        min_frames_count = _get_minimum_number_of_root_frames_for_marker(mkr)
        min_frames_count = max(min_frames_per_marker, min_frames_count)

        mkr_enabled_frames[mkr_node] = enabled_frames
        mkr_min_frames_count[mkr_node] = min_frames_count

    return mkr_node_list, mkr_enabled_frames, mkr_min_frames_count


def get_root_frames_from_markers(mkr_list, start_frame, end_frame):
    min_frames_per_marker = 2
    initial_root_frames = set()

    all_frames = range(start_frame, end_frame + 1)
    root_frames = set(initial_root_frames)
    mkr_root_frames = collections.defaultdict(set)
    root_frame_mkr_list = collections.defaultdict(set)

    # Convert Markers to data lists.
    mkr_node_list, mkr_enabled_frames, mkr_min_frames_count = \
        _markers_to_data_lists(
            mkr_list, start_frame, end_frame, min_frames_per_marker)

    # Create maps for frames and markers.
    for mkr_node in mkr_node_list:
        enabled_frames = mkr_enabled_frames[mkr_node]
        for f in all_frames:
            if f in enabled_frames:
                mkr_root_frames[mkr_node].add(f)
                root_frame_mkr_list[f].add(mkr_node)

    common_nodes = collections.defaultdict(
        lambda: collections.defaultdict(
            lambda: collections.defaultdict(set)))
    for mkr_node in sorted(mkr_node_list):
        min_frames_count = mkr_min_frames_count[mkr_node] - 1
        enabled_frames = mkr_enabled_frames[mkr_node]

        for f in enabled_frames:
            nodes = set(root_frame_mkr_list[f])
            nodes.discard(mkr_node)

            mkr_counts = len(nodes)
            if mkr_counts >= min_frames_count:
                common_nodes[mkr_node][mkr_counts][f] = nodes

    mkr_frames = collections.defaultdict(set)
    for mkr_node in mkr_node_list:
        min_frames_count = mkr_min_frames_count[mkr_node]

        mkr_counts = common_nodes[mkr_node].keys()
        mkr_counts = reversed(sorted(mkr_counts))
        for mkr_count in mkr_counts:
            if len(mkr_frames[mkr_node]) >= min_frames_count:
                break

            frame_map = common_nodes[mkr_node][mkr_count]
            frame_keys = frame_map.keys()
            i = 0
            while len(frame_keys) > 0:
                if len(mkr_frames[mkr_node]) >= min_frames_count:
                    break
                even = (i % 2) == 0
                if even is True:
                    f = frame_keys.pop(0)
                else:
                    f = frame_keys.pop(-1)
                mkr_frames[mkr_node].add(f)
                root_frames.add(f)
                i += 1
    return list(root_frames)
