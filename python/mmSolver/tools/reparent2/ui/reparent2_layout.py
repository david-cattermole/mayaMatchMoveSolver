# Copyright (C) 2021 David Cattermole
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
The main component of the user interface for the reparent v2
window.

Create a (option-box-like) UI with widgets to control the tool:

- The frame range to bake (using the common "inner", "outer" and
  "custom" options).

- Keyframe placement; "smart bake" (Maya's "smart bake option"),
  "parent node", "every-frame".

- Change nodes to "rotation order" (automatically change a transform
  from XYZ while re-parenting).

.. todo::

    When using the "parent node" or "smart bake" options it should be
    possible for the user to tell the tool to calculate the animation
    curve tangent angles to match the in-between frames, without
    adding more keyframes.

    This would mean integrating the 'animCurveMatch' tool inside
    mmSolver.

"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.reparent2.ui.ui_reparent2_layout as ui_layout
import mmSolver.tools.reparent2.constant as const
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.time as time_utils


LOG = mmSolver.logger.get_logger()


class Reparent2Layout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(Reparent2Layout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Children and Parent Nodes
        self.childrenGetButton.clicked.connect(self.childrenGetClicked)
        self.parentClearButton.clicked.connect(self.parentClearClicked)
        self.parentGetButton.clicked.connect(self.parentGetClicked)

        # Frame Range Mode
        frame_range_modes = const.FRAME_RANGE_MODE_LABELS
        self.frameRangeModeComboBox.addItems(frame_range_modes)
        self.frameRangeModeComboBox.currentIndexChanged.connect(
            self.frameRangeModeIndexChanged
        )

        # Start and End Frame
        self.frameRangeStartSpinBox.valueChanged.connect(self.startFrameValueChanged)
        self.frameRangeEndSpinBox.valueChanged.connect(self.endFrameValueChanged)

        # Bake Mode
        bake_modes = const.BAKE_MODE_LABELS
        self.bakeModeComboBox.addItems(bake_modes)
        self.bakeModeComboBox.currentIndexChanged.connect(self.bakeModeIndexChanged)

        # Rotate Order Mode
        rotate_order_modes = const.ROTATE_ORDER_MODE_LABELS
        self.rotateOrderModeComboBox.addItems(rotate_order_modes)
        self.rotateOrderModeComboBox.currentIndexChanged.connect(
            self.rotateOrderModeIndexChanged
        )

        # Delete Static AnimCurves
        self.deleteStaticAnimCurvesCheckBox.stateChanged.connect(
            self.deleteStaticAnimCurvesStateChanged
        )

        # Populate the UI with data
        self.populateUi()

    def frameRangeModeIndexChanged(self, index):
        name = const.CONFIG_FRAME_RANGE_MODE_KEY
        value = const.FRAME_RANGE_MODE_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

        enable_custom = value == const.FRAME_RANGE_MODE_CUSTOM_VALUE
        self.frameRangeStartSpinBox.setEnabled(enable_custom)
        self.frameRangeEndSpinBox.setEnabled(enable_custom)

        frame_start = configmaya.get_scene_option(
            const.CONFIG_FRAME_START_KEY, default=const.DEFAULT_FRAME_START
        )
        frame_end = configmaya.get_scene_option(
            const.CONFIG_FRAME_END_KEY, default=const.DEFAULT_FRAME_END
        )
        if value == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
            frame_start, frame_end = time_utils.get_maya_timeline_range_inner()
        elif value == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
            frame_start, frame_end = time_utils.get_maya_timeline_range_outer()
        self.frameRangeStartSpinBox.setValue(frame_start)
        self.frameRangeEndSpinBox.setValue(frame_end)

    def startFrameValueChanged(self, value):
        name = const.CONFIG_FRAME_START_KEY
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def endFrameValueChanged(self, value):
        name = const.CONFIG_FRAME_END_KEY
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def bakeModeIndexChanged(self, index):
        name = const.CONFIG_BAKE_MODE_KEY
        value = const.BAKE_MODE_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def rotateOrderModeIndexChanged(self, index):
        name = const.CONFIG_ROTATE_ORDER_MODE_KEY
        value = const.ROTATE_ORDER_MODE_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def deleteStaticAnimCurvesStateChanged(self, value):
        name = const.CONFIG_DELETE_STATIC_ANIM_CURVES_KEY
        value = bool(value)
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def childrenGetClicked(self):
        import maya.cmds

        nodes = maya.cmds.ls(selection=True, long=True) or []
        self.setChildrenNodes(nodes)

    def parentGetClicked(self):
        import maya.cmds

        nodes = maya.cmds.ls(selection=True, long=True) or []
        self.setParentNode(nodes)

    def parentClearClicked(self):
        self.setParentNode([])

    def setChildrenNodes(self, nodes):
        text = ''
        for node in nodes:
            text += str(node) + ', '
        text = text.strip(' ').strip(',')
        self.childrenLineEdit.setText(text)

    def setParentNode(self, nodes):
        text = ''
        if len(nodes) > 0:
            text = str(nodes[0])
        self.parentLineEdit.setText(text)

    def getChildrenNodes(self):
        import maya.cmds

        texts = str(self.childrenLineEdit.text()).split(',')
        nodes = []
        for text in texts:
            tmp_nodes = maya.cmds.ls(text, long=True) or []
            for node in tmp_nodes:
                nodes.append(node)
        return nodes

    def getParentNode(self):
        import maya.cmds

        text = self.parentLineEdit.text()
        tmp_nodes = maya.cmds.ls(text, long=True) or []
        node = None
        if len(tmp_nodes) > 0:
            node = tmp_nodes[0]
        return node

    def reset_options(self):
        text = ''
        self.parentLineEdit.setText(text)
        self.childrenLineEdit.setText(text)

        name = const.CONFIG_FRAME_RANGE_MODE_KEY
        value = const.DEFAULT_FRAME_RANGE_MODE
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_FRAME_START_KEY
        value = const.DEFAULT_FRAME_START
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_FRAME_END_KEY
        value = const.DEFAULT_FRAME_END
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_BAKE_MODE_KEY
        value = const.DEFAULT_BAKE_MODE
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_ROTATE_ORDER_MODE_KEY
        value = const.DEFAULT_ROTATE_ORDER_MODE
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_DELETE_STATIC_ANIM_CURVES_KEY
        value = const.DEFAULT_DELETE_STATIC_ANIM_CURVES
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        self.populateUi()
        return

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        name = const.CONFIG_FRAME_RANGE_MODE_KEY
        value = configmaya.get_scene_option(
            name, default=const.DEFAULT_FRAME_RANGE_MODE
        )
        index = const.FRAME_RANGE_MODE_VALUES.index(value)
        label = const.FRAME_RANGE_MODE_LABELS[index]
        LOG.debug('key=%r value=%r', name, value)
        self.frameRangeModeComboBox.setCurrentText(label)

        enable_custom = value == const.FRAME_RANGE_MODE_CUSTOM_VALUE
        self.frameRangeStartSpinBox.setEnabled(enable_custom)
        self.frameRangeEndSpinBox.setEnabled(enable_custom)

        frame_start = configmaya.get_scene_option(
            const.CONFIG_FRAME_START_KEY, default=const.DEFAULT_FRAME_START
        )
        frame_end = configmaya.get_scene_option(
            const.CONFIG_FRAME_END_KEY, default=const.DEFAULT_FRAME_END
        )
        if value == const.FRAME_RANGE_MODE_TIMELINE_INNER_VALUE:
            frame_start, frame_end = time_utils.get_maya_timeline_range_inner()
        elif value == const.FRAME_RANGE_MODE_TIMELINE_OUTER_VALUE:
            frame_start, frame_end = time_utils.get_maya_timeline_range_outer()
        LOG.debug('key=%r value=%r', const.CONFIG_FRAME_START_KEY, frame_start)
        LOG.debug('key=%r value=%r', const.CONFIG_FRAME_END_KEY, frame_end)
        self.frameRangeStartSpinBox.setValue(frame_start)
        self.frameRangeEndSpinBox.setValue(frame_end)

        name = const.CONFIG_BAKE_MODE_KEY
        value = configmaya.get_scene_option(name, default=const.DEFAULT_BAKE_MODE)
        index = const.BAKE_MODE_VALUES.index(value)
        label = const.BAKE_MODE_LABELS[index]
        LOG.debug('key=%r value=%r', name, value)
        self.rotateOrderModeComboBox.setCurrentText(label)

        name = const.CONFIG_ROTATE_ORDER_MODE_KEY
        value = configmaya.get_scene_option(
            name, default=const.DEFAULT_ROTATE_ORDER_MODE
        )
        index = const.ROTATE_ORDER_MODE_VALUES.index(value)
        label = const.ROTATE_ORDER_MODE_LABELS[index]
        LOG.debug('key=%r value=%r', name, value)
        self.rotateOrderModeComboBox.setCurrentText(label)

        name = const.CONFIG_DELETE_STATIC_ANIM_CURVES_KEY
        value = configmaya.get_scene_option(
            name, default=const.DEFAULT_DELETE_STATIC_ANIM_CURVES
        )
        LOG.debug('key=%r value=%r', name, value)
        self.deleteStaticAnimCurvesCheckBox.setChecked(value)
        return
