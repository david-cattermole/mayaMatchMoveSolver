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

import time

import maya.cmds
import maya.mel

import mmSolver.logger
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.constant as const_utils
import mmSolver.tools.fastbake.constant as const
import mmSolver.tools.fastbake.lib as lib

LOG = mmSolver.logger.get_logger()


def _get_channel_box_name():
    cmd = 'global string $gChannelBoxName; $temp=$gChannelBoxName;'
    return maya.mel.eval(cmd)


def _get_attributes(from_channelbox_state):
    channel_box = _get_channel_box_name()
    attrs = []
    if from_channelbox_state is True:
        attrs = maya.cmds.channelBox(
            channel_box, query=True, selectedMainAttributes=True)
    return attrs


def main():
    nodes = maya.cmds.ls(selection=True)
    if len(nodes) == 0:
        LOG.warn("Please select at least 1 object.")
        return

    # Get configuration values
    frame_range_mode = configmaya.get_scene_option(
        const.CONFIG_FRAME_RANGE_MODE_KEY,
        const.DEFAULT_FRAME_RANGE_MODE)
    custom_start_frame = configmaya.get_scene_option(
        const.CONFIG_FRAME_START_KEY,
        const.DEFAULT_FRAME_START)
    custom_end_frame = configmaya.get_scene_option(
        const.CONFIG_FRAME_END_KEY,
        const.DEFAULT_FRAME_END)
    smart_bake_state = configmaya.get_scene_option(
        const.CONFIG_SMART_BAKE_KEY,
        const.DEFAULT_SMART_BAKE_STATE)
    from_channelbox_state = configmaya.get_scene_option(
        const.CONFIG_FROM_CHANNELBOX_KEY,
        const.DEFAULT_FROM_CHANNELBOX_STATE)

    frame_range = lib.get_bake_frame_range(
        frame_range_mode, custom_start_frame, custom_end_frame)
    attrs = _get_attributes(from_channelbox_state)

    # Bake attributes
    s = time.time()
    ctx = tools_utils.tool_context(
        use_undo_chunk=True,
        restore_current_frame=True,
        use_dg_evaluation_mode=True,
        disable_viewport=True,
        disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE)
    with ctx:
        try:
            lib.bake_attributes(
                nodes, attrs,
                frame_range.start,
                frame_range.end,
                smart_bake_state)
        except Exception as e:
            LOG.error(e)
        finally:
            e = time.time()
            LOG.warn('Bake attribute success. Time elapsed: %r secs', e-s)
    return


def open_window():
    import mmSolver.tools.fastbake.ui.fastbake_window as window
    window.main()
