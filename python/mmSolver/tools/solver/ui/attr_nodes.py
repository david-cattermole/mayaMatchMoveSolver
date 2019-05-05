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
            icon = ':/mmSolver_plug.png'
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
        icon = ':/mmSolver_attr.png'
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
            return const.ATTR_DEFAULT_MIN_VALUE
        v = d.get_min_value()
        if v is None:
            return const.ATTR_DEFAULT_MIN_VALUE
        return str(v)

    def maxValue(self):
        d = self.data().get('data')
        if d is None:
            return const.ATTR_DEFAULT_MAX_VALUE
        v = d.get_max_value()
        if v is None:
            return const.ATTR_DEFAULT_MAX_VALUE
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
        icon = ':/mmSolver_node.png'
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
            0: 'Attr',
            1: 'State',
            # 2: 'Min',
            # 3: 'Max',
        }
        return column_names

    def getGetAttrFuncFromIndex(self, index):
        get_attr_dict = {
            'Attr': 'name',
            'State': 'state',
            # 'Min': 'minValue',
            # 'Max': 'maxValue',
        }
        return self._getGetAttrFuncFromIndex(index, get_attr_dict)

    def getSetAttrFuncFromIndex(self, index):
        set_attr_dict = {
            'Attr': 'setName',
            'State': 'setState',
            # 'Min': 'setMinValue',
            # 'Max': 'setMaxValue',
        }
        return self._getSetAttrFuncFromIndex(index, set_attr_dict)
