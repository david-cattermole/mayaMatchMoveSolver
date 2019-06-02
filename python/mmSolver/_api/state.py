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
Querying and setting global state information.
"""

import mmSolver.logger


LOG = mmSolver.logger.get_logger()

MM_SOLVER_IS_RUNNING = False
MM_SOLVER_USER_INTERRUPT = False


def is_solver_running():
    """
    Get the current state of the mmSolver command; is it running?

    :returns: State of mmSolver running.
    :rtype: bool
    """
    global MM_SOLVER_IS_RUNNING
    return MM_SOLVER_IS_RUNNING


def set_solver_running(value):
    """
    Get the current state of the mmSolver command; is it running?

    :param value: Value of the solver running, True or False.
    :type value: bool
    """
    assert isinstance(value, bool)
    global MM_SOLVER_IS_RUNNING
    MM_SOLVER_IS_RUNNING = value
    return


def get_user_interrupt():
    """
    Has the user requested to cancel the current solve?

    :returns: If the user wants to interrupt.
    :rtype: bool
    """
    global MM_SOLVER_USER_INTERRUPT
    return MM_SOLVER_USER_INTERRUPT


def set_user_interrupt(value):
    """
    Tell mmSolver if the user wants to interrupt.

    :param value: Value of the interrupt, True or False.
    :type value: bool
    """
    assert isinstance(value, bool)
    global MM_SOLVER_USER_INTERRUPT
    MM_SOLVER_USER_INTERRUPT = value
    return
