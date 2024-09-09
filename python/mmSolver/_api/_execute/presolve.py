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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import collections

import maya.cmds

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver._api.constant as const
import mmSolver._api.state as api_state
import mmSolver._api.excep as excep
import mmSolver._api.solveresult as solveresult
import mmSolver._api.collectionutils as collectionutils
import mmSolver._api.marker as api_marker


LOG = mmSolver.logger.get_logger()


def preSolve_updateProgress(prog_fn, status_fn):
    """
    Initialise solver is running, and send info to the Maya GUI before
    a solve starts.

    :param prog_fn: Function to use for printing progress messages.
    :type prog_fn: callable or None

    :param status_fn: Function to use for printing status messages.
    :type status_fn: callable or None
    """
    # Start up solver
    collectionutils.run_progress_func(prog_fn, 0)
    ts = solveresult.format_timestamp(time.time())
    collectionutils.run_status_func(status_fn, 'Solve start (%s)' % ts)
    api_state.set_solver_running(True)
    return


def preSolve_queryViewportState(refresh, do_isolate, display_node_types, panels):
    """
    Query the viewport state before solving.

    If 'refresh' is 'on' change all viewports to 'isolate
    selected' on only the markers and bundles being solved. This
    will speed up computations, especially per-frame solving as
    it will not re-compute any invisible nodes (such as rigs or
    image planes).

    :type refresh: bool or None
    :type do_isolate: bool or None
    :type display_node_types: {str: bool, ..}

    :param panels: List of panel names to query details from.
    :type panels: [str, ..]

    :rtype: ({str: [str, ..]}, {str: {str: bool}})
    """
    assert refresh is None or isinstance(refresh, bool)
    assert do_isolate is None or isinstance(do_isolate, bool)
    assert display_node_types is None or isinstance(display_node_types, dict)

    panel_objs = {}
    panel_node_type_vis = collections.defaultdict(dict)
    if refresh is not True:
        return panel_objs, panel_node_type_vis

    if display_node_types is not None:
        for panel in panels:
            node_types = display_node_types.keys()
            node_type_vis = dict()
            for node_type in node_types:
                value = viewport_utils.get_node_type_visibility(panel, node_type)
                node_type_vis[node_type] = value
            panel_node_type_vis[panel] = node_type_vis

    if do_isolate is True:
        for panel in panels:
            state = maya.cmds.isolateSelect(panel, query=True, state=True)
            nodes = None
            if state is True:
                nodes = viewport_utils.get_isolated_nodes(panel)
            panel_objs[panel] = nodes

    return panel_objs, panel_node_type_vis


def preSolve_setIsolatedNodes(
    actions_list, refresh, do_isolate, display_node_types, panels
):
    """
    Prepare frame solve

    Isolate all nodes used in all of the kwargs to be run.
    Note; This assumes the isolated objects are visible, but
    they may actually be hidden.

    :type refresh: bool or None
    :type do_isolate: bool or None
    :type display_node_types: {str: bool, ..}

    :returns: None
    """
    assert refresh is None or isinstance(refresh, bool)
    assert do_isolate is None or isinstance(do_isolate, bool)
    assert display_node_types is None or isinstance(display_node_types, dict)
    if refresh is not True:
        return
    if do_isolate is True:
        isolate_nodes = set()
        for action in actions_list:
            kwargs = action.kwargs
            isolate_nodes |= collectionutils.generate_isolate_nodes(kwargs)
        if len(isolate_nodes) == 0:
            raise excep.NotValid
        isolate_node_list = list(isolate_nodes)
        for panel in panels:
            viewport_utils.set_isolated_nodes(panel, isolate_node_list, True)

    if display_node_types is not None:
        for panel in panels:
            for node_type, value in display_node_types.items():
                if value is None:
                    continue
                assert isinstance(value, bool)
                viewport_utils.set_node_type_visibility(panel, node_type, value)
    return


def preSolve_triggerEvaluation(
    action_list, cur_frame, pre_solve_force_eval, force_update
):
    """
    Set the first current time to the frame before current.

    This is to help trigger evaluations on the 'current
    frame', if the current frame is the same as the first
    frame.

    :param action_list: List of :py:class:`Action` objects that are
                        used in the current solve.
    :type action_list: [Action, .. ]

    :param cur_frame: The current frame number.
    :type cur_frame: int or float

    :type pre_solve_force_eval: None or bool
    :type force_update: None or bool

    :rtype: None
    """
    if pre_solve_force_eval is not True:
        return
    frame_list = []
    for action in action_list:
        kwargs = action.kwargs
        frame_list += kwargs.get('frame', [])
    frame_list = list(set(frame_list))
    frame_list = list(sorted(frame_list))
    is_whole_solve_single_frame = len(frame_list) == 1
    if is_whole_solve_single_frame is False:
        maya.cmds.currentTime(
            cur_frame + 1,
            edit=True,
            update=force_update,
        )
    return


def preSolve_unlockCollectionAttrs(col):
    """
    Unlock all Collection attributes that will be set by mmSolver
    commands.
    """
    col_node = col.get_node()
    assert col_node is not None
    assert maya.cmds.objExists(col_node)
    relock_nodes = set([col_node])

    existing_attrs = set(maya.cmds.listAttr(col_node))
    attrs = existing_attrs & set(const.COLLECTION_RESULTS_STORE_ATTR_NAMES)

    for attr_name in attrs:
        # The plug may not exist, yet, but after a solve has finished the
        # attribute may need to be locked.
        plug = '{0}.{1}'.format(col_node, attr_name)

        locked = maya.cmds.getAttr(plug, lock=True)
        if locked is True:
            maya.cmds.setAttr(plug, lock=False)
    return relock_nodes


def preSolve_unlockMarkerAttrs(mkr_list):
    """
    Unlock all Marker attributes that will be set by mmSolver
    commands.
    """
    relock_nodes = set()
    for mkr in mkr_list:
        assert isinstance(mkr, api_marker.Marker)
        mkr_node = mkr.get_node()
        assert mkr_node is not None
        relock_nodes.add(mkr_node)

        existing_attrs = set(maya.cmds.listAttr(mkr_node))
        attrs = existing_attrs & set(const.MARKER_RESULTS_STORE_ATTR_NAMES)

        for attr_name in attrs:
            # The plug may not exist, yet, but after a solve has finished the
            # attribute may need to be locked.
            plug = '{0}.{1}'.format(mkr_node, attr_name)

            locked = maya.cmds.getAttr(plug, lock=True)
            if locked is True:
                maya.cmds.setAttr(plug, lock=False)
    return relock_nodes
