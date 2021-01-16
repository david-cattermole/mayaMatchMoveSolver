# Copyright (C) 2021 Patcha Saheb Binginapalli.
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
Window for the Create Controller tool.

Usage::

   import mmSolver.tools.createcontroller2.ui.createcontroller_window as createcontroller_window
   createcontroller_window.main()

"""

import mmSolver.ui.qtpyutils as qtpyutils
qtpyutils.override_binding_order()

import Qt.QtCore as QtCore
import Qt.QtGui as QtGui
import Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.tools.createcontroller2.ui.createcontroller_layout as createcontroller_layout
LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()

WINDOW_TITLE = "Create Controller"
WINDOW_WIDTH = 480
WINDOW_HEIGHT = 210

class CreateControllerWindow(BaseWindow):
    name = 'CreateControllerWindow'
    def __init__(self, parent=None, name=None):
        super(CreateControllerWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(createcontroller_layout.CreateControllerLayout)
        self.setWindowTitle(WINDOW_TITLE)
        self.setMinimumWidth(WINDOW_WIDTH)
        self.setMinimumHeight(WINDOW_HEIGHT)
        self.setMaximumWidth(WINDOW_WIDTH)
        self.setMaximumHeight(WINDOW_HEIGHT)
        self.setWindowFlags(QtCore.Qt.Tool)
        # Standard Buttons
        self.baseHideStandardButtons()
        # Hide irrelevant stuff
        self.baseHideMenuBar()
        self.baseHideProgressBar()

def main(show=True, auto_raise=True, delete=False):
    win = CreateControllerWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win