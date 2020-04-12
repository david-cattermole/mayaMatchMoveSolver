# Copyright (C) 2018, 2019 David Cattermole.
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
Attribute nodes for the mmSolver Window UI.
"""

import maya.cmds

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore

import mmSolver.logger
import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.nodes as nodes
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class PlugNode(nodes.Node):
    def __init__(self, name,
                 parent=None,
                 data=None,
                 icon=None,
                 enabled=True,
                 editable=False,
                 selectable=True,
                 checkable=False,
                 neverHasChildren=False):
        if icon is None:
            icon = const.PLUG_ICON_NAME
        super(PlugNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            enabled=enabled,
            selectable=selectable,
            editable=editable,
            checkable=checkable,
            neverHasChildren=neverHasChildren)
        self.typeInfo = 'plug'

    def uuid(self):
        uuid = ''
        d = self.data()
        if not d:
            return uuid
        return d.get('uuid', '')

    def state(self):
        return ''

    def minMaxValue(self):
        return ''

    def stiffnessValue(self):
        return ''

    def smoothnessValue(self):
        return ''


def _get_attr_type(attr):
    if attr is None:
        return None
    attr_name = attr.get_attr().lower()
    attr_type = const.ATTR_TYPE_OTHER
    if 'translate' in attr_name:
        attr_type = const.ATTR_TYPE_TRANSLATE
    elif 'rotate' in attr_name:
        attr_type = const.ATTR_TYPE_ROTATE
    elif 'scale' in attr_name:
        attr_type = const.ATTR_TYPE_SCALE
    else:
        node_name = attr.get_node()
        node_type = maya.cmds.nodeType(node_name)
        node_type = node_type.lower()
        if node_type == 'camera':
            attr_type = const.ATTR_TYPE_CAMERA
        elif 'lens' in node_type:
            attr_type = const.ATTR_TYPE_LENS
    return attr_type


class AttrNode(PlugNode):
    def __init__(self, name,
                 data=None,
                 parent=None):
        attr = None
        if data is not None:
            attr = data.get('data')
        icon = const.ATTR_ICON_NAME
        attr_type = _get_attr_type(attr)
        if attr_type == const.ATTR_TYPE_TRANSLATE:
            icon = const.ATTR_TYPE_TRANSLATE_ICON_NAME
        elif attr_type == const.ATTR_TYPE_ROTATE:
            icon = const.ATTR_TYPE_ROTATE_ICON_NAME
        elif attr_type == const.ATTR_TYPE_SCALE:
            icon = const.ATTR_TYPE_SCALE_ICON_NAME
        elif attr_type == const.ATTR_TYPE_CAMERA:
            icon = const.ATTR_TYPE_CAMERA_ICON_NAME
        elif attr_type == const.ATTR_TYPE_LENS:
            icon = const.ATTR_TYPE_LENS_ICON_NAME
        else:
            icon = const.ATTR_TYPE_OTHER_ICON_NAME
        super(AttrNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            selectable=True,
            editable=False)
        self.typeInfo = 'attr'

    def state(self):
        d = self.data().get('data')
        state = const.ATTR_STATE_INVALID
        if d is None:
            pass
        elif d.is_static() is True:
            state = const.ATTR_STATE_STATIC
        elif d.is_animated() is True:
            state = const.ATTR_STATE_ANIMATED
        elif d.is_locked() is True:
            state = const.ATTR_STATE_LOCKED
        return state

    def minMaxValue(self):
        col = self.data().get('collection')
        attr = self.data().get('data')
        if attr is None or col is None:
            min_value = const.ATTR_DEFAULT_MIN_UI_VALUE
            max_value = const.ATTR_DEFAULT_MAX_UI_VALUE
            value = const.ATTR_DEFAULT_MIN_MAX_UI_VALUE
            value = value.format(min=min_value, max=max_value)
            return value
        min_enable = col.get_attribute_min_enable(attr)
        max_enable = col.get_attribute_max_enable(attr)
        min_value = col.get_attribute_min_value(attr)
        max_value = col.get_attribute_max_value(attr)
        if min_enable is False:
            min_value = const.ATTR_DEFAULT_MIN_UI_VALUE
        if max_enable is False:
            max_value = const.ATTR_DEFAULT_MAX_UI_VALUE
        value = const.ATTR_DEFAULT_MIN_MAX_UI_VALUE
        value = value.format(min=min_value, max=max_value)
        return str(value)

    def stiffnessValue(self):
        col = self.data().get('collection')
        attr = self.data().get('data')
        if attr is None or col is None:
            return const.ATTR_DEFAULT_STIFFNESS_UI_VALUE
        stiff_enable = col.get_attribute_stiffness_enable(attr)
        stiff_value = col.get_attribute_stiffness_variance(attr)
        if stiff_enable is False or stiff_value is None:
            stiff_value = const.ATTR_DEFAULT_STIFFNESS_UI_VALUE
        if isinstance(stiff_value, float):
            stiff_value = str(stiff_value)
        return stiff_value

    def smoothnessValue(self):
        col = self.data().get('collection')
        attr = self.data().get('data')
        if attr is None or col is None:
            return const.ATTR_DEFAULT_SMOOTHNESS_UI_VALUE
        smooth_enable = col.get_attribute_smoothness_enable(attr)
        smooth_value = col.get_attribute_smoothness_variance(attr)
        if smooth_enable is False or smooth_value is None:
            smooth_value = const.ATTR_DEFAULT_SMOOTHNESS_UI_VALUE
        if isinstance(smooth_value, float):
            smooth_value = str(smooth_value)
        return smooth_value

    def mayaNodeName(self):
        return 'node'

    def mayaAttrName(self):
        return 'attr'

    def mayaPlug(self):
        return None


class MayaNode(PlugNode):
    def __init__(self, name,
                 data=None,
                 parent=None):
        icon = const.NODE_ICON_NAME
        super(MayaNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            selectable=True,
            editable=False)
        self.typeInfo = 'node'

    def mayaNodeName(self):
        return 'node'

    def mayaAttrName(self):
        return 'attr'

    def mayaPlug(self):
        return None


class AttrModel(uimodels.ItemModel):
    def __init__(self, root, font=None):
        super(AttrModel, self).__init__(root, font=font)

    def defaultNodeType(self):
        return MayaNode

    def columnNames(self):
        column_names = {
            0: const.ATTR_COLUMN_NAME_ATTRIBUTE,
            1: const.ATTR_COLUMN_NAME_STATE,
            2: const.ATTR_COLUMN_NAME_VALUE_SMOOTHNESS,
            3: const.ATTR_COLUMN_NAME_VALUE_STIFFNESS,
            4: const.ATTR_COLUMN_NAME_VALUE_MIN_MAX,
            5: const.ATTR_COLUMN_NAME_UUID,
        }
        return column_names

    def columnAlignments(self):
        values = {
            const.ATTR_COLUMN_NAME_ATTRIBUTE: QtCore.Qt.AlignLeft,
            const.ATTR_COLUMN_NAME_STATE: QtCore.Qt.AlignCenter,
            const.ATTR_COLUMN_NAME_VALUE_MIN_MAX: QtCore.Qt.AlignCenter,
            const.ATTR_COLUMN_NAME_VALUE_STIFFNESS: QtCore.Qt.AlignCenter,
            const.ATTR_COLUMN_NAME_VALUE_SMOOTHNESS: QtCore.Qt.AlignCenter,
            const.ATTR_COLUMN_NAME_UUID: QtCore.Qt.AlignCenter,
        }
        return values

    def getGetAttrFuncFromIndex(self, index):
        get_attr_dict = {
            const.ATTR_COLUMN_NAME_ATTRIBUTE: 'name',
            const.ATTR_COLUMN_NAME_STATE: 'state',
            const.ATTR_COLUMN_NAME_VALUE_MIN_MAX: 'minMaxValue',
            const.ATTR_COLUMN_NAME_VALUE_STIFFNESS: 'stiffnessValue',
            const.ATTR_COLUMN_NAME_VALUE_SMOOTHNESS: 'smoothnessValue',
            const.ATTR_COLUMN_NAME_UUID: 'uuid',
        }
        return self._getGetAttrFuncFromIndex(index, get_attr_dict)

    def getSetAttrFuncFromIndex(self, index):
        set_attr_dict = {}
        return self._getSetAttrFuncFromIndex(index, set_attr_dict)

    def indexEnabled(self, index):
        node = index.internalPointer()
        return node.enabled()

    def indexEditable(self, index):
        return False
