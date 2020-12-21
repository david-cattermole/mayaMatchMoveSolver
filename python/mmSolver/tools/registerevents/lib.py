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
Register events for mmSolver.

.. note:: Modules are imported inside the functions to avoid slow
    initial module loading, and instead we defer the module import
    until the function is triggered.

"""

import time
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def run_connect_markers_to_active_collection(**kwargs):
    import mmSolver.tools.userpreferences.constant as userprefs_const
    import mmSolver.tools.userpreferences.lib as userprefs_lib

    # Enable a toggle to turn on or off this affect.
    config = userprefs_lib.get_config()
    key = userprefs_const.REG_EVNT_ADD_NEW_MKR_TO_KEY
    run_event = userprefs_lib.get_value(config, key)
    if run_event == userprefs_const.REG_EVNT_ADD_NEW_MKR_TO_NONE_VALUE:
        return

    LOG.debug("run_connect_markers_to_active_collection: %s", kwargs)
    s = time.time()
    import mmSolver.api as mmapi
    import mmSolver.tools.solver.lib.state as state_lib
    mmapi.load_plugin()

    col = state_lib.get_active_collection()
    if col is None:
        return

    mkr = kwargs.get('mkr')
    if isinstance(mkr, list):
        col.add_marker_list(mkr)
    elif isinstance(mkr, mmapi.Marker):
        col.add_marker(mkr)

    e = time.time()
    LOG.debug("run_connect_markers_to_active_collection: time=%s", e - s)
    return


def run_update_input_objects_in_solver_ui(**kwargs):
    LOG.debug("run_update_input_objects_in_solver_ui: %r", kwargs)
    s = time.time()
    import mmSolver.tools.solver.ui.solver_window as solver_window
    win = solver_window.SolverWindow.get_instance()
    if win is not None:
        win.triggerInputObjectsUpdate()
    e = time.time()
    LOG.debug("run_update_input_objects_in_solver_ui: time=%s", e - s)
    return


def run_update_output_attributes_in_solver_ui(**kwargs):
    LOG.debug("run_update_output_attributes_in_solver_ui: %r", kwargs)
    s = time.time()
    import mmSolver.tools.solver.ui.solver_window as solver_window
    win = solver_window.SolverWindow.get_instance()
    if win is not None:
        win.triggerOutputAttributesUpdate()
    e = time.time()
    LOG.debug("run_update_output_attributes_in_solver_ui: time=%s", e - s)
    return
