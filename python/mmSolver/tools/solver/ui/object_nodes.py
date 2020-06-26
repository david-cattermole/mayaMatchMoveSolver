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
import Qt.QtGui as QtGui

import mmSolver.logger
import mmSolver.ui.uimodels as uimodels
import mmSolver.ui.nodes as uinodes
import mmSolver.tools.solver.constant as const


LOG = mmSolver.logger.get_logger()


class ObjectNode(uinodes.Node):
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
            icon = const.OBJECT_ICON_NAME
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

    def objectColor(self):
        return None

    def uuid(self):
        uuid = ''
        d = self.data()
        if not d:
            return uuid
        return d.get('uuid', '')

    def weight(self):
        return const.OBJECT_DEFAULT_WEIGHT_UI_VALUE

    def deviation(self):
        return const.OBJECT_DEFAULT_DEVIATION_UI_VALUE

    def avgDeviation(self):
        return const.OBJECT_DEFAULT_DEVIATION_UI_VALUE

    def maxDeviation(self):
        return const.OBJECT_DEFAULT_DEVIATION_UI_VALUE


class MarkerNode(ObjectNode):
    def __init__(self, name,
                 data=None,
                 parent=None):
        icon = const.MARKER_ICON_NAME
        super(MarkerNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            selectable=True,
            editable=False)
        self.typeInfo = 'marker'

    def objectColor(self):
        color = None
        d = self.data()
        mkr = d.get('marker')
        if mkr is None:
            return color
        enable = bool(mkr.get_enable())
        if enable is False:
            color = QtGui.QColor(QtCore.Qt.darkGray)
        return color

    def weight(self):
        """
        Get the current weight value of the marker.
        """
        weight = const.OBJECT_DEFAULT_WEIGHT_UI_VALUE
        d = self.data()
        mkr = d.get('marker')
        if mkr is None:
            return weight
        weight = mkr.get_weight()
        return str(weight)

    def avgDeviation(self):
        """
        Get the current deviation value of the marker.
        """
        dev = const.OBJECT_DEFAULT_DEVIATION_UI_VALUE
        d = self.data()
        if not d:
            return dev
        mkr = d.get('marker')
        if mkr is None:
            return dev
        dev_value = mkr.get_average_deviation()
        if dev_value is None:
            return dev
        if dev_value < 0:
            return dev
        return '%.2f' % dev_value

    def deviation(self):
        """
        Get the current deviation value of the marker.
        """
        dev = const.OBJECT_DEFAULT_DEVIATION_UI_VALUE
        d = self.data()
        if not d:
            return dev
        mkr = d.get('marker')
        if mkr is None:
            return dev
        enable = mkr.get_enable()
        if not enable:
            return dev
        dev_values = mkr.get_deviation(times=None)
        if dev_values is None:
            return dev
        if dev_values[0] < 0:
            return dev
        return '%.2f' % dev_values[0]

    def maxDeviation(self):
        """
        Get the current deviation value of the marker.
        """
        dev = const.OBJECT_DEFAULT_DEVIATION_UI_VALUE
        d = self.data()
        if not d:
            return dev
        mkr = d.get('marker')
        if mkr is None:
            return dev
        dev_value, dev_frame = mkr.get_maximum_deviation()
        if dev_value is None:
            return dev
        if dev_value < 0:
            return dev
        return '%.2f @ %s' % (dev_value, dev_frame)


class CameraNode(ObjectNode):
    def __init__(self, name,
                 data=None,
                 parent=None):
        icon = const.CAMERA_ICON_NAME
        super(CameraNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            selectable=True,
            editable=False)
        self.typeInfo = 'camera'

    def objectColor(self):
        return None

    def weight(self):
        return const.OBJECT_DEFAULT_WEIGHT_UI_VALUE

    def deviation(self):
        """
        Get the current deviation of the for the camera.
        """
        return '-'

    def avgDeviation(self):
        """
        Get the average deviation value of the camera.
        """
        return '-'

    def maxDeviation(self):
        """
        Get the average deviation value of the camera.
        """
        return '-'


class BundleNode(ObjectNode):
    def __init__(self, name,
                 data=None,
                 parent=None):
        icon = const.BUNDLE_ICON_NAME
        super(BundleNode, self).__init__(
            name,
            data=data,
            parent=parent,
            icon=icon,
            selectable=True,
            editable=False)
        self.typeInfo = 'bundle'

    def objectColor(self):
        return None

    def weight(self):
        return const.OBJECT_DEFAULT_WEIGHT_UI_VALUE

    def deviation(self):
        return const.OBJECT_DEFAULT_DEVIATION_UI_VALUE

    def avgDeviation(self):
        return const.OBJECT_DEFAULT_DEVIATION_UI_VALUE

    def maxDeviation(self):
        return const.OBJECT_DEFAULT_DEVIATION_UI_VALUE


class ObjectModel(uimodels.ItemModel):

    def __init__(self, root, font=None):
        super(ObjectModel, self).__init__(root, font=font)
        return

    def defaultNodeType(self):
        return MarkerNode

    def columnNames(self):
        column_names = {
            0: const.OBJECT_COLUMN_NAME_NODE,
            1: const.OBJECT_COLUMN_NAME_WEIGHT,
            2: const.OBJECT_COLUMN_NAME_DEVIATION_FRAME,
            3: const.OBJECT_COLUMN_NAME_DEVIATION_AVERAGE,
            4: const.OBJECT_COLUMN_NAME_DEVIATION_MAXIMUM,
            5: const.OBJECT_COLUMN_NAME_UUID,
        }
        return column_names

    def columnAlignments(self):
        values = {
            const.OBJECT_COLUMN_NAME_NODE: QtCore.Qt.AlignLeft,
            const.OBJECT_COLUMN_NAME_WEIGHT: QtCore.Qt.AlignRight,
            const.OBJECT_COLUMN_NAME_DEVIATION_FRAME: QtCore.Qt.AlignCenter,
            const.OBJECT_COLUMN_NAME_DEVIATION_AVERAGE: QtCore.Qt.AlignCenter,
            const.OBJECT_COLUMN_NAME_DEVIATION_MAXIMUM: QtCore.Qt.AlignCenter,
            const.OBJECT_COLUMN_NAME_UUID: QtCore.Qt.AlignRight,
        }
        return values

    def getGetAttrFuncFromIndex(self, index):
        get_attr_dict = {
            const.OBJECT_COLUMN_NAME_NODE: 'name',
            const.OBJECT_COLUMN_NAME_WEIGHT: 'weight',
            const.OBJECT_COLUMN_NAME_DEVIATION_FRAME: 'deviation',
            const.OBJECT_COLUMN_NAME_DEVIATION_AVERAGE: 'avgDeviation',
            const.OBJECT_COLUMN_NAME_DEVIATION_MAXIMUM: 'maxDeviation',
            const.OBJECT_COLUMN_NAME_UUID: 'uuid',
        }
        return self._getLookUpFuncFromIndex(index, get_attr_dict)

    def getColorFuncFromIndex(self, index):
        color_dict = {
            const.OBJECT_COLUMN_NAME_NODE: 'objectColor',
        }
        return self._getLookUpFuncFromIndex(index, color_dict)

    def getSetAttrFuncFromIndex(self, index):
        set_attr_dict = {}
        return self._getLookUpFuncFromIndex(index, set_attr_dict)

    def indexEnabled(self, index):
        node = index.internalPointer()
        return node.enabled()

    def indexEditable(self, index):
        return False
