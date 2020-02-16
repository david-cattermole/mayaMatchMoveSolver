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

    def minValue(self):
        return ''

    def maxValue(self):
        return ''


class AttrNode(PlugNode):
    def __init__(self, name,
                 data=None,
                 parent=None):
        icon = const.ATTR_ICON_NAME
        attrs_x = ['translateX', 'rotateX', 'scaleX']
        attrs_y = ['translateY', 'rotateY', 'scaleY']
        attrs_z = ['translateZ', 'rotateZ', 'scaleZ']
        if name in attrs_x:
            icon = const.ATTR_X_ICON_NAME
        elif name in attrs_y:
            icon = const.ATTR_Y_ICON_NAME
        elif name in attrs_z:
            icon = const.ATTR_Z_ICON_NAME
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

    def minValue(self):
        d = self.data().get('data')
        if d is None:
            return const.ATTR_DEFAULT_MIN_UI_VALUE
        v = d.get_min_value()
        if v is None:
            return const.ATTR_DEFAULT_MIN_UI_VALUE
        return str(v)

    def maxValue(self):
        d = self.data().get('data')
        if d is None:
            return const.ATTR_DEFAULT_MAX_UI_VALUE
        v = d.get_max_value()
        if v is None:
            return const.ATTR_DEFAULT_MAX_UI_VALUE
        return str(v)

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
            2: const.ATTR_COLUMN_NAME_VALUE_MIN,
            3: const.ATTR_COLUMN_NAME_VALUE_MAX,
            4: const.ATTR_COLUMN_NAME_UUID,
        }
        return column_names

    def columnAlignments(self):
        values = {
            const.ATTR_COLUMN_NAME_ATTRIBUTE: QtCore.Qt.AlignLeft,
            const.ATTR_COLUMN_NAME_STATE: QtCore.Qt.AlignRight,
            const.ATTR_COLUMN_NAME_VALUE_MIN: QtCore.Qt.AlignCenter,
            const.ATTR_COLUMN_NAME_VALUE_MAX: QtCore.Qt.AlignCenter,
            const.ATTR_COLUMN_NAME_UUID: QtCore.Qt.AlignCenter,
        }
        return values

    def getGetAttrFuncFromIndex(self, index):
        get_attr_dict = {
            const.ATTR_COLUMN_NAME_ATTRIBUTE: 'name',
            const.ATTR_COLUMN_NAME_STATE: 'state',
            const.ATTR_COLUMN_NAME_VALUE_MIN: 'minValue',
            const.ATTR_COLUMN_NAME_VALUE_MAX: 'maxValue',
            const.ATTR_COLUMN_NAME_UUID: 'uuid',
        }
        return self._getGetAttrFuncFromIndex(index, get_attr_dict)

    def getSetAttrFuncFromIndex(self, index):
        set_attr_dict = {
            # const.ATTR_COLUMN_NAME_ATTRIBUTE: 'setName',
            # const.ATTR_COLUMN_NAME_STATE: 'setState',
            # const.ATTR_COLUMN_NAME_VALUE_MIN: 'setMinValue',
            # const.ATTR_COLUMN_NAME_VALUE_MAX: 'setMaxValue',
        }
        return self._getSetAttrFuncFromIndex(index, set_attr_dict)
