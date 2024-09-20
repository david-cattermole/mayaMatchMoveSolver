# Copyright (C) 2021 Patcha Saheb Binginapalli.

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

import time

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.constant as const_utils
import mmSolver.ui.channelboxutils as channelbox_utils
import mmSolver.tools.attributebake.constant as const
import mmSolver.tools.attributebake.lib as lib

LOG = mmSolver.logger.get_logger()


def _get_attributes(from_channelbox_state):
    attrs = []
    if from_channelbox_state is True:
        name = channelbox_utils.get_ui_name()
        attrs = maya.cmds.channelBox(name, query=True, selectedMainAttributes=True)
    return attrs or []


def main():
    nodes = maya.cmds.ls(selection=True)
    if len(nodes) == 0:
        LOG.warn("Please select at least 1 object.")
        return

    # Get configuration values
    frame_range_mode = configmaya.get_scene_option(
        const.CONFIG_FRAME_RANGE_MODE_KEY, const.DEFAULT_FRAME_RANGE_MODE
    )
    custom_start_frame = configmaya.get_scene_option(
        const.CONFIG_FRAME_START_KEY, const.DEFAULT_FRAME_START
    )
    custom_end_frame = configmaya.get_scene_option(
        const.CONFIG_FRAME_END_KEY, const.DEFAULT_FRAME_END
    )
    smart_bake_state = configmaya.get_scene_option(
        const.CONFIG_SMART_BAKE_KEY, const.DEFAULT_SMART_BAKE_STATE
    )
    from_channelbox_state = configmaya.get_scene_option(
        const.CONFIG_FROM_CHANNELBOX_KEY, const.DEFAULT_FROM_CHANNELBOX_STATE
    )
    preserve_outside_keys_state = configmaya.get_scene_option(
        const.CONFIG_PRESERVE_OUTSIDE_KEYS_KEY,
        const.DEFAULT_PRESERVE_OUTSIDE_KEYS_STATE,
    )

    frame_range = lib.get_bake_frame_range(
        frame_range_mode, custom_start_frame, custom_end_frame
    )

    attrs = _get_attributes(from_channelbox_state)
    if from_channelbox_state is True and len(attrs) == 0:
        LOG.warn("Please select at least 1 attribute in the Channel Box.")
        return

    # Bake attributes
    s = time.time()
    ctx = tools_utils.tool_context(
        use_undo_chunk=True,
        restore_current_frame=True,
        use_dg_evaluation_mode=True,
        disable_viewport=True,
        disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE,
    )
    with ctx:
        bake_success = False
        try:
            lib.bake_attributes(
                nodes,
                attrs,
                frame_range.start,
                frame_range.end,
                smart_bake=smart_bake_state,
                preserve_outside_keys=preserve_outside_keys_state,
            )
            bake_success = True
        except Exception:
            LOG.exception('Bake attributes failed.')
        finally:
            e = time.time()
            if bake_success is True:
                LOG.info('Bake attribute success. Time elapsed: %r secs', e - s)
            else:
                LOG.error('Bake attribute failed. Time elapsed: %r secs', e - s)
    return


def open_window():
    import mmSolver.tools.attributebake.ui.attrbake_window as window

    window.main()
