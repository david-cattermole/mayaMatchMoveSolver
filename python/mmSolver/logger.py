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

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import sys
import os
import logging
import inspect
import time


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
        return None
    parentframe = stack[start][0]
    module = inspect.getmodule(parentframe)
    module_name = 'root'
    if module is not None:
        module_name = module.__name__

    logging.addLevelName(15, 'VERBOSE')  # between INFO and DEBUG.
    log = logging.getLogger(module_name)

    # Turn on debug logging.
    if level is None:
        debug = os.environ.get('MMSOLVER_DEBUG', 0)
        debug = bool(int(debug))
        if debug is True:
            level = logging.DEBUG

    # Maya Viewport messages
    if sys.modules.get('maya'):
        viewport_msgs = os.environ.get('MMSOLVER_VIEWPORT_MESSAGES', 1)
        viewport_msgs = bool(int(viewport_msgs))
        if viewport_msgs is True:
            add_maya_viewport_handler(log)

    if level is not None:
        log.setLevel(level)
    return log


def add_maya_viewport_handler(logger, level=None):
    if level is None:
        level = logging.WARNING
    handler = MayaViewportHandler()
    handler.setLevel(level)

    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return


class MayaViewportHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super(MayaViewportHandler, self).__init__(*args, **kwargs)
        self._last_few_message_hashes = collections.deque([], maxlen=3)
        self._time_of_last_message = 0

    def emit(self, record):
        """
        Emit a record.
        Output the record to the file, catering for rollover as described
        in doRollover().
        """
        try:
            record_format = self.format(record)

            # Avoid the same message being spammed at the user.
            #
            # We remember the last N number of messages and only print
            # new unique messages.
            #
            # Every few seconds, if the message is unique the message
            # is printed anyway to avoid a lack of user perceived
            # responsiveness.
            message_hash = hash(record_format)
            valid_message = message_hash not in self._last_few_message_hashes
            time_now = time.time()
            max_wait_time = 1.0  # in seconds
            waited_long_enough = (time_now - self._time_of_last_message) > max_wait_time
            if valid_message and waited_long_enough:
                self._last_few_message_hashes.append(message_hash)
                self._time_of_last_message = time_now
            else:
                return

            pre_text = ''
            post_text = ''
            fade_time = 1000  # in milliseconds
            if record.levelname == 'WARNING':
                pre_text = '<p style="color:#DCCE88";>'
                post_text = '</p>'
                fade_time = 2500
            elif record.levelname == 'ERROR':
                pre_text = '<p style="color:#FF5A5A";>'
                post_text = '</p>'
                fade_time = 5000
            elif record.levelname == 'CRITICAL':
                pre_text = '<p style="color:#FF0000";>'
                post_text = '</p>'
                fade_time = 10000
            message = pre_text + record_format + post_text

            import maya.cmds

            maya.cmds.inViewMessage(
                statusMessage=message,
                fadeStayTime=fade_time,
                fade=True,
                position='botLeft',
            )
        except (KeyboardInterrupt, SystemExit):
            raise
        except BaseException:
            self.handleError(record)
