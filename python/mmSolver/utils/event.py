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
Event registry and triggers for python functions.

The event system modelled is a 'publish/subscribe' pattern.
https://en.wikipedia.org/wiki/Publish%E2%80%93subscribe_pattern

This module does not use any external python dependencies, but does
rely on Maya's in-built 'maya.utils.executeDeferred()' function.

This event system automatically combines multiple functions with
single objects into a function that is run once with multiple
arguments. The reason for this, is to reduce function calls and
improve performance when operating on many arguments at once.


Example usage::

   >>> import mmSolver.utils.event as event_utils
   >>> def my_function(**kwargs):
   ...     print(kwargs)
   ...
   >>> event_utils.add_function_to_event('my_event', my_function, deferred=True)
   >>> event_utils.trigger_event('my_event', number=42)
   >>>
   {'number': 42}
   >>> for i in range(3):
   ...     event_utils.trigger_event('my_event', number=i)
   ...
   >>>
   {'number': [0, 1, 2]}

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import collections
import maya.utils
import mmSolver.logger
import mmSolver.utils.python_compat as pycompat


LOG = mmSolver.logger.get_logger()
_EVENT_NAMES_BLOCKED = set()
__EVENT_ARGUMENTS = collections.defaultdict(list)
__EVENT_FUNCTIONS = collections.defaultdict(list)
__EVENT_UNIQUE_FUNCTION_HASHES = collections.defaultdict(set)


class BlockedEvents(object):
    """
    A context manager used to stop events from being triggered.

    Example usage::

       >>> event_name = 'my_event'
       >>> with event_utils.BlockedEvents([event_name]):
       ...    # do stuff, and don't trigger events named 'my_event'.
       ...    pass

    """

    def __init__(self, event_names_to_block):
        assert isinstance(event_names_to_block, (set, list, tuple))
        self.__event_names_to_block = set(event_names_to_block)
        self.__old_blocked_event_names = set()

    def __enter__(self):
        global _EVENT_NAMES_BLOCKED
        self.__old_blocked_event_names = set(_EVENT_NAMES_BLOCKED)
        _EVENT_NAMES_BLOCKED |= self.__event_names_to_block
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        global _EVENT_NAMES_BLOCKED
        _EVENT_NAMES_BLOCKED = self.__old_blocked_event_names


def trigger_event(event_name, **kwargs):
    """
    Inform the event-driven system that 'event_name' has occurred.

    .. note:: It is possible the event will not be triggered if the
        user has called for it to be blocked. Do not assume the event
        will always be triggered.
    """
    global _EVENT_NAMES_BLOCKED
    global __EVENT_ARGUMENTS

    assert isinstance(event_name, pycompat.TEXT_TYPE)
    if event_name in _EVENT_NAMES_BLOCKED:
        LOG.debug('blocked trigger_event: event_name=%r kwargs=%r', event_name, kwargs)
        return

    LOG.debug('trigger_event: event_name=%r kwargs=%r', event_name, kwargs)
    __EVENT_ARGUMENTS[event_name].append(kwargs)

    maya.utils.executeDeferred(lambda: __call_functions(event_name))
    return


def __call_functions(event_name):
    LOG.debug('call_functions: event_name=%r', event_name)
    global __EVENT_ARGUMENTS
    global __EVENT_FUNCTIONS
    global __EVENT_UNIQUE_FUNCTION_HASHES

    kwargs_list = __EVENT_ARGUMENTS[event_name]
    if len(kwargs_list) == 0:
        # Don't run if there are no arguments to use.
        return
    # Clear all the arguments, so we cannot run the functions again.
    __EVENT_ARGUMENTS[event_name] = []

    # Combine keyword arguments.
    kwargs = collections.defaultdict(list)
    for kw in kwargs_list:
        for key, value in kw.items():
            if isinstance(value, list):
                kwargs[key] += value
            if isinstance(value, (tuple, set)):
                kwargs[key] += list(value)
            else:
                kwargs[key].append(value)

    functions = __EVENT_FUNCTIONS.get(event_name, [])
    assert isinstance(functions, list)

    kwargs['event_name'] = event_name
    for func in functions:
        if callable(func) is False:
            continue
        func(**kwargs)
    return


def add_function_to_event(event_name, func, deferred=True):
    LOG.debug(
        'add_function_to_event: event_name=%r func=%r deferred=%r',
        event_name,
        func,
        deferred,
    )
    assert isinstance(event_name, pycompat.TEXT_TYPE)
    assert callable(func) is True
    assert isinstance(deferred, bool)

    def deferred_func(**kwargs):
        maya.utils.executeDeferred(lambda: func(**kwargs))

    run_func = func
    if deferred is True:
        run_func = deferred_func

    global __EVENT_FUNCTIONS
    global __EVENT_UNIQUE_FUNCTION_HASHES
    func_hash = hash(func)
    func_hashes = __EVENT_UNIQUE_FUNCTION_HASHES.get(event_name, set())
    if func_hash not in func_hashes:
        __EVENT_UNIQUE_FUNCTION_HASHES[event_name].add(func_hash)
        __EVENT_FUNCTIONS[event_name].append(run_func)
    return
