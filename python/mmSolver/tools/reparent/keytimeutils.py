# Copyright (C) 2019 David Cattermole.
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
Keyframe time querying utilities.
"""

import maya.cmds
import mmSolver.logger
import mmSolver.utils.node as node_utils
import mmSolver.utils.python_compat as pycompat

LOG = mmSolver.logger.get_logger()


class KeyframeTimes(object):
    def __init__(self):
        self._frame_ranges_map = {}
        self._key_times_map = {}

    def add_node_attrs(self, node, attrs, start_frame, end_frame, parents=None):
        """
        Add node attributes into the keyframe times.
        """
        assert isinstance(node, pycompat.TEXT_TYPE)
        assert isinstance(attrs, (list, tuple))
        nodes = [node]
        if parents is not None:
            assert isinstance(parents, (list, tuple))
            nodes += parents
        # Times are accumulated for the given 'node' plus all
        # parent nodes, into the same 'node_uuid'.
        start = start_frame
        end = end_frame
        node_uuid = maya.cmds.ls(node, uuid=True)[0]
        for node in nodes:
            for attr in attrs:
                plug = node + '.' + attr
                attr_exists = node_utils.attribute_exists(attr, node)
                if attr_exists is False:
                    continue
                settable = maya.cmds.getAttr(plug, settable=True)
                if settable is False:
                    continue
                times = maya.cmds.keyframe(plug, query=True, timeChange=True) or []
                if len(times) == 0:
                    continue
                if node_uuid not in self._key_times_map:
                    self._key_times_map[node_uuid] = set()
                times = [int(t) for t in times]
                self._key_times_map[node_uuid] |= set(times)
                node_key_times = self._key_times_map.get(node_uuid)
                key_start = min(node_key_times)
                key_end = max(node_key_times)
                start = min(key_start, start)
                end = max(key_end, end)
        self._frame_ranges_map[node_uuid] = (start, end)
        return

    def get_nodes(self):
        nodes = self._frame_ranges_map.keys()
        return nodes

    def get_frame_range_for_node(self, node):
        node_uuid = maya.cmds.ls(node, uuid=True)[0]
        start, end = self._frame_ranges_map.get(node_uuid, (None, None))
        return start, end

    def sum_frame_range_for_nodes(self, nodes):
        total_start = 9999999
        total_end = -9999999
        for node in nodes:
            start, end = self.get_frame_range_for_node(node)
            if start is None or end is None:
                continue
            total_start = min(total_start, start)
            total_end = max(total_end, end)
        return total_start, total_end

    def get_times(self, node, sparse):
        """
        The logic to query time for a node, in sparse or dense mode.
        """
        times = []
        if sparse is True:
            node_uuid = maya.cmds.ls(node, uuid=True)[0]
            times = self._key_times_map.get(node_uuid, None)
        else:
            node_uuid = maya.cmds.ls(node, uuid=True)[0]
            start, end = self._frame_ranges_map.get(node_uuid, (None, None))
            if start is not None and end is not None:
                times = range(start, end + 1)
        if times is not None and len(times) > 0:
            times = list(times)
        return times
