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
Unified logging for the mmSolver package.
"""

import os
import logging
import inspect


def get_logger(level=None):
    """
    Returns a Logger object for logging events.

    If the environment variable 'MMSOLVER_DEBUG' is set to '1', and
    the 'level' kwarg is not given, the mmSolver logger will print
    debug messages.

    Example usage::

        import mmSolver.logger
        LOG = mmSolver.logger.get_logger()
        LOG.info('hello world')
        LOG.warning('be careful everyone')
        LOG.error('something bad has happened')

    :param level: Set the level for the newly created Logger object.
    :type level: str, int or None

    :return: A Logger object.
    """
    # The calling module name, in module hierarchy.
    # Source: https://gist.github.com/techtonik/2151727
    stack = inspect.stack()
    start = 1
    if len(stack) < start + 1:
        return ''
    parentframe = stack[start][0]
    module = inspect.getmodule(parentframe)
    module_name = 'root'
    if module is not None:
        module_name = module.__name__

    log = logging.getLogger(module_name)

    # Turn on debug logging.
    if level is None:
        debug = os.environ.get('MMSOLVER_DEBUG', 0)
        debug = bool(int(debug))
        if debug is True:
            level = logging.DEBUG

    if level is not None:
        log.setLevel(level)
    return log
