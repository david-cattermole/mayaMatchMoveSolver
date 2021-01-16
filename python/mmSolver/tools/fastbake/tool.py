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

import mmSolver.logger
import mmSolver.utils.configmaya as configmaya
import mmSolver.tools.fastbake.constant as const
import mmSolver.tools.fastbake.lib as lib

import maya.cmds as cmds
import maya.mel as mel
import time

LOG = mmSolver.logger.get_logger()

def main():
    #set configmaya defaults
    if not configmaya.get_scene_option(const.CONFIG_FRAME_RANGE_MODE_KEY):
        configmaya.set_scene_option(const.CONFIG_FRAME_RANGE_MODE_KEY, const.DEFAULT_FRAME_RANGE_MODE, add_attr=True)        
    if not configmaya.get_scene_option(const.CONFIG_FRAME_START_KEY):
        configmaya.set_scene_option(const.CONFIG_FRAME_START_KEY, const.DEFAULT_FRAME_START, add_attr=True)        
    if not configmaya.get_scene_option(const.CONFIG_FRAME_END_KEY):
        configmaya.set_scene_option(const.CONFIG_FRAME_END_KEY, const.DEFAULT_FRAME_END, add_attr=True)        
    if not configmaya.get_scene_option(const.CONFIG_SMARTBAKE_KEY):
        configmaya.set_scene_option(const.CONFIG_SMARTBAKE_KEY, const.DEFAULT_SMART_BAKE_STATE, add_attr=True)
    if not configmaya.get_scene_option(const.CONFIG_FROM_CHANNELBOX_KEY):
        configmaya.set_scene_option(const.CONFIG_FROM_CHANNELBOX_KEY, const.DEFAULT_FROM_CHANNELBOX_STATE, add_attr=True)    
    
    #get configmaya
    start_frame = configmaya.get_scene_option(const.CONFIG_FRAME_START_KEY)
    end_frame = configmaya.get_scene_option(const.CONFIG_FRAME_END_KEY)
    smart_bake_state = configmaya.get_scene_option(const.CONFIG_SMARTBAKE_KEY)
    from_channelbox_state = configmaya.get_scene_option(const.CONFIG_FROM_CHANNELBOX_KEY)
    channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')
    if from_channelbox_state == True:
        attrs = cmds.channelBox(channelBox, query=True, sma=True)
    else:
        attrs = []    

    #get selection and bake attributes
    nodes = cmds.ls(selection=True)
    if nodes != []:
        s = time.time()
        time.sleep(1)
        lib.bakeAttributes(nodes, int(start_frame), int(end_frame), bool(smart_bake_state), attrs)
        e = time.time()
        LOG.warn('Fastbake success. Time elapsed: %r secs', e-s)        
    else:
        LOG.warn("Please select at least on object.")
    return

def open_window():
    import mmSolver.tools.fastbake.ui.fastbake_window as window
    window.main()

