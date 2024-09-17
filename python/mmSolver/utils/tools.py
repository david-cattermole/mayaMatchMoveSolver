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
Utilities for Tools to help develop and standardise inside mmSolver.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import uuid
from contextlib import contextmanager

import maya.cmds

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.utils.viewport as viewport_utils

LOG = mmSolver.logger.get_logger()


@contextmanager
def tool_context(
    use_undo_chunk=None,
    undo_chunk_name=None,
    restore_current_frame=None,
    pre_update_frame=None,
    post_update_frame=None,
    use_dg_evaluation_mode=None,
    disable_viewport=None,
    disable_viewport_mode=None,
):
    """
    Create a temporary tool context.

    If arguments are not given, the most stable and performant path is
    used. Arguments are used to remove ambiguity and force specific
    behaviour, and should therefore only be used when sure it is
    appropriate in your specific usage. The context is allowed to
    change default values dynamically, for example based on Maya
    version used or if a GUI is available.

    Example usage:

    >>> with tool_context() as tool_ctx:
    ...     # do something with Maya
    ...     maya.cmds.createNode('transform')

    :param use_undo_chunk:  Treat the commands inside this context as a
         single "chunk" of operations. This makes undo'ing faster, so
         we don't need to undo many small changes.
    :type use_undo_chunk: bool or None

    :param undo_chunk_name: The name of the undo chunk. This is
        displayed to the user in the Script Editor when undo'ing. This
        name is expected to be unique each time. Using the date/time
        or a UUID for this name may be helpful.
    :type undo_chunk_name: str or None

    :param restore_current_frame: Keep track of the current frame at
        the start of the context, then restore to the correct frame
        number at the end of the context.
    :type restore_current_frame: bool or None

    :param pre_update_frame: Before starting the context functions,
        make sure the current frame is updated to help trigger Maya
        to evaluate.
    :type pre_update_frame: bool or None

    :param post_update_frame: After finishing the context functions
        tell Maya to update the frame number to help trigger Maya
        evaluate attributes and nodes. NOTE: This function only works
        if `restore_current_frame` is True.
    :type post_update_frame: bool or None

    :param use_dg_evaluation_mode: Changes Maya's Evaluation mode to
        DG mode for the duration of the context then reset to
        whatever preference the user has (in the
        "Settings/Preferences" window). Using DG Evaluation can
        dramatically speed up evaluation across time for many tools in
        mmSolver (as tested on Maya 2017).
    :type use_dg_evaluation_mode: bool or None

    :param disable_viewport: Turn off the Viewport inside the context
        function, and enable it once the context finishes. This can be
        used to dramatically speed up functions that cause the Maya
        viewport to update many times.
    :type disable_viewport: bool or None

    :param disable_viewport_mode: Use the given technique to disable and
        re-enable the Maya viewport (using the "disable_viewport" flag).
    :type disable_viewport_mode: mmSolver.utils.constant.DISABLE_VIEWPORT_MODE_*_VALUE

    :return: Yields (returns) a unique context hash id.
    """
    # Defaults
    if use_undo_chunk is None:
        use_undo_chunk = True
    if undo_chunk_name is None:
        undo_chunk_name = str(uuid.uuid4())
    assert isinstance(undo_chunk_name, pycompat.TEXT_TYPE)
    if pre_update_frame is None:
        pre_update_frame = False
    if post_update_frame is None:
        post_update_frame = False
    if restore_current_frame is None:
        restore_current_frame = True
    if disable_viewport is None:
        disable_viewport = True
    if use_dg_evaluation_mode is None:
        # Force DG mode, because it evaluates with DG Context faster
        # (in Maya 2017).
        #
        # TODO: Test that DG mode is actually faster in Maya versions
        # other than 2017.
        use_dg_evaluation_mode = True
    # Save current state.
    current_frame = maya.cmds.currentTime(query=True)
    undo_state = maya.cmds.undoInfo(query=True, state=True)
    current_eval_mode = maya.cmds.evaluationManager(query=True, mode=True)

    # TRY...
    try:
        if disable_viewport is True:
            viewport_utils.viewport_turn_off(mode=disable_viewport_mode)
        if use_dg_evaluation_mode is True:
            # 'off' == turn off the Parallel mode.
            maya.cmds.evaluationManager(mode='off')
        if pre_update_frame is True:
            maya.cmds.currentTime(current_frame, edit=True, update=True)
        if use_undo_chunk is True and undo_state is True:
            maya.cmds.undoInfo(openChunk=True, chunkName=undo_chunk_name)

        yield undo_chunk_name

    finally:
        # FINALLY, restore original state.
        if use_undo_chunk is True and undo_state is True:
            maya.cmds.undoInfo(closeChunk=True, chunkName=undo_chunk_name)
        if restore_current_frame is True:
            maya.cmds.currentTime(current_frame, edit=True, update=post_update_frame)
        if use_dg_evaluation_mode is True:
            maya.cmds.evaluationManager(mode=current_eval_mode[0])
        if disable_viewport is True:
            viewport_utils.viewport_turn_on(mode=disable_viewport_mode)
