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

from functools import wraps

import maya.cmds

import mmSolver.logger

LOG = mmSolver.logger.get_logger()


def undo_chunk(func):
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
