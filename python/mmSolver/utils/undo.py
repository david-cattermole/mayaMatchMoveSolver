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
Undo related tools.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import uuid
from functools import wraps
from contextlib import contextmanager

import maya.cmds

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def wrap_as_undo_chunk(func):
    """
    Undo/Redo Chunk Decorator.

    Puts the wrapped 'func' into a single Maya Undo action.
    If 'func' raises and exception, we close the chunk.
    """
    @wraps(func)
    def _func(*args, **kwargs):
        try:
            # start an undo chunk
            maya.cmds.undoInfo(openChunk=True)
            return func(*args, **kwargs)
        finally:
            # after calling the func, end the undo chunk and undo
            maya.cmds.undoInfo(closeChunk=True)
            maya.cmds.undo()
    return _func


@contextmanager
def undo_chunk_context(name=None):
    """
    Create an undo chunk, using a context manager.

    Example usage:
    >>> with undo_chunk_context() as chunk_name:
    ...     # do something with Maya
    ...     maya.cmds.createNode('transform')

    :param name: A string to use as the unique undo chunk name, or
                 None to generate a random UUID.
    :type name: str or None

    :return: Yields (returns) the name of the undo chunk.
    """
    if name is None:
        name = str(uuid.uuid4())
    undo_state = maya.cmds.undoInfo(query=True, state=True)
    if undo_state is True:
        maya.cmds.undoInfo(openChunk=True, chunkName=name)
    yield name
    if undo_state is True:
        maya.cmds.undoInfo(closeChunk=True, chunkName=name)


@contextmanager
def no_undo_context():
    """
    All statements inside the 'with' block will not be added to the Undo stack.

    Example usage:
    >>> with no_undo_context():
    ...     # do something with Maya, not recorded in undo stack
    ...     maya.cmds.createNode('transform')

    :return: Yields (returns)
    """
    undo_state = maya.cmds.undoInfo(query=True, state=True)
    if undo_state is True:
        maya.cmds.undoInfo(stateWithoutFlush=False)
    yield
    if undo_state is True:
        maya.cmds.undoInfo(stateWithoutFlush=undo_state)
