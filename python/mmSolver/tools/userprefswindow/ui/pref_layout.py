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
The 'Pref' layout, the contents of the userpreferences window.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtGui as QtGui
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.utils.python_compat as pycompat
import mmSolver.tools.userpreferences.lib as userprefs_lib
import mmSolver.tools.userpreferences.constant as pref_const
import mmSolver.tools.userprefswindow.ui.ui_pref_layout as ui_pref_layout

LOG = mmSolver.logger.get_logger()


class PrefLayout(QtWidgets.QWidget, ui_pref_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(PrefLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self._config = None
        return

    def set_config(self, config):
        self._config = config
        self.populateUI(self._config)
        return

    def populateUI(self, config):
        self.updateAddNewMarkersToWidget(config)
        self.updateAddNewLinesToWidget(config)
        self.updateSolverUIValidateOnOpenWidget(config)
        self.updateSolverUIShowValidateButtonWidget(config)
        self.updateSolverUIAllowObjectRelationsWidget(config)
        self.updateSolverUIMinimalUIWhileSolvingWidget(config)
        return

    def updateAddNewMarkersToWidget(self, config):
        key = pref_const.REG_EVNT_ADD_NEW_MKR_TO_KEY
        value = userprefs_lib.get_value(config, key)
        label = userprefs_lib.get_label_from_value(key, value)
        assert isinstance(label, pycompat.TEXT_TYPE)
        labels = userprefs_lib.get_labels(key)
        self.addNewMarkersToComboBox.clear()
        self.addNewMarkersToComboBox.addItems(labels)
        self.addNewMarkersToComboBox.setCurrentText(label)
        return

    def getAddNewMarkersToConfigValue(self):
        key = pref_const.REG_EVNT_ADD_NEW_MKR_TO_KEY
        label = self.addNewMarkersToComboBox.currentText()
        value = userprefs_lib.get_value_from_label(key, label)
        return value

    def updateAddNewLinesToWidget(self, config):
        key = pref_const.REG_EVNT_ADD_NEW_LINE_TO_KEY
        value = userprefs_lib.get_value(config, key)
        label = userprefs_lib.get_label_from_value(key, value)
        assert isinstance(label, pycompat.TEXT_TYPE)
        labels = userprefs_lib.get_labels(key)
        self.addNewLinesToComboBox.clear()
        self.addNewLinesToComboBox.addItems(labels)
        self.addNewLinesToComboBox.setCurrentText(label)
        return

    def getAddNewLinesToConfigValue(self):
        key = pref_const.REG_EVNT_ADD_NEW_LINE_TO_KEY
        label = self.addNewLinesToComboBox.currentText()
        value = userprefs_lib.get_value_from_label(key, label)
        return value

    def updateSolverUIValidateOnOpenWidget(self, config):
        key = pref_const.SOLVER_UI_VALIDATE_ON_OPEN_KEY
        value = userprefs_lib.get_value(config, key)
        label = userprefs_lib.get_label_from_value(key, value)
        assert isinstance(label, pycompat.TEXT_TYPE)
        labels = userprefs_lib.get_labels(key)
        self.validateSolverOnUIOpenComboBox.clear()
        self.validateSolverOnUIOpenComboBox.addItems(labels)
        self.validateSolverOnUIOpenComboBox.setCurrentText(label)
        return

    def getSolverUIValidateOnOpenConfigValue(self):
        key = pref_const.SOLVER_UI_VALIDATE_ON_OPEN_KEY
        label = self.validateSolverOnUIOpenComboBox.currentText()
        value = userprefs_lib.get_value_from_label(key, label)
        return value

    def updateSolverUIShowValidateButtonWidget(self, config):
        key = pref_const.SOLVER_UI_SHOW_VALIDATE_BTN_KEY
        value = userprefs_lib.get_value(config, key)
        label = userprefs_lib.get_label_from_value(key, value)
        assert isinstance(label, pycompat.TEXT_TYPE)
        labels = userprefs_lib.get_labels(key)
        self.showValidateButtonComboBox.clear()
        self.showValidateButtonComboBox.addItems(labels)
        self.showValidateButtonComboBox.setCurrentText(label)
        return

    def getSolverUIShowValidateButtonConfigValue(self):
        key = pref_const.SOLVER_UI_SHOW_VALIDATE_BTN_KEY
        label = self.showValidateButtonComboBox.currentText()
        value = userprefs_lib.get_value_from_label(key, label)
        return value

    def updateSolverUIAllowObjectRelationsWidget(self, config):
        key = pref_const.SOLVER_UI_ALLOW_OBJECT_RELATIONS_KEY
        value = userprefs_lib.get_value(config, key)
        label = userprefs_lib.get_label_from_value(key, value)
        assert isinstance(label, pycompat.TEXT_TYPE)
        labels = userprefs_lib.get_labels(key)
        self.allowObjectRelationsComboBox.clear()
        self.allowObjectRelationsComboBox.addItems(labels)
        self.allowObjectRelationsComboBox.setCurrentText(label)
        return

    def getSolverUIAllowObjectRelationsConfigValue(self):
        key = pref_const.SOLVER_UI_ALLOW_OBJECT_RELATIONS_KEY
        label = self.allowObjectRelationsComboBox.currentText()
        value = userprefs_lib.get_value_from_label(key, label)
        return value

    def updateSolverUIMinimalUIWhileSolvingWidget(self, config):
        key = pref_const.SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY
        value = userprefs_lib.get_value(config, key)
        label = userprefs_lib.get_label_from_value(key, value)
        assert isinstance(label, pycompat.TEXT_TYPE)
        labels = userprefs_lib.get_labels(key)
        self.minimalUIWhileSolvingComboBox.clear()
        self.minimalUIWhileSolvingComboBox.addItems(labels)
        self.minimalUIWhileSolvingComboBox.setCurrentText(label)
        return

    def getSolverUIMinimalUIWhileSolvingConfigValue(self):
        key = pref_const.SOLVER_UI_MINIMAL_UI_WHILE_SOLVING_KEY
        label = self.minimalUIWhileSolvingComboBox.currentText()
        value = userprefs_lib.get_value_from_label(key, label)
        return value
