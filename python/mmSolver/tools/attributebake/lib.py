# Copyright (C) 2021 Patcha Saheb Binginapalli.
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

import maya.cmds

import mmSolver.logger
import mmSolver.utils.time as time_utils
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.attributebake.constant as const


LOG = mmSolver.logger.get_logger()


def get_bake_frame_range(frame_range_mode, custom_start_frame, custom_end_frame):
    assert isinstance(frame_range_mode, pycompat.TEXT_TYPE)
    assert frame_range_mode in const.FRAME_RANGE_MODE_VALUES
    assert isinstance(custom_start_frame, pycompat.INT_TYPES)
    assert isinstance(custom_end_frame, pycompat.INT_TYPES)
    frame_range = None
    if frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
        frame_range = time_utils.get_maya_timeline_range_inner()
    elif frame_range_mode == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
        frame_range = time_utils.get_maya_timeline_range_outer()
    elif frame_range_mode == const.FRAME_RANGE_MODE_CUSTOM_VALUE:
        frame_range = time_utils.FrameRange(custom_start_frame, custom_end_frame)
    else:
        LOG.error("Invalid frame range mode: %r", frame_range_mode)
    return frame_range


def bake_attributes(
    nodes, attrs, start_frame, end_frame, smart_bake=False, preserve_outside_keys=False
):
    """
    Bake the attributes on nodes.

    .. note::
        If 'attrs' is empty, all keyable attributes are baked on the nodes.

    :param nodes: Nodes to bake.
    :param attrs: Attributes to bake. If empty, bake all keyable attributes.
    :param start_frame: Start frame to bake.
    :param end_frame: End frame to bake.
    :param smart_bake: Perform a "smart" bake - do not bake per-frame.
    :param preserve_outside_keys:
        Delete the keyframes outside the given frame range, or not.
    """
    assert isinstance(nodes, list)
    assert isinstance(start_frame, pycompat.INT_TYPES)
    assert isinstance(end_frame, pycompat.INT_TYPES)
    assert isinstance(smart_bake, bool)
    assert isinstance(preserve_outside_keys, bool)
    assert isinstance(attrs, list)
    if smart_bake is True:
        maya.cmds.bakeResults(
            nodes,
            time=(start_frame, end_frame),
            attribute=attrs,
            smart=int(smart_bake),
            preserveOutsideKeys=preserve_outside_keys,
            simulation=True,
            sparseAnimCurveBake=False,
            minimizeRotation=True,
        )
    else:
        maya.cmds.bakeResults(
            nodes,
            time=(start_frame, end_frame),
            attribute=attrs,
            preserveOutsideKeys=preserve_outside_keys,
            simulation=True,
            sparseAnimCurveBake=False,
            minimizeRotation=True,
        )
    return
