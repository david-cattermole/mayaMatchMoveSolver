# Copyright (C) 2023 David Cattermole
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
The main component of the user interface for the surface cluster
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.surfacecluster.ui.ui_surfacecluster_layout as ui_layout
import mmSolver.tools.surfacecluster.constant as const
import mmSolver.utils.configmaya as configmaya
import mmSolver.utils.constant as utils_const


LOG = mmSolver.logger.get_logger()


class SurfaceClusterLayout(QtWidgets.QWidget, ui_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(SurfaceClusterLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Create Mode
        self.createModeComboBox.addItems(const.CREATE_MODE_LABELS)
        self.createModeComboBox.currentIndexChanged.connect(self.createModeIndexChanged)

        # Open_Paint_Weights
        self.openPaintWeightsCheckBox.stateChanged.connect(
            self.openPaintWeightsCheckedChanged
        )

        # Populate the UI with data
        self.populateUi()

    def createModeIndexChanged(self, index):
        name = const.CONFIG_CREATE_MODE_KEY
        value = const.CREATE_MODE_VALUES[index]
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def openPaintWeightsCheckedChanged(self, value):
        name = const.CONFIG_OPEN_PAINT_WEIGHTS_KEY
        value = bool(value)
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def reset_options(self):
        name = const.CONFIG_CREATE_MODE_KEY
        value = const.DEFAULT_CREATE_MODE
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)

        name = const.CONFIG_OPEN_PAINT_WEIGHTS_KEY
        value = const.DEFAULT_OPEN_PAINT_WEIGHTS
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)
        self.populateUi()

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        name = const.CONFIG_CREATE_MODE_KEY
        value = configmaya.get_scene_option(name, default=const.DEFAULT_CREATE_MODE)
        value_index = const.CREATE_MODE_VALUES.index(value)
        label = const.CREATE_MODE_LABELS[value_index]
        LOG.debug('key=%r value=%r', name, value)
        self.createModeComboBox.setCurrentText(label)

        name = const.CONFIG_OPEN_PAINT_WEIGHTS_KEY
        value = configmaya.get_scene_option(
            name, default=const.DEFAULT_OPEN_PAINT_WEIGHTS
        )
        LOG.debug('key=%r value=%r', name, value)
        self.openPaintWeightsCheckBox.setChecked(value)
        return
