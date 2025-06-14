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
Window for the Attribute bake tool.

Usage::

   import mmSolver.tools.attributebake.ui.attrbake_window as window
   window.main()

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.tools.attributebake.constant as const
import mmSolver.tools.attributebake.ui.attrbake_layout as attrbake_layout
import mmSolver.tools.attributebake.tool as tool

LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def _open_help():
    src = helputils.get_help_source()
    page = 'tools_attributetools.html#bake-attributes'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


class AttributeBakeWindow(BaseWindow):
    name = 'AttributeBakeWindow'

    def __init__(self, parent=None, name=None):
        super(AttributeBakeWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(attrbake_layout.AttributeBakeLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowType(qtpyutils.WINDOW_TYPE_DIALOG)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.closeBtn.show()
        self.applyBtn.setText('Bake')

        self.applyBtn.clicked.connect(tool.main)

        # Hide irrelevant stuff
        self.baseHideProgressBar()

        self.add_menus(self.menubar)
        self.menubar.show()

    def add_menus(self, menubar):
        edit_menu = QtWidgets.QMenu('Edit', menubar)
        commonmenus.create_edit_menu_items(
            edit_menu, reset_settings_func=self.reset_options
        )
        menubar.addMenu(edit_menu)

        help_menu = QtWidgets.QMenu('Help', menubar)
        commonmenus.create_help_menu_items(help_menu, tool_help_func=_open_help)
        menubar.addMenu(help_menu)

    def reset_options(self):
        form = self.getSubForm()
        form.reset_options()
        return


def main(show=True, auto_raise=True, delete=False):
    win = AttributeBakeWindow.open_window(
        show=show, auto_raise=auto_raise, delete=delete
    )
    return win
