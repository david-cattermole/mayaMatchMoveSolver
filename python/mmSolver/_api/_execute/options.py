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

import collections

import mmSolver.logger

LOG = mmSolver.logger.get_logger()

ExecuteOptions = collections.namedtuple(
    'ExecuteOptions',
    (
        'verbose',
        'refresh',
        'disable_viewport_two',
        'force_update',
        'pre_solve_force_eval',
        'do_isolate',
        'display_grid',
        'display_node_types',
        'use_minimal_ui',
    ),
)


def create_execute_options(
    verbose=False,
    refresh=False,
    disable_viewport_two=True,
    force_update=False,
    do_isolate=False,
    pre_solve_force_eval=True,
    display_grid=True,
    display_node_types=None,
    use_minimal_ui=None,
):
    """
    Create :py:class:`ExecuteOptions` object.

    If a keyword argument is not given, a reasonable default value is
    used.

    :param verbose: Print extra solver information while a solve is running.
    :type verbose: bool

    :param refresh: Should the solver refresh the viewport while solving?
    :type refresh: bool

    :param disable_viewport_two: Turn off Viewport 2.0 update, before solving?
    :type disable_viewport_two: bool

    :param force_update: Force updating the DG network, to help the
                         solver in case of a Maya evaluation DG bug.
    :type force_update: bool

    :param do_isolate: Isolate only solving objects while performing
                       the solve.
    :type do_isolate: bool

    :param pre_solve_force_eval: Before solving, we kick-start the
                                 evaluation by changing time and
                                 forcing update.
    :type pre_solve_force_eval: bool

    :param display_grid: Display grid in the viewport while performing
                         the solve?
    :type display_grid: bool

    :param display_node_types: Allow a dict to be passed to the function
                               specifying the object type and the
                               visibility status during solving. This
                               allows us to turn on/off any object type
                               during solving. If an argument is not
                               given or is None, the object type
                               visibility will not be changed.

    :param use_minimal_ui: Change the Solver UI to be "minimal", the
                           revert after a solve completes (or fails).
    :type use_minimal_ui: bool
    """
    if display_node_types is None:
        display_node_types = dict()
    if use_minimal_ui is None:
        use_minimal_ui = False
    options = ExecuteOptions(
        verbose=verbose,
        refresh=refresh,
        disable_viewport_two=disable_viewport_two,
        force_update=force_update,
        do_isolate=do_isolate,
        pre_solve_force_eval=pre_solve_force_eval,
        display_grid=display_grid,
        display_node_types=display_node_types,
        use_minimal_ui=use_minimal_ui,
    )
    return options
