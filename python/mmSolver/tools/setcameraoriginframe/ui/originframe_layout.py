# Copyright (C) 2022 David Cattermole
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
The main component of the user interface for the Set Camera Origin Frame
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.setcameraoriginframe.ui.ui_originframe_layout as ui_originframe_layout
import mmSolver.tools.setcameraoriginframe.constant as const
import mmSolver.utils.configmaya as configmaya


LOG = mmSolver.logger.get_logger()


class OriginFrameLayout(QtWidgets.QWidget, ui_originframe_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(OriginFrameLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

        # Scene Scale
        self.sceneScale_doubleSpinBox.valueChanged.connect(
            self.sceneScaleSpinBoxValueChanged
        )

        # Populate the UI with data
        self.populateUi()

    def sceneScaleSpinBoxValueChanged(self, value):
        name = const.CONFIG_SCENE_SCALE_KEY
        value = float(value)
        configmaya.set_scene_option(name, value, add_attr=True)
        LOG.debug('key=%r value=%r', name, value)

    def reset_options(self):
        name = const.CONFIG_SCENE_SCALE_KEY
        value = const.DEFAULT_SCENE_SCALE
        configmaya.set_scene_option(name, value)
        LOG.debug('key=%r value=%r', name, value)
        self.populateUi()

    def populateUi(self):
        """
        Update the UI for the first time the class is created.
        """
        name = const.CONFIG_SCENE_SCALE_KEY
        value = configmaya.get_scene_option(name, default=const.DEFAULT_SCENE_SCALE)
        LOG.debug('key=%r value=%r', name, value)
        self.sceneScale_doubleSpinBox.setValue(value)
        return
