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

Currently implemented events:

 - When a Marker is created, automatically connect it to the active
   Collection.

"""

import mmSolver.logger

import mmSolver.utils.event as event_utils
import mmSolver.api as mmapi
import mmSolver.tools.registerevents.lib as lib

LOG = mmSolver.logger.get_logger()


def _register_created_marker_connect_to_collection():
    """
    Connect the created marker to the currently active Collectione.
    """
    event_utils.add_function_to_event(
        mmapi.EVENT_NAME_MARKER_CREATED,
        lib.run_connect_markers_to_active_collection,
        deferred=True)
    return


def register_events():
    """
    Initialises the registery of events for mmSolver.

    This function is called at Maya start up, and is used to ensure
    events are connected when the user starts Maya.
    """
    LOG.info('Registering mmSolver Events...')
    _register_created_marker_connect_to_collection()
    return
