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

import maya.cmds

import mmSolver.logger
import mmSolver.utils.viewport as viewport_utils
import mmSolver._api.constant as const
import mmSolver._api.state as api_state
import mmSolver._api.solveresult as solveresult
import mmSolver._api.collectionutils as collectionutils

LOG = mmSolver.logger.get_logger()


def postSolve_refreshViewport(refresh, force_update, frame):
    """
    Refresh the viewport after a solve has finished.

    :type refresh: bool or None
    :type do_isolate: bool or None

    :param frame:
        The list of frame numbers, first item in list is used to
        refresh the viewport.
    :type frame: [int or float, ..]
    """
    assert refresh is None or isinstance(refresh, bool)
    assert force_update is None or isinstance(force_update, bool)

    if refresh is not True:
        return

    maya.cmds.currentTime(
        frame[0],
        edit=True,
        update=force_update,
    )
    maya.cmds.refresh()
    return


def postSolve_setViewportState(refresh, do_isolate, panel_objs, panel_node_type_vis):
    """
    Change the viewport state based on the values given

    :type refresh: bool or None
    :type do_isolate: bool or None

    :param panel_objs:
        The panels and object to isolate, in a list of tuples.
    :type panel_objs: [(str, [str, ..] or None), ..]

    :param panel_node_type_vis:
        The panels and node-type visibility options in a list of tuples.
    :type panel_node_type_vis: [(str, {str: int or bool or None}), ..]
    """
    assert refresh is None or isinstance(refresh, bool)
    assert do_isolate is None or isinstance(do_isolate, bool)

    if refresh is not True:
        return

    # Isolate Objects restore.
    for panel, objs in panel_objs.items():
        if objs is None:
            # No original objects, disable 'isolate
            # selected' after resetting the objects.
            if do_isolate is True:
                viewport_utils.set_isolated_nodes(panel, [], False)

        elif do_isolate is True:
            viewport_utils.set_isolated_nodes(panel, list(objs), True)

    # Show menu restore.
    for panel, node_types_vis in panel_node_type_vis.items():
        for node_type, value in node_types_vis.items():
            if value is None:
                continue
            viewport_utils.set_node_type_visibility(panel, node_type, value)
    return


def postSolve_setUpdateProgress(
    progress_min, progress_value, progress_max, solres, prog_fn, status_fn
):
    """
    Update the Maya GUI with progress information, and detects users
    wanting to cancel the solve.

    :param progress_min:
        Minimum progress number possible.
        Usually the number is 0.
    :type progress_min: int

    :param progress_value:
        The actual progress value.
        The value is usually between 0 and 100 (inclusive).
    :type progress_value: int

    :param progress_max:
        THe maximum progress number possible.
        Usually the number is 100.
    :type progress_max: int

    :param solres:
        The SolveResult object for the last solved state.
    :type solres: SolveResult, int, bool or None

    :param prog_fn: The function used report progress messages to
                    the user.
    :type prog_fn: callable or None

    :param status_fn: The function used to report status messages
                      to the user.
    :type status_fn: callable or None

    :returns:
        Should the solver stop executing or not? Has the user
        cancelled the solve?
    :rtype: bool
    """
    stop_solving = False

    # Update progress
    ratio = float(progress_value) / float(progress_max)
    percent = float(progress_min) + (ratio * (100.0 - progress_min))
    collectionutils.run_progress_func(prog_fn, int(percent))

    # Check if the user wants to stop solving.
    cmd_cancel = False
    if isinstance(solres, solveresult.SolveResult):
        cmd_cancel = solres.get_user_interrupted()
    gui_cancel = api_state.get_user_interrupt()
    if cmd_cancel is True or gui_cancel is True:
        msg = 'Cancelled by User'
        api_state.set_user_interrupt(False)
        collectionutils.run_status_func(status_fn, 'WARNING: ' + msg)
        LOG.warn(msg)
        stop_solving = True

    if solres is not None:
        fail = None
        if isinstance(solres, solveresult.SolveResult):
            fail = solres.get_success() is False
        else:
            fail = bool(solres) is False
            if fail is True:
                stop_solving = True
        if fail is True:
            msg = 'Solver failed!!!'
            collectionutils.run_status_func(status_fn, 'ERROR: ' + msg)
            LOG.error(msg)
    return stop_solving


def _postSolve_relockAttrs(nodes, possible_attrs):
    assert isinstance(nodes, set)
    assert isinstance(possible_attrs, set)
    for node_name in nodes:
        existing_attrs = set(maya.cmds.listAttr(node_name))
        attrs = existing_attrs & possible_attrs
        for attr_name in attrs:
            plug = '{}.{}'.format(node_name, attr_name)
            maya.cmds.setAttr(plug, lock=True)
    return


def postSolve_relockCollectionAttrs(relock_nodes):
    possible_attrs = set(const.COLLECTION_RESULTS_STORE_ATTR_NAMES)
    return _postSolve_relockAttrs(relock_nodes, possible_attrs)


def postSolve_relockMarkerAttrs(relock_nodes):
    possible_attrs = set(const.MARKER_RESULTS_STORE_ATTR_NAMES)
    return _postSolve_relockAttrs(relock_nodes, possible_attrs)
