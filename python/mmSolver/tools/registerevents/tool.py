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


def _register_changed_collection_update_solver_ui():
    """
    When A Collection has been changed we must update the Solver UI.
    """
    import mmSolver.api as mmapi
    event_utils.add_function_to_event(
        mmapi.EVENT_NAME_COLLECTION_MARKERS_CHANGED,
        lib.run_update_input_objects_in_solver_ui,
        deferred=True)
    event_utils.add_function_to_event(
        mmapi.EVENT_NAME_COLLECTION_ATTRS_CHANGED,
        lib.run_update_output_attributes_in_solver_ui,
        deferred=True)
    return


def _register_changed_attribute_update_solver_ui():
    """
    Called when attributes are changed and the solver UI needs to be updated.
    """
    import mmSolver.api as mmapi
    func = lib.run_update_output_attributes_in_solver_ui
    event_utils.add_function_to_event(
        mmapi.EVENT_NAME_ATTRIBUTE_STATE_CHANGED,
        func,
        deferred=True)
    return


def register_events():
    """
    Initialises the registry of events for mmSolver.

    This function is called at Maya start up, and is used to ensure
    events are connected when the user starts Maya.
    """
    LOG.info('Registering mmSolver Events...')
    _register_created_marker_connect_to_collection()
    _register_changed_collection_update_solver_ui()
    _register_changed_attribute_update_solver_ui()
    return
