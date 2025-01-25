# Copyright (C) 2018, 2019 David Cattermole.
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
The Solver UI tool.
"""

import datetime
import uuid

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.utils.tools as tools_utils

import mmSolver.tools.solver.lib.collection as lib_col
import mmSolver.tools.solver.lib.collectionstate as lib_col_state
import mmSolver.tools.solver.lib.state as lib_state
import mmSolver.tools.solver.ui.solver_window as solver_window
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


def __get_override_current_frame_value(col, tab):
    value = None
    if tab in [const.SOLVER_TAB_BASIC_VALUE, const.SOLVER_TAB_STANDARD_VALUE]:
        value = lib_col_state.get_solver_range_type_from_collection(col)
    else:
        raise ValueError(
            'Cannot get override current frame; tab is not supported; tab=%r' % tab
        )
    return value


def __set_override_current_frame_value(col, layout_ui, tab, value):
    if tab in [const.SOLVER_TAB_BASIC_VALUE, const.SOLVER_TAB_STANDARD_VALUE]:
        if value is True:
            value = const.RANGE_TYPE_CURRENT_FRAME_VALUE
        lib_col_state.set_solver_range_type_on_collection(col, value)
    else:
        raise ValueError(
            'Cannot get override current frame; tab is not supported; tab=%r' % tab
        )
    return


def run_solve(override_current_frame=None):
    """
    Run the solver for the active collection.

    If the Solver UI is found, the window will update and show
    progress messages.

    This function is strongly dependent on the Solver UI.
    The following state information is set via the Solver UI.

    - Active Collection
    - Log Level
    - Refresh Viewport

    :param override_current_frame: Before running the solver, change
                                   the "override current frame" state to
                                   this value.
    :type override_current_frame: bool or None
    """
    assert override_current_frame is None or isinstance(override_current_frame, bool)
    if override_current_frame is None:
        override_current_frame = False

    col = lib_state.get_active_collection()
    if col is None:
        msg = 'No active Collection found. Skipping solve.'
        LOG.warning(msg)
        return
    log_level = lib_state.get_log_level()

    layout = None
    win = solver_window.SolverWindow.get_instance()
    win_valid = uiutils.isValidQtObject(win)
    if win is None and win_valid:
        msg = 'Could not get window.'
        LOG.warning(msg)
    else:
        layout = win.getSubForm()

    # Set 'override current frame' value.
    tab = lib_col_state.get_solver_tab_from_collection(col)
    prev_value = None
    if override_current_frame is True:
        prev_value = __get_override_current_frame_value(col, tab)
        __set_override_current_frame_value(col, layout, tab, override_current_frame)

    # Run Solver
    options = lib_col.gather_execute_options()
    lib_col.run_solve_ui(
        col,
        options,
        log_level,
        win,
    )

    # Restore previous value.
    if override_current_frame is True:
        __set_override_current_frame_value(col, layout, tab, prev_value)
    return


def run_solve_on_current_frame():
    """
    Run the solver, forcing 'Override Current Frame' on.
    """
    undo_id = 'mmSolver: '
    undo_id += str(datetime.datetime.isoformat(datetime.datetime.now()))
    undo_id += ' '
    undo_id += str(uuid.uuid4())
    with tools_utils.tool_context(
        use_undo_chunk=True,
        undo_chunk_name=undo_id,
        restore_current_frame=False,
        pre_update_frame=False,
        post_update_frame=False,
        use_dg_evaluation_mode=True,
        disable_viewport=False,
    ):
        run_solve(override_current_frame=True)
    return


def run_solve_on_all_frames():
    """
    Run the solver, forcing 'Override Current Frame' off.
    """
    undo_id = 'mmSolver: '
    undo_id += str(datetime.datetime.isoformat(datetime.datetime.now()))
    undo_id += ' '
    undo_id += str(uuid.uuid4())
    with tools_utils.tool_context(
        use_undo_chunk=True,
        undo_chunk_name=undo_id,
        restore_current_frame=False,
        pre_update_frame=False,
        post_update_frame=False,
        use_dg_evaluation_mode=True,
        disable_viewport=False,
    ):
        run_solve(override_current_frame=False)
    return


def open_window():
    """
    Open the Solver UI window.
    """
    col = lib_state.get_active_collection()
    if col is None:
        col_list = lib_col.get_collections()
        if len(col_list) == 0:
            msg = 'No active Collection found, creating new Collection...'
            LOG.warn(msg)
            lib_col.create_collection()
        elif len(col_list) > 0:
            col_list = sorted(col_list, key=lambda x: x.get_node())
            col = col_list[0]
            lib_state.set_active_collection(col)

    solver_window.main()
    return
