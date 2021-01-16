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
"""
The main component of the user interface for the fast bake
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.fastbake.ui.ui_fastbake_layout as ui_layout
import mmSolver.tools.fastbake.tool as tool
import mmSolver.tools.fastbake.constant as const
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.time as time_utils

LOG = mmSolver.logger.get_logger()

class FastBakeLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(FastBakeLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        #create connections
        self.frame_range_combo.currentIndexChanged.connect(self.frameRangeModeIndexChanged)  
        self.start_frame_text.editingFinished.connect(self.startFrameValueChanged)        
        self.end_frame_text.editingFinished.connect(self.endFrameValueChanged)
        self.smart_bake_cbox.stateChanged.connect(self.smartBakeValueChanged)
        self.channel_box_cbox.stateChanged.connect(self.fromChannelBoxValueChanged)
        self.fast_bake_btn.clicked.connect(tool.main)
        self.reset_btn.clicked.connect(self.resetWidgets)

        self.populateUi()

    def frameRangeModeIndexChangedHelper(self, v):
        start_name = const.CONFIG_FRAME_START_KEY
        end_name = const.CONFIG_FRAME_END_KEY      
        if v  == "fb_timeline_inner":
            self.start_frame_text.setEnabled(False)
            self.end_frame_text.setEnabled(False)
            self.smart_bake_cbox.setEnabled(True)
            frame_start, frame_end = time_utils.get_maya_timeline_range_inner()
            self.start_frame_text.setText(str(frame_start))
            self.end_frame_text.setText(str(frame_end))
            configmaya.set_scene_option(start_name, frame_start, add_attr=True)
            configmaya.set_scene_option(end_name, frame_end, add_attr=True)
        if v == "fb_timeline_outer":
            self.start_frame_text.setEnabled(False)
            self.end_frame_text.setEnabled(False) 
            self.smart_bake_cbox.setEnabled(True)       
            frame_start, frame_end = time_utils.get_maya_timeline_range_outer()
            self.start_frame_text.setText(str(frame_start))
            self.end_frame_text.setText(str(frame_end))
            configmaya.set_scene_option(start_name, frame_start, add_attr=True)
            configmaya.set_scene_option(end_name, frame_end, add_attr=True)                         
        if v == "fb_custom":
            self.start_frame_text.setEnabled(True)
            self.end_frame_text.setEnabled(True)
            self.smart_bake_cbox.setEnabled(False)
            self.smart_bake_cbox.setChecked(False)

    def frameRangeModeIndexChanged(self):
    	name = const.CONFIG_FRAME_RANGE_MODE_KEY
    	index = self.frame_range_combo.currentIndex()
    	value = const.FRAME_RANGE_MODE_VALUES[index]
    	configmaya.set_scene_option(name, value, add_attr=True)
        self.frameRangeModeIndexChangedHelper(value)

    def startFrameValueChanged(self):
    	name = const.CONFIG_FRAME_START_KEY
    	value = self.start_frame_text.text()
    	configmaya.set_scene_option(name, value, add_attr=True)

    def endFrameValueChanged(self):
    	name = const.CONFIG_FRAME_END_KEY
    	value = self.end_frame_text.text()
    	configmaya.set_scene_option(name, value, add_attr=True)

    def smartBakeValueChanged(self):
        name = const.CONFIG_SMARTBAKE_KEY
        if self.smart_bake_cbox.isChecked(): value = True    
        else: value = False
        configmaya.set_scene_option(name, value, add_attr=True)

    def fromChannelBoxValueChanged(self):
        name = const.CONFIG_FROM_CHANNELBOX_KEY
        if self.channel_box_cbox.isChecked(): value = True
        else: value = False
        configmaya.set_scene_option(name, value, add_attr=True)

    def resetWidgets(self):
        self.frame_range_combo.setCurrentIndex(0)
        self.smart_bake_cbox.setChecked(False)
        self.channel_box_cbox.setChecked(False)

    def setConfigDefaults(self):
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

    def populateUi(self):
        self.setConfigDefaults()        
        #get configmaya values and set them
    	frame_range_mode = configmaya.get_scene_option(const.CONFIG_FRAME_RANGE_MODE_KEY)
        start_frame = configmaya.get_scene_option(const.CONFIG_FRAME_START_KEY)
        end_frame = configmaya.get_scene_option(const.CONFIG_FRAME_END_KEY)
        smart_bake_state = configmaya.get_scene_option(const.CONFIG_SMARTBAKE_KEY)
        from_channelbox_state = configmaya.get_scene_option(const.CONFIG_FROM_CHANNELBOX_KEY)
        #frame range mode and start,end frame values
        if str(frame_range_mode) == "fb_timeline_inner":
            self.frame_range_combo.setCurrentIndex(0)          
        if str(frame_range_mode) == "fb_timeline_outer":
            self.frame_range_combo.setCurrentIndex(1)
        if str(frame_range_mode) == "fb_custom":
            self.frame_range_combo.setCurrentIndex(2)
            self.start_frame_text.setText(str(start_frame))
            self.end_frame_text.setText(str(end_frame))          
        self.frameRangeModeIndexChangedHelper(str(frame_range_mode))
        #smart bake checkbox state        
        self.smart_bake_cbox.setChecked(bool(smart_bake_state))
        #from channel box checkbox state        
        self.channel_box_cbox.setChecked(bool(from_channelbox_state))
        return