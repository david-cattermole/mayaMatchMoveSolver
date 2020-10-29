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

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
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
        LOG.warn('set_config: %r', config)
        self._config = config
        self.populateUI(self._config)
        return

    def populateUI(self, config):
        self.updateAddNewMarkersToWidget(config)
        return

    def updateAddNewMarkersToWidget(self, config):
        key = pref_const.REG_EVNT_ADD_NEW_MKR_TO_KEY
        value = userprefs_lib.get_value(config, key)
        label = userprefs_lib.get_label_from_value(key, value)
        assert isinstance(label, basestring)
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
