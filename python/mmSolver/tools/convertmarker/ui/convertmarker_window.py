# Copyright (C) 2019, 2021 David Cattermole
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
Window for the Convert To Marker tool.

Usage::

   import mmSolver.tools.convertmarker.ui.convertmarker_window as window
   window.main()

"""

import mmSolver.ui.qtpyutils as qtpyutils

qtpyutils.override_binding_order()

import mmSolver.ui.Qt.QtCore as QtCore
import mmSolver.ui.Qt.QtWidgets as QtWidgets

import mmSolver.logger
import mmSolver.ui.uiutils as uiutils
import mmSolver.ui.helputils as helputils
import mmSolver.ui.commonmenus as commonmenus
import mmSolver.tools.convertmarker.constant as const
import mmSolver.tools.convertmarker.tool as tool
import mmSolver.tools.convertmarker.ui.convertmarker_layout as convertmarker_layout


LOG = mmSolver.logger.get_logger()
baseModule, BaseWindow = uiutils.getBaseWindow()


def _open_help():
    src = helputils.get_help_source()
    page = 'tools_createnode.html#convert-to-marker'
    helputils.open_help_in_browser(page=page, help_source=src)
    return


class ConvertMarkerWindow(BaseWindow):
    name = 'ConvertMarkerWindow'

    def __init__(self, parent=None, name=None):
        super(ConvertMarkerWindow, self).__init__(parent, name=name)
        self.setupUi(self)
        self.addSubForm(convertmarker_layout.ConvertMarkerLayout)

        self.setWindowTitle(const.WINDOW_TITLE)
        self.setWindowType(qtpyutils.WINDOW_TYPE_DIALOG)

        # Standard Buttons
        self.baseHideStandardButtons()
        self.applyBtn.show()
        self.closeBtn.show()

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
    """
    Open the Convert To Marker UI window.

    :param show: Show the UI.
    :type show: bool

    :param auto_raise: If the UI is open, raise it to the front?
    :type auto_raise: bool

    :param delete: Delete the existing UI and rebuild it? Helpful when
                   developing the UI in Maya script editor.
    :type delete: bool

    :returns: A new convert marker window, or None if the window cannot be
              opened.
    :rtype: ConvertMarkerWindow or None.
    """
    win = ConvertMarkerWindow.open_window(
        show=show, auto_raise=auto_raise, delete=delete
    )
    return win
