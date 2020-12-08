# Copyright (C) 2020 John Smith.
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
The main component of the user interface for the channel sensitivity
window.
"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.tools.removesolvernodes.ui.ui_removesolvernodes_layout as ui_removesolvernodes_layout
# import mmSolver.tools.removesolvernodes.lib as lib


LOG = mmSolver.logger.get_logger()


class RemoveSolverNodesLayout(QtWidgets.QWidget, ui_removesolvernodes_layout.Ui_Form):
    def __init__(self, parent=None, *args, **kwargs):
        super(RemoveSolverNodesLayout, self).__init__(*args, **kwargs)
        self.setupUi(self)

    def reset_options(self):
        self.markers_checkBox.setChecked(False)
        self.bundles_checkBox.setChecked(False)
        self.markerGroup_checkBox.setChecked(False)
        self.collections_checkBox.setChecked(False)
        self.otherNodes_checkBox.setChecked(False)