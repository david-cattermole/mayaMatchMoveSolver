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
Object nodes for the mmSolver Window UI.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore

import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.nodes as nodes


class ObjectNode(nodes.Node):
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
            icon = ':/mmSolver_object.png'
        super(ObjectNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            enabled=enabled,
            selectable=selectable,
            editable=editable,
            checkable=checkable,
            neverHasChildren=neverHasChildren)
        self.typeInfo = 'object'

    def weight(self):
        return ''

    def deviation(self):
        return ''


class MarkerNode(ObjectNode):
    def __init__(self, name,
                 data=None,
                 parent=None):
        icon = ':/mmSolver_marker.png'
        super(MarkerNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            selectable=True,
            editable=False)
        self.typeInfo = 'marker'

    def weight(self):
        """
        Get the current weight value of the marker.
        """
        weight = '-'
        d = self.data()
        mkr = d.get('marker')
        if mkr is None:
            return weight
        weight = mkr.get_weight()
        return str(weight)

    def deviation(self):
        """
        Get the current deviation value of the marker.
        """
        dev = '-'
        d = self.data()
        if not d:
            return dev
        mkr = d.get('marker')
        if mkr is None:
            return dev
        enable = mkr.get_enable()
        if not enable:
            return dev
        dev = mkr.get_deviation(times=None)
        if dev is None:
            dev = -1.0
        return '%.2f' % dev[0]


class CameraNode(ObjectNode):
    def __init__(self, name,
                 data=None,
                 parent=None):
        icon = ':/mmSolver_camera.png'
        super(CameraNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            selectable=True,
            editable=False)
        self.typeInfo = 'camera'

    def weight(self):
        return ''

    def deviation(self):
        """
        Get the current deviation value of the marker.
        """
        dev = '-'
        d = self.data()
        if not d:
            return dev
        cam = d.get('camera')
        if cam is None:
            return dev
        dev_value = cam.get_deviation()
        if dev_value is None:
            return dev
        return '%.2f' % dev_value


class BundleNode(ObjectNode):
    def __init__(self, name,
                 data=None,
                 parent=None):
        icon = ':/mmSolver_bundle.png'
        super(BundleNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            selectable=True,
            editable=False)
        self.typeInfo = 'bundle'

    def weight(self):
        return ''
        
    def deviation(self):
        return ''


class ObjectModel(uimodels.ItemModel):
    def __init__(self, root, font=None):
        super(ObjectModel, self).__init__(root, font=font)
        self._column_names = {
            0: 'Node',
            1: 'Weight',
            2: 'Deviation (px)',
        }
        self._node_attr_key = {
            'Node': 'name',
            'Weight': 'weight',
            'Deviation (px)': 'deviation',
        }

    def defaultNodeType(self):
        return MarkerNode

    def columnNames(self):
        column_names = {
            0: 'Node',
            1: 'Weight',
            2: 'Deviation (px)',
        }
        return column_names

    def columnAlignments(self):
        values = {
            'Node': QtCore.Qt.AlignLeft,
            'Weight': QtCore.Qt.AlignRight,
            'Deviation (px)': QtCore.Qt.AlignRight,
        }
        return values
    
    def getGetAttrFuncFromIndex(self, index):
        get_attr_dict = {
            'Node': 'name',
            'Weight': 'weight',
            'Deviation (px)': 'deviation',
        }
        return self._getGetAttrFuncFromIndex(index, get_attr_dict)

    def getSetAttrFuncFromIndex(self, index):
        set_attr_dict = {
            'Node': 'setName',
        }
        return self._getGetAttrFuncFromIndex(index, set_attr_dict)
