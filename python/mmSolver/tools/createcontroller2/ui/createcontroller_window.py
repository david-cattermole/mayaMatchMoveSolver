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
# import mmSolver.ui.helputils as helputils
import mmSolver.utils.tools as tools_utils
import mmSolver.utils.constant as const_utils
import mmSolver.tools.createcontroller2.ui.createcontroller_layout as createcontroller_layout

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()
WINDOW_TITLE = "Create Controller"


class CreateControllerWindow(BaseWindow):
    name = 'CreateControllerWindow'

    def __init__(self, parent=None, name=None):
        super(CreateControllerWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(createcontroller_layout.CreateControllerLayout)

        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowFlags(QtCore.Qt.Tool)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.createBtn.show()
        self.applyBtn.show()
        self.resetBtn.show()
        # self.helpBtn.show()
        self.closeBtn.show()
        self.createBtn.setText('Create Locator/Group')
        self.applyBtn.setText('Create Controller')

        self.createBtn.clicked.connect(self.create_locator_group)
        self.applyBtn.clicked.connect(self.create_controller)
        self.resetBtn.clicked.connect(self.reset_options)
        # self.helpBtn.clicked.connect(self.help)

        # Hide irrelevant stuff
        self.baseHideMenuBar()
        self.baseHideProgressBar()

    def create_locator_group(self):
        form = self.getSubForm()
        ctx = tools_utils.tool_context(
            use_undo_chunk=True,
            restore_current_frame=True,
            use_dg_evaluation_mode=True,
            disable_viewport=True,
            disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE)
        with ctx:
            form.create_locator_group()
        return

    def create_controller(self):
        form = self.getSubForm()
        ctx = tools_utils.tool_context(
            use_undo_chunk=True,
            restore_current_frame=True,
            use_dg_evaluation_mode=True,
            disable_viewport=True,
            disable_viewport_mode=const_utils.DISABLE_VIEWPORT_MODE_VP1_VALUE)
        with ctx:
            form.create_controller_button_clicked()
        return

    def reset_options(self):
        form = self.getSubForm()
        form.reset_options()


def main(show=True, auto_raise=True, delete=False):
    win = CreateControllerWindow.open_window(
        show=show,
        auto_raise=auto_raise,
        delete=delete
    )
    return win
