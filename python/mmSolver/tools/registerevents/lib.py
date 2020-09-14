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
Functions to be run when events trigger them.

See the tool.py file to see how these functions are attached to
events.

.. note:: Modules are imported inside the functions to avoid slow
    initial module loading, and instead we defer the module import
    until the function is triggered.

.. note:: All functions are expected to be called with one or more
    individual objects, therefore if a single event operates on one
    int value, the run function will receive a list of values. This is
    to avoid performance issues from many triggered events at once.

"""

import time
import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def run_connect_markers_to_active_collection(**kwargs):
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
