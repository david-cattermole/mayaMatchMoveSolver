# Copyright (C) 2020 David Cattermole.
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
Dialog UI for the Set Attribute Details tool.

Example Usage::

 import maya.cmds
 import mmSolver.api as mmapi

 col_name = 'name'
 col = mmapi.Collection()
 if maya.cmds.objExists(col_name):
     col = mmapi.Collection(node=col_name)
 else:
     col = mmapi.Collection().create_node(col_name)

 import mmSolver.tools.setattributedetails.ui.dialog as dialog
 import mmSolver.tools.setattributedetails.lib as lib
 import mmSolver.tools.setattributedetails.tool as tool

 attr_list = [
     mmapi.Attribute(node='pSphere1', attr='translateX'),
     mmapi.Attribute(node='pSphere1', attr='translateY'),
     mmapi.Attribute(node='pSphere1', attr='translateZ'),

 ]
 dialog.main(col, attr_list)

"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt as Qt
import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.uimodels as uimodels
import mmSolver.api as mmapi
import mmSolver.tools.setattributedetails.constant as const
import mmSolver.tools.setattributedetails.lib as lib
import mmSolver.tools.setattributedetails.ui.ui_dialog as ui_dialog

LOG = mmSolver.logger.get_logger()


def set_internal_value(attr_detail_dict, attr, value_name, value):
    if attr is None:
        return attr_detail_dict
    kwargs = {value_name: value}
    attr_name = attr.get_name()
    value = attr_detail_dict.get(attr_name)
    value = lib.attr_detail_from_previous(value, **kwargs)
    attr_detail_dict[attr_name] = value
    return attr_detail_dict


class Dialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super(Dialog, self).__init__(parent)
        self.col = None
        self.current_attr = None
        self.attr_list = []
        self.attr_detail_dict = {}

        self.setObjectName(const.DIALOG_OBJECT_NAME)
        self.ui = ui_dialog.Ui_Form()
        self.ui.setupUi(self)
        self.create_connections()
        self.set_default_values()
        self.create_list_view()
        return

    def create_connections(self):
        self.ui.locked_radioButton.toggled.connect(
            self.ui.valueRange_groupBox.setDisabled
        )
        self.ui.locked_radioButton.toggled.connect(
            self.ui.animCurve_groupBox.setDisabled
        )
        self.ui.locked_radioButton.toggled.connect(
            self.ui.statistics_groupBox.setDisabled
        )

        self.ui.static_radioButton.toggled.connect(
            self.ui.valueRange_groupBox.setEnabled
        )
        self.ui.static_radioButton.toggled.connect(
            self.ui.animCurve_groupBox.setDisabled
        )
        self.ui.static_radioButton.toggled.connect(
            self.ui.statistics_groupBox.setDisabled
        )

        self.ui.animated_radioButton.toggled.connect(
            self.ui.valueRange_groupBox.setEnabled
        )
        self.ui.animated_radioButton.toggled.connect(
            self.ui.animCurve_groupBox.setEnabled
        )
        self.ui.animated_radioButton.toggled.connect(
            self.ui.statistics_groupBox.setEnabled
        )

        self.ui.max_checkBox.toggled.connect(self.ui.max_doubleSpinBox.setEnabled)
        self.ui.min_checkBox.toggled.connect(self.ui.min_doubleSpinBox.setEnabled)

        # self.ui.stiffness_checkBox.toggled.connect(
        #     self.ui.stiffnessVariance_doubleSpinBox.setEnabled
        # )
        # self.ui.stiffness_checkBox.toggled.connect(
        #     self.ui.stiffnessWeight_doubleSpinBox.setEnabled
        # )

        # self.ui.smoothness_checkBox.toggled.connect(
        #     self.ui.smoothnessVariance_doubleSpinBox.setEnabled
        # )
        # self.ui.smoothness_checkBox.toggled.connect(
        #     self.ui.smoothnessWeight_doubleSpinBox.setEnabled
        # )

        self.ui.locked_radioButton.toggled.connect(self.set_internal_state_locked)
        self.ui.static_radioButton.toggled.connect(self.set_internal_state_static)
        self.ui.animated_radioButton.toggled.connect(self.set_internal_state_animated)

        self.ui.min_checkBox.toggled.connect(self.set_internal_min_enable)
        self.ui.max_checkBox.toggled.connect(self.set_internal_max_enable)
        self.ui.min_doubleSpinBox.valueChanged.connect(self.set_internal_min_value)
        self.ui.max_doubleSpinBox.valueChanged.connect(self.set_internal_max_value)

        # self.ui.stiffness_checkBox.toggled.connect(self.set_internal_stiffness_enable)
        # self.ui.stiffnessVariance_doubleSpinBox.valueChanged.connect(
        #     self.set_internal_stiffness_variance
        # )
        # self.ui.stiffnessWeight_doubleSpinBox.valueChanged.connect(
        #     self.set_internal_stiffness_weight
        # )

        # self.ui.smoothness_checkBox.toggled.connect(self.set_internal_smoothness_enable)
        # self.ui.smoothnessVariance_doubleSpinBox.valueChanged.connect(
        #     self.set_internal_smoothness_variance
        # )
        # self.ui.smoothnessWeight_doubleSpinBox.valueChanged.connect(
        #     self.set_internal_smoothness_weight
        # )

        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.buttonBox.rejected.connect(self.reject)

    def set_internal_state_locked(self, checked):
        value = mmapi.ATTR_STATE_INVALID
        if checked:
            value = mmapi.ATTR_STATE_LOCKED
        self.attr_detail_dict = set_internal_value(
            self.attr_detail_dict.copy(), self.current_attr, 'state', value
        )

    def set_internal_state_static(self, checked):
        value = mmapi.ATTR_STATE_INVALID
        if checked:
            value = mmapi.ATTR_STATE_STATIC
        self.attr_detail_dict = set_internal_value(
            self.attr_detail_dict.copy(), self.current_attr, 'state', value
        )

    def set_internal_state_animated(self, checked):
        value = mmapi.ATTR_STATE_INVALID
        if checked:
            value = mmapi.ATTR_STATE_ANIMATED
        self.attr_detail_dict = set_internal_value(
            self.attr_detail_dict.copy(), self.current_attr, 'state', value
        )

    def set_internal_min_enable(self, value):
        self.attr_detail_dict = set_internal_value(
            self.attr_detail_dict.copy(), self.current_attr, 'min_enable', value
        )

    def set_internal_min_value(self, value):
        self.attr_detail_dict = set_internal_value(
            self.attr_detail_dict.copy(), self.current_attr, 'min_value', value
        )

    def set_internal_max_enable(self, value):
        self.attr_detail_dict = set_internal_value(
            self.attr_detail_dict.copy(), self.current_attr, 'max_enable', value
        )

    def set_internal_max_value(self, value):
        self.attr_detail_dict = set_internal_value(
            self.attr_detail_dict.copy(), self.current_attr, 'max_value', value
        )

    # def set_internal_stiffness_enable(self, value):
    #     self.attr_detail_dict = set_internal_value(
    #         self.attr_detail_dict.copy(), self.current_attr, 'stiffness_enable', value
    #     )

    # def set_internal_stiffness_variance(self, value):
    #     self.attr_detail_dict = set_internal_value(
    #         self.attr_detail_dict.copy(), self.current_attr, 'stiffness_variance', value
    #     )

    # def set_internal_stiffness_weight(self, value):
    #     self.attr_detail_dict = set_internal_value(
    #         self.attr_detail_dict.copy(), self.current_attr, 'stiffness_weight', value
    #     )

    # def set_internal_smoothness_enable(self, value):
    #     self.attr_detail_dict = set_internal_value(
    #         self.attr_detail_dict.copy(), self.current_attr, 'smoothness_enable', value
    #     )

    # def set_internal_smoothness_variance(self, value):
    #     self.attr_detail_dict = set_internal_value(
    #         self.attr_detail_dict.copy(),
    #         self.current_attr,
    #         'smoothness_variance',
    #         value,
    #     )

    # def set_internal_smoothness_weight(self, value):
    #     self.attr_detail_dict = set_internal_value(
    #         self.attr_detail_dict.copy(), self.current_attr, 'smoothness_weight', value
    #     )

    def set_default_values(self):
        # Disable the stiffness and smoothness feature.
        self.ui.animCurve_groupBox.setVisible(False)

        self.ui.min_doubleSpinBox.setEnabled(False)
        self.ui.max_doubleSpinBox.setEnabled(False)
        # self.ui.stiffnessVariance_doubleSpinBox.setEnabled(False)
        # self.ui.smoothnessVariance_doubleSpinBox.setEnabled(False)
        # self.ui.stiffnessWeight_doubleSpinBox.setEnabled(False)
        # self.ui.smoothnessWeight_doubleSpinBox.setEnabled(False)
        self.ui.statistics_groupBox.setEnabled(False)

        self.ui.min_checkBox.setChecked(const.MIN_ENABLE_DEFAULT_VALUE)
        self.ui.max_checkBox.setChecked(const.MAX_ENABLE_DEFAULT_VALUE)

        # self.ui.stiffness_checkBox.setChecked(const.STIFFNESS_ENABLE_DEFAULT_VALUE)
        # self.ui.stiffnessVariance_doubleSpinBox.setValue(
        #     const.STIFFNESS_VARIANCE_DEFAULT_VALUE
        # )
        # self.ui.stiffnessWeight_doubleSpinBox.setValue(
        #     const.STIFFNESS_WEIGHT_DEFAULT_VALUE
        # )

        # self.ui.smoothness_checkBox.setChecked(const.SMOOTHNESS_ENABLE_DEFAULT_VALUE)
        # self.ui.smoothnessVariance_doubleSpinBox.setValue(
        #     const.SMOOTHNESS_VARIANCE_DEFAULT_VALUE
        # )
        # self.ui.smoothnessWeight_doubleSpinBox.setValue(
        #     const.SMOOTHNESS_WEIGHT_DEFAULT_VALUE
        # )

        self.window().setWindowTitle(const.WINDOW_TITLE_BAR)
        return

    def create_list_view(self):
        self.attribute_model = uimodels.StringDataListModel()
        self.ui.attribute_listView.setModel(self.attribute_model)

        self.attribute_filter_model = QtCore.QSortFilterProxyModel()
        self.attribute_filter_model.setSourceModel(self.attribute_model)
        self.attribute_filter_model.setDynamicSortFilter(False)

        self.ui.attribute_listView.setModel(self.attribute_filter_model)
        self.ui.attribute_listView.setSelectionMode(
            QtWidgets.QAbstractItemView.SingleSelection
        )

        self.attribute_sel_model = self.ui.attribute_listView.selectionModel()
        self.attribute_sel_model.selectionChanged.connect(self.selectionChanged)
        return

    @QtCore.Slot(QtCore.QItemSelection, QtCore.QItemSelection)
    def selectionChanged(self, selected, deselected):
        select_indexes = [idx for idx in selected.indexes()]
        role = QtCore.Qt.UserRole
        for idx in select_indexes:
            data = idx.data(role)
            if data is None:
                continue
            self.current_attr = data
            attr_name = data.get_name()
            attr_detail = self.attr_detail_dict.get(attr_name)
            self.set_detail_values(attr_detail)
        return

    def set_attributes(self, col, attr_list):
        self.col = col
        self.attr_list = attr_list
        self.attr_detail_dict = lib.convert_attributes_to_detail_values(col, attr_list)
        string_data_list = []
        for attr in attr_list:
            node_name = attr.get_node(full_path=False)
            attr_name = attr.get_attr(long_name=True)
            name = '{0}.{1}'.format(node_name, attr_name)
            string_data_list.append((name, attr))
        self.attribute_model.setStringDataList(string_data_list)
        return

    def get_state(self):
        state = mmapi.ATTR_STATE_INVALID
        is_locked = self.ui.locked_radioButton.isChecked()
        is_static = self.ui.static_radioButton.isChecked()
        is_animated = self.ui.animated_radioButton.isChecked()
        if is_locked is True:
            state = mmapi.ATTR_STATE_LOCKED
        elif is_static is True:
            state = mmapi.ATTR_STATE_STATIC
        elif is_animated is True:
            state = mmapi.ATTR_STATE_ANIMATED
        else:
            # Invalid state.
            pass
        return state

    def set_state(self, state):
        assert isinstance(state, int)
        self.ui.locked_radioButton.setChecked(state == mmapi.ATTR_STATE_LOCKED)
        self.ui.static_radioButton.setChecked(state == mmapi.ATTR_STATE_STATIC)
        self.ui.animated_radioButton.setChecked(state == mmapi.ATTR_STATE_ANIMATED)
        return

    def get_min_enable(self):
        return self.ui.min_checkBox.isChecked()

    def set_min_enable(self, value):
        assert isinstance(value, bool)
        self.ui.min_checkBox.setChecked(value)
        return

    def get_min_value(self):
        return self.ui.min_doubleSpinBox.value()

    def set_min_value(self, value):
        assert isinstance(value, float)
        self.ui.min_doubleSpinBox.setValue(value)
        return

    def get_max_enable(self):
        return self.ui.max_checkBox.isChecked()

    def set_max_enable(self, value):
        assert isinstance(value, bool)
        self.ui.max_checkBox.setChecked(value)
        return

    def get_max_value(self):
        return self.ui.max_doubleSpinBox.value()

    def set_max_value(self, value):
        assert isinstance(value, float)
        self.ui.max_doubleSpinBox.setValue(value)
        return

    # def get_stiffness_enable(self):
    #     return self.ui.stiffness_checkBox.isChecked()

    # def set_stiffness_enable(self, value):
    #     assert isinstance(value, bool)
    #     self.ui.stiffness_checkBox.setChecked(value)
    #     return

    # def get_stiffness_variance(self):
    #     return self.ui.stiffnessVariance_doubleSpinBox.value()

    # def set_stiffness_variance(self, value):
    #     assert isinstance(value, float)
    #     self.ui.stiffnessVariance_doubleSpinBox.setValue(value)
    #     return

    # def get_stiffness_weight(self):
    #     return self.ui.stiffnessWeight_doubleSpinBox.value()

    # def set_stiffness_weight(self, value):
    #     assert isinstance(value, float)
    #     self.ui.stiffnessWeight_doubleSpinBox.setValue(value)
    #     return

    # def get_smoothness_enable(self):
    #     return self.ui.smoothness_checkBox.isChecked()

    # def set_smoothness_enable(self, value):
    #     assert isinstance(value, bool)
    #     self.ui.smoothness_checkBox.setChecked(value)
    #     return

    # def get_smoothness_variance(self):
    #     return self.ui.smoothnessVariance_doubleSpinBox.value()

    # def set_smoothness_variance(self, value):
    #     assert isinstance(value, float)
    #     self.ui.smoothnessVariance_doubleSpinBox.setValue(value)
    #     return

    # def get_smoothness_weight(self):
    #     return self.ui.smoothnessWeight_doubleSpinBox.value()

    # def set_smoothness_weight(self, value):
    #     assert isinstance(value, float)
    #     self.ui.smoothnessWeight_doubleSpinBox.setValue(value)
    #     return

    def get_curve_min(self):
        return self.ui.minStats_doubleSpinBox.value()

    def set_curve_min(self, value):
        assert isinstance(value, float)
        self.ui.minStats_doubleSpinBox.setValue(value)
        return

    def get_curve_max(self):
        return self.ui.maxStats_doubleSpinBox.value()

    def set_curve_max(self, value):
        assert isinstance(value, float)
        self.ui.maxStats_doubleSpinBox.setValue(value)
        return

    def get_curve_mean(self):
        return self.ui.meanStats_doubleSpinBox.value()

    def set_curve_mean(self, value):
        assert isinstance(value, float)
        self.ui.meanStats_doubleSpinBox.setValue(value)
        return

    def get_curve_variance(self):
        return self.ui.varianceStats_doubleSpinBox.value()

    def set_curve_variance(self, value):
        assert isinstance(value, float)
        self.ui.varianceStats_doubleSpinBox.setValue(value)
        return

    def get_curve_frame_variance(self):
        return self.ui.frameVarianceStats_doubleSpinBox.value()

    def set_curve_frame_variance(self, value):
        assert isinstance(value, float)
        self.ui.frameVarianceStats_doubleSpinBox.setValue(value)
        return

    def get_curve_max_variance(self):
        return self.ui.maxVarianceStats_doubleSpinBox.value()

    def set_curve_max_variance(self, value):
        assert isinstance(value, float)
        self.ui.maxVarianceStats_doubleSpinBox.setValue(value)
        return

    def set_detail_values(self, values):
        assert isinstance(values, lib.AttrDetail)
        self.set_state(values.state)

        self.set_min_enable(values.min_enable)
        self.set_min_value(values.min_value)

        self.set_max_enable(values.max_enable)
        self.set_max_value(values.max_value)

        # self.set_stiffness_enable(values.stiffness_enable)
        # self.set_stiffness_variance(values.stiffness_variance)
        # self.set_stiffness_weight(values.stiffness_weight)

        # self.set_smoothness_enable(values.smoothness_enable)
        # self.set_smoothness_variance(values.smoothness_variance)
        # self.set_smoothness_weight(values.smoothness_weight)

        curve_min = values.curve_min or const.CURVE_MIN_DEFAULT_VALUE
        curve_max = values.curve_max or const.CURVE_MAX_DEFAULT_VALUE
        curve_mean = values.curve_mean or const.CURVE_MEAN_DEFAULT_VALUE
        curve_variance = values.curve_variance or const.CURVE_VARIANCE_DEFAULT_VALUE
        curve_frame_variance = (
            values.curve_frame_variance or const.CURVE_FRAME_VARIANCE_DEFAULT_VALUE
        )
        curve_max_variance = (
            values.curve_max_variance or const.CURVE_MAX_VARIANCE_DEFAULT_VALUE
        )
        self.set_curve_min(curve_min)
        self.set_curve_max(curve_max)
        self.set_curve_mean(curve_mean)
        self.set_curve_variance(curve_variance)
        self.set_curve_frame_variance(curve_frame_variance)
        self.set_curve_max_variance(curve_max_variance)
        return

    def get_detail_values_for_attribute(self, attr):
        attr_name = attr.get_name()
        value = self.attr_detail_dict.get(attr_name)
        return value


def main(col, attr_list):
    app, parent_window = uiutils.getParent()
    dialog = Dialog(parent=parent_window)
    dialog.set_attributes(col, attr_list)
    ret = dialog.exec_()
    status = ret == QtWidgets.QDialog.Accepted
    return status, dialog


def warn_user(title, text):
    LOG.warn(text.replace('\n', ' '))
    app, parent_window = uiutils.getParent()
    Qt.QtWidgets.QMessageBox.warning(parent_window, title, text)
    return
