# Copyright (C) 2022 Patcha Saheb Binginapalli.
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
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.constant as const_utils
import mmSolver.tools.cameraobjectscaleadjust.lib as lib


LOG = mmSolver.logger.get_logger()


def main():
    selection = maya.cmds.ls(selection=True, long=True, type='transform') or []
    if not selection:
        LOG.warn('Please select scale rig(s) nodes.')
        return
    ctx = tools_utils.tool_context(
        use_undo_chunk=True,
        restore_current_frame=True,
        use_dg_evaluation_mode=True,
        disable_viewport=True,
        disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE,
    )
    with ctx:
        lib.remove_scale_rig(selection)
