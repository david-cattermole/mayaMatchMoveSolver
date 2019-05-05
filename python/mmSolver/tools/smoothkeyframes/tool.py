# Copyright (C) 2019 Anil Reddy, David Cattermole.
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
Smooths the selected keyframes.
"""

import maya.cmds

import mmSolver.logger
import mmSolver.utils.constant as utils_const
import mmSolver.tools.smoothkeyframes.lib as lib

LOG = mmSolver.logger.get_logger()


def main():
    """
    Smooth the selected keyframes in the Graph Editor.

    Usage::

    1) Select keyframes in Graph Editor.

    2) Run tool

    3) Keyframe values will be smoothed.

    """
    key_attrs = maya.cmds.keyframe(query=True, name=True) or []
    if len(key_attrs) == 0:
        msg = (
            'Please select keyframes '
            '(in the Graph Editor) to smooth.'
        )
        LOG.warning(msg)
        return
    
    for key_attr in key_attrs:
        selected_keyframes = maya.cmds.keyframe(
            key_attr,
            query=True,
            selected=True
        )
        if len(selected_keyframes) == 0:
            msg = (
                'Please select keyframes '
                '(in the Graph Editor) to smooth.'
            )
            LOG.warning(msg)
            continue

        smooth_type = utils_const.SMOOTH_TYPE_FOURIER
        width = 2
        blend_smooth_type = utils_const.SMOOTH_TYPE_GAUSSIAN
        blend_width = 2
        lib.smooth_animcurve(
            key_attr,
            selected_keyframes,
            smooth_type,
            width,
            blend_smooth_type,
            blend_width)
    return
